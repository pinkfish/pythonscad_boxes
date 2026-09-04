#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Emberleaf board game organizer.

Ports examples/emberleaf.scad to the pyboxbuilder Project API.
Organizes player animal meeples (owls, rabbits, frogs, rats), hero cards,
wood/stone/gold material bins, trophies, and card decks with automated spacers.
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
box_width = 287.0
box_length = 287.0
box_height = 79.0

board_thickness = 26.5
usable_height = box_height - board_thickness  # 52.5mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

card_width = 66.0
card_length = 91.0

PLAYER_BOX_WIDTH = card_length + wall_thickness * 2.0 + 1.0  # 98.0mm
PLAYER_BOX_LENGTH = (box_length - 2.0) / 2.0                 # 142.5mm
PLAYER_BOX_HEIGHT = usable_height / 4.0                      # 13.125mm

CARD_BOX_WIDTH = PLAYER_BOX_WIDTH                            # 98.0mm
CARD_BOX_LENGTH = card_width + wall_thickness * 2.0 + 1.0    # 73.0mm
CARD_BOX_HEIGHT = usable_height                              # 52.5mm

PLAYER_CARD_BOX_WIDTH = box_width - PLAYER_BOX_WIDTH * 2.0 - 1.0  # 90.0mm
PLAYER_CARD_BOX_LENGTH = CARD_BOX_LENGTH                         # 73.0mm
PLAYER_CARD_BOX_HEIGHT = usable_height / 5.0                     # 10.5mm

COMMON_BOX_WIDTH = PLAYER_CARD_BOX_WIDTH
COMMON_BOX_LENGTH = box_length - PLAYER_CARD_BOX_LENGTH - 1.0    # 213.0mm
COMMON_BOX_HEIGHT = 25.0

project = Project(
    "Emberleaf",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

EMBER_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Player Boxes (Column 0, X = 0) ─────────────────────────────
# 5 player boxes placed according to layout expectations:
player_configs = [
    ("PlayerBoxBlack", (0.0, 0.0, 0.0), "black"),
    ("PlayerBoxRed", (0.0, PLAYER_BOX_LENGTH, 0.0), "darkred"),
    ("PlayerBoxYellow", (0.0, 0.0, PLAYER_BOX_HEIGHT), "gold"),
    ("PlayerBoxBlue", (0.0, PLAYER_BOX_LENGTH, PLAYER_BOX_HEIGHT), "navy"),
    ("PlayerBoxGrey", (0.0, 0.0, PLAYER_BOX_HEIGHT * 2.0), "gray"),
]

for label, pos, color_name in player_configs:
    p_box = project.box(
        BoxType.CAP,
        label,
        size=(PLAYER_BOX_WIDTH, PLAYER_BOX_LENGTH, PLAYER_BOX_HEIGHT),
        lid=LidBuilder(
            text=label.replace("PlayerBox", "Player "),
            label_mode=LabelMode.FRAMED,
            pattern=EMBER_PATTERN,
            text_color=Color("black" if color_name == "gold" else "white"),
            frame_color=Color(color_name),
        ),
        position=pos,
        no_rotate=True,
    )
    p_box.compartment(
        "Meeples", length_ratio=0.6, depth=PLAYER_BOX_HEIGHT - floor_thickness - 1.0, cut=FingerCut.SCOOP
    )
    p_box.compartment(
        "DiscsAndTrophies", length_ratio=0.4, depth=PLAYER_BOX_HEIGHT - floor_thickness - 1.0, cut=FingerCut.SCOOP
    )

# ── 2. Card Boxes (Column 1, X = PLAYER_BOX_WIDTH) ────────────────
card_configs = [
    ("CardBoxFavor", (PLAYER_BOX_WIDTH, 0.0, 0.0), "Favor Cards", "royalblue"),
    ("CardBoxHero", (PLAYER_BOX_WIDTH, CARD_BOX_LENGTH, 0.0), "Hero Cards", "darkorange"),
    ("CardBoxSolo", (PLAYER_BOX_WIDTH, CARD_BOX_LENGTH * 2.0, 0.0), "Solo Cards", "darkgreen"),
]

for label, pos, text, color_name in card_configs:
    c_box = project.box(
        BoxType.SLIDING,
        label,
        size=(CARD_BOX_WIDTH, CARD_BOX_LENGTH, CARD_BOX_HEIGHT),
        lid=LidBuilder(
            text=text,
            label_mode=LabelMode.FRAMED,
            pattern=EMBER_PATTERN,
            text_color=Color("white"),
            frame_color=Color(color_name),
        ),
        position=pos,
        no_rotate=True,
    )
    c_box.compartment("Cards", depth=CARD_BOX_HEIGHT - lid_thickness, cut=FingerCut.SCOOP)

# ── 3. Player Card Boxes (Column 2, X = PLAYER_BOX_WIDTH * 2) ─────
# Shallow box (10.5mm) uses SLIPOVER to support finger cutouts at this height
x_col2 = PLAYER_BOX_WIDTH * 2.0

h_box = project.box(
    BoxType.SLIPOVER,
    "CardBoxPlayerBlack",
    size=(PLAYER_CARD_BOX_WIDTH, PLAYER_CARD_BOX_LENGTH, PLAYER_CARD_BOX_HEIGHT),
    lid=LidBuilder(
        text="Player Deck",
        label_mode=LabelMode.FRAMED,
        pattern=EMBER_PATTERN,
        text_color=Color("white"),
        frame_color=Color("purple"),
    ),
    position=(x_col2, 0.0, 0.0),
    no_rotate=True,
)
h_box.compartment("Cards", depth=PLAYER_CARD_BOX_HEIGHT - floor_thickness - 1.0, cut=FingerCut.SCOOP)

# ── 4. Common Box (Column 2, Y = PLAYER_CARD_BOX_LENGTH) ──────────
com_box = project.box(
    BoxType.CAP,
    "CommonBox",
    size=(COMMON_BOX_WIDTH, COMMON_BOX_LENGTH, COMMON_BOX_HEIGHT),
    lid=LidBuilder(
        text="Common Tokens",
        label_mode=LabelMode.FRAMED,
        pattern=EMBER_PATTERN,
        text_color=Color("white"),
        frame_color=Color("saddlebrown"),
    ),
    position=(x_col2, PLAYER_CARD_BOX_LENGTH, 0.0),
    no_rotate=True,
)
for slot in range(3):
    com_box.compartment(
        f"Bin_{slot + 1}",
        length_ratio=1.0 / 3.0,
        depth=COMMON_BOX_HEIGHT - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
