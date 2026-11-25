#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Brink board game organizer.

Ports examples/brink.scad to the pyboxbuilder Project API.
Organizes all Brink components (2-5 players):
- 5 Player boxes (upgrade board, Class I/II/III ships with floor inlays,
  3 cargo + nubs, 3 railguns + nubs, and player/score tokens with finger access)
- 4 Primary faction resource cube boxes (Komek, Ventus, Henko, Magnomi) with
  faction SVG logo lids
- 2 Secondary resource/extra boxes (Sorelia cubes + UA cubes/Flagship/Fusion Drive)
  with faction SVG logo lids
- 2 Hex tile boxes (25 map hexes + starting/bonus hexes)
- 7 Sliding card boxes (Actions, Riders, Ambassadors, Factions, Rivals,
  Community, Holo) with automated spacers.
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
    LabelShape,
    LidBuilder,
    PatternBuilder,
    PatternType,
    Project,
    ScoopSide,
    run,
)

# ── Box & Board Dimensions (from lib/brink.scad & brink.scad) ─────
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
single_card_thickness = 0.8

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

SVG_DIR = Path(__file__).resolve().parent / "svg"
CLASS_III_SVG = str(SVG_DIR / "class_iii_ship.svg")
BRINK_LOGO_SVG = str(SVG_DIR / "brink_logo.svg")
SECTOR_HEX_SVG = str(SVG_DIR / "sector_hex.svg")

# Card box footprints (from brink.scad)
card_box_width = box_width / 2.0 - 1.0                            # 106.5mm
card_box_length = small_card_length + wall_thickness * 2.0        # 77.5mm
ambassador_card_box_height = single_card_thickness * 25.0 + floor_thickness + lid_thickness + 0.5  # 24.5mm
faction_card_box_height = single_card_thickness * 5.0 + floor_thickness + lid_thickness + 0.5      # 8.5mm
rival_card_box_height = single_card_thickness * 4.0 + floor_thickness + lid_thickness + 0.5        # 7.7mm
bonus_card_box_height = single_card_thickness * 15.0 + floor_thickness + lid_thickness + 0.5       # 16.5mm
action_card_box_height = single_card_thickness * 52.0 / 2.0 + floor_thickness + lid_thickness      # 24.8mm
rider_card_box_height = single_card_thickness * 20.0 / 2.0 + floor_thickness + lid_thickness       # 12.0mm

# Player boxes (5 players, matching brink.scad)
player_box_width = (box_width - 3.0) / 2.0                        # 106.0mm
player_box_length = wall_thickness * 2.0 + upgrade_length + 2.0   # 110.0mm
player_box_height = (
    upgrade_thickness + cargo_thickness + round_nub_thickness
    + floor_thickness + lid_thickness + 2.0
)                                                                 # 21.0mm

# Hex boxes (77.5 + 110.0 + 119.5 = 307.0mm exact fit along Y)
hex_box_width = box_width - 2.0                                   # 213.0mm
hex_box_length = box_length - card_box_length - player_box_length  # 119.5mm
hex_box_height = math.ceil(25 / 3) * cardboard_token_thickness + floor_thickness + lid_thickness   # 22.0mm

# 4 primary faction cube boxes (stacked on top of HexBox + HexBonusBox)
resource_box_width = (box_width - 2.0) / 4.0                      # 53.25mm
resource_box_length = hex_box_length                              # 119.5mm
resource_box_height = 25.0                                        # 21mm inner (2 layers of 11mm cubes)

# Size HexBonusBox so HexBox + HexBonusBox + ResourceBox = 63.0mm (exact match to 3-high PlayerBox stack),
# eliminating the thin 5mm wafer spacer above the resource boxes.
hex_bonus_box_height = player_box_height * 3.0 - hex_box_height - resource_box_height  # 16.0mm

# 2 secondary boxes (Sorelia cubes + UA cubes/Flagship/Fusion Drive)
resource_box_2_width = player_box_width / 2.0                     # 53.0mm
resource_box_2_length = player_box_length                         # 110.0mm
resource_box_2_height = player_box_height                         # 21.0mm


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
    c3_cx = x_shift + class_i_ship_diameter + class_ii_ship_width + class_iii_ship_radius - 8.5
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
        cx = x_shift + (railgun_width + 3.0) * i + railgun_width / 2.0 + 10.0
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

    # 8. Player / score tokens (circular, d=14.5mm, stack of 2) + opposing finger access
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
            pull_out=False,
            label="PlayerTokens",
        )
    )
    elements.append(
        _centered(
            pt_cx,
            pt_cy,
            (28.0, 9.0),
            shape=ElementShape.ROUNDED_RECT,
            corner_radius=4.5,
            bottom_rounding=3.0,
            depth=inner_height - pt_z,
            z_offset=pt_z,
            pull_out=False,
            label="PlayerTokensFingerAccess",
        )
    )

    return tuple(elements)


def _hex_box_elements(
    inner_width: float,
    inner_length: float,
    inner_height: float,
) -> tuple[CompartmentElement, ...]:
    """Build 3 staggered 72mm hexagonal tile wells matching brink.scad HexBox."""
    hex_fw = hex_width / math.cos(math.radians(30.0))  # ~83.138mm point-to-point
    hex_r = hex_fw / 2.0                               # ~41.569mm
    centers = [
        ("HexStack_1", hex_r + 0.8, hex_width / 2.0 + 0.2),
        ("HexStack_2", inner_width - hex_r - 0.8, hex_width / 2.0 + 0.2),
        ("HexStack_3", inner_width / 2.0, inner_length - hex_width / 2.0 - 0.2),
    ]
    return tuple(
        CompartmentElement(
            offset=(cx - hex_fw / 2.0, cy - hex_width / 2.0),
            size=(hex_width, hex_width),
            shape=ElementShape.HEXAGON,
            depth=inner_height,
            z_offset=0.0,
            pull_out=True,
            label=label,
        )
        for label, cx, cy in centers
    )


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

# ── Game Component Inventory (with physical specs & SVG shapes) ───
project.define_tile("Map Sector Hex Tiles", 25, size=(hex_width, hex_width, cardboard_token_thickness), bulk=True)
project.define_tile("Starting & Bonus Hex Tiles", 15, size=(hex_width, hex_width, cardboard_token_thickness), bulk=True)
project.define_piece("Player Upgrade Boards", 5, size=(upgrade_width, upgrade_length, upgrade_thickness))
project.define_piece("Class I Ships", 5, diameter=class_i_ship_diameter, thickness=class_i_ship_thickness)
project.define_piece("Class II Ships", 5, size=(class_ii_ship_width, class_ii_ship_length, class_ii_ship_thickness))
project.define_piece(
    "Class III Ships",
    5,
    size=(class_iii_ship_edge_length, class_iii_ship_height, class_iii_ship_thickness),
    svg=CLASS_III_SVG,
)
project.define_piece("Cargo Modules", 15, size=(cargo_width, cargo_width, cargo_thickness))
project.define_piece("Railguns", 15, size=(railgun_width, railgun_length, railgun_thickness))
project.define_piece("Player & Score Tokens", 10, diameter=player_token_diameter, thickness=cardboard_token_thickness)
for _res_name, _res_qty in [
    ("Komek Resource Cubes", 25),
    ("Ventus Resource Cubes", 25),
    ("Henko Resource Cubes", 25),
    ("Magnomi Resource Cubes", 25),
    ("Sorelia Resource Cubes", 20),
    ("UA Cubes", 15),
    ("UA Flagship", 1),
    ("Fusion Drive", 1),
    ("First Player Token", 1),
]:
    project.define_piece(_res_name, _res_qty, bulk=True)

project.define_cards("Action Cards", 52, size=(card_width, card_length), thickness=single_card_thickness)
project.define_cards("Rider Cards", 20, size=(card_width, card_length), thickness=single_card_thickness)
project.define_cards(
    "Ambassador Cards", 25, size=(small_card_width, small_card_length), thickness=single_card_thickness
)
project.define_cards("Faction Cards", 5, size=(small_card_width, small_card_length), thickness=single_card_thickness)
project.define_cards("Rival Cards", 4, size=(small_card_width, small_card_length), thickness=single_card_thickness)
project.define_cards("Community Cards", 15, size=(small_card_width, small_card_length), thickness=single_card_thickness)
project.define_cards("Holo Cards", 15, size=(small_card_width, small_card_length), thickness=single_card_thickness)
project.component("Player Screens", 5, kind="board")
project.component("Main Board & Rulebooks", 1, kind="board")

# Partial boards resting behind the front card row (matching brink.scad)
project.board(
    "Player Screens",
    size=(210.0, 210.0, upgrade_thickness * 2.0),
    position=(0.0, card_box_length, usable_height),
    count=5,
    notes="Folded player screens behind front card row",
    component="Player Screens",
)
project.board(
    "Main Board & Rulebooks",
    size=(box_width, box_length - card_box_length, board_thickness - upgrade_thickness * 2.0),
    position=(0.0, card_box_length, usable_height + upgrade_thickness * 2.0),
    count=1,
    notes="Rests over player screens, hex & resource boxes",
    component="Main Board & Rulebooks",
)

BRINK_PATTERN = PatternBuilder(PatternType.VORONOI)
BRINK_FONT = "Futura:style=Bold"
BRINK_TEXT_SPACING = 1.18

# ── 1. Sector Hex Tile Boxes (Main + Bonus) ───────────────────────
hex_inner_w = hex_box_width - 2.0 * wall_thickness
hex_inner_l = hex_box_length - 2.0 * wall_thickness

for label, title, h, hex_comp, hex_qty in [
    ("HexBox", "Hexes", hex_box_height, "Map Sector Hex Tiles", 25),
    ("HexBonusBox", "Bonus Hexes", hex_bonus_box_height, "Starting & Bonus Hex Tiles", 15),
]:
    hb = project.box(
        BoxType.CAP,
        label,
        size=(hex_box_width, hex_box_length, h),
        lid=LidBuilder(
            text=title.upper(),
            logo=SECTOR_HEX_SVG,
            logo_color=Color("white"),
            logo_position="top",
            label_logo_size_mm=26.0,
            label_mode=LabelMode.FRAMED,
            label_shape=LabelShape.HEX_BRACKET,
            font=BRINK_FONT,
            text_spacing=BRINK_TEXT_SPACING,
            pattern=BRINK_PATTERN,
            text_color=Color("white"),
            frame_color=Color("dimgray"),
        ),
    )
    hb.compartment(
        "HexTiles",
        size=(hex_inner_w, hex_inner_l),
        elements=_hex_box_elements(hex_inner_w, hex_inner_l, h - floor_thickness - lid_thickness),
        element_margin=0.0,
        component=hex_comp,
        count=hex_qty,
    )
    hex_offset_x = hex_inner_w / 2.0 - (hex_width / (2.0 * math.cos(math.radians(30.0))) + 0.8)
    hb.finger_hole(ScoopSide.FRONT, width=22.0, offset=-hex_offset_x)
    hb.finger_hole(ScoopSide.FRONT, width=22.0, offset=hex_offset_x)
    hb.finger_hole(ScoopSide.BACK, width=22.0, offset=0.0)

# ── 2. Five Player Boxes (matching brink.scad) ────────────────────
player_inner_w = player_box_width - 2.0 * wall_thickness
player_inner_l = player_box_length - 2.0 * wall_thickness
player_inner_h = player_box_height - floor_thickness - lid_thickness
PLAYER_ELEMENTS = _player_box_elements(player_inner_w, player_inner_l, player_inner_h)

player_colors = [
    ("Yellow", "gold", "black"),
    ("Orange", "darkorange", "white"),
    ("Purple", "purple", "white"),
    ("Blue", "royalblue", "white"),
    ("Green", "forestgreen", "white"),
]
for color_label, frame_col, text_col in player_colors:
    p_box = project.box(
        BoxType.CAP,
        f"PlayerBox_{color_label}",
        size=(player_box_width, player_box_length, player_box_height),
        lid=LidBuilder(
            text="PLAYER",
            logo=BRINK_LOGO_SVG,
            logo_color=Color(frame_col),
            logo_position="top",
            label_logo_size_mm=22.0,
            label_mode=LabelMode.FRAMED,
            label_shape=LabelShape.HEX_BRACKET,
            font=BRINK_FONT,
            text_spacing=BRINK_TEXT_SPACING,
            pattern=BRINK_PATTERN,
            text_color=Color(text_col),
            frame_color=Color(frame_col),
        ),
    )
    p_box.compartment(
        "ShipsAndUpgrades",
        size=(player_inner_w, player_inner_l),
        elements=PLAYER_ELEMENTS,
        element_margin=0.0,
        allocates={
            "Player Upgrade Boards": 1,
            "Class I Ships": 1,
            "Class II Ships": 1,
            "Class III Ships": 1,
            "Cargo Modules": 3,
            "Railguns": 3,
            "Player & Score Tokens": 2,
        },
    )

# ── 3. Four Primary Faction Cube Boxes (Logo Lids) ────────────────
primary_factions = [
    ("Komek", "royalblue", "komek.svg"),
    ("Ventus", "gold", "ventus.svg"),
    ("Henko", "forestgreen", "henko.svg"),
    ("Magnomi", "darkorange", "magnomi.svg"),
]
for faction, color_name, logo_file in primary_factions:
    r_box = project.box(
        BoxType.CAP,
        f"ResourceBox_{faction}",
        size=(resource_box_width, resource_box_length, resource_box_height),
        lid=LidBuilder(
            logo=str(SVG_DIR / logo_file),
            logo_color=Color(color_name),
            pattern=BRINK_PATTERN,
        ),
    )
    r_box.compartment("Cubes", holds_pieces=True, component=f"{faction} Resource Cubes", count=25)

# ── 4. Secondary Faction (Sorelia) & UA / Extra Bits Boxes ────────
secondary_boxes: list[tuple[str, str, str, str, dict[str, int]]] = [
    ("Sorelia", "purple", "sorelia.svg", "Cubes", {"Sorelia Resource Cubes": 20}),
    (
        "UA",
        "crimson",
        "ua.svg",
        "UAAndExtras",
        {
            "UA Cubes": 15,
            "UA Flagship": 1,
            "Fusion Drive": 1,
            "First Player Token": 1,
        },
    ),
]
for name, color_name, logo_file, comp_name, allocs in secondary_boxes:
    r2_box = project.box(
        BoxType.CAP,
        f"ResourceBox_{name}",
        size=(resource_box_2_width, resource_box_2_length, resource_box_2_height),
        lid=LidBuilder(
            logo=str(SVG_DIR / logo_file),
            logo_color=Color(color_name),
            pattern=BRINK_PATTERN,
        ),
    )
    r2_box.compartment(comp_name, holds_pieces=True, allocates=allocs)

# ── 5. Seven Sliding Card Boxes (matching brink.scad) ─────────────
# Two-column small-card decks (Actions & Riders)
for deck_id, title, color_name, h, card_comp, half_qty in [
    ("Actions", "Actions", "gold", action_card_box_height, "Action Cards", 26),
    ("Riders", "Riders", "firebrick", rider_card_box_height, "Rider Cards", 10),
]:
    c_box = project.box(
        BoxType.SLIDING,
        f"CardBox_{deck_id}",
        size=(card_box_width, card_box_length, h),
        lid_slide_axis="y",
        lid=LidBuilder(
            text=title.upper(),
            label_mode=LabelMode.FRAMED,
            label_shape=LabelShape.HEX_BRACKET,
            font=BRINK_FONT,
            text_spacing=BRINK_TEXT_SPACING,
            pattern=BRINK_PATTERN,
            text_color=Color("black" if color_name == "gold" else "white"),
            frame_color=Color(color_name),
        ),
    )
    c_box.compartment("CardsLeft", width_ratio=0.5, cut=FingerCut.SCOOP, component=card_comp, count=half_qty)
    c_box.compartment("CardsRight", width_ratio=0.5, cut=FingerCut.SCOOP, component=card_comp, count=half_qty)

# Single-column standard-card decks (Ambassadors, Factions, Rivals, Community, Holo)
for deck_id, title, color_name, h, card_comp, qty in [
    ("Ambassadors", "Ambassadors", "navy", ambassador_card_box_height, "Ambassador Cards", 25),
    ("Factions", "Factions", "forestgreen", faction_card_box_height, "Faction Cards", 5),
    ("Rivals", "Rivals", "darkorange", rival_card_box_height, "Rival Cards", 4),
    ("Community", "Community", "teal", bonus_card_box_height, "Community Cards", 15),
    ("Holo", "Holo", "purple", bonus_card_box_height, "Holo Cards", 15),
]:
    c_box = project.box(
        BoxType.SLIDING,
        f"CardBox_{deck_id}",
        size=(card_box_width, card_box_length, h),
        lid_slide_axis="x",
        lid=LidBuilder(
            text=title.upper(),
            label_mode=LabelMode.FRAMED,
            label_shape=LabelShape.HEX_BRACKET,
            font=BRINK_FONT,
            text_spacing=BRINK_TEXT_SPACING,
            pattern=BRINK_PATTERN,
            text_color=Color("white"),
            frame_color=Color(color_name),
        ),
    )
    c_box.compartment("Cards", cut=FingerCut.SCOOP, component=card_comp, count=qty)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
