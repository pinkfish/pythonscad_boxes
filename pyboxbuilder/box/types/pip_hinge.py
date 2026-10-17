# SPDX-License-Identifier: Apache-2.0
"""PrintInPlaceHingeBox — monolithic print-in-place hinged box type (FR-090)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pybosl2 import Path2D
from pybosl2.constants import Anchor
from pybosl2.parts.hinges import KnuckleHingePair
from pybosl2.shapes2d import polygon
from pybosl2.shapes3d import wedge

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.shell import block, body_rounding
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.pip_hinge import PrintInPlaceHingeBoxBuilder
from pyboxbuilder.enums import BoxType, CatchType
from pyboxbuilder.rounding import round_edges

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
        """Return the monolithic print with body, lid, middle knuckle hinge, and front snap catch."""
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

        # 2. Interlocking print-in-place knuckle hinge in the middle section between body and lid
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

        # Apply corner rounding only to the front outer corners of body and back outer corners of lid,
        # preserving the square hinge interface along the back wall so the knuckle hinge
        # joins flush from side wall to side wall without disconnected edges.
        radius = body_rounding(spec)
        if radius > 0:
            body = round_edges(
                body,
                [spec.width, spec.length, half_h],
                radius,
                [Anchor.FRONT_LEFT, Anchor.FRONT_RIGHT],
                at=(0.0, 0.0, 0.0),
            )
            lid = round_edges(
                lid,
                [spec.width, spec.length, half_h],
                radius,
                [Anchor.BACK_LEFT, Anchor.BACK_RIGHT],
                at=(0.0, lid_origin_y, 0.0),
            )

        # 4. Snap-fit catch on the front walls (CatchType.WEDGE or BUMP)
        # Sits on the front rims: flat tab with triangular ridge on lid, recessed pocket on body
        # Cleanly avoids horizontal cylinders so it does not look like part of a hinge
        if spec.pip_snap_catch and spec.resolved_catch_type(CatchType.WEDGE) != CatchType.NONE:
            catch_w = min(spec.pip_snap_width, spec.width * 0.4)
            catch_h = min(half_h * 0.4, 4.0)
            tab_th = min(1.2, wt / 2.0)
            gap = 0.15
            ridge_d = 0.5
            ridge_h = 1.0
            x_center = spec.width / 2.0
            lid_front_y = lid_origin_y + spec.length

            # Lid tab with triangular ridge
            tab = block([catch_w, tab_th, catch_h], at=(x_center - catch_w / 2.0, lid_front_y - tab_th, half_h))
            ridge_poly = polygon(path=Path2D([
                (0.0, 0.0),
                (-ridge_d, 0.0),
                (0.0, ridge_h),
            ]))
            ridge = (
                ridge_poly.linear_extrude(height=catch_w)
                .rotate([0, 90, 0])
                .rotate([0, 0, 90])
                .translate([x_center - catch_w / 2.0, lid_front_y - tab_th, half_h + catch_h - ridge_h])
            )
            lid = lid | tab | ridge

            # Body pocket with matching groove
            pocket = block(
                [catch_w + 2 * gap, tab_th + gap, catch_h + gap],
                at=(x_center - catch_w / 2.0 - gap, -gap, half_h - catch_h),
            )
            groove = block(
                [catch_w + 2 * gap, ridge_d + gap + 0.1, ridge_h + gap],
                at=(x_center - catch_w / 2.0 - gap, tab_th - gap, half_h - catch_h),
            )
            body = body - (pocket | groove)

        monolithic = body | lid | hinge

        from pyboxbuilder.box.features import apply_stackable_body

        return apply_stackable_body(monolithic, spec)

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid | None:
        """Return None since PRINT_IN_PLACE_HINGE is a monolithic 1-piece print."""
        return None
