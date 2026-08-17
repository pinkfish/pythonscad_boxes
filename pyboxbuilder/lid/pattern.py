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

HOLE_SHARE = 0.55
"""How much of a pattern cell the hole itself takes.

The rest is the web between holes. Over about two thirds the webs get thinner
than a couple of extrusion widths and the lid loses its stiffness; much under a
half and the pattern stops saving filament, which is the point of it (FR-023).
"""

DENSE_SPACING_SHARE = 0.6
"""How much of the normal spacing a *dense* variant uses."""

DEPTH_OVERSHOOT = 1.2
"""How far a hole is over-extruded relative to the lid, so it breaks through."""

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
) -> Bosl2Solid | None:
    """Build the through-hole cutouts for a lid.

    Args:
        width: Lid width in mm.
        length: Lid length in mm.
        thickness: Lid thickness; the holes are cut deeper so they break through.
        pattern_type: Which pattern. :attr:`PatternType.NONE` returns ``None``.
        spacing: Distance between cell centres. ``None`` derives it from the
            lid (see :func:`default_spacing`).

    Returns:
        The solid to subtract from the lid, or ``None`` for no pattern and for
        a lid too small to hold a single whole hole.

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
    return fill(width, length, thickness, spacing)


# ── Cell placement ────────────────────────────────────────────────────

def _grid_cells(
    width: float, length: float, spacing: float, stagger: bool = False
) -> Iterator[tuple[float, float]]:
    """Centres of every cell whose hole fits whole inside the lid.

    Args:
        width: Lid width in mm.
        length: Lid length in mm.
        spacing: Distance between cell centres.
        stagger: Offset alternate rows by half a cell, for a honeycomb.

    Yields:
        ``(x, y)`` centres, inset so a hole of :data:`HOLE_SHARE` stays whole —
        a pattern that runs off the edge leaves slivers, not holes.

    """
    margin = spacing * HOLE_SHARE / 2.0
    row_step = spacing * (0.866 if stagger else 1.0)  # sin(60°) for hex rows

    y = margin
    row = 0
    while y <= length - margin:
        x = margin + (spacing / 2.0 if stagger and row % 2 else 0.0)
        while x <= width - margin:
            yield x, y
            x += spacing
        y += row_step
        row += 1


def _punch(
    shape_at: Callable[[float, float], Bosl2Solid],
    width: float,
    length: float,
    spacing: float,
    stagger: bool = False,
) -> Bosl2Solid | None:
    """Union one hole per cell.

    Args:
        shape_at: Called with ``(x, y)``; returns one hole solid in place.
        width: Lid width in mm.
        length: Lid length in mm.
        spacing: Cell size in mm.
        stagger: Offset alternate rows.

    Returns:
        The union of every hole, or ``None`` when none fit.

    """
    holes = None
    for x, y in _grid_cells(width, length, spacing, stagger):
        hole = shape_at(x, y)
        holes = hole if holes is None else holes | hole
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
    width: float, length: float, thickness: float, spacing: float
) -> Bosl2Solid | None:
    """Square holes on a square grid."""
    from pybosl2 import cuboid

    size = spacing * HOLE_SHARE
    return _punch(
        lambda x, y: cuboid([size, size, thickness * DEPTH_OVERSHOOT]).translate(
            [x, y, thickness / 2]
        ),
        width, length, spacing,
    )


def _circle_fill(
    width: float, length: float, thickness: float, spacing: float
) -> Bosl2Solid | None:
    """Round holes on a square grid."""
    from pybosl2 import cylinder

    return _punch(
        lambda x, y: cylinder(
            height=thickness * DEPTH_OVERSHOOT,
            radius=spacing * HOLE_SHARE / 2,
            **precision_kwargs(),
        ).translate([x, y, thickness / 2]),
        width, length, spacing,
    )


def _hex_fill(
    width: float, length: float, thickness: float, spacing: float, dense: bool = False
) -> Bosl2Solid | None:
    """Hexagonal holes in staggered rows — a honeycomb."""
    step = spacing * (DENSE_SPACING_SHARE if dense else 1.0)
    return _punch(
        lambda x, y: _prism(6, step * HOLE_SHARE, thickness).translate(
            [x, y, thickness / 2]
        ),
        width, length, step, stagger=True,
    )


def _triangle_fill(
    width: float, length: float, thickness: float, spacing: float, dense: bool = False
) -> Bosl2Solid | None:
    """Triangular holes, alternating point-up and point-down along each row."""
    step = spacing * (DENSE_SPACING_SHARE if dense else 1.0)

    def shape(x: float, y: float) -> Bosl2Solid:
        # Alternating spin is what makes a triangle grid read as one, rather
        # than as rows of identical wedges.
        spin = 180.0 if round(x / step) % 2 else 0.0
        return _prism(3, step * HOLE_SHARE, thickness, spin).translate(
            [x, y, thickness / 2]
        )

    return _punch(shape, width, length, step)


def _octagon_fill(
    width: float, length: float, thickness: float, spacing: float
) -> Bosl2Solid | None:
    """Octagonal holes on a square grid, leaving small square webs."""
    return _punch(
        lambda x, y: _prism(8, spacing * HOLE_SHARE, thickness, 22.5).translate(
            [x, y, thickness / 2]
        ),
        width, length, spacing,
    )


VORONOI_SEED = 42
"""Fixed seed, so a lid's pattern is the same on every build.

The pattern is part of the exported geometry and is what the export fingerprint
is taken over, so a fresh random layout each run would rewrite the file forever.
"""

VORONOI_JITTER = 0.28
"""How far a cell may wander from its grid point, as a share of the spacing."""


def _voronoi_fill(
    width: float, length: float, thickness: float, spacing: float
) -> Bosl2Solid | None:
    """Round holes of varying size on a jittered grid — an organic scatter."""
    from pybosl2 import cylinder

    rng = random.Random(VORONOI_SEED)
    holes = None
    for x, y in _grid_cells(width, length, spacing):
        jitter = spacing * VORONOI_JITTER
        cx = min(max(x + rng.uniform(-jitter, jitter), 0.0), width)
        cy = min(max(y + rng.uniform(-jitter, jitter), 0.0), length)
        radius = spacing * HOLE_SHARE / 2 * rng.uniform(0.7, 1.15)
        hole = cylinder(
            height=thickness * DEPTH_OVERSHOOT, radius=radius, **precision_kwargs()
        ).translate([cx, cy, thickness / 2])
        holes = hole if holes is None else holes | hole
    return holes


_PATTERN_FILLS: dict[PatternType, Callable[[float, float, float, float], Bosl2Solid | None]] = {
    PatternType.NONE: lambda w, l, t, s: None,
    PatternType.SQUARE: _square_fill,
    PatternType.CIRCLE: _circle_fill,
    PatternType.HEX: _hex_fill,
    PatternType.DENSE_HEX: lambda w, l, t, s: _hex_fill(w, l, t, s, dense=True),
    PatternType.TRIANGLE: _triangle_fill,
    PatternType.DENSE_TRIANGLE: lambda w, l, t, s: _triangle_fill(w, l, t, s, dense=True),
    PatternType.OCTAGON: _octagon_fill,
    PatternType.VORONOI: _voronoi_fill,
}
"""Every pattern the library can draw.

A member of :class:`PatternType` missing from here is a bug in one of the two,
which is what :func:`build_pattern` checks rather than papering over.
"""
