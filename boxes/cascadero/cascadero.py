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

# ── 1. Player Envoy Boxes (4 players: 2x2 grid) ───────────────────
player_colors = ["red", "gold", "forestgreen", "royalblue"]
for idx, color_name in enumerate(player_colors):
    col = idx % 2
    row = idx // 2
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
        position=(col * player_width, row * player_length, 0.0),
        no_rotate=True,
    )
    p_box.compartment(
        "Envoys",
        length_ratio=0.6,
        depth=section_height - lid_thickness,
        cut=FingerCut.SCOOP,
    )
    p_box.compartment(
        "Markers",
        length_ratio=0.4,
        depth=section_height - lid_thickness,
        cut=FingerCut.SCOOP,
    )

# ── 2. Herald, Farmer & Seal Boxes (Y = player_length * 2 = 210mm)
y_utility = player_length * 2.0

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
    position=(0.0, y_utility, 0.0),
    no_rotate=True,
).compartment(
    "Seals",
    depth=section_height - lid_thickness,
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
    position=(top_width, y_utility, 0.0),
    no_rotate=True,
).compartment(
    "Heralds",
    depth=section_height - lid_thickness,
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
    position=(top_width + herald_width, y_utility, 0.0),
    no_rotate=True,
).compartment(
    "Farmers",
    depth=section_height - lid_thickness,
    cut=FingerCut.SCOOP,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
