# SPDX-License-Identifier: Apache-2.0
"""ClamshellBox — bifold / clamshell book box type with filament pin hinge (FR-088)."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.features import (
    PRINT_IN_PLACE_GAP_MM,
    Closure,
    hinge_catch,
    hinge_intrusion,
)
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.shell import block, body_rounding, build_shell, corner
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.clamshell import ClamshellBoxBuilder
from pyboxbuilder.compartments.element import union_all
from pyboxbuilder.enums import BoxType
from pyboxbuilder.precision import kwargs as precision_kwargs
from pyboxbuilder.rounding import round_edges, vertical_edges

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


@register_box(BoxType.CLAMSHELL, builder=ClamshellBoxBuilder)
class ClamshellBox(BoxTypeBase):
    """Bifold clamshell book box with a mid-height filament pin hinge (FR-088)."""

    def interior(self, spec: BoxSpec) -> Interior:
        """Return the usable interior volume of the base tray half."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        half_h = spec.height / 2.0
        return Interior(
            width=spec.width - 2 * wt,
            length=spec.length - 2 * wt,
            height=half_h - ft,
            origin_x=wt,
            origin_y=wt,
            origin_z=ft,
        )

    @staticmethod
    def _body_spec(spec: BoxSpec) -> BoxSpec:
        """Return the lower tray half spec stopping at ``spec.height / 2``."""
        half_h = spec.height / 2.0
        radius_h = max(spec.wall_thickness, spec.filament_diameter)
        return replace(spec, height=half_h, interior_top=half_h, lid_thickness=radius_h)

    @staticmethod
    def _clamshell_hinge(spec: BoxSpec) -> Closure:
        """Build symmetric mid-plane filament-pin knuckles for lower and upper tray walls."""
        from pybosl2 import Path2D, cylinder
        from pybosl2.shapes2d import polygon

        wt = spec.wall_thickness
        half_h = spec.height / 2.0
        radius_h = max(wt, spec.filament_diameter)
        bore = spec.filament_diameter / 2.0 + 0.2
        gap = PRINT_IN_PLACE_GAP_MM
        r_c = radius_h + gap
        knuckles = max(2, spec.hinge_count)
        axis_y = spec.length - radius_h
        axis_z = half_h
        span = spec.width
        pitch = span / knuckles

        body_parts, lid_parts = [], []
        body_relief, lid_relief = [], []

        wedge_depth = 2.0 * radius_h
        body_poly = polygon(
            path=Path2D(
                [
                    (axis_y - radius_h, axis_z - gap / 2.0),
                    (spec.length, axis_z - gap / 2.0),
                    (spec.length, max(0.0, axis_z - wedge_depth)),
                ]
            )
        )
        lid_poly = polygon(
            path=Path2D(
                [
                    (axis_y - radius_h, axis_z + gap / 2.0),
                    (spec.length, min(spec.height, axis_z + wedge_depth)),
                    (spec.length, axis_z + gap / 2.0),
                ]
            )
        )

        for index in range(knuckles):
            x0 = 0.0 if index == 0 else index * pitch + gap / 2.0
            x1 = span if index == knuckles - 1 else (index + 1) * pitch - gap / 2.0
            length = x1 - x0
            if length <= 0:
                continue
            centre_x = (x0 + x1) / 2.0
            knuckle = (
                cylinder(height=length, radius=radius_h, **precision_kwargs())
                .rotate([0, 90, 0])
                .translate([centre_x, axis_y, axis_z])
            )
            r_x0 = -1.0 if index == 0 else x0 - gap
            r_x1 = span + 1.0 if index == knuckles - 1 else x1 + gap
            r_len = r_x1 - r_x0
            r_cx = (r_x0 + r_x1) / 2.0
            relief_cyl = (
                cylinder(height=r_len, radius=r_c, **precision_kwargs())
                .rotate([0, 90, 0])
                .translate([r_cx, axis_y, axis_z])
            )
            if index % 2 == 1:
                wedge = (
                    lid_poly.linear_extrude(height=length)
                    .rotate([0, 90, 0])
                    .rotate([-90, 0, 0])
                    .scale([1, -1, -1])
                    .translate([x0, 0.0, 0.0])
                )
                back_fill = block(
                    [length, radius_h, radius_h - gap / 2.0],
                    at=(x0, axis_y, axis_z + gap / 2.0),
                )
                lid_parts += [knuckle, wedge, back_fill]

                relief_back = block(
                    [r_len, radius_h + r_c + 1.0, r_c + 1.0],
                    at=(r_x0, axis_y - r_c, axis_z - r_c),
                )
                relief_above = block(
                    [r_len, 2.0 * radius_h + gap + 1.0, wedge_depth + gap + 1.0],
                    at=(r_x0, axis_y - radius_h - gap, axis_z),
                )
                body_relief += [relief_cyl, relief_back, relief_above]
            else:
                wedge = (
                    body_poly.linear_extrude(height=length)
                    .rotate([0, 90, 0])
                    .rotate([-90, 0, 0])
                    .scale([1, -1, -1])
                    .translate([x0, 0.0, 0.0])
                )
                back_fill = block(
                    [length, radius_h, radius_h - gap / 2.0],
                    at=(x0, axis_y, axis_z - radius_h),
                )
                body_parts += [knuckle, wedge, back_fill]

                relief_back = block(
                    [r_len, radius_h + r_c + 1.0, r_c + 1.0],
                    at=(r_x0, axis_y - r_c, axis_z - 1.0),
                )
                relief_below = block(
                    [r_len, 2.0 * radius_h + gap + 1.0, wedge_depth + gap + 1.0],
                    at=(r_x0, axis_y - radius_h - gap, axis_z - wedge_depth - gap - 1.0),
                )
                lid_relief += [relief_cyl, relief_back, relief_below]

        pin = (
            cylinder(height=spec.width + 2.0, radius=bore, **precision_kwargs())
            .rotate([0, 90, 0])
            .translate([spec.width / 2.0, axis_y, axis_z])
        )

        return Closure(
            body=union_all(body_parts),
            lid=union_all(lid_parts),
            body_cut=union_all(body_relief),
            lid_cut=union_all(lid_relief),
            pin=pin,
        )

    def interior_mask(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the lower tray interior, excluding the rear filament hinge intrusion."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        lt = spec.lid_thickness
        half_h = spec.height / 2.0
        available = block(
            [spec.width - 2 * wt, spec.length - 2 * wt, half_h],
            at=(wt, wt, ft),
        )
        mask = available - hinge_intrusion(self._body_spec(spec), spec.filament_diameter)
        if spec.closure_latch:
            catch = hinge_catch(replace(spec, height=half_h + lt), vertical_wall=True)
            if catch.body is not None:
                mask = mask - catch.body
        return mask

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the lower tray half with interleaved filament-hinge knuckles and front catch."""
        lt = spec.lid_thickness
        half_h = spec.height / 2.0

        body_spec = self._body_spec(spec)
        closure = self._clamshell_hinge(spec)
        body = build_shell(body_spec)
        if closure.body_cut is not None:
            body = body - closure.body_cut
        if closure.body is not None:
            body = body | closure.body
        if closure.pin is not None:
            body = body - closure.pin

        r_body = body_rounding(spec)
        if r_body > 0:
            body = round_edges(
                body,
                [spec.width, spec.length, spec.height],
                r_body,
                list(vertical_edges()),
            )

        if spec.closure_latch:
            catch = hinge_catch(replace(spec, height=half_h + lt), vertical_wall=True)
            if catch.body_cut is not None:
                body = body - catch.body_cut
            if catch.body is not None:
                body = body | catch.body

        self._reject_stackable(spec)
        from pyboxbuilder.box.features import apply_stackable_body

        return apply_stackable_body(body, spec, anchor_top_z=half_h - 0.2)

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Return the upper tray half with interleaving filament-hinge knuckles and front catch."""
        from pybosl2 import Anchor, cuboid

        wt = spec.wall_thickness
        lt = spec.lid_thickness
        half_h = spec.height / 2.0

        tray_outer = block([spec.width, spec.length, half_h], at=(0.0, 0.0, half_h))

        inner_w = spec.width - 2 * wt
        inner_l = spec.length - 2 * wt
        inner_h = max(0.5, half_h - lt)
        cavity_size = [inner_w, inner_l, inner_h + 0.1]
        r_inner = body_rounding(spec)
        if 0 < r_inner < min(cavity_size) / 2.0:
            cavity = corner(
                cuboid(cavity_size, rounding=r_inner, edges=Anchor.TOP, **precision_kwargs()),
                cavity_size,
                (wt, wt, half_h - 0.1),
            )
        else:
            cavity = block(cavity_size, at=(wt, wt, half_h - 0.1))
        lid = tray_outer - cavity

        closure = self._clamshell_hinge(spec)
        if closure.lid_cut is not None:
            lid = lid - closure.lid_cut
        if closure.lid is not None:
            lid = lid | closure.lid
        if closure.pin is not None:
            lid = lid - closure.pin

        if spec.closure_latch:
            catch = hinge_catch(replace(spec, height=half_h + lt), vertical_wall=True)
            if catch.lid_cut is not None:
                lid = lid - catch.lid_cut
            if catch.lid is not None:
                lid = lid | catch.lid

        self._reject_stackable(spec)
        return lid
