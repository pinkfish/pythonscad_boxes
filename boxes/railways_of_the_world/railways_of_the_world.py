#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Railways of the World board game insert.

Ports `examples/railways_of_the_world.scad` to the pyboxbuilder Project API.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd()
sys.path.insert(0, str(ROOT))
for _sp in ROOT.glob(".venv/lib/*/site-packages"):
    sys.path.insert(0, str(_sp))
for _sp in ROOT.glob("venv/*/lib/*/site-packages"):
    sys.path.insert(0, str(_sp))

from pybosl2 import Color
from pyboxbuilder import (
    BoxType,
    ElementShape,
    FingerCut,
    LabelMode,
    LidBuilder,
    Project,
    centered,
    run,
)

SVG_DIR = Path(__file__).parent / "svg"

# ── Game Box & Global Dimensions ──────────────────────────────────
box_width = 310.0
box_length = 385.0
box_height = 100.0
total_board_thickness = 22.0

wall_thickness = 2.0
lid_thickness = 3.0
floor_thickness = 2.0

card_width = 68.0
card_length = 92.0
bond_width = 59.0
bond_length = 78.0
bond_card_thickness = 17.0

train_card_width = 58.0
train_card_length = 90.0
train_card_thickness = 2.5

crossing_height = 14.0
crossing_length = 34.0

silo_piece_width = 22.0
silo_piece_height = 43.0
mine_height = 27.0
mine_width = 21.0
roundhouse_height = 40.0
roundhouse_total_width = 90.0

single_card_thickness = 0.6

money_thickness = 10.0
money_length = 134.0
money_width = 62.0

tile_width = 29.0
tile_radius = tile_width / 2.0 / math.cos(math.radians(30))
tile_thickness = 2.0

sweden_bonus_length = 35.5
sweden_bonus_width = 16.5
australia_switch_track_token_radius = 8.5
player_marker_diameter = 15.5
player_marker_thickness = 5.0

# Card counts
eastern_us_cards = 12 + 31 + 6 + 2   # 51
mexico_cards = 12 + 38 + 5 + 4       # 59
europe_cards = 10 + 29 + 5           # 44
western_us_cards = 12 + 38 + 6       # 56
great_britan_cards = 10 + 27 + 5     # 42
north_america_cards = 24 + 50 + 12   # 86
portugal_cards = 10 + 34 + 4         # 48
australia_cards = 63 + 15 + 6        # 84
sweden_cards = 12 + 43               # 55

inner_wall = 1.5


def card_box_width_calc(num_cards: int) -> float:
    return num_cards * single_card_thickness + wall_thickness * 2


all_boxes_height = card_width + wall_thickness + lid_thickness  # 73.0
card_box_width = card_length + wall_thickness * 2 + 1.0          # 97.0

eastern_us_card_box_length = card_box_width_calc(eastern_us_cards) + inner_wall + bond_card_thickness + 0.5  # 53.6

player_box_width = (box_length - card_box_width - 2.0) / 3.0  # 95.333
player_box_plastic_extra_length = (
    train_card_width + silo_piece_height * 2.0 + roundhouse_height + inner_wall * 2.0 + wall_thickness * 2.0
)  # 191.0
player_box_height = silo_piece_width + lid_thickness * 2.0  # 28.0
player_box_length = train_card_width + wall_thickness * 2.0 + 7.4  # 69.4
player_box_small_height = player_box_height * 2.0 / 3.0  # 18.667

top_section_height = all_boxes_height - player_box_height * 2.0  # 17.0
top_section_width = box_length - card_box_width - 2.0            # 286.0

money_section_width = money_width + 1.5 + wall_thickness * 2.0   # 67.5
money_section_length = money_length + 1.5 + wall_thickness * 2.0  # 139.5

hex_box_width = money_section_length                             # 139.5
hex_box_length = tile_width * 5.0 + wall_thickness * 2.0         # 149.0
hex_box_extra_height = (player_box_height * 2.0 - top_section_height * 3.0) / 2.0  # 2.5
hex_box_height = top_section_height + hex_box_extra_height       # 19.5

new_city_box_length = money_section_width                        # 67.5
new_city_box_width = money_section_length                        # 139.5
new_city_extra_length = (hex_box_width - money_section_width * 2.0) / 2.0  # 2.25
new_city_extra_width = hex_box_length - money_section_length     # 9.5

empty_city_width = 47.0
empty_city_length = (player_box_width * 3.0) / 2.0 - 0.5          # 142.5
empty_city_height = player_box_height * 2.0                       # 56.0

player_box_trains_length = box_width - empty_city_width - player_box_plastic_extra_length - 2.0  # 70.0

expansion_area_box_width = box_width - card_box_width_calc(portugal_cards) - money_section_width - 1.0 - new_city_extra_length  # 47.0

sweden_box_width = empty_city_width                              # 47.0
sweden_box_length = empty_city_length                            # 142.5

australia_box_width = empty_city_width                          # 47.0
australia_box_length = empty_city_length - 0.5                  # 142.0

# ── Project Definition ─────────────────────────────────────────────
project = Project(
    "Railways of the World",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=total_board_thickness,
    generate_spacers=True,
)

# ── 1. Card Boxes ──────────────────────────────────────────────────
# Eastern US Card Box
card_eastern_us_size = (eastern_us_card_box_length, card_box_width, all_boxes_height)
project.box(
    BoxType.SLIDING,
    "CardBoxEasternUS",
    size=card_eastern_us_size,
    lid=LidBuilder(text="Eastern US", label_mode=LabelMode.FRAMED, text_color=Color("black")),
    color=Color("purple"),
    position=(0.0, 0.0, total_board_thickness),
    no_rotate=True,
).compartment(
    "CardsAndBonds",
    elements=[
        # Main Eastern US cards compartment
        centered(
            None,
            (
                (card_box_width_calc(eastern_us_cards) - wall_thickness * 2.0) / 2.0,
                (card_box_width - wall_thickness * 2.0) / 2.0,
            ),
            (
                card_box_width_calc(eastern_us_cards) - wall_thickness * 2.0,
                card_box_width - wall_thickness * 2.0,
            ),
            depth=all_boxes_height - lid_thickness,
            pull_out=True,
            pull_out_width=25.0,
            pull_out_depth=(all_boxes_height - lid_thickness) / 2.0,
        ),
        # Bond cards compartment
        centered(
            None,
            (
                card_box_width_calc(eastern_us_cards) + inner_wall - wall_thickness * 2.0 + bond_card_thickness / 2.0,
                (card_box_width - wall_thickness * 2.0) / 2.0,
            ),
            (bond_card_thickness, bond_length),
            depth=bond_width + wall_thickness,
            z_offset=card_width - bond_width,
            pull_out=False,
        ),
    ],
)

# Australia Card Box
card_aus_len = card_box_width_calc(australia_cards)
project.box(
    BoxType.SLIDING,
    "CardBoxAustralia",
    size=(card_aus_len, card_box_width, all_boxes_height),
    lid=LidBuilder(
        text="Australia",
        logo=str(SVG_DIR / "australia.svg") if (SVG_DIR / "australia.svg").is_file() else None,
        label_mode=LabelMode.FRAMED,
        text_color=Color("black"),
    ),
    color=Color("purple"),
    position=(eastern_us_card_box_length, 0.0, total_board_thickness),
    no_rotate=True,
).compartment(
    "Cards",
    depth=all_boxes_height - lid_thickness,
    cut=FingerCut.SCOOP,
)

# Sweden Card Box
card_swe_len = card_box_width_calc(sweden_cards)
project.box(
    BoxType.SLIDING,
    "CardBoxSweden",
    size=(card_swe_len, card_box_width, all_boxes_height),
    lid=LidBuilder(
        text="Sweden",
        logo=str(SVG_DIR / "sweden.svg") if (SVG_DIR / "sweden.svg").is_file() else None,
        label_mode=LabelMode.FRAMED,
        text_color=Color("black"),
    ),
    color=Color("purple"),
    position=(eastern_us_card_box_length + card_aus_len, 0.0, total_board_thickness),
    no_rotate=True,
).compartment(
    "Cards",
    depth=all_boxes_height - lid_thickness,
    cut=FingerCut.SCOOP,
)

# Mexico Card Box
card_mex_len = card_box_width_calc(mexico_cards)
project.box(
    BoxType.SLIDING,
    "CardBoxMexico",
    size=(card_mex_len, card_box_width, all_boxes_height),
    lid=LidBuilder(text="Mexico", label_mode=LabelMode.FRAMED, text_color=Color("black")),
    color=Color("purple"),
    position=(eastern_us_card_box_length + card_aus_len + card_swe_len, 0.0, total_board_thickness),
    no_rotate=True,
).compartment(
    "Cards",
    depth=all_boxes_height - lid_thickness,
    cut=FingerCut.SCOOP,
)

# Portugal Card Box
card_por_len = card_box_width_calc(portugal_cards)
project.box(
    BoxType.SLIDING,
    "CardBoxPortugal",
    size=(card_por_len, card_box_width, all_boxes_height),
    lid=LidBuilder(
        text="Portugal",
        logo=str(SVG_DIR / "portugal_castle.svg") if (SVG_DIR / "portugal_castle.svg").is_file() else None,
        label_mode=LabelMode.FRAMED,
        text_color=Color("black"),
    ),
    color=Color("purple"),
    position=(
        eastern_us_card_box_length + card_aus_len + card_swe_len + card_mex_len,
        0.0,
        total_board_thickness,
    ),
    no_rotate=True,
).compartment(
    "Cards",
    depth=all_boxes_height - lid_thickness,
    cut=FingerCut.SCOOP,
)

# ── 2. Empty City Boxes ────────────────────────────────────────────
for idx, y_pos in enumerate([card_box_width, card_box_width + empty_city_length], start=1):
    project.box(
        BoxType.SLIDING,
        f"EmptyCityBox{idx}",
        size=(empty_city_width, empty_city_length, empty_city_height),
        lid=LidBuilder(text="Empty City", label_mode=LabelMode.FRAMED, text_color=Color("black")),
        color=Color("purple"),
        position=(0.0, y_pos, total_board_thickness),
        no_rotate=True,
    ).compartment(
        "Markers",
        depth=empty_city_height - floor_thickness,
        cut=FingerCut.SCOOP,
    )

# ── 3. Player Boxes ────────────────────────────────────────────────
PLAYER_COLORS = ["red", "blue", "green", "yellow", "black", "purple"]

# 6 Train Miniature Boxes (2 layers of 3 boxes)
for i, color_name in enumerate(PLAYER_COLORS):
    col = i % 3
    row = i // 3
    y_pos = card_box_width + col * player_box_width
    z_pos = total_board_thickness + row * player_box_height
    project.box(
        BoxType.SLIDING,
        f"PlayerBoxTrains_{color_name}",
        size=(player_box_trains_length, player_box_width, player_box_height),
        lid=LidBuilder(text=f"Trains ({color_name.title()})", label_mode=LabelMode.FRAMED, text_color=Color("black")),
        color=Color(color_name if color_name != "black" else "gray"),
        position=(empty_city_width, y_pos, z_pos),
        no_rotate=True,
    ).compartment(
        "Trains",
        depth=player_box_height - floor_thickness,
        cut=FingerCut.SCOOP,
    )

# 6 Player Card & Marker Boxes (2 columns of 3 boxes stacked)
for i, color_name in enumerate(PLAYER_COLORS):
    col = i // 3
    layer = i % 3
    x_pos = empty_city_width + player_box_trains_length + col * player_box_length
    z_pos = total_board_thickness + layer * player_box_small_height
    project.box(
        BoxType.CAP,
        f"PlayerBox_{color_name}",
        size=(player_box_length, player_box_width, player_box_small_height),
        lid=LidBuilder(text=f"Player ({color_name.title()})", label_mode=LabelMode.FRAMED, text_color=Color("black")),
        color=Color(color_name if color_name != "black" else "gray"),
        position=(x_pos, card_box_width, z_pos),
        no_rotate=True,
    ).compartment(
        "CardsAndMarker",
        elements=[
            # Locomotive card well
            centered(
                None,
                (
                    (player_box_length - wall_thickness * 2.0) / 2.0,
                    (player_box_width - wall_thickness * 2.0) / 2.0,
                ),
                (train_card_width, train_card_length),
                depth=train_card_thickness * 4.0 + 1.0,
                pull_out=True,
                pull_out_width=25.0,
            ),
            # Player score marker well
            centered(
                None,
                (
                    (player_box_length - wall_thickness * 2.0) / 2.0,
                    (player_box_width - wall_thickness * 2.0) / 2.0,
                ),
                (player_marker_diameter + 0.5, player_marker_diameter + 0.5),
                shape=ElementShape.CIRCLE,
                depth=player_marker_thickness + 2.0,
                z_offset=train_card_thickness * 4.0 + 1.0,
                pull_out=True,
                pull_out_width=15.0,
            ),
        ],
    )

# ── 4. Track Hex Boxes (2 stacked) ─────────────────────────────────
for i in range(2):
    project.box(
        BoxType.CAP,
        f"HexBox{i + 1}",
        size=(hex_box_width, hex_box_length, hex_box_height),
        lid=LidBuilder(text="Tracks", label_mode=LabelMode.FRAMED, text_color=Color("black")),
        color=Color("purple"),
        position=(
            empty_city_width + player_box_trains_length,
            card_box_width + player_box_width,
            total_board_thickness + i * hex_box_height,
        ),
        no_rotate=True,
    ).compartment(
        "HexGrid",
        depth=hex_box_height - floor_thickness,
    )

# ── 5. Money Box & New City Box ────────────────────────────────────
money_z_pos = total_board_thickness + top_section_height * 2.0 + hex_box_extra_height * 2.0
project.box(
    BoxType.SLIDING,
    "MoneyBox",
    size=(money_section_width + new_city_extra_length, money_section_length + new_city_extra_width, top_section_height),
    lid=LidBuilder(text="Money", label_mode=LabelMode.FRAMED, text_color=Color("black")),
    color=Color("purple"),
    position=(
        empty_city_width + player_box_trains_length,
        card_box_width + player_box_width,
        money_z_pos,
    ),
    no_rotate=True,
).compartment(
    "Money",
    depth=top_section_height - floor_thickness,
    cut=FingerCut.SCOOP,
)

project.box(
    BoxType.CAP,
    "NewCityBox",
    size=(money_section_width + new_city_extra_length, money_section_length + new_city_extra_width, top_section_height),
    lid=LidBuilder(text="New Cities", label_mode=LabelMode.FRAMED, text_color=Color("black")),
    color=Color("purple"),
    position=(
        empty_city_width + player_box_trains_length + money_section_width + new_city_extra_length,
        card_box_width + player_box_width,
        money_z_pos,
    ),
    no_rotate=True,
).compartment(
    "NewCities",
    elements=[
        # Hex cutouts for New City tiles
        centered(
            None,
            ((money_section_width + new_city_extra_length - wall_thickness * 2.0) / 2.0, 25.0),
            (tile_width, tile_width),
            shape=ElementShape.CIRCLE,
            depth=tile_thickness * 4.25,
            pull_out=True,
        ),
        centered(
            None,
            ((money_section_width + new_city_extra_length - wall_thickness * 2.0) / 2.0, 65.0),
            (tile_width, tile_width),
            shape=ElementShape.CIRCLE,
            depth=tile_thickness * 4.25,
            pull_out=True,
        ),
        # Token compartment
        centered(
            None,
            ((money_section_width + new_city_extra_length - wall_thickness * 2.0) / 2.0, 115.0),
            (41.0, 15.5),
            depth=10.0,
            pull_out=True,
        ),
    ],
)

# ── 6. Expansion Boxes ─────────────────────────────────────────────
# Australia Expansion Box
project.box(
    BoxType.CAP,
    "AustraliaBox",
    size=(australia_box_width, australia_box_length, top_section_height),
    lid=LidBuilder(
        text="Australia",
        logo=str(SVG_DIR / "australia.svg") if (SVG_DIR / "australia.svg").is_file() else None,
        label_mode=LabelMode.FRAMED,
        text_color=Color("blue"),
    ),
    color=Color("purple"),
    position=(0.0, card_box_width, total_board_thickness + empty_city_height),
    no_rotate=True,
).compartment(
    "AustraliaExpansion",
    elements=[
        # 5x4 Hex grid compartment for Australia tracks
        centered(
            None,
            ((australia_box_width - wall_thickness * 2.0) / 2.0, 38.0),
            (australia_box_width - wall_thickness * 2.0, 70.0),
            depth=top_section_height - floor_thickness,
            pull_out=True,
        ),
        # Bonus tiles
        centered(
            None,
            (32.0, 100.0),
            (sweden_bonus_width, sweden_bonus_length),
            depth=tile_thickness * 4.5,
            pull_out=True,
        ),
        # Switch track token wells
        *[
            centered(
                None,
                (
                    11.0 + 20.0 * (k % 2),
                    85.0 + (k // 2) * 22.0,
                ),
                (australia_switch_track_token_radius * 2.0, australia_switch_track_token_radius * 2.0),
                shape=ElementShape.CIRCLE,
                depth=tile_thickness * 2.4,
                pull_out=True,
            )
            for k in range(4)
        ],
    ],
)

# Sweden Expansion Box
project.box(
    BoxType.CAP,
    "SwedenBox",
    size=(sweden_box_width, sweden_box_length, top_section_height),
    lid=LidBuilder(
        text="Sweden",
        logo=str(SVG_DIR / "sweden.svg") if (SVG_DIR / "sweden.svg").is_file() else None,
        label_mode=LabelMode.FRAMED,
        text_color=Color("lightblue"),
    ),
    color=Color("purple"),
    position=(0.0, card_box_width + australia_box_length, total_board_thickness + empty_city_height),
    no_rotate=True,
).compartment(
    "SwedenExpansion",
    elements=[
        # 6x3 Hex grid compartment for Sweden tracks
        centered(
            None,
            ((sweden_box_width - wall_thickness * 2.0) / 2.0, 42.0),
            (sweden_box_width - wall_thickness * 2.0, 75.0),
            depth=top_section_height - floor_thickness,
            pull_out=True,
        ),
        # 2 Bonus tile wells
        *[
            centered(
                None,
                (
                    (sweden_box_width - wall_thickness * 2.0) / 2.0,
                    95.0 + i * 25.0,
                ),
                (sweden_bonus_width, sweden_bonus_length),
                depth=tile_thickness * 2.4,
                pull_out=True,
            )
            for i in range(2)
        ],
    ],
)

# ── 7. Spacers ─────────────────────────────────────────────────────
# Spacers are automatically derived from the leftover 3D space by pyboxbuilder
# (FR-014 / FR-014f) with automatic finger scoops along their longer walls.

if __name__ == "__main__":
    run(project)
