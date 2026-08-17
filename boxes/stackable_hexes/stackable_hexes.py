#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Stackable hexes — hexagonal stackable boxes with side magnets.

Ports examples/stackable_hexes.py to the pyboxbuilder Project API.
Standalone stackable boxes (no game box) with round or rectangular magnets
in the side walls and 1–4 internal divisions.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd()
sys.path.insert(0, str(ROOT))
# Venv site-packages (any Python version) so compiled extensions like shapely
# and pybosl2 load inside the PythonSCAD UI's embedded Python — relative to
# ROOT, no absolute paths, no hardcoded version.
for _sp in ROOT.glob(".venv/lib/*/site-packages"):
    sys.path.insert(0, str(_sp))
for _sp in ROOT.glob("venv/*/lib/*/site-packages"):
    sys.path.insert(0, str(_sp))

from pyboxbuilder import (
    BoxType,
    MagnetType,
    Project,
    StackableMode,
    run,
)

# ── Stackable Hex Parameters ──────────────────────────────────────
stackable_width = 100
stackable_height = 24
wall_thickness = 4

# Magnet defaults: round = [diameter, depth], rect = [width, length, depth]
ROUND_MAGNET_SIZE = (stackable_height / 2 - 1, 7, 2.9)
RECT_MAGNET_SIZE = (12, 6, 1.65)


def stackable_hex(
    project: Project,
    label: str,
    divisions: int,
    magnet_type: MagnetType,
    magnet_size: tuple,
) -> None:
    """Create a standalone stackable hex box."""
    box = project.box(
        BoxType.NO_LID,
        label,
        size=(stackable_width, stackable_width, stackable_height),
        wall_thickness=wall_thickness,
        stackable=StackableMode.INSIDE,  # interlocking rim (FR-038)
        stackable_thickness=2.0,
        magnet_type=magnet_type,         # round or rect (FR-039)
        magnet_size=magnet_size,
        no_rotate=True,                # hex is rotationally symmetric
    )
    if divisions > 1:
        # Partition the hex into N equal compartments. The ratio is a share of
        # the room the wells actually have, so N of them at 1/N fit — no
        # arithmetic here about the box's walls or the layout's gutters.
        for i in range(divisions):
            box.compartment(f"div{i + 1}", width_ratio=1 / divisions)


# Standalone project (no game box → each box exports independently)
project = Project(
    "StackableHexes",
    game_box_size=None,   # standalone: no enclosing game box (FR-037)
    wall_thickness=wall_thickness,
    floor_thickness=wall_thickness,
)

# 8 variants: 1–4 divisions × round/rect magnets
round_variants = [
    (1, "HexBoxSingle6x3RoundMagnet"),
    (2, "HexBoxSingle6x3RoundMagnetWithTwoPartitions"),
    (3, "HexBoxSingle6x3RoundMagnetWithThreePartitions"),
    (4, "HexBoxSingle6x3RoundMagnetWithFourPartitions"),
]
rect_variants = [
    (1, "HexBoxSingle10x5x2RectMagnet"),
    (2, "HexBoxSingle10x5x2RectMagnetWithTwoPartitions"),
    (3, "HexBoxSingle10x5x2RectMagnetWithThreePartitions"),
    (4, "HexBoxSingle10x5x2RectMagnetWithFourPartitions"),
]

for divisions, label in round_variants:
    stackable_hex(project, label, divisions, MagnetType.ROUND, ROUND_MAGNET_SIZE)
for divisions, label in rect_variants:
    stackable_hex(project, label, divisions, MagnetType.RECT, RECT_MAGNET_SIZE)

# ── Export ────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(project)
