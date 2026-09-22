# SPDX-License-Identifier: Apache-2.0
"""Unit and integration tests for horizontal side-interlocking and regular polygon boxes (FR-102, SC-102)."""

import math
import unittest

from mesh import volume
from pyboxbuilder.box.features import (
    build_horizontal_dovetail,
    build_interlock_clip,
    polygon_grid_position,
    regular_polygon_path,
)
from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
from pyboxbuilder.box.spec import BoxSpec, build_spec
from pyboxbuilder.box.types.modular_interlock import ModularInterlockBox
from pyboxbuilder.box.types.no_lid import NoLidBox
from pyboxbuilder.box.types.path import PathBox
from pyboxbuilder.box.validation import GeometryValidationError, GeometryValidator
from pyboxbuilder.enums import BoxType, InterlockType
from pyboxbuilder.project.core import Project


class InterlockGeometryPrimitivesTests(unittest.TestCase):
    """Test mathematical and geometric primitives for horizontal interlocking."""

    def test_regular_polygon_path_triangle(self) -> None:
        pts = regular_polygon_path(3, apothem=15.0)
        self.assertEqual(len(pts), 3)
        cx = sum(p[0] for p in pts) / 3.0
        cy = sum(p[1] for p in pts) / 3.0
        # Distance from polygon centroid (cx, cy) to each edge midpoint must equal apothem
        for i in range(3):
            p1 = pts[i]
            p2 = pts[(i + 1) % 3]
            mx, my = (p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0
            dist = math.hypot(mx - cx, my - cy)
            self.assertAlmostEqual(dist, 15.0, places=5)

    def test_regular_polygon_path_square(self) -> None:
        pts = regular_polygon_path(4, apothem=20.0)
        self.assertEqual(len(pts), 4)
        cx = sum(p[0] for p in pts) / 4.0
        cy = sum(p[1] for p in pts) / 4.0
        for i in range(4):
            p1 = pts[i]
            p2 = pts[(i + 1) % 4]
            mx, my = (p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0
            self.assertAlmostEqual(math.hypot(mx - cx, my - cy), 20.0, places=5)

    def test_regular_polygon_path_hexagon(self) -> None:
        pts = regular_polygon_path(6, apothem=25.0)
        self.assertEqual(len(pts), 6)
        cx = sum(p[0] for p in pts) / 6.0
        cy = sum(p[1] for p in pts) / 6.0
        for i in range(6):
            p1 = pts[i]
            p2 = pts[(i + 1) % 6]
            mx, my = (p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0
            self.assertAlmostEqual(math.hypot(mx - cx, my - cy), 25.0, places=5)

    def test_regular_polygon_path_invalid(self) -> None:
        with self.assertRaises(ValueError):
            regular_polygon_path(2, apothem=10.0)
        with self.assertRaises(ValueError):
            regular_polygon_path(5)

    def test_polygon_grid_position_square(self) -> None:
        pos00 = polygon_grid_position(0, 0, sides=4, apothem=20.0)
        pos01 = polygon_grid_position(0, 1, sides=4, apothem=20.0)
        pos10 = polygon_grid_position(1, 0, sides=4, apothem=20.0)
        self.assertEqual(pos00, (0.0, 0.0))
        self.assertEqual(pos01, (40.0, 0.0))
        self.assertEqual(pos10, (0.0, 40.0))

    def test_polygon_grid_position_hexagon(self) -> None:
        r = 20.0
        pos00 = polygon_grid_position(0, 0, sides=6, apothem=r)
        pos01 = polygon_grid_position(0, 1, sides=6, apothem=r)
        pos10 = polygon_grid_position(1, 0, sides=6, apothem=r)

        self.assertEqual(pos00, (0.0, 0.0))
        self.assertAlmostEqual(pos01[0], 2.0 * r)
        self.assertAlmostEqual(pos01[1], 0.0)

        # Distance between adjacent col 0 and col 1 is exactly 2*r
        d_col = math.hypot(pos01[0] - pos00[0], pos01[1] - pos00[1])
        self.assertAlmostEqual(d_col, 2.0 * r, places=5)

        # Distance between row 0 and staggered row 1 neighbor is also 2*r
        d_row = math.hypot(pos10[0] - pos00[0], pos10[1] - pos00[1])
        self.assertAlmostEqual(d_row, 2.0 * r, places=4)

    def test_build_horizontal_dovetail(self) -> None:
        dt = build_horizontal_dovetail(depth=3.0, width_tip=8.5, width_base=6.0, height=12.0)
        self.assertIsNotNone(dt)
        vol = volume(dt)
        # Trapezoid area = (8.5 + 6.0) / 2 * 3.0 = 21.75 mm2. Vol = 21.75 * 12.0 = 261.0 mm3
        self.assertAlmostEqual(vol, 261.0, places=1)

    def test_build_interlock_clip(self) -> None:
        clip = build_interlock_clip(depth=2.5, width_tip=7.0, width_base=4.5, height=10.0, clearance=0.15)
        self.assertIsNotNone(clip)
        vol = volume(clip)
        self.assertGreater(vol, 50.0)


class InterlockValidationTests(unittest.TestCase):
    """Test pre-CSG validation bounds for interlocking."""

    def test_invalid_polygon_sides(self) -> None:
        spec = BoxSpec(
            label="BadSides",
            width=50.0,
            length=50.0,
            height=20.0,
            polygon_sides=2,
        )
        with self.assertRaises(GeometryValidationError) as ctx:
            GeometryValidator.validate(spec)
        self.assertEqual(ctx.exception.invariant, "min_polygon_sides")

    def test_negative_interlock_clearance(self) -> None:
        spec = BoxSpec(
            label="NegativeClr",
            width=50.0,
            length=50.0,
            height=20.0,
            interlock_type=InterlockType.DOVETAIL,
            interlock_clearance=-0.05,
        )
        with self.assertRaises(GeometryValidationError) as ctx:
            GeometryValidator.validate(spec)
        self.assertEqual(ctx.exception.invariant, "non_negative_interlock_clearance")


class RectangularBoxInterlockingTests(unittest.TestCase):
    """Test horizontal side-locking between adjacent rectangular boxes."""

    def test_dovetail_zero_collision_and_positive_lock(self) -> None:
        spec = BoxSpec(
            label="ModTray",
            width=60.0,
            length=60.0,
            height=20.0,
            interlock_type=InterlockType.DOVETAIL,
            interlock_clearance=0.15,
        )
        handler = ModularInterlockBox()
        box_a = handler.build_body(spec)
        box_b = handler.build_body(spec)

        # Place box_b abutting box_a along +X: base origin at (60.0, 0.0, 0.0)
        box_b_abutting = box_b.translate([60.0, 0.0, 0.0])

        # 1. Zero solid collision volume (< 0.05 mm³) at nominal abutting position (SC-102)
        collision = volume(box_a & box_b_abutting)
        self.assertLess(
            collision,
            0.05,
            f"Expected 0mm³ collision volume at nominal touching position, got {collision:.4f}mm³",
        )

        # 2. Positive horizontal locking: attempting to pull box_b horizontally along +X by 0.6mm
        # causes the wider male dovetail tip (8.5mm) to wedge into the narrower female socket neck (6.0mm + 2*clr),
        # generating positive interference volume (> 0.0mm³) preventing horizontal separation.
        box_b_pulled = box_b.translate([60.6, 0.0, 0.0])
        pulled_collision = volume(box_a & box_b_pulled)
        self.assertGreater(
            pulled_collision,
            0.0,
            "Flared dovetail must generate positive collision when pulled horizontally apart",
        )

    def test_magnet_cavity_alignment(self) -> None:
        spec = BoxSpec(
            label="MagTray",
            width=50.0,
            length=50.0,
            height=25.0,
            interlock_type=InterlockType.MAGNET,
            interlock_clearance=0.1,
        )
        handler = ModularInterlockBox()
        box_a = handler.build_body(spec)
        box_b = handler.build_body(spec)

        box_b_abutting = box_b.translate([50.0, 0.0, 0.0])
        collision = volume(box_a & box_b_abutting)
        self.assertLess(collision, 0.05)

    def test_clip_slot_alignment(self) -> None:
        spec = BoxSpec(
            label="ClipTray",
            width=50.0,
            length=50.0,
            height=25.0,
            interlock_type=InterlockType.CLIP,
            interlock_clearance=0.15,
        )
        handler = ModularInterlockBox()
        box_a = handler.build_body(spec)
        box_b = handler.build_body(spec)

        box_b_abutting = box_b.translate([50.0, 0.0, 0.0])
        collision = volume(box_a & box_b_abutting)
        self.assertLess(collision, 0.05)


class RegularPolygonBoxGridTests(unittest.TestCase):
    """Test regular polygon box creation, project API methods, and grid clustering."""

    def test_project_regular_polygon_box(self) -> None:
        p = Project("PolygonTest")
        b = p.regular_polygon_box(
            "HexBox",
            sides=6,
            apothem=30.0,
            height=20.0,
            box_type=BoxType.PATH,
            interlock_type=InterlockType.DOVETAIL,
        )
        self.assertEqual(b.polygon_sides, 6)
        self.assertEqual(b.polygon_apothem, 30.0)
        self.assertEqual(b.interlock_type, InterlockType.DOVETAIL)
        self.assertEqual(len(b.path), 6)

        spec = build_spec(p, b, b.size)
        handler = PathBox()
        body = handler.build_body(spec)
        self.assertIsNotNone(body)
        self.assertGreater(volume(body), 1000.0)

    def test_project_hex_box(self) -> None:
        p = Project("HexProject")
        b = p.hex_box("HexTray", apothem=25.0, height=18.0)
        self.assertEqual(b.polygon_sides, 6)
        self.assertEqual(b.polygon_apothem, 25.0)

    def test_polygon_grid_hex_mating(self) -> None:
        p = Project("HexGridProject")
        boxes = p.polygon_grid(
            "HexGrid",
            rows=1,
            cols=2,
            sides=6,
            apothem=25.0,
            height=20.0,
            interlock_type=InterlockType.MAGNET,
        )
        self.assertEqual(len(boxes), 2)
        b0, b1 = boxes[0], boxes[1]

        # Verify distance between origins is exactly 2*apothem = 50.0 mm
        self.assertEqual(b0.position, (0.0, 0.0, 0.0))
        self.assertAlmostEqual(b1.position[0], 50.0, places=5)
        self.assertAlmostEqual(b1.position[1], 0.0, places=5)

        spec0 = build_spec(p, b0, b0.size)
        spec1 = build_spec(p, b1, b1.size)
        handler = PathBox()

        solid0 = handler.build_body(spec0).translate(b0.position)
        solid1 = handler.build_body(spec1).translate(b1.position)

        # 0mm³ collision volume at nominal abutting position (< 0.05 mm³)
        collision = volume(solid0 & solid1)
        self.assertLess(collision, 0.05)

    def test_polygon_grid_cluster_export(self) -> None:
        import tempfile
        from pathlib import Path

        p = Project("ClusterExport", game_box_size=(300, 300, 50))
        p.polygon_grid("Cluster", rows=2, cols=2, sides=6, apothem=20.0, height=15.0)

        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            self.assertGreaterEqual(result.total_files, 4)
            mmu = Path(tmpdir) / "ClusterExport" / "mmu"
            for r in range(2):
                for c in range(2):
                    self.assertTrue((mmu / f"Cluster_{r}_{c}_body.3mf").exists())
