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

from pyboxbuilder import (
    BoxType,
    Color,
    FingerCut,
    LabelMode,
    LidBuilder,
    PatternBuilder,
    PatternType,
    Project,
    StackableMode,
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
    box_defaults={"expandable": False},
)

MOON_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Command & Expansion Card Decks ─────────────────────────────
command_decks = [
    ("Thrusters", "Thrusters", "gold"),
    ("Damage", "Damage", "darkred"),
    ("Reactor", "Reactor", "royalblue"),
    ("Shield", "Shield", "forestgreen"),
    ("Miss", "Miss", "gray"),
    ("Crew", "Crew", "purple"),
    ("Contracts", "Contracts", "darkorange"),
    ("Ships", "Ship Parts", "navy"),
]

for deck_id, title, color_name in command_decks:
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
    )
    c_box.compartment("Cards", cut=FingerCut.SCOOP)

# ── 2. Objectives & Hazard Dice Tray ──────────────────────────────
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
)
obj_box.compartment("Cards", cut=FingerCut.SCOOP)

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
)
dice_box.compartment("Dice", cut=FingerCut.SCOOP)

project.stack_order("CardBox_Thrusters", "CardBox_Objectives", mode=StackableMode.PYRAMIDS)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
