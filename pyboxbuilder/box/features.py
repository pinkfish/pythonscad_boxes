# SPDX-License-Identifier: Apache-2.0
"""Reusable closure features shared by the box types (T162).

A lid only works if the body has the matching half of the same feature — a
rabbet needs a ledge cut for it, a sliding lid needs grooves the right depth,
a filament hinge needs knuckles that interleave and share a pin axis. Keeping
both halves of each feature in one function is what stops them drifting apart.

Everything is built in the box's own frame: (0, 0, 0) is its lower-left corner
at the bed. pybosl2 primitives are centre-anchored, so placement goes through
`shell.block` / `shell.corner`.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.enums import CatchType, PatternType, StackableShape
from pyboxbuilder.precision import kwargs as precision_kwargs

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid

FIT_SLACK_MM = 0.2
"""Clearance between a lid and the feature it seats into, per side."""

PRINT_IN_PLACE_GAP_MM = 0.4
"""Gap between two parts printed as one piece, so they separate."""

_COINCIDENT_EPS_MM = 0.02
"""How far a cutting solid is backed off a face it would otherwise touch exactly.

Coincident surfaces are the one case CSG cannot decide: the difference keeps a
zero-width sliver and the face survives, so a cut that is geometrically correct
measures as if it never ran.
"""

WIGGLE_MM = 0.2
"""Clearance between two printed parts that have to come apart again.

`m_piece_wiggle_room` in the original toolkit, and used the same way here.
"""


# --------------------------------------------------------- declared size

# A box's declared size is the outside of the CLOSED box -- lid on. That is the
# size the packer reserves space for, so a lid that adds to any dimension makes
# every layout wrong: it is not the box that was planned for. Both closures
# below therefore shrink the body to make room for the lid, rather than hanging
# the lid off the outside of a full-size body.


@dataclass(frozen=True)
class CapMetrics:
    """The numbers a cap box's body and lid must agree on.

    Derived once so the two halves cannot drift apart: the body's stepped-in top
    band is exactly what the lid's skirt wraps, and the lid's outer face is
    exactly the box's declared footprint.
    """

    body_height: float
    """Top of the body. The lid's plate sits above it, coming to `height`."""
    cap_height: float
    """How far the lid's skirt reaches down the outside of the body."""
    band_z: float
    """Where the body steps in to make room for that skirt."""
    band_width: float
    band_length: float
    inset: float
    """How far the band is set in from the declared footprint, per side."""


def cap_metrics(spec: BoxSpec) -> CapMetrics:
    """Work out a cap box's shared geometry from its declared size."""
    wt = spec.wall_thickness
    lt = spec.lid_thickness
    wiggle = spec.size_spacing
    # The original's CapBoxDefaultCapHeight / CapBoxDefaultLidWallThickness,
    # then capped so the corner finger cutout below it still has somewhere to
    # go. Half the height is a fine skirt on a tall box and swallows a short one
    # whole: at 11mm it would take 5.5, leaving 5.5 for a cut that needs 4 and a
    # 2mm foot. The floor is the lid plate plus the shortest usable skirt, so
    # the smallest cap box is exactly `lid + 3 + 4 + 2` (FR-002n).
    cap_h = spec.cap_height
    if cap_h is None:
        room = spec.height - CAP_FINGER_CURVE_TOTAL_MM - CAP_FINGER_FOOT_MM
        cap_h = min(
            min(10.0, spec.height / 2),
            max(lt + CAP_FINGER_MIN_SKIRT_MM, room),
        )
    lid_wall = wt / 2

    inset = lid_wall + 0.75 * wiggle
    return CapMetrics(
        body_height=spec.height - lt - wiggle,
        cap_height=cap_h,
        band_z=spec.height - cap_h,
        band_width=spec.width - 2 * inset,
        band_length=spec.length - 2 * inset,
        inset=inset,
    )


CAP_FINGER_MIN_RADIUS_MM = 2.0
"""Smallest either profile radius may be on a cap box's corner cutout (FR-002k).

The **pair** is the budget: 2mm rolling in at the top and 2mm rolling out at the
bottom, :data:`CAP_FINGER_CURVE_TOTAL_MM` between them.
"""

CAP_FINGER_CURVE_TOTAL_MM = 2 * CAP_FINGER_MIN_RADIUS_MM
"""Height the two rolls need between them, with no straight run at all (FR-002k).

This is what sets the smallest cap box that can be built: a lid thickness, this,
and a foot. Sized as a total rather than per-radius because it is the total that
competes with the box's height — a 4mm budget fits boxes an 8mm one refuses.
"""

CAP_FINGER_CURVE_MAX_MM = 6.0
"""Height the two rolls take when the box can spare it (FR-002k).

4mm is the floor, not the target. Where there is room the pair opens out to 6mm
— a 3mm roll each — which is a noticeably gentler curve for a fingertip. Growing
it rather than fixing it is the point: the same cutout suits a 12mm box and a
60mm one only if it can breathe on the taller one.
"""

CAP_FINGER_FOOT_MM = 2.0
"""Full-thickness body left below the cutout (FR-002l).

The cut is a recess in the side, not a through-slot; the corner it is cut into
is the corner the box is stacked and dropped on.
"""

CAP_FINGER_MIN_SKIRT_MM = 3.0
"""Shortest skirt a cap lid may have when the body is cut for finger holds.

The skirt has to grip *something* at the corner being pushed at. Below 3mm there
is not enough of it to hold the lid square, and the lid rocks off that corner
rather than lifting.
"""

CAP_FINGER_MIN_LENGTH_MM = 10.0
"""Shortest run along each side — a fingertip's width (FR-002m)."""

CAP_FINGER_MAX_LENGTH_SHARE = 1 / 6
"""Longest run along each side, as a share of it (FR-002m).

Two cutouts per side then leave two thirds of the band for the skirt to grip.
"""

CAP_FINGER_MIN_BAND_MM = 10.0
"""Uncut band that must survive between the two cutouts on a side (FR-002m1).

The two runs are what a finger needs; this is what the *lid* needs. Let the
cutouts meet in the middle and the side is one continuous slot, with the skirt
gripping nothing along that whole face — which the height check (FR-002n) does
not catch, because a small box can be tall.
"""


@dataclass(frozen=True)
class CapFingerMetrics:
    """The numbers a cap box's four corner cutouts are cut from."""

    length_x: float
    """How far each cutout runs along the width."""
    length_y: float
    """How far each cutout runs along the length."""
    height: float
    """How far down from the skirt the cut reaches."""
    radius: float
    """Both profile radii — the first and second roll."""
    base_z: float
    """Where the cut bottoms out. A foot of body survives below it."""


def cap_finger_metrics(spec: BoxSpec) -> CapFingerMetrics:
    """Size a cap box's corner finger cutouts, or explain why it cannot have any.

    Args:
        spec: Needs `width`, `length`, `height`; reads `floor_thickness` and
            optionally `cap_finger_length`, `cap_finger_height` and
            `cap_finger_radius`.

    Returns:
        The cutout geometry (FR-002i–FR-002m).

    Raises:
        ValueError: If the box cannot stack a lid, a 3mm skirt, both rolls and
            the foot (FR-002n) — the smallest cap box is
            ``lid + 3 + 4 + 2``. A cap box built without the cutouts has no way
            to be opened, so this refuses rather than shrinking them.

    """
    m = cap_metrics(spec)
    lt = spec.lid_thickness

    # The cut hangs below the skirt, so what it has to spend is everything from
    # there down to the foot.
    available = m.band_z - CAP_FINGER_FOOT_MM

    explicit = spec.cap_finger_radius
    if explicit is None:
        # 4mm is the floor, not the target: where the box can spare the height
        # the pair opens out to 6mm, which is a gentler curve under a fingertip.
        curves = min(
            CAP_FINGER_CURVE_MAX_MM, max(CAP_FINGER_CURVE_TOTAL_MM, available)
        )
        radius = curves / 2
    else:
        radius = max(explicit, CAP_FINGER_MIN_RADIUS_MM)
        curves = 2 * radius

    # Read down the box: the lid plate, then the skirt it grips by, then the two
    # rolls at their *floor* size, then the foot. That stack is the smallest cap
    # box there can be — growing the curve never raises the minimum.
    minimum = (
        lt + CAP_FINGER_MIN_SKIRT_MM + CAP_FINGER_CURVE_TOTAL_MM
        + CAP_FINGER_FOOT_MM
    )
    if m.cap_height - lt < CAP_FINGER_MIN_SKIRT_MM or available < curves - 1e-9:
        raise ValueError(
            f"cap box {spec.label!r} is {spec.height:.1f}mm tall "
            f"and cannot carry a corner finger cutout: it needs at least "
            f"{minimum:.1f}mm — a {lt:.1f}mm lid, a "
            f"{CAP_FINGER_MIN_SKIRT_MM:.1f}mm skirt, {curves:.1f}mm of curve "
            f"(two {radius:.1f}mm rolls) and a {CAP_FINGER_FOOT_MM:.1f}mm foot "
            f"— and has a {m.cap_height:.1f}mm skirt with {available:.1f}mm "
            f"below it. Use a slipover box at this size: its corner notches "
            f"open a shallow box that a cap lid cannot."
        )

    def _run(dimension: float) -> float:
        # A sixth of the side, but never less than a fingertip: 10mm is what a
        # finger needs, a sixth is what the skirt would prefer.
        return max(
            CAP_FINGER_MIN_LENGTH_MM, dimension * CAP_FINGER_MAX_LENGTH_SHARE
        )

    override = spec.cap_finger_length
    length_x = override if override is not None else _run(spec.width)
    length_y = override if override is not None else _run(spec.length)

    # A footprint too small for the cuts is refused exactly as a too-short box
    # is (FR-002m1). Two cutouts meet at each corner of every side, so a side
    # spends twice its run plus the band between them; let them meet and the
    # corner cuts merge into one slot down the whole face, and the skirt loses
    # its bearing there. The height check alone passes a 30 x 30mm box and
    # produces precisely that.
    for axis, side, run in (("width", spec.width, length_x),
                            ("length", spec.length, length_y)):
        needed = 2 * run + CAP_FINGER_MIN_BAND_MM
        if side < needed - 1e-9:
            raise ValueError(
                f"cap box {spec.label!r} is {side:.1f}mm across its "
                f"{axis} and cannot carry corner finger cutouts: two "
                f"{run:.1f}mm cutouts and the {CAP_FINGER_MIN_BAND_MM:.1f}mm "
                f"band between them need {needed:.1f}mm. Widen the box, set a "
                f"shorter `cap_finger_length`, or use a slipover box, whose "
                f"notches take two corners rather than four."
            )

    height = spec.cap_finger_height
    if height is None:
        height = curves
    height = min(max(height, curves), available)

    return CapFingerMetrics(
        length_x=length_x,
        length_y=length_y,
        height=height,
        radius=radius,
        base_z=m.band_z - height,
    )


def cap_finger_cutouts(spec: BoxSpec) -> Bosl2Solid:
    """Return the four corner cutouts that let a cap lid be pushed off (FR-002i).

    Two wall scoops meeting at each corner — the same :func:`corner_catch` a
    slipover sleeve uses, and the original toolkit's ``CornerCatch`` before
    that — so the cut arrives with the roll and the fillets already right.

    Corners rather than side-centres: a finger pushing up in a corner recess
    loads the skirt along **both** adjoining faces at once, so the lid lifts
    square instead of cocking, and the bearing stays in the middle of each wall
    where there is material behind it.

    Args:
        spec: As :func:`cap_finger_metrics`.

    Returns:
        The solid to subtract from the body.

    Raises:
        ValueError: Via :func:`cap_finger_metrics`, when the box is too short.

    """
    from pyboxbuilder.compartments.element import union_all

    m = cap_metrics(spec)
    f = cap_finger_metrics(spec)
    width, length = spec.width, spec.length

    parts = []
    for at, towards, run in (
        ((0.0, 0.0), (1, 1), (f.length_x, f.length_y)),
        ((width, 0.0), (-1, 1), (f.length_x, f.length_y)),
        ((0.0, length), (1, -1), (f.length_x, f.length_y)),
        ((width, length), (-1, -1), (f.length_x, f.length_y)),
    ):
        # `corner_catch` takes one half-width for both arms, so the shorter run
        # governs: a cutout that overran its own side would eat into the next
        # corner's.
        # The indent is exactly as deep as the lid's own offset — the step the
        # band above it is already set in by — so the recess and the skirt sit
        # in the same plane and the finger meets one continuous surface.
        parts.append(
            corner_catch(
                at, towards,
                radius=min(run),
                height=f.height,
                wall_thickness=m.inset,
                rounding_edge=m.inset / 2,
                top_rounding=f.radius,
                bottom_rounding=f.radius,
            ).translate([0.0, 0.0, f.base_z])
        )
    cutouts = union_all(parts)
    assert cutouts is not None, "four corners always produce a solid"
    return cutouts


def cap_body(spec: BoxSpec) -> Bosl2Solid:
    """Return a cap box's body: full footprint below, stepped in for the skirt above."""
    from pyboxbuilder.box.shell import block, build_shell

    m = cap_metrics(spec)
    # `interior_top`: the body is already shortened for the cap, so its own top
    # is the top of the inside — subtracting a lid thickness again would push
    # every finger hole a lid deeper than it belongs.
    shell = build_shell(
        replace(spec, height=m.body_height, interior_top=m.body_height)
    )
    if m.band_z >= m.body_height:
        return shell  # the cap is taller than the body; nothing to step in

    # Keep everything below the band at full size, and only the band above it.
    # The band is what the skirt grips, so its corners take the smaller mating
    # radius — matched by the lid's cavity in `cap_lid` — while everything below
    # it keeps the body's own outer rounding.
    from pyboxbuilder.rounding import mating_rounding, rounded_block, vertical_edges

    keep = block([spec.width, spec.length, m.band_z]) | rounded_block(
        [m.band_width, m.band_length, m.body_height - m.band_z],
        mating_rounding(spec),
        vertical_edges(),
        at=(m.inset, m.inset, m.band_z),
    )
    body = shell & keep
    # Somewhere to push the lid off from. Without this a cap box is a smooth
    # friction fit with no purchase but the seam (FR-002i).
    if spec.cap_finger_cutouts:
        body = body - cap_finger_cutouts(spec)
    return body


def cap_lid(spec: BoxSpec) -> Bosl2Solid:
    """Return a cap box's lid: a plate whose skirt grips the body's stepped-in band.

    Its outer face is the declared footprint and its top is the declared height,
    so a closed cap box measures exactly what it was asked for.
    """
    from pyboxbuilder.box.shell import block

    m = cap_metrics(spec)
    lt = spec.lid_thickness
    slack = spec.cap_slack

    from pyboxbuilder.rounding import mating_rounding, rounded_block, vertical_edges

    outer = block(
        [spec.width, spec.length, m.cap_height], at=(0.0, 0.0, m.band_z)
    )
    # The cavity's corners are rounded to the same radius as the band they slide
    # over, so the two nest instead of meeting at a gap.
    cavity = rounded_block(
        [m.band_width + 2 * slack, m.band_length + 2 * slack, m.cap_height - lt],
        mating_rounding(spec),
        vertical_edges(),
        at=(m.inset - slack, m.inset - slack, m.band_z),
    )
    return outer - cavity


SLIPOVER_SLEEVE_WALL_SHARE = 0.5
"""How thick the sleeve's wall is, as a share of the box's wall (FR-002o).

A **half** wall. The sleeve is a skin over a box that already has a full wall
behind it everywhere the sleeve touches, so a full-thickness sleeve is a second
wall carrying nothing — it costs the interior two full walls of width across
every axis, and prints a part twice as heavy as the job needs. The same
reasoning the cap box's skirt already uses.
"""


DEFAULT_SLIPOVER_FOOT_MM = 2.0
"""Default height of the exposed base/foot below a slipover sleeve (FR-002p)."""


SLIPOVER_GAP_MIN_MM = 0.0
"""Least body a slipover sleeve leaves showing above the foot (FR-002p)."""

SLIPOVER_GAP_MAX_MM = 0.0
"""Most body a slipover sleeve leaves showing above the foot (FR-002p)."""


def slipover_gap(spec: BoxSpec) -> float:
    """How much body a sleeve leaves exposed above the foot (FR-002p).

    By default the sleeve reaches all the way down to the foot (``0.0``),
    relying on the corner finger notches for grip unless ``slipover_gap``
    is explicitly set on the spec.

    Args:
        spec: Needs `height`; reads `foot` and `slipover_gap`.

    Returns:
        The gap in mm (defaults to ``0.0``).

    """
    explicit = spec.slipover_gap
    if explicit is not None:
        return max(0.0, float(explicit))
    return 0.0


def slipover_metrics(spec: BoxSpec) -> tuple[float, float]:
    """(inset per side, body height) for a slipover box.

    The sleeve's outer face is the declared footprint, so the body is set in by
    the sleeve's own wall thickness all round — **half** the box's wall
    (FR-002o) — and stops a lid thickness short.

    Args:
        spec: Needs `height`; reads `wall_thickness`, `lid_thickness` and
            `size_spacing`.

    Returns:
        ``(inset per side, body height)``.

    """
    wt = spec.wall_thickness
    lt = spec.lid_thickness
    wiggle = spec.size_spacing
    return wt * SLIPOVER_SLEEVE_WALL_SHARE + wiggle, spec.height - lt - wiggle


@dataclass(frozen=True)
class Closure:
    """The two halves of a closure feature.

    `body` is cut from or added to the box; `lid` likewise for the lid. Which
    of the two applies is the caller's business — a rabbet subtracts its body
    half and adds its lid half, a knuckle adds both.
    """

    body: Bosl2Solid | None = None
    lid: Bosl2Solid | None = None
    body_cut: Bosl2Solid | None = None
    """Volume the **body** must give up for the lid's half to move."""
    lid_cut: Bosl2Solid | None = None
    """Volume the **lid** must give up for the body's half.

    Both directions are needed once a hinge sits inside the box: each half's
    knuckles then stand in space the other half would otherwise fill. Relieving
    only one side leaves the two fused just as surely as relieving neither.
    """
    pin: Bosl2Solid | None = None

    def require_lid(self) -> Bosl2Solid:
        """Return the lid half, for a closure that is required to have one.

        Returns:
            The lid solid.

        Raises:
            ValueError: If this closure produced no lid half. A caller
                unioning two lid halves has no sensible answer without both,
                and `None | solid` fails with a message about operand types
                rather than about the geometry.

        """
        if self.lid is None:
            raise ValueError("this closure has no lid half to union")
        return self.lid


# ------------------------------------------------------------------- rabbet


def rabbet(spec: BoxSpec, inset: float = 1.0) -> Closure:
    """Return a ledge cut into the top rim, and the plate that drops into it.

    The lid finishes flush with the rim rather than sitting on top of it, which
    is what makes an inset box stackable.

    Args:
        spec: Box dimensions; reads `wall_thickness` and `lid_thickness`.
        inset: How far the ledge reaches in past the wall's inner face, so the
            lid has something to rest on rather than falling through.

    """
    from pyboxbuilder.box.shell import block

    wt = spec.wall_thickness
    lt = spec.lid_thickness
    ledge = max(wt - inset, 0.0)

    recess_w = spec.width - 2 * ledge
    recess_l = spec.length - 2 * ledge
    top = spec.height - lt

    return Closure(
        body=block([recess_w, recess_l, lt + 0.1], at=(ledge, ledge, top)),
        lid=block(
            [recess_w - 2 * FIT_SLACK_MM, recess_l - 2 * FIT_SLACK_MM, lt],
            at=(ledge + FIT_SLACK_MM, ledge + FIT_SLACK_MM, top),
        ),
    )


# ------------------------------------------------------------ sliding track


def sliding_dovetail(spec: BoxSpec) -> tuple[float, float]:
    """Return the dovetail depths that hold a sliding lid in its grooves.

    The lid's two long edges are angled — a dovetail — so the lid is trapped in
    its grooves. In cross-section, perpendicular to the slide axis, the lid is a
    trapezoid whose **top** face is the box interior (no key — the top sits
    flush with the inner walls) and whose **bottom** face reaches **half** the
    wall width into each wall. The groove never reaches the outer face, so
    there is always wall material behind it to support the lid (FR-002c).

    Args:
        spec: Reads `wall_thickness`.

    Returns:
        ``(top, bottom)`` — how far the key reaches into each side wall at the
        lid's top face and at its underside, in mm. The top is ``0`` (the lid's
        top face is the interior width); the bottom is half the wall width.

    """
    wt = spec.wall_thickness
    return 0.0, wt / 2


def lead_chamfer_size(spec: BoxSpec) -> float:
    """Return the slight chamfer that lets a lid start into its grooves (FR-002d).

    A **quarter** of the lid's thickness. It was half, which on a 2mm lid takes
    the leading end down to a 1mm knife edge — enough of a taper to read as a
    wedge, which is the shape a sliding lid should not have anywhere. A quarter
    still keeps the lip off the groove floor while the leading face stays
    recognisably a face.

    Args:
        spec: Reads `lid_thickness`; an explicit `lead_chamfer` wins.

    Returns:
        The chamfer depth in mm.

    """
    if spec.lead_chamfer is not None:
        return spec.lead_chamfer
    return spec.lid_thickness / 4


def lid_corner_rounding(spec: BoxSpec) -> float:
    """Return the radius on the sliding lid's leading corners (FR-002e4).

    Args:
        spec: Reads `wall_thickness`; an explicit `lid_corner_rounding` wins.

    Returns:
        The radius in mm — a quarter of the wall by default, capped at the
        dovetail's depth so the rounding cannot eat the key that retains the
        lid.

    """
    wt = spec.wall_thickness
    _, bottom_key = sliding_dovetail(spec)
    radius = spec.lid_corner_rounding
    if radius is None:
        radius = wt / 4
    return max(0.0, min(radius, bottom_key))


def _dovetail_solid(
    along_axis: str,
    bottom_along: tuple[float, float],
    top_along: tuple[float, float],
    across_center: float,
    bottom_across: float,
    top_across: float,
    height: float,
    z0: float,
    corner_rounding: float = 0.0,
) -> Bosl2Solid:
    """Return a prism dovetailed on its two flanks and, at the closed end, in depth.

    Both faces are rectangles given by their **along**-axis span and their
    **across**-axis width. The across width tapers between them — that is the
    dovetail on the two side walls. The along span may also differ, and when it
    does the difference is all at the *closed* end: the bottom face reaches
    further under the stop wall than the top face does, which is the back seat
    the lid's leading end slides into (FR-002e). The open end is the same at
    both faces, so the lid finishes flush with the mouth.

    ``corner_rounding`` rounds all four vertical corners, so the pair that goes
    in first does not snag on the groove mouths (FR-002e4).

    The rounding is uniform rather than per-corner because pybosl2 0.7.8's
    per-corner ``rounding`` list **translates the whole solid**: a lid asked for
    ``[0, 0, r, r]`` came out 23mm down the slide axis, its leading end 23mm
    inside the box and its trailing end hanging that far outside. A scalar (or
    four equal values) is correct. Rounding all four is no loss anyway — the
    trailing pair is the exposed end, which the box type rounds again anyway.
    """
    from pybosl2.shapes3d import prismoid

    bottom_size = bottom_along[1] - bottom_along[0]
    top_size = top_along[1] - top_along[0]
    bottom_center = (bottom_along[0] + bottom_along[1]) / 2
    shift_along = (top_along[0] + top_along[1]) / 2 - bottom_center

    if along_axis == "x":
        solid = prismoid(
            [bottom_size, bottom_across],
            [top_size, top_across],
            height=height,
            shift=[shift_along, 0.0],
            rounding=corner_rounding,
            **precision_kwargs(),
        )
        return solid.translate([bottom_center, across_center, z0])
    solid = prismoid(
        [bottom_across, bottom_size],
        [top_across, top_size],
        height=height,
        shift=[0.0, shift_along],
        rounding=corner_rounding,
        **precision_kwargs(),
    )
    return solid.translate([across_center, bottom_center, z0])


def _lead_chamfer(
    along_axis: str,
    lead: float,
    across_min: float,
    across_max: float,
    z_base: float,
    size: float,
    from_top: bool = False,
    face_slope: float = 0.0,
) -> Bosl2Solid:
    """Return a 45° wedge beveling one of the lid's leading horizontal edges.

    ``lead`` is the leading end's coordinate along the slide axis at the face
    being cut — the end that enters the box first. The wedge is ``size`` deep at
    that face and tapers to nothing ``size`` away from it, across the lid's full
    width, so the lid starts into the grooves instead of catching on their
    mouths.

    Args:
        along_axis: ``"x"`` or ``"y"`` — the slide axis.
        lead: The leading face's coordinate along that axis, at ``z_base``.
        across_min: Low edge of the span to cut, across the slide axis.
        across_max: High edge of that span.
        z_base: The face to cut from — the lid's underside, or its top face
            when ``from_top``.
        size: The chamfer's depth.
        from_top: Cut the leading **top** edge instead of the bottom one. The
            underside chamfer keeps the thin leading lip off the groove floor;
            the top one keeps the lid's top corner off the wall lip at the
            mouth. Between them the leading end is eased both ways.
        face_slope: How far the leading face advances along the slide axis per
            unit of height — the back seat's taper. Only the ``from_top`` cut
            needs it: that wedge's inner vertex has to sit **on** the sloped
            face, because the face leans away from a vertical cut going down,
            so a vertical one leaves a feather edge hanging off the face
            instead of taking the corner off it. The underside cut leans the
            other way and is already behind the face at every height.

    Returns:
        The wedge to subtract from the lid.

    """
    from pybosl2.shapes3d import prismoid

    span = across_max - across_min
    across_center = (across_min + across_max) / 2
    # The full-width face is at `z_base` and the wedge shrinks to a line `size`
    # away from it, so the prismoid's tapering end is whichever face is inside.
    lower, upper = ([0.0, size] if from_top else [size, 0.0])
    shift = (size / 2 + size * face_slope) if from_top else -size / 2
    z0 = z_base - size if from_top else z_base
    offset = (-size * face_slope) if from_top else size / 2
    # Riding the sloped face exactly makes the cutter's near surface *coincident*
    # with it, and a coincident subtraction leaves a zero-width sliver that keeps
    # the original face in the mesh — the cut measured as if it had never
    # happened. Backing the whole wedge off by a hair puts it clearly outside the
    # solid, at the cost of that hair off the chamfer.
    offset -= _COINCIDENT_EPS_MM
    if along_axis == "x":
        solid = prismoid(
            [lower, span], [upper, span], height=size, shift=[shift, 0.0],
            **precision_kwargs(),
        )
        return solid.translate([lead + offset, across_center, z0])
    solid = prismoid(
        [span, lower], [span, upper], height=size, shift=[0.0, shift],
        **precision_kwargs(),
    )
    return solid.translate([across_center, lead + offset, z0])


def dovetail_track(spec: BoxSpec, along_axis: str = "x") -> Closure:
    """Return the dovetailed channel a lid slides in, and the lid that fills it.

    One slot does both halves of the job, because they are the same slot: it
    leaves the interior clear at the top and bites half the wall width into
    each side wall at the bottom, to make the dovetail grooves, and it runs out
    through the far end wall so the lid has somewhere to enter. The groove is
    therefore wider at its floor than at its opening, which is what traps the
    lid: it can be slid along the axis but never lifted straight out. The
    groove never reaches the outer face — half the wall always remains behind
    it — so the walls still support the lid. Cutting only the grooves leaves a
    box with a solid wall across the front of its own track — a lid that can be
    dropped in but never slid.

    **The stop wall carries a dovetail too** (FR-002e), cut to the same depth as
    the sides: full thickness at the channel opening, half of it at the channel
    floor. That is a *seat*, not a catch. The lid's leading end is tapered to
    match, so the two faces stay parallel with the slide clearance between them
    for the whole travel — the lid slides in freely and lands in the seat — but
    once home, lifting the back of the lid drives its leading lip straight into
    the stop wall. Without it the leading end rests on nothing and the lid sits
    proud at the back.

    What must *not* be here is a **wedge catch**: a taper the lid has to be
    forced past to close and sprung back out to open. Nothing in this geometry
    interferes at any point in the travel, which is the property to check — a
    matched taper and a wedge look alike in a render and differ entirely in
    the hand. Holding the closed lid shut is :func:`sliding_catch`'s job, and
    that is a bump and dimple.

    The lid is the matching solid, cut short by `sliding_slack` on every mating
    face so it slides freely, with its two leading corners rounded and its
    leading edges chamfered so it starts into the grooves rather than snagging
    on their mouths (FR-002c, FR-002d, FR-002e4). The lid fills the channel
    flush with the open end.

    Args:
        spec: Needs `width`, `length`, `height`; reads `wall_thickness`,
            `lid_thickness`, and optionally `lead_chamfer`,
            `lid_corner_rounding` and `sliding_slack` (per-side clearance,
            default 0.1mm).
        along_axis: ``"x"`` to slide along the width, ``"y"`` along the length.

    Returns:
        The channel to subtract from the body, and the lid that fills it.

    """
    wt = spec.wall_thickness
    lt = spec.lid_thickness
    s = spec.sliding_slack
    chamfer = lead_chamfer_size(spec)
    corner_rounding = lid_corner_rounding(spec)
    top_key, bottom_key = sliding_dovetail(spec)

    if along_axis == "x":
        along = spec.width
        across = spec.length
    else:
        along = spec.length
        across = spec.width

    z0 = spec.height - lt
    interior_across = across - 2 * wt

    # The lid runs from under the stop wall out to the open face, so the closed
    # box is flush. Its top face is the interior (no key) and its underside
    # reaches `bottom_key` into each wall and under the stop wall, cut short by
    # the clearance on every mating face. The leading end's taper matches the
    # back seat's, so the two faces stay `s` apart for the whole travel.
    lid = _dovetail_solid(
        along_axis,
        (wt - bottom_key + s, along),
        (wt - top_key + s, along),
        across / 2,
        interior_across + 2 * bottom_key - 2 * s,
        interior_across + 2 * top_key - 2 * s,
        lt,
        z0,
        corner_rounding=corner_rounding,
    )

    # The channel: the same solid, larger by the clearance and a hair. Its floor
    # reaches `bottom_key` into each wall and into the stop wall, its opening
    # `top_key`, and it runs out through the open end wall. Its corners stay
    # square — the rounding is the lid's clearance, not a shape they share.
    channel = _dovetail_solid(
        along_axis,
        (wt - bottom_key - 0.05, along + 0.05),
        (wt - top_key - 0.05, along + 0.05),
        across / 2,
        interior_across + 2 * bottom_key + 0.1,
        interior_across + 2 * top_key + 0.1,
        lt + 0.1,
        z0 - 0.05,
    )

    # Chamfers on the leading end's two horizontal edges ease the lid in: the
    # underside one keeps the thin leading lip off the groove floor, the top one
    # keeps the lid's top corner off the wall lip at the mouth.
    if chamfer > 0:
        flank_min = wt - bottom_key + s
        flank_max = across - wt + bottom_key - s
        lid = lid - _lead_chamfer(
            along_axis, wt - bottom_key + s, flank_min, flank_max, z0, chamfer
        )
        lid = lid - _lead_chamfer(
            along_axis, wt - top_key + s, flank_min, flank_max, z0 + lt,
            chamfer, from_top=True,
            face_slope=(bottom_key - top_key) / lt if lt else 0.0,
        )

    return Closure(body=channel, lid=lid)


def sliding_track(spec: BoxSpec) -> Closure:
    """Return the sliding channel and lid, in the slide-along-X frame.

    A thin wrapper over :func:`dovetail_track` for the types that always slide
    along X (``SlidingCatchBox``, ``CardLibraryBox``).
    """
    return dovetail_track(spec, "x")



# ------------------------------------------------------------ retention catches (FR-099)


def build_bump_detent(
    radius: float,
    clearance: float = FIT_SLACK_MM / 2,
) -> tuple[Bosl2Solid, Bosl2Solid]:
    """Return positive bump and negative dimple (FR-099).

    Returns:
        tuple[Bosl2Solid, Bosl2Solid]: (bump, dimple)
    """
    from pybosl2 import sphere

    bump = sphere(radius=radius, **precision_kwargs())
    dimple = sphere(radius=radius + clearance, **precision_kwargs())
    return bump, dimple


def build_wedge_detent(
    depth: float,
    width: float,
    height: float,
    clearance: float = FIT_SLACK_MM / 2,
) -> tuple[Bosl2Solid, Bosl2Solid]:
    """Return positive wedge barb and negative pocket groove (FR-099).

    In detent local frame:
    X: [-width/2, width/2]
    Y: [0, depth]
    Z: [0, height]
    """
    from pybosl2 import Path2D
    from pybosl2.shapes2d import polygon

    # Sloped lead-in from (0, 0) to (depth, height), horizontal retaining shoulder at (0, height)
    wedge_poly = polygon(path=Path2D([
        (0.0, 0.0),
        (depth, height),
        (0.0, height),
    ]))
    wedge = (
        wedge_poly.linear_extrude(height=width)
        .rotate([0, 90, 0])
        .rotate([-90, 0, 0])
        .scale([1, -1, -1])
        .translate([-width / 2.0, 0.0, 0.0])
    )

    groove_poly = polygon(path=Path2D([
        (-0.05, -clearance),
        (depth + clearance, height + clearance),
        (-0.05, height + clearance),
    ]))
    groove = (
        groove_poly.linear_extrude(height=width + 2 * clearance)
        .rotate([0, 90, 0])
        .rotate([-90, 0, 0])
        .scale([1, -1, -1])
        .translate([-width / 2.0 - clearance, 0.0, -clearance])
    )
    return wedge, groove


def build_loop_detent(
    depth: float,
    width: float,
    height: float,
    tab_thickness: float = 1.0,
    clearance: float = 0.15,
) -> tuple[Bosl2Solid, Bosl2Solid]:
    """Return positive loop tab and negative body pocket cutter with hook (FR-099)."""
    from pyboxbuilder.box.shell import block

    t = min(tab_thickness, max(0.6, depth))
    outer_tab = block([width, t, height], at=(-width / 2.0, 0.0, 0.0))
    aperture_w = max(width / 2.0, width - 2 * t)
    aperture_h = max(height / 3.0, height / 2.0)
    aperture = block(
        [aperture_w, t + 0.2, aperture_h],
        at=(-aperture_w / 2.0, -0.1, (height - aperture_h) / 2.0),
    )
    loop_tab = outer_tab - aperture

    pocket = block(
        [width + 2 * clearance, depth + clearance, height + 2 * clearance],
        at=(-width / 2.0 - clearance, -0.05, -clearance),
    )
    hook_w = max(0.5, aperture_w - 2 * clearance)
    hook_bottom = (height - aperture_h) / 2.0 + clearance
    hook_h = max(0.5, aperture_h * 0.7 - 2 * clearance)
    hook_d = min(depth, t)
    hook = block([hook_w, hook_d, hook_h], at=(-hook_w / 2.0, 0.0, hook_bottom))
    body_cutter = pocket - hook
    return loop_tab, body_cutter


def build_magnet_detent(
    diameter: float,
    depth: float,
    clearance: float = 0.1,
) -> tuple[Bosl2Solid, Bosl2Solid]:
    """Return negative cylindrical magnet cavities for lid and body (FR-099).

    Both returns are negative cavities to be subtracted from lid and body,
    sized to accept press-fit or glued-in neodymium disc magnets.

    Returns:
        tuple[Bosl2Solid, Bosl2Solid]: (lid_pocket, body_pocket)
    """
    from pybosl2 import cylinder

    r = diameter / 2.0 + clearance
    h = depth + 0.1
    pocket_lid = cylinder(height=h, radius=r, **precision_kwargs())
    pocket_body = cylinder(height=h, radius=r, **precision_kwargs())
    return pocket_lid, pocket_body


def build_leaf_spring_detent(
    radius: float,
    arm_length: float = 8.0,
    arm_thickness: float = 1.0,
    slot_width: float = 0.8,
    clearance: float = FIT_SLACK_MM / 2,
) -> tuple[Bosl2Solid, Bosl2Solid, Bosl2Solid]:
    """Return positive detent bead, lid relief slot, and body dimple (FR-099).

    Generates a compliant cantilever flexure arm with relief clearance slots
    behind the detent bead, paired with an opposing clearance dimple.

    Returns:
        tuple[Bosl2Solid, Bosl2Solid, Bosl2Solid]: (bead, relief_slot, dimple)
    """
    from pybosl2 import sphere

    from pyboxbuilder.box.shell import block

    bead = sphere(radius=radius, **precision_kwargs())
    dimple = sphere(radius=radius + clearance, **precision_kwargs())
    slot = block(
        [arm_length, slot_width, 2 * radius + 0.4],
        at=(-arm_length / 2.0, arm_thickness, -radius - 0.2),
    )
    return bead, slot, dimple


def sliding_catch(
    spec: BoxSpec, radius: float = 1.0, along_axis: str = "x"
) -> Closure:
    """Return a retention catch that clicks the sliding lid shut (FR-002e1, FR-099).

    Supports CatchType.BUMP (default), CatchType.WEDGE, CatchType.LOOP, and CatchType.NONE.
    The catch sits at the outlet mouth, engaging in the final millimetres of slide.
    """
    from pyboxbuilder.box.shell import block

    catch_type = spec.resolved_catch_type(CatchType.BUMP)
    if catch_type == CatchType.NONE:
        return Closure()

    eff_radius = radius if radius is not None else spec.resolved_catch_size(1.0)
    if eff_radius <= 0.0:
        return Closure()

    wt = spec.wall_thickness
    lt = spec.lid_thickness
    s = spec.sliding_slack
    _, bottom_key = sliding_dovetail(spec)

    along = spec.width if along_axis == "x" else spec.length
    across = spec.length if along_axis == "x" else spec.width

    at_along = along - wt - 2 * eff_radius
    flank = wt - bottom_key / 2 + s
    z = spec.height - lt / 2
    envelope = block([spec.width, spec.length, spec.height])

    def _place(solid: Bosl2Solid, across_pos: float) -> Bosl2Solid:
        if along_axis == "x":
            return solid.translate([at_along, across_pos, z])
        return solid.translate([across_pos, at_along, z])

    if catch_type == CatchType.BUMP:
        bump, dimple = build_bump_detent(eff_radius, FIT_SLACK_MM / 2)
        bumps = _place(bump, flank) | _place(bump, across - flank)
        dimples = _place(dimple, flank) | _place(dimple, across - flank)
        return Closure(body=dimples, lid=bumps & envelope)

    if catch_type == CatchType.WEDGE:
        w_depth = min(eff_radius, max(0.4, bottom_key / 3.0))
        w_width = min(4.0, along / 8.0)
        w_height = min(lt * 0.8, 2.0)
        wedge, groove = build_wedge_detent(w_depth, w_width, w_height)

        # Place wedge and groove on both flanks pointing into wall (-Y on flank, +Y on across-flank)
        w_low = wedge.scale([1, -1, 1])
        g_low = groove.scale([1, -1, 1])
        wedges = _place(w_low, flank) | _place(wedge, across - flank)
        grooves = _place(g_low, flank) | _place(groove, across - flank)
        return Closure(body=grooves, lid=wedges & envelope)

    if catch_type == CatchType.LOOP:
        # Loop tab on the lid trailing edge, matching pocket on body outlet rim
        l_width = min(12.0, across / 3.0)
        l_depth = min(eff_radius * 1.5, wt)
        l_height = min(lt * 1.2, 3.0)
        loop_tab, body_cutter = build_loop_detent(l_depth, l_width, l_height)

        mid_across = across / 2.0
        if along_axis == "x":
            lid_part = loop_tab.translate([along - wt / 2.0, mid_across, spec.height - lt])
            body_part = body_cutter.translate([along - wt / 2.0, mid_across, spec.height - lt])
        else:
            lid_part = loop_tab.rotate([0, 0, 90]).translate([mid_across, along - wt / 2.0, spec.height - lt])
            body_part = body_cutter.rotate([0, 0, 90]).translate([mid_across, along - wt / 2.0, spec.height - lt])
        return Closure(body=body_part, lid=lid_part & envelope)

    if catch_type == CatchType.MAGNET:
        from pybosl2 import cylinder

        m_diam = min(spec.magnet_diameter, spec.resolved_catch_size(3.0))
        m_depth = min(spec.magnet_height, max(0.8, lt * 0.7))
        clr = 0.1
        mid_across = across / 2.0
        pos_along = wt + m_diam / 2.0 + 1.0
        if along_axis == "x":
            b_center = [pos_along, mid_across, spec.height - lt - m_depth / 2.0]
            l_center = [pos_along, mid_across, spec.height - lt + m_depth / 2.0]
        else:
            b_center = [mid_across, pos_along, spec.height - lt - m_depth / 2.0]
            l_center = [mid_across, pos_along, spec.height - lt + m_depth / 2.0]
        b_pocket = cylinder(height=m_depth, radius=m_diam / 2.0 + clr, **precision_kwargs()).translate(b_center)
        l_pocket = cylinder(height=m_depth, radius=m_diam / 2.0 + clr, **precision_kwargs()).translate(l_center)
        return Closure(body=b_pocket, lid_cut=l_pocket)

    if catch_type == CatchType.LEAF_SPRING:
        bead, slot, dimple = build_leaf_spring_detent(
            eff_radius, arm_length=min(8.0, along / 5.0)
        )
        bumps = _place(bead, flank) | _place(bead, across - flank)
        dimples = _place(dimple, flank) | _place(dimple, across - flank)
        slot_low = _place(slot, flank + eff_radius + 0.5)
        slot_high = _place(slot.scale([1, -1, 1]), across - flank - eff_radius - 0.5)
        slots = slot_low | slot_high
        return Closure(body=dimples, lid=bumps & envelope, lid_cut=slots & envelope)

    return Closure()



def cap_slipover_catch(spec: BoxSpec, is_slipover: bool = False) -> Closure:
    """Return a retention catch for cap boxes or slipover boxes (FR-002q2, FR-002q3, FR-099).

    Supports CatchType.BUMP (default), CatchType.WEDGE, CatchType.LOOP, and CatchType.NONE.
    Catches reside on the inside mating surface of the lid/sleeve, and cut
    into the box body's mating surface (the stepped band of the cap box body,
    or the outer wall of the slipover box body).
    """
    from pyboxbuilder.compartments.element import union_all

    catch_type = spec.resolved_catch_type(CatchType.BUMP)
    if catch_type == CatchType.NONE:
        return Closure()

    radius = spec.resolved_catch_size(spec.catch_radius if spec.catch_radius is not None else 1.0)
    if radius <= 0.0:
        return Closure()

    # Determine long axis and dimensions
    if spec.width >= spec.length:
        long_axis = "x"
        L = spec.width
        across_val = spec.length
    else:
        long_axis = "y"
        L = spec.length
        across_val = spec.width

    lt = spec.lid_thickness
    if is_slipover:
        from pyboxbuilder.box.features import slipover_gap, slipover_metrics
        inset, _ = slipover_metrics(spec)
        slack = spec.slip_slack
        foot = spec.foot
        gap = min(slipover_gap(spec), spec.height - foot - lt)
        # Center of catch along Z
        z = (foot + gap + spec.height - lt) / 2.0
    else:
        from pyboxbuilder.box.features import cap_metrics
        m = cap_metrics(spec)
        inset = m.inset
        slack = spec.cap_slack
        # Center of catch along Z
        z = (m.band_z + m.body_height) / 2.0

    # Spacing calculations
    margin = min(20.0, L / 4.0)
    avail = L - 2.0 * margin
    if avail / 3.0 >= 40.0:
        N = 4
    elif avail / 2.0 >= 40.0:
        N = 3
    else:
        N = 2

    spacing = avail / (N - 1) if N > 1 else 0.0

    body_solids = []
    lid_solids = []
    lid_cuts = []

    if catch_type == CatchType.BUMP:
        bump, dimple = build_bump_detent(radius, FIT_SLACK_MM / 2)
        for i in range(N):
            pos_long = margin + i * spacing
            for face in ("low", "high"):
                if face == "low":
                    pos_body = inset
                    pos_lid = inset - slack
                else:
                    pos_body = across_val - inset
                    pos_lid = across_val - (inset - slack)

                if long_axis == "x":
                    b_pt = [pos_long, pos_body, z]
                    l_pt = [pos_long, pos_lid, z]
                else:
                    b_pt = [pos_body, pos_long, z]
                    l_pt = [pos_lid, pos_long, z]

                body_solids.append(dimple.translate(b_pt))
                lid_solids.append(bump.translate(l_pt))

    elif catch_type == CatchType.WEDGE:
        w_depth = min(radius, max(0.4, inset * 0.4))
        w_width = min(6.0, spacing * 0.3 if spacing > 0 else 6.0)
        w_height = min(2.0, radius * 2.0)
        wedge, groove = build_wedge_detent(
            depth=w_depth, width=w_width, height=w_height, clearance=FIT_SLACK_MM / 2
        )
        z0 = z - w_height / 2.0

        for i in range(N):
            pos_long = margin + i * spacing
            if long_axis == "x":
                # low face: extends +Y
                lid_solids.append(wedge.translate([pos_long, inset - slack, z0]))
                body_solids.append(groove.translate([pos_long, inset, z0]))
                # high face: extends -Y
                lid_solids.append(wedge.scale([1, -1, 1]).translate([pos_long, across_val - (inset - slack), z0]))
                body_solids.append(groove.scale([1, -1, 1]).translate([pos_long, across_val - inset, z0]))
            else:
                # low face: extends +X
                lid_solids.append(wedge.rotate([0, 0, -90]).translate([inset - slack, pos_long, z0]))
                body_solids.append(groove.rotate([0, 0, -90]).translate([inset, pos_long, z0]))
                # high face: extends -X
                lid_solids.append(wedge.rotate([0, 0, 90]).translate([across_val - (inset - slack), pos_long, z0]))
                body_solids.append(groove.rotate([0, 0, 90]).translate([across_val - inset, pos_long, z0]))

    elif catch_type == CatchType.LOOP:
        l_width = min(8.0, spacing * 0.4 if spacing > 0 else 8.0)
        l_depth = min(radius, max(0.5, inset * 0.4))
        l_height = min(6.0, radius * 3.0)
        l_tab_th = min(1.0, l_depth)
        loop_tab, body_cutter = build_loop_detent(
            depth=l_depth, width=l_width, height=l_height, tab_thickness=l_tab_th, clearance=FIT_SLACK_MM / 2
        )
        z0 = z - l_height / 2.0

        for i in range(N):
            pos_long = margin + i * spacing
            if long_axis == "x":
                # low face: extends +Y
                lid_solids.append(loop_tab.translate([pos_long, inset - slack, z0]))
                body_solids.append(body_cutter.translate([pos_long, inset, z0]))
                # high face: extends -Y
                lid_solids.append(loop_tab.scale([1, -1, 1]).translate([pos_long, across_val - (inset - slack), z0]))
                body_solids.append(body_cutter.scale([1, -1, 1]).translate([pos_long, across_val - inset, z0]))
            else:
                # low face: extends +X
                lid_solids.append(loop_tab.rotate([0, 0, -90]).translate([inset - slack, pos_long, z0]))
                body_solids.append(body_cutter.rotate([0, 0, -90]).translate([inset, pos_long, z0]))
                # high face: extends -X
                lid_solids.append(loop_tab.rotate([0, 0, 90]).translate([across_val - (inset - slack), pos_long, z0]))
                body_solids.append(body_cutter.rotate([0, 0, 90]).translate([across_val - inset, pos_long, z0]))

    elif catch_type == CatchType.MAGNET:
        from pybosl2 import cylinder

        m_diam = min(spec.magnet_diameter, spec.resolved_catch_size(3.0))
        m_depth = min(spec.magnet_height, max(0.8, lt * 0.7))
        clr = 0.1
        for i in range(N):
            pos_long = margin + i * spacing
            for face in ("low", "high"):
                pos_body = inset if face == "low" else across_val - inset
                pos_lid = (inset - slack) if face == "low" else across_val - (inset - slack)
                if long_axis == "x":
                    b_pt = [pos_long, pos_body, z]
                    l_pt = [pos_long, pos_lid, z]
                else:
                    b_pt = [pos_body, pos_long, z]
                    l_pt = [pos_lid, pos_long, z]
                body_solids.append(
                    cylinder(height=m_depth, radius=m_diam / 2.0 + clr, **precision_kwargs()).translate(b_pt)
                )
                lid_cuts.append(
                    cylinder(height=m_depth, radius=m_diam / 2.0 + clr, **precision_kwargs()).translate(l_pt)
                )

    elif catch_type == CatchType.LEAF_SPRING:
        from pyboxbuilder.box.shell import block

        bump, dimple = build_bump_detent(radius, FIT_SLACK_MM / 2)
        slit_w = 0.8
        slit_len = min(6.0, radius * 3.0)
        slit_depth = inset + 1.0
        for i in range(N):
            pos_long = margin + i * spacing
            for face in ("low", "high"):
                pos_body = inset if face == "low" else across_val - inset
                pos_lid = (inset - slack) if face == "low" else across_val - (inset - slack)

                if long_axis == "x":
                    b_pt = [pos_long, pos_body, z]
                    l_pt = [pos_long, pos_lid, z]
                    s1 = block(
                        [slit_w, slit_depth, slit_len],
                        at=(pos_long - radius - slit_w, pos_lid - slit_depth / 2.0, z - slit_len / 2.0),
                    )
                    s2 = block(
                        [slit_w, slit_depth, slit_len],
                        at=(pos_long + radius, pos_lid - slit_depth / 2.0, z - slit_len / 2.0),
                    )
                else:
                    b_pt = [pos_body, pos_long, z]
                    l_pt = [pos_lid, pos_long, z]
                    s1 = block(
                        [slit_depth, slit_w, slit_len],
                        at=(pos_lid - slit_depth / 2.0, pos_long - radius - slit_w, z - slit_len / 2.0),
                    )
                    s2 = block(
                        [slit_depth, slit_w, slit_len],
                        at=(pos_lid - slit_depth / 2.0, pos_long + radius, z - slit_len / 2.0),
                    )

                body_solids.append(dimple.translate(b_pt))
                lid_solids.append(bump.translate(l_pt))
                lid_cuts.append(s1 | s2)

    elif catch_type in (
        CatchType.SLIDE_ACROSS,
        CatchType.SLIDE_UP,
        CatchType.SPIN,
        CatchType.PUSH_BUTTON,
        CatchType.TOGGLE_LATCH,
        CatchType.PINCH_SLIDE,
        CatchType.ROTARY_BOLT,
    ):
        from pybosl2 import cylinder

        from pyboxbuilder.box.shell import block

        pip_clr = max(0.22, min(0.35, getattr(spec, "pip_radial_clearance", 0.28)))
        skirt_t = max(0.7, inset - slack)
        mort_d = min(spec.wall_thickness * 0.55, max(0.65, radius * 0.8))
        win_w = min(L * 0.25, max(8.0, spec.wall_thickness * 4.5))
        win_h = min(4.0, max(2.0, lt * 1.4))
        slider_w = win_w * 0.58
        slider_h = max(1.2, win_h - 2 * pip_clr)
        lug_w = max(1.8, slider_w * 0.55)
        lug_h = max(0.9, slider_h * 0.65)
        pos_long = L / 2.0

        for face in ("low", "high"):
            # Body mortise cut on the body band's outer face, and captive mechanism on the lid skirt
            if long_axis == "x":
                if face == "low":
                    b_mort = block(
                        [win_w + 2 * pip_clr, mort_d + pip_clr + 0.1, lug_h + 2 * pip_clr],
                        at=(pos_long - win_w / 2.0 - pip_clr, inset - 0.05, z - lug_h / 2.0 - pip_clr),
                    )
                    l_win = block(
                        [win_w, skirt_t + 0.2, win_h],
                        at=(pos_long - win_w / 2.0, -0.1, z - win_h / 2.0),
                    )
                    if catch_type in (CatchType.SPIN, CatchType.ROTARY_BOLT):
                        r_cam = min(win_h * 0.45, 1.8)
                        l_mech = (
                            cylinder(height=skirt_t, radius=r_cam, **precision_kwargs())
                            .rotate([-90, 0, 0])
                            .translate([pos_long, skirt_t / 2.0, z])
                        )
                    else:
                        l_mech = block(
                            [slider_w, skirt_t, slider_h],
                            at=(pos_long - slider_w / 2.0, 0.0, z - slider_h / 2.0),
                        )
                    l_lug = block(
                        [lug_w, slack + mort_d - pip_clr + 0.2, lug_h],
                        at=(pos_long - lug_w / 2.0, skirt_t - 0.2, z - lug_h / 2.0),
                    )
                else:
                    y_b0 = across_val - inset - mort_d - pip_clr
                    y_l0 = across_val - skirt_t
                    b_mort = block(
                        [win_w + 2 * pip_clr, mort_d + pip_clr + 0.1, lug_h + 2 * pip_clr],
                        at=(pos_long - win_w / 2.0 - pip_clr, y_b0, z - lug_h / 2.0 - pip_clr),
                    )
                    l_win = block(
                        [win_w, skirt_t + 0.2, win_h],
                        at=(pos_long - win_w / 2.0, y_l0 - 0.1, z - win_h / 2.0),
                    )
                    if catch_type in (CatchType.SPIN, CatchType.ROTARY_BOLT):
                        r_cam = min(win_h * 0.45, 1.8)
                        l_mech = (
                            cylinder(height=skirt_t, radius=r_cam, **precision_kwargs())
                            .rotate([-90, 0, 0])
                            .translate([pos_long, y_l0 + skirt_t / 2.0, z])
                        )
                    else:
                        l_mech = block(
                            [slider_w, skirt_t, slider_h],
                            at=(pos_long - slider_w / 2.0, y_l0, z - slider_h / 2.0),
                        )
                    l_lug = block(
                        [lug_w, slack + mort_d - pip_clr + 0.2, lug_h],
                        at=(pos_long - lug_w / 2.0, across_val - inset - mort_d + pip_clr, z - lug_h / 2.0),
                    )
            else:
                if face == "low":
                    b_mort = block(
                        [mort_d + pip_clr + 0.1, win_w + 2 * pip_clr, lug_h + 2 * pip_clr],
                        at=(inset - 0.05, pos_long - win_w / 2.0 - pip_clr, z - lug_h / 2.0 - pip_clr),
                    )
                    l_win = block(
                        [skirt_t + 0.2, win_w, win_h],
                        at=(-0.1, pos_long - win_w / 2.0, z - win_h / 2.0),
                    )
                    l_mech = block(
                        [skirt_t, slider_w, slider_h],
                        at=(0.0, pos_long - slider_w / 2.0, z - slider_h / 2.0),
                    )
                    l_lug = block(
                        [slack + mort_d - pip_clr + 0.2, lug_w, lug_h],
                        at=(skirt_t - 0.2, pos_long - lug_w / 2.0, z - lug_h / 2.0),
                    )
                else:
                    x_b0 = across_val - inset - mort_d - pip_clr
                    x_l0 = across_val - skirt_t
                    b_mort = block(
                        [mort_d + pip_clr + 0.1, win_w + 2 * pip_clr, lug_h + 2 * pip_clr],
                        at=(x_b0, pos_long - win_w / 2.0 - pip_clr, z - lug_h / 2.0 - pip_clr),
                    )
                    l_win = block(
                        [skirt_t + 0.2, win_w, win_h],
                        at=(x_l0 - 0.1, pos_long - win_w / 2.0, z - win_h / 2.0),
                    )
                    l_mech = block(
                        [skirt_t, slider_w, slider_h],
                        at=(x_l0, pos_long - slider_w / 2.0, z - slider_h / 2.0),
                    )
                    l_lug = block(
                        [slack + mort_d - pip_clr + 0.2, lug_w, lug_h],
                        at=(across_val - inset - mort_d + pip_clr, pos_long - lug_w / 2.0, z - lug_h / 2.0),
                    )
            body_solids.append(b_mort)
            lid_cuts.append(l_win)
            lid_solids.append(l_mech | l_lug)

    return Closure(
        body=union_all(body_solids),
        lid=union_all(lid_solids),
        lid_cut=union_all(lid_cuts),
    )


# ------------------------------------------------------------ filament hinge


def corner_catch(
    at: tuple[float, float],
    towards: tuple[float, float],
    radius: float,
    height: float,
    wall_thickness: float,
    rounding_edge: float | None = None,
    top_rounding: float | None = None,
    bottom_rounding: float | None = None,
) -> Bosl2Solid:
    """Return a finger notch wrapping a corner, as the original's ``CornerCatch``.

    Not a new shape: the original builds it as **two `FingerHoleWall` scoops
    meeting at the corner**, one through each of the two walls, and this does
    the same with the same scoop builder. So the notch arrives with the roll,
    the floor fillet and the face fillets already right, and it cannot drift
    from the finger cuts elsewhere in the box.

    Args:
        at: The corner, in the piece's own frame.
        towards: Unit direction into the piece from that corner — ``(1, 1)``
            for the origin corner, ``(-1, -1)`` for the far one.
        radius: Half-width of each scoop.
        height: How far down from the top of the piece the notch reaches.
        wall_thickness: The wall each scoop cuts through.
        rounding_edge: Fillet where the cut meets each face; ``None`` uses the
            scoop default.
        top_rounding: ``r1`` — how far the mouth rolls in at the top. ``None``
            lets the scoop derive it from the half-width, which is what a
            sleeve notch wants; a cap box sets it, because there the pair of
            rolls is a fixed height budget rather than a proportion.
        bottom_rounding: ``r2`` — the roll out at the bottom of the cut.

    Returns:
        The solid to subtract from the piece.

    """
    from pyboxbuilder.compartments.element import union_all
    from pyboxbuilder.compartments.finger_cuts import build_wall_scoop
    from pyboxbuilder.compartments.finger_outline import CutProfile
    from pyboxbuilder.compartments.finger_sweep import FaceTreatment
    from pyboxbuilder.enums import ScoopSide

    # A span wide enough that the scoop is never capped by it; the scoop is
    # then slid from that span's midpoint onto the corner.
    span = max(4 * radius, 4 * wall_thickness)
    parts = []
    for side in (ScoopSide.FRONT, ScoopSide.LEFT):
        scoop = build_wall_scoop(
            span, span, height, side,
            radius=radius,
            wall_thickness=wall_thickness,
            profile=CutProfile(mouth_flare=top_rounding, base_radius=bottom_rounding),
            faces=FaceTreatment(
                fillet=rounding_edge,
                breach_floor=True,
                # There is material above a corner notch — the lid plate — so
                # the outline's rim overshoot is trimmed off rather than
                # carving through it.
                top_limit=height,
            ),
        )
        # `build_wall_scoop` puts its wall on the far side of the compartment
        # origin, so each arm's slab lands at [-wall_thickness, 0] across the
        # face rather than on the skin the notch is meant to cut. Moving it in
        # by the wall it was given puts it exactly over that skin: measured, a
        # cap box's indent was cutting 0.5mm of the 1.15mm it was asked for.
        if side is ScoopSide.FRONT:
            scoop = scoop.translate([-span / 2, wall_thickness, 0.0])
        else:
            scoop = scoop.translate([wall_thickness, -span / 2, 0.0])
        if towards[0] < 0:
            scoop = scoop.mirror([1, 0, 0])
        if towards[1] < 0:
            scoop = scoop.mirror([0, 1, 0])
        parts.append(scoop.translate([at[0], at[1], 0.0]))

    return union_all(parts)


def hinge_intrusion(spec: BoxSpec, filament_diameter: float = 1.75) -> Bosl2Solid:
    """Return the volume a hinge occupies inside the box, as a solid to subtract.

    A hinge that sits inside the box's outline has to take that room from
    somewhere, and it takes it from the interior: the barrel and the leaf webs
    stand in the back of the box, right where a compartment would otherwise
    go. Rather than leave a compartment to collide with them, a hinge box
    subtracts this from its contents mask (following the original's
    `FilamentBoxInsideMask`, which does the same for the filament hinge).

    Args:
        spec: Box dimensions; reads `wall_thickness` and `lid_thickness`.
        filament_diameter: The pin stock, which sets the barrel radius.

    Returns:
        The solid the contents must keep clear of.

    """
    from pybosl2 import cylinder
    from pybosl2.shapes2d import polygon

    wt = spec.wall_thickness
    radius = max(wt, filament_diameter)
    gap = PRINT_IN_PLACE_GAP_MM
    r_c = radius + gap
    leaf_thickness = spec.lid_thickness
    axis_y = spec.length - radius
    axis_z = min(spec.height, spec.height + leaf_thickness - radius)

    total_depth = radius + r_c

    # The barrel cylinder
    cyl = cylinder(
        height=spec.width, radius=r_c, **precision_kwargs()
    ).rotate([0, 90, 0]).translate([spec.width / 2, axis_y, axis_z])

    # The chamfered support web/wedge angling back to the back wall
    from pybosl2 import Path2D
    poly = polygon(path=Path2D([
        (spec.length, axis_z + total_depth),
        (spec.length - total_depth, axis_z),
        (spec.length, axis_z - total_depth),
    ]))
    wedge = poly.linear_extrude(height=spec.width).rotate([0, 90, 0]).rotate([-90, 0, 0]).scale([1, -1, -1])

    return cyl | wedge


def filament_hinge(
    spec: BoxSpec,
    filament_diameter: float = 1.75,
    knuckles: int = 5,
    lid_thickness: float | None = None,
) -> Closure:
    """Interleaved knuckles along the back edge, bored for a filament pin.

    The "hinge" is a length of filament threaded through the knuckles after
    printing, so the two halves stay separate parts. Both sets share one pin
    axis and alternate along it, with a print gap between neighbours.

    Args:
        spec: Box dimensions.
        filament_diameter: Pin stock diameter; the bore is a little wider.
        knuckles: Total knuckles across the hinge, alternating body and lid.
        lid_thickness: Thickness of the leaf the lid's knuckles web into;
            defaults to the spec's.

    """
    from pybosl2 import cylinder

    from pyboxbuilder.box.shell import block
    from pyboxbuilder.compartments.element import union_all

    wt = spec.wall_thickness
    radius = max(wt, filament_diameter)
    bore = filament_diameter / 2 + 0.2
    gap = PRINT_IN_PLACE_GAP_MM
    leaf_thickness = (
        spec.lid_thickness if lid_thickness is None else lid_thickness
    )

    # The pin runs along X, level with the joint between body and lid and set
    # **inside** the back wall: the barrel's outer face is flush with the box,
    # so the closed box is exactly its declared size with nothing hanging off
    # the back. The price is that the barrel intrudes into the interior, which
    # is why a hinge box carves that volume out of its contents mask.
    axis_y = spec.length - radius
    # Sunk far enough that the barrel's crown is flush with the *closed* box's
    # top, not just inside its footprint. `spec.height` here is the body's
    # height — the joint plane — and the lid adds its own thickness above it,
    # so a barrel wider than that thickness has to drop by the difference.
    axis_z = min(spec.height, spec.height + leaf_thickness - radius)

    span = spec.width
    pitch = span / knuckles
    # Each leaf webs inward from the barrel to its own half.
    web_y = axis_y
    web_depth = radius + 0.5

    body_parts, lid_parts = [], []
    body_relief, lid_relief = [], []
    for index in range(knuckles):
        length = pitch - gap
        if length <= 0:
            continue
        centre_x = pitch * (index + 0.5)
        knuckle = cylinder(height=length, radius=radius, **precision_kwargs()).rotate([0, 90, 0])
        knuckle = knuckle.translate([centre_x, axis_y, axis_z])

        # Each leaf webs back to its own half — the body's below the joint, the
        # lid's above it — so neither reaches across into the other.
        if index % 2:
            # Sized to the lid's own thickness — a taller web would stand proud
            # of the closed lid. It reaches *inward* now that the barrel is
            # inside the box.
            web = block(
                [length, web_depth, leaf_thickness - gap / 2],
                at=(centre_x - length / 2, web_y - web_depth, axis_z + gap / 2),
            )
            lid_parts += [knuckle, web]
            # The same knuckle and web, grown by the print gap: this is what
            # the body has to give up so the lid's leaf is a separate part.
            relief = cylinder(
                height=length + 2 * gap, radius=radius + gap, **precision_kwargs()
            ).rotate([0, 90, 0]).translate([centre_x, axis_y, axis_z])
            relief_web = block(
                [length + 2 * gap, web_depth + gap, leaf_thickness + gap],
                at=(
                    centre_x - length / 2 - gap,
                    web_y - web_depth - gap,
                    axis_z,
                ),
            )
            body_relief += [relief, relief_web]
        else:
            web = block(
                [length, web_depth, radius],
                at=(centre_x - length / 2, web_y - web_depth, axis_z - radius - gap / 2),
            )
            body_parts += [knuckle, web]
            # And the mirror image: what the lid gives up for this knuckle.
            relief = cylinder(
                height=length + 2 * gap, radius=radius + gap, **precision_kwargs()
            ).rotate([0, 90, 0]).translate([centre_x, axis_y, axis_z])
            relief_top = block(
                [length + 2 * gap, radius + gap + 1.0, leaf_thickness + gap + 1.0],
                at=(
                    centre_x - length / 2 - gap,
                    axis_y - gap,
                    axis_z,
                ),
            )
            lid_relief += [relief, relief_top]

    pin = cylinder(height=spec.width + 2, radius=bore, **precision_kwargs()).rotate([0, 90, 0])
    pin = pin.translate([spec.width / 2, axis_y, axis_z])

    return Closure(
        body=union_all(body_parts),
        lid=union_all(lid_parts),
        body_cut=union_all(body_relief),
        lid_cut=union_all(lid_relief),
        pin=pin,
    )


# --------------------------------------------------------------- path skirt


def offset_footprint(
    path: tuple[tuple[float, float], ...], distance: float
) -> tuple[tuple[float, float], ...]:
    """Grow or shrink a footprint outline by `distance` (positive shrinks)."""
    from pyboxbuilder.paths import inset_rectilinear, is_rectilinear

    if is_rectilinear(path):
        return inset_rectilinear(path, distance)

    cx = sum(p[0] for p in path) / len(path)
    cy = sum(p[1] for p in path) / len(path)
    out = []
    for x, y in path:
        dx, dy = x - cx, y - cy
        span = max((dx * dx + dy * dy) ** 0.5, 1e-9)
        scale = max(0.0, (span - distance) / span)
        out.append((cx + dx * scale, cy + dy * scale))
    return tuple(out)


def extrude_footprint(
    path: tuple[tuple[float, float], ...], height: float, base_z: float = 0.0
) -> Bosl2Solid:
    """Extrude a footprint outline upward from `base_z`.

    `linear_extrude` is the one operation that already grows from its base
    rather than being centre-anchored, so this only has to lift it.
    """
    from pybosl2 import Path2D

    profile = Path2D([(float(x), float(y)) for x, y in path], closed=True)
    solid = profile.linear_extrude(height=height)
    return solid if base_z == 0.0 else solid.translate([0.0, 0.0, base_z])


def extrude_rounded_footprint(
    path: tuple[tuple[float, float], ...],
    height: float,
    base_z: float = 0.0,
    *,
    r_corner: float = 0.0,
    r_bottom: float = 0.0,
    r_top: float = 0.0,
) -> Bosl2Solid:
    """Extrude a polygon footprint with rounded vertical corners and optional top/bottom roundovers."""
    import math

    from pybosl2 import Path2D
    from pybosl2.shapes3d.base import CsgSolid
    from pybosl2.skin import os_profile

    from pyboxbuilder.box.shell import block
    from pyboxbuilder.paths import is_rectilinear
    from pyboxbuilder.rounding import rounding_facets

    if height <= 0.0 or len(path) < 3:
        return extrude_footprint(path, max(0.01, height), base_z)

    try:
        steps = max(8, rounding_facets()["fn"] // 4)
        fn = rounding_facets()["fn"]
        p2d = Path2D([(float(x), float(y)) for x, y in path], closed=True)
        rc = 0.0
        if r_corner > 0.05 and is_rectilinear(path):
            min_edge = min(
                math.hypot(
                    path[(i + 1) % len(path)][0] - path[i][0],
                    path[(i + 1) % len(path)][1] - path[i][1],
                )
                for i in range(len(path))
            )
            rc = min(r_corner, min_edge * 0.2)
            if rc > 0.05:
                p2d = p2d.round_corners(radius=rc, fn=fn)

        r_bot = min(max(0.0, r_bottom), height * 0.45)
        r_tp = min(max(0.0, r_top), height * 0.45)
        if rc > 0.05:
            r_bot = min(r_bot, rc * 0.75)
            r_tp = min(r_tp, rc * 0.75)

        def _make_prof(r: float) -> object:
            pts = [
                [
                    -r * math.sin((math.pi / 2) * i / steps),
                    r * (1.0 - math.cos((math.pi / 2) * i / steps)),
                ]
                for i in range(steps + 1)
            ]
            return os_profile(Path2D(pts))

        if r_bot > 0.05 and r_tp > 0.05:
            r = min(r_bot, r_tp)
            prof = _make_prof(r)
            swept = p2d.offset(delta=-r).offset_sweep(
                height=height, bottom=prof, top=prof, steps=steps
            )
            solid = CsgSolid(swept.polyhedron()) if hasattr(swept, "polyhedron") else swept
        elif r_bot > 0.05:
            prof = _make_prof(r_bot)
            swept = p2d.offset(delta=-r_bot).offset_sweep(
                height=height, bottom=prof, steps=steps
            )
            solid = CsgSolid(swept.polyhedron()) if hasattr(swept, "polyhedron") else swept
        elif r_tp > 0.05:
            r = r_tp
            prof = _make_prof(r)
            swept = p2d.offset(delta=-r).offset_sweep(
                height=height + r, bottom=prof, top=prof, steps=steps
            )
            raw = CsgSolid(swept.polyhedron()) if hasattr(swept, "polyhedron") else swept
            raw = raw.translate([0.0, 0.0, -r])
            min_x = min(p[0] for p in path) - 2.0
            min_y = min(p[1] for p in path) - 2.0
            max_x = max(p[0] for p in path) + 2.0
            max_y = max(p[1] for p in path) + 2.0
            keep = block(
                [max_x - min_x, max_y - min_y, height + 0.1],
                at=(min_x, min_y, 0.0),
            )
            solid = raw & keep
        else:
            solid = p2d.linear_extrude(height=height)

        return solid if base_z == 0.0 else solid.translate([0.0, 0.0, base_z])
    except Exception:
        return extrude_footprint(path, height, base_z)


def path_body_metrics(spec: BoxSpec) -> tuple[float, float]:
    """(inset per side, body height) for a polygon-footprint body.

    Same rule as the rectangular closures: the declared outline and height are
    the outside of the closed box, so the body is set in and stops short, and
    the cap or sleeve fills the difference back out to the declared size.
    """
    wt = spec.wall_thickness
    lt = spec.lid_thickness
    wiggle = spec.size_spacing
    return wt / 2 + wiggle, spec.height - lt - wiggle


def path_cap(
    spec: BoxSpec, path: tuple[tuple[float, float], ...], cap_height: float
) -> Bosl2Solid:
    """Return a cap whose skirt follows a polygon footprint instead of a rectangle.

    Its outer face is the declared outline, so a closed box measures exactly
    what it was asked for.
    """
    from pyboxbuilder.box.shell import body_rounding
    from pyboxbuilder.rounding import lid_rounding, mating_rounding

    lt = spec.lid_thickness
    slack = spec.cap_slack
    inset, _ = path_body_metrics(spec)
    r_body = body_rounding(spec)
    r_mating = max(mating_rounding(spec), r_body * 0.75)
    r_lid = min(lid_rounding(spec), max(0.0, (inset - slack) * 0.85), lt * 0.85)

    base = spec.height - cap_height
    cap = extrude_rounded_footprint(
        path, cap_height, base, r_corner=r_body, r_top=r_lid
    )
    cavity = extrude_rounded_footprint(
        offset_footprint(path, inset - slack),
        cap_height - lt + 0.1,
        base - 0.1,
        r_corner=r_mating,
    )
    return cap - cavity


def path_sleeve(
    spec: BoxSpec,
    path: tuple[tuple[float, float], ...],
    slip: float,
    foot: float | None = None,
) -> Bosl2Solid:
    """Return a sleeve that slips over a polygon-footprint body, stopping at the foot."""
    from pyboxbuilder.box.shell import body_rounding
    from pyboxbuilder.rounding import lid_rounding, mating_rounding

    lt = spec.lid_thickness
    slack = spec.slip_slack
    inset, _ = path_body_metrics(spec)
    foot_val = spec.foot if foot is None else float(foot)
    gap = min(slipover_gap(spec), spec.height - foot_val - lt)
    skirt = spec.height - foot_val - gap
    base_z = foot_val + gap
    r_body = body_rounding(spec)
    r_mating = max(mating_rounding(spec), r_body * 0.75)
    r_lid = min(lid_rounding(spec), max(0.0, (inset - slack) * 0.85), lt * 0.85)

    outer = extrude_rounded_footprint(
        path, skirt, base_z, r_corner=r_body, r_top=r_lid
    )
    cavity = extrude_rounded_footprint(
        offset_footprint(path, inset - slack),
        skirt - lt + 0.1,
        base_z - 0.1,
        r_corner=r_mating,
    )
    return outer - cavity


# ------------------------------------------------------- fingernail catch

FINGERNAIL_RADIUS_MM = 4.0
"""Opening radius of a sliding lid's fingernail dish, where the lid can spare it.

Eight millimetres across, which takes a nail and the fingertip behind it
without turning the lid into a bowl. Capped against the lid's own narrow
dimension below, so a small card box gets a small dish rather than one sized
for a card lid.
"""

FINGERNAIL_MIN_RADIUS_MM = 2.0
"""Smallest dish worth cutting; below this a nail has nothing to hook."""

FINGERNAIL_DEPTH_SHARE = 0.5
"""How much of the lid's thickness the dish may take (FR-002e5).

Half, so a plate's worth of material always remains under it. The dish is a
thinned spot that gets pulled on — it is the depth that makes it a catch and
the material under it that makes it hold.
"""

FINGERNAIL_MARGIN_MM = 1.0
"""Solid lid kept around the dish, clear of any pattern (FR-002e5).

The ring the dish is pulled against. A hole opening onto its rim is where the
lid would tear.
"""


@dataclass(frozen=True)
class FingernailCatch:
    """A sliding lid's fingernail dish: where it is, and how big."""

    centre: tuple[float, float]
    """Where the dish sits on the lid, in the box's frame.

    The centre of the *whole* sphere the dish is half of, so it is also where
    the flat wall stands — see :func:`fingernail_dish`."""
    radius: float
    """The opening's radius — what a nail sees on the surface."""
    depth: float
    """How far it sinks below the lid's top face."""
    axis: str = "x"
    """The axis the lid slides along, which the flat wall stands square to."""

    @property
    def keepout_radius(self) -> float:
        """Radius a pattern must stay clear of, dish plus its margin."""
        return self.radius + FINGERNAIL_MARGIN_MM


def fingernail_catch(spec: BoxSpec, along_axis: str) -> FingernailCatch | None:
    """Size and place the dish that starts a sliding lid moving (FR-002e5).

    Args:
        spec: Reads `width`, `length`, `lid_thickness` and the `fingernail_*`
            overrides.
        along_axis: ``"x"`` or ``"y"`` — the axis the lid slides along, so the
            exit end is that axis's far end.

    Returns:
        The catch, or ``None`` when the box declines one or the lid is too
        small to carry a dish a nail could use.

    """
    if not spec.fingernail_catch:
        return None

    label_margin = 10.0
    if spec.lid_border_margin_mm is not None:
        label_margin = spec.lid_border_margin_mm

    across = spec.length if along_axis == "x" else spec.width
    radius = spec.fingernail_radius
    if radius is None:
        # Sized from the lid it is cut into, so a small lid gets a small dish.
        radius = min(FINGERNAIL_RADIUS_MM, across / 6.0)

    # Ensure we can fit the radius with the 2.5mm edge gap and 1.0mm label gap
    if radius > label_margin - 3.5:
        radius = label_margin - 3.5

    if radius < FINGERNAIL_MIN_RADIUS_MM:
        return None

    depth = spec.fingernail_depth
    if depth is None:
        depth = spec.lid_thickness * FINGERNAIL_DEPTH_SHARE
    depth = min(depth, spec.lid_thickness * FINGERNAIL_DEPTH_SHARE)
    if depth <= 0:
        return None

    # Move the finger catch back 1mm from the edge of the lid (so 2.5mm)
    inset = 2.5

    centre = (
        (spec.width - inset, spec.length / 2.0)
        if along_axis == "x"
        else (spec.width / 2.0, spec.length - inset)
    )
    return FingernailCatch(
        centre=centre, radius=radius, depth=depth, axis=along_axis
    )


def fingernail_dish(spec: BoxSpec, catch: FingernailCatch) -> Bosl2Solid:
    """Return the solid to subtract from a lid to leave the dish.

    **Half** the top of a sphere, split on a plane square to the slide axis:
    a bowl on the inboard side, and a flat wall standing across the pull on the
    outboard side. The two halves do different jobs. The bowl is what a nail
    goes into — a surface curving away in every direction, so the nail finds it
    without being aimed. The wall is what the nail then pulls on, and it has to
    be flat: a whole dish curves away on the pull side too, so a nail loading it
    is riding up a slope and skids out of the dish instead of moving the lid.

    Which half is kept is not a matter of taste. A nail can push and not pull,
    so the surface it bears on must have the lid's material on the far side of
    it *in the direction of travel* — the wall between the dish and the exit
    edge. Keeping the other half would give a wall that can only be pushed
    inboard, which drives the lid further into the box.

    Args:
        spec: Needs `height`; reads `lid_thickness`.
        catch: The dish to build.

    Returns:
        The half-sphere to subtract.

    """
    from pybosl2 import sphere

    from pyboxbuilder.box.shell import block

    # A cap of depth d showing an opening of radius r comes off a sphere of
    # radius (r² + d²) / 2d — solve the chord, do not guess it.
    ball = (catch.radius ** 2 + catch.depth ** 2) / (2 * catch.depth)
    top = spec.height
    dish = sphere(radius=ball, **precision_kwargs()).translate(
        [catch.centre[0], catch.centre[1], top - catch.depth + ball]
    )

    # Everything inboard of the wall. Sized off the ball rather than the
    # opening, because the sphere is wider below the surface than at it.
    reach = ball + 1
    span = 2 * reach
    x, y = catch.centre
    size = [span, span, span]
    at = [x - reach, y - reach, top - reach]
    # The wall stands on the centre line: the half kept runs from there back
    # along the slide axis, and the other half of the sphere is left as lid.
    axis = 0 if catch.axis == "x" else 1
    size[axis] = reach
    return dish & block(size, at=at)


def hinge_catch(spec: BoxSpec, *, vertical_wall: bool = False) -> Closure:
    """Return the front snap-fit or print-in-place catch for a hinged box (FR-002v, FR-099).

    When ``vertical_wall=True`` (or ``slide_catch_style="vertical"``), all catches are
    built to mount on vertical front/side walls where the lid may be a hollow upper tray
    or unfolded 180° on the print bed (`PrintInPlaceHingeBox`, `InsetHingeBox`, `ClamshellBox`).
    """
    from pybosl2.shapes2d import polygon
    from pybosl2.shapes3d import sphere

    from pyboxbuilder.compartments.element import union_all
    from pyboxbuilder.precision import kwargs as precision_kwargs

    catch_type = spec.resolved_catch_type(CatchType.WEDGE)
    if catch_type == CatchType.NONE:
        return Closure()

    is_vertical = vertical_wall or getattr(spec, "slide_catch_style", "front") in (
        "vertical",
        "card_library_vertical",
    )

    if catch_type == CatchType.SLIDE_ACROSS:
        if is_vertical:
            return build_vertical_slide_across_hinge_catch(spec)
        return build_slide_across_hinge_catch(spec)
    if catch_type == CatchType.SLIDE_UP:
        c = build_slide_up_hinge_catch(spec)
        if is_vertical and c.lid_cut is not None:
            wt = spec.wall_thickness
            track_w = min(spec.width * 0.35, max(10.0, wt * 5.0))
            track_d = min(wt * 0.75, max(1.2, wt - 0.5))
            l_boss = _lid_front_wall_backing_boss(
                spec, spec.width / 2.0, track_w + 2.0 * wt, max(wt, track_d + 1.2)
            )
            if l_boss is not None:
                return Closure(
                    body=c.body,
                    body_cut=c.body_cut,
                    lid=l_boss - c.lid_cut,
                    lid_cut=c.lid_cut,
                )
        return c
    if catch_type == CatchType.SPIN:
        c = build_spin_hinge_catch(spec)
        if is_vertical and c.lid_cut is not None:
            wt = spec.wall_thickness
            l_boss = _lid_front_wall_backing_boss(
                spec, spec.width / 2.0, max(12.0, 4.0 * wt), max(wt, wt * 1.4)
            )
            if l_boss is not None:
                return Closure(
                    body=c.body,
                    body_cut=c.body_cut,
                    lid=l_boss - c.lid_cut,
                    lid_cut=c.lid_cut,
                )
        return c
    if catch_type == CatchType.PUSH_BUTTON:
        return build_push_button_hinge_catch(spec, vertical_wall=is_vertical)
    if catch_type == CatchType.TOGGLE_LATCH:
        c = build_toggle_latch_hinge_catch(spec)
        if is_vertical and c.lid_cut is not None:
            wt = spec.wall_thickness
            bail_w = min(spec.width * 0.34, max(10.0, wt * 5.0))
            l_boss = _lid_front_wall_backing_boss(
                spec, spec.width / 2.0, bail_w + 2.0 * wt, max(wt, wt * 1.4)
            )
            if l_boss is not None:
                return Closure(
                    body=c.body,
                    body_cut=c.body_cut,
                    lid=l_boss - c.lid_cut,
                    lid_cut=c.lid_cut,
                )
        return c
    if catch_type == CatchType.PINCH_SLIDE:
        if is_vertical:
            return build_vertical_pinch_slide_hinge_catch(spec)
        return build_pinch_slide_hinge_catch(spec)
    if catch_type == CatchType.ROTARY_BOLT:
        if is_vertical:
            return build_vertical_rotary_bolt_hinge_catch(spec)
        return build_rotary_bolt_hinge_catch(spec)

    eff_size = spec.resolved_catch_size(1.0)
    if eff_size <= 0.0:
        return Closure()

    wt = spec.wall_thickness
    lt = spec.lid_thickness
    body_height = spec.height - lt

    # Catch dimensions
    if is_vertical:
        catch_height = min(body_height * 0.4, 4.0)
        catch_width = min(getattr(spec, "pip_snap_width", 12.0), spec.width * 0.4, 15.0)
    else:
        catch_height = min(spec.height / 2.0, 10.0)
        catch_width = min(spec.width * 0.4, 15.0)
    gap = 0.1
    fillet_r = wt / 2.0  # default rounding is wall_thickness/2

    x_center = spec.width / 2.0

    from pybosl2.constants import FRONT
    from pybosl2.shapes2d import rect

    tab_2d = rect([catch_width, wt / 2.0], rounding=[fillet_r, fillet_r, 0, 0], anchor=FRONT)
    tab_top_extra = lt if is_vertical else 0.0
    lid_tab = tab_2d.linear_extrude(height=catch_height + tab_top_extra).translate(
        [x_center, 0.0, body_height - catch_height]
    )

    body_cut_width = catch_width + 2 * gap
    body_cut_y = wt / 2.0 + gap
    body_cut_2d = rect(
        [body_cut_width, body_cut_y],
        rounding=[fillet_r + gap, fillet_r + gap, 0, 0],
        anchor=FRONT,
    )
    body_cut = body_cut_2d.linear_extrude(height=catch_height + gap).translate(
        [x_center, -gap, body_height - catch_height - gap]
    )

    from pybosl2 import Path2D
    gusset_poly = polygon(path=Path2D([
        (0.0, wt / 2.0),
        (0.0, wt - 0.2),  # stop slightly short of inner wall to prevent outer wall bleed/coincidence
        (lt, wt / 2.0),
    ]))
    gusset = (
        gusset_poly.linear_extrude(height=catch_width - 2 * fillet_r)
        .rotate([0, 90, 0])
        .rotate([-90, 0, 0])
        .scale([1, -1, -1])
        .translate([x_center - catch_width / 2.0 + fillet_r, 0, body_height])
    )

    pocket_poly = polygon(path=Path2D([
        (-gap, wt / 2.0 - gap),
        (-gap, wt + 0.1),
        (lt + gap, wt + 0.1),
        (lt + gap, wt / 2.0 - gap),
    ]))
    pocket_cut = (
        pocket_poly.linear_extrude(height=catch_width + 2 * gap)
        .rotate([0, 90, 0])
        .rotate([-90, 0, 0])
        .scale([1, -1, -1])
        .translate([x_center - catch_width / 2.0 - gap, 0, body_height])
    )

    if not is_vertical:
        body_cut = body_cut | pocket_cut
    lid_tab = lid_tab | gusset

    z_peak = body_height - catch_height / 2.0
    slope_height = min(1.2, catch_height * 0.45) if is_vertical else 2.0

    if catch_type == CatchType.WEDGE:
        bead_depth = min(eff_size, wt / 2.0)
        # Right-angled triangular ridge on lid tab (flat top, sloped bottom)
        ridge_poly = polygon(path=Path2D([
            (wt / 2.0, 0.0),
            (wt / 2.0 + bead_depth, slope_height),
            (wt / 2.0, slope_height),
        ]))
        ridge = (
            ridge_poly.linear_extrude(height=catch_width)
            .rotate([0, 90, 0])
            .rotate([-90, 0, 0])
            .scale([1, -1, -1])
            .translate([x_center - catch_width / 2.0, 0, z_peak - slope_height])
        )
        lid_catch = lid_tab | ridge

        # Body cut pocket groove (triangular matching cut, slightly larger)
        groove_poly = polygon(path=Path2D([
            (wt / 2.0 - 0.1, 0.0),
            (wt / 2.0 + bead_depth + gap, slope_height + 1.0 + gap),
            (wt / 2.0 - 0.1, slope_height + 1.0 + gap),
        ]))
        groove = (
            groove_poly.linear_extrude(height=catch_width + 2 * gap)
            .rotate([0, 90, 0])
            .rotate([-90, 0, 0])
            .scale([1, -1, -1])
            .translate([x_center - catch_width / 2.0 - gap, 0, z_peak - slope_height - 1.0 - gap])
        )
        body_catch_cut = body_cut | groove

    elif catch_type == CatchType.BUMP:
        # Bump catch (two side-by-side bumps)
        x1 = x_center - catch_width / 4.0
        x2 = x_center + catch_width / 4.0
        r_bump = min(eff_size, wt / 2.0)

        bump1 = sphere(radius=r_bump, **precision_kwargs()).translate([x1, wt / 2.0, z_peak])
        bump2 = sphere(radius=r_bump, **precision_kwargs()).translate([x2, wt / 2.0, z_peak])
        lid_catch = union_all([lid_tab, bump1, bump2])

        indent1 = sphere(radius=r_bump + gap, **precision_kwargs()).translate([x1, wt / 2.0, z_peak])
        indent2 = sphere(radius=r_bump + gap, **precision_kwargs()).translate([x2, wt / 2.0, z_peak])
        body_catch_cut = union_all([body_cut, indent1, indent2])

    elif catch_type == CatchType.LOOP:
        from pyboxbuilder.box.shell import block

        aperture_w = catch_width * 0.55
        aperture_h = catch_height * 0.35
        aperture = block(
            [aperture_w, wt / 2.0 + 0.4, aperture_h],
            at=(x_center - aperture_w / 2.0, -0.2, z_peak - aperture_h / 2.0),
        )
        lid_catch = lid_tab - aperture

        hook_w = aperture_w - 2 * gap
        hook_h = aperture_h * 0.7
        hook_d = wt / 2.0
        hook_stud = block(
            [hook_w, hook_d, hook_h],
            at=(x_center - hook_w / 2.0, 0.0, z_peak - aperture_h / 2.0),
        )
        body_catch_cut = body_cut - hook_stud

    elif catch_type == CatchType.MAGNET:
        from pybosl2 import cylinder

        m_diam = min(spec.magnet_diameter, eff_size * 2.0 if eff_size > 0 else 4.0, wt * 1.5)
        m_depth = min(spec.magnet_height, max(0.8, lt * 0.7))
        clr = 0.1
        pocket_body = cylinder(height=m_depth, radius=m_diam / 2.0 + clr, **precision_kwargs()).translate(
            [x_center, wt / 2.0, body_height - m_depth / 2.0]
        )
        pocket_lid = cylinder(height=m_depth, radius=m_diam / 2.0 + clr, **precision_kwargs()).translate(
            [x_center, wt / 2.0, body_height + m_depth / 2.0]
        )
        body_catch_cut = body_cut | pocket_body
        lid_catch = lid_tab - pocket_lid

    elif catch_type == CatchType.LEAF_SPRING:
        from pyboxbuilder.box.shell import block

        bead_depth = min(eff_size, wt / 2.0)
        ridge_poly = polygon(path=Path2D([
            (wt / 2.0, 0.0),
            (wt / 2.0 + bead_depth, slope_height),
            (wt / 2.0, slope_height),
        ]))
        ridge = (
            ridge_poly.linear_extrude(height=catch_width * 0.6)
            .rotate([0, 90, 0])
            .rotate([-90, 0, 0])
            .scale([1, -1, -1])
            .translate([x_center - catch_width * 0.3, 0, z_peak - slope_height])
        )
        slit_w = 0.8
        slit_h = catch_height * 0.8
        slit_d = wt + 0.4
        slit1 = block(
            [slit_w, slit_d, slit_h],
            at=(x_center - catch_width * 0.35, -0.2, body_height - catch_height),
        )
        slit2 = block(
            [slit_w, slit_d, slit_h],
            at=(x_center + catch_width * 0.35 - slit_w, -0.2, body_height - catch_height),
        )
        lid_catch = (lid_tab | ridge) - (slit1 | slit2)

        groove_poly = polygon(path=Path2D([
            (wt / 2.0 - 0.1, 0.0),
            (wt / 2.0 + bead_depth + gap, slope_height + 1.0 + gap),
            (wt / 2.0 - 0.1, slope_height + 1.0 + gap),
        ]))
        groove = (
            groove_poly.linear_extrude(height=catch_width * 0.6 + 2 * gap)
            .rotate([0, 90, 0])
            .rotate([-90, 0, 0])
            .scale([1, -1, -1])
            .translate([x_center - catch_width * 0.3 - gap, 0, z_peak - slope_height - 1.0 - gap])
        )
        body_catch_cut = body_cut | groove

    else:
        return Closure()

    return Closure(body_cut=body_catch_cut, lid=lid_catch)


def _front_wall_backing_boss(
    spec: BoxSpec,
    x_center: float,
    boss_w: float,
    boss_t: float,
    z_flat: float,
) -> Bosl2Solid | None:
    """Return a support-free 45°-tapered internal backing boss on the front wall (y = 0..boss_t)."""
    from pybosl2 import Path2D
    from pybosl2.shapes2d import polygon

    wt = spec.wall_thickness
    ft = spec.floor_thickness
    body_h = spec.height - spec.lid_thickness
    if boss_t <= wt + 0.05:
        return None
    w_clamped = min(spec.width - 2.0 * wt, boss_w)
    if w_clamped <= 1.0:
        return None
    z_f = max(ft, min(body_h - 1.0, z_flat))
    z_bot = max(ft, z_f - (boss_t - wt))
    pts = [
        (wt * 0.5, z_bot),
        (wt, z_bot),
        (boss_t, z_f),
        (boss_t, body_h),
        (wt * 0.5, body_h),
    ]
    poly = polygon(path=Path2D(pts))
    return (
        poly.linear_extrude(height=w_clamped)
        .rotate([0, 90, 0])
        .rotate([-90, 0, 0])
        .scale([1, -1, -1])
        .translate([x_center - w_clamped / 2.0, 0.0, 0.0])
    )


def _lid_front_wall_backing_boss(
    spec: BoxSpec,
    x_center: float,
    boss_w: float,
    boss_t: float,
    z_flat_top: float | None = None,
) -> Bosl2Solid | None:
    """Return a support-free 45°-tapered internal backing boss on the lid's front wall (z >= body_h)."""
    from pybosl2 import Path2D
    from pybosl2.shapes2d import polygon

    wt = spec.wall_thickness
    lt = spec.lid_thickness
    body_h = spec.height - lt
    if boss_t <= wt + 0.05:
        return None
    w_clamped = min(spec.width - 2.0 * wt, boss_w)
    if w_clamped <= 1.0:
        return None
    z_f = body_h + lt if z_flat_top is None else max(body_h + lt * 0.5, z_flat_top)
    z_top = z_f + (boss_t - wt)
    pts = [
        (wt * 0.5, body_h),
        (boss_t, body_h),
        (boss_t, z_f),
        (wt, z_top),
        (wt * 0.5, z_top),
    ]
    poly = polygon(path=Path2D(pts))
    return (
        poly.linear_extrude(height=w_clamped)
        .rotate([0, 90, 0])
        .rotate([-90, 0, 0])
        .scale([1, -1, -1])
        .translate([x_center - w_clamped / 2.0, 0.0, 0.0])
    )


def build_vertical_slide_across_hinge_catch(spec: BoxSpec) -> Closure:
    """Return a vertical-wall print-in-place horizontal dovetail sliding bolt catch.

    Places the captive dovetail slider inside the upright body wall below ``body_h``
    with an upward L-hook that engages a strike mortise in the vertical lid wall.
    Supports both ``slide_catch_style="front"`` and ``slide_catch_style="card_library"``.
    """
    from pybosl2 import Path2D
    from pybosl2.shapes2d import polygon

    from pyboxbuilder.box.shell import block
    from pyboxbuilder.compartments.element import union_all

    wt = spec.wall_thickness
    lt = spec.lid_thickness
    ft = spec.floor_thickness
    body_h = spec.height - lt
    pip_clr = max(0.22, min(0.35, getattr(spec, "pip_radial_clearance", 0.28)))
    style = getattr(spec, "slide_catch_style", "front")

    if style in ("card_library", "card_library_vertical"):
        # Dual side-wall vertical-face horizontal dovetail sliders along Y + front step
        y_latch = min(spec.length * 0.35, max(wt * 4.0, 14.0))
        chan_len = min(spec.length * 0.35, max(12.0, wt * 5.0))
        slider_len = chan_len * 0.56
        travel = max(1.8, (chan_len - slider_len) * 0.5 - pip_clr)
        track_h = min(max(4.5, (body_h - ft) * 0.42), 7.5)
        track_d = min(wt * 0.72, max(1.1, wt - 0.5))
        z_track_bot = max(ft + 0.8, body_h - track_h)
        lug_len = slider_len * 0.45
        ledge_h = max(0.55, lt * 0.35)
        z_hook_top = body_h + lt * 0.75
        bridge_t = min(0.65, track_d * 0.35)
        s_depth = max(0.75, track_d - pip_clr)

        body_cuts = []
        body_sliders = []
        lid_cuts = []

        for is_right in (False, True):
            x_cut0 = (spec.width - track_d) if is_right else -0.1
            x_s0 = (spec.width - s_depth) if is_right else 0.0
            x_hook0 = (spec.width - s_depth) if is_right else (bridge_t + pip_clr)
            x_mort0 = (spec.width - s_depth - pip_clr) if is_right else bridge_t

            b_track = block(
                [track_d + 0.1, chan_len, track_h + 0.1],
                at=(x_cut0, y_latch - chan_len / 2.0, z_track_bot),
            )
            body_cuts.append(b_track)

            s_core = block(
                [s_depth, slider_len, track_h - 2 * pip_clr],
                at=(x_s0, y_latch - slider_len / 2.0, z_track_bot + pip_clr),
            )
            stalk_len = lug_len * 0.55
            s_stalk = block(
                [s_depth - bridge_t - pip_clr, stalk_len, z_hook_top - (z_track_bot + pip_clr)],
                at=(x_hook0, y_latch - lug_len * 0.5, z_track_bot + pip_clr),
            )
            s_finger = block(
                [s_depth - bridge_t - pip_clr, lug_len, z_hook_top - (body_h + ledge_h + pip_clr)],
                at=(x_hook0, y_latch - lug_len * 0.5, body_h + ledge_h + pip_clr),
            )
            body_sliders.append(s_core | s_stalk | s_finger)

            l_entry = block(
                [s_depth - bridge_t + 2 * pip_clr, stalk_len + travel + 2 * pip_clr, lt * 0.8 + 2 * pip_clr],
                at=(x_mort0, y_latch - lug_len * 0.5 - travel - pip_clr, body_h - 0.1),
            )
            l_locked = block(
                [
                    s_depth - bridge_t + 2 * pip_clr,
                    lug_len + 2 * pip_clr,
                    (z_hook_top - (body_h + ledge_h)) + 2 * pip_clr,
                ],
                at=(x_mort0, y_latch - lug_len * 0.5 - pip_clr, body_h + ledge_h),
            )
            lid_cuts.append(l_entry | l_locked)

        all_body_cut = union_all(body_cuts)
        all_sliders = union_all(body_sliders)
        all_lid_cut = union_all(lid_cuts)
        return Closure(
            body=all_sliders,
            body_cut=all_body_cut,
            lid_cut=all_lid_cut,
        )

    # Front vertical-wall dovetail slide-across catch
    x_center = spec.width / 2.0
    chan_w = min(spec.width * 0.45, max(14.0, wt * 7.0))
    slider_w = chan_w * 0.54
    travel = max(2.0, (chan_w - slider_w) * 0.5 - pip_clr)
    track_h = min(max(4.8, (body_h - ft) * 0.42), 8.0)
    track_d = min(wt * 0.75, max(1.2, wt - 0.5))
    z_track_bot = max(ft + 0.8, body_h - track_h)
    z_mid = (z_track_bot + body_h) / 2.0
    dovetail_flare = min(0.65, track_h * 0.18)

    boss_t = max(wt, track_d + 1.2)
    boss = _front_wall_backing_boss(
        spec,
        x_center=x_center,
        boss_w=chan_w + 2.0 * wt,
        boss_t=boss_t,
        z_flat=z_track_bot - 1.0,
    )

    def _horiz_dovetail_x(x0: float, w_x: float, depth_y: float, h_front: float, h_back: float) -> Bosl2Solid:
        pts = [
            (0.0, z_mid - h_front / 2.0),
            (depth_y, z_mid - h_back / 2.0),
            (depth_y, z_mid + h_back / 2.0),
            (0.0, z_mid + h_front / 2.0),
        ]
        return (
            polygon(path=Path2D(pts))
            .linear_extrude(height=w_x)
            .rotate([0, 90, 0])
            .rotate([-90, 0, 0])
            .scale([1, -1, -1])
            .translate([x0, 0.0, 0.0])
        )

    h_front_cut = track_h - 2 * dovetail_flare
    track_cut = _horiz_dovetail_x(
        x_center - chan_w / 2.0, chan_w, track_d, h_front_cut, track_h
    )
    front_clear = block(
        [chan_w, 0.1, h_front_cut],
        at=(x_center - chan_w / 2.0, -0.1, z_mid - h_front_cut / 2.0),
    )

    lug_w = slider_w * 0.52
    stalk_w = lug_w * 0.55
    lid_bridge_t = min(0.7, track_d * 0.35)
    s_depth = max(0.8, track_d - pip_clr)
    top_neck_slot = block(
        [lug_w + travel + 2 * pip_clr, track_d - lid_bridge_t + 0.1, (body_h - z_mid) + 0.2],
        at=(x_center - lug_w * 0.5 - travel - pip_clr, lid_bridge_t, z_mid),
    )
    body_cut = track_cut | front_clear | top_neck_slot

    # Captive dovetail slider + upward L-hook
    slider_core = _horiz_dovetail_x(
        x_center - slider_w / 2.0,
        slider_w,
        s_depth,
        max(1.2, h_front_cut - 2 * pip_clr),
        max(1.6, track_h - 2 * pip_clr),
    )
    ledge_h = max(0.55, lt * 0.35)
    z_hook_top = body_h + lt * 0.75
    hook_y_span = max(0.5, s_depth - lid_bridge_t - pip_clr)
    hook_stalk = block(
        [stalk_w, hook_y_span, z_hook_top - z_mid],
        at=(x_center - lug_w * 0.5, lid_bridge_t + pip_clr, z_mid),
    )
    hook_finger = block(
        [lug_w, hook_y_span, z_hook_top - (body_h + ledge_h + pip_clr)],
        at=(x_center - lug_w * 0.5, lid_bridge_t + pip_clr, body_h + ledge_h + pip_clr),
    )
    slider = slider_core | hook_stalk | hook_finger
    body_solid = slider if boss is None else ((boss - body_cut) | slider)

    # Lid strike mortise (open entry slot at x - travel, undercut locked pocket at x_center)
    lid_entry_slot = block(
        [stalk_w + travel + 2 * pip_clr, hook_y_span + 2 * pip_clr, lt * 0.8 + 2 * pip_clr],
        at=(x_center - lug_w * 0.5 - travel - pip_clr, lid_bridge_t, body_h - 0.1),
    )
    lid_locked_mortise = block(
        [
            lug_w + 2 * pip_clr,
            hook_y_span + 2 * pip_clr,
            (z_hook_top - (body_h + ledge_h)) + 2 * pip_clr,
        ],
        at=(x_center - lug_w * 0.5 - pip_clr, lid_bridge_t, body_h + ledge_h),
    )
    lid_cut = lid_entry_slot | lid_locked_mortise
    lid_boss = _lid_front_wall_backing_boss(
        spec, x_center=x_center, boss_w=chan_w + 2.0 * wt, boss_t=boss_t
    )
    return Closure(
        body=body_solid,
        body_cut=body_cut,
        lid=None if lid_boss is None else (lid_boss - lid_cut),
        lid_cut=lid_cut,
    )


def build_vertical_pinch_slide_hinge_catch(spec: BoxSpec) -> Closure:
    """Return dual opposing captive horizontal dovetail sliders in the vertical body wall."""
    from pybosl2 import Path2D
    from pybosl2.shapes2d import polygon

    from pyboxbuilder.box.shell import block
    from pyboxbuilder.compartments.element import union_all

    wt = spec.wall_thickness
    lt = spec.lid_thickness
    ft = spec.floor_thickness
    body_h = spec.height - lt
    pip_clr = max(0.22, min(0.35, getattr(spec, "pip_radial_clearance", 0.28)))
    x_center = spec.width / 2.0

    chan_w = min(spec.width * 0.62, max(20.0, wt * 10.0))
    half_span = (chan_w - 2.0 * wt) / 2.0
    slider_w = half_span * 0.62
    travel = max(1.8, half_span - slider_w - 2 * pip_clr)
    track_h = min(max(4.8, (body_h - ft) * 0.42), 8.0)
    track_d = min(wt * 0.75, max(1.2, wt - 0.5))
    z_track_bot = max(ft + 0.8, body_h - track_h)
    z_mid = (z_track_bot + body_h) / 2.0
    dovetail_flare = min(0.65, track_h * 0.18)

    boss_t = max(wt, track_d + 1.2)
    boss = _front_wall_backing_boss(
        spec,
        x_center=x_center,
        boss_w=chan_w + 2.0 * wt,
        boss_t=boss_t,
        z_flat=z_track_bot - 1.0,
    )

    def _horiz_dovetail_x(x0: float, w_x: float, depth_y: float, h_front: float, h_back: float) -> Bosl2Solid:
        pts = [
            (0.0, z_mid - h_front / 2.0),
            (depth_y, z_mid - h_back / 2.0),
            (depth_y, z_mid + h_back / 2.0),
            (0.0, z_mid + h_front / 2.0),
        ]
        return (
            polygon(path=Path2D(pts))
            .linear_extrude(height=w_x)
            .rotate([0, 90, 0])
            .rotate([-90, 0, 0])
            .scale([1, -1, -1])
            .translate([x0, 0.0, 0.0])
        )

    h_front_cut = track_h - 2 * dovetail_flare
    track_cut = _horiz_dovetail_x(
        x_center - chan_w / 2.0, chan_w, track_d, h_front_cut, track_h
    )
    front_clear = block(
        [chan_w, 0.1, h_front_cut],
        at=(x_center - chan_w / 2.0, -0.1, z_mid - h_front_cut / 2.0),
    )

    lug_w = slider_w * 0.52
    stalk_w = lug_w * 0.55
    lid_bridge_t = min(0.7, track_d * 0.35)
    s_depth = max(0.8, track_d - pip_clr)
    hook_y_span = max(0.5, s_depth - lid_bridge_t - pip_clr)
    ledge_h = max(0.55, lt * 0.35)
    z_hook_top = body_h + lt * 0.75

    top_slots = []
    sliders = []
    lid_cuts = []

    for sign in (-1.0, 1.0):
        x_locked = x_center + sign * (wt * 0.4 + travel + slider_w / 2.0)
        s_core = _horiz_dovetail_x(
            x_locked - slider_w / 2.0,
            slider_w,
            s_depth,
            max(1.2, h_front_cut - 2 * pip_clr),
            max(1.6, track_h - 2 * pip_clr),
        )
        # Stalk sits on the inner side of lug_w, finger reaches outward
        if sign < 0:
            x_stalk0 = x_locked + lug_w * 0.5 - stalk_w
            x_finger0 = x_locked - lug_w * 0.5
            x_slot_min = x_finger0 - pip_clr
            x_entry_min = x_stalk0 - pip_clr
        else:
            x_stalk0 = x_locked - lug_w * 0.5
            x_finger0 = x_locked - lug_w * 0.5
            x_slot_min = x_finger0 - travel - pip_clr
            x_entry_min = x_stalk0 - travel - pip_clr

        top_slots.append(
            block(
                [lug_w + travel + 2 * pip_clr, track_d - lid_bridge_t + 0.1, (body_h - z_mid) + 0.2],
                at=(x_slot_min, lid_bridge_t, z_mid),
            )
        )
        h_stalk = block(
            [stalk_w, hook_y_span, z_hook_top - z_mid],
            at=(x_stalk0, lid_bridge_t + pip_clr, z_mid),
        )
        h_finger = block(
            [lug_w, hook_y_span, z_hook_top - (body_h + ledge_h + pip_clr)],
            at=(x_finger0, lid_bridge_t + pip_clr, body_h + ledge_h + pip_clr),
        )
        sliders.append(s_core | h_stalk | h_finger)

        l_entry = block(
            [stalk_w + travel + 2 * pip_clr, hook_y_span + 2 * pip_clr, lt * 0.8 + 2 * pip_clr],
            at=(x_entry_min, lid_bridge_t, body_h - 0.1),
        )
        l_locked = block(
            [
                lug_w + 2 * pip_clr,
                hook_y_span + 2 * pip_clr,
                (z_hook_top - (body_h + ledge_h)) + 2 * pip_clr,
            ],
            at=(x_finger0 - pip_clr, lid_bridge_t, body_h + ledge_h),
        )
        lid_cuts.append(l_entry | l_locked)

    body_cut = track_cut | front_clear | union_all(top_slots)
    all_sliders = union_all(sliders)
    body_solid = all_sliders if boss is None else ((boss - body_cut) | all_sliders)
    all_lid_cut = union_all(lid_cuts)
    lid_boss = _lid_front_wall_backing_boss(
        spec, x_center=x_center, boss_w=chan_w + 2.0 * wt, boss_t=boss_t
    )
    return Closure(
        body=body_solid,
        body_cut=body_cut,
        lid=None if lid_boss is None else (lid_boss - all_lid_cut),
        lid_cut=all_lid_cut,
    )


def build_vertical_rotary_bolt_hinge_catch(spec: BoxSpec) -> Closure:
    """Return a flush quarter-turn rotary cam disk mounted in the vertical body front wall."""
    from pybosl2 import cylinder

    from pyboxbuilder.box.shell import block

    wt = spec.wall_thickness
    lt = spec.lid_thickness
    ft = spec.floor_thickness
    body_h = spec.height - lt
    pip_clr = max(0.22, min(0.35, getattr(spec, "pip_radial_clearance", 0.28)))
    x_center = spec.width / 2.0

    pivot_drop = min(max(2.6, (body_h - ft) * 0.24), 4.2)
    z_pivot = max(ft + 2.2, body_h - pivot_drop)
    r_disk = min(pivot_drop - 0.35, 2.4)
    r_waist = max(1.1, r_disk - 0.85)
    recess_d = min(0.9, wt * 0.42)
    cone_len = max(1.0, r_disk - r_waist)
    boss_t = max(wt, recess_d + 2.0 * cone_len + 0.8)
    y_waist = recess_d + cone_len

    boss = _front_wall_backing_boss(
        spec,
        x_center=x_center,
        boss_w=max(12.0, 4.0 * r_disk + 2.0 * wt),
        boss_t=boss_t,
        z_flat=z_pivot - r_disk - 1.2,
    )

    bore_front_cone = (
        cylinder(
            height=cone_len + pip_clr,
            radius1=r_disk + pip_clr,
            radius2=r_waist + pip_clr,
            **precision_kwargs(),
        )
        .rotate([-90, 0, 0])
        .translate([x_center, recess_d + (cone_len - pip_clr) / 2.0, z_pivot])
    )
    bore_back_cone = (
        cylinder(
            height=cone_len + pip_clr,
            radius1=r_waist + pip_clr,
            radius2=r_disk + pip_clr,
            **precision_kwargs(),
        )
        .rotate([-90, 0, 0])
        .translate([x_center, y_waist + (cone_len + pip_clr) / 2.0, z_pivot])
    )
    front_bore = (
        cylinder(height=recess_d + pip_clr + 0.1, radius=r_disk + pip_clr, **precision_kwargs())
        .rotate([-90, 0, 0])
        .translate([x_center, (recess_d + pip_clr - 0.1) / 2.0, z_pivot])
    )
    cam_w = min(3.8, r_disk * 1.5)
    lid_bridge_t = min(0.75, recess_d)
    cam_y1 = min(boss_t - 0.4, recess_d + 1.4)
    upper_slot_body = block(
        [cam_w + 2 * pip_clr, (cam_y1 - lid_bridge_t) + 2 * pip_clr, body_h - z_pivot + 0.2],
        at=(x_center - cam_w / 2.0 - pip_clr, lid_bridge_t, z_pivot),
    )
    body_cut = bore_front_cone | bore_back_cone | front_bore | upper_slot_body

    shaft_front = (
        cylinder(height=cone_len, radius1=r_disk, radius2=r_waist, **precision_kwargs())
        .rotate([-90, 0, 0])
        .translate([x_center, recess_d + cone_len / 2.0, z_pivot])
    )
    shaft_back = (
        cylinder(height=cone_len, radius1=r_waist, radius2=r_disk, **precision_kwargs())
        .rotate([-90, 0, 0])
        .translate([x_center, y_waist + cone_len / 2.0, z_pivot])
    )
    face_t = max(0.55, recess_d - pip_clr)
    face_disk = (
        cylinder(height=face_t, radius=r_disk, **precision_kwargs())
        .rotate([-90, 0, 0])
        .translate([x_center, face_t / 2.0, z_pivot])
    )
    coin_slot = block(
        [r_disk * 1.4, face_t * 0.65, 0.8],
        at=(x_center - r_disk * 0.7, -0.05, z_pivot - 0.4),
    )
    z_cam_top = body_h + max(1.0, lt * 0.75)
    cam_bolt = block(
        [cam_w, max(0.55, cam_y1 - (lid_bridge_t + pip_clr)), z_cam_top - z_pivot],
        at=(x_center - cam_w / 2.0, lid_bridge_t + pip_clr, z_pivot),
    )
    rotor = (face_disk - coin_slot) | shaft_front | shaft_back | cam_bolt
    body_solid = rotor if boss is None else ((boss - body_cut) | rotor)

    lid_cut = block(
        [
            cam_w + 2 * pip_clr,
            (cam_y1 - lid_bridge_t) + 2 * pip_clr,
            (z_cam_top - body_h) + pip_clr + 0.1,
        ],
        at=(x_center - cam_w / 2.0 - pip_clr, lid_bridge_t, body_h - 0.05),
    )
    lid_boss = _lid_front_wall_backing_boss(
        spec, x_center=x_center, boss_w=max(12.0, 4.0 * r_disk + 2.0 * wt), boss_t=boss_t
    )
    return Closure(
        body=body_solid,
        body_cut=body_cut,
        lid=None if lid_boss is None else (lid_boss - lid_cut),
        lid_cut=lid_cut,
    )


def build_slide_across_hinge_catch(spec: BoxSpec) -> Closure:
    """Return a captive print-in-place horizontal dovetail sliding bolt catch (card_library style).

    Supports ``slide_catch_style="front"`` (centered front-wall dovetail bolt) and
    ``slide_catch_style="card_library"`` (dual side-wall sliding bolts + front lip).
    """
    from pybosl2.shapes3d import prismoid

    from pyboxbuilder.box.shell import block

    wt = spec.wall_thickness
    lt = spec.lid_thickness
    body_h = spec.height - lt
    pip_clr = max(0.22, min(0.35, getattr(spec, "pip_radial_clearance", 0.28)))
    style = getattr(spec, "slide_catch_style", "front")

    if style == "card_library":
        # Dual side-wall sliding dovetail bolts at y_pos near front + front retaining lip
        y_latch = min(spec.length * 0.32, max(wt * 3.5, 12.0))
        chan_len = min(spec.length * 0.35, max(12.0, wt * 5.0))
        slider_len = chan_len * 0.58
        travel = max(2.0, (chan_len - slider_len) * 0.5 - pip_clr)
        slot_w = min(wt * 2.2, max(3.6, spec.width * 0.14))
        lug_drop = min(wt * 0.85, max(1.2, (body_h - spec.floor_thickness) * 0.2))
        roof_h = min(0.9, max(0.6, wt * 0.4))

        body_cuts = []
        lid_cuts = []
        lid_parts = []

        for is_right in (False, True):
            x_wall = spec.width - wt if is_right else 0.0
            x_chan0 = (spec.width - wt - slot_w) if is_right else wt
            # Body side-wall L-mortise: open entry at y_latch - travel, undercut roof at y_latch
            mortise_locked = block(
                [wt + 0.2, slider_len * 0.55 + 2 * pip_clr, lug_drop + 2 * pip_clr],
                at=(
                    x_wall - 0.1,
                    y_latch - slider_len * 0.275 - pip_clr,
                    body_h - roof_h - lug_drop - pip_clr,
                ),
            )
            mortise_entry = block(
                [wt + 0.2, travel + slider_len * 0.45 + 2 * pip_clr, roof_h + lug_drop + 0.2],
                at=(
                    x_wall - 0.1,
                    y_latch - slider_len * 0.275 - travel - pip_clr,
                    body_h - roof_h - lug_drop - pip_clr,
                ),
            )
            body_cuts.append(mortise_locked | mortise_entry)

            # Lid window cut for captive slider thumb slot
            win_cut = block(
                [slot_w * 0.6, chan_len - 2.0, lt + 0.2],
                at=(x_chan0 + slot_w * 0.2, y_latch - (chan_len - 2.0) / 2.0, body_h - 0.1),
            )
            side_notch = block(
                [wt + 0.2, chan_len, lt + 0.2],
                at=(x_wall - 0.1, y_latch - chan_len / 2.0, body_h - 0.1),
            )
            lid_cuts.append(win_cut | side_notch)

            # Captive dovetail slider & guide rails inside lid
            rail_l = block(
                [slot_w * 0.25, chan_len, lt],
                at=(x_chan0, y_latch - chan_len / 2.0, body_h),
            )
            rail_r = block(
                [slot_w * 0.25, chan_len, lt],
                at=(x_chan0 + slot_w * 0.75, y_latch - chan_len / 2.0, body_h),
            )
            slider_body = prismoid(
                size1=[slot_w * 0.72 - 2 * pip_clr, slider_len],
                size2=[slot_w * 0.48 - 2 * pip_clr, slider_len],
                height=max(0.8, lt - pip_clr),
            ).translate([x_chan0 + slot_w * 0.5, y_latch, body_h + pip_clr])
            stalk_w = max(0.8, wt * 0.6)
            stalk_x = (spec.width - wt - pip_clr - stalk_w) if is_right else (wt + pip_clr)
            lug_x = (spec.width - wt + pip_clr) if is_right else pip_clr
            # Vertical stalk stays inside the box interior (clear of the side-wall roof),
            # and horizontal bolt foot extends outward into mortise_locked below body_h - roof_h.
            slider_stalk = block(
                [stalk_w, slider_len * 0.5, lug_drop + roof_h + 2 * pip_clr],
                at=(
                    stalk_x,
                    y_latch - slider_len * 0.25,
                    body_h - roof_h - lug_drop,
                ),
            )
            bolt_foot_w = (wt - 2 * pip_clr) + pip_clr + stalk_w
            bolt_foot_x = stalk_x if is_right else lug_x
            slider_lug = block(
                [bolt_foot_w, slider_len * 0.5, lug_drop],
                at=(
                    bolt_foot_x,
                    y_latch - slider_len * 0.25,
                    body_h - roof_h - lug_drop,
                ),
            )
            arm_x0 = min(stalk_x, x_chan0 + slot_w * 0.35)
            arm_x1 = max(stalk_x + stalk_w, x_chan0 + slot_w * 0.65)
            slider_arm = block(
                [arm_x1 - arm_x0, slider_len * 0.5, max(0.8, lt * 0.6)],
                at=(
                    arm_x0,
                    y_latch - slider_len * 0.25,
                    body_h + pip_clr,
                ),
            )
            lid_parts.append(rail_l | rail_r | slider_body | slider_arm | slider_stalk | slider_lug)

        # Front retaining lip on lid overlapping a shallow step on front wall
        lip_w = min(spec.width * 0.45, max(10.0, spec.width - 4 * wt))
        lip_h = min(lt * 1.2, max(1.6, (body_h - spec.floor_thickness) * 0.2))
        x_lip0 = (spec.width - lip_w) / 2.0
        front_step = block(
            [lip_w + 2 * pip_clr, wt * 0.5 + pip_clr, lip_h + pip_clr],
            at=(x_lip0 - pip_clr, -0.05, body_h - lip_h - pip_clr),
        )
        body_cuts.append(front_step)
        front_lip = block(
            [lip_w, wt * 0.5 - pip_clr, lip_h + lt],
            at=(x_lip0, 0.0, body_h - lip_h),
        )
        lid_parts.append(front_lip)

        from pyboxbuilder.compartments.element import union_all

        all_body_cut = union_all(body_cuts)
        front_boss = _front_wall_backing_boss(
            spec,
            x_center=spec.width / 2.0,
            boss_w=lip_w + 2 * wt,
            boss_t=wt + 0.8,
            z_flat=body_h - lip_h - 1.0,
        )
        return Closure(
            body=None if front_boss is None else (front_boss - all_body_cut),
            body_cut=all_body_cut,
            lid_cut=union_all(lid_cuts),
            lid=union_all(lid_parts),
        )

    # Default style == "front": Centered front-wall captive dovetail slide-across catch
    x_center = spec.width / 2.0
    chan_w = min(spec.width * 0.45, max(14.0, wt * 7.0))
    slider_w = chan_w * 0.54
    travel = max(2.2, (chan_w - slider_w) * 0.5 - pip_clr)
    chan_d = min(spec.length * 0.22, max(wt * 2.4, 5.2))
    lug_w = slider_w * 0.58
    lug_h = min(1.8, max(1.0, (body_h - spec.floor_thickness) * 0.18))
    roof_h = min(1.0, max(0.7, wt * 0.4))
    mortise_d = min(wt * 0.65, max(1.0, wt - 0.6))

    boss_t = max(wt, mortise_d + 1.2)
    boss = _front_wall_backing_boss(
        spec,
        x_center=x_center,
        boss_w=chan_w + 2.0 * wt,
        boss_t=boss_t,
        z_flat=body_h - roof_h - lug_h - 1.2,
    )

    # Body front wall L-mortise on the inner face (y in [wt - mortise_d, boss_t + 0.2]):
    # - Locked pocket under retaining bridge roof at x in [x_center - lug_w/2, x_center + lug_w/2]
    # - Open-top drop-in entry notch shifted by -travel along X
    y_mort0 = wt - mortise_d
    mort_span_y = boss_t - y_mort0 + 0.2
    locked_mortise = block(
        [lug_w + 2 * pip_clr, mort_span_y, lug_h + 2 * pip_clr],
        at=(
            x_center - lug_w / 2.0 - pip_clr,
            y_mort0,
            body_h - roof_h - lug_h - pip_clr,
        ),
    )
    entry_notch = block(
        [travel + lug_w * 0.6 + 2 * pip_clr, mort_span_y, roof_h + lug_h + 0.3],
        at=(
            x_center - lug_w / 2.0 - travel - pip_clr,
            y_mort0,
            body_h - roof_h - lug_h - pip_clr,
        ),
    )
    body_cut = locked_mortise | entry_notch

    # Lid window and captive 45° dovetail slider
    rail_y = max(0.9, chan_d * 0.22)
    win_cut = block(
        [chan_w, chan_d, lt + 0.2],
        at=(x_center - chan_w / 2.0, 0.0, body_h - 0.1),
    )

    # Front and rear fixed dovetail rails on the lid
    rail_front = block(
        [chan_w, rail_y, lt],
        at=(x_center - chan_w / 2.0, 0.0, body_h),
    )
    rail_back = block(
        [chan_w, rail_y, lt],
        at=(x_center - chan_w / 2.0, chan_d - rail_y, body_h),
    )
    end_left = block(
        [max(0.8, wt * 0.5), chan_d, lt],
        at=(x_center - chan_w / 2.0, 0.0, body_h),
    )
    end_right = block(
        [max(0.8, wt * 0.5), chan_d, lt],
        at=(x_center + chan_w / 2.0 - max(0.8, wt * 0.5), 0.0, body_h),
    )
    lid_frame = rail_front | rail_back | end_left | end_right

    # Captive dovetail slider (separated from lid_frame by pip_clr)
    inner_y_bot = (chan_d - 2 * rail_y) + 0.6 - 2 * pip_clr
    inner_y_top = (chan_d - 2 * rail_y) - 2 * pip_clr
    slider_core = prismoid(
        size1=[slider_w, max(0.8, inner_y_bot)],
        size2=[slider_w, max(0.6, inner_y_top)],
        height=max(0.8, lt - pip_clr),
    ).translate([x_center, chan_d / 2.0, body_h + pip_clr])

    # Thumb handle bar rising flush to spec.height
    thumb_knob = block(
        [slider_w * 0.45, max(0.6, inner_y_top), max(0.8, lt - pip_clr)],
        at=(x_center - slider_w * 0.225, (chan_d - max(0.6, inner_y_top)) / 2.0, body_h + pip_clr),
    )
    # L-shaped locking lug: vertical stalk inside the box (y >= boss_t + pip_clr)
    # and horizontal foot reaching forward (-Y) into locked_mortise below body_h - roof_h.
    stalk_t = max(0.8, wt * 0.45)
    y_stalk0 = boss_t + pip_clr
    arm_y0 = min(chan_d * 0.5, y_stalk0)
    arm_y1 = max(chan_d * 0.5, y_stalk0 + stalk_t)
    lug_arm = block(
        [lug_w, arm_y1 - arm_y0, max(0.6, lt * 0.5 - pip_clr)],
        at=(x_center - lug_w / 2.0, arm_y0, body_h + pip_clr),
    )
    lug_stalk = block(
        [lug_w, stalk_t, roof_h + lug_h + 2 * pip_clr],
        at=(x_center - lug_w / 2.0, y_stalk0, body_h - roof_h - lug_h),
    )
    y_foot0 = y_mort0 + pip_clr
    lug_foot = block(
        [lug_w, (y_stalk0 + stalk_t) - y_foot0, lug_h],
        at=(x_center - lug_w / 2.0, y_foot0, body_h - roof_h - lug_h),
    )
    slider = slider_core | thumb_knob | lug_arm | lug_stalk | lug_foot

    return Closure(
        body=None if boss is None else (boss - body_cut),
        body_cut=body_cut,
        lid_cut=win_cut,
        lid=lid_frame | slider,
    )


def build_slide_up_hinge_catch(spec: BoxSpec) -> Closure:
    """Return a captive print-in-place vertical dovetail slider catch on the front wall.

    The slider is trapped in a vertical dovetail track on the body's front face (``y = 0``).
    Sliding it UP (``+Z``) drives its top locking tongue behind the lid's front bridge;
    sliding it DOWN (``-Z``) drops the tongue below ``body_height`` to release the lid.
    """
    from pybosl2 import Path2D
    from pybosl2.shapes2d import polygon
    from pybosl2.shapes3d import sphere

    from pyboxbuilder.box.shell import block

    wt = spec.wall_thickness
    lt = spec.lid_thickness
    ft = spec.floor_thickness
    body_h = spec.height - lt
    pip_clr = max(0.22, min(0.35, getattr(spec, "pip_radial_clearance", 0.28)))
    x_center = spec.width / 2.0

    track_w = min(spec.width * 0.35, max(10.0, wt * 5.0))
    track_h = min(max(6.5, (body_h - ft) * 0.55), 11.0)
    track_d = min(wt * 0.75, max(1.2, wt - 0.5))
    z_track_bot = max(ft + 0.8, body_h - track_h)
    stop_h = min(1.6, track_h * 0.22)
    travel_z = min(2.4, max(1.4, (track_h - stop_h) * 0.32))
    slider_h = max(2.2, (body_h - stop_h - z_track_bot) - travel_z - 2 * pip_clr)
    dovetail_flare = min(0.8, track_d * 0.45)

    boss_t = max(wt, track_d + 1.2)
    boss = _front_wall_backing_boss(
        spec,
        x_center=x_center,
        boss_w=track_w + 2.0 * wt,
        boss_t=boss_t,
        z_flat=z_track_bot - 1.0,
    )

    def _dovetail_prism_z(w_front: float, w_back: float, depth: float, z0: float, h: float) -> Bosl2Solid:
        pts = [
            (-w_front / 2.0, 0.0),
            (w_front / 2.0, 0.0),
            (w_back / 2.0, depth),
            (-w_back / 2.0, depth),
        ]
        return polygon(path=Path2D(pts)).linear_extrude(height=h).translate([x_center, 0.0, z0])

    # Lower dovetail track cavity (from z_track_bot up to body_h - stop_h)
    lower_cut = _dovetail_prism_z(
        track_w,
        track_w + 2 * dovetail_flare,
        track_d,
        z_track_bot,
        body_h - z_track_bot - stop_h + 0.05,
    )
    # Upper stepped-in neck cavity (from body_h - stop_h to body_h + 0.1) that traps the wider slider base
    neck_w = track_w * 0.68
    upper_cut = _dovetail_prism_z(
        neck_w,
        neck_w + 2 * dovetail_flare,
        track_d,
        body_h - stop_h,
        stop_h + 0.1,
    )
    front_clear = block(
        [track_w, 0.1, body_h - z_track_bot + 0.1],
        at=(x_center - track_w / 2.0, -0.1, z_track_bot),
    )

    # Detent dimple at locked (top) position on back wall of track
    r_det = 0.35
    z_Slider_locked_bot = body_h - stop_h - pip_clr - slider_h
    z_det = z_Slider_locked_bot + slider_h * 0.5
    det_dimple = sphere(radius=r_det + pip_clr * 0.5, **precision_kwargs()).translate(
        [x_center, track_d, z_det]
    )
    body_cut = lower_cut | upper_cut | front_clear | det_dimple

    # Captive vertical dovetail slider (positioned at top/locked state in preview)
    s_depth = max(0.8, track_d - pip_clr)
    slider_base = _dovetail_prism_z(
        track_w - 2 * pip_clr,
        track_w + 2 * dovetail_flare - 2 * pip_clr,
        s_depth,
        z_Slider_locked_bot,
        slider_h,
    )
    # Upper locking tongue rising through the neck up to body_h + lt * 0.72
    tongue_top = body_h + lt * 0.72
    tongue_h = tongue_top - z_Slider_locked_bot
    tongue_w = neck_w - 2 * pip_clr
    slider_tongue = _dovetail_prism_z(
        tongue_w,
        tongue_w + 2 * dovetail_flare * 0.7,
        s_depth,
        z_Slider_locked_bot,
        tongue_h,
    )
    # Detent bead on back of slider
    det_bead = sphere(radius=r_det, **precision_kwargs()).translate(
        [x_center, s_depth, z_det]
    )
    slider = slider_base | slider_tongue | det_bead

    body_solid = slider if boss is None else ((boss - body_cut) | slider)

    # Lid strike mortise receiving the upper portion of slider_tongue behind a front retaining bridge
    lid_front_bridge_t = min(0.8, track_d * 0.35)
    # Trim the very top-front of slider_tongue above body_h so the lid's front bridge fits in front of it
    front_trim = block(
        [tongue_w + 2.0, lid_front_bridge_t + pip_clr, lt + 0.5],
        at=(x_center - tongue_w / 2.0 - 1.0, -0.1, body_h - pip_clr),
    )
    body_solid = body_solid - front_trim

    lid_mortise = block(
        [
            tongue_w + 2 * dovetail_flare + 2 * pip_clr,
            s_depth - lid_front_bridge_t + 2 * pip_clr,
            lt * 0.75 + pip_clr,
        ],
        at=(
            x_center - (tongue_w + 2 * dovetail_flare) / 2.0 - pip_clr,
            lid_front_bridge_t,
            body_h - 0.05,
        ),
    )

    return Closure(
        body=body_solid,
        body_cut=body_cut,
        lid_cut=lid_mortise,
    )


def build_spin_hinge_catch(spec: BoxSpec) -> Closure:
    """Return a print-in-place rotary spin catch (turn-button cam latch) on the front wall.

    Uses a 45° double-cone hourglass bearing in the body's front wall (``y = 0``).
    When spun UP (``0°``), the upper cam hook engages the lid's front catch ledge;
    when spun DOWN (``90°–180°``), the cam swings below ``body_height`` to release the lid.
    """
    from pybosl2 import cylinder
    from pybosl2.shapes3d import sphere

    from pyboxbuilder.box.shell import block

    wt = spec.wall_thickness
    lt = spec.lid_thickness
    ft = spec.floor_thickness
    body_h = spec.height - lt
    pip_clr = max(0.22, min(0.35, getattr(spec, "pip_radial_clearance", 0.28)))
    x_center = spec.width / 2.0

    # Pivot axis along Y at z_pivot below the rim
    pivot_drop = min(max(2.6, (body_h - ft) * 0.24), 4.2)
    z_pivot = max(ft + 2.2, body_h - pivot_drop)
    r_hub = min(pivot_drop - 0.35, 2.4)
    r_waist = max(1.1, r_hub - 0.9)

    recess_d = min(1.0, wt * 0.45)
    cone_len = max(1.1, r_hub - r_waist)
    boss_t = max(wt, recess_d + 2.0 * cone_len + 0.8)
    y_waist = recess_d + cone_len

    boss = _front_wall_backing_boss(
        spec,
        x_center=x_center,
        boss_w=max(12.0, 4.0 * r_hub + 2.0 * wt),
        boss_t=boss_t,
        z_flat=z_pivot - r_hub - 1.2,
    )

    # 1. Hourglass double-45°-cone bearing bore in body front wall
    bore_front_cone = (
        cylinder(
            height=cone_len + pip_clr,
            radius1=r_hub + pip_clr,
            radius2=r_waist + pip_clr,
            **precision_kwargs(),
        )
        .rotate([-90, 0, 0])
        .translate([x_center, recess_d + (cone_len - pip_clr) / 2.0, z_pivot])
    )
    bore_back_cone = (
        cylinder(
            height=cone_len + pip_clr,
            radius1=r_waist + pip_clr,
            radius2=r_hub + pip_clr,
            **precision_kwargs(),
        )
        .rotate([-90, 0, 0])
        .translate([x_center, y_waist + (cone_len + pip_clr) / 2.0, z_pivot])
    )
    bore_back_cap = (
        cylinder(
            height=pip_clr + 0.1,
            radius=r_hub + pip_clr,
            **precision_kwargs(),
        )
        .rotate([-90, 0, 0])
        .translate([x_center, y_waist + cone_len + (pip_clr + 0.1) / 2.0, z_pivot])
    )

    # Front paddle clearance recess on y = 0..recess_d
    wing_r = min(spec.width * 0.2, max(4.5, r_hub * 2.1))
    paddle_recess_cyl = (
        cylinder(
            height=recess_d + pip_clr + 0.1,
            radius=wing_r + pip_clr,
            **precision_kwargs(),
        )
        .rotate([-90, 0, 0])
        .translate([x_center, (recess_d + pip_clr - 0.1) / 2.0, z_pivot])
    )
    # Trim paddle_recess_cyl above body_h so it only cuts the body
    paddle_recess = paddle_recess_cyl & block(
        [spec.width, recess_d + pip_clr + 0.2, body_h + 0.1],
        at=(0.0, -0.1, 0.0),
    )
    # Upper hook clearance slot at top of body front wall (z in [z_pivot, body_h])
    cam_w = min(4.2, r_hub * 1.6)
    hook_reach_y = min(wt * 0.85, recess_d + 0.9)
    upper_slot_body = block(
        [cam_w + 2 * pip_clr, hook_reach_y + pip_clr + 0.1, body_h - z_pivot + 0.2],
        at=(x_center - cam_w / 2.0 - pip_clr, -0.1, z_pivot),
    )
    r_det = 0.32
    det_dimple = sphere(radius=r_det + pip_clr * 0.5, **precision_kwargs()).translate(
        [x_center, recess_d + pip_clr, z_pivot + r_hub + 0.5]
    )
    body_cut = bore_front_cone | bore_back_cone | bore_back_cap | paddle_recess | upper_slot_body | det_dimple

    # 2. Captive hourglass shaft + spin paddle + upper cam hook (in locked 0° up orientation)
    shaft_front = (
        cylinder(
            height=cone_len,
            radius1=r_hub,
            radius2=r_waist,
            **precision_kwargs(),
        )
        .rotate([-90, 0, 0])
        .translate([x_center, recess_d + cone_len / 2.0, z_pivot])
    )
    shaft_back = (
        cylinder(
            height=cone_len,
            radius1=r_waist,
            radius2=r_hub,
            **precision_kwargs(),
        )
        .rotate([-90, 0, 0])
        .translate([x_center, y_waist + cone_len / 2.0, z_pivot])
    )
    paddle_t = max(0.55, recess_d - pip_clr)
    hub_disk = (
        cylinder(height=paddle_t, radius=r_hub, **precision_kwargs())
        .rotate([-90, 0, 0])
        .translate([x_center, paddle_t / 2.0, z_pivot])
    )
    # Bilateral thumb lever bar for spinning down/up
    wing_h = max(1.6, r_hub * 0.85)
    thumb_wings = block(
        [wing_r * 1.85, paddle_t, wing_h],
        at=(x_center - wing_r * 0.925, 0.0, z_pivot - wing_h / 2.0),
    )
    # Upper cam arm & inward hook lip reaching into the lid front slot above z = body_h
    z_hook_ledge = body_h + max(0.55, lt * 0.38)
    z_cam_top = body_h + max(1.1, lt * 0.78)
    cam_arm = block(
        [cam_w, paddle_t, z_cam_top - z_pivot],
        at=(x_center - cam_w / 2.0, 0.0, z_pivot),
    )
    hook_lip = block(
        [cam_w, hook_reach_y, z_cam_top - z_hook_ledge],
        at=(x_center - cam_w / 2.0, 0.0, z_hook_ledge),
    )
    det_bead = sphere(radius=r_det, **precision_kwargs()).translate(
        [x_center, paddle_t, z_pivot + r_hub + 0.5]
    )
    rotor = shaft_front | shaft_back | hub_disk | thumb_wings | cam_arm | hook_lip | det_bead
    body_solid = rotor if boss is None else ((boss - body_cut) | rotor)

    # 3. Lid front slot: clears cam_arm (y in [0, paddle_t + pip_clr]) and hook_lip
    # (z >= z_hook_ledge - pip_clr), leaving the solid lid catch ledge at
    # y in [paddle_t + pip_clr, hook_reach_y], z in [body_h, z_hook_ledge - pip_clr]!
    lid_front_slot = block(
        [cam_w + 2 * pip_clr, paddle_t + pip_clr + 0.1, lt + 0.2],
        at=(x_center - cam_w / 2.0 - pip_clr, -0.1, body_h - 0.1),
    )
    lid_hook_pocket = block(
        [
            cam_w + 2 * pip_clr,
            hook_reach_y + pip_clr + 0.1,
            (z_cam_top - z_hook_ledge) + 2 * pip_clr,
        ],
        at=(
            x_center - cam_w / 2.0 - pip_clr,
            -0.1,
            z_hook_ledge - pip_clr,
        ),
    )
    lid_cut = lid_front_slot | lid_hook_pocket

    return Closure(
        body=body_solid,
        body_cut=body_cut,
        lid_cut=lid_cut,
    )


def build_push_button_hinge_catch(spec: BoxSpec, *, vertical_wall: bool = False) -> Closure:
    """Return a compliant thumb-press push-button release catch on the front wall."""
    from pyboxbuilder.box.shell import block

    wt = spec.wall_thickness
    lt = spec.lid_thickness
    ft = spec.floor_thickness
    body_h = spec.height - lt
    clr = 0.2
    x_center = spec.width / 2.0

    btn_w = min(spec.width * 0.32, max(9.0, wt * 4.5))
    btn_h = min(max(5.5, (body_h - ft) * 0.48), 9.5)
    slit_w = 0.8
    beam_t = min(1.2, wt * 0.55)
    hook_d = min(0.7, wt * 0.35)
    hook_h = min(1.4, lt * 0.7)

    boss_t = max(wt, beam_t + hook_d + 1.8)
    boss = _front_wall_backing_boss(
        spec,
        x_center=x_center,
        boss_w=btn_w + 2 * slit_w + 2 * wt,
        boss_t=boss_t,
        z_flat=body_h - btn_h - 1.0,
    )

    # U-slit & deflection pocket behind the compliant button beam
    slit_left = block(
        [slit_w, beam_t + hook_d + 0.6, btn_h + 0.1],
        at=(x_center - btn_w / 2.0 - slit_w, -0.1, body_h - btn_h),
    )
    slit_right = block(
        [slit_w, beam_t + hook_d + 0.6, btn_h + 0.1],
        at=(x_center + btn_w / 2.0, -0.1, body_h - btn_h),
    )
    flex_pocket = block(
        [btn_w + 2 * slit_w, hook_d + 0.8, btn_h + 0.1],
        at=(x_center - btn_w / 2.0 - slit_w, beam_t, body_h - btn_h),
    )
    body_cut = slit_left | slit_right | flex_pocket

    # Lid downward catch loop that hooks behind the compliant button's top rim
    loop_w = btn_w - 2 * clr
    loop_d = hook_d
    loop_drop = min(3.2, btn_h * 0.48)
    lid_stalk = block(
        [loop_w, loop_d, loop_drop + lt * 0.5],
        at=(x_center - loop_w / 2.0, beam_t + clr, body_h - loop_drop),
    )
    lid_barb = block(
        [loop_w, hook_d * 0.8, hook_h],
        at=(x_center - loop_w / 2.0, beam_t - hook_d * 0.8 + clr, body_h - loop_drop),
    )
    # Matching hook recess on the inner face of the button beam
    beam_hook_cut = block(
        [loop_w + 2 * clr, hook_d + clr, hook_h + 2 * clr],
        at=(x_center - loop_w / 2.0 - clr, beam_t - hook_d, body_h - loop_drop - clr),
    )
    body_cut = body_cut | beam_hook_cut

    lid_part = lid_stalk | lid_barb
    if vertical_wall:
        l_boss = _lid_front_wall_backing_boss(
            spec,
            x_center=x_center,
            boss_w=btn_w + 2 * wt,
            boss_t=max(wt, beam_t + clr + loop_d + 0.4),
        )
        if l_boss is not None:
            lid_part = lid_part | l_boss

    return Closure(
        body=None if boss is None else (boss - body_cut),
        body_cut=body_cut,
        lid=lid_part,
    )


def build_toggle_latch_hinge_catch(spec: BoxSpec) -> Closure:
    """Return a print-in-place articulated draw-latch bail on the front wall."""
    from pybosl2 import cylinder

    from pyboxbuilder.box.shell import block

    wt = spec.wall_thickness
    lt = spec.lid_thickness
    ft = spec.floor_thickness
    body_h = spec.height - lt
    pip_clr = max(0.22, min(0.35, getattr(spec, "pip_radial_clearance", 0.28)))
    x_center = spec.width / 2.0

    bail_w = min(spec.width * 0.34, max(10.0, wt * 5.0))
    bail_h = min(max(5.5, (body_h - ft) * 0.48), 9.0)
    r_piv = min(1.3, wt * 0.55)
    z_piv = max(ft + r_piv + 0.8, body_h - bail_h + r_piv)
    recess_d = min(1.2, wt * 0.6)

    boss_t = max(wt, recess_d + 2 * r_piv + 1.0)
    boss = _front_wall_backing_boss(
        spec,
        x_center=x_center,
        boss_w=bail_w + 2 * wt,
        boss_t=boss_t,
        z_flat=z_piv - r_piv - 1.0,
    )

    body_recess = block(
        [bail_w + 2 * pip_clr, recess_d + 0.1, body_h - (z_piv - r_piv - pip_clr) + 0.1],
        at=(x_center - bail_w / 2.0 - pip_clr, -0.1, z_piv - r_piv - pip_clr),
    )
    # Fixed pivot cones on the left and right walls of body_recess at z_piv
    cone_h = 1.1
    left_cone = (
        cylinder(height=cone_h, radius1=r_piv, radius2=0.2, **precision_kwargs())
        .rotate([0, 90, 0])
        .translate([x_center - bail_w / 2.0 - pip_clr + cone_h / 2.0, recess_d * 0.5, z_piv])
    )
    right_cone = (
        cylinder(height=cone_h, radius1=r_piv, radius2=0.2, **precision_kwargs())
        .rotate([0, -90, 0])
        .translate([x_center + bail_w / 2.0 + pip_clr - cone_h / 2.0, recess_d * 0.5, z_piv])
    )

    # Captive U-shaped bail loop pivoted on the cones and hooking into the lid front slot
    arm_w = max(1.2, bail_w * 0.2)
    bail_t = max(0.7, recess_d - pip_clr)
    z_bail_top = body_h + lt * 0.72
    hub_bar = (
        cylinder(height=bail_w - 2 * pip_clr, radius=r_piv, **precision_kwargs())
        .rotate([0, 90, 0])
        .translate([x_center, recess_d * 0.5, z_piv])
    )
    sock_l = (
        cylinder(height=cone_h + pip_clr, radius1=r_piv + pip_clr, radius2=0.2, **precision_kwargs())
        .rotate([0, 90, 0])
        .translate([x_center - bail_w / 2.0 - pip_clr + (cone_h + pip_clr) / 2.0, recess_d * 0.5, z_piv])
    )
    sock_r = (
        cylinder(height=cone_h + pip_clr, radius1=r_piv + pip_clr, radius2=0.2, **precision_kwargs())
        .rotate([0, -90, 0])
        .translate([x_center + bail_w / 2.0 + pip_clr - (cone_h + pip_clr) / 2.0, recess_d * 0.5, z_piv])
    )
    hub_piv = (hub_bar - sock_l - sock_r) & block(
        [bail_w - 2 * pip_clr, recess_d - pip_clr, 2 * r_piv],
        at=(x_center - bail_w / 2.0 + pip_clr, 0.0, z_piv - r_piv),
    )
    left_arm = block(
        [arm_w, bail_t, z_bail_top - z_piv],
        at=(x_center - bail_w / 2.0 + pip_clr, 0.0, z_piv),
    )
    right_arm = block(
        [arm_w, bail_t, z_bail_top - z_piv],
        at=(x_center + bail_w / 2.0 - pip_clr - arm_w, 0.0, z_piv),
    )
    top_crossbar = block(
        [bail_w - 2 * pip_clr, recess_d + 0.5, lt * 0.38],
        at=(x_center - bail_w / 2.0 + pip_clr, 0.0, z_bail_top - lt * 0.38),
    )
    bail = hub_piv | left_arm | right_arm | top_crossbar

    piv_mounts = left_cone | right_cone
    body_solid = (piv_mounts | bail) if boss is None else ((boss - body_recess) | piv_mounts | bail)

    # Lid front slot with central catch stud under top_crossbar
    lid_arm_cut_l = block(
        [arm_w + 2 * pip_clr, bail_t + pip_clr + 0.1, lt + 0.2],
        at=(x_center - bail_w / 2.0, -0.1, body_h - 0.1),
    )
    lid_arm_cut_r = block(
        [arm_w + 2 * pip_clr, bail_t + pip_clr + 0.1, lt + 0.2],
        at=(x_center + bail_w / 2.0 - arm_w - 2 * pip_clr, -0.1, body_h - 0.1),
    )
    lid_top_cut = block(
        [bail_w + 2 * pip_clr, recess_d + 0.5 + pip_clr + 0.1, lt * 0.38 + 2 * pip_clr],
        at=(x_center - bail_w / 2.0 - pip_clr, -0.1, z_bail_top - lt * 0.38 - pip_clr),
    )
    lid_cut = lid_arm_cut_l | lid_arm_cut_r | lid_top_cut

    return Closure(
        body=body_solid,
        body_cut=body_recess,
        lid_cut=lid_cut,
    )


def build_pinch_slide_hinge_catch(spec: BoxSpec) -> Closure:
    """Return dual opposing captive dovetail sliders that pinch toward the center to release."""
    from pybosl2.shapes3d import prismoid

    from pyboxbuilder.box.shell import block

    wt = spec.wall_thickness
    lt = spec.lid_thickness
    body_h = spec.height - lt
    pip_clr = max(0.22, min(0.35, getattr(spec, "pip_radial_clearance", 0.28)))
    x_center = spec.width / 2.0

    chan_w = min(spec.width * 0.62, max(20.0, wt * 10.0))
    chan_d = min(spec.length * 0.22, max(wt * 2.4, 5.2))
    half_span = (chan_w - 2.0 * wt) / 2.0
    slider_w = half_span * 0.62
    travel = max(1.8, half_span - slider_w - 2 * pip_clr)
    lug_w = slider_w * 0.55
    lug_h = min(1.6, max(1.0, (body_h - spec.floor_thickness) * 0.18))
    roof_h = min(0.9, max(0.65, wt * 0.4))
    mortise_d = min(wt * 0.65, max(1.0, wt - 0.6))

    boss_t = max(wt, mortise_d + 1.2)
    boss = _front_wall_backing_boss(
        spec,
        x_center=x_center,
        boss_w=chan_w + 2 * wt,
        boss_t=boss_t,
        z_flat=body_h - roof_h - lug_h - 1.2,
    )

    body_cuts = []
    sliders = []
    rail_y = max(0.9, chan_d * 0.22)
    inner_y_bot = (chan_d - 2 * rail_y) + 0.6 - 2 * pip_clr
    inner_y_top = (chan_d - 2 * rail_y) - 2 * pip_clr

    y_mort0 = wt - mortise_d
    mort_span_y = boss_t - y_mort0 + 0.2
    stalk_t = max(0.8, wt * 0.45)
    y_stalk0 = boss_t + pip_clr
    y_foot0 = y_mort0 + pip_clr

    for sign in (-1.0, 1.0):
        # Outer locked position of each slider center
        x_locked = x_center + sign * (wt * 0.5 + travel + slider_w / 2.0)
        x_lug = x_locked + sign * (slider_w - lug_w) * 0.4

        locked_mortise = block(
            [lug_w + 2 * pip_clr, mort_span_y, lug_h + 2 * pip_clr],
            at=(
                x_lug - lug_w / 2.0 - pip_clr,
                y_mort0,
                body_h - roof_h - lug_h - pip_clr,
            ),
        )
        # Entry notch shifted inward toward x_center by travel
        x_entry_min = min(x_lug - lug_w / 2.0, x_lug - sign * travel - lug_w / 2.0) - pip_clr
        entry_notch = block(
            [travel + lug_w + 2 * pip_clr, mort_span_y, roof_h + lug_h + 0.3],
            at=(
                x_entry_min,
                y_mort0,
                body_h - roof_h - lug_h - pip_clr,
            ),
        )
        body_cuts.append(locked_mortise | entry_notch)

        s_core = prismoid(
            size1=[slider_w, max(0.8, inner_y_bot)],
            size2=[slider_w, max(0.6, inner_y_top)],
            height=max(0.8, lt - pip_clr),
        ).translate([x_locked, chan_d / 2.0, body_h + pip_clr])
        arm_y0 = min(chan_d * 0.5, y_stalk0)
        arm_y1 = max(chan_d * 0.5, y_stalk0 + stalk_t)
        s_arm = block(
            [lug_w, arm_y1 - arm_y0, max(0.6, lt * 0.5 - pip_clr)],
            at=(x_lug - lug_w / 2.0, arm_y0, body_h + pip_clr),
        )
        s_stalk = block(
            [lug_w, stalk_t, roof_h + lug_h + 2 * pip_clr],
            at=(x_lug - lug_w / 2.0, y_stalk0, body_h - roof_h - lug_h),
        )
        s_foot = block(
            [lug_w, (y_stalk0 + stalk_t) - y_foot0, lug_h],
            at=(x_lug - lug_w / 2.0, y_foot0, body_h - roof_h - lug_h),
        )
        sliders.append(s_core | s_arm | s_stalk | s_foot)

    win_cut = block(
        [chan_w, chan_d, lt + 0.2],
        at=(x_center - chan_w / 2.0, 0.0, body_h - 0.1),
    )
    rail_front = block([chan_w, rail_y, lt], at=(x_center - chan_w / 2.0, 0.0, body_h))
    rail_back = block([chan_w, rail_y, lt], at=(x_center - chan_w / 2.0, chan_d - rail_y, body_h))
    end_l = block([wt * 0.5, chan_d, lt], at=(x_center - chan_w / 2.0, 0.0, body_h))
    end_r = block([wt * 0.5, chan_d, lt], at=(x_center + chan_w / 2.0 - wt * 0.5, 0.0, body_h))
    lid_frame = rail_front | rail_back | end_l | end_r

    from pyboxbuilder.compartments.element import union_all

    all_body_cut = union_all(body_cuts)
    return Closure(
        body=None if boss is None else (boss - all_body_cut),
        body_cut=all_body_cut,
        lid_cut=win_cut,
        lid=lid_frame | union_all(sliders),
    )


def build_rotary_bolt_hinge_catch(spec: BoxSpec) -> Closure:
    """Return a flush print-in-place quarter-turn rotary cam disk inside the lid."""
    from pybosl2 import cylinder

    from pyboxbuilder.box.shell import block

    wt = spec.wall_thickness
    lt = spec.lid_thickness
    body_h = spec.height - lt
    pip_clr = max(0.22, min(0.35, getattr(spec, "pip_radial_clearance", 0.28)))
    x_center = spec.width / 2.0

    r_disk = min(spec.width * 0.16, spec.length * 0.14, max(3.6, wt * 2.0))
    r_waist = max(2.2, r_disk - min(0.8, lt * 0.4))
    cam_drop = min(1.8, max(1.0, (body_h - spec.floor_thickness) * 0.18))
    roof_h = min(0.9, max(0.65, wt * 0.4))
    mortise_d = min(wt * 0.65, max(0.9, wt - 0.6))

    boss_t = max(wt, mortise_d + 1.2)
    y_disk = max(wt + r_disk + 0.4, boss_t + r_waist * 0.65 + pip_clr + 0.2)
    boss = _front_wall_backing_boss(
        spec,
        x_center=x_center,
        boss_w=2.0 * r_disk + 2.0 * wt,
        boss_t=boss_t,
        z_flat=body_h - roof_h - cam_drop - 1.2,
    )

    # Undercut cam slot in the inside face of the front wall (y in [wt - mortise_d, boss_t + 0.5])
    # leaving the outer face y = 0 completely unbroken!
    cam_w = max(2.2, r_waist * 0.9)
    body_mortise = block(
        [r_disk * 1.8, boss_t - (wt - mortise_d) + 0.5, cam_drop + 2 * pip_clr],
        at=(
            x_center - r_disk * 0.9,
            wt - mortise_d,
            body_h - roof_h - cam_drop - pip_clr,
        ),
    )

    # Hourglass double-cone bore in the lid plate around (x_center, y_disk, body_h..spec.height)
    half_lt = lt / 2.0
    lid_bore_bot = cylinder(
        height=half_lt + 0.05,
        radius1=r_disk + pip_clr,
        radius2=r_waist + pip_clr,
        **precision_kwargs(),
    ).translate([x_center, y_disk, body_h + half_lt / 2.0 - 0.025])
    lid_bore_top = cylinder(
        height=half_lt + 0.05,
        radius1=r_waist + pip_clr,
        radius2=r_disk + pip_clr,
        **precision_kwargs(),
    ).translate([x_center, y_disk, body_h + half_lt + half_lt / 2.0 + 0.025])
    lid_cut = lid_bore_bot | lid_bore_top

    # Captive rotary cam disk + lower eccentric locking tongue reaching forward into body_mortise
    disk_bot = cylinder(
        height=half_lt,
        radius1=r_disk,
        radius2=r_waist,
        **precision_kwargs(),
    ).translate([x_center, y_disk, body_h + half_lt / 2.0])
    disk_top = cylinder(
        height=half_lt,
        radius1=r_waist,
        radius2=r_disk,
        **precision_kwargs(),
    ).translate([x_center, y_disk, body_h + half_lt + half_lt / 2.0])
    coin_slot = block(
        [r_disk * 1.3, 1.0, half_lt * 0.7],
        at=(x_center - r_disk * 0.65, y_disk - 0.5, spec.height - half_lt * 0.6),
    )
    disk = (disk_bot | disk_top) - coin_slot

    cam_stalk = cylinder(
        height=roof_h + cam_drop,
        radius=r_waist * 0.65,
        **precision_kwargs(),
    ).translate([x_center, y_disk, body_h - (roof_h + cam_drop) / 2.0])
    cam_tongue = block(
        [cam_w, (y_disk - (wt - mortise_d + pip_clr)), cam_drop],
        at=(
            x_center - cam_w / 2.0,
            wt - mortise_d + pip_clr,
            body_h - roof_h - cam_drop,
        ),
    )
    rotor = disk | cam_stalk | cam_tongue

    return Closure(
        body=None if boss is None else (boss - body_mortise),
        body_cut=body_mortise,
        lid_cut=lid_cut,
        lid=rotor,
    )


def magnetic_hinge_catch_metrics(spec: BoxSpec) -> tuple[float, float, float]:
    """Return ``(x_center, y_center, r_boss)`` for a hinged box's front magnet catch."""
    wt = spec.wall_thickness
    md = min(float(spec.magnet_diameter), spec.width * 0.35, spec.length * 0.25)
    clr = 0.1
    r_pocket = md / 2.0 + clr
    front_skin = max(0.8, wt * 0.4)
    x_center = spec.width / 2.0
    y_center = max(wt / 2.0, front_skin + r_pocket)
    wall_ring = max(1.2, wt * 0.5)
    r_boss = r_pocket + wall_ring
    return x_center, y_center, r_boss


def magnetic_hinge_catch(spec: BoxSpec) -> Closure:
    """Return the front magnet boss and matching body/lid magnet sockets for a hinged box."""
    from pybosl2 import Path2D, cylinder
    from pybosl2.shapes2d import polygon

    from pyboxbuilder.box.shell import block

    wt = spec.wall_thickness
    lt = spec.lid_thickness
    ft = spec.floor_thickness
    body_height = spec.height - lt

    md = min(float(spec.magnet_diameter), spec.width * 0.35, spec.length * 0.25)
    mh = min(float(spec.magnet_height), max(0.8, (body_height - ft) * 0.35))
    clr = 0.1
    r_pocket = md / 2.0 + clr
    x_center, y_center, r_boss = magnetic_hinge_catch_metrics(spec)

    # Preserve a solid top skin above the lid pocket so the lid's top surface stays unbroken
    top_skin = max(0.6, min(0.8, lt * 0.4))
    lid_pocket_depth = min(mh + clr, max(0.6, lt - top_skin))
    extra_for_lid = max(0.0, (mh + clr) - lid_pocket_depth)
    body_pocket_depth = min(
        mh + clr + extra_for_lid + 0.1,
        max(1.0, body_height - ft - 1.2),
    )

    z_boss_flat = max(ft, body_height - body_pocket_depth - 1.0)
    protrusion = max(0.0, (y_center + r_boss) - wt)
    z_taper_bot = max(ft, z_boss_flat - protrusion)
    col_h = body_height - z_taper_bot

    cyl_col = cylinder(
        height=col_h, radius=r_boss, **precision_kwargs()
    ).translate([x_center, y_center, z_taper_bot + col_h / 2.0])
    web_col = block(
        [2.0 * r_boss, max(0.1, y_center - wt * 0.5), col_h],
        at=(x_center - r_boss, wt * 0.5, z_taper_bot),
    )
    boss = (cyl_col | web_col) & block(
        [spec.width - 2.0 * wt, spec.length - wt, col_h + 0.2],
        at=(wt, wt * 0.5, z_taper_bot - 0.1),
    )

    if z_boss_flat > z_taper_bot + 0.05 and protrusion > 0.05:
        bevel_poly = polygon(
            path=Path2D([
                (wt, z_taper_bot - 0.1),
                (y_center + r_boss + 1.0, z_taper_bot - 0.1),
                (y_center + r_boss + 1.0, z_boss_flat),
            ])
        )
        bevel_cut = (
            bevel_poly.linear_extrude(height=2.0 * r_boss + 2.0)
            .rotate([0, 90, 0])
            .rotate([-90, 0, 0])
            .scale([1, -1, -1])
            .translate([x_center - r_boss - 1.0, 0.0, 0.0])
        )
        boss = boss - bevel_cut

    h_body_cut = body_pocket_depth + 0.05
    pocket_body = cylinder(
        height=h_body_cut, radius=r_pocket, **precision_kwargs()
    ).translate([x_center, y_center, body_height + 0.05 - h_body_cut / 2.0])

    h_lid_cut = lid_pocket_depth + 0.05
    pocket_lid = cylinder(
        height=h_lid_cut, radius=r_pocket, **precision_kwargs()
    ).translate([x_center, y_center, body_height - 0.05 + h_lid_cut / 2.0])

    return Closure(body=boss, body_cut=pocket_body, lid_cut=pocket_lid)


# --------------------------------------------------------- stackable features (FR-101)


def _resolve_stackable_shape(spec: BoxSpec) -> StackableShape:
    """Return the effective StackableShape for a BoxSpec."""
    from pyboxbuilder.enums import StackableMode, StackableShape

    if spec.stackable_shape is not None:
        return spec.stackable_shape
    if spec.stackable is StackableMode.PATTERN:
        return StackableShape.PATTERN
    if spec.stackable in (StackableMode.PYRAMID, StackableMode.PERIMETER):
        return StackableShape.PYRAMID
    return StackableShape.PYRAMIDS


def _grown_xy(solid: Bosl2Solid, by: float, directions: int = 8) -> Bosl2Solid:
    """Return ``solid`` widened horizontally in XY by ``by`` mm."""
    if by <= 0.0:
        return solid
    import math

    grown = solid
    for i in range(directions):
        angle = 2.0 * math.pi * i / directions
        grown = grown | solid.translate([by * math.cos(angle), by * math.sin(angle), 0.0])
    return grown


def _resolve_stackable_pattern_params(
    spec: BoxSpec,
) -> tuple[PatternType, float, float | None, float]:
    """Return ``(pattern_type, border_mm, spacing, web)`` for pattern-matched stacking."""
    from pyboxbuilder.lid.builder import LID_BORDER_MM
    from pyboxbuilder.lid.pattern import DEFAULT_WEB_MM

    pat_type = getattr(spec, "stackable_pattern", None)
    if pat_type is None or pat_type in (PatternType.NONE, PatternType.SOLID):
        pat_type = PatternType.HEX

    wt = spec.wall_thickness
    req_border = getattr(spec, "stackable_pattern_border", None)
    base_border = LID_BORDER_MM if req_border is None else float(req_border)
    min_margin = wt + 1.5
    max_margin = max(min_margin, min(spec.width, spec.length) * 0.28)
    border = max(min_margin, min(base_border, max_margin))

    spacing = getattr(spec, "stackable_pattern_spacing", None)
    req_web = getattr(spec, "stackable_pattern_web", None)
    web = DEFAULT_WEB_MM if req_web is None else float(req_web)
    return pat_type, border, spacing, web


def _build_pattern_web_unit_slice(spec: BoxSpec) -> Bosl2Solid | None:
    """Build a 1.0 mm tall (z in [0, 1]) solid slice of the pattern web lattice for stacking."""
    from pybosl2 import cylinder

    from pyboxbuilder.box.shell import block
    from pyboxbuilder.lid.pattern import build_pattern

    pat_type, margin, spacing, web = _resolve_stackable_pattern_params(spec)
    area_w = spec.width - 2.0 * margin
    area_l = spec.length - 2.0 * margin
    if area_w < 4.0 or area_l < 4.0:
        return None

    h_slice = 2.0
    z_slice = -0.5
    holes = build_pattern(
        area_w,
        area_l,
        h_slice,
        pat_type,
        spacing=spacing,
        web=web,
        inlay=False,
        lid_thickness=h_slice,
    )
    if holes is None:
        return None

    hole_solid = holes.solid if hasattr(holes, "solid") and holes.solid is not None else holes
    if hole_solid is None:
        return None

    hole_solid = hole_solid.translate([margin, margin, z_slice])
    area_box = block([area_w, area_l, 1.0], at=(margin, margin, 0.0))
    web_slice = area_box - hole_solid

    # Keep clear of any sliding lid fingernail catch on both axes so the male ridge
    # never enters the nail dish and the female groove matches the ridge footprint.
    for axis in ("x", "y"):
        catch = fingernail_catch(spec, axis)
        if catch is not None:
            keepout = cylinder(
                height=3.0,
                radius=catch.keepout_radius + 0.4,
                **precision_kwargs(),
            ).translate([catch.centre[0], catch.centre[1], 0.5])
            web_slice = web_slice - keepout

    return web_slice


def build_pattern_stacking_ridge(
    spec: BoxSpec,
    base_z: float,
    depth: float | None = None,
    clearance: float | None = None,
    point_up: bool = True,
) -> Bosl2Solid | None:
    """Build the male pattern-matched stacking lattice ridge for a lid or tray top."""
    from pyboxbuilder.box.shell import block

    web_unit = _build_pattern_web_unit_slice(spec)
    if web_unit is None:
        return None

    clr = spec.stackable_fit_offset if clearance is None else clearance
    req_d = spec.stackable_foot_height if depth is None else depth
    h_female = min(req_d, max(0.6, spec.floor_thickness - 0.4))
    h_male = max(0.35, h_female - clr)
    eps = 0.05
    h_total = h_male + eps

    _pat_type, margin, _spacing, _web = _resolve_stackable_pattern_params(spec)
    inner_m = margin + clr
    inner_w = spec.width - 2.0 * inner_m
    inner_l = spec.length - 2.0 * inner_m
    if inner_w <= 1.0 or inner_l <= 1.0:
        return None

    clipped = web_unit & block([inner_w, inner_l, 2.0], at=(inner_m, inner_m, -0.5))
    z0 = (base_z - eps) if point_up else (base_z - h_male)
    return clipped.scale([1.0, 1.0, h_total]).translate([0.0, 0.0, z0])


def build_pattern_stacking_groove(
    spec: BoxSpec,
    surface_z: float = 0.0,
    depth: float | None = None,
    clearance: float | None = None,
    point_up: bool = True,
) -> Bosl2Solid | None:
    """Build the female pattern-matched stacking groove cutter for a box floor or lid.

    When ``point_up=True`` and ``surface_z=0.0``, the outer perimeter border AND all
    pattern tiles (hexagons, triangles, squares, rhombuses, etc.) sit 100% flat on
    the build plate at ``z = 0``, while only the narrow web channels between tiles
    are recessed into ``z in [0, h_female]`` with a 45-degree entry bevel.
    """
    from pyboxbuilder.box.shell import block

    web_unit = _build_pattern_web_unit_slice(spec)
    if web_unit is None:
        return None

    clr = spec.stackable_fit_offset if clearance is None else clearance
    req_d = spec.stackable_foot_height if depth is None else depth
    h_female = min(req_d, max(0.6, spec.floor_thickness - 0.4))
    eps = 0.05

    _pat_type, margin, _spacing, _web = _resolve_stackable_pattern_params(spec)
    inner_m = margin + clr
    inner_w = spec.width - 2.0 * inner_m
    inner_l = spec.length - 2.0 * inner_m
    if inner_w <= 1.0 or inner_l <= 1.0:
        return None

    male_xy = web_unit & block([inner_w, inner_l, 2.0], at=(inner_m, inner_m, -0.5))
    female_xy = _grown_xy(male_xy, clr + 0.03)
    bevel_h = min(0.35, h_female * 0.45)
    bevel_xy = _grown_xy(female_xy, bevel_h)

    if point_up:
        main_groove = female_xy.scale([1.0, 1.0, h_female + eps]).translate(
            [0.0, 0.0, surface_z - eps]
        )
        bevel_groove = bevel_xy.scale([1.0, 1.0, bevel_h + eps]).translate(
            [0.0, 0.0, surface_z - eps]
        )
    else:
        main_groove = female_xy.scale([1.0, 1.0, h_female + eps]).translate(
            [0.0, 0.0, surface_z - h_female]
        )
        bevel_groove = bevel_xy.scale([1.0, 1.0, bevel_h + eps]).translate(
            [0.0, 0.0, surface_z - bevel_h]
        )
    return main_groove | bevel_groove


def _pyramid_grid_metrics(
    foot_size: float,
    depth: float,
    clearance: float,
    pyramid_count: int | None = None,
    single_pyramid: bool = False,
) -> tuple[int, float, float, float, float, float, float]:
    """Compute 45-degree self-supporting pyramid grid parameters.

    Returns:
        (n, pitch, b_female, h_female, b_male, h_male, w_tip)
        where every pyramid wall slopes at >= 45 degrees from horizontal
        (<= 45 degrees overhang from vertical) and terminates at a tiny
        ``w_tip`` apex (<= 0.4 mm) so zero unsupported bridging occurs.
    """
    import math

    w_tip = min(0.4, max(0.15, foot_size * 0.08))
    if single_pyramid:
        n = 1
    elif pyramid_count is not None and pyramid_count >= 1:
        n = int(pyramid_count)
    else:
        n = max(2, math.ceil((foot_size - w_tip) / max(0.4, 2.0 * depth)))

    pitch = foot_size / float(n)
    b_female = min(pitch, 2.0 * depth + w_tip)
    h_female = max(0.3, (b_female - w_tip) / 2.0)
    b_male = max(w_tip + 0.2, b_female - 2.0 * clearance)
    h_male = max(0.2, h_female - clearance)
    return n, pitch, b_female, h_female, b_male, h_male, w_tip


def build_stacking_pyramids(
    width: float,
    length: float,
    foot_size: float,
    foot_height: float,
    foot_inset: float,
    clearance: float = 0.15,
    base_z: float = 0.0,
    pyramid_count: int | None = None,
    single_pyramid: bool = False,
    cone: bool = False,
    point_up: bool = True,
) -> Bosl2Solid:
    """Return 4 corner 45-degree pyramid (or multi-pyramid grid / cone) male bosses.

    Args:
        width: Box width in mm.
        length: Box length in mm.
        foot_size: Corner pad footprint width/length in mm.
        foot_height: Target height of pyramids in mm.
        foot_inset: Inset from outer box walls in mm.
        clearance: Lateral fit clearance offset per side in mm.
        base_z: Z coordinate of the mounting surface. When ``point_up=True``,
            pyramids protrude upward from ``base_z`` to ``base_z + h_male``.
            When ``point_up=False``, pyramids protrude downward from ``base_z``
            to ``base_z - h_male``.
        pyramid_count: Number of pyramids per side (N for an N x N grid per corner).
            When None, auto-computes N so every wall is at 45 degrees.
        single_pyramid: If True, builds a single 45-degree pyramid per corner (N=1).
        cone: If True, uses 45-degree conical frustums instead of square pyramids.
        point_up: If True, pyramids taper upward (+Z); if False, taper downward (-Z).
    """
    from pybosl2 import Anchor, cylinder
    from pybosl2.shapes3d import prismoid

    from pyboxbuilder.compartments.element import union_all

    n, pitch, _bf, _hf, b_male, h_male, w_tip = _pyramid_grid_metrics(
        foot_size,
        foot_height,
        clearance,
        pyramid_count=pyramid_count,
        single_pyramid=single_pyramid,
    )
    eps = 0.05
    b_root = b_male + 2.0 * eps
    h_total = h_male + eps

    positions = [
        (foot_inset, foot_inset),
        (width - foot_inset - foot_size, foot_inset),
        (foot_inset, length - foot_inset - foot_size),
        (width - foot_inset - foot_size, length - foot_inset - foot_size),
    ]
    solids = []
    for x0, y0 in positions:
        for i in range(n):
            for j in range(n):
                cx = x0 + (i + 0.5) * pitch
                cy = y0 + (j + 0.5) * pitch
                if point_up:
                    if cone:
                        p = cylinder(
                            height=h_total,
                            radius1=b_root / 2.0,
                            radius2=w_tip / 2.0,
                            anchor=Anchor.BOTTOM,
                            **precision_kwargs(),
                        ).translate([cx, cy, base_z - eps])
                    else:
                        p = prismoid(
                            [b_root, b_root],
                            [w_tip, w_tip],
                            height=h_total,
                            **precision_kwargs(),
                        ).translate([cx, cy, base_z - eps])
                else:
                    if cone:
                        p = cylinder(
                            height=h_total,
                            radius1=w_tip / 2.0,
                            radius2=b_root / 2.0,
                            anchor=Anchor.BOTTOM,
                            **precision_kwargs(),
                        ).translate([cx, cy, base_z - h_male])
                    else:
                        p = prismoid(
                            [w_tip, w_tip],
                            [b_root, b_root],
                            height=h_total,
                            **precision_kwargs(),
                        ).translate([cx, cy, base_z - h_male])
                solids.append(p)
    return union_all(solids)


def build_stacking_pyramid_indents(
    width: float,
    length: float,
    foot_size: float,
    indent_depth: float,
    foot_inset: float,
    clearance: float = 0.15,
    surface_z: float = 0.0,
    pyramid_count: int | None = None,
    single_pyramid: bool = False,
    cone: bool = False,
    point_up: bool = True,
) -> Bosl2Solid:
    """Return 4 corner 45-degree pyramid (or multi-pyramid grid / cone) female indent cutters.

    When ``point_up=True`` and ``surface_z=0.0``, the indents cut upward into the
    bottom floor from ``z = 0`` to ``z = h_female`` with 45-degree self-supporting
    walls and zero flat horizontal ceiling, making them 100% 3D-printer safe on the
    build plate without supports.
    """
    from pybosl2 import Anchor, cylinder
    from pybosl2.shapes3d import prismoid

    from pyboxbuilder.compartments.element import union_all

    n, pitch, b_female, h_female, _bm, _hm, w_tip = _pyramid_grid_metrics(
        foot_size,
        indent_depth,
        clearance,
        pyramid_count=pyramid_count,
        single_pyramid=single_pyramid,
    )
    eps = 0.05
    b_open = b_female + 2.0 * eps
    h_total = h_female + eps

    positions = [
        (foot_inset, foot_inset),
        (width - foot_inset - foot_size, foot_inset),
        (foot_inset, length - foot_inset - foot_size),
        (width - foot_inset - foot_size, length - foot_inset - foot_size),
    ]
    solids = []
    for x0, y0 in positions:
        for i in range(n):
            for j in range(n):
                cx = x0 + (i + 0.5) * pitch
                cy = y0 + (j + 0.5) * pitch
                if point_up:
                    if cone:
                        p = cylinder(
                            height=h_total,
                            radius1=b_open / 2.0,
                            radius2=w_tip / 2.0,
                            anchor=Anchor.BOTTOM,
                            **precision_kwargs(),
                        ).translate([cx, cy, surface_z - eps])
                    else:
                        p = prismoid(
                            [b_open, b_open],
                            [w_tip, w_tip],
                            height=h_total,
                            **precision_kwargs(),
                        ).translate([cx, cy, surface_z - eps])
                else:
                    if cone:
                        p = cylinder(
                            height=h_total,
                            radius1=w_tip / 2.0,
                            radius2=b_open / 2.0,
                            anchor=Anchor.BOTTOM,
                            **precision_kwargs(),
                        ).translate([cx, cy, surface_z - h_female])
                    else:
                        p = prismoid(
                            [w_tip, w_tip],
                            [b_open, b_open],
                            height=h_total,
                            **precision_kwargs(),
                        ).translate([cx, cy, surface_z - h_female])
                solids.append(p)
    return union_all(solids)


def build_stacking_feet(
    width: float,
    length: float,
    foot_size: float,
    foot_height: float,
    foot_inset: float,
    base_z: float = 0.0,
    chamfer: float = 0.6,
    shape: StackableShape | None = None,
    clearance: float = 0.15,
    pyramid_count: int | None = None,
    point_up: bool = False,
) -> Bosl2Solid:
    """Return 4 corner locator feet (FR-101).

    Args:
        width: Box width in mm.
        length: Box length in mm.
        foot_size: Width/length of each foot pad in mm.
        foot_height: Height of each foot in mm.
        foot_inset: Inset from box edges in mm.
        base_z: Z coordinate of the mounting face.
        chamfer: Edge chamfer size in mm when ``shape`` is ``StackableShape.FLAT``.
        shape: Geometry profile (``FLAT``, ``PYRAMID``, ``PYRAMIDS``, ``CONE``).
            Defaults to ``StackableShape.FLAT`` when called directly.
        clearance: Lateral fit clearance in mm for pyramid/cone sizing.
        pyramid_count: Number of pyramids per side when ``shape`` is ``PYRAMIDS``.
        point_up: When True, feet protrude upward (+Z) from ``base_z``; when False,
            feet protrude downward (-Z) from ``base_z``.

    Returns:
        Bosl2Solid: Union of the 4 corner feet.
    """
    from pybosl2 import Anchor, cuboid

    from pyboxbuilder.box.shell import block, corner
    from pyboxbuilder.compartments.element import union_all
    from pyboxbuilder.enums import StackableShape

    eff_shape = StackableShape.FLAT if shape is None else shape
    if eff_shape in (StackableShape.PYRAMID, StackableShape.PYRAMIDS, StackableShape.CONE):
        return build_stacking_pyramids(
            width=width,
            length=length,
            foot_size=foot_size,
            foot_height=foot_height,
            foot_inset=foot_inset,
            clearance=clearance,
            base_z=base_z,
            pyramid_count=pyramid_count,
            single_pyramid=(eff_shape is StackableShape.PYRAMID),
            cone=(eff_shape is StackableShape.CONE),
            point_up=point_up,
        )

    c = min(chamfer, foot_height * 0.45, foot_size * 0.45)
    solids = []
    positions = [
        (foot_inset, foot_inset),
        (width - foot_inset - foot_size, foot_inset),
        (foot_inset, length - foot_inset - foot_size),
        (width - foot_inset - foot_size, length - foot_inset - foot_size),
    ]
    z_bottom = base_z if point_up else (base_z - foot_height)
    edge_anchor = Anchor.TOP if point_up else Anchor.BOTTOM
    for x, y in positions:
        if c > 0.05:
            f = corner(
                cuboid([foot_size, foot_size, foot_height], chamfer=c, edges=[edge_anchor]),
                [foot_size, foot_size, foot_height],
                (x, y, z_bottom),
            )
        else:
            f = block([foot_size, foot_size, foot_height], at=(x, y, z_bottom))
        solids.append(f)

    return union_all(solids)


def build_stacking_indents(
    width: float,
    length: float,
    foot_size: float,
    indent_depth: float,
    foot_inset: float,
    clearance: float = 0.15,
    top_z: float = 0.0,
    shape: StackableShape | None = None,
    pyramid_count: int | None = None,
    point_up: bool = False,
) -> Bosl2Solid:
    """Return 4 corner indent cutter solids to be subtracted from floor or lid/rim (FR-101).

    Args:
        width: Box width in mm.
        length: Box length in mm.
        foot_size: Foot pad width in mm.
        indent_depth: Depth of each indent socket in mm.
        foot_inset: Inset from box edges in mm.
        clearance: Fit clearance offset per side in mm.
        top_z: Z coordinate of the reference surface.
        shape: Geometry profile (``FLAT``, ``PYRAMID``, ``PYRAMIDS``, ``CONE``).
            Defaults to ``StackableShape.FLAT`` when called directly.
        pyramid_count: Number of pyramids per side when ``shape`` is ``PYRAMIDS``.
        point_up: When True, indents cut upward (+Z) from ``surface_z = top_z - indent_depth``
            (or ``0.0`` when ``top_z == indent_depth``); when False, indents cut downward
            from ``top_z``.

    Returns:
        Bosl2Solid: Union of the 4 corner indent cutters.
    """
    from pyboxbuilder.box.shell import block
    from pyboxbuilder.compartments.element import union_all
    from pyboxbuilder.enums import StackableShape

    eff_shape = StackableShape.FLAT if shape is None else shape
    if eff_shape in (StackableShape.PYRAMID, StackableShape.PYRAMIDS, StackableShape.CONE):
        surface_z = (top_z - indent_depth) if point_up else top_z
        return build_stacking_pyramid_indents(
            width=width,
            length=length,
            foot_size=foot_size,
            indent_depth=indent_depth,
            foot_inset=foot_inset,
            clearance=clearance,
            surface_z=surface_z,
            pyramid_count=pyramid_count,
            single_pyramid=(eff_shape is StackableShape.PYRAMID),
            cone=(eff_shape is StackableShape.CONE),
            point_up=point_up,
        )

    s = foot_size + 2 * clearance
    h = indent_depth + clearance + 0.1
    z_start = top_z - indent_depth
    positions = [
        (foot_inset - clearance, foot_inset - clearance),
        (width - foot_inset - foot_size - clearance, foot_inset - clearance),
        (foot_inset - clearance, length - foot_inset - foot_size - clearance),
        (width - foot_inset - foot_size - clearance, length - foot_inset - foot_size - clearance),
    ]
    solids = [block([s, s, h], at=(x, y, z_start)) for x, y in positions]
    return union_all(solids)


def _perimeter_v_metrics(
    rim_thickness: float,
    depth: float,
    clearance: float,
) -> tuple[float, float, float, float, float]:
    """Compute 45-degree V-groove / V-ridge perimeter cross-section metrics."""
    w_tip = min(0.4, max(0.15, rim_thickness * 0.15))
    b_female = min(rim_thickness + 2.0 * clearance, 2.0 * depth + w_tip)
    h_female = max(0.3, (b_female - w_tip) / 2.0)
    b_male = max(w_tip + 0.2, b_female - 2.0 * clearance)
    h_male = max(0.2, h_female - clearance)
    return b_female, h_female, b_male, h_male, w_tip


def _build_perimeter_v_loop(
    width: float,
    length: float,
    rim_thickness: float,
    inset: float,
    base_w: float,
    tip_w: float,
    height: float,
    surface_z: float,
    point_up: bool = True,
) -> Bosl2Solid:
    """Build a 4-bar 45-degree V-ridge or V-groove loop around the box perimeter."""
    from pybosl2.shapes3d import prismoid

    from pyboxbuilder.compartments.element import union_all

    eps = 0.05
    b_open = base_w + 2.0 * eps
    h_total = height + eps

    x_l = inset + rim_thickness / 2.0
    x_r = width - inset - rim_thickness / 2.0
    y_f = inset + rim_thickness / 2.0
    y_b = length - inset - rim_thickness / 2.0
    dx = max(0.4, x_r - x_l)
    dy = max(0.4, y_b - y_f)
    xc = width / 2.0
    yc = length / 2.0

    if point_up:
        z0 = surface_z - eps
        s1_x, s2_x = [dx + b_open, b_open], [dx + tip_w, tip_w]
        s1_y, s2_y = [b_open, dy + b_open], [tip_w, dy + tip_w]
    else:
        z0 = surface_z - height
        s1_x, s2_x = [dx + tip_w, tip_w], [dx + b_open, b_open]
        s1_y, s2_y = [tip_w, dy + tip_w], [b_open, dy + b_open]

    bars = [
        prismoid(s1_x, s2_x, height=h_total, **precision_kwargs()).translate([xc, y_f, z0]),
        prismoid(s1_x, s2_x, height=h_total, **precision_kwargs()).translate([xc, y_b, z0]),
        prismoid(s1_y, s2_y, height=h_total, **precision_kwargs()).translate([x_l, yc, z0]),
        prismoid(s1_y, s2_y, height=h_total, **precision_kwargs()).translate([x_r, yc, z0]),
    ]
    return union_all(bars)


def build_perimeter_stacking_foot(
    width: float,
    length: float,
    rim_thickness: float,
    foot_height: float,
    inset: float,
    base_z: float = 0.0,
    shape: StackableShape | None = None,
    clearance: float = 0.15,
    point_up: bool = False,
) -> Bosl2Solid:
    """Return an inset perimeter foot/V-ridge rim (FR-101)."""
    from pyboxbuilder.box.shell import block
    from pyboxbuilder.enums import StackableShape

    eff_shape = StackableShape.FLAT if shape is None else shape
    if eff_shape in (StackableShape.PYRAMID, StackableShape.PYRAMIDS, StackableShape.CONE):
        _bf, _hf, b_male, h_male, w_tip = _perimeter_v_metrics(
            rim_thickness, foot_height, clearance
        )
        return _build_perimeter_v_loop(
            width=width,
            length=length,
            rim_thickness=rim_thickness,
            inset=inset,
            base_w=b_male,
            tip_w=w_tip,
            height=h_male,
            surface_z=base_z,
            point_up=point_up,
        )

    outer_w = width - 2 * inset
    outer_l = length - 2 * inset
    inner_w = outer_w - 2 * rim_thickness
    inner_l = outer_l - 2 * rim_thickness
    z = base_z if point_up else (base_z - foot_height)

    outer = block([outer_w, outer_l, foot_height], at=(inset, inset, z))
    inner = block([inner_w, inner_l, foot_height + 0.2], at=(inset + rim_thickness, inset + rim_thickness, z - 0.1))
    return outer - inner


def build_perimeter_stacking_indent(
    width: float,
    length: float,
    rim_thickness: float,
    indent_depth: float,
    inset: float,
    clearance: float = 0.15,
    top_z: float = 0.0,
    shape: StackableShape | None = None,
    point_up: bool = False,
) -> Bosl2Solid:
    """Return a perimeter channel/V-groove cutter to be subtracted from floor or lid top (FR-101)."""
    from pyboxbuilder.box.shell import block
    from pyboxbuilder.enums import StackableShape

    eff_shape = StackableShape.FLAT if shape is None else shape
    if eff_shape in (StackableShape.PYRAMID, StackableShape.PYRAMIDS, StackableShape.CONE):
        b_female, h_female, _bm, _hm, w_tip = _perimeter_v_metrics(
            rim_thickness, indent_depth, clearance
        )
        surface_z = (top_z - indent_depth) if point_up else top_z
        return _build_perimeter_v_loop(
            width=width,
            length=length,
            rim_thickness=rim_thickness,
            inset=inset,
            base_w=b_female,
            tip_w=w_tip,
            height=h_female,
            surface_z=surface_z,
            point_up=point_up,
        )

    outer_w = width - 2 * inset + 2 * clearance
    outer_l = length - 2 * inset + 2 * clearance
    inner_w = outer_w - 2 * (rim_thickness + 2 * clearance)
    inner_l = outer_l - 2 * (rim_thickness + 2 * clearance)
    h = indent_depth + clearance + 0.1
    z = top_z - indent_depth

    outer = block([outer_w, outer_l, h], at=(inset - clearance, inset - clearance, z))
    inner = block(
        [inner_w, inner_l, h + 0.2],
        at=(inset + rim_thickness + clearance, inset + rim_thickness + clearance, z - 0.1),
    )
    return outer - inner


def _build_top_corner_corbels(
    width: float,
    length: float,
    wt: float,
    floor_thickness: float,
    ledge_s: float,
    rim_h: float,
    top_z: float,
) -> Bosl2Solid:
    """Build 45-degree self-supporting corner corbel shelves at the top of an open tray."""
    from pybosl2.shapes3d import prismoid

    from pyboxbuilder.box.shell import block
    from pyboxbuilder.compartments.element import union_all

    margin = wt * 0.5
    top_span = max(0.6, ledge_s - margin)
    bot_span = max(0.4, wt * 0.5)
    corbel_h = min(max(0.2, top_span - bot_span), max(0.2, top_z - rim_h - floor_thickness))
    z_corbel = top_z - rim_h - corbel_h

    corners = [
        (margin, margin, 1.0, 1.0),
        (width - margin, margin, -1.0, 1.0),
        (margin, length - margin, 1.0, -1.0),
        (width - margin, length - margin, -1.0, -1.0),
    ]
    solids = []
    for x_wall, y_wall, sx, sy in corners:
        bx = x_wall + sx * (bot_span / 2.0)
        by = y_wall + sy * (bot_span / 2.0)
        tx = x_wall + sx * (top_span / 2.0)
        ty = y_wall + sy * (top_span / 2.0)
        corbel = prismoid(
            [bot_span, bot_span],
            [top_span, top_span],
            height=corbel_h + 0.05,
            shift=[tx - bx, ty - by],
            **precision_kwargs(),
        ).translate([bx, by, z_corbel])
        cap = block(
            [top_span, top_span, rim_h],
            at=(
                min(x_wall, x_wall + sx * top_span),
                min(y_wall, y_wall + sy * top_span),
                top_z - rim_h,
            ),
        )
        solids.append(corbel | cap)
    return union_all(solids)


def _build_top_perimeter_corbel(
    width: float,
    length: float,
    wt: float,
    floor_thickness: float,
    ledge_w: float,
    rim_h: float,
    top_z: float,
) -> Bosl2Solid:
    """Build a 45-degree self-supporting interior perimeter corbel shelf for an open tray."""
    from pybosl2.shapes3d import prismoid

    from pyboxbuilder.box.shell import block

    margin = wt * 0.5
    outer_w = width - 2.0 * margin
    outer_l = length - 2.0 * margin
    inner_top_w = max(1.0, width - 2.0 * ledge_w)
    inner_top_l = max(1.0, length - 2.0 * ledge_w)
    inner_bot_w = max(inner_top_w, width - 2.0 * wt)
    inner_bot_l = max(inner_top_l, length - 2.0 * wt)

    overhang = max(0.2, (inner_bot_w - inner_top_w) / 2.0)
    corbel_h = min(overhang, max(0.2, top_z - rim_h - floor_thickness))
    z_corbel = top_z - rim_h - corbel_h

    cap_outer = block([outer_w, outer_l, rim_h], at=(margin, margin, top_z - rim_h))
    cap_inner = block(
        [inner_top_w, inner_top_l, rim_h + 0.2],
        at=(ledge_w, ledge_w, top_z - rim_h - 0.1),
    )
    cap = cap_outer - cap_inner

    corbel_outer = block([outer_w, outer_l, corbel_h + 0.05], at=(margin, margin, z_corbel))
    corbel_inner = prismoid(
        [inner_bot_w, inner_bot_l],
        [inner_top_w, inner_top_l],
        height=corbel_h + 0.1,
        **precision_kwargs(),
    ).translate([width / 2.0, length / 2.0, z_corbel - 0.025])
    return cap | (corbel_outer - corbel_inner)


def apply_stackable_body(body: Bosl2Solid, spec: BoxSpec) -> Bosl2Solid:
    """Apply stacking features to a box body according to spec.stackable (FR-101)."""
    if spec.stackable is None:
        return body

    from pyboxbuilder.enums import StackableMode

    mode = spec.stackable
    wt = spec.wall_thickness
    foot_size = spec.stackable_foot_size or max(6.0, wt * 2.5)
    foot_height = spec.stackable_foot_height
    foot_inset = spec.stackable_foot_inset if spec.stackable_foot_inset is not None else (wt + 1.0)
    rim_thickness = spec.stackable_thickness or wt
    clearance = spec.stackable_fit_offset
    has_lid = spec.lid_thickness > 0.0
    shape = _resolve_stackable_shape(spec)
    pyr_count = getattr(spec, "stackable_pyramid_count", None)
    printer_safe = getattr(spec, "stackable_printer_safe", True)

    if mode is StackableMode.PATTERN or shape is StackableShape.PATTERN:
        depth = min(foot_height, max(0.8, spec.floor_thickness - 0.4))
        groove = build_pattern_stacking_groove(
            spec,
            surface_z=0.0,
            depth=depth,
            clearance=clearance,
            point_up=True,
        )
        if groove is not None:
            body = body - groove
        if not has_lid:
            _pat_type, margin, _spacing, _web = _resolve_stackable_pattern_params(spec)
            ledge_w = margin + clearance + 0.6
            corbel = _build_top_perimeter_corbel(
                spec.width,
                spec.length,
                wt,
                spec.floor_thickness,
                ledge_w,
                rim_h=0.6,
                top_z=spec.height,
            )
            ridge = build_pattern_stacking_ridge(
                spec,
                base_z=spec.height,
                depth=depth,
                clearance=clearance,
                point_up=True,
            )
            body = (body | corbel | ridge) if ridge is not None else (body | corbel)
        return body

    # In printer-safe mode (or INDENTS / PYRAMID / PYRAMIDS), the box floor stays
    # flat on the build plate (z = 0) with recessed 45-degree indents in z in [0, depth],
    # and the matching 45-degree bosses protrude upward from the top of the lid/rim.
    if mode in (StackableMode.INDENTS, StackableMode.PYRAMID, StackableMode.PYRAMIDS) or (
        mode is StackableMode.FEET and printer_safe
    ):
        depth = min(foot_height, max(0.8, spec.floor_thickness - 0.4))
        indents = build_stacking_indents(
            spec.width,
            spec.length,
            foot_size,
            depth,
            foot_inset,
            clearance=clearance,
            top_z=depth,
            shape=shape,
            pyramid_count=pyr_count,
            point_up=True,
        )
        body = body - indents
        if not has_lid:
            ledge_s = foot_inset + foot_size + clearance + 0.6
            corbels = _build_top_corner_corbels(
                spec.width,
                spec.length,
                wt,
                spec.floor_thickness,
                ledge_s,
                rim_h=0.6,
                top_z=spec.height,
            )
            feet = build_stacking_feet(
                spec.width,
                spec.length,
                foot_size,
                depth,
                foot_inset,
                base_z=spec.height,
                shape=shape,
                clearance=clearance,
                pyramid_count=pyr_count,
                point_up=True,
            )
            body = body | corbels | feet
        return body
    elif mode is StackableMode.FEET:
        # Legacy downward feet (stackable_printer_safe=False)
        depth = min(foot_height, max(0.8, (spec.lid_thickness if has_lid else spec.floor_thickness) - 0.6))
        feet = build_stacking_feet(
            spec.width,
            spec.length,
            foot_size,
            depth,
            foot_inset,
            base_z=0.0,
            shape=shape,
            clearance=clearance,
            pyramid_count=pyr_count,
            point_up=False,
        )
        body = body | feet
        if not has_lid:
            ledge_s = foot_inset + foot_size + clearance + 1.0
            corbels = _build_top_corner_corbels(
                spec.width,
                spec.length,
                wt,
                spec.floor_thickness,
                ledge_s,
                rim_h=depth + 0.4,
                top_z=spec.height,
            )
            body = body | corbels
        indents = build_stacking_indents(
            spec.width,
            spec.length,
            foot_size,
            depth,
            foot_inset,
            clearance=clearance,
            top_z=spec.height,
            shape=shape,
            pyramid_count=pyr_count,
            point_up=False,
        )
        return body - indents
    elif mode is StackableMode.PERIMETER:
        if printer_safe:
            depth = min(foot_height, max(0.8, spec.floor_thickness - 0.4))
            channel = build_perimeter_stacking_indent(
                spec.width,
                spec.length,
                rim_thickness,
                depth,
                foot_inset,
                clearance=clearance,
                top_z=depth,
                shape=shape,
                point_up=True,
            )
            body = body - channel
            if not has_lid:
                ledge_w = foot_inset + rim_thickness + clearance + 0.6
                corbel = _build_top_perimeter_corbel(
                    spec.width,
                    spec.length,
                    wt,
                    spec.floor_thickness,
                    ledge_w,
                    rim_h=0.6,
                    top_z=spec.height,
                )
                foot_rim = build_perimeter_stacking_foot(
                    spec.width,
                    spec.length,
                    rim_thickness,
                    depth,
                    foot_inset,
                    base_z=spec.height,
                    shape=shape,
                    clearance=clearance,
                    point_up=True,
                )
                body = body | corbel | foot_rim
            return body

        depth = min(foot_height, max(0.8, (spec.lid_thickness if has_lid else spec.floor_thickness) - 0.8))
        foot_rim = build_perimeter_stacking_foot(
            spec.width,
            spec.length,
            rim_thickness,
            depth,
            foot_inset,
            base_z=0.0,
            shape=shape,
            clearance=clearance,
            point_up=False,
        )
        body = body | foot_rim
        if not has_lid:
            ledge_w = foot_inset + rim_thickness + clearance + 1.0
            corbel = _build_top_perimeter_corbel(
                spec.width,
                spec.length,
                wt,
                spec.floor_thickness,
                ledge_w,
                rim_h=depth + 0.4,
                top_z=spec.height,
            )
            body = body | corbel
        channel = build_perimeter_stacking_indent(
            spec.width,
            spec.length,
            rim_thickness,
            depth,
            foot_inset,
            clearance=clearance,
            top_z=spec.height,
            shape=shape,
            point_up=False,
        )
        return body - channel
    elif mode is StackableMode.OUTSIDE:
        from pyboxbuilder.box.shell import block

        fit = spec.stackable_fit_offset
        stack = spec.stackable_thickness or wt
        ridge_w = spec.width + 2 * (stack - fit)
        ridge_l = spec.length + 2 * (stack - fit)
        ridge = block([ridge_w, ridge_l, stack], at=((spec.width - ridge_w) / 2, (spec.length - ridge_l) / 2, 0))
        return body | ridge
    return body


def apply_stackable_lid(lid: Bosl2Solid, spec: BoxSpec, top_z: float | None = None) -> Bosl2Solid:
    """Apply matching stacking features to a box lid according to spec.stackable (FR-101)."""
    if spec.stackable is None:
        return lid

    from pyboxbuilder.enums import StackableMode

    mode = spec.stackable
    wt = spec.wall_thickness
    lt = spec.lid_thickness
    z_top = spec.height if top_z is None else top_z
    foot_size = spec.stackable_foot_size or max(6.0, wt * 2.5)
    foot_height = spec.stackable_foot_height
    foot_inset = spec.stackable_foot_inset if spec.stackable_foot_inset is not None else (wt + 1.0)
    rim_thickness = spec.stackable_thickness or wt
    clearance = spec.stackable_fit_offset
    shape = _resolve_stackable_shape(spec)
    pyr_count = getattr(spec, "stackable_pyramid_count", None)
    printer_safe = getattr(spec, "stackable_printer_safe", True)

    if mode is StackableMode.PATTERN or shape is StackableShape.PATTERN:
        socket_depth = min(foot_height, max(0.8, spec.floor_thickness - 0.4))
        ridge = build_pattern_stacking_ridge(
            spec,
            base_z=z_top,
            depth=socket_depth,
            clearance=clearance,
            point_up=True,
        )
        return (lid | ridge) if ridge is not None else lid

    if mode in (StackableMode.INDENTS, StackableMode.PYRAMID, StackableMode.PYRAMIDS) or (
        mode is StackableMode.FEET and printer_safe
    ):
        socket_depth = min(foot_height, max(0.8, spec.floor_thickness - 0.4))
        feet = build_stacking_feet(
            spec.width,
            spec.length,
            foot_size,
            socket_depth,
            foot_inset,
            base_z=z_top,
            shape=shape,
            clearance=clearance,
            pyramid_count=pyr_count,
            point_up=True,
        )
        return lid | feet
    elif mode is StackableMode.FEET:
        depth = min(foot_height, max(0.8, lt - 0.6))
        indents = build_stacking_indents(
            spec.width,
            spec.length,
            foot_size,
            depth,
            foot_inset,
            clearance=clearance,
            top_z=z_top,
            shape=shape,
            pyramid_count=pyr_count,
            point_up=False,
        )
        return lid - indents
    elif mode is StackableMode.PERIMETER:
        if printer_safe:
            socket_depth = min(foot_height, max(0.8, spec.floor_thickness - 0.4))
            foot_rim = build_perimeter_stacking_foot(
                spec.width,
                spec.length,
                rim_thickness,
                socket_depth,
                foot_inset,
                base_z=z_top,
                shape=shape,
                clearance=clearance,
                point_up=True,
            )
            return lid | foot_rim

        depth = min(foot_height, max(0.8, lt - 0.8))
        channel = build_perimeter_stacking_indent(
            spec.width,
            spec.length,
            rim_thickness,
            depth,
            foot_inset,
            clearance=clearance,
            top_z=z_top,
            shape=shape,
            point_up=False,
        )
        return lid - channel
    return lid


def regular_polygon_path(
    sides: int,
    *,
    apothem: float | None = None,
    diameter: float | None = None,
    radius: float | None = None,
    orientation_deg: float = 0.0,
) -> tuple[tuple[float, float], ...]:
    """Generate closed 2D polygon vertices for a regular N-sided polygon (FR-102).

    Args:
        sides: Number of sides (N >= 3).
        apothem: Inradius (half flat-to-flat distance) in mm.
        diameter: Full flat-to-flat distance (2 * apothem) in mm.
        radius: Circumradius (distance from center to vertices) in mm.
        orientation_deg: Angular offset in degrees.

    Returns:
        tuple[tuple[float, float], ...]: Closed polygon vertices normalized to [0, W] x [0, L].
    """
    if sides < 3:
        raise ValueError(f"Regular polygon must have at least 3 sides; got {sides}")

    import math

    if apothem is not None:
        r_circum = apothem / math.cos(math.pi / sides)
    elif diameter is not None:
        r_circum = (diameter / 2.0) / math.cos(math.pi / sides)
    elif radius is not None:
        r_circum = radius
    else:
        raise ValueError("Must specify at least one of apothem, diameter, or radius")

    angle_offset = math.radians(orientation_deg) + (math.pi / sides)
    raw_pts = []
    for i in range(sides):
        angle = 2.0 * math.pi * i / sides + angle_offset
        x = r_circum * math.cos(angle)
        y = r_circum * math.sin(angle)
        raw_pts.append((x, y))

    min_x = min(p[0] for p in raw_pts)
    min_y = min(p[1] for p in raw_pts)
    return tuple((round(p[0] - min_x, 6), round(p[1] - min_y, 6)) for p in raw_pts)


def polygon_grid_position(
    row: int,
    col: int,
    sides: int,
    apothem: float,
    spacing: float = 0.0,
    origin: tuple[float, float] = (0.0, 0.0),
) -> tuple[float, float]:
    """Calculate the (x, y) world position for regular polygon cells in a tessellated grid (FR-102).

    Args:
        row: Row index in the grid (0-indexed).
        col: Column index in the grid (0-indexed).
        sides: Polygon sides (currently 3, 4, 6 supported).
        apothem: Polygon apothem (half flat-to-flat distance) in mm.
        spacing: Gap between adjacent polygon edges in mm (0.0 = touching faces).
        origin: Base (x0, y0) translation offset.

    Returns:
        tuple[float, float]: (x, y) coordinates of the bounding box origin (min_x, min_y).
    """
    import math

    if sides == 6:
        r = apothem
        dx = 2.0 * r + spacing
        dy = math.sqrt(3.0) * r + spacing * math.sqrt(3.0) / 2.0
        x = origin[0] + col * dx + (row % 2) * (r + spacing / 2.0)
        y = origin[1] + row * dy
        return (round(x, 4), round(y, 4))
    elif sides == 4:
        w = 2.0 * apothem + spacing
        return (round(origin[0] + col * w, 4), round(origin[1] + row * w, 4))
    elif sides == 3:
        r = apothem
        dx = (2.0 * r + spacing) / math.sqrt(3.0)
        dy = 3.0 * r + spacing
        x = origin[0] + col * dx
        y = origin[1] + row * dy
        return (round(x, 4), round(y, 4))
    else:
        w = 2.0 * apothem + spacing
        return (round(origin[0] + col * w, 4), round(origin[1] + row * w, 4))


def build_horizontal_dovetail(
    depth: float = 3.0,
    width_tip: float = 8.5,
    width_base: float = 6.0,
    height: float = 14.0,
    clearance: float = 0.0,
    is_female: bool = False,
) -> Bosl2Solid:
    """Build a true flared trapezoidal vertical dovetail joint key or socket (FR-102).

    The key extends in +X from x=0 to x=depth.
    At x=0, width is width_base; at x=depth, width is width_tip (where width_tip > width_base).
    The trapezoidal flare physically locks against horizontal pull-apart in both X and Y.

    Args:
        depth: Penetration depth of the dovetail in mm.
        width_tip: Width at the wide outer tip in mm.
        width_base: Width at the narrow base neck in mm.
        height: Vertical height of the joint in mm.
        clearance: Fit offset in mm (applied to female socket).
        is_female: True to create oversized female socket cutter.

    Returns:
        Bosl2Solid: Dovetail solid ready to translate and union/subtract.
    """
    from pybosl2.shapes3d import prismoid

    clr = clearance if is_female else 0.0
    w_base = width_base + 2.0 * clr
    w_tip = width_tip + 2.0 * clr
    h = height + (2.0 * clr if is_female else 0.0)
    d = depth + (clr + 0.1 if is_female else 0.0)

    return prismoid([h, w_base], [h, w_tip], height=d).rotate([0, 90, 0])


def build_interlock_clip(
    depth: float = 2.5,
    width_tip: float = 7.0,
    width_base: float = 4.5,
    height: float = 10.0,
    clearance: float = 0.15,
) -> Bosl2Solid:
    """Build a double-dovetail butterfly connector clip that locks adjacent boxes (FR-102).

    Args:
        depth: Penetration depth into each box wall in mm.
        width_tip: Width of each wide end in mm.
        width_base: Width at the central neck waist in mm.
        height: Height of the clip in mm.
        clearance: Fit clearance subtracted from the clip so it drops in easily.

    Returns:
        Bosl2Solid: Butterfly clip centered at the interface (x=0).
    """
    from pybosl2.shapes3d import prismoid

    w_tip = max(2.0, width_tip - 2.0 * clearance)
    w_base = max(1.5, width_base - 2.0 * clearance)
    h = max(2.0, height - clearance)
    d = max(1.0, depth - clearance)

    right = prismoid([h, w_base], [h, w_tip], height=d).rotate([0, 90, 0])
    left = prismoid([h, w_base], [h, w_tip], height=d).rotate([0, 90, 0]).rotate([0, 0, 180])
    return right | left


def apply_horizontal_interlock(body: Bosl2Solid, spec: BoxSpec) -> Bosl2Solid:
    """Apply horizontal side interlocking features according to spec.interlock_type (FR-089, FR-102)."""
    if spec.interlock_type is None:
        return body

    from pyboxbuilder.enums import InterlockType, MagnetType

    itype = spec.interlock_type
    if itype is InterlockType.NONE:
        return body

    if itype is InterlockType.GRIDFINITY:
        from pyboxbuilder.box.shell import block

        base_bevel_h = min(2.5, spec.floor_thickness)
        base_cut = block(
            [spec.width + 2.0, spec.length + 2.0, base_bevel_h],
            at=(-1.0, -1.0, -0.5),
        ) - block(
            [spec.width - 2.0, spec.length - 2.0, base_bevel_h + 1.0],
            at=(1.0, 1.0, -1.0),
        )
        return body - base_cut

    import math

    clr = spec.interlock_clearance
    body_h = spec.height if spec.lid_thickness == 0.0 else (spec.height - spec.lid_thickness)
    mid_z = body_h / 2.0

    # Dovetail defaults:
    dt_depth = 3.0
    dt_w_tip = 8.5
    dt_w_base = 6.0
    dt_h = min(14.0, max(4.0, body_h * 0.7))
    if isinstance(spec.interlock_size, (int, float)):
        dt_depth = float(spec.interlock_size)
    elif isinstance(spec.interlock_size, (tuple, list)) and len(spec.interlock_size) >= 1:
        dt_depth = float(spec.interlock_size[0])
        if len(spec.interlock_size) >= 2:
            dt_w_tip = float(spec.interlock_size[1])
        if len(spec.interlock_size) >= 3:
            dt_w_base = float(spec.interlock_size[2])

    if itype is InterlockType.DOVETAIL and spec.wall_thickness <= dt_depth:
        from pyboxbuilder.box.validation import GeometryValidationError

        raise GeometryValidationError(
            label=spec.label,
            invariant="dovetail_depth_fits_wall",
            message=(
                f"Wall thickness ({spec.wall_thickness:.2f}mm) must be strictly greater than "
                f"dovetail depth ({dt_depth:.2f}mm) to prevent piercing through the wall into the interior."
            ),
            guidance=(
                f"Increase wall_thickness to > {dt_depth:.2f}mm (e.g. wall_thickness=4.0) "
                f"or reduce dovetail depth (interlock_size) to < {spec.wall_thickness:.2f}mm."
            ),
        )

    # Magnet defaults:
    mag_dia = 6.0
    mag_depth = 2.0
    if spec.magnet_type is not None and spec.magnet_type is not MagnetType.NONE and spec.magnet_size:
        mag_dia = spec.magnet_size[0]
        mag_depth = spec.magnet_size[1] if len(spec.magnet_size) > 1 else 2.0

    # Clip defaults:
    clip_depth = 2.5
    clip_w_tip = 7.0
    clip_w_base = 4.5
    clip_h = min(10.0, max(3.0, body_h * 0.6))

    # 1. Polygon footprint (regular or arbitrary)
    if spec.path and len(spec.path) >= 3:
        pts = spec.path
        n = len(pts)
        for i in range(n):
            if spec.interlock_sides is not None and i not in spec.interlock_sides:
                continue

            p1 = pts[i]
            p2 = pts[(i + 1) % n]
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            length = math.hypot(dx, dy)
            if length < 4.0:
                continue

            tx, ty = dx / length, dy / length
            nx, ny = ty, -tx
            mx, my = (p1[0] + p2[0]) / 2.0, (p1[1] + p2[1]) / 2.0
            normal_deg = math.degrees(math.atan2(ny, nx))

            if itype is InterlockType.MAGNET:
                from pybosl2 import cylinder

                pocket = cylinder(height=mag_depth + 0.1, radius=mag_dia / 2.0 + clr, **precision_kwargs())
                pocket = pocket.rotate([0, 90, 0]).rotate([0, 0, normal_deg])
                pocket = pocket.translate([mx - nx * mag_depth / 2.0, my - ny * mag_depth / 2.0, mid_z])
                body = body - pocket

            elif itype is InterlockType.DOVETAIL:
                is_male = (i % 2 == 0)
                if is_male:
                    key = build_horizontal_dovetail(dt_depth, dt_w_tip, dt_w_base, dt_h, clearance=0.0)
                    key = key.rotate([0, 0, normal_deg]).translate([mx, my, mid_z])
                    body = body | key
                else:
                    fem = build_horizontal_dovetail(dt_depth, dt_w_tip, dt_w_base, dt_h, clearance=clr, is_female=True)
                    fem = fem.rotate([0, 0, normal_deg + 180.0]).translate([
                        mx + nx * 0.05,
                        my + ny * 0.05,
                        mid_z,
                    ])
                    body = body - fem

            elif itype is InterlockType.CLIP:
                from pybosl2.shapes3d import prismoid

                clip_total_d = clip_depth + clr + 0.1
                slot = prismoid(
                    [clip_h + 2.0 * clr, clip_w_base + 2.0 * clr],
                    [clip_h + 2.0 * clr, clip_w_tip + 2.0 * clr],
                    height=clip_total_d,
                ).rotate([0, 90, 0]).rotate([0, 0, normal_deg + 180.0])
                slot = slot.translate([
                    mx + nx * 0.05,
                    my + ny * 0.05,
                    body_h - clip_h / 2.0,
                ])
                body = body - slot

        return body

    # 2. Rectangular box
    w, length_val = spec.width, spec.length
    if itype is InterlockType.DOVETAIL:
        # Male keys on +X and +Y
        key_x = build_horizontal_dovetail(dt_depth, dt_w_tip, dt_w_base, dt_h, clearance=0.0)
        key_x = key_x.translate([w, length_val / 2.0, mid_z])

        key_y = build_horizontal_dovetail(dt_depth, dt_w_tip, dt_w_base, dt_h, clearance=0.0)
        key_y = key_y.rotate([0, 0, 90]).translate([w / 2.0, length_val, mid_z])
        body = body | key_x | key_y

        # Female sockets on -X (at x=0) and -Y (at y=0)
        fem_x = build_horizontal_dovetail(dt_depth, dt_w_tip, dt_w_base, dt_h, clearance=clr, is_female=True)
        fem_x = fem_x.translate([-0.05, length_val / 2.0, mid_z])

        fem_y = build_horizontal_dovetail(dt_depth, dt_w_tip, dt_w_base, dt_h, clearance=clr, is_female=True)
        fem_y = fem_y.rotate([0, 0, 90]).translate([w / 2.0, -0.05, mid_z])
        body = body - fem_x - fem_y

    elif itype is InterlockType.MAGNET:
        from pybosl2 import cylinder

        p_x_pos = cylinder(
            height=mag_depth + 0.1, radius=mag_dia / 2.0 + clr, **precision_kwargs()
        ).rotate([0, 90, 0]).translate([
            w - mag_depth / 2.0, length_val / 2.0, mid_z
        ])
        p_x_neg = cylinder(
            height=mag_depth + 0.1, radius=mag_dia / 2.0 + clr, **precision_kwargs()
        ).rotate([0, 90, 0]).translate([
            mag_depth / 2.0, length_val / 2.0, mid_z
        ])
        p_y_pos = cylinder(
            height=mag_depth + 0.1, radius=mag_dia / 2.0 + clr, **precision_kwargs()
        ).rotate([90, 0, 0]).translate([
            w / 2.0, length_val - mag_depth / 2.0, mid_z
        ])
        p_y_neg = cylinder(
            height=mag_depth + 0.1, radius=mag_dia / 2.0 + clr, **precision_kwargs()
        ).rotate([90, 0, 0]).translate([
            w / 2.0, mag_depth / 2.0, mid_z
        ])
        body = body - p_x_pos - p_x_neg - p_y_pos - p_y_neg

    elif itype is InterlockType.CLIP:
        from pybosl2.shapes3d import prismoid

        clip_total_d = clip_depth + clr + 0.1
        # Butterfly slots cut from top rim down into the walls
        slot_x_p = prismoid(
            [clip_h + 2.0 * clr, clip_w_base + 2.0 * clr],
            [clip_h + 2.0 * clr, clip_w_tip + 2.0 * clr],
            height=clip_total_d,
        ).rotate([0, 90, 0]).rotate([0, 0, 180]).translate([
            w + 0.05, length_val / 2.0, body_h - clip_h / 2.0
        ])
        slot_x_n = prismoid(
            [clip_h + 2.0 * clr, clip_w_base + 2.0 * clr],
            [clip_h + 2.0 * clr, clip_w_tip + 2.0 * clr],
            height=clip_total_d,
        ).rotate([0, 90, 0]).translate([
            -0.05, length_val / 2.0, body_h - clip_h / 2.0
        ])
        slot_y_p = prismoid(
            [clip_h + 2.0 * clr, clip_w_base + 2.0 * clr],
            [clip_h + 2.0 * clr, clip_w_tip + 2.0 * clr],
            height=clip_total_d,
        ).rotate([0, 90, 0]).rotate([0, 0, -90]).translate([
            w / 2.0, length_val + 0.05, body_h - clip_h / 2.0
        ])
        slot_y_n = prismoid(
            [clip_h + 2.0 * clr, clip_w_base + 2.0 * clr],
            [clip_h + 2.0 * clr, clip_w_tip + 2.0 * clr],
            height=clip_total_d,
        ).rotate([0, 90, 0]).rotate([0, 0, 90]).translate([
            w / 2.0, -0.05, body_h - clip_h / 2.0
        ])
        body = body - slot_x_p - slot_x_n - slot_y_p - slot_y_n

    return body

