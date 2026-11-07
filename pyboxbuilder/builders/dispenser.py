# SPDX-License-Identifier: Apache-2.0
"""DispenserBoxBuilder — typed builder for gravity tile and token dispensers."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType, DispenserExtractionMode


@dataclass(frozen=True)
class DispenserBoxBuilder(BoxBuilder):
    """Builder for gravity tile & token dispenser tower type (FR-084).

    Designed for cardboard tiles, chips, or resource tokens during gameplay.
    Features a top loading chute, a flat or configurable angled internal floor
    (default ``0.0°`` flat floor), a horizontal bottom dispensing slot, a vertical
    sight slot, and finger-pinch extraction cutouts (front pinch scoop and bottom
    floor notch by default, or forward landing tray, rear push, or arch).

    Example:
        .. pythonscad-example::

            project = Project("DispenserDemo")
            project.box(
                BoxType.DISPENSER,
                "TileTower",
                size=(60.0, 60.0, 90.0),
                token_thickness=3.0,
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.DISPENSER
    chute_angle: float = 0.0
    """Angle of the internal tile floor in degrees (defaults to ``0.0°`` flat; set e.g. ``35°`` for a ramp)."""
    tile_angle: float | None = None
    """Optional alias for ``chute_angle`` specifying the angle of the internal tile floor in degrees."""
    token_thickness: float = 3.0
    """Thickness of a single tile or token in mm."""
    dispense_slot_clearance: float = 0.8
    """Clearance height above token thickness for the dispensing slot in mm."""
    sight_slot_width: float = 8.0
    """Width of the vertical inspection/sight slot on the front wall in mm."""
    sight_slot_start: float | None = None
    """Starting height Z in mm of the sight slot. Defaults to covering the lower half (body_h * 0.5)."""
    dispenser_mode: DispenserExtractionMode = DispenserExtractionMode.SCOOP
    """:class:`~pyboxbuilder.enums.DispenserExtractionMode` selection: SCOOP (default), TRAY, REAR_PUSH, or ARCH."""
    scoop_radius: float = 14.0
    """Radius of the front finger scoop in mm for SCOOP mode."""
    floor_scoop_depth: float = 12.0
    """Depth of the front floor pinch cutout in mm for SCOOP mode."""
    floor_scoop_width: float = 24.0
    """Width of the front floor pinch cutout in mm for SCOOP mode."""
    tray_depth: float = 20.0
    """Depth of forward-protruding landing tray shelf in mm for TRAY mode."""
    rear_push_width: float = 22.0
    """Width of rear push finger cutout in mm for REAR_PUSH mode."""
    arch_height: float | None = None
    """Height of front open archway in mm for ARCH mode (defaults to 0.65 * body_h)."""

    def __post_init__(self) -> None:
        """Synchronize ``tile_angle`` and ``chute_angle``."""
        if self.tile_angle is not None:
            object.__setattr__(self, "chute_angle", float(self.tile_angle))
        super().__post_init__()


