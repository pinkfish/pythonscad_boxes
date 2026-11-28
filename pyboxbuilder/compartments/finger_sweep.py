# SPDX-License-Identifier: Apache-2.0
"""Turning a cut's outline into a solid that crosses a wall.

The outline (:mod:`pyboxbuilder.compartments.finger_outline`) says what shape
the cut is; this says what happens to it on the way through the wall. That is
two questions, and they are the ones this module owns:

* **how far it runs** — a wall's thickness plus the overshoot each end needs to
  leave cleanly, so no face of the cut is coplanar with a face of the box;
* **what each end does when it emerges** — square, or rolled over onto the face
  by a fillet, decided per face (:class:`FaceTreatment`).

The two faces are not interchangeable. The sweep runs from the compartment side
*outward*, so the near end is the inside of the wall and the far end its
outside, which is what a hand touches. Wiring those two the wrong way round is
invisible whenever both are rounded the same, and shipped once (T330).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyboxbuilder.compartments.finger_outline import RIM_OVERSHOOT_MM
from pyboxbuilder.enums import ScoopSide
from pyboxbuilder.rounding import rounding_facets, roundover_profile

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


DEFAULT_FLOOR_DIP_MM = 0.2
"""How far a cut passes below the well floor, by default.

Its only job is to keep the cut's bottom face off the floor plane, since a
coincident face renders as speckle and is how a boolean leaves a zero-thickness
skin. 0.2mm does that. Scaling it with the floor thickness — which an earlier
version did, up to a full millimetre — spends half a 2mm floor on a cosmetic
detail, and it showed as the cut visibly eating into the floor.
"""

_SIDE_CENTRES = {
    ScoopSide.FRONT: lambda w, l: (w / 2, 0.0),
    ScoopSide.BACK: lambda w, l: (w / 2, l),
    ScoopSide.LEFT: lambda w, l: (0.0, l / 2),
    ScoopSide.RIGHT: lambda w, l: (w, l / 2),
}

_SIDE_SPIN = {
    ScoopSide.FRONT: 0.0,
    ScoopSide.BACK: 180.0,
    ScoopSide.LEFT: 270.0,
    ScoopSide.RIGHT: 90.0,
}


DEFAULT_EDGE_ROUNDING_MM = 1.0
"""Fallback face fillet where no wall thickness is known.

The scoops normally derive it as ``wall_thickness / 2`` instead, which is what
the original passes and the largest fillet a wall has room for.
"""
@dataclass(frozen=True)
class FaceTreatment:
    """What happens where a cut **meets the wall it passes through** (FR-073).

    Kept apart from :class:`CutProfile` because it answers a different question:
    the profile is the shape of the opening, this is what its edges do. They
    were one flat parameter list, and the two most expensive bugs in this file
    lived exactly on the seam — a face rounded on the wrong side, and a rim
    profile on one end only leaving a ridge inside the cut.
    """

    fillet: float | None = None
    """The roundover radius where the cut emerges. ``None`` uses half the wall,
    the largest a wall can carry (FR-059)."""
    round_outer: bool = True
    """Round the box's **outside** face — the one a hand meets."""
    round_inner: bool = True
    """Round the compartment-side face. Off for a cut something rests against,
    where a fillet is a gap rather than a comfort."""
    inner_overshoot: float = 0.0
    """How far past the inner face to run the sweep, so a rim's transition
    finishes in the void instead of leaving a ridge inside the wall."""
    breach_floor: bool = False
    """Let the cut run below the well floor unclipped."""
    floor_clearance: float | None = None
    """How far below the well floor the cut may reach; ``None`` derives it."""
    top_limit: float | None = None
    """Height above which the cut is trimmed — the guard for material that must
    not be cut into."""
def scoop_face_flare(
    wall_thickness: float, rounding_edge: float | None = None
) -> float:
    """How far a wall scoop's face fillet reaches **beyond** its outline (FR-074).

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
def _offset_open_top_outline(
    outline: list[tuple[float, float]],
    comp_depth: float,
    offset: float,
) -> list[list[float]]:
    """Expand a symmetric open-top cut outline outward while keeping its rim tangent.

    A 2D polygon offset turns the 90-degree transition from the mouth roll into
    the vertical ``RIM_OVERSHOOT_MM`` stem inward/downward, leaving a sharp
    triangular step on the wall's rim where the face fillet emerges. Expanding
    along the outward normal below the roll and fading the vertical component
    to zero along the roll keeps every slice tangent at ``y = comp_depth``.
    """
    if abs(offset) < 1e-12:
        return [[float(x), float(y)] for x, y in outline]

    mid = len(outline) // 2
    right_full = outline[mid:]
    right = [pt for pt in right_full if pt[1] <= comp_depth + 1e-9]
    overshoot_count = len(right_full) - len(right)
    if not right:
        return [[float(x), float(y)] for x, y in outline]

    n = len(right)
    # Square sub-floor throat (e.g. build_through_hole) starts away from X=0
    # below the box base rather than tangent to Y=0 on the centreline.
    square_throat_base = abs(right[0][0]) > 1e-9

    tangents: list[tuple[float, float]] = []
    for i in range(n):
        j_prev = i - 1
        while j_prev >= 0 and math.dist(right[j_prev], right[i]) < 1e-9:
            j_prev -= 1
        j_next = i + 1
        while j_next < n and math.dist(right[j_next], right[i]) < 1e-9:
            j_next += 1

        if j_prev < 0:
            if square_throat_base:
                tangents.append((0.0, 1.0))
                continue
            tangents.append((1.0, 0.0))
            continue

        if j_next >= n:
            p_prev = right[j_prev]
            dx, dy = right[i][0] - p_prev[0], right[i][1] - p_prev[1]
        else:
            p_prev, p_next = right[j_prev], right[j_next]
            dx, dy = p_next[0] - p_prev[0], p_next[1] - p_prev[1]
        length = math.hypot(dx, dy)
        if length < 1e-12:
            tangents.append(tangents[-1] if tangents else (1.0, 0.0))
        else:
            tangents.append((dx / length, dy / length))

    normals = [(ty, -tx) for tx, ty in tangents]
    peak_i = max(range(n), key=lambda k: tangents[k][1])
    y_start = right[peak_i][1]
    span_y = comp_depth - y_start
    nx0, ny0 = normals[peak_i]

    out_right: list[tuple[float, float]] = []
    for i, (x, y) in enumerate(right):
        if i <= peak_i or span_y <= 1e-9:
            nx, ny = normals[i]
            ox = offset * nx
            oy = -offset if (i == 0 and square_throat_base) else offset * ny
        else:
            t = max(0.0, min(1.0, (y - y_start) / span_y))
            s = 0.5 * (1.0 - math.cos(math.pi * t))
            ox = offset * ((1.0 - s) * nx0 + s * 1.0)
            oy = offset * ((1.0 - s) * ny0)
        nx_pt = 0.0 if i == 0 and abs(x) < 1e-9 else x + ox
        out_right.append((nx_pt, y + oy))

    if overshoot_count > 0:
        top_x = out_right[-1][0]
        for _ in range(overshoot_count):
            out_right.append((top_x, comp_depth + RIM_OVERSHOOT_MM))

    out_left = [(-x, y) for x, y in reversed(out_right)]
    return [[float(x), float(y)] for x, y in (out_left + out_right)]


def _build_open_top_rounded_sweep(
    outline: list[tuple[float, float]],
    comp_depth: float,
    depth: float,
    fillet: float,
    round_inner: bool,
    round_outer: bool,
    steps: int,
) -> Bosl2Solid:
    """Loft a rounded open-top cut across the wall without a rim-corner cliff."""
    import math as _math

    from pybosl2 import VNF, Path3D
    from pybosl2.enums import VNFStyle
    from pybosl2.skin import CapType, _as_solid

    samples: list[tuple[float, float]] = []
    if round_inner:
        for i in range(steps + 1):
            a = (_math.pi / 2) * i / steps
            samples.append(
                (fillet * (1.0 - _math.cos(a)), fillet * (1.0 - _math.sin(a)))
            )
    else:
        samples.append((0.0, 0.0))

    if round_outer:
        for i in range(steps + 1):
            a = (_math.pi / 2) * (1.0 - i / steps)
            z = depth - fillet * (1.0 - _math.cos(a))
            if abs(z - samples[-1][0]) < 1e-7:
                continue
            samples.append((z, fillet * (1.0 - _math.sin(a))))
    elif abs(depth - samples[-1][0]) > 1e-7:
        samples.append((depth, 0.0))

    rows = [
        Path3D([
            [x, y, z]
            for x, y in _offset_open_top_outline(outline, comp_depth, offset)
        ])
        for z, offset in samples
    ]
    vnf = VNF.vertex_array(
        rows, caps=CapType.BUTT, col_wrap=True, style=VNFStyle.MIN_EDGE
    )
    if vnf.volume() < 0:
        vnf = vnf.reverse()
    return _as_solid(vnf)


def _sweep_through_wall(
    outline: list[tuple[float, float]],
    comp_width: float,
    comp_length: float,
    side: ScoopSide,
    *,
    comp_depth: float,
    wall_thickness: float,
    rounding_radius: float,
    span: float,
    radius: float,
    faces: FaceTreatment | None = None,
    floor_thickness: float | None = None,
) -> Bosl2Solid:
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
        span: The compartment span along the cut wall.
        radius: The scoop's half-width, used to size the floor clip.
        faces: What happens where the cut meets the wall — the fillet, which
            faces get it, the overshoot, the floor clip and the top trim. One
            record rather than seven parameters because the seam between "the
            shape of the opening" and "what its edges do" is where this file's
            two most expensive bugs lived: a face rounded on the wrong side,
            and a rim profile on one end only leaving a ridge inside the cut
            (:class:`FaceTreatment`).
        floor_thickness: Box floor, sizing the permitted dip below it.

    Returns:
        The cutout, positioned in the compartment frame.

    """
    if faces is None:
        faces = FaceTreatment()
    rounding_edge = faces.fillet if faces.fillet is not None else wall_thickness / 2
    round_inner, round_outer = faces.round_inner, faces.round_outer
    inner_overshoot = faces.inner_overshoot
    breach_floor, floor_clearance = faces.breach_floor, faces.floor_clearance
    top_limit = faces.top_limit

    fudge = 0.03
    depth = wall_thickness + fudge + inner_overshoot
    rim = scoop_face_flare(wall_thickness, rounding_edge)

    # BOSL2's own offset_sweep, which lofts between offsets of the outline, so
    # the fillet follows the cut's curve. (A hand-rolled stand-in chained
    # convex hulls between slices, and a hull across a U-shaped outline bridges
    # the notch — the fillet came out as a ramp across the opening.)
    from pybosl2 import current_backend, polygon
    from pybosl2.path2d import Path2D

    steps = max(8, rounding_facets()["fn"] // 4)
    ring = [[float(x), float(y)] for x, y in outline]
    fillet = rim if (rim > 0 and (round_outer or round_inner)) else 0.0
    is_open_top = max(y for _, y in outline) > comp_depth + 1e-4

    if current_backend() == "sdf":
        swept = polygon(Path2D(ring, closed=True)).linear_extrude(height=depth)
    elif fillet > 0 and is_open_top and top_limit is None:
        swept = _build_open_top_rounded_sweep(
            outline, comp_depth, depth, fillet, round_inner, round_outer, steps,
        )
    elif fillet > 0:
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
        if hasattr(swept, "polyhedron"):
            from pybosl2.shapes3d.base import CsgSolid
            swept = CsgSolid(swept.polyhedron())
    else:
        swept = Path2D(ring, closed=True).offset_sweep(height=depth, steps=steps)
        if hasattr(swept, "polyhedron"):
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
