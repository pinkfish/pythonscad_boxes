#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Explorers of Navoria board game organizer.

Ports boxes/explorers_of_navoria/explorers_of_navoria.scad to the pyboxbuilder
Project API. Organizes 8 player boxes (4 trading-post boxes + 4 explorer-marker
boxes for Green, Yellow, Purple, Black), favour tiles box, 3 sliding resource
boxes (Swords, Apples, Crystals), adventure card box, and open drawing-bag tray.
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
box_width = 211.0
box_length = 268.0
box_height = 68.0

board_thickness = 12.0
usable_height = box_height - board_thickness  # 56.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

# ── Component Dimensions ──────────────────────────────────────────
card_width = 68.0
card_length = 92.0
player_layout_thickness = 2.0
player_layout_num = 4
num_favour_tiles = 10

# ── Sub-Box Dimensions (matching explorers_of_navoria.scad) ───────
player_box_width = 98.0
player_box_length = (box_length - 2.0) / 2.0  # 133.0mm
player_box_height = usable_height / 4.0  # 14.0mm

favour_box_width = box_width - player_box_width - 1.5  # 111.5mm
favour_box_length = 60.0
favour_box_height = (
    lid_thickness * 2.0 + player_layout_thickness * num_favour_tiles / 2.0 + 0.5
)  # 14.5mm

stuff_box_width = favour_box_width / 3.0  # 37.167mm
stuff_box_length = favour_box_length  # 60.0mm
stuff_box_height = (
    usable_height - favour_box_height - 1.0 - player_layout_thickness * player_layout_num
)  # 32.5mm

card_box_width = box_width - player_box_width - 2.0  # 111.0mm
card_box_length = card_width + wall_thickness * 2.0 + 0.5  # 74.5mm
card_box_height = (
    usable_height - player_layout_thickness - 1.0 - player_layout_thickness * player_layout_num
)  # 45.0mm

bag_box_width = box_width - player_box_width - 2.0  # 111.0mm
bag_box_length = box_length - stuff_box_length - 2.0 - card_box_length  # 131.5mm
bag_box_height = card_box_height  # 45.0mm

project = Project(
    "ExplorersOfNavoria",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

NAVORIA_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── Column 0: 8 Player Boxes (4 Trading Posts + 4 Explorers) ──────
player_factions = [
    ("Green", "forestgreen"),
    ("Yellow", "gold"),
    ("Purple", "purple"),
    ("Black", "black"),
]

for layer_idx, (faction, color_name) in enumerate(player_factions):
    # Front stack: Trading Posts (PlayerBox*One)
    project.box(
        BoxType.CAP,
        f"PlayerBox_{faction}_One",
        size=(player_box_width, player_box_length, player_box_height),
        position=(0.0, 0.0, player_box_height * layer_idx),
        lid=LidBuilder(
            text=f"{faction} Posts",
            label_mode=LabelMode.FRAMED,
            pattern=NAVORIA_PATTERN,
            text_color=Color("black" if color_name == "gold" else "white"),
            frame_color=Color(color_name),
        ),
    ).compartment("TradingPosts", cut=FingerCut.SCOOP)

    # Back stack: Explorers & Turn Order Bird (PlayerBox*Two)
    project.box(
        BoxType.CAP,
        f"PlayerBox_{faction}_Two",
        size=(player_box_width, player_box_length, player_box_height),
        position=(0.0, player_box_length, player_box_height * layer_idx),
        lid=LidBuilder(
            text=f"{faction} Explorers",
            label_mode=LabelMode.FRAMED,
            pattern=NAVORIA_PATTERN,
            text_color=Color("black" if color_name == "gold" else "white"),
            frame_color=Color(color_name),
        ),
    ).compartment("Explorers", cut=FingerCut.SCOOP)

# ── Column 1 Front: Favour Box & 3 Stuff Boxes (Y = 0 .. 60) ──────
favour_box = project.box(
    BoxType.CAP,
    "FavourBox",
    size=(favour_box_width, favour_box_length, favour_box_height),
    position=(player_box_width, 0.0, 0.0),
    lid=LidBuilder(
        text="Favours",
        label_mode=LabelMode.FRAMED,
        pattern=NAVORIA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkorange"),
    ),
)
favour_box.compartment("FavoursLeft", width_ratio=0.5, cut=FingerCut.SCOOP)
favour_box.compartment("FavoursRight", width_ratio=0.5, cut=FingerCut.SCOOP)

for idx, (label, text, color_name) in enumerate([
    ("StuffBox_Swords", "Swords", "slategray"),
    ("StuffBox_Apples", "Apples", "crimson"),
    ("StuffBox_Crystals", "Crystals", "deepskyblue"),
]):
    project.box(
        BoxType.SLIDING,
        label,
        size=(stuff_box_width, stuff_box_length, stuff_box_height),
        position=(player_box_width + stuff_box_width * idx, 0.0, favour_box_height),
        lid=LidBuilder(
            text=text,
            label_mode=LabelMode.FRAMED,
            pattern=NAVORIA_PATTERN,
            text_color=Color("white"),
            frame_color=Color(color_name),
        ),
    ).compartment("Tokens", cut=FingerCut.SCOOP)

# ── Column 1 Middle: Adventure Cards Box (Y = 60 .. 134.5) ────────
project.box(
    BoxType.SLIDING,
    "CardBox",
    size=(card_box_width, card_box_length, card_box_height),
    position=(player_box_width, favour_box_length, 0.0),
    lid=LidBuilder(
        text="Cards",
        label_mode=LabelMode.FRAMED,
        pattern=NAVORIA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("navy"),
    ),
).compartment("AdventureCards", cut=FingerCut.SCOOP)

# ── Column 1 Back: Open Drawing Bag Tray (Y = 134.5 .. 266) ───────
project.box(
    BoxType.NO_LID,
    "BagBox",
    size=(bag_box_width, bag_box_length, bag_box_height),
    position=(player_box_width, favour_box_length + card_box_length, 0.0),
).compartment("BagAndBits", cut=FingerCut.SCOOP)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
