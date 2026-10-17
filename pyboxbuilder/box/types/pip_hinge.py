# SPDX-License-Identifier: Apache-2.0
"""PrintInPlaceHingeBox — monolithic print-in-place hinged box type (FR-090)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pybosl2.constants import Anchor
from pybosl2.shapes3d import cylinder, wedge

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.shell import block, body_rounding
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.pip_hinge import PrintInPlaceHingeBoxBuilder
from pyboxbuilder.enums import BoxType, CatchType
from pyboxbuilder.rounding import round_edges

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


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
        gap = getattr(spec, "pip_gap_mm", 1.0)
        hr = spec.pip_hinge_radius
        a_clr = spec.pip_axial_clearance
        r_clr = spec.pip_radial_clearance
        n_knuckles = max(3, spec.hinge_count)

        # 1. Main Box Body (tray of height half_h)
        inner_w = spec.width - 2 * wt
        inner_l = spec.length - 2 * wt
        body_outer = block([spec.width, spec.length, half_h], at=(0, 0, 0))
        body_cavity = block([inner_w, inner_l, half_h - ft + 1.0], at=(wt, wt, ft))
        body = body_outer - body_cavity

        # 2. Lid tray of height half_h unfolded flat 180° directly adjacent with gap (OpenSCAD toolkit convention)
        lid_origin_y = spec.length + gap
        lid_outer = block([spec.width, spec.length, half_h], at=(0, lid_origin_y, 0))
        lid_cavity = block([inner_w, inner_l, half_h - lt + 1.0], at=(wt, lid_origin_y + wt, lt))
        lid = lid_outer - lid_cavity

        # 3. Interlocking print-in-place knuckle hinge along the shared mating rim
        # Pivot axis is located exactly at the centerline of the gap at z = half_h
        y_pivot = spec.length + gap / 2.0
        z_pivot = half_h

        # 45-degree self-supporting conical pivots between adjacent knuckles (matching OpenSCAD HingeCone)
        r_cone = min(1.5, hr * 0.5)
        h_cone = r_cone  # 45-degree cone angle

        seg_w = spec.width / n_knuckles
        body_knuckles = []
        lid_knuckles = []
        body_cutouts = []
        lid_cutouts = []

        chamfer_dz = gap / 2.0

        for i in range(n_knuckles):
            x0 = i * seg_w
            x1 = (i + 1) * seg_w

            kx0 = 0.0 if i == 0 else x0 + a_clr / 2.0
            kx1 = spec.width if i == n_knuckles - 1 else x1 - a_clr / 2.0
            k_len = kx1 - kx0
            k_cx = (kx0 + kx1) / 2.0

            # Knuckle barrel cylinder along X
            barrel = (
                cylinder(height=k_len, radius=hr, fn=32)
                .rotate([0, 90, 0])
                .translate([k_cx, y_pivot, z_pivot])
            )

            if i % 2 == 0:
                # Body knuckle (attached to body back wall)
                # Solid attachment block extending from inner back wall to y_pivot
                supp = block(
                    [k_len, (y_pivot - (spec.length - wt)), hr],
                    at=(kx0, spec.length - wt, z_pivot - hr),
                )
                # 45° self-supporting chamfer bracket sloping under overhang into solid body back wall
                chamfer = (
                    wedge(
                        size=[k_len, chamfer_dz, chamfer_dz],
                        anchor=Anchor.FRONT + Anchor.LEFT + Anchor.BOTTOM,
                    )
                    .mirror([0, 0, 1])
                    .translate([kx0, spec.length, z_pivot - hr])
                )
                k_solid = barrel | supp | chamfer

                # Conical sockets on ends where adjacent to lid knuckles
                if i > 0:
                    sock_l = (
                        cylinder(
                            height=h_cone + a_clr,
                            radius1=r_cone + r_clr,
                            radius2=0.0,
                            fn=32,
                        )
                        .rotate([0, 90, 0])
                        .translate([kx0 + (h_cone + a_clr) / 2.0, y_pivot, z_pivot])
                    )
                    k_solid = k_solid - sock_l
                if i < n_knuckles - 1:
                    sock_r = (
                        cylinder(
                            height=h_cone + a_clr,
                            radius1=r_cone + r_clr,
                            radius2=0.0,
                            fn=32,
                        )
                        .rotate([0, -90, 0])
                        .translate([kx1 - (h_cone + a_clr) / 2.0, y_pivot, z_pivot])
                    )
                    k_solid = k_solid - sock_r

                body_knuckles.append(k_solid)

                # Clearance cutout in the lid half in this segment
                c_cyl = (
                    cylinder(height=k_len + a_clr, radius=hr + r_clr, fn=32)
                    .rotate([0, 90, 0])
                    .translate([k_cx, y_pivot, z_pivot])
                )
                c_box = block(
                    [k_len + a_clr, hr + r_clr + 0.5, hr + 1.0],
                    at=(kx0 - a_clr / 2.0, y_pivot, z_pivot - hr),
                )
                lid_cutouts.append(c_cyl | c_box)
            else:
                # Lid knuckle (attached to lid front mating wall)
                # Solid attachment block extending from y_pivot to inner lid front wall
                supp = block(
                    [k_len, (spec.length + gap + wt - y_pivot), hr],
                    at=(kx0, y_pivot, z_pivot - hr),
                )
                # 45° self-supporting chamfer bracket sloping under overhang into solid lid wall
                chamfer = (
                    wedge(
                        size=[k_len, chamfer_dz, chamfer_dz],
                        anchor=Anchor.FRONT + Anchor.LEFT + Anchor.BOTTOM,
                    )
                    .mirror([0, 0, 1])
                    .mirror([0, 1, 0])
                    .translate([kx0, spec.length + gap, z_pivot - hr])
                )
                k_solid = barrel | supp | chamfer

                # Male cones on ends pointing into adjacent body sockets
                if i > 0:
                    cone_l = (
                        cylinder(height=h_cone, radius1=r_cone, radius2=0.0, fn=32)
                        .rotate([0, -90, 0])
                        .translate([kx0 - h_cone / 2.0, y_pivot, z_pivot])
                    )
                    k_solid = k_solid | cone_l
                if i < n_knuckles - 1:
                    cone_r = (
                        cylinder(height=h_cone, radius1=r_cone, radius2=0.0, fn=32)
                        .rotate([0, 90, 0])
                        .translate([kx1 + h_cone / 2.0, y_pivot, z_pivot])
                    )
                    k_solid = k_solid | cone_r

                lid_knuckles.append(k_solid)

                # Clearance cutout in the body half in this segment
                c_cyl = (
                    cylinder(height=k_len + a_clr, radius=hr + r_clr, fn=32)
                    .rotate([0, 90, 0])
                    .translate([k_cx, y_pivot, z_pivot])
                )
                c_box = block(
                    [k_len + a_clr, hr + r_clr + 0.5, hr + 1.0],
                    at=(kx0 - a_clr / 2.0, y_pivot - hr - r_clr - 0.5, z_pivot - hr),
                )
                body_cutouts.append(c_cyl | c_box)

        for bk in body_knuckles:
            body = body | bk
        for bc in body_cutouts:
            body = body - bc

        for lk in lid_knuckles:
            lid = lid | lk
        for lc in lid_cutouts:
            lid = lid - lc

        # Apply corner rounding only to front outer corners of body and back outer corners of lid,
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
        if spec.pip_snap_catch and spec.resolved_catch_type(CatchType.WEDGE) != CatchType.NONE:
            catch_w = min(spec.pip_snap_width, spec.width * 0.4)
            catch_h = min(half_h * 0.4, 4.0)
            tab_th = min(1.2, wt / 2.0)
            c_gap = 0.15
            ridge_d = 0.5
            ridge_h = 1.0
            x_center = spec.width / 2.0
            lid_front_y = lid_origin_y + spec.length

            # Lid tab with triangular ridge
            tab = block([catch_w, tab_th, catch_h], at=(x_center - catch_w / 2.0, lid_front_y - tab_th, half_h))
            ridge = (
                wedge(
                    size=[catch_w, ridge_d, ridge_h],
                    anchor=Anchor.FRONT + Anchor.LEFT + Anchor.BOTTOM,
                )
                .translate([
                    x_center - catch_w / 2.0,
                    lid_front_y - tab_th - ridge_d,
                    half_h + catch_h - ridge_h,
                ])
            )
            lid = lid | tab | ridge

            # Body pocket with matching groove
            pocket = block(
                [catch_w + 2 * c_gap, tab_th + 2 * c_gap, catch_h + c_gap + 0.5],
                at=(x_center - catch_w / 2.0 - c_gap, -c_gap, half_h - catch_h - c_gap),
            )
            groove = block(
                [catch_w + 2 * c_gap, ridge_d + 2 * c_gap, ridge_h + 2 * c_gap],
                at=(x_center - catch_w / 2.0 - c_gap, tab_th - c_gap, half_h - catch_h - c_gap),
            )
            body = body - (pocket | groove)

        monolithic = body | lid

        from pyboxbuilder.box.features import apply_stackable_body

        return apply_stackable_body(monolithic, spec)

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid | None:
        """Return None since PRINT_IN_PLACE_HINGE is a monolithic 1-piece print."""
        return None
