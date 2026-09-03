#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pioneer Rails board game organizer.

Ports examples/pioneer_rails.scad to the pyboxbuilder Project API.
Organizes card decks (Goals, Playing, Forest, Company Owner), pencils,
erasers, and the poker chip dealer token with automated spacers.
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
box_width = 209.0
box_length = 209.0
box_height = 38.0

board_thickness = 16.0  # Player pad of score sheets
usable_height = box_height - board_thickness  # 22.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

card_width = 66.5
card_length = 90.0

card_box_width = usable_height                        # 22.0mm (cards stored on edge)
card_box_length = card_length + wall_thickness * 2.0  # 96.0mm
card_box_height = usable_height                       # 22.0mm

pencil_box_length = 115.0
pencil_box_width = 60.0
pencil_box_height = usable_height

project = Project(
    "PioneerRails",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

PIONEER_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Pencil & Accessory Box ─────────────────────────────────────
p_box = project.box(
    BoxType.CAP,
    "PencilBox",
    size=(pencil_box_width, pencil_box_length, pencil_box_height),
    lid=LidBuilder(
        text="Pencils",
        label_mode=LabelMode.FRAMED,
        pattern=PIONEER_PATTERN,
        text_color=Color("white"),
        frame_color=Color("peru"),
    ),
    position=(0.0, 0.0, 0.0),
    no_rotate=True,
)
p_box.compartment(
    "PencilsAndErasers",
    depth=pencil_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── 2. Card Decks (4 boxes side-by-side) ──────────────────────────
decks = [
    ("GoalCards", "Goal", "darkorange"),
    ("PlayingCards", "Playing", "navy"),
    ("ForestCards", "Forest", "forestgreen"),
    ("CompanyCards", "Company", "gold"),
]

for idx, (deck_id, title, color_name) in enumerate(decks):
    c_box = project.box(
        BoxType.SLIDING,
        f"CardBox_{deck_id}",
        size=(card_box_width, card_box_length, card_box_height),
        lid=LidBuilder(
            text=title,
            label_mode=LabelMode.FRAMELESS,
            pattern=PIONEER_PATTERN,
            text_color=Color("white"),
            frame_color=Color(color_name),
        ),
        position=(pencil_box_width + idx * card_box_width, 0.0, 0.0),
        no_rotate=True,
    )
    c_box.compartment(
        "Cards",
        depth=card_box_height - lid_thickness,
        cut=FingerCut.SCOOP,
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
