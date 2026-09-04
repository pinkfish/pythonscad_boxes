# SPDX-License-Identifier: Apache-2.0
"""Tests for the sleeve catalog."""

from __future__ import annotations

import contextlib

from pyboxbuilder.sleeves import (
    BRANDS,
    SLEEVE_CATALOG,
    Sleeve,
    find_sleeve,
    sleeve_by_sku,
    sleeves_for_card,
)


def test_catalog_covers_all_three_brands() -> None:
    assert BRANDS == ("Sleeve Kings", "Gamegenic", "Mayday Games")
    assert len(SLEEVE_CATALOG) > 50


def test_only_generic_sizes_are_listed() -> None:
    """No game-specific sets — only the actual sleeve size names."""
    names = {s.name for s in SLEEVE_CATALOG}
    assert names == {
        "Mini American",
        "Mini Chimera",
        "Mini European",
        "Standard American",
        "Chimera",
        "Standard European",
        "Standard Card Game",
        "Square",
        "Square Large",
        "Tarot",
        "Magnum",
        "Lost Cities Magnum",
        "Oversized",
        "54x80",
        "Retro",
    }


def test_every_entry_has_outer_and_card_dimensions() -> None:
    for sleeve in SLEEVE_CATALOG:
        assert sleeve.card_width > 0
        assert sleeve.card_length > 0
        assert sleeve.sleeve_size[0] > sleeve.card_width
        assert sleeve.sleeve_size[1] > sleeve.card_length


def test_gamegenic_publishes_its_own_sleeve_dimensions() -> None:
    retro = next(s for s in SLEEVE_CATALOG if s.brand == "Gamegenic" and s.name == "Retro")
    assert retro.sleeve_size == (66.5, 94.0)
    mini = next(s for s in SLEEVE_CATALOG if s.brand == "Gamegenic" and s.name == "Mini American")
    assert mini.sleeve_size == (44.0, 67.0)


def test_standard_card_game_is_found_across_brands() -> None:
    matches = sleeves_for_card(63.5, 88.0)
    brands = {s.brand for s in matches}
    assert {"Sleeve Kings", "Gamegenic", "Mayday Games"} <= brands


def test_sleeves_for_card_filters_by_brand() -> None:
    matches = sleeves_for_card(44.0, 68.0, brand="mayday games")
    assert matches
    assert all(s.brand == "Mayday Games" for s in matches)
    assert any(s.name == "Mini European" for s in matches)


def test_sleeves_for_card_filters_by_grade() -> None:
    matches = sleeves_for_card(63.5, 88.0, brand="Sleeve Kings", grade="Premium")
    assert matches
    assert all(s.grade == "Premium" for s in matches)
    assert matches[0].thickness_microns == 100


def test_too_large_card_returns_no_sleeves() -> None:
    assert sleeves_for_card(500.0, 500.0) == ()


def test_fits_is_inclusive_at_the_maximum() -> None:
    sleeve = sleeve_by_sku("SKS-8810")
    assert sleeve is not None
    assert sleeve.fits(63.5, 88.0)
    assert not sleeve.fits(63.6, 88.0)


def test_footprint_margin_is_sleeve_minus_card() -> None:
    sleeve = sleeve_by_sku("SKS-8810")  # card 63.5x88, sleeve 66x91
    assert sleeve is not None
    assert sleeve.footprint_margin == 3.0


def test_card_thickness_derivation() -> None:
    premium = sleeve_by_sku("SKS-9905")  # 100 micron
    assert premium is not None
    assert premium.card_thickness == 0.40
    standard = sleeve_by_sku("SKS-8810")  # 60 micron
    assert standard is not None
    assert standard.card_thickness == 0.36


def test_sleeve_by_sku_missing_returns_none() -> None:
    assert sleeve_by_sku("NOPE") is None


def test_find_sleeve_looks_up_a_specific_sleeve() -> None:
    sleeve = find_sleeve("Gamegenic", "Standard American")
    assert sleeve is not None
    assert sleeve.sleeve_size == (59.0, 91.0)
    assert sleeve.grade == "Prime / Matte"
    assert find_sleeve("Gamegenic", "Nope") is None


def test_find_sleeve_disambiguates_by_grade() -> None:
    standard = find_sleeve("Mayday Games", "Mini European", grade="Standard")
    premium = find_sleeve("Mayday Games", "Mini European", grade="Premium")
    assert standard is not None and premium is not None
    assert standard.thickness_microns == 40
    assert premium.thickness_microns == 90


def test_sleeve_is_frozen() -> None:
    sleeve = Sleeve("X", "Y", (1.0, 2.0), (3.0, 4.0))
    with contextlib.suppress(Exception):
        sleeve.card_size = (3.0, 4.0)  # type: ignore[misc]
    assert sleeve.card_size == (1.0, 2.0)
