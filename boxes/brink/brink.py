#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Brink board game organizer.

Ports examples/brink.scad to the pyboxbuilder Project API.
Organizes action cards, rider cards, ambassador cards, faction cards, hex
sector tiles, and player fleet trays (upgrade board, Class I/II/III ships
with floor inlays, 3 cargo + nubs, 3 railguns + nubs, and player tokens)
with automated spacers.
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
    StackableMode,
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

card_width = 66.5
card_length = 91.5

small_card_width = 49.0
small_card_length = 71.5

hex_width = 72.0

cardboard_token_thickness = 2.0

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
class_iii_ship_radius = class_iii_ship_edge_length / math.sqrt(3.0)
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

CLASS_III_SVG = str(Path(__file__).resolve().parent / "svg" / "class_iii_ship.svg")

ambassador_box_width = box_width / 2.0 - 1.0                      # 106.5mm
ambassador_box_length = small_card_length + wall_thickness * 2.0  # 77.5mm

player_box_width = (box_width - 3.0) / 2.0                        # 106.0mm
player_box_length = wall_thickness * 2.0 + upgrade_length + 2.0   # 110.0mm
player_box_height = usable_height / 3.0                           # 26.0mm

hex_box_width = box_width - 2.0                                   # 213.0mm
hex_box_length = hex_width * 1.5 + wall_thickness * 2.0 + 6.0     # 120.0mm
hex_box_height = usable_height / 3.0                              # 26.0mm


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


def _player_box_elements(
    inner_width: float,
    inner_length: float,
    inner_height: float,
) -> tuple[CompartmentElement, ...]:
    """Build all piece cutouts for the Brink PlayerBox (matching brink.scad)."""
    elements: list[CompartmentElement] = []
    x_shift = 7.5

    # 1. Top recess for the player upgrade board (86.5 x 102.5mm)
    upgrade_depth = upgrade_thickness + 1.0
    elements.append(
        _centered(
            inner_width / 2.0,
            inner_length / 2.0,
            (upgrade_width + 0.5, upgrade_length + 0.5),
            shape=ElementShape.RECT,
            depth=upgrade_depth,
            z_offset=inner_height - upgrade_depth,
            pull_out=False,
            label="UpgradeBoard",
        )
    )

    # 2. Under-upgrade shallow finger/clearance recesses
    under_depth = upgrade_thickness + 6.5
    under_z = inner_height - under_depth
    elements.append(
        CompartmentElement(
            offset=(x_shift + 5.0, 5.0),
            size=(upgrade_width - 10.0, upgrade_length - 25.0),
            shape=ElementShape.ROUNDED_RECT,
            corner_radius=5.0,
            bottom_rounding=2.0,
            depth=under_depth,
            z_offset=under_z,
            pull_out=False,
            label="UnderUpgradeLeft",
        )
    )
    elements.append(
        CompartmentElement(
            offset=(x_shift + 33.0, 5.0),
            size=(class_ii_ship_length + 10.0, upgrade_length - 10.0),
            shape=ElementShape.ROUNDED_RECT,
            corner_radius=5.0,
            bottom_rounding=2.0,
            depth=under_depth,
            z_offset=under_z,
            pull_out=False,
            label="UnderUpgradeRight",
        )
    )

    # 3. Class I ship (circular, d=24mm) + "1" floor inlay
    c1_cx = x_shift + class_i_ship_diameter - 1.0
    c1_cy = railgun_length + cargo_width + 17.0 + class_i_ship_diameter / 2.0
    c1_z = inner_height - class_i_ship_thickness - upgrade_thickness - 2.0
    elements.append(
        _centered(
            c1_cx,
            c1_cy,
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
            c1_cx,
            c1_cy,
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

    # 4. Class II ship (38 x 19mm rounded rect) + "2" floor inlay
    c2_cx = x_shift + class_ii_ship_length + class_i_ship_diameter - 5.0
    c2_cy = inner_length - class_ii_ship_width / 2.0 - 10.0
    c2_z = inner_height - class_ii_ship_thickness - upgrade_thickness - 2.0
    elements.append(
        _centered(
            c2_cx,
            c2_cy,
            (class_ii_ship_length, class_ii_ship_width),
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
            c2_cx,
            c2_cy,
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

    # 5. Class III ship (rounded equilateral triangle SVG, edge=43mm) + "3" inlay
    c3_cx = x_shift + class_i_ship_diameter + class_ii_ship_width + class_iii_ship_radius - 10.0
    c3_cy = inner_length - class_ii_ship_width - class_iii_ship_edge_length / 2.0 - 10.0
    c3_z = inner_height - class_iii_ship_thickness - upgrade_thickness - 2.0
    elements.append(
        _centered(
            c3_cx,
            c3_cy,
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
            c3_cx,
            c3_cy + 4.0,
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

    # 6. Three Cargo pieces (13.5 x 13.5mm) + deeper round nub holes
    cargo_z = inner_height - cargo_thickness - upgrade_thickness - 2.0
    for i in range(3):
        cx = x_shift + (cargo_width + 3.0) * i + cargo_width / 2.0 + 10.0
        cy = cargo_width / 2.0 + 10.0
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

    # 7. Three Railgun pieces (10 x 19mm) + offset round nub holes
    railgun_z = inner_height - railgun_thickness - upgrade_thickness - 2.0
    for i in range(3):
        cx = x_shift + (railgun_width + 3.0) * i + railgun_width / 2.0 + 15.0
        cy = railgun_length / 2.0 + cargo_width + 15.0
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

    # 8. Player tokens (circular, d=14.5mm, stack of 2)
    pt_cx = x_shift + player_token_diameter / 2.0 + 10.5
    pt_cy = inner_length - player_token_diameter / 2.0 - 6.0
    pt_z = inner_height - cardboard_token_thickness * 2.0 - upgrade_thickness - 2.0
    elements.append(
        _centered(
            pt_cx,
            pt_cy,
            (player_token_diameter, player_token_diameter),
            shape=ElementShape.CIRCLE,
            depth=inner_height - pt_z,
            z_offset=pt_z,
            pull_out=True,
            label="PlayerTokens",
        )
    )

    return tuple(elements)


project = Project(
    "Brink",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
    box_defaults={"expandable": False},
)

BRINK_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Sector Hex Tile Box ────────────────────────────────────────
hex_box = project.box(
    BoxType.CAP,
    "HexBox",
    size=(hex_box_width, hex_box_length, hex_box_height),
    lid=LidBuilder(
        text="Hex Tiles",
        label_mode=LabelMode.FRAMED,
        pattern=BRINK_PATTERN,
        text_color=Color("white"),
        frame_color=Color("dimgray"),
    ),
)
for h in range(3):
    hex_box.compartment(
        f"Sector_{h + 1}",
        width_ratio=1.0 / 3.0,
        cut=FingerCut.SCOOP,
    )

# ── 2. Player Boxes ───────────────────────────────────────────────
player_inner_w = player_box_width - 2.0 * wall_thickness
player_inner_l = player_box_length - 2.0 * wall_thickness
player_inner_h = player_box_height - floor_thickness - lid_thickness
PLAYER_ELEMENTS = _player_box_elements(player_inner_w, player_inner_l, player_inner_h)

player_factions = ["Solari", "Vanguard", "Eclipse", "Horizon"]
for faction in player_factions:
    p_box = project.box(
        BoxType.CAP,
        f"PlayerBox_{faction}",
        size=(player_box_width, player_box_length, player_box_height),
        lid=LidBuilder(
            text=faction,
            label_mode=LabelMode.FRAMED,
            pattern=BRINK_PATTERN,
            text_color=Color("white"),
            frame_color=Color("royalblue"),
        ),
    )
    p_box.compartment(
        "ShipsAndUpgrades",
        size=(player_inner_w, player_inner_l),
        elements=PLAYER_ELEMENTS,
        element_margin=0.0,
    )

# ── 3. Modular Card Boxes ─────────────────────────────────────────
card_types = [
    ("Actions", "Actions", "gold"),
    ("Riders", "Riders", "firebrick"),
    ("Ambassadors", "Ambassadors", "navy"),
    ("Factions", "Factions", "forestgreen"),
]

for deck_id, title, color_name in card_types:
    c_box = project.box(
        BoxType.SLIDING,
        f"CardBox_{deck_id}",
        size=(ambassador_box_width, ambassador_box_length, usable_height / 3.0),
        lid_slide_axis="x",
        lid=LidBuilder(
            text=title,
            label_mode=LabelMode.FRAMED,
            pattern=BRINK_PATTERN,
            text_color=Color("white"),
            frame_color=Color(color_name),
        ),
        stackable=StackableMode.PYRAMIDS,
    )
    c_box.compartment(
        "Cards",
        cut=FingerCut.SCOOP,
    )

project.stack_order("CardBox_Actions", "CardBox_Ambassadors")
project.stack_order("CardBox_Riders", "CardBox_Factions")

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
