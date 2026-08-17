# SPDX-License-Identifier: Apache-2.0
"""The walled shell every box type starts from, and how solids get placed.

Each box type used to carry its own copy of `outer - inner`, which meant the
hollowing rule lived in thirteen places. It lives here instead, and it takes one
decision with it: a box is only hollowed out wholesale when nothing else is
going to define its cavities. As soon as a box has compartments, the interior
stays solid and the compartments are what get carved out of it — otherwise the
individual wells (a slot per worker, say) would be lost inside one big void.

`block` and `corner` live here too. Every pybosl2 primitive is **centre**-
anchored — `cuboid([10, 20, 5])` spans -5..5 by -10..10 by -2.5..2.5 — while box
geometry is naturally written in corner coordinates ("the floor is `ft` thick,
so the interior starts at z = ft"). These two helpers do that conversion once,
so no caller has to remember to add half a size.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from typing import TYPE_CHECKING

from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.enums import ScoopSide
from pyboxbuilder.precision import kwargs as precision_kwargs
from pyboxbuilder.rounding import (
    default_rounding,
    round_edges,
    vertical_and_bottom_edges,
)

if TYPE_CHECKING:
    from pybosl2 import Anchor
    from pybosl2.shapes3d import Bosl2Solid

    from pyboxbuilder.builders._base import FingerHoleBuilder


MIN_FINGER_HOLE_REACH_MM = 2.0
"""The shallowest an automatic finger hole may be (FR-047).

Shallower than this is not a cut a finger can use, so a tray with no room for
it *and* the strip below (:data:`MIN_WALL_BELOW_HOLE_MM`) ships plain rather
than spending the strip on a token dip. This used to be a floor on the reach
instead of a threshold, which bought exactly that dip out of the wall the rule
protects.
"""

MIN_WALL_BELOW_HOLE_MM = 5.0
"""Tray wall that must survive **below** an automatic finger hole (FR-047).

The strip under the cut is what carries the tray: fingers hook into the hole
and the whole load runs through the wall beneath it. This was a wall thickness
plus a millimetre, which on the usual 2mm wall is a 3mm ribbon — it prints, and
it flexes. 5mm is stiff enough to lift a full tray by.
"""

MAX_FINGER_HOLE_HEIGHT_SHARE = 0.5
"""How deep an automatic finger hole may go, as a share of the box (FR-047).

A fingertip's radius is 20mm and a tray is often 25mm tall, so the radius on its
own takes four fifths of the wall: what is left reads as two posts and a bridge.
Half is where the wall still behaves like a wall — and it is a cap, not a
target, so a deep box's cut is still sized by the finger.
"""

SLIDING_RIM_ROUNDING_SHARE = 0.25
"""How much of the wall a sliding box's top edge rounds over (FR-043f1).

A lidded box's rim is usually left square because the lid seals against it and
carries the rounding itself (FR-043d). A **sliding** box is the exception: its
lid lies down in the channel, so what stands at the box's top is the rails'
own outer edges — that edge is on the outside of the closed box and a hand
runs along it.

A quarter of the wall rather than the usual half, because the rail is what is
left of the wall once the groove is cut into it: half a wall off its top edge
is most of the bearing the lid rides on.
"""


def sliding_rim_rounding(spec: BoxSpec) -> float:
    """Return the radius for a sliding box's exposed top edge (FR-043f1).

    Args:
        spec: Reads `wall_thickness`.

    Returns:
        A quarter of the wall, in mm.

    """
    return spec.wall_thickness * SLIDING_RIM_ROUNDING_SHARE


DEFAULT_MOUTH_FLARE_MM = 3.0
"""How far a finger cut's mouth rolls out at the rim when none is given."""

MAX_FINGER_HOLE_SPAN_SHARE = 0.75
"""How much of a wall an automatic hole's mouth may take (FR-047a).

Merely fitting is not the test. A mouth spanning the whole wall leaves two
corner posts holding the rim, which is a slot rather than a grip; a quarter of
the wall left uncut keeps something either side of the finger.
"""


def corner(
    solid: Bosl2Solid,
    size: Sequence[float],
    at: Sequence[float] = (0.0, 0.0, 0.0),
) -> Bosl2Solid:
    """Place a centre-anchored solid so its minimum corner sits at `at`.

    Args:
        solid: A centre-anchored solid, as every pybosl2 primitive is.
        size: The solid's (width, length, height).
        at: Where its minimum corner should end up.

    """
    return solid.translate(
        [
            at[0] + size[0] / 2,
            at[1] + size[1] / 2,
            at[2] + size[2] / 2,
        ]
    )


def block(size: Sequence[float], at: Sequence[float] = (0.0, 0.0, 0.0)) -> Bosl2Solid:
    """Return a cuboid of `size` whose minimum corner sits at `at`."""
    from pybosl2 import cuboid

    return corner(cuboid(list(size)), size, at)


def build_shell(spec: BoxSpec) -> Bosl2Solid:
    """Outer block, hollowed to the interior unless `spec.hollow` is False.

    Args:
        spec: Needs `width`, `length`, `height`; reads `wall_thickness`,
            `floor_thickness` and `hollow` (default True).

    Returns:
        The box body before any type-specific lid features are added.

    """
    size = [spec.width, spec.length, spec.height]
    outer = block(size)

    # Round what a hand grips: the vertical corners and the base always, and the
    # top rim too when nothing has to mate with it. On a lidded box the rim is a
    # sealing surface, so its rounding lives on the lid instead — the closed box
    # still reads as rounded top, sides and bottom (FR-043/FR-044).
    radius = body_rounding(spec)
    if radius > 0:
        edges = vertical_and_bottom_edges()
        if spec.rim_free:
            edges = [*edges, _top_anchor()]
        outer = round_edges(outer, size, radius, edges)

    # A type whose top face is exposed *with the lid on* rounds that edge too,
    # at its own radius — a sliding box, whose lid lies down in the channel so
    # the rails' outer edges are what a hand meets (FR-043f1). A lidless box
    # has already rounded its rim above, at the body radius.
    rim = 0.0 if spec.rim_free else float(spec.rim_rounding or 0.0)
    if rim > 0:
        outer = round_edges(outer, size, rim, [_top_anchor()])

    if spec.hollow:
        outer = outer - interior_block(spec)
        outer = round_inner_rim(outer, spec)
    return apply_finger_holes(outer, spec)


def body_rounding(spec: BoxSpec) -> float:
    """Return the edge radius for this box body.

    Args:
        spec: Reads `rounding`; falls back to half the wall thickness.

    Returns:
        The radius in mm. ``0`` disables rounding entirely.

    """
    explicit = spec.rounding
    if explicit is not None:
        return max(0.0, float(explicit))
    return default_rounding(spec.wall_thickness)


def _top_anchor() -> Anchor:
    """Return the TOP anchor, imported lazily so this module has no import-time pybosl2."""
    from pybosl2 import Anchor

    return Anchor.TOP


def _hole_flare(
    wall_thickness: float, hole: FingerHoleBuilder, reach: float, ends: int = 1
) -> float:
    """Return the face fillet an exterior finger hole's cut is built with.

    The fillet is made by flaring the sweep's ends, and the flare is isotropic
    in the profile plane — it grows down past the outline's flat bottom exactly
    as readily as it grows sideways. So this is also how far the cut reaches
    *below* its outline, which is what the placement has to allow for (T306).

    Capped at half the reach, and at a quarter of it where the cut is a closed
    window and so runs a flare past *both* ends (``ends=2``): on a cut shallower
    than that the flare would swallow the outline whole, leaving no straight run
    between the two curves — and no outline at all for `build_wall_scoop`.
    """
    from pyboxbuilder.compartments.finger_sweep import scoop_face_flare

    flare = scoop_face_flare(wall_thickness, hole.face_fillet)
    return min(flare, reach / (2.0 * max(1, ends)))


def finger_cut_conflicts(spec: BoxSpec) -> list[str]:
    """Finger cuts that overlap something, described one per line (FR-006c).

    Two cuts that overlap do not make two grips: they make one opening of a
    shape nobody asked for, and the geometry gives no sign of which two cuts
    made it — the merged solid looks deliberate. So the overlap is reported
    rather than left for a render to reveal.

    What is checked, and what is not: two holes on one wall are checked against
    each other, and a hole is checked against the magnet pocket that wall would
    carry. A lid track needs no check — every exterior hole is bounded by the
    interior top (FR-064) and the track lives above it, so the two cannot
    reach each other.

    Args:
        spec: Reads `finger_holes`, `width`, `length`, `height`,
            `wall_thickness`, `magnet_type` and `magnet_size`.

    Returns:
        One message per conflict, naming both features and where they are.
        Empty when the cuts are clear of each other.

    """
    from pyboxbuilder.enums import MagnetType

    holes: tuple[FingerHoleBuilder, ...] = spec.finger_holes or ()
    messages: list[str] = []

    def mouth(hole: FingerHoleBuilder) -> float:
        """Half the opening's width: the throat plus the flare it rolls out."""
        flare = hole.mouth_flare
        return hole.radius + (DEFAULT_MOUTH_FLARE_MM if flare is None else flare)

    by_side: dict[ScoopSide, list[FingerHoleBuilder]] = {}
    for hole in holes:
        by_side.setdefault(hole.side, []).append(hole)

    for side, side_holes in by_side.items():
        for index, first in enumerate(side_holes):
            for second in side_holes[index + 1:]:
                gap = abs(first.offset - second.offset)
                overlap = mouth(first) + mouth(second) - gap
                if overlap > 0:
                    messages.append(
                        f"finger holes on {side.value} overlap by "
                        f"{overlap:.1f}mm (offsets {first.offset} and "
                        f"{second.offset}): they will cut as one opening"
                    )

    magnet_type = spec.magnet_type
    if magnet_type not in (None, MagnetType.NONE) and holes:
        size = spec.magnet_size
        half = (size[0] if size else 6.0) / 2.0
        from pyboxbuilder.box.types.no_lid import NoLidBox

        magnet_sides = (
            (ScoopSide.FRONT, ScoopSide.BACK)
            if NoLidBox._magnet_sides_front_back(spec)
            else (ScoopSide.LEFT, ScoopSide.RIGHT)
        )
        mid_height = spec.height / 2.0
        for hole in holes:
            if hole.side not in magnet_sides:
                continue
            # The pocket sits at the middle of the wall at mid-height; the cut
            # hangs from the interior top. They clash when both ranges do.
            interior_top = spec.wall_top(hole.side)
            reach = min(hole.depth if hole.depth is not None else hole.radius,
                        interior_top - spec.floor_thickness)
            if interior_top - reach > mid_height:
                continue
            if abs(hole.offset) < mouth(hole) + half:
                messages.append(
                    f"the finger hole on {hole.side.value} "
                    f"overlaps the magnet pocket in that wall: the pocket is cut "
                    f"inside the hole"
                )
    return messages


def warn_about_finger_cuts(spec: BoxSpec) -> None:
    """Emit :func:`finger_cut_conflicts` as warnings, and build anyway (FR-006c).

    A warning rather than an error: the merged cut is still a box, and a user
    who meant it (two holes side by side making one long grip) is not wrong —
    they just have to be told that is what they are getting.
    """
    import warnings

    for message in finger_cut_conflicts(spec):
        warnings.warn(f"{spec.label}: {message}", stacklevel=2)


def apply_finger_holes(body: Bosl2Solid, spec: BoxSpec) -> Bosl2Solid:
    """Cut any exterior finger holes out of a box body (FR-006).

    A hole on the outside of a box is the same cut as a compartment's wall
    scoop — a bore with a mouth flared into the rim and a fillet where it
    emerges on each face — so it goes through the same builder rather than a
    second implementation that could drift from it.

    Following the original (``no_lid.scad``), each hole hangs from the top of
    the **interior** rather than rising from the floor, and its height is
    capped at the interior depth so the cut cannot reach the box's base.

    Args:
        body: The box body to cut.
        spec: Reads `finger_holes` (a sequence of finger-hole builders), plus
              `width`, `length`, `height`, `wall_thickness`, `floor_thickness`.

    Returns:
        The body with every hole subtracted; unchanged when there are none.

    """
    holes = spec.finger_holes or ()
    if not holes:
        return body

    warn_about_finger_cuts(spec)

    from pyboxbuilder.compartments.finger_cuts import build_wall_scoop
    from pyboxbuilder.compartments.finger_outline import CutProfile
    from pyboxbuilder.compartments.finger_sweep import DEFAULT_FLOOR_DIP_MM, FaceTreatment

    wt = spec.wall_thickness
    ft = spec.floor_thickness
    inner_width = spec.width - 2 * wt
    inner_length = spec.length - 2 * wt

    # Align to the top of the *inside*, not the outer rim. On a lidded box the
    # lid (or its track) occupies the band above the interior, so a hole hung
    # from the rim starts inside solid material and reads as a nick in the top
    # edge rather than as a cut into the well. A type whose body is already
    # shortened for its lid — cap, slipover — says so with `interior_top`.

    for hole in holes:
        # Per side: the four walls need not end level, and a hole aligned to
        # the wrong one either floats above its wall or cuts into a lid feature.
        interior_top = spec.wall_top(hole.side)
        interior_height = interior_top - ft
        radius = getattr(hole, "radius", 14.0)
        # The cut's height follows the finger unless told otherwise, and never
        # reaches deeper than the interior.
        reach = min(getattr(hole, "depth", None) or radius, interior_height)
        # Wall standing above the cut turns it into a different shape: with no
        # surface for the mouth roll to roll onto, the cut is a closed window
        # instead of a scoop, filleted the whole way round (FR-065). The
        # window's top then needs the same allowance as its bottom, since the
        # fillet grows past both — hence `ends`.
        walled_over = interior_top < spec.height - 1e-9
        flare = _hole_flare(wt, hole, reach, ends=2 if walled_over else 1)
        # Both ends are set by the outline's height, not by shifting the solid:
        # the cut runs a flare past each end of its outline, so an outline this
        # much shorter puts the material removed exactly where the reach says
        # (FR-006b/T306). Shifting instead moves one end for the other — which
        # is how the mouth ended up finishing above the wall top.
        outline_height = reach - (2 * flare if walled_over else flare)
        # A grip is never wider than it is deep (FR-056). The angle its flank
        # arrives at the rim follows that aspect and nothing else — 45mm over
        # 9mm can only come in at 34°, where the same width at 19mm deep comes
        # in at 70° — so a shallow box gets a *smaller* grip rather than a
        # stretched one, and the shape stays the one the rest of the library
        # uses. Sizing the circles differently cannot fix it: a bigger base
        # flattens the flank, a smaller one flattens it further.
        throat = min(radius, outline_height)
        scoop = build_wall_scoop(
            inner_width,
            inner_length,
            outline_height,
            hole.side,
            radius=throat,
            wall_thickness=wt,
            profile=CutProfile(
                # None lets the mouth derive from the throat rather than
                # pinning 3mm, and lets the base grow as the cut shallows
                # (FR-054/a7). Naming a value here reads as the same thing
                # and is not: it counts as a *request*, which switches the
                # derived rule off — that is how every shallow tray went back
                # to a ramp either side without anything failing.
                mouth_flare=hole.mouth_flare,
                base_radius=hole.base_radius,
                roll_rise=hole.roll_rise,
            ),
            faces=FaceTreatment(
                # Pinned rather than derived, because the alignment above is
                # measured off this exact flare.
                fillet=flare,
                # A scoop's outline overshoots its rim, which is free on a
                # lidless box and must not be on any other; the window has no
                # overshoot to trim, and its top is already the plane below.
                top_limit=None,
                # There is wall below an exterior hole, not floor, so the face
                # flare can finish instead of being sliced off at the outline's
                # flat bottom — which is what leaves the wall's sawn
                # cross-section showing at the base of the cut (FR-076).
                # Compartment scoops keep the default clip: they bottom on the
                # floor, and there the flare has nowhere to go but through it.
                floor_clearance=flare + DEFAULT_FLOOR_DIP_MM,
            ),
            keep_flat_bottom=False,
            closed_top=walled_over,
        )
        offset = getattr(hole, "offset", 0.0) or 0.0
        along_x = hole.side in (ScoopSide.FRONT, ScoopSide.BACK)
        body = body - scoop.translate(
            [
                wt + (offset if along_x else 0.0),
                wt + (0.0 if along_x else offset),
                interior_top - outline_height - (flare if walled_over else 0.0),
            ]
        )

    return body


def no_lid_finger_holes(spec: BoxSpec) -> tuple[FingerHoleBuilder, ...]:
    """Return the finger holes a no-lid box cuts into its longer walls (FR-047).

    An open tray is lifted by the rim, so the original (`no_lid.scad`) puts a
    finger dip into each wall of the longer dimension. The sizing is a formula
    on the spec, not a constant:

    - throat radius = `min(20, min(length, width) / 4, height - floor_thickness + 1)`
      — a fingertip, capped at 20mm and at a quarter of the smaller *outer*
      footprint dimension;
    - reach = the radius, never past **half the box's height**, and **stopping
      5mm above the tray's floor**;
    - mouth flare = 3mm.

    The reach's last term is a structural rule, not arithmetic: the strip of
    wall under the cut is what the tray is lifted by, so the cut stops 5mm short
    of the floor. Written inline as `height - ft - 5` it reads like a fudge and
    the older form has twice been "corrected" back to `height - 2 + 1`, which
    runs the cut into the floor of a shallow tray. A tray with no room for the
    strip and a usable cut gets **no** holes (FR-047a) rather than a token dip
    taken out of the strip.

    A wall too short for the hole's mouth is skipped: a finger hole wider than
    the wall it is cut through breaks into the adjoining walls, so the tray goes
    out with **no** hole rather than a broken one. The mouth must leave a
    quarter of the wall uncut, not merely fit inside it — a cut running wall to
    wall is a slot, and what is left at each end is too little to grip
    (FR-047a). That is what keeps a path box with a short side sound.

    Args:
        spec: Needs `width`, `length`, `height`; reads `wall_thickness` and
            `floor_thickness`.

    Returns:
        A tuple of `FingerHoleBuilder`s — one per longer wall — or an empty
        tuple when the holes would not fit.

    """
    from pyboxbuilder.builders._base import FingerHoleBuilder

    wt = spec.wall_thickness
    ft = spec.floor_thickness
    width = spec.width
    length = spec.length
    height = spec.height

    radius = min(20.0, min(length, width) / 4.0, height - ft + 1.0)
    # The strip of wall the tray is picked up by: the cut stops this far above
    # the tray's floor, so what is left under it keeps the wall's own section.
    deepest = height - ft - MIN_WALL_BELOW_HOLE_MM
    # And never past half the box, whatever the floor leaves: a fingertip's
    # radius is 20mm and a tray is often 25mm tall, so the radius alone would
    # take four fifths of the wall and leave two posts with a bridge between.
    hole_height = min(radius, height * MAX_FINGER_HOLE_HEIGHT_SHARE, deepest)
    if hole_height < MIN_FINGER_HOLE_REACH_MM:
        # No room for both. The strip wins: a tray this short is liftable by
        # its walls, and a grip cut out of what holds it is not a grip.
        return ()
    rounding_radius = 3.0

    if length >= width:
        sides = (ScoopSide.LEFT, ScoopSide.RIGHT)
        span = length - 2 * wt
    else:
        sides = (ScoopSide.FRONT, ScoopSide.BACK)
        span = width - 2 * wt

    # The mouth is `radius + rounding_radius` wide on each side of centre, and
    # has to leave a quarter of the wall uncut — fitting is not enough, since a
    # cut running wall to wall is a slot with nothing left at either end to grip.
    if 2.0 * (radius + rounding_radius) > span * MAX_FINGER_HOLE_SPAN_SHARE:
        return ()

    return tuple(
        FingerHoleBuilder(
            side=side,
            width=radius * 2.0,
            depth=hole_height,
            mouth_flare=rounding_radius,
        )
        for side in sides
    )


def with_no_lid_finger_holes(spec: BoxSpec) -> BoxSpec:
    """Return a no-lid spec with its default finger holes, unless it already has some.

    Idempotent: an explicit ``finger_hole(side)`` call on the builder wins, and
    a second call to this changes nothing. A spec that sets
    ``auto_finger_holes`` to ``False`` opts out entirely (FR-047b).

    A **polygon** footprint gets none either (FR-047c). The rule names four
    walls and a longer side, and a polygon has neither — `no_lid_finger_holes`
    would read the bounding box and place a cut on a wall that need not exist.
    The test is the footprint rather than the box type, because that is what
    the rule is actually about; an explicit `finger_hole(side)` still works,
    since the caller can see the outline.

    Args:
        spec: The box's resolved description.

    Returns:
        The spec, or a copy carrying the automatic pair.

    """
    if spec.auto_finger_holes and not spec.finger_holes and not spec.path:
        return replace(spec, finger_holes=no_lid_finger_holes(spec))
    return spec


def interior_block(spec: BoxSpec) -> Bosl2Solid:
    """Return the solid that `build_shell` removes — the box's full interior volume.

    The void's **bottom edges are rounded**, which is what leaves a fillet
    inside the box: a void slightly smaller where it meets the floor means the
    wall rises from the floor on a curve rather than a right angle, so nothing
    snags and nothing has to be dug out of a square internal corner (FR-043).

    The void's vertical corners deliberately stay square. Rounding them too is
    tempting — it is one more `edges=` entry — but the resulting fillets run the
    **full height** of the box, including the band where a sliding lid seats,
    and they add material exactly where the plate needs to pass: measured, it
    put 0.59mm³ of body into the lid on all three sliding types, which is a lid
    that jams. The top likewise stays square: it is the opening.

    Args:
        spec: Needs `width`, `length`, `height`; reads `wall_thickness`,
            `floor_thickness` and `rounding`.

    Returns:
        The interior volume, positioned in the box frame.

    """
    from pybosl2 import Anchor, cuboid

    wt = spec.wall_thickness
    ft = spec.floor_thickness
    size = [spec.width - 2 * wt, spec.length - 2 * wt, spec.height - ft]

    radius = body_rounding(spec)
    if radius <= 0 or radius >= min(size) / 2:
        return block(size, at=(wt, wt, ft))

    return corner(
        cuboid(size, rounding=radius, edges=Anchor.BOTTOM, **precision_kwargs()),
        size,
        (wt, wt, ft),
    )


def round_inner_rim(body: Bosl2Solid, spec: BoxSpec) -> Bosl2Solid:
    """Round the **inner** top edge of a lidless box's rim (FR-043f).

    An open tray's rim is exposed on both faces — it is the edge a hand runs
    along when lifting the tray — so both of its edges carry the wall's fillet.
    The outer one comes free with `build_shell`'s envelope rounding; the inner
    one cannot come from there, and not for want of trying: `round_edges`
    subtracts the sliver between an envelope and its rounded twin, and for the
    *interior* envelope that sliver lands in the hollow rather than in the wall
    (T303, measured: the wall at the rim went 7.2mm³ → 7.17mm³, i.e. nothing).

    The inner rim is a convex edge **of the wall**, so what it takes is a
    fillet ring subtracted at the interior's top perimeter: the interior prism,
    flared outward by the radius over the last radius of its height, tangent to
    the inner face where the flare starts and to the top face where it ends.
    Everything below the flare is the interior itself, which is already void,
    so the ring only ever removes the rim's inner corner.

    Args:
        body: The hollowed box body.
        spec: Reads `rim_free` (a lidded box's rim is a sealing surface and
            keeps its square inner edge), `hollow`, `width`, `length`,
            `height`, `wall_thickness`, `floor_thickness` and `rounding`.

    Returns:
        The body with its inner rim rounded, or unchanged when the box is
        lidded, solid, or too small to carry the fillet.

    """
    from pybosl2.path2d import Path2D
    from pybosl2.shapes3d.base import CsgSolid

    from pyboxbuilder.rounding import rounding_facets, roundover_profile

    if not spec.rim_free or not spec.hollow:
        return body

    wt = spec.wall_thickness
    ft = spec.floor_thickness
    inner_width = spec.width - 2 * wt
    inner_length = spec.length - 2 * wt
    interior_height = spec.height - ft
    # Half the wall is all a rim can give up on this side and still be a rim:
    # the outer edge is taking the same fillet from the other side (FR-043f).
    radius = min(body_rounding(spec), wt / 2)
    if radius <= 0 or min(inner_width, inner_length) <= 0:
        return body
    if interior_height <= radius:
        return body

    steps = max(8, rounding_facets()["fn"] // 4)
    # The widened perimeter: the sweep's flared end is the path itself, and the
    # roundover brings it back to the interior a radius along (that is the
    # profile's convention — see `roundover_profile`).
    rect = [
        [wt - radius, wt - radius],
        [wt + inner_width + radius, wt - radius],
        [wt + inner_width + radius, wt + inner_length + radius],
        [wt - radius, wt + inner_length + radius],
    ]
    # Swept mouth-down and flipped, because the flare has to be the sweep's
    # *first* rim: `offset_sweep` carries the last offset a rim reached along
    # its straight middle, so a flare asked for at the far end leaves the whole
    # run at the widened size — a radius of wall gone from top to bottom.
    swept = Path2D(rect, closed=True).offset_sweep(
        height=2 * radius, bottom=roundover_profile(radius, steps), steps=steps
    )
    # Only the flare itself is wanted. What follows it is a prism of the plain
    # interior — which is already void, so it removes nothing — carrying the
    # sweep's far end, where a zero-height flange back out to the widened path
    # would otherwise be left inside the wall.
    keep = block(
        [spec.width + 4 * radius, spec.length + 4 * radius, radius + 1.0],
        at=(-2 * radius, -2 * radius, -1.0),
    )
    ring = (CsgSolid(swept.polyhedron()) & keep).mirror([0, 0, 1])
    return body - ring.translate([0.0, 0.0, spec.height])
