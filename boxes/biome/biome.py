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
)

BIOME_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Nest Boards Longitudinal Tray (Column 0, X = 0) ────────────
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
    position=(0.0, 0.0, 0.0),
    no_rotate=True,
).compartment(
    "NestBoards",
    depth=nest_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── 2. Resource & Player Trays (Column 1, X = nest_box_width) ─────
# 4 columns along Y, stacked 3 high (12 boxes total: 4 player + 8 resources)
resources = [
    # Col 0
    [
        ("PlayerBox_Red", "Red", "darkred"),
        ("Resource_Mouse", "Mouse", "gray"),
        ("Resource_Sun", "Sun", "gold"),
    ],
    # Col 1
    [
        ("PlayerBox_Blue", "Blue", "navy"),
        ("Resource_Fish", "Fish", "dodgerblue"),
        ("Resource_Leaf", "Leaf", "forestgreen"),
    ],
    # Col 2
    [
        ("PlayerBox_Green", "Green", "green"),
        ("Resource_Spider", "Spider", "black"),
        ("Resource_Berry", "Berry", "purple"),
    ],
    # Col 3
    [
        ("PlayerBox_Yellow", "Yellow", "goldenrod"),
        ("Resource_Chicks", "Chicks", "khaki"),
        ("Resource_Rabbits", "Rabbits", "saddlebrown"),
    ],
]

for col_idx, col_items in enumerate(resources):
    y_pos = col_idx * res_box_length
    for tier_idx, (box_id, title, color_name) in enumerate(col_items):
        z_pos = tier_idx * res_box_height
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
            position=(nest_box_width, y_pos, z_pos),
            no_rotate=True,
        )
        bx.compartment(
            "Tokens",
            depth=res_box_height - floor_thickness - 1.0,
            cut=FingerCut.SCOOP,
        )

# ── 3. Playing Cards Boxes (Column 2, X = nest + res) ─────────────
x_cards = nest_box_width + res_box_width  # 108.0mm

card_decks = [
    ("MainDeck1", "Animals & Plants 1", "forestgreen"),
    ("MainDeck2", "Animals & Plants 2", "darkolivegreen"),
]

for idx, (deck_id, title, color_name) in enumerate(card_decks):
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
        position=(x_cards, idx * card_box_length, 0.0),
        no_rotate=True,
    )
    c_box.compartment(
        "Cards",
        depth=card_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
