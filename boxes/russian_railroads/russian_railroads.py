#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Russian Railroads board game organizer.

Ports examples/russian_railroads.scad to the pyboxbuilder Project API.
Organizes player wooden workers, track markers, train tiles, engineer tiles,
cards, and ruble tokens with automated spacers.
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
box_width = 219.0
box_length = 308.0
box_height = 70.0

board_thickness = 15.0
usable_height = box_height - board_thickness  # 55.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

player_box_width = (box_width - 2.0) / 2.0  # 108.5mm
player_box_length = 80.5
player_box_height = usable_height / 3.0     # 18.33mm

card_box_width = 18.0
card_box_length = 105.0
card_box_height = usable_height

train_box_width = box_width - 2.0 - card_box_width  # 199.0mm
train_box_length = 105.0
train_box_height = 17.0
engineer_box_height = 13.0
track_box_height = usable_height - train_box_height - engineer_box_height  # 25.0mm

project = Project(
    "RussianRailroads",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

RR_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Player & Currency Section (2 columns, stacked 3 high at Y = 0)
trays = [
    # Column 0
    ("PlayerBox_Red", "Red", "red", 0, 0),
    ("PlayerBox_Blue", "Blue", "navy", 0, 1),
    ("ExtraTokensBox", "Tokens", "dimgray", 0, 2),
    # Column 1
    ("PlayerBox_Green", "Green", "forestgreen", 1, 0),
    ("PlayerBox_Yellow", "Yellow", "gold", 1, 1),
    ("MoneyBox", "Rubels", "goldenrod", 1, 2),
]

for name, title, color_name, col, tier in trays:
    p_box = project.box(
        BoxType.CAP,
        name,
        size=(player_box_width, player_box_length, player_box_height),
        lid=LidBuilder(
            text=title,
            label_mode=LabelMode.FRAMED,
            pattern=RR_PATTERN,
            text_color=Color("black" if color_name in ("gold", "yellow") else "white"),
            frame_color=Color(color_name),
        ),
        position=(col * player_box_width, 0.0, tier * player_box_height),
        no_rotate=True,
    )
    p_box.compartment(
        "Workers",
        width_ratio=0.6,
        depth=player_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )
    p_box.compartment(
        "Markers",
        width_ratio=0.4,
        depth=player_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )

# ── 2. Train, Engineer, Track & Card Section (Y = player_box_length)
y_trains = player_box_length

project.box(
    BoxType.SLIDING,
    "CardBox",
    size=(card_box_width, card_box_length, card_box_height),
    lid=LidBuilder(
        text="Cards",
        label_mode=LabelMode.FRAMED,
        pattern=RR_PATTERN,
        text_color=Color("white"),
        frame_color=Color("peru"),
    ),
    position=(train_box_width, y_trains, 0.0),
    no_rotate=True,
).compartment(
    "Cards",
    depth=card_box_height - lid_thickness,
    cut=FingerCut.SCOOP,
)

# Stacked at X = 0, Y = y_trains
project.box(
    BoxType.CAP,
    "TrainBox",
    size=(train_box_width, train_box_length, train_box_height),
    lid=LidBuilder(
        text="Trains",
        label_mode=LabelMode.FRAMED,
        pattern=RR_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkred"),
    ),
    position=(0.0, y_trains, 0.0),
    no_rotate=True,
).compartment(
    "TrainTiles",
    depth=train_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

project.box(
    BoxType.CAP,
    "EngineerBox",
    size=(train_box_width, train_box_length, engineer_box_height),
    lid=LidBuilder(
        text="Engineers",
        label_mode=LabelMode.FRAMED,
        pattern=RR_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkslategray"),
    ),
    position=(0.0, y_trains, train_box_height),
    no_rotate=True,
).compartment(
    "EngineerTiles",
    depth=engineer_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

project.box(
    BoxType.CAP,
    "TrackBox",
    size=(train_box_width, train_box_length, track_box_height),
    lid=LidBuilder(
        text="Tracks",
        label_mode=LabelMode.FRAMED,
        pattern=RR_PATTERN,
        text_color=Color("white"),
        frame_color=Color("saddlebrown"),
    ),
    position=(0.0, y_trains, train_box_height + engineer_box_height),
    no_rotate=True,
).compartment(
    "WoodenTracks",
    depth=track_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
