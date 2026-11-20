# SPDX-License-Identifier: Apache-2.0
"""Tests for the Brink board game insert."""

import unittest

from boxes.brink.brink import (
    box_height,
    box_length,
    box_width,
    project,
)


class TestBrink(unittest.TestCase):
    """Test suite for Brink project build and layout."""

    def test_build_completes(self) -> None:
        """Verify the project builds all pieces without errors."""
        build = project.build()
        self.assertGreater(len(build.pieces), 8)

    def test_box_labels_present(self) -> None:
        """Verify all essential box labels are generated."""
        labels = {b.label for b in project._boxes}
        expected = {
            "HexBox",
            "PlayerBox_Solari",
            "PlayerBox_Vanguard",
            "PlayerBox_Eclipse",
            "PlayerBox_Horizon",
            "CardBox_Actions",
            "CardBox_Riders",
            "CardBox_Ambassadors",
            "CardBox_Factions",
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

    def test_player_box_contains_all_piece_spaces(self) -> None:
        """Verify PlayerBox includes all piece cutouts from brink.scad."""
        p_box = next(b for b in project._boxes if b.label == "PlayerBox_Solari")
        element_labels = {el.label for comp in p_box.compartments for el in comp.elements}
        expected = {
            "UpgradeBoard",
            "ClassIShip",
            "ClassIIShip",
            "ClassIIIShip",
            "Cargo_1",
            "Cargo_2",
            "Cargo_3",
            "CargoNub_1",
            "Railgun_1",
            "Railgun_2",
            "Railgun_3",
            "RailgunNub_1",
            "PlayerTokens",
        }
        for name in expected:
            self.assertIn(name, element_labels)

    def test_card_boxes_slide_along_x_matching_scoop_side(self) -> None:
        """Verify sliding card boxes open on the short wall (RIGHT) matching the scoop."""
        from pyboxbuilder.enums import ScoopSide

        project.build()
        for box in project._manifest.boxes:
            if not box.label.startswith("CardBox_"):
                continue
            resolved = project._pipeline._resolve_box(project._manifest, box)
            self.assertEqual(resolved.spec.lid_slide_axis, "x")
            self.assertIs(resolved.box.preferred_scoop_side(resolved.spec), ScoopSide.RIGHT)
