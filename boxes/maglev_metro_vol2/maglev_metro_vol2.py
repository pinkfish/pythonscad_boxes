#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Maglev Metro: Volume 2 expansion organizer.

Ports boxes/maglev_metro_vol2/maglev_metro_vol2.scad to the pyboxbuilder Project API.
Organizes all 18 boxes/trays: expansion cards, upgrade tiles, extra loop/outback
tiles, summon tiles, outback & ghost station hexes, metro tokens, 3 robot boxes,
3 nanobot boxes, 4 commuter boxes, and player/middle spacers.
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
    FingerCut,
    LabelFinial,
    LabelMode,
    LabelShape,
    LidBuilder,
    PatternBuilder,
    PatternType,
    Project,
    run,
)

ASSETS = (
    Path(__file__).resolve().parent / "assets"
    if "__file__" in globals()
    else ROOT / "boxes" / "maglev_metro_vol2" / "assets"
)

# ── Box & Board Dimensions (from maglev_metro_vol2.scad) ──────────
box_width = 286.0
box_length = 286.0
box_height = 65.0

player_board_length = 162.0
player_board_thickness = 2.5
game_board_thickness = 17.0
game_board_base_width = 242.0
game_board_base_thickness = 17.0

# Both main game boards (17mm + 17mm = 34mm) sit at Z = 31..65mm;
# 4 CommuterBoxes occupy the X = 0..44mm side strip beside the game board base (Z = 31..48mm).
board_reserve = game_board_thickness + game_board_base_thickness  # 34.0mm
usable_height = box_height - board_reserve  # 31.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 3.0

# ── Component Dimensions ──────────────────────────────────────────
factory_hex_width = 56.0
factory_hex_radius = factory_hex_width / math.sqrt(3.0)  # ~32.3316mm

upgrade_length = 42.0
upgrade_thickness = 3.5
upgrade_base_thickness = 1.5
robot_length = 18.5

card_width = 67.0
card_length = 90.0

# ── Derived Sub-Box Dimensions (exact .scad formulas) ─────────────
commuter_box_width = box_width - game_board_base_width  # 44.0mm
commuter_box_length = box_length / 4.0  # 71.5mm
commuter_box_height = game_board_base_thickness  # 17.0mm

extra_hex_boxes_width = box_width - factory_hex_radius * 3.5 - wall_thickness * 2.0  # ~166.84mm
extra_hex_boxes_length = wall_thickness * 2.0 + factory_hex_width * 2.0 + 4.0  # 122.0mm
extra_hex_boxes_height = (
    box_height - player_board_thickness * 4.0 - game_board_thickness - game_board_base_thickness
)  # 21.0mm

card_box_width = wall_thickness * 2.0 + card_width  # 73.0mm
card_box_length = wall_thickness * 2.0 + card_length  # 96.0mm
card_box_height = (
    floor_thickness + lid_thickness + upgrade_thickness * 3.0 - upgrade_base_thickness
)  # 14.0mm

upgrade_box_width = card_box_width  # 73.0mm
upgrade_box_length = upgrade_length * 3.0  # 126.0mm
upgrade_box_height = card_box_height  # 14.0mm

summon_box_width = extra_hex_boxes_width  # ~166.84mm
summon_box_length = box_length - extra_hex_boxes_length - upgrade_box_length  # 38.0mm
summon_box_height = upgrade_box_height  # 14.0mm

outback_ghost_tiles_box_width = wall_thickness + factory_hex_radius * 3.5  # ~116.16mm
outback_ghost_tiles_box_length = wall_thickness + factory_hex_width * 4.0  # 227.0mm
outback_ghost_tiles_box_height = usable_height  # 31.0mm

metro_token_box_width = outback_ghost_tiles_box_width  # ~116.16mm
metro_token_box_length = box_length - outback_ghost_tiles_box_length - 1.0  # 58.0mm
metro_token_box_height = usable_height  # 31.0mm

robot_box_width = extra_hex_boxes_width / 3.0  # ~55.61mm
robot_box_length = robot_length * 3.2 + 1.0 + wall_thickness * 2.0  # 66.2mm
robot_box_height = box_height - card_box_height - commuter_box_height - game_board_base_thickness  # 17.0mm

nanobot_box_width = robot_box_width  # ~55.61mm
nanobot_box_length = box_length - player_board_length - robot_box_length  # 57.8mm
nanobot_box_height = robot_box_height  # 17.0mm

player_board_spacer_width = extra_hex_boxes_width  # ~166.84mm
player_board_spacer_length = player_board_length - extra_hex_boxes_length - 1.0  # 39.0mm
player_board_spacer_height = extra_hex_boxes_height - card_box_height  # 7.0mm

middle_spacer_width = extra_hex_boxes_width - upgrade_box_width - card_box_width  # ~20.84mm
middle_spacer_length = upgrade_box_length  # 126.0mm
middle_spacer_height = card_box_height  # 14.0mm

project = Project(
    "MaglevMetroVol2",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_reserve,
    generate_spacers=True,
    box_defaults={"expandable": False},
)

# ── Game Component Inventory ──────────────────────────────────────
project.define_tile("Loop Tile", 1, bulk=True)
project.define_tile("Outback Small Tile", 1, bulk=True)
project.define_tile("Upgrade Tiles", 7, size=(upgrade_length, upgrade_length, upgrade_thickness), bulk=True)
project.define_cards("Expansion Cards", 16, size=(card_width, card_length), thickness=0.5)
project.define_tile("Summon Tiles", 4, bulk=True)
for _robot_name in ("Silver Robots", "Gold Robots", "Orange Robots"):
    project.define_piece(_robot_name, 18, bulk=True)
project.define_piece("Nanobots", 48, bulk=True)
project.define_tile("Outback Hex Tiles", 4, size=(factory_hex_width, factory_hex_width), bulk=True)
project.define_tile("Ghost Hex Tiles", 4, size=(factory_hex_width, factory_hex_width), bulk=True)
project.define_piece("Metro Tickets", 24, bulk=True)
for _commuter_name, _commuter_qty in (
    ("Pink Commuters", 14),
    ("Aqua Commuters", 14),
    ("Coral Commuters", 11),
    ("Purple Commuters", 11),
):
    project.define_piece(_commuter_name, _commuter_qty, bulk=True)
project.component("Map Boards", 3, kind="board")
project.component("Game Board Bases", 2, kind="board")
project.component("Player Boards", 4, kind="board")

project.board(
    "Map Boards",
    size=(280.0, 281.0, game_board_thickness),
    position=(box_width - 280.0, 0.0, box_height - game_board_thickness),
    count=3,
    component="Map Boards",
)
project.board(
    "Game Board Bases",
    size=(game_board_base_width, 272.0, game_board_base_thickness),
    position=(box_width - game_board_base_width, 0.0, usable_height),
    count=2,
    component="Game Board Bases",
)
project.board(
    "Player Boards",
    size=(145.0, player_board_length, player_board_thickness * 4.0),
    position=(0.0, 0.0, extra_hex_boxes_height),
    count=4,
    component="Player Boards",
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


# ── 1. Bottom Layer (Left Region: X=0..166.84, Z=0..14/21) ───────
project.box(
    BoxType.CAP,
    "ExtraTilesBox",
    size=(extra_hex_boxes_width, extra_hex_boxes_length, extra_hex_boxes_height),
    position=(0.0, 0.0, 0.0),
    lid=_lid("Tiles", "darkorange"),
).compartment(
    "LoopAndOutbackTiles",
    cut=FingerCut.SCOOP,
    allocates={"Loop Tile": 1, "Outback Small Tile": 1},
)

u_box = project.box(
    BoxType.CAP,
    "UpgradeTileBox",
    size=(upgrade_box_width, upgrade_box_length, upgrade_box_height),
    position=(0.0, extra_hex_boxes_length, 0.0),
    lid=_lid("Upgrades", "seagreen"),
)
for slot, upgrade_count in enumerate((3, 2, 2)):
    u_box.compartment(
        f"Upgrade_{slot + 1}",
        length_ratio=1.0 / 3.0,
        cut=FingerCut.SCOOP,
        component="Upgrade Tiles",
        count=upgrade_count,
    )

project.box(
    BoxType.SLIDING,
    "ExpansionCardsBox",
    size=(card_box_width, card_box_length, card_box_height),
    position=(upgrade_box_width, extra_hex_boxes_length, 0.0),
    lid=_lid("Maps 2", "darkorange"),
).compartment("Cards", cut=FingerCut.SCOOP, component="Expansion Cards", count=16)

project.box(
    BoxType.NO_LID,
    "MiddleBoxSpacer",
    size=(middle_spacer_width, middle_spacer_length, middle_spacer_height),
    position=(upgrade_box_width + card_box_width, extra_hex_boxes_length, 0.0),
    hollow=True,
)

s_box = project.box(
    BoxType.CAP,
    "SummonBox",
    size=(summon_box_width, summon_box_length, summon_box_height),
    position=(0.0, extra_hex_boxes_length + upgrade_box_length, 0.0),
    lid=_lid("Summons", "purple", image=str(ASSETS / "ghost.svg"), logo_size_mm=14.0),
)
s_box.compartment("Summon_1", width_ratio=0.5, cut=FingerCut.SCOOP, component="Summon Tiles", count=2)
s_box.compartment("Summon_2", width_ratio=0.5, cut=FingerCut.SCOOP, component="Summon Tiles", count=2)

# ── 2. Upper Layer (Left Region: Z=14..21/31) ────────────────────
project.box(
    BoxType.NO_LID,
    "PlayerBoxSpacer",
    size=(player_board_spacer_width, player_board_spacer_length, player_board_spacer_height),
    position=(0.0, extra_hex_boxes_length, card_box_height),
    hollow=True,
)

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
        position=(robot_box_width * idx, player_board_length, card_box_height),
        lid=_lid("Robots", color_name, image=str(ASSETS / "robot.svg"), logo_size_mm=15.0),
    ).compartment("Robots", cut=FingerCut.SCOOP, component=comp_name, count=18)

nanobot_specs = [
    ("NanobotBox_1", "darkorange", 0),
    ("NanobotBox_2", "teal", 1),
    ("NanobotBox_3", "royalblue", 2),
]
for label, color_name, idx in nanobot_specs:
    project.box(
        BoxType.CAP,
        label,
        size=(nanobot_box_width, nanobot_box_length, nanobot_box_height),
        position=(nanobot_box_width * idx, player_board_length + robot_box_length, card_box_height),
        lid=_lid("Nanobots", color_name, image=str(ASSETS / "robot.svg"), logo_size_mm=14.0),
    ).compartment("Nanobots", cut=FingerCut.SCOOP, component="Nanobots", count=16)

# ── 3. Right Column: Outback & Ghost Hexes + Metro Tokens ────────
t_box = project.box(
    BoxType.NO_LID,
    "OutbackGhostTilesBox",
    size=(outback_ghost_tiles_box_width, outback_ghost_tiles_box_length, outback_ghost_tiles_box_height),
    position=(extra_hex_boxes_width, 0.0, 0.0),
)
t_box.compartment("OutbackHexes", width_ratio=0.5, cut=FingerCut.SCOOP, component="Outback Hex Tiles", count=4)
t_box.compartment("GhostHexes", width_ratio=0.5, cut=FingerCut.SCOOP, component="Ghost Hex Tiles", count=4)

project.box(
    BoxType.CAP,
    "MetroTokenBox",
    size=(metro_token_box_width, metro_token_box_length, metro_token_box_height),
    position=(extra_hex_boxes_width, outback_ghost_tiles_box_length, 0.0),
    lid=_lid("Metro", "royalblue"),
).compartment("MetroTickets", cut=FingerCut.SCOOP, component="Metro Tickets", count=24)

# ── 4. Side-of-Board Strip: 4 Commuter Boxes (X=0..44, Z=31..48) ─
commuter_specs = [
    ("CommuterBox_Pink", "pink", 0, "Pink Commuters", 14),
    ("CommuterBox_Aqua", "aqua", 1, "Aqua Commuters", 14),
    ("CommuterBox_Coral", "coral", 2, "Coral Commuters", 11),
    ("CommuterBox_Purple", "purple", 3, "Purple Commuters", 11),
]
for label, color_name, idx, comp_name, qty in commuter_specs:
    project.box(
        BoxType.CAP,
        label,
        size=(commuter_box_width, commuter_box_length, commuter_box_height),
        position=(0.0, commuter_box_length * idx, usable_height),
        lid=_lid("Commuter", color_name, image=str(ASSETS / "commuter.svg"), logo_size_mm=14.0),
    ).compartment("Commuters", cut=FingerCut.SCOOP, component=comp_name, count=qty)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
