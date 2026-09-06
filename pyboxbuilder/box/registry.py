# SPDX-License-Identifier: Apache-2.0
"""Box type registry — maps BoxType enum to implementation classes."""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyboxbuilder.enums import BoxType

if TYPE_CHECKING:
    from pyboxbuilder.box.base import BoxTypeBase


@dataclass
class _RegistryEntry:
    box_class: type["BoxTypeBase"]
    builder_class: type


BOX_TYPE_REGISTRY: dict[BoxType, type] = {}
"""Maps BoxType enum members to their BoxBuilder subclass."""

BOX_IMPL_REGISTRY: dict[BoxType, type] = {}
"""Maps BoxType enum members to their BoxTypeBase implementation."""


def register_box(
    box_type: BoxType,
    builder_class: type,
    box_class: type | None = None,
) -> None:
    """Register a box type with its builder and optional implementation.

    Args:
        box_type: The BoxType enum member.
        builder_class: The BoxBuilder subclass for this type.
        box_class: The BoxTypeBase implementation (can be registered later).

    """
    BOX_TYPE_REGISTRY[box_type] = builder_class
    if box_class is not None:
        BOX_IMPL_REGISTRY[box_type] = box_class


# Register available box types
from pyboxbuilder.box.types.bayonet import BayonetBox  # noqa: E402
from pyboxbuilder.box.types.cap import CapBox  # noqa: E402
from pyboxbuilder.box.types.cap_path import CapPathBox  # noqa: E402
from pyboxbuilder.box.types.card_library import CardLibraryBox  # noqa: E402
from pyboxbuilder.box.types.card_shoe import CardShoeBox  # noqa: E402
from pyboxbuilder.box.types.clamshell import ClamshellBox  # noqa: E402
from pyboxbuilder.box.types.dice_tray import DiceTrayBox  # noqa: E402
from pyboxbuilder.box.types.dispenser import DispenserBox  # noqa: E402
from pyboxbuilder.box.types.filament_hinge import FilamentHingeBox  # noqa: E402
from pyboxbuilder.box.types.hinge import HingeBox  # noqa: E402
from pyboxbuilder.box.types.inset import InsetBox  # noqa: E402
from pyboxbuilder.box.types.magnetic import MagneticBox  # noqa: E402
from pyboxbuilder.box.types.modular_interlock import ModularInterlockBox  # noqa: E402
from pyboxbuilder.box.types.no_lid import NoLidBox  # noqa: E402
from pyboxbuilder.box.types.path import PathBox  # noqa: E402
from pyboxbuilder.box.types.pip_hinge import PrintInPlaceHingeBox  # noqa: E402
from pyboxbuilder.box.types.sleeve_drawer import SleeveDrawerBox  # noqa: E402
from pyboxbuilder.box.types.sliding import SlidingBox  # noqa: E402
from pyboxbuilder.box.types.sliding_catch import SlidingCatchBox  # noqa: E402
from pyboxbuilder.box.types.slipover import SlipoverBox  # noqa: E402
from pyboxbuilder.box.types.slipover_path import SlipoverPathBox  # noqa: E402
from pyboxbuilder.box.types.snap_fit import SnapFitBox  # noqa: E402
from pyboxbuilder.box.types.threaded import ThreadedBox  # noqa: E402
from pyboxbuilder.builders.bayonet import BayonetBoxBuilder  # noqa: E402
from pyboxbuilder.builders.cap import CapBoxBuilder  # noqa: E402
from pyboxbuilder.builders.cap_path import CapPathBoxBuilder  # noqa: E402
from pyboxbuilder.builders.card_library import CardLibraryBoxBuilder  # noqa: E402
from pyboxbuilder.builders.card_shoe import CardShoeBoxBuilder  # noqa: E402
from pyboxbuilder.builders.clamshell import ClamshellBoxBuilder  # noqa: E402
from pyboxbuilder.builders.dice_tray import DiceTrayBoxBuilder  # noqa: E402
from pyboxbuilder.builders.dispenser import DispenserBoxBuilder  # noqa: E402
from pyboxbuilder.builders.filament_hinge import FilamentHingeBoxBuilder  # noqa: E402
from pyboxbuilder.builders.hinge import HingeBoxBuilder  # noqa: E402
from pyboxbuilder.builders.inset import InsetBoxBuilder  # noqa: E402
from pyboxbuilder.builders.magnetic import MagneticBoxBuilder  # noqa: E402
from pyboxbuilder.builders.modular_interlock import ModularInterlockBoxBuilder  # noqa: E402
from pyboxbuilder.builders.no_lid import NoLidBoxBuilder  # noqa: E402
from pyboxbuilder.builders.path import PathBoxBuilder  # noqa: E402
from pyboxbuilder.builders.pip_hinge import PrintInPlaceHingeBoxBuilder  # noqa: E402
from pyboxbuilder.builders.sleeve_drawer import SleeveDrawerBoxBuilder  # noqa: E402
from pyboxbuilder.builders.sliding import SlidingBoxBuilder  # noqa: E402
from pyboxbuilder.builders.sliding_catch import SlidingCatchBoxBuilder  # noqa: E402
from pyboxbuilder.builders.slipover import SlipoverBoxBuilder  # noqa: E402
from pyboxbuilder.builders.slipover_path import SlipoverPathBoxBuilder  # noqa: E402
from pyboxbuilder.builders.snap_fit import SnapFitBoxBuilder  # noqa: E402
from pyboxbuilder.builders.threaded import ThreadedBoxBuilder  # noqa: E402

register_box(BoxType.SLIDING, SlidingBoxBuilder, SlidingBox)
register_box(BoxType.CAP, CapBoxBuilder, CapBox)
register_box(BoxType.HINGE, HingeBoxBuilder, HingeBox)
register_box(BoxType.FILAMENT_HINGE, FilamentHingeBoxBuilder, FilamentHingeBox)
register_box(BoxType.MAGNETIC, MagneticBoxBuilder, MagneticBox)
register_box(BoxType.INSET, InsetBoxBuilder, InsetBox)
register_box(BoxType.SLIDING_CATCH, SlidingCatchBoxBuilder, SlidingCatchBox)
register_box(BoxType.SLIPOVER, SlipoverBoxBuilder, SlipoverBox)
register_box(BoxType.SLIPOVER_PATH, SlipoverPathBoxBuilder, SlipoverPathBox)
register_box(BoxType.CAP_PATH, CapPathBoxBuilder, CapPathBox)
register_box(BoxType.NO_LID, NoLidBoxBuilder, NoLidBox)
register_box(BoxType.PATH, PathBoxBuilder, PathBox)
register_box(BoxType.CARD_LIBRARY, CardLibraryBoxBuilder, CardLibraryBox)
register_box(BoxType.SNAP_FIT, SnapFitBoxBuilder, SnapFitBox)
register_box(BoxType.BAYONET, BayonetBoxBuilder, BayonetBox)
register_box(BoxType.THREADED, ThreadedBoxBuilder, ThreadedBox)
register_box(BoxType.DISPENSER, DispenserBoxBuilder, DispenserBox)
register_box(BoxType.CARD_SHOE, CardShoeBoxBuilder, CardShoeBox)
register_box(BoxType.DICE_TRAY, DiceTrayBoxBuilder, DiceTrayBox)
register_box(BoxType.SLEEVE_DRAWER, SleeveDrawerBoxBuilder, SleeveDrawerBox)
register_box(BoxType.CLAMSHELL, ClamshellBoxBuilder, ClamshellBox)
register_box(BoxType.MODULAR_INTERLOCK, ModularInterlockBoxBuilder, ModularInterlockBox)
register_box(BoxType.PRINT_IN_PLACE_HINGE, PrintInPlaceHingeBoxBuilder, PrintInPlaceHingeBox)


LIDLESS_BOX_TYPES: frozenset[BoxType] = frozenset({
    BoxType.NO_LID,
    BoxType.PATH,
    BoxType.PRINT_IN_PLACE_HINGE,
})
"""Box types that produce a body file only — no lid geometry, no `_lid.3mf`."""
