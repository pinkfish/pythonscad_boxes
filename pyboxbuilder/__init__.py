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

__all__ = [
    "Cut", "FingerCut", "Project", "BoxType", "LabelMode", "PatternType", "ScoopSide",
           "MagnetType", "StackableMode",
           "ElementShape", "Color", "CompartmentElement", "grid_pack",
           "LidBuilder", "PatternBuilder", "ExportResult",
           "columns", "rows", "stack"]
