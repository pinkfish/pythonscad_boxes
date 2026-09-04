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
    lid_slide_axis="x",
)


def lid_for(box_type: BoxType, spec: BoxSpec = SPEC):
    return BOX_IMPL_REGISTRY[box_type]().build_lid(spec)


def catch_for(spec: BoxSpec = SPEC):
    """The catch a sliding box of `spec` gets, asked of the type itself."""
    from pyboxbuilder.box.features import fingernail_catch

    box = BOX_IMPL_REGISTRY[BoxType.SLIDING]()
    found = fingernail_catch(spec, box.slide_axis(spec))
    assert found is not None
    return found


def removed_at(catch, offset: float, spec: BoxSpec = SPEC) -> float:
    """Depth cut out of a thin column `offset` mm along the slide from centre.

    Negative is inboard, into the bowl; positive is outboard, past the wall and
    towards the lid's edge. Reported as a depth so it can be read against the
    lid's thickness.
    """
    side = 0.4
    x, y = catch.centre
    if catch.axis == "x":
        x += offset
    else:
        y += offset
    column = block(
        [side, side, spec.lid_thickness],
        at=(x - side / 2, y - side / 2, spec.height - spec.lid_thickness),
    )
    plain = lid_for(BoxType.SLIDING, replace(spec, fingernail_catch=False))
    dished = lid_for(BoxType.SLIDING, spec)
    return (volume(plain & column) - volume(dished & column)) / (side * side)


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
    catch = staticmethod(catch_for)

    def test_it_sits_at_the_exit_end_centred(self) -> None:
        """SC-050a: the only end a hand can reach, and centred so the pull is
        straight down the grooves rather than a twist."""
        wide = self.catch()                                   # exits +x
        self.assertGreater(wide.centre[0], SPEC.width * 0.75)
        self.assertAlmostEqual(wide.centre[1], SPEC.length / 2, places=3)

        tall = replace(SPEC, width=70.0, length=120.0, lid_slide_axis="y")        # exits +y
        catch = self.catch(tall)
        self.assertAlmostEqual(catch.centre[0], tall.width / 2, places=3)
        self.assertGreater(catch.centre[1], tall.length * 0.75)

    def test_the_wall_stands_on_the_border_line(self) -> None:
        """SC-050c: the catch belongs where the fingers are, keeping clear of the label/logo.
        """
        catch = self.catch()
        # Outboard edge gap from lid edge must be >= 2.5mm
        self.assertGreaterEqual(SPEC.width - catch.centre[0], 2.5)
        # Inboard edge gap from label border must be >= 1.0mm
        # Default label margin is 10.0mm. Inboard edge is at catch.centre[0] - catch.radius.
        label_margin = 10.0
        inboard_edge = catch.centre[0] - catch.radius
        label_gap = label_margin - (SPEC.width - inboard_edge)
        self.assertGreaterEqual(label_gap, 1.0 - 1e-6)

    def test_a_small_lid_gets_a_small_dish(self) -> None:
        """Derived from the lid, not fixed (FR-000)."""
        big = self.catch()
        small = self.catch(replace(SPEC, width=40.0, length=18.0, lid_slide_axis="x"))
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

    def test_the_bowl_is_a_spherical_cap_not_a_pocket(self) -> None:
        """SC-050b: deepest at the wall, shallowing to nothing at the rim.

        The bowl is what the nail goes *into*, and it curves away in every
        direction so the nail finds it without being aimed. A cylindrical
        pocket has a wall and a floor all round, and the nail catches on its
        rim rather than dropping in.
        """
        catch = catch_for(SPEC)
        deep = removed_at(catch, -0.2)
        middle = removed_at(catch, -catch.radius * 0.6)
        rim = removed_at(catch, -catch.radius * 0.95)
        self.assertGreater(deep, middle)
        self.assertGreater(middle, rim)


class TheWallTests(unittest.TestCase):
    """SC-050e: half a dish, so the nail has something flat to pull on."""

    def assertNothingCut(self, depth: float, msg: str = "") -> None:
        """Assert a probe found full-thickness lid, to within mesh noise."""
        self.assertAlmostEqual(depth, 0.0, places=6, msg=msg or None)

    def test_the_outboard_half_is_left_as_lid(self) -> None:
        """A whole dish curves away on the pull side too, and a nail loading it
        rides up that slope and skids out instead of moving the lid."""
        catch = catch_for(SPEC)
        self.assertGreater(removed_at(catch, -0.3), 0.0, "no bowl to get into")
        self.assertNothingCut(removed_at(catch, +0.3), "the wall was cut away")
        self.assertNothingCut(removed_at(catch, +catch.radius * 0.9))

    def test_the_wall_stands_across_the_pull(self) -> None:
        """Whichever way the lid slides — the flat has to face the hand."""
        tall = replace(SPEC, width=70.0, length=120.0, lid_slide_axis="y")          # exits +y
        catch = catch_for(tall)
        self.assertEqual(catch.axis, "y")
        self.assertGreater(removed_at(catch, -0.3, tall), 0.0)
        self.assertNothingCut(removed_at(catch, +0.3, tall))

    def test_the_wall_is_as_deep_as_the_dish(self) -> None:
        """Split through the sphere's centre, so the nail gets the whole depth
        to bear on rather than a sliver of it."""
        catch = catch_for(SPEC)
        # The probe averages over a small square, so it reads a shade under the
        # depth at the wall itself; a sliver would read a fraction of it.
        self.assertGreater(removed_at(catch, -0.3), catch.depth * 0.9)

    def test_the_material_behind_the_wall_reaches_the_lid_edge(self) -> None:
        """What the nail pushes on is the band of plain lid outside the wall;
        a hole cut through it is what would break away in the hand."""
        catch = catch_for(SPEC)
        for offset in (1.0, 3.0, 6.0):
            with self.subTest(mm_outboard=offset):
                self.assertNothingCut(removed_at(catch, offset))


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
