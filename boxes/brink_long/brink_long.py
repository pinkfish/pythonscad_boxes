#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Brink: Long Box Variant organizer.

Ports examples/brink_long.scad to the pyboxbuilder Project API.
Organizes player fleets in elongated longitudinal trays, action/rider/ambassador
cards, sector hexes, and resources with automated spacers.
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
box_width = 215.0
box_length = 307.0
box_height = 96.0

board_thickness = 18.0
usable_height = box_height - board_thickness  # 78.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

long_player_box_width = 106.0
long_player_box_length = box_length - 2.0  # 305.0mm
long_player_box_height = 24.0

hex_box_width = box_width - 2.0            # 213.0mm
hex_box_length = 114.0
hex_box_height = 24.0

card_box_width = box_width / 2.0 - 1.0     # 106.5mm
card_box_length = 77.5
card_box_height = 24.0

project = Project(
    "BrinkLong",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

BRINK_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Longitudinal Player Trays (Column 0, X = 0) ────────────────
# 2 long trays stacked 2 high along the full box length
player_fleets = [("FleetSolari", "Solari Fleet", "royalblue"), ("FleetHorizon", "Horizon Fleet", "gold")]
for tier, (label, title, color_name) in enumerate(player_fleets):
    p_box = project.box(
        BoxType.CAP,
        label,
        size=(long_player_box_width, long_player_box_length, long_player_box_height),
        lid=LidBuilder(
            text=title,
            label_mode=LabelMode.FRAMED,
            pattern=BRINK_PATTERN,
            text_color=Color("black" if color_name == "gold" else "white"),
            frame_color=Color(color_name),
        ),
        position=(0.0, 0.0, tier * long_player_box_height),
        no_rotate=True,
    )
    p_box.compartment("LongShips", length_ratio=0.5, depth=long_player_box_height - floor_thickness - 1.0, cut=FingerCut.SCOOP)
    p_box.compartment("Upgrades", length_ratio=0.5, depth=long_player_box_height - floor_thickness - 1.0, cut=FingerCut.SCOOP)

# ── 2. Card Boxes (Column 1, X = long_player_box_width) ───────────
x_col1 = long_player_box_width

card_decks = [
    ("Actions", "Actions", "gold"),
    ("Riders", "Riders", "firebrick"),
    ("Ambassadors", "Ambassadors", "navy"),
]

for idx, (deck_id, title, color_name) in enumerate(card_decks):
    c_box = project.box(
        BoxType.SLIDING,
        f"CardBox_{deck_id}",
        size=(card_box_width, card_box_length, card_box_height),
        lid=LidBuilder(
            text=title,
            label_mode=LabelMode.FRAMED,
            pattern=BRINK_PATTERN,
            text_color=Color("white"),
            frame_color=Color(color_name),
        ),
        position=(x_col1, idx * card_box_length, 0.0),
        no_rotate=True,
    )
    c_box.compartment("Cards", depth=card_box_height - lid_thickness, cut=FingerCut.SCOOP)

# ── 3. Sector Hex Box (Column 1, Y = card_box_length * 3) ─────────
y_hex = card_box_length * 3.0  # 232.5mm

h_box = project.box(
    BoxType.CAP,
    "HexBox",
    size=(card_box_width, box_length - y_hex - 2.0, hex_box_height),
    lid=LidBuilder(
        text="Hex Sectors",
        label_mode=LabelMode.FRAMED,
        pattern=BRINK_PATTERN,
        text_color=Color("white"),
        frame_color=Color("dimgray"),
    ),
    position=(x_col1, y_hex, 0.0),
    no_rotate=True,
)
h_box.compartment("Hexes", depth=hex_box_height - floor_thickness - 1.0, cut=FingerCut.SCOOP)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
