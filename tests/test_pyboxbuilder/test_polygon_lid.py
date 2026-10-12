# SPDX-License-Identifier: Apache-2.0
"""Tests for polygon footprint lid decoration with patterns and labels."""

import unittest

from pybosl2 import Color

from pyboxbuilder import Project
from pyboxbuilder.box.features import regular_polygon_path
from pyboxbuilder.enums import BoxType, LabelMode, PatternType
from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
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
        lid_piece = next(piece for piece in build.pieces if piece.kind == "lid")
        self.assertIsNotNone(lid_piece.solid)

        # Check preview rendering
        preview = p._pipeline.preview_pieces(p._manifest, show_lids=True)
        # Should have body, lid, and colored lid insert(s)
        kinds = [pp.kind for pp in preview]
        self.assertIn("body", kinds)
        self.assertIn("lid", kinds)
        self.assertGreaterEqual(len(preview), 3)

        # Verify text label position is in horizontal arm (y near 12.5), NOT in empty void (y near 27.5)
        text_insert = next(pp for pp in preview if pp.color == Color("white"))
        b = text_insert.solid.bounds()
        cy = float(b[0][1]) if not hasattr(b, "center") else float(b.center[1])
        self.assertLess(cy, 20.0)  # Located within y in [0, 25] arm

        # Verify frame insert hugs the sign in the longest open space
        frame_insert = next(pp for pp in preview if pp.color == Color("silver"))
        fb = frame_insert.solid.bounds()
        fcx = float(fb.center[0]) if hasattr(fb, "center") else float(fb[0][0])
        fcy = float(fb.center[1]) if hasattr(fb, "center") else float(fb[0][1])
        fsize_x = float(fb.size[0]) if hasattr(fb, "size") else float(fb[1][0])
        fsize_y = float(fb.size[1]) if hasattr(fb, "size") else float(fb[1][1])
        self.assertAlmostEqual(fcx, 27.5, delta=1.0)
        self.assertAlmostEqual(fcy, 12.5, delta=1.0)
        self.assertGreater(fsize_x, 35.0)
        self.assertLess(fsize_y, 20.0)

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

    def test_longest_inscribed_rectangle(self) -> None:
        """Verify longest_inscribed_rectangle finds the longest arm in an L-path."""
        from pyboxbuilder.box.features import offset_footprint
        from pyboxbuilder.paths import longest_inscribed_rectangle

        l_path = (
            (0.0, 0.0),
            (55.0, 0.0),
            (55.0, 25.0),
            (25.0, 25.0),
            (25.0, 55.0),
            (0.0, 55.0),
        )
        open_path = offset_footprint(l_path, 5.0)
        _rx, _ry, rw, rl = longest_inscribed_rectangle(open_path)
        self.assertEqual(max(rw, rl), 45.0)
        self.assertEqual(min(rw, rl), 15.0)

    def test_polygon_sign_in_longest_open_space(self) -> None:
        """Verify sign (plate + text + hatching) is contained inside the longest open space."""
        p = Project("LongestOpenSpaceTest")
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
            "L_Box",
            size=(55.0, 55.0, 20.0),
            path=l_path,
            lid=LidBuilder(
                label_mode=LabelMode.FRAMED,
                text_color=Color("white"),
                frame_color=Color("silver"),
            ).titled("SIGN"),
        )
        preview = p._pipeline.preview_pieces(p._manifest, show_lids=True)
        silver = next(pp for pp in preview if pp.color == Color("silver"))
        fb = silver.solid.bounds()
        fcx = float(fb.center[0]) if hasattr(fb, "center") else float(fb[0][0])
        fcy = float(fb.center[1]) if hasattr(fb, "center") else float(fb[0][1])
        # Located in the horizontal arm (y near 12.5, x near 27.5)
        self.assertAlmostEqual(fcx, 27.5, delta=1.0)
        self.assertAlmostEqual(fcy, 12.5, delta=1.0)


if __name__ == "__main__":
    unittest.main()
