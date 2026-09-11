# SPDX-License-Identifier: Apache-2.0
"""Unit tests for SlipoverBox with arbitrary polygon footprints."""

import unittest

from pyboxbuilder import Project
from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY, BOX_TYPE_REGISTRY
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.slipover import SlipoverBoxBuilder
from pyboxbuilder.enums import BoxType


class SlipoverBoxPolygonTests(unittest.TestCase):
    """Tests for BoxType.SLIPOVER with polygon paths."""

    def test_slipover_builder_accepts_path_and_hollow(self) -> None:
        p = Project("SlipPolyTest")
        l_path = (
            (0.0, 0.0),
            (50.0, 0.0),
            (50.0, 20.0),
            (20.0, 20.0),
            (20.0, 50.0),
            (0.0, 50.0),
        )
        box = p.box(
            BoxType.SLIPOVER,
            "SlipLShaped",
            size=(50.0, 50.0, 25.0),
            path=l_path,
            hollow=True,
            foot=5.0,
            slip=1.6,
        )
        self.assertEqual(box.path, l_path)
        self.assertTrue(box.hollow)
        self.assertEqual(box.foot, 5.0)
        self.assertEqual(box.slip, 1.6)

    def test_slipover_path_normalized_from_list(self) -> None:
        p = Project("SlipNormTest")
        list_path = [[0, 0], [45, 0], [45, 45], [0, 45]]
        box = p.box(
            BoxType.SLIPOVER,
            "SlipSquare",
            size=(45.0, 45.0, 20.0),
            path=list_path,
        )
        self.assertEqual(
            box.path,
            ((0.0, 0.0), (45.0, 0.0), (45.0, 45.0), (0.0, 45.0)),
        )

    def test_slipover_polygon_builds_body_and_lid(self) -> None:
        box = BOX_IMPL_REGISTRY[BoxType.SLIPOVER]()
        l_path = (
            (0.0, 0.0),
            (60.0, 0.0),
            (60.0, 25.0),
            (25.0, 25.0),
            (25.0, 60.0),
            (0.0, 60.0),
        )
        spec = BoxSpec(
            label="SlipL",
            width=60.0,
            length=60.0,
            height=25.0,
            wall_thickness=2.0,
            floor_thickness=1.6,
            lid_thickness=2.0,
            path=l_path,
            foot=4.0,
            slip=1.6,
        )
        body = box.build_body(spec)
        self.assertIsNotNone(body)
        lid = box.build_lid(spec)
        self.assertIsNotNone(lid)

        # Body bounds
        b_body = body.bounds()
        c_body, s_body = (b_body.center, b_body.size) if hasattr(b_body, "center") else b_body
        self.assertAlmostEqual(c_body[2] - s_body[2] / 2, 0.0, places=3)

        # Lid bounds
        b_lid = lid.bounds()
        c_lid, s_lid = (b_lid.center, b_lid.size) if hasattr(b_lid, "center") else b_lid
        self.assertAlmostEqual(c_lid[2] + s_lid[2] / 2, 25.0, places=3)

    def test_slipover_polygon_hollow_false_is_solid(self) -> None:
        box = BOX_IMPL_REGISTRY[BoxType.SLIPOVER]()
        l_path = (
            (0.0, 0.0),
            (40.0, 0.0),
            (40.0, 20.0),
            (20.0, 20.0),
            (20.0, 40.0),
            (0.0, 40.0),
        )
        spec = BoxSpec(
            label="SlipSolid",
            width=40.0,
            length=40.0,
            height=20.0,
            path=l_path,
            hollow=False,
        )
        body = box.build_body(spec)
        self.assertIsNotNone(body)


if __name__ == "__main__":
    unittest.main()
