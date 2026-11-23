#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Magical Athlete board game organizer.

Ports examples/magical_athlete.scad to the pyboxbuilder Project API.
Organizes athlete character cards, dice, race pieces/standees,
gold/silver award medals, and the Big Baby miniature with automated spacers.
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
    else ROOT / "boxes" / "magical_athlete" / "assets"
)

# ── Game Box Dimensions ───────────────────────────────────────────
box_width = 184.0
box_length = 294.0
box_height = 45.0
board_thickness = 7.0
usable_height = box_height - board_thickness  # 38.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

card_width = 67.0
card_length = 90.0

dice_size = 21.0
cardboard_thickness = 2.2
piece_thickness = 11.0
piece_width = 24.0
piece_length = 38.0
tall_piece_length = 52.0
tall_piece_width = 18.0
big_baby_width = 39.0
big_baby_length = 35.5

gold_height = (25.0, 23.0, 21.0)
gold_width = (32.0, 29.0, 26.0)
silver_diameter = (21.75, 18.5, 15.5)
silver_tag_diameter = (26.0, 23.5, 19.5)

card_box_width = card_length + wall_thickness * 2.0   # 96.0mm
card_box_length = card_width + wall_thickness * 2.0   # 73.0mm
card_box_height = usable_height                        # 38.0mm

dice_box_width = box_width - card_box_width           # 88.0mm
dice_box_length = card_box_length                     # 73.0mm
dice_box_height = dice_size + floor_thickness + lid_thickness + 1.0  # 26.0mm
award_box_height = usable_height - dice_box_height    # 12.0mm

big_baby_box_width = big_baby_length + 20.0 + wall_thickness * 2.0  # 61.5mm
big_baby_box_length = big_baby_width + wall_thickness * 2.0 + 1.0  # 46.0mm

piece_box_width = box_width                                                 # 184.0mm
piece_box_length = box_length - card_box_length - big_baby_box_length       # 175.0mm
piece_box_height = usable_height / 2.0                                      # 19.0mm

award_tokens_width = 50.0
award_tokens_length = big_baby_box_length                                   # 46.0mm
award_tokens_height = usable_height / 2.0                                   # 19.0mm

project = Project(
    "MagicalAthlete",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

ATHLETE_PATTERN = PatternBuilder(PatternType.DICE)
ATHLETE_FONT = "Futura:style=Bold"

# ── 1. Athlete Cards Box ──────────────────────────────────────────
project.box(
    BoxType.SLIDING,
    "AthleteCardsBox",
    size=(card_box_width, card_box_length, card_box_height),
    lid=LidBuilder(
        text="Athletes",
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.PILL,
        label_finial=LabelFinial.TRIPLE_DOT,
        font=ATHLETE_FONT,
        pattern=ATHLETE_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkblue"),
    ),
    expandable=False,
).compartment(
    "Cards",
    cut=FingerCut.SCOOP,
)

# ── 2. Dice Box & Award Medal Box ─────────────────────────────────
dice_inner_w = dice_box_width - wall_thickness * 2.0  # 82.0mm
dice_inner_l = dice_box_length - wall_thickness * 2.0  # 67.0mm
dice_inner_h = dice_box_height - floor_thickness - lid_thickness  # 22.0mm
dice_elements: tuple[CompartmentElement, ...] = (
    # Stepped upper finger-lift basin above dice mid-height
    CompartmentElement(
        shape=ElementShape.ROUNDED_RECT,
        size=(dice_inner_w, dice_inner_l),
        offset=(0.0, 0.0),
        depth=dice_inner_h - dice_size / 2.0,
        corner_radius=8.0,
        pull_out=False,
        label="DiceUpperBasin",
    ),
    # 3x2 grid of 21mm dice pockets
    *(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(dice_size, dice_size),
            offset=(
                (col - 1.5) * (dice_size + 1.0) + dice_inner_w / 2.0,
                (row - 1.0) * (dice_size + 1.0) + dice_inner_l / 2.0,
            ),
            depth=dice_inner_h,
            corner_radius=1.0,
            pull_out=False,
            label=f"Die_{col}_{row}",
        )
        for col in range(3)
        for row in range(2)
    ),
)

project.box(
    BoxType.CAP,
    "DiceBox",
    size=(dice_box_width, dice_box_length, dice_box_height),
    lid=LidBuilder(
        text="Dice",
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.PILL,
        label_finial=LabelFinial.TRIPLE_DOT,
        font=ATHLETE_FONT,
        pattern=ATHLETE_PATTERN,
        text_color=Color("white"),
        frame_color=Color("crimson"),
        logo=str(ASSETS / "dice.svg"),
        logo_color=Color("white"),
        logo_position="left",
        label_logo_size_mm=16.0,
    ),
).compartment(
    "Dice",
    size=(dice_inner_w, dice_inner_l),
    position=(0.0, 0.0),
    elements=dice_elements,
)

# SlipoverBox interior deducts wall_thickness + slipover lip (9.4mm total per axis)
award_inner_w = 78.6
award_inner_l = 63.6


def _award_medal_elements() -> tuple[CompartmentElement, ...]:
    """Build 3 GoldMedal trophy silhouettes + 3 SilverMedal ribboned circles + finger scoops."""
    elems: list[CompartmentElement] = []
    for i in range(3):
        depth = cardboard_thickness * (2.0 if i == 1 else 1.0)
        # GoldMedal (rotated 90° so footprint is (gold_height[i], gold_width[i]))
        g_cx = (gold_height[0] + 1.0) * (i + 0.5)
        g_cy = gold_width[0] / 2.0
        elems.append(
            CompartmentElement(
                shape=ElementShape.SVG,
                shape_file=str(ASSETS / "gold_medal.svg"),
                size=(gold_width[i], gold_height[i]),
                rotation=90.0,
                offset=(g_cx - gold_height[i] / 2.0, g_cy - gold_width[i] / 2.0),
                depth=depth,
                pull_out=False,
                label=f"GoldMedal_{i + 1}",
            )
        )
        if i == 1:
            scoop_d = 16.0
            dx = gold_width[i] / 2.0 - cardboard_thickness * 2.0
            elems.append(
                CompartmentElement(
                    shape=ElementShape.SPHERE_SCOOP,
                    size=(scoop_d, scoop_d),
                    offset=(g_cx + dx - scoop_d / 2.0, g_cy - scoop_d / 2.0),
                    depth=depth,
                    pull_out=False,
                    label="GoldMedal2ScoopRight",
                )
            )
            elems.append(
                CompartmentElement(
                    shape=ElementShape.SPHERE_SCOOP,
                    size=(scoop_d, scoop_d),
                    offset=(g_cx - dx - scoop_d / 2.0, g_cy - scoop_d / 2.0),
                    depth=depth,
                    pull_out=False,
                    label="GoldMedal2ScoopLeft",
                )
            )
        # SilverMedal (scaled to (silver_w, silver_h) keeping ribbons inside award_inner_l)
        s_scale = silver_diameter[i] / silver_diameter[0]
        s_w = 23.11 * s_scale
        s_h = 24.81 * s_scale
        s_cx = (gold_height[0] + 1.0) * (i + 0.5)
        s_y0 = award_inner_l - s_h
        elems.append(
            CompartmentElement(
                shape=ElementShape.SVG,
                shape_file=str(ASSETS / "silver_medal.svg"),
                size=(s_w, s_h),
                offset=(s_cx - s_w / 2.0, s_y0),
                depth=depth,
                pull_out=False,
                label=f"SilverMedal_{i + 1}",
            )
        )
        s_scoop_d = 14.0
        elems.append(
            CompartmentElement(
                shape=ElementShape.SPHERE_SCOOP,
                size=(s_scoop_d, s_scoop_d),
                offset=(s_cx - s_scoop_d / 2.0, max(0.0, s_y0 - s_scoop_d / 2.0 + cardboard_thickness)),
                depth=depth,
                pull_out=False,
                label=f"SilverMedalScoop_{i + 1}",
            )
        )
    return tuple(elems)


project.box(
    BoxType.SLIPOVER,
    "AwardMedalBox",
    size=(dice_box_width, dice_box_length, award_box_height),
    lid=LidBuilder(
        text="Awards",
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.PILL,
        label_finial=LabelFinial.TRIPLE_DOT,
        font=ATHLETE_FONT,
        pattern=ATHLETE_PATTERN,
        text_color=Color("white"),
        frame_color=Color("gold"),
        logo=str(ASSETS / "gold_medal.svg"),
        logo_color=Color("white"),
        logo_position="left",
        label_logo_size_mm=16.0,
    ),
).compartment(
    "Medals",
    size=(award_inner_w, award_inner_l),
    position=(0.0, 0.0),
    elements=_award_medal_elements(),
)

# ── 3. Athlete Character Pieces (2 stacked full-length trays) ─────
piece_inner_w = piece_box_width - wall_thickness * 2.0  # 178.0mm
piece_inner_l = piece_box_length - wall_thickness * 2.0  # 169.0mm
piece_inner_h = piece_box_height - floor_thickness - lid_thickness  # 15.0mm
piece_basin_depth = piece_inner_h - (piece_thickness / 2.0 + 1.0)  # 8.5mm


def _athlete_piece_elements(tray_index: int) -> tuple[CompartmentElement, ...]:
    """Build stepped upper basin + 20+1 (tray 1) or 14 (tray 2) athlete piece pockets."""
    elems: list[CompartmentElement] = [
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(piece_inner_w, piece_inner_l),
            offset=(0.0, 0.0),
            depth=piece_basin_depth,
            corner_radius=8.0,
            pull_out=False,
            label="PieceUpperBasin",
        )
    ]
    rows = 5 if tray_index == 0 else 4
    for col in range(4):
        for row in range(rows):
            if tray_index == 1 and row == 3 and col >= 2:
                continue
            elems.append(
                CompartmentElement(
                    shape=ElementShape.ROUNDED_RECT,
                    size=(piece_length, piece_width),
                    offset=(col * (piece_length + 2.0) + 10.0, row * (piece_width + 2.0) + 7.0),
                    depth=piece_inner_h,
                    corner_radius=1.0,
                    pull_out=False,
                    label=f"Athlete_{col}_{row}",
                )
            )
    if tray_index == 0:
        elems.append(
            CompartmentElement(
                shape=ElementShape.ROUNDED_RECT,
                size=(tall_piece_length, tall_piece_width),
                offset=(62.0, piece_inner_l - tall_piece_width - 12.0),
                depth=piece_inner_h,
                corner_radius=1.0,
                pull_out=False,
                label="TallAthlete",
            )
        )
    return tuple(elems)


for i in range(2):
    project.box(
        BoxType.CAP,
        f"AthletePiecesBox_{i + 1}",
        size=(piece_box_width, piece_box_length, piece_box_height),
        lid=LidBuilder(
            text=f"Athletes {i + 1}",
            label_mode=LabelMode.FRAMED,
            label_shape=LabelShape.PILL,
            label_finial=LabelFinial.TRIPLE_DOT,
            font=ATHLETE_FONT,
            pattern=ATHLETE_PATTERN,
            text_color=Color("white"),
            frame_color=Color("darkorange"),
        ),
    ).compartment(
        f"AthletePieces_{i + 1}",
        size=(piece_inner_w, piece_inner_l),
        position=(0.0, 0.0),
        elements=_athlete_piece_elements(i),
    )

# ── 4. Big Baby Standee Box ───────────────────────────────────────
project.box(
    BoxType.CAP,
    "BigBabyBox",
    size=(big_baby_box_width, big_baby_box_length, usable_height),
    lid=LidBuilder(
        text="Big Baby",
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.PILL,
        label_finial=LabelFinial.TRIPLE_DOT,
        font=ATHLETE_FONT,
        pattern=ATHLETE_PATTERN,
        text_color=Color("white"),
        frame_color=Color("purple"),
    ),
).compartment(
    "BigBaby",
    cut=FingerCut.SCOOP,
)

# ── 5. Award Tokens Boxes (2 stacked: "1" and "3") ────────────────
for token_val in ("1", "3"):
    project.box(
        BoxType.CAP,
        f"AwardTokensBox_{token_val}",
        size=(award_tokens_width, award_tokens_length, award_tokens_height),
        lid=LidBuilder(
            text=f"Awards {token_val}",
            label_mode=LabelMode.FRAMED,
            label_shape=LabelShape.PILL,
            label_finial=LabelFinial.TRIPLE_DOT,
            font=ATHLETE_FONT,
            pattern=ATHLETE_PATTERN,
            text_color=Color("white"),
            frame_color=Color("saddlebrown"),
            logo=str(ASSETS / "trophy.svg"),
            logo_color=Color("white"),
            logo_position="left",
            label_logo_size_mm=14.0,
        ),
    ).compartment(
        f"Tokens_{token_val}",
        cut=FingerCut.SCOOP,
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
