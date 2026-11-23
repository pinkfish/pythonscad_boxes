#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Cascadero board game organizer.

Ports examples/cascadero.scad to the pyboxbuilder Project API.
Organizes player wooden envoys, heralds, farmers, and royal seal tokens
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
    LabelMode,
    LidBuilder,
    PatternBuilder,
    PatternType,
    Project,
    run,
)

# ── Box & Board Dimensions ────────────────────────────────────────
box_width = 212.0
box_length = 304.0
box_height = 40.0

board_thickness = 14.0
usable_height = box_height - board_thickness  # 26.0mm

wall_thickness = 2.0
floor_thickness = 2.0
lid_thickness = 2.0

player_width = (box_width - 2.0) / 2.0  # 105.0mm
player_length = 105.0
section_height = usable_height          # 26.0mm

top_width = ((box_width - 2.0) - 40.0) / 2.0  # 85.0mm
herald_width = 40.0
utility_length = box_length - player_length * 2.0  # 304 - 210 = 94.0mm

project = Project(
    "Cascadero",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

CASCADERO_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Player Envoy Boxes (4 players) ─────────────────────────────
first_width = 40.0
player_well_radius = 10.0
player_inner_width = player_width - wall_thickness * 2.0      # 101.0mm
player_inner_length = player_length - wall_thickness * 2.0    # 101.0mm
player_inner_height = section_height - floor_thickness - lid_thickness  # 22.0mm


def _player_box_elements() -> tuple[CompartmentElement, ...]:
    """2 side-by-side front rounded wells + 1 full-width back rounded well (cascadero.scad)."""
    front_well_w = (player_inner_width - wall_thickness) / 2.0  # 49.5mm
    back_y = first_width + wall_thickness  # 42.0mm
    back_l = player_inner_length - back_y  # 59.0mm
    return (
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(front_well_w, first_width),
            offset=(0.0, 0.0),
            depth=player_inner_height,
            corner_radius=player_well_radius,
            bottom_rounding=player_well_radius,
            pull_out=False,
            label="Markers_1",
        ),
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(front_well_w, first_width),
            offset=(front_well_w + wall_thickness, 0.0),
            depth=player_inner_height,
            corner_radius=player_well_radius,
            bottom_rounding=player_well_radius,
            pull_out=False,
            label="Markers_2",
        ),
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(player_inner_width, back_l),
            offset=(0.0, back_y),
            depth=player_inner_height,
            corner_radius=player_well_radius,
            bottom_rounding=player_well_radius,
            pull_out=False,
            label="Envoys",
        ),
    )


player_colors = ["red", "gold", "forestgreen", "royalblue"]
for idx, color_name in enumerate(player_colors):
    p_box = project.box(
        BoxType.SLIDING,
        f"PlayerBox_{idx + 1}",
        size=(player_width, player_length, section_height),
        lid=LidBuilder(
            text=f"Player {idx + 1}",
            label_mode=LabelMode.FRAMED,
            pattern=CASCADERO_PATTERN,
            text_color=Color("white"),
            frame_color=Color(color_name),
        ),
    )
    p_box.compartment(
        "PlayerWells",
        size=(player_inner_width, player_inner_length),
        position=(0.0, 0.0),
        elements=_player_box_elements(),
    )

# ── 2. Herald, Farmer & Seal Boxes ────────────────────────────────
project.box(
    BoxType.SLIDING,
    "SealsBox",
    size=(top_width, utility_length, section_height),
    lid=LidBuilder(
        text="Seals",
        label_mode=LabelMode.FRAMED,
        pattern=CASCADERO_PATTERN,
        text_color=Color("white"),
        frame_color=Color("firebrick"),
    ),
).compartment(
    "Seals",
    cut=FingerCut.SCOOP,
)

project.box(
    BoxType.SLIDING,
    "HeraldBox",
    size=(herald_width, utility_length, section_height),
    lid=LidBuilder(
        text="Herald",
        label_mode=LabelMode.FRAMED,
        pattern=CASCADERO_PATTERN,
        text_color=Color("white"),
        frame_color=Color("goldenrod"),
    ),
).compartment(
    "Heralds",
    cut=FingerCut.SCOOP,
)

project.box(
    BoxType.SLIDING,
    "FarmerBox",
    size=(top_width, utility_length, section_height),
    lid=LidBuilder(
        text="Farmer",
        label_mode=LabelMode.FRAMED,
        pattern=CASCADERO_PATTERN,
        text_color=Color("white"),
        frame_color=Color("seagreen"),
    ),
).compartment(
    "Farmers",
    cut=FingerCut.SCOOP,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
