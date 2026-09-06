# SPDX-License-Identifier: Apache-2.0
"""CardLibraryBoxBuilder — typed builder for card-library box type."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder, SlidingLidFields
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class CardLibraryBoxBuilder(SlidingLidFields, BoxBuilder):
    """Builder for card-library box type.

    Example:
        .. pythonscad-example::

            project = Project("CardLibDemo", game_box_size=(80.0, 100.0, 35.0))
            project.box(
                BoxType.CARD_LIBRARY,
                "Deck",
                size=(55.0, 80.0, 25.0),
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.CARD_LIBRARY
