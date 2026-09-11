# SPDX-License-Identifier: Apache-2.0
"""SleeveDrawerBox — matchbox / sleeve & drawer box type (FR-087)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pybosl2.shapes3d import cyl

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.shell import block, body_rounding
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.sleeve_drawer import SleeveDrawerBoxBuilder
from pyboxbuilder.enums import BoxType
from pyboxbuilder.rounding import round_edges, vertical_edges

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


@register_box(BoxType.SLEEVE_DRAWER, builder=SleeveDrawerBoxBuilder)
class SleeveDrawerBox(BoxTypeBase):
    """Two-piece matchbox assembly with outer sleeve and sliding drawer (FR-087)."""

    def interior(self, spec: BoxSpec) -> Interior:
        """Return the usable interior volume of the inner drawer."""
        sw = spec.wall_thickness / 2.0
        slack = spec.sleeve_slack
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        drawer_w = spec.width - 2 * (sw + slack)
        drawer_l = spec.length - sw - slack
        drawer_h = spec.height - 2 * (sw + slack)
        return Interior(
            width=drawer_w - 2 * wt,
            length=drawer_l - 2 * wt,
            height=drawer_h - ft,
            origin_x=sw + slack + wt,
            origin_y=wt,
            origin_z=sw + slack + ft,
        )

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the inner sliding drawer with front pull tab/lip."""
        sw = spec.wall_thickness / 2.0
        slack = spec.sleeve_slack
        wt = spec.wall_thickness
        ft = spec.floor_thickness

        lip_len = spec.drawer_pull_lip
        drawer_w = spec.width - 2 * (sw + slack)
        drawer_l = max(10.0, spec.length - sw - slack - lip_len)
        drawer_h = spec.height - 2 * (sw + slack)

        origin_x = sw + slack
        origin_y = lip_len
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

        # Front pull lip/tab extending forward
        lip_len = spec.drawer_pull_lip
        if lip_len > 0:
            lip_h = max(3.0, drawer_h * 0.4)
            lip = block(
                [drawer_w * 0.6, lip_len, lip_h],
                at=(
                    origin_x + drawer_w * 0.2,
                    origin_y - lip_len,
                    origin_z + drawer_h - lip_h,
                ),
            )
            drawer = drawer | lip

        radius = body_rounding(spec)
        if radius > 0:
            drawer = round_edges(
                drawer,
                [drawer_w, drawer_l, drawer_h],
                radius,
                list(vertical_edges()),
            )
        return drawer

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Return the 4-sided outer sleeve with rear push-through hole."""
        sw = spec.wall_thickness / 2.0

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

        # Push-through hole on back wall (Y = spec.length)
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
            )
        return sleeve
