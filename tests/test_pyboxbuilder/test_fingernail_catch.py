# SPDX-License-Identifier: Apache-2.0
"""FR-002e5: the dish that gets a sliding lid moving.

A seated sliding lid is a plate flush with the box's top, trapped in its
grooves. Its only exposed surfaces are an end face one lid thickness tall and a
smooth top — nothing to grip. The dish is what a fingernail hooks into.
"""

from __future__ import annotations

import unittest
from dataclasses import replace

from mesh import volume
from pybosl2 import cylinder

from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
from pyboxbuilder.box.shell import block
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.enums import BoxType

SLIDING = (BoxType.SLIDING, BoxType.SLIDING_CATCH, BoxType.CARD_LIBRARY)
LIFT_OFF = (BoxType.CAP, BoxType.INSET, BoxType.SLIPOVER, BoxType.HINGE)

SPEC = BoxSpec(
    label="T", width=96.0, length=70.0, height=40.0,
    wall_thickness=3.0, lid_thickness=2.0, floor_thickness=2.0,
)


def lid_for(box_type: BoxType, spec: BoxSpec = SPEC):
    return BOX_IMPL_REGISTRY[box_type]().build_lid(spec)


class WhichTypesCarryOneTests(unittest.TestCase):
    def test_every_sliding_type_has_a_dish(self) -> None:
        """SC-050a."""
        for box_type in SLIDING:
            with self.subTest(box_type=box_type.value):
                plain = lid_for(box_type, replace(SPEC, fingernail_catch=False))
                dished = lid_for(box_type)
                self.assertGreater(volume(plain) - volume(dished), 1.0)

    def test_a_lift_off_lid_has_none(self) -> None:
        """It has its own way open; a dish in it would be decoration."""
        for box_type in LIFT_OFF:
            with self.subTest(box_type=box_type.value):
                plain = lid_for(box_type, replace(SPEC, fingernail_catch=False))
                self.assertAlmostEqual(
                    volume(lid_for(box_type)), volume(plain), places=3
                )

    def test_a_box_can_decline_it(self) -> None:
        self.assertEqual(
            BOX_IMPL_REGISTRY[BoxType.SLIDING]().lid_keepouts(
                replace(SPEC, fingernail_catch=False)
            ),
            [],
        )


class SetPerBoxTests(unittest.TestCase):
    """SC-050a: derived by default, and settable where a box disagrees."""

    def project(self):
        from pyboxbuilder import Project

        return Project("T", game_box_size=(300, 200, 80))

    def keepouts(self, **kwargs):
        from pyboxbuilder.box.spec import build_spec

        project = self.project()
        builder = project.box(
            BoxType.SLIDING, "B", size=(96.0, 70.0, 40.0), **kwargs
        )
        spec = build_spec(project, builder, (96.0, 70.0, 40.0))
        return BOX_IMPL_REGISTRY[BoxType.SLIDING]().lid_keepouts(spec)

    def test_a_box_sets_its_own_dish(self) -> None:
        self.assertGreater(
            self.keepouts(fingernail_radius=7.0)[0][2], self.keepouts()[0][2]
        )

    def test_a_box_declines_it(self) -> None:
        self.assertEqual(self.keepouts(fingernail_catch=False), [])

    def test_a_lift_off_type_has_no_such_setting(self) -> None:
        """FR-000f: a field the geometry never reads is a defect, not a knob."""
        with self.assertRaises(TypeError) as caught:
            self.project().box(
                BoxType.CAP, "B", size=(50.0, 50.0, 30.0), fingernail_radius=3.0
            )
        self.assertIn("fingernail_radius", str(caught.exception))


class WhereItSitsTests(unittest.TestCase):
    def catch(self, spec: BoxSpec = SPEC):
        from pyboxbuilder.box.features import fingernail_catch

        box = BOX_IMPL_REGISTRY[BoxType.SLIDING]()
        found = fingernail_catch(spec, box.slide_axis(spec))
        assert found is not None
        return found

    def test_it_sits_at_the_exit_end_centred(self) -> None:
        """SC-050a: the only end a hand can reach, and centred so the pull is
        straight down the grooves rather than a twist."""
        wide = self.catch()                                   # exits +x
        self.assertGreater(wide.centre[0], SPEC.width * 0.75)
        self.assertAlmostEqual(wide.centre[1], SPEC.length / 2, places=3)

        tall = replace(SPEC, width=70.0, length=120.0)        # exits +y
        catch = self.catch(tall)
        self.assertAlmostEqual(catch.centre[0], tall.width / 2, places=3)
        self.assertGreater(catch.centre[1], tall.length * 0.75)

    def test_it_overlaps_the_border(self) -> None:
        """SC-050c: the catch belongs where the fingers are, at the edge."""
        from pyboxbuilder.lid.builder import LID_BORDER_MM

        catch = self.catch()
        nearest = SPEC.width - (catch.centre[0] + catch.radius)
        furthest = SPEC.width - (catch.centre[0] - catch.radius)
        self.assertLess(nearest, LID_BORDER_MM, "wholly inside the patterned area")
        self.assertGreater(furthest, LID_BORDER_MM, "wholly inside the border")

    def test_a_small_lid_gets_a_small_dish(self) -> None:
        """Derived from the lid, not fixed (FR-000)."""
        big = self.catch()
        small = self.catch(replace(SPEC, width=40.0, length=18.0))
        self.assertLess(small.radius, big.radius)

    def test_the_size_is_settable(self) -> None:
        catch = self.catch(replace(SPEC, fingernail_radius=6.0))
        self.assertEqual(catch.radius, 6.0)


class HowDeepItGoesTests(unittest.TestCase):
    def test_it_never_pierces_the_lid(self) -> None:
        """SC-050b: a plate's worth of material always remains under it."""
        for thickness in (1.6, 2.0, 3.0):
            with self.subTest(lid_thickness=thickness):
                spec = replace(SPEC, lid_thickness=thickness)
                lid = lid_for(BoxType.SLIDING, spec)
                # A slab across the underside of the plate: still solid where
                # the dish is, or the dish has gone through.
                from pyboxbuilder.box.features import fingernail_catch

                catch = fingernail_catch(spec, "x")
                assert catch is not None
                under = block(
                    [2 * catch.radius, 2 * catch.radius, thickness / 4],
                    at=(
                        catch.centre[0] - catch.radius,
                        catch.centre[1] - catch.radius,
                        spec.height - thickness,
                    ),
                )
                self.assertGreater(volume(lid & under), 0.0)

    def test_the_depth_is_capped_at_half_the_plate(self) -> None:
        from pyboxbuilder.box.features import fingernail_catch

        greedy = replace(SPEC, fingernail_depth=10.0)
        catch = fingernail_catch(greedy, "x")
        assert catch is not None
        self.assertLessEqual(catch.depth, SPEC.lid_thickness / 2)

    def test_it_is_a_spherical_cap_not_a_pocket(self) -> None:
        """SC-050b: deepest at the centre, shallowing to nothing at the rim.

        A cylindrical pocket has a wall and a floor, and a nail catches on its
        rim rather than under it.
        """
        from pyboxbuilder.box.features import fingernail_catch

        catch = fingernail_catch(SPEC, "x")
        assert catch is not None
        lid = lid_for(BoxType.SLIDING)

        def removed_at(offset: float) -> float:
            """Material missing from a thin column at `offset` from centre."""
            column = block(
                [0.6, 0.6, SPEC.lid_thickness],
                at=(
                    catch.centre[0] + offset - 0.3,
                    catch.centre[1] - 0.3,
                    SPEC.height - SPEC.lid_thickness,
                ),
            )
            plain = lid_for(BoxType.SLIDING, replace(SPEC, fingernail_catch=False))
            return volume(plain & column) - volume(lid & column)

        centre = removed_at(0.0)
        middle = removed_at(catch.radius * 0.6)
        edge = removed_at(catch.radius * 0.95)
        self.assertGreater(centre, middle)
        self.assertGreater(middle, edge)


class PatternKeepsClearTests(unittest.TestCase):
    """SC-050d: the ring the dish is pulled against stays whole."""

    def test_a_pattern_leaves_a_millimetre_round_the_dish(self) -> None:
        from pyboxbuilder.box.features import FINGERNAIL_MARGIN_MM, fingernail_catch
        from pyboxbuilder.enums import PatternType
        from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
        from pyboxbuilder.lid.decorate import decorate_lid

        box = BOX_IMPL_REGISTRY[BoxType.SLIDING]()
        lid = box.build_lid(SPEC)
        catch = fingernail_catch(SPEC, "x")
        assert catch is not None

        decorated = decorate_lid(
            lid,
            LidBuilder(pattern=PatternBuilder(type=PatternType.HEX, spacing=8.0)),
            SPEC.lid_thickness, "mmu",
            reserved=box.lid_keepouts(SPEC),
        )

        # The ring between the dish's rim and its margin must be untouched: a
        # hole opening onto the rim is where the lid would tear when pulled.
        around = cylinder(
            height=SPEC.lid_thickness + 2, radius=catch.keepout_radius
        ).translate([catch.centre[0], catch.centre[1], SPEC.height])
        self.assertAlmostEqual(
            volume(lid & around), volume(decorated.solid & around), places=3,
            msg="the pattern cut into the dish's margin",
        )
        self.assertGreater(FINGERNAIL_MARGIN_MM, 0.0)

    def test_the_margin_is_the_only_thing_it_protects(self) -> None:
        """The keep-out is a ring, not an excuse to leave the lid plain."""
        from pyboxbuilder.enums import PatternType
        from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
        from pyboxbuilder.lid.decorate import decorate_lid

        box = BOX_IMPL_REGISTRY[BoxType.SLIDING]()
        lid = box.build_lid(SPEC)
        decorated = decorate_lid(
            lid,
            LidBuilder(pattern=PatternBuilder(type=PatternType.HEX, spacing=8.0)),
            SPEC.lid_thickness, "mmu",
            reserved=box.lid_keepouts(SPEC),
        )
        self.assertLess(volume(decorated.solid), volume(lid) - 100.0)


if __name__ == "__main__":
    unittest.main()
