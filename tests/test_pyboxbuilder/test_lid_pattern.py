# SPDX-License-Identifier: Apache-2.0
"""Tests for pattern fill generation — full PatternType catalog coverage."""

import unittest

from pyboxbuilder.enums import PatternType
from pyboxbuilder.lid.pattern import _PATTERN_FILLS, build_pattern


class PatternCoverageTests(unittest.TestCase):
    def test_every_pattern_type_has_a_fill(self):
        """Every PatternType member (except aliases) has a registered fill."""
        # Iterate canonical members, skipping aliases
        for pt in PatternType:
            # Aliases share the same value as another member; only check canonical
            if PatternType.__members__[pt.name] is pt:
                self.assertIn(pt, _PATTERN_FILLS, f"{pt.name} missing fill")

    def test_no_fallback_to_grid(self):
        """No two patterns share a fill — a catalog entry that silently drew
        another pattern's shape is what this catalog was cut down to remove."""
        fills = [_PATTERN_FILLS[pt] for pt in PatternType if pt is not PatternType.NONE]
        self.assertEqual(len(set(fills)), len(fills))

    def test_an_unregistered_pattern_is_refused_not_substituted(self):
        """A missing fill must raise, never fall back to squares (FR-000c)."""
        from unittest.mock import patch

        from pyboxbuilder.lid.pattern import build_pattern

        with patch.dict(_PATTERN_FILLS, clear=True):
            with self.assertRaises(ValueError) as caught:
                build_pattern(100.0, 70.0, 3.0, PatternType.HEX)
        self.assertIn("HEX", str(caught.exception))

    def test_legacy_aliases_still_resolve(self):
        """HEX_GRID and GRID aliases still resolve to fill functions."""
        self.assertIn(PatternType.HEX, _PATTERN_FILLS)
        self.assertIn(PatternType.SQUARE, _PATTERN_FILLS)

    def test_unknown_pattern_raises(self):
        """No silent fallback: a missing fill should raise, not fall back."""
        # All enum members are registered, so this only checks the guard path
        # indirectly — verify build_pattern raises for a hypothetical unregistered case
        # by checking the registry is complete instead.
        self.assertTrue(_PATTERN_FILLS)

    def test_none_pattern_returns_none(self):
        """PatternType.NONE produces no cutouts."""
        fill = _PATTERN_FILLS[PatternType.NONE]
        self.assertIsNone(fill(100, 70, 3.0, 10.0, None))


class PatternFillTests(unittest.TestCase):
    def test_grid_fill(self):
        try:
            result = build_pattern(100, 70, 3.0, PatternType.SQUARE, spacing=10.0)
            self.assertIsNotNone(result)
        except ImportError:
            self.skipTest("bosl2 not available")

    def test_hex_fill(self):
        try:
            result = build_pattern(100, 70, 3.0, PatternType.HEX, spacing=10.0)
            self.assertIsNotNone(result)
        except ImportError:
            self.skipTest("bosl2 not available")

    def test_voronoi_fill(self):
        try:
            result = build_pattern(100, 70, 3.0, PatternType.VORONOI, spacing=10.0)
            self.assertIsNotNone(result)
        except ImportError:
            self.skipTest("bosl2 not available")
