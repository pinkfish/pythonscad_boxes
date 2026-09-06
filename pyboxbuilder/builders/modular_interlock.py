# SPDX-License-Identifier: Apache-2.0
"""ModularInterlockBoxBuilder — typed builder for interlocking tabletop trays."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType, InterlockType


@dataclass(frozen=True)
class ModularInterlockBoxBuilder(BoxBuilder):
    """Builder for modular interlocking tabletop play tray type (FR-089).

    Trays featuring perimeter interlocking joints on outer walls to lock multiple
    boxes side-by-side into a unified player dashboard or shared bank on the table.
    Supports sliding dovetail perimeter interlocks and Gridfinity tiered base profiles.

    Example:
        .. pythonscad-example::

            project = Project("ModularDemo", game_box_size=(150.0, 150.0, 40.0))
            project.box(
                BoxType.MODULAR_INTERLOCK,
                "DashboardTray",
                size=(84.0, 84.0, 25.0),
                interlock_type=InterlockType.DOVETAIL,
                dovetail_clearance=0.15,
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.MODULAR_INTERLOCK
    interlock_type: InterlockType = InterlockType.GRIDFINITY
    """Interlock joint style (DOVETAIL or GRIDFINITY)."""
    dovetail_clearance: float = 0.15
    """Clearance for dovetail sliding tongue-and-groove joints in mm."""
    gridfinity_pitch: float = 42.0
    """Standard unit grid pitch for Gridfinity base profiles in mm."""
