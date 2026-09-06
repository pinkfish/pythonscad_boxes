# SPDX-License-Identifier: Apache-2.0
"""CardShoeBoxBuilder — typed builder for angled draw & discard card shoes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class CardShoeBoxBuilder(BoxBuilder):
    """Builder for angled draw & discard card shoe tray (FR-085).

    In-game tabletop utility tray with adjacent draw and discard wells.
    The draw well features a backward-slanted floor and backrest (15°–25° from
    vertical) with a low front retaining lip to prevent tall draw stacks from
    toppling, and an optional flat discard well with opposing U-shaped edge finger scoops.

    Example:
        .. pythonscad-example::

            project = Project("CardShoeDemo", game_box_size=(160.0, 120.0, 70.0))
            project.box(
                BoxType.CARD_SHOE,
                "MarketDeck",
                size=(150.0, 100.0, 50.0),
                draw_angle=20.0,
                retaining_lip_height=12.0,
                discard_well=True,
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.CARD_SHOE
    draw_angle: float = 20.0
    """Backward slant angle of the draw well in degrees (15°–25°)."""
    retaining_lip_height: float = 10.0
    """Height of the front retaining lip preventing cards from sliding out."""
    discard_well: bool = True
    """Include an adjacent flat discard well alongside the draw well."""
