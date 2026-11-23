#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""18Cuba board game organizer.

Ports examples/18cuba.scad to the pyboxbuilder Project API.
Organizes train cards, company stock share certificates, money slipovers,
hex track tiles, and tokens with automated spacers.
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
    else ROOT / "boxes" / "18_cuba" / "assets"
)

# ── Box & Board Dimensions ────────────────────────────────────────
box_width = 225.0
box_length = 314.0
box_height = 68.0

box_hexes = 20.0
total_board_thickness = 26.0
board_thickness = total_board_thickness + box_hexes  # 46.0mm
usable_height = box_height - board_thickness         # 22.0mm (rest_height in .scad)

wall_thickness = 1.5
floor_thickness = 1.0
lid_thickness = 1.0

# ── Card & Token Dimensions ───────────────────────────────────────
train_card_width = 40.0
train_card_length = 60.0
money_width = 46.0
money_length = 90.0

tray_height = usable_height / 2.0                          # 11.0mm
tray_width = box_width - 1.0                               # 224.0mm (spans across the 225mm box width)

money_box_len = money_length + wall_thickness * 4.0        # 96.0mm
train_box_len = train_card_length + wall_thickness * 4.0   # 66.0mm
rest_section_len = box_length - train_box_len * 2.0 - money_box_len - 1.0  # 85.0mm

project = Project(
    "18Cuba",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

CUBA_PATTERN = PatternBuilder(PatternType.CHEVRON)
CUBA_FONT = "Georgia:style=Bold"


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
        label_shape=LabelShape.CORNER_STUD,
        label_finial=LabelFinial.SPEAR,
        font=CUBA_FONT,
        pattern=CUBA_PATTERN,
        text_color=Color("white"),
        frame_color=Color(frame_color),
        logo=logo,
        logo_color=Color("white") if logo else None,
        logo_position="left",
        label_logo_size_mm=logo_size_mm if logo else None,
    )


# ── 1. Money Boxes (2 full-width stacked boxes, 4 denoms each) ────
for i in range(2):
    m_box = project.box(
        BoxType.SLIPOVER,
        f"MoneyBox_{i + 1}",
        size=(tray_width, money_box_len, tray_height),
        lid=_lid(
            "18Cuba",
            "gold",
            logo=str(ASSETS / "coin.svg"),
            logo_size_mm=16.0,
        ),
    )
    for slot in range(4):
        m_box.compartment(
            f"Denom_{slot + 1}",
            width_ratio=0.25,
            cut=FingerCut.SCOOP,
        )

# ── Interior Geometry Helpers (from 18_cuba.scad) ─────────────────
token_diameter = 15.0
token_thin_thickness = 5.0
rail_thickness = 5.0
rail_length = 25.0

# Slipover lid walls narrow interior by ~4.9mm for wall_thickness=1.5mm
slip_train_inner_l = 61.1
slip_large_inner_l = 80.1
train_inner_h = tray_height - floor_thickness - lid_thickness  # 9.0mm
large_inner_h = tray_height - floor_thickness - lid_thickness  # 9.0mm
inside_inner_w = tray_width - wall_thickness * 2.0             # 221.0mm
inside_inner_l = rest_section_len - wall_thickness * 2.0       # 82.0mm
inside_inner_h = tray_height - floor_thickness                 # 10.0mm (NO_LID)


def _train_box_elements() -> tuple[CompartmentElement, ...]:
    """5 train/wagon card pockets with finger bites and floor icon inlays."""
    elems: list[CompartmentElement] = []
    slot_w = train_card_width + 0.5   # 40.5mm
    slot_l = train_card_length + 0.5  # 60.5mm
    pitch = 43.8
    bite_d = 16.0
    train_svg = str(ASSETS / "train_icon.svg")
    wagon_svg = str(ASSETS / "wagon_icon.svg")
    for i in range(5):
        x0 = 1.5 + i * pitch
        y0 = 0.3
        elems.append(
            CompartmentElement(
                shape=ElementShape.RECT,
                size=(slot_w, slot_l),
                offset=(x0, y0),
                depth=train_inner_h,
                pull_out=False,
                label=f"TrainPocket_{i + 1}",
            )
        )
        # Finger bite at front edge
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(bite_d, bite_d),
                offset=(x0 + slot_w / 2.0 - bite_d / 2.0, 0.0),
                depth=train_inner_h,
                pull_out=False,
                label=f"TrainBite_{i + 1}",
            )
        )
        # Floor positive icon inlay (3 steam locomotives + 2 sugar wagons)
        icon_w, icon_l = 18.0, 30.0
        elems.append(
            CompartmentElement(
                shape=ElementShape.SVG,
                shape_file=train_svg if i < 3 else wagon_svg,
                size=(30.0, 18.0),
                rotation=90.0,
                offset=(x0 + (slot_w - icon_w) / 2.0, y0 + (slot_l - icon_l) / 2.0),
                depth=0.4,
                z_offset=0.0,
                color="black",
                pull_out=False,
                label=f"{'Train' if i < 3 else 'Wagon'}Inlay_{i + 1}",
            )
        )
    return tuple(elems)


def _last_box_elements() -> tuple[CompartmentElement, ...]:
    """LastBox: Concession card pocket, 30 minor-company circular token wells, rail well."""
    elems: list[CompartmentElement] = []
    # 1. Concession card pocket (40 x 60mm, full depth)
    elems.append(
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(train_card_width, train_card_length),
            offset=(0.5, 0.5),
            depth=train_inner_h,
            pull_out=False,
            label="ConcessionCards",
        )
    )
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(16.0, 16.0),
            offset=(0.5 + train_card_width / 2.0 - 8.0, 0.0),
            depth=train_inner_h,
            pull_out=False,
            label="ConcessionBite",
        )
    )

    # 2. 30 circular minor-company token wells (d=15.5mm, depth=5.5mm flush with top)
    tok_d = token_diameter + 0.5  # 15.5mm
    tok_r = tok_d / 2.0
    tok_depth = token_thin_thickness + 0.5  # 5.5mm
    tok_z = train_inner_h - tok_depth       # 3.5mm
    bite_d = 12.0
    pitch = 15.8
    row_cys = (8.5, 30.5, 52.5)
    for i in range(10):
        cx = 42.5 + tok_r + pitch * i
        for r_idx in (0, 1):
            cy = row_cys[r_idx]
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(tok_d, tok_d),
                    offset=(cx - tok_r, cy - tok_r),
                    depth=tok_depth,
                    z_offset=tok_z,
                    pull_out=False,
                    label=f"MinorToken_{r_idx}_{i}",
                )
            )
        # Row 2 (i > 7 shifts by +1 slot matching last_i in .scad)
        last_i = i + 1 if i > 7 else i
        cx2 = 42.5 + tok_r + pitch * last_i
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(tok_d, tok_d),
                offset=(cx2 - tok_r, row_cys[2] - tok_r),
                depth=tok_depth,
                z_offset=tok_z,
                pull_out=False,
                label=f"MinorToken_2_{i}",
            )
        )
        # Finger bites (front edge, middle between row 1 & 2, back edge)
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(bite_d, bite_d),
                offset=(cx - bite_d / 2.0, 0.0),
                depth=tok_depth,
                z_offset=tok_z,
                pull_out=False,
                label=f"MinorBiteFront_{i}",
            )
        )
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(bite_d, bite_d),
                offset=(cx - bite_d / 2.0, 41.5 - bite_d / 2.0),
                depth=tok_depth,
                z_offset=tok_z,
                pull_out=False,
                label=f"MinorBiteMid_{i}",
            )
        )
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(bite_d, bite_d),
                offset=(cx2 - bite_d / 2.0, slip_train_inner_l - bite_d),
                depth=tok_depth,
                z_offset=tok_z,
                pull_out=False,
                label=f"MinorBiteBack_{i}",
            )
        )

    # 3. Rail well (15 x 25mm, depth=6.0mm) + finger bite
    rail_w = rail_thickness * 3.0  # 15.0mm
    rail_depth = rail_thickness + 1.0  # 6.0mm
    rail_z = train_inner_h - rail_depth
    rail_x = 202.0
    rail_y = 8.0
    elems.append(
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(rail_w, rail_length),
            offset=(rail_x, rail_y),
            depth=rail_depth,
            z_offset=rail_z,
            pull_out=False,
            label="RailWell",
        )
    )
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(10.0, 10.0),
            offset=(rail_x + rail_w / 2.0 - 5.0, rail_y + rail_length - 5.0),
            depth=rail_depth,
            z_offset=rail_z,
            pull_out=False,
            label="RailBite",
        )
    )
    return tuple(elems)


def _large_tokens_elements() -> tuple[CompartmentElement, ...]:
    """LargeTokensBox: 48 circular major-company token wells (12x4) with finger bites."""
    elems: list[CompartmentElement] = []
    tok_d = token_diameter + 0.5  # 15.5mm
    tok_r = tok_d / 2.0
    bite_d = 12.0
    pitch = 17.8
    row_cys = (9.5, 30.0, 50.5, 71.0)
    for i in range(12):
        cx = 3.0 + tok_r + pitch * i
        for r_idx, cy in enumerate(row_cys):
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(tok_d, tok_d),
                    offset=(cx - tok_r, cy - tok_r),
                    depth=large_inner_h,
                    pull_out=False,
                    label=f"MajorToken_{r_idx}_{i}",
                )
            )
        # Outer & middle finger bites matching .scad xcyl/sphere cutouts
        for b_idx, by in enumerate((0.0, 34.25, 54.75, slip_large_inner_l - bite_d)):
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(bite_d, bite_d),
                    offset=(cx - bite_d / 2.0, by),
                    depth=large_inner_h,
                    pull_out=False,
                    label=f"MajorBite_{b_idx}_{i}",
                )
            )
    return tuple(elems)


def _inside_token_tray_elements() -> tuple[CompartmentElement, ...]:
    """InsideTokenTray: 5-col stepped circular token wells + far-end token well."""
    elems: list[CompartmentElement] = []
    tok_d = token_diameter + 0.5
    tok_r = tok_d / 2.0
    bite_d = 12.0
    pitch = token_diameter + 3.0
    row_cys = (10.05, 31.95, 53.95, 73.55)
    for i in range(5):
        cx = 4.0 + tok_r + pitch * i
        outer_depth = 5.2 if i == 4 else 9.8
        outer_z = inside_inner_h - outer_depth
        # Outer rows 0 & 3 for all 5 columns
        for r_idx in (0, 3):
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(tok_d, tok_d),
                    offset=(cx - tok_r, row_cys[r_idx] - tok_r),
                    depth=outer_depth,
                    z_offset=outer_z,
                    pull_out=False,
                    label=f"InsideToken_{r_idx}_{i}",
                )
            )
        # Outer finger bites
        for b_idx, by in enumerate((0.0, inside_inner_l - bite_d)):
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(bite_d, bite_d),
                    offset=(cx - bite_d / 2.0, by),
                    depth=outer_depth,
                    z_offset=outer_z,
                    pull_out=False,
                    label=f"InsideOuterBite_{b_idx}_{i}",
                )
            )
        # Middle rows 1 & 2 for cols 0, 2, 3 (leaving cols 1 & 4 for labels)
        if i not in (1, 4):
            for r_idx in (1, 2):
                elems.append(
                    CompartmentElement(
                        shape=ElementShape.CIRCLE,
                        size=(tok_d, tok_d),
                        offset=(cx - tok_r, row_cys[r_idx] - tok_r),
                        depth=9.8,
                        z_offset=inside_inner_h - 9.8,
                        pull_out=False,
                        label=f"InsideToken_{r_idx}_{i}",
                    )
                )
            for b_idx, by in enumerate((43.0 - bite_d / 2.0, 64.0 - bite_d / 2.0)):
                elems.append(
                    CompartmentElement(
                        shape=ElementShape.CIRCLE,
                        size=(bite_d, bite_d),
                        offset=(cx - bite_d / 2.0, by),
                        depth=9.8,
                        z_offset=inside_inner_h - 9.8,
                        pull_out=False,
                        label=f"InsideMidBite_{b_idx}_{i}",
                    )
                )
    # Far-end token well + finger bite
    far_cx = inside_inner_w - tok_r - 12.0
    far_cy = 39.75
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(tok_d, tok_d),
            offset=(far_cx - tok_r, far_cy - tok_r),
            depth=9.8,
            z_offset=inside_inner_h - 9.8,
            pull_out=False,
            label="InsideFarToken",
        )
    )
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(bite_d, bite_d),
            offset=(far_cx + tok_r - bite_d / 2.0, far_cy - bite_d / 2.0),
            depth=9.8,
            z_offset=inside_inner_h - 9.8,
            pull_out=False,
            label="InsideFarBite",
        )
    )
    return tuple(elems)


# ── 2. Train & Wagon Cards Box (5 pockets: 3 trains + 2 wagons) ───
t_box = project.box(
    BoxType.SLIPOVER,
    "TrainBox",
    size=(tray_width, train_box_len, tray_height),
    lid=_lid(
        "Trains",
        "blue",
        logo=str(ASSETS / "train_icon.svg"),
        logo_size_mm=16.0,
    ),
    expandable=False,
)
t_box.compartment(
    "TrainSlots",
    elements=_train_box_elements(),
)

# ── 3. Corporate Shares Boxes (2 full-width boxes, 5 companies each)
for i in range(2):
    s_box = project.box(
        BoxType.SLIPOVER,
        f"SharesBox_{i + 1}",
        size=(tray_width, train_box_len, tray_height),
        lid=_lid("Shares", "royalblue"),
        expandable=False,
    )
    for slot in range(5):
        s_box.compartment(
            f"ShareSlot_{slot + 1}",
            width_ratio=0.2,
            cut=FingerCut.SCOOP,
        )

# ── 4. Machine / Minor Companies & Concession Box (LastBox) ───────
last_box = project.box(
    BoxType.SLIPOVER,
    "LastBox",
    size=(tray_width, train_box_len, tray_height),
    lid=_lid("Machine/Minor", "teal"),
)
last_box.compartment(
    "MinorAndRails",
    elements=_last_box_elements(),
)

# ── 5. Large Tokens Box & Inside Token Tray (2-tier token section) ─
large_tokens = project.box(
    BoxType.SLIPOVER,
    "LargeTokensBox",
    size=(tray_width, rest_section_len, tray_height),
    lid=_lid("Major Tokens", "darkblue"),
)
large_tokens.compartment(
    "MajorTokens",
    elements=_large_tokens_elements(),
)

inside_tray = project.box(
    BoxType.NO_LID,
    "InsideTokenTray",
    size=(tray_width, rest_section_len, tray_height),
)
inside_tray.compartment(
    "InsideTokens",
    elements=_inside_token_tray_elements(),
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
