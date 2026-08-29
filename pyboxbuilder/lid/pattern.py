# SPDX-License-Identifier: Apache-2.0
"""Lid through-hole patterns — the shapes a lid is perforated with (FR-023).

Each member of :class:`~pyboxbuilder.enums.PatternType` draws the shape it is
named after. That is worth stating because it was not true: the catalog listed
47 members and three shapes, with a `_shape_grid_fill` that took the shape's
name as an argument and ignored it, hexagons and triangles built from cuboids,
and every tessellation wrapped in `except (ImportError, ..., Exception)` around
an import of a package that is not in this repo — so a lid asking for LEAF, or
PENROSE_TILING_5, or any of the fifteen pentagon tilings, silently came out with
square holes.

A pattern that quietly becomes a different pattern is worse than one that is
missing: the user sees a plausible lid and never learns the request was
dropped. So the catalog here is exactly what is implemented, and a member is
added when the geometry to draw it is (FR-000c).
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING

from pyboxbuilder.enums import PatternType
from pyboxbuilder.precision import kwargs as precision_kwargs

if TYPE_CHECKING:
    from pybosl2.shapes2d.base import Bosl2Shape2D
    from pybosl2.shapes3d import Bosl2Solid

DEFAULT_WEB_MM = 1.6
"""Material left **between** neighbouring holes, when nothing else says.

The web is the thing to state, not the hole: it is what has to print and what
carries the lid, so it is the quantity with a right answer. Four extrusion
widths at a 0.4mm nozzle, which is stiff enough to handle a large lid by.

Sizing the hole as a *share of the cell* instead — the previous rule, 55% —
made the web scale with the pitch, so a lid asking for 11mm cells got 6.2mm
hexes separated by 5.1mm of plastic. That is not a honeycomb; it is a sheet
with holes in it, and it saves almost no filament (FR-023).
"""

MIN_WEB_MM = 0.8
"""Thinnest web worth printing — two perimeters at a 0.4mm nozzle."""

MIN_HOLE_MM = 2.0
"""Smallest hole worth cutting.

Below this the pattern reads as a rough surface rather than as openings, and a
lid whose pitch cannot hold it gets no pattern at all rather than a peppering
of pinholes.
"""

DENSE_SPACING_SHARE = 1.6
"""How much of the normal spacing a *dense* variant uses."""

DEPTH_OVERSHOOT = 1.2
"""How far a hole is over-extruded relative to the lid, so it breaks through."""


def hole_size(spacing: float, web: float | None) -> float:
    """Return how big a hole is, given the pitch and the web between them.

    Args:
        spacing: Centre-to-centre distance between neighbouring holes, in mm.
        web: Material to leave between them; ``None`` uses
            :data:`DEFAULT_WEB_MM`.

    Returns:
        The hole's size across the flats, in mm. Zero when the pitch cannot
        hold a usable hole and the thinnest printable web at once — the caller
        then leaves the lid solid rather than perforating it uselessly.

    """
    gap = DEFAULT_WEB_MM if web is None else max(web, MIN_WEB_MM)
    size = spacing - gap
    if size < MIN_HOLE_MM:
        # Try again at the thinnest web that still prints before giving up.
        size = spacing - MIN_WEB_MM
    return size if size >= MIN_HOLE_MM else 0.0

def default_spacing(width: float, length: float) -> float:
    """Return the cell size a pattern uses when the caller names none.

    Derived from the lid rather than fixed, so the same pattern reads the same
    on a 40mm token lid and a 200mm card lid (FR-000).

    Args:
        width: Lid width in mm.
        length: Lid length in mm.

    Returns:
        The spacing in mm — an eighth of the shorter side, never below 5mm.

    """
    return max(min(width, length) / 8.0, 5.0)


MIN_DERIVED_SPACING_MM = {
    PatternType.VORONOI: 8.0,
}
"""Patterns whose derived pitch needs a higher floor than the generic one.

:func:`default_spacing` is calibrated for a hole **inscribed** in its cell, which
is what most of the catalog cuts. A Voronoi cell *tiles*, so the cell is the
hole, and the web is taken out of a cell rather than out of the gap around one.
An eighth of a small lid's shorter side leaves a cell only a few times the web,
which prints and reads as a peppering of pinholes rather than as a pattern.

Only the derived pitch is floored. A caller who asks for 5mm cells gets 5mm
cells: a named option does what it says (FR-000g).
"""


def build_pattern(
    width: float,
    length: float,
    thickness: float,
    pattern_type: PatternType,
    spacing: float | None = None,
    web: float | None = None,
) -> Bosl2Solid | None:
    """Build the through-hole cutouts for a lid.

    Args:
        width: Width of the area to fill, in mm — the lid less its border.
        length: Length of that area, in mm.
        thickness: Lid thickness; the holes are cut deeper so they break through.
        pattern_type: Which pattern. ``PatternType.NONE`` returns ``None``.
        spacing: Centre-to-centre distance between holes. ``None`` derives it
            from the area (see :func:`default_spacing`).
        web: Material left between neighbouring holes. ``None`` uses
            :data:`DEFAULT_WEB_MM`. This, rather than the hole size, is what a
            pattern is really specified by: it is what prints.

    Returns:
        The solid to subtract from the lid, or ``None`` for no pattern, for an
        area too small to hold a whole hole, or for a pitch too tight to hold a
        hole and a printable web at once.

    Raises:
        ValueError: If the pattern has no fill registered — which cannot happen
            for a catalog member, and is the check that keeps it that way.

    """
    if spacing is None:
        spacing = max(
            default_spacing(width, length),
            MIN_DERIVED_SPACING_MM.get(pattern_type, 0.0),
        )

    fill = _PATTERN_FILLS.get(pattern_type)
    if fill is None:
        available = ", ".join(sorted(p.name for p in _PATTERN_FILLS))
        raise ValueError(
            f"No fill registered for PatternType.{pattern_type.name}. "
            f"Available: {available}"
        )
    return fill(width, length, thickness, spacing, web)


# ── Cell placement ────────────────────────────────────────────────────

def _grid_cells(
    width: float,
    length: float,
    spacing: float,
    stagger: bool = False,
    row_step: float | None = None,
) -> Iterator[tuple[float, float]]:
    """Centres of a lattice covering the whole area, overhanging every edge.

    The holes are **clipped to the area** by the caller, so the ones at the
    boundary come out as partial hexes and the pattern reaches the border
    exactly. Placing only whole holes instead — inset by a hole's reach — left
    up to a cell's worth of unused margin inside the border, so a lid asking
    for an 8mm border got 12mm or more of solid edge on two sides and the
    pattern looked as though it had shrunk away from it.

    **The lattice starts a full pitch before the area, not on it.** A staggered
    row is shifted half a pitch, so a lattice that began at the area's own edge
    began *inside* it on every other row: those rows left a strip of material
    along the leading edge while the trailing edge was covered twice over. One
    pitch of run-up is enough for any row's offset, whatever the stagger, and
    the extra holes cost nothing — they fall outside the area and are clipped
    away with the rest of the overhang.

    Args:
        width: Width of the area to fill, in mm.
        length: Its length, in mm.
        spacing: Centre-to-centre distance between holes.
        stagger: Offset alternate rows by half a cell, for a honeycomb.
        row_step: Distance between rows. ``None`` uses the pitch itself, or
            ``sin(60°)`` of it when staggered — right for a hexagon, whose
            neighbours are the same distance away in all six directions. A
            shape that is not as tall as it is wide states its own: a leaf's
            rows interleave, so its step is well under its width.

    Yields:
        ``(x, y)`` centres, in the area's own frame. Many lie outside it: that
        is what puts a partial hole against each edge.

    """
    if row_step is None:
        row_step = spacing * (0.866 if stagger else 1.0)  # sin(60°) for hex rows
    if spacing <= 0 or row_step <= 0:
        return

    # Anchor a hole on the area's centre and grow outwards, rather than
    # starting at one edge and running to the other. Growing from an edge
    # leaves the lattice wherever the arithmetic puts it: measured on a 96 x 70
    # lid, the right edge lost 56mm³ of material to the border strip and the
    # left only 33mm³, because one side was being cut through the hexes and the
    # other through the webs between them. Anchored at the centre the two sides
    # are mirror images, which is what makes the border look deliberate.
    #
    # One extra ring beyond each edge covers the half-pitch a staggered row is
    # shifted by; the overhang is clipped away with the rest.
    half_columns = math.ceil(width / (2 * spacing)) + 1
    half_rows = math.ceil(length / (2 * row_step)) + 1

    for row in range(-half_rows, half_rows + 1):
        y = length / 2.0 + row * row_step
        offset = spacing / 2.0 if stagger and row % 2 else 0.0
        for column in range(-half_columns, half_columns + 1):
            yield width / 2.0 + column * spacing + offset, y


def _punch(
    shape_at: Callable[[float, float], Bosl2Solid],
    width: float,
    length: float,
    spacing: float,
    hole: float,
    stagger: bool = False,
    row_step: float | None = None,
) -> Bosl2Solid | None:
    """Union one hole per cell.

    Measures the shape rather than assuming its extent: each fill draws a
    different polygon, at a different spin, and what decides whether a hole
    stays inside the border is how far it actually reaches.

    Args:
        shape_at: Called with ``(x, y)``; returns one hole solid in place.
        width: Width of the area to fill, in mm.
        length: Its length, in mm.
        spacing: Centre-to-centre distance between holes.
        hole: The hole's nominal size; ``0`` means none will fit.
        stagger: Offset alternate rows.
        row_step: Distance between rows; ``None`` derives it from the pitch.

    Returns:
        The union of every hole, or ``None`` when none fit.

    """
    if hole <= 0:
        return None

    holes = None
    for x, y in _grid_cells(width, length, spacing, stagger, row_step):
        cut = shape_at(x, y)
        holes = cut if holes is None else holes | cut
    return holes


def _prism(
    sides: int, across_flats: float, thickness: float, spin: float = 0.0
) -> Bosl2Solid:
    """One regular-polygon hole, tall enough to break through the lid."""
    from pybosl2 import regular_prism

    # `inner_radius` is the apothem, which is what sizes a hole: the web left
    # between neighbours is set by how wide the hole is across its flats, not
    # by how far its corners reach.
    return regular_prism(
        sides=sides,
        inner_radius=across_flats / 2.0,
        height=thickness * DEPTH_OVERSHOOT,
        spin=spin,
        **precision_kwargs(),
    )


# ── Fills ─────────────────────────────────────────────────────────────

def _square_fill(
    width: float, length: float, thickness: float, spacing: float,
    web: float | None = None,
) -> Bosl2Solid | None:
    """Square holes on a square grid."""
    from pybosl2 import cuboid

    size = hole_size(spacing, web)
    return _punch(
        lambda x, y: cuboid([size, size, thickness * DEPTH_OVERSHOOT]).translate(
            [x, y, thickness / 2]
        ),
        width, length, spacing, size,
    )


def _circle_fill(
    width: float, length: float, thickness: float, spacing: float,
    web: float | None = None,
) -> Bosl2Solid | None:
    """Round holes on a square grid."""
    from pybosl2 import cylinder

    size = hole_size(spacing, web)
    return _punch(
        lambda x, y: cylinder(
            height=thickness * DEPTH_OVERSHOOT,
            radius=size / 2,
            **precision_kwargs(),
        ).translate([x, y, thickness / 2]),
        width, length, spacing, size,
    )


POINTY_TOP_SPIN = 30.0
"""Rotation that stands a hexagon on a flat, with its flats left and right.

`regular_prism` draws a hexagon with a vertex to the right — flats top and
bottom — and the staggered lattice below needs the opposite: flats *left and
right*, so a row's neighbours sit across-flats from each other and the next row
nests into the notches between them. Without this the lattice was tiling one
orientation with the spacing of the other, which left the rows barely clearing
each other horizontally and floating apart vertically. It is not a honeycomb
until the hexagon and the lattice agree.
"""


def _hex_fill(
    width: float, length: float, thickness: float, spacing: float,
    web: float | None = None, dense: bool = False,
) -> Bosl2Solid | None:
    """Hexagonal holes in staggered rows — a true honeycomb.

    Every neighbour, in the row and in the rows either side, sits exactly one
    pitch away: the horizontal pitch is the hole's width plus the web, and the
    rows step ``sin(60°)`` of that while offsetting half a pitch. So the web is
    the same in all six directions, which is what makes it a honeycomb rather
    than rows of hexagons.
    """
    step = spacing * (DENSE_SPACING_SHARE if dense else 1.0)
    size = hole_size(step, web)
    return _punch(
        lambda x, y: _prism(6, size, thickness, POINTY_TOP_SPIN).translate(
            [x, y, thickness / 2]
        ),
        width, length, step, size, stagger=True,
    )


def _triangle_fill(
    width: float, length: float, thickness: float, spacing: float,
    web: float | None = None, dense: bool = False,
) -> Bosl2Solid | None:
    """Triangular holes, alternating point-up and point-down along each row."""
    step = spacing * (DENSE_SPACING_SHARE if dense else 1.0)
    size = hole_size(step, web)

    def shape(x: float, y: float) -> Bosl2Solid:
        # Alternating spin is what makes a triangle grid read as one, rather
        # than as rows of identical wedges.
        spin = 180.0 if round(x / step) % 2 else 0.0
        return _prism(3, size, thickness, spin).translate([x, y, thickness / 2])

    return _punch(shape, width, length, step, size)


def _octagon_fill(
    width: float, length: float, thickness: float, spacing: float,
    web: float | None = None,
) -> Bosl2Solid | None:
    """Octagonal holes on a square grid, leaving small square webs."""
    size = hole_size(spacing, web)
    return _punch(
        lambda x, y: _prism(8, size, thickness, 22.5).translate(
            [x, y, thickness / 2]
        ),
        width, length, spacing, size,
    )


VORONOI_SEED = 42
"""Fixed seed, so a lid's pattern is the same on every build.

The pattern is part of the exported geometry and is what the export fingerprint
is taken over, so a fresh random layout each run would rewrite the file forever.
"""

VORONOI_JITTER = 0.99
"""How much of its cell a seed point may roam, as a share.

Near 1, so the points are all but uniformly scattered and the cells come out
genuinely irregular. Lower it and the cells converge on a square grid — which is
the pattern this one exists *not* to be.
"""

VORONOI_CORNER_MM = 1.0
"""Radius the cell corners are rounded by.

A Voronoi cell is a polygon, and its corners are where three cells meet at a
point. Left sharp, that point is a stress raiser in a lid whose whole job is to
be thin. The rounding is done by cutting the cells back further and growing them
returned after, so the web keeps its width along the edges and only opens out at
the junctions.
"""

VORONOI_NEIGHBOUR_REACH = 2.1 * 1.4142135623730951
"""How far a cell looks for the neighbours that bound it, in cell sizes.

A Voronoi cell is bounded by its Delaunay neighbours, which on a jittered grid
are near — but "near" has to be generous enough to cover a point that wandered
into one corner of its cell and a neighbour that wandered to the far side of
its own. Anything beyond this cannot cut the cell, so testing it is only cost.
"""


def _voronoi_points(
    width: float, length: float, spacing: float
) -> list[tuple[float, float]]:
    """Seed points: one per cell of a grid, each scattered within its cell.

    Args:
        width: Width of the area to fill, in mm.
        length: Its length, in mm.
        spacing: The grid's cell size.

    Returns:
        The points, including the ones outside the area. A cell only comes out
        the right shape if it has neighbours on every side, so the ring beyond
        the edge is what makes the cells *at* the edge real rather than bounded
        by nothing.

    """
    rng = random.Random(VORONOI_SEED)
    roam = spacing * VORONOI_JITTER / 2.0
    return [
        (x + rng.uniform(-roam, roam), y + rng.uniform(-roam, roam))
        for x, y in _grid_cells(width, length, spacing)
    ]


def _voronoi_cell(
    point: tuple[float, float],
    points: list[tuple[float, float]],
    inset: float,
    reach: float,
) -> Bosl2Shape2D | None:
    """Return the cell around `point`, pulled in by `inset` on every side.

    A point's cell is everywhere closer to it than to any other point, which is
    the intersection of one half-plane per neighbour: the side of their
    perpendicular bisector that `point` is on. Insetting each half-plane rather
    than the finished polygon is what makes the web an even width — every edge
    moves in by the same amount, whatever angle it sits at.

    Args:
        point: The cell's seed.
        points: Every seed, this one included.
        inset: How far to pull each bounding edge back towards `point`.
        reach: Ignore neighbours further off than this; they cannot bound it.

    Returns:
        The cell, or ``None`` when no neighbour was close enough to bound it.

    """
    from pybosl2 import shapes2d as s2

    # Wide enough to stand in for a half-plane across the whole cell.
    span = reach * 2.0
    half_plane = s2.rect([span * 2, span]).translate([0.0, -span / 2.0])

    cell = None
    for other in points:
        dx, dy = other[0] - point[0], other[1] - point[1]
        distance = math.hypot(dx, dy)
        if distance <= 1e-9 or distance > reach:
            continue
        # The bisector sits halfway between the two; step back towards `point`
        # by the inset, and face the plane so `point` is on the kept side.
        angle = 90.0 + math.degrees(math.atan2(-dy, -dx))
        cut = half_plane.rotate(angle).translate([
            (point[0] + other[0]) / 2.0 - dx / distance * inset,
            (point[1] + other[1]) / 2.0 - dy / distance * inset,
        ])
        cell = cut if cell is None else cell & cut
    return cell


def _voronoi_fill(
    width: float, length: float, thickness: float, spacing: float,
    web: float | None = None,
) -> Bosl2Solid | None:
    """Irregular cells with an even web between them — a true Voronoi.

    Each cell is the region closer to its own seed than to any other, so the
    cells **tile**: the material left over is exactly the web, and the lid comes
    out as a net rather than as a sheet with holes punched in it.

    This was round holes on a jittered grid, which is a scatter of circles and
    reads as one. What makes a Voronoi look like a Voronoi is that neighbouring
    cells share a straight edge, and circles never do (FR-023).
    """
    if hole_size(spacing, web) <= 0:
        return None
    gap = DEFAULT_WEB_MM if web is None else max(web, MIN_WEB_MM)
    corner = min(VORONOI_CORNER_MM, gap)

    points = _voronoi_points(width, length, spacing)
    reach = spacing * VORONOI_NEIGHBOUR_REACH
    # Cut back by the corner radius as well, then grow it all back at the end:
    # that rounds the junctions without widening the web along the edges.
    inset = gap / 2.0 + corner

    cells = None
    for point in points:
        cell = _voronoi_cell(point, points, inset, reach)
        if cell is not None:
            cells = cell if cells is None else cells | cell
    if cells is None:
        return None

    height = thickness * DEPTH_OVERSHOOT
    return cells.offset(radius=corner).linear_extrude(height=height).translate(
        [0.0, 0.0, -(height - thickness) / 2.0]
    )


LEAF_ASPECT = 2.0
"""How many times longer a leaf is than it is wide.

Two-to-one is the ratio at which a pointed oval stops reading as an eye and
starts reading as a leaf. It also sets how far the rows interleave, so it is one
number rather than two: see ``_leaf_row_step``.
"""

LEAF_MIDRIB_MIN_HALF_MM = 1.5
"""Narrowest half-leaf worth cutting either side of a midrib.

Below this the rib has split one hole into two slits, which reads as a crack in
the lid rather than as a leaf, so the leaf is cut whole instead.
"""


def _leaf_half_height(x: float, half_length: float, half_width: float) -> float:
    """Half the leaf's height at `x` from its centre — its outline, as a curve.

    The leaf is the lens where two equal circles overlap, so each side of it is
    a circular arc. A circle of radius R whose arc spans ``half_length`` and
    rises ``half_width`` is the same chord problem the fingernail dish solves:
    ``R = (a² + b²) / 2b``.

    Args:
        x: Distance from the leaf's centre along its long axis.
        half_length: Half the leaf's length — its tip, where the height is 0.
        half_width: Half its width at the middle, where the height is greatest.

    Returns:
        Half the leaf's height there, or ``0`` beyond its tips.

    """
    if abs(x) >= half_length:
        return 0.0
    ball = (half_length ** 2 + half_width ** 2) / (2 * half_width)
    return math.sqrt(ball ** 2 - x ** 2) - (ball - half_width)


def _leaf_row_step(half_length: float, half_width: float, web: float) -> float:
    """How far apart leaf rows sit, given that they interleave.

    Offset rows do not need a full leaf-width between them. A row is shifted
    half a pitch, so where one leaf is at its widest its neighbours above and
    below are near their tips, and the rows nest into each other. Stepping by
    the full width instead would leave a band of solid lid along every row —
    the leaves would read as stripes rather than as foliage.

    How far they nest is a property of the outline, so it is measured rather
    than guessed: the closest the two rows come is at the midpoint between the
    offset centres, where by symmetry both leaves are the same height.

    Args:
        half_length: Half a leaf's length.
        half_width: Half its width.
        web: Material to leave between the rows.

    Returns:
        The row-to-row distance that leaves exactly `web` between them.

    """
    # Half the pitch along the row, so the midpoint between a leaf and its
    # neighbour in the row below is a quarter of the pitch from each.
    quarter_pitch = (2 * half_length + web) / 4.0
    return web + 2 * _leaf_half_height(quarter_pitch, half_length, half_width)


def _leaf(length: float, width: float, thickness: float, rib: float) -> Bosl2Solid:
    """One leaf-shaped hole, lying along X, tall enough to break through."""
    from pybosl2 import cuboid, cylinder

    half_length, half_width = length / 2.0, width / 2.0
    ball = (half_length ** 2 + half_width ** 2) / (2 * half_width)
    height = thickness * DEPTH_OVERSHOOT
    # The lens two overlapping circles leave. Each is offset until its near
    # edge reaches the leaf's midline plus half its width.
    disc = cylinder(height=height, radius=ball, **precision_kwargs())
    leaf = disc.translate([0, half_width - ball, 0]) & disc.translate(
        [0, ball - half_width, 0]
    )
    if rib <= 0 or width / 2.0 - rib / 2.0 < LEAF_MIDRIB_MIN_HALF_MM:
        return leaf
    # The midrib: a bar of lid left along the leaf's spine. It is what tells a
    # viewer this is a leaf rather than a pointed oval, and it braces the
    # widest part of the hole, which is where a perforated lid gives way.
    return leaf - cuboid([length, rib, height * 2])


def _leaf_fill(
    width: float, length: float, thickness: float, spacing: float,
    web: float | None = None,
) -> Bosl2Solid | None:
    """Pointed-oval leaves with midribs, interlocking in offset rows.

    The pitch names the leaf's **length**, as it names a hexagon's width: what
    a caller sets is how far apart the holes are, and the shape fills that. A
    leaf is half as wide as it is long, and the rows nest into one another by
    the amount its taper allows, so the web is even across the lid rather than
    only along the rows.
    """
    leaf_length = hole_size(spacing, web)
    if leaf_length <= 0:
        return None
    leaf_width = leaf_length / LEAF_ASPECT
    gap = DEFAULT_WEB_MM if web is None else max(web, MIN_WEB_MM)
    rib = max(MIN_WEB_MM, gap / 2.0)

    return _punch(
        lambda x, y: _leaf(leaf_length, leaf_width, thickness, rib).translate(
            [x, y, thickness / 2]
        ),
        width, length, spacing, leaf_length, stagger=True,
        row_step=_leaf_row_step(leaf_length / 2.0, leaf_width / 2.0, gap),
    )


ROOT_THREE = math.sqrt(3.0)

LEAF_VEIN_BRANCHES = ((-0.45, 0.05), (0.05, 0.45), (0.45, 0.80))
"""Where each side vein leaves the midrib and where it lands, as fractions.

The first number is how far along the leaf's half-width the vein leaves the
midrib; the second is how far along the tip-side margin it lands. Both ends sit
**on** other material — the midrib and the outline — because a vein floating
loose in a hole is an island the printer has nothing to build on.

None of them starts at the leaf's base. Three leaves meet at each base, so veins
converging there compound into a six-pointed star across the lattice and the
leaf stops being legible: what the eye picks out is the star, not the outline
around it. Starting them along the midrib instead costs nothing and keeps each
leaf reading as one.
"""

LEAF_VEIN_SHARE = 0.5
"""How thick a vein is next to the web between leaves."""


def tessellating_leaf_path(section: float) -> list[tuple[float, float]]:
    """Return the outline of a leaf that tiles the plane, tip towards +X.

    Seven points, of which the useful fact is how their edges pair up. The two
    long edges to the tip are equal and opposite to the two from the base, so
    each is another leaf's edge under translation; the base's single long edge
    is matched by the *two* short notch edges of two different neighbours. That
    is what makes this leaf a tile rather than a leaf-shaped blob: it meets its
    neighbours edge to edge, with nothing left over between them.

    Args:
        section: The leaf's quarter-height — the module this is built from. The
            leaf comes out ``4 × section`` from notch to notch and
            ``2√3 × section`` from base to tip.

    Returns:
        The outline, anticlockwise, centred on the midrib's midpoint.

    """
    half_width = section * ROOT_THREE
    return [
        (half_width, 0.0),
        (0.0, section),
        (0.0, 2 * section),
        (-half_width, section),
        (-half_width, -section),
        (0.0, -2 * section),
        (0.0, -section),
    ]


def _leaf_veins(section: float, thickness: float) -> Bosl2Shape2D:
    """Return a midrib and its branches, as material to leave inside a leaf.

    A midrib from base to tip, and three pairs of side veins running forward
    from it to the tip-side margin. Every one ends on the outline or on the
    midrib, so nothing in here is an island for the printer to start in mid-air,
    and the midrib braces the middle of the hole, which is where a perforated
    lid gives way.

    That is the whole of it. The pattern this is modelled on branches each vein
    twice more and rotates the sub-branches about the base; drawn at a lid's
    scale the detail closes up into a blur, and the strokes that produced it
    were positioned by constants that only held at one leaf size.

    Args:
        section: The leaf's quarter-height, as :func:`tessellating_leaf_path`.
        thickness: How wide to draw each vein.

    Returns:
        The veins, in the leaf's own frame.

    """
    from pybosl2 import shapes2d as s2

    half_width = section * ROOT_THREE

    def stroke(
        start: tuple[float, float], end: tuple[float, float]
    ) -> Bosl2Shape2D:
        length = math.dist(start, end)
        angle = math.degrees(math.atan2(end[1] - start[1], end[0] - start[0]))
        return s2.rect([length, thickness]).rotate(angle).translate(
            [(start[0] + end[0]) / 2, (start[1] + end[1]) / 2]
        )

    veins = stroke((-half_width, 0.0), (half_width, 0.0))
    for sign in (1, -1):
        for from_rib, to_margin in LEAF_VEIN_BRANCHES:
            # The tip-side margin runs from the notch corner (0, section) to the
            # tip (half_width, 0), so one fraction gives both of a point on it.
            veins = veins | stroke(
                (from_rib * half_width, 0.0),
                (to_margin * half_width, sign * section * (1.0 - to_margin)),
            )
    return veins


def _leaf_tessellation_fill(
    width: float, length: float, thickness: float, spacing: float,
    web: float | None = None, veins: bool = False,
) -> Bosl2Solid | None:
    """Leaves that tile the lid edge to edge, leaving their outlines and veins.

    Unlike :func:`_leaf_fill`, which spaces pointed ovals out and solves for the
    gap between them, these leaves **tessellate**: the tile covers the plane, so
    the material left is exactly the web, and it comes out as a net of leaf
    outlines rather than as a field with holes in it.

    The pitch is what it is everywhere else — the distance from one hole to the
    next — which for this tile is the leaf's own base-to-tip length, since a
    leaf's tip lands on its neighbour's base.
    """
    if hole_size(spacing, web) <= 0:
        return None
    gap = DEFAULT_WEB_MM if web is None else max(web, MIN_WEB_MM)

    from pybosl2 import shapes2d as s2

    # `spacing` is the lattice pitch along a row, which for this tile is twice
    # the leaf's half-width, so the leaf is built from the section that gives it.
    section = spacing / (2 * ROOT_THREE)
    outline = s2.polygon(
        [[x, y] for x, y in tessellating_leaf_path(section)]
    ).offset(delta=-gap / 2.0)
    if veins:
        outline = outline - _leaf_veins(section, max(MIN_WEB_MM, gap * LEAF_VEIN_SHARE))

    height = thickness * DEPTH_OVERSHOOT
    hole = outline.linear_extrude(height=height).translate(
        [0, 0, -(height - thickness) / 2.0]
    )

    # Rows step half the leaf's height and shift half a pitch, which is the
    # lattice the tile actually tessellates on: each leaf's notches take the
    # neighbouring row's tips.
    return _punch(
        lambda x, y: hole.translate([x, y, 0]),
        width, length, spacing, spacing,
        stagger=True, row_step=2 * section,
    )


_PATTERN_FILLS: dict[
    PatternType,
    Callable[[float, float, float, float, float | None], Bosl2Solid | None],
] = {
    PatternType.NONE: lambda w, l, t, s, web: None,
    PatternType.SQUARE: _square_fill,
    PatternType.CIRCLE: _circle_fill,
    PatternType.HEX: _hex_fill,
    PatternType.DENSE_HEX: lambda w, l, t, s, web: _hex_fill(w, l, t, s, web, dense=True),
    PatternType.TRIANGLE: _triangle_fill,
    PatternType.DENSE_TRIANGLE: lambda w, l, t, s, web: _triangle_fill(
        w, l, t, s, web, dense=True
    ),
    PatternType.OCTAGON: _octagon_fill,
    PatternType.VORONOI: _voronoi_fill,
    PatternType.LEAF: _leaf_fill,
    PatternType.LEAF_TESSELLATION: _leaf_tessellation_fill,
    PatternType.LEAF_VEINS: lambda w, l, t, s, web: _leaf_tessellation_fill(
        w, l, t, s, web, veins=True
    ),
}
"""Every pattern the library can draw.

A member of :class:`PatternType` missing from here is a bug in one of the two,
which is what :func:`build_pattern` checks rather than papering over.
"""
