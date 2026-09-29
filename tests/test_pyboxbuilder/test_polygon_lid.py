# SPDX-License-Identifier: Apache-2.0
"""Tests for polygon footprint lid decoration with patterns and labels."""

import unittest

from pybosl2 import Color
from pyboxbuilder import Project
from pyboxbuilder.box.features import regular_polygon_path
from pyboxbuilder.enums import BoxType, LabelMode, PatternType
from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
from pyboxbuilder.lid.decorate import decorate_lid
from pyboxbuilder.paths import largest_inscribed_rectangle, point_in_polygon


class TestPolygonLid(unittest.TestCase):
    def test_point_in_polygon(self) -> None:
        poly = (
            (0.0, 0.0),
            (10.0, 0.0),
            (10.0, 10.0),
            (0.0, 10.0),
        )
        self.assertTrue(point_in_polygon(5.0, 5.0, poly))
        self.assertFalse(point_in_polygon(-1.0, 5.0, poly))
        self.assertFalse(point_in_polygon(15.0, 5.0, poly))

    def test_largest_inscribed_rectangle_rectilinear(self) -> None:
        # L-shape: 55x55 with a 30x30 corner cutout
        l_path = (
            (0.0, 0.0),
            (55.0, 0.0),
            (55.0, 25.0),
            (25.0, 25.0),
            (25.0, 55.0),
            (0.0, 55.0),
        )
        rx, ry, rw, rl = largest_inscribed_rectangle(l_path)
        # Should be either the horizontal arm (55 x 25) or vertical arm (25 x 55)
        # With horizontal tie-breaker, it picks (0, 0, 55, 25)
        self.assertEqual(rw * rl, 1375.0)
        self.assertTrue(rw == 55.0 or rl == 55.0)
        self.assertTrue(rw == 25.0 or rl == 25.0)

        # Rectangle
        rect_path = (
            (0.0, 0.0),
            (40.0, 0.0),
            (40.0, 30.0),
            (0.0, 30.0),
        )
        rx, ry, rw, rl = largest_inscribed_rectangle(rect_path)
        self.assertEqual((rx, ry, rw, rl), (0.0, 0.0, 40.0, 30.0))

    def test_largest_inscribed_rectangle_hexagon(self) -> None:
        hex_path = regular_polygon_path(6, apothem=25.0)
        rx, ry, rw, rl = largest_inscribed_rectangle(hex_path)
        self.assertGreater(rw, 0.0)
        self.assertGreater(rl, 0.0)
        # Inscribed rectangle center should be near polygon center
        cx = rx + rw / 2.0
        cy = ry + rl / 2.0
        self.assertAlmostEqual(cx, 25.0, delta=2.0)
        self.assertAlmostEqual(cy, 28.8675, delta=2.0)

    def test_cap_path_project_build(self) -> None:
        p = Project("CapPathTest")
        l_path = (
            (0.0, 0.0),
            (55.0, 0.0),
            (55.0, 25.0),
            (25.0, 25.0),
            (25.0, 55.0),
            (0.0, 55.0),
        )
        p.box(
            BoxType.CAP_PATH,
            "CapTray",
            size=(55.0, 55.0, 20.0),
            path=l_path,
            color=Color("crimson"),
            lid=LidBuilder(
                label_mode=LabelMode.FRAMED,
                pattern=PatternBuilder(PatternType.HEX, spacing=8.0),
                text_color=Color("white"),
                frame_color=Color("silver"),
            ).titled("L-TRAY"),
        )
        build = p.build()
        self.assertEqual(len(build.pieces), 2)
        lid_piece = [piece for piece in build.pieces if piece.kind == "lid"][0]
        self.assertIsNotNone(lid_piece.solid)

        # Check preview rendering
        preview = p._pipeline.preview_pieces(p._manifest, show_lids=True)
        # Should have body, lid, and colored lid insert(s)
        kinds = [pp.kind for pp in preview]
        self.assertIn("body", kinds)
        self.assertIn("lid", kinds)
        self.assertGreaterEqual(len(preview), 3)

        # Verify text label position is in horizontal arm (y near 12.5), NOT in empty void (y near 27.5)
        text_insert = [pp for pp in preview if pp.color == Color("white")][0]
        b = text_insert.solid.bounds()
        cy = float(b[0][1]) if not hasattr(b, "center") else float(b.center[1])
        self.assertLess(cy, 20.0)  # Located within y in [0, 25] arm

        # Verify frame insert follows the perimeter of the polygon footprint
        frame_insert = [pp for pp in preview if pp.color == Color("silver")][0]
        fb = frame_insert.solid.bounds()
        fcx = float(fb.center[0]) if hasattr(fb, "center") else float(fb[0][0])
        fcy = float(fb.center[1]) if hasattr(fb, "center") else float(fb[0][1])
        fsize_x = float(fb.size[0]) if hasattr(fb, "size") else float(fb[1][0])
        fsize_y = float(fb.size[1]) if hasattr(fb, "size") else float(fb[1][1])
        self.assertAlmostEqual(fcx, 27.5, delta=1.0)
        self.assertAlmostEqual(fcy, 27.5, delta=1.0)
        self.assertGreater(fsize_x, 40.0)
        self.assertGreater(fsize_y, 40.0)

    def test_explicit_label_center_override(self) -> None:
        p = Project("CapPathCenterTest")
        l_path = (
            (0.0, 0.0),
            (55.0, 0.0),
            (55.0, 25.0),
            (25.0, 25.0),
            (25.0, 55.0),
            (0.0, 55.0),
        )
        p.box(
            BoxType.CAP_PATH,
            "CapTrayVertical",
            size=(55.0, 55.0, 20.0),
            path=l_path,
            lid=LidBuilder(
                label_mode=LabelMode.FRAMELESS,
                label_center=(12.5, 35.0),
                pattern=PatternBuilder(PatternType.HEX, spacing=8.0),
            ).titled("VERT"),
        )
        preview = p._pipeline.preview_pieces(p._manifest, show_lids=True)
        label_insert = preview[-1]
        b = label_insert.solid.bounds()
        cx = float(b[0][0]) if not hasattr(b, "center") else float(b.center[0])
        cy = float(b[0][1]) if not hasattr(b, "center") else float(b.center[1])
        self.assertAlmostEqual(cx, 12.5, delta=3.0)
        self.assertAlmostEqual(cy, 35.0, delta=3.0)


    def test_polygon_perimeter_frame_with_center_hole(self) -> None:
        """When inner opening is >= min_hole_size_mm (10mm), a center hole is cut and pattern enters it."""
        from pyboxbuilder.lid.decorate import _build_label
        from tests.mesh import volume

        l_path = (
            (0.0, 0.0),
            (55.0, 0.0),
            (55.0, 25.0),
            (25.0, 25.0),
            (25.0, 55.0),
            (0.0, 55.0),
        )

        b_hole = LidBuilder(
            label_mode=LabelMode.FRAMED,
            border_margin_mm=3.0,
            pattern=PatternBuilder(PatternType.HEX, spacing=8.0),
            text_color=Color("white"),
            frame_color=Color("silver"),
            min_hole_size_mm=10.0,
        ).titled("HOLE")

        lbl_hole = _build_label(b_hole, 55.0, 55.0, "mmu", border_margin_mm=3.0, path=l_path)
        self.assertIsNotNone(lbl_hole)
        self.assertIsNotNone(lbl_hole.plate)
        self.assertIsNotNone(lbl_hole.hatching)

        # The plate volume of a hollow frame is smaller than a solid polygon plate
        vol_hole_plate = volume(lbl_hole.plate)
        self.assertLess(vol_hole_plate, 250.0)

    def test_polygon_perimeter_frame_suppressed_center_hole(self) -> None:
        """When inner opening is < min_hole_size_mm, the center hole is suppressed, leaving a solid plate."""
        from pyboxbuilder.lid.decorate import _build_label
        from tests.mesh import volume

        l_path = (
            (0.0, 0.0),
            (55.0, 0.0),
            (55.0, 25.0),
            (25.0, 25.0),
            (25.0, 55.0),
            (0.0, 55.0),
        )

        # Inner arm width of l_path with 3mm margin and 2mm frame is 15mm.
        # With min_hole_size_mm=20.0, 15 < 20, so center hole is omitted!
        b_solid = LidBuilder(
            label_mode=LabelMode.FRAMED,
            border_margin_mm=3.0,
            pattern=PatternBuilder(PatternType.HEX, spacing=8.0),
            text_color=Color("white"),
            frame_color=Color("silver"),
            min_hole_size_mm=20.0,
        ).titled("SOLID")

        lbl_solid = _build_label(b_solid, 55.0, 55.0, "mmu", border_margin_mm=3.0, path=l_path)
        self.assertIsNotNone(lbl_solid)
        self.assertIsNotNone(lbl_solid.plate)

        # Solid polygon plate volume is much larger (~600 mm³) than hollow frame (~150 mm³)
        vol_solid_plate = volume(lbl_solid.plate)
        self.assertGreater(vol_solid_plate, 500.0)

    def test_polygon_perimeter_frame_pattern_cut_difference(self) -> None:
        """Center hole creates a perimeter frame insert (~213mm³), while suppressed center hole produces a solid plate (~722mm³)."""
        from tests.mesh import volume

        l_path = (
            (0.0, 0.0),
            (55.0, 0.0),
            (55.0, 25.0),
            (25.0, 25.0),
            (25.0, 55.0),
            (0.0, 55.0),
        )

        p1 = Project("P1")
        p1.box(
            BoxType.CAP_PATH,
            "HoleTray",
            size=(55.0, 55.0, 20.0),
            path=l_path,
            lid=LidBuilder(
                label_mode=LabelMode.FRAMED,
                border_margin_mm=3.0,
                pattern=PatternBuilder(PatternType.HEX, spacing=8.0),
                frame_color=Color("silver"),
                min_hole_size_mm=10.0,
            ).titled("HOLE"),
        )
        b1 = p1.build()
        lid_pc1 = [pc for pc in b1.pieces if pc.kind == "lid"][0]
        _, inserts_hole = p1._pipeline._decorated_lid(p1._manifest, lid_pc1, "mmu")

        p2 = Project("P2")
        p2.box(
            BoxType.CAP_PATH,
            "SolidTray",
            size=(55.0, 55.0, 20.0),
            path=l_path,
            lid=LidBuilder(
                label_mode=LabelMode.FRAMED,
                border_margin_mm=3.0,
                pattern=PatternBuilder(PatternType.HEX, spacing=8.0),
                frame_color=Color("silver"),
                min_hole_size_mm=20.0,  # Center hole suppressed
            ).titled("SOLID"),
        )
        b2 = p2.build()
        lid_pc2 = [pc for pc in b2.pieces if pc.kind == "lid"][0]
        _, inserts_solid = p2._pipeline._decorated_lid(p2._manifest, lid_pc2, "mmu")

        self.assertIsNotNone(inserts_hole)
        self.assertIsNotNone(inserts_solid)

        vol_silver_hole = [volume(ins.solid) for ins in inserts_hole if ins.color == Color("silver")][0]
        vol_silver_solid = [volume(ins.solid) for ins in inserts_solid if ins.color == Color("silver")][0]

        self.assertLess(vol_silver_hole, 350.0)
        self.assertGreater(vol_silver_solid, 600.0)
        self.assertLess(vol_silver_hole, vol_silver_solid)


if __name__ == "__main__":
    unittest.main()
