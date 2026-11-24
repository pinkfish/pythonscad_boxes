#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Modern Art board game organizer.

Ports examples/modern_art.scad to the pyboxbuilder Project API.
Organizes art cards (2 card wells) and auction money/value tokens
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

from pyboxbuilder import (
    BoxType,
    Color,
    CompartmentElement,
    ElementShape,
    FingerCut,
    LabelFinial,
    LabelMode,
    LabelShape,
    LidBuilder,
    PatternBuilder,
    PatternType,
    Project,
    run,
)

ASSETS = ROOT / "boxes" / "modern_art" / "assets"

# ── Box & Board Dimensions ────────────────────────────────────────
box_width = 154.0
box_length = 208.0
box_height = 44.0

board_thickness = 6.0
usable_height = box_height - board_thickness  # 38.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

card_width = 61.0
card_length = 93.0

card_box_width = box_width - 3.0                     # 151.0mm
card_box_length = card_length + wall_thickness * 2.0 # 99.0mm
card_box_height = usable_height                      # 38.0mm

token_box_width = box_width - 3.0                    # 151.0mm
token_box_length = box_length - card_box_length - 3.0  # 106.0mm
token_box_height = usable_height                     # 38.0mm

project = Project(
    "ModernArt",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

# ── Game Piece Inventory ──────────────────────────────────────────
project.define_inventory({
    "Painting Cards": 70,
    "Money Coins": 112,
    "Artist Value Tiles": 12,
    "Auction Valuation Board": 1,
    "Player Screens": 5,
    "Rulebook": 1,
})

project.board(
    "Board, Screens & Rulebook",
    size=(box_width, box_length, board_thickness),
    position=(0.0, 0.0, usable_height),
    count=7,
    notes="Auction valuation board, 5 player screens, and rulebook atop insert",
    allocates={
        "Auction Valuation Board": 1,
        "Player Screens": 5,
        "Rulebook": 1,
    },
)

ART_PATTERN = PatternBuilder(PatternType.TUMBLING_BLOCKS)
ART_LID = LidBuilder(
    label_mode=LabelMode.FRAMED,
    label_shape=LabelShape.DOUBLE_FRAME,
    label_finial=LabelFinial.DIAMOND,
    font="Futura:style=Bold",
    pattern=ART_PATTERN,
    text_color=Color("white"),
    logo_color=Color("white"),
    logo_position="left",
    label_logo_size_mm=18.0,
)

# ── 1. Art Cards Box ──────────────────────────────────────────────
c_box = project.box(
    BoxType.CAP,
    "CardBox",
    size=(card_box_width, card_box_length, card_box_height),
    lid=ART_LID.titled(
        "Modern Art Cards",
        frame_color=Color("royalblue"),
        logo=str(ASSETS / "easel.svg"),
    ),
    expandable=False,
)
c_box.compartment(
    "Paintings_1",
    width_ratio=0.5,
    cut=FingerCut.SCOOP,
    component="Painting Cards",
    count=35,
)
c_box.compartment(
    "Paintings_2",
    width_ratio=0.5,
    cut=FingerCut.SCOOP,
    component="Painting Cards",
    count=35,
)

# ── 2. Auction Money & Chips Box ──────────────────────────────────
token_inner_width = token_box_width - wall_thickness * 2.0      # 145.0mm
token_inner_length = token_box_length - wall_thickness * 2.0    # 100.0mm
token_inner_height = token_box_height - floor_thickness - lid_thickness  # 34.0mm

t_box = project.box(
    BoxType.CAP,
    "TokensBox",
    size=(token_box_width, token_box_length, token_box_height),
    lid=ART_LID.titled(
        "Money & Chips",
        frame_color=Color("goldenrod"),
        logo=str(ASSETS / "gavel.svg"),
    ),
)
t_box.compartment(
    "Tokens",
    size=(token_inner_width, token_inner_length),
    position=(0.0, 0.0),
    allocates={"Money Coins": 112, "Artist Value Tiles": 12},
    elements=(
        # Single deeply-rounded dish (RoundedBoxAllSides radius=15 in modern_art.scad)
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(token_inner_width, token_inner_length),
            offset=(0.0, 0.0),
            depth=token_inner_height,
            corner_radius=15.0,
            bottom_rounding=15.0,
            pull_out=False,
            label="TokensDish",
        ),
    ),
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
