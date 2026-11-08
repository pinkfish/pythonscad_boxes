# SPDX-License-Identifier: Apache-2.0
"""SlidingHingeBox — hinged lid box with captive sliding or rotary spin catch."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.sliding_hinge import SlidingHingeBoxBuilder
from pyboxbuilder.enums import BoxType, CatchType

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


@register_box(BoxType.SLIDING_HINGE, builder=SlidingHingeBoxBuilder)
class SlidingHingeBox(BoxTypeBase):
    """Hinged lid box with a captive sliding or rotary print-in-place catch."""

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
        """Return the body spec stopping one lid thickness below ``spec.height``."""
        return replace(spec, height=spec.height - spec.lid_thickness)

    @staticmethod
    def _effective_spec(spec: BoxSpec) -> BoxSpec:
        """Default catch_type to SLIDE_ACROSS (or SLIDE_UP if slide_catch_style=='up')."""
        default_catch = (
            CatchType.SLIDE_UP
            if getattr(spec, "slide_catch_style", "front") == "up"
            else CatchType.SLIDE_ACROSS
        )
        if spec.catch_type is None and spec.hinge_catch_type is None:
            return replace(spec, catch_type=default_catch)
        return spec

    def interior_mask(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the usable interior volume clear of the rear hinge and front catch boss."""
        from pyboxbuilder.box.features import hinge_catch, hinge_intrusion
        from pyboxbuilder.box.shell import block

        eff_spec = self._effective_spec(spec)
        wt = eff_spec.wall_thickness
        ft = eff_spec.floor_thickness
        available = block(
            [eff_spec.width - 2 * wt, eff_spec.length - 2 * wt, eff_spec.height],
            at=(wt, wt, ft),
        )
        mask = available - hinge_intrusion(
            self._body_spec(eff_spec), eff_spec.filament_diameter
        )
        catch = hinge_catch(eff_spec)
        if catch.body is not None:
            mask = mask - catch.body
        return mask

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the box body with rear filament hinge knuckles and front/side catch."""
        from pyboxbuilder.box.features import (
            apply_stackable_body,
            filament_hinge,
            hinge_catch,
        )
        from pyboxbuilder.box.shell import body_rounding, build_shell
        from pyboxbuilder.rounding import round_edges, vertical_edges

        eff_spec = self._effective_spec(spec)
        body_spec = self._body_spec(eff_spec)
        closure = filament_hinge(
            body_spec,
            eff_spec.filament_diameter,
            eff_spec.hinge_count,
        )
        body = build_shell(body_spec)
        if closure.body_cut is not None:
            body = body - closure.body_cut
        body = body if closure.body is None else body | closure.body
        if closure.pin is not None:
            body = body - closure.pin

        radius = body_rounding(eff_spec)
        if radius > 0:
            body = round_edges(
                body,
                [eff_spec.width, eff_spec.length, eff_spec.height],
                radius,
                list(vertical_edges()),
            )

        catch = hinge_catch(eff_spec)
        if catch.body_cut is not None:
            body = body - catch.body_cut
        if catch.body is not None:
            body = body | catch.body

        return apply_stackable_body(body, eff_spec)

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Return the hinged lid carrying the interleaving knuckles and captive catch."""
        from pyboxbuilder.box.features import (
            apply_stackable_lid,
            filament_hinge,
            hinge_catch,
        )
        from pyboxbuilder.box.shell import block

        eff_spec = self._effective_spec(spec)
        lt = eff_spec.lid_thickness
        body_spec = self._body_spec(eff_spec)
        radius = max(eff_spec.wall_thickness, eff_spec.filament_diameter)
        axis_y = eff_spec.length - radius
        lid = block([eff_spec.width, axis_y, lt], at=(0.0, 0.0, body_spec.height))

        closure = filament_hinge(
            body_spec,
            eff_spec.filament_diameter,
            eff_spec.hinge_count,
        )
        if closure.lid_cut is not None:
            lid = lid - closure.lid_cut
        lid = lid if closure.lid is None else lid | closure.lid
        if closure.pin is not None:
            lid = lid - closure.pin

        catch = hinge_catch(eff_spec)
        if catch.lid_cut is not None:
            lid = lid - catch.lid_cut
        if catch.lid is not None:
            lid = lid | catch.lid

        return apply_stackable_lid(lid, eff_spec)

