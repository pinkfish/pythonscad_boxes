# SPDX-License-Identifier: Apache-2.0
"""Tests for Project high-level preset box methods."""

import unittest

from pyboxbuilder import BoxType, CardSize, Project, ScoopSide, SleeveType


class PresetTests(unittest.TestCase):
    def test_card_box_preset(self) -> None:
        p = Project("PresetCardTest", game_box_size=(300, 300, 80))
        builder = p.card_box(
            "MyDeck",
            card_size=CardSize.STANDARD_GAME,
            count=100,
            sleeve=SleeveType.PREMIUM_100MY,
            box_type=BoxType.SLIDING,
        )
        self.assertEqual(builder.label, "MyDeck")
        self.assertEqual(builder.box_type, BoxType.SLIDING)
        self.assertEqual(len(builder.compartments), 1)
        comp = builder.compartments[0]
        self.assertEqual(comp.label, "Cards")

    def test_token_tray_preset_default(self) -> None:
        p = Project("PresetTokenTest", game_box_size=(300, 300, 80))
        builder = p.token_tray(
            "MyTokens",
            rows=2,
            cols=3,
        )
        self.assertEqual(builder.box_type, BoxType.FILAMENT_HINGE)

    def test_token_tray_preset(self) -> None:
        p = Project("PresetTokenTest", game_box_size=(300, 300, 80))
        builder = p.token_tray(
            "MyTokens",
            rows=2,
            cols=3,
            scoop_side=ScoopSide.LEFT,
            box_type=BoxType.NO_LID,
        )
        self.assertEqual(builder.label, "MyTokens")
        self.assertEqual(builder.box_type, BoxType.NO_LID)
        self.assertEqual(len(builder.compartments), 6)
        # All 6 compartments should be created and have their ratios set
        for comp in builder.compartments:
            self.assertAlmostEqual(comp.width_ratio, 1.0 / 3)
            self.assertAlmostEqual(comp.length_ratio, 1.0 / 2)
            self.assertEqual(comp.cut.side, ScoopSide.LEFT)

    def test_hex_tile_box_preset(self) -> None:
        p = Project("PresetHexTest", game_box_size=(300, 300, 80))
        builder = p.hex_tile_box(
            "MyHexes",
            tile_width=45.0,
            count=10,
            box_type=BoxType.SLIDING,
        )
        self.assertEqual(builder.label, "MyHexes")
        self.assertEqual(builder.box_type, BoxType.SLIDING)
        self.assertEqual(len(builder.compartments), 1)
        comp = builder.compartments[0]
        self.assertEqual(comp.label, "Tiles")
        self.assertEqual(len(comp.elements), 1)
        self.assertEqual(comp.elements[0].size, (45.0, 45.0))
