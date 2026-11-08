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
    "chevron_tiling",
    "multigrid_colored_tiling",
    "multigrid_tiling",
    "polygon_area",
    "stepped_cube_tiling",
    "tumbling_blocks_tiling",
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


def multigrid_colored_tiling(
    width: float,
    length: float,
    symmetry: int,
    edge: float,
) -> list[tuple[list[Point], int]]:
    """Return ``(vertices, color_idx)`` for each rhombus in de Bruijn's multigrid tiling.

    Classifies each rhombus by the acute angle between its two generating line
    families ``j`` and ``k``: ``min(k - j, symmetry - (k - j)) - 1``, which
    separates thin and thick rhombi into distinct colour groups.
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
    reach = math.hypot(width, length) / edge / 2.0 + 2.0
    centre = (width / (2.0 * edge), length / (2.0 * edge))

    tiles: list[tuple[list[Point], int]] = []
    for j in range(symmetry):
        for k in range(j + 1, symmetry):
            color_idx = min(k - j, symmetry - (k - j)) - 1
            for poly in _multigrid_cell(j, k, normals, offsets, centre, reach, edge):
                tiles.append((poly, color_idx))
    return tiles


ROOT_THREE = math.sqrt(3.0)


def stepped_cube_tiling(
    width: float,
    length: float,
    edge: float,
) -> list[tuple[list[Point], int]]:
    """Tile an area with the 4-part stepped 3D cube & diamond rhombic tessellation.

    Every tile is a 60°/120° rhombus of side length ``edge`` (area ``√3/2 * edge²``),
    arranged in repeating cells of width ``√3 * edge`` and height ``2 * edge``:

    * **0**: Peak horizontal diamond (top of the stepped chevron band).
    * **1**: Valley horizontal diamond (nested between peak diamonds, forming the
      top face of each 3D cube).
    * **2**: Left-leaning vertical rhombus (left illuminated face of each 3D cube).
    * **3**: Right-leaning vertical rhombus (right shaded face of each 3D cube).

    Together the four rhombi partition the plane edge-to-edge with zero overlap.
    """
    if edge <= 0:
        raise ValueError(f"edge must be positive, got {edge}")

    s = edge
    w = ROOT_THREE * s
    half_w = w / 2.0
    half_s = s / 2.0
    step_y = 2.0 * s

    cx, cy = width / 2.0, length / 2.0
    cols = math.ceil(width / (2.0 * w)) + 2
    rows = math.ceil(length / (2.0 * step_y)) + 2

    tiles: list[tuple[list[Point], int]] = []
    for r in range(-rows, rows + 1):
        y0 = cy + r * step_y
        for c in range(-cols, cols + 1):
            x0 = cx + c * w
            # 0: Peak horizontal diamond centered at (x0, y0 + s/2)
            tiles.append((
                [
                    (x0, y0),
                    (x0 + half_w, y0 + half_s),
                    (x0, y0 + s),
                    (x0 - half_w, y0 + half_s),
                ],
                0,
            ))
            # 1: Valley horizontal diamond centered at (x0 + w/2, y0)
            tiles.append((
                [
                    (x0 + half_w, y0 - half_s),
                    (x0 + w, y0),
                    (x0 + half_w, y0 + half_s),
                    (x0, y0),
                ],
                1,
            ))
            # 2: Left vertical rhombus in [x0 - w/2, x0]
            tiles.append((
                [
                    (x0 - half_w, y0 + half_s),
                    (x0, y0 + s),
                    (x0, y0 + 2.0 * s),
                    (x0 - half_w, y0 + 1.5 * s),
                ],
                2,
            ))
            # 3: Right vertical rhombus in [x0, x0 + w/2]
            tiles.append((
                [
                    (x0, y0 + s),
                    (x0 + half_w, y0 + half_s),
                    (x0 + half_w, y0 + 1.5 * s),
                    (x0, y0 + 2.0 * s),
                ],
                3,
            ))
    return tiles


def tumbling_blocks_tiling(
    width: float,
    length: float,
    edge: float,
) -> list[tuple[list[Point], int]]:
    """Tile an area with the classic 3-rhombus isometric cube tessellation (tumbling blocks).

    Each pointy-top regular hexagon of side ``edge`` is subdivided into three
    60°/120° rhombi meeting at the hexagon centre:

    * **0**: Top horizontal diamond face.
    * **1**: Left vertical rhombus face.
    * **2**: Right vertical rhombus face.
    """
    if edge <= 0:
        raise ValueError(f"edge must be positive, got {edge}")

    s = edge
    w = ROOT_THREE * s
    half_w = w / 2.0
    half_s = s / 2.0
    row_step = 1.5 * s

    cx, cy = width / 2.0, length / 2.0
    cols = math.ceil(width / (2.0 * w)) + 2
    rows = math.ceil(length / (2.0 * row_step)) + 2

    tiles: list[tuple[list[Point], int]] = []
    for r in range(-rows, rows + 1):
        hy = cy + r * row_step
        x_shift = (r % 2) * half_w
        for c in range(-cols, cols + 1):
            hx = cx + c * w + x_shift
            # 0: Top diamond
            tiles.append((
                [
                    (hx, hy),
                    (hx + half_w, hy + half_s),
                    (hx, hy + s),
                    (hx - half_w, hy + half_s),
                ],
                0,
            ))
            # 1: Left vertical rhombus
            tiles.append((
                [
                    (hx, hy),
                    (hx - half_w, hy + half_s),
                    (hx - half_w, hy - half_s),
                    (hx, hy - s),
                ],
                1,
            ))
            # 2: Right vertical rhombus
            tiles.append((
                [
                    (hx, hy),
                    (hx, hy - s),
                    (hx + half_w, hy - half_s),
                    (hx + half_w, hy + half_s),
                ],
                2,
            ))
    return tiles


def chevron_tiling(
    width: float,
    length: float,
    edge: float,
) -> list[tuple[list[Point], int]]:
    """Tile an area with interlocking 60°/120° chevron / herringbone rhombi.

    Alternating columns of width ``√3/2 * edge`` slope up-right (colour ``0``)
    and down-right (colour ``1``), meeting along verticalzig-zag seams.
    """
    if edge <= 0:
        raise ValueError(f"edge must be positive, got {edge}")

    s = edge
    col_w = ROOT_THREE * s / 2.0
    half_s = s / 2.0

    cx, cy = width / 2.0, length / 2.0
    cols = math.ceil(width / (2.0 * col_w)) + 2
    rows = math.ceil(length / (2.0 * s)) + 2

    tiles: list[tuple[list[Point], int]] = []
    for c in range(-cols, cols + 1):
        x0 = cx + c * col_w
        is_odd = (c % 2) != 0
        for r in range(-rows, rows + 1):
            y0 = cy + r * s
            if not is_odd:
                tiles.append((
                    [
                        (x0, y0),
                        (x0 + col_w, y0 + half_s),
                        (x0 + col_w, y0 + 1.5 * s),
                        (x0, y0 + s),
                    ],
                    0,
                ))
            else:
                tiles.append((
                    [
                        (x0, y0 + half_s),
                        (x0 + col_w, y0),
                        (x0 + col_w, y0 + s),
                        (x0, y0 + 1.5 * s),
                    ],
                    1,
                ))
    return tiles
