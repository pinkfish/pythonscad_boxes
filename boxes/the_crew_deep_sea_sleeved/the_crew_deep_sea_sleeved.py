# SPDX-License-Identifier: Apache-2.0
"""The Crew: Mission Deep Sea — box insert for sleeved cards.

A variant of :file:`boxes/the_crew_deep_sea/the_crew_deep_sea.py` for sleeved
cards. The large cards take Gamegenic "Standard American" sleeves (59 x 91 mm)
and the small cards Gamegenic "Mini European" sleeves (46 x 71 mm); both are
100-micron Prime/Matte, sized at 0.32 mm per sleeved card. The 96 sleeved small
cards are a 31 mm stack, too tall for one box, so they split into two 48-card
stacks.

The deck stands full height in its own corner; the two task boxes sit beside it
with the accessory box stacked on top — the same arrangement as the unsleeved
variant, with bigger card wells for the sleeves. The sonar tokens stack in two
deep wells, as the unsleeved variant does.

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
    FingerCut,
    LabelMode,
    LidBuilder,
    PatternBuilder,
    PatternType,
    Project,
    columns,
    find_sleeve,
    run,
    stack,
)
from pyboxbuilder.compartments import CompartmentElement

#: The pieces are the same drawings as the unsleeved variant, so share its art.
SVG = str(REPO_ROOT / "boxes" / "the_crew_deep_sea" / "svg")

# ── Game box — the retail box's inside dimensions ───────────────────────────
BOX_WIDTH = 172.0
BOX_LENGTH = 122.0
BOX_HEIGHT = 36.0

# ── Material defaults ───────────────────────────────────────────────────────
WALL = 2.0
FLOOR = 1.6
LID = 2.0

# ── Cards — sleeved in Gamegenic Prime sleeves ───────────────────────────────
CARD_SLACK = 1.0
"""Extra clearance around a sleeve, so the deck still slips in and out."""

LARGE_CARD = (56.0, 88.0)
"""The 40 playing cards and the 5 same-sized reminder cards."""
LARGE_COUNT = 40 + 5

SMALL_CARD = (44.0, 68.0)
"""The 96 small task cards."""
SMALL_COUNT = 96

# The Gamegenic sleeves from the catalog. "Standard American" takes a 57x89 card
# in a 59x91 sleeve; "Mini European" a 44x69 card in a 46x71 sleeve. Both are
# 100-micron Prime/Matte.
LARGE_SLEEVE = find_sleeve("Gamegenic", "Standard American")
SMALL_SLEEVE = find_sleeve("Gamegenic", "Mini European")

# Gamegenic's own 100-micron rating would model a sleeved card at 0.40 mm; this
# insert sizes depth with the library's 0.32 mm premium value instead.
CARD_THICKNESS = 0.32

CARD_BOX_HEIGHT = (
    SMALL_COUNT // 2 * CARD_THICKNESS + CARD_SLACK + FLOOR + LID
)
"""Tall enough for the thickest stack: 48 sleeved small cards are 15.4 mm, plus
slack, floor and lid."""

# The deck box is as wide as its sleeve; the two task boxes widen to take up
# whatever the deck leaves, so no spacer is left along the width.
DECK_BOX_WIDTH = LARGE_SLEEVE.sleeve_size[0] + CARD_SLACK + 2 * WALL
TASK_BOX_WIDTH = (BOX_WIDTH - DECK_BOX_WIDTH) / 2

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
ACCESSORY_WIDTH = BOX_WIDTH - DECK_BOX_WIDTH   # 108.0 — the column beside the deck
ACCESSORY_LENGTH = BOX_LENGTH - 4.0            # 118.0
ACCESSORY_HEIGHT = 11.0
ACCESSORY_INNER_W = ACCESSORY_WIDTH - 2 * WALL
ACCESSORY_INNER_L = ACCESSORY_LENGTH - 2 * WALL
ACCESSORY_INNER_H = ACCESSORY_HEIGHT - FLOOR - LID   # 7.4 — the lid sits above the pieces

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


# ── Card boxes — full-height wells, sized for the sleeved deck ──────────────
def sleeved_card_box(
    label: str,
    sleeve,
    *,
    box_width: float | None = None,
    box_height: float = CARD_BOX_HEIGHT,
) -> None:
    """Add a sliding card box whose well fits a deck in ``sleeve``.

    ``box_width`` overrides the width derived from the sleeve, so a box can be
    widened to fill the game box; ``box_height`` overrides the height, so the
    deck can run the full height of the box.
    """
    well_w = sleeve.sleeve_size[0] + CARD_SLACK if box_width is None else box_width - 2 * WALL
    well_l = sleeve.sleeve_size[1] + CARD_SLACK
    box = project.box(
        BoxType.SLIDING,
        label,
        size=(well_w + 2 * WALL, well_l + 2 * WALL, box_height),
        lid=CREW_LID.titled(label),
    )
    box.compartment(
        label,
        size=(well_w, well_l),
        depth=None,  # the well runs the full height of the box
        cut=FingerCut.THROUGH_FLOOR,
    )


sleeved_card_box("Deck", LARGE_SLEEVE, box_height=BOX_HEIGHT)
for i in range(2):
    sleeved_card_box(f"Tasks{i + 1}", SMALL_SLEEVE, box_width=TASK_BOX_WIDTH)

# ── Accessory box — diver, base, tokens, lidded like the unsleeved variant ───
accessories = project.box(
    BoxType.SLIDING,
    "Accessories",
    size=(ACCESSORY_WIDTH, ACCESSORY_LENGTH, ACCESSORY_HEIGHT),
    lid=CREW_LID.titled("Captain"),
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


def stack_depth(count: int, thickness: float) -> float:
    """How deep a well must be to hold `count` stacked pieces plus the top slack."""
    return count * thickness + TOP_SLACK


DIVER_SLOT = pocket(stack_depth(1, DIVER_THICKNESS))   # 3.0 — one standee piece
SLOT = pocket(stack_depth(1, TOKEN_THICKNESS))         # 2.55 — one flat token
SONAR_THREE = pocket(stack_depth(3, TOKEN_THICKNESS))  # 6.65 — three stacked sonar
SONAR_TWO = pocket(stack_depth(2, TOKEN_THICKNESS))    # 4.6 — two stacked sonar

SONAR_WELL = SONAR_DIAMETER + 0.5
DISTRESS_WELL = (DISTRESS[0], DISTRESS[1])


def icon_pocket(well: dict) -> dict:
    return {"depth": ICON_DEPTH, "z_offset": well["z_offset"] - ICON_DEPTH + ICON_LIFT}


def accessory_elements() -> tuple[CompartmentElement, ...]:
    elements: list[CompartmentElement] = []

    # Diver on the left, base tucked beneath it — both aligned to the left edge.
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

    # The five sonar tokens stack in two wells in the strip to the right of the
    # diver — three above and two below the rotated distress token.
    elements.append(
        centered(
            None,
            (79.0, 15.0),
            (SONAR_WELL, SONAR_WELL),
            shape=ElementShape.CIRCLE,
            label="sonar_3",
            **SONAR_THREE,
        )
    )
    elements.append(
        centered(
            None,
            (79.0, 47.0),
            (SONAR_WELL, SONAR_WELL),
            shape=ElementShape.CIRCLE,
            label="sonar_2",
            **SONAR_TWO,
        )
    )
    elements.append(
        centered(
            None,
            (78.5, 86.0),
            DISTRESS_WELL,
            shape=ElementShape.ROUNDED_RECT,
            corner_radius=DISTRESS_WELL[1] / 2 - 1.0,
            rotation=90.0,
            label="distress",
            **SLOT,
        )
    )

    # Each well carries its icon pressed into the bottom as a second colour.
    elements.append(
        centered(
            f"{SVG}/the crew - sonar.svg",
            (79.0, 15.0),
            (SONAR_ICON_W, SONAR_ICON_L),
            shape=ElementShape.SVG,
            rotation=90.0,
            label="sonar_icon_3",
            color="green",
            **icon_pocket(SONAR_THREE),
        )
    )
    elements.append(
        centered(
            f"{SVG}/the crew - sonar.svg",
            (79.0, 47.0),
            (SONAR_ICON_W, SONAR_ICON_L),
            shape=ElementShape.SVG,
            rotation=90.0,
            label="sonar_icon_2",
            color="green",
            **icon_pocket(SONAR_TWO),
        )
    )
    elements.append(
        centered(
            f"{SVG}/the crew - distress.svg",
            (78.5, 86.0),
            (DISTRESS_ICON_W, DISTRESS_ICON_L),
            shape=ElementShape.SVG,
            rotation=90.0,
            label="distress_icon",
            color="blue",
            **icon_pocket(SLOT),
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
