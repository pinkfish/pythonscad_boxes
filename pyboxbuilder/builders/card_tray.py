# SPDX-License-Identifier: Apache-2.0
"""CardTrayBoxBuilder — typed builder for vertical & angled card trays with divider slots."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class CardTrayBoxBuilder(BoxBuilder):
    """Builder for a vertical or angled card tray with optional removable divider slots.

    Stores cards standing upright (``card_tilt_angle=0.0``) or tilted backward
    (``card_tilt_angle=15.0``–``35.0``) to fit tall cards inside shallow game boxes.
    Opposing inner-wall rails accept removable printed or cardstock dividers, and
    optional front/back U-shaped scoops let fingers browse cards comfortably.

    Example:
        .. pythonscad-example::

            project = Project("CardTrayDemo")
            project.box(
                BoxType.CARD_TRAY,
                "DominionCards",
                size=(72.0, 200.0, 75.0),
                card_tilt_angle=20.0,
                divider_slots=4,
            )
            project.show()
    """

    box_type: ClassVar[BoxType] = BoxType.CARD_TRAY
    card_tilt_angle: float = 0.0
    """Tilt angle in degrees from vertical (0° = upright, 15°–35° = tilted backward)."""
    divider_slots: int = 0
    """Number of evenly-spaced removable divider slot pairs along the length (Y) axis."""
    divider_positions: tuple[float, ...] = ()
    """Explicit Y positions (mm from interior front) for divider slot pairs; overrides ``divider_slots``."""
    divider_slot_width: float = 2.0
    """Width (Y thickness) of each divider rail slot in mm."""
    divider_slot_depth: float = 1.0
    """Depth each divider slot cuts into the left and right inner walls in mm."""
    front_cutout: bool = True
    """Cut opposing U-shaped finger scoops on the front and back walls for easy card browsing."""
