#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Canvas board game organizer.

Ports boxes/canvas/canvas.scad to the pyboxbuilder Project API.
Organizes:
- 2 independent Art Card boxes (ArtCardsBox_Left, ArtCardsBox_Right — 73 x 124 x 30mm)
  at the front-left and front-right (Y = 0..124mm) for the two 70 x 120mm Tarot art
  card stacks.
- 6 Ribbon token boxes (Red, Green, Grey, Blue, Purple, Palette — 73 x 41 x 29mm)
  arranged in two columns of 3 along the left and right walls (Y = 124..247mm).
- 1 open-ended, stepped-wall PlaymatSpacer cradle (50 x 247 x 29mm) running down
  the center channel (X = 73..123mm) with no front/back ends, 50% wall height
  along the middle for easy playmat removal, and full-height end posts bracing
  the adjacent card and ribbon boxes.
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
    LabelShape,
    LidBuilder,
    PatternBuilder,
    PatternType,
    Project,
    ScoopSide,
    run,
)

# ── Box & Channel Dimensions (matching canvas.scad) ───────────────
box_width = 200.0
box_length = 250.0
box_height = 50.0

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

piece_box_width = 73.0   # X-span (matches divider_upright_diff = 73mm)
piece_box_length = 41.0  # Y-span (3 x 41 = 123mm)
piece_box_height = 29.0

playmat_channel_width = 50.0  # 50mm center channel for the rolled-up cloth playmat
card_box_width = piece_box_width  # 73.0mm (interior 70.0mm with 1.5mm walls)
card_box_length = 124.0           # 124.0mm (interior 121.0mm for 120mm Tarot art cards)
card_box_height = 30.0

playmat_spacer_length = card_box_length + piece_box_length * 3.0  # 247.0mm
playmat_spacer_height = piece_box_height                          # 29.0mm

right_col_x = piece_box_width + playmat_channel_width  # 123.0mm

project = Project(
    "Canvas",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    generate_spacers=False,  # Center channel is occupied by PlaymatSpacer cradle
    box_defaults={"expandable": False},
)

# Circle lid pattern matching canvas.scad (SHAPE_TYPE_CIRCLE, width=7, thickness=1.5)
CANVAS_PATTERN = PatternBuilder(PatternType.CIRCLE, spacing=7.0, web=1.5)

# ── 1. Two Independent Art Card Boxes (Y = 0 .. 124mm) ────────────
# Left (X = 0..73mm) and Right (X = 123..196mm) flanking the 50mm center playmat channel.
for box_id, col_x in (("ArtCardsBox_Left", 0.0), ("ArtCardsBox_Right", right_col_x)):
    project.box(
        BoxType.SLIDING,
        box_id,
        size=(card_box_width, card_box_length, card_box_height),
        position=(col_x, 0.0, 0.0),
        wall_thickness=1.5,
        floor_thickness=1.5,
        lid=LidBuilder(
            text="Art Cards",
            label_mode=LabelMode.FRAMED,
            label_shape=LabelShape.PILL,
            pattern=CANVAS_PATTERN,
            text_color=Color("white"),
            frame_color=Color("darkslateblue"),
        ),
    ).compartment(
        "ArtCards",
        cut=FingerCut.SCOOP,
    )

# ── 2. Center Playmat Cradle Spacer (X = 73 .. 123mm, Y = 0 .. 247mm)
# Open front & back ends so the rolled playmat lies straight down the middle,
# with 50% wall height along the middle span and full-height end walls bracing
# the flanking card and ribbon boxes.
project.box(
    BoxType.NO_LID,
    "PlaymatSpacer",
    size=(playmat_channel_width, playmat_spacer_length, playmat_spacer_height),
    position=(piece_box_width, 0.0, 0.0),
    wall_thickness=2.0,
    floor_thickness=1.5,
    open_sides=(ScoopSide.FRONT, ScoopSide.BACK),
    mid_wall_height_ratio=0.5,
    end_wall_length=30.0,
)

# ── 3. Six Ribbon Token Boxes Flanking the Center Playmat Channel ─
# Left column (X = 0..73mm) and right column (X = 123..196mm), Y = 124..247mm
left_ribbons = [
    ("Red", "Red", "darkred"),
    ("Green", "Green", "forestgreen"),
    ("Grey", "Grey", "gray"),
]
right_ribbons = [
    ("Blue", "Blue", "navy"),
    ("Purple", "Purple", "purple"),
    ("Palette", "Palette", "goldenrod"),
]

for col_x, group in ((0.0, left_ribbons), (right_col_x, right_ribbons)):
    for row_idx, (token_id, title, color_name) in enumerate(group):
        r_box = project.box(
            BoxType.CAP,
            f"RibbonBox_{token_id}",
            size=(piece_box_width, piece_box_length, piece_box_height),
            position=(col_x, card_box_length + row_idx * piece_box_length, 0.0),
            lid=LidBuilder(
                text=title,
                label_mode=LabelMode.FRAMED,
                label_shape=LabelShape.PILL,
                pattern=CANVAS_PATTERN,
                text_color=Color("white"),
                frame_color=Color(color_name),
            ),
        )
        r_box.compartment(
            "Ribbons",
            cut=FingerCut.SCOOP,
        )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
