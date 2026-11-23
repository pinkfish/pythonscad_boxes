#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Explorers of Navoria: Forgotten Lands expansion organizer.

Ports examples/explorers_of_navoria_forgotten_lands.scad to the pyboxbuilder Project API.
Organizes 5th player (White) pieces, faction skill boards, exploration tiles,
and expansion cards with automated spacers.
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
    else ROOT / "boxes" / "explorers_of_navoria_forgotten_lands" / "assets"
)

# ── Box & Board Dimensions ────────────────────────────────────────
box_width = 211.0
box_length = 268.0
box_height = 50.0

board_thickness = 4.0
usable_height = box_height - board_thickness  # 46.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

player_box_width = 98.0
player_box_length = (box_length - 2.0) / 2.0  # 133.0mm
player_box_height = usable_height / 2.0       # 23.0mm

card_width = 68.0
card_length = 92.0

faction_skill_box_width = 67.0
faction_skill_box_length = 150.0
faction_skill_box_height = usable_height / 2.0  # 23.0mm

bits_box_width = box_width - player_box_width - 2.0  # 111.0mm
bits_box_length = faction_skill_box_length
bits_box_height = usable_height / 2.0

card_box_width = bits_box_width
card_box_length = box_length - faction_skill_box_length - 2.0  # 116.0mm
card_box_height = usable_height

project = Project(
    "ExplorersOfNavoriaForgottenLands",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

NAVORIA_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── Interior Geometry Helpers (from explorers_of_navoria_forgotten_lands.scad)
player_inner_w = player_box_width - wall_thickness * 2.0    # 92.0mm
player_inner_l = player_box_length - wall_thickness * 2.0   # 127.0mm
player_inner_h = player_box_height - floor_thickness - lid_thickness  # 19.0mm

faction_inner_w = faction_skill_box_width - wall_thickness * 2.0   # 61.0mm
faction_inner_l = faction_skill_box_length - wall_thickness * 2.0  # 144.0mm
faction_inner_h = faction_skill_box_height - floor_thickness - lid_thickness  # 19.0mm

bits_inner_w = bits_box_width - wall_thickness * 2.0        # 105.0mm
bits_inner_l = bits_box_length - wall_thickness * 2.0       # 144.0mm
bits_inner_h = bits_box_height - floor_thickness - lid_thickness  # 19.0mm


def _white_trading_post_elements() -> tuple[CompartmentElement, ...]:
    """8 White trading-post silhouette wells + central finger bites + marker tray."""
    svg_path = str(ASSETS / "trading_post_white.svg")
    post_w, post_h = 16.0, 15.0
    well_d = 10.0  # marker_thickness + 1
    elems: list[CompartmentElement] = []
    for row in range(4):
        cy = 14.0 + row * 24.0
        for col, (cx, rot) in enumerate(((30.0, 90.0), (62.0, -90.0))):
            elems.append(
                CompartmentElement(
                    shape=ElementShape.SVG,
                    shape_file=svg_path,
                    size=(post_w, post_h),
                    rotation=rot,
                    offset=(cx - post_h / 2.0, cy - post_w / 2.0),
                    depth=well_d,
                    pull_out=False,
                    label=f"WhitePost_{row}_{col}",
                )
            )
        bite_d = 20.0
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(bite_d, bite_d),
                offset=(player_inner_w / 2.0 - bite_d / 2.0, cy - bite_d / 2.0),
                depth=well_d,
                pull_out=False,
                label=f"WhitePostBite_{row}",
            )
        )
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(84.0, 25.0),
            offset=(4.0, 99.0),
            corner_radius=6.0,
            bottom_rounding=3.0,
            depth=player_inner_h,
            pull_out=False,
            label="WhiteMarkerTray",
        )
    )
    return tuple(elems)


def _white_explorer_elements() -> tuple[CompartmentElement, ...]:
    """6 White explorer meeple silhouette wells + central finger bites + bird tray."""
    svg_path = str(ASSETS / "explorer_white.svg")
    exp_w, exp_h = 18.5, 21.5
    well_d = 10.0
    elems: list[CompartmentElement] = []
    for row in range(3):
        cy = 16.0 + row * 26.0
        for col, (cx, rot) in enumerate(((29.0, 90.0), (63.0, -90.0))):
            elems.append(
                CompartmentElement(
                    shape=ElementShape.SVG,
                    shape_file=svg_path,
                    size=(exp_w, exp_h),
                    rotation=rot,
                    offset=(cx - exp_h / 2.0, cy - exp_w / 2.0),
                    depth=well_d,
                    pull_out=False,
                    label=f"WhiteExplorer_{row}_{col}",
                )
            )
        bite_d = 18.0
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(bite_d, bite_d),
                offset=(player_inner_w / 2.0 - bite_d / 2.0, cy - bite_d / 2.0),
                depth=well_d,
                pull_out=False,
                label=f"WhiteExplorerBite_{row}",
            )
        )
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(84.0, 39.0),
            offset=(4.0, 84.0),
            corner_radius=6.0,
            bottom_rounding=3.0,
            depth=player_inner_h,
            pull_out=False,
            label="WhiteBirdTray",
        )
    )
    return tuple(elems)


def _rounded_token_bin() -> tuple[CompartmentElement, ...]:
    """RoundedBoxAllSides(radius=5) matching TokensBox in .scad."""
    return (
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(player_inner_w, player_inner_l),
            offset=(0.0, 0.0),
            corner_radius=5.0,
            bottom_rounding=5.0,
            depth=player_inner_h,
            pull_out=False,
            label="RoundedTokenBin",
        ),
    )


def _faction_skill_elements() -> tuple[CompartmentElement, ...]:
    """2 faction skill tile wells (arrow-headed + rectangular) with center finger bite."""
    return (
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "faction_skill_tile.svg"),
            size=(60.0, 75.0),
            offset=(0.5, 0.0),
            depth=faction_inner_h,
            pull_out=False,
            label="FactionSkillFront",
        ),
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(60.0, 66.0),
            offset=(0.5, 78.0),
            depth=faction_inner_h,
            pull_out=False,
            label="FactionSkillBack",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(24.0, 24.0),
            offset=(faction_inner_w / 2.0 - 12.0, 75.0 - 12.0),
            depth=faction_inner_h,
            pull_out=False,
            label="FactionSkillCenterBite",
        ),
    )


def _bits_box_elements() -> tuple[CompartmentElement, ...]:
    """BitsBox: PlayerOverlay, StartOval, 3 exploration tile wells, 4 species token wells."""
    elems: list[CompartmentElement] = []

    # 1. PlayerOverlay custom bezier silhouette (deep well)
    elems.append(
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "player_overlay.svg"),
            size=(73.0, 120.0),
            offset=(1.0, 2.0),
            depth=bits_inner_h,
            pull_out=False,
            label="PlayerOverlay",
        )
    )

    # 2. StartOval custom bezier silhouette (stepped top recess, depth=3mm)
    oval_depth = 3.0
    elems.append(
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=str(ASSETS / "start_oval.svg"),
            size=(61.0, 92.0),
            offset=(1.0, 2.0),
            depth=oval_depth,
            z_offset=bits_inner_h - oval_depth,
            pull_out=False,
            label="StartOval",
        )
    )

    # 3. Three Exploration Tile wells (34 x 42mm, depth=5mm) with front finger bites
    tile_w, tile_l = 34.0, 42.0
    tile_depth = 5.0
    tile_z = bits_inner_h - tile_depth
    tile_y = bits_inner_l - tile_l - 2.0  # 100.0mm
    tile_bite_d = 16.0
    for idx, tx in enumerate((0.5, 35.5, 70.5)):
        elems.append(
            CompartmentElement(
                shape=ElementShape.RECT,
                size=(tile_w, tile_l),
                offset=(tx, tile_y),
                depth=tile_depth,
                z_offset=tile_z,
                pull_out=False,
                label=f"ExplorationTiles_{idx + 1}",
            )
        )
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(tile_bite_d, tile_bite_d),
                offset=(tx + tile_w / 2.0 - tile_bite_d / 2.0, tile_y - tile_bite_d / 2.0),
                depth=tile_depth,
                z_offset=tile_z,
                pull_out=False,
                label=f"ExplorationTilesBite_{idx + 1}",
            )
        )

    # 4. Four Species Token circular wells (d=25mm, depth=10mm) with CylinderWithIndents bites (r=10mm)
    tok_d = 25.0
    tok_r = tok_d / 2.0
    tok_depth = 10.0
    tok_z = bits_inner_h - tok_depth
    bite_d = 20.0
    species_specs = [
        (bits_inner_w - tok_d, tok_d * 0.5, (0.0, 180.0)),
        (bits_inner_w - tok_d, tok_d * 3.5, (0.0, 180.0)),
        (bits_inner_w - tok_d * 2.0 - 4.0, tok_d * 3.5, (0.0, 180.0)),
        (bits_inner_w - tok_r, tok_d * 1.5, (90.0, 270.0)),
    ]
    for idx, (cx, cy, angles) in enumerate(species_specs, start=1):
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(tok_d, tok_d),
                offset=(cx - tok_r, cy - tok_r),
                depth=tok_depth,
                z_offset=tok_z,
                pull_out=False,
                label=f"SpeciesToken_{idx}",
            )
        )
        for a_idx, deg in enumerate(angles):
            dx = tok_r if deg == 0.0 else (-tok_r if deg == 180.0 else 0.0)
            dy = tok_r if deg == 90.0 else (-tok_r if deg == 270.0 else 0.0)
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(bite_d, bite_d),
                    offset=(cx + dx - bite_d / 2.0, cy + dy - bite_d / 2.0),
                    depth=tok_depth,
                    z_offset=tok_z,
                    pull_out=False,
                    label=f"SpeciesTokenBite_{idx}_{a_idx}",
                )
            )

    return tuple(elems)


# ── 1. 5th Player (White x2) & Solo/Contract Token Boxes ──────────
project.box(
    BoxType.CAP,
    "PlayerBox_White",
    size=(player_box_width, player_box_length, player_box_height),
    lid=LidBuilder(
        text="Player (White 1)",
        label_mode=LabelMode.FRAMED,
        pattern=NAVORIA_PATTERN,
        text_color=Color("black"),
        frame_color=Color("white"),
    ),
).compartment(
    "TradingPosts",
    size=(player_inner_w, player_inner_l),
    position=(0.0, 0.0),
    elements=_white_trading_post_elements(),
)

project.box(
    BoxType.CAP,
    "PlayerBox_White_2",
    size=(player_box_width, player_box_length, player_box_height),
    lid=LidBuilder(
        text="Player (White 2)",
        label_mode=LabelMode.FRAMED,
        pattern=NAVORIA_PATTERN,
        text_color=Color("black"),
        frame_color=Color("white"),
    ),
).compartment(
    "Explorers",
    size=(player_inner_w, player_inner_l),
    position=(0.0, 0.0),
    elements=_white_explorer_elements(),
)

project.box(
    BoxType.SLIDING,
    "SpeciesTokensBox",
    size=(player_box_width, player_box_length, player_box_height),
    lid=LidBuilder(
        text="Solo",
        label_mode=LabelMode.FRAMED,
        pattern=NAVORIA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("peru"),
    ),
).compartment(
    "SoloTokens",
    size=(player_inner_w, player_inner_l),
    position=(0.0, 0.0),
    elements=_rounded_token_bin(),
)

project.box(
    BoxType.SLIDING,
    "ContractTokensBox",
    size=(player_box_width, player_box_length, player_box_height),
    lid=LidBuilder(
        text="Contract",
        label_mode=LabelMode.FRAMED,
        pattern=NAVORIA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("sienna"),
    ),
).compartment(
    "ContractTokens",
    size=(player_inner_w, player_inner_l),
    position=(0.0, 0.0),
    elements=_rounded_token_bin(),
)

# ── 2. Faction Skills & Bits ──────────────────────────────────────
project.box(
    BoxType.SLIDING,
    "FactionSkillBox",
    size=(faction_skill_box_width, faction_skill_box_length, faction_skill_box_height),
    lid=LidBuilder(
        text="Faction Skills",
        label_mode=LabelMode.FRAMED,
        pattern=NAVORIA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("purple"),
    ),
).compartment(
    "FactionTiles",
    size=(faction_inner_w, faction_inner_l),
    position=(0.0, 0.0),
    elements=_faction_skill_elements(),
)

project.box(
    BoxType.CAP,
    "ExplorationBitsBox",
    size=(bits_box_width, bits_box_length, bits_box_height),
    lid=LidBuilder(
        text="Exploration Bits",
        label_mode=LabelMode.FRAMED,
        pattern=NAVORIA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkorange"),
    ),
).compartment(
    "Bits",
    size=(bits_inner_w, bits_inner_l),
    position=(0.0, 0.0),
    elements=_bits_box_elements(),
)

# ── 3. Expansion Adventure Cards ──────────────────────────────────
project.box(
    BoxType.SLIDING,
    "ExpansionCardsBox",
    size=(card_box_width, card_box_length, card_box_height),
    lid=LidBuilder(
        text="Forgotten Cards",
        label_mode=LabelMode.FRAMED,
        pattern=NAVORIA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("navy"),
    ),
    expandable=False,
).compartment(
    "Cards",
    cut=FingerCut.SCOOP,
)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
