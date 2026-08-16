# SPDX-License-Identifier: Apache-2.0
"""Tests for finger-scoop smoothing, ported from the original toolkit (T248).

The three roundings under test — the mouth flare into the rim, the fillet where
the cut emerges on each face, and the floor blend — are all *geometry*, so the
assertions that matter are measured in the real app. Offline `bounds()` on a
lazy CSG tree is an estimate and cannot see a boolean's true extent.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "tests"))

from render_app import measure_python, render_available  # noqa: E402

from pyboxbuilder.compartments.finger_hole import (  # noqa: E402
    DEFAULT_MOUTH_ROUNDING_MM,
    MIN_WALL_SCOOP_DEPTH_MM,
    build_floor_scoop,
    build_scoop,
    build_wall_scoop,
    floor_bore_profile,
    scoop_profile,
)
from pyboxbuilder.enums import ScoopSide  # noqa: E402


class ScoopProfileTests(unittest.TestCase):
    """The 2-D profile: both branches build, and the inputs are validated."""

    def test_tall_profile_builds(self) -> None:
        self.assertIsNotNone(scoop_profile(10, 30, 3))

    def test_a_shallow_profile_still_builds(self) -> None:
        """No special case: the radii scale down to whatever height there is."""
        self.assertIsNotNone(scoop_profile(10, 6, 3))

    def test_zero_rounding_gives_a_plain_slot(self) -> None:
        self.assertIsNotNone(scoop_profile(10, 30, 0))

    def test_bad_inputs_rejected(self) -> None:
        for args in ((0, 30, 3), (-1, 30, 3), (10, 0, 3), (10, 30, -1)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                scoop_profile(*args)


class OutlineTests(unittest.TestCase):
    """The outline is a ring, and it must not close into a cusp."""

    def test_the_outline_overshoots_the_rim(self) -> None:
        """Closing flush across the top puts a zero-angle cusp at each end of
        the r1 arc, and offsetting such a corner miters to infinity — measured,
        a 15mm profile came back at 55mm."""
        from pyboxbuilder.compartments.finger_hole import (
            RIM_OVERSHOOT_MM,
            scoop_outline,
        )

        height = 30.0
        ring = scoop_outline(10, height, 5, 5)
        self.assertAlmostEqual(max(y for _, y in ring), height + RIM_OVERSHOOT_MM)

    def test_the_outline_is_a_closed_ring_around_the_cut(self) -> None:
        from pyboxbuilder.compartments.finger_hole import scoop_outline

        ring = scoop_outline(10, 30, 5, 5)
        self.assertGreater(len(ring), 8)
        # Symmetric about the centre line, and it reaches the full mouth width.
        self.assertAlmostEqual(min(x for x, _ in ring), -max(x for x, _ in ring))
        self.assertAlmostEqual(max(x for x, _ in ring), 15.0)
        self.assertAlmostEqual(min(y for _, y in ring), 0.0)

    def test_the_floor_bore_outline_is_a_bowl(self) -> None:
        """Its lowest point is a single tangent touch, not a flat run."""
        from pyboxbuilder.compartments.finger_hole import floor_bore_outline

        ring = floor_bore_outline(10, 30, 3)
        floor_points = [x for x, y in ring if abs(y) < 1e-6]
        self.assertLessEqual(len(floor_points), 2, "the bore has a flat bottom")

    def test_a_tall_scoop_has_a_straight_vertical_throat(self) -> None:
        """radius + smoothing << height: the floor and rim circles are joined by
        their common tangent — a straight vertical run, not a step at either join."""
        from pyboxbuilder.compartments.finger_hole import scoop_outline

        ring = scoop_outline(10, 30, 3, 3)
        right = [(x, y) for x, y in ring if x > 1e-6]
        throat = sorted(y for x, y in right if abs(x - 10.0) < 1e-6)
        self.assertGreaterEqual(len(throat), 2, "no straight throat")
        self.assertGreater(throat[-1] - throat[0], 10.0, "the throat collapsed to a point")


class ScoopSelectionTests(unittest.TestCase):
    def test_deep_compartment_gets_a_wall_notch(self) -> None:
        deep = build_scoop(40, 30, MIN_WALL_SCOOP_DEPTH_MM + 1, ScoopSide.FRONT)
        direct = build_wall_scoop(40, 30, MIN_WALL_SCOOP_DEPTH_MM + 1, ScoopSide.FRONT)
        self.assertEqual(repr(deep), repr(direct))

    def test_shallow_compartment_gets_the_floor_blend(self) -> None:
        shallow = build_scoop(40, 30, 4, ScoopSide.FRONT)
        direct = build_floor_scoop(40, 30, ScoopSide.FRONT, comp_depth=4, radius=12.0)
        self.assertEqual(repr(shallow), repr(direct))

    def test_a_card_well_notches_and_a_token_tray_bores(self) -> None:
        """SC-072/FR-043a9: the boundary sits below a card well.

        At the inherited 8mm, Emberleaf's 6.5mm player card well fell to the
        bore — which on a 10.5mm box is a nick in the rim a millimetre deep
        with the wall whole underneath. A card box wants a dip to get a
        fingertip under the stack; the bore is for the shallow token tray.
        """
        card_well = build_scoop(84.0, 92.0, 6.5, ScoopSide.BACK, wall_thickness=3.0)
        as_notch = build_wall_scoop(84.0, 92.0, 6.5, ScoopSide.BACK, wall_thickness=3.0)
        self.assertEqual(repr(card_well), repr(as_notch))

        token_tray = build_scoop(84.0, 92.0, 4.0, ScoopSide.BACK, wall_thickness=3.0)
        as_bore = build_floor_scoop(
            84.0, 92.0, ScoopSide.BACK, comp_depth=4.0, radius=12.0, wall_thickness=3.0
        )
        self.assertEqual(repr(token_tray), repr(as_bore))

    def test_bad_dimensions_rejected(self) -> None:
        with self.assertRaises(ValueError):
            build_wall_scoop(40, 30, 0, ScoopSide.FRONT)
        with self.assertRaises(ValueError):
            build_wall_scoop(40, 30, 20, ScoopSide.FRONT, wall_thickness=0)


@unittest.skipUnless(render_available(), "PythonSCAD binary not available")
class MeasuredScoopTests(unittest.TestCase):
    """Measured in the app: the promises the docstrings make must hold."""

    @classmethod
    def setUpClass(cls) -> None:
        body = '''
from pyboxbuilder.compartments.finger_hole import build_wall_scoop, build_floor_scoop
from pyboxbuilder.enums import ScoopSide
from pybosl2 import cuboid

# Compartment 40 x 30 x 20. For a FRONT scoop the wall's inner face is y=0 and
# its outer face is y=-wall_thickness.
measure("wt2", build_wall_scoop(40, 30, 20, ScoopSide.FRONT, radius=10, wall_thickness=2))
measure("wt3", build_wall_scoop(40, 30, 20, ScoopSide.FRONT, radius=10, wall_thickness=3))
measure("wt5", build_wall_scoop(40, 30, 20, ScoopSide.FRONT, radius=10, wall_thickness=5))
measure("square", build_wall_scoop(40, 30, 20, ScoopSide.FRONT, radius=10,
                                   wall_thickness=2, rounding_edge=0, rounding_radius=0))
measure("no_mouth", build_wall_scoop(40, 30, 20, ScoopSide.FRONT, radius=10,
                                      wall_thickness=2, rounding_radius=0))
measure("left", build_wall_scoop(40, 30, 20, ScoopSide.LEFT, radius=10, wall_thickness=2))
measure("right", build_wall_scoop(40, 30, 20, ScoopSide.RIGHT, radius=10, wall_thickness=2))
measure("back", build_wall_scoop(40, 30, 20, ScoopSide.BACK, radius=10, wall_thickness=2))
measure("breaching", build_wall_scoop(40, 30, 20, ScoopSide.FRONT, radius=10,
                                       wall_thickness=2, breach_floor=True))
measure("thick_floor", build_wall_scoop(40, 30, 20, ScoopSide.FRONT, radius=10,
                                         wall_thickness=2, floor_thickness=4))
measure("floor", build_floor_scoop(40, 30, ScoopSide.FRONT, radius=8, comp_depth=5,
                                    wall_thickness=2))

# The scoop must actually open the wall of a real box, not just touch it.
shell = cuboid([44, 34, 22], anchor=[-1, -1, -1])
well = cuboid([40, 30, 20], anchor=[-1, -1, -1]).translate([2, 2, 2])
scoop = build_wall_scoop(40, 30, 20, ScoopSide.FRONT, radius=10, wall_thickness=2)
measure("carved", shell - well - scoop.translate([2, 2, 2]))
cuboid([1, 1, 1]).show()
'''
        cls.result = measure_python(body)
        if not cls.result.ok:
            raise AssertionError(f"measurement run failed: {cls.result.error}\n{cls.result.stderr[-2000:]}")

    def span(self, name: str, axis: int) -> tuple[float, float]:
        box = self.result.boxes[name]
        return box.position[axis], box.position[axis] + box.size[axis]

    def test_dips_only_a_controlled_amount_into_the_floor(self) -> None:
        """The cut may not sit *on* the floor plane, nor sink far into it.

        Clipping flush with the floor leaves a coincident face, which renders as
        speckle; the original's answer is a small deliberate overshoot. So the
        bottom must be below 0 but no deeper than the dip, which defaults to
        0.2mm when no floor thickness is passed.
        """
        for name in ("wt2", "wt3", "wt5", "floor"):
            with self.subTest(name=name):
                low, _ = self.span(name, 2)
                self.assertLess(low, 0.0, "bottom face is coplanar with the floor")
                self.assertGreaterEqual(low, -0.25, "dipped further than the default 0.2mm")

    def test_a_scoop_with_no_fillet_has_nothing_to_dip(self) -> None:
        """The dip is a limit on the flare, not an offset applied regardless.

        With both roundings off there is no flare below the bore, so the cut
        bottoms out exactly at the floor and the clip never engages.
        """
        low, _ = self.span("square", 2)
        self.assertAlmostEqual(low, 0.0, places=3)

    def test_the_dip_stays_small_whatever_the_floor(self) -> None:
        """The dip only has to break a coincident face, so it is a small
        constant — not a share of the floor.

        Scaling it with thickness (up to 1mm) spent half a 2mm floor on a
        cosmetic detail and showed as the cut visibly eating into the floor.
        A thin floor still reduces it further; a thick one does not licence
        more.
        """
        default, _ = self.span("wt2", 2)
        thick, _ = self.span("thick_floor", 2)
        self.assertAlmostEqual(default, -0.2, places=2)
        self.assertAlmostEqual(thick, -0.2, places=2)

    def test_breaching_still_differs_from_the_clipped_cut(self) -> None:
        clipped, _ = self.span("wt2", 2)
        unclipped, _ = self.span("breaching", 2)
        self.assertLess(unclipped, clipped)

    def test_breach_floor_opt_in_dips_much_further(self) -> None:
        """The opt-out removes the clip entirely, so the flare runs free."""
        low, _ = self.span("breaching", 2)
        self.assertLess(low, -0.5)

    def test_overshoots_the_rim_so_no_skin_is_left(self) -> None:
        _, high = self.span("wt2", 2)
        self.assertGreater(high, 20.0)

    def test_pierces_the_wall_at_any_thickness(self) -> None:
        """The sweep spans exactly the wall: 0.015 clear of each face, no more.

        Overshooting further would put the face fillets outside the box, which
        is the bug this test exists to catch.
        """
        for name, wall in (("wt2", 2.0), ("wt3", 3.0), ("wt5", 5.0)):
            with self.subTest(wall=wall):
                low, high = self.span(name, 1)
                self.assertAlmostEqual(low, -wall - 0.015, places=2)
                self.assertAlmostEqual(high, 0.015, places=2)

    def test_face_fillet_and_mouth_flare_widen_the_cut(self) -> None:
        """A plain slot is 2*radius wide; each rounding adds to that.

        Widths carry a faceting tolerance: both the r1 arc and the face
        fillet's rim are sampled polygons, so each falls a little short of its
        exact radius. 0.1mm is well inside the 0.1mm dimensional precision the
        library promises and an order below what a nozzle resolves.
        """
        square_low, square_high = self.span("square", 0)
        self.assertAlmostEqual(square_high - square_low, 20.0, delta=0.1)

        # r1 off, face fillet on (wall/2 = 1mm each side).
        no_mouth_low, no_mouth_high = self.span("no_mouth", 0)
        self.assertAlmostEqual(no_mouth_high - no_mouth_low, 22.0, delta=0.1)

        # Both on: r1 defaults to half the throat (5mm here) on each side.
        full_low, full_high = self.span("wt2", 0)
        self.assertAlmostEqual(full_high - full_low, 32.0, delta=0.1)

    def test_carved_box_keeps_its_envelope(self) -> None:
        """Cutting the scoop must not enlarge the box or open its base."""
        box = self.result.boxes["carved"]
        self.assertAlmostEqual(box.position[2], 0.0, places=3)
        self.assertAlmostEqual(box.size[0], 44.0, places=2)
        self.assertAlmostEqual(box.size[1], 34.0, places=2)
        self.assertAlmostEqual(box.size[2], 22.0, places=2)

    def test_floor_scoop_blends_into_the_floor(self) -> None:
        """The floor blend reaches into the compartment past the wall face."""
        _, high = self.span("floor", 1)
        self.assertGreater(high, 0.5)

    def test_each_side_cuts_outward_through_its_own_wall(self) -> None:
        """Every side's cut must lie *outside* the compartment footprint.

        A scoop pointing the wrong way sits inside the well and shaves the
        wall's inner face by the sweep's 0.015 of fudge, piercing nothing. The
        bounding box is the same size either way, so the direction is what has
        to be asserted — LEFT/RIGHT were inverted until this test.
        """
        cases = {
            "left": (0, -2.015, 0.015),      # wall at x <= 0
            "right": (0, 39.985, 42.015),    # wall at x >= 40 (comp_width)
            "back": (1, 29.985, 32.015),     # wall at y >= 30 (comp_length)
            "wt2": (1, -2.015, 0.015),       # FRONT: wall at y <= 0
        }
        for name, (axis, low, high) in cases.items():
            with self.subTest(side=name):
                got_low, got_high = self.span(name, axis)
                self.assertAlmostEqual(got_low, low, places=2)
                self.assertAlmostEqual(got_high, high, places=2)


@unittest.skipUnless(render_available(), "PythonSCAD binary not available")
class ExteriorFingerHoleTests(unittest.TestCase):
    """A hole on the outside of a box goes through the same scoop builder."""

    @classmethod
    def setUpClass(cls) -> None:
        body = '''
from pyboxbuilder.enums import ScoopSide
from pyboxbuilder.box.shell import build_shell
from pybosl2 import cuboid

base = dict(label="Tray", width=100, length=80, height=40,
            wall_thickness=2.0, floor_thickness=1.6, lid_thickness=0.0, hollow=True)

class Hole:
    """Stands in for FingerHoleBuilder — build_shell only reads attributes."""
    def __init__(self, side, radius=14.0, depth=6.0, offset=0.0):
        self.side, self.radius, self.depth, self.offset = side, radius, depth, offset
        self.rounding_radius = self.rounding_edge = None

plain = build_shell(dict(base))
measure("plain", plain)
measure("holed", build_shell(dict(base, finger_holes=(Hole(ScoopSide.LEFT),
                                                      Hole(ScoopSide.RIGHT)))))
# What each hole actually removed from the wall.
measure("removed_left",
        build_shell(dict(base)) - build_shell(dict(base, finger_holes=(Hole(ScoopSide.LEFT),))))
measure("removed_front",
        build_shell(dict(base)) - build_shell(dict(base, finger_holes=(Hole(ScoopSide.FRONT),))))
# The same cut on a *lidded* box. `base` has lid_thickness 0, so its interior
# runs to the rim and a cut reaching 40 is correct there; a 2mm lid moves the
# interior top to 38 and the cut must follow it. Rounding is off on both so the
# comparison is not reading a facet-level disagreement between two
# independently meshed shells.
_lidless = dict(base, rounding=0, lid_thickness=0.0)
_lidded = dict(base, rounding=0, lid_thickness=2.0)
measure("removed_lidless",
        build_shell(dict(_lidless)) - build_shell(dict(_lidless, finger_holes=(Hole(ScoopSide.FRONT),))))
measure("removed_lidded",
        build_shell(dict(_lidded)) - build_shell(dict(_lidded, finger_holes=(Hole(ScoopSide.FRONT),))))
measure("removed_deep",
        build_shell(dict(base)) - build_shell(dict(base, finger_holes=(Hole(ScoopSide.FRONT, depth=100),))))

# The same capped cut on its own, where no mesh-difference sliver can appear.
from pyboxbuilder.compartments.finger_hole import build_wall_scoop
_reach = 40 - 1.6
measure("deep_scoop_solid",
        build_wall_scoop(96, 76, _reach, ScoopSide.FRONT, radius=14.0,
                         wall_thickness=2.0, rounding_radius=3.0)
        .translate([2, 2, 40 - _reach]))
cuboid([1, 1, 1]).show()
'''
        cls.result = measure_python(body)
        if not cls.result.ok:
            raise AssertionError(f"measurement run failed: {cls.result.error}")

    def box(self, name: str):
        return self.result.boxes[name]

    def test_a_hole_does_not_change_the_box_envelope(self) -> None:
        plain, holed = self.box("plain"), self.box("holed")
        self.assertEqual([round(v, 3) for v in plain.size], [round(v, 3) for v in holed.size])
        self.assertEqual([round(v, 3) for v in plain.position], [round(v, 3) for v in holed.position])

    def test_a_hole_removes_the_full_wall_thickness(self) -> None:
        """The point of the hole: a finger must pass through, not scuff the wall."""
        left = self.box("removed_left")
        self.assertAlmostEqual(left.position[0], 0.0, places=2)
        self.assertAlmostEqual(left.position[0] + left.size[0], 2.0, places=2)

        front = self.box("removed_front")
        self.assertAlmostEqual(front.position[1], 0.0, places=2)
        self.assertAlmostEqual(front.position[1] + front.size[1], 2.0, places=2)

    def test_a_hole_hangs_from_the_interior_top_not_the_rim(self) -> None:
        """FR-043b1. The spec here has a 2mm lid, so the interior tops out at
        38 and the cut must stop there rather than at the box's own 40.

        Only the top is asserted: this measures the *difference* of two
        independently meshed bodies, which can disagree by a facet down in the
        bottom fillet and report a sliver below the cut.
        """
        lidless = self.box("removed_lidless")
        lidded = self.box("removed_lidded")
        lidless_top = lidless.position[2] + lidless.size[2]
        lidded_top = lidded.position[2] + lidded.size[2]

        # No lid: the interior runs to the rim, so the cut reaches it.
        self.assertAlmostEqual(lidless_top, 40.0, delta=0.05)
        # 2mm lid: the interior tops out at 38, and the cut stops there rather
        # than carving through the band the lid seats in. The window's fillet
        # reaches that plane exactly *on* the wall's faces, which the body's own
        # surface excludes, so the top the difference can show sits a fraction
        # of a millimetre under it — the same effect as at the cut's bottom.
        self.assertAlmostEqual(lidded_top, 38.0, delta=0.15)
        self.assertLessEqual(lidded_top, 38.0 + 1e-6, "the cut reached the lid band")

    def test_depth_is_capped_at_the_interior_so_the_base_survives(self) -> None:
        """A hole asked to reach 100mm into a 40mm box stops inside the floor.

        Capped at the interior depth, the cut reaches the well floor and dips
        the default 0.2mm past it, so floor material is left underneath and the
        base is never opened.

        The exact depth is asserted on the scoop solid rather than here: this
        measures the *difference* of two independently meshed bodies, which can
        disagree by a facet in the bottom fillet and report a near-zero-volume
        sliver below the cut.
        """
        removed = self.box("removed_deep")
        floor_left = removed.position[2]
        self.assertGreater(floor_left, 0.0, "the cut opened the box's base")
        self.assertGreater(floor_left, 0.5, "too little floor left under the cut")

    def test_the_capped_cut_itself_stops_inside_the_floor(self) -> None:
        """The scoop solid, measured directly: floor at 1.6, dipping 0.2 past."""
        scoop = self.box("deep_scoop_solid")
        self.assertAlmostEqual(scoop.position[2], 1.6 - 0.2, places=2)


class FingerHoleBuilderTests(unittest.TestCase):
    """The builder API for exterior holes (pure Python)."""

    def project_box(self):
        from pyboxbuilder import BoxType, Project

        project = Project("Holes", game_box_size=(200, 150, 60))
        return project.box(BoxType.NO_LID, "Tray", size=(100, 80, 40))

    def test_finger_hole_registers_on_the_box(self) -> None:
        box = self.project_box()
        hole = box.finger_hole(ScoopSide.LEFT, radius=12.0, depth=8.0)
        self.assertEqual(box.finger_holes, (hole,))
        self.assertIs(hole.side, ScoopSide.LEFT)
        self.assertEqual(hole.radius, 12.0)

    def test_several_holes_accumulate(self) -> None:
        box = self.project_box()
        box.finger_hole(ScoopSide.LEFT)
        box.finger_hole(ScoopSide.RIGHT)
        self.assertEqual([h.side for h in box.finger_holes], [ScoopSide.LEFT, ScoopSide.RIGHT])

    def test_bare_string_side_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.project_box().finger_hole("left")

    def test_non_positive_dimensions_rejected(self) -> None:
        box = self.project_box()
        with self.assertRaises(ValueError):
            box.finger_hole(ScoopSide.LEFT, radius=0)
        with self.assertRaises(ValueError):
            box.finger_hole(ScoopSide.LEFT, depth=-1)


class NoLidFingerHoleTests(unittest.TestCase):
    """FR-047: a no-lid box puts default finger holes in its longer walls."""

    def spec(self, **overrides) -> dict:
        base = dict(
            width=100, length=80, height=40,
            wall_thickness=2.0, floor_thickness=2.0,
        )
        base.update(overrides)
        return base

    def test_the_holes_follow_the_original_sizing(self) -> None:
        from pyboxbuilder.box.shell import no_lid_finger_holes

        # width 100 > length 80, so the longer side is the width → FRONT/BACK.
        holes = no_lid_finger_holes(self.spec())
        self.assertEqual([h.side for h in holes], [ScoopSide.FRONT, ScoopSide.BACK])
        for hole in holes:
            self.assertEqual(hole.radius, 20.0)  # min(20, 80/4=20, 40-2+1=39)
            self.assertEqual(hole.depth, 20.0)   # min(20, 40-2+1=39)
            self.assertEqual(hole.rounding_radius, 3.0)

    def test_the_longer_dimension_chooses_the_side(self) -> None:
        from pyboxbuilder.box.shell import no_lid_finger_holes

        holes = no_lid_finger_holes(self.spec(width=80, length=120))
        self.assertEqual([h.side for h in holes], [ScoopSide.LEFT, ScoopSide.RIGHT])

    def test_the_cut_leaves_five_millimetres_of_wall_under_it(self) -> None:
        """SC-065/FR-047: the strip below the cut is what the tray is lifted by.

        The reach reads as `min(radius, height - ft - 5)`, and it is the second
        term that matters here — checked on boxes short enough for it to bind,
        since on a tall one the radius wins and the rule is invisible. It used
        to leave `wall + 1`, which is a 3mm ribbon on the usual wall: it prints,
        and it flexes.
        """
        from pyboxbuilder.box.shell import MIN_WALL_BELOW_HOLE_MM, no_lid_finger_holes

        for height, floor, wall in ((40, 2.0, 2.0), (14, 1.6, 2.0), (12, 2.0, 3.0)):
            with self.subTest(height=height):
                spec = self.spec(height=height, floor_thickness=floor,
                                 wall_thickness=wall)
                holes = no_lid_finger_holes(spec)
                self.assertTrue(holes, "the sizing rule dropped the holes entirely")
                for hole in holes:
                    left = (height - floor) - hole.depth
                    self.assertGreaterEqual(
                        round(left, 6), MIN_WALL_BELOW_HOLE_MM,
                        f"only {left}mm of tray wall left below the cut",
                    )

    def test_the_cut_is_never_deeper_than_half_the_box(self) -> None:
        """SC-068/FR-047: a fingertip's radius is 20mm and a tray is often 25mm
        tall, so without this the cut takes four fifths of the wall and what is
        left reads as two posts and a bridge.

        Checked where the cap binds (a shallow-to-middling tray) and where it
        does not (a deep one, sized by the finger instead).
        """
        from pyboxbuilder.box.shell import no_lid_finger_holes

        for height, expected in ((25, 12.5), (30, 15.0), (50, 20.0)):
            with self.subTest(height=height):
                holes = no_lid_finger_holes(self.spec(height=height))
                self.assertTrue(holes)
                for hole in holes:
                    self.assertLessEqual(hole.depth, height / 2 + 1e-9)
                    self.assertAlmostEqual(hole.depth, expected, places=6)

    def test_a_tray_with_no_room_for_the_strip_gets_no_holes(self) -> None:
        """The strip wins over the cut (FR-047a/SC-065).

        A 2mm floor on the reach is what this used to have, and it bought the
        dip out of the very wall the rule protects. A tray this short is
        liftable by its walls.
        """
        from pyboxbuilder.box.shell import no_lid_finger_holes

        self.assertEqual(no_lid_finger_holes(self.spec(height=5, floor_thickness=1.6)), ())
        self.assertEqual(no_lid_finger_holes(self.spec(height=8, floor_thickness=1.6)), ())
        self.assertTrue(no_lid_finger_holes(self.spec(height=9, floor_thickness=1.6)))

    def test_a_hole_too_wide_for_its_wall_is_skipped(self) -> None:
        from pyboxbuilder.box.shell import no_lid_finger_holes

        # radius = 12/4 = 3, mouth = 2*(3+3) = 12 > span 12-4 = 8 → no holes.
        self.assertEqual(no_lid_finger_holes(self.spec(width=12, length=12, height=10)), ())

    def test_auto_holes_are_added_and_can_be_opted_out(self) -> None:
        from pyboxbuilder.box.shell import add_no_lid_finger_holes

        spec = self.spec()
        add_no_lid_finger_holes(spec)
        self.assertEqual(len(spec["finger_holes"]), 2)

        opted = self.spec(auto_finger_holes=False)
        add_no_lid_finger_holes(opted)
        self.assertIsNone(opted.get("finger_holes"))

    def test_a_polygon_path_box_gets_none(self) -> None:
        """FR-047c/SC-064: the rule names four walls and a longer side, and a
        polygon has neither — `no_lid_finger_holes` would read its bounding box
        and cut into a wall that need not exist."""
        from pyboxbuilder.box.types.path import PathBox

        hexagon = [(0, 20), (17, 10), (17, -10), (0, -20), (-17, -10), (-17, 10)]
        spec = self.spec(path=tuple(hexagon))
        PathBox().build_body(spec)
        self.assertFalse(spec.get("finger_holes"))

        plain = self.spec()
        PathBox().build_body(plain)
        self.assertEqual(len(plain["finger_holes"]), 2)

    def test_explicit_holes_beat_the_automatic_ones(self) -> None:
        from pyboxbuilder.box.shell import add_no_lid_finger_holes

        spec = self.spec(finger_holes=(object(),))
        add_no_lid_finger_holes(spec)
        self.assertEqual(len(spec["finger_holes"]), 1)


if __name__ == "__main__":
    unittest.main()


class TwoRadiusProfileTests(unittest.TestCase):
    """FR-043a: an edge scoop is r1 at the rim, r2 into a flat bottom."""

    def outline(self, profile) -> str:
        return repr(profile)

    def test_both_radii_change_the_profile(self) -> None:
        square = scoop_profile(10, 30, 0, 0)
        top_only = scoop_profile(10, 30, 6, 0)
        both = scoop_profile(10, 30, 6, 5)
        self.assertNotEqual(self.outline(square), self.outline(top_only))
        self.assertNotEqual(self.outline(top_only), self.outline(both))

    def test_bottom_radius_defaults_to_a_share_of_the_throat(self) -> None:
        from pyboxbuilder.compartments.finger_hole import DEFAULT_BOTTOM_ROUNDING_RATIO

        self.assertEqual(
            self.outline(scoop_profile(10, 30, 6)),
            self.outline(scoop_profile(10, 30, 6, 10 * DEFAULT_BOTTOM_ROUNDING_RATIO)),
        )

    def test_radii_are_scaled_down_to_fit_a_shallow_scoop(self) -> None:
        """r1 + r2 cannot exceed the height; a shallow scoop shrinks both."""
        self.assertIsNotNone(scoop_profile(10, 4, 8, 8))

    def test_bottom_radius_cannot_exceed_the_throat(self) -> None:
        self.assertEqual(
            self.outline(scoop_profile(10, 30, 6, 50)),
            self.outline(scoop_profile(10, 30, 6, 10)),
        )

    def test_bad_inputs_rejected(self) -> None:
        for kwargs in ({"top_rounding": -1}, {"bottom_rounding": -1}):
            with self.subTest(**kwargs), self.assertRaises(ValueError):
                scoop_profile(10, 30, **kwargs)

    def test_the_floor_bore_is_a_different_shape(self) -> None:
        """An edge scoop is a channel; a floor hole is a bore. Not the same."""
        edge = scoop_profile(10, 20, 3)
        floor = floor_bore_profile(10, 20, 3)
        self.assertNotEqual(self.outline(edge), self.outline(floor))

    def test_the_floor_bore_validates_its_inputs(self) -> None:
        for args in ((0, 20, 3), (10, 0, 3), (10, 20, -1)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                floor_bore_profile(*args)


if __name__ == "__main__":
    unittest.main()


class FlatBottomTests(unittest.TestCase):
    """The base of an edge scoop keeps a flat run for a piece to sit on."""

    def test_r2_is_capped_so_the_flat_survives(self) -> None:
        from pyboxbuilder.compartments.finger_hole import MIN_FLAT_BOTTOM_RATIO

        radius = 10.0
        cap = radius * (1.0 - MIN_FLAT_BOTTOM_RATIO)
        # Anything at or past the cap gives the same profile as the cap itself.
        self.assertEqual(
            repr(scoop_profile(radius, 30, 6, 1000)),
            repr(scoop_profile(radius, 30, 6, cap)),
        )

    def test_the_cap_leaves_a_real_flat_run(self) -> None:
        from pyboxbuilder.compartments.finger_hole import MIN_FLAT_BOTTOM_RATIO

        self.assertGreater(MIN_FLAT_BOTTOM_RATIO, 0.0)
        self.assertLess(MIN_FLAT_BOTTOM_RATIO, 1.0)

    def test_the_floor_fillet_is_generous_but_leaves_a_flat(self) -> None:
        """It lives inside the throat, so it costs no mouth width and can
        afford a wide curve — but not the whole base."""
        from pyboxbuilder.compartments.finger_hole import (
            DEFAULT_BOTTOM_ROUNDING_RATIO,
            MIN_FLAT_BOTTOM_RATIO,
        )

        self.assertGreater(DEFAULT_BOTTOM_ROUNDING_RATIO, 0.5)
        self.assertLessEqual(
            DEFAULT_BOTTOM_ROUNDING_RATIO, 1.0 - MIN_FLAT_BOTTOM_RATIO
        )


class DerivedDefaultTests(unittest.TestCase):
    """FR-043a2/a3: the defaults have to work with no overrides."""

    def test_r1_scales_with_the_throat(self) -> None:
        """A fixed r1 is invisible on a big scoop and huge on a small one."""
        from pyboxbuilder.compartments.finger_hole import (
            DEFAULT_TOP_ROUNDING_RATIO,
            scoop_profile,
        )

        for radius in (4.0, 14.0):
            with self.subTest(radius=radius):
                derived = build_wall_scoop(200, 200, 30, ScoopSide.FRONT, radius=radius)
                explicit = build_wall_scoop(
                    200, 200, 30, ScoopSide.FRONT, radius=radius,
                    rounding_radius=radius * DEFAULT_TOP_ROUNDING_RATIO,
                )
                self.assertEqual(repr(derived), repr(explicit))
                self.assertIsNotNone(scoop_profile(radius, 30))

    def test_a_narrow_span_shrinks_both_not_just_r1(self) -> None:
        """The bug: capping the throat first left r1 at exactly zero."""
        from pyboxbuilder.compartments.finger_hole import scoop_profile

        span, radius = 20.0, 14.0
        narrow = build_wall_scoop(span, 40, 30, ScoopSide.FRONT, radius=radius)
        # r1 zeroed would make it identical to a scoop built with no roll at all.
        flat = build_wall_scoop(span, 40, 30, ScoopSide.FRONT, radius=radius,
                                rounding_radius=0.0)
        self.assertNotEqual(repr(narrow), repr(flat), "the top roll was zeroed")
        self.assertIsNotNone(scoop_profile(radius, 30))

    def test_hole_height_follows_the_radius(self) -> None:
        """`depth=None` means "as tall as the finger", not a fixed 6mm."""
        from pyboxbuilder.builders._base import FingerHoleBuilder

        self.assertIsNone(FingerHoleBuilder(side=ScoopSide.FRONT).depth)
        self.assertEqual(FingerHoleBuilder(side=ScoopSide.FRONT).radius, 14.0)


@unittest.skipUnless(render_available(), "PythonSCAD binary not available")
class HoleAlignmentTests(unittest.TestCase):
    """FR-043b1/b2: one call, right place, on every walled type."""

    @classmethod
    def setUpClass(cls) -> None:
        body = '''
from pyboxbuilder import BoxType, Project, ScoopSide
from pybosl2 import cuboid

for name in ("no_lid", "sliding", "cap", "slipover"):
    project = Project("A", game_box_size=(400, 200, 60), generate_spacers=False)
    # auto_finger_holes=False keeps the plain box free of FR-047's default
    # holes, so `plain - holed` isolates the one explicit finger_hole() call.
    box = project.box(BoxType(name), name, size=(100, 80, 40), position=(0, 0, 0),
                      auto_finger_holes=False)
    project._resolve_final_layout()
    plain = project._build_box_solids(box)[0]
    box.finger_hole(ScoopSide.FRONT)
    project._resolve_final_layout()
    holed = project._build_box_solids(box)[0]
    measure(name + "_removed", plain - holed)
    measure(name + "_body", holed)
cuboid([1, 1, 1]).show()
'''
        cls.result = measure_python(body)
        if not cls.result.ok:
            raise AssertionError(f"measurement run failed: {cls.result.error}")

    def test_every_type_gets_a_real_cut(self) -> None:
        for name in ("no_lid", "sliding", "cap", "slipover"):
            with self.subTest(box_type=name):
                removed = self.result.boxes[name + "_removed"]
                self.assertGreater(removed.size[0], 10.0, "the cut is a nick, not a scoop")
                self.assertGreater(removed.size[2], 5.0, "the cut is too shallow to use")

    def test_the_cut_starts_at_the_interior_top_not_the_rim(self) -> None:
        """On a lidded box the rim is above the interior; the hole follows the
        interior, so its top stops short of the box's own top."""
        lidless = self.result.boxes["no_lid_removed"]
        sliding = self.result.boxes["sliding_removed"]
        lidless_top = lidless.position[2] + lidless.size[2]
        sliding_top = sliding.position[2] + sliding.size[2]
        self.assertLess(sliding_top, lidless_top,
                        "the lidded box's hole was aligned to the rim")

    def test_the_cut_spans_exactly_the_depth_it_was_given(self) -> None:
        """FR-043a/T306: the roll finishes tangent to the rim, and the cut
        bottoms out its own depth below it.

        Both ends are set by the *outline's* height. Sizing the outline to the
        reach and then sliding the whole solid up to correct one end — which is
        what it took to stop the cut running deep — moves the other end with
        it, and the roll ends up finishing above the rim, so what the top face
        meets is the roll sliced through mid-curve rather than tangentially.
        """
        from pyboxbuilder.builders._base import FingerHoleBuilder

        removed = self.result.boxes["no_lid_removed"]
        top = removed.position[2] + removed.size[2]
        self.assertAlmostEqual(top, 40.0, delta=0.05,
                               msg="the roll does not finish at the rim")
        # The flare reaches its full depth *on* the wall's face, and the cut
        # crosses the face with 0.015 of fudge to spare, so the deepest point
        # the body itself can show sits a fraction of a millimetre inside it.
        # The error this guards against is a whole flare (1mm), not this.
        self.assertAlmostEqual(removed.size[2], FingerHoleBuilder.radius,
                               delta=0.2,
                               msg="the cut is not the depth it was asked for")

    def test_a_walled_over_hole_is_a_closed_window(self) -> None:
        """FR-043b1a/SC-058: where wall stands above the cut it is a window.

        A scoop trimmed off at the interior top leaves its ceiling meeting each
        face of the wall at a square edge, with the face fillet stopping dead at
        the trim — the one sharp edge in the library a finger is guaranteed to
        touch. With no surface for the mouth roll to roll onto, the cut is
        closed and filleted the whole way round instead.

        Measured on the outline, which is where the difference lives: the scoop
        is open at the top (its widest point is its last one), the window is
        not.
        """
        from pyboxbuilder.compartments.finger_hole import (
            scoop_outline, window_outline,
        )

        window = window_outline(14.0, 12.0, 4.0)
        tops = [y for _, y in window]
        self.assertAlmostEqual(max(tops), 12.0, places=6)
        # Closed: the topmost points are inset from the widest ones, so the
        # ring turns back on itself instead of running off the top.
        widest = max(abs(x) for x, _ in window)
        top_run = max(abs(x) for x, y in window if abs(y - 12.0) < 1e-9)
        self.assertLess(top_run, widest - 1.0, "the window is open at the top")

        scoop = scoop_outline(14.0, 12.0, 3.0, 4.0, 4.8)
        scoop_top = max(y for _, y in scoop)
        self.assertGreater(scoop_top, 12.0, "the scoop lost its rim overshoot")

    def test_no_type_is_enlarged_by_its_hole(self) -> None:
        for name in ("no_lid", "sliding", "cap", "slipover"):
            with self.subTest(box_type=name):
                box = self.result.boxes[name + "_body"]
                self.assertLessEqual(box.size[0], 100.5)
                self.assertLessEqual(box.size[1], 80.5)


@unittest.skipUnless(render_available(), "PythonSCAD binary not available")
class FaceRoundoverTests(unittest.TestCase):
    """FR-044e: the cut is wider at the face than mid-wall, or it is a cove.

    This is the measurement that separates the two, and it is the one that has
    caught the mistake three times: a cove and a roundover look equally smooth
    in a render, and differ only in which surface they are tangent to.
    """

    @classmethod
    def setUpClass(cls) -> None:
        body = '''
from pyboxbuilder.compartments.finger_hole import build_wall_scoop
from pyboxbuilder.enums import ScoopSide
from pybosl2 import cuboid

# 4mm wall, 2mm face fillet. The wall spans y = -4 .. 0.
scoop = build_wall_scoop(96, 76, 20, ScoopSide.FRONT, radius=14,
                         wall_thickness=4, rounding_edge=2.0)
for y, name in ((-3.9, "at_face"), (-2.0, "mid_wall")):
    measure(name, scoop & cuboid([300, 0.2, 300]).translate([0, y, 0]))

# With the fillet off there is nothing to widen: the two match.
square = build_wall_scoop(96, 76, 20, ScoopSide.FRONT, radius=14,
                          wall_thickness=4, rounding_edge=0.0)
for y, name in ((-3.9, "square_at_face"), (-2.0, "square_mid_wall")):
    measure(name, square & cuboid([300, 0.2, 300]).translate([0, y, 0]))
cuboid([1, 1, 1]).show()
'''
        cls.result = measure_python(body)
        if not cls.result.ok:
            raise AssertionError(f"measurement run failed: {cls.result.error}")

    def width(self, name: str) -> float:
        return self.result.boxes[name].size[0]

    def test_the_cut_is_wider_at_the_face(self) -> None:
        """A cove would make it *narrower* at the face, gouging the inside."""
        self.assertGreater(
            self.width("at_face"), self.width("mid_wall") + 1.0,
            "the fillet hollowed the wall instead of rolling the face in",
        )

    def test_it_widens_by_about_the_fillet_radius_each_side(self) -> None:
        self.assertAlmostEqual(
            self.width("at_face") - self.width("mid_wall"), 4.0, delta=0.5,
        )

    def test_no_fillet_means_no_widening(self) -> None:
        self.assertAlmostEqual(
            self.width("square_at_face"), self.width("square_mid_wall"), delta=0.1,
        )


class TangentJoinTests(unittest.TestCase):
    """FR-043a4: the run between the arcs is a solved common tangent."""

    def test_it_finds_the_throat_for_the_usual_placement(self) -> None:
        from pyboxbuilder.compartments.finger_hole import _tangent_join

        radius, r1, r2, height = 10.0, 7.0, 5.0, 30.0
        low, high = _tangent_join(
            (radius - r2, r2), r2, (radius + r1, height - r1), r1, radius,
        )
        # Both circles are placed tangent to x = radius, so that is the answer.
        self.assertAlmostEqual(low[0], radius, places=6)
        self.assertAlmostEqual(high[0], radius, places=6)
        self.assertAlmostEqual(low[1], r2, places=6)
        self.assertAlmostEqual(high[1], height - r1, places=6)

    def test_it_picks_the_internal_tangent(self) -> None:
        """An external tangent touches both circles on the same side and
        throws the profile wide — the natural filter picks one."""
        from pyboxbuilder.compartments.finger_hole import _tangent_join

        low, high = _tangent_join((5.0, 5.0), 5.0, (17.0, 23.0), 7.0, 10.0)
        self.assertLess(high[0], 17.0, "touched the rim circle on its far side")
        self.assertGreater(low[0], 5.0, "touched the floor circle on its far side")

    def test_it_falls_back_when_a_radius_is_zero(self) -> None:
        from pyboxbuilder.compartments.finger_hole import _tangent_join

        low, high = _tangent_join((10.0, 0.0), 0.0, (17.0, 23.0), 7.0, 10.0)
        self.assertAlmostEqual(low[0], 10.0)
        self.assertAlmostEqual(high[0], 10.0)


class ScoopSideDefaultTests(unittest.TestCase):
    """FR-043b4: the cut goes in the short wall unless told otherwise."""

    def placement(self, size):
        from pyboxbuilder.compartments.layout import CompartmentPlacement

        return CompartmentPlacement("c", size, 20.0, (0.0, 0.0))

    def test_wide_compartment_cuts_the_short_wall(self) -> None:
        from pyboxbuilder.compartments.carve import default_scoop_side

        self.assertIs(default_scoop_side(self.placement((92.0, 67.0))), ScoopSide.LEFT)

    def test_deep_compartment_cuts_the_short_wall(self) -> None:
        from pyboxbuilder.compartments.carve import default_scoop_side

        self.assertIs(default_scoop_side(self.placement((67.0, 92.0))), ScoopSide.FRONT)

    def test_an_explicit_side_still_wins(self) -> None:
        from pyboxbuilder.compartments.builder import CompartmentBuilder

        explicit = CompartmentBuilder(label="c", size=(92.0, 67.0),
                                      finger_scoop=True, scoop_side=ScoopSide.BACK)
        self.assertIs(explicit.scoop_side, ScoopSide.BACK)
        # Unspecified stays None so the short-wall rule can apply.
        self.assertIsNone(CompartmentBuilder(label="c", size=(92.0, 67.0)).scoop_side)


class SlidingLidAxisTests(unittest.TestCase):
    """FR-002b: the lid leaves through the shorter face."""

    def box(self):
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
        from pyboxbuilder.enums import BoxType

        return BOX_IMPL_REGISTRY[BoxType.SLIDING]()

    def test_a_long_box_slides_along_its_length(self) -> None:
        self.assertTrue(self.box().slides_along_length(
            {"width": 90.0, "length": 98.0}))

    def test_a_wide_box_slides_along_its_width(self) -> None:
        self.assertFalse(self.box().slides_along_length(
            {"width": 120.0, "length": 60.0}))


class SlidingScoopAndLidEdgeTests(unittest.TestCase):
    """FR-043b6 / FR-044h / FR-044i: the lid dictates both."""

    def box(self, box_type):
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY

        return BOX_IMPL_REGISTRY[box_type]()

    def test_a_sliding_scoop_goes_in_the_exit_wall(self) -> None:
        from pyboxbuilder.box.base import preferred_scoop_side
        from pyboxbuilder.enums import BoxType

        box = self.box(BoxType.SLIDING)
        # Longer than wide: slides along Y, so it exits the BACK wall.
        self.assertIs(
            preferred_scoop_side(box, {"width": 90.0, "length": 98.0}), ScoopSide.BACK
        )
        # Wider than long: slides along X, so it exits the RIGHT wall.
        self.assertIs(
            preferred_scoop_side(box, {"width": 120.0, "length": 60.0}), ScoopSide.RIGHT
        )

    def test_the_type_beats_the_compartment_shape(self) -> None:
        """A wide compartment would otherwise take the LEFT wall, which on a
        sliding box is a groove wall."""
        from pyboxbuilder.box.base import preferred_scoop_side
        from pyboxbuilder.compartments.carve import default_scoop_side
        from pyboxbuilder.compartments.layout import CompartmentPlacement
        from pyboxbuilder.enums import BoxType

        wide = CompartmentPlacement("c", (92.0, 67.0), 20.0, (0.0, 0.0))
        self.assertIs(default_scoop_side(wide), ScoopSide.LEFT)
        self.assertIs(
            preferred_scoop_side(self.box(BoxType.SLIDING), {"width": 90.0, "length": 98.0}),
            ScoopSide.BACK,
        )

    def test_types_without_an_opinion_leave_it_to_the_shape(self) -> None:
        from pyboxbuilder.box.base import preferred_scoop_side
        from pyboxbuilder.enums import BoxType

        for box_type in (BoxType.CAP, BoxType.NO_LID, BoxType.SLIPOVER):
            with self.subTest(box_type=box_type.value):
                self.assertIsNone(
                    preferred_scoop_side(self.box(box_type), {"width": 90.0, "length": 98.0})
                )

    def test_a_sliding_lid_rounds_only_its_exit_end(self) -> None:
        from pybosl2._edges_lang import edges

        from pyboxbuilder.box.base import lid_rounded_edges
        from pyboxbuilder.enums import BoxType

        spec = {"width": 90.0, "length": 98.0}
        sliding = edges(lid_rounded_edges(self.box(BoxType.SLIDING), spec))
        self.assertEqual(sum(sum(row) for row in sliding), 3,
                         "a sliding lid must not round its groove edges")

    def test_a_cap_lid_rounds_all_its_outside_edges(self) -> None:
        from pybosl2._edges_lang import edges

        from pyboxbuilder.box.base import lid_rounded_edges
        from pyboxbuilder.enums import BoxType

        cap = edges(lid_rounded_edges(self.box(BoxType.CAP), {"width": 90.0, "length": 98.0}))
        self.assertEqual(sum(sum(row) for row in cap), 8)

    def test_the_lid_radius_is_capped_by_its_thickness(self) -> None:
        from pyboxbuilder.rounding import lid_rounding

        # A 4mm wall would give a 2mm body radius; a 2mm lid may take 1mm.
        self.assertEqual(lid_rounding({"wall_thickness": 4.0, "lid_thickness": 2.0}), 1.0)
        # A thick lid is not the constraint, so the body radius stands.
        self.assertEqual(lid_rounding({"wall_thickness": 2.0, "lid_thickness": 8.0}), 1.0)


class WallTopTests(unittest.TestCase):
    """FR-043b7/b8: each wall's top is its own, not the box's."""

    def box(self, box_type):
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY

        return BOX_IMPL_REGISTRY[box_type]()

    def spec(self, **kwargs):
        base = dict(width=98.0, length=73.0, height=52.5,
                    wall_thickness=2.0, lid_thickness=2.0, floor_thickness=2.0)
        base.update(kwargs)
        return base

    def test_a_lidless_box_ends_at_its_own_top(self) -> None:
        from pyboxbuilder.box.base import wall_tops
        from pyboxbuilder.enums import BoxType

        tops = wall_tops(self.box(BoxType.NO_LID), self.spec(rim_free=True))
        for side, z in tops.items():
            with self.subTest(side=side.value):
                self.assertAlmostEqual(z, 52.5)

    def test_a_sliding_box_stops_at_its_channel(self) -> None:
        """Its exit wall's material ends there, and cutting the others above
        that line would break into the channel the lid rides in."""
        from pyboxbuilder.box.base import wall_tops
        from pyboxbuilder.enums import BoxType

        tops = wall_tops(self.box(BoxType.SLIDING), self.spec())
        for side, z in tops.items():
            with self.subTest(side=side.value):
                self.assertAlmostEqual(z, 50.5)

    def test_every_side_is_covered(self) -> None:
        from pyboxbuilder.box.base import wall_tops
        from pyboxbuilder.enums import BoxType

        tops = wall_tops(self.box(BoxType.CAP), self.spec())
        self.assertEqual(set(tops), set(ScoopSide))

    def test_a_spec_carrying_the_map_is_read_per_side(self) -> None:
        from pyboxbuilder.box.base import wall_top

        spec = self.spec(wall_tops={ScoopSide.BACK: 40.0})
        self.assertAlmostEqual(wall_top(spec, ScoopSide.BACK), 40.0)
        # A side the map does not mention falls back to the generic rule.
        self.assertAlmostEqual(wall_top(spec, ScoopSide.FRONT), 50.5)

    def test_without_a_map_it_still_allows_for_the_lid(self) -> None:
        from pyboxbuilder.box.base import default_wall_top

        self.assertAlmostEqual(default_wall_top(self.spec()), 50.5)
        self.assertAlmostEqual(default_wall_top(self.spec(rim_free=True)), 52.5)
        # An explicit interior_top wins, for bodies already shortened.
        self.assertAlmostEqual(default_wall_top(self.spec(interior_top=30.0)), 30.0)


class PullOutRollTests(unittest.TestCase):
    """FR-043c1: the roll spans the scoop's depth, not a token radius."""

    def test_only_the_vertical_extents_compete_for_the_height(self) -> None:
        """A shallow wall shortens the roll's rise and leaves the width alone.

        Tying the two together is what lost the player card box its top curve:
        the wall had height to spare for a curve and none to spare for a wider
        mouth, and one number was deciding both.
        """
        from pyboxbuilder.compartments.finger_hole import _fit_radii

        deep_flare, deep_rise, _ = _fit_radii(12.0, 26.0, 6.0, None)
        shallow_flare, shallow_rise, _ = _fit_radii(12.0, 6.5, 6.0, None)
        self.assertAlmostEqual(deep_flare, shallow_flare,
                               msg="the mouth narrowed on the shallow wall")
        self.assertLess(shallow_rise, deep_rise)
        self.assertGreater(shallow_rise, 0.0, "the shallow wall lost its curve")

    def test_the_rise_is_a_multiple_of_the_flare(self) -> None:
        from pyboxbuilder.compartments.finger_hole import (
            TOP_ROLL_RISE_RATIO,
            _fit_radii,
        )

        flare, rise, _ = _fit_radii(12.0, 100.0, 6.0, None)
        self.assertAlmostEqual(rise, flare * TOP_ROLL_RISE_RATIO)

    def test_the_vertical_extents_fit_the_height(self) -> None:
        _, rise, r2 = self.fit(12.0, 18.0)
        self.assertLessEqual(rise + r2, 18.0 + 1e-9)

    def fit(self, radius, height):
        from pyboxbuilder.compartments.finger_hole import _fit_radii

        return _fit_radii(radius, height, radius * 0.5, None)


class ScoopCurveSourcesTests(unittest.TestCase):
    """FR-043e/SC-054: the two curves are sized from two different quantities."""

    def fillet(self, radius: float, rounding: float, height: float = 40.0) -> float:
        """The floor fillet `build_wall_scoop` would actually use.

        Measured on a deep scoop by default, because the two curves do share
        one budget — the height — and on a shallow one both shrink together.
        That coupling is real; being sized off the same *radius* was not.
        """
        from pyboxbuilder.compartments.finger_hole import _fit_radii

        _, _, r2 = _fit_radii(radius, height, rounding, None)
        return r2

    def test_the_floor_fillet_ignores_the_rounding_radius(self) -> None:
        """It was fed the top roll's rise — 1.6x the flare — so both curves of
        the U moved together with the mouth's flare."""
        self.assertAlmostEqual(
            self.fillet(14.0, 7.0), self.fillet(14.0, 3.0), places=6
        )

    def test_a_shallow_scoop_still_shares_the_height(self) -> None:
        """The one coupling that is legitimate: both curves compete for the
        depth available, so on a shallow cut both are scaled back together."""
        self.assertLess(
            self.fillet(14.0, 7.0, height=12.0), self.fillet(14.0, 7.0)
        )

    def test_the_floor_fillet_follows_the_throat_radius(self) -> None:
        self.assertGreater(self.fillet(20.0, 7.0), self.fillet(10.0, 7.0))

    def test_the_outline_gets_the_fillet_not_the_rise(self) -> None:
        """The splat that caused it: `_fit_radii` returns (flare, rise, r2) and
        `scoop_outline` takes (top_rounding, bottom_rounding, top_rise)."""
        from pyboxbuilder.compartments.finger_hole import (
            _fit_radii, build_wall_scoop,
        )
        from pyboxbuilder.enums import ScoopSide

        flare, rise, r2 = _fit_radii(14.0, 20.0, 7.0, None)
        self.assertNotAlmostEqual(rise, r2, places=2)
        # Building must not raise, and must use the same numbers.
        build_wall_scoop(60.0, 60.0, 20.0, ScoopSide.FRONT, radius=14.0)


class ScoopFlareAlignmentTests(unittest.TestCase):
    """T306/FR-043g: a scoop's solid is taller than the height it was asked for."""

    def test_the_flare_reaches_below_the_outline(self) -> None:
        """The face fillet is isotropic in the profile plane, so it grows down
        past the flat bottom exactly as readily as it grows sideways."""
        from pyboxbuilder.compartments.finger_hole import (
            build_wall_scoop, scoop_face_flare,
        )
        from pyboxbuilder.enums import ScoopSide

        wt = 2.0
        # Unclipped, so the flare's own reach is what is measured. With the
        # default floor clip in force it is sliced at the dip instead — which
        # is correct for a compartment scoop bottoming on the floor, and is
        # why an exterior hole passes a `floor_clearance` that lets it finish.
        scoop = build_wall_scoop(
            76.0, 56.0, 14.0, ScoopSide.FRONT, radius=14.0, wall_thickness=wt,
            breach_floor=True,
        )
        centre, size = scoop.bounds()
        bottom = centre[2] - size[2] / 2
        self.assertAlmostEqual(bottom, -scoop_face_flare(wt), delta=0.05)

    def test_the_flare_is_half_the_wall(self) -> None:
        from pyboxbuilder.compartments.finger_hole import scoop_face_flare

        for wall in (2.0, 3.0, 4.0):
            with self.subTest(wall=wall):
                self.assertAlmostEqual(scoop_face_flare(wall), wall / 2, places=6)

    def test_an_explicit_edge_rounding_is_respected(self) -> None:
        from pyboxbuilder.compartments.finger_hole import scoop_face_flare

        self.assertAlmostEqual(scoop_face_flare(4.0, 0.5), 0.5, places=6)
        self.assertEqual(scoop_face_flare(2.0, 0.0), 0.0)

    def test_an_exterior_hole_uses_the_walls_flare(self) -> None:
        from pyboxbuilder.box.shell import _hole_flare
        from pyboxbuilder.builders._base import FingerHoleBuilder
        from pyboxbuilder.enums import ScoopSide

        hole = FingerHoleBuilder(side=ScoopSide.FRONT)
        self.assertAlmostEqual(_hole_flare(3.0, hole, 14.0), 1.5, places=6)

    def test_a_shallow_hole_caps_the_flare_at_half_its_reach(self) -> None:
        """The flare grows past *both* ends of the outline, so on a cut
        shallower than twice the wall's fillet it would leave no outline at
        all — and `build_wall_scoop` rejects a non-positive height."""
        from pyboxbuilder.box.shell import _hole_flare
        from pyboxbuilder.builders._base import FingerHoleBuilder
        from pyboxbuilder.enums import ScoopSide

        hole = FingerHoleBuilder(side=ScoopSide.FRONT)
        self.assertAlmostEqual(_hole_flare(6.0, hole, 2.0), 1.0, places=6)


class RollRiseIsReachableTests(unittest.TestCase):
    """FR-043a0/T313: all four numbers of the outline are settable.

    The rise is the one that says how *gently* the top surface turns into the
    wall, and it was a module constant — so the quantity FR-043c3 exists to
    separate from the mouth's width could not actually be varied by a caller.
    """

    def test_a_given_rise_reaches_the_outline(self) -> None:
        from pyboxbuilder.compartments.finger_hole import _fit_radii

        flare, rise, _ = _fit_radii(14.0, 30.0, 3.0, None, roll_rise=9.0)
        self.assertAlmostEqual(rise, 9.0, places=6)
        self.assertAlmostEqual(flare, 3.0, places=6, msg="the mouth widened with it")

    def test_none_still_derives_it_from_the_flare(self) -> None:
        from pyboxbuilder.compartments.finger_hole import (
            TOP_ROLL_RISE_RATIO, _fit_radii,
        )

        _, rise, _ = _fit_radii(14.0, 30.0, 3.0, None)
        self.assertAlmostEqual(rise, 3.0 * TOP_ROLL_RISE_RATIO, places=6)

    def test_a_hole_carries_it_through_to_the_cut(self) -> None:
        """The builder field reaches the geometry: a gentler roll on the same
        mouth makes the cut taller, not wider."""
        from pyboxbuilder.compartments.finger_hole import build_wall_scoop
        from pyboxbuilder.enums import ScoopSide

        def width(rise: float) -> float:
            scoop = build_wall_scoop(
                76.0, 56.0, 20.0, ScoopSide.FRONT, radius=14.0, wall_thickness=2.0,
                rounding_radius=3.0, roll_rise=rise,
            )
            _, size = scoop.bounds()
            return size[0]

        self.assertAlmostEqual(width(4.8), width(9.0), delta=0.01)


class OverlappingCutsAreReportedTests(unittest.TestCase):
    """FR-006c/SC-063: an overlap is invisible in the geometry, so it is said.

    Two cuts that overlap merge into one opening of a shape nobody specified,
    and the merged solid looks every bit as deliberate as an intended one.
    """

    def spec(self, holes, **overrides) -> dict:
        base = dict(
            label="T", width=100, length=80, height=40,
            wall_thickness=2.0, floor_thickness=2.0, finger_holes=holes,
        )
        base.update(overrides)
        return base

    def hole(self, side, **kw):
        from pyboxbuilder.builders._base import FingerHoleBuilder

        return FingerHoleBuilder(side=side, **kw)

    def test_two_holes_on_one_wall_are_reported(self) -> None:
        from pyboxbuilder.box.shell import finger_cut_conflicts

        holes = (self.hole(ScoopSide.FRONT, offset=-8.0),
                 self.hole(ScoopSide.FRONT, offset=8.0))
        messages = finger_cut_conflicts(self.spec(holes))
        self.assertEqual(len(messages), 1)
        self.assertIn("front", messages[0])
        self.assertIn("overlap", messages[0])

    def test_holes_far_enough_apart_are_not(self) -> None:
        from pyboxbuilder.box.shell import finger_cut_conflicts

        holes = (self.hole(ScoopSide.FRONT, radius=6.0, rounding_radius=2.0, offset=-20.0),
                 self.hole(ScoopSide.FRONT, radius=6.0, rounding_radius=2.0, offset=20.0))
        self.assertEqual(finger_cut_conflicts(self.spec(holes)), [])

    def test_holes_on_different_walls_are_not(self) -> None:
        from pyboxbuilder.box.shell import finger_cut_conflicts

        holes = (self.hole(ScoopSide.FRONT), self.hole(ScoopSide.BACK))
        self.assertEqual(finger_cut_conflicts(self.spec(holes)), [])

    def test_a_hole_over_a_magnet_pocket_is_reported(self) -> None:
        from pyboxbuilder.box.shell import finger_cut_conflicts
        from pyboxbuilder.enums import MagnetType

        # Holes on both pairs leave the magnets nowhere to go, which is the
        # case FR-039a hands to this check rather than guessing at.
        holes = (self.hole(ScoopSide.FRONT), self.hole(ScoopSide.BACK),
                 self.hole(ScoopSide.LEFT), self.hole(ScoopSide.RIGHT))
        # A 20mm box: the cut hangs from the rim by a fingertip's radius and so
        # reaches mid-height, where the pocket is. On a tall box the two miss
        # each other and nothing is reported — checked below.
        messages = finger_cut_conflicts(
            self.spec(holes, height=20, magnet_type=MagnetType.ROUND,
                      magnet_size=(6.0, 6.0, 3.0))
        )
        self.assertTrue(any("magnet" in m for m in messages), messages)

    def test_a_pocket_the_cut_cannot_reach_is_not(self) -> None:
        from pyboxbuilder.box.shell import finger_cut_conflicts
        from pyboxbuilder.enums import MagnetType

        holes = (self.hole(ScoopSide.FRONT), self.hole(ScoopSide.BACK),
                 self.hole(ScoopSide.LEFT), self.hole(ScoopSide.RIGHT))
        messages = finger_cut_conflicts(
            self.spec(holes, height=60, magnet_type=MagnetType.ROUND,
                      magnet_size=(6.0, 6.0, 3.0))
        )
        self.assertFalse([m for m in messages if "magnet" in m], messages)

    def test_the_warning_reaches_the_caller(self) -> None:
        import warnings

        from pyboxbuilder.box.shell import warn_about_finger_cuts

        holes = (self.hole(ScoopSide.FRONT, offset=-8.0),
                 self.hole(ScoopSide.FRONT, offset=8.0))
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            warn_about_finger_cuts(self.spec(holes))
        self.assertEqual(len(caught), 1)
        self.assertIn("T:", str(caught[0].message))


@unittest.skipUnless(render_available(), "PythonSCAD binary not available")
class FingertipFitsTests(unittest.TestCase):
    """SC-062: the cut admits the finger it is sized for.

    Every other criterion here checks a formula or a curve. This one checks the
    thing the whole family exists for, and it holds whichever formula produced
    the cut: a fingertip-sized prism, stood on the flat bottom of a default cut,
    is entirely inside the material removed.
    """

    @classmethod
    def setUpClass(cls) -> None:
        body = '''
import os, re, tempfile, zipfile
from openscad import export
from pyboxbuilder.compartments.finger_hole import build_wall_scoop, build_floor_scoop
from pyboxbuilder.enums import ScoopSide
from pybosl2 import cuboid

def volume(solid):
    with tempfile.NamedTemporaryFile(suffix=".3mf", delete=False) as handle:
        path = handle.name
    try:
        export(solid.shape, path)
        model = zipfile.ZipFile(path).read("3D/3dmodel.model").decode()
    finally:
        os.unlink(path)
    verts = [(float(x), float(y), float(z)) for x, y, z in re.findall(
        r'<vertex x="([-0-9.e+]+)" y="([-0-9.e+]+)" z="([-0-9.e+]+)"', model)]
    total = 0.0
    for a, b, c in re.findall(r'<triangle v1="(\\d+)" v2="(\\d+)" v3="(\\d+)"', model):
        p, q, r = verts[int(a)], verts[int(b)], verts[int(c)]
        total += (p[0]*(q[1]*r[2]-r[1]*q[2]) - p[1]*(q[0]*r[2]-r[0]*q[2])
                  + p[2]*(q[0]*r[1]-r[0]*q[1])) / 6.0
    return abs(total)

# A 14mm-wide fingertip, 8mm tall, standing on the cut's flat bottom in the
# middle of the wall. Wall scoop on a 76 x 56 compartment, 20mm deep.
scoop = build_wall_scoop(76, 56, 20, ScoopSide.FRONT, radius=14, wall_thickness=2)
finger = cuboid([14.0, 1.6, 8.0]).translate([38.0, -1.0, 4.0])
report("wall_finger", "%.4f" % volume(scoop & finger))
report("wall_finger_full", "%.4f" % volume(finger))

bore = build_floor_scoop(76, 56, ScoopSide.FRONT, radius=14, comp_depth=6,
                          wall_thickness=2)
tip = cuboid([14.0, 1.6, 3.0]).translate([38.0, -1.0, 3.0])
report("floor_finger", "%.4f" % volume(bore & tip))
report("floor_finger_full", "%.4f" % volume(tip))
cuboid([1, 1, 1]).show()
'''
        cls.result = measure_python(body)
        if not cls.result.ok:
            raise AssertionError(f"measurement run failed: {cls.result.error}")

    def test_a_fingertip_fits_the_wall_scoop(self) -> None:
        got = float(self.result.reports["wall_finger"])
        want = float(self.result.reports["wall_finger_full"])
        self.assertAlmostEqual(got, want, delta=want * 0.02,
                               msg="the scoop does not admit the finger it is sized for")

    def test_a_fingertip_fits_the_floor_bore(self) -> None:
        got = float(self.result.reports["floor_finger"])
        want = float(self.result.reports["floor_finger_full"])
        self.assertAlmostEqual(got, want, delta=want * 0.05,
                               msg="the bore does not admit the finger it is sized for")


class CornerRadiusIsKeptTests(unittest.TestCase):
    """FR-043a5/FR-043a6/SC-066: the radius asked for is the radius built.

    It used to be narrowed twice over — capped at 0.75 of the half-width to
    protect a flat run that a *grip* does not need, then scaled with the rise to
    fit the height — so 20mm came back 14.4mm with nothing in the geometry to
    say it had been refused. What gives instead is the straight run between the
    circles, which is what solving their common tangent is for.
    """

    def fit(self, half_width, depth, asked, **kw):
        from pyboxbuilder.compartments.finger_hole import _fit_radii

        return _fit_radii(half_width, depth, 3.0, asked, keep_flat_bottom=False, **kw)

    def test_a_radius_the_depth_can_hold_is_kept_exactly(self) -> None:
        for depth in (10.0, 15.0, 19.0, 24.0, 30.0):
            with self.subTest(depth=depth):
                _, _, r2 = self.fit(20.0, depth, 20.0)
                self.assertAlmostEqual(r2, 20.0, places=6)

    def test_a_grip_rolls_on_a_circle(self) -> None:
        """FR-043a7: the flank is the tangent between two circles, and only two
        circles have an exact one — so a grip's roll is circular. The gentler
        ellipse stays with the compartment scoop, whose flank is vertical."""
        flare, rise, _ = self.fit(20.0, 19.0, 20.0)
        self.assertAlmostEqual(rise, flare, places=6)

    def test_a_radius_past_what_the_shape_allows_is_capped_there(self) -> None:
        """The cap is the radius at which the base circle would *touch* the
        roll: past it there is no internal tangent, so no flank."""
        from pyboxbuilder.compartments.finger_hole import dish_radius

        _, rise, r2 = self.fit(20.0, 19.0, 500.0)
        self.assertAlmostEqual(r2, dish_radius(20.0, 19.0, rise), places=6)

    def test_the_cap_never_bites_the_default(self) -> None:
        """The touching radius is never below the half-width, whatever the
        depth, so the default base circle is always the one that gets built."""
        from pyboxbuilder.compartments.finger_hole import dish_radius

        for depth in range(6, 60, 2):
            with self.subTest(depth=depth):
                self.assertGreaterEqual(
                    dish_radius(20.0, float(depth), 3.0), 20.0 - 1e-9
                )

    def test_at_half_the_width_the_base_is_one_round_curve(self) -> None:
        from pyboxbuilder.compartments.finger_hole import scoop_outline

        flare, rise, r2 = self.fit(10.0, 25.0, 10.0)
        ring = scoop_outline(10.0, 25.0, flare, r2, rise)
        flat = [x for x, y in ring if abs(y) < 1e-9]
        self.assertLessEqual(len(flat), 2, "a flat run survived in a round base")
        self.assertAlmostEqual(max(flat) if flat else 0.0, 0.0, places=6)

    def test_a_compartment_scoop_keeps_its_flat_run(self) -> None:
        """FR-043a: something rests on it, so that cut is capped as before."""
        from pyboxbuilder.compartments.finger_hole import _fit_radii, scoop_outline

        flare, rise, r2 = _fit_radii(20.0, 19.0, 3.0, 20.0)
        ring = scoop_outline(20.0, 19.0, flare, r2, rise)
        flat = [x for x, y in ring if abs(y) < 1e-9]
        self.assertGreater(2 * max(flat), 1.0, "the flat bottom closed into a trough")

    def test_width_and_radius_move_independently(self) -> None:
        """FR-043a6: either one changes the outline without the other."""
        wide, _, r2_same = self.fit(20.0, 30.0, 8.0)
        narrow, _, r2_narrow = self.fit(10.0, 30.0, 8.0)
        self.assertAlmostEqual(r2_same, r2_narrow, places=6)

        _, _, r2_small = self.fit(20.0, 30.0, 4.0)
        _, _, r2_big = self.fit(20.0, 30.0, 16.0)
        self.assertNotAlmostEqual(r2_small, r2_big, places=3)

    def test_the_builder_carries_the_radius_and_the_width(self) -> None:
        from pyboxbuilder.builders.no_lid import NoLidBoxBuilder

        box = NoLidBoxBuilder(label="T", size=(100, 80, 40))
        hole = box.finger_hole(ScoopSide.FRONT, width=30.0, bottom_radius=6.0)
        self.assertAlmostEqual(hole.radius, 15.0)
        self.assertAlmostEqual(hole.bottom_radius, 6.0)


class TangentFlankTests(unittest.TestCase):
    """FR-043a7/SC-067: a grip is two circles joined by their internal tangent.

    One construction for every proportion: a base circle on the bottom of the
    cut, the roll at each end, and a straight run touching both. Deep, that run
    comes out vertical and the shape is the familiar round base with straight
    sides; shallow, the same circle presents a long flat sweep and the run
    tilts and lengthens to carry it up to the roll.

    The failure being guarded against is the base circle sized until the two
    circles *touch*: the run collapses to a point and the outline — still
    continuous, still tangent — reads as one wobbling curve with no flank.
    """

    def outline(self, half_width: float, depth: float):
        from pyboxbuilder.compartments.finger_hole import _fit_radii, scoop_outline

        flare, rise, r2 = _fit_radii(
            half_width, depth, 3.0, None, keep_flat_bottom=False
        )
        return scoop_outline(half_width, depth, flare, r2, rise), r2, rise

    def right_half(self, ring, depth):
        """The outline's right side, bottom to rim, without the rim overshoot."""
        return sorted(
            (p for p in ring if p[0] >= -1e-9 and p[1] <= depth + 1e-9),
            key=lambda p: p[1],
        )

    def flank(self, half_width: float, depth: float):
        """The longest straight run in the outline: (length, direction)."""
        import math

        ring, _, _ = self.outline(half_width, depth)
        points = self.right_half(ring, depth)
        segments = [
            (a, b) for a, b in zip(points, points[1:]) if math.dist(a, b) > 1e-9
        ]
        run = max(segments, key=lambda seg: math.dist(*seg))
        angle = math.degrees(
            math.atan2(run[1][1] - run[0][1], run[1][0] - run[0][0])
        )
        return math.dist(*run), angle

    def test_there_is_a_flank_at_every_depth(self) -> None:
        for depth in (8.0, 10.0, 15.0, 20.0, 26.0, 30.0):
            with self.subTest(depth=depth):
                length, _ = self.flank(20.0, depth)
                self.assertGreater(
                    length, 1.0, "the two circles touch — the flank collapsed"
                )

    def test_a_deep_cut_stands_its_flank_up_vertical(self) -> None:
        """Which is the classic straight throat, arrived at rather than
        assumed: nothing in the construction asks for it."""
        for depth in (26.0, 30.0, 40.0):
            with self.subTest(depth=depth):
                _, angle = self.flank(20.0, depth)
                self.assertAlmostEqual(angle, 90.0, delta=0.5)

    def test_a_shallow_cut_lays_its_flank_over(self) -> None:
        for depth, most in ((15.0, 60.0), (10.0, 40.0)):
            with self.subTest(depth=depth):
                _, angle = self.flank(20.0, depth)
                self.assertLess(angle, most)

    def test_the_base_takes_more_of_a_shallow_cut_not_less(self) -> None:
        """SC-069: half the width is the largest *round* base and the right size
        only while the cut can hold it.

        Below that, the arc covers barely half the half-width and the rest is a
        straight ramp — a shallow trapezoid with a dimple in it. The base has to
        grow as the depth falls away.
        """
        for depth, least in ((8.0, 0.70), (10.0, 0.75), (15.0, 0.75)):
            with self.subTest(depth=depth):
                ring, r2, _ = self.outline(20.0, depth)
                points = self.right_half(ring, depth)
                # Where the base arc hands over to the flank: the longest run
                # in the outline starts there.
                import math

                segments = [
                    (a, b) for a, b in zip(points, points[1:])
                    if math.dist(a, b) > 1e-9
                ]
                handover = max(segments, key=lambda seg: math.dist(*seg))[0]
                self.assertGreaterEqual(handover[0] / 20.0, least)

    def test_a_deep_cut_keeps_the_round_base_it_already_had(self) -> None:
        """The rule only bites where the shape was wrong: at these depths the
        base is still exactly half the width."""
        for depth in (25.0, 30.0, 40.0):
            with self.subTest(depth=depth):
                _, r2, _ = self.outline(20.0, depth)
                self.assertAlmostEqual(r2, 20.0, places=6)

    def test_the_base_is_a_full_round_sitting_on_the_bottom(self) -> None:
        ring, r2, _ = self.outline(20.0, 15.0)
        self.assertAlmostEqual(r2, 20.0, places=6)
        self.assertAlmostEqual(min(y for _, y in ring), 0.0, places=6)
        flat = [x for x, y in ring if abs(y) < 1e-9]
        self.assertAlmostEqual(max(flat) if flat else 0.0, 0.0, places=6)

    def test_nothing_creases_where_the_curves_meet_the_flank(self) -> None:
        """Every join is a touch point, so the direction carries across it: the
        only turns in the outline are one facet's worth."""
        import math

        for depth in (10.0, 15.0, 30.0):
            with self.subTest(depth=depth):
                ring, _, _ = self.outline(20.0, depth)
                points = self.right_half(ring, depth)
                segments = [
                    (a, b) for a, b in zip(points, points[1:])
                    if math.dist(a, b) > 1e-9
                ]
                angles = [
                    math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
                    for a, b in segments
                ]
                turns = [abs(b - a) for a, b in zip(angles, angles[1:])]
                self.assertLess(max(turns), 8.0, "a crease at one of the joins")

    def test_the_cut_widens_all_the_way_to_the_rim(self) -> None:
        ring, _, _ = self.outline(20.0, 14.0)
        xs = [x for x, _ in self.right_half(ring, 14.0)]
        for below, above in zip(xs, xs[1:]):
            self.assertGreaterEqual(above, below - 1e-6, "the outline curls back in")


class GripBaseIsDerivedNotPinnedTests(unittest.TestCase):
    """FR-043a7: the base's size is decided in one place — the fit.

    `apply_finger_holes` passed the half-width down as the base radius, which
    reads as "the default" and is not: an explicit value counts as a *request*,
    so the base stopped growing as the cut shallowed and every shallow tray went
    back to a ramp either side. The rule lives in `_fit_radii`; the caller says
    nothing unless the user did.
    """

    def scoop_call(self, **spec_overrides):
        """The keywords `apply_finger_holes` hands to the scoop builder."""
        from unittest.mock import MagicMock, patch

        from pyboxbuilder.box.shell import apply_finger_holes, no_lid_finger_holes

        spec = dict(
            width=100, length=80, height=20, wall_thickness=2.0,
            floor_thickness=1.6, rim_free=True,
        )
        spec.update(spec_overrides)
        spec.setdefault("finger_holes", no_lid_finger_holes(spec))
        self.assertTrue(spec["finger_holes"], "no holes to inspect")

        body = MagicMock()
        body.__sub__.return_value = body
        with patch(
            "pyboxbuilder.compartments.finger_hole.build_wall_scoop"
        ) as builder:
            builder.return_value = MagicMock()
            builder.return_value.translate.return_value = MagicMock()
            apply_finger_holes(body, spec)
        return builder.call_args.kwargs

    def test_the_base_radius_is_left_to_the_fit(self) -> None:
        self.assertIsNone(self.scoop_call()["bottom_rounding"])

    def test_an_explicit_radius_still_reaches_it(self) -> None:
        from pyboxbuilder.builders._base import FingerHoleBuilder

        hole = FingerHoleBuilder(side=ScoopSide.FRONT, bottom_radius=7.0)
        kwargs = self.scoop_call(finger_holes=(hole,))
        self.assertAlmostEqual(kwargs["bottom_rounding"], 7.0)

    def test_the_shallow_tray_gets_the_grown_base(self) -> None:
        """End to end on the numbers the tray actually builds with: a 20mm box
        cuts 10mm deep, and its base circle is larger than the half-width."""
        from pyboxbuilder.box.shell import _hole_flare, no_lid_finger_holes
        from pyboxbuilder.compartments.finger_hole import _fit_radii

        spec = dict(
            width=100, length=80, height=20, wall_thickness=2.0,
            floor_thickness=1.6, rim_free=True,
        )
        hole = no_lid_finger_holes(spec)[0]
        outline_height = hole.depth - _hole_flare(2.0, hole, hole.depth)
        _, _, r2 = _fit_radii(
            hole.radius, outline_height, hole.rounding_radius, None,
            keep_flat_bottom=False,
        )
        self.assertGreater(r2, hole.radius * 1.2)


class GripStaysInProportionTests(unittest.TestCase):
    """FR-043a8/SC-070: a grip is never wider than it is deep.

    The angle a cut's flank arrives at the rim follows its aspect and nothing
    else: 45mm wide over 9mm deep can only come in at about 34°, against about
    70° for the same width at 19mm deep, and the two stop reading as the same
    feature. Sizing the circles differently cannot fix it — a bigger base
    flattens the flank and a smaller one flattens it further, because the line
    has to climb across the whole width either way. So a shallow box gets a
    *smaller* grip rather than a stretched one.
    """

    def cut(self, box_height: float):
        """(throat half-width, depth, flank angle) for a tray's automatic hole."""
        import math

        from pyboxbuilder.box.shell import _hole_flare, no_lid_finger_holes
        from pyboxbuilder.compartments.finger_hole import _fit_radii, scoop_outline

        spec = dict(
            width=100, length=80, height=box_height,
            wall_thickness=2.0, floor_thickness=1.6, rim_free=True,
        )
        hole = no_lid_finger_holes(spec)[0]
        depth = hole.depth - _hole_flare(2.0, hole, hole.depth)
        throat = min(hole.radius, depth)
        flare, rise, r2 = _fit_radii(
            throat, depth, hole.rounding_radius, None, keep_flat_bottom=False
        )
        ring = scoop_outline(throat, depth, flare, r2, rise)
        points = sorted(
            (p for p in ring if p[0] >= -1e-9 and p[1] <= depth + 1e-9),
            key=lambda p: p[1],
        )
        segments = [
            (a, b) for a, b in zip(points, points[1:]) if math.dist(a, b) > 1e-9
        ]
        run = max(segments, key=lambda seg: math.dist(*seg))
        angle = math.degrees(math.atan2(run[1][1] - run[0][1], run[1][0] - run[0][0]))
        return throat, depth, angle

    def test_no_grip_is_wider_than_it_is_deep(self) -> None:
        for box_height in (12, 16, 20, 25, 30, 40, 50):
            with self.subTest(box=box_height):
                throat, depth, _ = self.cut(box_height)
                self.assertLessEqual(throat, depth + 1e-9)

    def test_the_flank_angles_stay_in_family(self) -> None:
        """The point of the rule: without it a 16mm box came in at 34° and a
        40mm box at 74°. Half the angle is a different feature, not a smaller
        one — the spread is what this holds down."""
        angles = [self.cut(h)[2] for h in (16, 20, 25, 30, 40)]
        self.assertLess(max(angles) - min(angles), 25.0, f"angles {angles}")

    def test_a_deep_box_keeps_the_grip_it_had(self) -> None:
        """The rule bites where the shape was wrong: on a box deep enough for
        the throat it already had, it changes nothing."""
        throat, depth, _ = self.cut(40)
        self.assertAlmostEqual(throat, depth, places=6)
        self.assertGreaterEqual(throat, 19.0)


class OutlineNeverRunsBackwardsTests(unittest.TestCase):
    """SC-071: the outline is a path a finger follows, so it never reverses.

    Walking the right half from the base to the rim, x must not decrease and y
    must not drop. Three separate defects have been caught by exactly this and
    by nothing else — a bounding box, a volume and a facet count all look
    perfectly healthy while the shoulder has a step in it:

    * the mouth roll swept 270° round the wrong way, because `atan2` reports a
      point directly left of a centre as +180 or **-180** depending on the sign
      of a floating-point zero;
    * the roll's rise clamped without its radius, leaving the tangent solved
      against a circle that was not the one drawn;
    * the base circle sized until it touched the roll, so the join fell back to
      a vertical lying on neither arc.

    The sweep is wide because each of those appeared at some sizes and not
    others; the one that prompted it was visible on a user's box and on none of
    ours.
    """

    def first_reversal(self, half_width, depth, flare, keep_flat_bottom):
        import math

        from pyboxbuilder.compartments.finger_hole import _fit_radii, scoop_outline

        roll, rise, base = _fit_radii(
            half_width, depth, flare, None, keep_flat_bottom=keep_flat_bottom
        )
        ring = scoop_outline(half_width, depth, roll, base, rise)
        right = [p for p in ring if p[0] >= -1e-9 and p[1] <= depth + 1e-9]
        for a, b in zip(right, right[1:]):
            if math.dist(a, b) < 1e-9:
                continue
            if b[0] < a[0] - 1e-6 or b[1] < a[1] - 1e-6:
                return a, b
        return None

    def test_no_grip_outline_reverses(self) -> None:
        for half_width in (3.0, 5.0, 8.0, 12.0, 20.0, 30.0):
            for depth in (2.0, 4.0, 6.0, 9.0, 14.0, 25.0, 45.0):
                for flare in (0.5, 1.0, 3.0, 5.0, 8.0):
                    found = self.first_reversal(half_width, depth, flare, False)
                    if found:  # subTest per case would be 210 of them
                        self.fail(
                            f"half-width {half_width}, depth {depth}, roll {flare}: "
                            f"outline runs backwards {found[0]} -> {found[1]}"
                        )

    def test_no_compartment_scoop_outline_reverses(self) -> None:
        for half_width in (3.0, 5.0, 8.0, 12.0, 20.0, 30.0):
            for depth in (2.0, 4.0, 6.0, 9.0, 14.0, 25.0, 45.0):
                for flare in (0.5, 1.0, 3.0, 5.0, 8.0):
                    found = self.first_reversal(half_width, depth, flare, True)
                    if found:
                        self.fail(
                            f"half-width {half_width}, depth {depth}, roll {flare}: "
                            f"outline runs backwards {found[0]} -> {found[1]}"
                        )

    def test_the_roll_never_pokes_above_the_rim(self) -> None:
        """It is a circle tangent to the top face: centre exactly its radius
        below the rim. Clamping the rise alone lifted the centre and left the
        circle its full size, which is how the tangent came to be solved
        against a circle that was not the one drawn."""
        from pyboxbuilder.compartments.finger_hole import _fit_radii

        for depth in (2.0, 3.0, 4.0, 6.0, 9.0, 20.0):
            for flare in (1.0, 3.0, 5.0, 8.0):
                with self.subTest(depth=depth, flare=flare):
                    roll, rise, _ = _fit_radii(
                        10.0, depth, flare, None, keep_flat_bottom=False
                    )
                    self.assertAlmostEqual(roll, rise, places=9)
                    self.assertLessEqual((depth - rise) + roll, depth + 1e-9)


@unittest.skipUnless(render_available(), "PythonSCAD binary not available")
class ThroughFloorCutTests(unittest.TestCase):
    """FR-043a10/SC-073: a card well is emptied from underneath.

    A scoop puts a finger down the *side* of what a well holds, and a stack
    that fills its well has no side to reach down — what lifts it is a thumb
    from below, so the cut has to go through the box's base. The original
    toolkit cuts every card box this way (`FingerHoleBase`, translated a floor
    thickness below the base).

    Measured under the box, because that is the whole point: a probe beneath
    the cut is open to the outside when the cut is a through hole and solid
    when it is a scoop.
    """

    @classmethod
    def setUpClass(cls) -> None:
        body = '''
import os, re, tempfile, zipfile
from openscad import export
from pyboxbuilder import BoxType, FingerCut, Project
from pybosl2 import cuboid

def volume(solid):
    with tempfile.NamedTemporaryFile(suffix=".3mf", delete=False) as handle:
        path = handle.name
    try:
        export(solid.shape, path)
        model = zipfile.ZipFile(path).read("3D/3dmodel.model").decode()
    finally:
        os.unlink(path)
    verts = [(float(x), float(y), float(z)) for x, y, z in re.findall(
        r'<vertex x="([-0-9.e+]+)" y="([-0-9.e+]+)" z="([-0-9.e+]+)"', model)]
    total = 0.0
    for a, b, c in re.findall(r'<triangle v1="(\\d+)" v2="(\\d+)" v3="(\\d+)"', model):
        p, q, r = verts[int(a)], verts[int(b)], verts[int(c)]
        total += (p[0]*(q[1]*r[2]-r[1]*q[2]) - p[1]*(q[0]*r[2]-r[0]*q[2])
                  + p[2]*(q[0]*r[1]-r[0]*q[1])) / 6.0
    return abs(total)

def build(kind):
    p = Project("A", game_box_size=(400, 300, 60), generate_spacers=False,
                wall_thickness=3.0, floor_thickness=2.0, lid_thickness=2.0)
    b = p.box(BoxType.SLIDING, "cards", size=(90, 98, 20), position=(0, 0, 0),
              expandable=False, no_rotate=True)
    b.compartment("Cards", size=(67, 92), depth=16.0, position=(9.0, 0.0),
                  finger_scoop=True, finger_cut=kind)
    p._resolve_final_layout()
    return p._build_box_solids(b)[0]

# The floor under the cut: the cut sits at the middle of a wall, so probe the
# floor there. 6 x 3 x 2 of floor = 36 when solid.
probe = cuboid([6.0, 3.0, 2.0]).translate([45.0, 94.0, 1.0])
report("through_floor", "%.2f" % volume(build(FingerCut.THROUGH_FLOOR) & probe))
report("scoop", "%.2f" % volume(build(FingerCut.SCOOP) & probe))
report("probe_full", "%.2f" % volume(probe))
cuboid([1, 1, 1]).show()
'''
        cls.result = measure_python(body)
        if not cls.result.ok:
            raise AssertionError(f"measurement run failed: {cls.result.error}")

    def test_the_base_is_open_under_a_through_cut(self) -> None:
        got = float(self.result.reports["through_floor"])
        self.assertLess(got, 1.0, "the floor is still there under the cut")

    def test_a_scoop_leaves_the_base_solid(self) -> None:
        got = float(self.result.reports["scoop"])
        full = float(self.result.reports["probe_full"])
        self.assertAlmostEqual(got, full, delta=full * 0.05,
                               msg="a scoop opened the box's base")
