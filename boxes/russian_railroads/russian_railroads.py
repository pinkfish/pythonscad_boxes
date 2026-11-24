#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Russian Railroads board game organizer.

Ports examples/russian_railroads.scad to the pyboxbuilder Project API.
Organizes player wooden workers, track markers, train tiles, engineer tiles,
cards, and ruble tokens with automated spacers.
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
    else ROOT / "boxes" / "russian_railroads" / "assets"
)

# ── Box & Board Dimensions ────────────────────────────────────────
box_width = 219.0
box_length = 308.0
box_height = 70.0

board_thickness = 15.0
usable_height = box_height - board_thickness  # 55.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

player_box_width = (box_width - 2.0) / 2.0  # 108.5mm
player_box_length = 80.5
player_box_height = usable_height / 3.0     # 18.33mm

card_box_width = 18.0
card_box_length = 105.0
card_box_height = usable_height

train_box_width = box_width - 2.0 - card_box_width  # 199.0mm
train_box_length = 105.0
train_box_height = 17.0
engineer_box_height = 13.0
track_box_height = usable_height - train_box_height - engineer_box_height  # 25.0mm

project = Project(
    "RussianRailroads",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
    box_defaults={"expandable": False},
)

RR_PATTERN = PatternBuilder(PatternType.STEPPED_CUBE)
RR_FONT = "Georgia:style=Bold"


def _lid(
    text: str,
    frame_color: str,
    *,
    text_color: str = "white",
    finial: LabelFinial = LabelFinial.SPEAR,
    logo: str | None = None,
    logo_size_mm: float = 16.0,
) -> LidBuilder:
    return LidBuilder(
        text=text,
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.CORNER_STUD,
        label_finial=finial,
        font=RR_FONT,
        pattern=RR_PATTERN,
        text_color=Color(text_color),
        frame_color=Color(frame_color),
        logo=logo,
        logo_color=Color(text_color) if logo else None,
        logo_position="left",
        label_logo_size_mm=logo_size_mm if logo else None,
    )

# ── 1. Player, Extra Tokens & Currency Section ────────────────────
tile_thickness = 2.0
worker_width = 17.5
worker_length = 24.0
worker_thickness = 10.0
industry_hex = 11.0
industry_thickness = 10.0
pawn_width = 21.5
pawn_length = 18.5
pawn_thickness = 10.0
question_token_diameter = 23.0
kiev_medal_width = 24.5
kiev_medal_length = 39.0
bonus_train_tile_width = 26.0
bonus_train_tile_length = 45.0
doubler_width = 21.0
doubler_length = 23.5
extra_score_track_width = 19.0
extra_score_track_length = 32.5

player_inner_width = player_box_width - wall_thickness * 2.0  # 102.5mm
player_inner_length = player_box_length - wall_thickness * 2.0  # 74.5mm


def _player_box_elements() -> tuple[CompartmentElement, ...]:
    """Build PlayerBox wells: 8 workers, 2 industry hexes, 2 pawns, question token disc well, stepped bonus tiles."""
    elems: list[CompartmentElement] = []
    # Top grab-dip over workers, hexes, and pawns
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=((worker_width + 1.0) * 4.0 + 2.0, player_inner_length),
            offset=(0.0, 0.0),
            corner_radius=5.0,
            depth=5.0,
            pull_out=False,
            label="WorkerGrabDip",
        )
    )
    # 8 Workers (2 rows of 4)
    w_depth = worker_thickness + 0.5
    for j in range(4):
        wx = (worker_width + 1.0) * j
        elems.append(
            CompartmentElement(
                shape=ElementShape.RECT,
                size=(worker_width, worker_length),
                offset=(wx, 0.0),
                depth=w_depth,
                pull_out=False,
                label=f"WorkerFront_{j + 1}",
            )
        )
        elems.append(
            CompartmentElement(
                shape=ElementShape.RECT,
                size=(worker_width, worker_length),
                offset=(wx, player_inner_length - worker_length),
                depth=w_depth,
                pull_out=False,
                label=f"WorkerBack_{j + 1}",
            )
        )
    # 2 Industry hex wells (rotated 30 deg: footprint = 11.0 x 12.702)
    hex_h = industry_hex / 0.8660254037844386
    for idx, hx_c in enumerate((industry_hex, industry_hex * 2.0 + 2.0)):
        elems.append(
            CompartmentElement(
                shape=ElementShape.HEXAGON,
                size=(industry_hex, industry_hex),
                rotation=30.0,
                offset=(hx_c - industry_hex / 2.0, player_inner_length / 2.0 - hex_h / 2.0),
                depth=industry_thickness + 0.5,
                pull_out=False,
                label=f"IndustryHex_{idx + 1}",
            )
        )
    # 2 Pawn silhouette wells (facing opposite directions)
    p_depth = pawn_thickness + 0.5
    elems.append(
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "pawn.svg"),
            size=(pawn_width, pawn_length),
            rotation=180.0,
            offset=(industry_hex * 4.0 - pawn_width / 2.0, player_inner_length / 2.0 - pawn_length / 2.0),
            depth=p_depth,
            pull_out=False,
            label="Pawn_1",
        )
    )
    elems.append(
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "pawn.svg"),
            size=(pawn_width, pawn_length),
            rotation=0.0,
            offset=(
                industry_hex * 4.0 + pawn_width - 3.0 - pawn_width / 2.0,
                player_inner_length / 2.0 - pawn_length / 2.0,
            ),
            depth=p_depth,
            pull_out=False,
            label="Pawn_2",
        )
    )
    # Circular Question Token stack well (7 tiles = 14.2mm) + side finger bite
    q_depth = 7.0 * tile_thickness + 0.2
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(question_token_diameter, question_token_diameter),
            offset=(player_inner_width - question_token_diameter, 0.0),
            depth=q_depth,
            pull_out=False,
            label="QuestionTokens",
        )
    )
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(12.0, 12.0),
            offset=(player_inner_width - question_token_diameter - 6.0, question_token_diameter / 2.0 - 6.0),
            depth=q_depth,
            pull_out=False,
            label="QuestionTokensBite",
        )
    )
    # Stepped Bonus Train Tile (upper) over Kiev Medal (deeper) + finger scoop
    bonus_cx = player_inner_width - bonus_train_tile_width / 2.0
    bonus_cy = player_inner_length - bonus_train_tile_length / 2.0 - 2.0
    elems.append(
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(bonus_train_tile_width, bonus_train_tile_length),
            offset=(bonus_cx - bonus_train_tile_width / 2.0, bonus_cy - bonus_train_tile_length / 2.0),
            depth=tile_thickness,
            pull_out=False,
            label="BonusTrainTile",
        )
    )
    elems.append(
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(kiev_medal_width, kiev_medal_length),
            offset=(bonus_cx - kiev_medal_width / 2.0, bonus_cy - kiev_medal_length / 2.0),
            depth=tile_thickness * 2.0 + 0.5,
            pull_out=False,
            label="KievMedal",
        )
    )
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(16.0, 16.0),
            offset=(bonus_cx - 8.0, bonus_cy - bonus_train_tile_length / 2.0 - 4.0),
            depth=tile_thickness * 2.0 + 0.5,
            pull_out=False,
            label="BonusTileScoop",
        )
    )
    return tuple(elems)


def _extra_tokens_elements() -> tuple[CompartmentElement, ...]:
    """Build ExtraTokensBox wells: 2 blue workers, 1 black worker, 6 doubler stacks, 2 bonus track stacks."""
    elems: list[CompartmentElement] = []
    # 2 Blue workers (front-left) + 1 Black worker (back-left)
    w_depth = worker_thickness + 1.5
    elems.append(
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(worker_width, worker_length),
            offset=(0.0, 0.0),
            depth=w_depth,
            pull_out=True,
            label="BlueWorker_1",
        )
    )
    elems.append(
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(worker_width, worker_length),
            offset=(worker_width + 2.0, 0.0),
            depth=w_depth,
            pull_out=True,
            label="BlueWorker_2",
        )
    )
    elems.append(
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(worker_width, worker_length),
            offset=(worker_width / 2.0, player_inner_length - worker_length),
            depth=w_depth,
            pull_out=True,
            label="BlackWorker",
        )
    )
    # 6 Doubler (x2) tile stacks (2 rows x 3 cols on right)
    d_depth = tile_thickness * 4.0 + 0.5
    d_x0 = 37.5
    for j in range(3):
        dx = d_x0 + j * (doubler_width + 1.0)
        elems.append(
            CompartmentElement(
                shape=ElementShape.RECT,
                size=(doubler_width, doubler_length),
                offset=(dx, 0.0),
                depth=d_depth,
                pull_out=True,
                label=f"DoublerFront_{j + 1}",
            )
        )
        elems.append(
            CompartmentElement(
                shape=ElementShape.RECT,
                size=(doubler_width, doubler_length),
                offset=(dx, player_inner_length - doubler_length),
                depth=d_depth,
                pull_out=True,
                label=f"DoublerBack_{j + 1}",
            )
        )
    # 2 Bonus score track tile stacks (middle row, left & right)
    mid_y = (player_inner_length - extra_score_track_width) / 2.0
    elems.append(
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(extra_score_track_length, extra_score_track_width),
            offset=(0.0, mid_y),
            depth=d_depth,
            pull_out=True,
            label="BonusTrack_1",
        )
    )
    elems.append(
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(extra_score_track_length, extra_score_track_width),
            offset=(player_inner_width - extra_score_track_length, mid_y),
            depth=d_depth,
            pull_out=True,
            label="BonusTrack_2",
        )
    )
    return tuple(elems)


for name, title, color_name in (
    ("PlayerBox_Red", "Red", "red"),
    ("PlayerBox_Blue", "Blue", "navy"),
    ("PlayerBox_Green", "Green", "forestgreen"),
    ("PlayerBox_Yellow", "Yellow", "gold"),
):
    project.box(
        BoxType.CAP,
        name,
        size=(player_box_width, player_box_length, player_box_height),
        lid=_lid(
            title,
            color_name,
            text_color="black" if color_name in ("gold", "yellow") else "white",
            logo=str(ASSETS / "pawn.svg"),
            logo_size_mm=15.0,
        ),
    ).compartment(
        "PlayerBits",
        size=(player_inner_width, player_inner_length),
        position=(0.0, 0.0),
        elements=_player_box_elements(),
    )

project.box(
    BoxType.CAP,
    "ExtraTokensBox",
    size=(player_box_width, player_box_length, player_box_height),
    lid=_lid("Tokens", "dimgray"),
).compartment(
    "ExtraTokens",
    size=(player_inner_width, player_inner_length),
    position=(0.0, 0.0),
    elements=_extra_tokens_elements(),
)

project.box(
    BoxType.CAP,
    "MoneyBox",
    size=(player_box_width, player_box_length, player_box_height),
    lid=_lid(
        "Rubels",
        "goldenrod",
        logo=str(ASSETS / "coin.svg"),
        logo_size_mm=15.0,
    ),
).compartment("Rubels", cut=FingerCut.SCOOP)

# ── 2. Train, Engineer, Track & Card Section ──────────────────────
project.box(
    BoxType.SLIDING,
    "CardBox",
    size=(card_box_width, card_box_length, card_box_height),
    lid=_lid("Cards", "peru", finial=LabelFinial.NONE),
).compartment(
    "Cards",
    cut=FingerCut.SCOOP,
)

train_inner_width = train_box_width - wall_thickness * 2.0  # 193.0mm
train_inner_length = train_box_length - wall_thickness * 2.0  # 99.0mm
train_tile_width = 31.0
train_tile_length = 58.0
start_tile_width = 41.0
start_tile_length = 76.0


def _train_box_elements() -> tuple[CompartmentElement, ...]:
    """Build 3x3 pointed TrainTile wells + shallow Start tile recess."""
    elems: list[CompartmentElement] = []
    t_depth = tile_thickness * 5.0 + 0.5  # 10.5mm
    row_ys = (0.0, (train_inner_length - train_tile_width) / 2.0, train_inner_length - train_tile_width)
    for i in range(3):
        tx = 2.0 + (train_tile_length + 8.0) * i
        for j, ty in enumerate(row_ys):
            elems.append(
                CompartmentElement(
                    shape=ElementShape.SVG,
                    shape_file=str(ASSETS / "train_tile.svg"),
                    size=(train_tile_length, train_tile_width),
                    offset=(tx, ty),
                    depth=t_depth,
                    pull_out=False,
                    label=f"TrainTile_{i * 3 + j + 1}",
                )
            )
            if j < 2:
                # Finger bite between adjacent rows
                bite_d = 15.0
                elems.append(
                    CompartmentElement(
                        shape=ElementShape.CIRCLE,
                        size=(bite_d, bite_d),
                        offset=(tx + train_tile_length / 2.0 - bite_d / 2.0, ty + train_tile_width - bite_d / 2.0),
                        depth=t_depth,
                        pull_out=False,
                        label=f"TrainBite_{i}_{j}",
                    )
                )
    # Shallow Start tile recess centered over middle column
    elems.append(
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(start_tile_length, start_tile_width),
            offset=(train_tile_length + 35.0 - start_tile_length / 2.0, (train_inner_length - start_tile_width) / 2.0),
            depth=tile_thickness + 0.5,
            pull_out=False,
            label="StartTile",
        )
    )
    return tuple(elems)


project.box(
    BoxType.CAP,
    "TrainBox",
    size=(train_box_width, train_box_length, train_box_height),
    lid=_lid(
        "Trains",
        "darkred",
        logo=str(ASSETS / "train_tile.svg"),
        logo_size_mm=16.0,
    ),
).compartment(
    "TrainTiles",
    size=(train_inner_width, train_inner_length),
    position=(0.0, 0.0),
    elements=_train_box_elements(),
)

engineer_width = 36.0
engineer_length = 81.5


def _engineer_box_elements() -> tuple[CompartmentElement, ...]:
    """Build 5 chamfered EngineerTile wells with front finger bites."""
    elems: list[CompartmentElement] = []
    e_depth = tile_thickness * 3.0 + 0.5  # 6.5mm
    ey = (train_inner_length - engineer_length) / 2.0  # 8.75mm
    bite_d = 16.0
    for i in range(5):
        ex = 3.0 + (engineer_width + 2.5) * i
        elems.append(
            CompartmentElement(
                shape=ElementShape.SVG,
                shape_file=str(ASSETS / "engineer_tile.svg"),
                size=(engineer_width, engineer_length),
                rotation=180.0,
                offset=(ex, ey),
                depth=e_depth,
                pull_out=False,
                label=f"EngineerTile_{i + 1}",
            )
        )
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(bite_d, bite_d),
                offset=(ex + engineer_width / 2.0 - bite_d / 2.0, ey - bite_d / 2.0),
                depth=e_depth,
                pull_out=False,
                label=f"EngineerBite_{i + 1}",
            )
        )
    return tuple(elems)


project.box(
    BoxType.CAP,
    "EngineerBox",
    size=(train_box_width, train_box_length, engineer_box_height),
    lid=_lid(
        "Engineers",
        "darkslategray",
        logo=str(ASSETS / "engineer_tile.svg"),
        logo_size_mm=16.0,
    ),
).compartment(
    "EngineerTiles",
    size=(train_inner_width, train_inner_length),
    position=(0.0, 0.0),
    elements=_engineer_box_elements(),
)

rail_white_length = 15.0
rail_white_width = 17.0
rail_white_thickness = 16.5
track_inner_height = track_box_height - floor_thickness - lid_thickness  # 21.0mm


def _track_box_elements() -> tuple[CompartmentElement, ...]:
    """Build 4 wooden track bins (Grey, Brown, Black, Natural) + 4 White I-beam rail wells."""
    elems: list[CompartmentElement] = []
    section_w = (train_inner_width - 5.0 - rail_white_width - 2.0) / 4.0  # 42.25mm
    for i, label in enumerate(("Grey", "Brown", "Black", "Natural")):
        elems.append(
            CompartmentElement(
                shape=ElementShape.RECT,
                size=(section_w, train_inner_length - 1.0),
                offset=(0.5 + (section_w + 2.0) * i, 0.5),
                depth=track_inner_height,
                bottom_rounding=4.0,
                pull_out=False,
                label=f"TrackBin_{label}",
            )
        )
    # Recessed grab-shelf over the 4 white track wells on the right
    white_x = 0.5 + (section_w + 2.0) * 4.0  # 177.5mm
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(train_inner_width - white_x + 1.0, train_inner_length - 1.0),
            offset=(white_x - 1.5, 0.5),
            corner_radius=5.0,
            depth=5.8,
            pull_out=False,
            label="WhiteTrackShelf",
        )
    )
    for i in range(4):
        elems.append(
            CompartmentElement(
                shape=ElementShape.SVG,
                shape_file=str(ASSETS / "white_track.svg"),
                size=(rail_white_length, rail_white_width),
                offset=(white_x, 4.0 + (rail_white_width + 5.0) * i),
                depth=rail_white_thickness + 0.5,
                pull_out=False,
                label=f"WhiteTrack_{i + 1}",
            )
        )
    return tuple(elems)


project.box(
    BoxType.CAP,
    "TrackBox",
    size=(train_box_width, train_box_length, track_box_height),
    lid=_lid(
        "Tracks",
        "saddlebrown",
        logo=str(ASSETS / "white_track.svg"),
        logo_size_mm=16.0,
    ),
).compartment(
    "WoodenTracks",
    size=(train_inner_width, train_inner_length),
    position=(0.0, 0.0),
    elements=_track_box_elements(),
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
