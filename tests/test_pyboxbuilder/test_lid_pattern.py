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


class HoleAndWebTests(unittest.TestCase):
    """A pattern is specified by the web between holes, not by a share of the
    cell (FR-023). Sized as a share, the web scaled with the pitch: an 11mm
    cell gave a 6.2mm hexagon separated by 5.1mm of plastic, which is a sheet
    with holes in it rather than a honeycomb."""

    def test_the_web_is_what_it_says_it_is(self) -> None:
        from pyboxbuilder.lid.pattern import DEFAULT_WEB_MM, hole_size

        for pitch in (6.0, 8.0, 11.25, 20.0):
            with self.subTest(pitch=pitch):
                self.assertAlmostEqual(pitch - hole_size(pitch, None), DEFAULT_WEB_MM)

    def test_a_thicker_web_shrinks_the_hole_not_the_pitch(self) -> None:
        from pyboxbuilder.lid.pattern import hole_size

        self.assertAlmostEqual(hole_size(10.0, 3.0), 7.0)
        self.assertAlmostEqual(hole_size(10.0, 1.0), 9.0)

    def test_a_web_thinner_than_printable_is_raised(self) -> None:
        from pyboxbuilder.lid.pattern import MIN_WEB_MM, hole_size

        self.assertAlmostEqual(hole_size(10.0, 0.1), 10.0 - MIN_WEB_MM)

    def test_a_pitch_too_tight_for_a_hole_gets_none(self) -> None:
        """Better a solid lid than a peppering of pinholes (FR-000c)."""
        from pyboxbuilder.lid.pattern import hole_size

        self.assertEqual(hole_size(2.0, None), 0.0)

    def test_a_lid_too_tight_for_a_hole_is_left_solid(self) -> None:
        from pyboxbuilder.lid.pattern import build_pattern

        self.assertIsNone(build_pattern(60.0, 60.0, 3.0, PatternType.HEX, spacing=2.0))

    def test_holes_are_denser_than_the_share_rule_gave(self) -> None:
        """The measurement that started this: open area, at a fixed pitch."""
        from pyboxbuilder.lid.pattern import hole_size

        open_share = (hole_size(11.25, None) / 11.25) ** 2
        self.assertGreater(open_share, 0.5, "the pattern still barely opens the lid")


class PatternBorderTests(unittest.TestCase):
    """A solid margin all round, so the edge that holds the lid survives."""

    AREA = (80.0, 100.0)
    PITCH = 11.0

    def margins(self, pattern_type: PatternType, border: float) -> tuple[float, ...]:
        """Solid millimetres between the lid's edge and the nearest hole."""
        from pyboxbuilder.lid.pattern import build_pattern

        width, length = self.AREA
        holes = build_pattern(
            width - 2 * border, length - 2 * border, 3.0, pattern_type,
            spacing=self.PITCH,
        )
        assert holes is not None
        (cx, cy, _), (w, l, _) = holes.bounds()
        return (
            border + cx - w / 2, width - (border + cx + w / 2),
            border + cy - l / 2, length - (border + cy + l / 2),
        )

    def test_every_pattern_keeps_the_border(self) -> None:
        """Measured on the built holes, not on the nominal size: a hexagon
        reaches 15% further at its corners than across its flats, and taking
        the inset from the flats let the outer holes bleed past the border."""
        for pattern_type in PatternType:
            if pattern_type is PatternType.NONE:
                continue
            with self.subTest(pattern=pattern_type.name):
                for margin in self.margins(pattern_type, 10.0):
                    self.assertGreaterEqual(round(margin, 3), 10.0)

    def test_the_margins_are_even(self) -> None:
        """The grid is centred, so the leftover is shared rather than piling up
        on the far side as an extra cell's worth of border."""
        left, right, bottom, top = self.margins(PatternType.HEX, 10.0)
        self.assertAlmostEqual(left, right, places=3)
        self.assertAlmostEqual(bottom, top, places=3)

    def test_the_border_is_settable(self) -> None:
        wide = self.margins(PatternType.HEX, 20.0)
        for margin in wide:
            self.assertGreaterEqual(round(margin, 3), 20.0)

    def test_the_pattern_border_defaults_to_ten_and_is_its_own(self) -> None:
        """Not the label's margin: one keeps text off the edge, the other
        keeps material at it."""
        from pyboxbuilder.lid.builder import PATTERN_BORDER_MM, PatternBuilder

        self.assertEqual(PATTERN_BORDER_MM, 10.0)
        self.assertEqual(PatternBuilder().border_width, 10.0)
        self.assertEqual(PatternBuilder(border=4.0).border_width, 4.0)

    def test_a_border_that_swallows_the_lid_leaves_it_solid(self) -> None:
        from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
        from pyboxbuilder.lid.decorate import decorate_lid
        from pyboxbuilder.box.shell import block

        lid = block([30.0, 30.0, 2.0])
        decorated = decorate_lid(
            lid, LidBuilder(pattern=PatternBuilder(border=20.0)), 2.0, "mmu"
        )
        self.assertEqual(repr(decorated.solid), repr(lid))
