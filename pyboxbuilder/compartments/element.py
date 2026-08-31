# SPDX-License-Identifier: Apache-2.0
"""Compartment elements — individual game components nested inside a compartment.

A `CompartmentElement` is one physical piece (a worker meeple, a hero standee, a
hex tile, a wooden marker) with its own silhouette, its own local (x, y) offset
inside the owning compartment, its own rotation and its own depth. A compartment
that carries elements is an *element pack*: the elements are positioned in a local
frame and the pack's bounding box is what the box-level layout engine sees, so the
pack behaves exactly like one ordinary rectangular compartment (FR-004b).

Geometry generation delegates to pybosl2 and is only imported when a cutout is
actually built, so the layout maths stays importable without PythonSCAD.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any

from pyboxbuilder.enums import ElementShape
from pyboxbuilder.precision import kwargs as precision_kwargs
from pyboxbuilder.rounding import vertical_edges

if TYPE_CHECKING:
    from pybosl2 import Color, Region
    from pybosl2.shapes3d import Bosl2Solid


@dataclass(frozen=True)
class CompartmentElement:
    """A physical game component nested inside a compartment's bounding box."""

    shape_file: str | None = None
    """Path to the SVG outline representing the component (ElementShape.SVG only)."""
    offset: tuple[float, float] = (0.0, 0.0)
    """2D offset (x, y) in mm of the element's lower-left corner, relative to the
    compartment's bottom-left origin."""
    rotation: float = 0.0
    """Rotation of the component in degrees, about the centre of its footprint."""
    size: tuple[float, float] | None = None
    """Bounding dimensions (width, length) of the component in mm."""
    shape: ElementShape = ElementShape.SVG
    """Silhouette kind. Defaults to SVG, which requires `shape_file`."""
    depth: float | None = None
    """Cutout depth in mm. None inherits the owning compartment's depth."""
    z_offset: float | None = None
    """Extra lift of the cutout floor above the compartment floor, in mm.
    If None, the pocket automatically aligns flush with the top of the box.
    Used for pieces that sit on top of other pieces (e.g. a tile over a token)."""
    corner_radius: float = 2.0
    """Corner radius for ElementShape.ROUNDED_RECT."""
    corner_rounding: float = 0.5
    """Corner rounding radius for ElementShape.RECT (default 0.5mm, 0 for sharp)."""
    bottom_rounding: float = 0.0
    """Bottom corner fillet radius in mm."""
    label: str | None = None
    """Optional identifier, handy for tests and layout diagnostics."""
    pull_out: bool = True
    """Cut a finger pull-out over this slot so the piece can be lifted out.

    A silhouette slot holds its piece snugly by design — that is the point of
    cutting to the outline — which also means there is nowhere to get a
    fingertip. The pull-out is a dish across the slot, curved in from the
    surrounding floor so a finger slides down it and under the piece.
    """
    pull_out_depth: float | None = None
    """How deep the pull-out dish goes below the slot's own floor.

    ``None`` takes **half the piece's depth**, which is enough to get under a
    piece without letting it drop into the dish and sit crooked.
    """
    pull_out_width: float | None = None
    """Width of the pull-out across the slot. ``None`` uses a fingertip width."""
    color: str | None = None
    """When set, this element is a **positive coloured insert** — a thin icon
    pressed into the bottom of its well — instead of a cutout. The value is a
    web colour name, applied as the insert's own material in mmu mode."""

    def __post_init__(self) -> None:
        """Validate the element's shape and size."""
        if self.shape is ElementShape.SVG and not self.shape_file:
            raise ValueError(
                "CompartmentElement with shape=SVG requires shape_file="
            )
        if self.size is None:
            raise ValueError(
                f"CompartmentElement {self.label or self.shape_file!r} requires size=(w, l)"
            )
        if self.size[0] <= 0 or self.size[1] <= 0:
            raise ValueError(
                f"CompartmentElement {self.label or self.shape_file!r} size must be positive"
            )

    # ---------------------------------------------------------------- geometry

    @property
    def base_footprint(self) -> tuple[float, float]:
        """Axis-aligned (width, length) of the silhouette before rotation.

        For most shapes this is just `size`. A hexagon is the exception: `size[0]`
        is its flat-to-flat width, exactly as `RegularPolygon(width=...)` reads it
        in the original toolkit, so it measures `width / cos(30°)` point-to-point
        across the other axis.
        """
        assert self.size is not None
        w, l = self.size
        if self.shape is ElementShape.HEXAGON:
            return (w / math.cos(math.radians(30)), w)
        if self.shape in (ElementShape.CIRCLE, ElementShape.SPHERE_SCOOP):
            d = min(w, l)
            return (d, d)
        return (w, l)

    @property
    def footprint(self) -> tuple[float, float]:
        """Axis-aligned (width, length) after `rotation` is applied."""
        if self.shape in (ElementShape.CIRCLE, ElementShape.SPHERE_SCOOP):
            return self.base_footprint  # rotating a disc changes nothing
        if self.shape is ElementShape.HEXAGON:
            return _hexagon_footprint(self.base_footprint[0] / 2, self.rotation)

        w, l = self.base_footprint
        rad = math.radians(self.rotation)
        cos_r, sin_r = abs(math.cos(rad)), abs(math.sin(rad))
        return (w * cos_r + l * sin_r, w * sin_r + l * cos_r)

    def bounds(self) -> tuple[float, float, float, float]:
        """Axis-aligned bounds (min_x, min_y, max_x, max_y) in the pack frame."""
        fw, fl = self.footprint
        return (
            self.offset[0],
            self.offset[1],
            self.offset[0] + fw,
            self.offset[1] + fl,
        )

    def translated(self, dx: float, dy: float) -> CompartmentElement:
        """Return a copy shifted by (dx, dy) in the pack frame."""
        return replace(self, offset=(self.offset[0] + dx, self.offset[1] + dy))


def _hexagon_footprint(circumradius: float, rotation: float) -> tuple[float, float]:
    """Exact axis-aligned extent of a regular hexagon rotated by `rotation`.

    A rect-bbox approximation overshoots badly here — at 30 degrees it claims
    36% more width than the hexagon actually occupies.
    """
    angles = [math.radians(rotation + 60 * k) for k in range(6)]
    xs = [circumradius * math.cos(a) for a in angles]
    ys = [circumradius * math.sin(a) for a in angles]
    return (max(xs) - min(xs), max(ys) - min(ys))


def elements_bounding_box(
    elements: Sequence[CompartmentElement],
) -> tuple[float, float, float, float]:
    """Return (min_x, min_y, max_x, max_y) covering every element in the pack."""
    if not elements:
        return (0.0, 0.0, 0.0, 0.0)
    boxes = [e.bounds() for e in elements]
    return (
        min(b[0] for b in boxes),
        min(b[1] for b in boxes),
        max(b[2] for b in boxes),
        max(b[3] for b in boxes),
    )


def elements_footprint(
    elements: Sequence[CompartmentElement], margin: float = 0.0
) -> tuple[float, float]:
    """Size of the rectangular compartment that holds this element pack (FR-004b).

    Offsets are measured from the compartment's own lower-left corner, so the
    footprint spans from that corner out to the furthest element — authored
    offsets are preserved rather than collapsed against the origin. Use
    `normalize_elements` first if you want the pack shrink-wrapped instead.

    Args:
        elements: The elements in the pack, positioned in the compartment frame.
        margin: Extra clearance added past the furthest element, in mm.

    Returns:
        (width, length) of the compartment needed to hold the pack, in mm.

    """
    if not elements:
        return (0.0, 0.0)
    _, _, max_x, max_y = elements_bounding_box(elements)
    return (round(max_x + margin, 1), round(max_y + margin, 1))


def normalize_elements(
    elements: Sequence[CompartmentElement], margin: float = 0.0
) -> tuple[CompartmentElement, ...]:
    """Shift a pack so its bounding box starts at (margin, margin).

    Keeps hand-written offsets readable — you can lay elements out in whatever
    coordinates suit the source drawing and let the pack normalise itself.
    """
    min_x, min_y, _, _ = elements_bounding_box(elements)
    dx, dy = margin - min_x, margin - min_y
    return tuple(e.translated(dx, dy) for e in elements)


def grid_pack(
    prototype: CompartmentElement,
    count: int,
    *,
    origin: tuple[float, float] = (0.0, 0.0),
    pitch: tuple[float, float] = (0.0, 0.0),
    alternate_rotation: float = 0.0,
) -> tuple[CompartmentElement, ...]:
    """Repeat one element `count` times along a straight line (FR-004b).

    This is the "five owl workers stacked in a column" case: the same silhouette
    at a fixed pitch, optionally flipping every other copy so the pieces nest.

    Args:
        prototype: The element to repeat; its `offset` is ignored.
        count: How many copies to place.
        origin: Position of the first copy.
        pitch: (dx, dy) step between successive copies.
        alternate_rotation: Extra rotation applied to every odd-indexed copy.

    Returns:
        The placed copies, in order.

    """
    out = []
    for i in range(count):
        rotation = prototype.rotation + (alternate_rotation if i % 2 else 0.0)
        out.append(
            replace(
                prototype,
                offset=(origin[0] + pitch[0] * i, origin[1] + pitch[1] * i),
                rotation=rotation,
                label=f"{prototype.label}_{i}" if prototype.label else None,
            )
        )
    return tuple(out)


def elements_overlap(
    elements: Sequence[CompartmentElement], tolerance: float = 0.0
) -> list[tuple[str, str]]:
    """Return the pairs of elements whose bounding boxes intersect.

    Bounding-box based, matching how the layout engine reasons about
    non-rectangular shapes (FR-004a). `tolerance` shrinks each box before the
    test, so silhouettes that only graze one another are not reported.
    """
    hits: list[tuple[str, str]] = []
    for i, a in enumerate(elements):
        ax0, ay0, ax1, ay1 = a.bounds()
        for b in elements[i + 1 :]:
            bx0, by0, bx1, by1 = b.bounds()
            if (
                ax0 + tolerance < bx1
                and bx0 + tolerance < ax1
                and ay0 + tolerance < by1
                and by0 + tolerance < ay1
            ):
                hits.append((_name(a), _name(b)))
    return hits


def _name(element: CompartmentElement) -> str:
    return element.label or element.shape_file or element.shape.value


# ------------------------------------------------------------------ geometry


def build_element(
    element: CompartmentElement, default_depth: float
) -> Bosl2Solid:
    """Build the cutout solid for one element, in the compartment's local frame.

    pybosl2 primitives are centre-anchored, so each branch below builds its shape
    around the origin, rotation spins it in place, and one final translate puts
    the element's lower-left corner on its `offset` with its floor at
    `z_offset`. The result can be subtracted from a box body once the compartment
    has been moved into the interior frame.
    """
    from pybosl2 import cuboid, cylinder, regular_prism, sphere

    assert element.size is not None
    w, l = element.size
    depth = element.depth if element.depth is not None else default_depth
    actual_z_offset = element.z_offset if element.z_offset is not None else (default_depth - depth)
    base_w, _ = element.base_footprint

    # A scoop is a ball resting ON the floor, not a well sunk into it, so it
    # lifts by its radius while every other shape lifts by half its depth.
    z_lift = base_w / 2 if element.shape is ElementShape.SPHERE_SCOOP else depth / 2

    if element.shape is ElementShape.SVG:
        assert element.shape_file is not None
        solid = svg_solid(element.shape_file, w, l, depth)
    elif element.shape is ElementShape.TEXT:
        from pybosl2.shapes2d.ops import text
        assert element.shape_file is not None
        font_size = min(w / len(element.shape_file) * 1.5, l * 0.7)
        solid = text(
            element.shape_file,
            font="Liberation Sans:style=Bold",
            size=font_size,
            halign="center",
            valign="center"
        ).linear_extrude(height=depth)
    elif element.shape is ElementShape.CIRCLE:
        if element.bottom_rounding > 0:
            solid = cylinder(
                height=depth, radius=base_w / 2, rounding1=element.bottom_rounding,
                **precision_kwargs()
            )
        else:
            solid = cylinder(height=depth, radius=base_w / 2, **precision_kwargs())
    elif element.shape is ElementShape.HEXAGON:
        # `w` is the flat-to-flat width, as `RegularPolygon(width=...)` reads it.
        solid = regular_prism(
            6, height=depth, radius=w / 2 / math.cos(math.radians(30))
        )
    elif element.shape is ElementShape.SPHERE_SCOOP:
        solid = sphere(radius=base_w / 2, **precision_kwargs())
    elif element.shape is ElementShape.ROUNDED_RECT:
        solid = cuboid([w, l, depth], rounding=element.corner_radius, edges=vertical_edges(),
                       **precision_kwargs())
        if element.bottom_rounding > 0:
            from pybosl2 import Anchor

            from pyboxbuilder.rounding import round_edges
            solid = round_edges(
                solid, [w, l, depth], element.bottom_rounding, [Anchor.BOTTOM],
                at=(-w / 2, -l / 2, -depth / 2),
            )
    else:
        if element.corner_rounding > 0:
            solid = cuboid([w, l, depth], rounding=element.corner_rounding, edges=vertical_edges(),
                           **precision_kwargs())
        else:
            solid = cuboid([w, l, depth])
        if element.bottom_rounding > 0:
            from pybosl2 import Anchor

            from pyboxbuilder.rounding import round_edges
            solid = round_edges(
                solid, [w, l, depth], element.bottom_rounding, [Anchor.BOTTOM],
                at=(-w / 2, -l / 2, -depth / 2),
            )

    if element.rotation:
        solid = solid.rotate([0.0, 0.0, element.rotation])

    footprint_w, footprint_l = element.footprint
    return solid.translate([
        element.offset[0] + footprint_w / 2,
        element.offset[1] + footprint_l / 2,
        actual_z_offset + z_lift,
    ])


def svg_solid(shape_file: str, width: float, length: float, depth: float) -> Bosl2Solid:
    """Extrude an SVG outline and scale it to fill `width` x `length` x `depth`.

    Returned centred on the origin, matching every pybosl2 primitive, so callers
    can place it the same way they place a cuboid.
    """
    solid = _svg_region(shape_file).linear_extrude(height=depth)
    (cx, cy, cz), (span_x, span_y, _) = solid.bounds()
    solid = solid.translate([-float(cx), -float(cy), -float(cz)])
    return solid.scale([
        width / max(float(span_x), 1e-9),
        length / max(float(span_y), 1e-9),
        1.0,
    ])


def _svg_region(shape_file: str) -> Region:
    """Parse an SVG once and reuse it — a pack repeats the same file many times.

    ``clip_to_viewbox=False`` is deliberate: pybosl2's default viewport clip
    flattens nested subpaths through a ``unary_union`` before clipping, which
    destroys the holes (windows, ring gaps) a silhouette draws with the
    even-odd rule. Box SVGs size their viewBox to the drawing, so skipping the
    clip loses nothing and keeps the cutouts.
    """
    from pathlib import Path
    from pybosl2.svg import region_from_svg

    region = _SVG_CACHE.get(shape_file)
    if region is None:
        path = Path(shape_file)
        if not path.is_absolute() and not path.exists():
            repo_root = Path(__file__).resolve().parents[2]
            resolved = repo_root / path
            if resolved.exists():
                path = resolved
        region = region_from_svg(str(path), clip_to_viewbox=False)
        _SVG_CACHE[shape_file] = region
    return region


_SVG_CACHE: dict[str, Region] = {}


PULL_OUT_DEPTH_SHARE = 0.5
"""How deep a pull-out goes, as a share of the piece's depth.

Half gets a fingertip under the piece while leaving the slot deep enough that
the piece still seats flat in it rather than tipping into the dish.
"""

DEFAULT_PULL_OUT_WIDTH_MM = 16.0
"""Fingertip width for a pull-out dish, when the element names none."""


def build_pull_out(
    element: CompartmentElement,
    default_depth: float,
    comp_size: tuple[float, float] = (1000.0, 1000.0),
    force_axis: str | None = None,
) -> Bosl2Solid | None:
    """Return the finger dish that lets a piece be lifted out of its slot.

    Cut across the slot and **curved in from the surrounding floor** on both
    sides, so a finger slides down into it rather than meeting a step. Without
    it a silhouette slot has no purchase at all: it fits the piece exactly,
    which is what makes it look right and what makes it impossible to empty.

    """
    if not element.pull_out:
        return None

    from pybosl2 import cuboid

    from pyboxbuilder.rounding import rounding_facets

    assert element.size is not None
    w, l = element.size
    width, length = (l, w) if abs(element.rotation) == 90 else (w, l)
    depth = element.depth or default_depth
    actual_z_offset = element.z_offset if element.z_offset is not None else (default_depth - depth)
    drop = depth * PULL_OUT_DEPTH_SHARE
    across = min(element.pull_out_width or DEFAULT_PULL_OUT_WIDTH_MM, max(width, length))

    # Calculate clearances to compartment boundaries to automatically pick the direction with most room
    comp_w, comp_l = comp_size
    clearance_x_left = element.offset[0]
    clearance_x_right = comp_w - (element.offset[0] + width)
    clearance_y_front = element.offset[1]
    clearance_y_back = comp_l - (element.offset[1] + length)

    clearance_x = min(clearance_x_left, clearance_x_right)
    clearance_y = min(clearance_y_front, clearance_y_back)

    use_y = force_axis == "y" if force_axis is not None else clearance_y >= clearance_x

    if use_y:
        # Orient along Y (lengthwise)
        drop_front = max(0.0, min(drop, clearance_y_front))
        drop_back = max(0.0, min(drop, clearance_y_back))
        actual_drop = max(0.1, max(drop_front, drop_back))
        radius = min(actual_drop, across / 2 - 0.01)
        centre_x = element.offset[0] + width / 2
        centre_y = element.offset[1] + length / 2 + (drop_back - drop_front) / 2
        z = actual_z_offset + depth - actual_drop

        from pybosl2 import Anchor
        dish_edges = [Anchor.BOTTOM_LEFT, Anchor.BOTTOM_RIGHT] + vertical_edges()
        total_len = length + drop_front + drop_back
        dish = cuboid(
            [across, total_len, actual_drop * 2],
            rounding=radius,
            edges=dish_edges,
            **rounding_facets(),
        ) if radius > 0 else cuboid([across, total_len, actual_drop * 2])
        dish = dish.translate([centre_x, centre_y, z])

        # Extend the pull-out upwards from its center to prevent top tapering, keeping the sides rounded
        block = cuboid(
            [across, total_len, 100.0],
            rounding=radius,
            edges=vertical_edges(),
            **rounding_facets(),
        ) if radius > 0 else cuboid([across, total_len, 100.0])
        block = block.translate([centre_x, centre_y, z + 50.0])
        return union_all([dish, block])
    else:
        # Orient along X (widthwise)
        drop_left = max(0.0, min(drop, clearance_x_left))
        drop_right = max(0.0, min(drop, clearance_x_right))
        actual_drop = max(0.1, max(drop_left, drop_right))
        radius = min(actual_drop, across / 2 - 0.01)
        centre_x = element.offset[0] + width / 2 + (drop_right - drop_left) / 2
        centre_y = element.offset[1] + length / 2
        z = actual_z_offset + depth - actual_drop

        from pybosl2 import Anchor
        dish_edges = [Anchor.BOTTOM_FRONT, Anchor.BOTTOM_BACK] + vertical_edges()
        total_w = width + drop_left + drop_right
        dish = cuboid(
            [total_w, across, actual_drop * 2],
            rounding=radius,
            edges=dish_edges,
            **rounding_facets(),
        ) if radius > 0 else cuboid([total_w, across, actual_drop * 2])
        dish = dish.translate([centre_x, centre_y, z])

        # Extend the pull-out upwards from its center to prevent top tapering, keeping the sides rounded
        block = cuboid(
            [total_w, across, 100.0],
            rounding=radius,
            edges=vertical_edges(),
            **rounding_facets(),
        ) if radius > 0 else cuboid([total_w, across, 100.0])
        block = block.translate([centre_x, centre_y, z + 50.0])
        return union_all([dish, block])


def build_element_pack(
    elements: Iterable[CompartmentElement], default_depth: float
) -> Bosl2Solid | None:
    """Union every element cutout in a pack. Returns None for an empty pack.

    A coloured element is carved *and* filled: it is included here so its
    silhouette is recessed into the well floor, and
    :func:`build_element_pack_inserts` supplies the coloured solid that fills
    that recess — together they make an inlay flush with the floor rather than
    a bump proud of it.
    """
    pieces = []
    for element in elements:
        pieces.append(build_element(element, default_depth))
    return union_all([p for p in pieces if p is not None])


def build_element_pack_inserts(
    elements: Iterable[CompartmentElement], default_depth: float
) -> list[tuple[Bosl2Solid, Color]]:
    """Build the coloured positive inserts of a pack, one per coloured element.

    Each insert is the element's own silhouette at its own depth and offset,
    returned uncoloured alongside its colour so the caller can print it as a
    separate material (mmu) or draw it in the right colour (preview). A pack
    with no coloured elements yields an empty list.
    """
    from pybosl2 import Color

    inserts: list[tuple[Bosl2Solid, Color]] = []
    for element in elements:
        if element.color is None:
            continue
        solid = build_element(element, default_depth)
        if solid is not None:
            inserts.append((solid, Color(element.color)))
    return inserts


def build_element_pack_pull_outs(
    elements: Iterable[CompartmentElement], default_depth: float, comp_size: tuple[float, float]
) -> Bosl2Solid | None:
    """Union every pull-out scoop in a pack, hulling overlapping scoops to avoid sharp edges."""
    elements_list = [el for el in elements if el.pull_out and el.color is None]
    if not elements_list:
        return None

    comp_w, comp_l = comp_size
    # Align all scoops in the compartment along the overall best axis.
    comp_w, comp_l = comp_size
    sum_clearance_x = 0.0
    sum_clearance_y = 0.0
    for element in elements_list:
        assert element.size is not None
        width, length = element.size
        sum_clearance_x += min(element.offset[0], comp_w - (element.offset[0] + width))
        sum_clearance_y += min(element.offset[1], comp_l - (element.offset[1] + length))

    use_y = sum_clearance_y >= sum_clearance_x

    # Map each element to its individual pull_out solid and its footprint bounds
    built_pieces = []
    for element in elements_list:
        solid = build_pull_out(element, default_depth, comp_size, force_axis="y" if use_y else "x")
        if solid is None:
            continue

        assert element.size is not None
        width, length = element.size
        depth = element.depth or default_depth
        drop = depth * PULL_OUT_DEPTH_SHARE

        if use_y:
            clearance_y_front = element.offset[1]
            clearance_y_back = comp_l - (element.offset[1] + length)
            drop_front = max(0.0, min(drop, clearance_y_front))
            drop_back = max(0.0, min(drop, clearance_y_back))

            min_x = element.offset[0]
            max_x = element.offset[0] + width
            min_y = element.offset[1] - drop_front
            max_y = element.offset[1] + length + drop_back
        else:
            clearance_x_left = element.offset[0]
            clearance_x_right = comp_w - (element.offset[0] + width)
            drop_left = max(0.0, min(drop, clearance_x_left))
            drop_right = max(0.0, min(drop, clearance_x_right))

            min_x = element.offset[0] - drop_left
            max_x = element.offset[0] + width + drop_right
            min_y = element.offset[1]
            max_y = element.offset[1] + length

        built_pieces.append({
            'solid': solid,
            'min_x': min_x, 'max_x': max_x,
            'min_y': min_y, 'max_y': max_y
        })

    # Group overlapping pieces
    groups: list[list[dict[str, Any]]] = []
    for p in built_pieces:
        matched_indices = []
        for idx, g in enumerate(groups):
            overlaps = False
            for other in g:
                tol = 0.5
                if use_y:
                    x_match = abs(p['min_x'] - other['min_x']) < 1.0 and abs(p['max_x'] - other['max_x']) < 1.0
                    y_overlap = p['min_y'] - tol < other['max_y'] and other['min_y'] - tol < p['max_y']
                    overlaps = x_match and y_overlap
                else:
                    y_match = abs(p['min_y'] - other['min_y']) < 1.0 and abs(p['max_y'] - other['max_y']) < 1.0
                    x_overlap = p['min_x'] - tol < other['max_x'] and other['min_x'] - tol < p['max_x']
                    overlaps = y_match and x_overlap
                if overlaps:
                    break
            if overlaps:
                matched_indices.append(idx)

        if not matched_indices:
            groups.append([p])
        else:
            new_group = [p]
            for idx in reversed(matched_indices):
                new_group.extend(groups.pop(idx))
            groups.append(new_group)

    # Hull overlapping groups, union non-overlapping ones
    final_solids = []
    from pybosl2._native import native
    from pybosl2.shapes3d.base import CsgSolid
    hull_fn = native("hull")

    for g in groups:
        if len(g) == 1:
            final_solids.append(g[0]['solid'])
        else:
            raw_shapes = [p['solid'].shape for p in g]
            final_solids.append(CsgSolid(hull_fn(raw_shapes)))

    return union_all([p for p in final_solids if p is not None])


def union_all(solids: list[Bosl2Solid]) -> Bosl2Solid | None:
    """Union a list of solids with a balanced fold.

    A left fold builds a chain as deep as the list, which the mesher pays for on
    every cell of a big pack; halving keeps the tree logarithmic.
    """
    if not solids:
        return None
    while len(solids) > 1:
        solids = [
            a | b if b is not None else a
            for a, b in zip(solids[::2], [*list(solids[1::2]), None], strict=False)
        ]
    return solids[0]


def centered(
    shape_file: str | None,
    center: tuple[float, float],
    size: tuple[float, float],
    *,
    shape: ElementShape = ElementShape.SVG,
    rotation: float = 0.0,
    label: str | None = None,
    pull_out: bool = True,
    **pocket_kwargs,
) -> CompartmentElement:
    """Return a CompartmentElement centered at the given coordinate."""
    from pyboxbuilder.enums import ElementShape

    if shape_file is None and shape == ElementShape.SVG:
        shape = ElementShape.RECT
    proto = CompartmentElement(
        shape_file=shape_file,
        offset=(0.0, 0.0),
        size=size,
        shape=shape,
        rotation=rotation,
        label=label,
        pull_out=pull_out,
        **pocket_kwargs,
    )
    fw, fl = proto.footprint
    return CompartmentElement(
        shape_file=shape_file,
        offset=(center[0] - fw / 2, center[1] - fl / 2),
        size=size,
        shape=shape,
        rotation=rotation,
        label=label,
        pull_out=pull_out,
        **pocket_kwargs,
    )


def centered_in_box(
    shape_file: str | None,
    box_size: tuple[float, float, float],
    element_size: tuple[float, float],
    wall_thickness: float = 2.0,
    **kwargs,
) -> CompartmentElement:
    """Return a CompartmentElement centered exactly in a box's interior frame."""
    interior_w = box_size[0] - 2 * wall_thickness
    interior_l = box_size[1] - 2 * wall_thickness
    return centered(
        shape_file, (interior_w / 2, interior_l / 2), element_size, **kwargs
    )
