# SPDX-License-Identifier: Apache-2.0
"""DispenserBox — gravity tile & token dispenser type (FR-084)."""

from __future__ import annotations

import math
from dataclasses import replace
from typing import TYPE_CHECKING

from pybosl2.shapes3d import cyl, wedge

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.shell import block, body_rounding, build_shell
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.dispenser import DispenserBoxBuilder
from pyboxbuilder.enums import BoxType, DispenserExtractionMode
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
        """Return the dispenser body with angled slide and extraction mechanism."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        body_h = spec.height - spec.lid_thickness

        body = build_shell(self._body_spec(spec))

        # 1. Angled slide ramp in the interior bottom sloping downwards toward the front (Y=wt)
        inner_w = spec.width - 2 * wt
        inner_l = spec.length - 2 * wt
        ramp_rad = math.radians(spec.chute_angle)
        ramp_rise = min(inner_l * math.tan(ramp_rad), body_h - ft - 25.0)
        if ramp_rise > 0.5:
            # wedge([x, y, z]) top edge at y=0, slopes down to z=0 at y=inner_l.
            # Rotate 180 deg around Z puts top edge at back (y=inner_l) and slopes down to front (y=0).
            ramp = (
                wedge([inner_w, inner_l, ramp_rise])
                .rotate([0, 0, 180])
                .translate([inner_w, inner_l, 0])
                .translate([wt, wt, ft])
            )
            body = body | ramp

        # 2. Bottom dispensing slot on front wall (Y=0)
        slot_h = spec.token_thickness + spec.dispense_slot_clearance
        slot_w = inner_w
        dispense_slot = block(
            [slot_w, wt * 2, slot_h],
            at=(wt, -wt, ft),
        )
        body = body - dispense_slot

        mode = spec.dispenser_mode

        if mode == DispenserExtractionMode.ARCH:
            # Tall open archway on front wall leaving upper lintel/band
            arch_h = spec.arch_height if spec.arch_height is not None else (body_h * 0.65)
            arch_cut = block([slot_w, wt * 2, arch_h], at=(wt, -wt, ft))
            body = body - arch_cut
        else:
            # SCOOP, TRAY, and REAR_PUSH all feature the front pinch scoop & floor cutout
            scoop_r = spec.scoop_radius
            scoop = cyl(height=wt * 3, radius=scoop_r).rotate([90, 0, 0]).translate(
                [spec.width / 2.0, 0, ft + slot_h / 2.0]
            )
            body = body - scoop

            floor_w = min(spec.floor_scoop_width, inner_w - 4.0)
            floor_d = spec.floor_scoop_depth
            floor_cut = block(
                [floor_w, floor_d + wt, ft * 3],
                at=((spec.width - floor_w) / 2.0, -wt, -ft),
            )
            body = body - floor_cut

            # Upper vertical sight slot with solid retaining bridge in between
            sight_w = spec.sight_slot_width
            if sight_w > 0:
                lower_cover_h = body_h * 0.5
                min_sight_start = ft + slot_h / 2.0 + scoop_r + 6.0
                sight_z_start = (
                    spec.sight_slot_start
                    if spec.sight_slot_start is not None
                    else max(lower_cover_h, min_sight_start)
                )
                sight_z_end = max(sight_z_start + 5.0, body_h - 6.0)
                sight_h = sight_z_end - sight_z_start
                if sight_h >= 5.0:
                    sight_slot = block(
                        [sight_w, wt * 2, sight_h],
                        at=((spec.width - sight_w) / 2.0, -wt, sight_z_start),
                    )
                    body = body - sight_slot

            if mode == DispenserExtractionMode.TRAY:
                # Protruding landing tray shelf in front of the tower
                tray_d = spec.tray_depth
                tray_floor = block([spec.width, tray_d, ft], at=(0, -tray_d, 0))
                rail_l = block([wt, tray_d, ft + slot_h], at=(0, -tray_d, 0))
                rail_r = block([wt, tray_d, ft + slot_h], at=(spec.width - wt, -tray_d, 0))
                lip = block([spec.width, wt, ft + 1.5], at=(0, -tray_d, 0))
                body = body | tray_floor | rail_l | rail_r | lip

            elif mode == DispenserExtractionMode.REAR_PUSH:
                # Finger push cutout in back wall at floor level
                push_w = min(spec.rear_push_width, inner_w - 4.0)
                push_h = slot_h + 8.0
                rear_slot = block(
                    [push_w, wt * 2, push_h],
                    at=((spec.width - push_w) / 2.0, spec.length - wt, ft),
                )
                body = body - rear_slot

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
