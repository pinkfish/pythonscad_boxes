# SPDX-License-Identifier: Apache-2.0
"""DispenserBoxBuilder — typed builder for gravity tile and token dispensers."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class DispenserBoxBuilder(BoxBuilder):
    """Builder for gravity tile & token dispenser tower type (FR-084).

    Designed for cardboard tiles, chips, or resource tokens during gameplay.
    Features a top loading chute, an internal slide floor angled toward the front
    wall, a horizontal bottom dispensing slot, a vertical sight slot, and a curved
    finger extraction scoop.

    Example:
        .. pythonscad-example::

            project = Project("DispenserDemo", game_box_size=(100.0, 100.0, 120.0))
            project.box(
                BoxType.DISPENSER,
                "TileTower",
                size=(60.0, 60.0, 90.0),
                token_thickness=3.0,
                chute_angle=40.0,
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.DISPENSER
    chute_angle: float = 40.0
    """Angle of the internal gravity slide floor in degrees (typically 35°–45°)."""
    token_thickness: float = 3.0
    """Thickness of a single tile or token in mm."""
    dispense_slot_clearance: float = 0.8
    """Clearance height above token thickness for the dispensing slot in mm."""
    sight_slot_width: float = 8.0
    """Width of the vertical inspection/sight slot on the front wall in mm."""
