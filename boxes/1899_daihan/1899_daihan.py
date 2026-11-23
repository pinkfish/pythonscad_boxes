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

from pyboxbuilder import (
    BoxType,
    Color,
    CompartmentElement,
    ElementShape,
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
train_card_box_length = small_card_width + wall_thickness * 2.0   # 54.0mm
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

# ── Interior Geometry Helpers (from 1899_daihan.scad) ─────────────
hex_inner_w = hex_box_width - wall_thickness * 2.0                 # ~141.564mm
hex_inner_l = hex_box_length - wall_thickness * 2.0                # 123.0mm
hex_inner_h = hex_box_height - floor_thickness - lid_thickness     # 12.0mm
company_inner_h = company_marker_box_height - floor_thickness - lid_thickness  # 14.0mm


def _hex_box_elements() -> tuple[CompartmentElement, ...]:
    """HexBox: 3x3 flat-top hexagonal tile grid (tile_width=40mm) with edge finger bites."""
    elems: list[CompartmentElement] = []
    p2p = tile_width / math.cos(math.radians(30.0))  # ~46.188mm
    x_margin = (hex_inner_w - 3.0 * p2p) / 2.0       # 1.5mm
    y_margin = (hex_inner_l - 3.0 * tile_width) / 2.0  # 1.5mm
    bite_d = 10.0
    for col in range(3):
        cx = x_margin + p2p / 2.0 + col * p2p
        for row in range(3):
            cy = y_margin + tile_width / 2.0 + row * tile_width
            elems.append(
                CompartmentElement(
                    shape=ElementShape.HEXAGON,
                    size=(tile_width, tile_width),
                    rotation=0.0,
                    offset=(cx - p2p / 2.0, cy - tile_width / 2.0),
                    depth=hex_inner_h,
                    pull_out=False,
                    label=f"Hex_{row}_{col}",
                )
            )
        # Circular finger bites at bottom, interior shared, and top flat edges
        for b_idx, by in enumerate((5.0, y_margin + tile_width, y_margin + tile_width * 2.0, hex_inner_l - 5.0)):
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(bite_d, bite_d),
                    offset=(cx - bite_d / 2.0, by - bite_d / 2.0),
                    depth=hex_inner_h,
                    pull_out=False,
                    label=f"HexBite_{col}_{b_idx}",
                )
            )
    return tuple(elems)


def _company_marker_elements() -> tuple[CompartmentElement, ...]:
    """CompanyMarkerBox: 2x8 circular disc wells (d=14mm) with alternating stepped depths & bites."""
    # Fits comfortably inside slipover interior (~138.1 x 33.6mm for wall_thickness=3.0)
    elems: list[CompartmentElement] = []
    r = disc_diameter / 2.0  # 7.0mm
    pitch = 16.8
    bite_d = 10.0
    deep_d = disc_thickness * 2.0 + 1.0    # 11.0mm (2-disc stack)
    shallow_d = disc_thickness + 1.0       # 6.0mm (1-disc stack on odd columns of row 1)
    for i in range(8):
        cx = 2.0 + r + pitch * i
        # Row 0 (front, 2-disc depth, front finger bite at 270 deg)
        cy0 = 8.0
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(disc_diameter, disc_diameter),
                offset=(cx - r, cy0 - r),
                depth=deep_d,
                z_offset=company_inner_h - deep_d,
                pull_out=False,
                label=f"CompanyDisc_0_{i}",
            )
        )
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(bite_d, bite_d),
                offset=(cx - bite_d / 2.0, 0.0),
                depth=deep_d,
                z_offset=company_inner_h - deep_d,
                pull_out=False,
                label=f"CompanyBite_0_{i}",
            )
        )
        # Row 1 (back, alternating stepped depth matching (i % 2) * disc_thickness, back bite at 90 deg)
        cy1 = 25.0
        d1 = shallow_d if (i % 2 == 1) else deep_d
        z1 = company_inner_h - d1
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(disc_diameter, disc_diameter),
                offset=(cx - r, cy1 - r),
                depth=d1,
                z_offset=z1,
                pull_out=False,
                label=f"CompanyDisc_1_{i}",
            )
        )
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(bite_d, bite_d),
                offset=(cx - bite_d / 2.0, 23.0),
                depth=d1,
                z_offset=z1,
                pull_out=False,
                label=f"CompanyBite_1_{i}",
            )
        )
    return tuple(elems)


# ── 1. Hex Tile Boxes ─────────────────────────────────────────────
for box_num in range(1, 5):
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
    )
    box.compartment(
        "Tiles",
        elements=_hex_box_elements(),
    )

# ── 2. Share & Money Boxes ────────────────────────────────────────
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
    )
    for slot in range(4):
        s_box.compartment(
            f"Slot_{slot + 1}",
            length_ratio=0.25,
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
)
for slot in range(5):
    m_box.compartment(
        f"Denom_{slot + 1}",
        length_ratio=0.2,
        cut=FingerCut.SCOOP,
    )

# ── 3. Company Markers, Private Cards & Extra Bits ────────────────
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
    )
    c_box.compartment(
        "Tokens",
        elements=_company_marker_elements(),
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
    expandable=False,
).compartment(
    "Cards",
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
).compartment(
    "Tokens",
    cut=FingerCut.SCOOP,
)

# ── 4. Train Card Box ─────────────────────────────────────────────
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
    expandable=False,
).compartment(
    "TrainCards",
    depth=min(train_card_box_height, usable_height) - lid_thickness,
    cut=FingerCut.SCOOP,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
