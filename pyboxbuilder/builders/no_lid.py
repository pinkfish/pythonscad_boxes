# SPDX-License-Identifier: Apache-2.0
"""NoLidBoxBuilder and PathBoxBuilder — typed builders for no-lid box types."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class NoLidBoxBuilder(BoxBuilder):
    """Builder for no-lid box type (open tray).

    Example:
        .. pythonscad-example::

            project = Project("StackDemo", game_box_size=(80.0, 80.0, 40.0))
            b1 = project.box(
                BoxType.NO_LID,
                "TrayLower",
                size=(60.0, 60.0, 16.0),
                position=(0.0, 0.0, 0.0),
                stackable=StackableMode.INSIDE,
            )
            b2 = project.box(
                BoxType.NO_LID,
                "TrayUpper",
                size=(60.0, 60.0, 16.0),
                position=(0.0, 0.0, 16.0),
                stackable=StackableMode.INSIDE,
            )
            project.show()
    """

    box_type: ClassVar[BoxType] = BoxType.NO_LID
