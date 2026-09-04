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

from pybosl2 import Color

from pyboxbuilder import (
    BoxType,
    FingerCut,
    LabelMode,
    LidBuilder,
    PatternBuilder,
    PatternType,
    Project,
    run,
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
piece_thickness = 11.0
big_baby_width = 39.0
big_baby_length = 35.5

card_box_width = card_length + wall_thickness * 2.0   # 96.0mm
card_box_length = card_width + wall_thickness * 2.0   # 73.0mm
card_box_height = usable_height                        # 38.0mm

dice_box_width = box_width - card_box_width           # 88.0mm
dice_box_length = card_box_length                     # 73.0mm
dice_box_height = dice_size + floor_thickness + lid_thickness + 1.0  # 26.0mm
award_box_height = usable_height - dice_box_height    # 12.0mm

big_baby_box_width = big_baby_length + 20.0 + wall_thickness * 2.0  # 61.5mm
big_baby_box_length = big_baby_width + wall_thickness * 2.0 + 1.0  # 46.0mm

piece_box_length = (box_length - card_box_length - big_baby_box_length) / 2.0  # 87.5mm
piece_box_height = usable_height / 2.0                                          # 19.0mm

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

ATHLETE_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Athlete Cards Box ──────────────────────────────────────────
project.box(
    BoxType.SLIDING,
    "AthleteCardsBox",
    size=(card_box_width, card_box_length, card_box_height),
    lid=LidBuilder(
        text="Athlete Cards",
        label_mode=LabelMode.FRAMED,
        pattern=ATHLETE_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkblue"),
    ),
    position=(0.0, 0.0, 0.0),
    no_rotate=True,
).compartment(
    "Cards",
    depth=card_box_height - lid_thickness,
    cut=FingerCut.SCOOP,
)

# ── 2. Dice Box & Award Medal Box (Stacked) ───────────────────────
project.box(
    BoxType.CAP,
    "DiceBox",
    size=(dice_box_width, dice_box_length, dice_box_height),
    lid=LidBuilder(
        text="Dice",
        label_mode=LabelMode.FRAMED,
        pattern=ATHLETE_PATTERN,
        text_color=Color("white"),
        frame_color=Color("crimson"),
    ),
    position=(card_box_width, 0.0, 0.0),
    no_rotate=True,
).compartment(
    "Dice",
    depth=dice_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

project.box(
    BoxType.CAP,
    "AwardMedalBox",
    size=(dice_box_width, dice_box_length, award_box_height),
    lid=LidBuilder(
        text="Medals",
        label_mode=LabelMode.FRAMED,
        pattern=ATHLETE_PATTERN,
        text_color=Color("white"),
        frame_color=Color("gold"),
    ),
    position=(card_box_width, 0.0, dice_box_height),
    no_rotate=True,
).compartment(
    "Medals",
    depth=award_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── 3. Athlete Character Pieces (2 stacked boxes) ─────────────────
for i in range(2):
    p_box = project.box(
        BoxType.CAP,
        f"AthletePiecesBox_{i + 1}",
        size=(box_width, piece_box_length, piece_box_height),
        lid=LidBuilder(
            text=f"Athletes {i + 1}",
            label_mode=LabelMode.FRAMED,
            pattern=ATHLETE_PATTERN,
            text_color=Color("white"),
            frame_color=Color("darkorange"),
        ),
        position=(0.0, card_box_length + i * piece_box_length, 0.0),
        no_rotate=True,
    )
    for slot in range(4):
        p_box.compartment(
            f"AthleteSlot_{slot + 1}",
            width_ratio=0.25,
            depth=piece_box_height - floor_thickness - 1.0,
            cut=FingerCut.SCOOP,
        )

# ── 4. Big Baby Standee Box ───────────────────────────────────────
project.box(
    BoxType.CAP,
    "BigBabyBox",
    size=(big_baby_box_width, big_baby_box_length, usable_height),
    lid=LidBuilder(
        text="Big Baby",
        label_mode=LabelMode.FRAMED,
        pattern=ATHLETE_PATTERN,
        text_color=Color("white"),
        frame_color=Color("purple"),
    ),
    position=(0.0, card_box_length + piece_box_length * 2.0, 0.0),
    no_rotate=True,
).compartment(
    "BigBaby",
    depth=usable_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
