#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Canvas board game organizer.

Ports examples/canvas.scad to the pyboxbuilder Project API.
Organizes:
- 6 Ribbon token boxes (Red, Green, Grey, Blue, Purple, Palette — 73 x 41 x 29mm)
  arranged in two columns of 3 along the left and right walls (Y = 124..247mm),
  leaving an open 50mm center channel down the middle for the rolled-up cloth playmat.
- 1 PlaymatDivider tray (196 x 124 x 30mm at Y = 0..124mm) holding the two
  70 x 120mm art card stacks on the left and right while continuing the open
  50mm rolled playmat channel through the middle.
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

# ── Box & Divider Dimensions (matching canvas.scad) ───────────────
box_width = 200.0
box_length = 250.0
box_height = 50.0

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

piece_box_width = 73.0   # X-span (matches divider_upright_diff = 73mm)
piece_box_length = 41.0  # Y-span (3 x 41 = 123mm)
piece_box_height = 29.0

playmat_channel_width = 50.0  # Open 50mm channel down the center for the rolled playmat
divider_total_width = piece_box_width * 2.0 + playmat_channel_width  # 196.0mm
divider_length = 124.0
divider_height = 30.0

project = Project(
    "Canvas",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    generate_spacers=False,  # Keep the 50mm center channel open for the rolled playmat!
    box_defaults={"expandable": False},
)

# Circle lid pattern matching canvas.scad (SHAPE_TYPE_CIRCLE, width=7, thickness=1.5)
CANVAS_PATTERN = PatternBuilder(PatternType.CIRCLE, spacing=7.0, web=1.5)

# ── 1. Front Art-Card & Playmat Divider (Y = 0 .. 124mm) ──────────
# Holds left & right Tarot art-card stacks (70 x 120mm) on either side of the
# open 50mm center channel for the rolled-up cloth playmat.
divider = project.box(
    BoxType.NO_LID,
    "PlaymatDivider",
    size=(divider_total_width, divider_length, divider_height),
    position=(0.0, 0.0, 0.0),
    wall_thickness=2.0,
    floor_thickness=1.5,
)
divider.compartment(
    "ArtCards_Left",
    width_ratio=0.375,
    cut=FingerCut.SCOOP,
)
divider.compartment(
    "PlaymatChannel",
    width_ratio=0.25,
)
divider.compartment(
    "ArtCards_Right",
    width_ratio=0.375,
    cut=FingerCut.SCOOP,
)
# Open front & back U-cutouts along the center channel so the rolled playmat slides through cleanly
divider.finger_hole(ScoopSide.FRONT, width=44.0, offset=0.0)
divider.finger_hole(ScoopSide.BACK, width=44.0, offset=0.0)

# ── 2. Six Ribbon Token Boxes Flanking the Center Playmat Channel ─
# Left column (X = 0..73mm) and right column (X = 123..196mm), Y = 124..247mm
# leaving X = 73..123mm (50mm wide) completely open for the rolled-up playmat.
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

for col_x, group in ((0.0, left_ribbons), (piece_box_width + playmat_channel_width, right_ribbons)):
    for row_idx, (token_id, title, color_name) in enumerate(group):
        r_box = project.box(
            BoxType.CAP,
            f"RibbonBox_{token_id}",
            size=(piece_box_width, piece_box_length, piece_box_height),
            position=(col_x, divider_length + row_idx * piece_box_length, 0.0),
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
