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

import random
from collections.abc import Callable, Iterator
from typing import TYPE_CHECKING

from pyboxbuilder.enums import PatternType
from pyboxbuilder.precision import kwargs as precision_kwargs

if TYPE_CHECKING:
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

DENSE_SPACING_SHARE = 0.6
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
        pattern_type: Which pattern. :attr:`PatternType.NONE` returns ``None``.
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
        spacing = default_spacing(width, length)

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
    reach: tuple[float, float],
    stagger: bool = False,
) -> Iterator[tuple[float, float]]:
    """Centres of every cell whose hole fits whole inside the area.

    Args:
        width: Width of the area to fill, in mm.
        length: Its length, in mm.
        spacing: Centre-to-centre distance between holes.
        reach: How far the hole extends from its centre along x and y. This is
            the shape's real half-extent, not half its nominal size: a hexagon
            reaches 15% further at its corners than across its flats, so an
            inset taken from the flats let the outermost holes bleed past the
            border and be clipped into slivers.
        stagger: Offset alternate rows by half a cell, for a honeycomb.

    Yields:
        ``(x, y)`` centres, inset so every hole stays whole — a pattern that
        runs off the edge leaves slivers, not holes.

    """
    reach_x, reach_y = reach
    row_step = spacing * (0.866 if stagger else 1.0)  # sin(60°) for hex rows

    # Centre the grid in the area. A pattern anchored at one corner leaves the
    # leftover — up to a whole cell — as extra margin on the far side, so a lid
    # comes out with a 10mm border on two edges and 16mm on the other two.
    start_x = reach_x + _slack(width, reach_x, spacing) / 2.0
    start_y = reach_y + _slack(length, reach_y, row_step) / 2.0

    y = start_y
    row = 0
    while y <= length - reach_y + _EPS:
        x = start_x + (spacing / 2.0 if stagger and row % 2 else 0.0)
        while x <= width - reach_x + _EPS:
            yield x, y
            x += spacing
        y += row_step
        row += 1


_EPS = 1e-9
"""Slack for the float comparison that decides whether the last cell fits."""


def _slack(extent: float, reach: float, step: float) -> float:
    """How much room is left over once as many cells as fit have been placed.

    Args:
        extent: The area's size along this axis, in mm.
        reach: How far a hole reaches from its centre along it.
        step: Distance between neighbouring centres.

    Returns:
        The unused millimetres, to be split evenly between the two ends.

    """
    usable = extent - 2 * reach
    if usable < 0 or step <= 0:
        return 0.0
    return usable - int(usable / step + _EPS) * step


def _punch(
    shape_at: Callable[[float, float], Bosl2Solid],
    width: float,
    length: float,
    spacing: float,
    hole: float,
    stagger: bool = False,
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

    Returns:
        The union of every hole, or ``None`` when none fit.

    """
    if hole <= 0:
        return None

    holes = None
    for x, y in _grid_cells(width, length, spacing, _reach(shape_at), stagger):
        cut = shape_at(x, y)
        holes = cut if holes is None else holes | cut
    return holes


def _reach(shape_at: Callable[[float, float], Bosl2Solid]) -> tuple[float, float]:
    """How far one hole extends from its centre, along x and y.

    Args:
        shape_at: The fill's shape factory, called once at the origin.

    Returns:
        ``(reach_x, reach_y)`` in mm.

    """
    (cx, cy, _), (w, l, _) = shape_at(0.0, 0.0).bounds()
    return (abs(cx) + w / 2.0, abs(cy) + l / 2.0)


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


def _hex_fill(
    width: float, length: float, thickness: float, spacing: float,
    web: float | None = None, dense: bool = False,
) -> Bosl2Solid | None:
    """Hexagonal holes in staggered rows — a honeycomb."""
    step = spacing * (DENSE_SPACING_SHARE if dense else 1.0)
    size = hole_size(step, web)
    return _punch(
        lambda x, y: _prism(6, size, thickness).translate([x, y, thickness / 2]),
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

VORONOI_JITTER = 0.28
"""How far a cell may wander from its grid point, as a share of the spacing."""

VORONOI_MIN_SCALE = 0.7
VORONOI_MAX_SCALE = 1.15
"""How much a hole's size varies about the nominal, low and high."""


def _voronoi_fill(
    width: float, length: float, thickness: float, spacing: float,
    web: float | None = None,
) -> Bosl2Solid | None:
    """Round holes of varying size on a jittered grid — an organic scatter.

    The jitter and the size variation both eat into the web, so the nominal
    hole is taken at the *largest* it will be drawn and the rest come out
    smaller — otherwise two neighbours that both wandered inwards would meet.
    """
    from pybosl2 import cylinder

    size = hole_size(spacing + 2 * spacing * VORONOI_JITTER, web)
    if size <= 0:
        return None

    rng = random.Random(VORONOI_SEED)
    holes = None
    reach = size / 2 * VORONOI_MAX_SCALE + spacing * VORONOI_JITTER
    for x, y in _grid_cells(width, length, spacing, (reach, reach)):
        jitter = spacing * VORONOI_JITTER
        cx = min(max(x + rng.uniform(-jitter, jitter), 0.0), width)
        cy = min(max(y + rng.uniform(-jitter, jitter), 0.0), length)
        radius = size / 2 * rng.uniform(VORONOI_MIN_SCALE, VORONOI_MAX_SCALE)
        cut = cylinder(
            height=thickness * DEPTH_OVERSHOOT, radius=radius, **precision_kwargs()
        ).translate([cx, cy, thickness / 2])
        holes = cut if holes is None else holes | cut
    return holes


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
}
"""Every pattern the library can draw.

A member of :class:`PatternType` missing from here is a bug in one of the two,
which is what :func:`build_pattern` checks rather than papering over.
"""
