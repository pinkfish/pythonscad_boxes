# SPDX-License-Identifier: Apache-2.0
"""Template for new board game insert projects.

Copy this file to boxes/your_game/your_game.py and customize.

Note what is *not* here: no wall, floor or lid thickness, no gap threshold, no
spacer minimum. Those all have defaults that produce a printable box, and a
template that restates them teaches the opposite of what the library is for
(FR-000a). Set one only when your game needs a different number, or use
`box_defaults` to set common options once for the whole insert.
"""

import sys
from pathlib import Path

# Repo root + venv site-packages on sys.path, robust to __file__ being
# undefined (Jupyter / exec). Relative to the repo root, no absolute paths.
ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd()
sys.path.insert(0, str(ROOT))
for _sp in [*ROOT.glob(".venv/lib/*/site-packages"), *ROOT.glob("venv/*/lib/*/site-packages")]:
    sys.path.insert(0, str(_sp))

# Imported ready for the examples below; uncomment what you need.
from pyboxbuilder import (  # noqa: F401
    BoxType,
    Color,
    Cut,
    FingerCut,
    LabelMode,
    LidBuilder,
    PatternBuilder,
    PatternType,
    Project,
    columns,
    rows,
    run,
    stack,
)

project = Project(
    "MyGame",
    game_box_size=(300, 200, 80),  # Outer game box dimensions [W, L, H] in mm
    board_thickness=8.0,            # Reserved clearance at top of box for folded boards
    generate_spacers=True,          # Automatically fill leftover voids with snug trays
    box_defaults={"no_rotate": True},  # Defaults applied across all boxes in this insert
)

# ── A card box, described by the cards ────────────────────────────
# Leave the height unset and it follows from the card count.
#
# cards = project.box(
#     BoxType.SLIDING,
#     "Cards",
#     size=(100, 70, None),
#     color=Color("midnightblue"),
#     lid=LidBuilder(
#         label_mode=LabelMode.FRAMED,
#         frame_color=Color("gold"),
#         text_color=Color("white"),
#         pattern=PatternBuilder(PatternType.HEX),
#     ).titled("Cards"),
# )
# cards.cards("Deck", count=120, size=(63.5, 88))

# ── A tray of loose pieces with ergonomic scoops ──────────────────
# Specifying `holds_pieces=True` automatically rounds corners and floors.
#
# tokens = project.box(
#     BoxType.CAP,
#     "Tokens",
#     size=(120, 80, 26),
#     color=Color("darkred"),
#     lid=LidBuilder(label_mode=LabelMode.FRAMED, text="RESOURCES"),
# )
# tokens.compartment("Wood", width_ratio=0.33, holds_pieces=True)
# tokens.compartment("Stone", width_ratio=0.33, holds_pieces=True)
# tokens.compartment("Gold", width_ratio=0.34, holds_pieces=True)

# ── Preview, or export when the build asks for files ──────────────
if __name__ == "__main__":
    run(project)
