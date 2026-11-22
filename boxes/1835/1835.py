#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""1835 board game organizer.

Ports examples/1835.scad to the pyboxbuilder Project API.
Organizes Prussian/Bavarian railroad company shares, money denominations,
hex track tiles, and the priority deal marker with automated spacers.
"""

import math
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
box_width = 216.0
box_length = 298.0
box_height = 50.0

board_thickness = 15.0
usable_height = box_height - board_thickness  # 35.0mm

wall_thickness = 2.0
floor_thickness = 2.0
lid_thickness = 2.0

share_width = 46.0
share_length = 66.0
money_length = 98.0
money_one_thickness = 5.0
large_marker_diameter = 20.0
tile_width = 40.0
tile_radius = tile_width / 2.0 / math.cos(math.radians(30.0))

# Row 1: MoneyBox_1, MoneyBox_2, MiddleBox (stacked to 35.0mm)
money_box_width = box_width - 1.0                                      # 215.0mm
money_box_length = money_length + wall_thickness * 2.0                 # 102.0mm
money_box_height_1 = floor_thickness + lid_thickness + money_one_thickness + 0.5  # 9.5mm
money_box_height_2 = money_box_height_1 - 1.0                          # 8.5mm
middle_box_height = usable_height - money_box_height_1 - money_box_height_2       # 17.0mm

# Row 2: 4x HexBox (stacked to 35.0mm)
hex_box_width = box_width - 1.0                                        # 215.0mm
hex_box_length = tile_radius * 6.0 + wall_thickness * 2.0              # ~142.564mm
hex_box_height = usable_height / 4.0                                   # 8.75mm

# Row 3: 4x SharesBox (stacked to 35.0mm) + FirstPlayerBox (24.0mm) + auto Spacer (11.0mm)
shares_box_width = share_length * 2.0 + 3.0 * 2.0                      # 138.0mm
shares_box_length = box_length - hex_box_length - money_box_length - 1.0  # ~52.436mm
shares_box_height = usable_height / 4.0                                # 8.75mm

first_player_box_width = box_width - shares_box_width - 1.0            # 77.0mm
first_player_box_length = shares_box_length                            # ~52.436mm
first_player_box_height = large_marker_diameter + 4.0                  # 24.0mm

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

# ── 1. Bank Money Trays (2 stacked slipover-lid trays, 4 denoms each)
for idx, (m_h, denom_label) in enumerate(
    [(money_box_height_1, "1-5-10-20"), (money_box_height_2, "50-100-200-500")],
    start=1,
):
    m_box = project.box(
        BoxType.SLIPOVER,
        f"MoneyBox_{idx}",
        size=(money_box_width, money_box_length, m_h),
        lid=LidBuilder(
            text=f"Money {denom_label}",
            label_mode=LabelMode.FRAMED,
            pattern=TRAIN_PATTERN,
            text_color=Color("white"),
            frame_color=Color("darkgreen"),
        ),
    )
    for slot in range(4):
        m_box.compartment(
            f"Denom_{slot + 1}",
            width_ratio=0.25,
            cut=FingerCut.SCOOP,
        )

# ── 2. Middle Box (Tokens, Trains & Private Companies) ────────────
middle_box = project.box(
    BoxType.CAP,
    "MiddleBox",
    size=(money_box_width, money_box_length, middle_box_height),
    lid=LidBuilder(
        text="Tokens/Trains",
        label_mode=LabelMode.FRAMED,
        pattern=TRAIN_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkslateblue"),
    ),
)
middle_box.compartment("Tokens", width_ratio=0.45, cut=FingerCut.SCOOP)
middle_box.compartment("Trains", width_ratio=0.275, cut=FingerCut.SCOOP)
middle_box.compartment("Private", width_ratio=0.275, cut=FingerCut.SCOOP)

# ── 3. Track Hex Tile Boxes (4 tiers stacked, inset lid) ──────────
hex_colors = ["goldenrod", "forestgreen", "saddlebrown", "dimgray"]
for tier in range(4):
    h_box = project.box(
        BoxType.INSET,
        f"HexBox_{tier + 1}",
        size=(hex_box_width, hex_box_length, hex_box_height),
        lid=LidBuilder(
            text=f"Tiles {tier + 1}",
            label_mode=LabelMode.FRAMED,
            pattern=TRAIN_PATTERN,
            text_color=Color("white"),
            frame_color=Color(hex_colors[tier]),
        ),
    )
    for slot in range(5):
        h_box.compartment(
            f"HexCol_{slot + 1}",
            width_ratio=0.2,
            cut=FingerCut.SCOOP,
        )

# ── 4. Railroad Company Shares (4 tiers stacked, slipover lid) ────
for tier in range(4):
    s_box = project.box(
        BoxType.SLIPOVER,
        f"SharesBox_{tier + 1}",
        size=(shares_box_width, shares_box_length, shares_box_height),
        wall_thickness=1.5,
        lid=LidBuilder(
            text=f"Shares {tier + 1}",
            label_mode=LabelMode.FRAMED,
            pattern=TRAIN_PATTERN,
            text_color=Color("white"),
            frame_color=Color("darkred"),
        ),
    )
    s_box.compartment("Shares_1", width_ratio=0.5, cut=FingerCut.SCOOP)
    s_box.compartment("Shares_2", width_ratio=0.5, cut=FingerCut.SCOOP)

# ── 5. First Player Marker Box (slipover lid, 24mm; auto spacer on top)
p_box = project.box(
    BoxType.SLIPOVER,
    "FirstPlayerBox",
    size=(first_player_box_width, first_player_box_length, first_player_box_height),
    wall_thickness=3.0,
    lid=LidBuilder(
        text="First",
        label_mode=LabelMode.FRAMED,
        pattern=TRAIN_PATTERN,
        text_color=Color("white"),
        frame_color=Color("navy"),
    ),
)
p_box.compartment("FirstPlayerMarker", cut=FingerCut.SCOOP)

project.stack_order("HexBox_1", "HexBox_2", "HexBox_3", "HexBox_4")

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
