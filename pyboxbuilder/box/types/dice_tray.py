# SPDX-License-Identifier: Apache-2.0
"""DiceTrayBox — dice tray & rolling arena box type (FR-086)."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.shell import block, body_rounding, build_shell
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.rounding import round_edges, vertical_edges

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


class DiceTrayBox(BoxTypeBase):
    """Dual-purpose storage box and active tabletop dice rolling arena (FR-086)."""

    def interior(self, spec: BoxSpec) -> Interior:
        """Return the usable interior volume of the storage body."""
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
        """Return the storage box body, stepped in at the top to receive the arena skirt."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        lt = spec.lid_thickness
        arena_h = min(spec.height - ft - 2.0, max(15.0, spec.arena_wall_height))
        band_z = spec.height - arena_h
        body_h = spec.height - lt

        body = build_shell(replace(spec, height=body_h, interior_top=body_h))
        # Step in the upper band above band_z so the arena lid skirt fits over it
        slack = 0.3
        inset = wt + slack
        keep = block([spec.width, spec.length, band_z]) | block(
            [spec.width - 2 * inset, spec.length - 2 * inset, body_h - band_z + 0.1],
            at=(inset, inset, band_z),
        )
        body = body & keep

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
        """Return the deep rolling arena lid with deflector corners and felt pocket."""
        wt = spec.wall_thickness
        lt = spec.lid_thickness
        ft = spec.floor_thickness
        arena_h = min(spec.height - ft - 2.0, max(15.0, spec.arena_wall_height))
        band_z = spec.height - arena_h

        # Arena outer footprint matches box footprint, placed from band_z to spec.height
        arena_outer = block([spec.width, spec.length, arena_h], at=(0, 0, band_z))

        # Arena interior well from band_z to spec.height - lt
        inner_w = spec.width - 2 * wt
        inner_l = spec.length - 2 * wt
        arena_inner = block(
            [inner_w, inner_l, arena_h - lt + 0.1],
            at=(wt, wt, band_z - 0.05),
        )

        lid = arena_outer - arena_inner

        # Recessed felt pad pocket in the arena floor
        pocket_d = spec.felt_pocket_depth
        if pocket_d > 0:
            margin = 1.0
            felt_w = inner_w - 2 * margin
            felt_l = inner_l - 2 * margin
            felt_pocket = block(
                [felt_w, felt_l, pocket_d + 0.1],
                at=(wt + margin, wt + margin, spec.height - lt - pocket_d + 0.05),
            )
            lid = lid - felt_pocket

        # 45° corner deflector fillets in interior corners
        if spec.corner_deflectors:
            fillet_size = min(12.0, min(inner_w, inner_l) * 0.15)
            fillet_h = arena_h - lt
            sw = block(
                [fillet_size, fillet_size, fillet_h],
                at=(wt, wt, band_z),
            )
            se = block(
                [fillet_size, fillet_size, fillet_h],
                at=(spec.width - wt - fillet_size, wt, band_z),
            )
            nw = block(
                [fillet_size, fillet_size, fillet_h],
                at=(wt, spec.length - wt - fillet_size, band_z),
            )
            ne = block(
                [fillet_size, fillet_size, fillet_h],
                at=(
                    spec.width - wt - fillet_size,
                    spec.length - wt - fillet_size,
                    band_z,
                ),
            )
            lid = lid | sw | se | nw | ne

        radius = body_rounding(spec)
        if radius > 0:
            lid = round_edges(
                lid,
                [spec.width, spec.length, arena_h],
                radius,
                list(vertical_edges()),
            )

        return lid
