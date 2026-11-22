#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Emberleaf board game organizer.

Ports boxes/emberleaf/emberleaf.scad to the pyboxbuilder Project API.
Organizes 5 player animal meeple boxes (black, red, yellow, blue, grey),
4 material boxes (food, stone, honey, wood), 3 main card boxes (favors,
heroes, solo), 5 player deck boxes, and the common trophy/hex box with
automatic spacers.
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

# ── Component Dimensions ──────────────────────────────────────────
card_width = 66.0
card_length = 91.0
cardboard_token_thickness = 2.0

# ── Sub-Box Dimensions (matching emberleaf.scad) ──────────────────
PLAYER_BOX_WIDTH = card_length + wall_thickness * 2.0 + 1.0  # 98.0mm
PLAYER_BOX_LENGTH = (box_length - 2.0) / 2.0  # 142.5mm
PLAYER_BOX_HEIGHT = usable_height / 4.0  # 13.125mm

MATERIAL_BOX_WIDTH = PLAYER_BOX_WIDTH  # 98.0mm
MATERIAL_BOX_LENGTH = PLAYER_BOX_LENGTH / 2.0  # 71.25mm
MATERIAL_BOX_HEIGHT = PLAYER_BOX_HEIGHT  # 13.125mm

CARD_BOX_WIDTH = PLAYER_BOX_WIDTH  # 98.0mm
CARD_BOX_LENGTH = card_width + wall_thickness * 2.0 + 1.0  # 73.0mm
CARD_BOX_HEIGHT = usable_height  # 52.5mm

PLAYER_CARD_BOX_WIDTH = box_width - PLAYER_BOX_WIDTH - CARD_BOX_WIDTH - 1.0  # 90.0mm
PLAYER_CARD_BOX_LENGTH = card_length + wall_thickness * 2.0 + 1.0  # 98.0mm
PLAYER_CARD_BOX_HEIGHT = usable_height / 5.0  # 10.5mm

COMMON_BOX_WIDTH = PLAYER_CARD_BOX_WIDTH  # 90.0mm
COMMON_BOX_LENGTH = box_length - PLAYER_CARD_BOX_LENGTH - 1.0  # 188.0mm
COMMON_BOX_HEIGHT = lid_thickness + floor_thickness + cardboard_token_thickness * 10.0 + 1.0  # 25.0mm

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

# ── Column 0: 5 Player Boxes & 4 Material Boxes (X = 0 .. 98) ─────
player_placements = [
    ("PlayerBoxBlack", "black", (0.0, 0.0, 0.0)),
    ("PlayerBoxRed", "darkred", (0.0, PLAYER_BOX_LENGTH, 0.0)),
    ("PlayerBoxYellow", "gold", (0.0, 0.0, PLAYER_BOX_HEIGHT)),
    ("PlayerBoxBlue", "navy", (0.0, PLAYER_BOX_LENGTH, PLAYER_BOX_HEIGHT)),
    ("PlayerBoxGrey", "gray", (0.0, 0.0, PLAYER_BOX_HEIGHT * 2.0)),
]

for label, color_name, pos in player_placements:
    p_box = project.box(
        BoxType.CAP,
        label,
        size=(PLAYER_BOX_WIDTH, PLAYER_BOX_LENGTH, PLAYER_BOX_HEIGHT),
        position=pos,
        lid=LidBuilder(
            text=label.replace("PlayerBox", "Player "),
            label_mode=LabelMode.FRAMED,
            pattern=EMBER_PATTERN,
            text_color=Color("black" if color_name == "gold" else "white"),
            frame_color=Color(color_name),
        ),
    )
    p_box.compartment("WorkersAndHero", length_ratio=0.65, cut=FingerCut.SCOOP)
    p_box.compartment("HexesAndVictory", length_ratio=0.35, cut=FingerCut.SCOOP)

material_placements = [
    ("MaterialBoxFood", "Food", "red", (0.0, PLAYER_BOX_LENGTH, PLAYER_BOX_HEIGHT * 2.0)),
    ("MaterialBoxStone", "Stone", "gray", (0.0, PLAYER_BOX_LENGTH + MATERIAL_BOX_LENGTH, PLAYER_BOX_HEIGHT * 2.0)),
    ("MaterialBoxHoney", "Honey", "gold", (0.0, 0.0, PLAYER_BOX_HEIGHT * 3.0)),
    ("MaterialBoxWood", "Wood", "saddlebrown", (0.0, MATERIAL_BOX_LENGTH, PLAYER_BOX_HEIGHT * 3.0)),
]

for label, text, color_name, pos in material_placements:
    project.box(
        BoxType.CAP,
        label,
        size=(MATERIAL_BOX_WIDTH, MATERIAL_BOX_LENGTH, MATERIAL_BOX_HEIGHT),
        position=pos,
        lid=LidBuilder(
            text=text,
            label_mode=LabelMode.FRAMED,
            pattern=EMBER_PATTERN,
            text_color=Color("black" if color_name == "gold" else "white"),
            frame_color=Color(color_name),
        ),
    ).compartment("Tokens", cut=FingerCut.SCOOP)

# ── Column 1: Main Card Boxes (X = 98 .. 196) ─────────────────────
card_configs = [
    ("CardBoxFavor", "Favors", "royalblue", 0),
    ("CardBoxHero", "Heroes", "darkorange", 1),
    ("CardBoxSolo", "Solo", "darkgreen", 2),
]

for label, text, color_name, row_idx in card_configs:
    project.box(
        BoxType.SLIDING,
        label,
        size=(CARD_BOX_WIDTH, CARD_BOX_LENGTH, CARD_BOX_HEIGHT),
        position=(PLAYER_BOX_WIDTH, CARD_BOX_LENGTH * row_idx, 0.0),
        lid=LidBuilder(
            text=text,
            label_mode=LabelMode.FRAMED,
            pattern=EMBER_PATTERN,
            text_color=Color("white"),
            frame_color=Color(color_name),
        ),
    ).compartment("Cards", cut=FingerCut.SCOOP)

# ── Column 2: 5 Player Card Boxes & Common Box (X = 196 .. 286) ───
col2_x = PLAYER_BOX_WIDTH + CARD_BOX_WIDTH

player_card_configs = [
    ("CardBoxPlayerBlack", "Player Black", "black"),
    ("CardBoxPlayerBlue", "Player Blue", "navy"),
    ("CardBoxPlayerYellow", "Player Yellow", "gold"),
    ("CardBoxPlayerGrey", "Player Grey", "gray"),
    ("CardBoxPlayerRed", "Player Red", "darkred"),
]

for layer_idx, (label, text, color_name) in enumerate(player_card_configs):
    project.box(
        BoxType.SLIDING,
        label,
        size=(PLAYER_CARD_BOX_WIDTH, PLAYER_CARD_BOX_LENGTH, PLAYER_CARD_BOX_HEIGHT),
        position=(col2_x, 0.0, PLAYER_CARD_BOX_HEIGHT * layer_idx),
        lid=LidBuilder(
            text=text,
            label_mode=LabelMode.FRAMED,
            pattern=EMBER_PATTERN,
            text_color=Color("black" if color_name == "gold" else "white"),
            frame_color=Color(color_name),
        ),
    ).compartment("Cards", cut=FingerCut.SCOOP)

com_box = project.box(
    BoxType.CAP,
    "CommonBox",
    size=(COMMON_BOX_WIDTH, COMMON_BOX_LENGTH, COMMON_BOX_HEIGHT),
    position=(col2_x, PLAYER_CARD_BOX_LENGTH, 0.0),
    lid=LidBuilder(
        text="Trophy",
        label_mode=LabelMode.FRAMED,
        pattern=EMBER_PATTERN,
        text_color=Color("white"),
        frame_color=Color("saddlebrown"),
    ),
)
com_box.compartment("CommonHexes", length_ratio=0.72, cut=FingerCut.SCOOP)
com_box.compartment("Trophies", length_ratio=0.28, cut=FingerCut.SCOOP)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
