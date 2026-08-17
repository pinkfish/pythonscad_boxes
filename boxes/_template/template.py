# SPDX-License-Identifier: Apache-2.0
"""Template for new board game insert projects.

Copy this file to boxes/your_game/your_game.py and customize.

Note what is *not* here: no wall, floor or lid thickness, no gap threshold, no
spacer minimum. Those all have defaults that produce a printable box, and a
template that restates them teaches the opposite of what the library is for
(FR-000a). Set one only when your game needs a different number.
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
    FingerCut,
    LabelMode,
    LidBuilder,
    Project,
    run,
)

project = Project(
    "MyGame",
    game_box_size=(300, 200, 80),  # Your game box outer dimensions [W, L, H]
)

# ── A card box, described by the cards ────────────────────────────
# Leave the height unset and it follows from the card count.
#
# cards = project.box(
#     BoxType.SLIDING, "Cards",
#     size=(100, 70, None),
#     lid=LidBuilder(label_mode=LabelMode.FRAMED,
#                    frame_color=Color("gold")).titled("Cards"),
# )
# cards.cards("Deck", count=120, size=(63.5, 88))

# ── A tray of loose pieces ────────────────────────────────────────
# No size and no depth: the well fills the box, and `holds_pieces` rounds its
# corners and floor so a finger can sweep a piece out.
#
# tokens = project.box(BoxType.NO_LID, "Tokens", size=(80, 60, 25))
# tokens.compartment("Wood", holds_pieces=True, cut=FingerCut.SCOOP)

# ── Preview, or export when the build asks for files ──────────────
if __name__ == "__main__":
    run(project)
