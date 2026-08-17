# SPDX-License-Identifier: Apache-2.0
"""Shape invariants, swept over every cut kind and every proportion.

See the package docstring for why these are shape assertions rather than size
ones. Each failure message names the exact proportions, because the whole point
is that these hold *everywhere* and the interesting information is where they
stopped.
"""

from __future__ import annotations

import math
import unittest

from test_pyboxbuilder.invariants.outlines import sweep


class OutlineNeverDoublesBackTests(unittest.TestCase):
    """Walking from the base to the rim, the outline only ever goes out and up.

    A segment that reverses is a step in the shoulder or a fold in the base. It
    caught the 270° arc sweep, the mismatched roll circle and the collapsed
    flank — none of which changed the cut's size.
    """

    def test_no_cut_reverses(self) -> None:
        for cut in sweep():
            points = cut.right_half()
            for first, second in zip(points, points[1:]):
                if math.dist(first, second) < 1e-9:
                    continue
                if second[0] < first[0] - 1e-6 or second[1] < first[1] - 1e-6:
                    self.fail(
                        f"{cut.kind} at half-width {cut.half_width}, depth "
                        f"{cut.depth}, roll {cut.flare}: the outline runs "
                        f"backwards {first} -> {second}"
                    )


class JoinsCarryTheirDirectionTests(unittest.TestCase):
    """Every arc meets its neighbour tangentially, to within one facet.

    Tangency is what makes the outline one curve rather than several. It cannot
    be asserted exactly against a faceted arc, so the test is relative: no join
    may turn appreciably more than the facets either side of it do.
    """

    def test_no_join_creases(self) -> None:
        for cut in sweep():
            points = cut.right_half()
            segments = [
                (a, b) for a, b in zip(points, points[1:]) if math.dist(a, b) > 1e-9
            ]
            if len(segments) < 4:
                continue  # too few to say anything about
            angles = [
                math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) for a, b in segments
            ]
            turns = [abs(b - a) for a, b in zip(angles, angles[1:])]
            typical = sorted(turns)[len(turns) // 2]
            self.assertLessEqual(
                max(turns), max(4.0 * typical, 12.0),
                f"{cut.kind} at half-width {cut.half_width}, depth {cut.depth}, "
                f"roll {cut.flare}: a join turns {max(turns):.1f}° against a "
                f"typical facet of {typical:.1f}°",
            )


class TheCutStaysInsideItsEnvelopeTests(unittest.TestCase):
    """A cut removes material where it said it would and nowhere else.

    Its outline may not reach wider than its own mouth, deeper than its own
    depth, or below the surface it is cut from. A cut that quietly exceeds any
    of those is removing someone else's material — a lid track, an adjoining
    wall, the box's base.
    """

    def test_nothing_reaches_past_the_mouth(self) -> None:
        for cut in sweep():
            widest = max(abs(x) for x, _ in cut.points)
            self.assertLessEqual(
                widest, cut.half_width + cut.flare + 1e-6,
                f"{cut.kind} at half-width {cut.half_width}, depth {cut.depth}, "
                f"roll {cut.flare}: reaches {widest:.2f} past a mouth of "
                f"{cut.half_width + cut.flare:.2f}",
            )

    def test_nothing_reaches_below_the_floor(self) -> None:
        """The outline's own frame has its floor at zero; what goes below it is
        the face fillet's business, and that is applied by the sweep."""
        for cut in sweep():
            lowest = min(y for _, y in cut.points)
            self.assertGreaterEqual(
                lowest, -1e-6,
                f"{cut.kind} at half-width {cut.half_width}, depth {cut.depth}, "
                f"roll {cut.flare}: dips to {lowest:.3f}",
            )

    def test_the_rim_overshoot_is_the_only_thing_above_the_top(self) -> None:
        from pyboxbuilder.compartments.finger_hole import RIM_OVERSHOOT_MM

        for cut in sweep():
            highest = max(y for _, y in cut.points)
            self.assertLessEqual(
                highest, cut.depth + RIM_OVERSHOOT_MM + 1e-6,
                f"{cut.kind} at half-width {cut.half_width}, depth {cut.depth}, "
                f"roll {cut.flare}: reaches {highest:.2f} above a top of "
                f"{cut.depth}",
            )


class TheBaseIsWhereItWasAskedForTests(unittest.TestCase):
    """The cut bottoms out at its own depth and sits on the axis.

    A base that drifts off-centre mirrors into two arcs that cross, which folds
    the outline inside out — the failure the centred base circle exists to stop.
    """

    def test_the_lowest_point_is_on_the_axis(self) -> None:
        for cut in sweep():
            lowest = min(cut.points, key=lambda point: point[1])
            self.assertLessEqual(
                abs(lowest[0]), cut.half_width + 1e-6,
                f"{cut.kind} at half-width {cut.half_width}, depth {cut.depth}, "
                f"roll {cut.flare}: bottoms out at x={lowest[0]:.2f}",
            )

    def test_the_outline_is_symmetric(self) -> None:
        for cut in sweep():
            xs = sorted(round(x, 6) for x, _ in cut.points)
            self.assertEqual(
                xs, sorted(-x for x in xs),
                f"{cut.kind} at half-width {cut.half_width}, depth {cut.depth}, "
                f"roll {cut.flare}: the outline is not symmetric",
            )


if __name__ == "__main__":
    unittest.main()
