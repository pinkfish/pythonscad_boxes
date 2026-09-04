# SPDX-License-Identifier: Apache-2.0
"""Tests for LidBuilder and PatternBuilder."""

import unittest

from pyboxbuilder.enums import LabelMode, PatternType
from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder


class PatternBuilderTests(unittest.TestCase):
    def test_defaults(self) -> None:
        pb = PatternBuilder()
        self.assertEqual(pb.type, PatternType.HEX)
        self.assertEqual(pb.colors, ())
        self.assertIsNone(pb.spacing)


class LidBuilderTests(unittest.TestCase):
    def test_defaults(self) -> None:
        lb = LidBuilder()
        self.assertIsNone(lb.text)
        # Unset, so a per-mode override can tell it from a stated FRAMED.
        self.assertIsNone(lb.label_mode)
        self.assertEqual(lb.mode, LabelMode.FRAMED)
        self.assertFalse(lb.is_diagonal)
        self.assertIsNone(lb.text_color)
        self.assertIsNone(lb.frame_color)
        self.assertEqual(lb.pattern.type, PatternType.DENSE_HEX)
        self.assertIsNone(lb.pattern_color)
        self.assertEqual(lb.min_text_height, 4.0)
        # The lid's border, plus the label's own 2mm inset inside it (FR-023).
        self.assertEqual(lb.border_margin, 10.0)

    def test_with_text(self) -> None:
        lb = LidBuilder(text="Cards")
        self.assertEqual(lb.text, "Cards")

    def test_frameless_diagonal(self) -> None:
        lb = LidBuilder(
            text="TOKENS",
            label_mode=LabelMode.FRAMELESS,
            diagonal=True,
        )
        self.assertEqual(lb.label_mode, LabelMode.FRAMELESS)
        self.assertTrue(lb.diagonal)

    def test_with_pattern(self) -> None:
        pb = PatternBuilder(type=PatternType.SQUARE, spacing=10.0)
        lb = LidBuilder(text="Test", pattern=pb)
        self.assertIsNotNone(lb.pattern)
        self.assertEqual(lb.pattern.type, PatternType.SQUARE)

    def test_per_mode_override_mmu(self) -> None:
        """mmu_label overrides parent for MMU mode."""
        parent = LidBuilder(
            text="Cards",
            label_mode=LabelMode.FRAMED,
            mmu_label=LidBuilder(text="Cards", label_mode=LabelMode.FRAMELESS),
        )
        resolved = parent.for_mode("mmu")
        self.assertEqual(resolved.label_mode, LabelMode.FRAMELESS)
        self.assertEqual(resolved.text, "Cards")

    def test_per_mode_override_single(self) -> None:
        """single_label overrides parent for single mode."""
        parent = LidBuilder(
            text="Cards",
            label_mode=LabelMode.FRAMED,
            single_label=LidBuilder(text="CARDZ", label_mode=LabelMode.FRAMED),
        )
        resolved = parent.for_mode("single")
        self.assertEqual(resolved.text, "CARDZ")

    def test_no_override_falls_back(self) -> None:
        """Unset mode falls back to parent."""
        lb = LidBuilder(text="Cards", label_mode=LabelMode.FRAMED)
        self.assertIs(lb.for_mode("mmu"), lb)
        self.assertIs(lb.for_mode("single"), lb)

    def test_override_does_not_affect_other_mode(self) -> None:
        """MMU override leaves single mode unchanged."""
        lb = LidBuilder(
            text="Cards",
            label_mode=LabelMode.FRAMED,
            mmu_label=LidBuilder(label_mode=LabelMode.FRAMELESS),
        )
        self.assertEqual(lb.for_mode("mmu").label_mode, LabelMode.FRAMELESS)
        self.assertEqual(lb.for_mode("single").label_mode, LabelMode.FRAMED)

    def test_an_override_may_state_the_value_that_used_to_be_the_default(self) -> None:
        """FRAMED as an override was indistinguishable from saying nothing.

        The merge decided intent by comparing against the field's default, so
        an override could never state FRAMED, could never turn `diagonal` back
        off, and always imposed its own margins whether it mentioned them or not.
        """
        lb = LidBuilder(
            text="Cards",
            label_mode=LabelMode.FRAMELESS,
            diagonal=True,
            border_margin_mm=9.0,
            single_label=LidBuilder(label_mode=LabelMode.FRAMED, diagonal=False),
        )
        single = lb.for_mode("single")
        self.assertEqual(single.mode, LabelMode.FRAMED)
        self.assertFalse(single.is_diagonal)
        # The override said nothing about the margin, so the parent's stands.
        self.assertEqual(single.border_margin, 9.0)
        self.assertEqual(single.text, "Cards")

    def test_titled_copies_a_style_for_one_box(self) -> None:
        """A style is written once and worn by many boxes (FR-000b)."""
        style = LidBuilder(label_mode=LabelMode.FRAMELESS, diagonal=True)
        favor = style.titled("Favors")
        self.assertEqual(favor.text, "Favors")
        self.assertEqual(favor.mode, LabelMode.FRAMELESS)
        self.assertTrue(favor.is_diagonal)
        self.assertIsNone(style.text, "the style itself is unchanged")

    def test_titled_takes_a_colour_too(self) -> None:
        from pybosl2 import Color

        style = LidBuilder(label_mode=LabelMode.FRAMELESS)
        red = style.titled("Player", text_color=Color("red"))
        self.assertEqual(red.text, "Player")
        self.assertIsNotNone(red.text_color)
