#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Isle of Trains: All Aboard board game organizer.

Ports examples/isle_of_trains.scad to the pyboxbuilder Project API.
Organizes playing cards, destination tiles, track tiles, ticket tiles,
victory hex tokens, and wooden train markers with automated spacers.
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

# ── Box Dimensions ────────────────────────────────────────────────
box_width = 130.0
box_length = 180.0
box_height = 38.0

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

card_width = 62.5
card_length = 89.0

destination_tile_width = 18.0
track_tile_width = 20.5
num_destination_tiles = 6
token_thickness = 2.0

destination_box_width = box_width - 1.0  # 129.0mm
destination_box_length = destination_tile_width + track_tile_width + 1.0 + wall_thickness * 2.0  # 45.5mm
destination_box_height = token_thickness * num_destination_tiles + 0.5 + lid_thickness * 2.0   # 16.5mm
victory_box_height = box_height - destination_box_height - 0.5                                   # 21.0mm

card_box_width = card_length + wall_thickness * 2.0 + 3.0  # 98.0mm
card_box_length = card_width + wall_thickness * 2.0 + 0.5  # 69.0mm
card_box_height = box_height - 1.0                         # 37.0mm

ticket_box_length = box_length - destination_box_length - 1.0  # 133.5mm
ticket_box_width = box_width - card_box_width - 1.0            # 31.0mm
ticket_box_height = box_height - 1.0

middle_box_length = ticket_box_length - card_box_length        # 64.5mm
middle_box_width = card_box_width
middle_box_height = box_height - 1.0

project = Project(
    "IsleOfTrains",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    generate_spacers=True,
)

TRAIN_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Destination Box & Victory Box (Stacked 2-high at Y = 0) ────
dest_box = project.box(
    BoxType.CAP,
    "DestinationBox",
    size=(destination_box_width, destination_box_length, destination_box_height),
    lid=LidBuilder(
        text="Destinations",
        label_mode=LabelMode.FRAMED,
        pattern=TRAIN_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkgreen"),
    ),
    position=(0.0, 0.0, 0.0),
    no_rotate=True,
)
dest_box.compartment(
    "Destinations",
    width_ratio=0.5,
    depth=destination_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)
dest_box.compartment(
    "Tracks",
    width_ratio=0.5,
    depth=destination_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

vic_box = project.box(
    BoxType.CAP,
    "VictoryBox",
    size=(destination_box_width, destination_box_length, victory_box_height),
    lid=LidBuilder(
        text="Victory",
        label_mode=LabelMode.FRAMED,
        pattern=TRAIN_PATTERN,
        text_color=Color("white"),
        frame_color=Color("gold"),
    ),
    position=(0.0, 0.0, destination_box_height),
    no_rotate=True,
)
for slot in range(4):
    vic_box.compartment(
        f"HexTokens_{slot + 1}",
        width_ratio=0.25,
        depth=victory_box_height - floor_thickness - 1.0,
        cut=FingerCut.SCOOP,
    )

# ── 2. Middle Storage Box (Y = destination_box_length) ────────────
mid_box = project.box(
    BoxType.CAP,
    "MiddleBox",
    size=(middle_box_width, middle_box_length, middle_box_height),
    lid=LidBuilder(
        text="Passengers",
        label_mode=LabelMode.FRAMED,
        pattern=TRAIN_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkslategray"),
    ),
    position=(0.0, destination_box_length, 0.0),
    no_rotate=True,
)
mid_box.compartment(
    "Tokens",
    depth=middle_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── 3. Playing Cards Box (Y = destination + middle) ───────────────
y_cards = destination_box_length + middle_box_length

card_box = project.box(
    BoxType.CAP,
    "CardBox",
    size=(card_box_width, card_box_length, card_box_height),
    lid=LidBuilder(
        text="Cards",
        label_mode=LabelMode.FRAMED,
        pattern=TRAIN_PATTERN,
        text_color=Color("white"),
        frame_color=Color("navy"),
    ),
    position=(0.0, y_cards, 0.0),
    no_rotate=True,
)
card_box.compartment(
    "Cards",
    depth=card_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── 4. Ticket Tiles & Train Token Box (Right Column) ──────────────
tick_box = project.box(
    BoxType.CAP,
    "TicketBox",
    size=(ticket_box_width, ticket_box_length, ticket_box_height),
    lid=LidBuilder(
        text="Tickets",
        label_mode=LabelMode.FRAMED,
        pattern=TRAIN_PATTERN,
        text_color=Color("white"),
        frame_color=Color("firebrick"),
    ),
    position=(card_box_width, destination_box_length, 0.0),
    no_rotate=True,
)
tick_box.compartment(
    "TicketTiles",
    length_ratio=0.7,
    depth=ticket_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)
tick_box.compartment(
    "TrainMarker",
    length_ratio=0.3,
    depth=ticket_box_height - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
