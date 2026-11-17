#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Nature board game organizer.

Ports examples/nature.scad to the pyboxbuilder Project API.
Organizes nature and hunter cards, player population dials, wooden leopard token,
and grass/meat food resources with automated spacers.
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
    FingerCut,
    LabelMode,
    LidBuilder,
    PatternBuilder,
    PatternType,
    Project,
    StackableMode,
    run,
)

# ── Box & Board Dimensions ────────────────────────────────────────
box_width = 210.0
box_length = 210.0
box_height = 75.0

board_thickness = 7.0
usable_height = box_height - board_thickness  # 68.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

card_width = 67.0
card_length = 92.0

card_box_width = (box_width - 2.0) / 2.0             # 104.0mm
card_box_length = card_width + wall_thickness * 2.0  # 73.0mm
card_box_height = usable_height                      # 68.0mm

hunter_card_box_width = card_box_width
hunter_card_box_length = card_box_length
hunter_card_box_height = 20.0

dial_box_width = 107.0
dial_box_length = (box_width - hunter_card_box_width - 2.0) / 2.0  # 52.0mm
dial_box_height = 51.0

resource_box_width = box_length - dial_box_width - 2.0             # 101.0mm
resource_box_length = (box_length - 2.0 - card_box_length) / 2.0   # 67.5mm
resource_box_height = dial_box_height / 2.0                        # 25.5mm

project = Project(
    "Nature",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

NATURE_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Main Nature Cards Box ──────────────────────────────────────
project.box(
    BoxType.SLIDING,
    "NatureCardsBox",
    size=(card_box_width, card_box_length, card_box_height),
    lid=LidBuilder(
        text="Nature Cards",
        label_mode=LabelMode.FRAMED,
        pattern=NATURE_PATTERN,
        text_color=Color("white"),
        frame_color=Color("forestgreen"),
    ),
    expandable=False,
).compartment("Cards", cut=FingerCut.SCOOP)

# ── 2. Small Decks (Hunter & Solo) ────────────────────────────────
project.box(
    BoxType.SLIDING,
    "HunterCardsBox",
    size=(hunter_card_box_width, hunter_card_box_length, hunter_card_box_height),
    lid=LidBuilder(
        text="Hunters",
        label_mode=LabelMode.FRAMED,
        pattern=NATURE_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkred"),
    ),
    expandable=False,
    stackable=StackableMode.PYRAMIDS,
).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "SoloCardsBox",
    size=(hunter_card_box_width, hunter_card_box_length, hunter_card_box_height),
    lid=LidBuilder(
        text="Solo / Event",
        label_mode=LabelMode.FRAMED,
        pattern=NATURE_PATTERN,
        text_color=Color("white"),
        frame_color=Color("royalblue"),
    ),
    expandable=False,
    stackable=StackableMode.PYRAMIDS,
).compartment("Cards", cut=FingerCut.SCOOP)

# ── 3. Population Dials & Leopard Box ─────────────────────────────
project.box(
    BoxType.CAP,
    "DialBox",
    size=(dial_box_width, dial_box_length, dial_box_height),
    lid=LidBuilder(
        text="Population Dials",
        label_mode=LabelMode.FRAMED,
        pattern=NATURE_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkgoldenrod"),
    ),
).compartment("Dials", cut=FingerCut.SCOOP)

project.box(
    BoxType.CAP,
    "LeopardBox",
    size=(dial_box_width, dial_box_length, dial_box_height),
    lid=LidBuilder(
        text="Apex Leopard",
        label_mode=LabelMode.FRAMED,
        pattern=NATURE_PATTERN,
        text_color=Color("white"),
        frame_color=Color("peru"),
    ),
).compartment("Leopard", cut=FingerCut.SCOOP)

# ── 4. Food Resource Trays (Grass & Meat) ─────────────────────────
project.box(
    BoxType.CAP,
    "ResourceBox_Grass",
    size=(resource_box_width, resource_box_length, resource_box_height),
    lid=LidBuilder(
        text="Grass",
        label_mode=LabelMode.FRAMED,
        pattern=NATURE_PATTERN,
        text_color=Color("white"),
        frame_color=Color("green"),
    ),
).compartment("GrassTokens", cut=FingerCut.SCOOP)

project.box(
    BoxType.CAP,
    "ResourceBox_Meat",
    size=(resource_box_width, resource_box_length, resource_box_height),
    lid=LidBuilder(
        text="Meat",
        label_mode=LabelMode.FRAMED,
        pattern=NATURE_PATTERN,
        text_color=Color("white"),
        frame_color=Color("firebrick"),
    ),
).compartment("MeatTokens", cut=FingerCut.SCOOP)

project.stack_order("HunterCardsBox", "SoloCardsBox")

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
