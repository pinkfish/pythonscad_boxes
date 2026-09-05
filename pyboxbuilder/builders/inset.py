# SPDX-License-Identifier: Apache-2.0
"""InsetBoxBuilder — typed builder for inset lid boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class InsetBoxBuilder(BoxBuilder):
    """Builder for inset lid box type.

    Example:
        .. pythonscad-example::

            project = Project("InsetDemo", game_box_size=(80.0, 80.0, 30.0))
            project.box(
                BoxType.INSET,
                "FlushTray",
                size=(60.0, 60.0, 22.0),
                lid=LidBuilder(text="TILES"),
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.INSET
