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

from pyboxbuilder import (
    BoxType,
    Color,
    FingerCut,
    LabelFinial,
    LabelMode,
    LabelShape,
    LidBuilder,
    PatternBuilder,
    PatternType,
    Project,
    run,
)

SVG_DIR = (
    Path(__file__).resolve().parent / "svg"
    if "__file__" in globals()
    else ROOT / "boxes" / "dominion" / "svg"
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
    box_defaults={"expandable": False},
)

# ── Game Component Inventory (cards stored upright along Y) ───────
project.component("Base Kingdom Cards", 260, kind="cards", size=(card_width, card_length), bulk=True)
project.component("Treasure & Victory Supply Cards", 250, kind="cards", size=(card_width, card_length), bulk=True)
project.component("Alchemy & Expansion Kingdom Cards", 120, kind="cards", size=(card_width, card_length), bulk=True)
project.define_piece("Metal Coin Tokens", 50, bulk=True)
project.define_piece("Debt Tokens", 50, bulk=True)
project.define_tile("Player Mats", 12, bulk=True)
project.define_piece("Special Tokens", 30, bulk=True)

DOMINION_PATTERN = PatternBuilder(PatternType.OCTAGON)
DOMINION_FONT = "Georgia:style=Bold"

# ── 1. Base Game Kingdom Cards Box ────────────────────────────────
base_box = project.box(
    BoxType.SLIDING,
    "BaseKingdomCards",
    size=(card_box_width, base_cards_len, all_boxes_height),
    lid=LidBuilder(
        text="Dominion: Kingdom Cards",
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.SCROLL,
        label_finial=LabelFinial.FLEURON,
        font=DOMINION_FONT,
        pattern=DOMINION_PATTERN,
        text_color=Color("white"),
        frame_color=Color("royalblue"),
        logo=str(SVG_DIR / "dominion.svg"),
        logo_color=Color("white"),
        logo_position="left",
        label_logo_size_mm=16.0,
    ),
)
base_box.compartment(
    "KingdomDecks",
    cut=FingerCut.SCOOP,
    component="Base Kingdom Cards",
    count=260,
)

# ── 2. Treasure & Victory Cards Box ───────────────────────────────
treasure_box = project.box(
    BoxType.SLIDING,
    "TreasureAndVictoryCards",
    size=(card_box_width, money_victory_len, all_boxes_height),
    lid=LidBuilder(
        text="Treasure & Victory",
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.SHIELD,
        label_finial=LabelFinial.FLEURON,
        font=DOMINION_FONT,
        pattern=DOMINION_PATTERN,
        text_color=Color("white"),
        frame_color=Color("gold"),
        logo=str(SVG_DIR / "prosperity-2ed.svg"),
        logo_color=Color("white"),
        logo_position="left",
        label_logo_size_mm=16.0,
    ),
)
treasure_box.compartment(
    "TreasuresAndVictory",
    cut=FingerCut.SCOOP,
    component="Treasure & Victory Supply Cards",
    count=250,
)

# ── 3. Alchemy & Expansion Cards Box ──────────────────────────────
alchemy_box = project.box(
    BoxType.SLIDING,
    "AlchemyExpansionCards",
    size=(card_box_width, alchemy_cards_len, all_boxes_height),
    lid=LidBuilder(
        text="Alchemy & Expansions",
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.SHIELD,
        label_finial=LabelFinial.FLEURON,
        font=DOMINION_FONT,
        pattern=DOMINION_PATTERN,
        text_color=Color("white"),
        frame_color=Color("purple"),
        logo=str(SVG_DIR / "alchemy.svg"),
        logo_color=Color("white"),
        logo_position="left",
        label_logo_size_mm=15.0,
    ),
)
alchemy_box.compartment(
    "AlchemyCards",
    cut=FingerCut.SCOOP,
    component="Alchemy & Expansion Kingdom Cards",
    count=120,
)

# ── 4. Token, Coin & Mat Trays ────────────────────────────────────
token_box_width = card_box_width
token_tray_len = (money_victory_len + alchemy_cards_len) / 2.0  # 140.0mm
token_tray_height = all_boxes_height / 2.0                     # 37.5mm

for idx, (label, svg_name, left_item, right_item) in enumerate(
    [
        ("CoinAndDebtTokens", "debt.svg", ("Metal Coin Tokens", 50), ("Debt Tokens", 50)),
        ("MatsAndSpecialTokens", "guilds.svg", ("Player Mats", 12), ("Special Tokens", 30)),
    ],
    start=1,
):
    tray = project.box(
        BoxType.CAP,
        f"TokenTray{idx}_{label}",
        size=(token_box_width, token_tray_len, token_tray_height),
        lid=LidBuilder(
            text=label,
            label_mode=LabelMode.FRAMED,
            label_shape=LabelShape.SCROLL,
            label_finial=LabelFinial.FLEURON,
            font=DOMINION_FONT,
            pattern=DOMINION_PATTERN,
            text_color=Color("white"),
            frame_color=Color("darkslategray"),
            logo=str(SVG_DIR / svg_name),
            logo_color=Color("white"),
            logo_position="left",
            label_logo_size_mm=15.0,
        ),
    )
    tray.compartment(
        "Tokens_Left",
        width_ratio=0.5,
        cut=FingerCut.SCOOP,
        component=left_item[0],
        count=left_item[1],
    )
    tray.compartment(
        "Tokens_Right",
        width_ratio=0.5,
        cut=FingerCut.SCOOP,
        component=right_item[0],
        count=right_item[1],
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
