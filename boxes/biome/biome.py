#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Biome board game organizer.

Ports examples/biome.scad to the pyboxbuilder Project API.
Organizes wooden animal/food resources (mice, fish, berries, chicks, rabbits),
climate spinner, nest boards, cards, and player tokens with automated spacers.
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
box_width = 285.0
box_length = 285.0
box_height = 73.0

board_thickness = 20.0
usable_height = box_height - board_thickness  # 53.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

nest_width = 45.0
nest_box_width = nest_width + wall_thickness * 2.0  # 51.0mm
nest_box_length = box_length - 2.0                 # 283.0mm
nest_box_height = usable_height                    # 53.0mm

res_box_width = 57.0
res_box_length = (box_length - 2.0) / 4.0          # ~70.75mm
res_box_height = usable_height / 3.0               # ~17.66mm

card_width = 66.0
card_length = 91.0
card_box_width = card_width + 1.0 + wall_thickness * 2.0   # 73.0mm
card_box_length = card_length + 1.0 + wall_thickness * 2.0 # 98.0mm
card_box_height = usable_height                            # 53.0mm

project = Project(
    "Biome",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
    box_defaults={"expandable": False},
)

BIOME_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Nest Boards Longitudinal Tray ──────────────────────────────
project.box(
    BoxType.CAP,
    "NestBox",
    size=(nest_box_width, nest_box_length, nest_box_height),
    lid=LidBuilder(
        text="Nests",
        label_mode=LabelMode.FRAMED,
        pattern=BIOME_PATTERN,
        text_color=Color("white"),
        frame_color=Color("peru"),
    ),
).compartment(
    "NestBoards",
    cut=FingerCut.SCOOP,
)

# ── 2. Resource & Player Trays ────────────────────────────────────
resources = [
    [
        ("PlayerBox_Red", "Red", "darkred"),
        ("Resource_Mouse", "Mouse", "gray"),
        ("Resource_Sun", "Sun", "gold"),
    ],
    [
        ("PlayerBox_Blue", "Blue", "navy"),
        ("Resource_Fish", "Fish", "dodgerblue"),
        ("Resource_Leaf", "Leaf", "forestgreen"),
    ],
    [
        ("PlayerBox_Green", "Green", "green"),
        ("Resource_Spider", "Spider", "black"),
        ("Resource_Berry", "Berry", "purple"),
    ],
    [
        ("PlayerBox_Yellow", "Yellow", "goldenrod"),
        ("Resource_Chicks", "Chicks", "khaki"),
        ("Resource_Rabbits", "Rabbits", "saddlebrown"),
    ],
]

for col_items in resources:
    for box_id, title, color_name in col_items:
        bx = project.box(
            BoxType.CAP,
            box_id,
            size=(res_box_width, res_box_length, res_box_height),
            lid=LidBuilder(
                text=title,
                label_mode=LabelMode.FRAMED,
                pattern=BIOME_PATTERN,
                text_color=Color("black" if color_name in ("gold", "khaki", "yellow") else "white"),
                frame_color=Color(color_name),
            ),
        )
        bx.compartment(
            "Tokens",
            cut=FingerCut.SCOOP,
        )

# ── 3. Playing Cards Boxes ────────────────────────────────────────
card_decks = [
    ("MainDeck1", "Animals & Plants 1", "forestgreen"),
    ("MainDeck2", "Animals & Plants 2", "darkolivegreen"),
]

for deck_id, title, color_name in card_decks:
    c_box = project.box(
        BoxType.CAP,
        f"CardBox_{deck_id}",
        size=(card_box_width, card_box_length, card_box_height),
        lid=LidBuilder(
            text=title,
            label_mode=LabelMode.FRAMED,
            pattern=BIOME_PATTERN,
            text_color=Color("white"),
            frame_color=Color(color_name),
        ),
    )
    c_box.compartment(
        "Cards",
        cut=FingerCut.SCOOP,
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
