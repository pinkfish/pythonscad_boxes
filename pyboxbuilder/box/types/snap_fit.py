# SPDX-License-Identifier: Apache-2.0
"""SnapFitBox — cantilever snap-fit latch box type (FR-081)."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.shell import block, body_rounding, build_shell
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.rounding import round_edges, vertical_edges

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


class SnapFitBox(BoxTypeBase):
    """Cantilever latch box with positive detents and thumb releases (FR-081)."""

    def interior(self, spec: BoxSpec) -> Interior:
        """Return the usable volume inside the box."""
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
        """Return the box body with recessed latch pockets."""
        body_spec = self._body_spec(spec)
        body = build_shell(body_spec)

        body_h = body_spec.height
        c_w = spec.cantilever_width
        c_t = spec.cantilever_thickness
        d_h = spec.detent_height
        clr = spec.deflection_clearance
        arm_drop = min(body_h - spec.floor_thickness, 12.0)

        pocket_w = c_w + 2 * clr
        pocket_h = max(4.0, d_h * 2.5)
        pocket_z = max(body_h - 10.0, spec.floor_thickness + 2.0)

        # Latch arm and pocket cuts on opposing walls
        if spec.latch_axis.lower() == "y":
            # Opposing Y walls (Y=0 and Y=length)
            x_c = spec.width / 2.0
            # Channel for arm (Y=0)
            chan_neg = block(
                [pocket_w, c_t + clr + 0.1, arm_drop + 0.2],
                at=(x_c - pocket_w / 2.0, -0.05, body_h - arm_drop - 0.1),
            )
            # Pocket for detent (Y=0)
            pocket_neg = block(
                [pocket_w, c_t + d_h + clr + 0.1, pocket_h],
                at=(x_c - pocket_w / 2.0, -0.05, pocket_z - clr),
            )
            # Channel for arm (Y=length)
            chan_pos = block(
                [pocket_w, c_t + clr + 0.1, arm_drop + 0.2],
                at=(x_c - pocket_w / 2.0, spec.length - c_t - clr - 0.05, body_h - arm_drop - 0.1),
            )
            # Pocket for detent (Y=length)
            pocket_pos = block(
                [pocket_w, c_t + d_h + clr + 0.1, pocket_h],
                at=(x_c - pocket_w / 2.0, spec.length - c_t - d_h - clr - 0.05, pocket_z - clr),
            )
            body = body - chan_neg - pocket_neg - chan_pos - pocket_pos
        else:
            # Opposing X walls (X=0 and X=width)
            y_c = spec.length / 2.0
            # Channel for arm (X=0)
            chan_neg = block(
                [c_t + clr + 0.1, pocket_w, arm_drop + 0.2],
                at=(-0.05, y_c - pocket_w / 2.0, body_h - arm_drop - 0.1),
            )
            # Pocket for detent (X=0)
            pocket_neg = block(
                [c_t + d_h + clr + 0.1, pocket_w, pocket_h],
                at=(-0.05, y_c - pocket_w / 2.0, pocket_z - clr),
            )
            # Channel for arm (X=width)
            chan_pos = block(
                [c_t + clr + 0.1, pocket_w, arm_drop + 0.2],
                at=(spec.width - c_t - clr - 0.05, y_c - pocket_w / 2.0, body_h - arm_drop - 0.1),
            )
            # Pocket for detent (X=width)
            pocket_pos = block(
                [c_t + d_h + clr + 0.1, pocket_w, pocket_h],
                at=(spec.width - c_t - d_h - clr - 0.05, y_c - pocket_w / 2.0, pocket_z - clr),
            )
            body = body - chan_neg - pocket_neg - chan_pos - pocket_pos

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
        """Return the lid plate with cantilever spring arms and retention detents."""
        lt = spec.lid_thickness
        body_h = spec.height - lt
        lid = block([spec.width, spec.length, lt], at=(0, 0, body_h))

        c_w = spec.cantilever_width
        c_t = spec.cantilever_thickness
        d_h = spec.detent_height
        arm_drop = min(body_h - spec.floor_thickness, 12.0)
        pocket_z = max(body_h - 10.0, spec.floor_thickness + 2.0)

        if spec.latch_axis.lower() == "y":
            x_c = spec.width / 2.0
            # Arm along Y=0 (flush with outer wall)
            arm_neg = block(
                [c_w, c_t, arm_drop + lt],
                at=(x_c - c_w / 2.0, 0.0, body_h - arm_drop),
            )
            detent_neg = block(
                [c_w, d_h, d_h],
                at=(x_c - c_w / 2.0, c_t, pocket_z),
            )
            # Arm along Y=length (flush with outer wall)
            arm_pos = block(
                [c_w, c_t, arm_drop + lt],
                at=(x_c - c_w / 2.0, spec.length - c_t, body_h - arm_drop),
            )
            detent_pos = block(
                [c_w, d_h, d_h],
                at=(x_c - c_w / 2.0, spec.length - c_t - d_h, pocket_z),
            )
            lid = lid | arm_neg | detent_neg | arm_pos | detent_pos
        else:
            y_c = spec.length / 2.0
            # Arm along X=0 (flush with outer wall)
            arm_neg = block(
                [c_t, c_w, arm_drop + lt],
                at=(0.0, y_c - c_w / 2.0, body_h - arm_drop),
            )
            detent_neg = block(
                [d_h, c_w, d_h],
                at=(c_t, y_c - c_w / 2.0, pocket_z),
            )
            # Arm along X=width (flush with outer wall)
            arm_pos = block(
                [c_t, c_w, arm_drop + lt],
                at=(spec.width - c_t, y_c - c_w / 2.0, body_h - arm_drop),
            )
            detent_pos = block(
                [d_h, c_w, d_h],
                at=(spec.width - c_t - d_h, y_c - c_w / 2.0, pocket_z),
            )
            lid = lid | arm_neg | detent_neg | arm_pos | detent_pos

        radius = body_rounding(spec)
        if radius > 0:
            lid = round_edges(
                lid,
                [spec.width, spec.length, lt],
                radius,
                list(vertical_edges()),
            )
        return lid
