# SPDX-License-Identifier: Apache-2.0
"""Tests for the Irish Gauge board game insert."""

import unittest

from boxes.irish_gauge.irish_gauge import (
    box_height,
    box_length,
    box_width,
    project,
)


class TestIrishGauge(unittest.TestCase):
    """Test suite for Irish Gauge project build and layout."""

    def test_build_completes(self) -> None:
        """Verify the project builds all pieces without errors."""
        build = project.build()
        self.assertGreater(len(build.pieces), 5)

    def test_box_labels_present(self) -> None:
        """Verify all essential box labels are generated."""
        labels = {b.label for b in project._boxes}
        expected = {
            "CompanyBox_Belfast",
            "CompanyBox_Cork",
            "CompanyBox_Midland",
            "CompanyBox_Waterford",
            "CompanyBox_GreatSouthern",
            "MoneyAndDividendsBox",
        }
        for name in expected:
            self.assertIn(name, labels)

    def test_automatic_spacers_generated(self) -> None:
        """Verify automatic spacers are generated from leftover volume."""
        build = project.build()
        spacers = [p for p in build.pieces if "spacer" in p.label.lower() or p.kind == "spacer"]
        self.assertGreater(len(spacers), 0)

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
