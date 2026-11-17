#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Earth board game organizer.

Ports examples/earth.scad to the pyboxbuilder Project API.
Organizes flora, terrain, event, and abundance cards, trunk pieces,
canopy tops, sprout cubes, and player tokens with automated spacers.
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
box_width = 288.0
box_length = 288.0
box_height = 72.0

player_board_thickness = 2.1 * 6.0   # 12.6mm
middle_board_thickness = 2.1 * 2.0   # 4.2mm
total_board_reserve = player_board_thickness + middle_board_thickness  # 16.8mm
usable_height = box_height - total_board_reserve  # 55.2mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

card_width = 62.0
card_length = 93.0
card_box_width = card_width + wall_thickness * 2.0   # 68.0mm
card_box_length = card_length + wall_thickness * 2.0  # 99.0mm
card_box_height = usable_height                       # 55.2mm

canopy_box_width = 75.0
canopy_box_length = 90.0
canopy_box_height = usable_height

sprout_box_width = canopy_box_width
sprout_box_length = canopy_box_length
sprout_box_height = usable_height

project = Project(
    "Earth",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=total_board_reserve,
    generate_spacers=True,
)

EARTH_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Main Card Decks ────────────────────────────────────────────
decks = [
    ("Flora", "Flora Cards", "forestgreen"),
    ("Terrain", "Terrain Cards", "sienna"),
    ("Events", "Event Cards", "royalblue"),
    ("Abundance", "Abundance", "darkgoldenrod"),
]

for deck_id, title, color_name in decks:
    c_box = project.box(
        BoxType.SLIDING,
        f"CardBox_{deck_id}",
        size=(card_box_width, card_box_length, card_box_height),
        lid=LidBuilder(
            text=title,
            label_mode=LabelMode.FRAMED,
            pattern=EARTH_PATTERN,
            text_color=Color("white"),
            frame_color=Color(color_name),
        ),
        expandable=False,
    )
    c_box.compartment(
        "Cards",
        cut=FingerCut.SCOOP,
    )

# ── 2. Canopies, Trunks & Sprout Cubes ────────────────────────────
project.box(
    BoxType.CAP,
    "CanopyBox",
    size=(canopy_box_width, canopy_box_length, canopy_box_height),
    lid=LidBuilder(
        text="Canopies",
        label_mode=LabelMode.FRAMED,
        pattern=EARTH_PATTERN,
        text_color=Color("white"),
        frame_color=Color("peru"),
    ),
).compartment(
    "CanopiesAndTrunks",
    cut=FingerCut.SCOOP,
)

project.box(
    BoxType.CAP,
    "SproutBox",
    size=(sprout_box_width, sprout_box_length, sprout_box_height),
    lid=LidBuilder(
        text="Sprouts",
        label_mode=LabelMode.FRAMED,
        pattern=EARTH_PATTERN,
        text_color=Color("white"),
        frame_color=Color("limegreen"),
    ),
).compartment(
    "SproutCubes",
    cut=FingerCut.SCOOP,
)

# ── 3. Player Leaf Token Trays (6 players) ────────────────────────
player_colors = ["red", "green", "yellow", "blue", "purple", "pink"]
p_width = (box_width - canopy_box_width * 2.0) / 2.0  # 69.0mm
p_length = canopy_box_length                         # 90.0mm
p_height = usable_height / 3.0                       # 18.4mm

for color_name in player_colors:
    p_box = project.box(
        BoxType.CAP,
        f"PlayerBox_{color_name.title()}",
        size=(p_width, p_length, p_height),
        lid=LidBuilder(
            text=f"Player ({color_name.title()})",
            label_mode=LabelMode.FRAMED,
            pattern=EARTH_PATTERN,
            text_color=Color("black" if color_name in ("yellow", "pink") else "white"),
            frame_color=Color(color_name),
        ),
    )
    p_box.compartment(
        "LeafTokens",
        cut=FingerCut.SCOOP,
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
