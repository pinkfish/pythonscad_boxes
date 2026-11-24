#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Earth (+ Abundance expansion) board game organizer.

Ports boxes/earth/earth.scad to the pyboxbuilder Project API.
Organizes all 26 boxes/trays: 4 main Earth card boxes + small Earth card box,
Ecosystem/Fauna/Island/Climate/Solo/Season/Abundance card boxes, Start token
box, 6 stacked slipover player trays, Canopy/Sprout/Compost/Seed boxes,
ScorePad tray, and top spacer above the standing Abundance boards.
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
    else ROOT / "boxes" / "earth" / "assets"
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

project.define_inventory(
    {
        "Player Boards": 6,
        "Fauna Board": 1,
        "Abundance Teams Board": 1,
        "Abundance Boards": 6,
        "Earth Cards": 353,
        "Ecosystem Cards": ecosystem_cards,
        "Fauna Cards": fauna_cards,
        "Island Cards": 10,
        "Climate Cards": climate_cards,
        "Solo Cards": solo_cards,
        "Season Cards": season_cards,
        "Abundance Reference & Setup Cards": abundance_other_cards,
        "Soil Tokens": 151,
        "Seed Tokens": 32,
        "First Player Token": 1,
        "Active Player Token": 1,
        "Score Override Marker": 1,
        "Readiness Tokens": 6,
        "Player Leaf Tokens": 30,
        "Tree Trunks": 125,
        "Tree Canopies": 104,
        "Score Pads": 2,
        "Sprout Cubes": 195,
    }
)

project.board(
    "Player & Island Boards",
    size=(player_board_width, player_board_width, total_board_reserve),
    position=(0.0, 0.0, usable_height),
    count=8,
    notes="6 player boards + 2 middle boards on top",
    allocates={"Player Boards": 6, "Fauna Board": 1, "Abundance Teams Board": 1},
)
project.board(
    "Abundance Boards",
    size=(
        abundance_board_thickness * abundance_board_count,
        abundance_board_length,
        abundance_board_width,
    ),
    position=(
        box_width - abundance_board_thickness * abundance_board_count,
        seed_box_length,
        0.0,
    ),
    count=6,
    notes="Standing on edge along right wall under TopSpacedBox",
    component="Abundance Boards",
)

EARTH_PATTERN = PatternBuilder(PatternType.LEAF_TESSELLATION)
EARTH_FONT = "Georgia:style=Bold"


def _lid(
    text: str,
    frame_color: str,
    text_color: str = "white",
    *,
    shape: LabelShape = LabelShape.SCROLL,
    logo_file: str | None = None,
    logo_size: float = 15.0,
    narrow: bool = False,
) -> LidBuilder:
    use_logo = logo_file is not None and not narrow
    return LidBuilder(
        text=text,
        label_mode=LabelMode.FRAMED,
        label_shape=shape,
        label_finial=LabelFinial.NONE if narrow else LabelFinial.FLEURON,
        font=EARTH_FONT,
        pattern=EARTH_PATTERN,
        text_color=Color(text_color),
        frame_color=Color(frame_color),
        logo=str(ASSETS / logo_file) if use_logo and logo_file is not None else None,
        logo_color=Color(text_color) if use_logo else None,
        logo_position="left" if use_logo else None,
        label_logo_size_mm=logo_size if use_logo else None,
    )


# ── 1. Row 0 (Y = 0..99): Main Earth Card Decks, Compost, Seed ───
main_decks = [
    ("CardBox_Flora", "Earth", "forestgreen", (0.0, 0.0, 0.0), 85),
    ("CardBox_Terrain", "Earth", "sienna", (card_box_width, 0.0, 0.0), 85),
    ("CardBox_Events", "Earth", "royalblue", (card_box_width * 2.0, 0.0, 0.0), 85),
    ("CardBox_Abundance", "Earth", "darkgoldenrod", (card_box_width * 2.0, card_box_length, 0.0), 75),
]
for label, title, color_name, pos, card_count in main_decks:
    project.box(
        BoxType.SLIDING,
        label,
        size=(card_box_width, card_box_length, card_box_height),
        position=pos,
        lid=_lid(title, color_name),
    ).compartment("Cards", cut=FingerCut.SCOOP, component="Earth Cards", count=card_count)

project.box(
    BoxType.SLIDING,
    "EarthCardBoxSmall",
    size=(card_box_width, card_box_length, earth_small_box_height),
    position=(card_box_width * 3.0, 0.0, 0.0),
    lid=_lid("Earth", "olive"),
).compartment("Cards", cut=FingerCut.SCOOP, component="Earth Cards", count=23)

project.box(
    BoxType.FILAMENT_HINGE,
    "CompostBox_1",
    size=(card_box_width, card_box_length, compost_box_height),
    position=(card_box_width * 3.0, 0.0, earth_small_box_height),
    lid=_lid("Compost", "dimgray", shape=LabelShape.OVAL, logo_file="compost.svg", logo_size=15.0),
).compartment("Compost", cut=FingerCut.SCOOP, component="Soil Tokens", count=76)

project.box(
    BoxType.FILAMENT_HINGE,
    "CompostBox_2",
    size=(card_box_width, card_box_length, compost_box_height),
    position=(card_box_width * 3.0, 0.0, earth_small_box_height + compost_box_height),
    lid=_lid("Compost", "dimgray", shape=LabelShape.OVAL, logo_file="compost.svg", logo_size=15.0),
).compartment("Compost", cut=FingerCut.SCOOP, component="Soil Tokens", count=75)

project.box(
    BoxType.SLIPOVER,
    "SeedBox",
    size=(seed_box_width, seed_box_length, seed_box_height),
    position=(card_box_width * 4.0, 0.0, 0.0),
    wall_thickness=2.0,
    lid=_lid("Seeds", "saddlebrown", shape=LabelShape.OVAL, narrow=True),
).compartment("Seeds", cut=FingerCut.SCOOP, component="Seed Tokens", count=32)

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
).compartment("EcosystemCards", cut=FingerCut.SCOOP, component="Ecosystem Cards", count=ecosystem_cards)

project.box(
    BoxType.SLIDING,
    "FaunaCardBox",
    size=(card_box_width, card_box_length, fauna_cards_height),
    position=(0.0, card_box_length, ecosystem_cards_height),
    lid=_lid("Fauna", "chocolate"),
).compartment("FaunaCards", cut=FingerCut.SCOOP, component="Fauna Cards", count=fauna_cards)

project.box(
    BoxType.SLIDING,
    "IslandCardBox",
    size=(card_box_width, card_box_length, island_cards_height),
    position=(0.0, card_box_length, ecosystem_cards_height + fauna_cards_height),
    lid=_lid("Island", "teal"),
).compartment("IslandCards", cut=FingerCut.SCOOP, component="Island Cards", count=10)

# ── 3. Row 1 Col 1 (X = 68..136, Y = 99..198): Climate, Solo, Season, Abundance, Start
col1_z = 0.0
col1_cards = [
    ("ClimateCardBox", "Climate", "steelblue", climate_cards_height, "Climate Cards", climate_cards),
    ("SoloCardBox", "Solo", "slategray", solo_cards_height, "Solo Cards", solo_cards),
    ("SeasonCardBox", "Season", "darkorange", season_cards_height, "Season Cards", season_cards),
    (
        "AbundanceOtherCardBox",
        "Abundance",
        "goldenrod",
        abundance_other_cards_height,
        "Abundance Reference & Setup Cards",
        abundance_other_cards,
    ),
]
for label, title, color_name, h, comp_name, card_count in col1_cards:
    project.box(
        BoxType.SLIDING,
        label,
        size=(card_box_width, card_box_length, h),
        position=(card_box_width, card_box_length, col1_z),
        lid=_lid(title, color_name),
    ).compartment("Cards", cut=FingerCut.SCOOP, component=comp_name, count=card_count)
    col1_z += h

card_inner_width = card_box_width - wall_thickness * 2.0  # 62.0mm
card_inner_length = card_box_length - wall_thickness * 2.0  # 93.0mm

start_disk_diameter = 41.0
start_disk_thickness = 5.0
readiness_token_width = 36.5
readiness_token_length = 59.0
readiness_token_thickness = 5.0
score_override_marker_width = 16.5
score_override_marker_length = 18.5
score_override_thickness = 3.0
leaf_width = 13.0
leaf_length = 17.5
leaf_thickness = 3.0


def _start_box_elements() -> tuple[CompartmentElement, ...]:
    """Build StartDisk (with angled finger bites), ActiveToken, and ScoreOverride wells."""
    elems: list[CompartmentElement] = []

    # 1. Start disk circular well (d=41mm, depth 5.5mm) + finger bites at 45 & 215 deg
    disk_cx = card_inner_width / 2.0 + 7.0  # 38.0mm
    disk_cy = start_disk_diameter / 2.0 + 2.0  # 22.5mm
    disk_depth = start_disk_thickness + 0.5  # 5.5mm
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(start_disk_diameter, start_disk_diameter),
            offset=(disk_cx - start_disk_diameter / 2.0, disk_cy - start_disk_diameter / 2.0),
            depth=disk_depth,
            pull_out=False,
            label="StartDisk",
        )
    )
    disk_bite_d = 18.0  # r=9.0 fits strictly inside [0, 62] x [0, 93]
    for idx, angle_deg in enumerate((45.0, 215.0), start=1):
        rad = math.radians(angle_deg)
        bite_cx = disk_cx + (start_disk_diameter / 2.0) * math.cos(rad)
        bite_cy = disk_cy + (start_disk_diameter / 2.0) * math.sin(rad)
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(disk_bite_d, disk_bite_d),
                offset=(bite_cx - disk_bite_d / 2.0, bite_cy - disk_bite_d / 2.0),
                depth=disk_depth,
                pull_out=False,
                label=f"StartDiskBite_{idx}",
            )
        )

    # 2. Active player token well (59x36.5mm, depth 5.5mm) + front finger bite
    active_cx = card_inner_width / 2.0  # 31.0mm
    active_cy = card_inner_length - readiness_token_width / 2.0 - 2.0  # 72.75mm
    active_depth = readiness_token_thickness + 0.5  # 5.5mm
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(readiness_token_length, readiness_token_width),
            offset=(active_cx - readiness_token_length / 2.0, active_cy - readiness_token_width / 2.0),
            depth=active_depth,
            corner_radius=1.0,
            pull_out=False,
            label="ActiveToken",
        )
    )
    active_bite_d = 24.0
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(active_bite_d, active_bite_d),
            offset=(
                active_cx - active_bite_d / 2.0,
                active_cy - readiness_token_width / 2.0 - active_bite_d / 2.0,
            ),
            depth=active_depth,
            pull_out=False,
            label="ActiveTokenBite",
        )
    )

    # 3. Score override marker "11" (16.5x18.5mm, depth 3.5mm) + front finger bite
    override_cx = score_override_marker_length / 2.0 + 2.0  # 11.25mm
    override_cy = start_disk_diameter  # 41.0mm
    override_depth = score_override_thickness + 0.5  # 3.5mm
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(score_override_marker_width, score_override_marker_length),
            offset=(
                override_cx - score_override_marker_width / 2.0,
                override_cy - score_override_marker_length / 2.0,
            ),
            depth=override_depth,
            corner_radius=1.0,
            pull_out=False,
            label="ScoreOverrideMarker",
        )
    )
    override_bite_d = 16.0
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(override_bite_d, override_bite_d),
            offset=(
                override_cx - override_bite_d / 2.0,
                override_cy - score_override_marker_length / 2.0 - override_bite_d / 2.0,
            ),
            depth=override_depth,
            pull_out=False,
            label="ScoreOverrideBite",
        )
    )

    return tuple(elems)


player_inner_width = 58.6  # SlipoverBox interior width for 68mm outer width
player_inner_length = 89.6  # SlipoverBox interior length for 99mm outer length


def _player_box_elements() -> tuple[CompartmentElement, ...]:
    """Build ReadinessToken + 5 staggered LeafTeardrop SVG wells with finger grabs."""
    elems: list[CompartmentElement] = []
    # SlipoverBox interior height for 9.2mm outer height (2mm floor + 2mm lid + 0.2mm clearance)
    player_inner_height = 5.0

    # 1. Readiness token (clamped to 58.6x36.5mm) + rear circular finger grab (d=22mm)
    ready_w = min(readiness_token_length, player_inner_width)
    ready_cx = player_inner_width / 2.0  # 29.3mm
    ready_y0 = 1.5
    ready_depth = min(readiness_token_thickness + 0.3, player_inner_height)  # 5.0mm
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(ready_w, readiness_token_width),
            offset=(ready_cx - ready_w / 2.0, ready_y0),
            depth=ready_depth,
            corner_radius=1.0,
            pull_out=False,
            label="ReadinessToken",
        )
    )
    ready_grab_d = 22.0
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(ready_grab_d, ready_grab_d),
            offset=(ready_cx - ready_grab_d / 2.0, ready_y0 + readiness_token_width - ready_grab_d / 2.0),
            depth=ready_depth,
            bottom_rounding=2.0,
            pull_out=False,
            label="ReadinessFingerGrab",
        )
    )

    # 2. 5 staggered leaf teardrop wells (rotated 90 deg -> 17.5x13mm) + left finger grabs (d=14mm)
    leaf_depth = leaf_thickness + 0.3  # 3.3mm
    leaf_grab_d = 14.0
    base_cx = player_inner_width / 2.0 + 1.5  # 30.8mm
    base_cy = 54.5
    leaf_svg = str(ASSETS / "leaf_teardrop.svg")
    leaf_idx = 0
    for i in range(3):
        for j in range(2):
            if j == 0 and i == 1:
                continue
            leaf_idx += 1
            lcx = base_cx + 13.5 * (i - 1)
            lcy = base_cy + 26.5 * (j - (i % 2) * 0.5)
            # After 90 deg rotation, footprint is (leaf_length, leaf_width) = (17.5, 13.0)
            elems.append(
                CompartmentElement(
                    shape=ElementShape.SVG,
                    shape_file=leaf_svg,
                    size=(leaf_width, leaf_length),
                    rotation=90.0,
                    offset=(lcx - leaf_length / 2.0, lcy - leaf_width / 2.0),
                    depth=leaf_depth,
                    pull_out=False,
                    label=f"LeafToken_{leaf_idx}",
                )
            )
            grab_cx = lcx - leaf_length / 2.0
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(leaf_grab_d, leaf_grab_d),
                    offset=(grab_cx - leaf_grab_d / 2.0, lcy - leaf_grab_d / 2.0),
                    depth=leaf_depth,
                    bottom_rounding=1.5,
                    pull_out=False,
                    label=f"LeafFingerGrab_{leaf_idx}",
                )
            )

    return tuple(elems)


start_box = project.box(
    BoxType.CAP,
    "StartBox",
    size=(card_box_width, card_box_length, start_box_height),
    position=(card_box_width, card_box_length, col1_z),
    lid=_lid("Start", "olive", shape=LabelShape.OVAL),
)
start_box.compartment(
    "StartTokens",
    size=(card_inner_width, card_inner_length),
    position=(0.0, 0.0),
    elements=_start_box_elements(),
    allocates={
        "First Player Token": 1,
        "Active Player Token": 1,
        "Score Override Marker": 1,
    },
)

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
            shape=LabelShape.OVAL,
            logo_file="leaf_teardrop.svg",
            logo_size=15.0,
        ),
    )
    p_box.compartment(
        "PlayerTokens",
        size=(player_inner_width, player_inner_length),
        position=(0.0, 0.0),
        elements=_player_box_elements(),
        allocates={"Readiness Tokens": 1, "Player Leaf Tokens": 5},
    )

# ── 5. Row 2 (Y = 198..287): Canopy, ScorePad, Sprouts ───────────
project.box(
    BoxType.FILAMENT_HINGE,
    "CanopyBox",
    size=(canopy_box_width, canopy_box_length, canopy_box_height),
    position=(0.0, card_box_length * 2.0, 0.0),
    lid=_lid("Canopy", "peru", shape=LabelShape.OVAL, logo_file="canopy.svg", logo_size=18.0),
).compartment(
    "CanopiesAndTrunks",
    cut=FingerCut.SCOOP,
    allocates={"Tree Trunks": 125, "Tree Canopies": 104},
)

project.box(
    BoxType.NO_LID,
    "ScorePadBox",
    size=(score_pad_box_width, score_pad_box_length, score_pad_box_height),
    position=(canopy_box_width, card_box_length * 2.0, 0.0),
    hollow=True,
).allocate("Score Pads", 2)

project.box(
    BoxType.FILAMENT_HINGE,
    "SproutBox",
    size=(sprout_box_width, sprout_box_length, sprout_box_height),
    position=(canopy_box_width, card_box_length * 2.0, score_pad_box_height),
    lid=_lid("Sprouts", "limegreen", shape=LabelShape.OVAL, logo_file="sprout.svg", logo_size=16.0),
).compartment("SproutCubes", cut=FingerCut.SCOOP, component="Sprout Cubes", count=195)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
