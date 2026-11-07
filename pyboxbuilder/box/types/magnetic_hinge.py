# SPDX-License-Identifier: Apache-2.0
"""MagneticHingeBox — rear filament-hinge box with a front magnet closure."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from pyboxbuilder.box.spec import BoxSpec

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.builders.magnetic_hinge import MagneticHingeBoxBuilder
from pyboxbuilder.enums import BoxType


@register_box(BoxType.MAGNETIC_HINGE, builder=MagneticHingeBoxBuilder)
class MagneticHingeBox(BoxTypeBase):
    """Hinged box with a filament pin hinge at the back and a small magnet catch at the front."""

    def interior(self, spec: BoxSpec) -> Interior:
        """Return the frame the box's contents may occupy."""
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

    @staticmethod
    def _body_spec(spec: BoxSpec) -> BoxSpec:
        """Return the body spec stopping one lid thickness short of declared height."""
        lt = spec.lid_thickness
        return replace(spec, height=spec.height - lt)

    def lid_keepouts(self, spec: BoxSpec) -> list[tuple[float, float, float]]:
        """Keep lid surface patterns clear of the front magnet socket."""
        from pyboxbuilder.box.features import magnetic_hinge_catch_metrics

        cx, cy, r_boss = magnetic_hinge_catch_metrics(spec)
        return [(cx, cy, r_boss)]

    def interior_mask(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the usable interior volume, less the rear hinge and front magnet boss."""
        from pyboxbuilder.box.features import hinge_intrusion, magnetic_hinge_catch
        from pyboxbuilder.box.shell import block

        wt = spec.wall_thickness
        ft = spec.floor_thickness
        available = block(
            [spec.width - 2 * wt, spec.length - 2 * wt, spec.height],
            at=(wt, wt, ft),
        )
        mask = available - hinge_intrusion(
            self._body_spec(spec), spec.filament_diameter
        )
        front_catch = magnetic_hinge_catch(spec)
        if front_catch.body is not None:
            mask = mask - front_catch.body
        return mask

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the shell with rear hinge knuckles and a front magnet boss and socket."""
        from pyboxbuilder.box.features import (
            apply_stackable_body,
            filament_hinge,
            magnetic_hinge_catch,
        )
        from pyboxbuilder.box.shell import body_rounding, build_shell
        from pyboxbuilder.rounding import round_edges, vertical_edges

        body_spec = self._body_spec(spec)
        closure = filament_hinge(
            body_spec,
            spec.filament_diameter,
            spec.hinge_count,
        )
        body = build_shell(body_spec)
        if closure.body_cut is not None:
            body = body - closure.body_cut
        body = body if closure.body is None else body | closure.body
        if closure.pin is not None:
            body = body - closure.pin

        front_catch = magnetic_hinge_catch(spec)
        if front_catch.body is not None:
            body = body | front_catch.body
        if front_catch.body_cut is not None:
            body = body - front_catch.body_cut

        radius = body_rounding(spec)
        if radius > 0:
            body = round_edges(
                body,
                [spec.width, spec.length, spec.height],
                radius,
                list(vertical_edges()),
            )

        return apply_stackable_body(body, spec)

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Return a hinged lid carrying rear knuckles and a front underside magnet socket."""
        from pyboxbuilder.box.features import (
            apply_stackable_lid,
            filament_hinge,
            magnetic_hinge_catch,
        )
        from pyboxbuilder.box.shell import block

        lt = spec.lid_thickness
        body_spec = self._body_spec(spec)
        radius = max(spec.wall_thickness, spec.filament_diameter)
        axis_y = spec.length - radius
        lid = block(
            [spec.width, axis_y, lt], at=(0, 0, body_spec.height)
        )
        closure = filament_hinge(
            body_spec,
            spec.filament_diameter,
            spec.hinge_count,
        )
        if closure.lid_cut is not None:
            lid = lid - closure.lid_cut
        lid = lid if closure.lid is None else lid | closure.lid
        if closure.pin is not None:
            lid = lid - closure.pin

        front_catch = magnetic_hinge_catch(spec)
        if front_catch.lid_cut is not None:
            lid = lid - front_catch.lid_cut
        if front_catch.lid is not None:
            lid = lid | front_catch.lid

        return apply_stackable_lid(lid, spec)

