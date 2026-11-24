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
    else ROOT / "boxes" / "adas_dream" / "assets"
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

# ── Game Component Inventory ──────────────────────────────────────
project.define_inventory({
    "Starting Player Cards": starting_player_card_num * 4,
    "Player Discs": 48,
    "Research Tokens": 16,
    "Innovation Tokens": 4,
    "Steam Cloud Tokens": 4,
    "Character Meeples": 4,
    "Scoring Tiles": 16,
    "Visitor Tokens": 4,
    "Silver Coins": 40,
    "Exhibitor & Other Cards": other_card_num,
    "Tier 1 Partner Cards": tier_1_partner_card_num,
    "Tier 2 Partner Cards": tier_2_partner_card_num,
    "Assignment Cards": assignment_card_num,
    "Book Tokens": 12,
    "Assignment Tiles": 16,
    "Engine Dice": 50,
    "First Player Token": 1,
    "Alternative Objective Tiles": 12,
    "Breakthrough Tiles": 9,
    "Score Pad": 1,
    "Program Tiles": 28,
    "Workshop Bonus Discs": 6,
    "University Tiles": 15,
    "Brass Resource Tokens": 30,
    "Coal Resource Tokens": 30,
    "Addition Gears": 15,
    "Subtraction Gears": 15,
    "Multiplier Gears": 14,
    "Objective Tiles": 24,
    "Main Game Board": 1,
    "Great Exhibition Board": 1,
    "Player Workshop Boards": 4,
    "Solo Reward Board": 1,
    "Assignment Tiles Board": 1,
})

project.board(
    "Game Boards & Player Mats",
    size=(box_width, box_length, board_thickness),
    position=(0.0, 0.0, usable_height),
    count=5,
    notes="Main game board and 4 player workshop mats atop insert",
    allocates={
        "Main Game Board": 1,
        "Player Workshop Boards": 4,
    },
)
project.board(
    "Great Exhibition Board",
    size=(box_width, box_length - card_box_length, great_exhibition_board_thickness),
    position=(0.0, card_box_length, usable_height - great_exhibition_board_thickness),
    count=1,
    notes="Rests over rear columns behind front player/scoring row",
    component="Great Exhibition Board",
)
project.board(
    "Solo Reward Board",
    size=(solo_reward_width_thin, box_length - card_box_length, solo_reward_thickness),
    position=(0.0, card_box_length, 0.0),
    count=1,
    notes="Rests under Dice, First Player & Assignment Card boxes along left wall",
    component="Solo Reward Board",
)
project.board(
    "Assignment Tiles Board",
    size=(box_width - card_box_width * 2.0, box_length - cog_box_length, assignment_tiles_thickness),
    position=(card_box_width * 2.0, 0.0, 0.0),
    count=1,
    notes="Rests under SpacerSide & ObjectiveBox along right wall",
    component="Assignment Tiles Board",
)

# Victorian steampunk Analytical Engine aesthetic:
# 8-fold quasiperiodic Ammann-Beenker brass filigree lattice, riveted/ornate
# Victorian plaques, scrollwork finials, and bold Georgia serif typography.
ADA_PATTERN = PatternBuilder(PatternType.AMMANN_BEENKER, spacing=9.0, web=1.6)
STEAMPUNK_FONT = "Georgia:style=Bold"


def _lid(
    text: str,
    frame_color: str,
    *,
    shape: LabelShape = LabelShape.CORNER_STUD,
    finial: LabelFinial = LabelFinial.SCROLLWORK,
    image: str | None = None,
    logo_position: str = "left",
    logo_size_mm: float | None = None,
) -> LidBuilder:
    return LidBuilder(
        text=text,
        label_mode=LabelMode.FRAMED,
        label_shape=shape,
        label_finial=finial,
        font=STEAMPUNK_FONT,
        logo=image,
        logo_color=Color("white") if image else None,
        logo_position=logo_position,
        label_logo_size_mm=logo_size_mm,
        pattern=ADA_PATTERN,
        text_color=Color("white"),
        frame_color=Color(frame_color),
    )


# ── 1. Player Boxes (4) + Scoring, Visitor, Money ────────────────
player_token_diameter = 16.5
research_token_diameter = 11.5
research_token_length = 20.0
research_token_thin = 4.0
research_token_thickness = 6.0
innovation_diameter = 15.0
innovation_length = 18.5
innovation_min_width = 7.5
steam_width = 20.0
steam_length = 18.0
woman_man_player_thickness = 8.5

player_inner_width = card_box_width - wall_thickness * 2.0  # 91.0mm
player_inner_length = card_box_length - wall_thickness * 2.0  # 66.0mm


def _player_box_elements(variant: str) -> tuple[CompartmentElement, ...]:
    """Build stepped interior wells for PlayerBoxInternal (cards, 6 discs, 4 research, innovation, steam, meeple)."""
    elems: list[CompartmentElement] = []
    card_h = single_card_thickness * starting_player_card_num + 1.0  # 5.2mm

    # Top full-area card shelf
    elems.append(
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(player_inner_width, player_inner_length),
            offset=(0.0, 0.0),
            depth=card_h,
            pull_out=False,
            label="StartingCards",
        )
    )

    # Recessed grab shelves over the token/meeple area (matching SCAD RoundedBoxAllSides)
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(research_token_length * 2.0 + 10.0, player_inner_length - 4.0),
            offset=(1.0, 2.0),
            corner_radius=5.0,
            depth=card_h + research_token_thickness / 2.0,
            pull_out=False,
            label="TokenGrabShelf",
        )
    )
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(research_token_length * 2.0 + 10.0, 40.0),
            offset=(1.0, player_inner_length - 42.0),
            corner_radius=5.0,
            depth=card_h + woman_man_player_thickness / 2.0,
            pull_out=False,
            label="MeepleGrabShelf",
        )
    )

    # 4 Research tokens (2x2 lollipop silhouettes: circle d=11.5 + thin stem)
    res_depth = card_h + research_token_thickness
    for i in range(2):
        py_c = research_token_diameter / 2.0 + 4.0 + (research_token_diameter + 1.0) * i
        # Row 0: stem extending +X, bulb at -X
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(research_token_diameter, research_token_diameter),
                offset=(6.0, py_c - research_token_diameter / 2.0),
                depth=res_depth,
                pull_out=False,
                label=f"ResearchBulb_0_{i}",
            )
        )
        elems.append(
            CompartmentElement(
                shape=ElementShape.ROUNDED_RECT,
                size=(research_token_length, research_token_thin),
                offset=(6.0, py_c - research_token_thin / 2.0),
                corner_radius=research_token_thin / 2.0,
                depth=res_depth,
                pull_out=False,
                label=f"ResearchStem_0_{i}",
            )
        )
        # Row 1: bulb at +X, stem extending -X
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(research_token_diameter, research_token_diameter),
                offset=(27.0 + research_token_length - research_token_diameter, py_c - research_token_diameter / 2.0),
                depth=res_depth,
                pull_out=False,
                label=f"ResearchBulb_1_{i}",
            )
        )
        elems.append(
            CompartmentElement(
                shape=ElementShape.ROUNDED_RECT,
                size=(research_token_length, research_token_thin),
                offset=(27.0, py_c - research_token_thin / 2.0),
                corner_radius=research_token_thin / 2.0,
                depth=res_depth,
                pull_out=False,
                label=f"ResearchStem_1_{i}",
            )
        )

    # 6 Player disc wells (3x2 grid of CylinderWithIndents, depth = card_h + 2 discs)
    disc_depth = card_h + player_token_thickness * 2.0
    bite_d = 18.0  # finger_hole_radius = 9.0mm
    for row_idx, px_c in enumerate(
        (
            player_inner_width - player_token_diameter / 2.0 - 2.0,
            player_inner_width - player_token_diameter * 1.5 - 3.0,
        )
    ):
        for i in range(3):
            py_c = player_token_diameter / 2.0 + (player_token_diameter + 5.0) * i + 2.0
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(player_token_diameter, player_token_diameter),
                    offset=(px_c - player_token_diameter / 2.0, py_c - player_token_diameter / 2.0),
                    depth=disc_depth,
                    pull_out=False,
                    label=f"PlayerDisc_{row_idx}_{i}",
                )
            )
            bite_py = py_c + (player_token_diameter / 2.0 if i < 2 else -player_token_diameter / 2.0)
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(bite_d, bite_d),
                    offset=(px_c - bite_d / 2.0, bite_py - bite_d / 2.0),
                    depth=disc_depth,
                    pull_out=False,
                    label=f"PlayerDiscBite_{row_idx}_{i}",
                )
            )

    # Innovation token (lightbulb: circle d=15 + rounded stem)
    tok_depth = card_h + woman_man_player_thickness
    inno_px = innovation_diameter * 2.0 + 4.0  # 34.0
    inno_py = research_token_diameter * 3.0 + 2.0  # 36.5
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(innovation_diameter, innovation_diameter),
            offset=(inno_px - innovation_diameter / 2.0, inno_py - innovation_diameter / 2.0),
            depth=tok_depth,
            pull_out=False,
            label="InnovationBulb",
        )
    )
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(innovation_length / 2.0 + innovation_min_width / 2.0, innovation_min_width),
            offset=(inno_px, inno_py - innovation_min_width / 2.0),
            corner_radius=innovation_min_width / 2.0,
            depth=tok_depth,
            pull_out=False,
            label="InnovationStem",
        )
    )

    # Steam cloud token
    elems.append(
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "steam_token.svg"),
            size=(steam_width, steam_length),
            offset=(5.5, 28.25),
            depth=tok_depth,
            pull_out=False,
            label="SteamToken",
        )
    )

    # Character meeple silhouette (unique per player color)
    meeple_depth = card_h + woman_man_player_thickness + 0.5
    meeple_py_c = research_token_diameter * 4.5  # 51.75
    if variant in ("red", "blue"):
        # Man meeple (height 26.5 along X, width 12.5..13.5 along Y)
        mx = 19.0
        elems.extend(
            [
                CompartmentElement(
                    shape=ElementShape.ROUNDED_RECT,
                    size=(4.5, 5.0),
                    offset=(mx, meeple_py_c - 2.5),
                    corner_radius=1.0,
                    depth=meeple_depth,
                    pull_out=False,
                    label="MeepleHead",
                ),
                CompartmentElement(
                    shape=ElementShape.ROUNDED_RECT,
                    size=(14.0 if variant == "red" else 17.0, 12.5),
                    offset=(mx + 4.5, meeple_py_c - 6.25),
                    corner_radius=0.5,
                    depth=meeple_depth,
                    pull_out=False,
                    label="MeepleCoat",
                ),
                CompartmentElement(
                    shape=ElementShape.RECT,
                    size=(22.0, 8.0),
                    offset=(mx + 4.5, meeple_py_c - 4.0),
                    depth=meeple_depth,
                    pull_out=False,
                    label="MeepleTrousers",
                ),
                CompartmentElement(
                    shape=ElementShape.ROUNDED_RECT,
                    size=(2.0, 11.5),
                    offset=(mx + 24.5, meeple_py_c - 5.75),
                    corner_radius=0.5,
                    depth=meeple_depth,
                    pull_out=False,
                    label="MeepleFeet",
                ),
            ]
        )
        if variant == "blue":
            elems.extend(
                [
                    CompartmentElement(
                        shape=ElementShape.ROUNDED_RECT,
                        size=(2.0, 7.0),
                        offset=(mx + 2.5, meeple_py_c - 3.5),
                        corner_radius=0.5,
                        depth=meeple_depth,
                        pull_out=False,
                        label="MeepleHat",
                    ),
                    CompartmentElement(
                        shape=ElementShape.ROUNDED_RECT,
                        size=(3.0, 13.5),
                        offset=(mx + 10.0, meeple_py_c - 6.75),
                        corner_radius=0.5,
                        depth=meeple_depth,
                        pull_out=False,
                        label="MeepleArmBump",
                    ),
                ]
            )
    else:
        svg_name = "woman_green.svg" if variant == "green" else "woman_purple.svg"
        elems.append(
            CompartmentElement(
                shape=ElementShape.SVG,
                shape_file=str(ASSETS / svg_name),
                size=(12.5, 22.5),
                rotation=90.0,
                offset=(19.0, meeple_py_c - 6.25),
                depth=meeple_depth,
                pull_out=False,
                label="MeepleWoman",
            )
        )

    return tuple(elems)


player_specs = [
    ("PlayerBox_Red", "Red", "darkred", "red", (0.0, 0.0, 0.0)),
    ("PlayerBox_Blue", "Blue", "navy", "blue", (card_box_width, 0.0, 0.0)),
    ("PlayerBox_Green", "Green", "forestgreen", "green", (0.0, 0.0, player_box_height)),
    ("PlayerBox_Purple", "Purple", "purple", "purple", (card_box_width, 0.0, player_box_height)),
]
for label, text, color, variant, pos in player_specs:
    project.box(
        BoxType.SLIDING,
        label,
        size=(card_box_width, card_box_length, player_box_height),
        position=pos,
        lid=_lid(text, color, shape=LabelShape.ORNATE_FRAME),
        stackable=StackableMode.PYRAMIDS,
    ).compartment(
        "PlayerBits",
        size=(player_inner_width, player_inner_length),
        position=(0.0, 0.0),
        elements=_player_box_elements(variant),
        allocates={
            "Starting Player Cards": starting_player_card_num,
            "Player Discs": 12,
            "Research Tokens": 4,
            "Innovation Tokens": 1,
            "Steam Cloud Tokens": 1,
            "Character Meeples": 1,
        },
    )

scoring_box = project.box(
    BoxType.CAP,
    "ScoringBox",
    size=(scoring_box_width, scoring_box_length, scoring_box_height),
    position=(0.0, 0.0, player_box_height * 2.0),
    lid=_lid("Scoring", "gold"),
)
for i in range(4):
    scoring_box.compartment(
        f"Scoring_{i + 1}",
        width_ratio=0.25,
        cut=FingerCut.SCOOP,
        component="Scoring Tiles",
        count=4,
    )

visitor_wall = 1.5
visitor_inner_width = visitor_box_width - visitor_wall * 2.0  # 94.0mm
visitor_inner_length = visitor_box_length - visitor_wall * 2.0  # 28.5mm
visitor_thickness = 8.5

project.box(
    BoxType.CAP,
    "VisitorBox",
    size=(visitor_box_width, visitor_box_length, visitor_box_height),
    position=(0.0, scoring_box_length, player_box_height * 2.0),
    wall_thickness=visitor_wall,
    lid=_lid("Visitors", "slategray"),
).compartment(
    "Visitors",
    size=(visitor_inner_width, visitor_inner_length),
    position=(0.0, 0.0),
    elements=(
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(12.0, 28.0),
            offset=(2.0, 0.25),
            depth=visitor_thickness,
            pull_out=False,
            label="VisitorYellow",
        ),
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(17.0, 27.5),
            offset=(16.0, 0.5),
            depth=visitor_thickness,
            pull_out=False,
            label="VisitorPurple",
        ),
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(20.0, 26.5),
            offset=(35.0, 1.0),
            depth=visitor_thickness,
            pull_out=False,
            label="VisitorBlue",
        ),
        # Green visitor token has an L-shaped silhouette
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(12.0, 25.0),
            offset=(57.0, 1.75),
            depth=visitor_thickness,
            pull_out=False,
            label="VisitorGreenStem",
        ),
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(23.0, 19.5),
            offset=(57.0, 7.25),
            depth=visitor_thickness,
            pull_out=False,
            label="VisitorGreenBase",
        ),
    ),
    component="Visitor Tokens",
    count=4,
)

project.box(
    BoxType.SLIDING,
    "MoneyBox",
    size=(money_box_width, money_box_length, money_box_height),
    position=(card_box_width, 0.0, player_box_height * 2.0),
    lid=_lid("Money", "silver"),
).compartment("Money", cut=FingerCut.SCOOP, component="Silver Coins", count=40)

# ── 2. Card Boxes (Other, Tier, Assignment) ──────────────────────
project.box(
    BoxType.SLIDING,
    "OtherCardBox",
    size=(card_box_width, card_box_length, other_card_box_height),
    position=(card_box_width, card_box_length, 0.0),
    lid=_lid("Other", "royalblue", shape=LabelShape.ORNATE_FRAME),
    stackable=StackableMode.PYRAMIDS,
).compartment(
    "OtherCards",
    cut=FingerCut.SCOOP,
    component="Exhibitor & Other Cards",
    count=other_card_num,
)

project.box(
    BoxType.SLIDING,
    "TierCardBox",
    size=(card_box_width, card_box_length, tier_card_box_height),
    position=(card_box_width, card_box_length, other_card_box_height),
    lid=_lid("Tier", "darkorange", shape=LabelShape.ORNATE_FRAME),
    stackable=StackableMode.PYRAMIDS,
).compartment(
    "TierCards",
    cut=FingerCut.SCOOP,
    allocates={
        "Tier 1 Partner Cards": tier_1_partner_card_num,
        "Tier 2 Partner Cards": tier_2_partner_card_num,
    },
)

project.box(
    BoxType.SLIDING,
    "AssignmentCardBox",
    size=(assignment_card_box_width, assignment_card_box_length, assignment_card_box_height),
    position=(
        0.0,
        card_box_length + dice_box_length + first_player_box_length,
        book_box_height,
    ),
    lid=_lid("Assign", "purple", shape=LabelShape.ORNATE_FRAME),
).compartment(
    "AssignmentCards",
    cut=FingerCut.SCOOP,
    component="Assignment Cards",
    count=assignment_card_num,
)

# ── 3. Left Column: Books, Assignment Tiles, Dice, First Player, Alt Obj, Breakthrough
book_box = project.box(
    BoxType.CAP,
    "BookBox",
    size=(book_box_width, book_box_length, book_box_height),
    position=(solo_reward_width_thin, card_box_length, 0.0),
    lid=_lid("Books", "teal"),
)
for i in range(3):
    book_box.compartment(
        f"Books_{i + 1}",
        width_ratio=1.0 / 3.0,
        cut=FingerCut.SCOOP,
        component="Book Tokens",
        count=4,
    )

assignment_box = project.box(
    BoxType.CAP,
    "AssignmentBox",
    size=(assignment_box_width, assignment_box_length, assignment_box_height),
    position=(solo_reward_width_thin, card_box_length + book_box_length, 0.0),
    lid=_lid("Assign", "steelblue"),
)
for i in range(2):
    assignment_box.compartment(
        f"Assign_{i + 1}",
        width_ratio=0.5,
        cut=FingerCut.SCOOP,
        component="Assignment Tiles",
        count=8,
    )

dice_inner_width = dice_box_width - wall_thickness * 2.0  # 91.0mm
dice_inner_length = dice_box_length - wall_thickness * 2.0  # 132.0mm
project.box(
    BoxType.CAP,
    "DiceBox",
    size=(dice_box_width, dice_box_length, dice_box_height),
    position=(0.0, card_box_length, book_box_height),
    lid=_lid("Dice", "firebrick"),
).compartment(
    "Dice",
    size=(dice_inner_width, dice_inner_length),
    position=(0.0, 0.0),
    elements=(
        # Top 4mm recessed rim shelf
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(dice_inner_width - 2.0, dice_inner_length - 2.0),
            offset=(1.0, 1.0),
            corner_radius=4.0,
            depth=4.0,
            pull_out=False,
            label="DiceTopShelf",
        ),
        # 6x8 = 48-dice main well
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(dice_thickness * 6.0, dice_thickness * 8.0),
            offset=(1.5, 0.5),
            depth=dice_thickness,
            pull_out=False,
            label="DiceGrid6x8",
        ),
        # 2x1 extension for the 49th & 50th dice
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(dice_thickness * 2.0, dice_thickness * 9.0),
            offset=(1.5, 0.5),
            depth=dice_thickness,
            pull_out=False,
            label="DiceGrid2x9",
        ),
    ),
    component="Engine Dice",
    count=50,
)

fp_inner_width = first_player_box_width - wall_thickness * 2.0  # 91.0mm
fp_inner_length = first_player_box_length - wall_thickness * 2.0  # 21.0mm
first_player_thickness = 11.5
fp_x0 = (fp_inner_width - 46.5) / 2.0  # 22.25mm
project.box(
    BoxType.SLIDING,
    "FirstPlayerBox",
    size=(first_player_box_width, first_player_box_length, first_player_box_height),
    position=(0.0, card_box_length + dice_box_length, book_box_height),
    lid=_lid("First", "darkgoldenrod", finial=LabelFinial.NONE),
).compartment(
    "FirstPlayer",
    size=(fp_inner_width, fp_inner_length),
    position=(0.0, 0.0),
    elements=(
        # Recessed grab-shelf at half token depth
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(fp_inner_width - 2.0, fp_inner_length - 2.0),
            offset=(1.0, 1.0),
            corner_radius=5.0,
            depth=first_player_thickness / 2.0,
            pull_out=False,
            label="FirstPlayerShelf",
        ),
        # Stepped FirstPlayerToken silhouette (base, arms, head) rotated 90 deg
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(46.5 - 19.0, fp_inner_length),
            offset=(fp_x0, 0.0),
            corner_radius=1.0,
            depth=first_player_thickness + 0.5,
            pull_out=False,
            label="FirstPlayerBase",
        ),
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(46.5 - 9.0, 13.0),
            offset=(fp_x0, (fp_inner_length - 13.0) / 2.0),
            corner_radius=1.0,
            depth=first_player_thickness + 0.5,
            pull_out=False,
            label="FirstPlayerArms",
        ),
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(46.5, 5.5),
            offset=(fp_x0, (fp_inner_length - 5.5) / 2.0),
            corner_radius=1.0,
            depth=first_player_thickness + 0.5,
            pull_out=False,
            label="FirstPlayerHead",
        ),
    ),
    component="First Player Token",
    count=1,
)

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
    alt_obj_box.compartment(
        f"AltObj_{i + 1}",
        width_ratio=0.5,
        cut=FingerCut.SCOOP,
        component="Alternative Objective Tiles",
        count=6,
    )

bt_wall = 1.2
bt_inner_width = breakthrough_box_width - bt_wall * 2.0  # 17.1mm
bt_inner_length = breakthrough_box_length - bt_wall * 2.0  # 51.6mm
bt_w = 17.0
bt_l = 21.0
bt_bite_d = 16.0  # finger_hole_radius = 8.0mm
project.box(
    BoxType.SLIDING,
    "BreakthroughBox",
    size=(breakthrough_box_width, breakthrough_box_length, breakthrough_box_height),
    position=(
        assignment_card_box_width,
        card_box_length + dice_box_length + first_player_box_length,
        book_box_height,
    ),
    wall_thickness=bt_wall,
    lid=_lid("Break", "magenta", finial=LabelFinial.NONE),
).compartment(
    "Breakthroughs",
    size=(bt_inner_width, bt_inner_length),
    position=(0.0, 0.0),
    elements=(
        # 5-tile stack (depth 10.5mm) + back finger bite
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(bt_w, bt_l),
            offset=((bt_inner_width - bt_w) / 2.0, 0.0),
            depth=cardboard_thickness * 5.0 + 0.5,
            pull_out=False,
            label="Breakthrough_1",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(bt_bite_d, bt_bite_d),
            offset=((bt_inner_width - bt_bite_d) / 2.0, bt_l - bt_bite_d / 2.0),
            depth=cardboard_thickness * 5.0 + 0.5,
            pull_out=False,
            label="BreakthroughBite_1",
        ),
        # 4-tile stack (depth 8.5mm) + front finger bite
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(bt_w, bt_l),
            offset=((bt_inner_width - bt_w) / 2.0, bt_l + 5.0),
            depth=cardboard_thickness * 4.0 + 0.5,
            pull_out=False,
            label="Breakthrough_2",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(bt_bite_d, bt_bite_d),
            offset=((bt_inner_width - bt_bite_d) / 2.0, bt_l + 5.0 - bt_bite_d / 2.0),
            depth=cardboard_thickness * 4.0 + 0.5,
            pull_out=False,
            label="BreakthroughBite_2",
        ),
    ),
    component="Breakthrough Tiles",
    count=9,
)

# ── 4. Middle Column: Score Pad, Program, University, Brass & Coal ─
project.box(
    BoxType.SLIDING,
    "ScorePadBox",
    size=(score_pad_box_width, score_pad_box_length, score_pad_box_height),
    position=(card_box_width, card_box_length * 2.0, 0.0),
    lid=_lid("Score Pad", "dimgray"),
).compartment("ScorePad", cut=FingerCut.SCOOP, component="Score Pad", count=1)

program_box = project.box(
    BoxType.SLIDING,
    "ProgramBox",
    size=(program_box_width, program_box_length, program_box_height),
    position=(card_box_width, card_box_length * 2.0, score_pad_box_height),
    lid=_lid("Program", "saddlebrown"),
)
program_box.compartment(
    "Program_1",
    length_ratio=0.5,
    cut=FingerCut.SCOOP,
    component="Program Tiles",
    count=14,
)
program_box.compartment(
    "Program_2",
    length_ratio=0.5,
    cut=FingerCut.SCOOP,
    component="Program Tiles",
    count=14,
)

univ_inner_width = university_box_width - wall_thickness * 2.0  # 41.0mm
univ_inner_length = university_box_length - wall_thickness * 2.0  # 36.5mm
university_width = 20.5
university_length = 32.5
workshop_bonus_diameter = 33.0
workshop_bonus_slot_w = 17.0  # workshop_bonus_tile_thickness * 6 + 1

project.box(
    BoxType.SLIDING,
    "UniversityBox",
    size=(university_box_width, university_box_length, university_box_height),
    position=(
        card_box_width,
        card_box_length * 2.0 + program_box_length,
        score_pad_box_height,
    ),
    lid=_lid("Univ", "darkcyan"),
).compartment(
    "UniversityAndBonus",
    size=(univ_inner_width, univ_inner_length),
    position=(0.0, 0.0),
    elements=(
        # Left: 6 circular workshop bonus tiles standing on edge (curved floor + side finger bite)
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(workshop_bonus_slot_w, workshop_bonus_diameter + 1.0),
            offset=(0.0, 0.0),
            depth=workshop_bonus_diameter + 0.5,
            bottom_rounding=8.0,
            pull_out=False,
            label="WorkshopBonusTiles",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(14.0, 14.0),
            offset=(workshop_bonus_slot_w - 7.0, (workshop_bonus_diameter + 1.0) / 2.0 - 7.0),
            depth=workshop_bonus_diameter + 0.5,
            pull_out=False,
            label="WorkshopBonusBite",
        ),
        # Right: 15 notched university tiles (with r=5mm concave corner cutout)
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "university_tile.svg"),
            size=(university_width, university_length),
            offset=(univ_inner_width - university_width - 1.0, 0.0),
            depth=cardboard_thickness * 16.0 + 1.0,
            pull_out=True,
            label="UniversityTiles",
        ),
    ),
    allocates={
        "Workshop Bonus Discs": 6,
        "University Tiles": 15,
    },
)

project.box(
    BoxType.SLIDING,
    "ResourceBox_Brass",
    size=(resource_box_width, resource_box_length, resource_box_height),
    position=(
        card_box_width + program_box_width,
        card_box_length * 2.0,
        score_pad_box_height,
    ),
    lid=_lid(
        "Brass",
        "goldenrod",
        shape=LabelShape.CORNER_STUD,
        image=str(ASSETS / "brass.svg"),
        logo_position="left",
        logo_size_mm=18.0,
    ),
).compartment("Brass", cut=FingerCut.SCOOP, component="Brass Resource Tokens", count=30)

project.box(
    BoxType.SLIDING,
    "ResourceBox_Coal",
    size=(resource_box_width, resource_box_length, resource_box_height),
    position=(
        card_box_width + program_box_width,
        card_box_length * 2.0,
        score_pad_box_height + resource_box_height,
    ),
    lid=_lid(
        "Coal",
        "darkslategray",
        shape=LabelShape.CORNER_STUD,
        image=str(ASSETS / "coal.svg"),
        logo_position="left",
        logo_size_mm=18.0,
    ),
).compartment("Coal", cut=FingerCut.SCOOP, component="Coal Resource Tokens", count=30)

# ── 5. Gear / Cog Boxes (3 stacked, 5 circular gear wells + finger bites each)
gear_width = 26.0
gear_thickness = 4.0
gear_finger_diameter = 20.0  # finger_hole_radius = 10mm in adas_dream.scad
cog_inner_width = cog_box_width - wall_thickness * 2.0
cog_inner_length = cog_box_length - wall_thickness * 2.0


def _gear_elements(top_box: bool) -> tuple[CompartmentElement, ...]:
    """Build the 5 staggered circular gear wells with finger bites (CylinderWithIndents)."""
    elems: list[CompartmentElement] = []
    std_depth = gear_thickness * 3.0
    for i in range(2):
        for j in range(2):
            cx = (gear_width / 2.0 if j == 0 else gear_width * 1.17) + gear_width * i * 1.35
            cy = gear_width / 2.0 if j == 0 else cog_inner_length - gear_width / 2.0
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(gear_width, gear_width),
                    offset=(cx - gear_width / 2.0, cy - gear_width / 2.0),
                    depth=std_depth,
                    pull_out=False,
                    label=f"Gear_{i}_{j}",
                )
            )
            # Finger bite at 0 deg (+X perimeter)
            bite_cx = cx + gear_width / 2.0
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(gear_finger_diameter, gear_finger_diameter),
                    offset=(bite_cx - gear_finger_diameter / 2.0, cy - gear_finger_diameter / 2.0),
                    depth=std_depth,
                    pull_out=False,
                    label=f"GearBite_{i}_{j}",
                )
            )
    # 5th gear well on the right center (finger bite at 180 deg / -X perimeter)
    cx5 = cog_inner_width - gear_width / 2.0 - 2.0
    cy5 = cog_inner_length / 2.0
    depth5 = gear_thickness * (2.0 if top_box else 3.0)
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(gear_width, gear_width),
            offset=(cx5 - gear_width / 2.0, cy5 - gear_width / 2.0),
            depth=depth5,
            pull_out=False,
            label="Gear_5",
        )
    )
    bite_cx5 = cx5 - gear_width / 2.0
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(gear_finger_diameter, gear_finger_diameter),
            offset=(bite_cx5 - gear_finger_diameter / 2.0, cy5 - gear_finger_diameter / 2.0),
            depth=depth5,
            pull_out=False,
            label="GearBite_5",
        )
    )
    return tuple(elems)


gear_specs = [
    ("GearBox_AddGears", "Addition", 0, False, "Addition Gears", 15),
    ("GearBox_SubGears", "Subtraction", 1, False, "Subtraction Gears", 15),
    ("GearBox_MulGears", "Multiplier", 2, True, "Multiplier Gears", 14),
]
for label, text, idx, is_top, gear_comp, gear_qty in gear_specs:
    project.box(
        BoxType.CAP,
        label,
        size=(cog_box_width, cog_box_length, cog_box_height),
        position=(
            card_box_width,
            card_box_length * 2.0 + score_pad_box_length,
            cog_box_height * idx,
        ),
        lid=_lid(text, "peru", shape=LabelShape.ORNATE_FRAME),
    ).compartment(
        "Gears",
        size=(cog_inner_width, cog_inner_length),
        position=(0.0, 0.0),
        elements=_gear_elements(top_box=is_top),
        component=gear_comp,
        count=gear_qty,
    )

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
    lid=_lid("Objective", "darkorange", finial=LabelFinial.NONE),
)
for i in range(3):
    obj_box.compartment(
        f"Objective_{i + 1}",
        length_ratio=1.0 / 3.0,
        cut=FingerCut.SCOOP,
        component="Objective Tiles",
        count=8,
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
