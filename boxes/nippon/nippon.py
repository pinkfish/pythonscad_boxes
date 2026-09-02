#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Nippon board game organizer.

Ports examples/nippon.scad to the pyboxbuilder Project API.
Organizes 4 player boxes (trains, ships, scoring markers), factory tiles,
demand tiles, resource cubes, contracts, and solo components with automated spacers.
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
    columns,
    run,
    stack,
)

# ── Game Box Dimensions ───────────────────────────────────────────
box_width = 303.0
box_length = 380.0
box_height = 70.0

board_thickness = 9.0
player_boards_thickness = 4.3 * 4.0  # 17.2mm
handbook_thickness = 6.0
total_board_reserve = board_thickness + player_boards_thickness + handbook_thickness  # 32.2mm
usable_height = box_height - total_board_reserve  # 37.8mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

player_box_width = box_width / 4.0    # 75.75mm
player_box_length = 92.0
player_box_height = usable_height / 2.0  # 18.9mm

factory_tile_width = 58.0
factory_tile_length = 62.5

project = Project(
    "Nippon",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=total_board_reserve,
    generate_spacers=True,
)

NIPPON_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Player Boxes (4 colors) ────────────────────────────────────
player_colors = ["white", "yellow", "red", "purple"]

for idx, color_name in enumerate(player_colors):
    box = project.box(
        BoxType.CAP,
        f"PlayerBox_{color_name}",
        size=(player_box_width, player_box_length, player_box_height),
        lid=LidBuilder(
            text=f"Player ({color_name.title()})",
            label_mode=LabelMode.FRAMED,
            pattern=NIPPON_PATTERN,
            text_color=Color("black" if color_name in ["white", "yellow"] else "white"),
            frame_color=Color(color_name if color_name != "white" else "silver"),
        ),
        position=(idx * player_box_width, 0.0, 0.0),
        no_rotate=True,
    )
    # Ships & Trains compartment
    box.compartment(
        "TrainsAndShips",
        width_ratio=0.6,
        depth=player_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )
    # Scoring discs & markers
    box.compartment(
        "DiscsAndMarkers",
        width_ratio=0.4,
        depth=player_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )

# ── 2. Factory & Demand Tile Boxes (Row 2) ─────────────────────────
y_offset = player_box_length  # 92.0mm

tile_boxes = [
    ("FactoryTiles_1", "Factories I"),
    ("FactoryTiles_2", "Factories II"),
    ("DemandTiles", "Demand"),
    ("StartingTiles", "Starting"),
]

tile_box_width = box_width / 4.0

for idx, (label, text) in enumerate(tile_boxes):
    project.box(
        BoxType.SLIDING,
        label,
        size=(tile_box_width, factory_tile_length, usable_height),
        lid=LidBuilder(
            text=text,
            label_mode=LabelMode.FRAMED,
            pattern=NIPPON_PATTERN,
            text_color=Color("white"),
            frame_color=Color("navy"),
        ),
        position=(idx * tile_box_width, y_offset, 0.0),
        no_rotate=True,
    ).compartment(
        "Tiles",
        depth=usable_height - lid_thickness,
        cut=FingerCut.SCOOP,
    )

# ── 3. Resource Cubes & Money Trays (Row 3) ───────────────────────
y_offset_3 = y_offset + factory_tile_length  # 154.5mm
resource_box_length = 80.0

for idx, (label, text, color) in enumerate([
    ("ResourceCubes_SilkPaper", "Silk & Paper", "crimson"),
    ("ResourceCubes_CoalCopper", "Coal & Copper", "dimgray"),
    ("MoneyAndContracts", "Money & Contracts", "gold"),
]):
    res_width = box_width / 3.0
    project.box(
        BoxType.CAP,
        label,
        size=(res_width, resource_box_length, usable_height / 2.0),
        lid=LidBuilder(
            text=text,
            label_mode=LabelMode.FRAMED,
            pattern=NIPPON_PATTERN,
            text_color=Color("white"),
            frame_color=Color(color),
        ),
        position=(idx * res_width, y_offset_3, 0.0),
        no_rotate=True,
    ).compartment(
        "Resources",
        depth=usable_height / 2.0 - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
