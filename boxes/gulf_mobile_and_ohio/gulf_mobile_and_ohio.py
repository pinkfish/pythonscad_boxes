#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Gulf, Mobile & Ohio board game organizer.

Ports examples/gulf_mobile_and_ohio.scad to the pyboxbuilder Project API.
Organizes paper money, company railroad cards, track resource cubes,
and player share discs with automated spacers.
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
box_width = 217.0
box_length = 307.0
box_height = 39.0

board_thickness = 9.5
usable_height = box_height - board_thickness  # 29.5mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

money_width = 53.0
money_length = 101.0
card_width = 66.0
card_length = 91.0

money_box_width = (money_width + 2.0) * 3.0 + wall_thickness * 2.0  # 171.0mm
money_box_length = money_length + wall_thickness * 2.0             # 107.0mm
money_box_height = usable_height                                   # 29.5mm

company_box_width = card_width + wall_thickness * 2.0              # 72.0mm
company_box_length = card_length + wall_thickness * 2.0            # 97.0mm
company_box_height = usable_height                                 # 29.5mm

cube_box_length = box_length - company_box_length - money_box_length  # 103.0mm
cube_box_width = box_width / 4.0                                   # 54.25mm
cube_box_height = usable_height / 2.0                              # 14.75mm

project = Project(
    "GulfMobileAndOhio",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
    box_defaults={"expandable": False},
)

GMO_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Bank Money Box ─────────────────────────────────────────────
money_box = project.box(
    BoxType.SLIDING,
    "BankMoneyBox",
    size=(money_box_width, money_box_length, money_box_height),
    lid=LidBuilder(
        text="Bank",
        label_mode=LabelMode.FRAMED,
        pattern=GMO_PATTERN,
        text_color=Color("white"),
        frame_color=Color("gold"),
    ),
)
for slot in range(3):
    money_box.compartment(
        f"Denom_{slot + 1}",
        width_ratio=1.0 / 3.0,
        cut=FingerCut.SCOOP,
    )

# ── 2. Company Railroad Card Boxes ────────────────────────────────
for i in range(2):
    c_box = project.box(
        BoxType.SLIDING,
        f"CompanyCardsBox_{i + 1}",
        size=(company_box_width, company_box_length, company_box_height),
        lid=LidBuilder(
            text=f"Companies {i + 1}",
            label_mode=LabelMode.FRAMED,
            pattern=GMO_PATTERN,
            text_color=Color("white"),
            frame_color=Color("navy"),
        ),
    )
    c_box.compartment(
        "Cards",
        cut=FingerCut.SCOOP,
    )

# ── 3. Resource Cube Boxes ────────────────────────────────────────
cube_colors = ["red", "yellow", "green", "blue", "black", "purple"]

for color_name in cube_colors:
    bx = project.box(
        BoxType.CAP,
        f"CubeBox_{color_name.title()}",
        size=(cube_box_width, cube_box_length, cube_box_height),
        lid=LidBuilder(
            text=color_name.title(),
            label_mode=LabelMode.FRAMED,
            pattern=GMO_PATTERN,
            text_color=Color("black" if color_name == "yellow" else "white"),
            frame_color=Color(color_name),
        ),
    )
    bx.compartment(
        "Cubes",
        cut=FingerCut.SCOOP,
    )

# ── 4. Player Tokens Box ──────────────────────────────────────────
tok_box = project.box(
    BoxType.CAP,
    "PlayerTokenBox",
    size=(cube_box_width, cube_box_length, usable_height),
    lid=LidBuilder(
        text="Tokens",
        label_mode=LabelMode.FRAMED,
        pattern=GMO_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkslategray"),
    ),
)
tok_box.compartment(
    "Tokens",
    cut=FingerCut.SCOOP,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
