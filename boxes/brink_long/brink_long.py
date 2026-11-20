#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Brink: Long Box Variant organizer.

Ports examples/brink_long.scad to the pyboxbuilder Project API.
Organizes player fleets in elongated longitudinal trays (upgrade board,
3 cargo + nubs, 3 railguns + nubs, player tokens, Class I/II/III ships
with floor inlays, voting board, and 5 resource bays), action/rider/ambassador
sliding card boxes, and sector hexes with automated spacers.
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

# ── Box & Board Dimensions (from lib/brink.scad) ──────────────────
box_width = 215.0
box_length = 307.0
box_height = 96.0

board_thickness = 18.0
usable_height = box_height - board_thickness  # 78.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

cardboard_token_thickness = 2.0

voting_board_width = 40.0
voting_board_length = 196.0

upgrade_width = 86.0
upgrade_length = 102.0
upgrade_thickness = 3.5

player_token_diameter = 14.5

class_i_ship_diameter = 24.0
class_i_ship_thickness = 10.0

class_ii_ship_length = 38.0
class_ii_ship_width = 19.0
class_ii_ship_thickness = 8.0

class_iii_ship_edge_length = 43.0
class_iii_ship_thickness = 10.0
class_iii_ship_apothem = class_iii_ship_edge_length * math.sqrt(3.0) / 6.0
class_iii_ship_height = class_iii_ship_apothem * 3.0  # ~37.239mm

railgun_length = 19.0
railgun_width = 10.0
railgun_thickness = 8.0
railgun_nub_offset = 4.0

cargo_width = 13.5
cargo_thickness = 8.5

round_nub = 4.5
round_nub_thickness = 3.0

CLASS_III_SVG = str(ROOT / "boxes" / "brink" / "svg" / "class_iii_ship.svg")

long_player_box_width = 106.0
long_player_box_length = box_length - 2.0  # 305.0mm
long_player_box_height = 24.0

hex_box_width = box_width - 2.0            # 213.0mm
hex_box_length = 114.0
hex_box_height = 24.0

card_box_width = box_width / 2.0 - 1.0     # 106.5mm
card_box_length = 77.5
card_box_height = 24.0


def _centered(
    cx: float,
    cy: float,
    size: tuple[float, float],
    **kwargs: object,
) -> CompartmentElement:
    """Create a CompartmentElement centered at (cx, cy)."""
    w, l = size
    return CompartmentElement(
        offset=(cx - w / 2.0, cy - l / 2.0),
        size=size,
        **kwargs,  # type: ignore[arg-type]
    )


def _long_player_elements(
    inner_width: float,
    inner_length: float,
    inner_height: float,
) -> tuple[CompartmentElement, ...]:
    """Build all piece cutouts for the Brink Long player fleet tray."""
    elements: list[CompartmentElement] = []

    # ── Top region (Y = 196.5..299.0): Upgrade board + Cargo + Railguns + Tokens
    upgrade_depth = upgrade_thickness + 0.5
    elements.append(
        _centered(
            inner_width / 2.0,
            inner_length - (upgrade_length + 0.5) / 2.0,
            (upgrade_width + 0.5, upgrade_length + 0.5),
            shape=ElementShape.RECT,
            depth=upgrade_depth,
            z_offset=inner_height - upgrade_depth,
            pull_out=False,
            label="UpgradeBoard",
        )
    )

    under_depth = upgrade_thickness + 5.5
    elements.append(
        CompartmentElement(
            offset=(12.0, 201.0),
            size=(76.0, 92.0),
            shape=ElementShape.ROUNDED_RECT,
            corner_radius=5.0,
            bottom_rounding=2.0,
            depth=under_depth,
            z_offset=inner_height - under_depth,
            pull_out=False,
            label="UnderUpgrade",
        )
    )

    cargo_z = inner_height - upgrade_thickness - cargo_thickness - 2.0
    for i in range(3):
        cx = 24.0 + 20.0 * i
        cy = 216.0
        elements.append(
            _centered(
                cx,
                cy,
                (cargo_width, cargo_width),
                shape=ElementShape.RECT,
                depth=inner_height - cargo_z,
                z_offset=cargo_z,
                pull_out=True,
                label=f"Cargo_{i + 1}",
            )
        )
        elements.append(
            _centered(
                cx,
                cy,
                (round_nub, round_nub),
                shape=ElementShape.CIRCLE,
                bottom_rounding=1.0,
                depth=cargo_thickness + round_nub_thickness,
                z_offset=cargo_z - round_nub_thickness,
                pull_out=False,
                label=f"CargoNub_{i + 1}",
            )
        )

    railgun_z = inner_height - upgrade_thickness - railgun_thickness - 2.0
    for i in range(3):
        cx = 24.0 + 20.0 * i
        cy = 250.0
        elements.append(
            _centered(
                cx,
                cy,
                (railgun_width, railgun_length),
                shape=ElementShape.RECT,
                depth=inner_height - railgun_z,
                z_offset=railgun_z,
                pull_out=True,
                label=f"Railgun_{i + 1}",
            )
        )
        elements.append(
            _centered(
                cx,
                cy + railgun_length / 2.0 - railgun_nub_offset,
                (round_nub, round_nub),
                shape=ElementShape.CIRCLE,
                bottom_rounding=1.0,
                depth=railgun_thickness + round_nub_thickness,
                z_offset=railgun_z - round_nub_thickness,
                pull_out=False,
                label=f"RailgunNub_{i + 1}",
            )
        )

    pt_z = inner_height - upgrade_thickness - cardboard_token_thickness * 2.0 - 2.0
    elements.append(
        _centered(
            82.0,
            234.0,
            (player_token_diameter, player_token_diameter),
            shape=ElementShape.CIRCLE,
            depth=inner_height - pt_z,
            z_offset=pt_z,
            pull_out=True,
            label="PlayerTokens",
        )
    )

    # ── Bottom-left region (X = 3..43.5, Y = 0..196): Voting board + 5 bays
    voting_depth = cardboard_token_thickness + 1.0
    elements.append(
        CompartmentElement(
            offset=(3.0, 0.0),
            size=(voting_board_width + 0.5, voting_board_length),
            shape=ElementShape.RECT,
            depth=voting_depth,
            z_offset=inner_height - voting_depth,
            pull_out=False,
            label="VotingBoard",
        )
    )
    bay_h = 34.5
    bay_step = 37.5
    for i in range(5):
        elements.append(
            CompartmentElement(
                offset=(3.0, 4.0 + bay_step * i),
                size=(42.0, bay_h),
                shape=ElementShape.ROUNDED_RECT,
                corner_radius=5.0,
                bottom_rounding=4.0,
                depth=inner_height,
                z_offset=0.0,
                pull_out=False,
                label=f"VotingBay_{i + 1}",
            )
        )

    # ── Bottom-right region (X = 50..96, Y = 4..190): Class III, II, I ships + tray
    c3_z = inner_height - upgrade_thickness - 1.0 - class_iii_ship_thickness
    elements.append(
        _centered(
            73.0,
            168.0,
            (class_iii_ship_edge_length, class_iii_ship_height),
            shape=ElementShape.SVG,
            shape_file=CLASS_III_SVG,
            depth=inner_height - c3_z,
            z_offset=c3_z,
            pull_out=True,
            label="ClassIIIShip",
        )
    )
    elements.append(
        _centered(
            73.0,
            172.0,
            (10.0, 12.0),
            shape=ElementShape.TEXT,
            shape_file="3",
            rotation=90.0,
            depth=0.4,
            z_offset=c3_z,
            color="white",
            pull_out=False,
            label="ClassIIILabel",
        )
    )

    c2_z = inner_height - upgrade_thickness - 1.0 - class_ii_ship_thickness
    elements.append(
        _centered(
            73.0,
            116.0,
            (class_ii_ship_width, class_ii_ship_length),
            shape=ElementShape.ROUNDED_RECT,
            corner_radius=2.0,
            depth=inner_height - c2_z,
            z_offset=c2_z,
            pull_out=True,
            label="ClassIIShip",
        )
    )
    elements.append(
        _centered(
            73.0,
            116.0,
            (10.0, 12.0),
            shape=ElementShape.TEXT,
            shape_file="2",
            rotation=90.0,
            depth=0.4,
            z_offset=c2_z,
            color="white",
            pull_out=False,
            label="ClassIILabel",
        )
    )

    c1_z = inner_height - upgrade_thickness - 1.0 - class_i_ship_thickness
    elements.append(
        _centered(
            73.0,
            66.0,
            (class_i_ship_diameter, class_i_ship_diameter),
            shape=ElementShape.CIRCLE,
            depth=inner_height - c1_z,
            z_offset=c1_z,
            pull_out=True,
            label="ClassIShip",
        )
    )
    elements.append(
        _centered(
            73.0,
            66.0,
            (10.0, 12.0),
            shape=ElementShape.TEXT,
            shape_file="1",
            rotation=90.0,
            depth=0.4,
            z_offset=c1_z,
            color="white",
            pull_out=False,
            label="ClassILabel",
        )
    )

    elements.append(
        CompartmentElement(
            offset=(52.0, 4.0),
            size=(42.0, 38.0),
            shape=ElementShape.ROUNDED_RECT,
            corner_radius=5.0,
            bottom_rounding=4.0,
            depth=inner_height,
            z_offset=0.0,
            pull_out=False,
            label="FleetTokens",
        )
    )

    return tuple(elements)


project = Project(
    "BrinkLong",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

BRINK_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Longitudinal Player Trays ──────────────────────────────────
long_inner_w = long_player_box_width - 2.0 * wall_thickness
long_inner_l = long_player_box_length - 2.0 * wall_thickness
long_inner_h = long_player_box_height - floor_thickness - lid_thickness
LONG_PLAYER_ELEMENTS = _long_player_elements(long_inner_w, long_inner_l, long_inner_h)

player_fleets = [("FleetSolari", "Solari Fleet", "royalblue"), ("FleetHorizon", "Horizon Fleet", "gold")]
for label, title, color_name in player_fleets:
    p_box = project.box(
        BoxType.CAP,
        label,
        size=(long_player_box_width, long_player_box_length, long_player_box_height),
        lid=LidBuilder(
            text=title,
            label_mode=LabelMode.FRAMED,
            pattern=BRINK_PATTERN,
            text_color=Color("black" if color_name == "gold" else "white"),
            frame_color=Color(color_name),
        ),
    )
    p_box.compartment(
        "FleetContents",
        size=(long_inner_w, long_inner_l),
        elements=LONG_PLAYER_ELEMENTS,
        element_margin=0.0,
    )

# ── 2. Card Boxes ─────────────────────────────────────────────────
card_decks = [
    ("Actions", "Actions", "gold"),
    ("Riders", "Riders", "firebrick"),
    ("Ambassadors", "Ambassadors", "navy"),
]

for deck_id, title, color_name in card_decks:
    c_box = project.box(
        BoxType.SLIDING,
        f"CardBox_{deck_id}",
        size=(card_box_width, card_box_length, card_box_height),
        lid_slide_axis="x",
        lid=LidBuilder(
            text=title,
            label_mode=LabelMode.FRAMED,
            pattern=BRINK_PATTERN,
            text_color=Color("white"),
            frame_color=Color(color_name),
        ),
        expandable=False,
    )
    c_box.compartment("Cards", cut=FingerCut.SCOOP)

# ── 3. Sector Hex Box ─────────────────────────────────────────────
y_hex = card_box_length * 3.0  # 232.5mm

h_box = project.box(
    BoxType.CAP,
    "HexBox",
    size=(card_box_width, box_length - y_hex - 2.0, hex_box_height),
    lid=LidBuilder(
        text="Hex Sectors",
        label_mode=LabelMode.FRAMED,
        pattern=BRINK_PATTERN,
        text_color=Color("white"),
        frame_color=Color("dimgray"),
    ),
)
h_box.compartment("Hexes", cut=FingerCut.SCOOP)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
