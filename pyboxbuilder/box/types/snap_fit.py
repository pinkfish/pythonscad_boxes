# SPDX-License-Identifier: Apache-2.0
"""SnapFitBox — cantilever snap-fit latch box type (FR-081)."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.shell import block, body_rounding, build_shell
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.snap_fit import SnapFitBoxBuilder
from pyboxbuilder.enums import BoxType
from pyboxbuilder.rounding import round_edges, vertical_edges

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


@register_box(BoxType.SNAP_FIT, builder=SnapFitBoxBuilder)
class SnapFitBox(BoxTypeBase):
    """Cantilever latch box with positive detents and thumb releases (FR-081)."""

    def interior(self, spec: BoxSpec) -> Interior:
        """Return the usable volume inside the box."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        lt = spec.lid_thickness
        return Interior(
            width=spec.width - 2 * wt,
            length=spec.length - 2 * wt,
            height=spec.height - lt - ft,
            origin_x=wt,
            origin_y=wt,
            origin_z=ft,
        )

    def _body_spec(self, spec: BoxSpec) -> BoxSpec:
        """Return the body spec stopped below the lid plate."""
        return replace(spec, height=spec.height - spec.lid_thickness)

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the box body with recessed latch pockets."""
        from pybosl2.shapes3d import sphere

        from pyboxbuilder.enums import CatchType
        from pyboxbuilder.precision import kwargs as precision_kwargs

        body_spec = self._body_spec(spec)
        body = build_shell(body_spec)

        catch_type = spec.resolved_catch_type(CatchType.WEDGE)
        body_h = body_spec.height
        c_w = spec.cantilever_width
        c_t = spec.cantilever_thickness
        d_h = spec.resolved_catch_size(spec.detent_height)
        clr = spec.deflection_clearance
        arm_drop = min(body_h - spec.floor_thickness, 12.0)

        pocket_w = c_w + 2 * clr
        pocket_h = max(4.0, d_h * 2.5)
        pocket_z = max(body_h - 10.0, spec.floor_thickness + 2.0)

        # Latch arm and pocket cuts on opposing walls
        if spec.latch_axis.lower() == "y":
            # Opposing Y walls (Y=0 and Y=length)
            x_c = spec.width / 2.0
            chan_neg = block(
                [pocket_w, c_t + clr + 0.1, arm_drop + 0.2],
                at=(x_c - pocket_w / 2.0, -0.05, body_h - arm_drop - 0.1),
            )
            chan_pos = block(
                [pocket_w, c_t + clr + 0.1, arm_drop + 0.2],
                at=(x_c - pocket_w / 2.0, spec.length - c_t - clr - 0.05, body_h - arm_drop - 0.1),
            )
            body = body - chan_neg - chan_pos

            if catch_type == CatchType.WEDGE:
                pocket_neg = block(
                    [pocket_w, c_t + d_h + clr + 0.1, pocket_h],
                    at=(x_c - pocket_w / 2.0, -0.05, pocket_z - clr),
                )
                pocket_pos = block(
                    [pocket_w, c_t + d_h + clr + 0.1, pocket_h],
                    at=(x_c - pocket_w / 2.0, spec.length - c_t - d_h - clr - 0.05, pocket_z - clr),
                )
                body = body - pocket_neg - pocket_pos
            elif catch_type == CatchType.BUMP:
                r_bump = min(d_h, c_w / 3.0) + clr
                dimple_neg = sphere(radius=r_bump, **precision_kwargs()).translate(
                    [x_c, c_t, pocket_z + d_h / 2.0]
                )
                dimple_pos = sphere(radius=r_bump, **precision_kwargs()).translate(
                    [x_c, spec.length - c_t, pocket_z + d_h / 2.0]
                )
                body = body - dimple_neg - dimple_pos
            elif catch_type == CatchType.LOOP:
                pocket_neg = block(
                    [pocket_w, c_t + d_h + clr + 0.1, pocket_h],
                    at=(x_c - pocket_w / 2.0, -0.05, pocket_z - clr),
                )
                pocket_pos = block(
                    [pocket_w, c_t + d_h + clr + 0.1, pocket_h],
                    at=(x_c - pocket_w / 2.0, spec.length - c_t - d_h - clr - 0.05, pocket_z - clr),
                )
                ap_w = c_w * 0.6
                ap_h = max(2.5, d_h * 1.5)
                stud_w = ap_w - 2 * clr
                stud_neg = block(
                    [stud_w, d_h, ap_h * 0.7],
                    at=(x_c - stud_w / 2.0, c_t, pocket_z),
                )
                stud_pos = block(
                    [stud_w, d_h, ap_h * 0.7],
                    at=(x_c - stud_w / 2.0, spec.length - c_t - d_h, pocket_z),
                )
                body = body - (pocket_neg - stud_neg) - (pocket_pos - stud_pos)
            elif catch_type == CatchType.MAGNET:
                from pybosl2 import cylinder

                r_m = min(d_h, c_w / 3.0) + clr
                cyl_neg = cylinder(height=d_h + 0.1, radius=r_m, **precision_kwargs()).rotate([90, 0, 0]).translate(
                    [x_c, c_t + d_h / 2.0, pocket_z + d_h / 2.0]
                )
                cyl_pos = cylinder(height=d_h + 0.1, radius=r_m, **precision_kwargs()).rotate([90, 0, 0]).translate(
                    [x_c, spec.length - c_t - d_h / 2.0, pocket_z + d_h / 2.0]
                )
                body = body - cyl_neg - cyl_pos
            elif catch_type == CatchType.LEAF_SPRING:
                pocket_neg = block(
                    [pocket_w, c_t + d_h + clr + 0.1, pocket_h],
                    at=(x_c - pocket_w / 2.0, -0.05, pocket_z - clr),
                )
                pocket_pos = block(
                    [pocket_w, c_t + d_h + clr + 0.1, pocket_h],
                    at=(x_c - pocket_w / 2.0, spec.length - c_t - d_h - clr - 0.05, pocket_z - clr),
                )
                body = body - pocket_neg - pocket_pos

        else:
            # Opposing X walls (X=0 and X=width)
            y_c = spec.length / 2.0
            chan_neg = block(
                [c_t + clr + 0.1, pocket_w, arm_drop + 0.2],
                at=(-0.05, y_c - pocket_w / 2.0, body_h - arm_drop - 0.1),
            )
            chan_pos = block(
                [c_t + clr + 0.1, pocket_w, arm_drop + 0.2],
                at=(spec.width - c_t - clr - 0.05, y_c - pocket_w / 2.0, body_h - arm_drop - 0.1),
            )
            body = body - chan_neg - chan_pos

            if catch_type == CatchType.WEDGE:
                pocket_neg = block(
                    [c_t + d_h + clr + 0.1, pocket_w, pocket_h],
                    at=(-0.05, y_c - pocket_w / 2.0, pocket_z - clr),
                )
                pocket_pos = block(
                    [c_t + d_h + clr + 0.1, pocket_w, pocket_h],
                    at=(spec.width - c_t - d_h - clr - 0.05, y_c - pocket_w / 2.0, pocket_z - clr),
                )
                body = body - pocket_neg - pocket_pos
            elif catch_type == CatchType.BUMP:
                r_bump = min(d_h, c_w / 3.0) + clr
                dimple_neg = sphere(radius=r_bump, **precision_kwargs()).translate(
                    [c_t, y_c, pocket_z + d_h / 2.0]
                )
                dimple_pos = sphere(radius=r_bump, **precision_kwargs()).translate(
                    [spec.width - c_t, y_c, pocket_z + d_h / 2.0]
                )
                body = body - dimple_neg - dimple_pos
            elif catch_type == CatchType.LOOP:
                pocket_neg = block(
                    [c_t + d_h + clr + 0.1, pocket_w, pocket_h],
                    at=(-0.05, y_c - pocket_w / 2.0, pocket_z - clr),
                )
                pocket_pos = block(
                    [c_t + d_h + clr + 0.1, pocket_w, pocket_h],
                    at=(spec.width - c_t - d_h - clr - 0.05, y_c - pocket_w / 2.0, pocket_z - clr),
                )
                ap_w = c_w * 0.6
                ap_h = max(2.5, d_h * 1.5)
                stud_w = ap_w - 2 * clr
                stud_neg = block(
                    [d_h, stud_w, ap_h * 0.7],
                    at=(c_t, y_c - stud_w / 2.0, pocket_z),
                )
                stud_pos = block(
                    [d_h, stud_w, ap_h * 0.7],
                    at=(spec.width - c_t - d_h, y_c - stud_w / 2.0, pocket_z),
                )
                body = body - (pocket_neg - stud_neg) - (pocket_pos - stud_pos)
            elif catch_type == CatchType.MAGNET:
                from pybosl2 import cylinder

                r_m = min(d_h, c_w / 3.0) + clr
                cyl_neg = cylinder(height=d_h + 0.1, radius=r_m, **precision_kwargs()).rotate([0, 90, 0]).translate(
                    [c_t + d_h / 2.0, y_c, pocket_z + d_h / 2.0]
                )
                cyl_pos = cylinder(height=d_h + 0.1, radius=r_m, **precision_kwargs()).rotate([0, 90, 0]).translate(
                    [spec.width - c_t - d_h / 2.0, y_c, pocket_z + d_h / 2.0]
                )
                body = body - cyl_neg - cyl_pos
            elif catch_type == CatchType.LEAF_SPRING:
                pocket_neg = block(
                    [c_t + d_h + clr + 0.1, pocket_w, pocket_h],
                    at=(-0.05, y_c - pocket_w / 2.0, pocket_z - clr),
                )
                pocket_pos = block(
                    [c_t + d_h + clr + 0.1, pocket_w, pocket_h],
                    at=(spec.width - c_t - d_h - clr - 0.05, y_c - pocket_w / 2.0, pocket_z - clr),
                )
                body = body - pocket_neg - pocket_pos

        radius = body_rounding(spec)
        if radius > 0:
            body = round_edges(
                body,
                [spec.width, spec.length, body_h],
                radius,
                list(vertical_edges()),
            )
        return body

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Return the lid plate with cantilever spring arms and retention detents."""
        from pybosl2.shapes3d import sphere

        from pyboxbuilder.enums import CatchType
        from pyboxbuilder.precision import kwargs as precision_kwargs

        lt = spec.lid_thickness
        body_h = spec.height - lt
        lid = block([spec.width, spec.length, lt], at=(0, 0, body_h))

        catch_type = spec.resolved_catch_type(CatchType.WEDGE)
        c_w = spec.cantilever_width
        c_t = spec.cantilever_thickness
        d_h = spec.resolved_catch_size(spec.detent_height)
        arm_drop = min(body_h - spec.floor_thickness, 12.0)
        pocket_z = max(body_h - 10.0, spec.floor_thickness + 2.0)
        pocket_h = max(4.0, d_h * 2.5)

        if spec.latch_axis.lower() == "y":
            x_c = spec.width / 2.0
            arm_neg = block(
                [c_w, c_t, arm_drop + lt],
                at=(x_c - c_w / 2.0, 0.0, body_h - arm_drop),
            )
            arm_pos = block(
                [c_w, c_t, arm_drop + lt],
                at=(x_c - c_w / 2.0, spec.length - c_t, body_h - arm_drop),
            )

            if catch_type == CatchType.WEDGE:
                detent_neg = block(
                    [c_w, d_h, d_h],
                    at=(x_c - c_w / 2.0, c_t, pocket_z),
                )
                detent_pos = block(
                    [c_w, d_h, d_h],
                    at=(x_c - c_w / 2.0, spec.length - c_t - d_h, pocket_z),
                )
                lid = lid | arm_neg | detent_neg | arm_pos | detent_pos
            elif catch_type == CatchType.BUMP:
                r_bump = min(d_h, c_w / 3.0)
                bump_neg = sphere(radius=r_bump, **precision_kwargs()).translate(
                    [x_c, c_t, pocket_z + d_h / 2.0]
                )
                bump_pos = sphere(radius=r_bump, **precision_kwargs()).translate(
                    [x_c, spec.length - c_t, pocket_z + d_h / 2.0]
                )
                lid = lid | arm_neg | bump_neg | arm_pos | bump_pos
            elif catch_type == CatchType.LOOP:
                ap_w = c_w * 0.6
                ap_h = max(2.5, d_h * 1.5)
                ap_neg = block([ap_w, c_t + 0.2, ap_h], at=(x_c - ap_w / 2.0, -0.1, pocket_z))
                ap_pos = block([ap_w, c_t + 0.2, ap_h], at=(x_c - ap_w / 2.0, spec.length - c_t - 0.1, pocket_z))
                lid = lid | (arm_neg - ap_neg) | (arm_pos - ap_pos)
            elif catch_type == CatchType.MAGNET:
                from pybosl2 import cylinder

                r_m = min(d_h, c_w / 3.0)
                cyl_neg = cylinder(height=c_t + 0.2, radius=r_m, **precision_kwargs()).rotate([90, 0, 0]).translate(
                    [x_c, c_t / 2.0, pocket_z + d_h / 2.0]
                )
                cyl_pos = cylinder(height=c_t + 0.2, radius=r_m, **precision_kwargs()).rotate([90, 0, 0]).translate(
                    [x_c, spec.length - c_t / 2.0, pocket_z + d_h / 2.0]
                )
                lid = lid | (arm_neg - cyl_neg) | (arm_pos - cyl_pos)
            elif catch_type == CatchType.LEAF_SPRING:
                detent_neg = block(
                    [c_w, d_h, d_h],
                    at=(x_c - c_w / 2.0, c_t, pocket_z),
                )
                detent_pos = block(
                    [c_w, d_h, d_h],
                    at=(x_c - c_w / 2.0, spec.length - c_t - d_h, pocket_z),
                )
                waist_h = max(2.0, (arm_drop - pocket_h) * 0.5)
                waist_neg = block(
                    [c_w + 0.2, c_t * 0.4, waist_h],
                    at=(x_c - c_w / 2.0 - 0.1, -0.1, body_h - waist_h),
                )
                waist_pos = block(
                    [c_w + 0.2, c_t * 0.4, waist_h],
                    at=(x_c - c_w / 2.0 - 0.1, spec.length - c_t * 0.4 + 0.1, body_h - waist_h),
                )
                lid = lid | (arm_neg - waist_neg) | detent_neg | (arm_pos - waist_pos) | detent_pos
            else:
                lid = lid | arm_neg | arm_pos
        else:
            y_c = spec.length / 2.0
            arm_neg = block(
                [c_t, c_w, arm_drop + lt],
                at=(0.0, y_c - c_w / 2.0, body_h - arm_drop),
            )
            arm_pos = block(
                [c_t, c_w, arm_drop + lt],
                at=(spec.width - c_t, y_c - c_w / 2.0, body_h - arm_drop),
            )

            if catch_type == CatchType.WEDGE:
                detent_neg = block(
                    [d_h, c_w, d_h],
                    at=(c_t, y_c - c_w / 2.0, pocket_z),
                )
                detent_pos = block(
                    [d_h, c_w, d_h],
                    at=(spec.width - c_t - d_h, y_c - c_w / 2.0, pocket_z),
                )
                lid = lid | arm_neg | detent_neg | arm_pos | detent_pos
            elif catch_type == CatchType.BUMP:
                r_bump = min(d_h, c_w / 3.0)
                bump_neg = sphere(radius=r_bump, **precision_kwargs()).translate(
                    [c_t, y_c, pocket_z + d_h / 2.0]
                )
                bump_pos = sphere(radius=r_bump, **precision_kwargs()).translate(
                    [spec.width - c_t, y_c, pocket_z + d_h / 2.0]
                )
                lid = lid | arm_neg | bump_neg | arm_pos | bump_pos
            elif catch_type == CatchType.LOOP:
                ap_w = c_w * 0.6
                ap_h = max(2.5, d_h * 1.5)
                ap_neg = block([c_t + 0.2, ap_w, ap_h], at=(-0.1, y_c - ap_w / 2.0, pocket_z))
                ap_pos = block([c_t + 0.2, ap_w, ap_h], at=(spec.width - c_t - 0.1, y_c - ap_w / 2.0, pocket_z))
                lid = lid | (arm_neg - ap_neg) | (arm_pos - ap_pos)
            elif catch_type == CatchType.MAGNET:
                from pybosl2 import cylinder

                r_m = min(d_h, c_w / 3.0)
                cyl_neg = cylinder(height=c_t + 0.2, radius=r_m, **precision_kwargs()).rotate([0, 90, 0]).translate(
                    [c_t / 2.0, y_c, pocket_z + d_h / 2.0]
                )
                cyl_pos = cylinder(height=c_t + 0.2, radius=r_m, **precision_kwargs()).rotate([0, 90, 0]).translate(
                    [spec.width - c_t / 2.0, y_c, pocket_z + d_h / 2.0]
                )
                lid = lid | (arm_neg - cyl_neg) | (arm_pos - cyl_pos)
            elif catch_type == CatchType.LEAF_SPRING:
                detent_neg = block(
                    [d_h, c_w, d_h],
                    at=(c_t, y_c - c_w / 2.0, pocket_z),
                )
                detent_pos = block(
                    [d_h, c_w, d_h],
                    at=(spec.width - c_t - d_h, y_c - c_w / 2.0, pocket_z),
                )
                waist_h = max(2.0, (arm_drop - pocket_h) * 0.5)
                waist_neg = block(
                    [c_t * 0.4, c_w + 0.2, waist_h],
                    at=(-0.1, y_c - c_w / 2.0 - 0.1, body_h - waist_h),
                )
                waist_pos = block(
                    [c_t * 0.4, c_w + 0.2, waist_h],
                    at=(spec.width - c_t * 0.4 + 0.1, y_c - c_w / 2.0 - 0.1, body_h - waist_h),
                )
                lid = lid | (arm_neg - waist_neg) | detent_neg | (arm_pos - waist_pos) | detent_pos
            else:
                lid = lid | arm_neg | arm_pos

        radius = body_rounding(spec)
        if radius > 0:
            lid = round_edges(
                lid,
                [spec.width, spec.length, lt],
                radius,
                list(vertical_edges()),
            )
        return lid
