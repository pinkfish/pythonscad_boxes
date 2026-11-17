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
    box_defaults={"expandable": False},
)

RR_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Player & Currency Section ──────────────────────────────────
trays = [
    ("PlayerBox_Red", "Red", "red"),
    ("PlayerBox_Blue", "Blue", "navy"),
    ("ExtraTokensBox", "Tokens", "dimgray"),
    ("PlayerBox_Green", "Green", "forestgreen"),
    ("PlayerBox_Yellow", "Yellow", "gold"),
    ("MoneyBox", "Rubels", "goldenrod"),
]

for name, title, color_name in trays:
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
    )
    p_box.compartment(
        "Workers",
        width_ratio=0.6,
        cut=FingerCut.SCOOP,
    )
    p_box.compartment(
        "Markers",
        width_ratio=0.4,
        cut=FingerCut.SCOOP,
    )

# ── 2. Train, Engineer, Track & Card Section ──────────────────────
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
).compartment(
    "Cards",
    cut=FingerCut.SCOOP,
)

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
).compartment(
    "TrainTiles",
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
).compartment(
    "EngineerTiles",
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
).compartment(
    "WoodenTracks",
    cut=FingerCut.SCOOP,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
