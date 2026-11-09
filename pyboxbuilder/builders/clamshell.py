# SPDX-License-Identifier: Apache-2.0
"""ClamshellBoxBuilder — typed builder for bifold / clamshell book boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType, CatchType, HingeCatchType


@dataclass(frozen=True)
class ClamshellBoxBuilder(BoxBuilder):
    """Builder for bifold / clamshell book box type (FR-088).

    Two symmetrical tray halves joined along a central filament-pin spine hinge,
    unfolding 180° flat onto the table so both halves serve as active token/card
    trays during play, and folding closed with a front catch for storage.

    Example:
        .. pythonscad-example::

            project = Project("ClamshellDemo")
            project.box(
                BoxType.CLAMSHELL,
                "SpellBook",
                size=(120.0, 80.0, 40.0),
                filament_diameter=1.75,
                hinge_count=5,
                closure_latch=True,
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.CLAMSHELL
    filament_diameter: float = 1.75
    """Diameter of the filament hinge pin in mm (default 1.75mm)."""
    hinge_count: int = 5
    """Total number of interleaving knuckles across the spine hinge."""
    spine_gap: float = 1.0
    """Gap along the central spine hinge in mm."""
    clamshell_hinge_radius: float = 2.5
    """Radius of the spine hinge knuckle barrel in mm."""
    closure_latch: bool = True
    """Add front retention catch to keep the clamshell closed."""
    hinge_catch_type: HingeCatchType | None = None
    """Optional hinge catch mechanism override (all HingeCatchType / CatchType values supported)."""

    def __post_init__(self) -> None:
        """Coerce hinge_catch_type if provided."""
        if self.hinge_catch_type is not None:
            if isinstance(self.hinge_catch_type, CatchType):
                object.__setattr__(self, "hinge_catch_type", HingeCatchType(self.hinge_catch_type.value))
            elif isinstance(self.hinge_catch_type, str):
                object.__setattr__(self, "hinge_catch_type", HingeCatchType(self.hinge_catch_type.lower()))
        super().__post_init__()
