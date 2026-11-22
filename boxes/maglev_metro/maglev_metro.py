#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Maglev Metro board game organizer.

Ports boxes/maglev_metro/maglev_metro.scad to the pyboxbuilder Project API.
Organizes all 25 boxes/trays: 4 card boxes, 3 robot boxes, 2 commuter boxes,
2 small commuter boxes, start token box, 4 player boxes, 6 factory station
hex boxes, metro & studios tile box, and top/side spacers.
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
    StackableMode,
    run,
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
player_overlay_hex_width = 55.5
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

METRO_PATTERN = PatternBuilder(PatternType.DENSE_HEX)


def _lid(text: str, frame_color: str) -> LidBuilder:
    return LidBuilder(
        text=text,
        label_mode=LabelMode.FRAMED,
        pattern=METRO_PATTERN,
        text_color=Color("white"),
        frame_color=Color(frame_color),
    )


# ── 1. Card Boxes (4, stacked 2x2 at X=0..73, Y=0..192) ──────────
card_specs = [
    ("CardBox_Connections", "Connection", (0.0, 0.0, 0.0)),
    ("CardBox_Tracks", "Track", (0.0, 0.0, card_box_height)),
    ("CardBox_Passengers", "Passenger", (0.0, card_box_length, 0.0)),
    ("CardBox_PlayerObjectives", "Player Board", (0.0, card_box_length, card_box_height)),
]
for label, title, pos in card_specs:
    project.box(
        BoxType.SLIDING,
        label,
        size=(card_box_width, card_box_length, card_box_height),
        position=pos,
        lid_thickness=4.0,
        lid=_lid(title, "royalblue"),
        stackable=StackableMode.PYRAMIDS,
    ).compartment("Cards", cut=FingerCut.SCOOP)

# ── 2. Robot & Commuter Boxes (X=10..73, Y=192..286) ─────────────
robot_specs = [
    ("RobotBox_Silver", "silver", 0),
    ("RobotBox_Gold", "gold", 1),
    ("RobotBox_Orange", "orange", 2),
]
for label, color_name, idx in robot_specs:
    project.box(
        BoxType.CAP,
        label,
        size=(robot_box_width, robot_box_length, robot_box_height),
        position=(start_token_box_width, card_box_length * 2.0, robot_box_height * idx),
        lid=_lid("Robots", color_name),
    ).compartment("Robots", cut=FingerCut.SCOOP)

commuter_specs = [
    ("CommuterBox_Pink", "pink", 0),
    ("CommuterBox_Aqua", "aqua", 1),
]
for label, color_name, idx in commuter_specs:
    project.box(
        BoxType.CAP,
        label,
        size=(commuter_box_width, commuter_box_length, commuter_box_height),
        position=(
            start_token_box_width,
            card_box_length * 2.0 + commuter_box_length * idx,
            robot_box_height * 3.0,
        ),
        lid=_lid("Commuter", color_name),
    ).compartment("Commuters", cut=FingerCut.SCOOP)

# ── 3. Side-of-Board Strip (X=0..45, Z=47.8..65.0) + StartTokenBox
project.box(
    BoxType.CAP,
    "CommuterBoxSmall_Purple",
    size=(commuter_box_small_width, commuter_box_small_length, commuter_box_small_height),
    position=(0.0, 0.0, card_box_height * 2.0),
    lid=_lid("Commuter", "purple"),
).compartment("Commuters", cut=FingerCut.SCOOP)

project.box(
    BoxType.CAP,
    "CommuterBoxSmall_Coral",
    size=(commuter_box_small_width, commuter_box_small_length, commuter_box_small_height),
    position=(0.0, commuter_box_small_length, card_box_height * 2.0),
    lid=_lid("Commuter", "coral"),
).compartment("Commuters", cut=FingerCut.SCOOP)

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
).compartment("StartToken", cut=FingerCut.SCOOP)

# ── 4. Player Boxes (4, X=73..134.5, Z=0..39.4) ──────────────────
player_specs = [
    ("PlayerBox_green", "green", (card_box_width, 0.0, 0.0)),
    ("PlayerBox_deeppink", "deeppink", (card_box_width, player_box_length, 0.0)),
    ("PlayerBox_cyan", "cyan", (card_box_width, 0.0, player_box_height)),
    ("PlayerBox_darkorange", "darkorange", (card_box_width, player_box_length, player_box_height)),
]
for label, color_name, pos in player_specs:
    p_box = project.box(
        BoxType.SLIDING,
        label,
        size=(player_box_width, player_box_length, player_box_height),
        position=pos,
        lid=_lid(f"Player ({color_name.title()})", color_name),
        stackable=StackableMode.PYRAMIDS,
    )
    p_box.compartment("TrackHexes", length_ratio=0.6, cut=FingerCut.SCOOP)
    p_box.compartment("TrainsAndBits", length_ratio=0.4, cut=FingerCut.SCOOP)

# ── 5. Factory Station Hex Tile Boxes (6) + MetroTileBox + SpacerBox
factory_x0 = card_box_width + player_box_width  # 134.5mm
factory_specs = [
    ("FactoryBox_Factories", "Factories", (factory_x0, 0.0, 0.0)),
    ("FactoryBox_Warehouses", "Warehouses", (factory_x0 + factory_box_width, 0.0, 0.0)),
    ("FactoryBox_Labs", "Labs", (factory_x0, factory_box_length, 0.0)),
    ("FactoryBox_Offices", "Offices", (factory_x0 + factory_box_width, factory_box_length, 0.0)),
    ("FactoryBox_Stores", "Stores", (factory_x0, 0.0, factory_box_height)),
    ("FactoryBox_Embassies", "Embassies", (factory_x0 + factory_box_width, 0.0, factory_box_height)),
]
for label, title, pos in factory_specs:
    project.box(
        BoxType.SLIDING,
        label,
        size=(factory_box_width, factory_box_length, factory_box_height),
        position=pos,
        lid=_lid(title, "goldenrod"),
    ).compartment("StationHexes", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "MetroTileBox",
    size=(metro_box_width, metro_box_length, metro_box_height),
    position=(factory_x0, factory_box_length * 2.0, 0.0),
    lid=_lid("Metro & Studios", "darkorange"),
).compartment("MetroTiles", cut=FingerCut.SCOOP)

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
