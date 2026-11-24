#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pioneer Rails board game organizer.

Ports examples/pioneer_rails.scad to the pyboxbuilder Project API.
Organizes card decks (Goals, Playing, Forest, Company Owner), pencils,
erasers, and the poker chip dealer token with automated spacers.
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
    else ROOT / "boxes" / "pioneer_rails" / "assets"
)

# ── Box & Board Dimensions ────────────────────────────────────────
box_width = 209.0
box_length = 209.0
box_height = 38.0

board_thickness = 16.0  # Player pad of score sheets
usable_height = box_height - board_thickness  # 22.0mm

wall_thickness = 3.0
floor_thickness = 2.0
lid_thickness = 2.0

card_width = 66.5
card_length = 90.0

pencil_width = 8.0
pencil_length = 90.0
eraser_width = 20.0
eraser_length = 40.0
eraser_thickness = 10.0
dealer_token_diameter = 41.0
token_thickness = 3.0

card_box_width = usable_height                        # 22.0mm (cards stored on edge)
card_box_length = card_length + wall_thickness * 2.0  # 96.0mm
card_box_height = usable_height                       # 22.0mm

pencil_box_length = pencil_length + eraser_width + wall_thickness * 3.0 + 1.0  # 120.0mm
pencil_box_width = 60.0
pencil_box_height = usable_height

pencil_inner_width = pencil_box_width - wall_thickness * 2.0    # 54.0mm
pencil_inner_length = pencil_box_length - wall_thickness * 2.0  # 114.0mm

project = Project(
    "PioneerRails",
    game_box_size=(box_width, box_length, box_height),
    wall_thickness=wall_thickness,
    floor_thickness=floor_thickness,
    lid_thickness=lid_thickness,
    clearance_slack=0.0,
    board_thickness=board_thickness,
    generate_spacers=True,
)

# ── Game Piece Inventory ──────────────────────────────────────────
project.define_inventory({
    "Pencils": 4,
    "Eraser": 1,
    "Dealer Token": 1,
    "Goal Cards": 18,
    "Playing Cards": 54,
    "Forest Cards": 12,
    "Company Owner Cards": 6,
    "Map Score Pad": 1,
    "Rulebook": 1,
})

project.board(
    "Score Pad & Rulebook",
    size=(box_width, box_length, board_thickness),
    position=(0.0, 0.0, usable_height),
    count=2,
    notes="Player map score sheet pad and rulebook sit atop insert",
    allocates={
        "Map Score Pad": 1,
        "Rulebook": 1,
    },
)

PIONEER_PATTERN = PatternBuilder(PatternType.CHEVRON)
PIONEER_FONT = "Georgia:style=Bold"


def _pencil_box_elements() -> tuple[CompartmentElement, ...]:
    """Stepped pencil trough, dealer token circle with finger bites, and eraser well."""
    pencil_trough_w = pencil_width * 4.0  # 32.0mm
    pencil_depth = pencil_width + 1.0 + token_thickness  # 12.0mm
    eraser_depth = eraser_thickness + 1.0  # 11.0mm
    token_depth = token_thickness + 0.5  # 3.5mm
    bite_diameter = 12.0

    cx = pencil_inner_width / 2.0
    pencil_cy = pencil_length / 2.0
    eraser_cy = pencil_inner_length - eraser_width / 2.0

    return (
        # Longitudinal pencil trough (4 pencils side-by-side)
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(pencil_trough_w, pencil_length),
            offset=(cx - pencil_trough_w / 2.0, 0.0),
            depth=pencil_depth,
            pull_out=False,
            label="PencilTrough",
        ),
        # Shallow circular dealer token recess centered above the pencil trough
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(dealer_token_diameter, dealer_token_diameter),
            offset=(cx - dealer_token_diameter / 2.0, pencil_cy - dealer_token_diameter / 2.0),
            depth=token_depth,
            pull_out=False,
            label="DealerToken",
        ),
        # Opposing finger bites at 0° (+X) and 180° (-X) on the dealer token rim
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(bite_diameter, bite_diameter),
            offset=(cx + dealer_token_diameter / 2.0 - bite_diameter / 2.0, pencil_cy - bite_diameter / 2.0),
            depth=token_depth,
            pull_out=False,
            label="DealerTokenBite_Right",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(bite_diameter, bite_diameter),
            offset=(cx - dealer_token_diameter / 2.0 - bite_diameter / 2.0, pencil_cy - bite_diameter / 2.0),
            depth=token_depth,
            pull_out=False,
            label="DealerTokenBite_Left",
        ),
        # Eraser pocket at the far end with a +X finger bite (CuboidWithIndentsBottom finger_holes=[0])
        CompartmentElement(
            shape=ElementShape.RECT,
            size=(eraser_length, eraser_width),
            offset=(cx - eraser_length / 2.0, eraser_cy - eraser_width / 2.0),
            depth=eraser_depth,
            pull_out=False,
            label="EraserWell",
        ),
        CompartmentElement(
            shape=ElementShape.CIRCLE,
            size=(bite_diameter, bite_diameter),
            offset=(cx + eraser_length / 2.0 - bite_diameter / 2.0, eraser_cy - bite_diameter / 2.0),
            depth=eraser_depth,
            pull_out=False,
            label="EraserBite",
        ),
    )


# ── 1. Pencil & Accessory Box ─────────────────────────────────────
p_box = project.box(
    BoxType.CAP,
    "PencilBox",
    size=(pencil_box_width, pencil_box_length, pencil_box_height),
    lid=LidBuilder(
        text="Pencils",
        label_mode=LabelMode.FRAMED,
        label_shape=LabelShape.BRACKET,
        label_finial=LabelFinial.SPEAR,
        font=PIONEER_FONT,
        logo=str(ASSETS / "pencil.svg"),
        logo_color=Color("white"),
        logo_position="left",
        label_logo_size_mm=16.0,
        pattern=PIONEER_PATTERN,
        text_color=Color("white"),
        frame_color=Color("peru"),
    ),
)
p_box.compartment(
    "PencilsAndErasers",
    size=(pencil_inner_width, pencil_inner_length),
    position=(0.0, 0.0),
    allocates={
        "Pencils": 4,
        "Eraser": 1,
        "Dealer Token": 1,
    },
    elements=_pencil_box_elements(),
)

# ── 2. Card Decks (4 boxes side-by-side) ──────────────────────────
decks = [
    ("GoalCards", "Goal", "darkorange", "Goal Cards", 18),
    ("PlayingCards", "Playing", "navy", "Playing Cards", 54),
    ("ForestCards", "Forest", "forestgreen", "Forest Cards", 12),
    ("CompanyCards", "Company", "gold", "Company Owner Cards", 6),
]

for deck_id, title, color_name, comp_name, card_qty in decks:
    c_box = project.box(
        BoxType.SLIDING,
        f"CardBox_{deck_id}",
        size=(card_box_width, card_box_length, card_box_height),
        lid=LidBuilder(
            text=title,
            label_mode=LabelMode.FRAMELESS,
            label_shape=LabelShape.BRACKET,
            label_finial=LabelFinial.NONE,
            font=PIONEER_FONT,
            pattern=PIONEER_PATTERN,
            text_color=Color("white"),
            frame_color=Color(color_name),
        ),
        expandable=False,
    )
    c_box.compartment(
        "Cards",
        cut=FingerCut.SCOOP,
        component=comp_name,
        count=card_qty,
    )

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
