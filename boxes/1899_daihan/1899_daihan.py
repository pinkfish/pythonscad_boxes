#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""1899: Daihan board game organizer.

Ports examples/1899daihan.scad to the pyboxbuilder Project API.
Organizes 18xx track hex tiles, corporate share certificates, paper money,
company charter markers, train cards, and private companies with automatic spacers.
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
box_length = 305.0
box_width = 225.0
box_height = 63.0

board_thickness = 13.0
usable_height = box_height - board_thickness  # 50.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

# ── Components & Dimensions ───────────────────────────────────────
tile_width = 40.0
tile_radius = tile_width / 2.0 / math.cos(math.radians(30.0))
tile_thickness = 2.5

disc_diameter = 14.0
disc_thickness = 5.0

money_width = 44.0
money_length = 68.0

small_card_width = 48.0
small_card_length = 71.0

card_width = 66.0
card_length = 91.0
single_card_thickness = 0.6

# ── Box Sizing ────────────────────────────────────────────────────
hex_box_width = tile_radius * 6.0 + wall_thickness * 3.0   # ~147.5mm
hex_box_length = tile_width * 3.0 + wall_thickness * 3.0   # 129.0mm
hex_box_height = tile_thickness * 4.0 + floor_thickness + lid_thickness + 2.0  # 16.0mm

money_box_width = box_width - hex_box_width - 1.0          # ~76.5mm
money_box_length = hex_box_length * 2.0                    # 258.0mm
money_box_height = usable_height / 3.0                     # ~16.66mm

share_box_width = money_box_width
share_box_length = money_box_length
share_box_height = usable_height / 3.0

train_card_box_width = small_card_length + wall_thickness * 2.0   # 77.0mm
train_card_box_length = box_length - hex_box_length * 2.0         # 47.0mm (fits within 305mm)
train_card_box_height = single_card_thickness * 48.0 + floor_thickness + lid_thickness  # 32.8mm

company_marker_box_width = hex_box_width
company_marker_box_length = disc_diameter * 2.0 + wall_thickness * 5.0  # 43.0mm
company_marker_box_height = usable_height - hex_box_height * 2.0        # 18.0mm

private_card_box_width = card_length + wall_thickness * 2.0            # 97.0mm
private_card_box_length = card_width + wall_thickness * 2.0            # 72.0mm
private_card_box_height = company_marker_box_height

extra_bits_box_width = hex_box_width - private_card_box_width           # ~50.5mm
extra_bits_box_length = private_card_box_length
extra_bits_box_height = company_marker_box_height

project = Project(
    "1899Daihan",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

HEX_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Hex Tile Boxes (4 boxes: 2 columns, stacked 2 high) ────────
for col in range(2):
    y_pos = col * hex_box_length
    for tier in range(2):
        z_pos = tier * hex_box_height
        box_num = col * 2 + tier + 1
        box = project.box(
            BoxType.CAP,
            f"HexBox_{box_num}",
            size=(hex_box_width, hex_box_length, hex_box_height),
            lid=LidBuilder(
                text="1899 Daihan",
                label_mode=LabelMode.FRAMED,
                pattern=HEX_PATTERN,
                text_color=Color("white"),
                frame_color=Color("darkgreen"),
            ),
            position=(0.0, y_pos, z_pos),
            no_rotate=True,
        )
        box.compartment(
            "Tiles",
            depth=hex_box_height - floor_thickness - 1.0,
            cut=FingerCut.SCOOP,
        )

# ── 2. Share & Money Boxes (Stacked 3 high at X = hex_box_width) ──
for i in range(2):
    s_box = project.box(
        BoxType.CAP,
        f"ShareBox_{i + 1}",
        size=(share_box_width, share_box_length, share_box_height),
        lid=LidBuilder(
            text="Shares",
            label_mode=LabelMode.FRAMED,
            pattern=HEX_PATTERN,
            text_color=Color("white"),
            frame_color=Color("navy"),
        ),
        position=(hex_box_width, 0.0, i * share_box_height),
        no_rotate=True,
    )
    for slot in range(4):
        s_box.compartment(
            f"Slot_{slot + 1}",
            length_ratio=0.25,
            depth=share_box_height - floor_thickness - 1.0,
            cut=FingerCut.SCOOP,
        )

m_box = project.box(
    BoxType.CAP,
    "MoneyBox",
    size=(money_box_width, money_box_length, money_box_height),
    lid=LidBuilder(
        text="Money",
        label_mode=LabelMode.FRAMED,
        pattern=HEX_PATTERN,
        text_color=Color("white"),
        frame_color=Color("gold"),
    ),
    position=(hex_box_width, 0.0, share_box_height * 2.0),
    no_rotate=True,
)
for slot in range(5):
    m_box.compartment(
        f"Denom_{slot + 1}",
        length_ratio=0.2,
        depth=money_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )

# ── 3. Company Markers, Private Cards & Extra Bits (atop HexBoxes) ─
z_top = hex_box_height * 2.0  # 32.0mm

for i in range(2):
    c_box = project.box(
        BoxType.SLIPOVER,
        f"CompanyMarkerBox_{i + 1}",
        size=(company_marker_box_width, company_marker_box_length, company_marker_box_height),
        lid=LidBuilder(
            text="Company",
            label_mode=LabelMode.FRAMED,
            pattern=HEX_PATTERN,
            text_color=Color("white"),
        ),
        position=(0.0, i * company_marker_box_length, z_top),
        no_rotate=True,
    )
    c_box.compartment(
        "Tokens",
        depth=company_marker_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )

project.box(
    BoxType.SLIDING,
    "PrivateCompanyCards",
    size=(private_card_box_width, private_card_box_length, private_card_box_height),
    lid=LidBuilder(
        text="Privates",
        label_mode=LabelMode.FRAMED,
        pattern=HEX_PATTERN,
        text_color=Color("white"),
    ),
    position=(0.0, company_marker_box_length * 2.0, z_top),
    no_rotate=True,
).compartment(
    "Cards",
    depth=private_card_box_height - lid_thickness,
    cut=FingerCut.SCOOP,
)

project.box(
    BoxType.SLIPOVER,
    "ExtraBitsBox",
    size=(extra_bits_box_width, extra_bits_box_length, extra_bits_box_height),
    lid=LidBuilder(
        text="Extra",
        label_mode=LabelMode.FRAMED,
        pattern=HEX_PATTERN,
        text_color=Color("white"),
    ),
    position=(private_card_box_width, company_marker_box_length * 2.0, z_top),
    no_rotate=True,
).compartment(
    "Tokens",
    depth=extra_bits_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── 4. Train Card Box (Row at Y = 258mm) ───────────────────────────
project.box(
    BoxType.SLIDING,
    "TrainCardBox",
    size=(train_card_box_width, train_card_box_length, min(train_card_box_height, usable_height)),
    lid=LidBuilder(
        text="Trains",
        label_mode=LabelMode.FRAMED,
        pattern=HEX_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkred"),
    ),
    position=(0.0, hex_box_length * 2.0, 0.0),
    no_rotate=True,
).compartment(
    "TrainCards",
    depth=min(train_card_box_height, usable_height) - lid_thickness,
    cut=FingerCut.SCOOP,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
