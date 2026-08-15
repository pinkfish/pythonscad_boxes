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

from typing import Sequence, TYPE_CHECKING

from pyboxbuilder.enums import ScoopSide
from pyboxbuilder.precision import kwargs as precision_kwargs
from pyboxbuilder.rounding import (
    default_rounding,
    round_edges,
    vertical_and_bottom_edges,
)

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


def corner(
    solid: "Bosl2Solid",
    size: Sequence[float],
    at: Sequence[float] = (0.0, 0.0, 0.0),
) -> "Bosl2Solid":
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


def block(size: Sequence[float], at: Sequence[float] = (0.0, 0.0, 0.0)) -> "Bosl2Solid":
    """A cuboid of `size` whose minimum corner sits at `at`."""
    from pybosl2 import cuboid

    return corner(cuboid(list(size)), size, at)


def build_shell(spec: dict) -> "Bosl2Solid":
    """Outer block, hollowed to the interior unless `spec["hollow"]` is False.

    Args:
        spec: Needs `width`, `length`, `height`; reads `wall_thickness`,
            `floor_thickness` and `hollow` (default True).

    Returns:
        The box body before any type-specific lid features are added.
    """
    size = [spec["width"], spec["length"], spec["height"]]
    outer = block(size)

    # Round what a hand grips: the vertical corners and the base always, and the
    # top rim too when nothing has to mate with it. On a lidded box the rim is a
    # sealing surface, so its rounding lives on the lid instead — the closed box
    # still reads as rounded top, sides and bottom (FR-043/FR-044).
    radius = body_rounding(spec)
    if radius > 0:
        edges = vertical_and_bottom_edges()
        if spec.get("rim_free"):
            edges = edges + [_top_anchor()]
        outer = round_edges(outer, size, radius, edges)

    if spec.get("hollow", True):
        outer = outer - interior_block(spec)
        outer = round_inner_rim(outer, spec)
    return apply_finger_holes(outer, spec)


def body_rounding(spec: dict) -> float:
    """The edge radius for this box body.

    Args:
        spec: Reads `rounding`; falls back to half the wall thickness.

    Returns:
        The radius in mm. ``0`` disables rounding entirely.
    """
    explicit = spec.get("rounding")
    if explicit is not None:
        return max(0.0, float(explicit))
    return default_rounding(spec.get("wall_thickness", 2.0))


def _top_anchor():
    """The TOP anchor, imported lazily so this module has no import-time pybosl2."""
    from pybosl2 import Anchor

    return Anchor.TOP


def _hole_flare(wall_thickness: float, hole, reach: float) -> float:
    """The face fillet an exterior finger hole's cut is built with.

    The fillet is made by flaring the sweep's ends, and the flare is isotropic
    in the profile plane — it grows down past the outline's flat bottom exactly
    as readily as it grows sideways. So this is also how far the cut reaches
    *below* its outline, which is what the placement has to allow for (T306).

    Capped at half the reach: on a cut shallower than twice the wall's fillet
    the flare would swallow the outline whole, leaving no straight run between
    the roll at the top and the flare at the bottom.
    """
    from pyboxbuilder.compartments.finger_hole import scoop_face_flare

    flare = scoop_face_flare(wall_thickness, getattr(hole, "rounding_edge", None))
    return min(flare, reach / 2.0)


def apply_finger_holes(body: "Bosl2Solid", spec: dict) -> "Bosl2Solid":
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
    holes = spec.get("finger_holes") or ()
    if not holes:
        return body

    from pyboxbuilder.compartments.finger_hole import (
        DEFAULT_FLOOR_DIP_MM, build_wall_scoop,
    )

    wt = spec.get("wall_thickness", 2.0)
    ft = spec.get("floor_thickness", 1.6)
    inner_width = spec["width"] - 2 * wt
    inner_length = spec["length"] - 2 * wt

    # Align to the top of the *inside*, not the outer rim. On a lidded box the
    # lid (or its track) occupies the band above the interior, so a hole hung
    # from the rim starts inside solid material and reads as a nick in the top
    # edge rather than as a cut into the well. A type whose body is already
    # shortened for its lid — cap, slipover — says so with `interior_top`.
    from pyboxbuilder.box.base import wall_top

    for hole in holes:
        # Per side: the four walls need not end level, and a hole aligned to
        # the wrong one either floats above its wall or cuts into a lid feature.
        interior_top = wall_top(spec, hole.side)
        interior_height = interior_top - ft
        radius = getattr(hole, "radius", 14.0)
        # The cut's height follows the finger unless told otherwise, and never
        # reaches deeper than the interior.
        reach = min(getattr(hole, "depth", None) or radius, interior_height)
        flare = _hole_flare(wt, hole, reach)
        # The outline's roll finishes tangent to the plane `outline_height`
        # above its flat bottom, and that plane is the top of the wall: the
        # outline is hung from `interior_top` so the mouth flows into the rim
        # (FR-043a) instead of being sliced through mid-curve. It is a flare
        # shorter than the reach because the cut runs that much below its
        # outline, so the deepest point of the cut is the reach asked for
        # (T306) — the two ends are aligned by the *outline's* height, not by
        # shifting the whole solid, which moves one end for the other.
        outline_height = reach - flare
        scoop = build_wall_scoop(
            inner_width,
            inner_length,
            outline_height,
            hole.side,
            radius=radius,
            wall_thickness=wt,
            # None lets r1 derive from the throat rather than pinning 3mm.
            rounding_radius=getattr(hole, "rounding_radius", None),
            # Pinned rather than left to default, because the alignment above
            # is measured off this exact flare.
            rounding_edge=flare,
            # Anything above the interior — a lid band, a sliding track — is
            # material the hole must not cut into, so the outline's rim
            # overshoot is trimmed off at the outline's own top, which is
            # where the roll has finished and the overshoot begins.
            top_limit=(
                outline_height if interior_top < spec["height"] - 1e-9 else None
            ),
            # There is wall below an exterior hole, not floor, so the face
            # flare can finish instead of being sliced off at the outline's
            # flat bottom — which is what leaves the wall's sawn cross-section
            # showing at the base of the cut (FR-043g). Compartment scoops keep
            # the default clip: they bottom on the floor, and there the flare
            # has nowhere to go but through it.
            floor_clearance=flare + DEFAULT_FLOOR_DIP_MM,
        )
        offset = getattr(hole, "offset", 0.0) or 0.0
        along_x = hole.side in (ScoopSide.FRONT, ScoopSide.BACK)
        body = body - scoop.translate(
            [
                wt + (offset if along_x else 0.0),
                wt + (0.0 if along_x else offset),
                interior_top - outline_height,
            ]
        )

    return body


def no_lid_finger_holes(spec: dict):
    """The finger holes a no-lid box cuts into its longer walls (FR-047).

    An open tray is lifted by the rim, so the original (`no_lid.scad`) puts a
    finger dip into each wall of the longer dimension. The sizing is a formula
    on the spec, not a constant:

    - radius = `min(20, min(length, width) / 4, height - floor_thickness + 1)`;
    - height = `min(radius, height - default_floor_thickness + 1)` (2mm floor);
    - mouth rounding = 3mm.

    A wall too short for the hole's mouth is skipped: a finger hole wider than
    the wall it is cut through breaks into the adjoining walls, so the tray goes
    out with **no** hole rather than a broken one. That is what keeps a path box
    with a short side sound.

    Args:
        spec: Needs `width`, `length`, `height`; reads `wall_thickness` and
            `floor_thickness`.

    Returns:
        A tuple of `FingerHoleBuilder`s — one per longer wall — or an empty
        tuple when the holes would not fit.
    """
    from pyboxbuilder.builders._base import FingerHoleBuilder

    wt = spec.get("wall_thickness", 2.0)
    ft = spec.get("floor_thickness", 1.6)
    width = spec["width"]
    length = spec["length"]
    height = spec["height"]

    radius = min(20.0, min(length, width) / 4.0, height - ft + 1.0)
    hole_height = max(min(radius, height - ft - wt - 1.0), 2)
    rounding_radius = 3.0

    if length >= width:
        sides = (ScoopSide.LEFT, ScoopSide.RIGHT)
        span = length - 2 * wt
    else:
        sides = (ScoopSide.FRONT, ScoopSide.BACK)
        span = width - 2 * wt

    # The mouth is `radius + rounding_radius` wide on each side of centre; the
    # two of them have to fit inside the wall the hole is cut through.
    if 2.0 * (radius + rounding_radius) > span:
        return ()

    return tuple(
        FingerHoleBuilder(
            side=side,
            radius=radius,
            depth=hole_height,
            rounding_radius=rounding_radius,
        )
        for side in sides
    )


def add_no_lid_finger_holes(spec: dict) -> None:
    """Give a no-lid spec its default finger holes, unless it already has some.

    Idempotent on the ``finger_holes`` key: an explicit ``finger_hole(side)``
    call on the builder wins, and a second call to this is a no-op. A spec that
    sets ``auto_finger_holes`` to ``False`` opts out entirely.
    """
    if spec.get("auto_finger_holes", True) and not spec.get("finger_holes"):
        spec["finger_holes"] = no_lid_finger_holes(spec)


def interior_block(spec: dict) -> "Bosl2Solid":
    """The solid that `build_shell` removes — the box's full interior volume.

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

    wt = spec.get("wall_thickness", 2.0)
    ft = spec.get("floor_thickness", 1.6)
    size = [spec["width"] - 2 * wt, spec["length"] - 2 * wt, spec["height"] - ft]

    radius = body_rounding(spec)
    if radius <= 0 or radius >= min(size) / 2:
        return block(size, at=(wt, wt, ft))

    return corner(
        cuboid(size, rounding=radius, edges=Anchor.BOTTOM, **precision_kwargs()),
        size,
        (wt, wt, ft),
    )


def round_inner_rim(body: "Bosl2Solid", spec: dict) -> "Bosl2Solid":
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

    if not spec.get("rim_free") or not spec.get("hollow", True):
        return body

    wt = spec.get("wall_thickness", 2.0)
    ft = spec.get("floor_thickness", 1.6)
    inner_width = spec["width"] - 2 * wt
    inner_length = spec["length"] - 2 * wt
    interior_height = spec["height"] - ft
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
        [spec["width"] + 4 * radius, spec["length"] + 4 * radius, radius + 1.0],
        at=(-2 * radius, -2 * radius, -1.0),
    )
    ring = (CsgSolid(swept.polyhedron()) & keep).mirror([0, 0, 1])
    return body - ring.translate([0.0, 0.0, spec["height"]])
