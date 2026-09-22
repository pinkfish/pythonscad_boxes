# SPDX-License-Identifier: Apache-2.0
"""ModularInterlockBox — modular interlocking play tray type (FR-089)."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.shell import block, body_rounding, build_shell
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.modular_interlock import ModularInterlockBoxBuilder
from pyboxbuilder.enums import BoxType
from pyboxbuilder.rounding import round_edges, vertical_edges

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


@register_box(BoxType.MODULAR_INTERLOCK, builder=ModularInterlockBoxBuilder)
class ModularInterlockBox(BoxTypeBase):
    """Tabletop play tray with modular interlocking perimeter joints (FR-089)."""

    def interior(self, spec: BoxSpec) -> Interior:
        """Return the usable interior volume."""
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
        """Return the tray body with perimeter interlocking features."""
        body_spec = self._body_spec(spec)
        body = build_shell(body_spec)
        body_h = body_spec.height

        radius = body_rounding(spec)
        if radius > 0:
            body = round_edges(
                body,
                [spec.width, spec.length, body_h],
                radius,
                list(vertical_edges()),
            )
        from pyboxbuilder.box.features import apply_horizontal_interlock, apply_stackable_body

        body = apply_horizontal_interlock(body, body_spec)
        return apply_stackable_body(body, spec)

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Return the matching protective cover lid."""
        lt = spec.lid_thickness
        body_h = spec.height - lt

        lid = block([spec.width, spec.length, lt], at=(0, 0, body_h))
        radius = body_rounding(spec)
        if radius > 0:
            lid = round_edges(
                lid,
                [spec.width, spec.length, lt],
                radius,
                list(vertical_edges()),
            )
        from pyboxbuilder.box.features import apply_stackable_lid

        return apply_stackable_lid(lid, spec, top_z=spec.height)
