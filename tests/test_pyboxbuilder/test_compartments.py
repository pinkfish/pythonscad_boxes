# SPDX-License-Identifier: Apache-2.0
"""Tests for CompartmentBuilder."""

import unittest

from pyboxbuilder.builders._base import Cut
from pyboxbuilder.compartments.builder import CompartmentBuilder
from pyboxbuilder.enums import ScoopSide


class CompartmentBuilderTests(unittest.TestCase):
    def test_basic_compartment(self) -> None:
        cb = CompartmentBuilder(label="Well", size=(50, 50), depth=30)
        self.assertEqual(cb.label, "Well")
        self.assertEqual(cb.size, (50, 50))
        self.assertEqual(cb.depth, 30)
        self.assertEqual(cb.rounded_corners, 0.0)
        self.assertIsNone(cb.cut)

    def test_ratio_based_sizing(self) -> None:
        """Compartment sized by ratio of interior."""
        cb = CompartmentBuilder(
            label="RWell", width_ratio=0.5, length_ratio=0.8, depth=30,
        )
        self.assertEqual(cb.width_ratio, 0.5)
        self.assertEqual(cb.length_ratio, 0.8)
        self.assertIsNone(cb.size)

    def test_ratio_resolve_absolute(self) -> None:
        """resolve_size computes absolute from ratio and interior."""
        cb = CompartmentBuilder(
            label="Half", width_ratio=0.5, length_ratio=1.0, depth=20,
        )
        w, l = cb.resolve_size(200, 150)
        self.assertEqual(w, 100.0)
        self.assertEqual(l, 150.0)

    def test_ratio_resolve_mixed(self) -> None:
        """Mixed absolute width + ratio length."""
        cb = CompartmentBuilder(
            label="Mixed", size=(50, None), length_ratio=0.5, depth=20,
        )
        w, l = cb.resolve_size(200, 150)
        self.assertEqual(w, 50.0)
        self.assertEqual(l, 75.0)

    def test_ratio_precision_tenth_mm(self) -> None:
        """Ratios resolve to 0.1mm precision, not whole mm."""
        cb = CompartmentBuilder(
            label="Precise", width_ratio=0.333, length_ratio=0.777, depth=20,
        )
        w, l = cb.resolve_size(100, 100)
        self.assertEqual(w, 33.3)
        self.assertEqual(l, 77.7)

    def test_ratio_invalid_range(self) -> None:
        """Ratios outside (0, 1] are rejected."""
        with self.assertRaises(ValueError):
            CompartmentBuilder(label="Bad", width_ratio=0, depth=20)
        with self.assertRaises(ValueError):
            CompartmentBuilder(label="Bad", width_ratio=1.5, depth=20)

    def test_no_size_means_fill_the_interior(self) -> None:
        """A well with nothing said about it takes the whole interior (FR-000).

        This is the common case — one box, one well — and it used to be an
        error, which meant every such box repeated `size - 2 * wall` at the
        call site to say what the library already knew.
        """
        well = CompartmentBuilder(label="NoSize", depth=20)
        self.assertTrue(well.fills_interior)
        self.assertEqual(well.resolve_size(96.0, 76.0), (96.0, 76.0))
        # And it demands nothing of a box that has no size of its own.
        self.assertIsNone(well.min_footprint())

    def test_no_depth_means_run_to_the_floor(self) -> None:
        well = CompartmentBuilder(label="Deep", size=(50.0, 40.0))
        self.assertEqual(well.resolve_depth(36.4), 36.4)
        self.assertEqual(well.resolve_depth(12.0), 12.0)

    def test_a_box_whose_wells_all_fill_needs_its_own_size(self) -> None:
        """Nothing can be derived from a well that only fills, so say so."""
        from pyboxbuilder.enums import BoxType
        from pyboxbuilder.project import Project

        p = Project("Fill", game_box_size=(200, 150, 60))
        b = p.box(BoxType.NO_LID, "Tray")
        b.compartment("Everything")
        with self.assertRaises(ValueError) as caught:
            p.build()
        message = str(caught.exception)
        self.assertIn("Tray", message)
        self.assertIn("Everything", message)
        self.assertIn("size=", message)

    def test_ratio_overflow_rejected_in_project(self) -> None:
        """Project export rejects compartments whose ratios sum > 1.0."""
        from pyboxbuilder.enums import BoxType
        from pyboxbuilder.project import Project
        p = Project("Overflow", game_box_size=(200, 150, 60))
        b = p.box(BoxType.SLIDING, "Bad", size=(100, 100, 50))
        b.compartment("A", width_ratio=0.6, depth=20)
        b.compartment("B", width_ratio=0.6, depth=20)
        with self.assertRaises(ValueError) as ctx:
            p.export("/tmp/test_overflow")
        self.assertIn("1.20", str(ctx.exception))

    def test_default_scoop_side(self) -> None:
        """Unset until carve time, where the *shorter* wall is chosen.

        Pinning FRONT here would have hidden the shape from the decision, and
        that is how Emberleaf's card boxes ended up with their finger cut in
        the long wall.
        """
        cb = CompartmentBuilder(
            label="Well", size=(50, 50), depth=30, cut=Cut(),
        )
        self.assertIsNone(cb.cut.side)

    def test_explicit_scoop_side(self) -> None:
        cb = CompartmentBuilder(
            label="Well", size=(50, 50), depth=30,
            cut=Cut(side=ScoopSide.BACK),
        )
        self.assertEqual(cb.cut.side, ScoopSide.BACK)

    def test_rounded_corners_default(self) -> None:
        cb = CompartmentBuilder(label="Well", size=(50, 50), depth=30)
        self.assertEqual(cb.rounded_corners, 0.0)


class ContentSizingTests(unittest.TestCase):
    """FR-000: describe what goes in the box, not the geometry."""

    def project(self):
        from pyboxbuilder.project import Project

        return Project("Cards", game_box_size=(300, 200, 80))

    def test_a_card_box_is_sized_by_its_cards(self) -> None:
        from pyboxbuilder.enums import BoxType

        p = self.project()
        box = p.box(BoxType.SLIDING, "Deck", size=(70, 100, None))
        box.cards("Cards", count=50, size=(62.0, 93.0))

        # The well is the card plus its slack; the box's height follows from
        # the stack, the floor and the lid — none of it written at the call site.
        well = box.compartments[0]
        self.assertEqual(well.size, (63.0, 94.0))
        self.assertAlmostEqual(well.depth, 50 * 0.6 + 1.0)
        self.assertGreater(p._min_size(box)[2], well.depth)

    def test_a_stack_comes_out_through_the_floor_by_default(self) -> None:
        """A stack that fills its well leaves no side for a finger (FR-060)."""
        from pyboxbuilder.enums import BoxType, FingerCut

        box = self.project().box(BoxType.SLIDING, "Deck", size=(70, 100, None))
        box.cards("Cards", count=10, size=(62.0, 93.0))
        self.assertIs(box.compartments[0].cut.kind, FingerCut.THROUGH_FLOOR)

    def test_sleeved_cards_take_a_thicker_stack(self) -> None:
        from pyboxbuilder.enums import BoxType

        box = self.project().box(BoxType.SLIDING, "Deck", size=(70, 100, None))
        box.cards("Cards", count=50, size=(62.0, 93.0), thickness=0.8)
        self.assertAlmostEqual(box.compartments[0].depth, 50 * 0.8 + 1.0)

    def test_no_cards_is_refused(self) -> None:
        from pyboxbuilder.enums import BoxType

        box = self.project().box(BoxType.SLIDING, "Deck", size=(70, 100, None))
        with self.assertRaises(ValueError):
            box.cards("Cards", count=0, size=(62.0, 93.0))


class BoxDefaultsTests(unittest.TestCase):
    """FR-000b: a value shared by every box is said once."""

    def test_defaults_reach_every_box(self) -> None:
        from pyboxbuilder.enums import BoxType
        from pyboxbuilder.project import Project

        p = Project("G", game_box_size=(300, 200, 80),
                    box_defaults={"wall_thickness": 3.0, "no_rotate": True})
        box = p.box(BoxType.SLIDING, "A", size=(70, 100, 40))
        self.assertEqual(box.wall_thickness, 3.0)
        self.assertTrue(box.no_rotate)

    def test_a_box_may_still_say_otherwise(self) -> None:
        from pyboxbuilder.enums import BoxType
        from pyboxbuilder.project import Project

        p = Project("G", game_box_size=(300, 200, 80),
                    box_defaults={"wall_thickness": 3.0})
        box = p.box(BoxType.SLIDING, "A", size=(70, 100, 40), wall_thickness=1.5)
        self.assertEqual(box.wall_thickness, 1.5)

    def test_a_default_a_builder_does_not_have_is_ignored(self) -> None:
        """A project-wide default is not an error for the types that lack it."""
        from pyboxbuilder.enums import BoxType
        from pyboxbuilder.project import Project

        p = Project("G", game_box_size=(300, 200, 80),
                    box_defaults={"cap_height": 8.0})
        sliding = p.box(BoxType.SLIDING, "A", size=(70, 100, 40))
        cap = p.box(BoxType.CAP, "B", size=(70, 100, 40))
        self.assertFalse(hasattr(sliding, "cap_height"))
        self.assertEqual(cap.cap_height, 8.0)

    def test_an_unknown_keyword_is_refused_by_name(self) -> None:
        """A parameter the type does not have used to be silently dropped."""
        from pyboxbuilder.enums import BoxType
        from pyboxbuilder.project import Project

        p = Project("G", game_box_size=(300, 200, 80))
        with self.assertRaises(TypeError) as caught:
            p.box(BoxType.SLIDING, "A", size=(70, 100, 40), two_layer=True)
        message = str(caught.exception)
        self.assertIn("two_layer", message)
        self.assertIn("SlidingBoxBuilder", message)
