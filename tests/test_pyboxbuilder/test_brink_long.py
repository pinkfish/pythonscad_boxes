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
            "FleetKomek",
            "FleetVentus",
            "FleetHenko",
            "FleetMagnomi",
            "FleetSorelia",
            "CardBox_Actions",
            "CardBox_Riders",
            "CardBox_Ambassadors",
            "HexBox",
        }
        for name in expected:
            self.assertIn(name, labels)

    def test_faction_lids_use_logo_instead_of_text(self) -> None:
        """Verify each long fleet lid uses its faction SVG logo instead of text."""
        from pathlib import Path

        fleet_boxes = [b for b in project._boxes if b.label.startswith("Fleet")]
        self.assertEqual(len(fleet_boxes), 5)
        for box in fleet_boxes:
            self.assertIsNotNone(box.lid)
            assert box.lid is not None
            self.assertIsNone(box.lid.text, f"{box.label} lid should use logo instead of text")
            self.assertIsInstance(box.lid.logo, str)
            self.assertTrue(Path(box.lid.logo).is_file(), f"Missing SVG logo for {box.label}: {box.lid.logo}")

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

    def test_fleet_box_contains_all_piece_spaces(self) -> None:
        """Verify long player fleet trays include all piece cutouts from brink_long.scad."""
        p_box = next(b for b in project._boxes if b.label == "FleetKomek")
        element_labels = {el.label for comp in p_box.compartments for el in comp.elements}
        expected = {
            "UpgradeBoard",
            "ClassIShip",
            "ClassIIShip",
            "ClassIIIShip",
            "Cargo_1",
            "Cargo_2",
            "Cargo_3",
            "Railgun_1",
            "Railgun_2",
            "Railgun_3",
            "PlayerTokens",
            "PlayerTokensFingerAccess",
            "VotingBoard",
            "VotingBay_1",
            "VotingBay_5",
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
