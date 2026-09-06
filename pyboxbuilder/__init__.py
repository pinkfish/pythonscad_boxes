# SPDX-License-Identifier: Apache-2.0
"""OpenSCAD Board Game Toolkit — pyboxbuilder box library."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _distribution_version

from pybosl2 import Color

from pyboxbuilder.builders import (
    CapBoxBuilder,
    CapPathBoxBuilder,
    CardLibraryBoxBuilder,
    FilamentHingeBoxBuilder,
    HingeBoxBuilder,
    InsetBoxBuilder,
    MagneticBoxBuilder,
    NoLidBoxBuilder,
    PathBoxBuilder,
    SlidingBoxBuilder,
    SlidingCatchBoxBuilder,
    SlipoverBoxBuilder,
    SlipoverPathBoxBuilder,
)
from pyboxbuilder.builders._base import Cut
from pyboxbuilder.compartments.element import CompartmentElement, centered, centered_in_box, grid_pack
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
from pyboxbuilder.helpers import CardSize, CardSpec, SleeveType
from pyboxbuilder.layout import columns, rows, stack
from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
from pyboxbuilder.project import Project
from pyboxbuilder.run import run
from pyboxbuilder.sleeves import (
    BRANDS,
    SLEEVE_CATALOG,
    Sleeve,
    find_sleeve,
    sleeve_by_sku,
    sleeves_for_card,
)

try:
    __version__ = _distribution_version("pyboxbuilder")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = [
    "BRANDS",
    "SLEEVE_CATALOG",
    "BoxType",
    "CapBoxBuilder",
    "CapPathBoxBuilder",
    "CardLibraryBoxBuilder",
    "CardSize",
    "CardSpec",
    "Color",
    "CompartmentElement",
    "Cut",
    "ElementShape",
    "ExportResult",
    "FilamentHingeBoxBuilder",
    "FingerCut",
    "HingeBoxBuilder",
    "InsetBoxBuilder",
    "LabelMode",
    "LidBuilder",
    "MagnetType",
    "MagneticBoxBuilder",
    "NoLidBoxBuilder",
    "PathBoxBuilder",
    "PatternBuilder",
    "PatternType",
    "Project",
    "ScoopSide",
    "Sleeve",
    "SleeveType",
    "SlidingBoxBuilder",
    "SlidingCatchBoxBuilder",
    "SlipoverBoxBuilder",
    "SlipoverPathBoxBuilder",
    "StackableMode",
    "__version__",
    "centered",
    "centered_in_box",
    "columns",
    "find_sleeve",
    "grid_pack",
    "rows",
    "run",
    "sleeve_by_sku",
    "sleeves_for_card",
    "stack",
]
