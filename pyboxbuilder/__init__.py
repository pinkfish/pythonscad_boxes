# SPDX-License-Identifier: Apache-2.0
"""OpenSCAD Board Game Toolkit — pyboxbuilder box library."""

from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _distribution_version

from pybosl2 import Color

from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.spec import BoxSpec, ResolvedBoxSpec, UnresolvedBoxSpec
from pyboxbuilder.box.validation import GeometryValidationError, GeometryValidator
from pyboxbuilder.builders import (
    BayonetBoxBuilder,
    CapBoxBuilder,
    CapPathBoxBuilder,
    CardLibraryBoxBuilder,
    CardShoeBoxBuilder,
    ClamshellBoxBuilder,
    DiceTrayBoxBuilder,
    DispenserBoxBuilder,
    FilamentHingeBoxBuilder,
    HingeBoxBuilder,
    InsetBoxBuilder,
    MagneticBoxBuilder,
    ModularInterlockBoxBuilder,
    NoLidBoxBuilder,
    PathBoxBuilder,
    PrintInPlaceHingeBoxBuilder,
    SleeveDrawerBoxBuilder,
    SlidingBoxBuilder,
    SlidingCatchBoxBuilder,
    SlipoverBoxBuilder,
    SlipoverPathBoxBuilder,
    SnapFitBoxBuilder,
    ThreadedBoxBuilder,
)
from pyboxbuilder.builders._base import Cut
from pyboxbuilder.compartments.element import CompartmentElement, centered, centered_in_box, grid_pack
from pyboxbuilder.enums import (
    BoxType,
    ElementShape,
    FingerCut,
    InterlockType,
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
from pyboxbuilder.project import GeometryPipeline, LayoutCompiler, Project, ProjectManifest
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
    "BayonetBoxBuilder",
    "BoxSpec",
    "BoxType",
    "CapBoxBuilder",
    "CapPathBoxBuilder",
    "CardLibraryBoxBuilder",
    "CardShoeBoxBuilder",
    "CardSize",
    "CardSpec",
    "ClamshellBoxBuilder",
    "Color",
    "CompartmentElement",
    "Cut",
    "DiceTrayBoxBuilder",
    "DispenserBoxBuilder",
    "ElementShape",
    "ExportResult",
    "FilamentHingeBoxBuilder",
    "FingerCut",
    "GeometryPipeline",
    "GeometryValidationError",
    "GeometryValidator",
    "HingeBoxBuilder",
    "InsetBoxBuilder",
    "InterlockType",
    "LabelMode",
    "LayoutCompiler",
    "LidBuilder",
    "MagnetType",
    "MagneticBoxBuilder",
    "ModularInterlockBoxBuilder",
    "NoLidBoxBuilder",
    "PathBoxBuilder",
    "PatternBuilder",
    "PatternType",
    "PrintInPlaceHingeBoxBuilder",
    "Project",
    "ProjectManifest",
    "ResolvedBoxSpec",
    "ScoopSide",
    "Sleeve",
    "SleeveDrawerBoxBuilder",
    "SleeveType",
    "SlidingBoxBuilder",
    "SlidingCatchBoxBuilder",
    "SlipoverBoxBuilder",
    "SlipoverPathBoxBuilder",
    "SnapFitBoxBuilder",
    "StackableMode",
    "ThreadedBoxBuilder",
    "UnresolvedBoxSpec",
    "__version__",
    "centered",
    "centered_in_box",
    "columns",
    "find_sleeve",
    "grid_pack",
    "register_box",
    "rows",
    "run",
    "sleeve_by_sku",
    "sleeves_for_card",
    "stack",
]
