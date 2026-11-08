# SPDX-License-Identifier: Apache-2.0
"""User-facing builders that describe a box's contents in the game's terms."""

from pyboxbuilder.builders.bayonet import BayonetBoxBuilder
from pyboxbuilder.builders.cap import CapBoxBuilder
from pyboxbuilder.builders.cap_path import CapPathBoxBuilder
from pyboxbuilder.builders.card_library import CardLibraryBoxBuilder
from pyboxbuilder.builders.card_shoe import CardShoeBoxBuilder
from pyboxbuilder.builders.clamshell import ClamshellBoxBuilder
from pyboxbuilder.builders.dice_tray import DiceTrayBoxBuilder
from pyboxbuilder.builders.dispenser import DispenserBoxBuilder
from pyboxbuilder.builders.filament_hinge import FilamentHingeBoxBuilder
from pyboxbuilder.builders.inset import InsetBoxBuilder
from pyboxbuilder.builders.inset_hinge import InsetHingeBoxBuilder
from pyboxbuilder.builders.magnetic import MagneticBoxBuilder
from pyboxbuilder.builders.magnetic_hinge import MagneticHingeBoxBuilder
from pyboxbuilder.builders.modular_interlock import ModularInterlockBoxBuilder
from pyboxbuilder.builders.no_lid import NoLidBoxBuilder
from pyboxbuilder.builders.path import PathBoxBuilder
from pyboxbuilder.builders.pip_hinge import PrintInPlaceHingeBoxBuilder
from pyboxbuilder.builders.sleeve_drawer import SleeveDrawerBoxBuilder
from pyboxbuilder.builders.sliding import SlidingBoxBuilder
from pyboxbuilder.builders.sliding_catch import SlidingCatchBoxBuilder
from pyboxbuilder.builders.sliding_hinge import SlidingHingeBoxBuilder
from pyboxbuilder.builders.slipover import SlipoverBoxBuilder
from pyboxbuilder.builders.slipover_path import SlipoverPathBoxBuilder
from pyboxbuilder.builders.snap_fit import SnapFitBoxBuilder
from pyboxbuilder.builders.threaded import ThreadedBoxBuilder

__all__ = [
    "BayonetBoxBuilder",
    "CapBoxBuilder",
    "CapPathBoxBuilder",
    "CardLibraryBoxBuilder",
    "CardShoeBoxBuilder",
    "ClamshellBoxBuilder",
    "DiceTrayBoxBuilder",
    "DispenserBoxBuilder",
    "FilamentHingeBoxBuilder",
    "InsetBoxBuilder",
    "InsetHingeBoxBuilder",
    "MagneticBoxBuilder",
    "MagneticHingeBoxBuilder",
    "ModularInterlockBoxBuilder",
    "NoLidBoxBuilder",
    "PathBoxBuilder",
    "PrintInPlaceHingeBoxBuilder",
    "SleeveDrawerBoxBuilder",
    "SlidingBoxBuilder",
    "SlidingCatchBoxBuilder",
    "SlidingHingeBoxBuilder",
    "SlipoverBoxBuilder",
    "SlipoverPathBoxBuilder",
    "SnapFitBoxBuilder",
    "ThreadedBoxBuilder",
]
