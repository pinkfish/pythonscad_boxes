# SPDX-License-Identifier: Apache-2.0
"""The finger cuts themselves — three shapes, and the one thing that chooses.

Ported from the original toolkit's ``FingerHoleWall`` and ``FingerHoleBase``
(``components.scad``), which are the reference for how a finger cut is meant to
be smoothed. A request for a finger cut becomes one of three solids:

* a **wall scoop** — a dip notched into the top of a wall, for a well deep
  enough that a finger can hook into it;
* a **floor scoop** — a bowl in the well's own floor, for a tray too shallow
  for a notch to be a notch;
* a **through hole** — a bore straight through the box's base at the wall, for
  a well holding a stack, which fills its well and leaves no side to reach down.

Which one you get turns on two questions — the kind asked for, and whether the
well is deep enough — and :func:`build_cut` answers both. It is the only place
either question is answered; when they were split across two modules, a caller
could satisfy one rule and miss the other, and the card boxes shipped with
scoops for a release (T327, T341).

Every builder here returns a cutout in the compartment's own frame: (0, 0, 0)
is the compartment's lower-left corner at its floor, the footprint runs out to
(comp_width, comp_length), and +Z is up towards the rim.

Three separate roundings are at work, and they are easy to conflate:

1. **The mouth** (``mouth_flare``) — the top of the profile flares outward into
   the compartment rim, so the opening curves into the wall instead of ending
   in a right-angle lip. This is the part a fingertip actually rides over. It
   belongs to the outline; see :mod:`.finger_outline`.
2. **The faces** (``FaceTreatment.fillet``) — where the cut emerges on each
   side of the wall it flows onto that face tangentially rather than leaving a
   sharp shadow line. It belongs to the sweep; see :mod:`.finger_sweep`.
3. **The base** — a floor scoop additionally fillets the cut into the floor
   plane, so the bottom blends into the box's inside surface.
"""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from pyboxbuilder.compartments.finger_outline import (
    ARC_SAMPLES,
    BASE_ARC_SHARE,
    DEFAULT_BOTTOM_ROUNDING_RATIO,
    DEFAULT_MOUTH_ROUNDING_MM,
    DEFAULT_TOP_ROUNDING_RATIO,
    MIN_FLAT_BOTTOM_RATIO,
    RIM_OVERSHOOT_MM,
    TOP_ROLL_RISE_RATIO,
    TOUCHING_TOLERANCE_MM,
    CutProfile,
    _fit_radii,
    _quarter_arc,
    dish_radius,
    floor_bore_outline,
    floor_bore_profile,
    scoop_outline,
    scoop_profile,
    window_outline,
)
from pyboxbuilder.compartments.finger_sweep import (
    _SIDE_CENTRES,
    _SIDE_SPIN,
    DEFAULT_EDGE_ROUNDING_MM,
    DEFAULT_FLOOR_DIP_MM,
    FaceTreatment,
    _sweep_through_wall,
    scoop_face_flare,
)
from pyboxbuilder.enums import ScoopSide
from pyboxbuilder.precision import kwargs as precision_kwargs
from pyboxbuilder.rounding import rounding_facets

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid

    from pyboxbuilder.enums import FingerCut


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
__all__ = [
    "ARC_SAMPLES",
    "BASE_ARC_SHARE",
    "DEFAULT_BOTTOM_ROUNDING_RATIO",
    "DEFAULT_EDGE_ROUNDING_MM",
    "DEFAULT_FLOOR_DIP_MM",
    "DEFAULT_MOUTH_ROUNDING_MM",
    "DEFAULT_TOP_ROUNDING_RATIO",
    "MIN_FLAT_BOTTOM_RATIO",
    "RIM_OVERSHOOT_MM",
    "TOP_ROLL_RISE_RATIO",
    "TOUCHING_TOLERANCE_MM",
    "_SIDE_CENTRES",
    "_SIDE_SPIN",
    "CutProfile",
    "FaceTreatment",
    "_fit_radii",
    "_quarter_arc",
    "_sweep_through_wall",
    "build_cut",
    "build_floor_scoop",
    "build_scoop",
    "build_through_hole",
    "build_wall_scoop",
    "dish_radius",
    "floor_bore_outline",
    "floor_bore_profile",
    "scoop_face_flare",
    "scoop_outline",
    "scoop_profile",
    "window_outline",
]
"""Re-exported so a caller has one import for the whole finger-cut vocabulary
(FR-006a), rather than having to know which of three modules a name lives in."""


def build_wall_scoop(
    comp_width: float,
    comp_length: float,
    comp_depth: float,
    side: ScoopSide,
    radius: float = 12.0,
    wall_thickness: float = 2.0,
    *,
    profile: CutProfile | None = None,
    faces: FaceTreatment | None = None,
    floor_thickness: float | None = None,
    closed_top: bool = False,
    keep_flat_bottom: bool = True,
) -> Bosl2Solid:
    """Build a finger notch through a compartment wall.

    The **edge** profile from :func:`~pyboxbuilder.compartments.finger_outline.scoop_profile` — flat bottom, straight
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
        profile: The cut's edge profile — a ``CutProfile`` holding shape
            settings (mouth flare, base radius, roll rise).
        faces: The cut's face treatment — a ``FaceTreatment`` holding face
            settings (fillet, which faces round, floor clip, breach floor, top limit).
        floor_thickness: The box floor under this compartment. Used to size the
            dip below the well floor (half the floor, at most 1mm), which is
            what keeps the cut's bottom face off the floor plane.
        closed_top: Build a **closed window** (:func:`~pyboxbuilder.compartments.finger_outline.window_outline`) instead
            of a top-opening scoop. For a cut with wall standing above it,
            where there is no surface for the mouth roll to roll onto and a
            trimmed-off scoop would meet the faces at a square edge
            (FR-065).
        keep_flat_bottom: Keep part of the base flat by capping the corner
            radius (FR-050) — for a well something rests in. A grip passes
            ``False`` and gets the radius it asked for, with a round base
            (FR-054).

    Returns:
        Bosl2Solid cutout, positioned in the compartment frame.

    Raises:
        ValueError: If the compartment or wall dimensions are not positive.

    """
    if profile is None:
        profile = CutProfile()
    if faces is None:
        faces = FaceTreatment()
    if comp_depth <= 0:
        raise ValueError(f"comp_depth must be > 0; got {comp_depth}")
    # The records carry the shape and the faces; `radius` stays a parameter
    # because it is the one dimension every caller states, and a profile that
    # names a width wins over it.
    if profile.half_width is not None:
        radius = profile.half_width
    rounding_radius = profile.mouth_flare
    bottom_rounding = profile.base_radius
    roll_rise = profile.roll_rise
    rounding_edge = faces.fillet
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
        floor_thickness=floor_thickness,
        span=span,
        radius=radius,
        faces=replace(faces, fillet=rounding_edge),
    )
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
) -> Bosl2Solid:
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
        floor_thickness: The box floor under the compartment, sizing how far
            the bore may dip below the well floor.

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
        floor_thickness=floor_thickness,
        span=span,
        radius=min(radius, span / 2),
        faces=FaceTreatment(fillet=rounding_edge),
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
def build_cut(
    kind: FingerCut,
    comp_width: float,
    comp_length: float,
    comp_depth: float,
    side: ScoopSide,
    *,
    radius: float = 12.0,
    wall_thickness: float = 2.0,
    floor_thickness: float | None = None,
    profile: CutProfile | None = None,
    faces: FaceTreatment | None = None,
) -> Bosl2Solid:
    """Build whichever finger cut this compartment wants — the only chooser.

    Three shapes can come out of a request for a finger cut, and which one it
    is turns on two questions:

    1. **What kind was asked for** — `THROUGH_FLOOR` goes through the base for
       a stack, `SCOOP` dips the side for loose pieces (FR-060);
    2. **How deep the well is** — a scoop in a well shallower than
       `MIN_WALL_SCOOP_DEPTH_MM` becomes the floor-blended bore instead, because
       a notch in a 5mm wall gives a finger nothing to bite on.

    Both questions are answered *here* and nowhere else. They used to be split
    — the kind decided in `carve.py`, the depth decided in `build_scoop` — which
    is how a caller could reach the wall builder having satisfied one rule and
    not the other, and why the card boxes spent a release getting scoops.

    Args:
        kind: Through the floor, or a dip in the side.
        comp_width: Compartment footprint width.
        comp_length: Compartment footprint length.
        comp_depth: Compartment depth; decides scoop against floor bore.
        side: Which wall or edge the cut sits on.
        radius: Throat half-width; `profile.width` overrides it when given.
        wall_thickness: Wall the cut passes through.
        floor_thickness: The box's base under the well.
        profile: The outline's four numbers (FR-051); `None` fields derive.
        faces: How the cut is treated where it emerges.

    Returns:
        Bosl2Solid cutout, positioned in the compartment frame.

    """
    from pyboxbuilder.enums import FingerCut

    if profile is None:
        profile = CutProfile()
    if faces is None:
        faces = FaceTreatment()
    if profile.half_width is not None:
        radius = profile.half_width
    if kind is FingerCut.THROUGH_FLOOR:
        return build_through_hole(
            comp_width, comp_length, side,
            radius=radius,
            comp_depth=comp_depth,
            wall_thickness=wall_thickness,
            floor_thickness=floor_thickness if floor_thickness else 2.0,
            mouth_flare=profile.mouth_flare,
            rounding_edge=faces.fillet,
        )
    if comp_depth >= MIN_WALL_SCOOP_DEPTH_MM:
        return build_wall_scoop(
            comp_width, comp_length, comp_depth, side,
            radius=radius, wall_thickness=wall_thickness,
            profile=profile,
            faces=faces,
            floor_thickness=floor_thickness,
        )
    return build_floor_scoop(
        comp_width, comp_length, side,
        radius=radius, comp_depth=comp_depth, wall_thickness=wall_thickness,
        rounding_radius=profile.mouth_flare, rounding_edge=faces.fillet,
        floor_thickness=floor_thickness,
    )
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
) -> Bosl2Solid:
    """Return a side scoop, wall or floor-blended by depth — `build_cut`'s SCOOP arm.

    Kept as its own name because "give me a scoop" reads better at a call site
    than "give me a cut of kind SCOOP", but it decides nothing: the two rules
    live in :func:`build_cut`.
    """
    from pyboxbuilder.enums import FingerCut

    return build_cut(
        FingerCut.SCOOP,
        comp_width, comp_length, comp_depth, side,
        radius=radius, wall_thickness=wall_thickness,
        floor_thickness=floor_thickness,
        profile=CutProfile(mouth_flare=rounding_radius),
        faces=FaceTreatment(fillet=rounding_edge),
    )
def build_through_hole(
    comp_width: float,
    comp_length: float,
    side: ScoopSide,
    radius: float = 17.0,
    comp_depth: float = 20.0,
    wall_thickness: float = 2.0,
    floor_thickness: float = 2.0,
    mouth_flare: float | None = None,
    rounding_edge: float | None = None,
) -> Bosl2Solid:
    """Return a finger hole cut **through the floor**, for a well holding a stack.

    A scoop puts a finger down the *side* of what a well holds. A card stack
    fills its well, so there is no side to reach down — what lifts it is a thumb
    from underneath, which means the cut has to go through the box's base
    (FR-060). Every card box in the original toolkit does this: `FingerHoleBase`
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
    # around the hole's underside. The hole meets the base flat (FR-060).
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
    # the same fillet the scoops use (FR-073).
    #
    # Its **top corners roll into the wall's rim** rather than meeting it
    # square (FR-060) — the original flares them by `rounding_radius` and
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

    slot = _sweep_through_wall(
        outline,
        comp_width,
        comp_length,
        side,
        comp_depth=comp_depth,
        wall_thickness=wall_thickness,
        rounding_radius=0.0,
        span=span,
        radius=radius,
        # Only the box's **outside** is rolled — the inside is what the stack
        # rests against, and a fillet there is a gap the bottom card slides
        # into rather than anything a hand touches. It is still swept with
        # *both* rims and run a fillet further into the compartment: that puts
        # the inner rim's whole transition in the well, which is void, so what
        # the wall gets is one constant section, square at its inner face and
        # rolled at its outer one. Asking for a single rim instead leaves the
        # middle at the path's full width with the other rim stepping in from
        # it — a ridge inside the hole a fillet's depth from the outer face.
        faces=FaceTreatment(
            fillet=rounding_edge,
            round_inner=True,
            round_outer=True,
            inner_overshoot=rounding_edge,
            breach_floor=True,
        ),
    )

    # The overshoot is there to move the inner rim's transition out of the
    # wall, and it must not reach the **base**: below the well's floor it would
    # take a rounded bite out of the floor *inside* the well, right across the
    # cut's width — measured, 2mm in from the wall over the full 33mm. Below
    # the floor the slot is the wall's own thickness and nothing more; the bore
    # is what opens the base, and it is unioned after this.
    reach = rounding_edge * 2 + 0.1
    strip = {
        ScoopSide.FRONT: (comp_width, reach, 0.0, reach / 2),
        ScoopSide.BACK: (comp_width, reach, 0.0, comp_length - reach / 2),
        ScoopSide.LEFT: (reach, comp_length, reach / 2, 0.0),
        ScoopSide.RIGHT: (reach, comp_length, comp_width - reach / 2, 0.0),
    }[side]
    sunk = below + rounding_edge + 2.0
    slot = slot - cuboid(
        [max(strip[0], 1.0) * 2, max(strip[1], 1.0) * 2, sunk]
    ).translate([strip[2] or comp_width / 2, strip[3] or comp_length / 2, -sunk / 2])

    x, y = _SIDE_CENTRES[side](comp_width, comp_length)
    return slot | bore.translate([x, y, 0.0])
