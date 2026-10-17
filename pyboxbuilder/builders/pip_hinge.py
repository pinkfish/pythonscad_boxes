# SPDX-License-Identifier: Apache-2.0
"""PrintInPlaceHingeBoxBuilder — typed builder for print-in-place hinged boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class PrintInPlaceHingeBoxBuilder(BoxBuilder):
    """Builder for monolithic print-in-place hinged box type (FR-090).

    A single-piece, zero-assembly hinged box where body and lid are laid flat
    at 180° on the print bed in a single print job, joined by a 3D-printable flexible
    bridge hinge along the shared rim (z = height / 2.0).

    Example:
        .. pythonscad-example::

            project = Project("PIPHingeDemo")
            project.box(
                BoxType.PRINT_IN_PLACE_HINGE,
                "MiniDeckBox",
                size=(70.0, 50.0, 25.0),
                pip_bridge_width=0.40,
                pip_bridge_thickness=0.40,
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.PRINT_IN_PLACE_HINGE
    pip_radial_clearance: float = 0.35
    """Radial air gap clearance around captive hinge pins in mm."""
    pip_axial_clearance: float = 0.40
    """Axial air gap clearance between adjacent hinge knuckles in mm."""
    pip_cone_angle: float = 45.0
    """Self-supporting overhang angle for captive hinge cones in degrees."""
    pip_hinge_radius: float = 3.0
    """Outer radius of the hinge knuckle barrel in mm."""
    pip_bridge_width: float = 0.4
    """Width of the flexible 3D-printable bridge joining the two halves of the box in mm (minimum 0.4mm)."""
    pip_bridge_thickness: float = 0.4
    """Vertical thickness of the print-in-place bridge in mm (default 0.4mm)."""
    pip_snap_catch: bool = True
    """Include pybosl2 SnapLock and SnapSocket catches on front rims."""
    pip_snap_width: float = 12.0
    """Length of the snap catch tab in mm."""
    pip_snap_diameter: float = 3.0
    """Diameter of the snap ridge in mm."""
    pip_gap_mm: float = 1.0
    """Gap between the two box halves on the print bed in mm (default 1.0mm, matching OpenSCAD toolkit)."""
