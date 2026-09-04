#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Explorers of Navoria: Forgotten Lands expansion organizer.

Ports examples/explorers_of_navoria_forgotten_lands.scad to the pyboxbuilder Project API.
Organizes 5th player (White) pieces, faction skill boards, exploration tiles,
and expansion cards with automated spacers.
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
    run,
)

# ── Box & Board Dimensions ────────────────────────────────────────
box_width = 211.0
box_length = 268.0
box_height = 50.0

board_thickness = 4.0
usable_height = box_height - board_thickness  # 46.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

player_box_width = 98.0
player_box_length = (box_length - 2.0) / 2.0  # 133.0mm
player_box_height = usable_height / 2.0       # 23.0mm

card_width = 68.0
card_length = 92.0

faction_skill_box_width = 67.0
faction_skill_box_length = 150.0
faction_skill_box_height = usable_height / 2.0  # 23.0mm

bits_box_width = box_width - player_box_width - 2.0  # 111.0mm
bits_box_length = faction_skill_box_length
bits_box_height = usable_height / 2.0

card_box_width = bits_box_width
card_box_length = box_length - faction_skill_box_length - 2.0  # 116.0mm
card_box_height = usable_height

project = Project(
    "ExplorersOfNavoriaForgottenLands",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

NAVORIA_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. 5th Player & Species Tokens (Column 0, X = 0) ──────────────
project.box(
    BoxType.CAP,
    "PlayerBox_White",
    size=(player_box_width, player_box_length, player_box_height),
    lid=LidBuilder(
        text="Player (White)",
        label_mode=LabelMode.FRAMED,
        pattern=NAVORIA_PATTERN,
        text_color=Color("black"),
        frame_color=Color("white"),
    ),
    position=(0.0, 0.0, 0.0),
    no_rotate=True,
).compartment(
    "TradingPosts",
    depth=player_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

project.box(
    BoxType.CAP,
    "SpeciesTokensBox",
    size=(player_box_width, player_box_length, player_box_height),
    lid=LidBuilder(
        text="Species Tokens",
        label_mode=LabelMode.FRAMED,
        pattern=NAVORIA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("peru"),
    ),
    position=(0.0, 0.0, player_box_height),
    no_rotate=True,
).compartment(
    "Tokens",
    depth=player_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── 2. Faction Skills & Bits (Column 1, X = player_box_width) ─────
x_col1 = player_box_width

project.box(
    BoxType.CAP,
    "FactionSkillBox",
    size=(bits_box_width, bits_box_length, bits_box_height),
    lid=LidBuilder(
        text="Faction Skills",
        label_mode=LabelMode.FRAMED,
        pattern=NAVORIA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("purple"),
    ),
    position=(x_col1, 0.0, 0.0),
    no_rotate=True,
).compartment(
    "FactionTiles",
    depth=bits_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

project.box(
    BoxType.CAP,
    "ExplorationBitsBox",
    size=(bits_box_width, bits_box_length, bits_box_height),
    lid=LidBuilder(
        text="Exploration Bits",
        label_mode=LabelMode.FRAMED,
        pattern=NAVORIA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkorange"),
    ),
    position=(x_col1, 0.0, bits_box_height),
    no_rotate=True,
).compartment(
    "Bits",
    depth=bits_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── 3. Expansion Adventure Cards (Column 1, Y = bits_box_length) ──
y_cards = bits_box_length

project.box(
    BoxType.SLIDING,
    "ExpansionCardsBox",
    size=(card_box_width, card_box_length, card_box_height),
    lid=LidBuilder(
        text="Forgotten Cards",
        label_mode=LabelMode.FRAMED,
        pattern=NAVORIA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("navy"),
    ),
    position=(x_col1, y_cards, 0.0),
    no_rotate=True,
).compartment(
    "Cards",
    depth=card_box_height - lid_thickness,
    cut=FingerCut.SCOOP,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
