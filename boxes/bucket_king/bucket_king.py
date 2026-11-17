#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bucket King 3D board game organizer.

Ports examples/bucket_king.scad to the pyboxbuilder Project API.
Organizes card decks and 6 player sets of cardboard bucket tokens
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
    FingerCut,
    LabelMode,
    LidBuilder,
    PatternBuilder,
    PatternType,
    Project,
    run,
)

# ── Box Dimensions ────────────────────────────────────────────────
box_width = 140.0
box_length = 288.0
box_height = 70.0

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

card_width = 68.0
card_length = 92.0

card_box_width = box_width - 2.0                                # 138.0mm
card_box_length = card_width + wall_thickness * 2.0 + 1.0       # 75.0mm
card_box_height = box_height - 2.0                              # 68.0mm

player_box_width = (box_width - 2.0) / 2.0                      # 69.0mm
player_box_length = (box_length - 2.0 - card_box_length) / 3.0  # 70.33mm
player_box_height = (box_height - 1.0) / 2.0                    # 34.5mm

project = Project(
    "BucketKing",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    generate_spacers=True,
)

BUCKET_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Playing Card Box ───────────────────────────────────────────
c_box = project.box(
    BoxType.CAP,
    "CardBox",
    size=(card_box_width, card_box_length, card_box_height),
    lid=LidBuilder(
        text="Bucket King Cards",
        label_mode=LabelMode.FRAMED,
        pattern=BUCKET_PATTERN,
        text_color=Color("white"),
        frame_color=Color("royalblue"),
    ),
    expandable=False,
)
c_box.compartment(
    "Deck_Left",
    width_ratio=0.5,
    cut=FingerCut.SCOOP,
)
c_box.compartment(
    "Deck_Right",
    width_ratio=0.5,
    cut=FingerCut.SCOOP,
)

# ── 2. Player Bucket Boxes (6 players) ────────────────────────────
player_names = ["Player_1", "Player_2", "Player_3", "Player_4", "Player_5", "Player_6"]
for idx, _name in enumerate(player_names):
    p_box = project.box(
        BoxType.CAP,
        f"PlayerBox_{idx + 1}",
        size=(player_box_width, player_box_length, player_box_height),
        lid=LidBuilder(
            text=f"Buckets {idx + 1}",
            label_mode=LabelMode.FRAMED,
            pattern=BUCKET_PATTERN,
            text_color=Color("white"),
            frame_color=Color("darkorange"),
        ),
    )
    p_box.compartment(
        "Buckets",
        cut=FingerCut.SCOOP,
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
