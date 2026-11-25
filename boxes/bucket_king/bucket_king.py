#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Bucket King 3D board game organizer.

Ports examples/bucket_king.scad to the pyboxbuilder Project API.
Organizes:
- 1 CardBox (single full-width well for 68 x 92mm cards with left finger scoop)
- 6 PlayerBoxes (69 x 71 x 34.5mm, each with a 2x2 grid of 3+4+4+4 = 15
  bucket-shaped tile wells and finger access cutouts)
- Automated spacer tray above the 2x3 player box layer.
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
    LabelFinial,
    LabelMode,
    LabelShape,
    LidBuilder,
    PatternBuilder,
    PatternType,
    Project,
    ScoopSide,
    run,
)

# ── Box & Component Dimensions (matching bucket_king.scad) ────────
box_width = 140.0
box_length = 288.0
box_height = 70.0

wall_thickness = 2.0
floor_thickness = 2.0
lid_thickness = 2.0

bucket_top_width = 28.0
bucket_length = 32.0
tile_thickness = 2.0

card_width = 68.0
card_length = 92.0

card_box_width = box_width - 2.0                                # 138.0mm
card_box_length = card_width + wall_thickness * 2.0 + 1.0       # 73.0mm
card_box_height = box_height - 2.0                              # 68.0mm

player_box_width = (box_width - 2.0) / 2.0                      # 69.0mm
player_box_length = (box_length - 2.0 - card_box_length) / 3.0  # 71.0mm
player_box_height = (box_height - 1.0) / 2.0                    # 34.5mm

SVG_DIR = Path(__file__).resolve().parent / "svg"
BUCKET_SVG = str(SVG_DIR / "bucket.svg")


def _player_bucket_elements(
    inner_width: float,
    inner_length: float,
    inner_height: float,
) -> tuple[CompartmentElement, ...]:
    """Build the 2x2 grid of 3+4+4+4 = 15 bucket tile wells with finger access."""
    elements: list[CompartmentElement] = []
    # Center the 2x2 bucket grid cleanly inside (inner_width, inner_length)
    grid_w = bucket_top_width * 2.0 + 1.0  # 57.0mm
    grid_l = bucket_length * 2.0 + 2.0     # 66.0mm
    x0 = (inner_width - grid_w) / 2.0
    y0 = (inner_length - grid_l) / 2.0

    for j in range(2):
        for i in range(2):
            num_tiles = 3 if (i == 0 and j == 0) else 4
            depth = num_tiles * tile_thickness + 0.5
            z_off = inner_height - depth
            bx = x0 + (bucket_top_width + 1.0) * i
            by = y0 + (bucket_length + 2.0) * j
            cx = bx + bucket_top_width / 2.0
            elements.append(
                CompartmentElement(
                    offset=(bx, by),
                    size=(bucket_top_width, bucket_length),
                    shape=ElementShape.SVG,
                    shape_file=BUCKET_SVG,
                    depth=depth,
                    z_offset=z_off,
                    pull_out=False,
                    label=f"BucketStack_{j * 2 + i + 1}",
                )
            )
            # Top & bottom finger-pinch slots for easy tile retrieval
            finger_d = 12.0
            for side_idx, fy in enumerate((by, by + bucket_length)):
                clamped_y = max(finger_d / 2.0, min(inner_length - finger_d / 2.0, fy))
                elements.append(
                    CompartmentElement(
                        offset=(cx - finger_d / 2.0, clamped_y - finger_d / 2.0),
                        size=(finger_d, finger_d),
                        shape=ElementShape.CIRCLE,
                        bottom_rounding=3.0,
                        depth=depth,
                        z_offset=z_off,
                        pull_out=False,
                        label=f"BucketFinger_{j * 2 + i + 1}_{side_idx + 1}",
                    )
                )
    return tuple(elements)


project = Project(
    "BucketKing",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    generate_spacers=True,
    box_defaults={"expandable": False},
)

# ── Game Component Inventory (with physical specs & SVG shapes) ───
project.define_cards("Animal Suit Cards", 80, size=(card_width, card_length), thickness=0.6)
project.define_tile(
    "Player Bucket Tiles",
    90,
    size=(bucket_top_width, bucket_length, tile_thickness),
    svg=BUCKET_SVG,
)

BUCKET_PATTERN = PatternBuilder(PatternType.CIRCLE)
BUCKET_FONT = "Futura:style=Bold"

# ── 1. Playing Card Box (single full-width compartment + left finger hole) ──
c_box = project.box(
    BoxType.CAP,
    "CardBox",
    size=(card_box_width, card_box_length, card_box_height),
    position=(0.0, 0.0, 0.0),
    lid=LidBuilder(
        text="Bucket King",
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.DOUBLE_FRAME,
        label_finial=LabelFinial.TRIPLE_DOT,
        font=BUCKET_FONT,
        pattern=BUCKET_PATTERN,
        text_color=Color("white"),
        frame_color=Color("royalblue"),
    ),
)
c_box.compartment("Cards", component="Animal Suit Cards", count=80)
c_box.finger_hole(ScoopSide.LEFT, width=20.0)

# ── 2. Six Player Bucket Boxes (2x3 grid behind CardBox) ──────────
player_inner_w = player_box_width - 2.0 * wall_thickness
player_inner_l = player_box_length - 2.0 * wall_thickness
player_inner_h = player_box_height - floor_thickness - lid_thickness
PLAYER_ELEMENTS = _player_bucket_elements(player_inner_w, player_inner_l, player_inner_h)

player_colors = [
    ("1", "crimson"),
    ("2", "royalblue"),
    ("3", "forestgreen"),
    ("4", "gold"),
    ("5", "purple"),
    ("6", "darkorange"),
]
for idx, (num, frame_col) in enumerate(player_colors):
    col = idx % 2
    row = idx // 2
    player_ink = Color("black" if frame_col == "gold" else "white")
    p_box = project.box(
        BoxType.CAP,
        f"PlayerBox_{num}",
        size=(player_box_width, player_box_length, player_box_height),
        position=(col * player_box_width, card_box_length + row * player_box_length, 0.0),
        lid=LidBuilder(
            text="Buckets",
            label_mode=LabelMode.FRAMED,
            label_shape=LabelShape.PILL,
            label_finial=LabelFinial.TRIPLE_DOT,
            font=BUCKET_FONT,
            pattern=BUCKET_PATTERN,
            text_color=player_ink,
            frame_color=Color(frame_col),
            logo=BUCKET_SVG,
            logo_color=player_ink,
            logo_position="left",
            label_logo_size_mm=15.0,
        ),
    )
    p_box.compartment(
        "Buckets",
        size=(player_inner_w, player_inner_l),
        elements=PLAYER_ELEMENTS,
        element_margin=0.0,
        component="Player Bucket Tiles",
        count=15,
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
