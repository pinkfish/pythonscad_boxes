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
cube_size = 8.25
cube_inner_width = cube_box_width - wall_thickness * 2.0  # 48.25mm
cube_inner_length = cube_box_length - wall_thickness * 2.0  # 97.0mm

# Per-color cube grid dimensions matching cube_info in gulf_mobile_and_ohio.scad
cube_specs: list[tuple[str, int, int, int]] = [
    ("red", 4, 5, 0),
    ("yellow", 3, 8, 2),
    ("green", 4, 8, 0),
    ("blue", 2, 8, 0),
    ("black", 2, 6, 0),
    ("purple", 1, 6, 0),
]


def _cube_box_elements(num_x: int, num_y: int, remainder: int) -> tuple[CompartmentElement, ...]:
    """Build exact per-color cube grid well + stepped upper rounded finger dish."""
    cx = cube_inner_width / 2.0
    cy = cube_inner_length / 2.0
    grid_w = cube_size * num_x
    grid_l = cube_size * num_y
    cube_depth = cube_size + 0.5  # 8.75mm

    elems: list[CompartmentElement] = [
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(grid_w, grid_l),
            offset=(cx - grid_w / 2.0, cy - grid_l / 2.0),
            depth=cube_depth,
            pull_out=False,
            label="CubeGrid",
        )
    ]
    if remainder > 0:
        rem_l = cube_size * remainder
        rem_cx = cx + grid_w / 2.0 + cube_size / 2.0
        elems.append(
            CompartmentElement(
                shape=ElementShape.RECT,
                size=(cube_size, rem_l),
                offset=(rem_cx - cube_size / 2.0, cy - rem_l / 2.0),
                depth=cube_depth,
                pull_out=False,
                label="CubeRemainder",
            )
        )
    # Stepped upper rounded finger dish around the cube well
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(cube_inner_width - 4.0, cube_inner_length - 4.0),
            offset=(2.0, 2.0),
            depth=cube_size / 2.0,
            corner_radius=5.0,
            bottom_rounding=2.0,
            pull_out=False,
            label="UpperFingerDish",
        )
    )
    return tuple(elems)


for color_name, num_x, num_y, remainder in cube_specs:
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
        size=(cube_inner_width, cube_inner_length),
        position=(0.0, 0.0),
        elements=_cube_box_elements(num_x, num_y, remainder),
    )

# ── 4. Player Tokens Box ──────────────────────────────────────────
marker_diameter = 16.5
marker_thickness = 14.5
common_share_diameter = 20.5
common_share_thickness = 31.0


def _player_token_elements() -> tuple[CompartmentElement, ...]:
    """Build 5 circular marker wells + common share cradle + stepped upper finger dish."""
    elems: list[CompartmentElement] = []

    # 5 circular marker wells along the left side (d=16.5mm, depth=14.5mm)
    for i in range(5):
        mcx = 5.0 + marker_diameter / 2.0
        mcy = 6.0 + marker_diameter / 2.0 + (marker_diameter + 1.0) * i
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(marker_diameter, marker_diameter),
                offset=(mcx - marker_diameter / 2.0, mcy - marker_diameter / 2.0),
                depth=marker_thickness,
                pull_out=False,
                label=f"MarkerWell_{i + 1}",
            )
        )

    # Common share standing-disc cradle on the right side (20.5x31mm, depth=21.0mm)
    share_cx = cube_inner_width - common_share_diameter * 0.75
    share_cy = cube_inner_length / 2.0
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(common_share_diameter, common_share_thickness),
            offset=(
                share_cx - common_share_diameter / 2.0,
                share_cy - common_share_thickness / 2.0,
            ),
            depth=common_share_diameter + 0.5,
            corner_radius=1.0,
            bottom_rounding=8.0,
            pull_out=False,
            label="CommonSharesCradle",
        )
    )

    # Stepped upper rounded finger dish (depth=7.25mm)
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(cube_inner_width - 2.0, cube_inner_length - 2.0),
            offset=(1.0, 1.0),
            depth=marker_thickness / 2.0,
            corner_radius=5.0,
            bottom_rounding=2.5,
            pull_out=False,
            label="UpperFingerDish",
        )
    )
    return tuple(elems)


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
    size=(cube_inner_width, cube_inner_length),
    position=(0.0, 0.0),
    elements=_player_token_elements(),
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
