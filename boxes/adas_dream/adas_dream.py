#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Ada's Dream board game organizer.

Ports boxes/adas_dream/adas_dream.scad to the pyboxbuilder Project API.
Organizes all 26 boxes/trays: 4 player boxes, scoring & visitor boxes, money,
partner/tier/other/assignment cards, gears/cogs, dice, first-player token,
books, assignment tiles, alternative & standard objectives, breakthrough tiles,
score pad, program & university tiles, brass & coal resources, and side spacer.
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
    StackableMode,
    run,
)

# ── Box & Board Dimensions (from adas_dream.scad) ─────────────────
box_width = 212.0
box_length = 291.0
box_height = 90.0

board_thickness = 31.0
usable_height = box_height - board_thickness  # 59.0mm
great_exhibition_board_thickness = 4.0

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

# ── Component Dimensions ──────────────────────────────────────────
assignment_tiles_thickness = 9.0
solo_reward_thickness = 16.0
solo_reward_width_thin = 36.0
solo_reward_length_thin = 22.5

player_token_thickness = 6.5
cardboard_thickness = 2.0

program_width = 25.5
program_length = 41.0
objective_length = 47.0
scoring_length = 34.5
dice_thickness = 14.5
book_length = 21.25
score_pad_length = 96.5
score_pad_thickness = 6.0

card_width = 66.0
card_length = 91.0
single_card_thickness = 0.6
assignment_card_width = 48.0
assignment_card_length = 70.5
other_card_num = 24
starting_player_card_num = 7
tier_1_partner_card_num = 10
tier_2_partner_card_num = 30
assignment_card_num = 30

# ── Derived Sub-Box Dimensions (exact .scad formulas) ─────────────
card_box_width = card_length + wall_thickness * 2.0  # 97.0mm
card_box_length = card_width + wall_thickness * 2.0  # 72.0mm

tier_card_box_height = (
    lid_thickness
    + floor_thickness
    + single_card_thickness * (tier_1_partner_card_num + tier_2_partner_card_num)
)  # 28.0mm
other_card_box_height = (
    floor_thickness + lid_thickness + single_card_thickness * other_card_num
)  # 18.4mm

player_box_height = (
    floor_thickness
    + lid_thickness
    + player_token_thickness * 2.0
    + single_card_thickness * (starting_player_card_num + 2)
)  # 22.4mm

scoring_box_width = card_box_width  # 97.0mm
scoring_box_length = wall_thickness * 2.0 + scoring_length  # 40.5mm
scoring_box_height = box_height - player_box_height * 2.0 - board_thickness  # 14.2mm

visitor_box_width = card_box_width  # 97.0mm
visitor_box_length = card_box_length - scoring_box_length  # 31.5mm
visitor_box_height = scoring_box_height  # 14.2mm

money_box_width = box_width - card_box_width - 1.0  # 114.0mm
money_box_length = card_box_length  # 72.0mm
money_box_height = scoring_box_height  # 14.2mm

book_box_width = card_box_width - solo_reward_width_thin  # 61.0mm
book_box_length = wall_thickness * 2.0 + (book_length + 1.0) * 4.0  # 95.0mm
book_box_height = solo_reward_thickness  # 16.0mm

assignment_box_width = book_box_width  # 61.0mm
assignment_box_length = (
    box_length - solo_reward_length_thin - 2.0 - card_box_length - book_box_length
)  # 99.5mm
assignment_box_height = book_box_height  # 16.0mm

dice_box_width = card_box_width  # 97.0mm
dice_box_length = wall_thickness * 2.0 + dice_thickness * 9.0 + 1.5  # 138.0mm
dice_box_height = dice_thickness + floor_thickness + lid_thickness  # 18.5mm

assignment_card_box_width = assignment_card_length + wall_thickness * 2.0  # 76.5mm
assignment_card_box_length = assignment_card_width + wall_thickness * 2.0  # 54.0mm
assignment_card_box_height = (
    floor_thickness + lid_thickness + single_card_thickness * assignment_card_num + 1.0
)  # 23.0mm

first_player_box_width = card_box_width  # 97.0mm
first_player_box_length = (
    box_length - card_box_length - dice_box_length - assignment_card_box_length
)  # 27.0mm
first_player_box_height = dice_box_height  # 18.5mm

alternative_objective_box_width = card_box_width  # 97.0mm
alternative_objective_box_length = (
    box_length - card_box_length - assignment_card_box_length - 1.0
)  # 164.0mm
alternative_objective_box_height = (
    box_height
    - board_thickness
    - great_exhibition_board_thickness
    - 1.0
    - dice_box_height
    - solo_reward_thickness
)  # 19.5mm

score_pad_box_width = dice_box_width  # 97.0mm
score_pad_box_length = score_pad_length + wall_thickness * 2.0  # 102.5mm
score_pad_box_height = floor_thickness + lid_thickness + score_pad_thickness  # 10.0mm

program_box_width = program_length + wall_thickness * 2.0  # 47.0mm
program_box_length = program_width * 2.0 + wall_thickness * 3.0  # 60.0mm
program_box_height = (
    box_height - board_thickness - solo_reward_thickness - great_exhibition_board_thickness
)  # 39.0mm

university_box_width = program_box_width  # 47.0mm
university_box_length = score_pad_box_length - program_box_length  # 42.5mm
university_box_height = program_box_height  # 39.0mm

resource_box_width = score_pad_box_width / 2.0  # 48.5mm
resource_box_length = score_pad_box_length  # 102.5mm
resource_box_height = (
    box_height
    - board_thickness
    - great_exhibition_board_thickness
    - score_pad_box_height
    - 1.0
) / 2.0  # 22.0mm

cog_box_width = box_width - card_box_width  # 115.0mm
cog_box_length = box_length - card_box_length * 2.0 - score_pad_box_length  # 44.5mm
cog_box_height = (
    box_height - board_thickness - great_exhibition_board_thickness - 1.0
) / 3.0  # 18.0mm

breakthrough_box_width = box_width - cog_box_width - assignment_card_box_width - 1.0  # 19.5mm
breakthrough_box_length = assignment_card_box_length  # 54.0mm
breakthrough_box_height = assignment_box_height  # 16.0mm

objective_box_width = box_width - card_box_width * 2.0 - 1.0  # 17.0mm
objective_box_length = wall_thickness * 5.0 + objective_length * 3.0  # 156.0mm
objective_box_height = player_box_height * 2.0 - assignment_tiles_thickness  # 35.8mm

spacer_side_box_width = objective_box_width  # 17.0mm
spacer_side_box_length = score_pad_box_length + card_box_length * 2.0 - objective_box_length  # 90.5mm
spacer_side_box_height = objective_box_height  # 35.8mm

project = Project(
    "AdasDream",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
    box_defaults={"expandable": False},
)

ADA_PATTERN = PatternBuilder(PatternType.DENSE_HEX)


def _lid(text: str, frame_color: str) -> LidBuilder:
    return LidBuilder(
        text=text,
        label_mode=LabelMode.FRAMED,
        pattern=ADA_PATTERN,
        text_color=Color("white"),
        frame_color=Color(frame_color),
    )


# ── 1. Player Boxes (4) + Scoring, Visitor, Money ────────────────
player_specs = [
    ("PlayerBox_Red", "Red", "darkred", (0.0, 0.0, 0.0)),
    ("PlayerBox_Blue", "Blue", "navy", (card_box_width, 0.0, 0.0)),
    ("PlayerBox_Green", "Green", "forestgreen", (0.0, 0.0, player_box_height)),
    ("PlayerBox_Purple", "Purple", "purple", (card_box_width, 0.0, player_box_height)),
]
for label, text, color, pos in player_specs:
    project.box(
        BoxType.SLIDING,
        label,
        size=(card_box_width, card_box_length, player_box_height),
        position=pos,
        lid=_lid(text, color),
        stackable=StackableMode.PYRAMIDS,
    ).compartment("PlayerBits", cut=FingerCut.SCOOP)

scoring_box = project.box(
    BoxType.CAP,
    "ScoringBox",
    size=(scoring_box_width, scoring_box_length, scoring_box_height),
    position=(0.0, 0.0, player_box_height * 2.0),
    lid=_lid("Scoring", "gold"),
)
for i in range(4):
    scoring_box.compartment(f"Scoring_{i + 1}", width_ratio=0.25, cut=FingerCut.SCOOP)

visitor_box = project.box(
    BoxType.CAP,
    "VisitorBox",
    size=(visitor_box_width, visitor_box_length, visitor_box_height),
    position=(0.0, scoring_box_length, player_box_height * 2.0),
    lid=_lid("Visitors", "slategray"),
)
for name in ("Yellow", "Purple", "Blue", "Green"):
    visitor_box.compartment(name, width_ratio=0.25, cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "MoneyBox",
    size=(money_box_width, money_box_length, money_box_height),
    position=(card_box_width, 0.0, player_box_height * 2.0),
    lid=_lid("Money", "silver"),
).compartment("Money", cut=FingerCut.SCOOP)

# ── 2. Card Boxes (Other, Tier, Assignment) ──────────────────────
project.box(
    BoxType.SLIDING,
    "OtherCardBox",
    size=(card_box_width, card_box_length, other_card_box_height),
    position=(card_box_width, card_box_length, 0.0),
    lid=_lid("Other", "royalblue"),
    stackable=StackableMode.PYRAMIDS,
).compartment("OtherCards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "TierCardBox",
    size=(card_box_width, card_box_length, tier_card_box_height),
    position=(card_box_width, card_box_length, other_card_box_height),
    lid=_lid("Tier", "darkorange"),
    stackable=StackableMode.PYRAMIDS,
).compartment("TierCards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "AssignmentCardBox",
    size=(assignment_card_box_width, assignment_card_box_length, assignment_card_box_height),
    position=(
        0.0,
        card_box_length + dice_box_length + first_player_box_length,
        book_box_height,
    ),
    lid=_lid("Assign", "purple"),
).compartment("AssignmentCards", cut=FingerCut.SCOOP)

# ── 3. Left Column: Books, Assignment Tiles, Dice, First Player, Alt Obj, Breakthrough
book_box = project.box(
    BoxType.CAP,
    "BookBox",
    size=(book_box_width, book_box_length, book_box_height),
    position=(solo_reward_width_thin, card_box_length, 0.0),
    lid=_lid("Books", "teal"),
)
for i in range(3):
    book_box.compartment(f"Books_{i + 1}", width_ratio=1.0 / 3.0, cut=FingerCut.SCOOP)

assignment_box = project.box(
    BoxType.CAP,
    "AssignmentBox",
    size=(assignment_box_width, assignment_box_length, assignment_box_height),
    position=(solo_reward_width_thin, card_box_length + book_box_length, 0.0),
    lid=_lid("Assign", "steelblue"),
)
for i in range(2):
    assignment_box.compartment(f"Assign_{i + 1}", width_ratio=0.5, cut=FingerCut.SCOOP)

project.box(
    BoxType.CAP,
    "DiceBox",
    size=(dice_box_width, dice_box_length, dice_box_height),
    position=(0.0, card_box_length, book_box_height),
    lid=_lid("Dice", "firebrick"),
).compartment("Dice", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "FirstPlayerBox",
    size=(first_player_box_width, first_player_box_length, first_player_box_height),
    position=(0.0, card_box_length + dice_box_length, book_box_height),
    lid=_lid("First", "darkgoldenrod"),
).compartment("FirstPlayer", cut=FingerCut.SCOOP)

alt_obj_box = project.box(
    BoxType.CAP,
    "AlternativeObjectiveBox",
    size=(
        alternative_objective_box_width,
        alternative_objective_box_length,
        alternative_objective_box_height,
    ),
    position=(0.0, card_box_length, book_box_height + dice_box_height),
    lid=_lid("Alt Obj", "mediumpurple"),
)
for i in range(2):
    alt_obj_box.compartment(f"AltObj_{i + 1}", width_ratio=0.5, cut=FingerCut.SCOOP)

breakthrough_box = project.box(
    BoxType.SLIDING,
    "BreakthroughBox",
    size=(breakthrough_box_width, breakthrough_box_length, breakthrough_box_height),
    position=(
        assignment_card_box_width,
        card_box_length + dice_box_length + first_player_box_length,
        book_box_height,
    ),
    wall_thickness=1.2,
    lid=_lid("Break", "magenta"),
)
breakthrough_box.compartment("Breakthrough_1", length_ratio=0.5, cut=FingerCut.SCOOP)
breakthrough_box.compartment("Breakthrough_2", length_ratio=0.5, cut=FingerCut.SCOOP)

# ── 4. Middle Column: Score Pad, Program, University, Brass & Coal ─
project.box(
    BoxType.SLIDING,
    "ScorePadBox",
    size=(score_pad_box_width, score_pad_box_length, score_pad_box_height),
    position=(card_box_width, card_box_length * 2.0, 0.0),
    lid=_lid("Score Pad", "dimgray"),
).compartment("ScorePad", cut=FingerCut.SCOOP)

program_box = project.box(
    BoxType.SLIDING,
    "ProgramBox",
    size=(program_box_width, program_box_length, program_box_height),
    position=(card_box_width, card_box_length * 2.0, score_pad_box_height),
    lid=_lid("Program", "saddlebrown"),
)
program_box.compartment("Program_1", length_ratio=0.5, cut=FingerCut.SCOOP)
program_box.compartment("Program_2", length_ratio=0.5, cut=FingerCut.SCOOP)

university_box = project.box(
    BoxType.SLIDING,
    "UniversityBox",
    size=(university_box_width, university_box_length, university_box_height),
    position=(
        card_box_width,
        card_box_length * 2.0 + program_box_length,
        score_pad_box_height,
    ),
    lid=_lid("Univ", "darkcyan"),
)
university_box.compartment("University", width_ratio=0.5, cut=FingerCut.SCOOP)
university_box.compartment("WorkshopBonus", width_ratio=0.5, cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "ResourceBox_Brass",
    size=(resource_box_width, resource_box_length, resource_box_height),
    position=(
        card_box_width + program_box_width,
        card_box_length * 2.0,
        score_pad_box_height,
    ),
    lid=_lid("Brass", "goldenrod"),
).compartment("Brass", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "ResourceBox_Coal",
    size=(resource_box_width, resource_box_length, resource_box_height),
    position=(
        card_box_width + program_box_width,
        card_box_length * 2.0,
        score_pad_box_height + resource_box_height,
    ),
    lid=_lid("Coal", "darkslategray"),
).compartment("Coal", cut=FingerCut.SCOOP)

# ── 5. Gear / Cog Boxes (3 stacked) ──────────────────────────────
gear_specs = [
    ("GearBox_AddGears", "Addition", 0),
    ("GearBox_SubGears", "Subtraction", 1),
    ("GearBox_MulGears", "Multiplier", 2),
]
for label, text, idx in gear_specs:
    project.box(
        BoxType.CAP,
        label,
        size=(cog_box_width, cog_box_length, cog_box_height),
        position=(
            card_box_width,
            card_box_length * 2.0 + score_pad_box_length,
            cog_box_height * idx,
        ),
        lid=_lid(text, "peru"),
    ).compartment("Gears", cut=FingerCut.SCOOP)

# ── 6. Right Side Strip: SpacerSide & ObjectiveBox ────────────────
project.box(
    BoxType.NO_LID,
    "SpacerSide",
    size=(spacer_side_box_width, spacer_side_box_length, spacer_side_box_height),
    position=(card_box_width * 2.0, 0.0, assignment_tiles_thickness),
    hollow=True,
)

obj_box = project.box(
    BoxType.SLIDING,
    "ObjectiveBox",
    size=(objective_box_width, objective_box_length, objective_box_height),
    position=(card_box_width * 2.0, spacer_side_box_length, assignment_tiles_thickness),
    lid=_lid("Objective", "darkorange"),
)
for i in range(3):
    obj_box.compartment(f"Objective_{i + 1}", length_ratio=1.0 / 3.0, cut=FingerCut.SCOOP)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
