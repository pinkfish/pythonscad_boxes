#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Ada's Dream board game organizer.

Ports examples/adas_dream.scad to the pyboxbuilder Project API.
Organizes player figures, partner & tier cards, gears/cogs, dice, books,
universities, programs, breakthroughs, and tokens with automated spacers.
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
box_width = 212.0
box_length = 291.0
box_height = 90.0

board_thickness = 31.0
usable_height = box_height - board_thickness  # 59.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

card_width = 66.0
card_length = 91.0
card_box_width = card_width + wall_thickness * 2.0   # 72.0mm
card_box_length = card_length + wall_thickness * 2.0  # 97.0mm

player_box_width = card_box_width                    # 72.0mm
player_box_length = card_box_length                  # 97.0mm
player_box_height = usable_height / 3.0              # 19.66mm

gear_box_width = card_box_width
gear_box_length = 80.0
gear_box_height = usable_height / 3.0

project = Project(
    "AdasDream",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

ADA_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Player Boxes & Small Utility Boxes (Columns 0 & 1, Y = 0) ──
# Left column (X = 0)
project.box(
    BoxType.SLIDING,
    "PlayerBox_Red",
    size=(player_box_width, player_box_length, player_box_height),
    lid=LidBuilder(
        text="Red",
        label_mode=LabelMode.FRAMED,
        pattern=ADA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkred"),
    ),
    position=(0.0, 0.0, 0.0),
    no_rotate=True,
).compartment("Bits", depth=player_box_height - lid_thickness, cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "PlayerBox_Green",
    size=(player_box_width, player_box_length, player_box_height),
    lid=LidBuilder(
        text="Green",
        label_mode=LabelMode.FRAMED,
        pattern=ADA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("forestgreen"),
    ),
    position=(0.0, 0.0, player_box_height),
    no_rotate=True,
).compartment("Bits", depth=player_box_height - lid_thickness, cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "ScoringBox",
    size=(player_box_width, player_box_length, player_box_height),
    lid=LidBuilder(
        text="Scoring",
        label_mode=LabelMode.FRAMED,
        pattern=ADA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("gold"),
    ),
    position=(0.0, 0.0, player_box_height * 2.0),
    no_rotate=True,
).compartment("Bits", depth=player_box_height - lid_thickness, cut=FingerCut.SCOOP)

# Right column (X = card_box_width = 72mm)
project.box(
    BoxType.SLIDING,
    "PlayerBox_Blue",
    size=(player_box_width, player_box_length, player_box_height),
    lid=LidBuilder(
        text="Blue",
        label_mode=LabelMode.FRAMED,
        pattern=ADA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("navy"),
    ),
    position=(card_box_width, 0.0, 0.0),
    no_rotate=True,
).compartment("Bits", depth=player_box_height - lid_thickness, cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "PlayerBox_Purple",
    size=(player_box_width, player_box_length, player_box_height),
    lid=LidBuilder(
        text="Purple",
        label_mode=LabelMode.FRAMED,
        pattern=ADA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("purple"),
    ),
    position=(card_box_width, 0.0, player_box_height),
    no_rotate=True,
).compartment("Bits", depth=player_box_height - lid_thickness, cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "MoneyBox",
    size=(player_box_width, player_box_length, player_box_height),
    lid=LidBuilder(
        text="Money",
        label_mode=LabelMode.FRAMED,
        pattern=ADA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("silver"),
    ),
    position=(card_box_width, 0.0, player_box_height * 2.0),
    no_rotate=True,
).compartment("Money", depth=player_box_height - lid_thickness, cut=FingerCut.SCOOP)

# ── 2. Card Boxes (Row 2, Y = card_box_length = 97mm) ─────────────
y_row2 = card_box_length

project.box(
    BoxType.SLIDING,
    "OtherCardBox",
    size=(card_box_width, card_box_length, usable_height / 2.0),
    lid=LidBuilder(
        text="Cards",
        label_mode=LabelMode.FRAMED,
        pattern=ADA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("royalblue"),
    ),
    position=(card_box_width, y_row2, 0.0),
    no_rotate=True,
).compartment("Cards", depth=usable_height / 2.0 - lid_thickness, cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "TierCardBox",
    size=(card_box_width, card_box_length, usable_height / 2.0),
    lid=LidBuilder(
        text="Tiers",
        label_mode=LabelMode.FRAMED,
        pattern=ADA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkorange"),
    ),
    position=(card_box_width, y_row2, usable_height / 2.0),
    no_rotate=True,
).compartment("Cards", depth=usable_height / 2.0 - lid_thickness, cut=FingerCut.SCOOP)

# ── 3. Gear / Cog Boxes (Stacked 3 high at Y = 97 + 97 = 194mm) ───
y_row3 = card_box_length * 2.0  # 194.0mm

gear_labels = ["AddGears", "SubGears", "MulGears"]
for idx, label in enumerate(gear_labels):
    g_box = project.box(
        BoxType.CAP,
        f"GearBox_{label}",
        size=(gear_box_width, gear_box_length, gear_box_height),
        lid=LidBuilder(
            text="Gears",
            label_mode=LabelMode.FRAMED,
            pattern=ADA_PATTERN,
            text_color=Color("white"),
            frame_color=Color("peru"),
        ),
        position=(card_box_width, y_row3, idx * gear_box_height),
        no_rotate=True,
    )
    g_box.compartment(
        "Gears",
        depth=gear_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )

# ── 4. Dice & Token Boxes (X = 0, Y = 97mm) ───────────────────────
project.box(
    BoxType.CAP,
    "DiceBox",
    size=(card_box_width, card_box_length / 2.0, usable_height / 2.0),
    lid=LidBuilder(
        text="Dice",
        label_mode=LabelMode.FRAMED,
        pattern=ADA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("firebrick"),
    ),
    position=(0.0, y_row2, 0.0),
    no_rotate=True,
).compartment("Dice", depth=usable_height / 2.0 - floor_thickness - 1.0, cut=FingerCut.SCOOP)

project.box(
    BoxType.CAP,
    "BookBox",
    size=(card_box_width, card_box_length / 2.0, usable_height / 2.0),
    lid=LidBuilder(
        text="Books",
        label_mode=LabelMode.FRAMED,
        pattern=ADA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("teal"),
    ),
    position=(0.0, y_row2 + card_box_length / 2.0, 0.0),
    no_rotate=True,
).compartment("Books", depth=usable_height / 2.0 - floor_thickness - 1.0, cut=FingerCut.SCOOP)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
