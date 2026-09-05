# SPDX-License-Identifier: Apache-2.0
"""HingeBoxBuilder — typed builder for pin-hinge lid boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class HingeBoxBuilder(BoxBuilder):
    """Builder for pin-hinge lid box type.

    Example:
        .. pythonscad-example::

            project = Project("HingeDemo", game_box_size=(80.0, 80.0, 30.0))
            project.box(
                BoxType.HINGE,
                "Chest",
                size=(60.0, 50.0, 22.0),
                lid=LidBuilder(text="SUPPLIES"),
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.HINGE
    hinge_count: int | None = None
    """Knuckles across the hinge; ``None`` uses the geometry's own default."""
    hinge_pin_diameter: float | None = None
    """Pin stock diameter in mm; ``None`` uses the geometry's own default."""
    hinge_catch_type: str = "ridge"
    """Catch type for hinged boxes; 'ridge' or 'bump'."""
