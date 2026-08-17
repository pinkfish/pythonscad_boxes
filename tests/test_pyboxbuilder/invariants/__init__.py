# SPDX-License-Identifier: Apache-2.0
"""Geometric invariants every finger cut must hold, swept over its parameters.

These are the tests that have actually caught things. Three separate defects in
the scoop's outline reached a user's render and none of them moved a bounding
box, a volume or a facet count by anything a threshold would notice:

* the mouth roll swept 270° the wrong way round, because `atan2` reports a point
  directly left of a centre as +180 or **-180** depending on the sign of a zero;
* the roll's rise was clamped without its radius, so the tangent was solved
  against a circle that was not the one drawn;
* the base circle was sized until it *touched* the roll, collapsing the flank to
  a point.

What they have in common is that the shape stayed the right size while ceasing
to be the right shape. So the assertions here are about *shape*: an outline that
never doubles back, joins that carry their direction across, a section that
changes only where it should. They are swept across a grid of proportions
because each of those three appeared at some sizes and not others — the one that
prompted this appeared on a user's box and on none of ours.

Adding a cut kind means registering it in `CUT_KINDS`; it then inherits every
invariant here rather than needing someone to remember them.
"""
