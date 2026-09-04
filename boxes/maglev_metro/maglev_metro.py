#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Maglev Metro board game organizer.

Ports examples/maglev_metro.scad to the pyboxbuilder Project API.
Organizes card decks, factory station hex tiles, player boards,
robots, commuter meeples, and trains with automated spacers.
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
box_width = 286.0
box_length = 286.0
box_height = 65.0

game_board_base_thickness = 4.2 * 2.0   # 8.4mm
player_board_thickness = 2.2 * 4.0      # 8.8mm
total_board_reserve = game_board_base_thickness + player_board_thickness  # 17.2mm
usable_height = box_height - total_board_reserve  # 47.8mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

card_width = 67.0
card_length = 90.0
card_box_width = wall_thickness * 2.0 + card_width    # 73.0mm
card_box_length = wall_thickness * 2.0 + card_length  # 96.0mm
card_box_height = usable_height / 2.0                 # 23.9mm

player_box_width = 61.5                               # hex width + walls
player_box_length = box_width / 2.0                   # 143.0mm
player_box_height = usable_height / 2.0               # 23.9mm

factory_box_width = (box_width - card_box_width - player_box_width) / 2.0  # ~75.75mm
factory_box_length = box_width / 4.0                                       # 71.5mm
factory_box_height = usable_height / 2.0

project = Project(
    "MaglevMetro",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=total_board_reserve,
    generate_spacers=True,
)

METRO_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Card Boxes (2 columns of 2, stacked 2 high) ────────────────
card_titles = ["Connections", "Passengers", "Tracks", "Player Objectives"]
for idx, title in enumerate(card_titles):
    tier = idx // 2
    col = idx % 2
    c_box = project.box(
        BoxType.SLIDING,
        f"CardBox_{title.replace(' ', '')}",
        size=(card_box_width, card_box_length, card_box_height),
        lid=LidBuilder(
            text=title,
            label_mode=LabelMode.FRAMED,
            pattern=METRO_PATTERN,
            text_color=Color("white"),
            frame_color=Color("royalblue"),
        ),
        position=(0.0, col * card_box_length, tier * card_box_height),
        no_rotate=True,
    )
    c_box.compartment(
        "Cards",
        depth=card_box_height - lid_thickness,
        cut=FingerCut.SCOOP,
    )

# ── 2. Player Boxes (4 colors, 2 stacked in 2 tiers) ──────────────
player_colors = ["green", "deeppink", "cyan", "darkorange"]
for idx, color_name in enumerate(player_colors):
    col = idx % 2
    tier = idx // 2
    p_box = project.box(
        BoxType.SLIDING,
        f"PlayerBox_{color_name}",
        size=(player_box_width, player_box_length, player_box_height),
        lid=LidBuilder(
            text=f"Player ({color_name.title()})",
            label_mode=LabelMode.FRAMED,
            pattern=METRO_PATTERN,
            text_color=Color("white"),
            frame_color=Color(color_name),
        ),
        position=(card_box_width, col * player_box_length, tier * player_box_height),
        no_rotate=True,
    )
    p_box.compartment(
        "TrackHexes",
        length_ratio=0.6,
        depth=player_box_height - lid_thickness,
        cut=FingerCut.SCOOP,
    )
    p_box.compartment(
        "TrainsAndBits",
        length_ratio=0.4,
        depth=player_box_height - lid_thickness,
        cut=FingerCut.SCOOP,
    )

# ── 3. Factory Station Hex Tile Boxes (6 types, 2x3 grid) ─────────
factory_types = ["Factories", "Warehouses", "Labs", "Offices", "Stores", "Embassies"]
x_factories = card_box_width + player_box_width  # 134.5mm

for idx, f_name in enumerate(factory_types):
    col = idx % 2
    row = idx // 2
    f_box = project.box(
        BoxType.SLIDING,
        f"FactoryBox_{f_name}",
        size=(factory_box_width, factory_box_length, factory_box_height),
        lid=LidBuilder(
            text=f_name,
            label_mode=LabelMode.FRAMED,
            pattern=METRO_PATTERN,
            text_color=Color("white"),
            frame_color=Color("goldenrod"),
        ),
        position=(x_factories + col * factory_box_width, row * factory_box_length, 0.0),
        no_rotate=True,
    )
    f_box.compartment(
        "StationHexes",
        depth=factory_box_height - lid_thickness,
        cut=FingerCut.SCOOP,
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
