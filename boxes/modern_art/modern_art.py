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

ART_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Art Cards Box (Row 0, Y = 0) ───────────────────────────────
c_box = project.box(
    BoxType.CAP,
    "CardBox",
    size=(card_box_width, card_box_length, card_box_height),
    lid=LidBuilder(
        text="Modern Art Cards",
        label_mode=LabelMode.FRAMED,
        pattern=ART_PATTERN,
        text_color=Color("white"),
        frame_color=Color("royalblue"),
    ),
    position=(0.0, 0.0, 0.0),
    no_rotate=True,
)
c_box.compartment(
    "Paintings_1",
    width_ratio=0.5,
    depth=card_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)
c_box.compartment(
    "Paintings_2",
    width_ratio=0.5,
    depth=card_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── 2. Auction Money & Chips Box (Row 1, Y = card_box_length) ─────
y_tokens = card_box_length

t_box = project.box(
    BoxType.CAP,
    "TokensBox",
    size=(token_box_width, token_box_length, token_box_height),
    lid=LidBuilder(
        text="Money & Chips",
        label_mode=LabelMode.FRAMED,
        pattern=ART_PATTERN,
        text_color=Color("white"),
        frame_color=Color("goldenrod"),
    ),
    position=(0.0, y_tokens, 0.0),
    no_rotate=True,
)
t_box.compartment(
    "MoneyTokens",
    length_ratio=0.6,
    depth=token_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)
t_box.compartment(
    "ValueMarkers",
    length_ratio=0.4,
    depth=token_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
