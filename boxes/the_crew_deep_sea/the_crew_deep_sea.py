# SPDX-License-Identifier: Apache-2.0
"""The Crew: Mission Deep Sea — box insert.

A two-layer insert for the shallow card-game box. The main card box (the 45
large playing and reminder cards) is the full height of the box, so it fills a
whole corner by itself. Beside it, the 96 small task cards sit in two sliding
boxes split into 48-card stacks, and the lidded accessory box — the 86 mm-tall
diver standee, its 58 mm-wide base, the five sonar tokens and the distress
token — sits on top of them. Sliding its lid off reveals the pieces, and
lifting the boxes out reveals the cards underneath.

The accessory box is not a recessed tray: each piece sits in its own hole cut
to its silhouette, with a finger pull curved into each hole so the piece can be
lifted out. The diver and base SVGs are the Illustrator files the pieces were
cut from, so the silhouettes are the pieces themselves scaled to their real
sizes — the diver's height drives one axis and its width follows the drawing,
and the same for the base's width. The five sonar tokens are round and 2.05 mm
thick, so they stack two to a well rather than all five — a full stack would be
taller than the box. Everything else (wall, floor, lid, card thickness,
the clearance around a card stack) is a default the library already knows, so
the file states only what the game is: the box, the cards, the tokens and the
two shapes.
"""

import sys
from pathlib import Path

# Repo root on sys.path, robust to __file__ being undefined (Jupyter / exec).
REPO_ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd()
sys.path.insert(0, str(REPO_ROOT))
# Venv site-packages (any Python version) so compiled extensions like shapely
# and pybosl2 load inside the PythonSCAD UI's embedded Python — relative to
# REPO_ROOT, no absolute paths, no hardcoded version.
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
    columns,
    run,
    stack,
)
from pyboxbuilder.compartments import CompartmentElement

#: SVG silhouettes live beside this example (boxes/the_crew_deep_sea/svg), so
#: the example is self-contained and builds the same from any directory.
SVG = str(REPO_ROOT / "boxes" / "the_crew_deep_sea" / "svg")

# ── Game box — the retail box's inside dimensions ───────────────────────────
BOX_WIDTH = 172.0
BOX_LENGTH = 122.0
BOX_HEIGHT = 26.0

# ── Material defaults ───────────────────────────────────────────────────────
WALL = 2.0
FLOOR = 1.6
LID = 2.0

# ── Cards ───────────────────────────────────────────────────────────────────
CARD_THICKNESS = 0.2
"""One unsleeved card — the library's standard. The 96 small cards are split
into two 48-card stacks so each stack, plus the accessory tray on top, stays
inside the box's 26 mm of height."""

CARD_SLACK = 1.0

LARGE_CARD = (56.0, 88.0)
"""The 40 playing cards and the 5 same-sized reminder cards."""
LARGE_COUNT = 40 + 5

SMALL_CARD = (44.0, 68.0)
"""The 96 small task cards."""
SMALL_COUNT = 96

# ── Tokens ──────────────────────────────────────────────────────────────────
SONAR_DIAMETER = 29.5
SONAR_COUNT = 5
DISTRESS = (44.0, 29.0)  # (length, width) of the oval distress token

TOKEN_THICKNESS = 2.05
"""The sonar and distress tokens are 2.05 mm thick. Five of them stacked is
10.25 mm — taller than the tray — so the sonar tokens split across two wells
rather than one."""

DIVER_THICKNESS = 2.5
"""The diver standee and its base are 2.5 mm thick."""

TOP_SLACK = 0.5
"""Extra depth on top of a piece, so a fingertip can get under its edge."""

# ── First-player standee, scaled from the source drawings ───────────────────
# The silhouettes are single clean outlines — the Illustrator art's internal
# details (eyes, goggle lenses, tank seams) were filled in, so the viewBox is
# the outline's own extent. The diver is 86 mm tall in the box and its width
# follows the drawing; the base is 58 mm wide and its depth follows the drawing.
DIVER_VIEWBOX = (176.013, 240.880)
DIVER_HEIGHT = 86.0
DIVER_WIDTH = DIVER_VIEWBOX[0] * DIVER_HEIGHT / DIVER_VIEWBOX[1]

BASE_VIEWBOX = (161.530, 60.160)
BASE_WIDTH = 58.0
BASE_HEIGHT = BASE_VIEWBOX[1] * BASE_WIDTH / BASE_VIEWBOX[0]

# ── Box sizes ───────────────────────────────────────────────────────────────
def card_box_size(card: tuple[float, float]) -> tuple[float, float]:
    """Outer (width, length) of a sliding box holding one card stack."""
    return (
        card[0] + CARD_SLACK + 2 * WALL,
        card[1] + CARD_SLACK + 2 * WALL,
    )


DECK_SIZE = card_box_size(LARGE_CARD)          # (61.0, 93.0)
TASK_SIZE = card_box_size(SMALL_CARD)          # (49.0, 73.0)

# The task boxes' height follows from their card count (the library derives it);
# the accessory tray takes the rest of the box's height, so the two together
# stack exactly inside the 26 mm interior.
TASK_CARDS_PER_BOX = SMALL_COUNT // 2          # 48
TASK_DEPTH = TASK_CARDS_PER_BOX * CARD_THICKNESS + CARD_SLACK
TASK_HEIGHT = TASK_DEPTH + FLOOR + LID + 0.5   # 14.7

ACCESSORY_WIDTH = BOX_WIDTH - DECK_SIZE[0]     # 111.0 — the column beside the deck
ACCESSORY_LENGTH = BOX_LENGTH - 4.0            # 118.0
ACCESSORY_HEIGHT = 11.0                        # the 26 mm left over above the tasks

ACCESSORY_INNER_W = ACCESSORY_WIDTH - 2 * WALL
ACCESSORY_INNER_L = ACCESSORY_LENGTH - 2 * WALL
ACCESSORY_INNER_H = ACCESSORY_HEIGHT - FLOOR - LID   # the lid sits above the pieces

# ── Project ─────────────────────────────────────────────────────────────────
project = Project(
    "TheCrewDeepSea",
    game_box_size=(BOX_WIDTH, BOX_LENGTH, BOX_HEIGHT),
    wall_thickness=WALL,
    floor_thickness=FLOOR,
    lid_thickness=LID,
    generate_spacers=True,
)

# Bubbles suit a game about diving; the lid style is shared by the card boxes
# and only the text changes between them.
BUBBLES = PatternBuilder(type=PatternType.VORONOI)
CREW_LID = LidBuilder(label_mode=LabelMode.FRAMELESS, diagonal=True, pattern=BUBBLES)

# ── 1. Deck — the 45 large cards, full height ───────────────────────────────
deck = project.box(
    BoxType.SLIDING,
    "Deck",
    size=(*DECK_SIZE, BOX_HEIGHT),
    lid=CREW_LID.titled("Deck"),
)
deck.cards("Deck", count=LARGE_COUNT, size=LARGE_CARD, thickness=CARD_THICKNESS, slack=CARD_SLACK)

# ── 2 & 3. Task cards — 96 cards split into two 48-card stacks ──────────────
for i in range(2):
    task_box = project.box(
        BoxType.SLIDING,
        f"Tasks{i + 1}",
        size=(*TASK_SIZE, None),  # height follows from the card count
        lid=CREW_LID.titled("Tasks"),
    )
    task_box.cards("Tasks", count=SMALL_COUNT // 2, size=SMALL_CARD, thickness=CARD_THICKNESS, slack=CARD_SLACK)

# ── 4. Accessories box — diver, base and tokens ─────────────────────────────
accessories = project.box(
    BoxType.SLIDING,
    "Accessories",
    size=(ACCESSORY_WIDTH, ACCESSORY_LENGTH, ACCESSORY_HEIGHT),
    lid=CREW_LID.titled("Captain"),
)

OVERSHOOT = 0.5
"""Extra height on every cutout so it breaks cleanly through the box's rim."""


def pocket(depth_from_top: float) -> dict:
    """Element depth for a piece `depth_from_top` mm below the tray's top face."""
    z = max(0.0, ACCESSORY_INNER_H - depth_from_top)
    return {"z_offset": z, "depth": ACCESSORY_INNER_H - z + OVERSHOOT}


def centered(
    shape_file: str | None,
    center: tuple[float, float],
    size: tuple[float, float],
    *,
    shape: ElementShape = ElementShape.SVG,
    label: str | None = None,
    corner_radius: float = 2.0,
    **pocket_kwargs,
) -> CompartmentElement:
    """An element positioned by its centre, the way the pieces are laid out.

    `CompartmentElement.offset` is a lower-left corner, so convert here once
    instead of at each call site.
    """
    proto = CompartmentElement(
        shape_file=shape_file,
        offset=(0.0, 0.0),
        size=size,
        shape=shape,
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
        label=label,
        corner_radius=corner_radius,
        **pocket_kwargs,
    )


# Every well is its piece (or stack of pieces) plus a little slack on top, so a
# fingertip can get under the top edge. The diver and base are thicker than the
# tokens, so they get their own deeper well; the sonar tokens stack, split
# across two wells (three in one, two in the other).
def stack_depth(count: int, thickness: float) -> float:
    """How deep a well must be to hold `count` stacked pieces plus the top slack."""
    return count * thickness + TOP_SLACK


DIVER_SLOT = pocket(stack_depth(1, DIVER_THICKNESS))   # 3.0 — one standee piece
SLOT = pocket(stack_depth(1, TOKEN_THICKNESS))         # 2.55 — one flat token
SONAR_THREE = pocket(stack_depth(3, TOKEN_THICKNESS))  # three stacked sonar tokens
SONAR_TWO = pocket(stack_depth(2, TOKEN_THICKNESS))    # two stacked sonar tokens

SONAR_SLOT = SONAR_DIAMETER + 0.5
"""A sonar well, half a millimetre larger than the tokens."""

DISTRESS_SLOT = (DISTRESS[0], DISTRESS[1])
"""The distress token's slot. The tray's right column is only a fraction wider
than the token, so it is cut to the token's own size."""


def accessory_elements() -> tuple[CompartmentElement, ...]:
    """Diver and base silhouettes, the sonar stack and the distress token."""
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

    # The five sonar tokens stack in two wells — three above and two below the
    # distress token, all in the strip to the right of the diver.
    elements.append(
        centered(
            None,
            (79.0, 15.0),
            (SONAR_SLOT, SONAR_SLOT),
            shape=ElementShape.CIRCLE,
            label="sonar_3",
            **SONAR_THREE,
        )
    )
    elements.append(
        centered(
            None,
            (85.0, 46.5),
            DISTRESS_SLOT,
            shape=ElementShape.ROUNDED_RECT,
            corner_radius=DISTRESS_SLOT[1] / 2 - 1.0,
            label="distress",
            **SLOT,
        )
    )
    elements.append(
        centered(
            None,
            (79.0, 78.0),
            (SONAR_SLOT, SONAR_SLOT),
            shape=ElementShape.CIRCLE,
            label="sonar_2",
            **SONAR_TWO,
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
# The deck fills a whole corner at full height; the two task boxes sit beside
# it with the lidded accessory box stacked on top, so sliding the lid off
# reveals the pieces and lifting the boxes out reveals the cards underneath.
project.arrange(
    columns(
        "Deck",
        stack(columns("Tasks1", "Tasks2"), "Accessories"),
    )
)

if __name__ == "__main__":
    run(project)
