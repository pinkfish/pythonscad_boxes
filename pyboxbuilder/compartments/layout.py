# SPDX-License-Identifier: Apache-2.0
"""Compartment auto-layout — 2D shelf + obstacle-aware MaxRects bin packing."""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from typing import Any

from pyboxbuilder.box.interior import Interior

# Imported for real rather than under TYPE_CHECKING: `CompartmentPlacement`
# annotates a field with it, and Sphinx resolves annotations through
# `get_type_hints`, which needs the name in this module's namespace.
from pyboxbuilder.compartments.element import CompartmentElement

CompartmentSpec = tuple[
    str, float, float, float,
    str | None, tuple[float, float] | None, tuple[Any, ...],
]
"""One compartment as the layout takes it.

``(label, width, length, depth, shape_file, position, elements)``. The short
forms — a bare ``(label, width, length, depth)`` from `compute_min_box_size`,
say — are padded by :func:`normalise_compartments` rather than being a second
shape every reader has to allow for.
"""

OuterSizerFn = Callable[[float, float, float], tuple[float, float, float]]


def normalise_compartments(
    compartments: Sequence[Sequence[Any]],
) -> list[CompartmentSpec]:
    """Pad every compartment tuple out to the full seven fields."""
    from typing import cast

    padding: tuple[Any, ...] = (None, None, ())
    return [
        cast(
            CompartmentSpec,
            (tuple(c) + padding[len(c) - 4 :]) if len(c) < 7 else tuple(c),
        )
        for c in compartments
    ]


WALL_SPACING_MM = 2.0
"""Wall left between adjacent compartments, and between one and the box wall."""


@dataclass
class CompartmentPlacement:
    """Position of a single compartment inside a box."""

    label: str
    size: tuple[float, float]
    depth: float
    position: tuple[float, float]  # (x, y) in box frame
    shape_file: str | None = None
    elements: tuple[CompartmentElement, ...] = ()


@dataclass
class CompartmentLayout:
    """Result of laying out compartments inside a box interior."""

    placements: list[CompartmentPlacement] = field(default_factory=list)
    overflow: bool = False

    def all_compartment_sizes(self) -> list[tuple[float, float]]:
        """Return (width, length) for each placement."""
        return [p.size for p in self.placements]


def _subtract_rect_2d(
    free_rects: list[tuple[float, float, float, float]],
    obs: tuple[float, float, float, float],
) -> list[tuple[float, float, float, float]]:
    """Subtract obstacle ``(ox, oy, ow, ol)`` from ``free_rects`` and prune dominated rects."""
    ox0, oy0, ow, ol = obs
    ox1, oy1 = ox0 + ow, oy0 + ol
    next_free: list[tuple[float, float, float, float]] = []

    for fx, fy, fw, fl in free_rects:
        fx1, fy1 = fx + fw, fy + fl
        if ox1 <= fx + 1e-7 or ox0 >= fx1 - 1e-7 or oy1 <= fy + 1e-7 or oy0 >= fy1 - 1e-7:
            next_free.append((fx, fy, fw, fl))
            continue
        if ox0 > fx + 1e-6:
            next_free.append((fx, fy, ox0 - fx, fl))
        if ox1 < fx1 - 1e-6:
            next_free.append((ox1, fy, fx1 - ox1, fl))
        if oy0 > fy + 1e-6:
            next_free.append((fx, fy, fw, oy0 - fy))
        if oy1 < fy1 - 1e-6:
            next_free.append((fx, oy1, fw, fy1 - oy1))

    pruned: list[tuple[float, float, float, float]] = []
    for i, (ax0, ay0, aw, al) in enumerate(next_free):
        ax1, ay1 = ax0 + aw, ay0 + al
        dominated = False
        for j, (bx0, by0, bw, bl) in enumerate(next_free):
            if i == j:
                continue
            if (
                bx0 <= ax0 + 1e-6
                and by0 <= ay0 + 1e-6
                and bx0 + bw >= ax1 - 1e-6
                and by0 + bl >= ay1 - 1e-6
            ) and ((bw * bl > aw * al + 1e-6) or j < i):
                dominated = True
                break
        if not dominated:
            pruned.append((ax0, ay0, aw, al))
    return pruned


def _pack_maxrects_2d(
    interior: Interior,
    auto_comps: list[CompartmentSpec],
    manual_boxes: list[tuple[float, float, float, float]],
    wall_spacing: float,
    no_rotate_labels: set[str],
    preserve_order: bool,
) -> tuple[list[CompartmentPlacement], bool]:
    """Pack ``auto_comps`` into ``interior`` around ``manual_boxes`` using 2D MaxRects BSSF."""
    avail_w = interior.width - 2.0 * wall_spacing
    avail_l = interior.length - 2.0 * wall_spacing
    if avail_w < -1e-6 or avail_l < -1e-6:
        return [], True

    free_rects: list[tuple[float, float, float, float]] = [
        (wall_spacing, wall_spacing, max(0.0, avail_w), max(0.0, avail_l))
    ]
    for mx, my, mw, ml in manual_boxes:
        free_rects = _subtract_rect_2d(
            free_rects,
            (
                mx - wall_spacing,
                my - wall_spacing,
                mw + 2.0 * wall_spacing,
                ml + 2.0 * wall_spacing,
            ),
        )

    items = (
        list(auto_comps)
        if preserve_order
        else sorted(auto_comps, key=lambda c: c[1] * c[2], reverse=True)
    )

    placed: list[CompartmentPlacement] = []
    for label, comp_w, comp_l, comp_depth, shape_file, _, elements in items:
        can_rotate = label not in no_rotate_labels
        orientations: list[tuple[float, float, int]] = [(comp_w, comp_l, 0)]
        if can_rotate and abs(comp_w - comp_l) > 1e-6:
            orientations.append((comp_l, comp_w, 1))

        best_score: tuple[float, float, float, int] | None = None
        best_choice: tuple[float, float, float, float] | None = None

        for rx, ry, rw, rl in free_rects:
            for w, l, rot_pen in orientations:
                if w <= rw + 1e-6 and l <= rl + 1e-6:
                    short_side = min(max(0.0, rw - w), max(0.0, rl - l))
                    long_side = max(max(0.0, rw - w), max(0.0, rl - l))
                    # Top-left skyline + Best-Short-Side-Fit
                    score = (round(ry, 4), round(short_side, 4), round(long_side, 4), rot_pen)
                    if best_score is None or score < best_score:
                        best_score = score
                        best_choice = (rx, ry, w, l)

        if best_choice is None:
            return placed, True

        px, py, pw, pl = best_choice
        placed.append(
            CompartmentPlacement(
                label=label,
                size=(pw, pl),
                depth=comp_depth,
                position=(interior.origin_x + px, interior.origin_y + py),
                shape_file=shape_file,
                elements=elements or (),
            )
        )
        free_rects = _subtract_rect_2d(
            free_rects,
            (
                px - wall_spacing,
                py - wall_spacing,
                pw + 2.0 * wall_spacing,
                pl + 2.0 * wall_spacing,
            ),
        )

    return placed, False


def _pack_shelf_2d(
    interior: Interior,
    auto_comps: list[CompartmentSpec],
    wall_spacing: float,
    no_rotate_labels: set[str],
    preserve_order: bool,
) -> tuple[list[CompartmentPlacement], bool]:
    """Shelf-pack ``auto_comps`` into an empty ``interior``."""
    interior_w = interior.width
    interior_l = interior.length
    sorted_comps = (
        list(auto_comps)
        if preserve_order
        else sorted(auto_comps, key=lambda c: c[1] * c[2], reverse=True)
    )

    x_cursor = wall_spacing
    y_cursor = wall_spacing
    current_row_height = 0.0
    placements: list[CompartmentPlacement] = []

    for label, comp_w, comp_l, comp_depth, shape_file, _, elements in sorted_comps:
        can_rotate = label not in no_rotate_labels
        fits_normal = (
            (x_cursor + comp_w + wall_spacing <= interior_w + 1e-6)
            and (y_cursor + comp_l + wall_spacing <= interior_l + 1e-6)
        )
        fits_rotated = (
            can_rotate
            and (x_cursor + comp_l + wall_spacing <= interior_w + 1e-6)
            and (y_cursor + comp_w + wall_spacing <= interior_l + 1e-6)
        )

        w, l = comp_w, comp_l
        if fits_normal or fits_rotated:
            if fits_normal and fits_rotated:
                if comp_l > comp_w:
                    w, l = comp_l, comp_w
            elif fits_rotated:
                w, l = comp_l, comp_w
        else:
            x_cursor = wall_spacing
            y_cursor += current_row_height + wall_spacing
            current_row_height = 0.0

            fits_normal_new = (
                (x_cursor + comp_w + wall_spacing <= interior_w + 1e-6)
                and (y_cursor + comp_l + wall_spacing <= interior_l + 1e-6)
            )
            fits_rotated_new = (
                can_rotate
                and (x_cursor + comp_l + wall_spacing <= interior_w + 1e-6)
                and (y_cursor + comp_w + wall_spacing <= interior_l + 1e-6)
            )

            if fits_normal_new or fits_rotated_new:
                if fits_normal_new and fits_rotated_new:
                    if comp_l > comp_w:
                        w, l = comp_l, comp_w
                elif fits_rotated_new:
                    w, l = comp_l, comp_w
            else:
                return placements, True

        if w > interior_w + 1e-6 or l > interior_l + 1e-6:
            return placements, True

        placements.append(
            CompartmentPlacement(
                label=label,
                size=(w, l),
                depth=comp_depth,
                position=(
                    interior.origin_x + x_cursor,
                    interior.origin_y + y_cursor,
                ),
                shape_file=shape_file,
                elements=elements or (),
            )
        )
        x_cursor += w + wall_spacing
        current_row_height = max(current_row_height, l)

    return placements, False


def layout_compartments(
    interior: Interior,
    compartments: Sequence[Sequence[Any]],
    wall_spacing: float = WALL_SPACING_MM,
    no_rotate_labels: set[str] | None = None,
    preserve_order: bool = False,
) -> CompartmentLayout:
    """2D layout of compartments inside the box interior with obstacle and rotation support.

    Uses aligned shelf rows when compartments fit cleanly without manual obstacles,
    and automatically falls back to obstacle-aware 2D MaxRects Best-Short-Side-Fit
    when manual compartments are present or when 1D shelves fragment the space.
    """
    comps = normalise_compartments(compartments)

    layout = CompartmentLayout()
    if not comps:
        return layout

    no_rotate_labels = no_rotate_labels or set()

    interior_w = interior.width
    interior_l = interior.length

    # 1. Process manually placed compartments first and record them as 2D obstacles
    auto_comps: list[CompartmentSpec] = []
    manual_boxes: list[tuple[float, float, float, float]] = []
    for comp in comps:
        label, comp_w, comp_l, comp_depth, shape_file, pos, elements = comp
        if pos is not None:
            if (
                pos[0] < -1e-6
                or pos[1] < -1e-6
                or pos[0] + comp_w > interior_w + 1e-6
                or pos[1] + comp_l > interior_l + 1e-6
            ):
                layout.overflow = True
            layout.placements.append(
                CompartmentPlacement(
                    label=label,
                    size=(comp_w, comp_l),
                    depth=comp_depth,
                    position=(interior.origin_x + pos[0], interior.origin_y + pos[1]),
                    shape_file=shape_file,
                    elements=elements or (),
                )
            )
            manual_boxes.append((pos[0], pos[1], comp_w, comp_l))
        else:
            auto_comps.append(comp)

    if not auto_comps:
        return layout

    # Only drop wall_spacing when there is a single compartment in the entire box
    effective_spacing = 0.0 if (len(comps) == 1 and not manual_boxes) else wall_spacing

    if not manual_boxes:
        shelf_placements, shelf_overflow = _pack_shelf_2d(
            interior, auto_comps, effective_spacing, no_rotate_labels, preserve_order
        )
        if not shelf_overflow:
            layout.placements.extend(shelf_placements)
            return layout

    mr_placements, mr_overflow = _pack_maxrects_2d(
        interior,
        auto_comps,
        manual_boxes,
        effective_spacing,
        no_rotate_labels,
        preserve_order,
    )
    layout.placements.extend(mr_placements)
    if mr_overflow:
        layout.overflow = True
    return layout


def _measure_layout_for_width(
    compartments: list[tuple[str, float, float, float]],
    target_inner_w: float,
    target_inner_l: float,
    no_rotate_labels: set[str],
    outer_sizer: OuterSizerFn,
) -> tuple[float, float, float] | None:
    """Lay out ``compartments`` within ``(target_inner_w, target_inner_l)`` and measure outer size."""
    max_d = max(d for _, _, _, d in compartments)
    interior = Interior(
        width=target_inner_w,
        length=target_inner_l,
        origin_x=0.0,
        origin_y=0.0,
        height=max_d + 1.0,
    )
    layout = layout_compartments(interior, compartments, no_rotate_labels=no_rotate_labels)
    if layout.overflow or not layout.placements:
        return None
    gutter = 0.0 if len(layout.placements) == 1 else WALL_SPACING_MM
    used_w = max(p.position[0] + p.size[0] for p in layout.placements) + gutter
    used_l = max(p.position[1] + p.size[1] for p in layout.placements) + gutter
    used_d = max(p.depth for p in layout.placements)
    return outer_sizer(used_w, used_l, used_d)


def candidate_box_sizes(
    compartments: list[tuple[str, float, float, float]],
    wall_thickness: float = 2.0,
    floor_thickness: float = 1.6,
    lid_thickness: float = 2.0,
    max_w: float | None = None,
    max_l: float | None = None,
    *,
    no_rotate_labels: set[str] | None = None,
    outer_sizer: OuterSizerFn | None = None,
) -> list[tuple[float, float, float]]:
    """Generate Pareto-non-dominated outer ``(W, L, H)`` envelopes for ``compartments``.

    Sweeps distinct row-wrap width targets (1-column, near-square, 2-row, 1-row)
    so an unsized multi-compartment box offers compact and elongated variants to
    the 3D game-box packer rather than only a single greedy full-width strip.
    """
    sizer: OuterSizerFn = outer_sizer or (
        lambda iw, il, ih: (
            iw + 2.0 * wall_thickness + 0.5,
            il + 2.0 * wall_thickness + 0.5,
            ih + floor_thickness + lid_thickness + 0.5,
        )
    )
    if not compartments:
        return [sizer(2.0 * wall_thickness - 0.5, 2.0 * wall_thickness - 0.5, 0.0)]

    no_rot = no_rotate_labels or set()
    gutter = 0.0 if len(compartments) == 1 else WALL_SPACING_MM

    min_item_w = max(
        (w if lbl in no_rot else min(w, l)) for lbl, w, l, _ in compartments
    )
    sum_w = sum(max(w, l) + gutter for _, w, l, _ in compartments) + gutter
    total_area = sum((w + gutter) * (l + gutter) for _, w, l, _ in compartments)
    sqrt_w = math.sqrt(total_area)

    bound_w = max_w if max_w is not None else sum_w + 10.0
    bound_l = max_l if max_l is not None else sum_w + 10.0

    probe_widths = sorted({
        round(v, 2)
        for v in (
            min_item_w + 2.0 * gutter,
            sqrt_w * 0.85,
            sqrt_w,
            sqrt_w * 1.25,
            sum_w * 0.55,
            sum_w,
            bound_w,
        )
        if min_item_w + 2.0 * gutter - 1e-6 <= v <= bound_w + 1e-6
    })
    if bound_w not in probe_widths and bound_w > 0:
        probe_widths.append(bound_w)

    raw_candidates: list[tuple[float, float, float]] = []
    for pw in probe_widths:
        measured = _measure_layout_for_width(compartments, pw, bound_l, no_rot, sizer)
        if measured is not None:
            raw_candidates.append(measured)

    # Also test rotated container bounds when max_w != max_l so rotatable boxes can fit sideways
    if max_w is not None and max_l is not None and abs(max_w - max_l) > 1e-3:
        measured_rot = _measure_layout_for_width(compartments, max_l, max_w, no_rot, sizer)
        if measured_rot is not None:
            raw_candidates.append(measured_rot)

    if not raw_candidates:
        # Unbounded fallback when compartments exceed (max_w, max_l)
        fallback = _measure_layout_for_width(
            compartments, max(sqrt_w, min_item_w + 2.0 * gutter), sum_w * 2.0 + 20.0, no_rot, sizer
        )
        if fallback is not None:
            return [fallback]

    # Deduplicate and keep Pareto frontier (no candidate strictly >= another on both W and L)
    unique: list[tuple[float, float, float]] = []
    for c in raw_candidates:
        rc = (round(c[0], 3), round(c[1], 3), round(c[2], 3))
        if not any(
            abs(rc[0] - u[0]) < 0.05 and abs(rc[1] - u[1]) < 0.05 and abs(rc[2] - u[2]) < 0.05
            for u in unique
        ):
            unique.append(c)

    pareto: list[tuple[float, float, float]] = []
    for i, a in enumerate(unique):
        dominated = any(
            j != i
            and b[0] <= a[0] + 1e-5
            and b[1] <= a[1] + 1e-5
            and b[2] <= a[2] + 1e-5
            and (b[0] < a[0] - 1e-4 or b[1] < a[1] - 1e-4)
            for j, b in enumerate(unique)
        )
        if not dominated:
            pareto.append(a)

    # Order most compact volume + balanced aspect ratio first
    pareto.sort(key=lambda s: (round(s[0] * s[1] * s[2], 2), abs(s[0] - s[1])))
    return pareto


def compute_min_box_size(
    compartments: list[tuple[str, float, float, float]],
    wall_thickness: float = 2.0,
    floor_thickness: float = 1.6,
    lid_thickness: float = 2.0,
    max_w: float | None = None,
    max_l: float | None = None,
    *,
    no_rotate_labels: set[str] | None = None,
    outer_sizer: OuterSizerFn | None = None,
) -> tuple[float, float, float]:
    """Return the smallest compact box that holds these compartments.

    Includes layout gutters around compartments, respects ``no_rotate_labels``
    (preventing card compartments from being rotated during sizing), and delegates
    wall/sleeve/hinge/lid envelope offsets to ``outer_sizer`` when given.
    """
    if not compartments:
        if outer_sizer is not None:
            return outer_sizer(2.0 * wall_thickness - 0.5, 2.0 * wall_thickness - 0.5, 0.0)
        return (
            wall_thickness * 4,
            wall_thickness * 4,
            floor_thickness + lid_thickness + 0.5,
        )

    candidates = candidate_box_sizes(
        compartments,
        wall_thickness=wall_thickness,
        floor_thickness=floor_thickness,
        lid_thickness=lid_thickness,
        max_w=max_w,
        max_l=max_l,
        no_rotate_labels=no_rotate_labels,
        outer_sizer=outer_sizer,
    )
    if candidates:
        return candidates[0]

    # Fallback square-target estimate when even unbounded MaxRects had no candidates
    sizer: OuterSizerFn = outer_sizer or (
        lambda iw, il, ih: (
            iw + 2.0 * wall_thickness + 0.5,
            il + 2.0 * wall_thickness + 0.5,
            ih + floor_thickness + lid_thickness + 0.5,
        )
    )
    max_w_comp = max(w for _, w, _, _ in compartments)
    max_l_comp = max(l for _, _, l, _ in compartments)
    max_d_comp = max(d for _, _, _, d in compartments)
    spacing = 0.0 if len(compartments) == 1 else WALL_SPACING_MM
    total_area = sum((w + spacing) * (l + spacing) for _, w, l, _ in compartments)
    target_width = max(max_w_comp + spacing, math.sqrt(total_area))

    total_width = 0.0
    total_rows = 0.0
    current_width = spacing
    current_row_height = 0.0

    for _, comp_w, comp_l, _ in sorted(compartments, key=lambda x: x[1] * x[2], reverse=True):
        if current_width + comp_w > target_width and current_width > spacing:
            total_width = max(total_width, current_width)
            current_width = spacing
            total_rows += current_row_height + spacing
            current_row_height = 0.0
        current_width += comp_w + spacing
        current_row_height = max(current_row_height, comp_l)

    total_width = max(total_width, current_width)
    total_rows += current_row_height + spacing
    return sizer(max(total_width, max_w_comp), max(total_rows, max_l_comp), max_d_comp)


def pack_compartments_across_bins(
    compartments: list[tuple[str, float, float, float]],
    bin_sizes: list[tuple[float, float]],
    wall_spacing: float = WALL_SPACING_MM,
    no_rotate_labels: set[str] | None = None,
) -> list[list[tuple[str, float, float, float]]] | None:
    """Partition compartments across multiple bin interior footprints with symmetry-broken 2D packing."""
    sorted_items = sorted(compartments, key=lambda x: x[1] * x[2], reverse=True)
    bins_content: list[list[tuple[str, float, float, float]]] = [[] for _ in bin_sizes]
    bins_area: list[float] = [0.0 for _ in bin_sizes]
    no_rot = no_rotate_labels or set()

    def check_fit(bin_idx: int, candidate_list: list[tuple[str, float, float, float]]) -> bool:
        bin_w, bin_l = bin_sizes[bin_idx]
        interior = Interior(width=bin_w, length=bin_l, height=100.0)
        res = layout_compartments(
            interior, candidate_list, wall_spacing=wall_spacing, no_rotate_labels=no_rot
        )
        return not res.overflow

    steps = 0
    max_steps = 50_000

    def search(idx: int) -> list[list[tuple[str, float, float, float]]] | None:
        nonlocal steps
        steps += 1
        if steps > max_steps:
            return None

        if idx == len(sorted_items):
            return [list(b) for b in bins_content]

        item = sorted_items[idx]
        item_area = item[1] * item[2]
        tried_bin_states: set[tuple[float, float, tuple[tuple[float, float], ...]]] = set()

        for i, (bw, bl) in enumerate(bin_sizes):
            if bins_area[i] + item_area > bw * bl + 1e-5:
                continue
            state_sig = (
                round(bw, 3),
                round(bl, 3),
                tuple((round(c[1], 3), round(c[2], 3)) for c in bins_content[i]),
            )
            if state_sig in tried_bin_states:
                continue
            tried_bin_states.add(state_sig)

            bins_content[i].append(item)
            bins_area[i] += item_area
            if check_fit(i, bins_content[i]):
                res = search(idx + 1)
                if res is not None:
                    return res
            bins_area[i] -= item_area
            bins_content[i].pop()

        return None

    return search(0)
