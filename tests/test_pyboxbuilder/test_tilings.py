# SPDX-License-Identifier: Apache-2.0
"""Tests for the multigrid tiling (FR-023).

A tiling is a statement about polygons, so it is testable as arithmetic: the
tiles are rhombi, they wind anticlockwise, and clipped to the area they cover
their areas sum to exactly that area — coverage and non-overlap at once.
"""

import math
import unittest

from pyboxbuilder.lid.tilings import Tile, multigrid_tiling, polygon_area
from pyboxbuilder.paths import signed_area

Point = tuple[float, float]


def _clip_to_box(poly: list[Point], width: float, length: float) -> list[Point]:
    """Clip a convex polygon to ``[0, width] x [0, length]`` (Sutherland-Hodgman)."""

    def clip_axis(pts: list[Point], keep, intersect) -> list[Point]:
        if not pts:
            return []
        out: list[Point] = []
        prev = pts[-1]
        prev_in = keep(prev)
        for cur in pts:
            cur_in = keep(cur)
            if cur_in != prev_in:
                out.append(intersect(prev, cur))
            if cur_in:
                out.append(cur)
            prev, prev_in = cur, cur_in
        return out

    def x_cross(a: Point, b: Point, x: float) -> Point:
        t = (x - a[0]) / (b[0] - a[0])
        return (x, a[1] + t * (b[1] - a[1]))

    def y_cross(a: Point, b: Point, y: float) -> Point:
        t = (y - a[1]) / (b[1] - a[1])
        return (a[0] + t * (b[0] - a[0]), y)

    poly = clip_axis(poly, lambda p: p[0] >= 0.0, lambda a, b: x_cross(a, b, 0.0))
    poly = clip_axis(poly, lambda p: p[0] <= width, lambda a, b: x_cross(a, b, width))
    poly = clip_axis(poly, lambda p: p[1] >= 0.0, lambda a, b: y_cross(a, b, 0.0))
    poly = clip_axis(poly, lambda p: p[1] <= length, lambda a, b: y_cross(a, b, length))
    return poly


class PolygonAreaTests(unittest.TestCase):
    def test_unit_square(self) -> None:
        self.assertAlmostEqual(polygon_area([(0, 0), (1, 0), (1, 1), (0, 1)]), 1.0)

    def test_right_triangle(self) -> None:
        self.assertAlmostEqual(polygon_area([(0, 0), (2, 0), (0, 2)]), 2.0)

    def test_winding_does_not_matter(self) -> None:
        clockwise = [(0, 0), (0, 1), (1, 1), (1, 0)]
        self.assertAlmostEqual(polygon_area(clockwise), 1.0)


class TileTests(unittest.TestCase):
    def test_tile_is_a_point_tuple(self) -> None:
        tile = Tile(((0, 0), (1, 0), (1, 1)))
        self.assertIsInstance(tile, tuple)
        self.assertEqual(tile[0], (0, 0))


class MultigridValidationTests(unittest.TestCase):
    def test_symmetry_below_four_is_refused(self) -> None:
        for symmetry in (0, 1, 2, 3):
            with self.assertRaises(ValueError):
                multigrid_tiling(100, 100, symmetry, edge=8)

    def test_non_positive_edge_is_refused(self) -> None:
        for edge in (0.0, -1.0):
            with self.assertRaises(ValueError):
                multigrid_tiling(100, 100, symmetry=5, edge=edge)


class MultigridTileTests(unittest.TestCase):
    """The shape and winding invariants, for the symmetries that matter."""

    SYMMETRIES = (4, 5, 7)

    def _tiles(self, symmetry: int) -> list[list[Point]]:
        return multigrid_tiling(120, 90, symmetry, edge=8)

    def test_produces_tiles(self) -> None:
        for symmetry in self.SYMMETRIES:
            self.assertGreater(len(self._tiles(symmetry)), 0)

    def test_every_tile_is_a_rhombus(self) -> None:
        for symmetry in self.SYMMETRIES:
            for tile in self._tiles(symmetry):
                self.assertEqual(len(tile), 4, msg=f"symmetry={symmetry}")
                edges = [
                    math.dist(tile[i], tile[(i + 1) % 4]) for i in range(4)
                ]
                for e in edges:
                    self.assertAlmostEqual(e, 8.0, places=6, msg=f"{tile}")

    def test_every_tile_winds_anticlockwise(self) -> None:
        for symmetry in self.SYMMETRIES:
            for tile in self._tiles(symmetry):
                self.assertGreater(signed_area(tile), 0.0, msg=f"{tile}")


class MultigridCoverageTests(unittest.TestCase):
    """The tiling property itself: tiles cover the box exactly, no overlap."""

    SYMMETRIES = (4, 5, 6, 7)
    WIDTH, LENGTH = 120.0, 90.0

    def test_tiles_cover_the_area_without_overlap(self) -> None:
        for symmetry in self.SYMMETRIES:
            tiles = multigrid_tiling(self.WIDTH, self.LENGTH, symmetry, edge=8)
            covered = 0.0
            for tile in tiles:
                covered += polygon_area(_clip_to_box(tile, self.WIDTH, self.LENGTH))
            expected = self.WIDTH * self.LENGTH
            self.assertAlmostEqual(
                covered, expected, delta=expected * 1e-6, msg=f"symmetry={symmetry}"
            )
