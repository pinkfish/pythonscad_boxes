# SPDX-License-Identifier: Apache-2.0
"""InsetHingeBoxBuilder — typed builder for print-in-place inset-hinge boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class InsetHingeBoxBuilder(BoxBuilder):
    """Builder for print-in-place inset-hinge box type (``BoxType.INSET_HINGE``).

    A single-piece, zero-assembly hinged box based on ``MakeBoxAndLidWithInsetHinge``
    from ``hinge_box.scad``. Both base and lid halves sit side-by-side along the X
    axis on the print bed separated by ``pip_gap_mm`` (default ``1.0 mm``), joined by
    a recessed print-in-place conical knuckle hinge (``InsetHinge``) with 45°
    self-supporting mounting brackets, a self-aligning perimeter rim and rabbet, and
    a front snap-latch tab (``MakeLidTab``).

    Example:
        .. pythonscad-example::

            project = Project("InsetHingeDemo")
            project.box(
                BoxType.INSET_HINGE,
                "InsetDeckBox",
                size=(70.0, 50.0, 26.0),
                pip_hinge_radius=3.0,
                pip_radial_clearance=0.30,
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.INSET_HINGE
    pip_hinge_radius: float = 3.0
    """Outer radius of the inset hinge knuckle barrel in mm (hinge diameter = 2 * radius)."""
    pip_radial_clearance: float = 0.30
    """Clearance offset around the captive conical hinge knuckles in mm (hinge_offset)."""
    pip_gap_mm: float = 1.0
    """Gap between the base and lid halves on the print bed in mm."""
    inset_hinge_side_gap: float = 3.0
    """End wall margin at the front and back of the inset hinge pocket in mm."""
    pip_snap_catch: bool = True
    """Include the front snap latch tab and catch recess (MakeLidTab)."""
    pip_snap_width: float = 10.0
    """Length of the front snap latch tab along the Y axis in mm."""
    inset_hinge_tab_height: float = 6.0
    """Height of the front snap latch tab in mm."""

