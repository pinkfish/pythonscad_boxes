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
    LabelFinial,
    LabelMode,
    LabelShape,
    LidBuilder,
    PatternBuilder,
    PatternType,
    Project,
    run,
)

ASSETS = ROOT / "boxes" / "moonrakers" / "assets"

# ── Box & Board Dimensions ────────────────────────────────────────
box_width = 213.0
box_length = 303.0
box_height = 93.0

base_board_thickness = 9.0
player_board_thickness = 15.0
board_thickness = base_board_thickness + player_board_thickness  # 24.0mm (matching BoxLayout in moonrakers.scad)
usable_height = box_height - board_thickness  # 69.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

dice_size = 17.0
card_width = 67.0
card_length = 90.0
ten_cards_thickness = 6.0
single_card_thickness = ten_cards_thickness / 10.0  # 0.6mm

card_box_width = card_length + wall_thickness * 2.0  # 96.0mm
card_box_length = card_width + wall_thickness * 2.0  # 73.0mm

# Exact per-deck box heights from moonrakers.scad
thruster_card_box_height = floor_thickness + lid_thickness + single_card_thickness * 25 + 2.0        # 21.0mm
damage_card_box_height = floor_thickness + lid_thickness + single_card_thickness * 35 + 2.0          # 27.0mm
shield_card_box_height = floor_thickness + lid_thickness + single_card_thickness * 25 + 1.5          # 20.5mm
reactor_card_box_height = floor_thickness + lid_thickness + single_card_thickness * 30 + 0.5         # 22.5mm
miss_card_box_height = floor_thickness + lid_thickness + single_card_thickness * 15 + 0.5            # 13.5mm
reference_card_box_height = floor_thickness + lid_thickness + single_card_thickness * 10             # 10.0mm
crew_card_box_height = floor_thickness + lid_thickness + single_card_thickness * (20 + 10) + 1.0     # 23.0mm
contract_card_box_height = floor_thickness + lid_thickness + single_card_thickness * (40 + 10) + 1.0 # 35.0mm
ship_card_box_height = floor_thickness + lid_thickness + single_card_thickness * (37 + 10) + 1.0     # 33.2mm
objective_card_box_height = floor_thickness + lid_thickness + single_card_thickness * (23 + 10) + 1.0  # 24.8mm
dice_box_height = floor_thickness + lid_thickness + dice_size + 1.0                                  # 22.0mm

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

MOON_PATTERN = PatternBuilder(PatternType.PENROSE)
MOON_LID = LidBuilder(
    label_mode=LabelMode.FRAMED,
    label_shape=LabelShape.HEX_BRACKET,
    label_finial=LabelFinial.CHEVRON,
    font="Futura:style=Bold",
    pattern=MOON_PATTERN,
    text_color=Color("white"),
    logo_color=Color("white"),
    logo_position="left",
    label_logo_size_mm=15.0,
)

# ── 1. All 10 Card Decks (matching moonrakers.scad) ───────────────
card_decks = [
    ("Thrusters", "Thrusters", "gold", thruster_card_box_height, "thruster.svg"),
    ("Damage", "Damage", "darkred", damage_card_box_height, "reactor.svg"),
    ("Reactor", "Reactor", "royalblue", reactor_card_box_height, "reactor.svg"),
    ("Miss", "Miss", "gray", miss_card_box_height, "dice.svg"),
    ("Shield", "Shield", "forestgreen", shield_card_box_height, "shield.svg"),
    ("Reference", "Reference", "slategray", reference_card_box_height, "shield.svg"),
    ("Crew", "Crew", "darkorange", crew_card_box_height, "credit.svg"),
    ("Contracts", "Contracts", "purple", contract_card_box_height, "credit.svg"),
    ("Ships", "Ship Parts", "navy", ship_card_box_height, "thruster.svg"),
    ("Objectives", "Objectives", "teal", objective_card_box_height, "credit.svg"),
]

for deck_id, title, color_name, deck_height, icon_file in card_decks:
    c_box = project.box(
        BoxType.SLIDING,
        f"CardBox_{deck_id}",
        size=(card_box_width, card_box_length, deck_height),
        lid=MOON_LID.titled(
            title,
            frame_color=Color(color_name),
            logo=str(ASSETS / icon_file),
        ),
    )
    c_box.compartment("Cards", cut=FingerCut.SCOOP)

# ── 2. Hazard Dice & Tokens Tray ──────────────────────────────────
dice_box = project.box(
    BoxType.CAP,
    "DiceAndTokensBox",
    size=(card_box_width, card_box_length, dice_box_height),
    lid=MOON_LID.titled(
        "Hazard Dice",
        frame_color=Color("firebrick"),
        logo=str(ASSETS / "dice.svg"),
    ),
)
dice_box.compartment("Dice", cut=FingerCut.SCOOP)

project.stack_order("CardBox_Thrusters", "CardBox_Damage", "CardBox_Shield")
project.stack_order("CardBox_Reactor", "CardBox_Miss", "CardBox_Crew", "CardBox_Reference")
project.stack_order("CardBox_Contracts", "CardBox_Ships")

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
