#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Brink board game organizer.

Ports examples/brink.scad to the pyboxbuilder Project API.
Organizes action cards, rider cards, ambassador cards, hex sector tiles,
player upgrade tokens, and faction resource cubes with automated spacers.
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

card_width = 66.5
card_length = 91.5

small_card_width = 49.0
small_card_length = 71.5

hex_width = 72.0

ambassador_box_width = box_width / 2.0 - 1.0          # 106.5mm
ambassador_box_length = small_card_length + wall_thickness * 2.0  # 77.5mm

player_box_width = (box_width - 3.0) / 2.0            # 106.0mm
player_box_length = 80.0
player_box_height = usable_height / 3.0               # 26.0mm

hex_box_width = box_width - 2.0                       # 213.0mm
hex_box_length = hex_width * 1.5 + wall_thickness * 2.0 + 6.0  # ~120.0mm
hex_box_height = usable_height / 3.0                  # 26.0mm

project = Project(
    "Brink",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

BRINK_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Sector Hex Tile Box (X = 0, Y = 0) ─────────────────────────
hex_box = project.box(
    BoxType.CAP,
    "HexBox",
    size=(hex_box_width, hex_box_length, hex_box_height),
    lid=LidBuilder(
        text="Hex Tiles",
        label_mode=LabelMode.FRAMED,
        pattern=BRINK_PATTERN,
        text_color=Color("white"),
        frame_color=Color("dimgray"),
    ),
    position=(0.0, 0.0, 0.0),
    no_rotate=True,
)
for h in range(3):
    hex_box.compartment(
        f"Sector_{h + 1}",
        width_ratio=1.0 / 3.0,
        depth=hex_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )

# ── 2. Player Boxes (4 boxes: 2 columns, stacked 2 high at Y = hex_box_length)
y_player = hex_box_length

player_factions = ["Solari", "Vanguard", "Eclipse", "Horizon"]
for idx, faction in enumerate(player_factions):
    col = idx % 2
    tier = idx // 2
    p_box = project.box(
        BoxType.CAP,
        f"PlayerBox_{faction}",
        size=(player_box_width, player_box_length, player_box_height),
        lid=LidBuilder(
            text=faction,
            label_mode=LabelMode.FRAMED,
            pattern=BRINK_PATTERN,
            text_color=Color("white"),
            frame_color=Color("royalblue"),
        ),
        position=(col * player_box_width, y_player, tier * player_box_height),
        no_rotate=True,
    )
    p_box.compartment(
        "ShipsAndUpgrades",
        depth=player_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )

# ── 3. Modular Card Boxes (Y = hex_box_length + player_box_length) ─
y_cards = hex_box_length + player_box_length

card_types = [
    ("Actions", "Actions", "gold"),
    ("Riders", "Riders", "firebrick"),
    ("Ambassadors", "Ambassadors", "navy"),
    ("Factions", "Factions", "forestgreen"),
]

for idx, (deck_id, title, color_name) in enumerate(card_types):
    col = idx % 2
    tier = idx // 2
    c_box = project.box(
        BoxType.SLIDING,
        f"CardBox_{deck_id}",
        size=(ambassador_box_width, ambassador_box_length, usable_height / 3.0),
        lid=LidBuilder(
            text=title,
            label_mode=LabelMode.FRAMED,
            pattern=BRINK_PATTERN,
            text_color=Color("white"),
            frame_color=Color(color_name),
        ),
        position=(col * ambassador_box_width, y_cards, tier * (usable_height / 3.0)),
        no_rotate=True,
    )
    c_box.compartment(
        "Cards",
        depth=usable_height / 3.0 - lid_thickness,
        cut=FingerCut.SCOOP,
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
