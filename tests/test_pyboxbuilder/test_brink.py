# SPDX-License-Identifier: Apache-2.0
"""Tests for the Brink board game insert."""

import unittest
from pathlib import Path

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
        self.assertGreater(len(build.pieces), 35)

    def test_box_labels_present(self) -> None:
        """Verify all essential box labels from brink.scad are generated."""
        labels = {b.label for b in project._boxes}
        expected = {
            "HexBox",
            "HexBonusBox",
            "PlayerBox_Yellow",
            "PlayerBox_Orange",
            "PlayerBox_Purple",
            "PlayerBox_Blue",
            "PlayerBox_Green",
            "ResourceBox_Komek",
            "ResourceBox_Ventus",
            "ResourceBox_Henko",
            "ResourceBox_Magnomi",
            "ResourceBox_Sorelia",
            "ResourceBox_UA",
            "CardBox_Actions",
            "CardBox_Riders",
            "CardBox_Ambassadors",
            "CardBox_Factions",
            "CardBox_Rivals",
            "CardBox_Community",
            "CardBox_Holo",
        }
        for name in expected:
            self.assertIn(name, labels)

    def test_faction_resource_lids_use_logo_instead_of_text(self) -> None:
        """Verify each faction/UA resource cube box lid uses its SVG logo instead of text."""
        resource_boxes = [b for b in project._boxes if b.label.startswith("ResourceBox_")]
        self.assertEqual(len(resource_boxes), 6)
        for box in resource_boxes:
            self.assertIsNotNone(box.lid)
            assert box.lid is not None
            self.assertIsNone(box.lid.text, f"{box.label} lid should use logo instead of text")
            self.assertIsInstance(box.lid.logo, str)
            self.assertTrue(Path(box.lid.logo).is_file(), f"Missing SVG logo for {box.label}: {box.lid.logo}")

    def test_automatic_spacers_generated(self) -> None:
        """Verify automatic spacers are generated and no thin (< 10mm) wafer spacer exists."""
        build = project.build()
        spacers = [p for p in build.pieces if "spacer" in p.label.lower() or p.kind == "spacer"]
        self.assertGreater(len(spacers), 0)
        for sp in spacers:
            self.assertIsNotNone(sp.size)
            assert sp.size is not None
            self.assertGreaterEqual(sp.size[2], 10.0, f"{sp.label} is too thin ({sp.size[2]}mm)")

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
        p_box = next(b for b in project._boxes if b.label == "PlayerBox_Yellow")
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
            "PlayerTokensFingerAccess",
        }
        for name in expected:
            self.assertIn(name, element_labels)

        by_label = {el.label: el for comp in p_box.compartments for el in comp.elements}
        r3_x0, r3_y0, r3_x1, r3_y1 = by_label["Railgun_3"].bounds()
        c3_x0, c3_y0, c3_x1, c3_y1 = by_label["ClassIIIShip"].bounds()
        c3_cx = (c3_x0 + c3_x1) / 2.0
        half_w_at_r3 = ((r3_y1 - c3_y0) / (c3_y1 - c3_y0)) * ((c3_x1 - c3_x0) / 2.0)
        self.assertGreater(c3_cx - half_w_at_r3 - r3_x1, 3.0)

    def test_hex_boxes_have_three_hexagonal_cutouts(self) -> None:
        """Verify HexBox and HexBonusBox have 3 staggered 72mm hexagonal tile wells."""
        from pyboxbuilder.enums import ElementShape

        for label in ("HexBox", "HexBonusBox"):
            h_box = next(b for b in project._boxes if b.label == label)
            hex_els = [
                el
                for comp in h_box.compartments
                for el in comp.elements
                if el.shape is ElementShape.HEXAGON
            ]
            self.assertEqual(len(hex_els), 3, f"{label} should have 3 hexagonal cutouts")
            for el in hex_els:
                self.assertEqual(el.size, (72.0, 72.0))

    def test_card_boxes_slide_axis_matches_scoop_side(self) -> None:
        """Verify sliding card boxes open on the wall matching their finger scoop."""
        from pyboxbuilder.enums import ScoopSide

        project.build()
        for box in project._manifest.boxes:
            if not box.label.startswith("CardBox_"):
                continue
            resolved = project._pipeline._resolve_box(project._manifest, box)
            if box.label in ("CardBox_Actions", "CardBox_Riders"):
                self.assertEqual(resolved.spec.lid_slide_axis, "y")
                self.assertIs(resolved.box.preferred_scoop_side(resolved.spec), ScoopSide.BACK)
            else:
                self.assertEqual(resolved.spec.lid_slide_axis, "x")
                self.assertIs(resolved.box.preferred_scoop_side(resolved.spec), ScoopSide.RIGHT)
