#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Earth: Animal Kingdom expansion organizer.

Ports examples/earth_animal_kingdom.scad to the pyboxbuilder Project API.
Organizes oversized animal tarot cards, animal tokens, canopies, and sprout cubes
with automated spacers.
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

# ── Box & Board Dimensions ────────────────────────────────────────
box_width = 288.0
box_length = 158.0
box_height = 47.0

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

animal_card_width = 72.0
animal_card_length = 123.0
card_box_width = animal_card_width + wall_thickness * 2.0   # 78.0mm
card_box_length = animal_card_length + wall_thickness * 2.0 # 129.0mm
card_box_height = 24.0

canopy_box_width = 38.0
canopy_box_length = card_box_length
canopy_box_height = box_height - 2.0  # 45.0mm

animal_box_width = box_width - card_box_width - canopy_box_width - 2.0  # 170.0mm
animal_box_length = card_box_length
animal_box_height = 13.0

sprout_box_width = card_box_width
sprout_box_length = card_box_length
sprout_box_height = box_height - card_box_height - 2.0  # 21.0mm

project = Project(
    "EarthAnimalKingdom",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    generate_spacers=True,
)

ANIMAL_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Oversized Animal Cards & Sprout Box (Column 0, X = 0) ──────
project.box(
    BoxType.SLIDING,
    "AnimalCardsBox",
    size=(card_box_width, card_box_length, card_box_height),
    lid=LidBuilder(
        text="Animal Cards",
        label_mode=LabelMode.FRAMED,
        pattern=ANIMAL_PATTERN,
        text_color=Color("white"),
        frame_color=Color("maroon"),
    ),
    position=(0.0, 0.0, 0.0),
    no_rotate=True,
).compartment(
    "Cards",
    depth=card_box_height - lid_thickness,
    cut=FingerCut.SCOOP,
)

project.box(
    BoxType.CAP,
    "ExpansionSproutBox",
    size=(sprout_box_width, sprout_box_length, sprout_box_height),
    lid=LidBuilder(
        text="Sprouts",
        label_mode=LabelMode.FRAMED,
        pattern=ANIMAL_PATTERN,
        text_color=Color("white"),
        frame_color=Color("forestgreen"),
    ),
    position=(0.0, 0.0, card_box_height),
    no_rotate=True,
).compartment(
    "Cubes",
    depth=sprout_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── 2. Canopy Toppers Box (Column 1, X = card_box_width) ──────────
project.box(
    BoxType.CAP,
    "ExpansionCanopyBox",
    size=(canopy_box_width, canopy_box_length, canopy_box_height),
    lid=LidBuilder(
        text="Canopies",
        label_mode=LabelMode.FRAMED,
        pattern=ANIMAL_PATTERN,
        text_color=Color("white"),
        frame_color=Color("peru"),
    ),
    position=(card_box_width, 0.0, 0.0),
    no_rotate=True,
).compartment(
    "Canopies",
    depth=canopy_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── 3. Animal Token Trays (Column 2, stacked 2-high at X = card + canopy)
x_animals = card_box_width + canopy_box_width  # 116.0mm

for tier in range(2):
    a_box = project.box(
        BoxType.CAP,
        f"AnimalTokensBox_{tier + 1}",
        size=(animal_box_width, animal_box_length, animal_box_height),
        lid=LidBuilder(
            text=f"Animal Tokens {tier + 1}",
            label_mode=LabelMode.FRAMED,
            pattern=ANIMAL_PATTERN,
            text_color=Color("white"),
            frame_color=Color("darkgoldenrod"),
        ),
        position=(x_animals, 0.0, tier * animal_box_height),
        no_rotate=True,
    )
    for slot in range(3):
        a_box.compartment(
            f"Species_{slot + 1}",
            width_ratio=1.0 / 3.0,
            depth=animal_box_height - floor_thickness - 1.0,
            cut=FingerCut.SCOOP,
        )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
