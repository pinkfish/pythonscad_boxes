#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Railway Boom board game organizer.

Ports boxes/railway_boom/railway_boom.scad to the pyboxbuilder Project API.
Organizes all 21 boxes/trays: 4 player boxes, Station/Objective/Route standard
card boxes, Carriage/Locomotive/Development (x2) small card boxes, City &
Tourist tile boxes, 4 stacked resource boxes (Materials/VP/Tech/Coal), Money
box, Indicator box, and Front/Player-board spacers.
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
    run,
)

# ── Box & Board Dimensions (from railway_boom.scad) ───────────────
box_width = 209.0
box_length = 300.0
box_height = 46.0

board_thickness = 10.0
player_board_thickness = 2.0
player_board_width = 161.0
player_board_num = 4

# Main board (10mm) sits at Z = 36..46mm; 4 player boards (8mm) sit at X=0..161, Y=0..228, Z=28..36mm.
full_usable_height = box_height - board_thickness  # 36.0mm
usable_height = full_usable_height - player_board_num * player_board_thickness  # 28.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

# ── Component Dimensions ──────────────────────────────────────────
card_width = 67.0
card_length = 92.0
single_card_thickness = 14.0 / 20.0  # 0.7mm
objective_cards = 18

small_card_width = 46.0
small_card_length = 66.0

indicator_octagon_diameter = 17.318

# ── Derived Sub-Box Dimensions (exact .scad formulas) ─────────────
player_box_width = (box_width - 2.0) / 2.0  # 103.5mm
player_box_length = 108.0
player_box_height = usable_height / 2.0  # 14.0mm

card_box_width = card_length + wall_thickness * 2.0  # 98.0mm
card_box_length = card_width + wall_thickness * 2.0  # 73.0mm
station_card_box_height = usable_height  # 28.0mm
objective_card_box_height = (
    single_card_thickness * objective_cards + floor_thickness + lid_thickness + 1.0
)  # 17.6mm
route_card_box_height = usable_height - objective_card_box_height - 0.5  # 9.9mm

small_card_box_width = small_card_length + wall_thickness * 2.0  # 72.0mm
small_card_box_length = small_card_width + wall_thickness * 2.0  # 52.0mm
development_card_box_height = full_usable_height  # 36.0mm

city_tile_box_width = card_box_width * 2.0 - small_card_box_width * 2.0  # 52.0mm
city_tile_box_length = small_card_box_length  # 52.0mm
city_tile_box_height = usable_height  # 28.0mm

tourist_tile_box_width = box_width - 2.0 * card_box_width  # 13.0mm
tourist_tile_box_length = card_box_length  # 73.0mm
tourist_tile_box_height = full_usable_height  # 36.0mm

resource_box_width = box_width - 2.0 * small_card_box_width  # 65.0mm
resource_box_length = (
    box_length - player_box_length - card_box_length - small_card_box_length
) / 2.0  # 33.5mm
resource_box_height = full_usable_height / 2.0  # 18.0mm

indicator_box_width = indicator_octagon_diameter * 4.0 + wall_thickness * 2.0 + 2.0  # 77.272mm
indicator_box_length = (
    box_length - player_box_length - card_box_length - small_card_box_length * 2.0 - 1.0
)  # 14.0mm
indicator_box_height = full_usable_height  # 36.0mm

money_box_width = small_card_box_width * 2.0 - indicator_box_width  # 66.728mm
money_box_length = indicator_box_length  # 14.0mm
money_box_height = full_usable_height  # 36.0mm

spacer_front_width = tourist_tile_box_width  # 13.0mm
spacer_front_length = small_card_box_length  # 52.0mm
spacer_front_height = full_usable_height  # 36.0mm

spacer_player_board_width = box_width - player_board_width - 1.0  # 47.0mm
spacer_player_board_length = player_box_length  # 108.0mm
spacer_player_board_height = player_board_thickness * player_board_num  # 8.0mm

project = Project(
    "RailwayBoom",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
    box_defaults={"expandable": False},
)

BOOM_PATTERN = PatternBuilder(PatternType.DENSE_HEX)


def _lid(text: str, frame_color: str, text_color: str = "white") -> LidBuilder:
    return LidBuilder(
        text=text,
        label_mode=LabelMode.FRAMED,
        pattern=BOOM_PATTERN,
        text_color=Color(text_color),
        frame_color=Color(frame_color),
    )


# ── 1. Row 0 (Y = 0..108): 4 Player Boxes + Player-Board Spacer ──
player_specs = [
    ("PlayerBox_Green", "green", (0.0, 0.0, 0.0)),
    ("PlayerBox_Blue", "blue", (0.0, 0.0, player_box_height)),
    ("PlayerBox_Red", "red", (player_box_width, 0.0, 0.0)),
    ("PlayerBox_Yellow", "yellow", (player_box_width, 0.0, player_box_height)),
]
for label, color_name, pos in player_specs:
    p_box = project.box(
        BoxType.CAP,
        label,
        size=(player_box_width, player_box_length, player_box_height),
        position=pos,
        lid=_lid(
            f"Player ({color_name.title()})",
            color_name,
            text_color="black" if color_name == "yellow" else "white",
        ),
    )
    p_box.compartment("TrainsAndStations", width_ratio=0.6, cut=FingerCut.SCOOP)
    p_box.compartment("CubesAndDiscs", width_ratio=0.4, cut=FingerCut.SCOOP)

project.box(
    BoxType.NO_LID,
    "SpacerPlayerBoardBox",
    size=(spacer_player_board_width, spacer_player_board_length, spacer_player_board_height),
    position=(player_board_width, 0.0, usable_height),
    hollow=True,
)

# ── 2. Row 1 (Y = 108..181): Station, Objective, Route Cards & Tourist Tiles
y_row1 = player_box_length  # 108.0mm
project.box(
    BoxType.SLIDING,
    "StationCardBox",
    size=(card_box_width, card_box_length, station_card_box_height),
    position=(0.0, y_row1, 0.0),
    lid=_lid("Stations", "navy"),
).compartment("StationCards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "ObjectiveCardBox",
    size=(card_box_width, card_box_length, objective_card_box_height),
    position=(card_box_width, y_row1, 0.0),
    lid=_lid("Objectives", "darkorange"),
).compartment("ObjectiveCards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "RouteCardBox",
    size=(card_box_width, card_box_length, route_card_box_height),
    position=(card_box_width, y_row1, objective_card_box_height),
    lid=_lid("Routes", "teal"),
).compartment("RouteCards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "TouristTileBox",
    size=(tourist_tile_box_width, tourist_tile_box_length, tourist_tile_box_height),
    position=(card_box_width * 2.0, y_row1, 0.0),
    wall_thickness=1.5,
    lid=_lid("Tourist", "seagreen"),
).compartment("TouristTiles", cut=FingerCut.SCOOP)

# ── 3. Row 2 (Y = 181..233): Carriages, Locomotives, City Tiles & Front Spacer
y_row2 = y_row1 + card_box_length  # 181.0mm
project.box(
    BoxType.SLIDING,
    "SmallCardBox_Carriages",
    size=(small_card_box_width, small_card_box_length, usable_height),
    position=(0.0, y_row2, 0.0),
    lid=_lid("Carriages", "peru"),
).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "SmallCardBox_Locomotives",
    size=(small_card_box_width, small_card_box_length, usable_height),
    position=(small_card_box_width, y_row2, 0.0),
    lid=_lid("Locomotives", "darkred"),
).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "SmallCardBox_CityTiles",
    size=(city_tile_box_width, city_tile_box_length, city_tile_box_height),
    position=(small_card_box_width * 2.0, y_row2, 0.0),
    lid=_lid("City", "dimgray"),
).compartment("CityTiles", cut=FingerCut.SCOOP)

project.box(
    BoxType.NO_LID,
    "FrontSpacerBox",
    size=(spacer_front_width, spacer_front_length, spacer_front_height),
    position=(small_card_box_width * 2.0 + city_tile_box_width, y_row2, 0.0),
    hollow=True,
)

# ── 4. Row 3 (Y = 233..300): Development Cards (x2) & 4 Resource Boxes
y_row3 = y_row2 + small_card_box_length  # 233.0mm
project.box(
    BoxType.SLIDING,
    "DevelopmentCardBox_1",
    size=(small_card_box_width, small_card_box_length, development_card_box_height),
    position=(0.0, y_row3, 0.0),
    lid=_lid("Development", "royalblue"),
).compartment("DevelopmentCards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "DevelopmentCardBox_2",
    size=(small_card_box_width, small_card_box_length, development_card_box_height),
    position=(small_card_box_width, y_row3, 0.0),
    lid=_lid("Development", "royalblue"),
).compartment("DevelopmentCards", cut=FingerCut.SCOOP)

resource_specs = [
    ("ResourceBox_Materials", "Materials", "saddlebrown", (small_card_box_width * 2.0, y_row3, 0.0)),
    ("ResourceBox_VP", "VP", "blue", (small_card_box_width * 2.0, y_row3, resource_box_height)),
    (
        "ResourceBox_Tech",
        "Tech",
        "purple",
        (small_card_box_width * 2.0, y_row3 + resource_box_length, 0.0),
    ),
    (
        "ResourceBox_Coal",
        "Coal",
        "black",
        (small_card_box_width * 2.0, y_row3 + resource_box_length, resource_box_height),
    ),
]
for label, title, color_name, pos in resource_specs:
    project.box(
        BoxType.CAP,
        label,
        size=(resource_box_width, resource_box_length, resource_box_height),
        position=pos,
        lid=_lid(title, color_name),
    ).compartment(title, cut=FingerCut.SCOOP)

# ── 5. Row 4 (Y = 285..299): Indicator Box & Money Box ───────────
y_row4 = y_row3 + small_card_box_length  # 285.0mm
project.box(
    BoxType.SLIDING,
    "IndicatorBox",
    size=(indicator_box_width, indicator_box_length, indicator_box_height),
    position=(0.0, y_row4, 0.0),
    wall_thickness=1.5,
    lid=_lid("Indicators", "darkslategray"),
).compartment("Indicators", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIPOVER,
    "ResourceBox_Money",
    size=(money_box_width, money_box_length, money_box_height),
    position=(indicator_box_width, y_row4, 0.0),
    wall_thickness=1.5,
    lid=_lid("Money", "darkorange"),
).compartment("Money", cut=FingerCut.SCOOP)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
