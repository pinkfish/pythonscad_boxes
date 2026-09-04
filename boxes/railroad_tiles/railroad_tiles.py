#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Railroad Tiles board game organizer.

Ports examples/railroad_tiles.scad to the pyboxbuilder Project API.
Organizes square railroad track tiles, objective tiles, player markers,
and starting clock tiles with automated spacers.
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
box_width = 230.0
box_length = 230.0
box_height = 63.0

board_thickness = 2.5
usable_height = box_height - board_thickness  # 60.5mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

railroad_tile = 46.0
clock_diameter = 32.0

player_box_width = (box_width - 2.0) / 2.0            # 114.0mm
player_box_length = clock_diameter + wall_thickness * 2.0  # 38.0mm
player_box_height = 12.0

token_box_width = (box_width - 2.0) / 4.0             # 57.0mm
token_box_length = player_box_length                  # 38.0mm
token_box_height = (usable_height - player_box_height) / 2.0  # 24.25mm

objective_box_width = player_box_width                # 114.0mm
objective_box_length = wall_thickness * 2.0 + railroad_tile  # 52.0mm
objective_box_height = usable_height / 5.0            # 12.1mm

project = Project(
    "RailroadTiles",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

TILE_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Tokens Boxes (4 columns, stacked 2 high at Y = 0) ──────────
token_labels = ["Tokens_1", "Tokens_2", "Tokens_3", "Tokens_4"]
for idx, label in enumerate(token_labels):
    for tier in range(2):
        t_box = project.box(
            BoxType.CAP,
            f"{label}_Tier{tier + 1}",
            size=(token_box_width, token_box_length, token_box_height),
            lid=LidBuilder(
                text=label,
                label_mode=LabelMode.FRAMED,
                pattern=TILE_PATTERN,
                text_color=Color("white"),
                frame_color=Color("navy"),
            ),
            position=(idx * token_box_width, 0.0, tier * token_box_height),
            no_rotate=True,
        )
        t_box.compartment(
            "Tokens",
            depth=token_box_height - floor_thickness - 1.0,
            cut=FingerCut.SCOOP,
        )

# ── 2. Player & Starting Marker Boxes (atop token boxes) ──────────
z_top = token_box_height * 2.0

project.box(
    BoxType.CAP,
    "PlayerMarkersBox",
    size=(player_box_width, player_box_length, player_box_height),
    lid=LidBuilder(
        text="Player Markers",
        label_mode=LabelMode.FRAMED,
        pattern=TILE_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkgreen"),
    ),
    position=(0.0, 0.0, z_top),
    no_rotate=True,
).compartment(
    "Markers",
    depth=player_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

project.box(
    BoxType.CAP,
    "StartingClocksBox",
    size=(player_box_width, player_box_length, player_box_height),
    lid=LidBuilder(
        text="Clocks",
        label_mode=LabelMode.FRAMED,
        pattern=TILE_PATTERN,
        text_color=Color("white"),
        frame_color=Color("gold"),
    ),
    position=(player_box_width, 0.0, z_top),
    no_rotate=True,
).compartment(
    "Clocks",
    depth=player_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── 3. Objective Tile Boxes (5 stacked trays at Y = token_box_length)
for i in range(5):
    obj_box = project.box(
        BoxType.CAP,
        f"ObjectiveBox_{i + 1}",
        size=(objective_box_width, objective_box_length, objective_box_height),
        lid=LidBuilder(
            text=f"Objectives {i + 1}",
            label_mode=LabelMode.FRAMED,
            pattern=TILE_PATTERN,
            text_color=Color("white"),
            frame_color=Color("darkorange"),
        ),
        position=(0.0, token_box_length, i * objective_box_height),
        no_rotate=True,
    )
    obj_box.compartment(
        "ObjectiveTiles_Left",
        width_ratio=0.5,
        depth=objective_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )
    obj_box.compartment(
        "ObjectiveTiles_Right",
        width_ratio=0.5,
        depth=objective_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
