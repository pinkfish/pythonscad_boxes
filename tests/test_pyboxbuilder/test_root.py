# SPDX-License-Identifier: Apache-2.0
"""Tests for the Root board game insert."""

import unittest

from boxes.root.root import project


class TestRoot(unittest.TestCase):
    """Test suite for Root project build and layout."""

    def test_build_completes(self) -> None:
        """Verify the project builds all pieces without errors."""
        build = project.build()
        self.assertGreater(len(build.pieces), 20)

    def test_box_labels_present(self) -> None:
        """Verify key faction box labels are present."""
        labels = {b.label for b in project._boxes}
        expected = {
            "MarquisBoxBottom",
            "MarquisBoxTop",
            "ErieBoxBottom",
            "ErieBoxTop",
            "AllianceBoxBottom",
            "AllianceBoxTop",
            "RiverfolkBoxBottom",
            "RiverfolkBoxTop",
            "LizardBoxBottom",
            "LizardBoxTop",
            "VagabondBox",
            "VagabondBox2",
            "BaseCardBox",
            "ErieCardBox",
            "VagabondCardBox",
            "OverviewCardBox",
            "ItemsBoxBottom",
            "ItemsBoxMiddle",
            "ItemsBoxWinter",
            "ItemsBoxExtras",
            "DiceBox",
        }
        for name in expected:
            self.assertIn(name, labels)

    def test_all_pieces_fit_within_box_bounds(self) -> None:
        """Verify pieces are placed within game box boundaries."""
        build = project.build()
        tol = 1e-3
        box_width, box_length, box_height = 214.0, 278.0, 67.0
        for piece in build.pieces:
            if piece.position is None or piece.size is None:
                continue
            x, y, z = piece.position
            w, l, h = piece.size
            self.assertGreaterEqual(x, -tol, f"{piece.label} X < 0")
            self.assertGreaterEqual(y, -tol, f"{piece.label} Y < 0")
            self.assertGreaterEqual(z, -tol, f"{piece.label} Z < 0")
            self.assertLessEqual(x + w, box_width + tol, f"{piece.label} overflows box width ({x+w} > {box_width})")
            self.assertLessEqual(y + l, box_length + tol, f"{piece.label} overflows box length ({y+l} > {box_length})")
            self.assertLessEqual(z + h, box_height + tol, f"{piece.label} overflows box height ({z+h} > {box_height})")

    def test_bottom_board_space_reserved_not_spacer(self) -> None:
        """Verify bottom 28mm board bay has no pieces or auto-generated spacers."""
        build = project.build()
        spacers = [piece for piece in build.pieces if piece.kind == "spacer"]
        self.assertEqual(len(spacers), 2)
        for piece in build.pieces:
            if piece.position is None:
                continue
            self.assertGreaterEqual(
                piece.position[2],
                28.0 - 1e-3,
                f"{piece.label} encroaches on bottom 28mm board bay at z={piece.position[2]}",
            )

    def test_two_vagabond_boxes_with_relation_pockets(self) -> None:
        """Verify both Vagabond boxes are present with warrior, score, and 2 Relation pockets."""
        for label in ("VagabondBox", "VagabondBox2"):
            box = next(b for b in project._boxes if b.label == label)
            elements = box.compartments[0].elements
            texts = [el.shape_file for el in elements if el.shape_file == "Relation"]
            self.assertEqual(len(texts), 2, f"{label} should have two Relation inlays")
