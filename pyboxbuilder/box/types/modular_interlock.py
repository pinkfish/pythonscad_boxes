# SPDX-License-Identifier: Apache-2.0
"""ModularInterlockBox — modular interlocking play tray type (FR-089)."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.shell import block, body_rounding, build_shell
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.enums import InterlockType
from pyboxbuilder.rounding import round_edges, vertical_edges

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


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

        if spec.interlock_type == InterlockType.DOVETAIL:
            # Add male dovetails on +X and +Y walls; cut female sockets on -X and -Y walls
            dt_w_tip = 8.5
            dt_depth = 3.0
            dt_h = body_h * 0.7
            dt_z = (body_h - dt_h) / 2.0
            clr = spec.dovetail_clearance

            # Male keys
            male_x = block(
                [dt_depth, dt_w_tip, dt_h],
                at=(spec.width, (spec.length - dt_w_tip) / 2.0, dt_z),
            )
            male_y = block(
                [dt_w_tip, dt_depth, dt_h],
                at=((spec.width - dt_w_tip) / 2.0, spec.length, dt_z),
            )
            body = body | male_x | male_y

            # Female sockets (with clearance)
            socket_depth = dt_depth + clr
            socket_w = dt_w_tip + 2 * clr
            socket_h = dt_h + 2 * clr
            fem_x = block(
                [socket_depth * 2, socket_w, socket_h],
                at=(-socket_depth, (spec.length - socket_w) / 2.0, dt_z - clr),
            )
            fem_y = block(
                [socket_w, socket_depth * 2, socket_h],
                at=((spec.width - socket_w) / 2.0, -socket_depth, dt_z - clr),
            )
            body = body - fem_x - fem_y

        elif spec.interlock_type == InterlockType.GRIDFINITY:
            # Gridfinity-compatible tiered base bevel
            base_bevel_h = min(2.5, spec.floor_thickness)
            base_cut = block(
                [spec.width + 2, spec.length + 2, base_bevel_h],
                at=(-1, -1, -0.5),
            ) - block(
                [spec.width - 2.0, spec.length - 2.0, base_bevel_h + 1],
                at=(1.0, 1.0, -1.0),
            )
            body = body - base_cut

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
        return lid
