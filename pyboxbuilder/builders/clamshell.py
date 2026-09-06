# SPDX-License-Identifier: Apache-2.0
"""ClamshellBoxBuilder — typed builder for bifold / clamshell book boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class ClamshellBoxBuilder(BoxBuilder):
    """Builder for bifold / clamshell book box type (FR-088).

    Two tray halves joined along a central spine hinge, unfolding 180° flat onto
    the table so both halves serve as active token/card trays during play, and
    folding closed for secure vertical book-style storage.

    Example:
        .. pythonscad-example::

            project = Project("ClamshellDemo", game_box_size=(150.0, 100.0, 60.0))
            project.box(
                BoxType.CLAMSHELL,
                "SpellBook",
                size=(120.0, 80.0, 40.0),
                spine_gap=1.0,
                clamshell_hinge_radius=2.5,
                closure_latch=True,
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.CLAMSHELL
    spine_gap: float = 1.0
    """Gap along the central spine hinge in mm."""
    clamshell_hinge_radius: float = 2.5
    """Radius of the spine hinge knuckle barrel in mm."""
    closure_latch: bool = True
    """Add perimeter retention ridge catches to keep the clamshell closed."""
