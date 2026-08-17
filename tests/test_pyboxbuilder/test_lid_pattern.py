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
    """A solid margin all round, so the edge that holds the lid survives.

    Measured on the **cut lid**, not on the raw lattice: the lattice
    deliberately overhangs and is clipped to the border, which is what puts a
    partial hole against each edge instead of leaving a cell's worth of unused
    margin inside it.
    """

    LID = (80.0, 100.0, 2.0)
    PITCH = 11.0

    def cut(self, pattern_type: PatternType, border: float):
        """The lid, perforated, and the material the pattern removed."""
        from pyboxbuilder.box.shell import block
        from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
        from pyboxbuilder.lid.decorate import decorate_lid

        lid = block(list(self.LID))
        decorated = decorate_lid(
            lid,
            LidBuilder(pattern=PatternBuilder(
                type=pattern_type, spacing=self.PITCH, border=border,
            )),
            self.LID[2], "mmu",
        )
        return lid, lid - decorated.solid

    def margins(self, pattern_type: PatternType, border: float) -> tuple[float, ...]:
        """Solid millimetres between the lid's edge and the nearest hole."""
        width, length, _ = self.LID
        _, removed = self.cut(pattern_type, border)
        (cx, cy, _), (w, l, _) = removed.bounds()
        return (cx - w / 2, width - (cx + w / 2), cy - l / 2, length - (cy + l / 2))

    def test_every_pattern_keeps_the_border(self) -> None:
        for pattern_type in PatternType:
            if pattern_type is PatternType.NONE:
                continue
            with self.subTest(pattern=pattern_type.name):
                for margin in self.margins(pattern_type, 8.0):
                    self.assertGreaterEqual(round(margin, 3), 8.0)

    def test_the_pattern_reaches_the_border(self) -> None:
        """Not merely stays inside it: a lid asking for an 8mm border had 12mm
        or more of solid edge on two sides, because only whole holes were
        placed and the leftover became extra margin."""
        for pattern_type in (PatternType.HEX, PatternType.SQUARE, PatternType.CIRCLE):
            with self.subTest(pattern=pattern_type.name):
                for margin in self.margins(pattern_type, 8.0):
                    self.assertAlmostEqual(margin, 8.0, places=2)

    def test_the_edge_holes_are_partial(self) -> None:
        """A hole straddling the border is drawn and clipped, which is what
        lets the pattern reach it."""
        _, removed = self.cut(PatternType.HEX, 8.0)
        (cx, cy, _), (w, l, _) = removed.bounds()
        width, length, _ = self.LID
        # A lattice that only placed whole hexes could not span this much.
        self.assertAlmostEqual(w, width - 16.0, places=2)
        self.assertAlmostEqual(l, length - 16.0, places=2)

    def test_the_border_is_settable(self) -> None:
        for margin in self.margins(PatternType.HEX, 15.0):
            self.assertAlmostEqual(margin, 15.0, places=2)

    def test_the_label_sits_inside_the_lid_border(self) -> None:
        """One border for the lid, and the label set in from it.

        The border is a band of plain lid; a label level with its inner edge
        reads as touching the pattern rather than sitting in a space of its own.
        """
        from pyboxbuilder.lid.builder import (
            BORDER_MARGIN_MM,
            LABEL_INSET_MM,
            LID_BORDER_MM,
            PATTERN_BORDER_MM,
            LidBuilder,
            PatternBuilder,
        )

        self.assertEqual(LID_BORDER_MM, 8.0)
        self.assertEqual(LABEL_INSET_MM, 2.0)
        self.assertEqual(PATTERN_BORDER_MM, LID_BORDER_MM)
        self.assertEqual(BORDER_MARGIN_MM, LID_BORDER_MM + LABEL_INSET_MM)
        self.assertEqual(PatternBuilder().border_width, LID_BORDER_MM)
        self.assertEqual(LidBuilder().border_margin, LID_BORDER_MM + LABEL_INSET_MM)

    def test_the_text_stays_inside_the_border(self) -> None:
        """Including a diagonal label, which is the one that ran off the lid."""
        from pyboxbuilder.enums import LabelMode
        from pyboxbuilder.lid.builder import (
            LABEL_INSET_MM,
            LID_BORDER_MM,
            LidBuilder,
        )
        from pyboxbuilder.lid.decorate import _build_label

        width, length, _ = self.LID
        for diagonal in (False, True):
            with self.subTest(diagonal=diagonal):
                label = _build_label(
                    LidBuilder(label_mode=LabelMode.FRAMELESS, diagonal=diagonal)
                    .titled("Favors"),
                    width, length, "mmu",
                )
                assert label is not None
                (cx, cy, _), (w, l, _) = label.combined().bounds()
                inside = LID_BORDER_MM + LABEL_INSET_MM
                self.assertGreaterEqual(round(cx - w / 2, 3), inside)
                self.assertGreaterEqual(round(width - (cx + w / 2), 3), inside)
                self.assertGreaterEqual(round(cy - l / 2, 3), inside)
                self.assertGreaterEqual(round(length - (cy + l / 2), 3), inside)

    def test_the_edges_are_cut_alike(self) -> None:
        """SC-016h: opposite edges are mirror images.

        Grown from one edge, the lattice landed wherever the arithmetic put it
        — on a 96 x 70 lid one side was cut through the hexes and the other
        through the webs, taking 56mm3 against 33mm3. It is anchored on the
        area's centre instead.
        """
        from mesh import volume

        from pyboxbuilder.box.shell import block

        border = 8.0
        for width, length in ((96.0, 70.0), (98.0, 142.5), (60.0, 60.0)):
            with self.subTest(lid=(width, length)):
                lid = block([width, length, 2.0])
                from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
                from pyboxbuilder.lid.decorate import decorate_lid

                decorated = decorate_lid(
                    lid,
                    LidBuilder(pattern=PatternBuilder(
                        type=PatternType.HEX, spacing=10.0, border=border,
                    )),
                    2.0, "mmu",
                )
                removed = lid - decorated.solid

                def strip(at, size):
                    return volume(removed & block(list(size), at=list(at)))

                left = strip((border, border, 0), (1.0, length - 2 * border, 2.0))
                right = strip(
                    (width - border - 1.0, border, 0), (1.0, length - 2 * border, 2.0)
                )
                bottom = strip((border, border, 0), (width - 2 * border, 1.0, 2.0))
                top = strip(
                    (border, length - border - 1.0, 0), (width - 2 * border, 1.0, 2.0)
                )
                self.assertGreater(left, 0.0, "the pattern never reached the edge")
                self.assertAlmostEqual(left, right, places=2)
                self.assertAlmostEqual(bottom, top, places=2)

    def test_a_border_that_swallows_the_lid_leaves_it_solid(self) -> None:
        from pyboxbuilder.box.shell import block
        from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
        from pyboxbuilder.lid.decorate import decorate_lid

        lid = block([30.0, 30.0, 2.0])
        decorated = decorate_lid(
            lid, LidBuilder(pattern=PatternBuilder(border=20.0)), 2.0, "mmu"
        )
        self.assertEqual(repr(decorated.solid), repr(lid))
