#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Explorers of Navoria board game organizer.

Ports examples/explorers_of_navoria.scad to the pyboxbuilder Project API.
Organizes player trading posts and explorers (Yellow, Purple, Black, Green),
adventure cards, favor tiles, crafting tokens, and drawing bag with automated spacers.
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
box_height = 68.0

board_thickness = 12.0
usable_height = box_height - board_thickness  # 56.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

player_box_width = 98.0
player_box_length = (box_length - 2.0) / 2.0  # 133.0mm
player_box_height = usable_height / 2.0       # 28.0mm

card_width = 68.0
card_length = 92.0
card_box_width = box_width - player_box_width - 2.0   # 111.0mm
card_box_length = card_width + wall_thickness * 2.0   # 74.0mm
card_box_height = usable_height                       # 56.0mm

favour_box_width = card_box_width                     # 111.0mm
favour_box_length = 60.0
favour_box_height = usable_height / 2.0               # 28.0mm

bag_box_width = card_box_width                        # 111.0mm
bag_box_length = box_length - card_box_length - favour_box_length - 2.0  # 132.0mm
bag_box_height = usable_height                        # 56.0mm

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

# ── 1. Player Boxes (Column 0, 2 rows x 2 tiers at X = 0) ─────────
player_factions = ["Yellow", "Purple", "Black", "Green"]
player_colors = ["gold", "purple", "black", "forestgreen"]

for idx, (faction, color_name) in enumerate(zip(player_factions, player_colors)):
    row = idx % 2
    tier = idx // 2
    p_box = project.box(
        BoxType.CAP,
        f"PlayerBox_{faction}",
        size=(player_box_width, player_box_length, player_box_height),
        lid=LidBuilder(
            text=faction,
            label_mode=LabelMode.FRAMED,
            pattern=NAVORIA_PATTERN,
            text_color=Color("black" if color_name == "gold" else "white"),
            frame_color=Color(color_name),
        ),
        position=(0.0, row * player_box_length, tier * player_box_height),
        no_rotate=True,
    )
    p_box.compartment(
        "TradingPosts",
        length_ratio=0.6,
        depth=player_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )
    p_box.compartment(
        "Explorers",
        length_ratio=0.4,
        depth=player_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )

# ── 2. Adventure Cards Box (Column 1, X = player_box_width) ───────
x_col1 = player_box_width

project.box(
    BoxType.SLIDING,
    "CardBox",
    size=(card_box_width, card_box_length, card_box_height),
    lid=LidBuilder(
        text="Cards",
        label_mode=LabelMode.FRAMED,
        pattern=NAVORIA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("navy"),
    ),
    position=(x_col1, 0.0, 0.0),
    no_rotate=True,
).compartment(
    "AdventureCards",
    depth=card_box_height - lid_thickness,
    cut=FingerCut.SCOOP,
)

# ── 3. Favour & Token Trays (Y = card_box_length) ─────────────────
for tier in range(2):
    f_box = project.box(
        BoxType.CAP,
        f"FavourBox_{tier + 1}",
        size=(favour_box_width, favour_box_length, favour_box_height),
        lid=LidBuilder(
            text="Favour Tiles" if tier == 0 else "Tokens",
            label_mode=LabelMode.FRAMED,
            pattern=NAVORIA_PATTERN,
            text_color=Color("white"),
            frame_color=Color("darkorange"),
        ),
        position=(x_col1, card_box_length, tier * favour_box_height),
        no_rotate=True,
    )
    f_box.compartment(
        "Tiles",
        depth=favour_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )

# ── 4. Drawing Bag & Large Bits (Y = card_box_length + favour_box_length)
y_bag = card_box_length + favour_box_length

project.box(
    BoxType.CAP,
    "BagBox",
    size=(bag_box_width, bag_box_length, bag_box_height),
    lid=LidBuilder(
        text="Bag & Components",
        label_mode=LabelMode.FRAMED,
        pattern=NAVORIA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("peru"),
    ),
    position=(x_col1, y_bag, 0.0),
    no_rotate=True,
).compartment(
    "BagAndBits",
    depth=bag_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
