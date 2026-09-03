#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Canvas board game organizer.

Ports examples/canvas.scad to the pyboxbuilder Project API.
Organizes ribbon award tokens (Red, Green, Grey, Blue, Purple, Palette)
and the transparent art card deck with automated spacers.
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
box_width = 200.0
box_length = 250.0
box_height = 50.0

board_thickness = 15.0  # Cloth canvas mat
usable_height = box_height - board_thickness  # 35.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

piece_box_width = 41.0
piece_box_length = 73.0
piece_box_height = 29.0

card_tray_width = 196.0
card_tray_length = 124.0
card_tray_height = 30.0

project = Project(
    "Canvas",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

CANVAS_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Ribbon Token Boxes (6 boxes across X at Y = 0) ─────────────
ribbons = [
    ("Red", "Red", "darkred"),
    ("Green", "Green", "forestgreen"),
    ("Grey", "Grey", "gray"),
    ("Blue", "Blue", "navy"),
    ("Purple", "Purple", "purple"),
    ("Palette", "Palette", "goldenrod"),
]

# 2 rows of 3 boxes across the 200mm box width (41mm * 3 = 123mm <= 200mm)
for idx, (token_id, title, color_name) in enumerate(ribbons):
    col = idx % 3
    row = idx // 3
    r_box = project.box(
        BoxType.CAP,
        f"RibbonBox_{token_id}",
        size=(piece_box_width, piece_box_length, piece_box_height),
        lid=LidBuilder(
            text=title,
            label_mode=LabelMode.FRAMED,
            pattern=CANVAS_PATTERN,
            text_color=Color("white"),
            frame_color=Color(color_name),
        ),
        position=(col * piece_box_width, row * piece_box_length, 0.0),
        no_rotate=True,
    )
    r_box.compartment(
        "Ribbons",
        depth=piece_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )

# ── 2. Card Tray Rack (Y = piece_box_length * 2 = 146mm) ──────────
c_tray = project.box(
    BoxType.CAP,
    "CardTray",
    size=(card_tray_width, card_tray_length / 2.0, card_tray_height),
    lid=LidBuilder(
        text="Art Cards",
        label_mode=LabelMode.FRAMED,
        pattern=CANVAS_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkslateblue"),
    ),
    position=(0.0, piece_box_length * 2.0, 0.0),
    no_rotate=True,
)
c_tray.compartment(
    "ArtCards_Left",
    width_ratio=0.5,
    depth=card_tray_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)
c_tray.compartment(
    "ArtCards_Right",
    width_ratio=0.5,
    depth=card_tray_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
