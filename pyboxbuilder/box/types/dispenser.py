# SPDX-License-Identifier: Apache-2.0
"""DispenserBox — gravity tile & token dispenser type (FR-084)."""

from __future__ import annotations

import math
from dataclasses import replace
from typing import TYPE_CHECKING

from pybosl2.shapes3d import cyl

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.shell import block, body_rounding, build_shell
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.dispenser import DispenserBoxBuilder
from pyboxbuilder.enums import BoxType
from pyboxbuilder.rounding import round_edges, vertical_edges

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


@register_box(BoxType.DISPENSER, builder=DispenserBoxBuilder)
class DispenserBox(BoxTypeBase):
    """Gravity tile & token dispenser tower with bottom dispensing slot (FR-084)."""

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
        """Return the dispenser body with angled slide, dispensing slot, and sight slot."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        body_h = spec.height - spec.lid_thickness

        body = build_shell(self._body_spec(spec))

        # 1. Angled slide ramp in the interior bottom
        inner_w = spec.width - 2 * wt
        inner_l = spec.length - 2 * wt
        ramp_rad = math.radians(spec.chute_angle)
        # Wedge or stepped ramp block under the back
        ramp_rise = min(inner_l * math.tan(ramp_rad), body_h - ft - 20.0)
        if ramp_rise > 0.5:
            # Wedge added to floor sloping towards Y=wt
            ramp = block(
                [inner_w, inner_l, ramp_rise],
                at=(wt, wt, ft),
            )
            # Trim top of ramp to slope downwards to Y=wt
            # Using cutting block rotated by chute_angle
            cutter_h = ramp_rise * 2
            cutter = block(
                [inner_w + 2.0, inner_l * 2, cutter_h],
                at=(wt - 1.0, wt, ft),
            ).rot([-spec.chute_angle, 0, 0]).translate([0, 0, ramp_rise])
            body = body | (ramp - cutter)

        # 2. Bottom dispensing slot on front wall (Y=0)
        slot_h = spec.token_thickness + spec.dispense_slot_clearance
        slot_w = inner_w
        dispense_slot = block(
            [slot_w, wt * 2, slot_h],
            at=(wt, -wt, ft),
        )
        body = body - dispense_slot

        # 3. Finger scoop at bottom center to pull tile forward
        scoop_r = 12.0
        scoop = cyl(height=wt * 3, radius=scoop_r).rot([90, 0, 0]).translate(
            [spec.width / 2.0, 0, ft + slot_h / 2.0]
        )
        body = body - scoop

        # 4. Vertical sight slot on front wall
        sight_w = spec.sight_slot_width
        sight_z_start = ft + slot_h + 4.0
        sight_z_end = max(sight_z_start + 5.0, body_h - 6.0)
        sight_h = sight_z_end - sight_z_start
        sight_slot = block(
            [sight_w, wt * 2, sight_h],
            at=((spec.width - sight_w) / 2.0, -wt, sight_z_start),
        )
        body = body - sight_slot

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
        """Return the top loading chute cover lid."""
        wt = spec.wall_thickness
        lt = spec.lid_thickness
        body_h = spec.height - lt

        lid = block([spec.width, spec.length, lt], at=(0, 0, body_h))

        # Downward plug flange into top chute opening
        plug_w = spec.width - 2 * wt - 2 * spec.size_spacing
        plug_l = spec.length - 2 * wt - 2 * spec.size_spacing
        plug_h = min(4.0, lt * 1.5)
        plug = block(
            [plug_w, plug_l, plug_h],
            at=(
                wt + spec.size_spacing,
                wt + spec.size_spacing,
                body_h - plug_h,
            ),
        )
        lid = lid | plug

        radius = body_rounding(spec)
        if radius > 0:
            lid = round_edges(
                lid,
                [spec.width, spec.length, lt],
                radius,
                list(vertical_edges()),
            )
        return lid
