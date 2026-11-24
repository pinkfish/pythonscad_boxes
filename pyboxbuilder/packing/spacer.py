# SPDX-License-Identifier: Apache-2.0
"""Spacer tray generation — fill leftover space with minimal, hole-free, supported trays.

Four stages (FR-014, FR-014a/b/c, FR-018):

1. **Sweep** the game box for empty volume using an axis-unbiased 3D histogram
   maximal-empty-cuboid DP ($O(N_x N_y N_z^2)$), extracting the globally largest
   empty cuboid at every step regardless of axis orientation.
2. **Merge** adjacent cuboids whose union is itself a cuboid via indexed face
   matching to a deterministic fixed point.
3. **Rectilinear polygon merge** of coplanar same-Z neighbors into L/T/U
   `PathBox` footprints, automatically splitting genus >= 1 ring/donut frames
   around interior boxes so no spacer ever swallows an enclosed box.
4. **Support & clearance filter** shrinking footprints by `clearance` and
   verifying both vertical support from below and minimum printable thickness.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyboxbuilder.packing.layout import Placement

EPSILON = 0.01
"""Coordinates closer than this are the same plane."""

MIN_SPACER_DIM = 5.0
"""A tray thinner than this in any axis is too fragile to print (FR-014)."""

MAX_GRID_CELLS = 200_000
"""Above this the exact 3D histogram search falls back to the cheap linear scan."""


@dataclass(frozen=True)
class SpacerSpec:
    """Configuration for a single spacer tray."""

    label: str
    width: float
    length: float
    height: float
    position: tuple[float, float, float]


@dataclass(frozen=True)
class Void:
    """An empty region: a box, or a prism over a non-rectangular footprint."""

    position: tuple[float, float, float]
    size: tuple[float, float, float]
    path: tuple[tuple[float, float], ...] | None = None

    @property
    def volume(self) -> float:
        """The void's volume."""
        if self.path is not None:
            return _polygon_area(self.path) * self.size[2]
        return self.size[0] * self.size[1] * self.size[2]

    def far_corner(self) -> tuple[float, float, float]:
        """Return the void's far corner (origin plus size)."""
        return tuple(p + s for p, s in zip(self.position, self.size, strict=False))  # type: ignore[return-value]

    def thinnest(self) -> float:
        """Return the void's thinnest dimension."""
        return min(self.size)

    def relative_path(self) -> tuple[tuple[float, float], ...] | None:
        """`path` moved into the void's own frame, which is what PathBox wants."""
        if self.path is None:
            return None
        return tuple(
            (x - self.position[0], y - self.position[1]) for x, y in self.path
        )


# --------------------------------------------------------------------- sweep


def _dedupe_planes(values: set[float], upper: float) -> list[float]:
    """Sort plane coordinates inside ``[0..upper]`` and collapse < EPSILON/10 duplicates."""
    raw = sorted(v for v in values if -EPSILON <= v <= upper + EPSILON)
    out: list[float] = []
    for v in raw:
        clamped = min(max(v, 0.0), upper)
        if not out or abs(clamped - out[-1]) > 1e-5:
            out.append(clamped)
    return out


def _plane_grid(
    container: tuple[float, float, float], placements: Sequence[Placement]
) -> tuple[list[float], list[float], list[float]]:
    """Return the sorted X/Y/Z planes bounding every box and the container itself."""
    axes: list[set[float]] = [{0.0, float(container[i])} for i in range(3)]
    for placement in placements:
        for i in range(3):
            axes[i].add(float(placement.position[i]))
            axes[i].add(float(placement.position[i] + placement.size[i]))
    return (
        _dedupe_planes(axes[0], float(container[0])),
        _dedupe_planes(axes[1], float(container[1])),
        _dedupe_planes(axes[2], float(container[2])),
    )


def _occupancy(
    planes: tuple[list[float], list[float], list[float]], placements: Sequence[Placement]
) -> list[list[list[bool]]]:
    """Mark every grid cell that lies inside a placed box."""
    xs, ys, zs = planes
    nx, ny, nz = len(xs) - 1, len(ys) - 1, len(zs) - 1
    occupied = [[[False] * nz for _ in range(ny)] for _ in range(nx)]

    for placement in placements:
        px, py, pz = placement.position
        pw, pl, ph = placement.size
        for i in range(nx):
            if not (xs[i] >= px - EPSILON and xs[i + 1] <= px + pw + EPSILON):
                continue
            for j in range(ny):
                if not (ys[j] >= py - EPSILON and ys[j + 1] <= py + pl + EPSILON):
                    continue
                for k in range(nz):
                    if zs[k] >= pz - EPSILON and zs[k + 1] <= pz + ph + EPSILON:
                        occupied[i][j][k] = True
    return occupied


def _grow(
    taken: list[list[list[bool]]],
    start: tuple[int, int, int],
    counts: tuple[int, int, int],
) -> tuple[int, int, int]:
    """Cheap linear fallback growth from ``start`` when grid exceeds MAX_GRID_CELLS."""
    i, j, k = start
    nx, ny, nz = counts

    i2 = i
    while i2 < nx and not taken[i2][j][k]:
        i2 += 1

    j2 = j + 1
    while j2 < ny and all(not taken[ii][j2][k] for ii in range(i, i2)):
        j2 += 1

    k2 = k + 1
    while k2 < nz and all(
        not taken[ii][jj][k2] for ii in range(i, i2) for jj in range(j, j2)
    ):
        k2 += 1

    return i2, j2, k2


def _best_empty_cuboid_3d(
    taken: list[list[list[bool]]],
    xs: list[float],
    ys: list[float],
    zs: list[float],
) -> tuple[float, tuple[int, int, int], tuple[int, int, int]] | None:
    """Find the globally largest-volume empty 3D cuboid via 2D histogram DP across Z slabs."""
    nx, ny, nz = len(xs) - 1, len(ys) - 1, len(zs) - 1
    max_xy_area = (xs[-1] - xs[0]) * (ys[-1] - ys[0])

    best_vol = 0.0
    best_bounds: tuple[tuple[int, int, int], tuple[int, int, int]] | None = None
    best_tiebreak: tuple[float, float, float] = (0.0, 0.0, 0.0)

    for k1 in range(nz):
        if (zs[-1] - zs[k1]) * max_xy_area <= best_vol + 1e-9:
            break
        slab_free = [[True] * ny for _ in range(nx)]

        for k2 in range(k1 + 1, nz + 1):
            kk = k2 - 1
            any_free = False
            for i in range(nx):
                tk_col = taken[i]
                sf_col = slab_free[i]
                for j in range(ny):
                    if sf_col[j]:
                        if tk_col[j][kk]:
                            sf_col[j] = False
                        else:
                            any_free = True
            if not any_free:
                break

            h_mm = zs[k2] - zs[k1]
            if h_mm * max_xy_area <= best_vol + 1e-9:
                continue

            # Monotonic-stack largest physical-area rectangle on (xs, ys)
            start_j = [0] * nx
            for j in range(ny):
                y_end = ys[j + 1]
                # Stack entries: (start_col_i, physical_len_y, row_start_j)
                stack: list[tuple[int, float, int]] = []
                for i in range(nx + 1):
                    if i < nx:
                        if slab_free[i][j]:
                            sj = start_j[i]
                            hy = y_end - ys[sj]
                        else:
                            start_j[i] = j + 1
                            sj = j + 1
                            hy = 0.0
                    else:
                        sj = j + 1
                        hy = 0.0

                    push_i = i
                    while stack and stack[-1][1] > hy + 1e-9:
                        si, prev_hy, prev_sj = stack.pop()
                        vol = (xs[i] - xs[si]) * prev_hy * h_mm
                        tb = (-xs[si], -ys[prev_sj], -zs[k1])
                        if vol > best_vol + 1e-9 or (
                            abs(vol - best_vol) <= 1e-9 and tb > best_tiebreak
                        ):
                            best_vol = vol
                            best_bounds = ((si, prev_sj, k1), (i, j + 1, k2))
                            best_tiebreak = tb
                        push_i = si

                    if hy > 1e-9 and (not stack or stack[-1][1] < hy - 1e-9):
                        stack.append((push_i, hy, sj))

    if best_bounds is None or best_vol <= 0.0:
        return None
    return best_vol, best_bounds[0], best_bounds[1]


def sweep_free_space(
    container: tuple[float, float, float], placements: Sequence[Placement]
) -> list[Void]:
    """Decompose the space no placement occupies into disjoint boxes, largest first."""
    if not placements:
        return []

    planes = _plane_grid(container, placements)
    xs, ys, zs = planes
    counts = (len(xs) - 1, len(ys) - 1, len(zs) - 1)
    if min(counts) <= 0:
        return []

    taken = _occupancy(planes, placements)
    exact_dp = counts[0] * counts[1] * counts[2] <= MAX_GRID_CELLS

    def void_from(start: tuple[int, int, int], end: tuple[int, int, int]) -> Void:
        i, j, k = start
        i2, j2, k2 = end
        return Void(
            position=(xs[i], ys[j], zs[k]),
            size=(xs[i2] - xs[i], ys[j2] - ys[j], zs[k2] - zs[k]),
        )

    voids: list[Void] = []
    if exact_dp:
        while True:
            found = _best_empty_cuboid_3d(taken, xs, ys, zs)
            if found is None:
                return voids
            _vol, (i, j, k), (i2, j2, k2) = found
            for ii in range(i, i2):
                for jj in range(j, j2):
                    for kk in range(k, k2):
                        taken[ii][jj][kk] = True
            voids.append(void_from((i, j, k), (i2, j2, k2)))

    # Fallback cheap linear scan when grid exceeds MAX_GRID_CELLS
    for i in range(counts[0]):
        for j in range(counts[1]):
            for k in range(counts[2]):
                if taken[i][j][k]:
                    continue
                i2, j2, k2 = _grow(taken, (i, j, k), counts)
                for ii in range(i, i2):
                    for jj in range(j, j2):
                        for kk in range(k, k2):
                            taken[ii][jj][kk] = True
                voids.append(void_from((i, j, k), (i2, j2, k2)))
    return voids


# --------------------------------------------------------------------- merge


def _mergeable_axis(a: Void, b: Void) -> int | None:
    """Return the axis along which `a` and `b` fuse into one box, or None."""
    for axis in range(3):
        others = [i for i in range(3) if i != axis]
        if any(
            abs(a.position[i] - b.position[i]) > EPSILON
            or abs(a.size[i] - b.size[i]) > EPSILON
            for i in others
        ):
            continue
        a_far, b_far = a.far_corner(), b.far_corner()
        if (
            abs(a_far[axis] - b.position[axis]) <= EPSILON
            or abs(b_far[axis] - a.position[axis]) <= EPSILON
        ):
            return axis
    return None


def _fuse(a: Void, b: Void, axis: int) -> Void:
    position = list(a.position)
    size = list(a.size)
    position[axis] = min(a.position[axis], b.position[axis])
    size[axis] = a.size[axis] + b.size[axis]
    return Void(position=tuple(position), size=tuple(size))  # type: ignore[arg-type]


def merge_voids(voids: list[Void]) -> list[Void]:
    """Fuse mergeable voids deterministically using orthogonal face-bucket indexing (FR-014b)."""
    if len(voids) <= 1:
        return list(voids)

    remaining = sorted(
        voids,
        key=lambda v: (
            round(v.position[0], 3),
            round(v.position[1], 3),
            round(v.position[2], 3),
            round(v.size[0], 3),
            round(v.size[1], 3),
            round(v.size[2], 3),
        ),
    )

    # Fuse along each axis in canonical order, repeating until fixed point
    changed = True
    while changed:
        changed = False
        for axis in range(3):
            o1, o2 = [i for i in range(3) if i != axis]
            buckets: dict[tuple[int, int, int, int], list[Void]] = {}
            for v in remaining:
                bkey = (
                    round(v.position[o1] * 50),
                    round(v.size[o1] * 50),
                    round(v.position[o2] * 50),
                    round(v.size[o2] * 50),
                )
                buckets.setdefault(bkey, []).append(v)

            next_remaining: list[Void] = []
            for group in buckets.values():
                group.sort(key=lambda v: v.position[axis])
                cur = group[0]
                for nxt in group[1:]:
                    if _mergeable_axis(cur, nxt) == axis:
                        cur = _fuse(cur, nxt, axis)
                        changed = True
                    else:
                        next_remaining.append(cur)
                        cur = nxt
                next_remaining.append(cur)
            remaining = next_remaining

    remaining.sort(
        key=lambda v: (
            round(v.position[0], 3),
            round(v.position[1], 3),
            round(v.position[2], 3),
            round(v.size[0], 3),
            round(v.size[1], 3),
            round(v.size[2], 3),
        )
    )
    return remaining


# -------------------------------------------------- rectilinear merge (FR-018)


def _polygon_area(path: tuple[tuple[float, float], ...]) -> float:
    from pyboxbuilder.paths import polygon_area

    return polygon_area(path)


def _footprints_touch(a: Void, b: Void) -> bool:
    """Return True when two footprints share a border segment of non-zero length."""
    for axis in range(2):
        other = 1 - axis
        a_lo, a_hi = a.position[axis], a.position[axis] + a.size[axis]
        b_lo, b_hi = b.position[axis], b.position[axis] + b.size[axis]
        flush = abs(a_hi - b_lo) <= EPSILON or abs(b_hi - a_lo) <= EPSILON
        if not flush:
            continue
        overlap = min(
            a.position[other] + a.size[other], b.position[other] + b.size[other]
        ) - max(a.position[other], b.position[other])
        if overlap > EPSILON:
            return True
    return False


def _components(voids: list[Void]) -> list[list[Void]]:
    """Group voids into connected clusters by footprint adjacency."""
    unassigned = list(voids)
    groups: list[list[Void]] = []
    while unassigned:
        group = [unassigned.pop()]
        grew = True
        while grew:
            grew = False
            for candidate in list(unassigned):
                if any(_footprints_touch(candidate, member) for member in group):
                    group.append(candidate)
                    unassigned.remove(candidate)
                    grew = True
        groups.append(group)
    return groups


def _extract_boundary_loops(voids: list[Void]) -> list[tuple[tuple[float, float], ...]]:
    """Extract all closed boundary rings (outer CCW rings and inner CW hole rings)."""
    xs = _dedupe_planes(
        {v.position[0] for v in voids} | {v.position[0] + v.size[0] for v in voids},
        max((v.position[0] + v.size[0] for v in voids), default=0.0) + 1.0,
    )
    ys = _dedupe_planes(
        {v.position[1] for v in voids} | {v.position[1] + v.size[1] for v in voids},
        max((v.position[1] + v.size[1] for v in voids), default=0.0) + 1.0,
    )

    filled: set[tuple[int, int]] = set()
    for void in voids:
        for i in range(len(xs) - 1):
            if not (
                xs[i] >= void.position[0] - EPSILON
                and xs[i + 1] <= void.position[0] + void.size[0] + EPSILON
            ):
                continue
            for j in range(len(ys) - 1):
                if (
                    ys[j] >= void.position[1] - EPSILON
                    and ys[j + 1] <= void.position[1] + void.size[1] + EPSILON
                ):
                    filled.add((i, j))

    edges: set[tuple[tuple[int, int], tuple[int, int]]] = set()
    for i, j in sorted(filled):
        corners = [(i, j), (i + 1, j), (i + 1, j + 1), (i, j + 1)]
        for n in range(4):
            start, end = corners[n], corners[(n + 1) % 4]
            if (end, start) in edges:
                edges.discard((end, start))
            else:
                edges.add((start, end))

    if not edges:
        return []

    outgoing: dict[tuple[int, int], list[tuple[int, int]]] = {}
    for start, end in sorted(edges):
        outgoing.setdefault(start, []).append(end)

    # Right-turn preference at degree-4 saddle vertices keeps filled cells on the left
    # and splits figure-8 pinches cleanly without self-crossing.
    def turn_priority(prev_pt: tuple[int, int], cur_pt: tuple[int, int], nxt_pt: tuple[int, int]) -> int:
        dx1, dy1 = cur_pt[0] - prev_pt[0], cur_pt[1] - prev_pt[1]
        dx2, dy2 = nxt_pt[0] - cur_pt[0], nxt_pt[1] - cur_pt[1]
        cross = dx1 * dy2 - dy1 * dx2
        dot = dx1 * dx2 + dy1 * dy2
        if cross < 0:
            return 0  # right turn (keeps interior connected locally)
        if dot > 0:
            return 1  # straight
        if cross > 0:
            return 2  # left turn
        return 3

    loops: list[tuple[tuple[float, float], ...]] = []
    max_steps = len(edges) + 2

    while outgoing:
        first = min(outgoing)
        opts_first = outgoing[first]
        nxt = opts_first.pop(0)
        if not opts_first:
            del outgoing[first]

        ring_idx = [first]
        prev, node = first, nxt
        steps = 0
        while node != first:
            steps += 1
            if steps > max_steps:
                return []
            ring_idx.append(node)
            options = outgoing.get(node)
            if not options:
                return []
            if len(options) > 1:
                options.sort(key=lambda cand: turn_priority(prev, node, cand))
            chosen = options.pop(0)
            if not options:
                del outgoing[node]
            prev, node = node, chosen

        pts = _drop_collinear([(xs[i], ys[j]) for i, j in ring_idx])
        if len(pts) >= 4:
            loops.append(pts)

    return loops


def union_outline(voids: list[Void]) -> tuple[tuple[float, float], ...]:
    """Trace the single genus-0 outline of a union of axis-aligned footprints.

    Returns ``()`` if the union is disconnected or contains an interior hole
    (genus >= 1), so callers never swallow an enclosed box inside a ring void.
    """
    loops = _extract_boundary_loops(voids)
    if len(loops) != 1:
        return ()
    from pyboxbuilder.paths import signed_area

    if signed_area(loops[0]) <= 0:
        return ()
    return loops[0]


def _drop_collinear(points: Sequence[tuple[float, float]]) -> tuple[tuple[float, float], ...]:
    """Remove points that sit in the middle of a straight run."""
    if len(points) < 3:
        return tuple(points)
    kept = []
    for n, point in enumerate(points):
        before = points[n - 1]
        after = points[(n + 1) % len(points)]
        straight = (
            abs(before[0] - point[0]) <= EPSILON and abs(point[0] - after[0]) <= EPSILON
        ) or (
            abs(before[1] - point[1]) <= EPSILON and abs(point[1] - after[1]) <= EPSILON
        )
        if not straight:
            kept.append(point)
    return tuple(kept)


def _slice_voids_at_y(voids: list[Void], cut_y: float) -> tuple[list[Void], list[Void]]:
    """Split rectangular voids across horizontal plane ``y = cut_y``."""
    below: list[Void] = []
    above: list[Void] = []
    for v in voids:
        y0, y1 = v.position[1], v.position[1] + v.size[1]
        if y1 <= cut_y + EPSILON:
            below.append(v)
        elif y0 >= cut_y - EPSILON:
            above.append(v)
        else:
            below.append(Void(v.position, (v.size[0], cut_y - y0, v.size[2])))
            above.append(
                Void((v.position[0], cut_y, v.position[2]), (v.size[0], y1 - cut_y, v.size[2]))
            )
    return merge_voids(below), merge_voids(above)


def _merge_component_with_hole_split(group: list[Void], z_origin: float, z_size: float) -> list[Void]:
    """Merge a connected coplanar component, splitting along interior holes if genus >= 1."""
    if len(group) == 1:
        return group

    loops = _extract_boundary_loops(group)
    if not loops:
        return group

    from pyboxbuilder.paths import signed_area

    outer_loops = [lp for lp in loops if signed_area(lp) > 0]
    hole_loops = [lp for lp in loops if signed_area(lp) < 0]

    if len(outer_loops) == 1 and not hole_loops:
        outline = outer_loops[0]
        xs = [x for x, _ in outline]
        ys = [y for _, y in outline]
        return [
            Void(
                position=(min(xs), min(ys), z_origin),
                size=(max(xs) - min(xs), max(ys) - min(ys), z_size),
                path=outline,
            )
        ]

    if hole_loops and all(v.path is None for v in group):
        # Cut across the middle of the first interior hole so the donut splits into two U/L trays!
        hys = [y for _, y in hole_loops[0]]
        cut_y = (min(hys) + max(hys)) / 2.0
        low_part, high_part = _slice_voids_at_y(group, cut_y)
        if low_part and high_part:
            out: list[Void] = []
            for half in (low_part, high_part):
                for sub_comp in _components(half):
                    out.extend(_merge_component_with_hole_split(sub_comp, z_origin, z_size))
            return out

    return group


def merge_rectilinear(voids: list[Void]) -> list[Void]:
    """Fuse coplanar same-Z neighbours into polygon-footprint trays, splitting holes (FR-018)."""
    by_layer: dict[tuple[float, float], list[Void]] = {}
    for void in voids:
        if void.path is not None:
            by_layer.setdefault((void.position[2], void.size[2]), []).append(void)
            continue
        key = (round(void.position[2], 4), round(void.size[2], 4))
        by_layer.setdefault(key, []).append(void)

    merged: list[Void] = []
    for (z_origin, z_size), layer in sorted(by_layer.items()):
        passthrough = [v for v in layer if v.path is not None]
        rects = [v for v in layer if v.path is None]
        merged.extend(passthrough)
        for group in _components(rects):
            merged.extend(_merge_component_with_hole_split(group, z_origin, z_size))
    return merged


# ------------------------------------------------------------------ assemble


def apply_clearance(void: Void, slack: float) -> Void:
    """Shrink a void by `slack` on every horizontal side so the tray lifts out freely."""
    if slack <= 0:
        return void

    if void.path is not None:
        return _inset_polygon_void(void, slack)

    return Void(
        position=(void.position[0] + slack, void.position[1] + slack, void.position[2]),
        size=(
            max(void.size[0] - 2 * slack, 0.0),
            max(void.size[1] - 2 * slack, 0.0),
            void.size[2],
        ),
    )


def _inset_polygon_void(void: Void, slack: float) -> Void:
    """Pull an L/T/U footprint inward by `slack` on every side, guarding against inversion."""
    from pyboxbuilder.paths import bounds, inset_rectilinear, signed_area

    assert void.path is not None
    orig_sign = signed_area(void.path)
    moved = inset_rectilinear(void.path, slack)
    if orig_sign * signed_area(moved) <= 0:
        # Arm collapsed/inverted under slack
        return Void(position=void.position, size=(0.0, 0.0, void.size[2]))
    (min_x, min_y), (max_x, max_y) = bounds(moved)
    return Void(
        position=(min_x, min_y, void.position[2]),
        size=(max(0.0, max_x - min_x), max(0.0, max_y - min_y), void.size[2]),
        path=moved,
    )


def _has_vertical_support(
    void: Void,
    placements: Sequence[Placement],
    lower_spacers: Sequence[Void],
) -> bool:
    """Return True if ``void`` sits on the floor or has substantial support at ``z = void.position[2]``."""
    z = void.position[2]
    if z <= EPSILON:
        return True

    vx, vy, _ = void.position
    vw, vl, _ = void.size
    footprint_area = _polygon_area(void.path) if void.path is not None else (vw * vl)
    if footprint_area <= 1e-6:
        return False

    supported_area = 0.0
    # Sum overlap with placed boxes whose top sits at z
    for p in placements:
        if abs((p.position[2] + p.size[2]) - z) > EPSILON * 2:
            continue
        ox = max(0.0, min(vx + vw, p.position[0] + p.size[0]) - max(vx, p.position[0]))
        oy = max(0.0, min(vy + vl, p.position[1] + p.size[1]) - max(vy, p.position[1]))
        supported_area += ox * oy

    for s in lower_spacers:
        if abs((s.position[2] + s.size[2]) - z) > EPSILON * 2:
            continue
        ox = max(0.0, min(vx + vw, s.position[0] + s.size[0]) - max(vx, s.position[0]))
        oy = max(0.0, min(vy + vl, s.position[1] + s.size[1]) - max(vy, s.position[1]))
        supported_area += ox * oy

    return supported_area >= footprint_area * 0.70 - 1e-4


def generate_spacer_voids(
    container: tuple[float, float, float],
    placements: Sequence[Placement],
    *,
    clearance: float = 0.0,
    min_dim: float = MIN_SPACER_DIM,
    min_xy: float | None = None,
) -> list[Void]:
    """Sweep, merge, split holes, verify support, shrink and filter — the whole spacer pass."""
    xy_floor = min_dim if min_xy is None else min_xy
    voids = merge_voids(sweep_free_space(container, placements))
    printable = [
        v
        for v in voids
        if v.size[2] >= min_dim - EPSILON
        and v.size[0] >= xy_floor - EPSILON
        and v.size[1] >= xy_floor - EPSILON
    ]

    # Check vertical support from bottom to top so an upper spacer never floats over a dropped sliver
    supported_rects: list[Void] = []
    for v in sorted(printable, key=lambda item: item.position[2]):
        if _has_vertical_support(v, placements, supported_rects):
            supported_rects.append(v)

    min_post_xy = max(2.0, xy_floor - 2.0 * clearance) - EPSILON
    trays = [apply_clearance(v, clearance) for v in merge_rectilinear(supported_rects)]
    kept = [
        v
        for v in trays
        if v.size[2] >= min_dim - EPSILON
        and v.size[0] >= min_post_xy
        and v.size[1] >= min_post_xy
        and v.volume > 0
    ]
    return sorted(kept, key=lambda v: (-v.volume, v.position))


def generate_spacer_placements(
    container: tuple[float, float, float],
    placements: Sequence[Placement],
    *,
    clearance: float = 0.0,
    min_dim: float = MIN_SPACER_DIM,
    min_xy: float | None = None,
) -> list[Placement]:
    """`generate_spacer_voids` as `Placement`s named `spacer_1..spacer_N`."""
    from pyboxbuilder.packing.layout import Placement

    return [
        Placement(
            label=f"spacer_{n}",
            position=void.position,
            size=void.size,
            rotation=False,
            path=void.relative_path(),
        )
        for n, void in enumerate(
            generate_spacer_voids(
                container,
                placements,
                clearance=clearance,
                min_dim=min_dim,
                min_xy=min_xy,
            ),
            start=1,
        )
    ]


# --------------------------------------------------------- row-based (legacy)


def generate_spacers(
    container_width: float,
    container_length: float,
    row_widths: list[float],
    row_lengths: list[float],
    gap_threshold: float = 10.0,
    min_spacer_dim: float = 15.0,
    min_spacer_height: float = 5.0,
) -> list[SpacerSpec]:
    """Generate spacer tray specs for gaps left at the end of 2D rows."""
    spacers: list[SpacerSpec] = []
    counter = 1

    for i, (row_w, row_l) in enumerate(zip(row_widths, row_lengths, strict=False)):
        remaining_w = container_width - row_w
        if remaining_w >= min_spacer_dim and remaining_w >= gap_threshold:
            y_offset = sum(row_lengths[:i]) if i > 0 else 0.0
            spacers.append(
                SpacerSpec(
                    label=f"spacer_{counter}",
                    width=remaining_w,
                    length=row_l,
                    height=min_spacer_height,
                    position=(row_w, y_offset, 0),
                )
            )
            counter += 1

    total_length_used = sum(row_lengths)
    remaining_l = container_length - total_length_used
    if remaining_l >= min_spacer_dim and remaining_l >= gap_threshold:
        spacers.append(
            SpacerSpec(
                label=f"spacer_{counter}",
                width=container_width,
                length=remaining_l,
                height=min_spacer_height,
                position=(0, total_length_used, 0),
            )
        )

    return spacers
