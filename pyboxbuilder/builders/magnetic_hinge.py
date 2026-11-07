# SPDX-License-Identifier: Apache-2.0
"""MagneticHingeBoxBuilder — typed builder for hinged boxes with front magnet closure."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class MagneticHingeBoxBuilder(BoxBuilder):
    """Builder for a filament-hinged box with a small front magnet closure.

    Combines a rear filament pin hinge with a front magnet boss and matching
    blind magnet sockets in the front body rim and lid underside to keep the
    lid securely closed.

    Example:
        .. pythonscad-example::

            project = Project("MagneticHingeDemo")
            project.box(
                BoxType.MAGNETIC_HINGE,
                "MagChest",
                size=(60.0, 50.0, 22.0),
                magnet_diameter=4.0,
                magnet_height=2.0,
                lid=LidBuilder(text="RELICS"),
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.MAGNETIC_HINGE
    magnet_diameter: float = 4.0
    """Round front magnet diameter in mm (default 4.0mm)."""
    magnet_height: float = 2.0
    """Round front magnet thickness in mm (default 2.0mm)."""
    hinge_count: int | None = None
    """Knuckles across the rear hinge; ``None`` uses the geometry's own default."""
    filament_diameter: float | None = None
    """Pin/filament stock diameter in mm; ``None`` uses the geometry's own default (1.75mm)."""

