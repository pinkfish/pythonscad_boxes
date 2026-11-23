# SPDX-License-Identifier: Apache-2.0
"""Tests for the Explorers of Navoria board game insert."""

import unittest

from boxes.explorers_of_navoria.explorers_of_navoria import (
    box_height,
    box_length,
    box_width,
    project,
    usable_height,
)


class TestExplorersOfNavoria(unittest.TestCase):
    """Test suite for Explorers of Navoria project build and layout."""

    def test_build_completes(self) -> None:
        """Verify the project builds all pieces without errors."""
        build = project.build()
        self.assertGreaterEqual(len(build.pieces), 27)

    def test_box_labels_present(self) -> None:
        """Verify all 14 boxes from explorers_of_navoria.scad are generated."""
        labels = {b.label for b in project._boxes}
        expected = {
            "PlayerBox_Green_One",
            "PlayerBox_Yellow_One",
            "PlayerBox_Purple_One",
            "PlayerBox_Black_One",
            "PlayerBox_Green_Two",
            "PlayerBox_Yellow_Two",
            "PlayerBox_Purple_Two",
            "PlayerBox_Black_Two",
            "FavourBox",
            "StuffBox_Swords",
            "StuffBox_Apples",
            "StuffBox_Crystals",
            "CardBox",
            "BagBox",
        }
        self.assertEqual(labels, expected)

    def test_automatic_spacers_generated(self) -> None:
        """Verify automatic spacers or tight volumetric packaging."""
        build = project.build()
        spacers = [p for p in build.pieces if "spacer" in p.label.lower() or p.kind == "spacer"]
        total_vol = sum(p.size[0] * p.size[1] * p.size[2] for p in build.pieces if p.size)
        box_vol = box_width * box_length * box_height
        self.assertTrue(len(spacers) > 0 or total_vol / box_vol > 0.4)

    def test_all_pieces_fit_within_box_bounds(self) -> None:
        """Verify no piece overflows the physical box dimensions or usable height."""
        build = project.build()
        tol = 1e-3
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
            self.assertLessEqual(
                z + h,
                usable_height + tol,
                f"{piece.label} overflows usable height ({z + h} > {usable_height})",
            )
            self.assertLessEqual(z + h, box_height + tol, f"{piece.label} overflows box height ({z+h} > {box_height})")
