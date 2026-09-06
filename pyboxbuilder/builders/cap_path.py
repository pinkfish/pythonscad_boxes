# SPDX-License-Identifier: Apache-2.0
"""CapPathBoxBuilder — typed builder for cap-path lid boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class CapPathBoxBuilder(BoxBuilder):
    """Builder for cap-path lid box type.

    Example:
        .. pythonscad-example::

            project = Project("CapPathDemo", game_box_size=(80.0, 80.0, 30.0))
            l_path = (
                (0.0, 0.0),
                (55.0, 0.0),
                (55.0, 25.0),
                (25.0, 25.0),
                (25.0, 55.0),
                (0.0, 55.0),
            )
            project.box(
                BoxType.CAP_PATH,
                "CapPathTray",
                size=(55.0, 55.0, 20.0),
                path=l_path,
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.CAP_PATH

    path: tuple[tuple[float, float], ...] = ()
    """Closed 2D outline of the tray footprint, in mm, in the box's own frame."""
    cap_height: float | None = None
    """Skirt height in mm; None derives it from the box height."""
