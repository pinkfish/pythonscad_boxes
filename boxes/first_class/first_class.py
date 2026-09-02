#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""First Class: All Aboard the Orient Express organizer.

Ports examples/first_class.scad to the pyboxbuilder Project API.
Organizes player train/meeple boxes, modular card decks (A-E),
locomotive tiles, and score boards with automatic spacers.
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
    ElementShape,
    FingerCut,
    LabelMode,
    LidBuilder,
    PatternBuilder,
    PatternType,
    Project,
    columns,
    run,
    stack,
    centered,
)

# ── Game Box Dimensions ───────────────────────────────────────────
box_width = 217.0
box_length = 307.0
box_height = 70.0

rule_book_thickness = 3.0
board_thickness = 2.5
usable_height = box_height - rule_book_thickness - board_thickness  # 64.5mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

card_width = 47.0
card_length = 70.0

player_box_width = box_width / 2.0                                # 108.5mm
player_box_length = card_width + wall_thickness * 2.0             # 53.0mm
player_box_height = usable_height / 3.0                            # 21.5mm

card_box_width = box_width / 4.0                                  # 54.25mm
card_box_length = card_length + wall_thickness * 2.0              # 76.0mm
module_box_height = usable_height / 3.0                           # 21.5mm

locomotive_tile_width = 68.5
locomotive_tile_length = 64.5

project = Project(
    "FirstClass",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness + rule_book_thickness,
    generate_spacers=True,
)

ORIENT_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Player Boxes (4 colors, 2x2 stacking) ──────────────────────
player_colors = ["yellow", "blue", "red", "green"]

for idx, color_name in enumerate(player_colors):
    col = idx % 2
    row = idx // 2
    box = project.box(
        BoxType.CAP,
        f"PlayerBox_{color_name}",
        size=(player_box_width, player_box_length, player_box_height),
        lid=LidBuilder(
            text=f"Player ({color_name.title()})",
            label_mode=LabelMode.FRAMED,
            pattern=ORIENT_PATTERN,
            text_color=Color("white"),
            frame_color=Color(color_name),
        ),
        position=(col * player_box_width, row * player_box_length, 0.0),
        no_rotate=True,
    )
    # Meeple slot
    box.compartment(
        "MeeplesAndTrains",
        width_ratio=0.6,
        depth=player_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )
    # Player cubes slot
    box.compartment(
        "Cubes",
        width_ratio=0.4,
        depth=player_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )

# ── 2. Card Boxes (Modules A, B, C, D, E & Railroads) ─────────────
y_offset = player_box_length * 2.0  # 106.0mm

card_decks = [
    ("ModuleA", "Module A"),
    ("ModuleB", "Module B"),
    ("ModuleC", "Module C"),
    ("ModuleD", "Module D"),
    ("ModuleE", "Module E"),
    ("RailroadCards", "Railroads"),
]

for idx, (deck_id, label_text) in enumerate(card_decks):
    col = idx % 4
    tier = idx // 4
    project.box(
        BoxType.SLIDING,
        f"CardBox_{deck_id}",
        size=(card_box_width, card_box_length, module_box_height),
        lid=LidBuilder(
            text=label_text,
            label_mode=LabelMode.FRAMED,
            pattern=ORIENT_PATTERN,
            text_color=Color("white"),
            frame_color=Color("darkblue"),
        ),
        position=(col * card_box_width, y_offset + tier * card_box_length, 0.0),
        no_rotate=True,
    ).compartment(
        "Cards",
        depth=module_box_height - lid_thickness,
        cut=FingerCut.SCOOP,
    )

# ── 3. Locomotive Tile Box ────────────────────────────────────────
loco_width = locomotive_tile_width + wall_thickness * 2.0
loco_length = locomotive_tile_length + wall_thickness * 2.0
loco_height = usable_height / 2.0

project.box(
    BoxType.CAP,
    "LocomotiveTileBox",
    size=(loco_width, loco_length, loco_height),
    lid=LidBuilder(
        text="Locomotives",
        label_mode=LabelMode.FRAMED,
        pattern=ORIENT_PATTERN,
        text_color=Color("white"),
        frame_color=Color("gold"),
    ),
    position=(card_box_width * 2.0, y_offset + card_box_length, 0.0),
    no_rotate=True,
).compartment(
    "Tiles",
    depth=loco_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
