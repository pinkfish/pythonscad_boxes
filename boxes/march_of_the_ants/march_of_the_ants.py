#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""March of the Ants board game organizer.

Ports examples/march_of_the_ants.scad to the pyboxbuilder Project API.
Organizes territory hexes, evolution cards, player ant cubes, food tokens,
aphids, and predator meeples with automated spacers.
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
box_width = 195.0
box_length = 275.0
box_height = 65.0

board_thickness = 6.0
usable_height = box_height - board_thickness  # 59.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

tile_width = 84.0
tile_box_width = box_width - 1.0  # 194.0mm
tile_box_length = 100.0
tile_box_height = usable_height   # 59.0mm

card_box_width = 73.0
card_box_length = 98.0
card_box_height = usable_height / 2.0  # 29.5mm

res_box_width = box_width - card_box_width - 1.0  # 121.0mm
res_box_length = card_box_length                  # 98.0mm
res_box_height = usable_height / 2.0              # 29.5mm

player_box_width = (box_width - 1.0) / 2.0        # 97.0mm
player_box_length = box_length - tile_box_length - card_box_length - 1.0  # 76.0mm
player_box_height = usable_height / 3.0           # 19.66mm

project = Project(
    "MarchOfTheAnts",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

ANT_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Territory Hex Tiles Box (Row 0, Y = 0) ─────────────────────
t_box = project.box(
    BoxType.CAP,
    "HexTileBox",
    size=(tile_box_width, tile_box_length, tile_box_height),
    lid=LidBuilder(
        text="Territory Hexes",
        label_mode=LabelMode.FRAMED,
        pattern=ANT_PATTERN,
        text_color=Color("white"),
        frame_color=Color("saddlebrown"),
    ),
    position=(0.0, 0.0, 0.0),
    no_rotate=True,
)
t_box.compartment("Hexes_Left", width_ratio=0.5, depth=tile_box_height - floor_thickness - 1.0, cut=FingerCut.SCOOP)
t_box.compartment("Hexes_Right", width_ratio=0.5, depth=tile_box_height - floor_thickness - 1.0, cut=FingerCut.SCOOP)

# ── 2. Card Boxes & Resource Trays (Row 1, Y = tile_box_length) ───
y_cards = tile_box_length

project.box(
    BoxType.SLIDING,
    "CardBox_Base",
    size=(card_box_width, card_box_length, card_box_height),
    lid=LidBuilder(
        text="Base Cards",
        label_mode=LabelMode.FRAMED,
        pattern=ANT_PATTERN,
        text_color=Color("white"),
        frame_color=Color("royalblue"),
    ),
    position=(0.0, y_cards, 0.0),
    no_rotate=True,
).compartment("Cards", depth=card_box_height - lid_thickness, cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "CardBox_Expansion",
    size=(card_box_width, card_box_length, card_box_height),
    lid=LidBuilder(
        text="Minions Cards",
        label_mode=LabelMode.FRAMED,
        pattern=ANT_PATTERN,
        text_color=Color("white"),
        frame_color=Color("purple"),
    ),
    position=(0.0, y_cards, card_box_height),
    no_rotate=True,
).compartment("Cards", depth=card_box_height - lid_thickness, cut=FingerCut.SCOOP)

project.box(
    BoxType.CAP,
    "FoodTokensBox",
    size=(res_box_width, res_box_length, res_box_height),
    lid=LidBuilder(
        text="Food & Aphids",
        label_mode=LabelMode.FRAMED,
        pattern=ANT_PATTERN,
        text_color=Color("white"),
        frame_color=Color("forestgreen"),
    ),
    position=(card_box_width, y_cards, 0.0),
    no_rotate=True,
).compartment("Food", depth=res_box_height - floor_thickness - 1.0, cut=FingerCut.SCOOP)

project.box(
    BoxType.CAP,
    "PredatorsBox",
    size=(res_box_width, res_box_length, res_box_height),
    lid=LidBuilder(
        text="Predators",
        label_mode=LabelMode.FRAMED,
        pattern=ANT_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkred"),
    ),
    position=(card_box_width, y_cards, res_box_height),
    no_rotate=True,
).compartment("Predators", depth=res_box_height - floor_thickness - 1.0, cut=FingerCut.SCOOP)

# ── 3. Player Ant Colony Boxes (Row 2, Y = tile + card = 198mm) ───
y_players = tile_box_length + card_box_length

player_factions = [
    ("Red", "darkred"),
    ("Blue", "navy"),
    ("Yellow", "gold"),
    ("Green", "forestgreen"),
    ("Black", "black"),
]

for idx, (p_name, color_name) in enumerate(player_factions):
    col = idx % 2
    tier = idx // 2
    p_box = project.box(
        BoxType.CAP,
        f"PlayerBox_{p_name}",
        size=(player_box_width, player_box_length, player_box_height),
        lid=LidBuilder(
            text=f"Ants ({p_name})",
            label_mode=LabelMode.FRAMED,
            pattern=ANT_PATTERN,
            text_color=Color("black" if color_name == "gold" else "white"),
            frame_color=Color(color_name),
        ),
        position=(col * player_box_width, y_players, tier * player_box_height),
        no_rotate=True,
    )
    p_box.compartment("Cubes", depth=player_box_height - floor_thickness - 1.0, cut=FingerCut.SCOOP)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
