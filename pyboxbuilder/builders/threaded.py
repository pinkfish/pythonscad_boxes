# SPDX-License-Identifier: Apache-2.0
"""ThreadedBoxBuilder — typed builder for screw-thread containers."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class ThreadedBoxBuilder(BoxBuilder):
    """Builder for threaded screw-top container type (FR-083).

    Container with helical male/female screw threads on a circular cylindrical
    profile using coarse modified trapezoidal threads with flat crests and roots.

    Example:
        .. pythonscad-example::

            project = Project("ThreadedDemo", game_box_size=(80.0, 80.0, 60.0))
            project.box(
                BoxType.THREADED,
                "ScrewVessel",
                size=(50.0, 50.0, 45.0),
                thread_pitch=3.0,
                thread_turns=2.5,
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.THREADED
    thread_pitch: float = 3.0
    """Thread pitch in mm (>= 2.5mm to avoid layer binding, default 3.0mm)."""
    thread_turns: float = 2.0
    """Number of thread revolutions on the neck."""
    thread_clearance: float = 0.25
    """Radial clearance between male and female threads in mm."""
    thread_depth: float = 1.0
    """Depth / radial height of the thread profile in mm."""
