#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Emberleaf board game organizer.

Ports boxes/emberleaf/emberleaf.scad to the pyboxbuilder Project API.
Organizes 5 player animal meeple boxes (black, red, yellow, blue, grey),
4 material boxes (food, stone, honey, wood), 3 main card boxes (favors,
heroes, solo), 5 player deck boxes, and the common trophy/hex box with
automatic spacers.
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

SVG_DIR = (
    Path(__file__).resolve().parent / "svg"
    if "__file__" in globals()
    else ROOT / "boxes" / "emberleaf" / "svg"
)
ASSETS = (
    Path(__file__).resolve().parent / "assets"
    if "__file__" in globals()
    else ROOT / "boxes" / "emberleaf" / "assets"
)

# ── Box & Board Dimensions ────────────────────────────────────────
box_width = 287.0
box_length = 287.0
box_height = 79.0

board_thickness = 26.5
usable_height = box_height - board_thickness  # 52.5mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

# ── Component Dimensions ──────────────────────────────────────────
card_width = 66.0
card_length = 91.0
cardboard_token_thickness = 2.0

# ── Sub-Box Dimensions (matching emberleaf.scad) ──────────────────
PLAYER_BOX_WIDTH = card_length + wall_thickness * 2.0 + 1.0  # 98.0mm
PLAYER_BOX_LENGTH = (box_length - 2.0) / 2.0  # 142.5mm
PLAYER_BOX_HEIGHT = usable_height / 4.0  # 13.125mm

MATERIAL_BOX_WIDTH = PLAYER_BOX_WIDTH  # 98.0mm
MATERIAL_BOX_LENGTH = PLAYER_BOX_LENGTH / 2.0  # 71.25mm
MATERIAL_BOX_HEIGHT = PLAYER_BOX_HEIGHT  # 13.125mm

CARD_BOX_WIDTH = PLAYER_BOX_WIDTH  # 98.0mm
CARD_BOX_LENGTH = card_width + wall_thickness * 2.0 + 1.0  # 73.0mm
CARD_BOX_HEIGHT = usable_height  # 52.5mm

PLAYER_CARD_BOX_WIDTH = box_width - PLAYER_BOX_WIDTH - CARD_BOX_WIDTH - 1.0  # 90.0mm
PLAYER_CARD_BOX_LENGTH = card_length + wall_thickness * 2.0 + 1.0  # 98.0mm
PLAYER_CARD_BOX_HEIGHT = usable_height / 5.0  # 10.5mm

COMMON_BOX_WIDTH = PLAYER_CARD_BOX_WIDTH  # 90.0mm
COMMON_BOX_LENGTH = box_length - PLAYER_CARD_BOX_LENGTH - 1.0  # 188.0mm
COMMON_BOX_HEIGHT = lid_thickness + floor_thickness + cardboard_token_thickness * 10.0 + 1.0  # 25.0mm

project = Project(
    "Emberleaf",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

project.define_inventory(
    {
        "Villager Figures": 100,
        "Hero Figures": 5,
        "Favour Discs": 25,
        "Fellowship Building Tiles": 30,
        "Score Tokens": 5,
        "100+ Score Tokens": 5,
        "Food Tokens": 35,
        "Stone Tokens": 30,
        "Honey Tokens": 20,
        "Wood Tokens": 35,
        "Favour Cards": 88,
        "Hero Cards": 47,
        "Solo Cards": 64,
        "Fellowship Deck Cards": 30,
        "Player Reference Cards": 5,
        "General Building Tiles": 50,
        "Trophy Tokens": 6,
        "Tracker Disc": 1,
        "Game Board": 1,
        "Building Board": 1,
        "Trophy Board": 1,
        "Fellowship Player Boards": 5,
        "Rulebook": 1,
    }
)

project.board(
    "Game Boards & Rulebook",
    size=(box_width, box_length, board_thickness),
    position=(0.0, 0.0, usable_height),
    count=9,
    notes="Main game board, building board, trophy board, 5 fellowship player boards, and rulebook on top",
    allocates={
        "Game Board": 1,
        "Building Board": 1,
        "Trophy Board": 1,
        "Fellowship Player Boards": 5,
        "Rulebook": 1,
    },
)

EMBER_PATTERN = PatternBuilder(PatternType.LEAF_VEINS)
EMBER_FONT = "Georgia:style=Bold"


def _ember_lid(
    text: str,
    frame_color: str,
    *,
    shape: LabelShape = LabelShape.RIBBON,
    logo_path: str | None = None,
    logo_size: float = 16.0,
) -> LidBuilder:
    text_color = "black" if frame_color == "gold" else "white"
    return LidBuilder(
        text=text,
        label_mode=LabelMode.FRAMED,
        label_shape=shape,
        label_finial=LabelFinial.FLEURON,
        font=EMBER_FONT,
        pattern=EMBER_PATTERN,
        text_color=Color(text_color),
        frame_color=Color(frame_color),
        logo=logo_path,
        logo_color=Color(text_color) if logo_path is not None else None,
        logo_position="left" if logo_path is not None else None,
        label_logo_size_mm=logo_size if logo_path is not None else None,
    )

# ── Column 0: 5 Player Boxes & 4 Material Boxes (X = 0 .. 98) ─────
player_inner_width = PLAYER_BOX_WIDTH - wall_thickness * 2.0  # 92.0mm
player_inner_length = PLAYER_BOX_LENGTH - wall_thickness * 2.0  # 136.5mm
player_inner_height = PLAYER_BOX_HEIGHT - floor_thickness - lid_thickness  # 9.125mm
hex_size = 38.5
wood_token_diameter = 16.5
wood_token_thickness = 4.0
token_thickness = 9.0


def _player_box_elements(hero_svg: str, hero_rot: float = 0.0) -> tuple[CompartmentElement, ...]:
    """Build 20 animal worker silhouettes, unique hero, 3 wooden markers, 2 hex stacks, and stepped victory tokens."""
    elems: list[CompartmentElement] = [
        # Two overlapping top grab shelves over workers & hero
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(player_inner_width, 80.0),
            offset=(0.0, 0.0),
            corner_radius=5.0,
            depth=token_thickness / 2.0,
            pull_out=False,
            label="WorkersGrabShelf",
        ),
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(50.0, 96.0),
            offset=(0.0, 0.0),
            corner_radius=5.0,
            depth=token_thickness / 2.0,
            pull_out=False,
            label="HeroGrabShelf",
        ),
    ]
    # 20 Animal Workers (4 cols x 5 rows)
    worker_cols = (
        ("Owl", "owl worker.svg", 12.0, 8.0, 12.0, 18.0, 10.5, False),
        ("Rabbit", "rabbit worker.svg", 36.0, 8.0, 12.0, 18.0, 10.5, True),
        ("Frog", "frog worker.svg", 57.5, 9.0, 14.5, 15.5, 13.0, False),
        ("Rat", "rat worker.svg", 77.0, 9.0, 15.0, 18.0, 13.5, True),
    )
    for w_name, svg_file, cx, y0, dy, ww, wl, alt_rot in worker_cols:
        for i in range(5):
            cy = y0 + dy * i
            elems.append(
                CompartmentElement(
                    shape=ElementShape.SVG,
                    shape_file=str(SVG_DIR / svg_file),
                    size=(ww, wl),
                    rotation=180.0 if (alt_rot and i % 2 == 1) else 0.0,
                    offset=(cx - ww / 2.0, cy - wl / 2.0),
                    depth=token_thickness,
                    pull_out=False,
                    label=f"{w_name}_{i + 1}",
                )
            )
    # Unique Player Hero silhouette
    hero_w, hero_l = (22.0, 28.0) if hero_rot == 90.0 else (28.0, 22.0)
    elems.append(
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(SVG_DIR / hero_svg),
            size=(28.0, 22.0) if hero_rot == 0.0 else (22.0, 28.0),
            rotation=hero_rot,
            offset=(25.0 - hero_w / 2.0, 78.0 - hero_l / 2.0),
            depth=token_thickness,
            pull_out=False,
            label="PlayerHero",
        )
    )
    # 3 Circular Wooden Marker wells + finger bites
    m_bite_d = 13.0
    m1_cx, m1_cy = player_inner_width - wood_token_diameter / 2.0, 89.0
    m2_cx, m2_cy = player_inner_width - wood_token_diameter * 1.5 - 5.0, 89.0
    m3_cx, m3_cy = player_inner_width / 2.0, 102.0
    wr = wood_token_diameter / 2.0
    marker_specs = (
        ("Marker_1", m1_cx, m1_cy, wood_token_thickness * 2.0 + 0.5, ((-wr, 0.0), (0.0, -wr))),
        ("Marker_2", m2_cx, m2_cy, wood_token_thickness * 2.0 + 0.5, ((wr, 0.0), (0.0, -wr))),
        ("Marker_3", m3_cx, m3_cy, wood_token_thickness + 0.5, ((wr, 0.0),)),
    )
    for m_name, mcx, mcy, m_depth, bites in marker_specs:
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(wood_token_diameter, wood_token_diameter),
                offset=(mcx - wood_token_diameter / 2.0, mcy - wood_token_diameter / 2.0),
                depth=m_depth,
                pull_out=False,
                label=m_name,
            )
        )
        for b_idx, (bdx, bdy) in enumerate(bites):
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(m_bite_d, m_bite_d),
                    offset=(mcx + bdx - m_bite_d / 2.0, mcy + bdy - m_bite_d / 2.0),
                    depth=m_depth,
                    bottom_rounding=4.0,
                    pull_out=False,
                    label=f"{m_name}_Bite_{b_idx + 1}",
                )
            )
    # 2 Hex tile wells + stepped victory tokens under left hex
    hex_x_span = hex_size / math.cos(math.radians(30.0))  # 44.456mm
    hex_cy = player_inner_length - hex_size / 2.0  # 117.25mm
    left_hex_cx = hex_x_span / 2.0 + 0.25  # 22.48mm
    right_hex_cx = player_inner_width - hex_x_span / 2.0 - 0.25  # 69.52mm
    elems.extend(
        [
            CompartmentElement(
                shape=ElementShape.HEXAGON,
                size=(hex_size, hex_size),
                rotation=0.0,
                offset=(left_hex_cx - hex_x_span / 2.0, hex_cy - hex_size / 2.0),
                depth=cardboard_token_thickness + 0.3,
                pull_out=False,
                label="HexStackLeft",
            ),
            CompartmentElement(
                shape=ElementShape.SVG,
                shape_file=str(SVG_DIR / "victory.svg"),
                size=(24.0, 21.0),
                offset=(left_hex_cx - 12.0, hex_cy - 10.5),
                depth=cardboard_token_thickness * 2.0 + 0.8,
                pull_out=False,
                label="VictoryToken",
            ),
            CompartmentElement(
                shape=ElementShape.SVG,
                shape_file=str(SVG_DIR / "victory.svg"),
                size=(17.5, 20.5),
                offset=(left_hex_cx - 8.75, hex_cy - 10.25),
                depth=cardboard_token_thickness * 3.0 + 1.1,
                pull_out=False,
                label="VictoryTokenSmall",
            ),
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(14.0, 14.0),
                offset=(0.0, hex_cy - 7.0),
                depth=cardboard_token_thickness * 3.0 + 1.1,
                pull_out=False,
                label="HexLeftBite",
            ),
            CompartmentElement(
                shape=ElementShape.HEXAGON,
                size=(hex_size, hex_size),
                rotation=0.0,
                offset=(right_hex_cx - hex_x_span / 2.0, hex_cy - hex_size / 2.0),
                depth=player_inner_height,
                pull_out=False,
                label="HexStackRight",
            ),
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(14.0, 14.0),
                offset=(right_hex_cx - hex_x_span / 2.0 - 7.0, hex_cy - 7.0),
                depth=player_inner_height,
                pull_out=False,
                label="HexRightBite",
            ),
        ]
    )
    return tuple(elems)


player_placements = [
    ("PlayerBoxBlack", "black", "black leader.svg", 0.0, (0.0, 0.0, 0.0)),
    ("PlayerBoxRed", "darkred", "red leader.svg", 0.0, (0.0, PLAYER_BOX_LENGTH, 0.0)),
    ("PlayerBoxYellow", "gold", "yellow leader.svg", 0.0, (0.0, 0.0, PLAYER_BOX_HEIGHT)),
    ("PlayerBoxBlue", "navy", "blue leader.svg", 0.0, (0.0, PLAYER_BOX_LENGTH, PLAYER_BOX_HEIGHT)),
    ("PlayerBoxGrey", "gray", "grey leader.svg", 90.0, (0.0, 0.0, PLAYER_BOX_HEIGHT * 2.0)),
]

for label, color_name, hero_svg, hero_rot, pos in player_placements:
    project.box(
        BoxType.CAP,
        label,
        size=(PLAYER_BOX_WIDTH, PLAYER_BOX_LENGTH, PLAYER_BOX_HEIGHT),
        position=pos,
        lid=_ember_lid(
            label.replace("PlayerBox", "Player "),
            color_name,
            shape=LabelShape.SHIELD,
            logo_path=str(SVG_DIR / hero_svg),
            logo_size=16.0,
        ),
    ).compartment(
        "PlayerBits",
        size=(player_inner_width, player_inner_length),
        position=(0.0, 0.0),
        elements=_player_box_elements(hero_svg, hero_rot),
        allocates={
            "Villager Figures": 20,
            "Hero Figures": 1,
            "Favour Discs": 5,
            "Fellowship Building Tiles": 6,
            "Score Tokens": 1,
            "100+ Score Tokens": 1,
        },
    )

material_placements = [
    (
        "MaterialBoxFood",
        "Food",
        "red",
        "berry.svg",
        (0.0, PLAYER_BOX_LENGTH, PLAYER_BOX_HEIGHT * 2.0),
        "Food Tokens",
        35,
    ),
    (
        "MaterialBoxStone",
        "Stone",
        "gray",
        "stone.svg",
        (0.0, PLAYER_BOX_LENGTH + MATERIAL_BOX_LENGTH, PLAYER_BOX_HEIGHT * 2.0),
        "Stone Tokens",
        30,
    ),
    ("MaterialBoxHoney", "Honey", "gold", "honey.svg", (0.0, 0.0, PLAYER_BOX_HEIGHT * 3.0), "Honey Tokens", 20),
    (
        "MaterialBoxWood",
        "Wood",
        "saddlebrown",
        "wood.svg",
        (0.0, MATERIAL_BOX_LENGTH, PLAYER_BOX_HEIGHT * 3.0),
        "Wood Tokens",
        35,
    ),
]

for label, text, color_name, logo_file, pos, comp_name, comp_count in material_placements:
    project.box(
        BoxType.CAP,
        label,
        size=(MATERIAL_BOX_WIDTH, MATERIAL_BOX_LENGTH, MATERIAL_BOX_HEIGHT),
        position=pos,
        lid=_ember_lid(text, color_name, logo_path=str(ASSETS / logo_file), logo_size=15.0),
    ).compartment("Tokens", cut=FingerCut.SCOOP, component=comp_name, count=comp_count)

# ── Column 1: Main Card Boxes (X = 98 .. 196) ─────────────────────
card_configs = [
    ("CardBoxFavor", "Favors", "royalblue", 0, "Favour Cards", 88),
    ("CardBoxHero", "Heroes", "darkorange", 1, "Hero Cards", 47),
    ("CardBoxSolo", "Solo", "darkgreen", 2, "Solo Cards", 64),
]

for label, text, color_name, row_idx, comp_name, comp_count in card_configs:
    project.box(
        BoxType.SLIDING,
        label,
        size=(CARD_BOX_WIDTH, CARD_BOX_LENGTH, CARD_BOX_HEIGHT),
        position=(PLAYER_BOX_WIDTH, CARD_BOX_LENGTH * row_idx, 0.0),
        lid=_ember_lid(text, color_name),
    ).compartment("Cards", cut=FingerCut.SCOOP, component=comp_name, count=comp_count)

# ── Column 2: 5 Player Card Boxes & Common Box (X = 196 .. 286) ───
col2_x = PLAYER_BOX_WIDTH + CARD_BOX_WIDTH

player_card_configs = [
    ("CardBoxPlayerBlack", "Player Black", "black"),
    ("CardBoxPlayerBlue", "Player Blue", "navy"),
    ("CardBoxPlayerYellow", "Player Yellow", "gold"),
    ("CardBoxPlayerGrey", "Player Grey", "gray"),
    ("CardBoxPlayerRed", "Player Red", "darkred"),
]

for layer_idx, (label, text, color_name) in enumerate(player_card_configs):
    project.box(
        BoxType.SLIDING,
        label,
        size=(PLAYER_CARD_BOX_WIDTH, PLAYER_CARD_BOX_LENGTH, PLAYER_CARD_BOX_HEIGHT),
        position=(col2_x, 0.0, PLAYER_CARD_BOX_HEIGHT * layer_idx),
        lid=_ember_lid(text, color_name),
    ).compartment(
        "Cards",
        cut=FingerCut.SCOOP,
        allocates={"Fellowship Deck Cards": 6, "Player Reference Cards": 1},
    )

common_inner_width = COMMON_BOX_WIDTH - wall_thickness * 2.0  # 84.0mm
common_inner_length = COMMON_BOX_LENGTH - wall_thickness * 2.0  # 182.0mm


def _common_box_elements() -> tuple[CompartmentElement, ...]:
    """Build 5 common hex tile stacks + trophy marker circular well + trophy tile stack with finger scoops."""
    elems: list[CompartmentElement] = []
    hex_y_span = hex_size / math.cos(math.radians(30.0))  # 44.456mm
    hex_depth = cardboard_token_thickness * 10.0 - 0.5  # 19.5mm
    bite_d = 14.0
    for i in range(2):
        cx = 21.0 + 42.0 * i
        for j in range(3):
            if j == 2 and i == 1:
                continue
            cy = 29.25 + 48.5 * j
            elems.append(
                CompartmentElement(
                    shape=ElementShape.HEXAGON,
                    size=(hex_size, hex_size),
                    rotation=30.0,
                    offset=(cx - hex_size / 2.0, cy - hex_y_span / 2.0),
                    depth=hex_depth,
                    pull_out=False,
                    label=f"CommonHex_{i}_{j}",
                )
            )
            bite_y = max(bite_d / 2.0, min(common_inner_length - bite_d / 2.0, cy - hex_y_span / 2.0))
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(bite_d, bite_d),
                    offset=(cx - bite_d / 2.0, bite_y - bite_d / 2.0),
                    depth=hex_depth,
                    pull_out=False,
                    label=f"CommonHexBite_{i}_{j}",
                )
            )
    # Trophy wooden marker circular well + left/right scoops
    tm_cx = common_inner_width * 0.75
    tm_cy = common_inner_length - wood_token_diameter / 2.0 - 7.0 - hex_size
    tm_depth = wood_token_thickness + 0.5
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(wood_token_diameter, wood_token_diameter),
            offset=(tm_cx - wood_token_diameter / 2.0, tm_cy - wood_token_diameter / 2.0),
            depth=tm_depth,
            pull_out=False,
            label="TrophyMarker",
        )
    )
    for s_idx, bdx in enumerate((-wood_token_diameter / 2.0, wood_token_diameter / 2.0)):
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(16.0, 16.0),
                offset=(tm_cx + bdx - 8.0, tm_cy - 8.0),
                depth=tm_depth,
                pull_out=False,
                label=f"TrophyMarkerBite_{s_idx + 1}",
            )
        )
    # Trophy tile stack (back center) + left/right finger scoops
    tr_l, tr_w = 36.0, 26.0
    tr_depth = cardboard_token_thickness * 6.0 - 0.5  # 11.5mm
    tr_x = (common_inner_width - tr_l) / 2.0
    tr_y = common_inner_length - tr_w - 2.0
    elems.append(
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(tr_l, tr_w),
            offset=(tr_x, tr_y),
            depth=tr_depth,
            pull_out=False,
            label="TrophyTiles",
        )
    )
    for s_idx, bx in enumerate((tr_x, tr_x + tr_l)):
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(24.0, 24.0),
                offset=(bx - 12.0, tr_y + tr_w / 2.0 - 12.0),
                depth=tr_depth,
                pull_out=False,
                label=f"TrophyBite_{s_idx + 1}",
            )
        )
    return tuple(elems)


project.box(
    BoxType.CAP,
    "CommonBox",
    size=(COMMON_BOX_WIDTH, COMMON_BOX_LENGTH, COMMON_BOX_HEIGHT),
    position=(col2_x, PLAYER_CARD_BOX_LENGTH, 0.0),
    lid=_ember_lid("Trophy", "saddlebrown"),
).compartment(
    "CommonHexesAndTrophies",
    size=(common_inner_width, common_inner_length),
    position=(0.0, 0.0),
    elements=_common_box_elements(),
    allocates={
        "General Building Tiles": 50,
        "Trophy Tokens": 6,
        "Tracker Disc": 1,
    },
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
