# SPDX-License-Identifier: Apache-2.0
"""Earth insert.

Card boxes are described by the cards they hold — `box.cards(count=..., size=...)`
works out the well and the box's height from that — and the arrangement is
written down rather than typed out as coordinates.
"""

import sys
from pathlib import Path

# Repo root on sys.path, robust to __file__ being undefined (Jupyter / exec).
ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd()
sys.path.insert(0, str(ROOT))
# Venv site-packages (any Python version) so compiled extensions like shapely
# and pybosl2 load inside the PythonSCAD UI's embedded Python.
for _sp in [*ROOT.glob(".venv/lib/*/site-packages"), *ROOT.glob("venv/*/lib/*/site-packages")]:
    sys.path.insert(0, str(_sp))

from pyboxbuilder import (  # noqa: E402
    BoxType,
    Color,
    FingerCut,
    LabelMode,
    LidBuilder,
    Project,
    columns,
    rows,
    run,
    stack,
)

# ── Game box and card constants ───────────────────────────────────
CARD = (62.0, 93.0)
"""One Earth card, in mm."""

WALL = 3.0
"""Card boxes take a thicker wall than the library's default."""

SLACK = 1.0
"""Clearance around a card, so it goes in and comes out freely. The same
number `cards()` uses around the stack."""

FOOTPRINT = (CARD[0] + 2 * WALL + SLACK, CARD[1] + 2 * WALL + SLACK)
"""Every card and player box shares this footprint (FR-013a), so they stack
into uniform columns. Derived from the card rather than typed as 68 x 99, so a
different game's card moves every box that holds one."""

project = Project(
    "Earth",
    game_box_size=(288.0, 288.0, 72.0),
    clearance_slack=0.0,
    generate_spacers=False,
    # The card boxes take a thicker wall. Nothing else here differs from the
    # library's defaults, so nothing else is set.
    box_defaults={"wall_thickness": WALL},
)

# ── Lid styles ────────────────────────────────────────────────────
# Written once and worn by many boxes: only the text and the accent change.
EARTH_LID = LidBuilder(label_mode=LabelMode.FRAMED, text_color=Color("white"),
                       frame_color=Color("darkgreen"))
GOLD_LID = LidBuilder(text_color=Color("white"), frame_color=Color("gold"))
TEAL_LID = LidBuilder(text_color=Color("white"), frame_color=Color("teal"))


def card_box(label: str, count: int, lid: LidBuilder, text: str):
    """A sliding card box holding `count` cards.

    The height is left unset: it falls out of the card count, the floor and the
    lid, which is what `cards()` is for.
    """
    box = project.box(
        BoxType.SLIDING, label,
        size=(FOOTPRINT[0], FOOTPRINT[1], None),
        lid=lid.titled(text),
    )
    box.cards("Cards", count=count, size=CARD)
    return box


# ── 1. Earth card boxes ───────────────────────────────────────────
# Flora, terrain and events, split four ways so a column fits under the boards.
EARTH_CARDS = 179 + 66 + 38
for i in range(4):
    card_box(f"EarthCardBox{i + 1}", EARTH_CARDS // 4, EARTH_LID, "Earth")

card_box("EarthCardBoxSmall", 20, EARTH_LID, "Earth")

# ── 2. The other decks ────────────────────────────────────────────
card_box("EcosystemCardBox", 32, GOLD_LID, "Ecosystem")
card_box("FaunaCardBox", 23, GOLD_LID, "Fauna")
card_box("IslandCardBox", 10, GOLD_LID, "Island")
card_box("ClimateCardBox", 10, TEAL_LID, "Climate")
card_box("SoloCardBox", 6, TEAL_LID, "Solo")
card_box("SeasonCardBox", 12, TEAL_LID, "Season")
card_box("AbundanceOtherCardBox", 10, TEAL_LID, "Abundance")

# ── 3. Compost, start and player boxes ────────────────────────────
compost = project.box(
    BoxType.FILAMENT_HINGE, "CompostBox",
    size=(*FOOTPRINT, 36.8),
    lid=LidBuilder(text_color=Color("white"), frame_color=Color("brown")).titled("Compost"),
)
compost.compartment("Compost", holds_pieces=True, cut=FingerCut.SCOOP)

start_box = project.box(
    BoxType.CAP, "StartBox",
    size=(*FOOTPRINT, 12.0),
    lid=GOLD_LID.titled("Start"),
)
start_box.compartment("Start", holds_pieces=True, cut=FingerCut.SCOOP)

PLAYER_COLOURS = ["red", "green", "yellow", "blue", "purple", "pink"]
for colour in PLAYER_COLOURS:
    player = project.box(
        BoxType.SLIPOVER, f"PlayerBox{colour.capitalize()}",
        size=(*FOOTPRINT, 9.2),
        lid=LidBuilder(text_color=Color("white")).titled("Player"),
    )
    player.compartment("PlayerComponents", holds_pieces=True, cut=FingerCut.SCOOP)

# ── 4. Canopy, sprouts, score pad and seeds ───────────────────────
canopy = project.box(
    BoxType.FILAMENT_HINGE, "CanopyBox", size=(168.0, 88.0, 55.2),
    lid=LidBuilder(text_color=Color("white"), frame_color=Color("olive")).titled("Canopy"),
)
canopy.compartment("Canopies", holds_pieces=True, cut=FingerCut.SCOOP)

score_pad = project.box(BoxType.NO_LID, "ScorePadBox", size=(107.0, 88.0, 6.6))
score_pad.compartment("Pad")

sprout = project.box(
    BoxType.FILAMENT_HINGE, "SproutBox", size=(107.0, 88.0, 48.6),
    lid=LidBuilder(text_color=Color("white"), frame_color=Color("green")).titled("Sprouts"),
)
sprout.compartment("Sprouts", holds_pieces=True, cut=FingerCut.SCOOP)

seed = project.box(
    BoxType.FILAMENT_HINGE, "SeedBox", size=(12.0, 46.0, 72.0),
    lid=LidBuilder(text_color=Color("white"), frame_color=Color("brown")).titled("Seeds"),
)
seed.compartment("Seeds", holds_pieces=True)

# ── 5. Boards ─────────────────────────────────────────────────────
# Six player boards, a middle board and the abundance board go on top; the
# abundance boards stand on edge down the right side.
project.box(BoxType.NO_LID, "PlayerBoards", size=(242.0, 288.0, 16.8))
project.box(BoxType.NO_LID, "AbundanceBoards", size=(12.0, 241.0, 57.0))

# ── 6. Arrangement ────────────────────────────────────────────────
# Three columns of stacked boxes across the front, the tall boxes behind them,
# and the boards on top. Change a card count and everything downstream moves.
project.arrange(columns(
    stack(
        rows(
            # Front row: the four Earth decks side by side.
            columns(*(f"EarthCardBox{i + 1}" for i in range(4))),
            # Middle row: four columns of stacked boxes, each to the same height.
            columns(
                stack("EarthCardBoxSmall", "CompostBox"),
                stack("EcosystemCardBox", "FaunaCardBox", "IslandCardBox"),
                stack("ClimateCardBox", "SoloCardBox", "SeasonCardBox",
                      "AbundanceOtherCardBox", "StartBox"),
                stack(*(f"PlayerBox{c.capitalize()}" for c in PLAYER_COLOURS)),
            ),
            # Back row: the canopy, and the sprouts under the score pad.
            columns("CanopyBox", stack("ScorePadBox", "SproutBox")),
        ),
        # The boards go on top of all of it — first thing out of the box.
        "PlayerBoards",
    ),
    # A narrow strip down the right for the seeds and the abundance boards.
    rows("SeedBox", "AbundanceBoards"),
))

if __name__ == "__main__":
    run(project)
