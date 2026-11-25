#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Brink: Long Box Variant organizer.

Ports examples/brink_long.scad to the pyboxbuilder Project API.
Organizes all Brink components (2-5 players) using elongated longitudinal
player trays:
- 5 Long Player trays (upgrade board, 3 cargo + nubs, 3 railguns + nubs,
  player/score tokens with finger access, Class I/II/III ships with floor
  inlays, voting board, and 5 resource bays)
- 4 Primary faction resource cube boxes (Komek, Ventus, Henko, Magnomi) +
  2 Secondary boxes (Sorelia cubes + UA cubes/Flagship/Fusion Drive) with
  faction SVG logo lids
- Sliding card boxes (Actions, Riders, Ambassadors, Factions, Rivals,
  Community, Holo) and Sector Hex box with automated spacers.
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

# ── Box & Board Dimensions (from lib/brink.scad & brink_long.scad) ──
box_width = 215.0
box_length = 307.0
box_height = 96.0

board_thickness = 18.0
usable_height = box_height - board_thickness  # 78.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

single_card_thickness = 0.8
small_card_width = 49.0
small_card_length = 71.5
hex_width = 72.0
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

SVG_DIR = ROOT / "boxes" / "brink" / "svg"
CLASS_III_SVG = str(SVG_DIR / "class_iii_ship.svg")
BRINK_LOGO_SVG = str(SVG_DIR / "brink_logo.svg")
SECTOR_HEX_SVG = str(SVG_DIR / "sector_hex.svg")

long_player_box_width = 106.0
long_player_box_length = box_length - 2.0  # 305.0mm
long_player_box_height = (
    floor_thickness + lid_thickness + cargo_thickness
    + round_nub_thickness + upgrade_thickness
)                                          # 19.0mm (matches brink_long.scad: 3 stacked=57mm, 2 stacked=38mm)

card_box_width = 106.0                     # 106 + 106 = 212mm <= 215mm
card_box_length = small_card_length + wall_thickness * 2.0  # 77.5mm
card_floor_lid = 1.5                       # 1.5mm floor + 1.5mm lid keeps all 5 decks in the 40mm upper-right band
action_card_box_height = 26.0              # 23.0mm inner (52 small cards in 2 stacks = 20.8mm)
rider_card_box_height = 14.0               # 11.0mm inner (20 small cards in 2 stacks = 8.0mm); 26+14=40mm at Z=78mm
ambassador_card_box_height = 23.5          # 20.5mm inner (25 Ambassador cards = 20.0mm)
faction_card_box_height = 8.0              # 5.0mm inner (5 Faction Objective cards = 4.0mm)
rival_card_box_height = 8.5                # 5.5mm inner (4 Rival + Guide cards)

# Full-width 3-stack HexBox sitting atop the 3-high player stack (Z = 57..78mm)
# 1.5mm floor + 1.5mm lid -> 18.0mm inner = 3 x 9 = 27 hexes (25 map hexes + starting tile)
hex_box_width = 212.0
hex_box_length = 119.5
hex_box_height = 21.0
hex_floor_lid = 1.5

# 4 Primary Faction cube boxes (2x2 grid filling X=0..106, Y=119.5..306.5, Z=57..78mm)
# With 2.5mm walls -> 48 x 88.5 x 17mm inner (72.2 cm^3, easily holds 28+ 11mm cubes each)
resource_box_width = 53.0
resource_box_length = 93.5
resource_box_height = 21.0
resource_wall_thickness = 2.5

# 2 Secondary boxes (Sorelia + UA) bridging right side Z=38..57mm cleanly under HexBox
resource_box_2_width = 53.0
resource_box_2_length = hex_box_length     # 119.5mm
resource_box_2_height = long_player_box_height  # 19.0mm (levels right side to Z=57mm!)


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
    """Build all piece cutouts for the Brink Long player tray."""
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

    under_depth = upgrade_thickness + 4.5
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

    cargo_z = inner_height - upgrade_thickness - cargo_thickness
    for i in range(3):
        cx = 30.0 + 20.0 * i
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

    railgun_z = inner_height - upgrade_thickness - railgun_thickness
    for i in range(3):
        cx = 30.0 + 20.0 * i
        cy = 247.0
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

    # Player / victory score tokens centered cleanly above the railguns inside UnderUpgrade
    pt_z = inner_height - upgrade_thickness - cardboard_token_thickness * 2.0 - 1.0
    elements.append(
        _centered(
            50.0,
            278.0,
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
            50.0,
            278.0,
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

    # ── Bottom-left region (X = 2..59, Y = 0..196): Voting board + 5 wide cube bays
    voting_depth = cardboard_token_thickness + 1.0
    elements.append(
        CompartmentElement(
            offset=(2.0, 0.0),
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
                offset=(2.0, 4.0 + bay_step * i),
                size=(57.0, bay_h),
                shape=ElementShape.ROUNDED_RECT,
                corner_radius=5.0,
                bottom_rounding=4.0,
                depth=inner_height,
                z_offset=0.0,
                pull_out=False,
                label=f"VotingBay_{i + 1}",
            )
        )

    # ── Bottom-right region (X = 61.5..98.5, Y = 4..188): Class III, II, I ships + tray
    c3_z = inner_height - upgrade_thickness - 1.0 - class_iii_ship_thickness
    elements.append(
        CompartmentElement(
            offset=(80.0 - class_iii_ship_height / 2.0, 165.0 - class_iii_ship_edge_length / 2.0),
            size=(class_iii_ship_edge_length, class_iii_ship_height),
            rotation=90.0,
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
            77.0,
            165.0,
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
            80.0,
            114.0,
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
            80.0,
            114.0,
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
            80.0,
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
            80.0,
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
            offset=(62.5, 4.0),
            size=(35.0, 38.0),
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
    box_defaults={"expandable": False},
)

# ── Game Component Inventory (with physical specs & SVG shapes) ───
project.component("Main Map Board", 1, kind="board")
project.component("Player Shields", 5, kind="board")
project.component("Rulebook", 1, kind="board")

project.define_piece("Upgrade Boards", 5, size=(upgrade_width, upgrade_length, upgrade_thickness))
project.define_piece("Voting Boards", 5, size=(voting_board_width, voting_board_length, cardboard_token_thickness))
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
project.define_piece("Player Score Tokens", 10, diameter=player_token_diameter, thickness=cardboard_token_thickness)

for _res_name, _res_qty in [
    ("Komek Resource Cubes", 28),
    ("Ventus Resource Cubes", 28),
    ("Henko Resource Cubes", 28),
    ("Magnomi Resource Cubes", 28),
    ("Sorelia Resource Cubes", 28),
    ("UA Resource Cubes", 15),
    ("UA Flagship", 1),
    ("Fusion Drive", 1),
    ("First Player Token", 1),
]:
    project.define_piece(_res_name, _res_qty, bulk=True)

project.define_cards("Action Cards", 52, size=(small_card_width, small_card_length), thickness=single_card_thickness)
project.define_cards("Rider Cards", 20, size=(small_card_width, small_card_length), thickness=single_card_thickness)
project.define_cards(
    "Ambassador Cards", 25, size=(small_card_width, small_card_length), thickness=single_card_thickness
)
project.define_cards(
    "Faction Objective Cards", 5, size=(small_card_width, small_card_length), thickness=single_card_thickness
)
project.define_cards(
    "Rival & Guide Cards", 4, size=(small_card_width, small_card_length), thickness=single_card_thickness
)

project.define_tile("Sector Hex Tiles", 25, size=(hex_width, hex_width, cardboard_token_thickness), bulk=True)
project.define_tile("Starting Hex Tile", 1, size=(hex_width, hex_width, cardboard_token_thickness), bulk=True)

project.board(
    "Main Board & Rulebooks",
    size=(box_width, box_length, board_thickness),
    position=(0.0, 0.0, box_height - board_thickness),
    count=1,
    notes="Rests flush on top of all boxes",
    allocates={"Main Map Board": 1, "Player Shields": 5, "Rulebook": 1},
)

BRINK_PATTERN = PatternBuilder(PatternType.VORONOI)
BRINK_FONT = "Futura:style=Bold"
BRINK_TEXT_SPACING = 1.18

# ── 1. Five Longitudinal Player Trays (3 left + 2 right) ──────────
long_inner_w = long_player_box_width - 2.0 * wall_thickness
long_inner_l = long_player_box_length - 2.0 * wall_thickness
long_inner_h = long_player_box_height - floor_thickness - lid_thickness
LONG_PLAYER_ELEMENTS = _long_player_elements(long_inner_w, long_inner_l, long_inner_h)

player_specs = [
    ("Yellow", "gold", "black", (0.0, 0.0, 0.0)),
    ("Purple", "purple", "white", (0.0, 0.0, long_player_box_height)),
    ("Green", "forestgreen", "white", (0.0, 0.0, long_player_box_height * 2.0)),
    ("Orange", "darkorange", "white", (long_player_box_width, 0.0, 0.0)),
    ("Blue", "royalblue", "white", (long_player_box_width, 0.0, long_player_box_height)),
]
for color_label, frame_col, text_col, pos in player_specs:
    p_box = project.box(
        BoxType.CAP,
        f"PlayerBox_{color_label}",
        size=(long_player_box_width, long_player_box_length, long_player_box_height),
        position=pos,
        lid=LidBuilder(
            text="PLAYER",
            logo=BRINK_LOGO_SVG,
            logo_color=Color(frame_col),
            logo_position="left",
            label_logo_size_mm=24.0,
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
        "FleetContents",
        size=(long_inner_w, long_inner_l),
        elements=LONG_PLAYER_ELEMENTS,
        element_margin=0.0,
        allocates={
            "Upgrade Boards": 1,
            "Voting Boards": 1,
            "Class I Ships": 1,
            "Class II Ships": 1,
            "Class III Ships": 1,
            "Cargo Modules": 3,
            "Railguns": 3,
            "Player Score Tokens": 2,
        },
    )

# ── 2. Faction Cube & UA / Extra Bits Boxes (Logo Lids) ──────────
z_top_band = long_player_box_height * 3.0  # 57.0mm
z_mid_right = long_player_box_height * 2.0  # 38.0mm

primary_factions = [
    ("Komek", "royalblue", "komek.svg", (0.0, hex_box_length, z_top_band)),
    ("Ventus", "gold", "ventus.svg", (resource_box_width, hex_box_length, z_top_band)),
    ("Henko", "forestgreen", "henko.svg", (0.0, hex_box_length + resource_box_length, z_top_band)),
    ("Magnomi", "darkorange", "magnomi.svg", (resource_box_width, hex_box_length + resource_box_length, z_top_band)),
]
for name, color_name, logo_file, pos in primary_factions:
    r_box = project.box(
        BoxType.CAP,
        f"ResourceBox_{name}",
        size=(resource_box_width, resource_box_length, resource_box_height),
        position=pos,
        wall_thickness=resource_wall_thickness,
        lid=LidBuilder(
            logo=str(SVG_DIR / logo_file),
            logo_color=Color(color_name),
            pattern=BRINK_PATTERN,
        ),
    )
    r_box.compartment("Cubes", holds_pieces=True, component=f"{name} Resource Cubes", count=28)

secondary_boxes = [
    (
        "Sorelia",
        "purple",
        "sorelia.svg",
        "Cubes",
        (long_player_box_width, 0.0, z_mid_right),
        {"Sorelia Resource Cubes": 28},
    ),
    (
        "UA",
        "crimson",
        "ua.svg",
        "UAAndExtras",
        (long_player_box_width + resource_box_2_width, 0.0, z_mid_right),
        {
            "UA Resource Cubes": 15,
            "UA Flagship": 1,
            "Fusion Drive": 1,
            "First Player Token": 1,
        },
    ),
]
for name, color_name, logo_file, comp_name, pos, alloc in secondary_boxes:
    r2_box = project.box(
        BoxType.CAP,
        f"ResourceBox_{name}",
        size=(resource_box_2_width, resource_box_2_length, resource_box_2_height),
        position=pos,
        wall_thickness=resource_wall_thickness,
        lid=LidBuilder(
            logo=str(SVG_DIR / logo_file),
            logo_color=Color(color_name),
            pattern=BRINK_PATTERN,
        ),
    )
    r2_box.compartment(comp_name, holds_pieces=True, allocates=alloc)

# ── 3. Sliding Card Boxes ─────────────────────────────────────────
for deck_id, title, color_name, h, pos, card_comp, half_count in [
    (
        "Actions",
        "Actions",
        "gold",
        action_card_box_height,
        (long_player_box_width, hex_box_length, z_mid_right),
        "Action Cards",
        26,
    ),
    (
        "Riders",
        "Riders",
        "firebrick",
        rider_card_box_height,
        (long_player_box_width, hex_box_length, z_mid_right + action_card_box_height),
        "Rider Cards",
        10,
    ),
]:
    c_box = project.box(
        BoxType.SLIDING,
        f"CardBox_{deck_id}",
        size=(card_box_width, card_box_length, h),
        position=pos,
        floor_thickness=card_floor_lid,
        lid_thickness=card_floor_lid,
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
    c_box.compartment("CardsLeft", width_ratio=0.5, cut=FingerCut.SCOOP, component=card_comp, count=half_count)
    c_box.compartment("CardsRight", width_ratio=0.5, cut=FingerCut.SCOOP, component=card_comp, count=half_count)

y_right_cards2 = hex_box_length + card_box_length          # 197.0mm
for deck_id, title, color_name, h, pos, card_comp, card_count in [
    (
        "Ambassadors",
        "Ambassadors",
        "navy",
        ambassador_card_box_height,
        (long_player_box_width, y_right_cards2, z_mid_right),
        "Ambassador Cards",
        25,
    ),
    (
        "Factions",
        "Factions",
        "forestgreen",
        faction_card_box_height,
        (long_player_box_width, y_right_cards2, z_mid_right + ambassador_card_box_height),
        "Faction Objective Cards",
        5,
    ),
    (
        "Rivals",
        "Rivals",
        "darkorange",
        rival_card_box_height,
        (
            long_player_box_width,
            y_right_cards2,
            z_mid_right + ambassador_card_box_height + faction_card_box_height,
        ),
        "Rival & Guide Cards",
        4,
    ),
]:
    c_box = project.box(
        BoxType.SLIDING,
        f"CardBox_{deck_id}",
        size=(card_box_width, card_box_length, h),
        position=pos,
        floor_thickness=card_floor_lid,
        lid_thickness=card_floor_lid,
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
    c_box.compartment("Cards", cut=FingerCut.SCOOP, component=card_comp, count=card_count)

# ── 4. Full-Width 3-Stack Sector Hex Box ──────────────────────────
hex_inner_w = hex_box_width - 2.0 * wall_thickness
hex_inner_l = hex_box_length - 2.0 * wall_thickness
hex_inner_h = hex_box_height - 2.0 * hex_floor_lid  # 18.0mm = 9 hexes x 3 stacks = 27 hexes
_hex_fw = hex_width / math.cos(math.radians(30.0))
_hex_r = _hex_fw / 2.0
HEX_ELEMENTS = tuple(
    CompartmentElement(
        offset=(cx - _hex_fw / 2.0, cy - hex_width / 2.0),
        size=(hex_width, hex_width),
        shape=ElementShape.HEXAGON,
        depth=hex_inner_h,
        z_offset=0.0,
        pull_out=True,
        label=lbl,
    )
    for lbl, cx, cy in [
        ("HexStack_1", _hex_r + 0.8, hex_width / 2.0 + 0.2),
        ("HexStack_2", hex_inner_w - _hex_r - 0.8, hex_width / 2.0 + 0.2),
        ("HexStack_3", hex_inner_w / 2.0, hex_inner_l - hex_width / 2.0 - 0.2),
    ]
)

h_box = project.box(
    BoxType.CAP,
    "HexBox",
    size=(hex_box_width, hex_box_length, hex_box_height),
    position=(0.0, 0.0, z_top_band),
    floor_thickness=hex_floor_lid,
    lid_thickness=hex_floor_lid,
    lid=LidBuilder(
        text="HEXES",
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
h_box.compartment(
    "HexTiles",
    size=(hex_inner_w, hex_inner_l),
    elements=HEX_ELEMENTS,
    element_margin=0.0,
    allocates={"Sector Hex Tiles": 25, "Starting Hex Tile": 1},
)
_hex_offset_x = hex_inner_w / 2.0 - (_hex_r + 0.8)
h_box.finger_hole(ScoopSide.FRONT, width=22.0, offset=-_hex_offset_x)
h_box.finger_hole(ScoopSide.FRONT, width=22.0, offset=_hex_offset_x)
h_box.finger_hole(ScoopSide.BACK, width=22.0, offset=0.0)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
