# SPDX-License-Identifier: Apache-2.0
"""CapBoxBuilder — typed builder for friction-fit cap lid boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class CapBoxBuilder(BoxBuilder):
    """Builder for cap (friction-fit) lid box type.

    Example:
        .. pythonscad-example::

            project = Project("CapDemo", game_box_size=(80.0, 80.0, 30.0))
            box = project.box(
                BoxType.CAP,
                "PlayerTray",
                size=(60.0, 60.0, 22.0),
                lid=LidBuilder(text="PLAYER 1"),
            )
            box.compartment("LeftWell", width_ratio=0.5)
            box.compartment("RightWell", width_ratio=0.5)
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.CAP
    cap_height: float | None = None
    """Skirt height in mm; ``None`` derives it from the box height."""
