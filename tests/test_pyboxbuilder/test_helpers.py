# SPDX-License-Identifier: Apache-2.0
"""Tests for Sleeve and Card standards helpers."""

from __future__ import annotations

from pyboxbuilder.helpers import CardSize, CardSpec, SleeveType


def test_sleeve_type_properties() -> None:
    """Verify sleeve type footprint margins and thickness multipliers."""
    assert SleeveType.UNSLEEVED.footprint_margin == 1.0
    assert SleeveType.UNSLEEVED.card_thickness == 0.20

    assert SleeveType.STANDARD_60MY.footprint_margin == 2.5
    assert SleeveType.STANDARD_60MY.card_thickness == 0.26

    assert SleeveType.PREMIUM_100MY.footprint_margin == 3.5
    assert SleeveType.PREMIUM_100MY.card_thickness == 0.32

    assert SleeveType.DOUBLE_SLEEVED.footprint_margin == 5.0
    assert SleeveType.DOUBLE_SLEEVED.card_thickness == 0.40


def test_card_spec_calculation() -> None:
    """Verify CardSpec deck footprint and depth calculations."""
    # Test unsleeved standard cards
    spec = CardSpec(CardSize.STANDARD_GAME, count=100, sleeve=SleeveType.UNSLEEVED)
    assert spec.width == 64.5
    assert spec.length == 89.0
    assert spec.depth == 20.0
    assert spec.as_tuple() == (64.5, 89.0, 20.0)

    # Test premium sleeved tarot cards
    spec_tarot = CardSpec(CardSize.TAROT, count=50, sleeve=SleeveType.PREMIUM_100MY)
    assert spec_tarot.width == 73.5
    assert spec_tarot.length == 123.5
    assert spec_tarot.depth == 16.0
    assert spec_tarot.as_tuple() == (73.5, 123.5, 16.0)

    # Test custom card sizes
    spec_custom = CardSpec((50.0, 50.0), count=10, sleeve=SleeveType.DOUBLE_SLEEVED)
    assert spec_custom.width == 55.0
    assert spec_custom.length == 55.0
    assert spec_custom.depth == 4.0
