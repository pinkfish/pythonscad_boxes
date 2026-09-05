# SPDX-License-Identifier: Apache-2.0
"""SlipoverPathBoxBuilder — typed builder for slipover path lid boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class SlipoverPathBoxBuilder(BoxBuilder):
    """Builder for slipover-path lid box type.

    Example:
        .. pythonscad-example::

            project = Project("SlipPathDemo", game_box_size=(80.0, 80.0, 30.0))
            l_path = (
                (0.0, 0.0),
                (55.0, 0.0),
                (55.0, 25.0),
                (25.0, 25.0),
                (25.0, 55.0),
                (0.0, 55.0),
            )
            project.box(
                BoxType.SLIPOVER_PATH,
                "SlipPathTray",
                size=(55.0, 55.0, 20.0),
                path=l_path,
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.SLIPOVER_PATH

    path: tuple[tuple[float, float], ...] = ()
    """Closed 2D outline of the tray footprint, in mm, in the box's own frame."""
    foot: float = 0.0
    """Height of the exposed base the sleeve stops against, in mm."""
    slip: float = 1.6
    """Thickness of the sleeve wall that wraps the body."""
