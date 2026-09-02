#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Arkham Horror LCG insert.

Ports examples/arkham_horror_tcg.scad to the pyboxbuilder Project API.
Organizes player investigator decks, campaign scenario encounter decks,
tokens, and accessories in modular card and token trays with automated spacers.
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
    columns,
    run,
    stack,
)

# ── Game Box Dimensions ───────────────────────────────────────────
box_width = 242.0
box_length = 283.0
box_height = 75.0

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 3.0

# ── Card & Deck Sizing ────────────────────────────────────────────
card_width = 66.0
card_length = 92.0
single_card_thickness = 0.533  # sleeved / premium card thickness

card_box_width = card_length + wall_thickness * 2.0 + 2.0  # 100.0mm
all_boxes_height = box_height - 2.0                         # 73.0mm

# Core player cards (13 decks/categories, ~250 cards total)
core_player_cards = [
    ("Agnes Baker", 34),
    ("Roland Banks", 34),
    ("Daisy Walker", 34),
    ("Skids O'Toole", 34),
    ("Wendy Adams", 34),
    ("Level 0", 15),
    ("Guardian 1+", 12),
    ("Survivor 1+", 12),
    ("Rogue 1+", 12),
    ("Seeker 1+", 12),
    ("Mystic 1+", 12),
    ("Neutral 1+", 10),
    ("Weaknesses", 10),
]

# Core scenario encounter cards (~120 cards total)
core_scenario_cards = [
    ("The Gathering", 16),
    ("The Midnight Masks", 20),
    ("The Devourer Below", 18),
    ("Chilling Cold", 8),
    ("Cultists", 10),
    ("Ancient Evils", 8),
    ("Ghouls", 7),
    ("Agents", 16),
    ("Rats & Doors", 8),
]

total_player_cards = sum(c[1] for c in core_player_cards)
total_scenario_cards = sum(c[1] for c in core_scenario_cards)

player_box_len = 140.0
scenario_box_len = 140.0

project = Project(
    "ArkhamHorrorLCG",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    generate_spacers=True,
)

ARKHAM_PATTERN = PatternBuilder(PatternType.VORONOI)

# ── 1. Core Set Player Card Box ────────────────────────────────────
player_box = project.box(
    BoxType.SLIDING,
    "CorePlayerCards",
    size=(card_box_width, player_box_len, all_boxes_height),
    lid=LidBuilder(
        text="Core Investigators",
        label_mode=LabelMode.FRAMED,
        pattern=ARKHAM_PATTERN,
        text_color=Color("white"),
        frame_color=Color("teal"),
    ),
    position=(0.0, 0.0, 0.0),
    no_rotate=True,
)
player_box.compartment(
    "Investigators",
    depth=all_boxes_height - lid_thickness,
    cut=FingerCut.SCOOP,
)

# ── 2. Core Set Campaign Encounter Card Box ────────────────────────
scenario_box = project.box(
    BoxType.SLIDING,
    "CoreScenarioCards",
    size=(card_box_width, scenario_box_len, all_boxes_height),
    lid=LidBuilder(
        text="Core Campaign",
        label_mode=LabelMode.FRAMED,
        pattern=ARKHAM_PATTERN,
        text_color=Color("white"),
        frame_color=Color("midnightblue"),
    ),
    position=(0.0, player_box_len, 0.0),
    no_rotate=True,
)
scenario_box.compartment(
    "Encounters",
    depth=all_boxes_height - lid_thickness,
    cut=FingerCut.SCOOP,
)

# ── 3. Chaos Token & Resource Token Trays ──────────────────────────
token_box_width = box_width - card_box_width - 2.0  # 140.0mm
token_tray_height = all_boxes_height / 3.0          # ~24.3mm

for idx, label in enumerate(["ChaosTokens", "DamageAndHorror", "CluesAndResources"], start=1):
    tray = project.box(
        BoxType.CAP,
        f"TokenTray{idx}_{label}",
        size=(token_box_width, player_box_len, token_tray_height),
        lid=LidBuilder(
            text=label,
            label_mode=LabelMode.FRAMED,
            pattern=ARKHAM_PATTERN,
            text_color=Color("white"),
            frame_color=Color("darkred"),
        ),
        position=(card_box_width, 0.0, (idx - 1) * token_tray_height),
        no_rotate=True,
    )
    for c_idx in range(4):
        tray.compartment(
            f"Pocket_{c_idx + 1}",
            width_ratio=0.25,
            depth=token_tray_height - floor_thickness - 1.0,
            cut=FingerCut.SCOOP,
        )

# ── 4. Accessory & Encounter Token Tray ────────────────────────────
accessory_box = project.box(
    BoxType.CAP,
    "AccessoryTray",
    size=(token_box_width, scenario_box_len, all_boxes_height / 2.0),
    lid=LidBuilder(
        text="Accessories",
        label_mode=LabelMode.FRAMED,
        pattern=ARKHAM_PATTERN,
        text_color=Color("white"),
    ),
    position=(card_box_width, player_box_len, 0.0),
    no_rotate=True,
)
accessory_box.compartment(
    "MinisAndDials",
    width_ratio=0.5,
    depth=all_boxes_height / 2.0 - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)
accessory_box.compartment(
    "StandsAndMarkers",
    width_ratio=0.5,
    depth=all_boxes_height / 2.0 - floor_thickness - 1.0,
    cut=FingerCut.SCOOP,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
