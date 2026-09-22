# SPDX-License-Identifier: Apache-2.0
"""Tests for Project constructor and box registration."""

import unittest
from pathlib import Path

from pyboxbuilder.enums import BoxType
from pyboxbuilder.project import Project


class ProjectTests(unittest.TestCase):
    def test_constructor_defaults(self) -> None:
        p = Project("TestGame", game_box_size=(200, 150, 60))
        self.assertEqual(p.name, "TestGame")
        self.assertEqual(p.game_box_size, (200, 150, 60))
        self.assertEqual(p.wall_thickness, 2.0)
        self.assertEqual(p.floor_thickness, 1.6)
        self.assertEqual(p.lid_thickness, 2.0)
        self.assertEqual(p.gap_threshold, 10.0)
        self.assertEqual(p.min_spacer_dim, 15.0)

    def test_add_box_sliding(self) -> None:
        p = Project("Test", game_box_size=(200, 150, 60))
        b = p.box(BoxType.SLIDING, "Cards", size=(100, 70, 50))
        self.assertEqual(b.label, "Cards")
        self.assertEqual(b.size, (100, 70, 50))

    def test_add_box_without_size(self) -> None:
        p = Project("Test", game_box_size=(200, 150, 60))
        b = p.box(BoxType.SLIDING, "AutoBox")
        self.assertIsNone(b.size)

    def test_export_empty_project(self) -> None:
        p = Project("Empty", game_box_size=(100, 100, 50))
        result = p.export("/tmp/test_output")
        self.assertEqual(result.written, ())
        self.assertEqual(result.skipped, ())
        self.assertEqual(result.total_files, 0)

    def test_export_with_box(self) -> None:
        p = Project("WithBox", game_box_size=(200, 150, 60))
        p.box(BoxType.SLIDING, "Cards", size=(100, 70, 50))
        result = p.export("/tmp/test_output")
        self.assertIsNotNone(result)

    def test_standalone_box_has_no_spacers(self) -> None:
        p = Project("Standalone")
        p.box(BoxType.SLIDING, "Tokens", size=(60.0, 60.0, 22.0))
        build = p.build()
        self.assertEqual(len(build.pieces), 2)  # body + lid
        self.assertEqual([p.kind for p in build.pieces], ["body", "lid"])
        self.assertTrue(all(p.label == "Tokens" for p in build.pieces))

    def test_standalone_boxes_respect_explicit_positions(self) -> None:
        p = Project("StackDemo")
        p.box(BoxType.NO_LID, "Lower", size=(60.0, 60.0, 16.0), position=(0.0, 0.0, 0.0))
        p.box(BoxType.NO_LID, "Upper", size=(60.0, 60.0, 16.0), position=(0.0, 0.0, 16.0))
        build = p.build()
        self.assertEqual([p.position for p in build.pieces], [(0.0, 0.0, 0.0), (0.0, 0.0, 16.0)])

