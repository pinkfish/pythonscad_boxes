# SPDX-License-Identifier: Apache-2.0
"""The **outline** of a finger cut — its shape in two dimensions.

A finger cut is one closed path, swept through a wall. This module is the path,
and nothing else: no solids are built here, no side is chosen, no wall is
crossed. Everything is millimetres in the profile plane, X out from the cut's
centreline and Z up towards the rim.

The outline is four numbers (FR-051) and three parts:

* a **base circle** of radius ``r2``, which the cut's bottom is an arc of;
* a **straight flank** on each side, running up from that circle along the
  internal tangent to
* a **mouth roll** of flare ``r1`` and rise, an ellipse quadrant that turns the
  flank over into the rim so the top surface is entered tangentially.

Keeping this separate from the sweep is what makes the shape testable without a
renderer: :mod:`tests.test_pyboxbuilder.invariants` walks 420 of these paths and
asserts they never double back, always carry direction across a join, and stay
inside the envelope the four numbers describe. Every shape defect that has
reached a render was visible in the path alone.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from pyboxbuilder.precision import kwargs as precision_kwargs

if TYPE_CHECKING:
    from pybosl2.shapes2d import Bosl2Shape2D


DEFAULT_MOUTH_ROUNDING_MM = 3.0
"""Fallback ``r1`` where nothing better can be derived."""
DEFAULT_TOP_ROUNDING_RATIO = 0.5
"""How far the top roll flares **outward**, as a fraction of the throat half-width.

Derived rather than fixed so the roll stays in proportion: a 3mm constant is
invisible on a 14mm finger hole and overwhelming on a 4mm one. This is the one
number that sets how *wide* the scoop's mouth is, so it is also the one to
leave alone when the width is already right.
"""
TOP_ROLL_RISE_RATIO = 1.6
"""How far the top roll reaches **down**, as a multiple of its outward flare.

The roll is an ellipse quadrant, not a circle, because its two extents answer
different questions: the flare decides how wide the mouth is, and the rise
decides how gently the top surface turns into the wall. A circle ties them
together, so the only way to get a gentler curve is a wider cut — which is
backwards on a shallow wall, where there is height to spare for the curve but
no width to spare for the mouth.
"""
RIM_OVERSHOOT_MM = 1.0
"""How far a scoop's outline continues above the rim.

Keeps the outline free of the zero-angle cusp that closing it flush across the
top would create, and leaves no skin at the top face. Nothing sits above the
rim, so the overshoot removes nothing that was there.
"""
ARC_SAMPLES = 16
"""Points per quarter-arc in the scoop profile. 16 is smooth at print scale."""
DEFAULT_BOTTOM_ROUNDING_RATIO = 0.65
"""``r2`` as a fraction of the throat half-width, when the caller names none.

Wider than the half it started at: the floor fillet does not change how wide
the cut is — it lives inside the throat — so it can afford a generous curve,
and a finger following the wall down wants one.
"""
TOUCHING_TOLERANCE_MM = 0.05
"""How near touching two circles may be and still be joined at a point.

Exact touching is a real configuration — a cut exactly a half-width plus a roll
deep has it — and there the flank is a point on the line of centres, with the
outline still tangent to both arcs. Inside this band that point is used; only a
genuine overlap falls back to the vertical.
"""
BASE_ARC_SHARE = 0.9
"""How near the touching cap a grip's base circle is sized (FR-052).

The cap is where the base circle meets the roll and the flank between them
vanishes; the base takes as much of the cut as it can while leaving a run to
see, and the last tenth is that run. A proportion rather than a length, so it
holds at every size of cut.

It is what makes a *shallow* grip a dip rather than a trapezoid. Half the cut's
width is the largest round base, and it is the right size only while the cut is
deep enough to hold that circle: at 40mm wide and 10mm deep the arc covers
barely half the half-width and the rest is a straight ramp. Where the cut is
deep the cap sits close to the half-width, this lands under it, and the rule
changes nothing.
"""
MIN_FLAT_BOTTOM_RATIO = 0.25
"""How much of the throat's half-width stays flat, however large ``r2`` is.

The base of an edge scoop is a **flat run**, not just the meeting point of two
fillets. A piece rests on it, and a finger slides along it to get under the
piece; let r2 grow to the full half-width and the flat vanishes into a U, which
is the trough shape the flat bottom exists to avoid. r2 is therefore capped so
at least this fraction of each half stays straight.
"""
@dataclass(frozen=True)
class CutProfile:
    """The four numbers that decide a finger cut's **outline** (FR-051).

    Grouped rather than passed loose because every defect that reached a user
    in this shape was a wiring one, not a maths one: a rise clamped without its
    radius, a value passed where ``None`` was the contract and the derived rule
    silently switched off, a base sized until it touched. A record makes the
    contract visible at the call site and puts the derivations in one place.

    Every field is ``None`` for "derive it", because the derivation depends on
    the others and on the cut's depth — which the builder knows and the caller
    usually does not (FR-059).
    """

    width: float | None = None
    """How wide the cut is, wall to wall of the finger. ``None`` uses twice
    :data:`DEFAULT_THROAT_RADIUS_MM`."""
    base_radius: float | None = None
    """How the base curves into the sides. ``None`` derives it from the depth
    (FR-054/a7) — the flattest arc that still meets the roll."""
    mouth_flare: float | None = None
    """How far the mouth rolls **outward** at the rim. ``None`` takes a share
    of the throat (FR-059)."""
    roll_rise: float | None = None
    """How far that roll reaches **down** — the gentleness of it, independent
    of the width (FR-057). ``None`` derives it from the flare."""

    @property
    def half_width(self) -> float | None:
        """The throat's half-width, which is what the outline maths works in."""
        return None if self.width is None else self.width / 2.0

    def with_half_width(self, half_width: float) -> "CutProfile":
        """A copy whose width is set from a half-width."""
        return replace(self, width=half_width * 2.0)
def _quarter_arc(
    centre: tuple[float, float],
    radius: float,
    start_angle: float,
    end_angle: float,
    samples: int | None = None,
) -> list[tuple[float, float]]:
    """Sample an arc, endpoints included.

    Args:
        centre: The arc's centre in the profile plane.
        radius: Arc radius; ``0`` collapses to the single centre point.
        start_angle: Start angle in degrees.
        end_angle: End angle in degrees.
        samples: Segments along the arc. ``None`` follows the curve precision
            in force, so an export tessellates these arcs as finely as every
            other curve rather than pinning a count the caller cannot reach.

    Returns:
        ``[(x, y), ...]`` from start to end.
    """
    if radius <= 0:
        return [centre]
    if samples is None:
        from pyboxbuilder.precision import precision

        # A quarter arc gets a quarter of the facets a full circle would.
        samples = max(ARC_SAMPLES, (precision().fn or 0) // 4)
    points = []
    for index in range(samples + 1):
        angle = math.radians(
            start_angle + (end_angle - start_angle) * index / samples
        )
        points.append(
            (centre[0] + radius * math.cos(angle), centre[1] + radius * math.sin(angle))
        )
    return points
def scoop_profile(
    radius: float,
    height: float,
    top_rounding: float = DEFAULT_MOUTH_ROUNDING_MM,
    bottom_rounding: float | None = None,
) -> "Bosl2Shape2D":
    r"""Build the 2-D side profile of an **edge** scoop, in the X-Z plane.

    Two radii and three straight runs, read from the top down::

        ===========...                      ...===========   flat top surface
                     ''..                ..''                r1: rolls the top
                         \              /                    over into the wall
                          |            |                     straight throat
                          '..      ..''                      r2: wall into floor
                             ''--''                          flat bottom

    **r1** (``top_rounding``) turns the flat top surface into the scoop wall:
    the arc leaves the top face horizontally, so the surface rolls over the rim
    instead of meeting the cut at an edge, and arrives vertical at the throat.
    **r2** (``bottom_rounding``) turns the wall into the floor, leaving a flat
    bottom for a piece to sit on rather than a semicircular trough.

    Both arcs are tangent at both ends, so the whole outline is smooth without
    needing a parametric blend: the tangency is what makes it so, and two radii
    say it more directly than any curve fitted between them.

    Args:
        radius: Half-width of the straight throat — the narrowest part.
        height: Height from the floor to the rim.
        top_rounding: r1, how far the mouth rolls out at the rim. ``0`` gives a
            square-topped slot.
        bottom_rounding: r2, the fillet from the throat into the flat bottom.
            ``None`` derives it as half the throat half-width; ``0`` gives a
            square floor. Capped so part of the base stays flat whatever is
            asked for.

    Returns:
        The profile as 2-D geometry, floor at ``y=0``, rim at ``y=height``,
        centred on ``x=0``.

    Raises:
        ValueError: If ``radius`` or ``height`` is not positive, or either
            radius is negative.
    """
    from pybosl2 import shapes2d

    if radius <= 0:
        raise ValueError(f"scoop radius must be > 0; got {radius}")
    if height <= 0:
        raise ValueError(f"scoop height must be > 0; got {height}")
    if top_rounding < 0:
        raise ValueError(f"top_rounding must be >= 0; got {top_rounding}")

    if bottom_rounding is None:
        bottom_rounding = radius * DEFAULT_BOTTOM_ROUNDING_RATIO
    if bottom_rounding < 0:
        raise ValueError(f"bottom_rounding must be >= 0; got {bottom_rounding}")

    flare, rise, r2 = _fit_radii(radius, height, top_rounding, bottom_rounding)

    ring = scoop_outline(radius, height, flare, r2, rise)
    return shapes2d.polygon([[float(x), float(y)] for x, y in ring])
def dish_radius(radius: float, height: float, flare: float) -> float:
    """The radius of a **shallow** cut's base: one arc across its whole width.

    A deep cut is a bore — a round base with sides running up from it — and its
    base radius is the half-width. A shallow one is a **dish**, and sizing it
    the same way is what produces the U with tight corners a fingertip cannot
    follow: a corner circle is bounded by the depth while the width is not, so
    as the tray gets shallower the corners tighten and a flat run opens up
    between them. The base has to stop being two circles and become one
    (FR-052).

    This is the flattest arc that still meets the mouth's roll **tangentially**,
    which makes the join disappear — the base runs into the roll and the roll
    into the top face with nothing to feel between them. Solved from the
    tangency condition on the two centres, ``(0, R)`` and ``(A, u)``::

        A² + (R - u)² = (R + flare)²   →   R = (A² + u² - flare²) / (2(u + flare))

    Args:
        radius: Half-width of the cut.
        height: The outline's height.
        flare: The mouth roll's outward flare, which is also its radius here —
            the roll is circular in this branch, because a circle and an
            ellipse cannot be made exactly tangent.

    Returns:
        The arc's radius, always larger than the half-width and, on a cut this
        shallow, larger than the cut is deep — so the arc widens all the way up
        instead of curling back in.
    """
    mouth = radius + flare
    below_roll = height - flare
    return (mouth * mouth + below_roll * below_roll - flare * flare) / (
        2.0 * (below_roll + flare)
    )
def _fit_radii(
    radius: float,
    height: float,
    top_rounding: float,
    bottom_rounding: float | None,
    roll_rise: float | None = None,
    keep_flat_bottom: bool = True,
) -> tuple[float, float, float]:
    """Size the two rolls to the scoop they are shaping.

    Args:
        radius: Half-width of the throat.
        height: Floor to rim.
        top_rounding: The top roll's outward flare (r1).
        bottom_rounding: Requested r2, or ``None`` to derive it.
        keep_flat_bottom: Cap the corner radius so a flat run survives at the
            base — right for a compartment scoop, which something rests in
            (FR-050), wrong for a grip, whose base is round (FR-054).
        roll_rise: How far the top roll reaches **down**. ``None`` derives it
            as ``TOP_ROLL_RISE_RATIO`` times the flare. It is the fourth of the
            numbers that define the outline (FR-051) and the one that says
            how gently the top surface turns into the wall, so it has to be
            reachable rather than fixed — on a wall with height to spare and no
            width to spare, it is the only one that can give.

    Returns:
        ``(flare, rise, r2)`` — how far the top roll reaches out, how far it
        reaches down, and the corner radius.

    Only the two *vertical* extents compete for the height, so a shallow wall
    shortens the rise and leaves the flare — and therefore the width of the cut
    — alone. Scaling the flare too would narrow the mouth on exactly the boxes
    where a finger has least room to begin with.

    **The corner radius is kept, not fitted** (FR-054). The straight run
    between the two circles is what gives when a large radius meets a short cut,
    and solving their common tangent is what makes that work — so the radius is
    spent only against what is physically left after the rise has given way down
    to a circular roll. Scaling it to fit, which is what this did, returned
    14.4mm to a caller who asked for 20 and left nothing in the geometry to say
    so.
    """
    asked = bottom_rounding
    flare = max(0.0, top_rounding)
    rise = flare * TOP_ROLL_RISE_RATIO if roll_rise is None else max(0.0, roll_rise)
    # A roll has to have somewhere to sit; a circular one (rise = flare) is as
    # little as a roll can be and still roll.
    floor_rise = min(flare, height / 2.0)

    if keep_flat_bottom:
        # A compartment scoop holds something, so part of its base stays flat
        # (FR-050), and its corner circles must not overlap each other.
        r2 = radius * DEFAULT_BOTTOM_ROUNDING_RATIO if asked is None else asked
        r2 = min(max(0.0, r2), radius * (1.0 - MIN_FLAT_BOTTOM_RATIO))
        # Everything past that comes off the rise before it comes off r2.
        r2 = max(0.0, min(r2, radius, height - floor_rise))
        rise = max(floor_rise, min(rise, height - r2)) if height > r2 else 0.0
        return flare, rise, r2

    # A grip. One shape for every proportion (FR-052): a base circle sitting
    # on the bottom of the cut, the roll at each end, and the internal tangent
    # between them as the flank. Deep, that tangent comes out vertical and the
    # result is a round base with straight sides; shallow, the same circle
    # presents a long flat sweep and the tangent carries it up and out.
    #
    # The roll is circular here so the tangent is exact — two circles have one,
    # a circle and an ellipse do not, and this is where that matters. Radius and
    # rise are **one number**: the circle is tangent to the top face, so its
    # centre sits exactly its radius below the rim. Clamping the rise alone
    # lifts that centre without shrinking the circle, which pushes it above the
    # rim and leaves the cap and the tangent solved against a circle that is not
    # the one drawn — and the outline then runs sideways to reach it.
    flare = rise = floor_rise
    # Never as far as the radius that makes the two circles *touch*: there the
    # flank collapses to a point and the outline reads as one wobbling curve.
    # The cap sits above the half-width at every proportion (its minimum, over
    # all depths, is the half-width itself), so the default is always kept and
    # this binds only on a request larger than the shape can hold.
    cap = dish_radius(radius, height, flare)
    # Half the width is the largest *round* base, and the right size while the
    # cut is deep enough to hold that circle. Below that the base has to take
    # **more** of the cut, not less, or it covers half the width and leaves a
    # ramp either side. Only then: the cap climbs again on a deep cut, and
    # following it there would widen the belly past the throat and tilt the
    # flank off vertical.
    if asked is not None:
        r2 = max(0.0, asked)
    elif height < radius:
        r2 = max(radius, cap * BASE_ARC_SHARE)
    else:
        r2 = radius
    r2 = max(0.0, min(r2, cap))
    return flare, rise, r2
def floor_bore_outline(
    radius: float,
    height: float,
    top_rounding: float = DEFAULT_MOUTH_ROUNDING_MM,
) -> list[tuple[float, float]]:
    """The floor finger hole's closed outline, as one ring of points.

    The bore counterpart to :func:`scoop_outline`: a bowl tangent to the floor
    instead of a flat bottom, carrying the same r1 roll at its rim and the same
    overshoot above it.

    Args:
        radius: Bore radius — the widest part of the bowl.
        height: Floor to rim.
        top_rounding: r1 at the rim.

    Returns:
        ``[(x, y), ...]`` closed, floor at ``y=0``.

    Raises:
        ValueError: If ``radius`` or ``height`` is not positive, or
            ``top_rounding`` is negative.
    """
    if radius <= 0:
        raise ValueError(f"bore radius must be > 0; got {radius}")
    if height <= 0:
        raise ValueError(f"bore height must be > 0; got {height}")
    if top_rounding < 0:
        raise ValueError(f"top_rounding must be >= 0; got {top_rounding}")

    r1 = min(top_rounding, max(0.0, height - radius))
    right: list[tuple[float, float]] = []
    # The bowl: a quarter of the bore circle, from its lowest point out to the
    # side, tangent to the floor at the bottom and vertical at the side.
    right += _quarter_arc((0.0, radius), radius, -90.0, 0.0)
    right.append((radius, height - r1))
    if r1 > 0:
        right += _quarter_arc((radius + r1, height - r1), r1, 180.0, 90.0)
    right.append((radius + r1, height + RIM_OVERSHOOT_MM))

    left = [(-x, y) for x, y in reversed(right)]
    return left + right
def _elliptical_quarter(
    centre: tuple[float, float],
    flare: float,
    rise: float,
    samples: int | None = None,
) -> list[tuple[float, float]]:
    """The top roll: a quarter ellipse from the wall out to the top face.

    Vertical where it leaves the wall and horizontal where it meets the top
    face, like a quarter circle, but with the two extents settable apart so a
    shallow wall can have a gentle curve without a wide mouth.

    Args:
        centre: The ellipse's centre.
        flare: Horizontal semi-axis — how far the mouth opens out.
        rise: Vertical semi-axis — how far down the turn takes.
        samples: Segments along the arc; ``None`` follows the curve precision.

    Returns:
        ``[(x, y), ...]`` from the wall to the top face.
    """
    if flare <= 0 or rise <= 0:
        return [(centre[0], centre[1] + rise)]
    if samples is None:
        from pyboxbuilder.precision import precision

        samples = max(ARC_SAMPLES, (precision().fn or 0) // 4)
    # Stepped by the **tangent's** direction rather than by the parameter. An
    # ellipse sampled evenly in its parameter bunches its facets at the flatter
    # end, and the more the two axes differ the worse it gets: on a 5:1 roll the
    # first segment turns four times as far as the last, which reads as a crease
    # at the join and is only a facet. Even turning also means the facet budget
    # buys curve where the curve is.
    #
    # The quarter runs from the wall (tangent pointing straight down, -90°) to
    # the top face (tangent horizontal, 0°), so the direction is stepped evenly
    # through that range and the parameter solved back out of it:
    # `tan u = rise / (-flare · tan θ)`.
    points = []
    for index in range(samples + 1):
        theta = math.radians(-90.0 + 90.0 * index / samples)
        if index == 0:
            offset = 0.0
        elif index == samples:
            offset = math.pi / 2
        else:
            offset = math.atan2(rise, -flare * math.tan(theta))
        angle = math.pi + offset
        points.append(
            (centre[0] + flare * math.cos(angle), centre[1] - rise * math.sin(angle))
        )
    return points
def _angle_at(centre: tuple[float, float], point: tuple[float, float]) -> float:
    """The angle, in degrees, from ``centre`` to ``point``."""
    return math.degrees(math.atan2(point[1] - centre[1], point[0] - centre[0]))
def _tangent_join(
    bottom_centre: tuple[float, float],
    bottom_radius: float,
    top_centre: tuple[float, float],
    top_radius: float,
    fallback_x: float,
) -> tuple[tuple[float, float], tuple[float, float]]:
    """Where the two arcs meet the straight run between them.

    Solved as the circles' **common tangent** rather than assumed to be the
    vertical line ``x = fallback_x``. For the usual placement the answer *is*
    that vertical — both circles are constructed tangent to it — so this
    changes no geometry today. It earns its place by not depending on that
    placement: move either centre and the profile stays tangent at both joins
    instead of stepping, which is what a step in a scoop's wall looks like.

    Args:
        bottom_centre: Centre of the r2 (floor) circle.
        bottom_radius: r2.
        top_centre: Centre of the r1 (rim) circle.
        top_radius: r1.
        fallback_x: The vertical to fall back to when no usable tangent exists
            — coincident or overlapping circles, or a degenerate radius.

    Returns:
        ``(point_on_bottom_circle, point_on_top_circle)``.
    """
    if bottom_radius <= 0 or top_radius <= 0:
        return (
            (fallback_x, bottom_centre[1]),
            (fallback_x, top_centre[1]),
        )

    # Solved here rather than through `geometry.circle_circle_tangents`, which
    # returns the external tangents too and has *nothing* to return on the
    # internal branch as the circles approach touching — precisely the case the
    # base circle is sized against (FR-052). With d the distance between the
    # centres and gamma their bearing:
    #
    #     beta = acos((r1 + r2) / d)
    #     touch on circle 1 at gamma ± beta, on circle 2 at the same angle + pi
    #
    # The wanted tangent is the **internal** one: the cut's boundary wraps the
    # *outside* of the base circle and the *inside* of the roll, so the run
    # crosses between them. An external tangent touches both the same way and
    # throws the flank wide of the cut — measured, 12mm wide of it.
    span = (top_centre[0] - bottom_centre[0], top_centre[1] - bottom_centre[1])
    distance = math.hypot(*span)
    reach = bottom_radius + top_radius
    if distance <= reach:
        # Touching is a real configuration — a cut exactly `half-width + roll`
        # deep has it — and there the flank is a *point*, not a vertical: the
        # circles meet on the line between their centres, and the outline runs
        # through that point still tangent to both. Returning the vertical
        # instead puts the join on neither arc, and the outline reaches it
        # sideways: a step in the shoulder.
        if distance > 1e-9 and reach - distance < TOUCHING_TOLERANCE_MM:
            share = bottom_radius / reach
            touch = (
                bottom_centre[0] + span[0] * share,
                bottom_centre[1] + span[1] * share,
            )
            return touch, touch
        # Genuinely overlapping: there is no join to find. The vertical keeps
        # the outline closed, and the sizing rules above are what stop this
        # being reached.
        return (
            (fallback_x, bottom_centre[1]),
            (fallback_x, top_centre[1]),
        )

    gamma = math.atan2(span[1], span[0])
    beta = math.acos(min(1.0, reach / distance))
    best = None
    for sign in (1.0, -1.0):
        angle = gamma + sign * beta
        low = (
            bottom_centre[0] + bottom_radius * math.cos(angle),
            bottom_centre[1] + bottom_radius * math.sin(angle),
        )
        high = (
            top_centre[0] + top_radius * math.cos(angle + math.pi),
            top_centre[1] + top_radius * math.sin(angle + math.pi),
        )
        if high[1] <= low[1]:
            continue  # runs downward: that is the mirrored half's tangent
        if low[0] < bottom_centre[0] - 1e-9:
            continue  # touches the base circle on its buried side
        skew = abs(high[0] - low[0])
        if best is None or skew < best[0]:
            best = (skew, low, high)

    if best is None:
        return (
            (fallback_x, bottom_centre[1]),
            (fallback_x, top_centre[1]),
        )
    return best[1], best[2]
def window_outline(
    radius: float,
    height: float,
    bottom_rounding: float,
) -> list[tuple[float, float]]:
    """A **closed** finger opening: the scoop's outline with a roof on it.

    An edge scoop opens onto the top of the wall it is cut into, and its mouth
    roll is the transition onto that surface. Where the wall carries on above
    the cut — a lidded box, whose hole stops at the interior top with the lid's
    band standing over it (FR-064) — there is no surface to roll onto, and the
    scoop's own outline cannot be used: capping it leaves the cut's ceiling
    meeting each face of the wall at a square edge, with the face fillet
    stopping dead at the cap. What belongs there is a closed window, filleted
    the whole way round, which the offset sweep gives for nothing because the
    fillet follows the ring (FR-044e1, FR-065).

    So the roll is dropped and the floor treatment is mirrored at the top: a
    flat run with a fillet into each side, top and bottom alike.

    Args:
        radius: Half-width of the straight throat.
        height: Bottom to top of the opening.
        bottom_rounding: The corner fillet, already capped to fit; used at all
            four corners.

    Returns:
        ``[(x, y), ...]`` closed counter-clockwise, bottom at ``y=0``.
    """
    r2 = max(0.0, min(bottom_rounding, radius, height / 2))
    right: list[tuple[float, float]] = []
    right += _quarter_arc((radius - r2, r2), r2, -90.0, 0.0)
    right += _quarter_arc((radius - r2, height - r2), r2, 0.0, 90.0)
    left = [(-x, y) for x, y in reversed(right)]
    return left + right
def _sweep_end(angle: float, toward: float) -> float:
    """*angle*, wound to within half a turn of *toward*, so an arc sweeps the short way.

    `_angle_at` reports through :func:`math.atan2`, whose range straddles ±180
    and which distinguishes ``+0.0`` from ``-0.0`` — so a point directly left of
    a centre comes back as +180 or -180 depending on the sign of a zero, and an
    arc swept to the wrong one goes 270° round instead of 90°. That is a cut
    running sideways and down to reach its join, and which of the two you get
    turns on floating-point arithmetic, so it appears at one box size and not
    the next (FR-052).
    """
    while angle - toward > 180.0:
        angle -= 360.0
    while toward - angle > 180.0:
        angle += 360.0
    return angle
def scoop_outline(
    radius: float,
    height: float,
    top_rounding: float,
    bottom_rounding: float,
    top_rise: float | None = None,
) -> list[tuple[float, float]]:
    """The edge scoop's closed outline, as one ring of points.

    Returned as a point ring rather than as 2-D geometry because the ring is
    what an offset sweep needs: it follows the outline around, so the fillet it
    lays on each face traces the scoop's own curve. A shape built by unioning
    two mirrored halves loses that — it is the same region, but the boundary
    has to be recovered from it, and anything that recovers it convexly (a
    hull, say) bridges straight across the notch.

    Args:
        radius: Half-width of the straight throat.
        height: Floor to rim.
        top_rounding: How far the top roll flares outward, already capped.
        bottom_rounding: r2, already capped to fit.
        top_rise: How far the top roll reaches down. ``None`` makes it equal to
            the flare, i.e. a circular quarter-roll.

    Returns:
        ``[(x, y), ...]`` closed counter-clockwise, floor at ``y=0``.
    """
    flare, r2 = top_rounding, bottom_rounding
    rise = flare if top_rise is None else top_rise
    # Past the half-width the base is no longer a pair of corner circles but a
    # single arc across the cut, so its centre stops sliding outward and sits on
    # the axis (FR-052). Left to slide, the two mirrored arcs cross over each
    # other and the base folds inside out.
    bottom_centre = (max(0.0, radius - r2), r2)
    top_centre = (radius + flare, height - rise)

    right: list[tuple[float, float]] = []
    join_low, join_high = _tangent_join(bottom_centre, r2, top_centre, flare, radius)
    # Base arc, then the **internal tangent** between the two circles as the
    # flank, then the roll on to the top face (FR-052). Every join is a touch
    # point, so the direction never changes across one: deep, the run comes out
    # vertical and this is the familiar throat; shallow, it tilts and shortens
    # and the base's arc does the rest.
    right += _quarter_arc(
        bottom_centre, r2, -90.0, _sweep_end(_angle_at(bottom_centre, join_low), -90.0)
    )
    if abs(rise - flare) < 1e-9:
        # A circular roll: the tangent's touch point is on it exactly, so the
        # arc can start there — pointed the right way round. The touch sits on
        # the roll's left half, at 90°..270°, and `_angle_at` reports that as
        # either +180 or **-180** depending on the sign of a floating-point
        # zero: `atan2(-0.0, -5.5)` is -180. Sweeping -180 → 90 takes the arc
        # the long way round the bottom of the circle — 270° of it — which is
        # the cut running sideways and down to reach a join it should have met
        # head-on, and it lands on one box size and not the next.
        right += _quarter_arc(
            top_centre, flare, _sweep_end(_angle_at(top_centre, join_high), 90.0), 90.0
        )
    else:
        # An elliptical roll (a compartment scoop): the touch point is computed
        # against a circle of the flare and is not on the ellipse, so the run
        # ends where the ellipse starts, which is vertical there and matches.
        right.append((radius, height - rise))
        right += _elliptical_quarter(top_centre, flare, rise)
    # Carry on straight up past the rim. Closing the ring along the top instead
    # would put a **cusp** at each end of the r1 arc: the arc arrives there
    # travelling horizontally outward and the closing edge leaves horizontally
    # back inward, so the outline doubles on itself at zero angle. Offsetting
    # such a corner miters to infinity — measured, a ±15mm profile came back
    # ±55mm. There is no material above the rim, so the overshoot costs nothing
    # and it also guarantees the cut leaves no skin at the top face.
    right.append((radius + flare, height + RIM_OVERSHOOT_MM))

    left = [(-x, y) for x, y in reversed(right)]
    return left + right
def floor_bore_profile(
    radius: float,
    height: float,
    top_rounding: float = DEFAULT_MOUTH_ROUNDING_MM,
) -> "Bosl2Shape2D":
    """Build the 2-D profile of a **floor** finger hole, in the X-Z plane.

    Deliberately not the edge profile. An edge scoop is a shape you sweep a
    finger *along* — flat floor, straight throat, rolled rim — while a floor
    finger hole is a bore you push a piece *up* through, so its bottom is a
    bowl tangent to the floor rather than a flat pan. Sharing one profile
    between them was convenient and produced a flat-bottomed pit where a bowl
    belongs.

    Args:
        radius: Bore radius — the widest part of the bowl.
        height: Height from the floor to the rim.
        top_rounding: How far the mouth rolls out at the rim, as ``r1`` on an
            edge scoop. ``0`` gives a square-topped bore.

    Returns:
        The profile as 2-D geometry, floor at ``y=0``, rim at ``y=height``,
        centred on ``x=0``.

    Raises:
        ValueError: If ``radius`` or ``height`` is not positive, or
            ``top_rounding`` is negative.
    """
    from pybosl2 import shapes2d

    if radius <= 0:
        raise ValueError(f"bore radius must be > 0; got {radius}")
    if height <= 0:
        raise ValueError(f"bore height must be > 0; got {height}")
    if top_rounding < 0:
        raise ValueError(f"top_rounding must be >= 0; got {top_rounding}")

    # A full circle sitting on the floor: its lower half is the bowl, tangent
    # to the floor plane, so the bottom of the cut curves into the floor.
    bore = shapes2d.circle(radius=radius, **precision_kwargs()).translate([0.0, radius])
    profile = bore

    throat_top = height - top_rounding
    if throat_top > radius:
        profile = profile | shapes2d.square(
            [radius * 2, throat_top - radius], center=True
        ).translate([0.0, radius + (throat_top - radius) / 2])

    if top_rounding > 0:
        # The same r1 roll as an edge scoop: horizontal at the top face,
        # vertical where it meets the throat.
        points = [(0.0, max(0.0, throat_top))]
        points += _quarter_arc(
            (radius + top_rounding, throat_top), top_rounding, 180.0, 90.0
        )
        points.append((0.0, height))
        mouth = shapes2d.polygon([[float(x), float(y)] for x, y in points])
        profile = profile | mouth | mouth.mirror([1, 0])

    return profile
