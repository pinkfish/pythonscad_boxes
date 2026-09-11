# SPDX-License-Identifier: Apache-2.0
"""PrintInPlaceHingeBox — monolithic print-in-place hinged box type (FR-090)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pybosl2.parts.hinges import KnuckleHingePair, SnapLock, SnapSocket

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.shell import block, body_rounding, build_shell
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.pip_hinge import PrintInPlaceHingeBoxBuilder
from pyboxbuilder.enums import BoxType
from pyboxbuilder.rounding import round_edges, vertical_edges

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


def _to_solid(obj: object) -> Bosl2Solid:
    """Extract the underlying Bosl2Solid across different pybosl2 versions."""
    from typing import cast

    shape_attr = getattr(obj, "shape", None)
    if callable(shape_attr):
        return cast("Bosl2Solid", shape_attr())
    if hasattr(obj, "_solid"):
        return cast("Bosl2Solid", obj._solid)
    if hasattr(obj, "translate"):
        return cast("Bosl2Solid", obj)
    return cast("Bosl2Solid", shape_attr)


@register_box(BoxType.PRINT_IN_PLACE_HINGE, builder=PrintInPlaceHingeBoxBuilder)
class PrintInPlaceHingeBox(BoxTypeBase):
    """Monolithic 180° flat print-in-place captive hinge box (FR-090)."""

    def interior(self, spec: BoxSpec) -> Interior:
        """Return the usable interior volume of the box body."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        lt = spec.lid_thickness
        body_h = spec.height - lt
        inner_w = spec.width - 2 * wt
        inner_l = spec.length - 2 * wt
        inner_h = body_h - ft
        return Interior(
            width=inner_w,
            length=inner_l,
            height=inner_h,
            origin_x=wt,
            origin_y=wt,
            origin_z=ft,
        )

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the monolithic print containing body, lid, pybosl2 KnuckleHingePair, and snap catches."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        lt = spec.lid_thickness
        body_h = spec.height - lt
        hr = spec.pip_hinge_radius
        a_clr = spec.pip_axial_clearance

        # 1. Main Box Body
        body = build_shell(spec)

        # 2. Interlocking print-in-place knuckle hinge pair from pybosl2
        arm = 4.0
        hinge_gap = 2.0 * (arm + hr)
        hinge_y = spec.length + arm + hr
        lid_origin_y = spec.length + hinge_gap

        hinge_obj = KnuckleHingePair(
            length=spec.width,
            segs=spec.hinge_count,
            knuckle_diam=hr * 2.0,
            pin_diam=max(1.5, hr * 0.8),
            arm=arm,
            thick=lt,
            gap=a_clr,
            pin=True,
        )
        hinge = _to_solid(hinge_obj).translate([spec.width / 2.0, hinge_y, hr])

        # 3. Lid unfolded flat 180° behind the body along Y
        lid_outer = block(
            [spec.width, spec.length, lt],
            at=(0, lid_origin_y, 0),
        )
        inner_w = spec.width - 2 * wt
        inner_l = spec.length - 2 * wt
        lid_cavity = block(
            [inner_w, inner_l, lt],
            at=(wt, lid_origin_y + wt, ft),
        )
        lid = lid_outer - lid_cavity

        monolithic = body | lid | hinge

        # 4. SnapLock & SnapSocket catches from pybosl2.parts.hinges
        if spec.pip_snap_catch:
            catch_w = min(spec.pip_snap_width, spec.width * 0.4)
            snap_diam = spec.pip_snap_diameter
            sock_obj = SnapSocket(
                thick=wt,
                snaplen=catch_w,
                snapdiam=snap_diam,
                foldangle=180,
            )
            sock = _to_solid(sock_obj)
            sock_placed = sock.translate([spec.width / 2.0, wt / 2.0, body_h])

            lock_obj = SnapLock(
                thick=wt,
                snaplen=catch_w,
                snapdiam=snap_diam,
                foldangle=180,
            )
            lock = _to_solid(lock_obj)
            lock_placed = lock.translate(
                [spec.width / 2.0, lid_origin_y + spec.length - wt / 2.0, lt]
            )
            monolithic = monolithic | sock_placed | lock_placed

        radius = body_rounding(spec)
        if radius > 0:
            monolithic = round_edges(
                monolithic,
                [spec.width, spec.length, body_h],
                radius,
                list(vertical_edges()),
            )
        return monolithic

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid | None:
        """Return None since PRINT_IN_PLACE_HINGE is a monolithic 1-piece print."""
        return None
