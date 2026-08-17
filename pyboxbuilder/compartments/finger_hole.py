# SPDX-License-Identifier: Apache-2.0
"""Finger cut geometry — the name the rest of the library imports.

The geometry itself lives in three modules, split along the seam a finger cut
actually has:

* :mod:`pyboxbuilder.compartments.finger_outline` — the **shape**, in two
  dimensions. Pure path maths; no solids, no wall, no side.
* :mod:`pyboxbuilder.compartments.finger_sweep` — taking that outline
  **through a wall**, and what each end does when it emerges.
* :mod:`pyboxbuilder.compartments.finger_cuts` — the three **cuts** built out
  of those two, and :func:`build_cut`, which chooses between them.

They were one 1,500-line file, which is a long way to read to find out whether
a number is about the shape or about the wall — and the defects that reached a
render were all one or the other, never both. This module re-exports the three
so existing imports keep working; new code can take the specific module.
"""

from __future__ import annotations

from pyboxbuilder.compartments.finger_cuts import (
    _SIDE_CENTRES,
    _SIDE_SPIN,
    DEFAULT_FLOOR_DIP_MM,
    MIN_WALL_SCOOP_DEPTH_MM,
    build_cut,
    build_floor_scoop,
    build_scoop,
    build_through_hole,
    build_wall_scoop,
)
from pyboxbuilder.compartments.finger_outline import (
    ARC_SAMPLES,
    BASE_ARC_SHARE,
    DEFAULT_BOTTOM_ROUNDING_RATIO,
    DEFAULT_MOUTH_ROUNDING_MM,
    DEFAULT_TOP_ROUNDING_RATIO,
    MIN_FLAT_BOTTOM_RATIO,
    RIM_OVERSHOOT_MM,
    TOP_ROLL_RISE_RATIO,
    TOUCHING_TOLERANCE_MM,
    CutProfile,
    _angle_at,
    _elliptical_quarter,
    _fit_radii,
    _quarter_arc,
    _sweep_end,
    _tangent_join,
    dish_radius,
    floor_bore_outline,
    floor_bore_profile,
    scoop_outline,
    scoop_profile,
    window_outline,
)
from pyboxbuilder.compartments.finger_sweep import (
    DEFAULT_EDGE_ROUNDING_MM,
    FaceTreatment,
    _sweep_through_wall,
    scoop_face_flare,
)

__all__ = [
    "ARC_SAMPLES",
    "BASE_ARC_SHARE",
    "DEFAULT_BOTTOM_ROUNDING_RATIO",
    "DEFAULT_EDGE_ROUNDING_MM",
    "DEFAULT_FLOOR_DIP_MM",
    "DEFAULT_MOUTH_ROUNDING_MM",
    "DEFAULT_TOP_ROUNDING_RATIO",
    "MIN_FLAT_BOTTOM_RATIO",
    "MIN_WALL_SCOOP_DEPTH_MM",
    "RIM_OVERSHOOT_MM",
    "TOP_ROLL_RISE_RATIO",
    "TOUCHING_TOLERANCE_MM",
    "CutProfile",
    "FaceTreatment",
    "build_cut",
    "build_floor_scoop",
    "build_scoop",
    "build_through_hole",
    "build_wall_scoop",
    "dish_radius",
    "floor_bore_outline",
    "floor_bore_profile",
    "scoop_face_flare",
    "scoop_outline",
    "scoop_profile",
    "window_outline",
]
