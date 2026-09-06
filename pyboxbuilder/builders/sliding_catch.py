# SPDX-License-Identifier: Apache-2.0
"""SlidingCatchBoxBuilder — typed builder for sliding-catch lid boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder, SlidingLidFields
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class SlidingCatchBoxBuilder(SlidingLidFields, BoxBuilder):
    """Builder for sliding-catch lid box type.

    Example:
        .. pythonscad-example::

            project = Project("CatchDemo", game_box_size=(80.0, 80.0, 30.0))
            project.box(
                BoxType.SLIDING_CATCH,
                "CatchBox",
                size=(60.0, 60.0, 22.0),
                lid=LidBuilder(text="LOCKED"),
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.SLIDING_CATCH
