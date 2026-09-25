# SPDX-License-Identifier: Apache-2.0
"""SleeveDrawerBox — matchbox / sleeve & drawer box type (FR-087)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pybosl2.shapes3d import cuboid, cyl

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.shell import block, body_rounding
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.sleeve_drawer import SleeveDrawerBoxBuilder
from pyboxbuilder.enums import BoxType
from pyboxbuilder.precision import precision
from pyboxbuilder.rounding import round_edges, vertical_edges

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


@register_box(BoxType.SLEEVE_DRAWER, builder=SleeveDrawerBoxBuilder)
class SleeveDrawerBox(BoxTypeBase):
    """Two-piece matchbox assembly with outer sleeve and sliding drawer (FR-087)."""

    def _sleeve_wall(self, spec: BoxSpec) -> float:
        """Return the sleeve wall thickness, defaulting to half the standard wall thickness."""
        if spec.sleeve_wall_thickness is not None:
            return max(0.8, spec.sleeve_wall_thickness)
        return max(1.2, spec.wall_thickness / 2.0)

    def interior(self, spec: BoxSpec) -> Interior:
        """Return the usable interior volume of the inner drawer."""
        sw = self._sleeve_wall(spec)
        slack = spec.sleeve_slack
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        drawer_w = spec.width - 2 * (sw + slack)
        drawer_l = spec.length - sw - slack
        drawer_h = spec.height - 2 * (sw + slack)
        return Interior(
            width=max(1.0, drawer_w - 2 * wt),
            length=max(1.0, drawer_l - 2 * wt),
            height=max(1.0, drawer_h - ft),
            origin_x=sw + slack + wt,
            origin_y=wt,
            origin_z=sw + slack + ft,
        )

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the inner sliding drawer with solid walls and front pull handle."""
        sw = self._sleeve_wall(spec)
        slack = spec.sleeve_slack
        wt = spec.wall_thickness
        ft = spec.floor_thickness

        drawer_w = spec.width - 2 * (sw + slack)
        drawer_l = max(10.0, spec.length - sw - slack)
        drawer_h = spec.height - 2 * (sw + slack)

        origin_x = sw + slack
        origin_y = 0.0
        origin_z = sw + slack

        # Outer drawer solid
        drawer_outer = block(
            [drawer_w, drawer_l, drawer_h],
            at=(origin_x, origin_y, origin_z),
        )

        # Cavity
        inner_w = max(1.0, drawer_w - 2 * wt)
        inner_l = max(1.0, drawer_l - 2 * wt)
        inner_h = max(1.0, drawer_h - ft + 1.0)
        cavity = block(
            [inner_w, inner_l, inner_h],
            at=(origin_x + wt, origin_y + wt, origin_z + ft),
        )
        drawer = drawer_outer - cavity

        # Rounding on drawer vertical corners
        radius = body_rounding(spec)
        if radius > 0:
            drawer = round_edges(
                drawer,
                [drawer_w, drawer_l, drawer_h],
                min(radius, sw),
                list(vertical_edges()),
                at=(origin_x, origin_y, origin_z),
            )

        # Front pull handle / lip
        handle_len = (
            spec.drawer_handle_length
            if spec.drawer_handle_length is not None
            else spec.drawer_pull_lip
        )
        style = (spec.drawer_handle_style or "handle").lower()
        if handle_len > 0 and style != "none":
            if style == "lip":
                lip_w = drawer_w * 0.7
                lip_h = max(3.0, drawer_h * 0.3)
                lip = cuboid(
                    [lip_w, handle_len, lip_h],
                    rounding=min(1.5, handle_len / 2.0),
                    edges=vertical_edges(),
                    **precision().kwargs(),
                ).translate([
                    spec.width / 2.0,
                    origin_y - handle_len / 2.0,
                    origin_z + drawer_h - lip_h / 2.0,
                ])
                drawer = drawer | lip
            else:
                # Default "handle": centered ergonomic pull knob/handle
                hw = min(22.0, drawer_w * 0.5)
                hh = min(8.0, drawer_h * 0.4)
                handle = cuboid(
                    [hw, handle_len, hh],
                    rounding=min(1.5, handle_len / 2.0),
                    edges=vertical_edges(),
                    **precision().kwargs(),
                ).translate([
                    spec.width / 2.0,
                    origin_y - handle_len / 2.0,
                    origin_z + drawer_h / 2.0,
                ])
                drawer = drawer | handle

        return drawer

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Return the 4-sided outer sleeve with solid back wall (or optional rear push hole)."""
        sw = self._sleeve_wall(spec)

        # Outer sleeve solid
        sleeve_outer = block([spec.width, spec.length, spec.height], at=(0, 0, 0))

        # Horizontal tunnel open at front (Y=0) and stopping at back wall (Y=spec.length - sw)
        tunnel_w = spec.width - 2 * sw
        tunnel_l = spec.length - sw + 1.0
        tunnel_h = spec.height - 2 * sw
        tunnel = block(
            [tunnel_w, tunnel_l, tunnel_h],
            at=(sw, -0.5, sw),
        )
        sleeve = sleeve_outer - tunnel

        # Push-through hole on back wall (Y = spec.length) only if explicitly enabled
        if spec.push_hole_radius > 0:
            push_r = min(spec.push_hole_radius, tunnel_h / 2.0 - 1.0)
            if push_r > 0:
                push_hole = cyl(height=sw * 3, radius=push_r).rotate([90, 0, 0]).translate(
                    [spec.width / 2.0, spec.length, spec.height / 2.0]
                )
                sleeve = sleeve - push_hole

        radius = body_rounding(spec)
        if radius > 0:
            sleeve = round_edges(
                sleeve,
                [spec.width, spec.length, spec.height],
                radius,
                list(vertical_edges()),
                at=(0, 0, 0),
            )
        from pyboxbuilder.box.features import apply_stackable_body, apply_stackable_lid

        sleeve = apply_stackable_body(sleeve, spec)
        return apply_stackable_lid(sleeve, spec, top_z=spec.height)
