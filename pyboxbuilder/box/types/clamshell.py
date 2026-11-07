# SPDX-License-Identifier: Apache-2.0
"""ClamshellBox — bifold / clamshell book box type with filament pin hinge (FR-088)."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.features import (
    apply_stackable_body,
    apply_stackable_lid,
    filament_hinge,
    hinge_catch,
    hinge_intrusion,
)
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.shell import block, body_rounding, build_shell
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.clamshell import ClamshellBoxBuilder
from pyboxbuilder.enums import BoxType
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
        return replace(spec, height=half_h, interior_top=half_h)

    def interior_mask(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the lower tray interior, excluding the rear filament hinge intrusion."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        half_h = spec.height / 2.0
        available = block(
            [spec.width - 2 * wt, spec.length - 2 * wt, half_h],
            at=(wt, wt, ft),
        )
        return available - hinge_intrusion(self._body_spec(spec), spec.filament_diameter)

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the lower tray half with interleaved filament-hinge knuckles and front catch."""
        wt = spec.wall_thickness
        lt = spec.lid_thickness
        half_h = spec.height / 2.0
        radius_h = max(wt, spec.filament_diameter)

        body_spec = self._body_spec(spec)
        closure = filament_hinge(
            body_spec,
            spec.filament_diameter,
            spec.hinge_count,
            lid_thickness=radius_h,
        )
        body = build_shell(body_spec)
        if closure.body_cut is not None:
            body = body - closure.body_cut
        if closure.body is not None:
            body = body | closure.body
        if closure.pin is not None:
            body = body - closure.pin

        if spec.closure_latch:
            catch = hinge_catch(replace(spec, height=half_h + lt))
            if catch.body_cut is not None:
                body = body - catch.body_cut

        r_body = body_rounding(spec)
        if r_body > 0:
            body = round_edges(
                body,
                [spec.width, spec.length, spec.height],
                r_body,
                list(vertical_edges()),
            )
        return apply_stackable_body(body, spec)

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Return the upper tray half with interleaving filament-hinge knuckles and front catch."""
        wt = spec.wall_thickness
        lt = spec.lid_thickness
        half_h = spec.height / 2.0
        radius_h = max(wt, spec.filament_diameter)
        body_spec = self._body_spec(spec)

        # Upper tray half from z=half_h to z=spec.height, trimmed along back edge for hinge barrel
        axis_y = spec.length - radius_h
        tray_outer = block([spec.width, axis_y, half_h], at=(0.0, 0.0, half_h))
        if half_h > radius_h:
            tray_outer = tray_outer | block(
                [spec.width, radius_h, half_h - radius_h],
                at=(0.0, axis_y, half_h + radius_h),
            )

        inner_w = spec.width - 2 * wt
        inner_l = spec.length - 2 * wt
        inner_h = max(0.5, half_h - lt)
        cavity = block(
            [inner_w, inner_l, inner_h + 0.1],
            at=(wt, wt, half_h - 0.1),
        ) - hinge_intrusion(body_spec, spec.filament_diameter)
        lid = tray_outer - cavity

        closure = filament_hinge(
            body_spec,
            spec.filament_diameter,
            spec.hinge_count,
            lid_thickness=radius_h,
        )
        if closure.lid_cut is not None:
            lid = lid - closure.lid_cut
        if closure.lid is not None:
            lid = lid | closure.lid
        if closure.pin is not None:
            lid = lid - closure.pin

        if spec.closure_latch:
            catch = hinge_catch(replace(spec, height=half_h + lt))
            if catch.lid_cut is not None:
                lid = lid - catch.lid_cut
            if catch.lid is not None:
                lid = lid | catch.lid

        return apply_stackable_lid(lid, spec, top_z=spec.height)
