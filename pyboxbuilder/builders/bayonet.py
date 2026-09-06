# SPDX-License-Identifier: Apache-2.0
"""BayonetBoxBuilder — typed builder for twist-lock bayonet containers."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class BayonetBoxBuilder(BoxBuilder):
    """Builder for twist-lock bayonet container type (FR-082).

    Designed for cylindrical or rounded footprints, the lid and body mate via a
    quarter-turn (90°) or eighth-turn (45°) bayonet mechanism with vertical entry
    keyways and horizontal retention channels.

    Example:
        .. pythonscad-example::

            project = Project("BayonetDemo", game_box_size=(80.0, 80.0, 50.0))
            project.box(
                BoxType.BAYONET,
                "TokenCanister",
                size=(60.0, 60.0, 40.0),
                lug_count=4,
                turn_angle=90.0,
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.BAYONET
    lug_count: int = 4
    """Number of bayonet retention lugs (typically 2, 3, or 4)."""
    turn_angle: float = 90.0
    """Twist angle in degrees to lock/unlock (typically 45° or 90°)."""
    lug_height: float = 2.5
    """Height of each retention lug in mm."""
    lug_depth: float = 1.2
    """Radial engagement depth of each lug in mm."""
    bayonet_slack: float = 0.3
    """Clearance between lugs and retention channels in mm."""
    round_footprint: bool = True
    """Use a true cylindrical profile rather than rounded rectangle."""
