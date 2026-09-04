#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Irish Gauge board game organizer.

Ports examples/irish_gauge.scad to the pyboxbuilder Project API.
Organizes 5 railway companies (Belfast, Cork, Midland, Waterford, Great Southern)
with trains & share cards, banknotes, and dividend cubes with automated spacers.
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
box_width = 214.0
box_length = 302.0
box_height = 39.0

board_thickness = 10.5
usable_height = box_height - board_thickness  # 28.5mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

card_width = 49.0
card_length = 71.0

company_box_width = box_width / 4.0  # 53.5mm
company_box_length = card_length * 1.8 + wall_thickness * 2.0  # 133.8mm
company_box_height = usable_height / 2.0                       # 14.25mm

money_box_width = box_width                                    # 214.0mm
money_box_length = card_length + wall_thickness * 2.0          # 77.0mm
money_box_height = usable_height                               # 28.5mm

project = Project(
    "IrishGauge",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

IRISH_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Railway Company Boxes (4 columns across X, 2 tiers) ────────
companies = [
    ("Belfast", "Belfast", "darkorange"),
    ("Cork", "Cork", "gold"),
    ("Midland", "Midland", "darkred"),
    ("Waterford", "Waterford", "purple"),
    ("GreatSouthern", "Great Southern", "navy"),
]

for idx, (company_id, title, color_name) in enumerate(companies):
    col = idx % 4
    tier = idx // 4
    c_box = project.box(
        BoxType.SLIDING,
        f"CompanyBox_{company_id}",
        size=(company_box_width, company_box_length, company_box_height),
        lid=LidBuilder(
            text=title,
            label_mode=LabelMode.FRAMED,
            pattern=IRISH_PATTERN,
            text_color=Color("black" if color_name == "gold" else "white"),
            frame_color=Color(color_name),
        ),
        position=(col * company_box_width, 0.0, tier * company_box_height),
        no_rotate=True,
    )
    c_box.compartment("SharesAndLocos", depth=company_box_height - lid_thickness, cut=FingerCut.SCOOP)

# ── 2. Bank Money & Dividend Cubes Box (Y = company_box_length) ───
y_money = company_box_length

m_box = project.box(
    BoxType.SLIDING,
    "MoneyAndDividendsBox",
    size=(money_box_width, money_box_length, money_box_height),
    lid=LidBuilder(
        text="Bank & Dividends",
        label_mode=LabelMode.FRAMED,
        pattern=IRISH_PATTERN,
        text_color=Color("white"),
        frame_color=Color("forestgreen"),
    ),
    position=(0.0, y_money, 0.0),
    no_rotate=True,
)
for name in ["Money_1", "Money_5", "Money_10", "DividendCubes"]:
    m_box.compartment(
        name,
        width_ratio=0.25,
        depth=money_box_height - lid_thickness,
        cut=FingerCut.SCOOP,
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
