# SPDX-License-Identifier: Apache-2.0
"""Sleeve and Card standards helpers for pyboxbuilder."""

from __future__ import annotations

from enum import Enum


class SleeveType(Enum):
    """Sleeve weight and margin presets."""

    UNSLEEVED = "unsleeved"
    STANDARD_60MY = "standard_60"
    PREMIUM_100MY = "premium_100"
    DOUBLE_SLEEVED = "double"

    @property
    def footprint_margin(self) -> float:
        """Footprint margin to add to card width and length (mm)."""
        match self:
            case SleeveType.UNSLEEVED:
                return 1.0
            case SleeveType.STANDARD_60MY:
                return 2.5
            case SleeveType.PREMIUM_100MY:
                return 3.5
            case SleeveType.DOUBLE_SLEEVED:
                return 5.0

    @property
    def card_thickness(self) -> float:
        """Thickness of a single card including sleeve (mm)."""
        match self:
            case SleeveType.UNSLEEVED:
                return 0.20
            case SleeveType.STANDARD_60MY:
                return 0.26
            case SleeveType.PREMIUM_100MY:
                return 0.32
            case SleeveType.DOUBLE_SLEEVED:
                return 0.40


class CardSize(Enum):
    """Standard card sizes (width, length) in mm."""

    STANDARD_GAME = (63.5, 88.0)
    TAROT = (70.0, 120.0)
    MINI_AMERICAN = (41.0, 63.0)
    MINI_EUROPEAN = (44.0, 68.0)
    SQUARE_MEDIUM = (70.0, 70.0)
    OVERSIZED = (80.0, 120.0)


class CardSpec:
    """Calculates width, length, and depth for a deck of cards based on sleeve type."""

    def __init__(
        self,
        card_size: CardSize | tuple[float, float],
        count: int,
        sleeve: SleeveType = SleeveType.UNSLEEVED,
    ) -> None:
        """Initialize CardSpec.

        Args:
            card_size: CardSize enum or custom (width, length) tuple in mm.
            count: Number of cards in the deck.
            sleeve: SleeveType selection.

        """
        self.card_size = card_size
        self.count = count
        self.sleeve = sleeve

    @property
    def width(self) -> float:
        """Width of the sleeved card deck (mm)."""
        base_w = self.card_size.value[0] if isinstance(self.card_size, CardSize) else self.card_size[0]
        return base_w + self.sleeve.footprint_margin

    @property
    def length(self) -> float:
        """Length of the sleeved card deck (mm)."""
        base_l = self.card_size.value[1] if isinstance(self.card_size, CardSize) else self.card_size[1]
        return base_l + self.sleeve.footprint_margin

    @property
    def depth(self) -> float:
        """Depth of the sleeved card deck (mm)."""
        return self.count * self.sleeve.card_thickness

    def as_tuple(self) -> tuple[float, float, float]:
        """Return (width, length, depth) tuple."""
        return (self.width, self.length, self.depth)
