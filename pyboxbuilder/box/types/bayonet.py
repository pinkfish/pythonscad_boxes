# SPDX-License-Identifier: Apache-2.0
"""BayonetBox — twist-lock bayonet container type (FR-082)."""

from __future__ import annotations

import math
from dataclasses import replace
from typing import TYPE_CHECKING

from pybosl2.shapes3d import cyl

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.shell import block, body_rounding, build_shell
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.bayonet import BayonetBoxBuilder
from pyboxbuilder.enums import BoxType
from pyboxbuilder.rounding import round_edges, vertical_edges

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


@register_box(BoxType.BAYONET, builder=BayonetBoxBuilder)
class BayonetBox(BoxTypeBase):
    """Twist-lock bayonet container with entry keyways and locking channels (FR-082)."""

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
        """Return the container body with bayonet entry keyways and channels."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        lt = spec.lid_thickness
        body_h = spec.height - lt
        d = min(spec.width, spec.length)
        r = d / 2.0
        x_c = spec.width / 2.0
        y_c = spec.length / 2.0

        if spec.round_footprint:
            # Cylindrical container body
            outer = cyl(height=body_h, radius=r).translate([x_c, y_c, body_h / 2.0])
            inner_r = max(1.0, r - wt)
            inner_h = body_h - ft + 1.0
            inner_cut = cyl(height=inner_h, radius=inner_r).translate(
                [x_c, y_c, ft + inner_h / 2.0]
            )
            body = outer - inner_cut

            # Stepped neck for lid skirt
            neck_h = max(6.0, spec.lug_height * 2.5)
            r_neck = r - wt * 0.4
            neck_recess = (
                cyl(height=neck_h + 1.0, radius=r + 1.0)
                - cyl(height=neck_h + 1.0, radius=r_neck)
            ).translate([x_c, y_c, body_h - neck_h / 2.0 + 0.5])
            body = body - neck_recess

            # Cut bayonet vertical entry keyways and horizontal retention channels
            lug_h = spec.lug_height
            keyway_w = max(4.0, lug_h * 2.0)

            cuts: list[Bosl2Solid] = []
            for i in range(spec.lug_count):
                angle = 360.0 / spec.lug_count * i
                rad = math.radians(angle)
                kx = x_c + (r_neck + 0.5) * math.cos(rad)
                ky = y_c + (r_neck + 0.5) * math.sin(rad)
                # Vertical entry keyway
                cuts.append(
                    block(
                        [keyway_w, keyway_w, neck_h + 1.0],
                        at=(kx - keyway_w / 2.0, ky - keyway_w / 2.0, body_h - neck_h),
                    )
                )
            for c in cuts:
                body = body - c

            return body

        # Rectangular footprint with rounded corners and bayonet neck
        body_spec = self._body_spec(spec)
        body = build_shell(body_spec)
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
        """Return the bayonet cap with internal engagement lugs."""
        wt = spec.wall_thickness
        lt = spec.lid_thickness
        body_h = spec.height - lt
        d = min(spec.width, spec.length)
        r = d / 2.0
        x_c = spec.width / 2.0
        y_c = spec.length / 2.0

        if spec.round_footprint:
            neck_h = max(6.0, spec.lug_height * 2.5)
            total_lid_h = neck_h + lt
            lid_outer = cyl(height=total_lid_h, radius=r).translate(
                [x_c, y_c, body_h - neck_h + total_lid_h / 2.0]
            )
            r_neck = r - wt * 0.4
            inner_r = r_neck + spec.bayonet_slack
            recess = cyl(height=neck_h + 0.5, radius=inner_r).translate(
                [x_c, y_c, body_h - neck_h + neck_h / 2.0]
            )
            lid = lid_outer - recess

            # Inward-projecting retention lugs
            lug_h = spec.lug_height
            lug_depth = spec.lug_depth
            lug_w = max(3.5, lug_h * 1.5)
            lug_z = body_h - neck_h + lug_h / 2.0

            lugs: list[Bosl2Solid] = []
            for i in range(spec.lug_count):
                angle = 360.0 / spec.lug_count * i
                rad = math.radians(angle)
                lx = x_c + (inner_r - lug_depth / 2.0) * math.cos(rad)
                ly = y_c + (inner_r - lug_depth / 2.0) * math.sin(rad)
                lugs.append(
                    block(
                        [lug_w, lug_w, lug_h],
                        at=(lx - lug_w / 2.0, ly - lug_w / 2.0, lug_z),
                    )
                )
            for lg in lugs:
                lid = lid | lg

            return lid & lid_outer

        # Rectangular fallback cap
        lid = block([spec.width, spec.length, lt], at=(0, 0, body_h))
        radius = body_rounding(spec)
        if radius > 0:
            lid = round_edges(
                lid,
                [spec.width, spec.length, lt],
                radius,
                list(vertical_edges()),
            )
        return lid
