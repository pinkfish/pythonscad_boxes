#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Biome board game organizer.

Ports boxes/biome/biome.scad to the pyboxbuilder Project API.
Organizes 4 player boxes, 8 wooden resource boxes (mouse, sun, fish, leaf,
spider, berry, chicks, rabbits), nest boards tray, climate spinner holder,
extra bits box (cubes, coin, die, season & start-player tokens), and all
8 card boxes (2 main plant/animal decks, starting, achievement, changing
condition, legend, extra plant/animal, and big biome deck) with automatic spacers.
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
board_width = 255.0
usable_height = box_height - board_thickness  # 53.0mm
insert_height = usable_height - 1.0  # 52.0mm (1mm vertical slack per biome.scad)

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 3.0

# ── Component Dimensions ──────────────────────────────────────────
nest_width = 45.0
spinner_thickness = 9.0
card_width = 66.0
card_length = 91.0
single_card_thickness = 0.6

# ── Sub-Box Dimensions (matching biome.scad) ──────────────────────
player_box_width = wall_thickness * 4.0 + nest_width  # 57.0mm
player_box_length = (box_length - 2.0) / 4.0  # 70.75mm
player_box_height = insert_height / 3.0  # 17.333mm

nest_box_width = nest_width + floor_thickness + lid_thickness + 2.0  # 52.0mm
nest_box_length = box_length - 2.0  # 283.0mm
nest_box_height = insert_height  # 52.0mm

spinner_box_height = spinner_thickness + floor_thickness  # 11.0mm
card_box_width = card_width + 1.0 + wall_thickness * 2.0  # 73.0mm
card_box_length = card_length + 1.0 + wall_thickness * 2.0  # 98.0mm
card_box_height = insert_height - spinner_box_height  # 41.0mm

spinner_box_width = box_width - player_box_width - nest_box_width - 2.0  # 174.0mm
spinner_box_length = box_length - 2.0 - card_box_length  # 185.0mm

starting_card_box_height = single_card_thickness * 14.0 + lid_thickness + floor_thickness + 1.0  # 14.4mm
achievement_card_box_height = single_card_thickness * 13.0 + lid_thickness + floor_thickness + 1.0  # 13.8mm
changing_condition_card_box_height = single_card_thickness * 11.0 + lid_thickness + floor_thickness + 1.0  # 12.6mm
legend_card_box_height = single_card_thickness * 9.0 + lid_thickness + floor_thickness + 1.0  # 11.4mm
plant_animal_extra_card_box_height = card_box_height - legend_card_box_height  # 29.6mm
big_card_box_height = insert_height  # 52.0mm

extra_bits_box_width = box_width - board_width - 1.0  # 29.0mm
extra_bits_box_length = box_length - 1.0  # 284.0mm
extra_bits_box_height = card_box_height  # 41.0mm

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

# ── Column 0: Player & Resource Trays (4x3 stack at X = 0 .. 57) ──
col0_layers = [
    [
        ("PlayerBox_Red", "Red", "darkred"),
        ("PlayerBox_Blue", "Blue", "navy"),
        ("PlayerBox_Green", "Green", "green"),
        ("PlayerBox_Yellow", "Yellow", "goldenrod"),
    ],
    [
        ("Resource_Mouse", "Mouse", "gray"),
        ("Resource_Sun", "Sun", "gold"),
        ("Resource_Fish", "Fish", "dodgerblue"),
        ("Resource_Leaf", "Leaf", "forestgreen"),
    ],
    [
        ("Resource_Spider", "Spider", "black"),
        ("Resource_Berry", "Berry", "purple"),
        ("Resource_Chicks", "Chicks", "khaki"),
        ("Resource_Rabbits", "Rabbits", "saddlebrown"),
    ],
]

for layer_idx, items in enumerate(col0_layers):
    for row_idx, (box_id, title, color_name) in enumerate(items):
        project.box(
            BoxType.CAP,
            box_id,
            size=(player_box_width, player_box_length, player_box_height),
            position=(0.0, player_box_length * row_idx, player_box_height * layer_idx),
            lid=LidBuilder(
                text=title,
                label_mode=LabelMode.FRAMED,
                pattern=BIOME_PATTERN,
                text_color=Color("black" if color_name in ("gold", "khaki", "yellow") else "white"),
                frame_color=Color(color_name),
            ),
        ).compartment("Tokens", cut=FingerCut.SCOOP)

# ── Column 1: Nest Boards Longitudinal Tray (X = 57 .. 109) ───────
project.box(
    BoxType.CAP,
    "NestBox",
    size=(nest_box_width, nest_box_length, nest_box_height),
    position=(player_box_width, 0.0, 0.0),
    lid=LidBuilder(
        text="Nests",
        label_mode=LabelMode.FRAMED,
        pattern=BIOME_PATTERN,
        text_color=Color("white"),
        frame_color=Color("peru"),
    ),
).compartment("NestBoards", cut=FingerCut.SCOOP)

# ── Columns 2–3: Card Boxes & Spinner Holder (X = 109 .. 255) ─────
cards_x0 = player_box_width + nest_box_width  # 109.0mm
cards_x1 = cards_x0 + card_box_width  # 182.0mm

for deck_id, title, x_pos, color_name in [
    ("CardBox_MainDeck1", "Play", cards_x0, "forestgreen"),
    ("CardBox_MainDeck2", "Play", cards_x1, "darkolivegreen"),
]:
    project.box(
        BoxType.SLIDING,
        deck_id,
        size=(card_box_width, card_box_length, card_box_height),
        position=(x_pos, 0.0, 0.0),
        lid=LidBuilder(
            text=title,
            label_mode=LabelMode.FRAMED,
            pattern=BIOME_PATTERN,
            text_color=Color("white"),
            frame_color=Color(color_name),
        ),
    ).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "CardBox_Starting",
    size=(card_box_width, card_box_length, starting_card_box_height),
    position=(cards_x0, card_box_length, 0.0),
    lid=LidBuilder(
        text="Starting",
        label_mode=LabelMode.FRAMED,
        pattern=BIOME_PATTERN,
        text_color=Color("white"),
        frame_color=Color("teal"),
    ),
).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "CardBox_Achievement",
    size=(card_box_width, card_box_length, achievement_card_box_height),
    position=(cards_x0, card_box_length, starting_card_box_height),
    lid=LidBuilder(
        text="Achievement",
        label_mode=LabelMode.FRAMED,
        pattern=BIOME_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkgoldenrod"),
    ),
).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "CardBox_ChangingCondition",
    size=(card_box_width, card_box_length, changing_condition_card_box_height),
    position=(cards_x0, card_box_length, starting_card_box_height + achievement_card_box_height),
    lid=LidBuilder(
        text="Change",
        label_mode=LabelMode.FRAMED,
        pattern=BIOME_PATTERN,
        text_color=Color("white"),
        frame_color=Color("sienna"),
    ),
).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "CardBox_Legend",
    size=(card_box_width, card_box_length, legend_card_box_height),
    position=(cards_x1, card_box_length, 0.0),
    lid=LidBuilder(
        text="Legend",
        label_mode=LabelMode.FRAMED,
        pattern=BIOME_PATTERN,
        text_color=Color("white"),
        frame_color=Color("indigo"),
    ),
).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "CardBox_PlantAnimalExtra",
    size=(card_box_width, card_box_length, plant_animal_extra_card_box_height),
    position=(cards_x1, card_box_length, legend_card_box_height),
    lid=LidBuilder(
        text="Play Extra",
        label_mode=LabelMode.FRAMED,
        pattern=BIOME_PATTERN,
        text_color=Color("white"),
        frame_color=Color("seagreen"),
    ),
).compartment("Cards", cut=FingerCut.SCOOP)

# BigCardBox is rotated 90 deg in biome.scad (98mm wide x 73mm long x 52mm tall)
project.box(
    BoxType.SLIDING,
    "CardBox_BigBiome",
    size=(card_box_length, card_box_width, big_card_box_height),
    position=(cards_x0, card_box_length * 2.0, 0.0),
    lid=LidBuilder(
        text="Biome",
        label_mode=LabelMode.FRAMED,
        pattern=BIOME_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkgreen"),
    ),
).compartment("Cards", cut=FingerCut.SCOOP)

# SpinnerHolder sits atop the card boxes and ExtraBitsBox at Z = 41mm
project.box(
    BoxType.NO_LID,
    "SpinnerHolder",
    size=(spinner_box_width, spinner_box_length, spinner_box_height),
    position=(cards_x0, 0.0, card_box_height),
).compartment("Spinner", cut=FingerCut.SCOOP)

# ── Column 4: Extra Bits Box (X = 255 .. 284) ─────────────────────
extra_bits = project.box(
    BoxType.SLIPOVER,
    "ExtraBitsBox",
    size=(extra_bits_box_width, extra_bits_box_length, extra_bits_box_height),
    position=(board_width, 0.0, 0.0),
    lid=LidBuilder(
        text="Biome",
        label_mode=LabelMode.FRAMED,
        pattern=BIOME_PATTERN,
        text_color=Color("white"),
        frame_color=Color("olivedrab"),
    ),
)
extra_bits.compartment("CubesCoinTokensDie", cut=FingerCut.SCOOP)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
