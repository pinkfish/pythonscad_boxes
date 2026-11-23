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

from pyboxbuilder import (
    BoxType,
    Color,
    CompartmentElement,
    ElementShape,
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
    box_defaults={"expandable": False},
)

IRISH_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Railway Company Boxes ──────────────────────────────────────
company_inner_width = company_box_width - wall_thickness * 2.0  # 47.5mm
company_inner_length = company_box_length - wall_thickness * 2.0  # 127.8mm
company_inner_height = company_box_height - floor_thickness - lid_thickness  # 10.25mm

single_card_thickness = 14.0 / 20.0  # 0.7mm
dividend_marker_diameter = 7.5
dividend_marker_thickness = 3.0
train_width = 7.75
train_length = 5.5
train_height = 8.0


def _company_box_elements(shares: int) -> tuple[CompartmentElement, ...]:
    """Build share card well (stepped by share count), dividend marker well, and train tray."""
    elems: list[CompartmentElement] = []

    # 1. Share cards well (clamped to inner_width=47.5mm, depth stepped by share count)
    card_well_w = min(card_width, company_inner_width)
    share_depth = single_card_thickness * shares + 1.0  # 2.4mm / 3.1mm / 3.8mm
    elems.append(
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(card_well_w, card_length),
            offset=(0.0, 0.0),
            depth=share_depth,
            pull_out=False,
            label="ShareCards",
        )
    )
    # Front finger access notch for lifting share cards
    card_notch_d = 20.0
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(card_notch_d, card_notch_d),
            offset=(card_well_w / 2.0 - card_notch_d / 2.0, 0.0),
            depth=min(share_depth + 4.0, company_inner_height),
            bottom_rounding=2.0,
            pull_out=False,
            label="ShareCardsFingerNotch",
        )
    )

    # 2. Dividend marker circular well (d=7.5mm, depth=4.0mm) + 0/180-deg finger bites
    div_cx = company_inner_width / 2.0
    div_cy = card_length + dividend_marker_diameter - 1.5  # 77.0mm
    div_depth = dividend_marker_thickness + 1.0  # 4.0mm
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(dividend_marker_diameter, dividend_marker_diameter),
            offset=(
                div_cx - dividend_marker_diameter / 2.0,
                div_cy - dividend_marker_diameter / 2.0,
            ),
            depth=div_depth,
            pull_out=False,
            label="DividendMarker",
        )
    )
    div_bite_d = 8.0  # finger_hole_radius=4.0 in irish_gauge.scad
    for idx, sign in enumerate((-1.0, 1.0), start=1):
        bite_cx = div_cx + sign * (dividend_marker_diameter / 2.0)
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(div_bite_d, div_bite_d),
                offset=(bite_cx - div_bite_d / 2.0, div_cy - div_bite_d / 2.0),
                depth=div_depth,
                pull_out=False,
                label=f"DividendMarkerBite_{idx}",
            )
        )

    # 3. Train cubes pocket (33x31mm, depth=8.5mm) + stepped upper rounded finger dish (43x42mm, depth=4.5mm)
    train_pocket_w = train_length * 6.0  # 33.0mm
    train_pocket_l = train_width * 4.0  # 31.0mm
    train_right_x = company_inner_width - 8.0  # 39.5mm
    train_cy = company_inner_length - train_width * 3.0  # 104.55mm
    elems.append(
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(train_pocket_w, train_pocket_l),
            offset=(train_right_x - train_pocket_w, train_cy - train_pocket_l / 2.0),
            depth=train_height + 0.5,  # 8.5mm
            pull_out=False,
            label="TrainCubes",
        )
    )
    dish_w = train_pocket_w + 10.0  # 43.0mm
    dish_l = train_length * 4.0 + 20.0  # 42.0mm
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(dish_w, dish_l),
            offset=(train_right_x - train_pocket_w - 5.0, train_cy - dish_l / 2.0),
            depth=train_height / 2.0 + 0.5,  # 4.5mm
            corner_radius=5.0,
            bottom_rounding=2.0,
            pull_out=False,
            label="TrainFingerDish",
        )
    )

    return tuple(elems)


companies = [
    ("Belfast", "Belfast", "darkorange", 2),
    ("Cork", "Cork", "gold", 3),
    ("Midland", "Midland", "darkred", 3),
    ("Waterford", "Waterford", "purple", 4),
    ("GreatSouthern", "Great Southern", "navy", 4),
]

for company_id, title, color_name, shares in companies:
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
    )
    c_box.compartment(
        "SharesAndLocos",
        size=(company_inner_width, company_inner_length),
        position=(0.0, 0.0),
        elements=_company_box_elements(shares),
    )

project.stack_order("CompanyBox_Belfast", "CompanyBox_GreatSouthern")

# ── 2. Bank Money & Dividend Cubes Box ────────────────────────────
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
)
for name in ["Money_1", "Money_5", "Money_10", "DividendCubes"]:
    m_box.compartment(
        name,
        width_ratio=0.25,
        cut=FingerCut.SCOOP,
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
