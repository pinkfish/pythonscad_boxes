# SPDX-License-Identifier: Apache-2.0
"""Guillotine 3D box packer for densely-filled inserts (T187 / Auto-Layout v2).

Tracks disjoint free regions using exact 64-bit integer picometre arithmetic
(eliminating floating-point subtraction drift on fractional splits like H/3),
supports Corner, Full-Layer, and 1D Slab-Layer cuts (allowing independent Z
bridges within individual rows or columns), supports pre-cut pinned obstacles,
multi-choice Pareto box envelopes, and composite vertical stack chains, and uses
a 2-stage root-budgeted search to escape heavy-tailed root dead ends in <12 ms.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator, Sequence
from dataclasses import dataclass

SCALE = 1_000_000_000
"""Picometres per millimetre (10^-9 mm). Exact 64-bit int arithmetic with zero drift."""

TOL = 200
"""Comparison tolerance in picometres (2e-7 mm), well inside 1e-6 mm validation."""

MEMO_QUANT = 10_000
"""Quantisation step (10 nm = 1e-5 mm) for position-free memoisation keys."""

EPS = 1e-9
"""Float tolerance for orientation symmetry checks."""

Region = tuple[int, int, int, int, int, int, bool]
"""One free region in integer picometres — ``(x, y, z, w, l, h, full)``."""


@dataclass(frozen=True)
class Item:
    """A box (or composite vertical stack / multi-choice box) to place."""

    label: str
    size: tuple[float, float, float]
    no_rotate: bool = False
    size_options: tuple[tuple[float, float, float], ...] = ()
    """Optional Pareto-optimal alternative ``(w, l, h)`` envelopes for unsized boxes."""
    stack_members: tuple[tuple[str, tuple[float, float, float]], ...] = ()
    """Optional bottom-to-top ``(label, size)`` members bound into one vertical stack."""


@dataclass(frozen=True)
class Placed:
    """Where one box ended up."""

    label: str
    position: tuple[float, float, float]
    size: tuple[float, float, float]
    rotated: bool


def _to_int(mm: float) -> int:
    return round(float(mm) * SCALE)


def _orientations(
    options: Sequence[tuple[float, float, float]], no_rotate: bool
) -> list[tuple[tuple[int, int, int], tuple[float, float, float], bool]]:
    """Return unique ``(int_size, float_size, rotated)`` orientations across ``options``."""
    out: list[tuple[tuple[int, int, int], tuple[float, float, float], bool]] = []
    seen: set[tuple[int, int, int, bool]] = set()
    for raw in options:
        w, l, h = raw[0], raw[1], raw[2]
        iw, il, ih = _to_int(w), _to_int(l), _to_int(h)
        k0 = (iw // MEMO_QUANT, il // MEMO_QUANT, ih // MEMO_QUANT, False)
        if k0 not in seen:
            seen.add(k0)
            out.append(((iw, il, ih), raw, False))
        if not no_rotate and abs(w - l) > EPS:
            k1 = (il // MEMO_QUANT, iw // MEMO_QUANT, ih // MEMO_QUANT, True)
            if k1 not in seen:
                seen.add(k1)
                out.append(((il, iw, ih), (l, w, h), True))
    return out


def subtract_obstacles_3d(
    container: tuple[float, float, float],
    obstacles: Sequence[tuple[float, float, float, float, float, float]],
) -> tuple[Region, ...]:
    """Cut pinned boxes ``(x, y, z, w, l, h)`` out of ``container`` into disjoint supported regions."""
    cw, cl, ch = _to_int(container[0]), _to_int(container[1]), _to_int(container[2])
    regions: list[Region] = [(0, 0, 0, cw, cl, ch, False)]

    for ox_f, oy_f, oz_f, ow_f, ol_f, oh_f in obstacles:
        ox, oy, oz = _to_int(ox_f), _to_int(oy_f), _to_int(oz_f)
        ox1, oy1, oz1 = ox + _to_int(ow_f), oy + _to_int(ol_f), oz + _to_int(oh_f)
        next_regions: list[Region] = []

        for rx, ry, rz, rw, rl, rh, rfull in regions:
            rx1, ry1, rz1 = rx + rw, ry + rl, rz + rh
            if (
                ox1 <= rx + TOL
                or ox >= rx1 - TOL
                or oy1 <= ry + TOL
                or oy >= ry1 - TOL
                or oz1 <= rz + TOL
                or oz >= rz1 - TOL
            ):
                next_regions.append((rx, ry, rz, rw, rl, rh, rfull))
                continue

            ix0, ix1 = max(rx, ox), min(rx1, ox1)
            iy0, iy1 = max(ry, oy), min(ry1, oy1)

            # Left & right full-depth/full-height slabs
            if ix0 - rx > TOL:
                next_regions.append((rx, ry, rz, ix0 - rx, rl, rh, rfull))
            if rx1 - ix1 > TOL:
                next_regions.append((ix1, ry, rz, rx1 - ix1, rl, rh, rfull))

            # Front & back slabs within [ix0..ix1]
            if iy0 - ry > TOL and ix1 - ix0 > TOL:
                next_regions.append((ix0, ry, rz, ix1 - ix0, iy0 - ry, rh, rfull))
            if ry1 - iy1 > TOL and ix1 - ix0 > TOL:
                next_regions.append((ix0, iy1, rz, ix1 - ix0, ry1 - iy1, rh, rfull))

            # Above the obstacle (supported by the obstacle's own top face oz1!)
            if rz1 - oz1 > TOL and ix1 - ix0 > TOL and iy1 - iy0 > TOL and oz <= rz + TOL:
                next_regions.append((ix0, iy0, oz1, ix1 - ix0, iy1 - iy0, rz1 - oz1, False))

            # Below the obstacle (only usable if fully filled or no obstacle rests solely on air)
            if oz - rz > TOL and ix1 - ix0 > TOL and iy1 - iy0 > TOL:
                next_regions.append((ix0, iy0, rz, ix1 - ix0, iy1 - iy0, oz - rz, True))

        regions = next_regions

    return tuple(regions)


def _solve_core(
    initial_regions: tuple[Region, ...],
    items: list[Item],
    node_budget: int,
) -> list[Placed] | None:
    """Core exact-integer guillotine solver with slab-layer cuts and 2-stage root cap."""
    if not items:
        return []

    # Group identical items (same options, no_rotate, and stack signature) into equivalence classes
    class_keys: list[tuple[tuple[tuple[int, int, int], ...], bool, int]] = []
    class_orients: list[list[tuple[tuple[int, int, int], tuple[float, float, float], bool]]] = []
    class_items: list[list[Item]] = []

    for item in items:
        opts = item.size_options if item.size_options else (item.size,)
        quant_opts = tuple(
            (_to_int(s[0]) // MEMO_QUANT, _to_int(s[1]) // MEMO_QUANT, _to_int(s[2]) // MEMO_QUANT)
            for s in opts
        )
        # Keep items with distinct stack_members separate unless identical member sizes
        stack_sig = hash(tuple((m[1][0], m[1][1], m[1][2]) for m in item.stack_members)) if item.stack_members else 0
        key = (quant_opts, item.no_rotate, stack_sig)
        if key in class_keys and not item.size_options and not item.stack_members:
            idx = class_keys.index(key)
            class_items[idx].append(item)
        else:
            class_keys.append(key)
            class_orients.append(_orientations(opts, item.no_rotate))
            class_items.append([item])

    n_classes = len(class_keys)
    counts = tuple(len(group) for group in class_items)

    # Minimum possible volume and minimum possible dimension per class (for multi-choice bounds)
    class_min_vol = [
        min(iw * il * ih for (iw, il, ih), _, _ in orients)
        for orients in class_orients
    ]
    total_min_vol = sum(counts[i] * class_min_vol[i] for i in range(n_classes))

    def region_fits_any(rw: int, rl: int, rh: int, must_fill: bool, remaining: tuple[int, ...]) -> bool:
        for i in range(n_classes):
            if not remaining[i]:
                continue
            for (iw, il, ih), _, _ in class_orients[i]:
                if iw <= rw + TOL and il <= rl + TOL and ih <= rh + TOL:
                    if must_fill and abs(ih - rh) > TOL:
                        continue
                    return True
        return False

    def splits(
        region: Region,
        isize: tuple[int, int, int],
        remaining_after: tuple[int, ...],
    ) -> Iterator[tuple[Region, ...]]:
        """Yield Corner, Full-Layer, and 1D Slab-Layer cuts of ``region``."""
        x, y, z, w, l, h, full = region
        bw, bl, bh = isize
        gap_h = max(0, h - bh)
        dw = max(0, w - bw)
        dl = max(0, l - bl)

        def keep(r: Region) -> bool:
            if min(r[3], r[4], r[5]) <= TOL:
                return False
            # Keep `full=True` obligations so `any(not usable)` rejects unfillable holes!
            return region_fits_any(r[3], r[4], r[5], r[6], remaining_after)

        for x_major in (True, False):
            if x_major:
                sides = (
                    (x + bw, y, z, dw, l, h, full),
                    (x, y + bl, z, bw, dl, h, full),
                )
            else:
                sides = (
                    (x, y + bl, z, w, dl, h, full),
                    (x + bw, y, z, dw, bl, h, full),
                )

            # 1. Corner family: space above is strictly the box's own top face
            if not full or gap_h <= TOL:
                if full:
                    # Any leftover in a `full` region must also be fillable to full height!
                    raw_sides = [s for s in sides if min(s[3], s[4], s[5]) > TOL]
                    if all(keep(s) for s in raw_sides):
                        yield tuple(raw_sides)
                else:
                    above = (x, y, z + bh, bw, bl, gap_h, False)
                    yield tuple(r for r in (*sides, above) if keep(r))

            # 2. Full-Layer family: cut across entire (w, l) at z + bh
            if gap_h > TOL and not full:
                layer_sides = tuple(
                    (sx, sy, sz, sw, sl, bh, True)
                    for (sx, sy, sz, sw, sl, _sh, _f) in sides
                    if min(sw, sl) > TOL
                )
                if all(keep(r) for r in layer_sides):
                    above_full = (x, y, z + bh, w, l, gap_h, False)
                    yield (*layer_sides, *((above_full,) if keep(above_full) else ()))

        # 3. 1D Slab-Layer family: isolate a Y-row (w x bl) or X-column (bw x l) first,
        #    and cut a horizontal bridge layer ONLY across that row/column!
        if gap_h > TOL and not full:
            if dw > TOL:
                y_slab_side = (x + bw, y, z, dw, bl, bh, True)
                if keep(y_slab_side):
                    y_above = (x, y, z + bh, w, bl, gap_h, False)
                    y_rem = (x, y + bl, z, w, dl, h, False)
                    out_y = [y_slab_side]
                    if keep(y_above):
                        out_y.append(y_above)
                    if keep(y_rem):
                        out_y.append(y_rem)
                    yield tuple(out_y)
            if dl > TOL:
                x_slab_side = (x, y + bl, z, bw, dl, bh, True)
                if keep(x_slab_side):
                    x_above = (x, y, z + bh, bw, l, gap_h, False)
                    x_rem = (x + bw, y, z, dw, l, h, False)
                    out_x = [x_slab_side]
                    if keep(x_above):
                        out_x.append(x_above)
                    if keep(x_rem):
                        out_x.append(x_rem)
                    yield tuple(out_x)

    def memo_shape(r: Region) -> tuple[int, int, int, bool]:
        return (r[3] // MEMO_QUANT, r[4] // MEMO_QUANT, r[5] // MEMO_QUANT, r[6])

    total_nodes = 0
    dead: set[tuple[tuple[tuple[int, int, int, bool], ...], tuple[int, ...]]] = set()

    SolutionStep = tuple[int, int, int, tuple[float, float, float], bool, int]

    def solve(
        regions: tuple[Region, ...],
        remaining: tuple[int, ...],
        need_vol: int,
        branch_limit: list[int | None],
        is_root: bool = False,
    ) -> list[SolutionStep] | None:
        nonlocal total_nodes
        if total_nodes > node_budget:
            return None
        if not any(remaining):
            return [] if not any(r[6] for r in regions) else None
        if not regions:
            return None

        # Tight volume bound: only count regions that can hold at least one remaining item
        usable_vol = 0
        for r in regions:
            if r[6] and not region_fits_any(r[3], r[4], r[5], True, remaining):
                return None
            if region_fits_any(r[3], r[4], r[5], r[6], remaining):
                usable_vol += r[3] * r[4] * r[5]
        if usable_vol < need_vol:
            return None

        key = (tuple(sorted(memo_shape(r) for r in regions)), remaining)
        if key in dead:
            return None

        # Fail-first: must_fill regions first, then smallest volume region
        index = min(
            range(len(regions)),
            key=lambda i: (not regions[i][6], regions[i][3] * regions[i][4] * regions[i][5]),
        )
        region = regions[index]
        rest = regions[:index] + regions[index + 1:]
        rw, rl, rh, must_fill = region[3], region[4], region[5], region[6]

        candidates: list[
            tuple[int, int, int, int, tuple[int, int, int], tuple[float, float, float], bool]
        ] = []
        for i in range(n_classes):
            if not remaining[i]:
                continue
            for isize, fsize, rotated in class_orients[i]:
                iw, il, ih = isize
                if iw > rw + TOL or il > rl + TOL or ih > rh + TOL:
                    continue
                if must_fill and abs(ih - rh) > TOL:
                    continue
                flush = (abs(iw - rw) <= TOL) + (abs(il - rl) <= TOL) + (abs(ih - rh) <= TOL)
                candidates.append((-flush, -(iw * il * ih), int(rotated), i, isize, fsize, rotated))
        candidates.sort()

        fully_explored = True
        root_cap = max(250, min(600, node_budget // 10))

        for _flush, _vol, _turn, i, isize, fsize, rotated in candidates:
            nxt_list = list(remaining)
            nxt_list[i] -= 1
            nxt = tuple(nxt_list)
            next_need = need_vol - class_min_vol[i]

            shapes_tried: set[tuple[tuple[int, int, int, bool], ...]] = set()
            for subs in splits(region, isize, nxt):
                shape = tuple(sorted(memo_shape(s) for s in subs))
                if shape in shapes_tried:
                    continue
                shapes_tried.add(shape)

                sub_limit: list[int | None] = (
                    [root_cap] if (is_root and branch_limit[0] is not None) else branch_limit
                )
                if sub_limit[0] is not None:
                    if sub_limit[0] <= 0:
                        fully_explored = False
                        continue
                    sub_limit[0] -= 1

                total_nodes += 1
                if total_nodes > node_budget:
                    return None

                tail = solve(tuple(sorted(rest + subs)), nxt, next_need, sub_limit, False)
                if tail is not None:
                    return [(region[0], region[1], region[2], fsize, rotated, i), *tail]
                if sub_limit[0] is not None and sub_limit[0] <= 0:
                    fully_explored = False

        if not must_fill:
            if branch_limit[0] is None or branch_limit[0] > 0:
                if branch_limit[0] is not None:
                    branch_limit[0] -= 1
                total_nodes += 1
                tail = solve(rest, remaining, need_vol, branch_limit, False)
                if tail is not None:
                    return tail
                if branch_limit[0] is not None and branch_limit[0] <= 0:
                    fully_explored = False
            else:
                fully_explored = False

        if fully_explored and total_nodes <= node_budget:
            dead.add(key)
        return None

    # Pass 1: per-root-choice node cap escapes bad depth-0 choices rapidly
    solution = None
    if node_budget >= 2_000 and len(items) >= 6:
        solution = solve(initial_regions, counts, total_min_vol, [600], is_root=True)
    # Pass 2: full remaining budget reusing all proven-dead states from Pass 1
    if solution is None and total_nodes <= node_budget:
        solution = solve(initial_regions, counts, total_min_vol, [None], is_root=False)
    if solution is None:
        return None

    pool = [list(group) for group in class_items]
    placed_out: list[Placed] = []
    for rx, ry, rz, fsize, rotated, i in solution:
        item = pool[i].pop(0)
        px, py, pz = rx / SCALE, ry / SCALE, rz / SCALE
        if item.stack_members:
            z_cur = pz
            for member_label, msize in item.stack_members:
                ms = (msize[1], msize[0], msize[2]) if rotated else msize
                placed_out.append(
                    Placed(
                        label=member_label,
                        position=(px, py, z_cur),
                        size=ms,
                        rotated=rotated,
                    )
                )
                z_cur += msize[2]
        else:
            placed_out.append(
                Placed(
                    label=item.label,
                    position=(px, py, pz),
                    size=fsize,
                    rotated=rotated,
                )
            )
    return placed_out


def _pregroup_full_height_columns(
    container_h: float, items: list[Item]
) -> list[Item] | None:
    """Group identical-(W, L) single-size items whose heights partition into ``container_h``."""
    by_fp: dict[tuple[int, int, bool], list[Item]] = defaultdict(list)
    passthrough: list[Item] = []

    ih_target = _to_int(container_h)
    for item in items:
        if (
            item.size_options
            or item.stack_members
            or abs(_to_int(item.size[2]) - ih_target) <= TOL
        ):
            passthrough.append(item)
        else:
            iw, il = _to_int(item.size[0]) // MEMO_QUANT, _to_int(item.size[1]) // MEMO_QUANT
            by_fp[(iw, il, item.no_rotate)].append(item)

    grouped = list(passthrough)
    made_any_group = False

    for (_iw, _il, nr), group in by_fp.items():
        if len(group) < 2:
            grouped.extend(group)
            continue
        rem = sorted(group, key=lambda it: -it.size[2])
        used = [False] * len(rem)

        def find_subset(
            start: int,
            target_h: int,
            rem_items: list[Item] = rem,
            used_flags: list[bool] = used,
        ) -> list[int] | None:
            if abs(target_h) <= TOL:
                return []
            for idx in range(start, len(rem_items)):
                if used_flags[idx]:
                    continue
                mh = _to_int(rem_items[idx].size[2])
                if mh > target_h + TOL:
                    continue
                sub = find_subset(idx + 1, target_h - mh, rem_items, used_flags)
                if sub is not None:
                    return [idx, *sub]
            return None

        while True:
            sub = find_subset(0, ih_target)
            if not sub or len(sub) < 2:
                break
            for idx in sub:
                used[idx] = True
            made_any_group = True
            members = tuple((rem[idx].label, rem[idx].size) for idx in sub)
            base_w, base_l, _ = rem[sub[0]].size
            grouped.append(
                Item(
                    label="+".join(m[0] for m in members),
                    size=(base_w, base_l, container_h),
                    no_rotate=nr,
                    stack_members=members,
                )
            )
        for idx, it in enumerate(rem):
            if not used[idx]:
                grouped.append(it)

    return grouped if made_any_group else None


def pack_guillotine(
    container: tuple[float, float, float],
    items: list[Item],
    *,
    node_budget: int = 200_000,
    obstacles: Sequence[tuple[float, float, float, float, float, float]] = (),
) -> list[Placed] | None:
    """Pack ``items`` into ``container`` around optional ``obstacles``, or return ``None``.

    Args:
        container: ``(width, length, height)`` of the space to fill in mm.
        items: Boxes to place (may carry ``size_options`` or ``stack_members``).
        node_budget: Search nodes before giving up.
        obstacles: Already-placed ``(x, y, z, w, l, h)`` boxes to pack around.

    Returns:
        List of ``Placed`` records, or ``None`` if no packing was found within budget.

    """
    if not items:
        return []
    if min(container) <= 0:
        return None

    initial_regions = (
        subtract_obstacles_3d(container, obstacles)
        if obstacles
        else ((0, 0, 0, _to_int(container[0]), _to_int(container[1]), _to_int(container[2]), False),)
    )
    if not initial_regions:
        return None

    # Fast pre-grouped pass for structured multi-column inserts (e.g. Root, 1899 Daihan);
    # falls back cleanly to ungrouped search if pre-grouping was over-constrained.
    if not obstacles and len(items) >= 8:
        macro_items = _pregroup_full_height_columns(container[2], items)
        if macro_items is not None:
            fast_budget = min(25_000, max(5_000, node_budget // 4))
            grouped_res = _solve_core(initial_regions, macro_items, fast_budget)
            if grouped_res is not None:
                return grouped_res
            node_budget = max(1, node_budget - fast_budget)

    return _solve_core(initial_regions, items, node_budget)
