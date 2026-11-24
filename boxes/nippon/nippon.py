#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Nippon board game organizer.

Ports boxes/nippon/nippon.scad to the pyboxbuilder Project API.
Organizes 4 player boxes (ships, trains, track cylinders), 4 player bits boxes
(machine disks, influence/favour/contract tokens, scoring disks), factory tiles,
demand tiles, starting/old factory tiles, upgrade tiles, money, solo tokens,
late-game factories, round markers, 6 worker boxes, and 4 resource cube boxes
with automatic spacers.
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
    else ROOT / "boxes" / "nippon" / "assets"
)

# ── Game Box Dimensions ───────────────────────────────────────────
box_width = 303.0
box_length = 380.0
box_height = 70.0

board_thickness = 9.0
player_boards_thickness = 4.3 * 4.0  # 17.2mm
handbook_thickness = 6.0
total_board_reserve = board_thickness + player_boards_thickness + handbook_thickness  # 32.2mm
usable_height = box_height - total_board_reserve  # 37.8mm

wall_thickness = 2.0
floor_thickness = 2.0
lid_thickness = 2.0

# ── Component Dimensions ──────────────────────────────────────────
cube_size = 10.5
cardboard_token_thickness = 2.5
ship_thickness = 10.0
factory_token_width = 51.0
factory_token_length = 55.5
demand_token_width = 42.0
old_factory_tile_width = 51.0

# ── Sub-Box Dimensions (matching nippon.scad) ─────────────────────
player_box_width = box_width / 4.0  # 75.75mm
player_box_length = 92.0
player_box_height = floor_thickness + lid_thickness + 1.0 + ship_thickness  # 15.0mm

player_box_bits_width = box_width / 2.0  # 151.5mm
player_box_bits_length = 92.0
player_box_bits_height = (usable_height - player_box_height) / 2.0  # 11.4mm

factory_tile_box_width = wall_thickness * 2.0 + factory_token_width + 1.0  # 56.0mm
factory_tile_box_length = wall_thickness * 2.0 + factory_token_length + 1.0  # 60.5mm
factory_tile_box_height = usable_height  # 37.8mm

demand_tile_box_width = wall_thickness * 2.0 + demand_token_width + 1.0  # 47.0mm
demand_tile_box_length = factory_tile_box_length  # 60.5mm
demand_tile_box_height = factory_tile_box_height  # 37.8mm

starting_tile_box_width = wall_thickness * 2.0 + old_factory_tile_width + 1.0  # 56.0mm
starting_tile_box_length = factory_tile_box_length  # 60.5mm
starting_tile_box_height = factory_tile_box_height  # 37.8mm

upgraded_tile_box_width = (
    box_width - starting_tile_box_width - demand_tile_box_width - factory_tile_box_width * 2.0
)  # 88.0mm
upgraded_tile_box_length = factory_tile_box_length  # 60.5mm
upgraded_tile_box_height = (
    cardboard_token_thickness + floor_thickness + lid_thickness
)  # 6.5mm (adjusted to 8.0mm if needed for sliding lid)

money_box_width = upgraded_tile_box_width  # 88.0mm
money_box_length = upgraded_tile_box_length  # 60.5mm
money_box_height = usable_height - upgraded_tile_box_height  # 31.3mm

solo_box_width = 93.0
solo_box_length = upgraded_tile_box_length  # 60.5mm
solo_box_height = floor_thickness + lid_thickness + 1.0 + cardboard_token_thickness * 5.0  # 17.5mm

late_game_factory_box_width = wall_thickness * 2.0 + factory_token_width + 1.0  # 56.0mm
late_game_factory_box_length = solo_box_length  # 60.5mm
late_game_factory_box_height = usable_height - solo_box_height  # 20.3mm

round_marker_box_width = solo_box_width - late_game_factory_box_width - 0.5  # 36.5mm
round_marker_box_length = solo_box_length  # 60.5mm
round_marker_box_height = usable_height - solo_box_height  # 20.3mm

worker_box_width = (box_width - solo_box_width - 1.0) / 3.0  # 69.67mm
worker_box_length = upgraded_tile_box_length  # 60.5mm
worker_box_height = usable_height / 2.0  # 18.9mm

resource_box_width = wall_thickness * 2.0 + cube_size * 8.0 + 24.0  # 112.0mm
resource_box_length = wall_thickness * 2.0 + cube_size * 3.0 + 2.0  # 37.5mm
resource_box_height = usable_height / 2.0  # 18.9mm
resource_box_double_width = box_width - resource_box_width  # 191.0mm

project = Project(
    "Nippon",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=total_board_reserve,
    generate_spacers=True,
    box_defaults={"expandable": False},
)

# ── Game Piece Inventory ──────────────────────────────────────────
project.define_inventory({
    "Player Ships": 24,
    "Player Trains": 24,
    "Track Marker Cylinders": 12,
    "Machine Disks": 24,
    "Influence & Favour Tokens": 80,
    "Contract Tokens": 32,
    "Scoring Disks": 8,
    "Factory Tiles": 24,
    "Demand Tiles": 12,
    "Starting Tiles": 4,
    "Old Factory Tiles": 8,
    "Upgrade Tiles": 12,
    "Money Tokens": 50,
    "Solo Goal Tokens": 9,
    "Solo Action Tokens": 9,
    "Late-Game Factory Tiles": 6,
    "Round Marker Cylinders": 2,
    "Worker Meeples": 48,
    "Expert Worker Tokens": 6,
    "Silk Cubes": 24,
    "Paper Cubes": 24,
    "Coal Cubes": 32,
    "Copper Cubes": 32,
    "Main Game Board": 1,
    "Player Boards": 4,
    "Rulebook": 1,
})

project.board(
    "Main Board, Player Boards & Rulebook",
    size=(box_width, box_length, total_board_reserve),
    position=(0.0, 0.0, usable_height),
    count=6,
    notes="Main game board (9mm), 4 player boards (17.2mm), and handbook (6mm) atop insert",
    allocates={
        "Main Game Board": 1,
        "Player Boards": 4,
        "Rulebook": 1,
    },
)

NIPPON_PATTERN = PatternBuilder(PatternType.AMMANN_BEENKER)
NIPPON_FONT = "Georgia:style=Bold"

# ── Row 1: Player Boxes & Player Bits Boxes (Y = 0 .. 92) ─────────
player_colors = ["purple", "yellow", "green", "red"]
player_inner_width = player_box_width - wall_thickness * 2.0  # 71.75mm
player_inner_length = player_box_length - wall_thickness * 2.0  # 88.0mm
bits_inner_width = player_box_bits_width - wall_thickness * 2.0  # 147.5mm
bits_inner_length = player_box_bits_length - wall_thickness * 2.0  # 88.0mm


def _player_ships_trains_elements() -> tuple[CompartmentElement, ...]:
    """Build 6 ship silhouettes, 6 train silhouettes, and 3 track marker troughs under a grab shelf."""
    elems: list[CompartmentElement] = [
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(player_inner_width, player_inner_length),
            offset=(0.0, 0.0),
            corner_radius=5.0,
            depth=ship_thickness / 2.0,
            pull_out=False,
            label="PlayerGrabShelf",
        )
    ]
    ship_len, ship_w = 21.0, 13.5
    train_len, train_w = 21.0, 13.5
    st_depth = ship_thickness + 0.5
    # 6 Ships (5 in col 0 + 1 in col 1)
    for i in range(5):
        for j in range(2):
            if j != 1 or i < 1:
                elems.append(
                    CompartmentElement(
                        shape=ElementShape.SVG,
                        shape_file=str(ASSETS / "ship.svg"),
                        size=(ship_len, ship_w),
                        offset=(3.0 + (ship_len + 0.5) * j, 5.0 + (ship_w + 2.4) * i),
                        depth=st_depth,
                        pull_out=False,
                        label=f"Ship_{j}_{i}",
                    )
                )
    # 6 Trains (4 in col 1 + 2 in col 2)
    tx0 = 3.0 + ship_len + 0.5
    for i in range(5):
        for j in range(2):
            if (j == 1 or i >= 1) and (j == 0 or i > 2):
                elems.append(
                    CompartmentElement(
                        shape=ElementShape.SVG,
                        shape_file=str(ASSETS / "train.svg"),
                        size=(train_len, train_w),
                        offset=(tx0 + (train_len + 1.0) * j, 5.0 + (train_w + 2.4) * i),
                        depth=st_depth,
                        pull_out=False,
                        label=f"Train_{j}_{i}",
                    )
                )
    # 3 Track marker cylinder troughs (col 2, front)
    tm_d, tm_len = 11.0, 15.0
    tm_x = tx0 + train_len + 3.5
    for i in range(3):
        elems.append(
            CompartmentElement(
                shape=ElementShape.RECT,
                size=(tm_len, tm_d),
                offset=(tm_x, 8.0 + (10.5 + 2.5) * i),
                depth=11.0,
                bottom_rounding=5.0,
                pull_out=False,
                label=f"TrackMarker_{i + 1}",
            )
        )
    return tuple(elems)


def _player_bits_elements() -> tuple[CompartmentElement, ...]:
    """Build 6 machine disks, 10 influence/favour wells, 4 contract wells, and 2 scoring disks."""
    elems: list[CompartmentElement] = []
    # 6 Circular machine disks (2x3) + vertical finger bites
    mach_d = 15.5
    mach_depth = 6.5
    mach_bite_d = 12.0
    for i in range(3):
        for j in range(2):
            cx = 1.0 + mach_d / 2.0 + (mach_d + 1.5) * j
            cy = 14.0 + (mach_d + 1.5) * i
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(mach_d, mach_d),
                    offset=(cx - mach_d / 2.0, cy - mach_d / 2.0),
                    depth=mach_depth,
                    pull_out=False,
                    label=f"MachineDisk_{i}_{j}",
                )
            )
            for s_idx, by in enumerate((cy - mach_d / 2.0, cy + mach_d / 2.0)):
                elems.append(
                    CompartmentElement(
                        shape=ElementShape.CIRCLE,
                        size=(mach_bite_d, mach_bite_d),
                        offset=(cx - mach_bite_d / 2.0, by - mach_bite_d / 2.0),
                        depth=mach_depth,
                        pull_out=False,
                        label=f"MachineBite_{i}_{j}_{s_idx}",
                    )
                )
    # 10 Square influence / favour tokens (5x2) + left/right finger bites
    inf_w = 16.0
    inf_depth = cardboard_token_thickness * 2.0 + 0.5  # 5.5mm
    inf_bite_d = 13.0
    inf_x0 = mach_d * 2.0 + 10.0  # 41.0mm
    for j in range(5):
        for i in range(2):
            ix = inf_x0 + (inf_w + 1.5) * j
            iy = 2.0 + (inf_w + 2.0) * i
            elems.append(
                CompartmentElement(
                    shape=ElementShape.RECT,
                    size=(inf_w, inf_w),
                    offset=(ix, iy),
                    depth=inf_depth,
                    pull_out=False,
                    label=f"InfluenceFavour_{j}_{i}",
                )
            )
            for s_idx, bx in enumerate((ix, ix + inf_w)):
                elems.append(
                    CompartmentElement(
                        shape=ElementShape.CIRCLE,
                        size=(inf_bite_d, inf_bite_d),
                        offset=(bx - inf_bite_d / 2.0, iy + inf_w / 2.0 - inf_bite_d / 2.0),
                        depth=inf_depth,
                        pull_out=False,
                        label=f"InfBite_{j}_{i}_{s_idx}",
                    )
                )
    # 4 Rectangular contract token stacks (2x2) + left/right finger bites
    con_l, con_w = 41.0, 21.0
    con_bite_d = 16.0
    for i in range(2):
        for j in range(2):
            cx_left = mach_d * 2.0 + 15.0 + (con_l + 2.0) * j
            cy_bot = bits_inner_length - con_w * 2.0 - 5.0 + (con_w + 2.0) * i
            elems.append(
                CompartmentElement(
                    shape=ElementShape.RECT,
                    size=(con_l, con_w),
                    offset=(cx_left, cy_bot),
                    depth=inf_depth,
                    pull_out=False,
                    label=f"Contract_{i}_{j}",
                )
            )
            for s_idx, bx in enumerate((cx_left, cx_left + con_l)):
                elems.append(
                    CompartmentElement(
                        shape=ElementShape.CIRCLE,
                        size=(con_bite_d, con_bite_d),
                        offset=(bx - con_bite_d / 2.0, cy_bot + con_w / 2.0 - con_bite_d / 2.0),
                        depth=inf_depth,
                        bottom_rounding=4.0,
                        pull_out=False,
                        label=f"ContractBite_{i}_{j}_{s_idx}",
                    )
                )
    # 2 Circular scoring disks (back-left) + front finger bites
    sd_d = 15.5
    sd_depth = 7.0
    sd_bite_d = 16.0
    for i in range(2):
        cx = 2.0 + sd_d / 2.0 + (sd_d + 1.0) * i
        cy = bits_inner_length - sd_d / 2.0 - 2.0
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(sd_d, sd_d),
                offset=(cx - sd_d / 2.0, cy - sd_d / 2.0),
                depth=sd_depth,
                pull_out=False,
                label=f"ScoringDisk_{i + 1}",
            )
        )
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(sd_bite_d, sd_bite_d),
                offset=(cx - sd_bite_d / 2.0, cy - sd_d / 2.0 - sd_bite_d / 2.0),
                depth=sd_depth,
                pull_out=False,
                label=f"ScoringDiskBite_{i + 1}",
            )
        )
    return tuple(elems)


for i, color_name in enumerate(player_colors):
    txt_color = Color("black" if color_name == "yellow" else "white")
    project.box(
        BoxType.CAP,
        f"PlayerBox_{color_name}",
        size=(player_box_width, player_box_length, player_box_height),
        position=(player_box_width * i, 0.0, 0.0),
        lid=LidBuilder(
            text="Ships & Trains",
            label_mode=LabelMode.FRAMED,
            label_shape=LabelShape.ORNATE_FRAME,
            label_finial=LabelFinial.DIAMOND,
            font=NIPPON_FONT,
            pattern=NIPPON_PATTERN,
            text_color=txt_color,
            frame_color=Color(color_name),
            logo=str(ASSETS / "ship.svg"),
            logo_color=txt_color,
            logo_position="left",
            label_logo_size_mm=15.0,
        ),
    ).compartment(
        "ShipsAndTrains",
        size=(player_inner_width, player_inner_length),
        position=(0.0, 0.0),
        allocates={
            "Player Ships": 6,
            "Player Trains": 6,
            "Track Marker Cylinders": 3,
        },
        elements=_player_ships_trains_elements(),
    )

for i, color_name in enumerate(player_colors):
    col = i % 2
    layer = i // 2
    txt_color = Color("black" if color_name == "yellow" else "white")
    project.box(
        BoxType.CAP,
        f"PlayerBoxBits_{color_name}",
        size=(player_box_bits_width, player_box_bits_length, player_box_bits_height),
        position=(
            player_box_bits_width * col,
            0.0,
            player_box_height + player_box_bits_height * layer,
        ),
        lid=LidBuilder(
            text=f"Player ({color_name.title()})",
            label_mode=LabelMode.FRAMED,
            label_shape=LabelShape.ORNATE_FRAME,
            label_finial=LabelFinial.DIAMOND,
            font=NIPPON_FONT,
            pattern=NIPPON_PATTERN,
            text_color=txt_color,
            frame_color=Color(color_name),
            logo=str(ASSETS / "train.svg"),
            logo_color=txt_color,
            logo_position="left",
            label_logo_size_mm=16.0,
        ),
    ).compartment(
        "PlayerBits",
        size=(bits_inner_width, bits_inner_length),
        position=(0.0, 0.0),
        allocates={
            "Machine Disks": 6,
            "Influence & Favour Tokens": 20,
            "Contract Tokens": 8,
            "Scoring Disks": 2,
        },
        elements=_player_bits_elements(),
    )

# ── Row 2: Factory, Demand, Starting, Upgrade & Money (Y = 92 .. 152.5) ──
row2_y = player_box_length
row2_x = 0.0

for idx, text in enumerate(["Factories I", "Factories II"], start=1):
    project.box(
        BoxType.SLIDING,
        f"FactoryTiles_{idx}",
        size=(factory_tile_box_width, factory_tile_box_length, factory_tile_box_height),
        position=(row2_x, row2_y, 0.0),
        lid=LidBuilder(
            text=text,
            label_mode=LabelMode.FRAMED,
            label_shape=LabelShape.NOTCHED,
            label_finial=LabelFinial.DIAMOND,
            font=NIPPON_FONT,
            pattern=NIPPON_PATTERN,
            text_color=Color("white"),
            frame_color=Color("navy"),
            logo=str(ASSETS / "factory.svg"),
            logo_color=Color("white"),
            logo_position="left",
            label_logo_size_mm=14.0,
        ),
    ).compartment("Tiles", cut=FingerCut.SCOOP, component="Factory Tiles", count=12)
    row2_x += factory_tile_box_width

project.box(
    BoxType.SLIDING,
    "DemandTiles",
    size=(demand_tile_box_width, demand_tile_box_length, demand_tile_box_height),
    position=(row2_x, row2_y, 0.0),
    lid=LidBuilder(
        text="Demand",
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.NOTCHED,
        label_finial=LabelFinial.DIAMOND,
        font=NIPPON_FONT,
        pattern=NIPPON_PATTERN,
        text_color=Color("white"),
        frame_color=Color("navy"),
    ),
).compartment("Tiles", cut=FingerCut.SCOOP, component="Demand Tiles", count=12)
row2_x += demand_tile_box_width

project.box(
    BoxType.SLIDING,
    "StartingTiles",
    size=(starting_tile_box_width, starting_tile_box_length, starting_tile_box_height),
    position=(row2_x, row2_y, 0.0),
    lid=LidBuilder(
        text="Start",
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.NOTCHED,
        label_finial=LabelFinial.DIAMOND,
        font=NIPPON_FONT,
        pattern=NIPPON_PATTERN,
        text_color=Color("white"),
        frame_color=Color("navy"),
    ),
).compartment(
    "Tiles",
    cut=FingerCut.SCOOP,
    allocates={"Starting Tiles": 4, "Old Factory Tiles": 8},
)
row2_x += starting_tile_box_width

upg_inner_width = upgraded_tile_box_width - wall_thickness * 2.0  # 84.0mm
upg_inner_length = upgraded_tile_box_length - wall_thickness * 2.0  # 56.5mm


def _upgrade_tile_elements() -> tuple[CompartmentElement, ...]:
    """Build 4x3 = 12 square upgrade token wells with side finger bites."""
    elems: list[CompartmentElement] = []
    upg_w = 16.0
    bite_d = 12.0
    for i in range(3):
        for j in range(4):
            ux = 6.0 + (upg_w + 2.0) * j
            uy = (upg_w + 4.0) * i
            elems.append(
                CompartmentElement(
                    shape=ElementShape.RECT,
                    size=(upg_w, upg_w),
                    offset=(ux, uy),
                    depth=cardboard_token_thickness,
                    pull_out=False,
                    label=f"Upgrade_{i}_{j}",
                )
            )
            for s_idx, bx in enumerate((ux, ux + upg_w)):
                elems.append(
                    CompartmentElement(
                        shape=ElementShape.CIRCLE,
                        size=(bite_d, bite_d),
                        offset=(bx - bite_d / 2.0, uy + upg_w / 2.0 - bite_d / 2.0),
                        depth=cardboard_token_thickness,
                        pull_out=False,
                        label=f"UpgradeBite_{i}_{j}_{s_idx}",
                    )
                )
    return tuple(elems)


project.box(
    BoxType.SLIDING,
    "UpgradeTiles",
    size=(upgraded_tile_box_width, upgraded_tile_box_length, upgraded_tile_box_height),
    position=(row2_x, row2_y, 0.0),
    lid=LidBuilder(
        text="Upgraded",
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.NOTCHED,
        label_finial=LabelFinial.DIAMOND,
        font=NIPPON_FONT,
        pattern=NIPPON_PATTERN,
        text_color=Color("white"),
        frame_color=Color("teal"),
    ),
).compartment(
    "Upgrades",
    size=(upg_inner_width, upg_inner_length),
    position=(0.0, 0.0),
    component="Upgrade Tiles",
    count=12,
    elements=_upgrade_tile_elements(),
)

project.box(
    BoxType.CAP,
    "MoneyBox",
    size=(money_box_width, money_box_length, money_box_height),
    position=(row2_x, row2_y, upgraded_tile_box_height),
    lid=LidBuilder(
        text="Money",
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.ORNATE_FRAME,
        label_finial=LabelFinial.DIAMOND,
        font=NIPPON_FONT,
        pattern=NIPPON_PATTERN,
        text_color=Color("black"),
        frame_color=Color("gold"),
        logo=str(ASSETS / "coin.svg"),
        logo_color=Color("black"),
        logo_position="left",
        label_logo_size_mm=15.0,
    ),
).compartment("Money", cut=FingerCut.SCOOP, component="Money Tokens", count=50)

# ── Row 3: Solo, Late Game, Round Marker & 6 Worker Boxes (Y = 152.5 .. 213.0) ──
row3_y = row2_y + factory_tile_box_length
solo_inner_width = solo_box_width - wall_thickness * 2.0  # 89.0mm
solo_inner_length = solo_box_length - wall_thickness * 2.0  # 56.5mm


def _solo_box_elements() -> tuple[CompartmentElement, ...]:
    """Build 2 stepped Solo Goal wells + 2 stepped Solo Action wells with side finger bites."""
    elems: list[CompartmentElement] = []
    bite_d = 16.0
    specs = (
        ("SoloGoal_1", 9.0, 5.0, 31.0, 22.0, cardboard_token_thickness * 4.0),
        ("SoloGoal_2", 9.0, 30.0, 31.0, 22.0, cardboard_token_thickness * 5.0),
        ("SoloAction_1", 41.0, 2.0, 38.0, 25.5, cardboard_token_thickness * 4.0),
        ("SoloAction_2", 41.0, 29.0, 38.0, 25.5, cardboard_token_thickness * 5.0),
    )
    for lbl, sx, sy, sw, sl, sd in specs:
        elems.append(
            CompartmentElement(
                shape=ElementShape.ROUNDED_RECT,
                size=(sw, sl),
                offset=(sx, sy),
                corner_radius=2.5,
                depth=sd,
                pull_out=False,
                label=lbl,
            )
        )
        for s_idx, bx in enumerate((sx, sx + sw)):
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(bite_d, bite_d),
                    offset=(bx - bite_d / 2.0, sy + sl / 2.0 - bite_d / 2.0),
                    depth=sd,
                    pull_out=False,
                    label=f"{lbl}_Bite_{s_idx}",
                )
            )
    return tuple(elems)


project.box(
    BoxType.CAP,
    "SoloBox",
    size=(solo_box_width, solo_box_length, solo_box_height),
    position=(0.0, row3_y, 0.0),
    lid=LidBuilder(
        text="Solo",
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.NOTCHED,
        label_finial=LabelFinial.DIAMOND,
        font=NIPPON_FONT,
        pattern=NIPPON_PATTERN,
        text_color=Color("white"),
        frame_color=Color("slategray"),
    ),
).compartment(
    "SoloTokens",
    size=(solo_inner_width, solo_inner_length),
    position=(0.0, 0.0),
    allocates={"Solo Goal Tokens": 9, "Solo Action Tokens": 9},
    elements=_solo_box_elements(),
)

project.box(
    BoxType.SLIDING,
    "LateGameFactoryBox",
    size=(late_game_factory_box_width, late_game_factory_box_length, late_game_factory_box_height),
    position=(0.0, row3_y, solo_box_height),
    lid=LidBuilder(
        text="Late Game",
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.NOTCHED,
        label_finial=LabelFinial.DIAMOND,
        font=NIPPON_FONT,
        pattern=NIPPON_PATTERN,
        text_color=Color("white"),
        frame_color=Color("navy"),
        logo=str(ASSETS / "factory.svg"),
        logo_color=Color("white"),
        logo_position="left",
        label_logo_size_mm=14.0,
    ),
).compartment("LateGameFactories", cut=FingerCut.SCOOP, component="Late-Game Factory Tiles", count=6)

rm_inner_width = round_marker_box_width - wall_thickness * 2.0  # 32.5mm
rm_inner_length = round_marker_box_length - wall_thickness * 2.0  # 56.5mm
rm_d = 12.0
rm_len = 16.0
project.box(
    BoxType.SLIDING,
    "RoundMarkerBox",
    size=(round_marker_box_width, round_marker_box_length, round_marker_box_height),
    position=(late_game_factory_box_width, row3_y, solo_box_height),
    lid=LidBuilder(
        text="Round",
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.NOTCHED,
        label_finial=LabelFinial.NONE,
        font=NIPPON_FONT,
        pattern=NIPPON_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkred"),
    ),
).compartment(
    "RoundMarkers",
    size=(rm_inner_width, rm_inner_length),
    position=(0.0, 0.0),
    component="Round Marker Cylinders",
    count=2,
    elements=(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(rm_inner_width, rm_inner_length),
            offset=(0.0, 0.0),
            corner_radius=5.0,
            depth=rm_len / 2.0,
            pull_out=False,
            label="RoundMarkerShelf",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(rm_d, rm_d),
            offset=(rm_inner_width / 2.0 - rm_d / 2.0, rm_inner_length * 0.25 - rm_d / 2.0),
            depth=rm_len,
            pull_out=False,
            label="RoundMarker_1",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(rm_d, rm_d),
            offset=(rm_inner_width / 2.0 - rm_d / 2.0, rm_inner_length * 0.75 - rm_d / 2.0),
            depth=rm_len,
            pull_out=False,
            label="RoundMarker_2",
        ),
    ),
)

worker_inner_width = worker_box_width - wall_thickness * 2.0  # 65.67mm
worker_inner_length = worker_box_length - wall_thickness * 2.0  # 56.5mm


def _worker_box_elements() -> tuple[CompartmentElement, ...]:
    """Build 8 worker silhouette wells + 1 expert worker square well under a grab shelf."""
    w_len, w_w, w_thick = 18.5, 14.5, 10.0
    exp_w, exp_thick = 16.5, 7.0
    elems: list[CompartmentElement] = [
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(worker_inner_width, worker_inner_length),
            offset=(0.0, 0.0),
            corner_radius=5.0,
            depth=w_thick / 2.0,
            pull_out=False,
            label="WorkerGrabShelf",
        )
    ]
    # 2x3 worker grid on left (rotated 90 deg: footprint 18.5 x 14.5)
    for i in range(2):
        for j in range(3):
            elems.append(
                CompartmentElement(
                    shape=ElementShape.SVG,
                    shape_file=str(ASSETS / "worker.svg"),
                    size=(w_w, w_len),
                    rotation=90.0,
                    offset=(4.5 + (w_len + 1.0) * i, 7.0 + (w_w + 1.0) * j),
                    depth=w_thick + 0.5,
                    pull_out=False,
                    label=f"Worker_{i}_{j}",
                )
            )
    # 2 workers on right (top & bottom)
    for i in range(2):
        elems.append(
            CompartmentElement(
                shape=ElementShape.SVG,
                shape_file=str(ASSETS / "worker.svg"),
                size=(w_w, w_len),
                rotation=90.0,
                offset=(4.5 + (w_len + 1.0) + w_len + 0.75, 5.0 + (w_w * 2.0 + 4.5) * i),
                depth=w_thick + 0.5,
                pull_out=False,
                label=f"WorkerRight_{i + 1}",
            )
        )
    # 1 Expert worker square well (middle-right)
    elems.append(
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(exp_w, exp_w),
            offset=(worker_inner_width - exp_w - 6.0, (worker_inner_length - exp_w) / 2.0),
            depth=exp_thick + 0.5,
            pull_out=False,
            label="ExpertWorker",
        )
    )
    return tuple(elems)


worker_colors = ["white", "blue", "grey", "yellow", "red", "black"]
for idx, wcolor in enumerate(worker_colors):
    col = idx % 3
    layer = idx // 3
    txt_color = Color("black" if wcolor in ("white", "yellow") else "white")
    project.box(
        BoxType.CAP,
        f"WorkerBox_{wcolor}",
        size=(worker_box_width, worker_box_length, worker_box_height),
        position=(solo_box_width + worker_box_width * col, row3_y, worker_box_height * layer),
        lid=LidBuilder(
            text="Workers",
            label_mode=LabelMode.FRAMED,
            label_shape=LabelShape.NOTCHED,
            label_finial=LabelFinial.DIAMOND,
            font=NIPPON_FONT,
            pattern=NIPPON_PATTERN,
            text_color=txt_color,
            frame_color=Color(wcolor if wcolor != "white" else "silver"),
            logo=str(ASSETS / "worker.svg"),
            logo_color=txt_color,
            logo_position="left",
            label_logo_size_mm=14.0,
        ),
    ).compartment(
        "Workers",
        size=(worker_inner_width, worker_inner_length),
        position=(0.0, 0.0),
        allocates={"Worker Meeples": 8, "Expert Worker Tokens": 1},
        elements=_worker_box_elements(),
    )

# ── Row 4: Resource Cube Boxes (Y = 213.0 .. 250.5) ───────────────
row4_y = row3_y + solo_box_length
res_inner_width = resource_box_width - wall_thickness * 2.0  # 108.0mm
res_inner_length = resource_box_length - wall_thickness * 2.0  # 33.5mm
res_dbl_inner_width = resource_box_double_width - wall_thickness * 2.0  # 187.0mm

for layer, (label, color, comp_name) in enumerate([
    ("ResourceBox_silk", "lightgrey", "Silk Cubes"),
    ("ResourceBox_paper", "red", "Paper Cubes"),
]):
    txt_color = Color("black" if color == "lightgrey" else "white")
    project.box(
        BoxType.SLIDING,
        label,
        size=(resource_box_width, resource_box_length, resource_box_height),
        position=(0.0, row4_y, resource_box_height * layer),
        lid=LidBuilder(
            text="Resources",
            label_mode=LabelMode.FRAMED,
            label_shape=LabelShape.NOTCHED,
            label_finial=LabelFinial.NONE,
            font=NIPPON_FONT,
            pattern=NIPPON_PATTERN,
            text_color=txt_color,
            frame_color=Color(color),
            logo=str(ASSETS / "coal.svg"),
            logo_color=txt_color,
            logo_position="left",
            label_logo_size_mm=14.0,
        ),
    ).compartment(
        "Cubes",
        size=(res_inner_width, res_inner_length),
        position=(0.0, 0.0),
        component=comp_name,
        count=24,
        elements=(
            CompartmentElement(
                shape=ElementShape.ROUNDED_RECT,
                size=(res_inner_width, res_inner_length),
                offset=(0.0, 0.0),
                corner_radius=5.0,
                depth=cube_size / 2.0,
                pull_out=False,
                label="CubeGrabShelf",
            ),
            CompartmentElement(
                shape=ElementShape.RECT,
                size=(cube_size * 8.0 + 1.0, cube_size * 3.0),
                offset=((res_inner_width - (cube_size * 8.0 + 1.0)) / 2.0, (res_inner_length - cube_size * 3.0) / 2.0),
                depth=cube_size + 0.5,
                pull_out=False,
                label="CubeGrid8x3",
            ),
        ),
    )

for layer, (label, color, comp_name) in enumerate([
    ("ResourceDoubleBox_coal", "black", "Coal Cubes"),
    ("ResourceDoubleBox_copper", "palegoldenrod", "Copper Cubes"),
]):
    main_w = cube_size * 10.0 + 1.0  # 106.0mm
    main_l = cube_size * 3.0 + 0.5  # 32.0mm
    ext_w = cube_size + 1.0  # 11.5mm
    ext_l = cube_size * 2.0 + 0.5  # 21.5mm
    txt_color = Color("black" if color == "palegoldenrod" else "white")
    project.box(
        BoxType.SLIDING,
        label,
        size=(resource_box_double_width, resource_box_length, resource_box_height),
        position=(resource_box_width, row4_y, resource_box_height * layer),
        lid=LidBuilder(
            text="Resources",
            label_mode=LabelMode.FRAMED,
            label_shape=LabelShape.NOTCHED,
            label_finial=LabelFinial.NONE,
            font=NIPPON_FONT,
            pattern=NIPPON_PATTERN,
            text_color=txt_color,
            frame_color=Color(color),
            logo=str(ASSETS / "coal.svg"),
            logo_color=txt_color,
            logo_position="left",
            label_logo_size_mm=14.0,
        ),
    ).compartment(
        "Cubes",
        size=(res_dbl_inner_width, res_inner_length),
        position=(0.0, 0.0),
        component=comp_name,
        count=32,
        elements=(
            CompartmentElement(
                shape=ElementShape.ROUNDED_RECT,
                size=(res_dbl_inner_width, res_inner_length),
                offset=(0.0, 0.0),
                corner_radius=5.0,
                depth=cube_size / 2.0,
                pull_out=False,
                label="CubeGrabShelf",
            ),
            CompartmentElement(
                shape=ElementShape.RECT,
                size=(main_w, main_l),
                offset=(res_dbl_inner_width / 2.0 - cube_size / 2.0 - main_w / 2.0, (res_inner_length - main_l) / 2.0),
                depth=cube_size + 0.5,
                pull_out=False,
                label="CubeGrid10x3",
            ),
            CompartmentElement(
                shape=ElementShape.RECT,
                size=(ext_w, ext_l),
                offset=(res_dbl_inner_width / 2.0 + cube_size * 5.0 - ext_w / 2.0, (res_inner_length - ext_l) / 2.0),
                depth=cube_size + 0.5,
                pull_out=False,
                label="CubeGrid1x2",
            ),
        ),
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
