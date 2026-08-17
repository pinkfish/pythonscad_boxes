# SPDX-License-Identifier: Apache-2.0
"""HingeBoxBuilder — typed builder for pin-hinge lid boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class HingeBoxBuilder(BoxBuilder):
    """Builder for pin-hinge lid box type."""

    box_type: ClassVar[BoxType] = BoxType.HINGE
    hinge_count: int | None = None
    """Knuckles across the hinge; ``None`` uses the geometry's own default."""
    hinge_pin_diameter: float | None = None
    """Pin stock diameter in mm; ``None`` uses the geometry's own default."""
