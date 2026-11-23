#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Biome board game organizer.

Ports boxes/biome/biome.scad to the pyboxbuilder Project API.
Organizes 4 player boxes, 8 wooden resource boxes (mouse, sun, fish, leaf,
spider, berry, chicks, rabbits), nest boards tray, climate spinner holder,
extra bits box (cubes, coin, die, season & start-player tokens), and all
8 card boxes (2 main plant/animal decks, starting, achievement, changing
condition, legend, extra plant/animal, and big biome deck) with automatic spacers.
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
    else ROOT / "boxes" / "biome" / "assets"
)

# ── Box & Board Dimensions ────────────────────────────────────────
box_width = 285.0
box_length = 285.0
box_height = 73.0

board_thickness = 20.0
board_width = 255.0
usable_height = box_height - board_thickness  # 53.0mm
insert_height = usable_height - 1.0  # 52.0mm (1mm vertical slack per biome.scad)

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 3.0

# ── Component Dimensions ──────────────────────────────────────────
nest_width = 45.0
spinner_thickness = 9.0
card_width = 66.0
card_length = 91.0
single_card_thickness = 0.6

# ── Sub-Box Dimensions (matching biome.scad) ──────────────────────
player_box_width = wall_thickness * 4.0 + nest_width  # 57.0mm
player_box_length = (box_length - 2.0) / 4.0  # 70.75mm
player_box_height = insert_height / 3.0  # 17.333mm

nest_box_width = nest_width + floor_thickness + lid_thickness + 2.0  # 52.0mm
nest_box_length = box_length - 2.0  # 283.0mm
nest_box_height = insert_height  # 52.0mm

spinner_box_height = spinner_thickness + floor_thickness  # 11.0mm
card_box_width = card_width + 1.0 + wall_thickness * 2.0  # 73.0mm
card_box_length = card_length + 1.0 + wall_thickness * 2.0  # 98.0mm
card_box_height = insert_height - spinner_box_height  # 41.0mm

spinner_box_width = box_width - player_box_width - nest_box_width - 2.0  # 174.0mm
spinner_box_length = box_length - 2.0 - card_box_length  # 185.0mm

starting_card_box_height = single_card_thickness * 14.0 + lid_thickness + floor_thickness + 1.0  # 14.4mm
achievement_card_box_height = single_card_thickness * 13.0 + lid_thickness + floor_thickness + 1.0  # 13.8mm
changing_condition_card_box_height = single_card_thickness * 11.0 + lid_thickness + floor_thickness + 1.0  # 12.6mm
legend_card_box_height = single_card_thickness * 9.0 + lid_thickness + floor_thickness + 1.0  # 11.4mm
plant_animal_extra_card_box_height = card_box_height - legend_card_box_height  # 29.6mm
big_card_box_height = insert_height  # 52.0mm

extra_bits_box_width = box_width - board_width - 1.0  # 29.0mm
extra_bits_box_length = box_length - 1.0  # 284.0mm
extra_bits_box_height = card_box_height  # 41.0mm

project = Project(
    "Biome",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
    box_defaults={"expandable": False},
)

BIOME_PATTERN = PatternBuilder(PatternType.LEAF_VEINS)
BIOME_FONT = "Georgia:style=Bold"


def _biome_lid(
    text: str,
    frame_color: str,
    *,
    text_color: str | None = None,
    logo_file: str | None = None,
    logo_size: float = 15.0,
    narrow: bool = False,
) -> LidBuilder:
    resolved_text_color = text_color or ("black" if frame_color in ("gold", "khaki", "yellow") else "white")
    use_logo = logo_file is not None and not narrow
    return LidBuilder(
        text=text,
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.SCALLOPED,
        label_finial=LabelFinial.NONE if narrow else LabelFinial.FLEURON,
        font=BIOME_FONT,
        pattern=BIOME_PATTERN,
        text_color=Color(resolved_text_color),
        frame_color=Color(frame_color),
        logo=str(ASSETS / logo_file) if use_logo and logo_file is not None else None,
        logo_color=Color(resolved_text_color) if use_logo else None,
        logo_position="left" if use_logo else None,
        label_logo_size_mm=logo_size if use_logo else None,
    )


# ── Column 0: Player & Resource Trays (4x3 stack at X = 0 .. 57) ──
col0_layers: list[list[tuple[str, str, str, str | None]]] = [
    [
        ("PlayerBox_Red", "Red", "darkred", None),
        ("PlayerBox_Blue", "Blue", "navy", None),
        ("PlayerBox_Green", "Green", "green", None),
        ("PlayerBox_Yellow", "Yellow", "goldenrod", None),
    ],
    [
        ("Resource_Mouse", "Mouse", "gray", "mouse.svg"),
        ("Resource_Sun", "Sun", "gold", "sun.svg"),
        ("Resource_Fish", "Fish", "dodgerblue", "fish.svg"),
        ("Resource_Leaf", "Leaf", "forestgreen", "leaf.svg"),
    ],
    [
        ("Resource_Spider", "Spider", "black", "spider.svg"),
        ("Resource_Berry", "Berry", "purple", "berry.svg"),
        ("Resource_Chicks", "Chicks", "khaki", "chick.svg"),
        ("Resource_Rabbits", "Rabbits", "saddlebrown", "rabbit.svg"),
    ],
]

for layer_idx, items in enumerate(col0_layers):
    for row_idx, (box_id, title, color_name, logo_file) in enumerate(items):
        project.box(
            BoxType.CAP,
            box_id,
            size=(player_box_width, player_box_length, player_box_height),
            position=(0.0, player_box_length * row_idx, player_box_height * layer_idx),
            lid=_biome_lid(title, color_name, logo_file=logo_file, logo_size=14.0),
        ).compartment("Tokens", cut=FingerCut.SCOOP)

# ── Column 1: Nest Boards Longitudinal Tray (X = 57 .. 109) ───────
project.box(
    BoxType.CAP,
    "NestBox",
    size=(nest_box_width, nest_box_length, nest_box_height),
    position=(player_box_width, 0.0, 0.0),
    lid=_biome_lid("Nests", "peru", logo_file="nest.svg", logo_size=16.0),
).compartment("NestBoards", cut=FingerCut.SCOOP)

# ── Columns 2–3: Card Boxes & Spinner Holder (X = 109 .. 255) ─────
cards_x0 = player_box_width + nest_box_width  # 109.0mm
cards_x1 = cards_x0 + card_box_width  # 182.0mm

for deck_id, title, x_pos, color_name in [
    ("CardBox_MainDeck1", "Play", cards_x0, "forestgreen"),
    ("CardBox_MainDeck2", "Play", cards_x1, "darkolivegreen"),
]:
    project.box(
        BoxType.SLIDING,
        deck_id,
        size=(card_box_width, card_box_length, card_box_height),
        position=(x_pos, 0.0, 0.0),
        lid=_biome_lid(title, color_name),
    ).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "CardBox_Starting",
    size=(card_box_width, card_box_length, starting_card_box_height),
    position=(cards_x0, card_box_length, 0.0),
    lid=_biome_lid("Starting", "teal"),
).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "CardBox_Achievement",
    size=(card_box_width, card_box_length, achievement_card_box_height),
    position=(cards_x0, card_box_length, starting_card_box_height),
    lid=_biome_lid("Achievement", "darkgoldenrod"),
).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "CardBox_ChangingCondition",
    size=(card_box_width, card_box_length, changing_condition_card_box_height),
    position=(cards_x0, card_box_length, starting_card_box_height + achievement_card_box_height),
    lid=_biome_lid("Change", "sienna"),
).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "CardBox_Legend",
    size=(card_box_width, card_box_length, legend_card_box_height),
    position=(cards_x1, card_box_length, 0.0),
    lid=_biome_lid("Legend", "indigo"),
).compartment("Cards", cut=FingerCut.SCOOP)

project.box(
    BoxType.SLIDING,
    "CardBox_PlantAnimalExtra",
    size=(card_box_width, card_box_length, plant_animal_extra_card_box_height),
    position=(cards_x1, card_box_length, legend_card_box_height),
    lid=_biome_lid("Play Extra", "seagreen"),
).compartment("Cards", cut=FingerCut.SCOOP)

# BigCardBox is rotated 90 deg in biome.scad (98mm wide x 73mm long x 52mm tall)
project.box(
    BoxType.SLIDING,
    "CardBox_BigBiome",
    size=(card_box_length, card_box_width, big_card_box_height),
    position=(cards_x0, card_box_length * 2.0, 0.0),
    lid=_biome_lid("Biome", "darkgreen"),
).compartment("Cards", cut=FingerCut.SCOOP)

# SpinnerHolder sits atop the card boxes and ExtraBitsBox at Z = 41mm
project.box(
    BoxType.NO_LID,
    "SpinnerHolder",
    size=(spinner_box_width, spinner_box_length, spinner_box_height),
    position=(cards_x0, 0.0, card_box_height),
).compartment("Spinner", cut=FingerCut.SCOOP)

# ── Column 4: Extra Bits Box (X = 255 .. 284) ─────────────────────
# SlipoverBox interior is reduced by outer slipover lid wall + clearance (9.4mm total)
extra_bits_inner_width = 19.6
extra_bits_inner_length = 274.6

player_cube = 9.0
other_token_thickness = 6.5
crescent_diameter = 16.0
crescent_height = 12.05
leaf_well_width = 11.0
leaf_well_length = 29.5
die_size = 17.0
coin_well_diameter = min(26.0, extra_bits_inner_width - 0.6)  # 19.0mm (clamped to slipover interior)
coin_thickness = 3.0


def _extra_bits_elements() -> tuple[CompartmentElement, ...]:
    """Build custom stepped token/cube/coin/die wells matching ExtraBitsBox in biome.scad."""
    cx = extra_bits_inner_width / 2.0  # 9.8mm
    trough_w = extra_bits_inner_width - 1.6  # 18.0mm
    elems: list[CompartmentElement] = []

    # Phase & year cubes (9x9mm, depth 9.5mm) + shared upper finger trough (depth 5.5mm)
    cube_depth = player_cube + 0.5
    for idx, cube_cy in enumerate((15.0, 30.0), start=1):
        elems.append(
            CompartmentElement(
                shape=ElementShape.RECT,
                size=(player_cube, player_cube),
                offset=(cx - player_cube / 2.0, cube_cy - player_cube / 2.0),
                depth=cube_depth,
                pull_out=False,
                label=f"PhaseYearCube_{idx}",
            )
        )
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(trough_w, 36.0),
            offset=(cx - trough_w / 2.0, 22.5 - 18.0),
            depth=cube_depth - 4.0,
            corner_radius=6.0,
            bottom_rounding=2.0,
            pull_out=False,
            label="PhaseYearFingerTrough",
        )
    )

    # Coin well (depth 3.5mm) + top/bottom circular finger bites
    coin_cy = extra_bits_inner_length / 2.0  # 137.3mm
    coin_depth = coin_thickness + 0.5
    elems.append(
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(coin_well_diameter, coin_well_diameter),
            offset=(cx - coin_well_diameter / 2.0, coin_cy - coin_well_diameter / 2.0),
            depth=coin_depth,
            pull_out=False,
            label="Coin",
        )
    )
    coin_bite_d = 16.0
    for side_idx, sign in enumerate((-1.0, 1.0), start=1):
        bite_cy = coin_cy + sign * (coin_well_diameter / 2.0)
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(coin_bite_d, coin_bite_d),
                offset=(cx - coin_bite_d / 2.0, bite_cy - coin_bite_d / 2.0),
                depth=coin_depth,
                bottom_rounding=1.5,
                pull_out=False,
                label=f"CoinBite_{side_idx}",
            )
        )

    # Season crescent token (SVG) + Start-player leaf token (SVG) + shared finger channel
    season_cy = extra_bits_inner_length / 2.0 + 35.0  # 172.3mm
    leaf_cy = season_cy + 25.0  # 197.3mm
    token_depth = other_token_thickness + 0.5
    elems.append(
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "crescent.svg"),
            size=(crescent_diameter, crescent_height),
            offset=(cx - crescent_diameter / 2.0, season_cy - crescent_height / 2.0),
            depth=token_depth,
            pull_out=False,
            label="SeasonCrescentToken",
        )
    )
    elems.append(
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "leaf.svg"),
            size=(leaf_well_width, leaf_well_length),
            offset=(cx - leaf_well_width / 2.0, leaf_cy - leaf_well_length / 2.0),
            depth=token_depth,
            pull_out=False,
            label="StartPlayerLeafToken",
        )
    )
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(trough_w, 56.0),
            offset=(cx - trough_w / 2.0, (season_cy + 20.0) - 28.0),
            depth=other_token_thickness / 2.0,
            corner_radius=6.0,
            bottom_rounding=1.5,
            pull_out=False,
            label="SeasonLeafFingerTrough",
        )
    )

    # Die well (17x17mm, depth 17.5mm) + upper finger trough (depth 9.0mm)
    die_cy = extra_bits_inner_length - 30.0  # 244.6mm
    die_depth = die_size + 0.5
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(die_size, die_size),
            offset=(cx - die_size / 2.0, die_cy - die_size / 2.0),
            depth=die_depth,
            corner_radius=1.0,
            pull_out=False,
            label="Die",
        )
    )
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(trough_w, 34.0),
            offset=(cx - trough_w / 2.0, die_cy - 17.0),
            depth=die_depth - die_size / 2.0,
            corner_radius=6.0,
            bottom_rounding=3.0,
            pull_out=False,
            label="DieFingerTrough",
        )
    )

    return tuple(elems)


extra_bits = project.box(
    BoxType.SLIPOVER,
    "ExtraBitsBox",
    size=(extra_bits_box_width, extra_bits_box_length, extra_bits_box_height),
    position=(board_width, 0.0, 0.0),
    lid=_biome_lid("Biome", "olivedrab", narrow=True),
)
extra_bits.compartment(
    "CubesCoinTokensDie",
    size=(extra_bits_inner_width, extra_bits_inner_length),
    position=(0.0, 0.0),
    elements=_extra_bits_elements(),
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
