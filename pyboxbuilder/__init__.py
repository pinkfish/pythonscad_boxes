# SPDX-License-Identifier: Apache-2.0
"""OpenSCAD Board Game Toolkit — pyboxbuilder box library."""

from pybosl2 import Color

from pyboxbuilder.builders._base import Cut
from pyboxbuilder.compartments.element import CompartmentElement, grid_pack
from pyboxbuilder.enums import (
    BoxType,
    ElementShape,
    FingerCut,
    LabelMode,
    MagnetType,
    PatternType,
    ScoopSide,
    StackableMode,
)
from pyboxbuilder.export.result import ExportResult
from pyboxbuilder.layout import columns, rows, stack
from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
from pyboxbuilder.project import Project
from pyboxbuilder.run import run

__all__ = [
    "BoxType",
    "Color",
    "CompartmentElement",
    "Cut",
    "ElementShape",
    "ExportResult",
    "FingerCut",
    "LabelMode",
    "LidBuilder",
    "MagnetType",
    "PatternBuilder",
    "PatternType",
    "Project",
    "ScoopSide",
    "StackableMode",
    "columns",
    "grid_pack",
    "rows",
    "run",
    "stack",
]
