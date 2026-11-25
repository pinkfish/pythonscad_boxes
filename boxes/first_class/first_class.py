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
    else ROOT / "boxes" / "first_class" / "assets"
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

player_cube = 8.5
meeple_width = 15.5
meeple_length = 21.0
meeple_thickness = 10.5
train_length = 15.5
train_width = 11.5

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

# ── Game Component Inventory (with physical specs & SVG shapes) ───
project.define_piece(
    "Locomotives",
    4,
    size=(train_length, train_width, meeple_thickness),
    svg=ASSETS / "train_token.svg",
)
project.define_piece(
    "Conductors",
    12,
    size=(meeple_width, meeple_length, meeple_thickness),
    svg=ASSETS / "meeple_token.svg",
)
project.define_piece("Scoring Cubes", 24, size=(player_cube, player_cube, player_cube), bulk=True)
project.define_piece("Coins", 48, bulk=True)
project.define_piece("Evidence Tokens", 26, bulk=True)
project.define_cards("Module Cards", 120, size=(card_width, card_length), thickness=single_card_thickness)
project.define_cards("Base Action Cards", 72, size=(card_width, card_length), thickness=0.45)
project.define_cards("Mail Car Cards", 16, size=(card_width, card_length), thickness=single_card_thickness)
project.define_cards("Railroad 0-1 Cards", 50, size=(card_width, card_length), thickness=single_card_thickness)
project.define_cards("Railroad 2-4 Cards", 24, size=(card_width, card_length), thickness=single_card_thickness)
project.define_cards("Railroad 7-12 Cards", 20, size=(card_width, card_length), thickness=single_card_thickness)
project.define_cards("Whodunit Cards", 4, size=(card_width, card_length), thickness=single_card_thickness)
project.define_cards("Game End Cards", 21, size=(card_width, card_length), thickness=single_card_thickness)
project.define_tile("Start Player Tile", 1, size=(card_width, card_length, board_thickness))
project.define_piece("Start Player Figure", 1, bulk=True)
project.define_tile("Locomotive Tiles", 8, size=(locomotive_tile_width, locomotive_tile_length, board_thickness))
project.define_tile("Constantinople Tile", 1, size=(locomotive_tile_width, locomotive_tile_length, board_thickness))
project.component("Score Board", 1, kind="board")
project.component("Player Boards", 4, kind="board")
project.component("Rulebook", 1, kind="board")

project.board(
    "Boards & Rulebook",
    size=(box_width, box_length, board_thickness + rule_book_thickness),
    position=(0.0, 0.0, usable_height),
    count=6,
    notes="Score board, 4 player boards, and rulebook",
    allocates={"Score Board": 1, "Player Boards": 4, "Rulebook": 1},
)

ORIENT_PATTERN = PatternBuilder(PatternType.CHEVRON)
ORIENT_FONT = "Georgia:style=Bold"


def _lid(
    text: str,
    frame_color: str,
    *,
    text_color: str = "white",
    shape: LabelShape = LabelShape.DOUBLE_FRAME,
    logo: str | None = None,
    logo_size_mm: float = 15.0,
) -> LidBuilder:
    return LidBuilder(
        text=text,
        label_mode=LabelMode.FRAMED,
        label_shape=shape,
        label_finial=LabelFinial.DIAMOND,
        font=ORIENT_FONT,
        pattern=ORIENT_PATTERN,
        text_color=Color(text_color),
        frame_color=Color(frame_color),
        logo=logo,
        logo_color=Color(text_color) if logo else None,
        logo_position="left",
        label_logo_size_mm=logo_size_mm if logo else None,
    )

# ── Row 1: Player Boxes (x4), Money Box & Evidence Box (Y = 0 .. 53) ──
player_inner_w = player_box_width - wall_thickness * 2.0  # 102.5mm
player_inner_l = player_box_length - wall_thickness * 2.0  # 47.0mm
player_card_diff = 1.0 + single_card_thickness * 6.0  # 4.6mm
player_token_depth = player_card_diff + meeple_thickness + 0.5  # 15.6mm
player_elements: tuple[CompartmentElement, ...] = (
    # Top card shelf (6 player cards resting over train + 3 meeples)
    CompartmentElement(
        shape=ElementShape.RECT,
        size=(card_length, card_width),
        offset=(0.0, 0.0),
        depth=player_card_diff,
        pull_out=False,
        label="PlayerCardsShelf",
    ),
    # Mid-depth finger relief dish under the card shelf
    CompartmentElement(
        shape=ElementShape.ROUNDED_RECT,
        size=(card_length - 5.0, card_width - 10.0),
        offset=(2.5, 5.0),
        depth=player_card_diff + meeple_thickness / 2.0,
        corner_radius=5.0,
        pull_out=False,
        label="MeepleFingerDish",
    ),
    # Train token silhouette well
    CompartmentElement(
        shape=ElementShape.SVG,
        shape_file=str(ASSETS / "train_token.svg"),
        size=(train_length, train_width),
        offset=(25.0, 7.0),
        depth=player_token_depth,
        pull_out=False,
        label="TrainToken",
    ),
    # 3 Meeple token silhouette wells
    *(
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "meeple_token.svg"),
            size=(meeple_width, meeple_length),
            offset=(9.0 + (meeple_width + 2.0) * i, 20.0),
            depth=player_token_depth,
            pull_out=False,
            label=f"MeepleToken_{i + 1}",
        )
        for i in range(3)
    ),
    # Player cubes well + shallow finger-lift dish on right end
    CompartmentElement(
        shape=ElementShape.RECT,
        size=(player_cube * 2.0, player_cube * 3.0),
        offset=(player_inner_w - 7.0 - player_cube * 2.0, (player_inner_l - player_cube * 3.0) / 2.0),
        depth=player_cube + 0.5,
        pull_out=False,
        label="CubesWell",
    ),
    CompartmentElement(
        shape=ElementShape.ROUNDED_RECT,
        size=(player_cube * 2.0 + 10.0, player_cube * 3.0 + 10.0),
        offset=(
            player_inner_w - 7.0 - player_cube * 2.0 - 5.0,
            (player_inner_l - (player_cube * 3.0 + 10.0)) / 2.0,
        ),
        depth=player_cube / 2.0,
        corner_radius=5.0,
        pull_out=False,
        label="CubesFingerDish",
    ),
)

player_positions = [
    ("yellow", (0.0, 0.0, 0.0)),
    ("blue", (0.0, 0.0, player_box_height)),
    ("red", (0.0, 0.0, player_box_height * 2.0)),
    ("green", (player_box_width, 0.0, 0.0)),
]

for color_name, pos in player_positions:
    project.box(
        BoxType.SLIDING,
        f"PlayerBox_{color_name}",
        size=(player_box_width, player_box_length, player_box_height),
        position=pos,
        lid=_lid(
            f"Player ({color_name.title()})",
            color_name,
            text_color="black" if color_name == "yellow" else "white",
            shape=LabelShape.ORNATE_FRAME,
            logo=str(ASSETS / "meeple_token.svg"),
            logo_size_mm=14.0,
        ),
    ).compartment(
        "PlayerBits",
        size=(player_inner_w, player_inner_l),
        position=(0.0, 0.0),
        elements=player_elements,
        allocates={"Locomotives": 1, "Conductors": 3, "Scoring Cubes": 6},
    )

project.box(
    BoxType.SLIDING,
    "MoneyBox",
    size=(player_box_width, player_box_length, player_box_height),
    position=(player_box_width, 0.0, player_box_height),
    lid=_lid(
        "Money",
        "lightgrey",
        text_color="black",
        logo=str(ASSETS / "coin.svg"),
        logo_size_mm=15.0,
    ),
).compartment("Coins", cut=FingerCut.SCOOP, component="Coins", count=48)

project.box(
    BoxType.SLIDING,
    "EvidenceBox",
    size=(player_box_width, player_box_length, player_box_height),
    position=(player_box_width, 0.0, player_box_height * 2.0),
    lid=_lid("Evidence", "lightsalmon", text_color="black"),
).compartment("Tokens", cut=FingerCut.SCOOP, component="Evidence Tokens", count=26)

# ── Row 2: Module, Base/Mail/Evidence, Railroad & Whodunit Cards (Y = 53 .. 129) ──
row2_y = player_box_length

module_decks = [
    ("ModuleA", "Module A", 0, 0, "Module Cards", 24),
    ("ModuleB", "Module B", 0, 1, "Module Cards", 24),
    ("ModuleC", "Module C", 0, 2, "Module Cards", 24),
    ("ModuleD", "Module D", 1, 0, "Module Cards", 24),
    ("ModuleE", "Module E", 1, 1, "Module Cards", 24),
    ("BaseCards_1", "Base I", 1, 2, "Base Action Cards", 36),
    ("BaseCards_2", "Base II", 2, 0, "Base Action Cards", 36),
    ("EvidenceAndMail", "Mail & Ev.", 2, 1, "Mail Car Cards", 16),
]

for deck_id, label_text, col, layer, comp_name, comp_count in module_decks:
    project.box(
        BoxType.SLIDING,
        f"CardBox_{deck_id}",
        size=(card_box_width, card_box_length, module_box_height),
        position=(card_box_width * col, row2_y, module_box_height * layer),
        lid=_lid(label_text, "darkblue"),
    ).compartment("Cards", cut=FingerCut.SCOOP, component=comp_name, count=comp_count)

project.box(
    BoxType.SLIDING,
    "CardBox_Railroad712",
    size=(card_box_width, card_box_length, railroad_7_12_height),
    position=(card_box_width * 2.0, row2_y, module_box_height * 2.0),
    lid=_lid("7-12", "cyan", text_color="black"),
).compartment("Cards", cut=FingerCut.SCOOP, component="Railroad 7-12 Cards", count=20)

project.box(
    BoxType.SLIDING,
    "CardBox_Railroad01",
    size=(card_box_width, card_box_length, railroad_0_1_height),
    position=(card_box_width * 3.0, row2_y, 0.0),
    lid=_lid("0-1", "cyan", text_color="black"),
).compartment("Cards", cut=FingerCut.SCOOP, component="Railroad 0-1 Cards", count=50)

project.box(
    BoxType.SLIDING,
    "CardBox_Railroad24",
    size=(card_box_width, card_box_length, railroad_2_4_height),
    position=(card_box_width * 3.0, row2_y, railroad_0_1_height),
    lid=_lid("2-4", "cyan", text_color="black"),
).compartment("Cards", cut=FingerCut.SCOOP, component="Railroad 2-4 Cards", count=24)

project.box(
    BoxType.SLIDING,
    "CardBox_Whodunit",
    size=(card_box_width, card_box_length, whodunit_card_box_height),
    position=(card_box_width * 3.0, row2_y, railroad_0_1_height + railroad_2_4_height),
    lid=_lid("Whodunit", "darkred"),
).compartment("Cards", cut=FingerCut.SCOOP, component="Whodunit Cards", count=4)

# ── Row 3: Game End, Start Tile & Locomotive Tile Boxes (Y = 129 .. 205) ──
row3_y = row2_y + card_box_length

project.box(
    BoxType.SLIDING,
    "CardBox_GameEnd",
    size=(card_box_width, card_box_length, game_end_card_box_height),
    position=(0.0, row3_y, 0.0),
    lid=_lid("End", "deepskyblue"),
).compartment("Cards", cut=FingerCut.SCOOP, component="Game End Cards", count=21)

project.box(
    BoxType.SLIDING,
    "StartTileCardBox",
    size=(card_box_width, card_box_length, start_tile_box_height),
    position=(0.0, row3_y, game_end_card_box_height),
    lid=_lid("Start", "khaki", text_color="black"),
).compartment(
    "StartTile",
    cut=FingerCut.SCOOP,
    allocates={"Start Player Tile": 1, "Start Player Figure": 1},
)

project.box(
    BoxType.SLIDING,
    "LocomotiveTileBox",
    size=(locomotive_box_width, locomotive_box_length, locomotive_box_height),
    position=(card_box_width, row3_y, 0.0),
    lid=_lid(
        "Locomotive",
        "aquamarine",
        text_color="black",
        shape=LabelShape.ORNATE_FRAME,
        logo=str(ASSETS / "train_token.svg"),
        logo_size_mm=15.0,
    ),
).compartment(
    "Tiles",
    cut=FingerCut.SCOOP,
    allocates={"Locomotive Tiles": 8, "Constantinople Tile": 1},
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
