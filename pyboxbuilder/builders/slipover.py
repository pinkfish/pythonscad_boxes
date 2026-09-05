# SPDX-License-Identifier: Apache-2.0
"""SlipoverBoxBuilder — typed builder for slipover lid boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class SlipoverBoxBuilder(BoxBuilder):
    """Builder for slipover lid box type.

    Example:
        .. pythonscad-example::

            project = Project("SlipoverDemo", game_box_size=(80.0, 80.0, 35.0))
            project.box(
                BoxType.SLIPOVER,
                "MiniDeck",
                size=(55.0, 70.0, 26.0),
                lid=LidBuilder(
                    pattern=PatternBuilder(PatternType.CIRCLE),
                    text="CARDS",
                ),
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.SLIPOVER

    foot: float = 0.0
    """Height of the exposed base the sleeve stops against, in mm. 0 = the
    sleeve covers the whole body."""
    slip: float = 1.6
    """Thickness of the sleeve wall that wraps the body."""
