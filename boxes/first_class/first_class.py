#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""First Class: All Aboard the Orient Express organizer.

Ports boxes/first_class/first_class.scad to the pyboxbuilder Project API.
Organizes 4 player boxes (meeples, trains, cubes), money box, evidence box,
8 module/base/mail/evidence card boxes, 3 railroad card boxes (0-1, 2-4, 7-12),
whodunit card box, game-end card box, start-player tile box, and locomotive
tile box with automatic spacers.
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
    FingerCut,
    LabelMode,
    LidBuilder,
    PatternBuilder,
    PatternType,
    Project,
    run,
)

# ── Game Box Dimensions ───────────────────────────────────────────
box_width = 217.0
box_length = 307.0
box_height = 70.0

rule_book_thickness = 3.0
board_thickness = 2.5
player_board_thickness = 9.5
usable_height = box_height - rule_book_thickness - board_thickness  # 64.5mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

# ── Component Dimensions ──────────────────────────────────────────
card_width = 47.0
card_length = 70.0
single_card_thickness = 0.6

num_railroad_0_1_card = 50
num_module_cards = 24

locomotive_tile_width = 68.5
locomotive_tile_length = 64.5

# ── Sub-Box Dimensions (matching first_class.scad) ────────────────
player_box_width = box_width / 2.0  # 108.5mm
player_box_length = card_width + wall_thickness * 2.0  # 53.0mm
player_box_height = usable_height / 3.0  # 21.5mm

card_box_width = box_width / 4.0  # 54.25mm
card_box_length = card_length + wall_thickness * 2.0  # 76.0mm
module_box_height = usable_height / 3.0  # 21.5mm

railroad_0_1_height = (
    floor_thickness + lid_thickness + single_card_thickness * num_railroad_0_1_card + 1.0
)  # 35.0mm
railroad_2_4_height = (
    floor_thickness + lid_thickness + single_card_thickness * num_module_cards + 1.0
)  # 19.4mm
railroad_7_12_height = module_box_height  # 21.5mm
whodunit_card_box_height = (
    usable_height - railroad_0_1_height - railroad_2_4_height
)  # 10.1mm

start_tile_box_height = floor_thickness + lid_thickness + board_thickness + 1.0  # 7.5mm
locomotive_box_length = card_box_length  # 76.0mm
locomotive_box_width = (
    floor_thickness + lid_thickness + locomotive_tile_length + wall_thickness * 2.0
)  # 74.5mm
locomotive_box_height = (
    floor_thickness + lid_thickness + board_thickness * 9.0 + 1.0
)  # 27.5mm
game_end_card_box_height = locomotive_box_height - start_tile_box_height  # 20.0mm

project = Project(
    "FirstClass",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness + rule_book_thickness,
    generate_spacers=True,
    box_defaults={"expandable": False},
)

ORIENT_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── Row 1: Player Boxes (x4), Money Box & Evidence Box (Y = 0 .. 53) ──
player_positions = [
    ("yellow", (0.0, 0.0, 0.0)),
    ("blue", (0.0, 0.0, player_box_height)),
    ("red", (0.0, 0.0, player_box_height * 2.0)),
    ("green", (player_box_width, 0.0, 0.0)),
]

for color_name, pos in player_positions:
    box = project.box(
        BoxType.SLIDING,
        f"PlayerBox_{color_name}",
        size=(player_box_width, player_box_length, player_box_height),
        position=pos,
        lid=LidBuilder(
            text=f"Player ({color_name.title()})",
            label_mode=LabelMode.FRAMED,
            pattern=ORIENT_PATTERN,
            text_color=Color("black" if color_name == "yellow" else "white"),
            frame_color=Color(color_name),
        ),
    )
    box.compartment("CardsMeeplesTrains", width_ratio=0.65, cut=FingerCut.SCOOP)
    box.compartment("Cubes", width_ratio=0.35, cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "MoneyBox",
    size=(player_box_width, player_box_length, player_box_height),
    position=(player_box_width, 0.0, player_box_height),
    lid=LidBuilder(
        text="Money",
        label_mode=LabelMode.FRAMED,
        pattern=ORIENT_PATTERN,
        text_color=Color("black"),
        frame_color=Color("lightgrey"),
    ),
).compartment("Coins", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "EvidenceBox",
    size=(player_box_width, player_box_length, player_box_height),
    position=(player_box_width, 0.0, player_box_height * 2.0),
    lid=LidBuilder(
        text="Evidence",
        label_mode=LabelMode.FRAMED,
        pattern=ORIENT_PATTERN,
        text_color=Color("black"),
        frame_color=Color("lightsalmon"),
    ),
).compartment("Tokens", cut=FingerCut.SCOOP)

# ── Row 2: Module, Base/Mail/Evidence, Railroad & Whodunit Cards (Y = 53 .. 129) ──
row2_y = player_box_length

module_decks = [
    ("ModuleA", "Module A", 0, 0),
    ("ModuleB", "Module B", 0, 1),
    ("ModuleC", "Module C", 0, 2),
    ("ModuleD", "Module D", 1, 0),
    ("ModuleE", "Module E", 1, 1),
    ("BaseCards_1", "Base I", 1, 2),
    ("BaseCards_2", "Base II", 2, 0),
    ("EvidenceAndMail", "Mail & Ev.", 2, 1),
]

for deck_id, label_text, col, layer in module_decks:
    project.box(
        BoxType.SLIDING,
        f"CardBox_{deck_id}",
        size=(card_box_width, card_box_length, module_box_height),
        position=(card_box_width * col, row2_y, module_box_height * layer),
        lid=LidBuilder(
            text=label_text,
            label_mode=LabelMode.FRAMED,
            pattern=ORIENT_PATTERN,
            text_color=Color("white"),
            frame_color=Color("darkblue"),
        ),
    ).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "CardBox_Railroad712",
    size=(card_box_width, card_box_length, railroad_7_12_height),
    position=(card_box_width * 2.0, row2_y, module_box_height * 2.0),
    lid=LidBuilder(
        text="7-12",
        label_mode=LabelMode.FRAMED,
        pattern=ORIENT_PATTERN,
        text_color=Color("black"),
        frame_color=Color("cyan"),
    ),
).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "CardBox_Railroad01",
    size=(card_box_width, card_box_length, railroad_0_1_height),
    position=(card_box_width * 3.0, row2_y, 0.0),
    lid=LidBuilder(
        text="0-1",
        label_mode=LabelMode.FRAMED,
        pattern=ORIENT_PATTERN,
        text_color=Color("black"),
        frame_color=Color("cyan"),
    ),
).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "CardBox_Railroad24",
    size=(card_box_width, card_box_length, railroad_2_4_height),
    position=(card_box_width * 3.0, row2_y, railroad_0_1_height),
    lid=LidBuilder(
        text="2-4",
        label_mode=LabelMode.FRAMED,
        pattern=ORIENT_PATTERN,
        text_color=Color("black"),
        frame_color=Color("cyan"),
    ),
).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "CardBox_Whodunit",
    size=(card_box_width, card_box_length, whodunit_card_box_height),
    position=(card_box_width * 3.0, row2_y, railroad_0_1_height + railroad_2_4_height),
    lid=LidBuilder(
        text="Whodunit",
        label_mode=LabelMode.FRAMED,
        pattern=ORIENT_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkred"),
    ),
).compartment("Cards", cut=FingerCut.SCOOP)

# ── Row 3: Game End, Start Tile & Locomotive Tile Boxes (Y = 129 .. 205) ──
row3_y = row2_y + card_box_length

project.box(
    BoxType.SLIDING,
    "CardBox_GameEnd",
    size=(card_box_width, card_box_length, game_end_card_box_height),
    position=(0.0, row3_y, 0.0),
    lid=LidBuilder(
        text="End",
        label_mode=LabelMode.FRAMED,
        pattern=ORIENT_PATTERN,
        text_color=Color("white"),
        frame_color=Color("deepskyblue"),
    ),
).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "StartTileCardBox",
    size=(card_box_width, card_box_length, start_tile_box_height),
    position=(0.0, row3_y, game_end_card_box_height),
    lid=LidBuilder(
        text="Start",
        label_mode=LabelMode.FRAMED,
        pattern=ORIENT_PATTERN,
        text_color=Color("black"),
        frame_color=Color("khaki"),
    ),
).compartment("StartTile", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "LocomotiveTileBox",
    size=(locomotive_box_width, locomotive_box_length, locomotive_box_height),
    position=(card_box_width, row3_y, 0.0),
    lid=LidBuilder(
        text="Locomotive",
        label_mode=LabelMode.FRAMED,
        pattern=ORIENT_PATTERN,
        text_color=Color("black"),
        frame_color=Color("aquamarine"),
    ),
).compartment("Tiles", cut=FingerCut.SCOOP)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
