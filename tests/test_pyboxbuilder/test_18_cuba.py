# SPDX-License-Identifier: Apache-2.0
"""Tests for the 18Cuba board game insert."""

import importlib.util
from pathlib import Path
import unittest

_PATH = Path(__file__).resolve().parents[2] / "boxes" / "18_cuba" / "18_cuba.py"
_SPEC = importlib.util.spec_from_file_location("cuba_mod", _PATH)
cuba_mod = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(cuba_mod)

project = cuba_mod.project
box_width = cuba_mod.box_width
box_length = cuba_mod.box_length
box_height = cuba_mod.box_height


class Test18Cuba(unittest.TestCase):
    """Test suite for 18Cuba project build and layout."""

    def test_build_completes(self) -> None:
        """Verify the project builds all pieces without errors."""
        build = project.build()
        self.assertGreater(len(build.pieces), 5)

    def test_box_labels_present(self) -> None:
        """Verify all essential box labels are generated."""
        labels = {b.label for b in project._boxes}
        expected = {
            "MoneyBox_1",
            "MoneyBox_2",
            "TrainBox",
            "SharesBox_1",
            "SharesBox_2",
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
