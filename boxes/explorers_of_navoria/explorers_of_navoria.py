#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Explorers of Navoria board game organizer.

Ports boxes/explorers_of_navoria/explorers_of_navoria.scad to the pyboxbuilder
Project API. Organizes 8 player boxes (4 trading-post boxes + 4 explorer-marker
boxes for Green, Yellow, Purple, Black), favour tiles box, 3 sliding resource
boxes (Swords, Apples, Crystals), adventure card box, and open drawing-bag tray.
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
    else ROOT / "boxes" / "explorers_of_navoria" / "assets"
)

# ── Box & Board Dimensions ────────────────────────────────────────
box_width = 211.0
box_length = 268.0
box_height = 68.0

board_thickness = 12.0
usable_height = box_height - board_thickness  # 56.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

# ── Component Dimensions ──────────────────────────────────────────
card_width = 68.0
card_length = 92.0
player_layout_thickness = 2.0
player_layout_num = 4
num_favour_tiles = 10

# ── Sub-Box Dimensions (matching explorers_of_navoria.scad) ───────
player_box_width = 98.0
player_box_length = (box_length - 2.0) / 2.0  # 133.0mm
player_box_height = usable_height / 4.0  # 14.0mm

favour_box_width = box_width - player_box_width - 1.5  # 111.5mm
favour_box_length = 60.0
favour_box_height = (
    lid_thickness * 2.0 + player_layout_thickness * num_favour_tiles / 2.0 + 0.5
)  # 14.5mm

stuff_box_width = favour_box_width / 3.0  # 37.167mm
stuff_box_length = favour_box_length  # 60.0mm
stuff_box_height = (
    usable_height - favour_box_height - 1.0 - player_layout_thickness * player_layout_num
)  # 32.5mm

card_box_width = box_width - player_box_width - 2.0  # 111.0mm
card_box_length = card_width + wall_thickness * 2.0 + 0.5  # 74.5mm
card_box_height = (
    usable_height - player_layout_thickness - 1.0 - player_layout_thickness * player_layout_num
)  # 45.0mm

bag_box_width = box_width - player_box_width - 2.0  # 111.0mm
bag_box_length = box_length - stuff_box_length - 2.0 - card_box_length  # 131.5mm
bag_box_height = card_box_height  # 45.0mm

project = Project(
    "ExplorersOfNavoria",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

NAVORIA_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── Interior Geometry Helpers (from explorers_of_navoria.scad) ────
player_inner_w = player_box_width - wall_thickness * 2.0   # 92.0mm
player_inner_l = player_box_length - wall_thickness * 2.0  # 127.0mm
player_inner_h = player_box_height - floor_thickness - lid_thickness  # 10.0mm

favour_inner_w = favour_box_width - wall_thickness * 2.0   # 105.5mm
favour_inner_l = favour_box_length - wall_thickness * 2.0  # 54.0mm
favour_inner_h = favour_box_height - floor_thickness - lid_thickness  # 10.5mm

stuff_inner_w = stuff_box_width - wall_thickness * 2.0     # 31.167mm
stuff_inner_l = stuff_box_length - wall_thickness * 2.0    # 54.0mm
stuff_inner_h = stuff_box_height - floor_thickness - lid_thickness  # 28.5mm


def _trading_post_elements(faction_key: str) -> tuple[CompartmentElement, ...]:
    """8 faction-specific trading-post silhouette wells + finger bites + token tray."""
    svg_path = str(ASSETS / f"trading_post_{faction_key}.svg")
    post_w = 17.5 if faction_key in ("yellow", "purple") else 17.0
    post_h = 16.0
    elems: list[CompartmentElement] = []
    # 4 rows x 2 interlocking columns rotated +90 / -90 deg (footprint 16.0 x post_w)
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
                    depth=player_inner_h,
                    pull_out=False,
                    label=f"TradingPost_{row}_{col}",
                )
            )
        # Central finger bite overlapping both trading posts in the row
        bite_d = 20.0
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(bite_d, bite_d),
                offset=(player_inner_w / 2.0 - bite_d / 2.0, cy - bite_d / 2.0),
                depth=player_inner_h,
                pull_out=False,
                label=f"PostBite_{row}",
            )
        )
    # Back rounded tray for remaining player markers
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(84.0, 25.0),
            offset=(4.0, 99.0),
            corner_radius=6.0,
            bottom_rounding=3.0,
            depth=player_inner_h,
            pull_out=False,
            label="MarkerTray",
        )
    )
    return tuple(elems)


def _explorer_elements(faction_key: str) -> tuple[CompartmentElement, ...]:
    """6 faction-specific explorer meeple wells + finger bites + turn-order bird tray."""
    svg_path = str(ASSETS / f"explorer_{faction_key}.svg")
    exp_w = 18.5
    exp_h = 21.5
    elems: list[CompartmentElement] = []
    # 3 rows x 2 interlocking columns rotated +90 / -90 deg (footprint 21.5 x 18.5)
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
                    depth=player_inner_h,
                    pull_out=False,
                    label=f"Explorer_{row}_{col}",
                )
            )
        bite_d = 18.0
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(bite_d, bite_d),
                offset=(player_inner_w / 2.0 - bite_d / 2.0, cy - bite_d / 2.0),
                depth=player_inner_h,
                pull_out=False,
                label=f"ExplorerBite_{row}",
            )
        )
    # Back rounded tray for turn-order bird and player discs
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(84.0, 39.0),
            offset=(4.0, 84.0),
            corner_radius=6.0,
            bottom_rounding=3.0,
            depth=player_inner_h,
            pull_out=False,
            label="BirdAndDiscsTray",
        )
    )
    return tuple(elems)


def _favour_elements() -> tuple[CompartmentElement, ...]:
    """2 notched FavourTile silhouette wells (rotated 270/90 deg) + center finger bites."""
    svg_path = str(ASSETS / "favour_tile.svg")
    tile_w = 54.0
    tile_l = 48.0
    top_dip = 7.0
    bite_d = 22.0  # r = 11.0mm in explorers_of_navoria.scad
    return (
        # Left favour tile (rotated 270 deg -> footprint 48.0 x 54.0)
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=svg_path,
            size=(tile_w, tile_l),
            rotation=270.0,
            offset=(0.0, 0.0),
            depth=favour_inner_h,
            pull_out=False,
            label="FavourTileLeft",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(bite_d, bite_d),
            offset=(tile_l - top_dip - bite_d / 2.0, tile_w / 2.0 - bite_d / 2.0),
            bottom_rounding=4.0,
            depth=favour_inner_h,
            pull_out=False,
            label="FavourBiteLeft",
        ),
        # Right favour tile (rotated 90 deg -> footprint 48.0 x 54.0)
        CompartmentElement(
            shape=ElementShape.SVG,
            shape_file=svg_path,
            size=(tile_w, tile_l),
            rotation=90.0,
            offset=(favour_inner_w - tile_l, 0.0),
            depth=favour_inner_h,
            pull_out=False,
            label="FavourTileRight",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(bite_d, bite_d),
            offset=(favour_inner_w - tile_l + top_dip - bite_d / 2.0, tile_w / 2.0 - bite_d / 2.0),
            bottom_rounding=4.0,
            depth=favour_inner_h,
            pull_out=False,
            label="FavourBiteRight",
        ),
    )


def _stuff_box_elements() -> tuple[CompartmentElement, ...]:
    """Rounded-all-sides resource bin (RoundedBoxAllSides r=10mm in .scad)."""
    return (
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(stuff_inner_w, stuff_inner_l),
            offset=(0.0, 0.0),
            corner_radius=10.0,
            bottom_rounding=10.0,
            depth=stuff_inner_h,
            pull_out=False,
            label="RoundedBin",
        ),
    )


# ── Column 0: 8 Player Boxes (4 Trading Posts + 4 Explorers) ──────
player_factions = [
    ("Green", "forestgreen"),
    ("Yellow", "gold"),
    ("Purple", "purple"),
    ("Black", "black"),
]

for layer_idx, (faction, color_name) in enumerate(player_factions):
    faction_key = faction.lower()
    # Front stack: Trading Posts (PlayerBox*One)
    project.box(
        BoxType.CAP,
        f"PlayerBox_{faction}_One",
        size=(player_box_width, player_box_length, player_box_height),
        position=(0.0, 0.0, player_box_height * layer_idx),
        lid=LidBuilder(
            text=f"{faction} Posts",
            label_mode=LabelMode.FRAMED,
            pattern=NAVORIA_PATTERN,
            text_color=Color("black" if color_name == "gold" else "white"),
            frame_color=Color(color_name),
        ),
    ).compartment(
        "TradingPosts",
        size=(player_inner_w, player_inner_l),
        position=(0.0, 0.0),
        elements=_trading_post_elements(faction_key),
    )

    # Back stack: Explorers & Turn Order Bird (PlayerBox*Two)
    project.box(
        BoxType.CAP,
        f"PlayerBox_{faction}_Two",
        size=(player_box_width, player_box_length, player_box_height),
        position=(0.0, player_box_length, player_box_height * layer_idx),
        lid=LidBuilder(
            text=f"{faction} Explorers",
            label_mode=LabelMode.FRAMED,
            pattern=NAVORIA_PATTERN,
            text_color=Color("black" if color_name == "gold" else "white"),
            frame_color=Color(color_name),
        ),
    ).compartment(
        "Explorers",
        size=(player_inner_w, player_inner_l),
        position=(0.0, 0.0),
        elements=_explorer_elements(faction_key),
    )

# ── Column 1 Front: Favour Box & 3 Stuff Boxes (Y = 0 .. 60) ──────
favour_box = project.box(
    BoxType.CAP,
    "FavourBox",
    size=(favour_box_width, favour_box_length, favour_box_height),
    position=(player_box_width, 0.0, 0.0),
    lid=LidBuilder(
        text="Favours",
        label_mode=LabelMode.FRAMED,
        pattern=NAVORIA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkorange"),
    ),
)
favour_box.compartment(
    "Favours",
    size=(favour_inner_w, favour_inner_l),
    position=(0.0, 0.0),
    elements=_favour_elements(),
)

for idx, (label, text, color_name) in enumerate([
    ("StuffBox_Swords", "Swords", "slategray"),
    ("StuffBox_Apples", "Apples", "crimson"),
    ("StuffBox_Crystals", "Crystals", "deepskyblue"),
]):
    project.box(
        BoxType.SLIDING,
        label,
        size=(stuff_box_width, stuff_box_length, stuff_box_height),
        position=(player_box_width + stuff_box_width * idx, 0.0, favour_box_height),
        lid=LidBuilder(
            text=text,
            label_mode=LabelMode.FRAMED,
            pattern=NAVORIA_PATTERN,
            text_color=Color("white"),
            frame_color=Color(color_name),
        ),
    ).compartment(
        "Tokens",
        size=(stuff_inner_w, stuff_inner_l),
        position=(0.0, 0.0),
        elements=_stuff_box_elements(),
    )

# ── Column 1 Middle: Adventure Cards Box (Y = 60 .. 134.5) ────────
project.box(
    BoxType.SLIDING,
    "CardBox",
    size=(card_box_width, card_box_length, card_box_height),
    position=(player_box_width, favour_box_length, 0.0),
    lid=LidBuilder(
        text="Cards",
        label_mode=LabelMode.FRAMED,
        pattern=NAVORIA_PATTERN,
        text_color=Color("white"),
        frame_color=Color("navy"),
    ),
).compartment("AdventureCards", cut=FingerCut.SCOOP)

# ── Column 1 Back: Open Drawing Bag Tray (Y = 134.5 .. 266) ───────
project.box(
    BoxType.NO_LID,
    "BagBox",
    size=(bag_box_width, bag_box_length, bag_box_height),
    position=(player_box_width, favour_box_length + card_box_length, 0.0),
).compartment("BagAndBits", cut=FingerCut.SCOOP)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
