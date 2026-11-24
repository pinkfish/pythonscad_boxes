#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Maglev Metro board game organizer.

Ports boxes/maglev_metro/maglev_metro.scad to the pyboxbuilder Project API.
Organizes all 25 boxes/trays: 4 card boxes, 3 robot boxes, 2 commuter boxes,
2 small commuter boxes, start token box, 4 player boxes, 6 factory station
hex boxes, metro & studios tile box, and top/side spacers.
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
    LabelFinial,
    LabelMode,
    LabelShape,
    LidBuilder,
    PatternBuilder,
    PatternType,
    Project,
    StackableMode,
    run,
)

ASSETS = (
    Path(__file__).resolve().parent / "assets"
    if "__file__" in globals()
    else ROOT / "boxes" / "maglev_metro" / "assets"
)

# ── Box & Board Dimensions (from maglev_metro.scad) ───────────────
box_width = 286.0
box_length = 286.0
box_height = 65.0

player_board_thickness = 2.2
game_board_thickness = 4.2
game_board_base_thickness = 4.2
game_board_base_width = 241.0

# Boards stacked over the main columns:
# - Over X=45..73 (CardBox): 2 game_board_base (8.4) + 4 player_board (8.8) = 17.2mm
# - Over X=79..286 (Player/Factory/Metro): + 2 game_board (8.4) = 25.6mm
total_board_reserve = game_board_base_thickness * 2.0 + player_board_thickness * 4.0  # 17.2mm
usable_height = box_height - total_board_reserve  # 47.8mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

# ── Component Dimensions ──────────────────────────────────────────
factory_hex_width = 56.0
factory_hex_thickness = 7.5
factory_hex_radius = factory_hex_width / (2.0 * math.cos(math.radians(30.0)))

player_overlay_hex_width = 55.5
player_overlay_hex_radius = player_overlay_hex_width / (2.0 * math.cos(math.radians(30.0)))
player_overlay_hex_thickness = 1.5
player_overlay_hex_per_player = 18

train_width = 14.0
train_length = 41.5
train_thickness = 10.0

robot_width = 8.5
card_width = 67.0
card_length = 90.0

# ── Derived Sub-Box Dimensions (exact .scad formulas) ─────────────
card_box_width = wall_thickness * 2.0 + card_width  # 73.0mm
card_box_length = wall_thickness * 2.0 + card_length  # 96.0mm
card_box_height = usable_height / 2.0  # 23.9mm

start_token_box_width = 10.0
robot_box_width = card_box_width - start_token_box_width  # 63.0mm
robot_box_length = box_length - card_box_length * 2.0  # 94.0mm
robot_box_height = card_box_height / 2.0  # 11.95mm

commuter_box_width = robot_box_width  # 63.0mm
commuter_box_length = robot_box_length / 2.0  # 47.0mm
commuter_box_height = robot_box_height  # 11.95mm

commuter_box_small_width = box_width - game_board_base_width  # 45.0mm
commuter_box_small_length = wall_thickness * 2.0 + robot_width * 7.0 + 2.0  # 67.5mm
commuter_box_small_height = box_height - card_box_height * 2.0  # 17.2mm

start_token_box_length = robot_box_length  # 94.0mm
start_token_box_height = box_height  # 65.0mm (in the X=0..10 side strip beside boards)

player_box_width = wall_thickness * 2.0 + player_overlay_hex_width  # 61.5mm
player_box_length = box_width / 2.0  # 143.0mm
player_box_height = (
    box_height
    - game_board_base_thickness * 2.0
    - player_board_thickness * 4.0
    - game_board_thickness * 2.0
) / 2.0  # 19.7mm

factory_box_width = (box_width - card_box_width - player_box_width) / 2.0  # 75.75mm
factory_box_length = box_width / 4.0  # 71.5mm
factory_box_height = player_box_height  # 19.7mm

metro_box_width = box_width - card_box_width - player_box_width  # 151.5mm
metro_box_length = box_length - factory_box_length * 2.0  # 143.0mm
metro_box_height = factory_box_height  # 19.7mm

spacer_box_width = metro_box_width  # 151.5mm
spacer_box_length = metro_box_length + factory_box_length - 2.0  # 212.5mm
spacer_box_height = factory_box_height  # 19.7mm

spacer_top_width = commuter_box_small_width  # 45.0mm
spacer_top_length = card_box_length * 2.0 - commuter_box_small_length * 2.0  # 57.0mm
spacer_top_height = commuter_box_small_height  # 17.2mm

project = Project(
    "MaglevMetro",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=total_board_reserve,
    generate_spacers=True,
    box_defaults={"expandable": False},
)

project.define_inventory({
    "Connection Cards": 13,
    "Track Cards": 13,
    "Passenger Cards": 13,
    "Player Objective Cards": 13,
    "Silver Robots": 18,
    "Gold Robots": 18,
    "Orange Robots": 18,
    "Pink Commuters": 14,
    "Aqua Commuters": 14,
    "Purple Commuters": 11,
    "Coral Commuters": 11,
    "Start Token": 1,
    "Player Track Hexes": player_overlay_hex_per_player * 4,
    "Player Trains": 4,
    "Factory Station Hexes": 2,
    "Warehouse Station Hexes": 2,
    "Lab Station Hexes": 2,
    "Office Station Hexes": 2,
    "Store Station Hexes": 2,
    "Embassy Station Hexes": 2,
    "Studio Station Hexes": 2,
    "Metro Hub Tile": 1,
    "Game Board Bases": 2,
    "Player Boards": 4,
    "Game Boards": 2,
})

project.board(
    "Game Board Bases",
    size=(game_board_base_width, 272.0, game_board_base_thickness * 2.0),
    position=(box_width - game_board_base_width, 0.0, box_height - game_board_base_thickness * 2.0),
    count=2,
    component="Game Board Bases",
)
project.board(
    "Player Boards",
    size=(221.0, 245.0, player_board_thickness * 4.0),
    position=(box_width - 221.0, 0.0, usable_height),
    count=4,
    component="Player Boards",
)
project.board(
    "Game Boards",
    size=(207.0, 281.0, game_board_thickness * 2.0),
    position=(box_width - 207.0, 0.0, usable_height - game_board_thickness * 2.0),
    count=2,
    component="Game Boards",
)

METRO_PATTERN = PatternBuilder(PatternType.PENROSE)
METRO_FONT = "Futura:style=Bold"


def _lid(
    text: str,
    frame_color: str,
    *,
    image: str | None = None,
    logo_size_mm: float | None = None,
    finial: LabelFinial = LabelFinial.CHEVRON,
) -> LidBuilder:
    return LidBuilder(
        text=text,
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.HEX_BRACKET,
        label_finial=finial,
        font=METRO_FONT,
        logo=image,
        logo_color=Color("white") if image else None,
        logo_position="left",
        label_logo_size_mm=logo_size_mm,
        pattern=METRO_PATTERN,
        text_color=Color("white"),
        frame_color=Color(frame_color),
    )


# ── 1. Card Boxes (4, stacked 2x2 at X=0..73, Y=0..192) ──────────
card_specs = [
    ("CardBox_Connections", "Connection", (0.0, 0.0, 0.0), "Connection Cards"),
    ("CardBox_Tracks", "Track", (0.0, 0.0, card_box_height), "Track Cards"),
    ("CardBox_Passengers", "Passenger", (0.0, card_box_length, 0.0), "Passenger Cards"),
    ("CardBox_PlayerObjectives", "Player Board", (0.0, card_box_length, card_box_height), "Player Objective Cards"),
]
for label, title, pos, comp_name in card_specs:
    project.box(
        BoxType.SLIDING,
        label,
        size=(card_box_width, card_box_length, card_box_height),
        position=pos,
        lid_thickness=4.0,
        lid=_lid(title, "royalblue"),
        stackable=StackableMode.PYRAMIDS,
    ).compartment("Cards", cut=FingerCut.SCOOP, component=comp_name, count=13)

# ── 2. Robot & Commuter Boxes (X=10..73, Y=192..286) ─────────────
robot_specs = [
    ("RobotBox_Silver", "silver", 0, "Silver Robots"),
    ("RobotBox_Gold", "gold", 1, "Gold Robots"),
    ("RobotBox_Orange", "orange", 2, "Orange Robots"),
]
for label, color_name, idx, comp_name in robot_specs:
    project.box(
        BoxType.CAP,
        label,
        size=(robot_box_width, robot_box_length, robot_box_height),
        position=(start_token_box_width, card_box_length * 2.0, robot_box_height * idx),
        lid=_lid("Robots", color_name, image=str(ASSETS / "robot.svg"), logo_size_mm=16.0),
    ).compartment("Robots", cut=FingerCut.SCOOP, component=comp_name, count=18)

commuter_specs = [
    ("CommuterBox_Pink", "pink", 0, "Pink Commuters"),
    ("CommuterBox_Aqua", "aqua", 1, "Aqua Commuters"),
]
for label, color_name, idx, comp_name in commuter_specs:
    project.box(
        BoxType.CAP,
        label,
        size=(commuter_box_width, commuter_box_length, commuter_box_height),
        position=(
            start_token_box_width,
            card_box_length * 2.0 + commuter_box_length * idx,
            robot_box_height * 3.0,
        ),
        lid=_lid("Commuter", color_name, image=str(ASSETS / "commuter.svg"), logo_size_mm=14.0),
    ).compartment("Commuters", cut=FingerCut.SCOOP, component=comp_name, count=14)

# ── 3. Side-of-Board Strip (X=0..45, Z=47.8..65.0) + StartTokenBox
project.box(
    BoxType.CAP,
    "CommuterBoxSmall_Purple",
    size=(commuter_box_small_width, commuter_box_small_length, commuter_box_small_height),
    position=(0.0, 0.0, card_box_height * 2.0),
    lid=_lid("Commuter", "purple", image=str(ASSETS / "commuter.svg"), logo_size_mm=14.0),
).compartment("Commuters", cut=FingerCut.SCOOP, component="Purple Commuters", count=11)

project.box(
    BoxType.CAP,
    "CommuterBoxSmall_Coral",
    size=(commuter_box_small_width, commuter_box_small_length, commuter_box_small_height),
    position=(0.0, commuter_box_small_length, card_box_height * 2.0),
    lid=_lid("Commuter", "coral", image=str(ASSETS / "commuter.svg"), logo_size_mm=14.0),
).compartment("Commuters", cut=FingerCut.SCOOP, component="Coral Commuters", count=11)

project.box(
    BoxType.NO_LID,
    "SpacerTop",
    size=(spacer_top_width, spacer_top_length, spacer_top_height),
    position=(0.0, commuter_box_small_length * 2.0, card_box_height * 2.0),
    hollow=True,
)

project.box(
    BoxType.NO_LID,
    "StartTokenBox",
    size=(start_token_box_width, start_token_box_length, start_token_box_height),
    position=(0.0, card_box_length * 2.0, 0.0),
    wall_thickness=2.0,
).compartment("StartToken", cut=FingerCut.SCOOP, component="Start Token", count=1)

# ── 4. Player Boxes (4, X=73..134.5, Z=0..39.4) ──────────────────
player_inner_w = player_box_width - wall_thickness * 2.0  # 55.5mm
player_inner_l = player_box_length - wall_thickness * 2.0  # 137.0mm
player_hex_depth = player_overlay_hex_per_player * player_overlay_hex_thickness / 2.0 + 1.0  # 14.5mm
player_hex_span = player_overlay_hex_radius * 2.0  # 64.086mm
player_elements: tuple[CompartmentElement, ...] = (
    CompartmentElement(
        shape=ElementShape.HEXAGON,
        size=(player_overlay_hex_width, player_overlay_hex_width),
        rotation=90.0,
        offset=(0.0, 0.0),
        depth=player_hex_depth,
        pull_out=False,
        label="TrackHexFront",
    ),
    CompartmentElement(
        shape=ElementShape.HEXAGON,
        size=(player_overlay_hex_width, player_overlay_hex_width),
        rotation=90.0,
        offset=(0.0, player_inner_l - player_hex_span),
        depth=player_hex_depth,
        pull_out=False,
        label="TrackHexBack",
    ),
    CompartmentElement(
        shape=ElementShape.ROUNDED_RECT,
        size=(train_width, train_length),
        offset=((player_inner_w - train_width) / 2.0, (player_inner_l - train_length) / 2.0),
        depth=train_thickness,
        corner_radius=2.0,
        bottom_rounding=2.0,
        pull_out=False,
        label="TrainSlot",
    ),
    CompartmentElement(
        shape=ElementShape.ROUNDED_RECT,
        size=(train_length, 20.0),
        offset=((player_inner_w - train_length) / 2.0, (player_inner_l - 20.0) / 2.0),
        depth=train_thickness,
        corner_radius=2.0,
        bottom_rounding=5.0,
        pull_out=False,
        label="TrainFingerRelief",
    ),
)

player_specs = [
    ("PlayerBox_green", "green", (card_box_width, 0.0, 0.0)),
    ("PlayerBox_deeppink", "deeppink", (card_box_width, player_box_length, 0.0)),
    ("PlayerBox_cyan", "cyan", (card_box_width, 0.0, player_box_height)),
    ("PlayerBox_darkorange", "darkorange", (card_box_width, player_box_length, player_box_height)),
]
for label, color_name, pos in player_specs:
    project.box(
        BoxType.SLIDING,
        label,
        size=(player_box_width, player_box_length, player_box_height),
        position=pos,
        lid=_lid(f"Player ({color_name.title()})", color_name),
        stackable=StackableMode.PYRAMIDS,
    ).compartment(
        "PlayerBits",
        size=(player_inner_w, player_inner_l),
        position=(0.0, 0.0),
        allocates={"Player Track Hexes": player_overlay_hex_per_player, "Player Trains": 1},
        elements=player_elements,
    )

# ── 5. Factory Station Hex Tile Boxes (6) + MetroTileBox + SpacerBox
factory_x0 = card_box_width + player_box_width  # 134.5mm
factory_inner_w = factory_box_width - wall_thickness * 2.0  # 69.75mm
factory_inner_l = factory_box_length - wall_thickness * 2.0  # 65.5mm
factory_hex_span = factory_hex_radius * 2.0  # 64.663mm
factory_hex_depth = factory_hex_thickness * 2.0  # 15.0mm
factory_elements: tuple[CompartmentElement, ...] = (
    CompartmentElement(
        shape=ElementShape.HEXAGON,
        size=(factory_hex_width, factory_hex_width),
        offset=((factory_inner_w - factory_hex_span) / 2.0, (factory_inner_l - factory_hex_width) / 2.0),
        depth=factory_hex_depth,
        pull_out=False,
        label="StationHex",
    ),
    CompartmentElement(
        shape=ElementShape.CIRCLE,
        size=(18.0, 18.0),
        offset=(factory_inner_w / 2.0 - 9.0, 0.0),
        depth=factory_hex_depth,
        pull_out=False,
        label="StationHexFingerBite",
    ),
)

factory_specs = [
    ("FactoryBox_Factories", "Factories", (factory_x0, 0.0, 0.0), "Factory Station Hexes"),
    ("FactoryBox_Warehouses", "Warehouses", (factory_x0 + factory_box_width, 0.0, 0.0), "Warehouse Station Hexes"),
    ("FactoryBox_Labs", "Labs", (factory_x0, factory_box_length, 0.0), "Lab Station Hexes"),
    (
        "FactoryBox_Offices",
        "Offices",
        (factory_x0 + factory_box_width, factory_box_length, 0.0),
        "Office Station Hexes",
    ),
    ("FactoryBox_Stores", "Stores", (factory_x0, 0.0, factory_box_height), "Store Station Hexes"),
    (
        "FactoryBox_Embassies",
        "Embassies",
        (factory_x0 + factory_box_width, 0.0, factory_box_height),
        "Embassy Station Hexes",
    ),
]
for label, title, pos, comp_name in factory_specs:
    project.box(
        BoxType.SLIDING,
        label,
        size=(factory_box_width, factory_box_length, factory_box_height),
        position=pos,
        lid=_lid(title, "goldenrod", image=str(ASSETS / "factory_hex.svg"), logo_size_mm=16.0),
    ).compartment(
        "StationHexes",
        size=(factory_inner_w, factory_inner_l),
        position=(0.0, 0.0),
        component=comp_name,
        count=2,
        elements=factory_elements,
    )

metro_inner_w = metro_box_width - wall_thickness * 2.0  # 145.5mm
metro_inner_l = metro_box_length - wall_thickness * 2.0  # 137.0mm
clover_cx = factory_hex_width  # 56.0mm
clover_cy = factory_hex_radius * 1.5  # 48.5mm
metro_elements: tuple[CompartmentElement, ...] = (
    # Tri-hex MetroTile clover (3 touching hexagons at 90°, 210°, 330°), depth = 7.5mm
    *(
        CompartmentElement(
            shape=ElementShape.HEXAGON,
            size=(factory_hex_width, factory_hex_width),
            rotation=90.0,
            offset=(
                clover_cx + factory_hex_radius * math.cos(math.radians(angle)) - factory_hex_width / 2.0,
                clover_cy + factory_hex_radius * math.sin(math.radians(angle)) - factory_hex_radius,
            ),
            depth=factory_hex_thickness,
            pull_out=False,
            label=f"MetroCloverHex_{idx + 1}",
        )
        for idx, angle in enumerate((90.0, 210.0, 330.0))
    ),
    # 4th single hex well in top-right corner, double depth = 15.0mm
    CompartmentElement(
        shape=ElementShape.HEXAGON,
        size=(factory_hex_width, factory_hex_width),
        rotation=90.0,
        offset=(metro_inner_w - factory_hex_width, metro_inner_l - factory_hex_span),
        depth=factory_hex_thickness * 2.0,
        pull_out=False,
        label="StudioHex",
    ),
)

project.box(
    BoxType.SLIDING,
    "MetroTileBox",
    size=(metro_box_width, metro_box_length, metro_box_height),
    position=(factory_x0, factory_box_length * 2.0, 0.0),
    lid=_lid("Metro & Studios", "darkorange"),
).compartment(
    "MetroTiles",
    size=(metro_inner_w, metro_inner_l),
    position=(0.0, 0.0),
    allocates={"Metro Hub Tile": 1, "Studio Station Hexes": 2},
    elements=metro_elements,
)

project.box(
    BoxType.NO_LID,
    "SpacerBox",
    size=(spacer_box_width, spacer_box_length, spacer_box_height),
    position=(factory_x0, factory_box_length, metro_box_height),
    hollow=True,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
