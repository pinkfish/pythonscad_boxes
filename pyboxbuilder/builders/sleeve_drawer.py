# SPDX-License-Identifier: Apache-2.0
"""SleeveDrawerBoxBuilder — typed builder for matchbox-style sleeve & drawer boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class SleeveDrawerBoxBuilder(BoxBuilder):
    """Builder for matchbox / sleeve & drawer box type (FR-087).

    A two-piece assembly consisting of a hollow 4-sided outer perimeter sleeve
    and an inner sliding compartment drawer. Enables horizontal drawer access
    without lifting stacked trays above it.

    Example:
        .. pythonscad-example::

            project = Project("SleeveDrawerDemo", game_box_size=(100.0, 100.0, 50.0))
            project.box(
                BoxType.SLEEVE_DRAWER,
                "ResourceDrawer",
                size=(80.0, 70.0, 35.0),
                push_hole_radius=12.0,
                drawer_pull_lip=4.0,
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.SLEEVE_DRAWER
    push_hole_radius: float = 12.0
    """Radius of the finger push-through hole on the sleeve back wall in mm."""
    drawer_pull_lip: float = 4.0
    """Extension length of the drawer front pull tab/lip in mm."""
    sleeve_slack: float = 0.2
    """Clearance between outer sleeve and inner sliding drawer in mm."""
