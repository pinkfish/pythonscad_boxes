# SPDX-License-Identifier: Apache-2.0
"""Unit tests for NoLidBox and NoLidBoxBuilder arbitrary polygon footprint support."""

from dataclasses import replace
import unittest

from pyboxbuilder import Project
from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY, BOX_TYPE_REGISTRY
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.no_lid import NoLidBoxBuilder
from pyboxbuilder.enums import BoxType, MagnetType, StackableMode


class NoLidBoxTests(unittest.TestCase):
    """Tests for BoxType.NO_LID with rectangular and arbitrary polygon footprints."""

    def test_no_lid_is_registered(self) -> None:
        self.assertIn(BoxType.NO_LID, BOX_TYPE_REGISTRY)
        self.assertIn(BoxType.NO_LID, BOX_IMPL_REGISTRY)
        self.assertIs(BOX_TYPE_REGISTRY[BoxType.NO_LID], NoLidBoxBuilder)

    def test_builder_accepts_path_and_hollow(self) -> None:
        p = Project("PathNoLidTest")
        l_path = (
            (0.0, 0.0),
            (50.0, 0.0),
            (50.0, 20.0),
            (20.0, 20.0),
            (20.0, 50.0),
            (0.0, 50.0),
        )
        box = p.box(
            BoxType.NO_LID,
            "LShapedTray",
            size=(50.0, 50.0, 20.0),
            path=l_path,
            hollow=True,
        )
        self.assertEqual(box.path, l_path)
        self.assertTrue(box.hollow)

    def test_path_as_list_is_normalized(self) -> None:
        p = Project("NormTest")
        list_path = [[0, 0], [40, 0], [40, 40], [0, 40]]
        box = p.box(
            BoxType.NO_LID,
            "SquareTray",
            size=(40.0, 40.0, 15.0),
            path=list_path,
        )
        self.assertEqual(
            box.path,
            ((0.0, 0.0), (40.0, 0.0), (40.0, 40.0), (0.0, 40.0)),
        )

    def test_no_lid_box_with_polygon_path_builds_body(self) -> None:
        box = BOX_IMPL_REGISTRY[BoxType.NO_LID]()
        l_path = (
            (0.0, 0.0),
            (60.0, 0.0),
            (60.0, 25.0),
            (25.0, 25.0),
            (25.0, 60.0),
            (0.0, 60.0),
        )
        spec = BoxSpec(
            label="LShaped",
            width=60.0,
            length=60.0,
            height=20.0,
            wall_thickness=2.0,
            floor_thickness=1.6,
            path=l_path,
        )
        body = box.build_body(spec)
        self.assertIsNotNone(body)
        b = body.bounds()
        centre, size = (b.center, b.size) if hasattr(b, "center") else b
        self.assertAlmostEqual(size[2], 20.0, places=3)
        self.assertAlmostEqual(centre[2] - size[2] / 2, 0.0, places=3)

    def test_no_lid_box_is_lidless(self) -> None:
        box = BOX_IMPL_REGISTRY[BoxType.NO_LID]()
        spec = BoxSpec(label="Tray", width=50.0, length=50.0, height=20.0)
        self.assertIsNone(box.build_lid(spec))

    def test_no_lid_polygon_hollow_false_is_solid(self) -> None:
        box = BOX_IMPL_REGISTRY[BoxType.NO_LID]()
        l_path = (
            (0.0, 0.0),
            (40.0, 0.0),
            (40.0, 20.0),
            (20.0, 20.0),
            (20.0, 40.0),
            (0.0, 40.0),
        )
        spec = BoxSpec(
            label="LSolid",
            width=40.0,
            length=40.0,
            height=15.0,
            path=l_path,
            hollow=False,
        )
        solid_body = box.build_body(spec)
        self.assertIsNotNone(solid_body)

    def test_no_lid_polygon_stackable_inside(self) -> None:
        box = BOX_IMPL_REGISTRY[BoxType.NO_LID]()
        l_path = (
            (0.0, 0.0),
            (50.0, 0.0),
            (50.0, 25.0),
            (25.0, 25.0),
            (25.0, 50.0),
            (0.0, 50.0),
        )
        spec_plain = BoxSpec(
            label="LPlain",
            width=50.0,
            length=50.0,
            height=20.0,
            wall_thickness=2.0,
            floor_thickness=1.6,
            path=l_path,
        )
        spec_stacked = replace(spec_plain, stackable=StackableMode.INSIDE)
        plain = repr(box.build_body(spec_plain))
        stacked = repr(box.build_body(spec_stacked))
        self.assertNotEqual(plain, stacked)

    def test_no_lid_polygon_stackable_outside(self) -> None:
        box = BOX_IMPL_REGISTRY[BoxType.NO_LID]()
        l_path = (
            (0.0, 0.0),
            (50.0, 0.0),
            (50.0, 25.0),
            (25.0, 25.0),
            (25.0, 50.0),
            (0.0, 50.0),
        )
        spec_plain = BoxSpec(
            label="LPlain",
            width=50.0,
            length=50.0,
            height=20.0,
            wall_thickness=2.0,
            floor_thickness=1.6,
            path=l_path,
        )
        spec_stacked = replace(spec_plain, stackable=StackableMode.OUTSIDE)
        plain = repr(box.build_body(spec_plain))
        stacked = repr(box.build_body(spec_stacked))
        self.assertNotEqual(plain, stacked)

    def test_no_lid_polygon_magnet_skipped(self) -> None:
        box = BOX_IMPL_REGISTRY[BoxType.NO_LID]()
        l_path = (
            (0.0, 0.0),
            (50.0, 0.0),
            (50.0, 25.0),
            (25.0, 25.0),
            (25.0, 50.0),
            (0.0, 50.0),
        )
        spec_plain = BoxSpec(
            label="LPlain",
            width=50.0,
            length=50.0,
            height=20.0,
            wall_thickness=2.0,
            floor_thickness=1.6,
            path=l_path,
        )
        spec_magnet = replace(
            spec_plain,
            magnet_type=MagnetType.ROUND,
            magnet_size=(6.0, 6.0, 3.0),
        )
        plain = repr(box.build_body(spec_plain))
        with_mag = repr(box.build_body(spec_magnet))
        # Magnet pockets on arbitrary polygons are safely skipped without error
        self.assertEqual(plain, with_mag)


if __name__ == "__main__":
    unittest.main()
