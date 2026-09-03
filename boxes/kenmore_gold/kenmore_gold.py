#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Kenmore Gold board game organizer.

Ports examples/kenmore_gold.scad to the pyboxbuilder Project API.
Organizes square dungeon tiles, start cave piece, and loot tokens
with automated spacers.
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

# ── Box Dimensions ────────────────────────────────────────────────
box_width = 130.0
box_length = 120.0
box_height = 77.0

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

square_tile_width = 58.0
tile_box_width = square_tile_width * 2.0 + wall_thickness * 2.0 + 2.0  # 124.0mm
tile_box_length = square_tile_width + wall_thickness * 2.0              # 64.0mm
tile_box_height = 69.0

start_cave_box_width = tile_box_width
start_cave_box_length = 50.0
start_cave_box_height = 21.0

loot_box_width = tile_box_width
loot_box_length = 50.0
loot_box_height = tile_box_height - start_cave_box_height  # 48.0mm

project = Project(
    "KenmoreGold",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    generate_spacers=True,
)

GOLD_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Square Dungeon Tile Box (Row 0, Y = 0) ─────────────────────
t_box = project.box(
    BoxType.CAP,
    "SquareTileBox",
    size=(tile_box_width, tile_box_length, tile_box_height),
    lid=LidBuilder(
        text="Kenmore Gold",
        label_mode=LabelMode.FRAMED,
        pattern=GOLD_PATTERN,
        text_color=Color("white"),
        frame_color=Color("goldenrod"),
    ),
    position=(0.0, 0.0, 0.0),
    no_rotate=True,
)
t_box.compartment(
    "Tiles_A",
    width_ratio=0.5,
    depth=tile_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)
t_box.compartment(
    "Tiles_B",
    width_ratio=0.5,
    depth=tile_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── 2. Start Cave & Loot Boxes (Row 1, Y = tile_box_length = 64mm) 
y_cave = tile_box_length

project.box(
    BoxType.CAP,
    "StartCaveBox",
    size=(start_cave_box_width, start_cave_box_length, start_cave_box_height),
    lid=LidBuilder(
        text="Start Cave",
        label_mode=LabelMode.FRAMED,
        pattern=GOLD_PATTERN,
        text_color=Color("white"),
        frame_color=Color("saddlebrown"),
    ),
    position=(0.0, y_cave, 0.0),
    no_rotate=True,
).compartment(
    "CaveTile",
    depth=start_cave_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

project.box(
    BoxType.CAP,
    "LootBox",
    size=(loot_box_width, loot_box_length, loot_box_height),
    lid=LidBuilder(
        text="Loot",
        label_mode=LabelMode.FRAMED,
        pattern=GOLD_PATTERN,
        text_color=Color("white"),
        frame_color=Color("gold"),
    ),
    position=(0.0, y_cave, start_cave_box_height),
    no_rotate=True,
).compartment(
    "LootTokens",
    depth=loot_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
