#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Nature board game organizer.

Ports examples/nature.scad to the pyboxbuilder Project API.
Organizes nature and hunter cards, player population dials, wooden leopard token,
and grass/meat food resources with automated spacers.
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
    StackableMode,
    run,
)

ASSETS = (
    Path(__file__).resolve().parent / "assets"
    if "__file__" in globals()
    else ROOT / "boxes" / "nature" / "assets"
)

# ── Box & Board Dimensions ────────────────────────────────────────
box_width = 210.0
box_length = 210.0
box_height = 75.0

board_thickness = 7.0
usable_height = box_height - board_thickness  # 68.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

card_width = 67.0
card_length = 92.0
disk_diameter = 46.0
disk_thickness = 4.0

card_box_width = (box_width - 2.0) / 2.0             # 104.0mm
card_box_length = card_width + wall_thickness * 2.0  # 73.0mm
card_box_height = usable_height                      # 68.0mm

hunter_card_box_width = card_box_width
hunter_card_box_length = card_box_length
hunter_card_box_height = 20.0

dial_box_width = 107.0
dial_box_length = (box_width - hunter_card_box_width - 2.0) / 2.0  # 52.0mm
dial_box_height = 51.0

leopard_box_width = dial_box_width                                        # 107.0mm
leopard_box_length = box_length - 2.0 - dial_box_length * 2.0 - card_box_length  # 31.0mm
leopard_box_height = dial_box_height                                      # 51.0mm

resource_box_width = box_length - dial_box_width - 2.0             # 101.0mm
resource_box_length = (box_length - 2.0 - card_box_length) / 2.0   # 67.5mm
resource_box_double_length = box_length - 2.0 - card_box_length    # 135.0mm
resource_box_height = dial_box_height / 2.0                        # 25.5mm

project = Project(
    "Nature",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

# ── Game Component Inventory (with physical specs) ────────────────
project.define_cards("Nature Cards", 99, size=(card_width, card_length))
project.define_cards("Hunter Cards", 10, size=(card_width, card_length))
project.define_cards("Solo / Event Cards", 6, size=(card_width, card_length))
project.define_piece("Population Dials", 20, diameter=disk_diameter, thickness=disk_thickness)
project.define_piece("Apex Leopard Meeple", 1, bulk=True)
project.define_piece("Grass Food Tokens", 60, bulk=True)
project.define_piece("Meat Food Tokens", 30, bulk=True)
project.define_piece("Population Tokens", 40, bulk=True)
project.component("Watering Hole Board", 1, kind="board")
project.component("Player Screens", 4, kind="board")
project.component("Rulebook", 1, kind="board")

project.board(
    "Boards, Screens & Rulebook",
    size=(box_width, box_length, board_thickness),
    position=(0.0, 0.0, usable_height),
    count=6,
    notes="Central watering hole board, 4 player screens, and rulebook atop insert",
    allocates={
        "Watering Hole Board": 1,
        "Player Screens": 4,
        "Rulebook": 1,
    },
)

NATURE_PATTERN = PatternBuilder(PatternType.VORONOI)
NATURE_FONT = "Futura:style=Bold"


def _nature_lid(
    text: str,
    frame_color: str,
    *,
    logo_file: str | None = None,
    logo_size: float = 16.0,
    narrow: bool = False,
) -> LidBuilder:
    use_logo = logo_file is not None and not narrow
    return LidBuilder(
        text=text,
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.CHAMFERED,
        label_finial=LabelFinial.NONE if narrow else LabelFinial.DIAMOND,
        font=NATURE_FONT,
        pattern=NATURE_PATTERN,
        text_color=Color("white"),
        frame_color=Color(frame_color),
        logo=str(ASSETS / logo_file) if use_logo and logo_file is not None else None,
        logo_color=Color("white") if use_logo else None,
        logo_position="left" if use_logo else None,
        label_logo_size_mm=logo_size if use_logo else None,
    )


# ── 1. Main Nature Cards Box ──────────────────────────────────────
project.box(
    BoxType.SLIDING,
    "NatureCardsBox",
    size=(card_box_width, card_box_length, card_box_height),
    position=(0.0, 0.0, 0.0),
    lid=_nature_lid("Nature Cards", "forestgreen"),
).compartment("Cards", cut=FingerCut.SCOOP, component="Nature Cards", count=99)

# ── 2. Small Decks (Hunter & Solo) ────────────────────────────────
project.box(
    BoxType.SLIDING,
    "HunterCardsBox",
    size=(hunter_card_box_width, hunter_card_box_length, hunter_card_box_height),
    position=(card_box_width, 0.0, 0.0),
    lid=_nature_lid("Hunters", "darkred"),
    stackable=StackableMode.PYRAMIDS,
).compartment("Cards", cut=FingerCut.SCOOP, component="Hunter Cards", count=10)

project.box(
    BoxType.SLIDING,
    "SoloCardsBox",
    size=(hunter_card_box_width, hunter_card_box_length, hunter_card_box_height),
    position=(card_box_width, 0.0, hunter_card_box_height),
    lid=_nature_lid("Solo / Event", "royalblue"),
    stackable=StackableMode.PYRAMIDS,
).compartment("Cards", cut=FingerCut.SCOOP, component="Solo / Event Cards", count=6)

# ── 3. Population Dials (x2) & Leopard Box ────────────────────────
dial_inner_width = dial_box_width - wall_thickness * 2.0      # 101.0mm
dial_inner_length = dial_box_length - wall_thickness * 2.0    # 46.0mm
dial_inner_height = dial_box_height - floor_thickness - lid_thickness  # 47.0mm


def _dial_box_elements() -> tuple[CompartmentElement, ...]:
    """Build 10 vertical standing dial slots intersected by a central finger channel."""
    elems: list[CompartmentElement] = [
        # Longitudinal finger-grab channel across the top center of all 10 dial slots
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(dial_inner_width, disk_diameter / 2.0),
            offset=(0.0, (dial_inner_length - disk_diameter / 2.0) / 2.0),
            depth=disk_diameter / 2.0 + 5.0,
            bottom_rounding=6.0,
            pull_out=False,
            label="DialFingerChannel",
        )
    ]
    slot_w = disk_thickness + 0.5
    for i in range(10):
        cx = disk_thickness / 2.0 + 5.0 + (disk_thickness + 5.6) * i
        elems.append(
            CompartmentElement(
                shape=ElementShape.RECT,
                size=(slot_w, dial_inner_length),
                offset=(cx - slot_w / 2.0, 0.0),
                depth=dial_inner_height,
                corner_rounding=0.5,
                pull_out=False,
                label=f"DialSlot_{i + 1}",
            )
        )
    return tuple(elems)


for idx in range(1, 3):
    project.box(
        BoxType.CAP,
        f"DialBox_{idx}",
        size=(dial_box_width, dial_box_length, dial_box_height),
        position=(resource_box_width, card_box_length + dial_box_length * (idx - 1), 0.0),
        lid=_nature_lid("Population Dials", "darkgoldenrod"),
    ).compartment(
        "Dials",
        size=(dial_inner_width, dial_inner_length),
        position=(0.0, 0.0),
        component="Population Dials",
        count=10,
        elements=_dial_box_elements(),
    )

project.box(
    BoxType.SLIDING,
    "LeopardBox",
    size=(leopard_box_width, leopard_box_length, leopard_box_height),
    position=(resource_box_width, card_box_length + dial_box_length * 2.0, 0.0),
    lid=_nature_lid("Apex Leopard", "peru", narrow=True),
).compartment("Leopard", cut=FingerCut.SCOOP, component="Apex Leopard Meeple", count=1)

# ── 4. Food & Population Resource Trays (Grass, Meat & Population) ─
project.box(
    BoxType.CAP,
    "ResourceBox_Grass",
    size=(resource_box_width, resource_box_length, resource_box_height),
    position=(0.0, card_box_length, resource_box_height),
    lid=_nature_lid("Grass", "green", logo_file="grass.svg", logo_size=16.0),
).compartment("GrassTokens", cut=FingerCut.SCOOP, component="Grass Food Tokens", count=60)

project.box(
    BoxType.CAP,
    "ResourceBox_Meat",
    size=(resource_box_width, resource_box_length, resource_box_height),
    position=(0.0, card_box_length + resource_box_length, resource_box_height),
    lid=_nature_lid("Meat", "firebrick", logo_file="meat.svg", logo_size=16.0),
).compartment("MeatTokens", cut=FingerCut.SCOOP, component="Meat Food Tokens", count=30)

project.box(
    BoxType.CAP,
    "ResourceBox_Population",
    size=(resource_box_width, resource_box_double_length, resource_box_height),
    position=(0.0, card_box_length, 0.0),
    lid=_nature_lid("Population", "darkgoldenrod", logo_file="population.svg", logo_size=18.0),
).compartment("PopulationTokens", cut=FingerCut.SCOOP, component="Population Tokens", count=40)

project.stack_order("HunterCardsBox", "SoloCardsBox")

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
