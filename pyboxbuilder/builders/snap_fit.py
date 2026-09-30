# SPDX-License-Identifier: Apache-2.0
"""SnapFitBoxBuilder — typed builder for cantilever snap-fit latch boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType, LatchAxis


@dataclass(frozen=True)
class SnapFitBoxBuilder(BoxBuilder):
    """Builder for snap-fit cantilever latch box type (FR-081).

    The lid features integrated downward-extending cantilever spring arms on
    opposing walls with positive retention detents (a 45° lead-in ramp and flat
    horizontal lock shoulder), mating with matching catch pockets recessed into
    the box body.

    Example:
        .. pythonscad-example::

            project = Project("SnapFitDemo")
            project.box(
                BoxType.SNAP_FIT,
                "TokenBox",
                size=(70.0, 60.0, 30.0),
                cantilever_thickness=1.6,
                cantilever_width=14.0,
                latch_axis=LatchAxis.X,
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
    latch_axis: LatchAxis = LatchAxis.X
    """Axis on whose opposing walls the latches sit (LatchAxis.X or LatchAxis.Y, FR-106)."""

    def __post_init__(self) -> None:
        """Coerce latch_axis string or validate enum instance."""
        if isinstance(self.latch_axis, str):
            try:
                object.__setattr__(self, "latch_axis", LatchAxis(self.latch_axis.lower()))
            except ValueError:
                valid = [e.value for e in LatchAxis]
                raise ValueError(
                    f"Invalid latch_axis '{self.latch_axis}'. "
                    f"Must be LatchAxis enum member: {valid}"
                ) from None
        elif not isinstance(self.latch_axis, LatchAxis):
            raise TypeError(
                f"latch_axis must be a LatchAxis enum, got {type(self.latch_axis).__name__}"
            )
        super().__post_init__()

