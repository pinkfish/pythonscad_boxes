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

ASSETS = (
    Path(__file__).resolve().parent / "assets"
    if "__file__" in globals()
    else ROOT / "boxes" / "railway_boom" / "assets"
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

cube_size = 8.5
train_length = 16.0
train_width = 9.0
train_height = 9.0
house_top_width = 13.0
house_length = 16.0
disc_diameter = 16.0
disc_thickness = 3.5
pentagon_width = 16.0
pentagon_length = 16.823
pentagon_thickness = 3.5

city_tile_width = 14.5
city_tile_length = 33.0
city_tile_thickness = 2.2

indicator_octagon_diameter = 17.318
indicator_octagon_length = 24.0

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
player_inner_w = player_box_width - wall_thickness * 2.0  # 97.5mm
player_inner_l = player_box_length - wall_thickness * 2.0  # 102.0mm


def _player_box_elements() -> tuple[CompartmentElement, ...]:
    """Build PlayerBox stepped wells: trains, 4 stations, L-cubes, disc & pentagon with bites."""
    elems: list[CompartmentElement] = [
        # Upper grab shelf over trains, stations & cubes
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(player_inner_w - train_length - 2.0, player_inner_l),
            offset=(0.0, 0.0),
            depth=4.0,
            corner_radius=3.0,
            pull_out=False,
            label="UpperShelfMain",
        ),
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(cube_size + 7.0, cube_size * 2.0 + 2.0),
            offset=(5.0 + cube_size * 3.0 + train_length * 3.0, 0.0),
            depth=4.0,
            corner_radius=3.0,
            pull_out=False,
            label="UpperShelfFrontRight",
        ),
        # Trains well (3x10 trains)
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(train_length * 3.0, train_width * 10.0),
            offset=(1.0, 7.0),
            depth=train_height + 0.5,
            pull_out=False,
            label="Trains",
        ),
        # Cubes main well (2x11 cubes) + 1-cube L-extension
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(cube_size * 2.0, cube_size * 11.0),
            offset=(train_length * 3.0 + 15.0, 5.0),
            depth=cube_size + 0.5,
            pull_out=False,
            label="CubesMain",
        ),
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(cube_size + 1.0, cube_size),
            offset=(train_length * 3.0 + 14.75 + cube_size * 2.0, 5.0),
            depth=cube_size + 0.5,
            pull_out=False,
            label="CubesExt",
        ),
    ]
    # 4 Station wells + finger channels between trains and cubes
    for i in range(4):
        elems.append(
            CompartmentElement(
                shape=ElementShape.ROUNDED_RECT,
                size=(house_top_width, house_length),
                offset=(train_length * 3.0 + 2.0, 8.0 + (house_length + 2.0) * i),
                depth=9.5,
                corner_radius=1.0,
                pull_out=False,
                label=f"Station_{i + 1}",
            )
        )
        elems.append(
            CompartmentElement(
                shape=ElementShape.ROUNDED_RECT,
                size=(house_top_width, house_length + 8.0),
                offset=(train_length * 3.0 + 2.0, 4.0 + (house_length + 2.0) * i),
                depth=5.0,
                corner_radius=3.0,
                pull_out=False,
                label=f"StationRelief_{i + 1}",
            )
        )
    # Disc well + 90°/270° finger bites (clamped strictly inside player_inner_w)
    disc_cx = min(17.5 + cube_size * 3.0 + train_length * 3.0, player_inner_w - disc_diameter / 2.0)
    disc_cy = train_width * 3.0 + 16.0
    disc_depth = disc_thickness + 0.5
    bite_d = 12.0
    elems.extend(
        [
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(disc_diameter, disc_diameter),
                offset=(disc_cx - disc_diameter / 2.0, disc_cy - disc_diameter / 2.0),
                depth=disc_depth,
                pull_out=False,
                label="Disc",
            ),
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(bite_d, bite_d),
                offset=(disc_cx - bite_d / 2.0, disc_cy + disc_diameter / 2.0 - bite_d / 2.0),
                depth=disc_depth,
                pull_out=False,
                label="DiscBiteTop",
            ),
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(bite_d, bite_d),
                offset=(disc_cx - bite_d / 2.0, disc_cy - disc_diameter / 2.0 - bite_d / 2.0),
                depth=disc_depth,
                pull_out=False,
                label="DiscBiteBottom",
            ),
        ]
    )
    # Pentagon well + 70°/290° finger bites
    pent_cx = min(16.5 + cube_size * 3.0 + train_length * 3.0, player_inner_w - pentagon_width / 2.0)
    pent_cy = train_width * 6.0 + 15.0
    pent_depth = pentagon_thickness + 0.5
    pent_bite_cx = min(pent_cx + 3.0, player_inner_w - bite_d / 2.0)
    elems.extend(
        [
            CompartmentElement(
                shape=ElementShape.SVG,
                shape_file=str(ASSETS / "pentagon.svg"),
                size=(pentagon_width, pentagon_length),
                offset=(pent_cx - pentagon_width / 2.0, pent_cy - pentagon_length / 2.0),
                depth=pent_depth,
                pull_out=False,
                label="Pentagon",
            ),
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(bite_d, bite_d),
                offset=(pent_bite_cx - bite_d / 2.0, pent_cy + 8.3 - bite_d / 2.0),
                depth=pent_depth,
                pull_out=False,
                label="PentagonBiteTop",
            ),
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(bite_d, bite_d),
                offset=(pent_bite_cx - bite_d / 2.0, pent_cy - 8.3 - bite_d / 2.0),
                depth=pent_depth,
                pull_out=False,
                label="PentagonBiteBottom",
            ),
        ]
    )
    return tuple(elems)


player_specs = [
    ("PlayerBox_Green", "green", (0.0, 0.0, 0.0)),
    ("PlayerBox_Blue", "blue", (0.0, 0.0, player_box_height)),
    ("PlayerBox_Red", "red", (player_box_width, 0.0, 0.0)),
    ("PlayerBox_Yellow", "yellow", (player_box_width, 0.0, player_box_height)),
]
for label, color_name, pos in player_specs:
    project.box(
        BoxType.CAP,
        label,
        size=(player_box_width, player_box_length, player_box_height),
        position=pos,
        lid=_lid(
            f"Player ({color_name.title()})",
            color_name,
            text_color="black" if color_name == "yellow" else "white",
        ),
    ).compartment(
        "PlayerBits",
        size=(player_inner_w, player_inner_l),
        position=(0.0, 0.0),
        elements=_player_box_elements(),
    )

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

tourist_inner_w = tourist_tile_box_width - 1.5 * 2.0  # 10.0mm
tourist_inner_l = tourist_tile_box_length - 1.5 * 2.0  # 70.0mm
tourist_inner_h = tourist_tile_box_height - floor_thickness - lid_thickness  # 32.0mm
project.box(
    BoxType.SLIDING,
    "TouristTileBox",
    size=(tourist_tile_box_width, tourist_tile_box_length, tourist_tile_box_height),
    position=(card_box_width * 2.0, y_row1, 0.0),
    wall_thickness=1.5,
    lid=_lid("Tourist", "seagreen"),
).compartment(
    "TouristTiles",
    size=(tourist_inner_w, tourist_inner_l),
    position=(0.0, 0.0),
    elements=(
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "city_tile.svg"),
            size=(city_tile_length, tourist_inner_w),
            rotation=90.0,
            offset=(0.0, (tourist_inner_l - city_tile_length) / 2.0),
            depth=tourist_inner_h,
            pull_out=False,
            label="TouristCityTile",
        ),
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(tourist_inner_w, 20.0),
            offset=(0.0, 0.0),
            depth=tourist_inner_h,
            corner_radius=3.0,
            pull_out=False,
            label="TouristFingerSlot",
        ),
    ),
)

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

city_inner_w = city_tile_box_width - wall_thickness * 2.0  # 46.0mm
city_inner_l = city_tile_box_length - wall_thickness * 2.0  # 46.0mm
city_inner_h = city_tile_box_height - floor_thickness - lid_thickness  # 24.0mm
city_side_depth = 3.0 * city_tile_thickness  # 6.6mm
city_elements: tuple[CompartmentElement, ...] = (
    *(
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "city_tile.svg"),
            size=(city_tile_length, city_tile_width),
            rotation=180.0,
            offset=(0.0, i * (city_tile_width + 1.0)),
            depth=city_inner_h,
            pull_out=False,
            label=f"CityTile_{i + 1}",
        )
        for i in range(3)
    ),
    CompartmentElement(
        shape=ElementShape.ROUNDED_RECT,
        size=(15.0, city_tile_width * 3.0),
        offset=(city_tile_length / 2.0 - 7.5, 0.0),
        depth=city_inner_h,
        corner_radius=7.0,
        pull_out=False,
        label="CityFingerChannel",
    ),
    CompartmentElement(
        shape=ElementShape.SVG,
        shape_file=str(ASSETS / "city_tile.svg"),
        size=(city_tile_length, city_tile_width),
        rotation=90.0,
        offset=(city_inner_w - city_tile_width, (city_inner_l - city_tile_length) / 2.0),
        depth=city_side_depth,
        pull_out=False,
        label="CityTileSide",
    ),
    CompartmentElement(
        shape=ElementShape.SPHERE_SCOOP,
        size=(10.0, 10.0),
        offset=(city_inner_w - city_tile_width / 2.0 - 6.0, (city_inner_l - city_tile_length) / 2.0 - 5.0),
        depth=city_side_depth,
        pull_out=False,
        label="CitySideScoopFront",
    ),
    CompartmentElement(
        shape=ElementShape.SPHERE_SCOOP,
        size=(10.0, 10.0),
        offset=(city_inner_w - city_tile_width / 2.0 - 6.0, (city_inner_l + city_tile_length) / 2.0 - 5.0),
        depth=city_side_depth,
        pull_out=False,
        label="CitySideScoopBack",
    ),
)
project.box(
    BoxType.SLIDING,
    "SmallCardBox_CityTiles",
    size=(city_tile_box_width, city_tile_box_length, city_tile_box_height),
    position=(small_card_box_width * 2.0, y_row2, 0.0),
    lid=_lid("City", "dimgray"),
).compartment(
    "CityTiles",
    size=(city_inner_w, city_inner_l),
    position=(0.0, 0.0),
    elements=city_elements,
)

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
indicator_inner_w = indicator_box_width - 1.5 * 2.0  # 74.272mm
indicator_inner_l = indicator_box_length - 1.5 * 2.0  # 11.0mm
indicator_elements: tuple[CompartmentElement, ...] = tuple(
    elem
    for i in range(4)
    for elem in (
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "octagon.svg"),
            size=(17.0, indicator_inner_l),
            offset=(1.5 + indicator_octagon_diameter * i, 0.0),
            depth=indicator_octagon_length,
            pull_out=False,
            label=f"Indicator_{i + 1}",
        ),
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(8.0, indicator_inner_l),
            offset=(1.5 + indicator_octagon_diameter * i + 4.5, 0.0),
            depth=indicator_octagon_length,
            corner_radius=3.0,
            pull_out=False,
            label=f"IndicatorFinger_{i + 1}",
        ),
    )
)
project.box(
    BoxType.SLIDING,
    "IndicatorBox",
    size=(indicator_box_width, indicator_box_length, indicator_box_height),
    position=(0.0, y_row4, 0.0),
    wall_thickness=1.5,
    lid=_lid("Indicators", "darkslategray"),
).compartment(
    "Indicators",
    size=(indicator_inner_w, indicator_inner_l),
    position=(0.0, 0.0),
    elements=indicator_elements,
)

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
