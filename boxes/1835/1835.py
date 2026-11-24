#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""1835 board game organizer.

Ports examples/1835.scad to the pyboxbuilder Project API.
Organizes Prussian/Bavarian railroad company shares, money denominations,
hex track tiles, and the priority deal marker with automated spacers.
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

ASSETS = (
    Path(__file__).resolve().parent / "assets"
    if "__file__" in globals()
    else ROOT / "boxes" / "1835" / "assets"
)

# ── Box & Board Dimensions ────────────────────────────────────────
box_width = 216.0
box_length = 298.0
box_height = 50.0

board_thickness = 15.0
usable_height = box_height - board_thickness  # 35.0mm

wall_thickness = 2.0
floor_thickness = 2.0
lid_thickness = 2.0

share_width = 46.0
share_length = 66.0
money_length = 98.0
money_one_thickness = 5.0
large_marker_diameter = 20.0
tile_width = 40.0
tile_radius = tile_width / 2.0 / math.cos(math.radians(30.0))

# Row 1: MoneyBox_1, MoneyBox_2, MiddleBox (stacked to 35.0mm)
money_box_width = box_width - 1.0                                      # 215.0mm
money_box_length = money_length + wall_thickness * 2.0                 # 102.0mm
money_box_height_1 = floor_thickness + lid_thickness + money_one_thickness + 0.5  # 9.5mm
money_box_height_2 = money_box_height_1 - 1.0                          # 8.5mm
middle_box_height = usable_height - money_box_height_1 - money_box_height_2       # 17.0mm

# Row 2: 4x HexBox (stacked to 35.0mm)
hex_box_width = box_width - 1.0                                        # 215.0mm
hex_box_length = tile_radius * 6.0 + wall_thickness * 2.0              # ~142.564mm
hex_box_height = usable_height / 4.0                                   # 8.75mm

# Row 3: 4x SharesBox (stacked to 35.0mm) + FirstPlayerBox (24.0mm) + auto Spacer (11.0mm)
shares_box_width = share_length * 2.0 + 3.0 * 2.0                      # 138.0mm
shares_box_length = box_length - hex_box_length - money_box_length - 1.0  # ~52.436mm
shares_box_height = usable_height / 4.0                                # 8.75mm

first_player_box_width = box_width - shares_box_width - 1.0            # 77.0mm
first_player_box_length = shares_box_length                            # ~52.436mm
first_player_box_height = large_marker_diameter + 4.0                  # 24.0mm

project = Project(
    "EighteenThirtyFive",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

# ── Game Component Inventory ──────────────────────────────────────
project.define_inventory({
    "Banknotes": 200,
    "Station Tokens": 41,
    "Train Cards": 33,
    "Private Railroad Cards": 6,
    "Yellow Track Hex Tiles": 53,
    "Green Track Hex Tiles": 46,
    "Brown Track Hex Tiles": 34,
    "Grey Track Hex Tiles": 4,
    "Company Share Certificates": 68,
    "First Player Marker": 1,
    "Game Board": 1,
    "Company Charters": 8,
})

project.board(
    "Game Board & Charters",
    size=(box_width, box_length, board_thickness),
    position=(0.0, 0.0, usable_height),
    count=9,
    notes="Mounted map board and 8 railroad company charters atop insert",
    allocates={"Game Board": 1, "Company Charters": 8},
)

TRAIN_PATTERN = PatternBuilder(PatternType.OCTAGON)
RAILWAY_FONT = "Georgia:style=Bold"


def _lid(
    text: str,
    frame_color: str,
    *,
    logo: str | None = None,
    logo_size_mm: float = 16.0,
) -> LidBuilder:
    return LidBuilder(
        text=text,
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.DOUBLE_FRAME,
        label_finial=LabelFinial.SPEAR,
        font=RAILWAY_FONT,
        pattern=TRAIN_PATTERN,
        text_color=Color("white"),
        frame_color=Color(frame_color),
        logo=logo,
        logo_color=Color("white") if logo else None,
        logo_position="left",
        label_logo_size_mm=logo_size_mm if logo else None,
    )


# ── 1. Bank Money Trays (2 stacked slipover-lid trays, 4 denoms each)
for idx, (m_h, denom_label) in enumerate(
    [(money_box_height_1, "1-5-10-20"), (money_box_height_2, "50-100-200-500")],
    start=1,
):
    m_box = project.box(
        BoxType.SLIPOVER,
        f"MoneyBox_{idx}",
        size=(money_box_width, money_box_length, m_h),
        lid=_lid(
            f"Money {denom_label}",
            "darkgreen",
            logo=str(ASSETS / "coin.svg"),
            logo_size_mm=16.0,
        ),
    )
    for slot in range(4):
        m_box.compartment(
            f"Denom_{slot + 1}",
            width_ratio=0.25,
            cut=FingerCut.SCOOP,
            component="Banknotes",
            count=25,
        )

# ── Interior Geometry Helpers (from 1835.scad) ────────────────────
middle_inner_h = middle_box_height - floor_thickness - lid_thickness  # 13.0mm
hex_inner_w = hex_box_width - wall_thickness * 2.0                    # 211.0mm
hex_inner_l = hex_box_length - wall_thickness * 2.0                   # ~138.564mm
hex_inner_h = hex_box_height - floor_thickness - lid_thickness        # 4.75mm
first_player_inner_h = first_player_box_height - floor_thickness - lid_thickness  # 20.0mm


def _middle_box_elements() -> tuple[CompartmentElement, ...]:
    """MiddleBox: 40 circular token wells (14 rows), Trains well, stepped Private well."""
    elems: list[CompartmentElement] = []
    # 1. 14 rows of small circular token wells (d=6mm, depth=3mm flush with top)
    token_depths = (1, 1, 3, 3, 3, 3, 3, 3, 3, 4, 3, 3, 4, 4)
    tok_d = 6.0
    tok_r = tok_d / 2.0
    tok_depth = 3.0
    tok_z = middle_inner_h - tok_depth  # 10.0mm
    for i, count in enumerate(token_depths):
        col_idx = i if i < 4 else i + 1
        cx = 5.0 + col_idx * 14.0 + tok_r
        for j in range(count):
            cy = 6.0 + j * 11.0
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(tok_d, tok_d),
                    offset=(cx - tok_r, cy - tok_r),
                    depth=tok_depth,
                    z_offset=tok_z,
                    pull_out=False,
                    label=f"Token_{i}_{j}",
                )
            )
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(tok_d, tok_d),
                    offset=(cx - tok_r, cy),
                    depth=tok_depth,
                    z_offset=tok_z,
                    pull_out=False,
                    label=f"TokenBite_{i}_{j}",
                )
            )

    # 2. Trains card well (66.5 x 46.5mm, full depth) + left circular finger bite
    trains_w = share_length + 0.5  # 66.5mm
    trains_l = share_width + 0.5   # 46.5mm
    elems.append(
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(trains_w, trains_l),
            offset=(41.0, 49.0),
            depth=middle_inner_h,
            pull_out=False,
            label="TrainsCards",
        )
    )
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(20.0, 20.0),
            offset=(41.0 - 10.0, 49.0 + trains_l / 2.0 - 10.0),
            depth=middle_inner_h,
            pull_out=False,
            label="TrainsBite",
        )
    )

    # 3. Private company cards well (66 x 46mm, shallow stepped depth=4.5mm) + right bite
    priv_depth = 4.5
    priv_z = middle_inner_h - priv_depth  # 8.5mm
    elems.append(
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(share_length, share_width),
            offset=(124.0, 49.0),
            depth=priv_depth,
            z_offset=priv_z,
            pull_out=False,
            label="PrivateCards",
        )
    )
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(20.0, 20.0),
            offset=(124.0 + share_length - 10.0, 49.0 + share_width / 2.0 - 10.0),
            depth=priv_depth,
            z_offset=priv_z,
            pull_out=False,
            label="PrivateBite",
        )
    )
    return tuple(elems)


def _hex_box_elements() -> tuple[CompartmentElement, ...]:
    """HexBox: 3x5 pointy-top hexagonal tile grid with circular edge finger bites."""
    elems: list[CompartmentElement] = []
    tw = 39.9  # tiny clearance inside 6 * tile_radius
    p2p = tw / math.cos(math.radians(30.0))  # ~46.073mm
    x_margin = (hex_inner_w - 5.0 * tw) / 2.0
    y_margin = (hex_inner_l - 3.0 * p2p) / 2.0
    bite_d = 10.0
    for row in range(3):
        cy = y_margin + p2p / 2.0 + row * p2p
        for col in range(5):
            cx = x_margin + tw / 2.0 + col * tw
            elems.append(
                CompartmentElement(
                    shape=ElementShape.HEXAGON,
                    size=(tw, tw),
                    rotation=30.0,
                    offset=(cx - tw / 2.0, cy - p2p / 2.0),
                    depth=hex_inner_h,
                    pull_out=False,
                    label=f"Hex_{row}_{col}",
                )
            )
        # Circular finger bites straddling each vertical hex edge
        for k in range(6):
            bx = x_margin + k * tw
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(bite_d, bite_d),
                    offset=(bx - bite_d / 2.0, cy - bite_d / 2.0),
                    depth=hex_inner_h,
                    pull_out=False,
                    label=f"HexBite_{row}_{k}",
                )
            )
    return tuple(elems)


def _first_player_elements() -> tuple[CompartmentElement, ...]:
    """FirstPlayerBox: horizontal cylindrical marker cradle (d=20, l=41) + twin pinch bites."""
    # Fits comfortably inside slipover interior (~67.6 x 43.0mm for wall_thickness=3.0)
    cx, cy = 33.5, 21.25
    cradle_w, cradle_l = 20.5, 41.0
    bite_d = 20.0
    return (
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(cradle_w, cradle_l),
            offset=(cx - cradle_w / 2.0, cy - cradle_l / 2.0),
            corner_radius=2.0,
            bottom_rounding=9.5,
            depth=first_player_inner_h,
            pull_out=False,
            label="MarkerCradle",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(bite_d, bite_d),
            offset=(cx - 12.0 - bite_d / 2.0, cy - bite_d / 2.0),
            bottom_rounding=8.0,
            depth=first_player_inner_h,
            pull_out=False,
            label="PinchBiteLeft",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(bite_d, bite_d),
            offset=(cx + 12.0 - bite_d / 2.0, cy - bite_d / 2.0),
            bottom_rounding=8.0,
            depth=first_player_inner_h,
            pull_out=False,
            label="PinchBiteRight",
        ),
    )


# ── 2. Middle Box (Tokens, Trains & Private Companies) ────────────
middle_box = project.box(
    BoxType.CAP,
    "MiddleBox",
    size=(money_box_width, money_box_length, middle_box_height),
    lid=_lid(
        "Tokens/Trains",
        "darkslateblue",
        logo=str(ASSETS / "locomotive.svg"),
        logo_size_mm=16.0,
    ),
)
middle_box.compartment(
    "TokensAndCards",
    elements=_middle_box_elements(),
    allocates={
        "Station Tokens": 41,
        "Train Cards": 33,
        "Private Railroad Cards": 6,
    },
)

# ── 3. Track Hex Tile Boxes (4 tiers stacked, inset lid) ──────────
hex_tiers = [
    ("goldenrod", "Yellow Track Hex Tiles", 53),
    ("forestgreen", "Green Track Hex Tiles", 46),
    ("saddlebrown", "Brown Track Hex Tiles", 34),
    ("dimgray", "Grey Track Hex Tiles", 4),
]
for tier, (color_name, tile_comp, tile_qty) in enumerate(hex_tiers):
    h_box = project.box(
        BoxType.INSET,
        f"HexBox_{tier + 1}",
        size=(hex_box_width, hex_box_length, hex_box_height),
        lid=_lid(f"Tiles {tier + 1}", color_name),
    )
    h_box.compartment(
        "HexGrid",
        elements=_hex_box_elements(),
        component=tile_comp,
        count=tile_qty,
    )

# ── 4. Railroad Company Shares (4 tiers stacked, slipover lid) ────
_share_counts = ((9, 9), (9, 9), (8, 12), (6, 6))  # 68 total across 8 companies
for tier in range(4):
    s_box = project.box(
        BoxType.SLIPOVER,
        f"SharesBox_{tier + 1}",
        size=(shares_box_width, shares_box_length, shares_box_height),
        wall_thickness=1.5,
        lid=_lid(
            f"Shares {tier + 1}",
            "darkred",
            logo=str(ASSETS / "share_cert.svg"),
            logo_size_mm=14.0,
        ),
    )
    s_box.compartment(
        "Shares_1",
        width_ratio=0.5,
        cut=FingerCut.SCOOP,
        component="Company Share Certificates",
        count=_share_counts[tier][0],
    )
    s_box.compartment(
        "Shares_2",
        width_ratio=0.5,
        cut=FingerCut.SCOOP,
        component="Company Share Certificates",
        count=_share_counts[tier][1],
    )

# ── 5. First Player Marker Box (slipover lid, 24mm; auto spacer on top)
p_box = project.box(
    BoxType.SLIPOVER,
    "FirstPlayerBox",
    size=(first_player_box_width, first_player_box_length, first_player_box_height),
    wall_thickness=3.0,
    lid=_lid("First", "navy"),
)
p_box.compartment(
    "FirstPlayerMarker",
    elements=_first_player_elements(),
    component="First Player Marker",
    count=1,
)

project.stack_order("HexBox_1", "HexBox_2", "HexBox_3", "HexBox_4")

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
