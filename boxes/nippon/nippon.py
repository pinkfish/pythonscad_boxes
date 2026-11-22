#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Nippon board game organizer.

Ports boxes/nippon/nippon.scad to the pyboxbuilder Project API.
Organizes 4 player boxes (ships, trains, track cylinders), 4 player bits boxes
(machine disks, influence/favour/contract tokens, scoring disks), factory tiles,
demand tiles, starting/old factory tiles, upgrade tiles, money, solo tokens,
late-game factories, round markers, 6 worker boxes, and 4 resource cube boxes
with automatic spacers.
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
box_width = 303.0
box_length = 380.0
box_height = 70.0

board_thickness = 9.0
player_boards_thickness = 4.3 * 4.0  # 17.2mm
handbook_thickness = 6.0
total_board_reserve = board_thickness + player_boards_thickness + handbook_thickness  # 32.2mm
usable_height = box_height - total_board_reserve  # 37.8mm

wall_thickness = 2.0
floor_thickness = 2.0
lid_thickness = 2.0

# ── Component Dimensions ──────────────────────────────────────────
cube_size = 10.5
cardboard_token_thickness = 2.5
ship_thickness = 10.0
factory_token_width = 51.0
factory_token_length = 55.5
demand_token_width = 42.0
old_factory_tile_width = 51.0

# ── Sub-Box Dimensions (matching nippon.scad) ─────────────────────
player_box_width = box_width / 4.0  # 75.75mm
player_box_length = 92.0
player_box_height = floor_thickness + lid_thickness + 1.0 + ship_thickness  # 15.0mm

player_box_bits_width = box_width / 2.0  # 151.5mm
player_box_bits_length = 92.0
player_box_bits_height = (usable_height - player_box_height) / 2.0  # 11.4mm

factory_tile_box_width = wall_thickness * 2.0 + factory_token_width + 1.0  # 56.0mm
factory_tile_box_length = wall_thickness * 2.0 + factory_token_length + 1.0  # 60.5mm
factory_tile_box_height = usable_height  # 37.8mm

demand_tile_box_width = wall_thickness * 2.0 + demand_token_width + 1.0  # 47.0mm
demand_tile_box_length = factory_tile_box_length  # 60.5mm
demand_tile_box_height = factory_tile_box_height  # 37.8mm

starting_tile_box_width = wall_thickness * 2.0 + old_factory_tile_width + 1.0  # 56.0mm
starting_tile_box_length = factory_tile_box_length  # 60.5mm
starting_tile_box_height = factory_tile_box_height  # 37.8mm

upgraded_tile_box_width = (
    box_width - starting_tile_box_width - demand_tile_box_width - factory_tile_box_width * 2.0
)  # 88.0mm
upgraded_tile_box_length = factory_tile_box_length  # 60.5mm
upgraded_tile_box_height = (
    cardboard_token_thickness + floor_thickness + lid_thickness
)  # 6.5mm (adjusted to 8.0mm if needed for sliding lid)

money_box_width = upgraded_tile_box_width  # 88.0mm
money_box_length = upgraded_tile_box_length  # 60.5mm
money_box_height = usable_height - upgraded_tile_box_height  # 31.3mm

solo_box_width = 93.0
solo_box_length = upgraded_tile_box_length  # 60.5mm
solo_box_height = floor_thickness + lid_thickness + 1.0 + cardboard_token_thickness * 5.0  # 17.5mm

late_game_factory_box_width = wall_thickness * 2.0 + factory_token_width + 1.0  # 56.0mm
late_game_factory_box_length = solo_box_length  # 60.5mm
late_game_factory_box_height = usable_height - solo_box_height  # 20.3mm

round_marker_box_width = solo_box_width - late_game_factory_box_width - 0.5  # 36.5mm
round_marker_box_length = solo_box_length  # 60.5mm
round_marker_box_height = usable_height - solo_box_height  # 20.3mm

worker_box_width = (box_width - solo_box_width - 1.0) / 3.0  # 69.67mm
worker_box_length = upgraded_tile_box_length  # 60.5mm
worker_box_height = usable_height / 2.0  # 18.9mm

resource_box_width = wall_thickness * 2.0 + cube_size * 8.0 + 24.0  # 112.0mm
resource_box_length = wall_thickness * 2.0 + cube_size * 3.0 + 2.0  # 37.5mm
resource_box_height = usable_height / 2.0  # 18.9mm
resource_box_double_width = box_width - resource_box_width  # 191.0mm

project = Project(
    "Nippon",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=total_board_reserve,
    generate_spacers=True,
    box_defaults={"expandable": False},
)

NIPPON_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── Row 1: Player Boxes & Player Bits Boxes (Y = 0 .. 92) ─────────
player_colors = ["purple", "yellow", "green", "red"]

for i, color_name in enumerate(player_colors):
    box = project.box(
        BoxType.CAP,
        f"PlayerBox_{color_name}",
        size=(player_box_width, player_box_length, player_box_height),
        position=(player_box_width * i, 0.0, 0.0),
        lid=LidBuilder(
            text="Ships & Trains",
            label_mode=LabelMode.FRAMED,
            pattern=NIPPON_PATTERN,
            text_color=Color("black" if color_name == "yellow" else "white"),
            frame_color=Color(color_name),
        ),
    )
    box.compartment("Ships", width_ratio=0.45, cut=FingerCut.SCOOP)
    box.compartment("TrainsAndMarkers", width_ratio=0.55, cut=FingerCut.SCOOP)

for i, color_name in enumerate(player_colors):
    col = i % 2
    layer = i // 2
    bits_box = project.box(
        BoxType.CAP,
        f"PlayerBoxBits_{color_name}",
        size=(player_box_bits_width, player_box_bits_length, player_box_bits_height),
        position=(
            player_box_bits_width * col,
            0.0,
            player_box_height + player_box_bits_height * layer,
        ),
        lid=LidBuilder(
            text=f"Player ({color_name.title()})",
            label_mode=LabelMode.FRAMED,
            pattern=NIPPON_PATTERN,
            text_color=Color("black" if color_name == "yellow" else "white"),
            frame_color=Color(color_name),
        ),
    )
    bits_box.compartment("MachinesAndDisks", width_ratio=0.3, cut=FingerCut.SCOOP)
    bits_box.compartment("InfluenceFavourContracts", width_ratio=0.7, cut=FingerCut.SCOOP)

# ── Row 2: Factory, Demand, Starting, Upgrade & Money (Y = 92 .. 152.5) ──
row2_y = player_box_length
row2_x = 0.0

for idx, text in enumerate(["Factories I", "Factories II"], start=1):
    project.box(
        BoxType.SLIDING,
        f"FactoryTiles_{idx}",
        size=(factory_tile_box_width, factory_tile_box_length, factory_tile_box_height),
        position=(row2_x, row2_y, 0.0),
        lid=LidBuilder(
            text=text,
            label_mode=LabelMode.FRAMED,
            pattern=NIPPON_PATTERN,
            text_color=Color("white"),
            frame_color=Color("navy"),
        ),
    ).compartment("Tiles", cut=FingerCut.SCOOP)
    row2_x += factory_tile_box_width

project.box(
    BoxType.SLIDING,
    "DemandTiles",
    size=(demand_tile_box_width, demand_tile_box_length, demand_tile_box_height),
    position=(row2_x, row2_y, 0.0),
    lid=LidBuilder(
        text="Demand",
        label_mode=LabelMode.FRAMED,
        pattern=NIPPON_PATTERN,
        text_color=Color("white"),
        frame_color=Color("navy"),
    ),
).compartment("Tiles", cut=FingerCut.SCOOP)
row2_x += demand_tile_box_width

project.box(
    BoxType.SLIDING,
    "StartingTiles",
    size=(starting_tile_box_width, starting_tile_box_length, starting_tile_box_height),
    position=(row2_x, row2_y, 0.0),
    lid=LidBuilder(
        text="Start",
        label_mode=LabelMode.FRAMED,
        pattern=NIPPON_PATTERN,
        text_color=Color("white"),
        frame_color=Color("navy"),
    ),
).compartment("Tiles", cut=FingerCut.SCOOP)
row2_x += starting_tile_box_width

project.box(
    BoxType.SLIDING,
    "UpgradeTiles",
    size=(upgraded_tile_box_width, upgraded_tile_box_length, upgraded_tile_box_height),
    position=(row2_x, row2_y, 0.0),
    lid=LidBuilder(
        text="Upgraded",
        label_mode=LabelMode.FRAMED,
        pattern=NIPPON_PATTERN,
        text_color=Color("white"),
        frame_color=Color("teal"),
    ),
).compartment("Upgrades", cut=FingerCut.SCOOP)

project.box(
    BoxType.CAP,
    "MoneyBox",
    size=(money_box_width, money_box_length, money_box_height),
    position=(row2_x, row2_y, upgraded_tile_box_height),
    lid=LidBuilder(
        text="Money",
        label_mode=LabelMode.FRAMED,
        pattern=NIPPON_PATTERN,
        text_color=Color("black"),
        frame_color=Color("gold"),
    ),
).compartment("Money", cut=FingerCut.SCOOP)

# ── Row 3: Solo, Late Game, Round Marker & 6 Worker Boxes (Y = 152.5 .. 213.0) ──
row3_y = row2_y + factory_tile_box_length

solo_box = project.box(
    BoxType.CAP,
    "SoloBox",
    size=(solo_box_width, solo_box_length, solo_box_height),
    position=(0.0, row3_y, 0.0),
    lid=LidBuilder(
        text="Solo",
        label_mode=LabelMode.FRAMED,
        pattern=NIPPON_PATTERN,
        text_color=Color("white"),
        frame_color=Color("slategray"),
    ),
)
solo_box.compartment("SoloGoals", width_ratio=0.45, cut=FingerCut.SCOOP)
solo_box.compartment("SoloActions", width_ratio=0.55, cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "LateGameFactoryBox",
    size=(late_game_factory_box_width, late_game_factory_box_length, late_game_factory_box_height),
    position=(0.0, row3_y, solo_box_height),
    lid=LidBuilder(
        text="Late Game",
        label_mode=LabelMode.FRAMED,
        pattern=NIPPON_PATTERN,
        text_color=Color("white"),
        frame_color=Color("navy"),
    ),
).compartment("LateGameFactories", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "RoundMarkerBox",
    size=(round_marker_box_width, round_marker_box_length, round_marker_box_height),
    position=(late_game_factory_box_width, row3_y, solo_box_height),
    lid=LidBuilder(
        text="Round",
        label_mode=LabelMode.FRAMED,
        pattern=NIPPON_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkred"),
    ),
).compartment("RoundMarkers", cut=FingerCut.SCOOP)

worker_colors = ["white", "blue", "grey", "yellow", "red", "black"]
for idx, wcolor in enumerate(worker_colors):
    col = idx % 3
    layer = idx // 3
    project.box(
        BoxType.CAP,
        f"WorkerBox_{wcolor}",
        size=(worker_box_width, worker_box_length, worker_box_height),
        position=(solo_box_width + worker_box_width * col, row3_y, worker_box_height * layer),
        lid=LidBuilder(
            text="Workers",
            label_mode=LabelMode.FRAMED,
            pattern=NIPPON_PATTERN,
            text_color=Color("black" if wcolor in ("white", "yellow") else "white"),
            frame_color=Color(wcolor if wcolor != "white" else "silver"),
        ),
    ).compartment("Workers", cut=FingerCut.SCOOP)

# ── Row 4: Resource Cube Boxes (Y = 213.0 .. 250.5) ───────────────
row4_y = row3_y + solo_box_length

for layer, (label, color) in enumerate([
    ("ResourceBox_silk", "lightgrey"),
    ("ResourceBox_paper", "red"),
]):
    project.box(
        BoxType.SLIDING,
        label,
        size=(resource_box_width, resource_box_length, resource_box_height),
        position=(0.0, row4_y, resource_box_height * layer),
        lid=LidBuilder(
            text="Resources",
            label_mode=LabelMode.FRAMED,
            pattern=NIPPON_PATTERN,
            text_color=Color("black" if color == "lightgrey" else "white"),
            frame_color=Color(color),
        ),
    ).compartment("Cubes", cut=FingerCut.SCOOP)

for layer, (label, color) in enumerate([
    ("ResourceDoubleBox_coal", "black"),
    ("ResourceDoubleBox_copper", "palegoldenrod"),
]):
    project.box(
        BoxType.SLIDING,
        label,
        size=(resource_box_double_width, resource_box_length, resource_box_height),
        position=(resource_box_width, row4_y, resource_box_height * layer),
        lid=LidBuilder(
            text="Resources",
            label_mode=LabelMode.FRAMED,
            pattern=NIPPON_PATTERN,
            text_color=Color("black" if color == "palegoldenrod" else "white"),
            frame_color=Color(color),
        ),
    ).compartment("Cubes", cut=FingerCut.SCOOP)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
