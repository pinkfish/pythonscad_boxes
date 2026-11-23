#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Isle of Trains: All Aboard board game organizer.

Ports examples/isle_of_trains.scad to the pyboxbuilder Project API.
Organizes playing cards, destination tiles, track tiles, ticket tiles,
victory hex tokens, and wooden train markers with automated spacers.
"""

import math
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

ASSETS = (
    Path(__file__).resolve().parent / "assets"
    if "__file__" in globals()
    else ROOT / "boxes" / "isle_of_trains" / "assets"
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
destination_tile_length = 80.5
track_tile_width = 20.5
track_tile_length = 90.5
num_destination_tiles = 6
num_track_tiles = 2
token_thickness = 2.0

ticket_tile_width = 30.0
ticket_tile_length = 80.0
num_ticket_tiles = 10

train_token_length = 31.5
train_token_width = 17.5
train_token_thickness = 10.0

victory_hex_one_width = 18.0
victory_hex_three_width = 20.0
victory_hex_five_width = 21.5
victory_hex_ten_width = 24.0
num_victory_tokens = (12, 6, 4, 4)

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

# ── 1. Destination Box & Victory Box ──────────────────────────────
dest_inner_w = destination_box_width - wall_thickness * 2.0  # 123.0mm
dest_inner_l = destination_box_length - wall_thickness * 2.0  # 39.5mm
dest_tile_depth = token_thickness * num_destination_tiles + 0.5  # 12.5mm
track_tile_depth = token_thickness * num_track_tiles + 0.5  # 4.5mm
track_x0 = (dest_inner_w - track_tile_length) / 2.0  # 16.25mm
track_y0 = destination_tile_width + 1.0  # 19.0mm
track_bite_d = 20.0

project.box(
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
).compartment(
    "DestinationsAndTracks",
    size=(dest_inner_w, dest_inner_l),
    position=(0.0, 0.0),
    elements=(
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "destination_tile.svg"),
            size=(destination_tile_length, destination_tile_width),
            offset=((dest_inner_w - destination_tile_length) / 2.0, 0.0),
            depth=dest_tile_depth,
            pull_out=False,
            label="DestinationTiles",
        ),
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(track_tile_length, track_tile_width),
            offset=(track_x0, track_y0),
            depth=track_tile_depth,
            pull_out=False,
            label="TrackTiles",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(track_bite_d, track_bite_d),
            offset=(track_x0 - track_bite_d / 2.0, track_y0 + (track_tile_width - track_bite_d) / 2.0),
            depth=track_tile_depth,
            pull_out=False,
            label="TrackBiteLeft",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(track_bite_d, track_bite_d),
            offset=(
                track_x0 + track_tile_length - track_bite_d / 2.0,
                track_y0 + (track_tile_width - track_bite_d) / 2.0,
            ),
            depth=track_tile_depth,
            pull_out=False,
            label="TrackBiteRight",
        ),
    ),
)

vic_inner_w = destination_box_width - wall_thickness * 2.0  # 123.0mm
vic_inner_l = destination_box_length - wall_thickness * 2.0  # 39.5mm
vic_inner_h = victory_box_height - floor_thickness - lid_thickness  # 17.0mm
_cos30 = math.cos(math.radians(30.0))

one_diam = (victory_hex_one_width + 0.5) / _cos30
one_bit_len = num_victory_tokens[0] * token_thickness + 2.0
three_diam = (victory_hex_three_width + 0.5) / _cos30
three_bit_len = num_victory_tokens[1] * token_thickness + 1.0

five_flat = victory_hex_five_width + 0.5
five_diam = five_flat / _cos30
five_depth = token_thickness * num_victory_tokens[2] + 0.5
five_cx = 74.3
five_bite_d = 17.0

ten_flat = victory_hex_ten_width + 0.5
ten_diam = ten_flat / _cos30
ten_depth = token_thickness * num_victory_tokens[3] + 0.5
ten_cx = vic_inner_w - ten_diam / 2.0 - 2.0
ten_bite_d = 15.0

project.box(
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
).compartment(
    "VictoryHexTokens",
    size=(vic_inner_w, vic_inner_l),
    position=(0.0, 0.0),
    elements=(
        # 1-VP hex stack stored on-edge + finger channel
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(one_diam, one_bit_len),
            offset=(3.5, (vic_inner_l - one_bit_len) / 2.0),
            depth=vic_inner_h,
            corner_radius=2.0,
            bottom_rounding=4.0,
            pull_out=False,
            label="VictoryOneStack",
        ),
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(14.0, vic_inner_l),
            offset=(3.5 + (one_diam - 14.0) / 2.0, 0.0),
            depth=8.0,
            corner_radius=3.0,
            pull_out=False,
            label="VictoryOneFinger",
        ),
        # 3-VP hex stack stored on-edge + finger channel
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(three_diam, three_bit_len),
            offset=(10.0 + one_diam, (vic_inner_l - three_bit_len) / 2.0),
            depth=vic_inner_h,
            corner_radius=2.0,
            bottom_rounding=4.0,
            pull_out=False,
            label="VictoryThreeStack",
        ),
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(14.0, vic_inner_l),
            offset=(10.0 + one_diam + (three_diam - 14.0) / 2.0, 0.0),
            depth=8.0,
            corner_radius=3.0,
            pull_out=False,
            label="VictoryThreeFinger",
        ),
        # 5-VP flat hex stack + top/bottom finger bites
        CompartmentElement(
            shape=ElementShape.HEXAGON,
            size=(five_flat, five_flat),
            offset=(five_cx - five_diam / 2.0, (vic_inner_l - five_flat) / 2.0),
            depth=five_depth,
            pull_out=False,
            label="VictoryFiveHex",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(five_bite_d, five_bite_d),
            offset=(five_cx - five_bite_d / 2.0, vic_inner_l / 2.0 + five_flat / 2.0 - five_bite_d / 2.0),
            depth=five_depth,
            pull_out=False,
            label="VictoryFiveBiteTop",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(five_bite_d, five_bite_d),
            offset=(five_cx - five_bite_d / 2.0, vic_inner_l / 2.0 - five_flat / 2.0 - five_bite_d / 2.0),
            depth=five_depth,
            pull_out=False,
            label="VictoryFiveBiteBottom",
        ),
        # 10-VP flat hex stack + top/bottom finger bites
        CompartmentElement(
            shape=ElementShape.HEXAGON,
            size=(ten_flat, ten_flat),
            offset=(ten_cx - ten_diam / 2.0, (vic_inner_l - ten_flat) / 2.0),
            depth=ten_depth,
            pull_out=False,
            label="VictoryTenHex",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(ten_bite_d, ten_bite_d),
            offset=(ten_cx - ten_bite_d / 2.0, vic_inner_l / 2.0 + ten_flat / 2.0 - ten_bite_d / 2.0),
            depth=ten_depth,
            pull_out=False,
            label="VictoryTenBiteTop",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(ten_bite_d, ten_bite_d),
            offset=(ten_cx - ten_bite_d / 2.0, vic_inner_l / 2.0 - ten_flat / 2.0 - ten_bite_d / 2.0),
            depth=ten_depth,
            pull_out=False,
            label="VictoryTenBiteBottom",
        ),
    ),
)

# ── 2. Middle Storage Box ─────────────────────────────────────────
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
)
mid_box.compartment(
    "Tokens",
    cut=FingerCut.SCOOP,
)

# ── 3. Playing Cards Box ──────────────────────────────────────────
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
    expandable=False,
)
card_box.compartment(
    "Cards",
    cut=FingerCut.SCOOP,
)

# ── 4. Ticket Tiles & Train Token Box ─────────────────────────────
ticket_inner_w = ticket_box_width - wall_thickness * 2.0  # 25.0mm
ticket_inner_l = ticket_box_length - wall_thickness * 2.0  # 127.5mm
ticket_slot_w = token_thickness * num_ticket_tiles + 0.5  # 20.5mm
ticket_slot_y = ticket_inner_l - ticket_tile_length - 2.0  # 45.5mm
train_depth = train_token_thickness + 0.5  # 10.5mm
train_y0 = 7.0
train_bite_d = 14.0

project.box(
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
).compartment(
    "TicketsAndTrain",
    size=(ticket_inner_w, ticket_inner_l),
    position=(0.0, 0.0),
    elements=(
        # Standing ticket tiles slot + cross finger scoop
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(ticket_slot_w, ticket_tile_length),
            offset=((ticket_inner_w - ticket_slot_w) / 2.0, ticket_slot_y),
            depth=ticket_tile_width + 0.5,
            pull_out=False,
            label="TicketTiles",
        ),
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(ticket_inner_w, 20.0),
            offset=(0.0, ticket_slot_y + ticket_tile_length / 2.0 - 10.0),
            depth=16.0,
            corner_radius=5.0,
            pull_out=False,
            label="TicketFingerChannel",
        ),
        # Shallow train token well + front/back finger bites
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(train_token_width, train_token_length),
            offset=((ticket_inner_w - train_token_width) / 2.0, train_y0),
            depth=train_depth,
            pull_out=False,
            label="TrainMarker",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(train_bite_d, train_bite_d),
            offset=((ticket_inner_w - train_bite_d) / 2.0, train_y0 - train_bite_d / 2.0),
            depth=train_depth,
            pull_out=False,
            label="TrainBiteFront",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(train_bite_d, train_bite_d),
            offset=((ticket_inner_w - train_bite_d) / 2.0, train_y0 + train_token_length - train_bite_d / 2.0),
            depth=train_depth,
            pull_out=False,
            label="TrainBiteBack",
        ),
    ),
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
