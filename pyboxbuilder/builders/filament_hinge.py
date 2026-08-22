# SPDX-License-Identifier: Apache-2.0
"""FilamentHingeBoxBuilder — typed builder for living-hinge lid boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class FilamentHingeBoxBuilder(BoxBuilder):
    """Builder for filament (living) hinge lid box type."""

    box_type: ClassVar[BoxType] = BoxType.FILAMENT_HINGE
    hinge_catch_type: str = "ridge"
    """Catch type for hinged boxes; 'ridge' or 'bump'."""
