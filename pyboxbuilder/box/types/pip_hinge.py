# SPDX-License-Identifier: Apache-2.0
"""PrintInPlaceHingeBox — monolithic print-in-place hinged box type (FR-090)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pybosl2.parts.hinges import KnuckleHingePair, SnapLock, SnapSocket

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.shell import block, body_rounding
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.pip_hinge import PrintInPlaceHingeBoxBuilder
from pyboxbuilder.enums import BoxType, CatchType
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
        """Return the usable interior volume of the base tray half."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        half_h = spec.height / 2.0
        inner_w = spec.width - 2 * wt
        inner_l = spec.length - 2 * wt
        inner_h = half_h - ft
        return Interior(
            width=inner_w,
            length=inner_l,
            height=inner_h,
            origin_x=wt,
            origin_y=wt,
            origin_z=ft,
        )

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the monolithic print containing body tray, lid tray, pybosl2 KnuckleHingePair, and snap catches."""
        from pybosl2.constants import Anchor
        from pybosl2.shapes3d import wedge

        wt = spec.wall_thickness
        ft = spec.floor_thickness
        lt = spec.lid_thickness
        half_h = spec.height / 2.0
        hr = spec.pip_hinge_radius
        a_clr = spec.pip_axial_clearance

        # 1. Main Box Body (tray of height half_h)
        inner_w = spec.width - 2 * wt
        inner_l = spec.length - 2 * wt
        body_outer = block([spec.width, spec.length, half_h], at=(0, 0, 0))
        body_cavity = block([inner_w, inner_l, half_h - ft + 1.0], at=(wt, wt, ft))
        body = body_outer - body_cavity

        # 2. Interlocking print-in-place knuckle hinge pair from pybosl2 along shared rim (z = half_h)
        arm = max(4.0, hr + 1.0)
        hinge_gap = 2.0 * (arm + hr)
        hinge_y = spec.length + arm + hr
        lid_origin_y = spec.length + hinge_gap
        thick = min(wt, hr)

        hinge_obj = KnuckleHingePair(
            length=spec.width,
            segs=spec.hinge_count,
            knuckle_diam=hr * 2.0,
            pin_diam=max(1.5, hr * 0.8),
            arm=arm,
            thick=thick,
            gap=a_clr,
            pin=True,
        )
        hinge = _to_solid(hinge_obj).translate([spec.width / 2.0, hinge_y, half_h])

        # Self-supporting 45-degree chamfer brackets under the hinge arms
        z_arm_bottom = half_h - thick / 2.0
        chamfer_h = min(arm, z_arm_bottom)
        if chamfer_h > 0.5:
            supp_body = wedge(
                size=[spec.width, arm, chamfer_h],
                anchor=Anchor.FRONT + Anchor.LEFT + Anchor.BOTTOM,
            ).translate([0.0, spec.length, z_arm_bottom - chamfer_h])

            supp_lid = wedge(
                size=[spec.width, arm, chamfer_h],
                anchor=Anchor.FRONT + Anchor.LEFT + Anchor.BOTTOM,
            ).mirror([0, 1, 0]).translate([0.0, lid_origin_y, z_arm_bottom - chamfer_h])

            hinge = hinge | supp_body | supp_lid

        # 3. Lid tray of height half_h unfolded flat 180° behind the body along Y
        lid_outer = block(
            [spec.width, spec.length, half_h],
            at=(0, lid_origin_y, 0),
        )
        lid_cavity = block(
            [inner_w, inner_l, half_h - lt + 1.0],
            at=(wt, lid_origin_y + wt, lt),
        )
        lid = lid_outer - lid_cavity

        monolithic = body | lid | hinge

        # 4. SnapLock & SnapSocket catches from pybosl2.parts.hinges
        if spec.pip_snap_catch and spec.resolved_catch_type(CatchType.WEDGE) != CatchType.NONE:
            catch_w = min(spec.pip_snap_width, spec.width * 0.4)
            snap_diam = spec.pip_snap_diameter
            sock_obj = SnapSocket(
                thick=wt,
                snaplen=catch_w,
                snapdiam=snap_diam,
                foldangle=180,
            )
            sock = _to_solid(sock_obj)
            sock_placed = sock.translate([spec.width / 2.0, wt / 2.0, half_h])

            lock_obj = SnapLock(
                thick=wt,
                snaplen=catch_w,
                snapdiam=snap_diam,
                foldangle=180,
            )
            lock = _to_solid(lock_obj)
            lock_placed = lock.translate(
                [spec.width / 2.0, lid_origin_y + spec.length - wt / 2.0, half_h]
            )
            monolithic = monolithic | sock_placed | lock_placed

        radius = body_rounding(spec)
        if radius > 0:
            monolithic = round_edges(
                monolithic,
                [spec.width, spec.length, half_h],
                radius,
                list(vertical_edges()),
            )
        from pyboxbuilder.box.features import apply_stackable_body

        return apply_stackable_body(monolithic, spec)

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid | None:
        """Return None since PRINT_IN_PLACE_HINGE is a monolithic 1-piece print."""
        return None
