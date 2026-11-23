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
    else ROOT / "boxes" / "earth_animal_kingdom" / "assets"
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

ANIMAL_PATTERN = PatternBuilder(PatternType.LEAF)
ANIMAL_FONT = "Georgia:style=Bold"


def _animal_lid(
    text: str,
    frame_color: str,
    *,
    logo_file: str | None = None,
    logo_size: float = 16.0,
) -> LidBuilder:
    return LidBuilder(
        text=text,
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.SCALLOPED,
        label_finial=LabelFinial.FLEURON,
        font=ANIMAL_FONT,
        pattern=ANIMAL_PATTERN,
        text_color=Color("white"),
        frame_color=Color(frame_color),
        logo=str(ASSETS / logo_file) if logo_file is not None else None,
        logo_color=Color("white") if logo_file is not None else None,
        logo_position="left" if logo_file is not None else None,
        label_logo_size_mm=logo_size if logo_file is not None else None,
    )


# ── 1. Oversized Animal Cards & Sprout Box ────────────────────────
project.box(
    BoxType.SLIDING,
    "AnimalCardsBox",
    size=(card_box_width, card_box_length, card_box_height),
    lid=_animal_lid("Animal Cards", "maroon"),
    expandable=False,
).compartment(
    "Cards",
    cut=FingerCut.SCOOP,
)

project.box(
    BoxType.CAP,
    "ExpansionSproutBox",
    size=(sprout_box_width, sprout_box_length, sprout_box_height),
    lid=_animal_lid("Sprouts", "forestgreen", logo_file="sprout.svg", logo_size=16.0),
    expandable=False,
).compartment(
    "Cubes",
    cut=FingerCut.SCOOP,
)

# ── 2. Canopy Toppers Box ─────────────────────────────────────────
project.box(
    BoxType.CAP,
    "ExpansionCanopyBox",
    size=(canopy_box_width, canopy_box_length, canopy_box_height),
    lid=_animal_lid("Canopies", "peru", logo_file="canopy.svg", logo_size=14.0),
    expandable=False,
).compartment(
    "Canopies",
    cut=FingerCut.SCOOP,
)

# ── 3. Animal Token Trays ─────────────────────────────────────────
animal_token_thickness = 8.0
animal_inner_width = animal_box_width - wall_thickness * 2.0      # 164.0mm
animal_inner_length = animal_box_length - wall_thickness * 2.0    # 123.0mm


def _animal_tray_elements(tray_idx: int) -> tuple[CompartmentElement, ...]:
    """Stepped-depth tray: shallow upper finger clearance + 12 deep animal token wells."""
    upper_depth = animal_token_thickness / 2.0  # 4.0mm
    well_depth = animal_token_thickness + 0.5   # 8.5mm (<= 9.0mm interior height)
    elems: list[CompartmentElement] = [
        # Upper rounded clearance terrace (RoundedBoxAllSides inset 1mm, radius=3)
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(animal_inner_width - 2.0, animal_inner_length - 2.0),
            offset=(1.0, 1.0),
            depth=upper_depth,
            corner_radius=3.0,
            bottom_rounding=2.0,
            pull_out=False,
            label=f"UpperClearance_{tray_idx}",
        )
    ]
    # 4x3 grid of deeper individual animal token pockets below the upper terrace
    cols, rows = 4, 3
    slot_w, slot_l = 35.0, 34.0
    gap = 4.0
    start_x = (animal_inner_width - (cols * slot_w + (cols - 1) * gap)) / 2.0
    start_y = (animal_inner_length - (rows * slot_l + (rows - 1) * gap)) / 2.0
    for r in range(rows):
        for c in range(cols):
            elems.append(
                CompartmentElement(
                    shape=ElementShape.ROUNDED_RECT,
                    size=(slot_w, slot_l),
                    offset=(start_x + c * (slot_w + gap), start_y + r * (slot_l + gap)),
                    depth=well_depth,
                    corner_radius=4.0,
                    pull_out=False,
                    label=f"Animal_{tray_idx}_{r + 1}_{c + 1}",
                )
            )
    return tuple(elems)


for tier in range(2):
    a_box = project.box(
        BoxType.CAP,
        f"AnimalTokensBox_{tier + 1}",
        size=(animal_box_width, animal_box_length, animal_box_height),
        lid=_animal_lid(f"Animal Tokens {tier + 1}", "darkgoldenrod", logo_file="paw.svg", logo_size=18.0),
    )
    a_box.compartment(
        f"AnimalTray_{tier + 1}",
        size=(animal_inner_width, animal_inner_length),
        position=(0.0, 0.0),
        elements=_animal_tray_elements(tier + 1),
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
