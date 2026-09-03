#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Railway Boom board game organizer.

Ports examples/railway_boom.scad to the pyboxbuilder Project API.
Organizes player train and station components, development and locomotive cards,
city tiles, resource cubes, and indicators with automated spacers.
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
box_width = 209.0
box_length = 300.0
box_height = 46.0

board_thickness = 10.0
player_board_thickness = 2.0 * 4.0  # 8.0mm
usable_height = box_height - board_thickness - player_board_thickness  # 28.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

player_box_width = (box_width - 2.0) / 2.0  # 103.5mm
player_box_length = 108.0
player_box_height = usable_height / 2.0     # 14.0mm

card_width = 67.0
card_length = 92.0
card_box_width = card_length + wall_thickness * 2.0   # 98.0mm
card_box_length = card_width + wall_thickness * 2.0   # 73.0mm
card_box_height = usable_height                        # 28.0mm

small_card_width = 46.0
small_card_length = 66.0
small_card_box_width = small_card_length + wall_thickness * 2.0  # 72.0mm
small_card_box_length = small_card_width + wall_thickness * 2.0  # 52.0mm

project = Project(
    "RailwayBoom",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness + player_board_thickness,
    generate_spacers=True,
)

BOOM_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Player Boxes (4 boxes: 2 columns, stacked 2 high at Y = 0) ─
player_colors = ["red", "yellow", "blue", "green"]
for idx, color_name in enumerate(player_colors):
    col = idx % 2
    tier = idx // 2
    p_box = project.box(
        BoxType.CAP,
        f"PlayerBox_{color_name.title()}",
        size=(player_box_width, player_box_length, player_box_height),
        lid=LidBuilder(
            text=f"Player ({color_name.title()})",
            label_mode=LabelMode.FRAMED,
            pattern=BOOM_PATTERN,
            text_color=Color("black" if color_name == "yellow" else "white"),
            frame_color=Color(color_name),
        ),
        position=(col * player_box_width, 0.0, tier * player_box_height),
        no_rotate=True,
    )
    p_box.compartment(
        "TrainsAndStations",
        width_ratio=0.6,
        depth=player_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )
    p_box.compartment(
        "CubesAndDiscs",
        width_ratio=0.4,
        depth=player_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )

# ── 2. Standard Card Boxes (Y = player_box_length = 108mm) ────────
y_cards = player_box_length

project.box(
    BoxType.SLIDING,
    "StationCardBox",
    size=(card_box_width, card_box_length, card_box_height),
    lid=LidBuilder(
        text="Stations",
        label_mode=LabelMode.FRAMED,
        pattern=BOOM_PATTERN,
        text_color=Color("white"),
        frame_color=Color("navy"),
    ),
    position=(0.0, y_cards, 0.0),
    no_rotate=True,
).compartment(
    "StationCards",
    depth=card_box_height - lid_thickness,
    cut=FingerCut.SCOOP,
)

project.box(
    BoxType.SLIDING,
    "ObjectiveCardBox",
    size=(card_box_width, card_box_length, card_box_height),
    lid=LidBuilder(
        text="Objectives",
        label_mode=LabelMode.FRAMED,
        pattern=BOOM_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkorange"),
    ),
    position=(card_box_width, y_cards, 0.0),
    no_rotate=True,
).compartment(
    "ObjectiveCards",
    depth=card_box_height - lid_thickness,
    cut=FingerCut.SCOOP,
)

# ── 3. Small Card Boxes & City Tiles (Y = 108 + 73 = 181mm) ───────
y_small = y_cards + card_box_length

small_decks = [
    ("Locomotives", "Locomotives", "darkred"),
    ("Carriages", "Carriages", "peru"),
]

for idx, (deck_id, title, color_name) in enumerate(small_decks):
    s_box = project.box(
        BoxType.SLIDING,
        f"SmallCardBox_{deck_id}",
        size=(small_card_box_width, small_card_box_length, usable_height),
        lid=LidBuilder(
            text=title,
            label_mode=LabelMode.FRAMED,
            pattern=BOOM_PATTERN,
            text_color=Color("white"),
            frame_color=Color(color_name),
        ),
        position=(idx * small_card_box_width, y_small, 0.0),
        no_rotate=True,
    )
    s_box.compartment(
        "Cards",
        depth=usable_height - lid_thickness,
        cut=FingerCut.SCOOP,
    )

city_tile_box_width = 52.0
project.box(
    BoxType.SLIDING,
    "SmallCardBox_CityTiles",
    size=(city_tile_box_width, small_card_box_length, usable_height),
    lid=LidBuilder(
        text="City Tiles",
        label_mode=LabelMode.FRAMED,
        pattern=BOOM_PATTERN,
        text_color=Color("white"),
        frame_color=Color("dimgray"),
    ),
    position=(small_card_box_width * 2.0, y_small, 0.0),
    no_rotate=True,
).compartment(
    "CityTiles",
    depth=usable_height - lid_thickness,
    cut=FingerCut.SCOOP,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
