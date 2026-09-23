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

        # Verify label position is in horizontal arm (y near 12.5), NOT in empty void (y near 27.5)
        label_insert = preview[-1]
        b = label_insert.solid.bounds()
        cy = float(b[0][1]) if not hasattr(b, "center") else float(b.center[1])
        self.assertLess(cy, 20.0)  # Located within y in [0, 25] arm

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


if __name__ == "__main__":
    unittest.main()
