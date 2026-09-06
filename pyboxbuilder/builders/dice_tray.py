# SPDX-License-Identifier: Apache-2.0
"""DiceTrayBoxBuilder — typed builder for dice tray and rolling arena boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class DiceTrayBoxBuilder(BoxBuilder):
    """Builder for dice tray & rolling arena box type (FR-086).

    A dual-purpose container where the body stores dice or components and the
    deep nesting lid doubles as an active tabletop dice rolling arena.
    Features 25mm+ arena walls, 45° corner deflector fillets to bounce dice back
    toward the center, and a recessed felt pad pocket.

    Example:
        .. pythonscad-example::

            project = Project("DiceTrayDemo", game_box_size=(200.0, 150.0, 60.0))
            project.box(
                BoxType.DICE_TRAY,
                "RollingArena",
                size=(180.0, 130.0, 45.0),
                arena_wall_height=28.0,
                felt_pocket_depth=1.2,
                corner_deflectors=True,
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.DICE_TRAY
    arena_wall_height: float = 28.0
    """Height of the rolling arena walls in mm (MUST be >= 25.0mm)."""
    felt_pocket_depth: float = 1.2
    """Depth of the acoustic felt/leatherette pad recess in mm."""
    corner_deflectors: bool = True
    """Add 45° corner deflector fillets to bounce rolling dice inward."""
