#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""March of the Ants board game organizer.

Ports boxes/march_of_the_ants/march_of_the_ants.scad to the pyboxbuilder Project API.
Organizes base territory hexes, Minions of the Meadow hexes, base & expansion
sleeved evolution cards, food/centipede/day-night tokens, predator meeples,
5 player ant colony boxes, and the aphid box.
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
    run,
)

ASSETS = (
    Path(__file__).resolve().parent / "assets"
    if "__file__" in globals()
    else ROOT / "boxes" / "march_of_the_ants" / "assets"
)

# ── Box & Board Dimensions ────────────────────────────────────────
box_width = 195.0
box_length = 275.0
box_height = 65.0

board_thickness = 6.0
usable_height = box_height - board_thickness  # 59.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

# ── Component Dimensions (matching march_of_the_ants.scad) ────────
tile_thickness = 2.0
tile_width = 84.0
tile_radius = tile_width / 2.0 / math.cos(math.radians(30.0))  # 48.497mm

food_token_num = 30
food_token_thickness = 3.5

sleeved_card_width = 66.0
sleeved_card_length = 91.0
twenty_sleeved_cards_thickness = 8.5
total_cards = 66
num_mm_cards = 36 + 5 + 8  # 49
num_mm_hex = 1 + 1 + 4  # 6

# ── Sub-Box Dimensions ────────────────────────────────────────────
tile_box_width = box_width - 1.0  # 194.0mm
tile_box_length = (tile_radius * 2.0 + 0.5) + wall_thickness * 2.0  # 103.495mm
tile_box_height = usable_height  # 59.0mm

card_box_width = sleeved_card_width + 1.0 + wall_thickness * 2.0  # 73.0mm
card_box_length = sleeved_card_length + 1.0 + wall_thickness * 2.0  # 98.0mm
card_box_height = twenty_sleeved_cards_thickness * total_cards / 20.0 + lid_thickness * 2.0 + 1.0  # 33.05mm
mm_card_box_height = (
    twenty_sleeved_cards_thickness * num_mm_cards / 20.0 + lid_thickness * 2.0 + 0.75
)  # 25.575mm

mm_box_width = box_width - card_box_width - 1.0  # 121.0mm
mm_box_length = card_box_length  # 98.0mm
mm_box_height = tile_thickness * num_mm_hex + lid_thickness * 2.0  # 16.0mm

food_box_width = mm_box_width  # 121.0mm
food_box_length = mm_box_length  # 98.0mm
food_box_height = food_token_num / 6.0 * food_token_thickness + wall_thickness * 2.0  # 23.5mm

predator_box_width = mm_box_width  # 121.0mm
predator_box_length = mm_box_length  # 98.0mm
predator_box_height = usable_height - food_box_height - mm_box_height - 1.0  # 18.5mm

player_box_width = (box_width - 1.0) / 2.0  # 97.0mm
player_box_length = box_length - tile_box_length - card_box_length - 1.0  # 72.505mm
player_box_height = usable_height / 3.0  # 19.667mm

project = Project(
    "MarchOfTheAnts",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
    box_defaults={"expandable": False},
)

project.define_inventory({
    "Territory Hex Tiles": 25,
    "Base Evolution Cards": total_cards,
    "Minions Expansion Cards": num_mm_cards,
    "Minions Expansion Hex Tiles": num_mm_hex,
    "Food Tokens": food_token_num,
    "Centipede Tokens": 15,
    "Day/Night Token": 1,
    "Active Player Leaf": 1,
    "Predator Meeples": 5,
    "Ant Cubes": 36 * 5,
    "Player Marker Discs": 5,
    "Major Workers": 5,
    "Major Worker Tokens": 15,
    "Aphid Tokens": 36,
    "Score Track Board": 1,
    "Player Helper Boards": 5,
    "Rulebook": 1,
})

project.board(
    "Score Track, Helper Boards & Rules",
    size=(box_width, box_length, board_thickness),
    position=(0.0, 0.0, usable_height),
    count=7,
    allocates={
        "Score Track Board": 1,
        "Player Helper Boards": 5,
        "Rulebook": 1,
    },
)

ANT_PATTERN = PatternBuilder(PatternType.VORONOI)
ANT_FONT = "Futura:style=Bold"


def _ant_lid(
    text: str,
    frame_color: str,
    *,
    shape: LabelShape = LabelShape.CHAMFERED,
    logo_file: str | None = None,
    logo_size: float = 16.0,
) -> LidBuilder:
    text_color = "black" if frame_color == "gold" else "white"
    return LidBuilder(
        text=text,
        label_mode=LabelMode.FRAMED,
        label_shape=shape,
        label_finial=LabelFinial.CHEVRON,
        font=ANT_FONT,
        pattern=ANT_PATTERN,
        text_color=Color(text_color),
        frame_color=Color(frame_color),
        logo=str(ASSETS / logo_file) if logo_file is not None else None,
        logo_color=Color(text_color) if logo_file is not None else None,
        logo_position="left" if logo_file is not None else None,
        label_logo_size_mm=logo_size if logo_file is not None else None,
    )

# ── Row 0: Territory Hex Tiles Box (Y = 0 .. 103.5) ───────────────
tile_inner_width = tile_box_width - wall_thickness * 2.0  # 188.0mm
tile_inner_length = tile_box_length - wall_thickness * 2.0  # 97.495mm
tile_inner_height = tile_box_height - floor_thickness - lid_thickness  # 55.0mm


def _tile_box_elements() -> tuple[CompartmentElement, ...]:
    """Build 2 large hex tile wells + 4 corner finger bites + center trough."""
    elems: list[CompartmentElement] = []
    hex_w = tile_width + 0.4  # 84.4mm flat-to-flat -> 97.457mm point-to-point <= 97.495mm
    hex_h = hex_w / math.cos(math.radians(30.0))
    hex_y = (tile_inner_length - hex_h) / 2.0
    bite_d = 26.0  # r = 13mm
    centers_x = (8.0 + tile_width / 2.0, 8.0 + tile_width * 1.5 + 3.0)
    for idx, cx in enumerate(centers_x):
        elems.append(
            CompartmentElement(
                shape=ElementShape.HEXAGON,
                size=(hex_w, hex_w),
                rotation=30.0,
                offset=(cx - hex_w / 2.0, hex_y),
                depth=tile_inner_height,
                pull_out=False,
                label=f"HexTileStack_{idx + 1}",
            )
        )
        # Two diagonal finger bites per hex stack
        for b_idx, (bx, by) in enumerate(
            (
                (cx + tile_width / 4.0, tile_inner_length / 2.0 + tile_radius * 0.75),
                (cx - tile_width / 4.0, tile_inner_length / 2.0 - tile_radius * 0.75),
            )
        ):
            clamped_x = max(bite_d / 2.0, min(tile_inner_width - bite_d / 2.0, bx))
            clamped_y = max(bite_d / 2.0, min(tile_inner_length - bite_d / 2.0, by))
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(bite_d, bite_d),
                    offset=(clamped_x - bite_d / 2.0, clamped_y - bite_d / 2.0),
                    depth=tile_inner_height,
                    bottom_rounding=6.0,
                    pull_out=False,
                    label=f"HexTileBite_{idx + 1}_{b_idx + 1}",
                )
            )
    # Center finger access trough between the two hex stacks
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(30.0, tile_width / 2.0),
            offset=(8.0 + tile_width - 14.0, tile_radius * 4.0 / 7.0),
            corner_radius=5.0,
            depth=tile_inner_height,
            pull_out=False,
            label="HexTileCenterTrough",
        )
    )
    return tuple(elems)


project.box(
    BoxType.CAP,
    "HexTileBox",
    size=(tile_box_width, tile_box_length, tile_box_height),
    position=(0.0, 0.0, 0.0),
    lid=_ant_lid("Tiles", "saddlebrown", shape=LabelShape.HEXAGON),
).compartment(
    "HexTiles",
    size=(tile_inner_width, tile_inner_length),
    position=(0.0, 0.0),
    component="Territory Hex Tiles",
    count=25,
    elements=_tile_box_elements(),
)

# ── Row 1: Cards, Minions Hexes, Food & Predators (Y = 103.5 .. 201.5) ──
row1_y = tile_box_length

project.box(
    BoxType.CAP,
    "CardBox_Base",
    size=(card_box_width, card_box_length, card_box_height),
    position=(0.0, row1_y, 0.0),
    lid=_ant_lid("Cards", "royalblue"),
).compartment("Cards", cut=FingerCut.SCOOP, component="Base Evolution Cards", count=total_cards)

project.box(
    BoxType.CAP,
    "CardBox_Expansion",
    size=(card_box_width, card_box_length, mm_card_box_height),
    position=(0.0, row1_y, card_box_height),
    lid=_ant_lid("Minions Cards", "purple"),
).compartment("Cards", cut=FingerCut.SCOOP, component="Minions Expansion Cards", count=num_mm_cards)

mm_inner_width = mm_box_width - wall_thickness * 2.0  # 115.0mm
mm_inner_length = mm_box_length - wall_thickness * 2.0  # 92.0mm
mm_inner_height = mm_box_height - floor_thickness - lid_thickness  # 12.0mm


def _mm_hex_elements() -> tuple[CompartmentElement, ...]:
    """Build 1 rotated hex tile well + 2 diagonal finger scoops."""
    hex_w = tile_width + 0.5  # 84.5mm flat-to-flat (Y) -> 97.57mm point-to-point (X)
    hex_x_span = hex_w / math.cos(math.radians(30.0))
    cx = mm_inner_width / 2.0
    cy = mm_inner_length / 2.0
    bite_d = 24.0
    return (
        CompartmentElement(
            shape=ElementShape.HEXAGON,
            size=(hex_w, hex_w),
            rotation=0.0,
            offset=(cx - hex_x_span / 2.0, cy - hex_w / 2.0),
            depth=mm_inner_height,
            pull_out=False,
            label="ExpansionHexStack",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(bite_d, bite_d),
            offset=(
                min(mm_inner_width - bite_d, cx + tile_radius * 0.75 - bite_d / 2.0),
                min(mm_inner_length - bite_d, cy + tile_width / 4.0 - bite_d / 2.0),
            ),
            depth=mm_inner_height,
            pull_out=False,
            label="ExpansionHexBite_1",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(bite_d, bite_d),
            offset=(max(0.0, cx - tile_radius * 0.75 - bite_d / 2.0), max(0.0, cy - tile_width / 4.0 - bite_d / 2.0)),
            depth=mm_inner_height,
            pull_out=False,
            label="ExpansionHexBite_2",
        ),
    )


project.box(
    BoxType.CAP,
    "MinionsOfTheMeadowBox",
    size=(mm_box_width, mm_box_length, mm_box_height),
    position=(card_box_width, row1_y, 0.0),
    lid=_ant_lid("Minions Hexes", "olive", shape=LabelShape.HEXAGON),
).compartment(
    "ExpansionHexes",
    size=(mm_inner_width, mm_inner_length),
    position=(0.0, 0.0),
    component="Minions Expansion Hex Tiles",
    count=num_mm_hex,
    elements=_mm_hex_elements(),
)


def _food_box_elements() -> tuple[CompartmentElement, ...]:
    """Build 12 stepped circular food wells, 3 centipede stacks + bites, day/night disc, active leaf."""
    elems: list[CompartmentElement] = []
    food_d = 14.0
    col0_depth = 3.0 * food_token_thickness + 0.5  # 11.0mm
    col1_depth = 2.0 * food_token_thickness + 0.5  # 7.5mm
    for i in range(6):
        cy = food_d / 2.0 + i * (food_d + 1.5)
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(food_d, food_d),
                offset=(0.0, cy - food_d / 2.0),
                depth=col0_depth,
                pull_out=False,
                label=f"FoodWellA_{i + 1}",
            )
        )
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(food_d, food_d),
                offset=(food_d + 5.0, cy - food_d / 2.0),
                depth=col1_depth,
                pull_out=False,
                label=f"FoodWellB_{i + 1}",
            )
        )
        # Finger trough connecting paired food wells
        elems.append(
            CompartmentElement(
                shape=ElementShape.RECT,
                size=(food_d + 5.0, 10.0),
                offset=(food_d / 2.0, cy - 5.0),
                depth=col1_depth,
                pull_out=False,
                label=f"FoodTrough_{i + 1}",
            )
        )
    # 3 Centipede token stacks + right finger bites
    cent_d = 26.0
    cent_depth = tile_thickness * 5.0 + 1.0  # 11.0mm
    for i in range(3):
        cy = cent_d / 2.0 + i * (cent_d + 7.0)
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(cent_d, cent_d),
                offset=(40.0, cy - cent_d / 2.0),
                depth=cent_depth,
                pull_out=False,
                label=f"CentipedeStack_{i + 1}",
            )
        )
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(15.0, 15.0),
                offset=(40.0 + cent_d - 7.5, cy - 7.5),
                depth=cent_depth,
                bottom_rounding=4.0,
                pull_out=False,
                label=f"CentipedeBite_{i + 1}",
            )
        )
    # Day/Night circular token (front-right)
    dn_d = 37.0
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(dn_d, dn_d),
            offset=(mm_inner_width - dn_d - 1.5, 3.5),
            depth=tile_thickness + 0.5,
            pull_out=True,
            label="DayNightToken",
        )
    )
    # Active Player Leaf silhouette (back-right)
    elems.append(
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "leaf.svg"),
            size=(22.42, 38.0),
            offset=(84.0, 48.0),
            depth=tile_thickness + 0.5,
            pull_out=True,
            label="ActivePlayerLeaf",
        )
    )
    return tuple(elems)


project.box(
    BoxType.CAP,
    "FoodTokensBox",
    size=(food_box_width, food_box_length, food_box_height),
    position=(card_box_width, row1_y, mm_box_height),
    lid=_ant_lid("Food", "forestgreen", logo_file="leaf.svg", logo_size=16.0),
).compartment(
    "FoodAndTokens",
    size=(mm_inner_width, mm_inner_length),
    position=(0.0, 0.0),
    allocates={
        "Food Tokens": food_token_num,
        "Centipede Tokens": 15,
        "Day/Night Token": 1,
        "Active Player Leaf": 1,
    },
    elements=_food_box_elements(),
)

major_token_thickness = 10.0

project.box(
    BoxType.CAP,
    "PredatorsBox",
    size=(predator_box_width, predator_box_length, predator_box_height),
    position=(card_box_width, row1_y, mm_box_height + food_box_height),
    lid=_ant_lid("Predator", "darkred", logo_file="mantis.svg", logo_size=16.0),
).compartment(
    "Predators",
    size=(mm_inner_width, mm_inner_length),
    position=(0.0, 0.0),
    component="Predator Meeples",
    count=5,
    elements=(
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "spider.svg"),
            size=(34.5, 35.5),
            offset=(3.0, 19.0),
            depth=major_token_thickness,
            pull_out=True,
            label="Spider",
        ),
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "mantis.svg"),
            size=(37.0, 32.0),
            offset=(39.0, 2.0),
            depth=major_token_thickness,
            pull_out=True,
            label="Mantis",
        ),
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "ladybird.svg"),
            size=(22.0, 38.0),
            offset=(89.0, 18.0),
            depth=major_token_thickness,
            pull_out=True,
            label="Ladybird",
        ),
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "fungus.svg"),
            size=(34.0, 31.0),
            offset=(12.0, 56.0),
            depth=major_token_thickness,
            pull_out=True,
            label="Fungus",
        ),
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "centipede.svg"),
            size=(35.0, 39.0),
            offset=(52.0, 52.0),
            depth=major_token_thickness,
            pull_out=True,
            label="Centipede",
        ),
    ),
)

# ── Row 2: 5 Player Boxes & Aphid Box (Y = 201.5 .. 274.0) ────────
row2_y = row1_y + card_box_length
player_inner_width = player_box_width - wall_thickness * 2.0  # 91.0mm
player_inner_length = player_box_length - wall_thickness * 2.0  # 66.505mm


def _player_box_elements() -> tuple[CompartmentElement, ...]:
    """Build T-shaped 36-cube tray, player marker disc, major worker silhouette, 3 major worker tokens."""
    cube = 9.0
    elems: list[CompartmentElement] = [
        # 10x3 + 6x1 = 36 ant cubes
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(cube * 10.0 + 1.0, cube * 3.0 + 1.0),
            offset=(0.0, 0.0),
            depth=cube + 0.5,
            pull_out=False,
            label="CubesMain",
        ),
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(cube * 6.0 + 1.0, cube + 1.0),
            offset=(cube * 2.0, cube * 3.0 + 0.5),
            depth=cube + 0.5,
            pull_out=False,
            label="CubesExt",
        ),
        # Player marker disc
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(15.0, 15.0),
            offset=(player_inner_width - 15.0, cube * 3.0 + 1.5),
            depth=3.5,
            pull_out=True,
            label="PlayerMarker",
        ),
        # Major worker silhouette
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "major_worker.svg"),
            size=(15.0, 25.0),
            offset=(0.0, cube * 3.0 + 3.0),
            depth=major_token_thickness,
            pull_out=True,
            label="MajorWorker",
        ),
    ]
    # 3 Major worker circular token wells
    mwt_d = 24.0
    for i in range(3):
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(mwt_d, mwt_d),
                offset=(16.0 + i * (mwt_d + 1.0), player_inner_length - mwt_d),
                depth=tile_thickness + 0.5,
                pull_out=True,
                label=f"MajorWorkerToken_{i + 1}",
            )
        )
    return tuple(elems)


def _aphid_box_elements() -> tuple[CompartmentElement, ...]:
    """Build 4x9 = 36 aphid silhouette wells (disc + bump) under a top grab recess."""
    elems: list[CompartmentElement] = [
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(player_inner_width - 0.1, 62.0),
            offset=(0.05, 2.25),
            corner_radius=4.0,
            depth=3.0,
            pull_out=False,
            label="AphidGrabRecess",
        )
    ]
    aphid_d = 9.0
    aphid_len = 10.5
    aphid_bump_w = 4.0
    aphid_depth = 9.5
    for j in range(4):
        cy = 10.0 + j * (aphid_len + 4.0)
        for i in range(9):
            cx = 5.0 + (aphid_d + 1.1) * i
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(aphid_d, aphid_d),
                    offset=(cx - aphid_d / 2.0, cy - aphid_d / 2.0),
                    depth=aphid_depth,
                    pull_out=False,
                    label=f"AphidBody_{j}_{i}",
                )
            )
            elems.append(
                CompartmentElement(
                    shape=ElementShape.ROUNDED_RECT,
                    size=(aphid_bump_w, aphid_len / 2.0),
                    offset=(cx - aphid_bump_w / 2.0, cy + (aphid_len - aphid_d)),
                    corner_radius=1.5,
                    depth=aphid_depth,
                    pull_out=False,
                    label=f"AphidBump_{j}_{i}",
                )
            )
    return tuple(elems)


player_placements = [
    ("Red", "darkred", 0.0, 0),
    ("Yellow", "gold", 0.0, 1),
    ("Black", "black", 0.0, 2),
    ("Blue", "navy", player_box_width, 0),
    ("Green", "forestgreen", player_box_width, 1),
]

for p_name, color_name, x_pos, layer in player_placements:
    project.box(
        BoxType.CAP,
        f"PlayerBox_{p_name}",
        size=(player_box_width, player_box_length, player_box_height),
        position=(x_pos, row2_y, player_box_height * layer),
        lid=_ant_lid(
            f"Player ({p_name})",
            color_name,
            logo_file="major_worker.svg",
            logo_size=15.0,
        ),
    ).compartment(
        "CubesAndWorkers",
        size=(player_inner_width, player_inner_length),
        position=(0.0, 0.0),
        allocates={
            "Ant Cubes": 36,
            "Player Marker Discs": 1,
            "Major Workers": 1,
            "Major Worker Tokens": 3,
        },
        elements=_player_box_elements(),
    )

project.box(
    BoxType.CAP,
    "AphidBox",
    size=(player_box_width, player_box_length, player_box_height),
    position=(player_box_width, row2_y, player_box_height * 2.0),
    lid=_ant_lid("Aphids", "yellowgreen"),
).compartment(
    "Aphids",
    size=(player_inner_width, player_inner_length),
    position=(0.0, 0.0),
    component="Aphid Tokens",
    count=36,
    elements=_aphid_box_elements(),
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
