# SPDX-License-Identifier: Apache-2.0
"""Root board game insert — pyboxbuilder port of `examples/root.scad`."""

import math
import sys
from pathlib import Path
from typing import Any

# Repo root on sys.path
REPO_ROOT = (
    Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd()
)
sys.path.insert(0, str(REPO_ROOT))
for _sp in REPO_ROOT.glob(".venv/lib/*/site-packages"):
    sys.path.insert(0, str(_sp))
for _sp in REPO_ROOT.glob("venv/*/lib/*/site-packages"):
    sys.path.insert(0, str(_sp))

from dataclasses import replace
from pyboxbuilder import (
    BoxType,
    Color,
    LidBuilder,
    Project,
    run,
    centered,
    centered_in_box,
    PatternBuilder,
    PatternType,
)
from pyboxbuilder.compartments import CompartmentElement
from pyboxbuilder.enums import ElementShape


def pack_in_columns(
    items: list[dict[str, Any]],
    comp_size: tuple[float, float],
    column_width: float,
    spacing_x: float = 2.0,
    spacing_y: float = 2.0,
    comp_depth: float = 5.0,
) -> list[CompartmentElement]:
    comp_w, _comp_l = comp_size
    cols = max(1, int((comp_w + spacing_x) / (column_width + spacing_x)))
    col_y = [spacing_y] * cols
    col_x = [spacing_x + i * (column_width + spacing_x) for i in range(cols)]

    elements = []
    for item in items:
        c = col_y.index(min(col_y))
        w, l = item.get("size", (column_width, column_width))
        shape = item.get("shape", ElementShape.RECT)
        depth = item.get("depth", 4.0)
        svg = item.get("svg")
        rotation = item.get("rotation", 0.0)

        # Calculate rotated footprint size
        fw, fl = (l, w) if abs(rotation) == 90 else (w, l)

        cx = col_x[c] + fw / 2
        cy = col_y[c] + fl / 2

        pull_out = item.get("pull_out", True)
        pull_out_width = item.get("pull_out_width")

        has_custom_scoop = False
        if depth == 2.0:
            pull_out = False
            has_custom_scoop = True

        elements.append(
            centered(
                svg,
                (cx, cy),
                (w, l),
                shape=shape,
                rotation=rotation,
                depth=depth,
                pull_out=pull_out,
                pull_out_width=pull_out_width,
            )
        )
        if has_custom_scoop:
            # Cut a vertical cylinder notch on the bottom edge of the pocket
            # pointing towards the interior (Row 3) to avoid outer wall intrusion
            elements.append(
                centered(
                    None,
                    (cx, cy - l / 2),
                    (12.0, 12.0),
                    shape=ElementShape.CIRCLE,
                    depth=depth,
                    pull_out=False,
                )
            )
        insert_svg = item.get("insert_svg", svg)
        insert_text = item.get("text")
        if "insert_color" in item and (
            insert_svg is not None or insert_text is not None
        ):
            if item.get("is_winter"):
                # Offset the stamp center to the circular cap (unrotated x=1.5, y=0)
                rad = math.radians(rotation)
                ox = 1.5 * math.cos(rad)
                oy = 1.5 * math.sin(rad)
                rot = rotation - 90.0
                stamp_size = (4.0, 4.0)
            else:
                ox = 0.0
                oy = 0.0
                rot = rotation
                stamp_size = (w * 0.35, l * 0.35)

            if insert_text is not None:
                stamp_shape = ElementShape.TEXT
                stamp_content = insert_text
            else:
                stamp_shape = ElementShape.SVG
                stamp_content = insert_svg

            elements.append(
                centered(
                    stamp_content,
                    (cx + ox, cy + oy),
                    stamp_size,
                    shape=stamp_shape,
                    rotation=rot,
                    depth=0.6,
                    z_offset=comp_depth - depth,
                    color=item["insert_color"],
                    pull_out=False,
                )
            )
        col_y[c] += fl + spacing_y
    return elements


# SVG Assets directory path
SVG_DIR = REPO_ROOT / "boxes" / "root" / "svg"

# Project Setup
project = Project("Root", game_box_size=(214.0, 278.0, 67.0))

from pybosl2.shapes3d.base import CsgSolid

class MultiColorSolid(CsgSolid):
    def color(self, color_val):
        return self

def make_marquis_mmu_logo(w, l, depth):
    from pyboxbuilder.compartments.element import _svg_region
    black_raw = _svg_region(str(SVG_DIR / "marquis_multicolor_black.svg")).linear_extrude(height=depth)
    orange_raw = _svg_region(str(SVG_DIR / "marquis_multicolor_orange.svg")).linear_extrude(height=depth)
    white_raw = _svg_region(str(SVG_DIR / "marquis_multicolor_white.svg")).linear_extrude(height=depth)
    (cx, cy, cz), (span_x, span_y, _) = (black_raw | orange_raw | white_raw).bounds()
    black_centered = black_raw.translate([-cx, -cy, -cz])
    orange_centered = orange_raw.translate([-cx, -cy, -cz])
    white_centered = white_raw.translate([-cx, -cy, -cz])
    orange_non_overlap = (orange_centered - black_centered - white_centered).color("#ea7d27")
    white_non_overlap = (white_centered - black_centered).color("white")
    black_non_overlap = black_centered.color("black")
    logo_solid = black_non_overlap | orange_non_overlap | white_non_overlap
    logo_solid = logo_solid.translate([0.0, 0.0, depth / 2])
    logo_scaled = logo_solid.scale([w / max(float(span_x), 1e-9), l / max(float(span_y), 1e-9), 1.0])
    return MultiColorSolid(logo_scaled.shape)

def make_lizard_mmu_logo(w, l, depth):
    from pyboxbuilder.compartments.element import _svg_region
    black_raw = _svg_region(str(SVG_DIR / "lizard_multicolor_black.svg")).linear_extrude(height=depth)
    yellow_raw = _svg_region(str(SVG_DIR / "lizard_multicolor_yellow.svg")).linear_extrude(height=depth)
    (cx, cy, cz), (span_x, span_y, _) = (black_raw | yellow_raw).bounds()
    black_centered = black_raw.translate([-cx, -cy, -cz])
    yellow_centered = yellow_raw.translate([-cx, -cy, -cz])
    yellow_non_overlap = (yellow_centered - black_centered).color("#f2e45f")
    black_non_overlap = black_centered.color("black")
    logo_solid = black_non_overlap | yellow_non_overlap
    logo_solid = logo_solid.translate([0.0, 0.0, depth / 2])
    logo_scaled = logo_solid.scale([w / max(float(span_x), 1e-9), l / max(float(span_y), 1e-9), 1.0])
    return MultiColorSolid(logo_scaled.shape)

def make_riverfolk_mmu_logo(w, l, depth):
    from pyboxbuilder.compartments.element import _svg_region
    black_raw = _svg_region(str(SVG_DIR / "riverfolk_multicolor_black.svg")).linear_extrude(height=depth)
    green_raw = _svg_region(str(SVG_DIR / "riverfolk_multicolor_green.svg")).linear_extrude(height=depth)
    white_raw = _svg_region(str(SVG_DIR / "riverfolk_multicolor_white.svg")).linear_extrude(height=depth)
    (cx, cy, cz), (span_x, span_y, _) = (black_raw | green_raw | white_raw).bounds()
    black_centered = black_raw.translate([-cx, -cy, -cz])
    green_centered = green_raw.translate([-cx, -cy, -cz])
    white_centered = white_raw.translate([-cx, -cy, -cz])
    green_non_overlap = (green_centered - black_centered - white_centered).color("#4db6af")
    white_non_overlap = (white_centered - black_centered).color("white")
    black_non_overlap = black_centered.color("black")
    logo_solid = black_non_overlap | green_non_overlap | white_non_overlap
    logo_solid = logo_solid.translate([0.0, 0.0, depth / 2])
    logo_scaled = logo_solid.scale([w / max(float(span_x), 1e-9), l / max(float(span_y), 1e-9), 1.0])
    return MultiColorSolid(logo_scaled.shape)

def make_erie_mmu_logo(w, l, depth):
    from pyboxbuilder.compartments.element import _svg_region
    black_raw = _svg_region(str(SVG_DIR / "erie_multicolor_black.svg")).linear_extrude(height=depth)
    blue_raw = _svg_region(str(SVG_DIR / "erie_multicolor_blue.svg")).linear_extrude(height=depth)
    lightblue_raw = _svg_region(str(SVG_DIR / "erie_multicolor_lightblue.svg")).linear_extrude(height=depth)
    white_raw = _svg_region(str(SVG_DIR / "erie_multicolor_white.svg")).linear_extrude(height=depth)
    (cx, cy, cz), (span_x, span_y, _) = (black_raw | blue_raw | lightblue_raw | white_raw).bounds()
    black_centered = black_raw.translate([-cx, -cy, -cz])
    blue_centered = blue_raw.translate([-cx, -cy, -cz])
    lightblue_centered = lightblue_raw.translate([-cx, -cy, -cz])
    white_centered = white_raw.translate([-cx, -cy, -cz])
    blue_non_overlap = (blue_centered - black_centered - lightblue_centered - white_centered).color("#5690c7")
    lightblue_non_overlap = (lightblue_centered - black_centered - white_centered).color("#8ab3d5")
    white_non_overlap = (white_centered - black_centered).color("white")
    black_non_overlap = black_centered.color("black")
    logo_solid = black_non_overlap | blue_non_overlap | lightblue_non_overlap | white_non_overlap
    logo_solid = logo_solid.translate([0.0, 0.0, depth / 2])
    logo_scaled = logo_solid.scale([w / max(float(span_x), 1e-9), l / max(float(span_y), 1e-9), 1.0])
    return MultiColorSolid(logo_scaled.shape)

def make_vagabond_mmu_logo(w, l, depth):
    from pyboxbuilder.compartments.element import _svg_region
    black_raw = _svg_region(str(SVG_DIR / "vagabond_multicolor_black.svg")).linear_extrude(height=depth)
    grey_raw = _svg_region(str(SVG_DIR / "vagabond_multicolor_grey.svg")).linear_extrude(height=depth)
    white_raw = _svg_region(str(SVG_DIR / "vagabond_multicolor_white.svg")).linear_extrude(height=depth)
    (cx, cy, cz), (span_x, span_y, _) = (black_raw | grey_raw | white_raw).bounds()
    black_centered = black_raw.translate([-cx, -cy, -cz])
    grey_centered = grey_raw.translate([-cx, -cy, -cz])
    white_centered = white_raw.translate([-cx, -cy, -cz])
    grey_non_overlap = (grey_centered - black_centered - white_centered).color("#9b9b9b")
    white_non_overlap = (white_centered - black_centered).color("white")
    black_non_overlap = black_centered.color("black")
    logo_solid = black_non_overlap | grey_non_overlap | white_non_overlap
    logo_solid = logo_solid.translate([0.0, 0.0, depth / 2])
    logo_scaled = logo_solid.scale([w / max(float(span_x), 1e-9), l / max(float(span_y), 1e-9), 1.0])
    return MultiColorSolid(logo_scaled.shape)

# Base Lid configuration using SQUARE pattern matching original SCAD lids
LID_BASE = LidBuilder(pattern=PatternBuilder(PatternType.DENSE_HEX))

LID_MARQUIS = replace(
    LID_BASE, logo=make_marquis_mmu_logo, logo_color=Color("#ea7d27")
)
LID_ERIE = replace(LID_BASE, logo=make_erie_mmu_logo, logo_color=Color("#5690c7"))
LID_ALLIANCE = replace(
    LID_BASE, logo=str(SVG_DIR / "alliance_eyes.svg"), logo_color=Color("black")
)

LID_LIZARD = replace(
    LID_BASE, logo=make_lizard_mmu_logo, logo_color=Color("#f5d033")
)
LID_RIVERFOLK = replace(
    LID_BASE, logo=make_riverfolk_mmu_logo, logo_color=Color("#4db6af")
)
LID_VAGABOND = replace(
    LID_BASE, logo=make_vagabond_mmu_logo, logo_color=Color("grey")
)

# ── Boxes ─────────────────────────────────────────────────────────────────

# Card Boxes
card_size = (79.875, 98.5, 39.0)
project.card_box(
    "BaseCardBox",
    card_size=(74.875, 93.5),
    size=card_size,
    lid=LID_BASE.titled("Shared"),
    position=(0.0, 0.0, 28.0),
    no_rotate=True,
)

card_erie_size = (79.875, 98.5, 8.6)
project.card_box(
    "ErieCardBox",
    card_size=(74.875, 93.5),
    size=card_erie_size,
    lid=LID_BASE.titled("Erie"),
    position=(79.875, 0.0, 28.0),
    no_rotate=True,
)

card_vagabond_size = (79.875, 98.5, 19.4)
project.card_box(
    "VagabondCardBox",
    card_size=(74.875, 93.5),
    size=card_vagabond_size,
    lid=LID_BASE.titled("Vagabond"),
    position=(79.875, 0.0, 28.0 + 8.6),
    no_rotate=True,
)

card_overview_size = (79.875, 98.5, 11.0)
project.card_box(
    "OverviewCardBox",
    card_size=(74.875, 93.5),
    size=card_overview_size,
    lid=LID_BASE.titled("Overview"),
    position=(79.875, 0.0, 28.0 + 8.6 + 19.4),
    no_rotate=True,
)

# Stacked Item Boxes
item_box_length = 103.5
item_comp_size = (49.25, 99.5)

# ItemsBoxBottom (comp_depth = 6.0)
project.box(
    BoxType.SLIDING,
    "ItemsBoxBottom",
    size=(53.25, item_box_length, 10.0),
    lid=LID_BASE.titled("Items Bot"),
    position=(159.75, 0.0, 28.0),
    no_rotate=True,
).compartment(
    "Items",
    depth=6.0,
    elements=pack_in_columns(
        items=[
            {"svg": str(SVG_DIR / "torch.svg"), "depth": 4.0, "insert_color": "black"},
            {"svg": str(SVG_DIR / "boot.svg"), "depth": 6.0, "insert_color": "black"},
            {
                "svg": str(SVG_DIR / "crossbow.svg"),
                "depth": 4.0,
                "insert_color": "black",
            },
            {"svg": str(SVG_DIR / "sword.svg"), "depth": 6.0, "insert_color": "black"},
            {"svg": str(SVG_DIR / "teapot.svg"), "depth": 4.0, "insert_color": "black"},
            {"svg": str(SVG_DIR / "ruins.svg"), "depth": 6.0, "insert_color": "black"},
            {"svg": str(SVG_DIR / "ruins.svg"), "depth": 6.0, "insert_color": "black"},
            {"svg": str(SVG_DIR / "ruins.svg"), "depth": 4.0, "insert_color": "black"},
            {"svg": str(SVG_DIR / "coins.svg"), "depth": 2.0, "insert_color": "black"},
            {"svg": str(SVG_DIR / "bag.svg"), "depth": 2.0, "insert_color": "black"},
        ],
        comp_size=item_comp_size,
        column_width=18.5,
        spacing_x=4.08,
        spacing_y=1.16,
        comp_depth=6.0,
    ),
)

# ItemsBoxMiddle (comp_depth = 5.0)
project.box(
    BoxType.SLIDING,
    "ItemsBoxMiddle",
    size=(53.25, item_box_length, 9.0),
    lid=LID_BASE.titled("Items Mid"),
    position=(159.75, 0.0, 28.0 + 10.0),
    no_rotate=True,
).compartment(
    "Items",
    depth=5.0,
    elements=pack_in_columns(
        items=[
            {"svg": str(SVG_DIR / "bag.svg"), "depth": 4.0, "insert_color": "black"},
            {"svg": str(SVG_DIR / "boot.svg"), "depth": 4.0, "insert_color": "black"},
            {"svg": str(SVG_DIR / "sword.svg"), "depth": 4.0, "insert_color": "black"},
            {"svg": str(SVG_DIR / "teapot.svg"), "depth": 4.0, "insert_color": "black"},
            {"svg": str(SVG_DIR / "coins.svg"), "depth": 4.0, "insert_color": "black"},
            {"svg": str(SVG_DIR / "ruins.svg"), "depth": 4.0, "insert_color": "black"},
            {"svg": str(SVG_DIR / "ruins.svg"), "depth": 4.0, "insert_color": "black"},
            {
                "svg": str(SVG_DIR / "crossbow.svg"),
                "depth": 2.0,
                "insert_color": "black",
            },
            {"svg": str(SVG_DIR / "anvil.svg"), "depth": 2.0, "insert_color": "black"},
        ],
        comp_size=item_comp_size,
        column_width=18.5,
        spacing_x=4.08,
        spacing_y=1.16,
        comp_depth=5.0,
    ),
)

# ItemsBoxWinter (comp_depth = 5.0)
project.box(
    BoxType.SLIDING,
    "ItemsBoxWinter",
    size=(53.25, item_box_length, 9.0),
    lid=LID_BASE.titled("Winter"),
    position=(159.75, 0.0, 28.0 + 10.0 + 9.0),
    no_rotate=True,
).compartment(
    "WinterTokens",
    depth=5.0,
    elements=pack_in_columns(
        items=[
            # 2 slots for Fox (4 tokens)
            {
                "svg": str(SVG_DIR / "winter_token.svg"),
                "insert_svg": str(SVG_DIR / "fox.svg"),
                "shape": ElementShape.SVG,
                "depth": 5.0,
                "size": (15.5, 29.5),
                "rotation": 90,
                "insert_color": "black",
                "pull_out_width": 12.0,  # Smaller finger scoop to avoid wall intrusion
                "is_winter": True,
            },
            {
                "svg": str(SVG_DIR / "winter_token.svg"),
                "insert_svg": str(SVG_DIR / "fox.svg"),
                "shape": ElementShape.SVG,
                "depth": 5.0,
                "size": (15.5, 29.5),
                "rotation": 90,
                "insert_color": "black",
                "is_winter": True,
            },
            # 2 slots for Rabbit (4 tokens)
            {
                "svg": str(SVG_DIR / "winter_token.svg"),
                "insert_svg": str(SVG_DIR / "rabbit.svg"),
                "shape": ElementShape.SVG,
                "depth": 5.0,
                "size": (15.5, 29.5),
                "rotation": 90,
                "insert_color": "black",
                "is_winter": True,
            },
            {
                "svg": str(SVG_DIR / "winter_token.svg"),
                "insert_svg": str(SVG_DIR / "rabbit.svg"),
                "shape": ElementShape.SVG,
                "depth": 5.0,
                "size": (15.5, 29.5),
                "rotation": 90,
                "insert_color": "black",
                "is_winter": True,
            },
            # 2 slots for Mouse (4 tokens)
            {
                "svg": str(SVG_DIR / "winter_token.svg"),
                "insert_svg": str(SVG_DIR / "mouse.svg"),
                "shape": ElementShape.SVG,
                "depth": 5.0,
                "size": (15.5, 29.5),
                "rotation": 90,
                "insert_color": "black",
                "is_winter": True,
            },
            {
                "svg": str(SVG_DIR / "winter_token.svg"),
                "insert_svg": str(SVG_DIR / "mouse.svg"),
                "shape": ElementShape.SVG,
                "depth": 5.0,
                "size": (15.5, 29.5),
                "rotation": 90,
                "insert_color": "black",
                "pull_out_width": 12.0,  # Smaller finger scoop to avoid wall intrusion
                "is_winter": True,
            },
        ],
        comp_size=item_comp_size,
        column_width=29.5,
        spacing_x=7.875,
        spacing_y=1.0,
        comp_depth=5.0,
    ),
)

# ItemsBoxExtras (comp_depth = 7.0)
project.box(
    BoxType.SLIDING,
    "ItemsBoxExtras",
    size=(53.25, item_box_length, 11.0),
    lid=LID_BASE.titled("Extras"),
    position=(159.75, 0.0, 28.0 + 10.0 + 9.0 + 9.0),
    no_rotate=True,
).compartment(
    "Extras",
    depth=7.0,
    elements=pack_in_columns(
        items=[
            {
                "shape": ElementShape.CIRCLE,
                "size": (21.0, 21.0),
                "depth": 5.0,
                "text": "a/b",
                "insert_color": "black",
            },
            {
                "shape": ElementShape.CIRCLE,
                "size": (21.0, 21.0),
                "depth": 5.0,
                "text": "c/d",
                "insert_color": "black",
            },
            {
                "shape": ElementShape.CIRCLE,
                "size": (21.0, 21.0),
                "depth": 5.0,
                "text": "e/f",
                "insert_color": "black",
            },
            {
                "shape": ElementShape.RECT,
                "size": (18.5, 18.5),
                "depth": 5.0,
                "text": "g/h",
                "insert_color": "black",
            },
            {
                "shape": ElementShape.RECT,
                "size": (18.5, 18.5),
                "depth": 5.0,
                "text": "i/j",
                "insert_color": "black",
            },
            {
                "shape": ElementShape.RECT,
                "size": (18.5, 18.5),
                "depth": 5.0,
                "text": "k/l",
                "insert_color": "black",
            },
            {
                "shape": ElementShape.RECT,
                "size": (18.5, 18.5),
                "depth": 5.0,
                "text": "m/n",
                "insert_color": "black",
            },
            {
                "shape": ElementShape.RECT,
                "size": (18.5, 18.5),
                "depth": 5.0,
                "text": "o/p",
                "insert_color": "black",
            },
        ],
        comp_size=item_comp_size,
        column_width=21.0,
        spacing_x=2.41,
        spacing_y=3.3,
        comp_depth=7.0,
    ),
)

# Marquis Box Bottom
marquis_bottom_size = (106.5, 59.833, 24.5)
project.box(
    BoxType.CAP,
    "MarquisBoxBottom",
    size=marquis_bottom_size,
    lid=LID_MARQUIS,
    color=Color("orange"),
    position=(0.0, 98.5, 28.0),
    no_rotate=True,
).compartment(
    "Warriors",
    elements=[
        # 3 horizontal channels for cat tokens
        centered(None, (20.0, 27.916), (22.0, 46.0), depth=18.0, pull_out=True),
        centered(None, (50.0, 27.916), (22.0, 46.0), depth=18.0, pull_out=True),
        centered(None, (80.0, 27.916), (22.0, 46.0), depth=18.0, pull_out=True),
    ],
)

# Marquis Box Top
project.box(
    BoxType.SLIDING,
    "MarquisBoxTop",
    size=(106.5, 59.833, 14.5),
    lid=LID_MARQUIS,
    color=Color("orange"),
    position=(0.0, 98.5, 28.0 + 24.5),
    no_rotate=True,
).compartment(
    "WoodAndBuildings",
    elements=[
        # --- Wood Logs (2 slots, stacked 4-high, depth 8.0) ---
        centered(
            None,
            (10.91, 9.25),
            (15.0, 15.0),
            shape=ElementShape.CIRCLE,
            depth=8.0,
            pull_out=True,
        ),
        centered(
            None,
            (31.07, 9.25),
            (15.0, 15.0),
            shape=ElementShape.CIRCLE,
            depth=8.0,
            pull_out=True,
        ),
        # --- Recruiters / Handshake (2 slots, stacked 3-high, depth 6.0) ---
        centered(
            None,
            (71.39, 9.25),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=6.0,
            pull_out=True,
        ),
        centered(
            None,
            (91.55, 9.25),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=6.0,
            pull_out=True,
        ),
        # --- Workshops / Anvil (2 slots, stacked 3-high, depth 6.0) ---
        centered(
            None,
            (10.91, 46.583),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=6.0,
            pull_out=True,
        ),
        centered(
            None,
            (31.07, 46.583),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=6.0,
            pull_out=True,
        ),
        # --- Sawmills / Saw (2 slots, stacked 3-high, depth 6.0) ---
        centered(
            None,
            (71.39, 46.583),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=6.0,
            pull_out=True,
        ),
        centered(
            None,
            (91.55, 46.583),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=6.0,
            pull_out=True,
        ),
        # --- Keep (1 slot, stacked 1-high, depth 2.0) ---
        centered(
            None,
            (51.23, 11.25),
            (18.5, 18.5),
            shape=ElementShape.CIRCLE,
            depth=2.0,
            pull_out=True,
        ),
        # --- Score Laurel (1 slot, stacked 1-high, depth 2.0) ---
        centered(
            None,
            (51.23, 41.583),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=2.0,
            pull_out=True,
        ),
        # --- Wood Stamps ---
        centered(
            str(SVG_DIR / "log.svg"),
            (10.91, 9.25),
            (15.0 * 0.35, 15.0 * 0.35),
            depth=0.6,
            z_offset=12.9 - 8.0,
            color="black",
            pull_out=False,
        ),
        centered(
            str(SVG_DIR / "log.svg"),
            (31.07, 9.25),
            (15.0 * 0.35, 15.0 * 0.35),
            depth=0.6,
            z_offset=12.9 - 8.0,
            color="black",
            pull_out=False,
        ),
        # --- Recruiter Stamps ---
        centered(
            str(SVG_DIR / "handshake.svg"),
            (71.39, 9.25),
            (18.5 * 0.35, 18.5 * 0.35),
            depth=0.6,
            z_offset=12.9 - 6.0,
            color="black",
            pull_out=False,
        ),
        centered(
            str(SVG_DIR / "handshake.svg"),
            (91.55, 9.25),
            (18.5 * 0.35, 18.5 * 0.35),
            depth=0.6,
            z_offset=12.9 - 6.0,
            color="black",
            pull_out=False,
        ),
        # --- Workshop Stamps ---
        centered(
            str(SVG_DIR / "anvil.svg"),
            (10.91, 46.583),
            (18.5 * 0.35, 18.5 * 0.35),
            depth=0.6,
            z_offset=12.9 - 6.0,
            color="black",
            pull_out=False,
        ),
        centered(
            str(SVG_DIR / "anvil.svg"),
            (31.07, 46.583),
            (18.5 * 0.35, 18.5 * 0.35),
            depth=0.6,
            z_offset=12.9 - 6.0,
            color="black",
            pull_out=False,
        ),
        # --- Sawmill Stamps ---
        centered(
            str(SVG_DIR / "saw.svg"),
            (71.39, 46.583),
            (18.5 * 0.35, 18.5 * 0.35),
            depth=0.6,
            z_offset=12.9 - 6.0,
            color="black",
            pull_out=False,
        ),
        centered(
            str(SVG_DIR / "saw.svg"),
            (91.55, 46.583),
            (18.5 * 0.35, 18.5 * 0.35),
            depth=0.6,
            z_offset=12.9 - 6.0,
            color="black",
            pull_out=False,
        ),
        # --- Keep Stamp ---
        centered(
            str(SVG_DIR / "keep.svg"),
            (51.23, 11.25),
            (18.5 * 0.35, 18.5 * 0.35),
            depth=0.6,
            z_offset=12.9 - 2.0,
            color="black",
            pull_out=False,
        ),
        # --- Score Laurel Stamp ---
        centered(
            str(SVG_DIR / "laurel_wreath.svg"),
            (51.23, 41.583),
            (18.5 * 0.35, 18.5 * 0.35),
            depth=0.6,
            z_offset=12.9 - 2.0,
            color="black",
            pull_out=False,
        ),
    ],
)

# Erie Box Bottom
erie_bottom_size = (106.5, 59.833, 24.5)
project.box(
    BoxType.CAP,
    "ErieBoxBottom",
    size=erie_bottom_size,
    lid=LID_ERIE,
    color=Color("blue"),
    position=(0.0, 158.333, 28.0),
    no_rotate=True,
).compartment(
    "Warriors",
    elements=[
        # 2 horizontal channels for bird tokens
        centered(None, (30.0, 27.916), (22.0, 46.0), depth=18.0, pull_out=True),
        centered(None, (70.0, 27.916), (22.0, 46.0), depth=18.0, pull_out=True),
    ],
)

# Erie Box Top
project.box(
    BoxType.SLIDING,
    "ErieBoxTop",
    size=(53.25, 59.833, 14.5),
    lid=LID_ERIE,
    color=Color("blue"),
    position=(0.0, 158.333, 28.0 + 24.5),
    no_rotate=True,
).compartment(
    "Roosts",
    elements=[
        # Roost slots (stacked 4-high, depth 8.0)
        centered(
            None,
            (15.0, 20.0),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=8.0,
            pull_out=True,
        ),
        centered(
            None,
            (35.0, 20.0),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=8.0,
            pull_out=True,
        ),
        # Score marker (laurel wreath)
        centered(
            None,
            (25.0, 45.0),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=2.0,
            pull_out=True,
        ),
        # Floor Stamps
        centered(
            str(SVG_DIR / "tree.svg"),
            (15.0, 20.0),
            (18.5 * 0.35, 18.5 * 0.35),
            depth=0.6,
            z_offset=12.9 - 8.0,
            color="black",
            pull_out=False,
        ),
        centered(
            str(SVG_DIR / "tree.svg"),
            (35.0, 20.0),
            (18.5 * 0.35, 18.5 * 0.35),
            depth=0.6,
            z_offset=12.9 - 8.0,
            color="black",
            pull_out=False,
        ),
        centered(
            str(SVG_DIR / "laurel_wreath.svg"),
            (25.0, 45.0),
            (18.5 * 0.35, 18.5 * 0.35),
            depth=0.6,
            z_offset=12.9 - 2.0,
            color="black",
            pull_out=False,
        ),
    ],
)

# Alliance Box Bottom
alliance_bottom_size = (53.25, 59.833, 25.5)
project.box(
    BoxType.CAP,
    "AllianceBoxBottom",
    size=alliance_bottom_size,
    lid=LID_ALLIANCE,
    color=Color("green"),
    position=(106.5, 98.5, 28.0),
    no_rotate=True,
).compartment(
    "Warriors",
    elements=[
        # 2 horizontal channels for alliance tokens
        centered(None, (15.0, 27.916), (19.5, 46.0), depth=18.0, pull_out=True),
        centered(None, (34.25, 27.916), (19.5, 46.0), depth=18.0, pull_out=True),
        # Stamps/Inlays at the bottom of the channels (depth=0.6, z_offset = comp_depth - depth = 21.9 - 18.0 = 3.9)
        centered(
            str(SVG_DIR / "alliance_warrior.svg"),
            (15.0, 27.916),
            (12.0, 12.0),
            depth=0.6,
            z_offset=3.9,
            color="black",
            pull_out=False,
        ),
        centered(
            str(SVG_DIR / "alliance_warrior.svg"),
            (34.25, 27.916),
            (12.0, 12.0),
            depth=0.6,
            z_offset=3.9,
            color="black",
            pull_out=False,
        ),
    ],
)

# Alliance Box Top
project.box(
    BoxType.SLIDING,
    "AllianceBoxTop",
    size=(53.25, 59.833, 13.5),
    lid=LID_ALLIANCE,
    color=Color("green"),
    position=(106.5, 98.5, 28.0 + 25.5),
    no_rotate=True,
).compartment(
    "BasesAndSympathy",
    elements=[
        # Pockets (wells)
        # Alliance Camp / Bases (rectangular well, depth 6.0 for 3-high stack)
        centered(
            None,
            (15.0, 15.0),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=6.0,
            pull_out=True,
        ),
        # Sympathy / Fist (circular wells, depth 9.5 for 5-high stack)
        centered(
            None,
            (35.0, 15.0),
            (18.5, 18.5),
            shape=ElementShape.CIRCLE,
            depth=9.5,
            pull_out=True,
        ),
        centered(
            None,
            (25.0, 40.0),
            (18.5, 18.5),
            shape=ElementShape.CIRCLE,
            depth=9.5,
            pull_out=True,
        ),
        # Stamps/Inlays at the bottom of the pockets (depth=0.6, comp_depth = 9.9)
        # Bases (z_offset = 9.9 - 6.0 = 3.9)
        centered(
            str(SVG_DIR / "camp.svg"),
            (15.0, 15.0),
            (12.0, 12.0),
            depth=0.6,
            z_offset=3.9,
            color="black",
            pull_out=False,
        ),
        # Sympathy (z_offset = 9.9 - 9.5 = 0.4)
        centered(
            str(SVG_DIR / "fist.svg"),
            (35.0, 15.0),
            (12.0, 12.0),
            depth=0.6,
            z_offset=0.4,
            color="black",
            pull_out=False,
        ),
        centered(
            str(SVG_DIR / "fist.svg"),
            (25.0, 40.0),
            (12.0, 12.0),
            depth=0.6,
            z_offset=0.4,
            color="black",
            pull_out=False,
        ),
    ],
)

# Lizard Box Bottom
lizard_bottom_size = (106.5, 59.833, 26.5)
project.box(
    BoxType.CAP,
    "LizardBoxBottom",
    size=lizard_bottom_size,
    lid=LID_LIZARD,
    color=Color("yellow"),
    position=(0.0, 218.166, 28.0),
    no_rotate=True,
).compartment(
    "Warriors",
    elements=[
        # 5 rows of 5 individual lizard warrior slots
        *[
            centered(
                None,
                (10.0 + 19.8 * i, 7.0 + 10.0 * j),
                (18.0, 9.0),
                depth=20.0,
                pull_out=True,
            )
            for i in range(5)
            for j in range(5)
        ]
    ],
)

# Lizard Box Top
project.box(
    BoxType.SLIDING,
    "LizardBoxTop",
    size=(79.875, 59.833, 12.5),
    lid=LID_LIZARD,
    color=Color("yellow"),
    position=(0.0, 218.166, 28.0 + 26.5),
    no_rotate=True,
).compartment(
    "Gardens",
    elements=[
        # Rectangular Pockets (3x2 Grid)
        centered(
            None,
            (16.34, 17.5),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=8.0,
            pull_out=True,
        ),
        centered(
            None,
            (39.93, 17.5),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=8.0,
            pull_out=True,
        ),
        centered(
            None,
            (63.52, 17.5),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=8.0,
            pull_out=True,
        ),
        centered(
            None,
            (16.34, 42.333),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=3.0,
            pull_out=True,
        ),
        centered(
            None,
            (39.93, 42.333),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=4.0,
            pull_out=True,
        ),
        centered(
            None,
            (63.52, 42.333),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=2.0,
            pull_out=True,
        ),
        # Stamps/Inlays at the bottom of the pockets (depth=0.6, comp_depth = 8.9)
        # Gardens (z_offset = 8.9 - 8.0 = 0.9)
        centered(
            str(SVG_DIR / "fox.svg"),
            (16.34, 17.5),
            (10.0, 10.0),
            depth=0.6,
            z_offset=0.9,
            color="black",
            pull_out=False,
        ),
        centered(
            str(SVG_DIR / "rabbit.svg"),
            (39.93, 17.5),
            (10.0, 10.0),
            depth=0.6,
            z_offset=0.9,
            color="black",
            pull_out=False,
        ),
        centered(
            str(SVG_DIR / "mouse.svg"),
            (63.52, 17.5),
            (10.0, 10.0),
            depth=0.6,
            z_offset=0.9,
            color="black",
            pull_out=False,
        ),
        # Score Laurel (z_offset = 8.9 - 3.0 = 5.9)
        centered(
            str(SVG_DIR / "laurel_wreath.svg"),
            (16.34, 42.333),
            (12.0, 12.0),
            depth=0.6,
            z_offset=5.9,
            color="black",
            pull_out=False,
        ),
        # Faction (z_offset = 8.9 - 4.0 = 4.9)
        centered(
            str(SVG_DIR / "lizard_faction.svg"),
            (39.93, 42.333),
            (10.0, 10.0),
            depth=0.6,
            z_offset=4.9,
            color="black",
            pull_out=False,
        ),
        # Outcast (z_offset = 8.9 - 2.0 = 6.9)
        centered(
            str(SVG_DIR / "outcast.svg"),
            (63.52, 42.333),
            (10.0, 10.0),
            depth=0.6,
            z_offset=6.9,
            color="black",
            pull_out=False,
        ),
    ],
)

# Riverfolk Box Bottom
riverfolk_bottom_size = (53.25, 59.833, 26.5)
project.box(
    BoxType.CAP,
    "RiverfolkBoxBottom",
    size=riverfolk_bottom_size,
    lid=LID_RIVERFOLK,
    color=Color("teal"),
    position=(106.5, 218.166, 28.0),
    no_rotate=True,
).compartment(
    "Warriors",
    elements=[
        # 3 horizontal channels
        centered(None, (10.0, 27.916), (16.0, 46.0), depth=18.0, pull_out=True),
        centered(None, (24.625, 27.916), (16.0, 46.0), depth=18.0, pull_out=True),
        centered(None, (39.25, 27.916), (16.0, 46.0), depth=18.0, pull_out=True),
        # Stamps/Inlays at the bottom of the channels (depth=0.6, z_offset = comp_depth - depth = 22.9 - 18.0 = 4.9)
        centered(
            str(SVG_DIR / "riverfolk_warrior.svg"),
            (10.0, 27.916),
            (12.0, 15.0),
            depth=0.6,
            z_offset=4.9,
            color="black",
            pull_out=False,
        ),
        centered(
            str(SVG_DIR / "riverfolk_warrior.svg"),
            (24.625, 27.916),
            (12.0, 15.0),
            depth=0.6,
            z_offset=4.9,
            color="black",
            pull_out=False,
        ),
        centered(
            str(SVG_DIR / "riverfolk_warrior.svg"),
            (39.25, 27.916),
            (12.0, 15.0),
            depth=0.6,
            z_offset=4.9,
            color="black",
            pull_out=False,
        ),
    ],
)

# Riverfolk Box Top
project.box(
    BoxType.SLIDING,
    "RiverfolkBoxTop",
    size=(79.875, 59.833, 12.5),
    lid=LID_RIVERFOLK,
    color=Color("teal"),
    position=(79.875, 218.166, 28.0 + 26.5),
    no_rotate=True,
).compartment(
    "TradePosts",
    elements=[
        # Pockets (wells, depth 8.0)
        # Trade Posts (Signs)
        centered(
            None,
            (16.34, 17.5),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=8.0,
            pull_out=True,
        ),
        centered(
            None,
            (39.93, 17.5),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=8.0,
            pull_out=True,
        ),
        # Glass gems (Egg shapes)
        centered(
            None,
            (63.52, 17.5),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=8.0,
            pull_out=True,
        ),
        # Glass Gem 2
        centered(
            None,
            (16.34, 42.333),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=8.0,
            pull_out=True,
        ),
        # Glass Gem 3
        centered(
            None,
            (39.93, 42.333),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=8.0,
            pull_out=True,
        ),
        # Score marker (Laurel wreath)
        centered(
            None,
            (63.52, 42.333),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=3.0,
            pull_out=True,
        ),
        # Stamps/Inlays at the bottom of the pockets (depth=0.6, comp_depth = 8.9)
        # Trade Posts (z_offset = 8.9 - 8.0 = 0.9)
        centered(
            str(SVG_DIR / "sign.svg"),
            (16.34, 17.5),
            (12.0, 12.0),
            depth=0.6,
            z_offset=0.9,
            color="black",
            pull_out=False,
        ),
        centered(
            str(SVG_DIR / "sign.svg"),
            (39.93, 17.5),
            (12.0, 12.0),
            depth=0.6,
            z_offset=0.9,
            color="black",
            pull_out=False,
        ),
        # Glass Gem 1 (z_offset = 8.9 - 8.0 = 0.9)
        centered(
            str(SVG_DIR / "gem.svg"),
            (63.52, 17.5),
            (12.0, 12.0),
            depth=0.6,
            z_offset=0.9,
            color="black",
            pull_out=False,
        ),
        # Glass Gem 2 & 3 (z_offset = 8.9 - 8.0 = 0.9)
        centered(
            str(SVG_DIR / "gem.svg"),
            (16.34, 42.333),
            (12.0, 12.0),
            depth=0.6,
            z_offset=0.9,
            color="black",
            pull_out=False,
        ),
        centered(
            str(SVG_DIR / "gem.svg"),
            (39.93, 42.333),
            (12.0, 12.0),
            depth=0.6,
            z_offset=0.9,
            color="black",
            pull_out=False,
        ),
        # Score marker (z_offset = 8.9 - 3.0 = 5.9)
        centered(
            str(SVG_DIR / "laurel_wreath.svg"),
            (63.52, 42.333),
            (12.0, 12.0),
            depth=0.6,
            z_offset=5.9,
            color="black",
            pull_out=False,
        ),
    ],
)

# Vagabond Box
project.box(
    BoxType.SLIDING,
    "VagabondBox",
    size=(53.25, 59.833, 16.0),
    lid=LID_VAGABOND,
    color=Color("grey"),
    position=(106.5, 158.333, 28.0),
    no_rotate=True,
).compartment(
    "ItemsAndScore",
    elements=[
        centered(
            str(SVG_DIR / "vagabond_warrior.svg"), (15.0, 20.0), (21.0, 22.0), depth=9.0
        ),
        # Relations
        # Pocket (well, depth 4.0)
        centered(
            None,
            (35.0, 20.0),
            (18.5, 18.5),
            shape=ElementShape.RECT,
            depth=4.0,
            pull_out=True,
        ),
        # Stamp/Inlay at the bottom (z_offset = 12.4 - 4.0 = 8.4)
        centered(
            str(SVG_DIR / "laurel_wreath.svg"),
            (35.0, 20.0),
            (12.0, 12.0),
            depth=0.6,
            z_offset=8.4,
            color="black",
            pull_out=False,
        ),
    ],
)

# Spacer Box (actual size of remaining box area, acting as the placeholder/boards spacer)
project.box(
    BoxType.NO_LID,
    "SpacerBox",
    size=(53.25, 172.5, 39.0),
    position=(159.75, 103.5, 28.0),
    no_rotate=True,
)

# Dice Box
project.box(
    BoxType.SLIDING,
    "DiceBox",
    size=(53.25, 59.833, 26.0),
    lid=LID_BASE.titled("Dice"),
    position=(106.5, 158.333, 28.0 + 16.0),
    no_rotate=True,
).compartment(
    "Dice",
    elements=[
        centered(
            None,
            (14.0, 14.0),
            (22.0, 22.0),
            shape=ElementShape.CIRCLE,
            depth=20.0,
            pull_out=True,
        ),
        centered(
            None,
            (35.25, 41.833),
            (22.0, 22.0),
            shape=ElementShape.CIRCLE,
            depth=20.0,
            pull_out=True,
        ),
    ],
)

if __name__ == "__main__":
    run(project, show_lids=True, remove_layers=0)
