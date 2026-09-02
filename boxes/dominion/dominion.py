#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Dominion Big Box organizer.

Ports examples/dominion.scad to the pyboxbuilder Project API.
Organizes base game kingdom cards, money and victory supply decks,
Alchemy/Prosperity expansion decks, mats, and tokens.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd()
sys.path.insert(0, str(ROOT))
for _sp in ROOT.glob(".venv/lib/*/site-packages"):
    sys.path.insert(0, str(_sp))
for _sp in ROOT.glob("venv/*/lib/*/site-packages"):
    sys.path.insert(0, str(_sp))

from pybosl2 import Color

from pyboxbuilder import (
    BoxType,
    FingerCut,
    LabelMode,
    LidBuilder,
    PatternBuilder,
    PatternType,
    Project,
    columns,
    run,
    stack,
)

# ── Game Box Dimensions (Big Box) ─────────────────────────────────
box_width = 470.0
box_length = 290.0
box_height = 90.0

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 3.0

# ── Card Dimensions ───────────────────────────────────────────────
card_width = 62.0
card_length = 93.0

card_box_width = card_length + wall_thickness * 2.0 + 2.0  # 101.0mm
all_boxes_height = 75.0                                    # standard card library height

base_cards_len = 230.0
money_victory_len = 200.0
alchemy_cards_len = 80.0

project = Project(
    "DominionBigBox",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    generate_spacers=True,
)

DOMINION_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Base Game Kingdom Cards Box ────────────────────────────────
base_box = project.box(
    BoxType.SLIDING,
    "BaseKingdomCards",
    size=(card_box_width, base_cards_len, all_boxes_height),
    lid=LidBuilder(
        text="Dominion: Kingdom Cards",
        label_mode=LabelMode.FRAMED,
        pattern=DOMINION_PATTERN,
        text_color=Color("white"),
        frame_color=Color("royalblue"),
    ),
    position=(0.0, 0.0, 0.0),
    no_rotate=True,
)
base_box.compartment(
    "KingdomDecks",
    depth=all_boxes_height - lid_thickness,
    cut=FingerCut.SCOOP,
)

# ── 2. Treasure & Victory Cards Box ───────────────────────────────
treasure_box = project.box(
    BoxType.SLIDING,
    "TreasureAndVictoryCards",
    size=(card_box_width, money_victory_len, all_boxes_height),
    lid=LidBuilder(
        text="Treasure & Victory",
        label_mode=LabelMode.FRAMED,
        pattern=DOMINION_PATTERN,
        text_color=Color("white"),
        frame_color=Color("gold"),
    ),
    position=(card_box_width, 0.0, 0.0),
    no_rotate=True,
)
treasure_box.compartment(
    "TreasuresAndVictory",
    depth=all_boxes_height - lid_thickness,
    cut=FingerCut.SCOOP,
)

# ── 3. Alchemy & Expansion Cards Box ──────────────────────────────
alchemy_box = project.box(
    BoxType.SLIDING,
    "AlchemyExpansionCards",
    size=(card_box_width, alchemy_cards_len, all_boxes_height),
    lid=LidBuilder(
        text="Alchemy & Expansions",
        label_mode=LabelMode.FRAMED,
        pattern=DOMINION_PATTERN,
        text_color=Color("white"),
        frame_color=Color("purple"),
    ),
    position=(card_box_width, money_victory_len, 0.0),
    no_rotate=True,
)
alchemy_box.compartment(
    "AlchemyCards",
    depth=all_boxes_height - lid_thickness,
    cut=FingerCut.SCOOP,
)

# ── 4. Token, Coin & Mat Trays (Column 3) ─────────────────────────
token_box_width = card_box_width
token_tray_len = (money_victory_len + alchemy_cards_len) / 2.0  # 140.0mm
token_tray_height = all_boxes_height / 2.0                     # 37.5mm

for idx, label in enumerate(["CoinAndDebtTokens", "MatsAndSpecialTokens"], start=1):
    tray = project.box(
        BoxType.CAP,
        f"TokenTray{idx}_{label}",
        size=(token_box_width, token_tray_len, token_tray_height),
        lid=LidBuilder(
            text=label,
            label_mode=LabelMode.FRAMED,
            pattern=DOMINION_PATTERN,
            text_color=Color("white"),
            frame_color=Color("darkslategray"),
        ),
        position=(card_box_width * 2.0, (idx - 1) * token_tray_len, 0.0),
        no_rotate=True,
    )
    tray.compartment(
        "Tokens_Left",
        width_ratio=0.5,
        depth=token_tray_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )
    tray.compartment(
        "Tokens_Right",
        width_ratio=0.5,
        depth=token_tray_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
