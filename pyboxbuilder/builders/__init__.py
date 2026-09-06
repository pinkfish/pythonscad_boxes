# SPDX-License-Identifier: Apache-2.0
"""User-facing builders that describe a box's contents in the game's terms."""

from pyboxbuilder.builders.cap import CapBoxBuilder
from pyboxbuilder.builders.cap_path import CapPathBoxBuilder
from pyboxbuilder.builders.card_library import CardLibraryBoxBuilder
from pyboxbuilder.builders.filament_hinge import FilamentHingeBoxBuilder
from pyboxbuilder.builders.hinge import HingeBoxBuilder
from pyboxbuilder.builders.inset import InsetBoxBuilder
from pyboxbuilder.builders.magnetic import MagneticBoxBuilder
from pyboxbuilder.builders.no_lid import NoLidBoxBuilder
from pyboxbuilder.builders.path import PathBoxBuilder
from pyboxbuilder.builders.sliding import SlidingBoxBuilder
from pyboxbuilder.builders.sliding_catch import SlidingCatchBoxBuilder
from pyboxbuilder.builders.slipover import SlipoverBoxBuilder
from pyboxbuilder.builders.slipover_path import SlipoverPathBoxBuilder

__all__ = [
    "CapBoxBuilder",
    "CapPathBoxBuilder",
    "CardLibraryBoxBuilder",
    "FilamentHingeBoxBuilder",
    "HingeBoxBuilder",
    "InsetBoxBuilder",
    "MagneticBoxBuilder",
    "NoLidBoxBuilder",
    "PathBoxBuilder",
    "SlidingBoxBuilder",
    "SlidingCatchBoxBuilder",
    "SlipoverBoxBuilder",
    "SlipoverPathBoxBuilder",
]
