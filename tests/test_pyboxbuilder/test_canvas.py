# SPDX-License-Identifier: Apache-2.0
"""Tests for the Canvas board game insert."""

import unittest

from boxes.canvas.canvas import (
    box_height,
    box_length,
    box_width,
    project,
)


class TestCanvas(unittest.TestCase):
    """Test suite for Canvas project build and layout."""

    def test_build_completes(self) -> None:
        """Verify the project builds all pieces without errors."""
        build = project.build()
        self.assertGreater(len(build.pieces), 6)

    def test_box_labels_present(self) -> None:
        """Verify all essential box labels are generated."""
        labels = {b.label for b in project._boxes}
        expected = {
            "RibbonBox_Red",
            "RibbonBox_Green",
            "RibbonBox_Grey",
            "RibbonBox_Blue",
            "RibbonBox_Purple",
            "RibbonBox_Palette",
            "PlaymatDivider",
        }
        for name in expected:
            self.assertIn(name, labels)

    def test_center_playmat_channel_kept_open(self) -> None:
        """Verify the 50mm center channel down the middle is open for the rolled playmat."""
        build = project.build()
        spacers = [p for p in build.pieces if "spacer" in p.label.lower() or p.kind == "spacer"]
        self.assertEqual(len(spacers), 0)
        for piece in build.pieces:
            if piece.position is None or piece.size is None or piece.label == "PlaymatDivider":
                continue
            x, _y, _z = piece.position
            w, _l, _h = piece.size
            # Ribbon boxes must stay strictly outside the X = 73..123mm playmat channel
            self.assertTrue(
                x + w <= 73.0 + 1e-3 or x >= 123.0 - 1e-3,
                f"{piece.label} intrudes into center playmat channel ({x}..{x + w})",
            )

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
