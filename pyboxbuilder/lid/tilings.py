# SPDX-License-Identifier: Apache-2.0
"""Tile geometry for the lid patterns that tessellate (FR-023).

This module answers one question — *what shapes cover this area, and where* —
and answers it in plain coordinates. It builds no solids and knows nothing about
lids, webs or thickness; :mod:`pyboxbuilder.lid.pattern` takes the polygons from
here and cuts them.

That split is what makes the tilings checkable. "It tiles" is a statement about
polygons, and it is testable as arithmetic: the tiles' areas sum to the area
they cover, and no two of them overlap. A tiling that is only ever seen as a
rendered lid can be wrong in ways nobody notices until it prints.
"""

from __future__ import annotations

import math

__all__ = [
    "Tile",
    "multigrid_tiling",
    "polygon_area",
]

Point = tuple[float, float]


class Tile(tuple[Point, ...]):
    """One tile: its vertices, anticlockwise, in the tiling's own frame."""

    __slots__ = ()


def polygon_area(points: list[Point]) -> float:
    """Return a polygon's area by the shoelace formula.

    Args:
        points: Its vertices in order, either winding.

    Returns:
        The area, always positive.

    """
    total = 0.0
    for i, (x, y) in enumerate(points):
        nx, ny = points[(i + 1) % len(points)]
        total += x * ny - nx * y
    return abs(total) / 2.0


# ── de Bruijn's multigrid ─────────────────────────────────────────────

MULTIGRID_OFFSETS = (0.19, 0.23, 0.17, 0.29, 0.12, 0.27, 0.14, 0.21, 0.26, 0.15,
                     0.11, 0.24)
"""Where each grid family sits, as a fraction of a line spacing.

Fixed, because the pattern is part of the exported geometry and the export
fingerprint is taken over it — a fresh offset each run would rewrite the file
forever (SC-012). They are deliberately **unequal**: equal offsets put every
line of every family through one point, and the tiling degenerates there into a
rosette of overlapping tiles rather than a tiling at all.
"""


def multigrid_tiling(
    width: float,
    length: float,
    symmetry: int,
    edge: float,
) -> list[list[Point]]:
    """Tile an area with rhombi, by de Bruijn's multigrid method.

    Take `symmetry` families of equally spaced parallel lines, each family
    turned by ``180° / symmetry`` from the last. Every crossing of a line from
    one family with a line from another is a rhombus of the tiling, and which
    rhombus is decided by counting how many lines of every *other* family the
    crossing lies past. The rhombus's edges are the two families' normals, so
    its shape comes from the angle between them and nothing else.

    This is the whole family in one function. Five-fold with offsets summing to
    a whole number is the Penrose rhombus tiling — the thin-and-thick one people
    mean by "Penrose". Eight-fold is Ammann–Beenker. Seven- and twelve-fold are
    the same construction at their own symmetries, and none of them repeats.

    Args:
        width: Width of the area to cover, in mm.
        length: Its length, in mm.
        symmetry: How many line families. The tiling's rotational symmetry is
            twice this for an even count and equal to it for an odd one, so 4
            gives the eight-fold Ammann–Beenker, 5 the ten-fold Penrose, 6 the
            twelve-fold, and 7 the fourteen-fold. Four is the floor: with three
            families the crossings give a plain lattice, not a quasicrystal.
        edge: Edge length of every rhombus, in mm. All tiles share it: that is
            what a rhombus tiling is.

    Returns:
        One list of four vertices per tile, anticlockwise, covering the area
        and overhanging it — the caller clips, as it does for every lattice.

    Raises:
        ValueError: If `symmetry` is below 4 or `edge` is not positive.

    """
    if symmetry < 4:
        raise ValueError(
            f"a multigrid tiling needs at least 4 line families, got {symmetry}: "
            "with three the crossings give a plain lattice, not a quasicrystal"
        )
    if edge <= 0:
        raise ValueError(f"edge must be positive, got {edge}")

    normals = [
        (math.cos(math.pi * j / symmetry), math.sin(math.pi * j / symmetry))
        for j in range(symmetry)
    ]
    offsets = [MULTIGRID_OFFSETS[j % len(MULTIGRID_OFFSETS)] for j in range(symmetry)]

    # The tiling is generated in units where the line spacing is 1, then scaled
    # by `edge`. Cover the area's diagonal, plus a tile, so the clip has
    # something to cut on every side.
    reach = math.hypot(width, length) / edge / 2.0 + 2.0
    centre = (width / (2.0 * edge), length / (2.0 * edge))

    tiles: list[list[Point]] = []
    for j in range(symmetry):
        for k in range(j + 1, symmetry):
            tiles.extend(
                _multigrid_cell(j, k, normals, offsets, centre, reach, edge)
            )
    return tiles


def _multigrid_cell(
    j: int,
    k: int,
    normals: list[Point],
    offsets: list[float],
    centre: Point,
    reach: float,
    edge: float,
) -> list[list[Point]]:
    """Every rhombus formed where family `j` crosses family `k`."""
    ej, ek = normals[j], normals[k]
    # Two families are parallel only if the caller asked for a degenerate
    # symmetry, which the public function has already refused.
    det = ej[0] * ek[1] - ej[1] * ek[0]

    # Which lines of each family can reach the area at all.
    mid_j = centre[0] * ej[0] + centre[1] * ej[1] - offsets[j]
    mid_k = centre[0] * ek[0] + centre[1] * ek[1] - offsets[k]

    out: list[list[Point]] = []
    for a in range(math.floor(mid_j - reach), math.ceil(mid_j + reach) + 1):
        for b in range(math.floor(mid_k - reach), math.ceil(mid_k + reach) + 1):
            # Where the two lines cross.
            pj, pk = a + offsets[j], b + offsets[k]
            x = (pj * ek[1] - pk * ej[1]) / det
            y = (pk * ej[0] - pj * ek[0]) / det
            if math.hypot(x - centre[0], y - centre[1]) > reach:
                continue

            # The tile's position is the sum of how far past every family's
            # lines the crossing sits. This is the step that makes the tiling
            # quasiperiodic rather than a lattice of rhombi.
            base_x = base_y = 0.0
            for m, (ex, ey) in enumerate(normals):
                index = a if m == j else b if m == k else math.ceil(
                    x * ex + y * ey - offsets[m]
                )
                base_x += index * ex
                base_y += index * ey

            out.append([
                ((base_x + da * ej[0] + db * ek[0]) * edge,
                 (base_y + da * ej[1] + db * ek[1]) * edge)
                for da, db in ((0, 0), (1, 0), (1, 1), (0, 1))
            ])
    return out
