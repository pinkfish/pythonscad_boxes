# SPDX-License-Identifier: Apache-2.0
"""The Crew: Mission Deep Sea — box insert for sleeved cards.

A variant of :file:`boxes/the_crew_deep_sea/the_crew_deep_sea.py` for sleeved
cards. A 100-micron premium sleeve adds 3.5 mm around every card and thickens
each one to 0.32 mm, so the card boxes grow in both footprint and height — the
96 sleeved small cards are a 31 mm stack, too tall for one box, so they still
split into two 48-card stacks, and the deck plus those two boxes fill the whole
footprint.

That leaves no room to stack the accessory tray beside a full-height deck, so
this variant returns to the two-layer layout: the three card boxes on the
bottom, the accessory tray across the full box on top. The sonar tokens lie flat
in a row rather than stacked in a deep well, and the tray is an open lidless
tray — together those keep it a shallow 5 mm, which is what leaves 20 mm for
the card boxes and still fits the same 26 mm.

The game's pieces are unchanged, so the diver, base, sonar and distress art is
shared with the unsleeved variant.
"""

import sys
from pathlib import Path

# Repo root on sys.path, robust to __file__ being undefined (Jupyter / exec).
REPO_ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd()
sys.path.insert(0, str(REPO_ROOT))
# Venv site-packages (any Python version) so compiled extensions like shapely
# and pybosl2 load inside the PythonSCAD UI's embedded Python.
for _sp in REPO_ROOT.glob(".venv/lib/*/site-packages"):
    sys.path.insert(0, str(_sp))
for _sp in REPO_ROOT.glob("venv/*/lib/*/site-packages"):
    sys.path.insert(0, str(_sp))

from pyboxbuilder import (
    BoxType,
    ElementShape,
    LabelMode,
    LidBuilder,
    PatternBuilder,
    PatternType,
    Project,
    SleeveType,
    columns,
    run,
    stack,
)
from pyboxbuilder.compartments import CompartmentElement

#: The pieces are the same drawings as the unsleeved variant, so share its art.
SVG = str(REPO_ROOT / "boxes" / "the_crew_deep_sea" / "svg")

# ── Game box — the retail box's inside dimensions ───────────────────────────
BOX_WIDTH = 172.0
BOX_LENGTH = 122.0
BOX_HEIGHT = 26.0

# ── Material defaults ───────────────────────────────────────────────────────
WALL = 2.0
FLOOR = 1.6
LID = 2.0

# ── Cards — sleeved ─────────────────────────────────────────────────────────
SLEEVE = SleeveType.PREMIUM_100MY
"""A 100-micron premium sleeve: 0.32 mm per sleeved card, 3.5 mm around the edge.

The thinnest sleeve (STANDARD_60MY, 0.26 mm) understates a real sleeved card —
a board game card is ~0.3 mm before the sleeve — so this uses the premium value,
which is the thickest a single sleeve reaches while the 96 small cards still
split into two 48-card stacks that fit the box."""

CARD_SLACK = 1.0
"""Extra clearance beyond the sleeve, so the deck still slips in and out."""

LARGE_CARD = (56.0, 88.0)
"""The 40 playing cards and the 5 same-sized reminder cards."""
LARGE_COUNT = 40 + 5

SMALL_CARD = (44.0, 68.0)
"""The 96 small task cards."""
SMALL_COUNT = 96

CARD_BOX_HEIGHT = 20.0
"""Tall enough for the thickest stack: 48 sleeved cards are 15.4 mm, plus slack
for a fingertip, inside a 16.4 mm interior."""

# ── Tokens ──────────────────────────────────────────────────────────────────
SONAR_DIAMETER = 29.5
SONAR_COUNT = 5
DISTRESS = (44.0, 29.0)  # (length, width) of the oval distress token

TOKEN_THICKNESS = 2.05
"""The sonar and distress tokens are 2.05 mm thick."""

DIVER_THICKNESS = 2.5
"""The diver standee and its base are 2.5 mm thick."""

TOP_SLACK = 0.5
"""Extra depth on top of a piece, so a fingertip can get under its edge."""

# ── First-player standee, scaled from the source drawings ───────────────────
DIVER_VIEWBOX = (176.013, 240.880)
DIVER_HEIGHT = 86.0
DIVER_WIDTH = DIVER_VIEWBOX[0] * DIVER_HEIGHT / DIVER_VIEWBOX[1]

BASE_VIEWBOX = (161.530, 60.160)
BASE_WIDTH = 58.0
BASE_HEIGHT = BASE_VIEWBOX[1] * BASE_WIDTH / BASE_VIEWBOX[0]

# ── Token icons, scaled from the game's own art ─────────────────────────────
SONAR_VIEWBOX = (110.359, 95.127)
SONAR_ICON_W = 24.0
SONAR_ICON_L = SONAR_ICON_W * SONAR_VIEWBOX[1] / SONAR_VIEWBOX[0]

DISTRESS_VIEWBOX = (81.630, 164.802)
DISTRESS_ICON_W = 16.0
DISTRESS_ICON_L = DISTRESS_ICON_W * DISTRESS_VIEWBOX[1] / DISTRESS_VIEWBOX[0]

# ── Accessory tray ──────────────────────────────────────────────────────────
ACCESSORY_WIDTH = BOX_WIDTH - 4.0    # 168.0
ACCESSORY_LENGTH = BOX_LENGTH - 4.0   # 118.0
ACCESSORY_HEIGHT = 5.0
ACCESSORY_INNER_W = ACCESSORY_WIDTH - 2 * WALL
ACCESSORY_INNER_L = ACCESSORY_LENGTH - 2 * WALL
ACCESSORY_INNER_H = ACCESSORY_HEIGHT - FLOOR   # 3.4 — the pieces lie flat

ICON_DEPTH = 0.2
ICON_LIFT = 0.001

# ── Project ─────────────────────────────────────────────────────────────────
project = Project(
    "TheCrewDeepSeaSleeved",
    game_box_size=(BOX_WIDTH, BOX_LENGTH, BOX_HEIGHT),
    wall_thickness=WALL,
    floor_thickness=FLOOR,
    lid_thickness=LID,
    generate_spacers=True,
)

BUBBLES = PatternBuilder(type=PatternType.VORONOI)
CREW_LID = LidBuilder(label_mode=LabelMode.FRAMELESS, diagonal=True, pattern=BUBBLES)


# ── Card boxes — full-height wells, sized for sleeved cards ─────────────────
def sleeved_card_box(label: str, card_size: tuple[float, float]) -> None:
    """Add a sliding card box whose well is sized for a sleeved deck."""
    margin = SLEEVE.footprint_margin + CARD_SLACK
    box = project.box(
        BoxType.SLIDING,
        label,
        size=(
            card_size[0] + margin + 2 * WALL,
            card_size[1] + margin + 2 * WALL,
            CARD_BOX_HEIGHT,
        ),
        lid=CREW_LID.titled(label),
    )
    box.cards(
        label,
        count=None,  # the well runs the full height of the box
        size=card_size,
        thickness=SLEEVE.card_thickness,
        slack=margin,
    )


sleeved_card_box("Deck", LARGE_CARD)
for i in range(2):
    sleeved_card_box(f"Tasks{i + 1}", SMALL_CARD)

# ── Accessory tray — diver, base, tokens, all flat, lidless ─────────────────
accessories = project.box(
    BoxType.NO_LID,
    "Accessories",
    size=(ACCESSORY_WIDTH, ACCESSORY_LENGTH, ACCESSORY_HEIGHT),
)

OVERSHOOT = 0.5


def pocket(depth_from_top: float) -> dict:
    z = max(0.0, ACCESSORY_INNER_H - depth_from_top)
    return {"z_offset": z, "depth": ACCESSORY_INNER_H - z + OVERSHOOT}


def centered(
    shape_file: str | None,
    center: tuple[float, float],
    size: tuple[float, float],
    *,
    shape: ElementShape = ElementShape.SVG,
    rotation: float = 0.0,
    label: str | None = None,
    corner_radius: float = 2.0,
    **pocket_kwargs,
) -> CompartmentElement:
    proto = CompartmentElement(
        shape_file=shape_file,
        offset=(0.0, 0.0),
        size=size,
        shape=shape,
        rotation=rotation,
        label=label,
        corner_radius=corner_radius,
        **pocket_kwargs,
    )
    fw, fl = proto.footprint
    return CompartmentElement(
        shape_file=shape_file,
        offset=(center[0] - fw / 2, center[1] - fl / 2),
        size=size,
        shape=shape,
        rotation=rotation,
        label=label,
        corner_radius=corner_radius,
        **pocket_kwargs,
    )


DIVER_SLOT = pocket(DIVER_THICKNESS + TOP_SLACK)      # 3.0 — the standee lies flat
SONAR_SLOT = pocket(TOKEN_THICKNESS + TOP_SLACK)      # 2.55 — a flat token
DISTRESS_SLOT = pocket(TOKEN_THICKNESS + TOP_SLACK)   # 2.55 — a flat token

SONAR_WELL = SONAR_DIAMETER + 0.5
DISTRESS_WELL = (DISTRESS[0] + 1.0, DISTRESS[1] + 1.0)


def icon_pocket(well: dict) -> dict:
    return {"depth": ICON_DEPTH, "z_offset": well["z_offset"] - ICON_DEPTH + ICON_LIFT}


def accessory_elements() -> tuple[CompartmentElement, ...]:
    elements: list[CompartmentElement] = []

    # Diver on the left, base tucked beneath it.
    elements.append(
        centered(
            f"{SVG}/the crew - diver.svg",
            (DIVER_WIDTH / 2, DIVER_HEIGHT / 2),
            (DIVER_WIDTH, DIVER_HEIGHT),
            label="diver",
            **DIVER_SLOT,
        )
    )
    elements.append(
        centered(
            f"{SVG}/the crew - base.svg",
            (BASE_WIDTH / 2, DIVER_HEIGHT + 3.0 + BASE_HEIGHT / 2),
            (BASE_WIDTH, BASE_HEIGHT),
            label="base",
            **DIVER_SLOT,
        )
    )

    # The sonar tokens lie flat — three across the top of the right half, two
    # beneath — so the tray stays shallow instead of needing a deep stack well.
    sonar_centres = (
        (81.0, 15.0), (113.0, 15.0), (145.0, 15.0),
        (81.0, 47.0), (113.0, 47.0),
    )
    for i, (x, y) in enumerate(sonar_centres):
        elements.append(
            centered(
                None,
                (x, y),
                (SONAR_WELL, SONAR_WELL),
                shape=ElementShape.CIRCLE,
                label=f"sonar_{i}",
                **SONAR_SLOT,
            )
        )
        elements.append(
            centered(
                f"{SVG}/the crew - sonar.svg",
                (x, y),
                (SONAR_ICON_W, SONAR_ICON_L),
                shape=ElementShape.SVG,
                rotation=90.0,
                label=f"sonar_icon_{i}",
                color="green",
                **icon_pocket(SONAR_SLOT),
            )
        )

    # The distress token and its blue tower icon, below the sonar rows.
    elements.append(
        centered(
            None,
            (88.0, 78.5),
            DISTRESS_WELL,
            shape=ElementShape.ROUNDED_RECT,
            corner_radius=DISTRESS_WELL[1] / 2 - 1.0,
            label="distress",
            **DISTRESS_SLOT,
        )
    )
    elements.append(
        centered(
            f"{SVG}/the crew - distress.svg",
            (88.0, 78.5),
            (DISTRESS_ICON_W, DISTRESS_ICON_L),
            shape=ElementShape.SVG,
            rotation=90.0,
            label="distress_icon",
            color="blue",
            **icon_pocket(DISTRESS_SLOT),
        )
    )

    return tuple(elements)


accessories.compartment(
    "Contents",
    size=(ACCESSORY_INNER_W, ACCESSORY_INNER_L),
    depth=ACCESSORY_INNER_H,
    position=(0.0, 0.0),
    elements=accessory_elements(),
)

# ── Arrangement ─────────────────────────────────────────────────────────────
# Sleeved cards fill the whole footprint, so the accessory tray sits on top of
# the three card boxes: lift the tray out and the cards are underneath.
project.arrange(
    stack(
        columns("Deck", columns("Tasks1", "Tasks2")),
        "Accessories",
    )
)

if __name__ == "__main__":
    run(project)
