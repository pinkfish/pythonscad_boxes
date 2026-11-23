#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Earth (+ Abundance expansion) board game organizer.

Ports boxes/earth/earth.scad to the pyboxbuilder Project API.
Organizes all 26 boxes/trays: 4 main Earth card boxes + small Earth card box,
Ecosystem/Fauna/Island/Climate/Solo/Season/Abundance card boxes, Start token
box, 6 stacked slipover player trays, Canopy/Sprout/Compost/Seed boxes,
ScorePad tray, and top spacer above the standing Abundance boards.
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

# ── Box & Board Dimensions (from earth.scad) ──────────────────────
box_width = 288.0
box_length = 288.0
box_height = 72.0

player_board_width = 242.0
player_board_thickness = 2.1
player_board_count = 6
middle_board_thickness = 2.1
abundance_middle_board_thickness = 2.1

abundance_board_width = 57.0
abundance_board_length = 241.0
abundance_board_thickness = 2.1
abundance_board_count = 6

total_board_reserve = (
    player_board_thickness * player_board_count
    + middle_board_thickness
    + abundance_middle_board_thickness
)  # 16.8mm
usable_height = box_height - total_board_reserve  # 55.2mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

# ── Card & Component Dimensions ───────────────────────────────────
card_width = 62.0
card_length = 93.0
single_card_thickness = 0.6

ecosystem_cards = 32
fauna_cards = 23
climate_cards = 10
solo_cards = 6
season_cards = 12
abundance_other_cards = 10

score_pad_length = 99.0
score_pad_thickness = 5.0

# ── Derived Sub-Box Dimensions (exact .scad formulas) ─────────────
card_box_width = wall_thickness * 2.0 + card_width  # 68.0mm
card_box_length = wall_thickness * 2.0 + card_length  # 99.0mm
card_box_height = usable_height  # 55.2mm

ecosystem_cards_height = floor_thickness + lid_thickness + single_card_thickness * ecosystem_cards + 1.0  # 24.2mm
fauna_cards_height = floor_thickness + lid_thickness + single_card_thickness * fauna_cards + 1.0  # 18.8mm
island_cards_height = card_box_height - ecosystem_cards_height - fauna_cards_height  # 12.2mm

climate_cards_height = floor_thickness + lid_thickness + single_card_thickness * climate_cards + 1.0  # 11.0mm
solo_cards_height = floor_thickness + lid_thickness + single_card_thickness * solo_cards + 1.0  # 8.6mm
season_cards_height = floor_thickness + lid_thickness + single_card_thickness * season_cards + 1.0  # 12.2mm
abundance_other_cards_height = (
    floor_thickness + lid_thickness + single_card_thickness * abundance_other_cards + 1.0
)  # 11.0mm
start_box_height = (
    card_box_height
    - climate_cards_height
    - solo_cards_height
    - season_cards_height
    - abundance_other_cards_height
)  # 12.4mm

earth_small_box_height = card_box_height / 3.0  # 18.4mm
compost_box_height = (card_box_height * 2.0 / 3.0) / 2.0  # 18.4mm

player_box_width = card_box_width  # 68.0mm
player_box_length = card_box_length  # 99.0mm
player_box_height = card_box_height / 6.0  # 9.2mm

score_pad_box_width = score_pad_length + wall_thickness * 4.0  # 111.0mm
score_pad_box_length = box_length - card_box_length * 2.0 - 1.0  # 89.0mm
score_pad_box_height = score_pad_thickness + floor_thickness  # 7.0mm

canopy_box_width = (
    box_width - abundance_board_thickness * abundance_board_count - 0.5 - score_pad_box_width
)  # 163.9mm
canopy_box_length = score_pad_box_length  # 89.0mm
canopy_box_height = card_box_height  # 55.2mm

sprout_box_width = score_pad_box_width  # 111.0mm
sprout_box_length = canopy_box_length  # 89.0mm
sprout_box_height = card_box_height - score_pad_box_height  # 48.2mm

seed_box_width = box_width - card_box_width * 4.0  # 16.0mm
seed_box_length = box_length - abundance_board_length - 1.0  # 46.0mm
seed_box_height = box_height  # 72.0mm (in corner beside player boards)

spacer_box_width = box_width - player_board_width  # 46.0mm
spacer_box_length = abundance_board_length - 0.5  # 240.5mm
spacer_box_height = box_height - abundance_board_width  # 15.0mm (above standing abundance boards)

project = Project(
    "Earth",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=total_board_reserve,
    generate_spacers=True,
)

EARTH_PATTERN = PatternBuilder(PatternType.DENSE_HEX)


def _lid(text: str, frame_color: str, text_color: str = "white") -> LidBuilder:
    return LidBuilder(
        text=text,
        label_mode=LabelMode.FRAMED,
        pattern=EARTH_PATTERN,
        text_color=Color(text_color),
        frame_color=Color(frame_color),
    )


# ── 1. Row 0 (Y = 0..99): Main Earth Card Decks, Compost, Seed ───
main_decks = [
    ("CardBox_Flora", "Earth", "forestgreen", (0.0, 0.0, 0.0)),
    ("CardBox_Terrain", "Earth", "sienna", (card_box_width, 0.0, 0.0)),
    ("CardBox_Events", "Earth", "royalblue", (card_box_width * 2.0, 0.0, 0.0)),
    ("CardBox_Abundance", "Earth", "darkgoldenrod", (card_box_width * 2.0, card_box_length, 0.0)),
]
for label, title, color_name, pos in main_decks:
    project.box(
        BoxType.SLIDING,
        label,
        size=(card_box_width, card_box_length, card_box_height),
        position=pos,
        lid=_lid(title, color_name),
    ).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "EarthCardBoxSmall",
    size=(card_box_width, card_box_length, earth_small_box_height),
    position=(card_box_width * 3.0, 0.0, 0.0),
    lid=_lid("Earth", "olive"),
).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.FILAMENT_HINGE,
    "CompostBox_1",
    size=(card_box_width, card_box_length, compost_box_height),
    position=(card_box_width * 3.0, 0.0, earth_small_box_height),
    lid=_lid("Compost", "dimgray"),
).compartment("Compost", cut=FingerCut.SCOOP)

project.box(
    BoxType.FILAMENT_HINGE,
    "CompostBox_2",
    size=(card_box_width, card_box_length, compost_box_height),
    position=(card_box_width * 3.0, 0.0, earth_small_box_height + compost_box_height),
    lid=_lid("Compost", "dimgray"),
).compartment("Compost", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIPOVER,
    "SeedBox",
    size=(seed_box_width, seed_box_length, seed_box_height),
    position=(card_box_width * 4.0, 0.0, 0.0),
    wall_thickness=2.0,
    lid=_lid("Seeds", "saddlebrown"),
).compartment("Seeds", cut=FingerCut.SCOOP)

project.box(
    BoxType.NO_LID,
    "TopSpacedBox",
    size=(spacer_box_width, spacer_box_length, spacer_box_height),
    position=(player_board_width, seed_box_length, abundance_board_width),
    hollow=True,
)

# ── 2. Row 1 Col 0 (X = 0..68, Y = 99..198): Ecosystem, Fauna, Island
project.box(
    BoxType.SLIDING,
    "EcosystemCardBox",
    size=(card_box_width, card_box_length, ecosystem_cards_height),
    position=(0.0, card_box_length, 0.0),
    lid=_lid("Ecosystem", "seagreen"),
).compartment("EcosystemCards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "FaunaCardBox",
    size=(card_box_width, card_box_length, fauna_cards_height),
    position=(0.0, card_box_length, ecosystem_cards_height),
    lid=_lid("Fauna", "chocolate"),
).compartment("FaunaCards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "IslandCardBox",
    size=(card_box_width, card_box_length, island_cards_height),
    position=(0.0, card_box_length, ecosystem_cards_height + fauna_cards_height),
    lid=_lid("Island", "teal"),
).compartment("IslandCards", cut=FingerCut.SCOOP)

# ── 3. Row 1 Col 1 (X = 68..136, Y = 99..198): Climate, Solo, Season, Abundance, Start
col1_z = 0.0
col1_cards = [
    ("ClimateCardBox", "Climate", "steelblue", climate_cards_height),
    ("SoloCardBox", "Solo", "slategray", solo_cards_height),
    ("SeasonCardBox", "Season", "darkorange", season_cards_height),
    ("AbundanceOtherCardBox", "Abundance", "goldenrod", abundance_other_cards_height),
]
for label, title, color_name, h in col1_cards:
    project.box(
        BoxType.SLIDING,
        label,
        size=(card_box_width, card_box_length, h),
        position=(card_box_width, card_box_length, col1_z),
        lid=_lid(title, color_name),
    ).compartment("Cards", cut=FingerCut.SCOOP)
    col1_z += h

start_box = project.box(
    BoxType.CAP,
    "StartBox",
    size=(card_box_width, card_box_length, start_box_height),
    position=(card_box_width, card_box_length, col1_z),
    lid=_lid("Start", "olive"),
)
start_box.compartment("StartDisk", length_ratio=0.5, cut=FingerCut.SCOOP)
start_box.compartment("ActiveToken", length_ratio=0.5, cut=FingerCut.SCOOP)

# ── 4. Row 1 Col 3 (X = 204..272, Y = 99..198): 6 Stacked Player Boxes
player_colors = ["red", "green", "yellow", "blue", "purple", "pink"]
for idx, color_name in enumerate(player_colors):
    p_box = project.box(
        BoxType.SLIPOVER,
        f"PlayerBox_{color_name.title()}",
        size=(player_box_width, player_box_length, player_box_height),
        position=(card_box_width * 3.0, card_box_length, player_box_height * idx),
        lid=_lid(
            f"Player ({color_name.title()})",
            color_name,
            text_color="black" if color_name in ("yellow", "pink") else "white",
        ),
    )
    p_box.compartment("ReadinessToken", length_ratio=0.45, cut=FingerCut.SCOOP)
    p_box.compartment("LeafTokens", length_ratio=0.55, cut=FingerCut.SCOOP)

# ── 5. Row 2 (Y = 198..287): Canopy, ScorePad, Sprouts ───────────
project.box(
    BoxType.FILAMENT_HINGE,
    "CanopyBox",
    size=(canopy_box_width, canopy_box_length, canopy_box_height),
    position=(0.0, card_box_length * 2.0, 0.0),
    lid=_lid("Canopy", "peru"),
).compartment("CanopiesAndTrunks", cut=FingerCut.SCOOP)

project.box(
    BoxType.NO_LID,
    "ScorePadBox",
    size=(score_pad_box_width, score_pad_box_length, score_pad_box_height),
    position=(canopy_box_width, card_box_length * 2.0, 0.0),
    hollow=True,
)

project.box(
    BoxType.FILAMENT_HINGE,
    "SproutBox",
    size=(sprout_box_width, sprout_box_length, sprout_box_height),
    position=(canopy_box_width, card_box_length * 2.0, score_pad_box_height),
    lid=_lid("Sprouts", "limegreen"),
).compartment("SproutCubes", cut=FingerCut.SCOOP)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
