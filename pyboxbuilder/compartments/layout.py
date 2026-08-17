# SPDX-License-Identifier: Apache-2.0
"""Compartment auto-layout — 2D shelf-based bin packing."""

from dataclasses import dataclass, field
from typing import Any, Sequence

from pyboxbuilder.box.interior import Interior

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


def normalise_compartments(
    compartments: Sequence[Sequence[Any]],
) -> list[CompartmentSpec]:
    """Pad every compartment tuple out to the full seven fields.

    Args:
        compartments: Tuples of four to seven fields, in `CompartmentSpec`
            order.

    Returns:
        The same compartments, all seven fields long.
    """
    padding: tuple[Any, ...] = (None, None, ())
    return [
        (tuple(c) + padding[len(c) - 4:]) if len(c) < 7 else tuple(c)
        for c in compartments
    ]

WALL_SPACING_MM = 2.0
"""Wall left between adjacent compartments, and between one and the box wall.

Declared here because two things have to agree on it: the layout that inserts
the gutters, and the ratio sizing that has to leave room for them.
"""


@dataclass
class CompartmentPlacement:
    """Position of a single compartment inside a box."""

    label: str
    size: tuple[float, float]
    depth: float
    position: tuple[float, float]  # (x, y) in interior frame
    shape_file: str | None = None
    elements: tuple = ()


@dataclass
class CompartmentLayout:
    """Result of laying out compartments inside a box interior."""

    placements: list[CompartmentPlacement] = field(default_factory=list)
    overflow: bool = False

    def all_compartment_sizes(self) -> list[tuple[float, float]]:
        """Return (width, length) for each placement."""
        return [p.size for p in self.placements]


def layout_compartments(
    interior: Interior,
    compartments: Sequence[Sequence[Any]],
    wall_spacing: float = WALL_SPACING_MM,
    no_rotate_labels: set[str] | None = None,
) -> CompartmentLayout:
    """Row-based layout of compartments inside the box interior with 90-degree rotation support.

    Handles manual coordinates if position is specified in the compartment tuple.
    """
    comps = normalise_compartments(compartments)

    layout = CompartmentLayout()
    if not comps:
        return layout

    no_rotate_labels = no_rotate_labels or set()

    interior_w = interior.width
    interior_l = interior.length

    # 1. Process manually placed compartments first
    auto_comps = []
    for comp in comps:
        label, comp_w, comp_l, comp_depth, shape_file, pos, elements = comp
        if pos is not None:
            # Validate fit
            if pos[0] + comp_w > interior_w or pos[1] + comp_l > interior_l:
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
        else:
            auto_comps.append(comp)

    if not auto_comps:
        return layout

    # If there is only a single compartment, it should sit flush with the walls
    if len(auto_comps) == 1:
        wall_spacing = 0.0

    # Sort compartments by area descending to match the multi-bin solver
    sorted_comps = sorted(auto_comps, key=lambda c: c[1] * c[2], reverse=True)

    x_cursor = wall_spacing
    y_cursor = wall_spacing
    current_row_height = 0.0

    for label, comp_w, comp_l, comp_depth, shape_file, _, elements in sorted_comps:
        can_rotate = label not in no_rotate_labels
        # Check both normal and rotated orientations
        fits_normal = (
            (x_cursor + comp_w + wall_spacing <= interior_w)
            and (y_cursor + comp_l + wall_spacing <= interior_l)
        )
        fits_rotated = (
            can_rotate
            and (x_cursor + comp_l + wall_spacing <= interior_w)
            and (y_cursor + comp_w + wall_spacing <= interior_l)
        )

        w, l = comp_w, comp_l
        if fits_normal or fits_rotated:
            if fits_normal and fits_rotated:
                # Both fit: rotate portrait items to landscape to keep rows short
                if comp_l > comp_w:
                    w, l = comp_l, comp_w
            elif fits_rotated:
                w, l = comp_l, comp_w
        else:
            # Wrap to a new row
            x_cursor = wall_spacing
            y_cursor += current_row_height + wall_spacing
            current_row_height = 0.0

            # Re-evaluate fit in new row
            fits_normal_new = (
                (x_cursor + comp_w + wall_spacing <= interior_w)
                and (y_cursor + comp_l + wall_spacing <= interior_l)
            )
            fits_rotated_new = (
                can_rotate
                and (x_cursor + comp_l + wall_spacing <= interior_w)
                and (y_cursor + comp_w + wall_spacing <= interior_l)
            )

            if fits_normal_new or fits_rotated_new:
                if fits_normal_new and fits_rotated_new:
                    if comp_l > comp_w:
                        w, l = comp_l, comp_w
                elif fits_rotated_new:
                    w, l = comp_l, comp_w
            else:
                layout.overflow = True
                break

        if w > interior_w or l > interior_l:
            layout.overflow = True
            break

        layout.placements.append(
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

    return layout


def compute_min_box_size(
    compartments: list[tuple[str, float, float, float]],
    wall_thickness: float = 2.0,
    floor_thickness: float = 1.6,
    lid_thickness: float = 2.0,
    max_w: float | None = None,
    max_l: float | None = None,
) -> tuple[float, float, float]:
    """The smallest box that holds these compartments.

    With `max_w`/`max_l` given, lays the compartments out and measures the
    result; otherwise estimates a square footprint.

    The measurement **includes the gutters the layout puts around them**. It
    used to measure only the placements' own extent, so the size it returned was
    one gutter short on each axis — and a box sized from its compartments then
    failed to fit those same compartments, which is a confusing error to get
    from a box you never gave a size to.

    Args:
        compartments: `(label, width, length, depth)` per compartment.
        wall_thickness: The box's wall, in mm.
        floor_thickness: The box's floor, in mm.
        lid_thickness: The box's lid, in mm.
        max_w: Interior width available, if the box sits in a container.
        max_l: Interior length available.

    Returns:
        The box's outer `(width, length, height)` in mm.
    """
    if not compartments:
        return (
            wall_thickness * 4,
            wall_thickness * 4,
            floor_thickness + lid_thickness + 0.5,
        )

    # If max dimensions are provided, try laying out the compartments
    if max_w is not None and max_l is not None:
        try:
            interior = Interior(
                width=max_w,
                length=max_l,
                origin_x=0.0,
                origin_y=0.0,
                height=max(d for _, _, _, d in compartments) + 1.0,
            )
            layout = layout_compartments(interior, compartments)
            if not layout.overflow and layout.placements:
                # From the interior's own origin, not from the first placement:
                # the gutter before it is part of what the box has to hold, and
                # so is the one after the last.
                gutter = 0.0 if len(layout.placements) == 1 else WALL_SPACING_MM
                min_x = min_y = 0.0
                max_x = max(p.position[0] + p.size[0] for p in layout.placements) + gutter
                max_y = max(p.position[1] + p.size[1] for p in layout.placements) + gutter
                w = (max_x - min_x) + 2 * wall_thickness + 0.5
                l = (max_y - min_y) + 2 * wall_thickness + 0.5
                h = max(p.depth for p in layout.placements) + floor_thickness + lid_thickness + 0.5
                return (w, l, h)
        except Exception:
            pass

    # Fallback to estimating a square layout
    max_w_comp = max(w for _, w, _, _ in compartments)
    max_l_comp = max(l for _, _, l, _ in compartments)
    max_d_comp = max(d for _, _, _, d in compartments)
    spacing = 2.0

    import math
    total_area = sum((w + spacing) * (l + spacing) for _, w, l, _ in compartments)
    target_width = max(max_w_comp + spacing, math.sqrt(total_area))

    total_width = 0.0
    total_rows = 0.0
    current_width = spacing
    current_row_height = 0.0

    sorted_items = sorted(compartments, key=lambda x: x[1]*x[2], reverse=True)
    for _, comp_w, comp_l, _ in sorted_items:
        if current_width + comp_w > target_width:
            total_width = max(total_width, current_width)
            current_width = spacing
            total_rows += current_row_height + spacing
            current_row_height = 0.0
        current_width += comp_w + spacing
        current_row_height = max(current_row_height, comp_l)

    total_width = max(total_width, current_width)
    total_rows += current_row_height + spacing

    box_w = max(total_width, max_w_comp) + 2 * wall_thickness + 0.5
    box_l = max(total_rows, max_l_comp) + 2 * wall_thickness + 0.5
    box_h = max_d_comp + floor_thickness + lid_thickness + 0.5

    return (box_w, box_l, box_h)


def pack_compartments_across_bins(
    compartments: list[tuple[str, float, float, float]],
    bin_sizes: list[tuple[float, float]],
    wall_spacing: float = WALL_SPACING_MM,
) -> list[list[tuple[str, float, float, float]]] | None:
    """Partitions compartments across multiple bin interior footprints using backtracking shelf packing.

    Args:
        compartments: List of (label, width, length, depth) tuples.
        bin_sizes: List of (width, length) representing available bin footprints.
        wall_spacing: Gap between compartments.

    Returns:
        A list of lists containing the partitioned compartments for each bin,
        or None if they cannot be successfully packed.
    """
    sorted_items = sorted(compartments, key=lambda x: x[1] * x[2], reverse=True)
    bins_content: list[list[Any]] = [[] for _ in bin_sizes]

    def check_fit(bin_idx: int, candidate_list: list) -> bool:
        bin_w, bin_l = bin_sizes[bin_idx]
        local_wall_spacing = 0.0 if len(candidate_list) == 1 else wall_spacing
        x_cursor = local_wall_spacing
        y_cursor = local_wall_spacing
        current_row_height = 0.0

        for _, comp_w, comp_l, _ in candidate_list:
            fits_normal = (
                (x_cursor + comp_w + local_wall_spacing <= bin_w)
                and (y_cursor + comp_l + local_wall_spacing <= bin_l)
            )
            fits_rotated = (
                (x_cursor + comp_l + local_wall_spacing <= bin_w)
                and (y_cursor + comp_w + local_wall_spacing <= bin_l)
            )

            w, l = comp_w, comp_l
            if fits_normal or fits_rotated:
                if fits_normal and fits_rotated:
                    if comp_l > comp_w:
                        w, l = comp_l, comp_w
                elif fits_rotated:
                    w, l = comp_l, comp_w
            else:
                x_cursor = local_wall_spacing
                y_cursor += current_row_height + local_wall_spacing
                current_row_height = 0.0

                fits_normal_new = (
                    (x_cursor + comp_w + local_wall_spacing <= bin_w)
                    and (y_cursor + comp_l + local_wall_spacing <= bin_l)
                )
                fits_rotated_new = (
                    (x_cursor + comp_l + local_wall_spacing <= bin_w)
                    and (y_cursor + comp_w + local_wall_spacing <= bin_l)
                )

                if fits_normal_new or fits_rotated_new:
                    if fits_normal_new and fits_rotated_new:
                        if comp_l > comp_w:
                            w, l = comp_l, comp_w
                    elif fits_rotated_new:
                        w, l = comp_l, comp_w
                else:
                    return False

            x_cursor += w + local_wall_spacing
            current_row_height = max(current_row_height, l)

        return True

    steps = 0
    max_steps = 100000

    def search(idx: int) -> list | None:
        nonlocal steps
        steps += 1
        if steps > max_steps:
            return None

        if idx == len(sorted_items):
            return [list(b) for b in bins_content]

        item = sorted_items[idx]
        for i in range(len(bin_sizes)):
            bins_content[i].append(item)
            if check_fit(i, bins_content[i]):
                res = search(idx + 1)
                if res is not None:
                    return res
            bins_content[i].pop()

        return None

    return search(0)
