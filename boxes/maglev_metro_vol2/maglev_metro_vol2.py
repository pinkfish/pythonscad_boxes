#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Maglev Metro: Volume 2 expansion organizer.

Ports examples/maglev_metro_vol2.scad to the pyboxbuilder Project API.
Organizes expansion cards, upgrade tiles, summon tiles, outback & ghost station hexes,
nanobots, and metro tokens with automated spacers.
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
box_width = 286.0
box_length = 286.0
box_height = 65.0

game_board_thickness = 17.0
game_board_base_thickness = 17.0
player_board_thickness = 2.5 * 4.0  # 10.0mm
usable_height = box_height - (game_board_thickness + player_board_thickness)  # 38.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

card_width = 67.0
card_length = 90.0

card_box_width = wall_thickness * 2.0 + card_width    # 73.0mm
card_box_length = wall_thickness * 2.0 + card_length  # 96.0mm
card_box_height = usable_height / 2.0                 # 19.0mm

upgrade_box_width = card_box_width                    # 73.0mm
upgrade_box_length = 126.0                            # 42mm * 3
upgrade_box_height = card_box_height

tile_box_width = 110.0
tile_box_length = 140.0
tile_box_height = usable_height / 2.0

project = Project(
    "MaglevMetroVol2",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=game_board_thickness + player_board_thickness,
    generate_spacers=True,
)

METRO_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Expansion Cards Box ────────────────────────────────────────
c_box = project.box(
    BoxType.SLIDING,
    "ExpansionCardsBox",
    size=(card_box_width, card_box_length, card_box_height),
    lid=LidBuilder(
        text="Maps 2",
        label_mode=LabelMode.FRAMED,
        pattern=METRO_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkorange"),
    ),
    position=(0.0, 0.0, 0.0),
    no_rotate=True,
)
c_box.compartment(
    "Cards",
    depth=card_box_height - lid_thickness,
    cut=FingerCut.SCOOP,
)

# ── 2. Upgrade Tile Box ───────────────────────────────────────────
u_box = project.box(
    BoxType.CAP,
    "UpgradeTileBox",
    size=(upgrade_box_width, upgrade_box_length, upgrade_box_height),
    lid=LidBuilder(
        text="Upgrades",
        label_mode=LabelMode.FRAMED,
        pattern=METRO_PATTERN,
        text_color=Color("white"),
        frame_color=Color("seagreen"),
    ),
    position=(0.0, card_box_length, 0.0),
    no_rotate=True,
)
for slot in range(3):
    u_box.compartment(
        f"Upgrade_{slot + 1}",
        length_ratio=1.0 / 3.0,
        depth=upgrade_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )

# ── 3. Outback & Ghost Station Hex Tiles ──────────────────────────
t_box = project.box(
    BoxType.CAP,
    "OutbackGhostTilesBox",
    size=(tile_box_width, tile_box_length, tile_box_height),
    lid=LidBuilder(
        text="Outback & Ghost",
        label_mode=LabelMode.FRAMED,
        pattern=METRO_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkviolet"),
    ),
    position=(card_box_width, 0.0, 0.0),
    no_rotate=True,
)
t_box.compartment(
    "OutbackHexes",
    width_ratio=0.5,
    depth=tile_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)
t_box.compartment(
    "GhostHexes",
    width_ratio=0.5,
    depth=tile_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── 4. Metro Tokens & Nanobots ────────────────────────────────────
tok_box = project.box(
    BoxType.CAP,
    "MetroTokenBox",
    size=(tile_box_width, tile_box_length, tile_box_height),
    lid=LidBuilder(
        text="Tokens & Nanobots",
        label_mode=LabelMode.FRAMED,
        pattern=METRO_PATTERN,
        text_color=Color("white"),
        frame_color=Color("gold"),
    ),
    position=(card_box_width, 0.0, tile_box_height),
    no_rotate=True,
)
tok_box.compartment(
    "Tickets",
    width_ratio=0.5,
    depth=tile_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)
tok_box.compartment(
    "Nanobots",
    width_ratio=0.5,
    depth=tile_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
