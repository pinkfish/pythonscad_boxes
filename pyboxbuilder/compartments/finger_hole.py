# SPDX-License-Identifier: Apache-2.0
"""Finger scoop and notch geometry for compartment walls and floors.

Ported from the original toolkit's ``FingerHoleWall`` and ``FingerHoleBase``
(``components.scad``), which are the reference for how a finger cut is meant to
be smoothed. Three separate roundings are at work, and they are easy to
conflate:

1. **The mouth** (``rounding_radius``) — the top of the profile flares outward
   into the compartment rim with a pair of concave fillets, so the opening
   curves into the wall instead of ending in a right-angle lip. This is the
   part a fingertip actually rides over.
2. **The faces** (``rounding_edge``) — the sweep's two ends get a *negative*
   (concave) rim, so where the cut emerges on each side of the wall it flows
   onto that face tangentially rather than leaving a sharp shadow line. Each
   face is independently switchable, because the outside of a box wants the
   softening far more than a compartment-internal divider does.
3. **The base** — a floor scoop additionally fillets the cut into the floor
   plane, so the bottom of the cut blends into the box's inside surface.

Both helpers return cutouts in the compartment's own frame: (0, 0, 0) is the
compartment's lower-left corner at its floor, the footprint runs out to
(comp_width, comp_length), and +Z is up towards the rim.
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from pyboxbuilder.enums import ScoopSide
from pyboxbuilder.precision import kwargs as precision_kwargs
from pyboxbuilder.rounding import rounding_facets, roundover_profile

if TYPE_CHECKING:
    from pybosl2.shapes2d import Bosl2Shape2D
    from pybosl2.shapes3d import Bosl2Solid

DEFAULT_FLOOR_DIP_MM = 0.2
"""How far a cut passes below the well floor, by default.

Its only job is to keep the cut's bottom face off the floor plane, since a
coincident face renders as speckle and is how a boolean leaves a zero-thickness
skin. 0.2mm does that. Scaling it with the floor thickness — which an earlier
version did, up to a full millimetre — spends half a 2mm floor on a cosmetic
detail, and it showed as the cut visibly eating into the floor.
"""

MIN_WALL_SCOOP_DEPTH_MM = 5.0
"""Below this a wall notch has nothing to grip, so the floor scoop is used.

The two cuts answer different situations. A notch in the wall is a dip a finger
hooks into, and it needs depth to be a dip at all; a floor bore is a bowl in the
well's own floor, for a tray too shallow for one — the original's 4mm token
case.

**8mm was too high**, and by more than it looks: Emberleaf's player card box has
a 6.5mm well, which fell to the bore and came out as a nick in the rim about a
millimetre deep, with the wall whole underneath it. What a card box needs there
is a dip to get a fingertip under the stack. 5mm sits between that well and the
4mm tray the bore is actually for, and it is the number the plan already assumed
when it recorded these boxes cutting wall scoops.
"""

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

DEFAULT_EDGE_ROUNDING_MM = 1.0
"""Fallback face fillet where no wall thickness is known.

The scoops normally derive it as ``wall_thickness / 2`` instead, which is what
the original passes and the largest fillet a wall has room for.
"""

_SIDE_CENTRES = {
    ScoopSide.FRONT: lambda w, l: (w / 2, 0.0),
    ScoopSide.BACK: lambda w, l: (w / 2, l),
    ScoopSide.LEFT: lambda w, l: (0.0, l / 2),
    ScoopSide.RIGHT: lambda w, l: (w, l / 2),
}

# Rotation about Z that turns the front-facing profile to face each side. The
# profile is built in the X-Z plane and swept along -Y — outward through the
# FRONT wall — so each spin has to carry that outward direction to the right
# side. Spin 90 maps (x, y) to (-y, x), which sends -Y to +X: that is RIGHT,
# not LEFT. Getting these backwards leaves the cut inside the compartment,
# shaving the wall's inner face by the sweep's 0.015 of fudge and piercing
# nothing — invisible in a bounding box, which is how it survived once.
_SIDE_SPIN = {
    ScoopSide.FRONT: 0.0,
    ScoopSide.BACK: 180.0,
    ScoopSide.LEFT: 270.0,
    ScoopSide.RIGHT: 90.0,
}


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
"""How near the touching cap a grip's base circle is sized (FR-043a7).

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
    (FR-043a7).

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
            (FR-043a), wrong for a grip, whose base is round (FR-043a5).
        roll_rise: How far the top roll reaches **down**. ``None`` derives it
            as ``TOP_ROLL_RISE_RATIO`` times the flare. It is the fourth of the
            numbers that define the outline (FR-043a0) and the one that says
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

    **The corner radius is kept, not fitted** (FR-043a5). The straight run
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
        # (FR-043a), and its corner circles must not overlap each other.
        r2 = radius * DEFAULT_BOTTOM_ROUNDING_RATIO if asked is None else asked
        r2 = min(max(0.0, r2), radius * (1.0 - MIN_FLAT_BOTTOM_RATIO))
        # Everything past that comes off the rise before it comes off r2.
        r2 = max(0.0, min(r2, radius, height - floor_rise))
        rise = max(floor_rise, min(rise, height - r2)) if height > r2 else 0.0
        return flare, rise, r2

    # A grip. One shape for every proportion (FR-043a7): a base circle sitting
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
    points = []
    for index in range(samples + 1):
        angle = math.pi + (math.pi / 2) * index / samples
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
    # base circle is sized against (FR-043a7). With d the distance between the
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
    band standing over it (FR-043b1) — there is no surface to roll onto, and the
    scoop's own outline cannot be used: capping it leaves the cut's ceiling
    meeting each face of the wall at a square edge, with the face fillet
    stopping dead at the cap. What belongs there is a closed window, filleted
    the whole way round, which the offset sweep gives for nothing because the
    fillet follows the ring (FR-044e1, FR-043b1a).

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
    the next (FR-043a7).
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
    # the axis (FR-043a7). Left to slide, the two mirrored arcs cross over each
    # other and the base folds inside out.
    bottom_centre = (max(0.0, radius - r2), r2)
    top_centre = (radius + flare, height - rise)

    right: list[tuple[float, float]] = []
    join_low, join_high = _tangent_join(bottom_centre, r2, top_centre, flare, radius)
    # Base arc, then the **internal tangent** between the two circles as the
    # flank, then the roll on to the top face (FR-043a7). Every join is a touch
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


def scoop_face_flare(
    wall_thickness: float, rounding_edge: float | None = None
) -> float:
    """How far a wall scoop's face fillet reaches **beyond** its outline (FR-043g).

    The fillet that rolls the cut onto each face is produced by flaring the
    sweep's end, and the flare is isotropic in the profile plane — it grows
    downward past the flat bottom exactly as readily as it grows sideways. So
    the solid `build_wall_scoop` returns is this much taller than the height it
    was asked for, at each end.

    Callers that place a scoop against something — a floor, an interior top —
    must add this back, or the cut lands lower than the height they asked for
    (T306). It is also what the floor clip has to allow for: clipping at the
    outline's flat bottom slices the flare off mid-curve and leaves the wall's
    sawn cross-section showing at the base of the scoop.

    Args:
        wall_thickness: The wall the cut passes through.
        rounding_edge: Requested face fillet; ``None`` uses ``wall_thickness / 2``.

    Returns:
        The flare in mm — normally ``wall_thickness / 2``.
    """
    if rounding_edge is None:
        rounding_edge = wall_thickness / 2
    fudge = 0.03
    return max(0.0, min(rounding_edge, (wall_thickness + fudge - 0.01) / 2))


def build_wall_scoop(
    comp_width: float,
    comp_length: float,
    comp_depth: float,
    side: ScoopSide,
    radius: float = 12.0,
    wall_thickness: float = 2.0,
    rounding_radius: float | None = None,
    bottom_rounding: float | None = None,
    rounding_edge: float | None = None,
    round_inner: bool = True,
    round_outer: bool = True,
    breach_floor: bool = False,
    floor_thickness: float | None = None,
    floor_clearance: float | None = None,
    top_limit: float | None = None,
    closed_top: bool = False,
    roll_rise: float | None = None,
    keep_flat_bottom: bool = True,
) -> "Bosl2Solid":
    """Build a finger notch through a compartment wall.

    The **edge** profile from :func:`scoop_profile` — flat bottom, straight
    throat, rolled rim — swept through the wall, with a
    concave rim on each end so the cut flows onto the wall's faces instead of
    ending in a sharp line (``FingerHoleWall``'s ``rounding_edge``).

    **The sweep is exactly the wall thickness, centred on the wall** (the
    original passes ``depth_of_hole = wall_thickness + 0.03``), and that is
    load-bearing rather than incidental: a face fillet is produced by flaring
    the sweep's *end*, so the end has to coincide with the face. Overshooting
    the wall by a millimetre — the obvious way to make sure a boolean leaves no
    skin — puts both fillets out in the air beyond the box and leaves the cut
    meeting the faces at a hard edge after all. The 0.03 of fudge is the whole
    margin available.

    The sweep runs from the compartment floor to the rim, so a finger can reach
    the last card at the bottom of the stack, and is clipped at the floor plane
    so the box's base is not breached from the outside.

    Args:
        comp_width: Compartment footprint width.
        comp_length: Compartment footprint length.
        comp_depth: Compartment depth; the scoop runs its full height.
        side: Which wall to notch.
        radius: Notch radius in mm, capped so it cannot swallow the compartment.
        wall_thickness: Wall the cut passes through. Sets the sweep depth and,
            by default, the face fillet.
        rounding_radius: ``r1`` — how far the mouth rolls out at the rim.
            ``None`` derives it as half the throat half-width, so the roll
            stays in proportion to the scoop.
        bottom_rounding: ``r2`` — the fillet from the throat into the flat
            bottom. ``None`` derives it as half the throat width.
        rounding_edge: Fillet where the cut emerges on a face. Defaults to
            ``wall_thickness / 2``, the largest fillet the wall has room for
            (and what the original uses). ``0`` squares the edge.
        round_inner: Fillet the compartment-side face.
        round_outer: Fillet the outward face — the visible outside of the box.
        breach_floor: Let the cut run as deep as the flare naturally reaches,
            with no clip at all. Off by default.
        floor_thickness: The box floor under this compartment. Used to size the
            dip below the well floor (half the floor, at most 1mm), which is
            what keeps the cut's bottom face off the floor plane.
        floor_clearance: Dip below the well floor, overriding the value derived
            from ``floor_thickness``. ``0`` clips exactly at the floor, at the
            cost of a coincident face.
        top_limit: Height, in the cut's own frame, above which it is trimmed
            away — the guard for material that must not be cut into.
        keep_flat_bottom: Keep part of the base flat by capping the corner
            radius (FR-043a) — for a well something rests in. A grip passes
            ``False`` and gets the radius it asked for, with a round base
            (FR-043a5).
        roll_rise: How far the mouth roll reaches down; ``None`` derives it
            from the flare (FR-043c3). Width and gentleness are separate
            settings, so a shallow wall can have a gentler curve without a
            wider mouth.
        closed_top: Build a **closed window** (:func:`window_outline`) instead
            of a top-opening scoop. For a cut with wall standing above it,
            where there is no surface for the mouth roll to roll onto and a
            trimmed-off scoop would meet the faces at a square edge
            (FR-043b1a).

    Returns:
        Bosl2Solid cutout, positioned in the compartment frame.

    Raises:
        ValueError: If the compartment or wall dimensions are not positive.
    """
    if comp_depth <= 0:
        raise ValueError(f"comp_depth must be > 0; got {comp_depth}")
    if rounding_radius is None:
        rounding_radius = radius * DEFAULT_TOP_ROUNDING_RATIO
    if wall_thickness <= 0:
        raise ValueError(f"wall_thickness must be > 0; got {wall_thickness}")

    span = comp_width if side in (ScoopSide.FRONT, ScoopSide.BACK) else comp_length

    # The mouth is `radius + r1` wide on each side, and the two have to share
    # the span. Capping the throat first and giving r1 whatever is left sounds
    # equivalent and is not: a throat already at half the span leaves r1 exactly
    # zero, which silently deletes the top roll — the most visible part of the
    # scoop — on every narrow compartment. Shrink them together instead, so a
    # tight span costs both a little rather than costing r1 everything.
    if radius + rounding_radius > span / 2:
        scale = (span / 2) / (radius + rounding_radius)
        radius, rounding_radius = radius * scale, rounding_radius * scale
    rounding_radius = max(0.0, rounding_radius)

    if rounding_edge is None:
        rounding_edge = wall_thickness / 2

    # Just the wall, plus a hair at each face so the boolean has no coincident
    # plane to resolve. See the note above on why this must not be larger.
    fudge = 0.03
    depth = wall_thickness + fudge
    rim = scoop_face_flare(wall_thickness, rounding_edge)

    # Named rather than splatted: `_fit_radii` returns (flare, rise, r2) and
    # `scoop_outline` takes (top_rounding, bottom_rounding, top_rise), so
    # `*_fit_radii(...)` fed the top roll's **rise** to the floor fillet and the
    # floor fillet to the rise. The bottom curve was therefore sized off the
    # rounding radius (1.6x the top flare) instead of off the throat radius —
    # both curves of the U driven by the same number, which is exactly what it
    # looked like. `scoop_profile` had the order right all along.
    flare, rise, r2 = _fit_radii(
        radius, comp_depth, rounding_radius, bottom_rounding, roll_rise,
        keep_flat_bottom=keep_flat_bottom,
    )
    outline = (
        window_outline(radius, comp_depth, r2)
        if closed_top
        else scoop_outline(radius, comp_depth, flare, r2, rise)
    )
    return _sweep_through_wall(
        outline, comp_width, comp_length, side,
        comp_depth=comp_depth,
        wall_thickness=wall_thickness,
        rounding_radius=rounding_radius,
        rounding_edge=rounding_edge,
        round_inner=round_inner,
        round_outer=round_outer,
        breach_floor=breach_floor,
        floor_thickness=floor_thickness,
        floor_clearance=floor_clearance,
        top_limit=top_limit,
        span=span,
        radius=radius,
    )


def _sweep_through_wall(
    outline: list,
    comp_width: float,
    comp_length: float,
    side: ScoopSide,
    *,
    comp_depth: float,
    wall_thickness: float,
    rounding_radius: float,
    rounding_edge: float | None,
    span: float,
    radius: float,
    round_inner: bool = True,
    round_outer: bool = True,
    breach_floor: bool = False,
    floor_thickness: float | None = None,
    floor_clearance: float | None = None,
    top_limit: float | None = None,
    inner_overshoot: float = 0.0,
) -> "Bosl2Solid":
    """Sweep a 2-D scoop profile through a wall and place it on a side.

    Shared by the edge scoop and the floor finger hole: the *profiles* differ
    (that is the point — one is a channel, the other a bore), but everything
    around them is the same, and duplicating it is how the two drift apart.

    Args:
        outline: The scoop's closed 2-D outline as a point ring, floor at
            ``y=0``. A ring rather than a 2-D shape because the fillet has to
            follow it around: the sweep offsets the outline itself, so the
            fillet traces the scoop's own curve on each face.
        comp_width: Compartment footprint width.
        comp_length: Compartment footprint length.
        side: Which wall to cut through.
        comp_depth: Compartment depth, used to size the floor clip.
        wall_thickness: The wall being crossed; sets the sweep depth.
        rounding_radius: r1, used to size the floor clip.
        rounding_edge: Face fillet; ``None`` uses half the wall.
        span: The compartment span along the cut wall.
        radius: The scoop's half-width, used to size the floor clip.
        round_inner: Fillet the compartment-side face.
        round_outer: Fillet the outward face.
        breach_floor: Skip the floor clip entirely.
        floor_thickness: Box floor, sizing the permitted dip below it.
        floor_clearance: Explicit dip below the well floor.
        inner_overshoot: How far past the wall's **inner** face to run the
            sweep. `offset_sweep` holds its straight middle at the last offset
            its *first* rim reached, so a rim on one end only leaves the middle
            at the path's full width and the other rim stepping in from it — a
            ridge inside the cut, a fillet's depth from the face. Running the
            sweep a fillet further into the compartment puts that rim's whole
            transition in the well, which is void anyway, and leaves the wall
            with one constant section and a square inner edge.
        top_limit: Height, in the scoop's own frame, above which the cut is
            trimmed away. Needed when there is material above the cut — the
            lid band of a lidded box — where the outline's rim overshoot would
            otherwise carry the cut straight through it. ``None`` (a free rim)
            keeps the overshoot, which is what leaves no skin at the top face.

    Returns:
        The cutout, positioned in the compartment frame.
    """
    if rounding_edge is None:
        rounding_edge = wall_thickness / 2

    fudge = 0.03
    depth = wall_thickness + fudge + inner_overshoot
    rim = scoop_face_flare(wall_thickness, rounding_edge)

    # BOSL2's own offset_sweep, which lofts between offsets of the outline, so
    # the fillet follows the cut's curve. (A hand-rolled stand-in chained
    # convex hulls between slices, and a hull across a U-shaped outline bridges
    # the notch — the fillet came out as a ramp across the opening.)
    from pybosl2.path2d import Path2D

    steps = max(8, rounding_facets()["fn"] // 4)
    ring = [[float(x), float(y)] for x, y in outline]
    fillet = rim if (rim > 0 and (round_outer or round_inner)) else 0.0

    if fillet > 0:
        # The path is the cross-section **at the end face**, and a rim profile
        # moves it as you travel inward. So the widened outline is the path and
        # the rim brings it back in: that is what puts the extra material at
        # the face, where the roundover belongs.
        path = Path2D(ring, closed=True).offset(delta=fillet)
        swept = path.offset_sweep(
            height=depth,
            # Which end is which: the sweep runs from the compartment side
            # **outward** through the wall (the rotation below sends +z to -y,
            # and the side placement puts z=0 on the compartment's own edge),
            # so `bottom` is the inner face and `top` the box's outside. Naming
            # them the other way round is the obvious mistake and a silent one
            # — with both faces rounded, which every compartment scoop does,
            # nothing distinguishes them. Measured: asking for the outward face
            # alone used to leave it square at the nominal width and widen the
            # compartment side instead.
            bottom=roundover_profile(fillet, steps) if round_inner else None,
            top=roundover_profile(fillet, steps) if round_outer else None,
            steps=steps,
        )
    else:
        swept = Path2D(ring, closed=True).offset_sweep(height=depth, steps=steps)
    # offset_sweep hands back a VNF; realise it and wrap the native solid so
    # the transforms and booleans below have something to work with.
    from pybosl2.shapes3d.base import CsgSolid

    swept = CsgSolid(swept.polyhedron())

    # The profile is built in X-Z and extruded along +Z. Stand it up so the
    # extrusion runs along -Y (into the wall), then shift it so it spans the
    # wall from just outside the outer face to just inside the inner one.
    standing = swept.rotate([90.0, 0.0, 0.0]).translate(
        [0.0, fudge / 2 + inner_overshoot, 0.0]
    )

    if not breach_floor:
        # Clip the cut just *below* the well floor. The flare is isotropic in
        # the profile plane, so it grows downwards past the bore as readily as
        # sideways, and left alone it would thin the floor by the fillet.
        #
        # The clip does not sit exactly on the floor plane, though: that leaves
        # the cut's bottom face coplanar with the floor, and a coincident face
        # renders as speckle and is the classic way a boolean leaves a
        # zero-thickness skin. The original's answer is to overshoot into the
        # floor by about a millimetre; this does the same, bounded by half the
        # floor so the box's base is still solid underneath.
        from pybosl2 import cuboid

        dip = floor_clearance if floor_clearance is not None else min(
            DEFAULT_FLOOR_DIP_MM,
            (floor_thickness / 4) if floor_thickness else DEFAULT_FLOOR_DIP_MM,
        )
        dip = max(0.0, dip)
        reach = comp_depth + rounding_radius + rim + 1.0
        keep = cuboid([span * 2 + radius * 4, depth * 4, reach * 2]).translate(
            [0.0, 0.0, reach - dip]
        )
        standing = standing & keep

    if top_limit is not None:
        from pybosl2 import cuboid

        reach = comp_depth + rounding_radius + rim + RIM_OVERSHOOT_MM + 1.0
        standing = standing & cuboid(
            [span * 2 + radius * 4, depth * 4, reach * 2]
        ).translate([0.0, 0.0, top_limit - reach])

    oriented = standing.rotate([0.0, 0.0, _SIDE_SPIN[side]])
    x, y = _SIDE_CENTRES[side](comp_width, comp_length)
    return oriented.translate([x, y, 0.0])


def build_floor_scoop(
    comp_width: float,
    comp_length: float,
    side: ScoopSide,
    radius: float = 14.0,
    comp_depth: float | None = None,
    wall_thickness: float = 2.0,
    rounding_radius: float | None = None,
    rounding_edge: float | None = None,
    floor_thickness: float | None = None,
) -> "Bosl2Solid":
    """Build a scoop that blends into the compartment floor, at one edge.

    Ported from ``FingerHoleBase``, which is the shallow-compartment case: a
    wall notch in a 4mm wall gives a finger nothing to bite, so the cut is
    taken into the *floor* instead. Three parts, matching the original:

    1. the bore itself, running the compartment's full depth;
    2. a mouth flared into the rim, as on a wall scoop;
    3. a fillet blending the cut into the floor plane, so the bottom of the
       scoop curves into the box's inside surface rather than meeting it at a
       right angle.

    The floor fillet is what distinguishes this from a plain dish, and it is
    sized off the wall thickness (the original uses ``wall_thickness / 2``) so
    it stays proportionate to the box rather than to the finger.

    Args:
        comp_width: Compartment footprint width.
        comp_length: Compartment footprint length.
        side: Which edge the scoop sits against.
        radius: Bore radius in mm, capped to half the compartment's span.
        comp_depth: Compartment depth. Defaults to ``radius`` when unknown.
        wall_thickness: Wall the cut passes through; also sets the floor fillet.
        rounding_radius: Flare at the mouth where the cut meets the rim.
        rounding_edge: Fillet where the cut emerges on a face.

    Returns:
        Bosl2Solid cutout, positioned in the compartment frame. It reaches down
        to the floor plane and no further, so the box's base stays intact.

    Raises:
        ValueError: If the compartment span is not positive.
    """
    from pybosl2 import cuboid

    span = comp_width if side in (ScoopSide.FRONT, ScoopSide.BACK) else comp_length
    if span <= 0:
        raise ValueError(f"compartment span must be > 0; got {span}")

    radius = min(radius, span / 2)
    if rounding_radius is None:
        rounding_radius = radius * DEFAULT_TOP_ROUNDING_RATIO
    depth = comp_depth if comp_depth and comp_depth > 0 else radius

    # Parts 1 and 2: the bore, swept through the wall with the same face
    # fillets an edge scoop gets. The *profile* is the floor one — a bowl
    # tangent to the floor — because this is a hole you push a piece up
    # through, not a channel you sweep a finger along.
    cut = _sweep_through_wall(
        floor_bore_outline(min(radius, span / 2), depth, rounding_radius),
        comp_width, comp_length, side,
        comp_depth=depth,
        wall_thickness=wall_thickness,
        rounding_radius=rounding_radius,
        rounding_edge=rounding_edge,
        floor_thickness=floor_thickness,
        span=span,
        radius=min(radius, span / 2),
    )

    # Part 3: blend the cut into the floor. A cuboid whose top edges carry a
    # negative (concave) rounding leaves a fillet against the floor plane, so
    # the finger follows a curve out of the bore and onto the floor instead of
    # catching on a right-angled step.
    fillet = wall_thickness / 2
    if fillet > 0:
        from pybosl2.constants import Anchor

        run = radius * 2 + fillet * 2
        dip = min(1.0, floor_thickness / 2) if floor_thickness else 0.2
        pad = cuboid(
            [run, fillet, fillet + dip],
            rounding=-fillet,
            edges=[Anchor.TOP + Anchor.FRONT, Anchor.TOP + Anchor.BACK],
            **precision_kwargs(),
        )
        x, y = _SIDE_CENTRES[side](comp_width, comp_length)
        inward = 1.0 if side in (ScoopSide.FRONT, ScoopSide.LEFT) else -1.0
        centre_z = (fillet - dip) / 2
        if side in (ScoopSide.FRONT, ScoopSide.BACK):
            placed = pad.translate([x, y + inward * fillet / 2, centre_z])
        else:
            placed = pad.rotate([0.0, 0.0, 90.0]).translate(
                [x + inward * fillet / 2, y, centre_z]
            )
        cut = cut | placed

    return cut


def build_scoop(
    comp_width: float,
    comp_length: float,
    comp_depth: float,
    side: ScoopSide,
    radius: float = 12.0,
    wall_thickness: float = 2.0,
    rounding_radius: float | None = None,
    rounding_edge: float | None = None,
    floor_thickness: float | None = None,
) -> "Bosl2Solid":
    """Pick the right scoop for the compartment's depth.

    Deep compartments get a wall notch; shallow ones get the floor-blended cut,
    because a notch in a 4mm-deep well is not something a finger can use.

    Args:
        comp_width: Compartment footprint width.
        comp_length: Compartment footprint length.
        comp_depth: Compartment depth; decides which scoop is built.
        side: Which wall or edge the scoop sits on.
        radius: Scoop radius in mm.
        wall_thickness: Wall the cut passes through.
        rounding_radius: ``r1``; ``None`` derives it from the throat width.
        rounding_edge: Fillet where the cut emerges on a face.

    Returns:
        Bosl2Solid cutout, positioned in the compartment frame.
    """
    if comp_depth >= MIN_WALL_SCOOP_DEPTH_MM:
        return build_wall_scoop(
            comp_width, comp_length, comp_depth, side,
            radius=radius, wall_thickness=wall_thickness,
            rounding_radius=rounding_radius, rounding_edge=rounding_edge,
            floor_thickness=floor_thickness,
        )
    return build_floor_scoop(
        comp_width, comp_length, side,
        radius=radius, comp_depth=comp_depth, wall_thickness=wall_thickness,
        rounding_radius=rounding_radius, rounding_edge=rounding_edge,
        floor_thickness=floor_thickness,
    )


def build_through_hole(
    comp_width: float,
    comp_length: float,
    side: ScoopSide,
    radius: float = 14.0,
    comp_depth: float = 20.0,
    wall_thickness: float = 2.0,
    floor_thickness: float = 2.0,
    mouth_flare: float | None = None,
    rounding_edge: float | None = None,
) -> "Bosl2Solid":
    """A finger hole cut **through the floor**, for a well holding a stack.

    A scoop puts a finger down the *side* of what a well holds. A card stack
    fills its well, so there is no side to reach down — what lifts it is a thumb
    from underneath, which means the cut has to go through the box's base
    (FR-043a10). Every card box in the original toolkit does this: `FingerHoleBase`
    is a cylinder, and its callers translate it ``-default_floor_thickness - 0.5``
    so it starts below the base and cuts right through.

    The circle sits **on the wall** the ``side`` names, straddling it, so the
    finger arrives under the *edge* of the stack — where a card is lifted from —
    and the middle of the floor is left to hold the pieces up. Rolled where it
    emerges: onto both faces of the wall, and into the wall's top.

    Args:
        comp_width: Compartment footprint width.
        comp_length: Compartment footprint length.
        side: Which wall the hole is cut at.
        radius: Hole radius in mm; capped to half the wall's span.
        comp_depth: Compartment depth — the cut runs from below the base to
            the top of the wall.
        wall_thickness: The wall the hole breaks through.
        floor_thickness: The floor it passes through; the cut starts below it.
        mouth_flare: How far the hole's top rolls outward into the wall's rim;
            ``None`` uses the 3mm the original does.
        rounding_edge: Fillet where the cut emerges on the wall's **outside**
            face. The inside face and the base stay square: the inside is what
            a card stack rests against, and the base is a surface the box sits
            on. ``None`` uses
            ``wall_thickness / 2``, as everywhere else.

    Returns:
        Bosl2Solid cutout, positioned in the compartment frame — its floor at
        ``z = 0``, so the cut reaches down to ``-floor_thickness`` and below.

    Raises:
        ValueError: If the compartment span, depth or radius is not positive.
    """
    from pybosl2 import cuboid, cylinder

    span = comp_width if side in (ScoopSide.FRONT, ScoopSide.BACK) else comp_length
    if span <= 0:
        raise ValueError(f"compartment span must be > 0; got {span}")
    if comp_depth <= 0:
        raise ValueError(f"comp_depth must be > 0; got {comp_depth}")
    if radius <= 0:
        raise ValueError(f"radius must be > 0; got {radius}")
    if rounding_edge is None:
        rounding_edge = wall_thickness / 2
    radius = min(radius, span / 2)

    # Below the base and above the rim: the cut has to *leave* on both sides,
    # so neither end is a coincident face for the boolean to resolve. Clear of
    # the base by the **face fillet** as well, not just a hair: the fillet rolls
    # right around the slot's ring, so a ring ending a millimetre under a 2mm
    # floor puts its bottom roll back up inside the base and leaves a curled lip
    # around the hole's underside. The hole meets the base flat (FR-043a10).
    below = floor_thickness + rounding_edge + 0.5
    height = comp_depth + below + RIM_OVERSHOOT_MM
    # The bore's wall is a surface a finger runs right around, and a big one —
    # 30mm across on a card box. The ambient preview precision caps a circle at
    # `fa = 12°`, i.e. 30 facets however large it is, which on a hole this size
    # is a visible polygon rather than a curve. `rounding_facets` is the same
    # floor every fillet in the library uses, and the original pins a count of
    # 64 on this exact cylinder for the same reason; an export's higher count
    # still wins.
    bore = cylinder(
        height=height, radius=radius, **rounding_facets()
    ).translate([0.0, 0.0, height / 2 - below])

    # The wall itself: the bore only reaches the wall's inner half, so the rest
    # of the way through is a slot of the same width, rolled onto each face by
    # the same fillet the scoops use (FR-043c).
    #
    # Its **top corners roll into the wall's rim** rather than meeting it
    # square (FR-043a10) — the original flares them by `rounding_radius` and
    # rolls the top edge over by half the wall besides. This is the edge a hand
    # meets when it picks the box up, so a square one is felt immediately. The
    # roll is circular and tangent to the top face, as a grip's is.
    if mouth_flare is None:
        mouth_flare = DEFAULT_MOUTH_ROUNDING_MM
    mouth_flare = max(0.0, min(mouth_flare, radius))
    right: list[tuple[float, float]] = [(radius, -below)]
    if mouth_flare > 0:
        right += _quarter_arc(
            (radius + mouth_flare, comp_depth - mouth_flare), mouth_flare, 180.0, 90.0
        )
    right.append((radius + mouth_flare, comp_depth + RIM_OVERSHOOT_MM))
    outline = [(-x, y) for x, y in reversed(right)] + right

    depth = wall_thickness + 0.03
    slot = _sweep_through_wall(
        outline,
        comp_width,
        comp_length,
        side,
        comp_depth=comp_depth,
        wall_thickness=wall_thickness,
        rounding_radius=0.0,
        rounding_edge=rounding_edge,
        # Only the box's **outside** is rolled — the inside is what the stack
        # rests against, and a fillet there is a gap the bottom card slides
        # into rather than anything a hand touches. It is still swept with
        # *both* rims and run a fillet further into the compartment: that puts
        # the inner rim's whole transition in the well, which is void, so what
        # the wall gets is one constant section, square at its inner face and
        # rolled at its outer one. Asking for a single rim instead leaves the
        # middle at the path's full width with the other rim stepping in from
        # it — a ridge inside the hole a fillet's depth from the outer face.
        round_inner=True,
        round_outer=True,
        inner_overshoot=rounding_edge,
        breach_floor=True,
        span=span,
        radius=radius,
    )

    x, y = _SIDE_CENTRES[side](comp_width, comp_length)
    return slot | bore.translate([x, y, 0.0])
