# SPDX-License-Identifier: Apache-2.0
"""SnapFitBoxBuilder — typed builder for cantilever snap-fit latch boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class SnapFitBoxBuilder(BoxBuilder):
    """Builder for snap-fit cantilever latch box type (FR-081).

    The lid features integrated downward-extending cantilever spring arms on
    opposing walls with positive retention detents (a 45° lead-in ramp and flat
    horizontal lock shoulder), mating with matching catch pockets recessed into
    the box body.

    Example:
        .. pythonscad-example::

            project = Project("SnapFitDemo", game_box_size=(100.0, 100.0, 50.0))
            project.box(
                BoxType.SNAP_FIT,
                "TokenBox",
                size=(70.0, 60.0, 30.0),
                cantilever_thickness=1.6,
                cantilever_width=14.0,
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.SNAP_FIT
    cantilever_thickness: float = 1.6
    """Cantilever spring arm thickness in mm (FR-081 default 1.6mm)."""
    cantilever_width: float = 12.0
    """Width of each cantilever latch arm in mm."""
    deflection_clearance: float = 0.3
    """Horizontal deflection clearance in mm."""
    detent_height: float = 1.5
    """Height / protrusion of the retention detent in mm."""
    latch_axis: str = "x"
    """Axis on whose opposing walls the latches sit ('x' or 'y')."""
