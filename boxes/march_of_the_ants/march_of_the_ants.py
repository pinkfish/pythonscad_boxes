#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""March of the Ants board game organizer.

Ports boxes/march_of_the_ants/march_of_the_ants.scad to the pyboxbuilder Project API.
Organizes base territory hexes, Minions of the Meadow hexes, base & expansion
sleeved evolution cards, food/centipede/day-night tokens, predator meeples,
5 player ant colony boxes, and the aphid box.
"""

import math
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
box_width = 195.0
box_length = 275.0
box_height = 65.0

board_thickness = 6.0
usable_height = box_height - board_thickness  # 59.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

# ── Component Dimensions (matching march_of_the_ants.scad) ────────
tile_thickness = 2.0
tile_width = 84.0
tile_radius = tile_width / 2.0 / math.cos(math.radians(30.0))  # 48.497mm

food_token_num = 30
food_token_thickness = 3.5

sleeved_card_width = 66.0
sleeved_card_length = 91.0
twenty_sleeved_cards_thickness = 8.5
total_cards = 66
num_mm_cards = 36 + 5 + 8  # 49
num_mm_hex = 1 + 1 + 4  # 6

# ── Sub-Box Dimensions ────────────────────────────────────────────
tile_box_width = box_width - 1.0  # 194.0mm
tile_box_length = (tile_radius * 2.0 + 0.5) + wall_thickness * 2.0  # 103.495mm
tile_box_height = usable_height  # 59.0mm

card_box_width = sleeved_card_width + 1.0 + wall_thickness * 2.0  # 73.0mm
card_box_length = sleeved_card_length + 1.0 + wall_thickness * 2.0  # 98.0mm
card_box_height = twenty_sleeved_cards_thickness * total_cards / 20.0 + lid_thickness * 2.0 + 1.0  # 33.05mm
mm_card_box_height = (
    twenty_sleeved_cards_thickness * num_mm_cards / 20.0 + lid_thickness * 2.0 + 0.75
)  # 25.575mm

mm_box_width = box_width - card_box_width - 1.0  # 121.0mm
mm_box_length = card_box_length  # 98.0mm
mm_box_height = tile_thickness * num_mm_hex + lid_thickness * 2.0  # 16.0mm

food_box_width = mm_box_width  # 121.0mm
food_box_length = mm_box_length  # 98.0mm
food_box_height = food_token_num / 6.0 * food_token_thickness + wall_thickness * 2.0  # 23.5mm

predator_box_width = mm_box_width  # 121.0mm
predator_box_length = mm_box_length  # 98.0mm
predator_box_height = usable_height - food_box_height - mm_box_height - 1.0  # 18.5mm

player_box_width = (box_width - 1.0) / 2.0  # 97.0mm
player_box_length = box_length - tile_box_length - card_box_length - 1.0  # 72.505mm
player_box_height = usable_height / 3.0  # 19.667mm

project = Project(
    "MarchOfTheAnts",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
    box_defaults={"expandable": False},
)

ANT_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── Row 0: Territory Hex Tiles Box (Y = 0 .. 103.5) ───────────────
t_box = project.box(
    BoxType.CAP,
    "HexTileBox",
    size=(tile_box_width, tile_box_length, tile_box_height),
    position=(0.0, 0.0, 0.0),
    lid=LidBuilder(
        text="Tiles",
        label_mode=LabelMode.FRAMED,
        pattern=ANT_PATTERN,
        text_color=Color("white"),
        frame_color=Color("saddlebrown"),
    ),
)
t_box.compartment("Hexes_Left", width_ratio=0.5, cut=FingerCut.SCOOP)
t_box.compartment("Hexes_Right", width_ratio=0.5, cut=FingerCut.SCOOP)

# ── Row 1: Cards, Minions Hexes, Food & Predators (Y = 103.5 .. 201.5) ──
row1_y = tile_box_length

project.box(
    BoxType.CAP,
    "CardBox_Base",
    size=(card_box_width, card_box_length, card_box_height),
    position=(0.0, row1_y, 0.0),
    lid=LidBuilder(
        text="Cards",
        label_mode=LabelMode.FRAMED,
        pattern=ANT_PATTERN,
        text_color=Color("white"),
        frame_color=Color("royalblue"),
    ),
).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.CAP,
    "CardBox_Expansion",
    size=(card_box_width, card_box_length, mm_card_box_height),
    position=(0.0, row1_y, card_box_height),
    lid=LidBuilder(
        text="Minions Cards",
        label_mode=LabelMode.FRAMED,
        pattern=ANT_PATTERN,
        text_color=Color("white"),
        frame_color=Color("purple"),
    ),
).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.CAP,
    "MinionsOfTheMeadowBox",
    size=(mm_box_width, mm_box_length, mm_box_height),
    position=(card_box_width, row1_y, 0.0),
    lid=LidBuilder(
        text="Minions Hexes",
        label_mode=LabelMode.FRAMED,
        pattern=ANT_PATTERN,
        text_color=Color("white"),
        frame_color=Color("olive"),
    ),
).compartment("ExpansionHexes", cut=FingerCut.SCOOP)

food_box = project.box(
    BoxType.CAP,
    "FoodTokensBox",
    size=(food_box_width, food_box_length, food_box_height),
    position=(card_box_width, row1_y, mm_box_height),
    lid=LidBuilder(
        text="Food",
        label_mode=LabelMode.FRAMED,
        pattern=ANT_PATTERN,
        text_color=Color("white"),
        frame_color=Color("forestgreen"),
    ),
)
food_box.compartment("FoodTokens", width_ratio=0.45, cut=FingerCut.SCOOP)
food_box.compartment("CentipedeAndDayNight", width_ratio=0.55, cut=FingerCut.SCOOP)

project.box(
    BoxType.CAP,
    "PredatorsBox",
    size=(predator_box_width, predator_box_length, predator_box_height),
    position=(card_box_width, row1_y, mm_box_height + food_box_height),
    lid=LidBuilder(
        text="Predator",
        label_mode=LabelMode.FRAMED,
        pattern=ANT_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkred"),
    ),
).compartment("Predators", cut=FingerCut.SCOOP)

# ── Row 2: 5 Player Boxes & Aphid Box (Y = 201.5 .. 274.0) ────────
row2_y = row1_y + card_box_length

player_placements = [
    ("Red", "darkred", 0.0, 0),
    ("Yellow", "gold", 0.0, 1),
    ("Black", "black", 0.0, 2),
    ("Blue", "navy", player_box_width, 0),
    ("Green", "forestgreen", player_box_width, 1),
]

for p_name, color_name, x_pos, layer in player_placements:
    p_box = project.box(
        BoxType.CAP,
        f"PlayerBox_{p_name}",
        size=(player_box_width, player_box_length, player_box_height),
        position=(x_pos, row2_y, player_box_height * layer),
        lid=LidBuilder(
            text=f"Player ({p_name})",
            label_mode=LabelMode.FRAMED,
            pattern=ANT_PATTERN,
            text_color=Color("black" if color_name == "gold" else "white"),
            frame_color=Color(color_name),
        ),
    )
    p_box.compartment("CubesAndWorkers", cut=FingerCut.SCOOP)

project.box(
    BoxType.CAP,
    "AphidBox",
    size=(player_box_width, player_box_length, player_box_height),
    position=(player_box_width, row2_y, player_box_height * 2.0),
    lid=LidBuilder(
        text="Aphids",
        label_mode=LabelMode.FRAMED,
        pattern=ANT_PATTERN,
        text_color=Color("white"),
        frame_color=Color("yellowgreen"),
    ),
).compartment("Aphids", cut=FingerCut.SCOOP)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
