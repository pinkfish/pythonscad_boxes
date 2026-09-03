#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""18Cuba board game organizer.

Ports examples/18cuba.scad to the pyboxbuilder Project API.
Organizes train cards, company stock share certificates, money slipovers,
hex track tiles, and tokens with automated spacers.
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
box_width = 225.0
box_length = 314.0
box_height = 68.0

total_board_thickness = 26.0
usable_height = box_height - total_board_thickness  # 42.0mm

wall_thickness = 2.0
floor_thickness = 2.0
lid_thickness = 2.0

# ── Card & Token Dimensions ───────────────────────────────────────
train_card_width = 40.0
train_card_length = 60.0
money_width = 46.0
money_length = 90.0

tray_height = usable_height / 2.0                   # 21.0mm
tray_width = box_width - 2.0                        # 223.0mm (spans across the 225mm box width)

money_box_len = money_length + wall_thickness * 4.0   # 98.0mm
train_box_len = train_card_length + wall_thickness * 4.0  # 68.0mm
shares_box_len = train_box_len                        # 68.0mm

project = Project(
    "18Cuba",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=total_board_thickness,
    generate_spacers=True,
)

CUBA_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Money Boxes (2 split boxes side-by-side across width) ───────
half_width = tray_width / 2.0  # 111.5mm

for i in range(2):
    m_box = project.box(
        BoxType.SLIPOVER,
        f"MoneyBox_{i + 1}",
        size=(half_width, money_box_len, tray_height),
        lid=LidBuilder(
            text="18Cuba Money",
            label_mode=LabelMode.FRAMED,
            pattern=CUBA_PATTERN,
            text_color=Color("white"),
            frame_color=Color("gold"),
        ),
        position=(i * half_width, 0.0, 0.0),
        no_rotate=True,
    )
    for slot in range(4):
        m_box.compartment(
            f"Denom_{slot + 1}",
            width_ratio=0.25,
            depth=tray_height - floor_thickness - 1.0,
            cut=FingerCut.SCOOP,
        )

# ── 2. Train & Wagon Cards Box ─────────────────────────────────────
t_box = project.box(
    BoxType.SLIPOVER,
    "TrainBox",
    size=(tray_width, train_box_len, tray_height),
    lid=LidBuilder(
        text="Trains",
        label_mode=LabelMode.FRAMED,
        pattern=CUBA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("blue"),
    ),
    position=(0.0, money_box_len, 0.0),
    no_rotate=True,
)
for slot in range(5):
    t_box.compartment(
        f"TrainSlot_{slot + 1}",
        width_ratio=0.2,
        depth=tray_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )

# ── 3. Corporate Shares Boxes (2 split boxes across width) ─────────
y_shares = money_box_len + train_box_len  # 166.0mm

for i in range(2):
    s_box = project.box(
        BoxType.SLIPOVER,
        f"SharesBox_{i + 1}",
        size=(half_width, shares_box_len, tray_height),
        lid=LidBuilder(
            text="Shares",
            label_mode=LabelMode.FRAMED,
            pattern=CUBA_PATTERN,
            text_color=Color("white"),
            frame_color=Color("royalblue"),
        ),
        position=(i * half_width, y_shares, 0.0),
        no_rotate=True,
    )
    for slot in range(4):
        s_box.compartment(
            f"ShareSlot_{slot + 1}",
            width_ratio=0.25,
            depth=tray_height - floor_thickness - 1.0,
            cut=FingerCut.SCOOP,
        )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
