#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Railroad Tiles board game organizer.

Ports examples/railroad_tiles.scad to the pyboxbuilder Project API.
Organizes square railroad track tiles, objective tiles, player markers,
and starting clock tiles with automated spacers.
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
    else ROOT / "boxes" / "railroad_tiles" / "assets"
)

# ── Box & Board Dimensions ────────────────────────────────────────
box_width = 230.0
box_length = 230.0
box_height = 63.0

board_thickness = 2.5
usable_height = box_height - board_thickness  # 60.5mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

railroad_tile = 46.0
clock_diameter = 32.0

player_box_width = (box_width - 2.0) / 2.0            # 114.0mm
player_box_length = clock_diameter + wall_thickness * 2.0  # 38.0mm
player_box_height = 12.0

token_box_width = (box_width - 2.0) / 4.0             # 57.0mm
token_box_length = player_box_length                  # 38.0mm
token_box_height = (usable_height - player_box_height) / 2.0  # 24.25mm

objective_box_width = player_box_width                # 114.0mm
objective_box_length = wall_thickness * 2.0 + railroad_tile  # 52.0mm
objective_box_height = usable_height / 5.0            # 12.1mm

project = Project(
    "RailroadTiles",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
    box_defaults={"expandable": False},
)

TILE_PATTERN = PatternBuilder(PatternType.DENSE_HEX)

# ── 1. Tokens Boxes (4 columns, stacked 2 high at Y = 0) ──────────
token_labels = ["Tokens_1", "Tokens_2", "Tokens_3", "Tokens_4"]
for label in token_labels:
    for tier in range(2):
        t_box = project.box(
            BoxType.CAP,
            f"{label}_Tier{tier + 1}",
            size=(token_box_width, token_box_length, token_box_height),
            lid=LidBuilder(
                text=label,
                label_mode=LabelMode.FRAMED,
                pattern=TILE_PATTERN,
                text_color=Color("white"),
                frame_color=Color("navy"),
            ),
        )
        t_box.compartment(
            "Tokens",
            cut=FingerCut.SCOOP,
        )

# ── 2. Player & Starting Marker Boxes ─────────────────────────────
player_inner_width = player_box_width - wall_thickness * 2.0  # 108.0mm
player_inner_length = player_box_length - wall_thickness * 2.0  # 32.0mm

cardboard_thickness = 1.5
railroad_tile_two_player = 29.0
player_marker_width = 13.0
player_marker_total_height = 21.25
player_marker_thickness = 7.0


def _player_markers_elements() -> tuple[CompartmentElement, ...]:
    """Build 4 conductor SVG marker wells + 2-player tile well with finger bites."""
    elems: list[CompartmentElement] = []
    marker_svg = str(ASSETS / "player_marker.svg")
    marker_depth = player_marker_thickness + 1.0  # 8.0mm
    cy = player_inner_length / 2.0  # 16.0mm

    # 4 player conductor markers
    for i in range(4):
        cx = player_marker_width / 2.0 + (player_marker_width + 2.0) * i
        elems.append(
            CompartmentElement(
                shape=ElementShape.SVG,
                shape_file=marker_svg,
                size=(player_marker_width, player_marker_total_height),
                offset=(cx - player_marker_width / 2.0, cy - player_marker_total_height / 2.0),
                depth=marker_depth,
                pull_out=False,
                label=f"PlayerMarker_{i + 1}",
            )
        )
        # Subtle top finger notch for lifting marker
        notch_d = 8.0
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(notch_d, notch_d),
                offset=(cx - notch_d / 2.0, cy - player_marker_total_height / 2.0 - notch_d / 2.0),
                depth=marker_depth / 2.0,
                bottom_rounding=1.5,
                pull_out=False,
                label=f"PlayerMarkerNotch_{i + 1}",
            )
        )

    # 2-player square tile well (29x29mm, depth 2.5mm) + left/right finger bites
    tile_cx = player_inner_width - player_box_height - 10.0  # 86.0mm
    tile_depth = cardboard_thickness + 1.0  # 2.5mm
    elems.append(
        CompartmentElement(
            shape=ElementShape.ROUNDED_RECT,
            size=(railroad_tile_two_player, railroad_tile_two_player),
            offset=(tile_cx - railroad_tile_two_player / 2.0, cy - railroad_tile_two_player / 2.0),
            depth=tile_depth,
            corner_radius=1.0,
            pull_out=False,
            label="TwoPlayerTile",
        )
    )
    bite_d = 14.0
    for idx, sign in enumerate((-1.0, 1.0), start=1):
        bite_cx = tile_cx + sign * (railroad_tile_two_player / 2.0)
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(bite_d, bite_d),
                offset=(bite_cx - bite_d / 2.0, cy - bite_d / 2.0),
                depth=tile_depth,
                bottom_rounding=1.0,
                pull_out=False,
                label=f"TwoPlayerTileBite_{idx}",
            )
        )

    return tuple(elems)


def _starting_clocks_elements() -> tuple[CompartmentElement, ...]:
    """Build 3 circular clock tile wells with stepped depths and 0/180-deg finger bites."""
    elems: list[CompartmentElement] = []
    cy = player_inner_length / 2.0  # 16.0mm
    bite_d = 14.0
    bite_r = bite_d / 2.0

    for i in range(3):
        cx = player_inner_width - clock_diameter / 2.0 - (clock_diameter + 2.0) * i - 4.0
        depth = cardboard_thickness * (3 if i == 0 else 2) + 1.0  # 5.5mm, 4.0mm, 4.0mm
        elems.append(
            CompartmentElement(
                shape=ElementShape.CIRCLE,
                size=(clock_diameter, clock_diameter),
                offset=(cx - clock_diameter / 2.0, cy - clock_diameter / 2.0),
                depth=depth,
                pull_out=False,
                label=f"ClockWell_{i + 1}",
            )
        )
        for side_idx, sign in enumerate((-1.0, 1.0), start=1):
            raw_bite_cx = cx + sign * (clock_diameter / 2.0)
            clamped_bite_cx = max(bite_r, min(player_inner_width - bite_r, raw_bite_cx))
            elems.append(
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(bite_d, bite_d),
                    offset=(clamped_bite_cx - bite_r, cy - bite_r),
                    depth=depth,
                    pull_out=False,
                    label=f"ClockBite_{i + 1}_{side_idx}",
                )
            )

    return tuple(elems)


project.box(
    BoxType.CAP,
    "PlayerMarkersBox",
    size=(player_box_width, player_box_length, player_box_height),
    lid=LidBuilder(
        text="Player Markers",
        label_mode=LabelMode.FRAMED,
        pattern=TILE_PATTERN,
        text_color=Color("white"),
        frame_color=Color("darkgreen"),
    ),
).compartment(
    "Markers",
    size=(player_inner_width, player_inner_length),
    position=(0.0, 0.0),
    elements=_player_markers_elements(),
)

project.box(
    BoxType.CAP,
    "StartingClocksBox",
    size=(player_box_width, player_box_length, player_box_height),
    lid=LidBuilder(
        text="Clocks",
        label_mode=LabelMode.FRAMED,
        pattern=TILE_PATTERN,
        text_color=Color("white"),
        frame_color=Color("gold"),
    ),
).compartment(
    "Clocks",
    size=(player_inner_width, player_inner_length),
    position=(0.0, 0.0),
    elements=_starting_clocks_elements(),
)

# ── 3. Objective Tile Boxes (5 trays) ─────────────────────────────
for i in range(5):
    obj_box = project.box(
        BoxType.CAP,
        f"ObjectiveBox_{i + 1}",
        size=(objective_box_width, objective_box_length, objective_box_height),
        lid=LidBuilder(
            text=f"Objectives {i + 1}",
            label_mode=LabelMode.FRAMED,
            pattern=TILE_PATTERN,
            text_color=Color("white"),
            frame_color=Color("darkorange"),
        ),
    )
    obj_box.compartment(
        "ObjectiveTiles_Left",
        width_ratio=0.5,
        cut=FingerCut.SCOOP,
    )
    obj_box.compartment(
        "ObjectiveTiles_Right",
        width_ratio=0.5,
        cut=FingerCut.SCOOP,
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
