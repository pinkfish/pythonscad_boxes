# SPDX-License-Identifier: Apache-2.0
"""FilamentHingeBoxBuilder — typed builder for living-hinge lid boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class FilamentHingeBoxBuilder(BoxBuilder):
    """Builder for filament (living) hinge lid box type.

    Example:
        .. pythonscad-example::

            project = Project("FilamentHingeDemo", game_box_size=(80.0, 80.0, 30.0))
            project.box(
                BoxType.FILAMENT_HINGE,
                "PinBox",
                size=(60.0, 50.0, 22.0),
                lid=LidBuilder(text="GEAR"),
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.FILAMENT_HINGE
    hinge_catch_type: str = "ridge"
    """Catch type for hinged boxes; 'ridge' or 'bump'."""
