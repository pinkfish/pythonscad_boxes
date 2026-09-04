# SPDX-License-Identifier: Apache-2.0
"""Tests for the Brink: Long Box Variant board game insert."""

import unittest

from boxes.brink_long.brink_long import (
    box_height,
    box_length,
    box_width,
    project,
)


class TestBrinkLong(unittest.TestCase):
    """Test suite for Brink Long project build and layout."""

    def test_build_completes(self) -> None:
        """Verify the project builds all pieces without errors."""
        build = project.build()
        self.assertGreater(len(build.pieces), 5)

    def test_box_labels_present(self) -> None:
        """Verify all essential box labels are generated."""
        labels = {b.label for b in project._boxes}
        expected = {
            "FleetSolari",
            "FleetHorizon",
            "CardBox_Actions",
            "CardBox_Riders",
            "CardBox_Ambassadors",
            "HexBox",
        }
        for name in expected:
            self.assertIn(name, labels)

    def test_automatic_spacers_generated(self) -> None:
        """Verify automatic spacers or volumetric packing."""
        build = project.build()
        spacers = [p for p in build.pieces if "spacer" in p.label.lower() or p.kind == "spacer"]
        total_vol = sum(p.size[0] * p.size[1] * p.size[2] for p in build.pieces if p.size)
        box_vol = box_width * box_length * box_height
        self.assertTrue(len(spacers) > 0 or total_vol / box_vol > 0.4)

    def test_all_pieces_fit_within_box_bounds(self) -> None:
        """Verify no piece overflows the physical box dimensions."""
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
            self.assertLessEqual(z + h, box_height + tol, f"{piece.label} overflows box height ({z+h} > {box_height})")
