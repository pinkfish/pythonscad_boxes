#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Moonrakers board game organizer.

Ports examples/moonrakers.scad to the pyboxbuilder Project API.
Organizes command cards (Thrusters, Damage, Reactor, Shield, Miss),
contracts, crew, ship parts, objectives, and dice with automated spacers.
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
box_width = 213.0
box_length = 303.0
box_height = 93.0

board_thickness = 37.5  # Main board + player boards + Binding Ties expansion
usable_height = box_height - board_thickness  # 55.5mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

card_width = 67.0
card_length = 90.0

card_box_width = card_length + wall_thickness * 2.0  # 96.0mm
card_box_length = card_width + wall_thickness * 2.0  # 73.0mm
card_box_height = usable_height / 2.0                # 27.75mm

project = Project(
    "Moonrakers",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

MOON_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Command & Expansion Card Decks (2 columns of 4, stacked 2 high)
# 8 boxes across 2 columns along X (96mm * 2 = 192mm <= 213mm):
command_decks = [
    # Col 0
    [("Thrusters", "Thrusters", "gold"), ("Damage", "Damage", "darkred")],
    [("Reactor", "Reactor", "royalblue"), ("Shield", "Shield", "forestgreen")],
    [("Miss", "Miss", "gray"), ("Crew", "Crew", "purple")],
    [("Contracts", "Contracts", "darkorange"), ("Ships", "Ship Parts", "navy")],
]

for row_idx, row_pair in enumerate(command_decks):
    y_pos = row_idx * card_box_length
    for col_idx, (deck_id, title, color_name) in enumerate(row_pair):
        c_box = project.box(
            BoxType.SLIDING,
            f"CardBox_{deck_id}",
            size=(card_box_width, card_box_length, card_box_height),
            lid=LidBuilder(
                text=title,
                label_mode=LabelMode.FRAMED,
                pattern=MOON_PATTERN,
                text_color=Color("white"),
                frame_color=Color(color_name),
            ),
            position=(col_idx * card_box_width, y_pos, 0.0),
            no_rotate=True,
        )
        c_box.compartment("Cards", depth=card_box_height - lid_thickness, cut=FingerCut.SCOOP)

# ── 2. Objectives & Hazard Dice Tray (Stacked at Z = card_box_height)
# Tier 2 at row 0 & 1
obj_box = project.box(
    BoxType.SLIDING,
    "CardBox_Objectives",
    size=(card_box_width, card_box_length, card_box_height),
    lid=LidBuilder(
        text="Objectives",
        label_mode=LabelMode.FRAMED,
        pattern=MOON_PATTERN,
        text_color=Color("white"),
        frame_color=Color("teal"),
    ),
    position=(0.0, 0.0, card_box_height),
    no_rotate=True,
)
obj_box.compartment("Cards", depth=card_box_height - lid_thickness, cut=FingerCut.SCOOP)

dice_box = project.box(
    BoxType.CAP,
    "DiceAndTokensBox",
    size=(card_box_width, card_box_length, card_box_height),
    lid=LidBuilder(
        text="Hazard Dice",
        label_mode=LabelMode.FRAMED,
        pattern=MOON_PATTERN,
        text_color=Color("white"),
        frame_color=Color("firebrick"),
    ),
    position=(card_box_width, 0.0, card_box_height),
    no_rotate=True,
)
dice_box.compartment("Dice", depth=card_box_height - floor_thickness - 1.0, cut=FingerCut.SCOOP)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
