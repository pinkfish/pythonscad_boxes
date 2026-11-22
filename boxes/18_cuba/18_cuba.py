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
box_width = 225.0
box_length = 314.0
box_height = 68.0

box_hexes = 20.0
total_board_thickness = 26.0
board_thickness = total_board_thickness + box_hexes  # 46.0mm
usable_height = box_height - board_thickness         # 22.0mm (rest_height in .scad)

wall_thickness = 1.5
floor_thickness = 1.0
lid_thickness = 1.0

# ── Card & Token Dimensions ───────────────────────────────────────
train_card_width = 40.0
train_card_length = 60.0
money_width = 46.0
money_length = 90.0

tray_height = usable_height / 2.0                          # 11.0mm
tray_width = box_width - 1.0                               # 224.0mm (spans across the 225mm box width)

money_box_len = money_length + wall_thickness * 4.0        # 96.0mm
train_box_len = train_card_length + wall_thickness * 4.0   # 66.0mm
rest_section_len = box_length - train_box_len * 2.0 - money_box_len - 1.0  # 85.0mm

project = Project(
    "18Cuba",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
    box_defaults={"expandable": False},
)

CUBA_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Money Boxes (2 full-width stacked boxes, 4 denoms each) ────
for i in range(2):
    m_box = project.box(
        BoxType.SLIPOVER,
        f"MoneyBox_{i + 1}",
        size=(tray_width, money_box_len, tray_height),
        lid=LidBuilder(
            text="18Cuba",
            label_mode=LabelMode.FRAMED,
            pattern=CUBA_PATTERN,
            text_color=Color("white"),
            frame_color=Color("gold"),
        ),
    )
    for slot in range(4):
        m_box.compartment(
            f"Denom_{slot + 1}",
            width_ratio=0.25,
            cut=FingerCut.SCOOP,
        )

# ── 2. Train & Wagon Cards Box (5 pockets: 3 trains + 2 wagons) ───
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
)
for slot in range(5):
    t_box.compartment(
        f"TrainSlot_{slot + 1}",
        width_ratio=0.2,
        cut=FingerCut.SCOOP,
    )

# ── 3. Corporate Shares Boxes (2 full-width boxes, 5 companies each)
for i in range(2):
    s_box = project.box(
        BoxType.SLIPOVER,
        f"SharesBox_{i + 1}",
        size=(tray_width, train_box_len, tray_height),
        lid=LidBuilder(
            text="Shares",
            label_mode=LabelMode.FRAMED,
            pattern=CUBA_PATTERN,
            text_color=Color("white"),
            frame_color=Color("royalblue"),
        ),
    )
    for slot in range(5):
        s_box.compartment(
            f"ShareSlot_{slot + 1}",
            width_ratio=0.2,
            cut=FingerCut.SCOOP,
        )

# ── 4. Machine / Minor Companies & Concession Box (LastBox) ───────
last_box = project.box(
    BoxType.SLIPOVER,
    "LastBox",
    size=(tray_width, train_box_len, tray_height),
    lid=LidBuilder(
        text="Machine/Minor",
        label_mode=LabelMode.FRAMED,
        pattern=CUBA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("teal"),
    ),
)
last_box.compartment("Concession", width_ratio=0.2, cut=FingerCut.SCOOP)
last_box.compartment("MinorTokens", width_ratio=0.65, cut=FingerCut.SCOOP)
last_box.compartment("Rails", width_ratio=0.15, cut=FingerCut.SCOOP)

# ── 5. Large Tokens Box & Inside Token Tray (2-tier token section) ─
large_tokens = project.box(
    BoxType.SLIPOVER,
    "LargeTokensBox",
    size=(tray_width, rest_section_len, tray_height),
    lid=LidBuilder(
        text="Major Tokens",
        label_mode=LabelMode.FRAMED,
        pattern=CUBA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkblue"),
    ),
)
for slot in range(4):
    large_tokens.compartment(
        f"MajorTokenRow_{slot + 1}",
        width_ratio=0.25,
        cut=FingerCut.SCOOP,
    )

inside_tray = project.box(
    BoxType.NO_LID,
    "InsideTokenTray",
    size=(tray_width, rest_section_len, tray_height),
)
inside_tray.compartment("CentralTokens", width_ratio=0.5, cut=FingerCut.SCOOP)
inside_tray.compartment("YellowTokens", width_ratio=0.5, cut=FingerCut.SCOOP)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
