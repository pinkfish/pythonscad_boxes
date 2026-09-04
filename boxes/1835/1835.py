#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""1835 board game organizer.

Ports examples/1835.scad to the pyboxbuilder Project API.
Organizes Prussian/Bavarian railroad company shares, money denominations,
hex track tiles, and the priority deal marker with automated spacers.
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
box_width = 216.0
box_length = 298.0
box_height = 50.0

board_thickness = 15.0
usable_height = box_height - board_thickness  # 35.0mm

wall_thickness = 2.0
floor_thickness = 2.0
lid_thickness = 2.0

tile_width = 40.0
hex_box_width = 135.0
hex_box_length = box_width - 1.0  # 215.0mm
hex_box_height = usable_height / 3.0  # ~11.66mm

money_box_width = 102.0
money_box_length = box_width - 1.0
money_box_height = usable_height / 3.0

shares_box_width = box_length - hex_box_width - 1.0  # 162.0mm
shares_box_length = 138.0
shares_box_height = usable_height / 2.0             # 17.5mm

marker_box_width = shares_box_width
marker_box_length = box_width - shares_box_length - 1.0  # 77.0mm
marker_box_height = usable_height / 2.0

project = Project(
    "EighteenThirtyFive",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

TRAIN_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Track Hex Tile Boxes (3 tiers stacked at X = 0, Y = 0) ─────
for tier in range(3):
    h_box = project.box(
        BoxType.SLIDING,
        f"HexBox_{tier + 1}",
        size=(hex_box_width, hex_box_length / 2.0, hex_box_height),
        lid=LidBuilder(
            text=f"Track Hexes {tier + 1}",
            label_mode=LabelMode.FRAMED,
            pattern=TRAIN_PATTERN,
            text_color=Color("white"),
            frame_color=Color("goldenrod" if tier == 0 else "forestgreen" if tier == 1 else "saddlebrown"),
        ),
        position=(0.0, 0.0, tier * hex_box_height),
        no_rotate=True,
    )
    for slot in range(3):
        h_box.compartment(
            f"Col_{slot + 1}",
            width_ratio=1.0 / 3.0,
            depth=hex_box_height - lid_thickness,
            cut=FingerCut.SCOOP,
        )

# ── 2. Bank Money Trays (3 tiers stacked at X = 0, Y = hex_box_length / 2)
y_money = hex_box_length / 2.0

money_denoms = ["1-5-10", "20-50-100", "200-500"]
for tier, denom in enumerate(money_denoms):
    m_box = project.box(
        BoxType.SLIDING,
        f"MoneyBox_{tier + 1}",
        size=(hex_box_width, hex_box_length / 2.0, hex_box_height),
        lid=LidBuilder(
            text=f"Bank {denom}",
            label_mode=LabelMode.FRAMED,
            pattern=TRAIN_PATTERN,
            text_color=Color("white"),
            frame_color=Color("darkgreen"),
        ),
        position=(0.0, y_money, tier * hex_box_height),
        no_rotate=True,
    )
    for slot in range(3):
        m_box.compartment(
            f"Slot_{slot + 1}",
            width_ratio=1.0 / 3.0,
            depth=hex_box_height - lid_thickness,
            cut=FingerCut.SCOOP,
        )

# ── 3. Railroad Company Shares (X = hex_box_width) ────────────────
x_shares = hex_box_width

for tier in range(2):
    s_box = project.box(
        BoxType.SLIDING,
        f"SharesBox_{tier + 1}",
        size=(box_width - x_shares, shares_box_length, shares_box_height),
        lid=LidBuilder(
            text=f"Company Shares {tier + 1}",
            label_mode=LabelMode.FRAMED,
            pattern=TRAIN_PATTERN,
            text_color=Color("white"),
            frame_color=Color("darkred"),
        ),
        position=(x_shares, 0.0, tier * shares_box_height),
        no_rotate=True,
    )
    s_box.compartment(
        "Shares_1",
        length_ratio=0.5,
        depth=shares_box_height - lid_thickness,
        cut=FingerCut.SCOOP,
    )
    s_box.compartment(
        "Shares_2",
        length_ratio=0.5,
        depth=shares_box_height - lid_thickness,
        cut=FingerCut.SCOOP,
    )

# ── 4. Priority Deal & Markers Box (Y = shares_box_length) ────────
p_box = project.box(
    BoxType.SLIDING,
    "MarkerBox",
    size=(box_width - x_shares, marker_box_length, marker_box_height),
    lid=LidBuilder(
        text="Markers",
        label_mode=LabelMode.FRAMED,
        pattern=TRAIN_PATTERN,
        text_color=Color("white"),
        frame_color=Color("navy"),
    ),
    position=(x_shares, shares_box_length, 0.0),
    no_rotate=True,
)
p_box.compartment("Markers", depth=marker_box_height - lid_thickness, cut=FingerCut.SCOOP)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
