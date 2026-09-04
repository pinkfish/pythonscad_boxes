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
