# SPDX-License-Identifier: Apache-2.0
"""NoLidBox — no-lid (open tray) box type with stackable rims and magnets."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.precision import kwargs as precision_kwargs

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.enums import MagnetType, ScoopSide, StackableMode


class NoLidBox(BoxTypeBase):
    """No-lid box type (open tray). Supports stackable rims and side magnets."""

    def interior(self, spec: BoxSpec) -> Interior:
        """Return the frame the box's contents may occupy."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        return Interior(
            width=spec.width - 2 * wt,
            length=spec.length - 2 * wt,
            height=spec.height - ft,
            origin_x=wt, origin_y=wt, origin_z=ft,
        )

    def _build_shell(self, spec: BoxSpec) -> Bosl2Solid:
        from pyboxbuilder.box.shell import build_shell, with_no_lid_finger_holes

        # A no-lid box has no lid band, whoever built the spec: `Project` sets
        # this from the box type, but a spec assembled by hand would otherwise
        # get its rim left square and every top-aligned feature — the finger
        # holes below among them — hung a lid thickness too low (FR-043f).
        spec = replace(spec, rim_free=True)
        spec = with_no_lid_finger_holes(spec)
        body = build_shell(spec)
        return body

    def _add_stackable_rim(self, body: Bosl2Solid, spec: BoxSpec) -> Bosl2Solid:
        """Add an interlocking ring for stackable boxes.

        inside  → a recess carved into the top rim (box nests inside the box above)
        outside → a ridge added around the outside (box fits around the box below)
        """
        from pyboxbuilder.box.shell import block

        wt = spec.wall_thickness
        stack = spec.stackable_thickness or wt
        fit = spec.stackable_fit_offset
        mode = spec.stackable or StackableMode.INSIDE

        if mode is StackableMode.INSIDE:
            # Carve a recess around the top rim, so the box above nests into it.
            recess_w = spec.width - 2 * (wt - fit)
            recess_l = spec.length - 2 * (wt - fit)
            recess = block(
                [recess_w, recess_l, stack + 0.5],
                at=(
                    (spec.width - recess_w) / 2,
                    (spec.length - recess_l) / 2,
                    spec.height - stack,
                ),
            )
            return body - recess
        elif mode == "outside":
            # Add a ridge around the bottom outside, so it grips the box below.
            ridge_w = spec.width + 2 * (stack - fit)
            ridge_l = spec.length + 2 * (stack - fit)
            ridge = block(
                [ridge_w, ridge_l, stack],
                at=(
                    (spec.width - ridge_w) / 2,
                    (spec.length - ridge_l) / 2,
                    0,
                ),
            )
            return body | ridge
        return body

    def _add_magnet_slots(self, body: Bosl2Solid, spec: BoxSpec) -> Bosl2Solid:
        """Carve magnet cavities into the opposing walls that carry no finger hole.

        Which pair is not cosmetic (FR-039a). A pocket is cut at the middle of a
        wall at mid-height, and FR-047's holes are cut at the middle of the two
        longer walls: pinned to one fixed pair, the two land in the same wall
        whenever the footprint is the other way round, and the magnet ends up
        inside the finger cut — a tray with a hole where a magnet should be, and
        nothing in the geometry to say so. Both pairs are opposing, so taking
        the free one costs the attraction FR-039 is about exactly nothing.
        """
        from pybosl2 import cuboid, cylinder

        magnet_type = spec.magnet_type
        if magnet_type is None or magnet_type is MagnetType.NONE:
            return body

        size = spec.magnet_size
        depth = size[2] if size and len(size) > 2 else (
            3.0 if magnet_type is MagnetType.ROUND else 2.0
        )
        on_front_back = self._magnet_sides_front_back(spec)

        def slot() -> Bosl2Solid:
            """Return a fresh solid per side — one handle must not span two branches."""
            if magnet_type is MagnetType.ROUND:
                diameter = size[0] if size else 6.0
                # Lay the cylinder along the axis it sinks into the wall on.
                spin = [90, 0, 0] if on_front_back else [0, 90, 0]
                return cylinder(height=depth, radius=diameter / 2 + 0.1, **precision_kwargs()).rotate(spin)
            w = size[0] if size else 10.0
            l = size[1] if size and len(size) > 1 else 5.0
            box = [w + 0.2, depth, l + 0.2] if on_front_back else [depth, w + 0.2, l + 0.2]
            return cuboid(box)

        mid_h = spec.height / 2
        # Blind pockets in the middle of the two opposing walls, open outward.
        if on_front_back:
            centres = (
                [spec.width / 2, depth / 2, mid_h],
                [spec.width / 2, spec.length - depth / 2, mid_h],
            )
        else:
            centres = (
                [depth / 2, spec.length / 2, mid_h],
                [spec.width - depth / 2, spec.length / 2, mid_h],
            )

        return body - slot().translate(centres[0]) - slot().translate(centres[1])

    @staticmethod
    def _magnet_sides_front_back(spec: BoxSpec) -> bool:
        """Return True when the magnets belong in the FRONT/BACK pair (FR-039a).

        The free pair is whichever one the finger holes did not take. Holes are
        read off the spec rather than recomputed, so an explicit `finger_hole()`
        moves the magnets exactly as the automatic pair does; with holes on both
        pairs (or none) the front/back default stands and FR-006c reports any
        collision rather than this guessing.
        """
        holes = spec.finger_holes or ()
        sides = {getattr(hole, "side", None) for hole in holes}
        front_back = {ScoopSide.FRONT, ScoopSide.BACK} & sides
        left_right = {ScoopSide.LEFT, ScoopSide.RIGHT} & sides
        return not (front_back and not left_right)

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Build the tray, adding the stackable rim and magnet slots when asked."""
        body = self._build_shell(spec)
        if spec.stackable:
            body = self._add_stackable_rim(body, spec)
        if spec.magnet_type not in (None, MagnetType.NONE):
            body = self._add_magnet_slots(body, spec)
        return body

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """No-lid boxes have no lid."""
        return None
