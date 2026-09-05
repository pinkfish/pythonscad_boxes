# SPDX-License-Identifier: Apache-2.0
"""MagneticBoxBuilder — typed builder for magnetic-closure lid boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class MagneticBoxBuilder(BoxBuilder):
    """Builder for magnetic-closure lid box type.

    Example:
        .. pythonscad-example::

            project = Project("MagneticDemo", game_box_size=(80.0, 80.0, 30.0))
            project.box(
                BoxType.MAGNETIC,
                "Vault",
                size=(60.0, 60.0, 22.0),
                magnet_type=MagnetType.ROUND,
                magnet_diameter=6.0,
                magnet_height=3.0,
                lid=LidBuilder(text="VAULT"),
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.MAGNETIC
    magnet_diameter: float = 6.0
    magnet_height: float = 3.0
    magnet_count_width: int = 2
    magnet_count_length: int = 2
