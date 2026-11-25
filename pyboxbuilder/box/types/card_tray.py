# SPDX-License-Identifier: Apache-2.0
"""CardTrayBox — vertical & angled card tray with slotted divider rails."""

from __future__ import annotations

import math
from dataclasses import replace
from typing import TYPE_CHECKING

from pybosl2.shapes3d import cyl, wedge

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.shell import block, build_shell
from pyboxbuilder.box.spec import BoxSpec, UnresolvedBoxSpec
from pyboxbuilder.builders.card_tray import CardTrayBoxBuilder
from pyboxbuilder.enums import BoxType
from pyboxbuilder.precision import kwargs as precision_kwargs

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


@register_box(BoxType.CARD_TRAY, builder=CardTrayBoxBuilder)
class CardTrayBox(BoxTypeBase):
    """Open-top card tray for upright or tilted cards with removable divider slots."""

    def interior(self, spec: BoxSpec) -> Interior:
        """Return the usable interior volume of the card tray."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        return Interior(
            width=spec.width - 2.0 * wt,
            length=spec.length - 2.0 * wt,
            height=spec.height - ft,
            origin_x=wt,
            origin_y=wt,
            origin_z=ft,
        )

    def outer_size_for_interior(
        self,
        spec: BoxSpec | UnresolvedBoxSpec,
        inner_w: float,
        inner_l: float,
        inner_h: float,
    ) -> tuple[float, float, float]:
        """Return outer ``(W, L, H)`` for a lidless card tray."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        return (inner_w + 2.0 * wt + 0.5, inner_l + 2.0 * wt + 0.5, inner_h + ft + 0.5)

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Build the vertical/angled card tray body with rear tilt wedge, divider slots, and scoops."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        w = spec.width
        l_dim = spec.length
        h = spec.height
        inner_w = max(1.0, w - 2.0 * wt)
        inner_l = max(1.0, l_dim - 2.0 * wt)
        inner_h = max(1.0, h - ft)

        shell_spec = replace(spec, rim_free=True, auto_finger_holes=False)
        body = build_shell(shell_spec)

        tilt = max(0.0, min(45.0, float(spec.card_tilt_angle)))

        # Rear backrest wedge when cards tilt backward so the last card rests flush
        if tilt > 0.0:
            wedge_run = min(inner_h * math.tan(math.radians(tilt)), inner_l * 0.45)
            if wedge_run > 0.5:
                wedge_3d = (
                    wedge([inner_w, wedge_run, inner_h], center=True)
                    .rotate([0, 0, 180])
                    .translate([w / 2.0, l_dim - wt - wedge_run / 2.0, ft + inner_h / 2.0])
                )
                body = body | wedge_3d

        # Opposing inner-wall divider slots along the Y axis
        slot_ys: list[float] = []
        if spec.divider_positions:
            slot_ys = [wt + float(y) for y in spec.divider_positions if 0.5 < float(y) < inner_l - 0.5]
        elif spec.divider_slots > 0:
            n = int(spec.divider_slots)
            slot_ys = [wt + inner_l * (i + 1) / (n + 1) for i in range(n)]

        if slot_ys:
            slot_w = max(0.6, float(spec.divider_slot_width))
            slot_d = min(max(0.4, float(spec.divider_slot_depth)), max(0.4, wt * 0.6))
            slot_h = inner_h + 2.0
            for sy in slot_ys:
                left_slot = block([slot_d + 0.2, slot_w, slot_h], at=(0.0, -slot_w / 2.0, 0.0))
                right_slot = block([slot_d + 0.2, slot_w, slot_h], at=(0.0, -slot_w / 2.0, 0.0))
                if tilt > 0.0:
                    left_slot = left_slot.rotate([-tilt, 0, 0])
                    right_slot = right_slot.rotate([-tilt, 0, 0])
                left_slot = left_slot.translate([wt - slot_d, sy, ft])
                right_slot = right_slot.translate([w - wt - 0.2, sy, ft])
                body = body - left_slot - right_slot

        # Optional front and back U-shaped finger scoops for easy card browsing
        if spec.front_cutout:
            scoop_r = min(14.0, inner_w * 0.28, inner_h * 0.45)
            if scoop_r >= 3.0:
                front_scoop = (
                    cyl(height=wt * 3.0, radius=scoop_r, **precision_kwargs())
                    .rotate([90, 0, 0])
                    .translate([w / 2.0, 0.0, h])
                )
                back_scoop = (
                    cyl(height=wt * 3.0, radius=scoop_r, **precision_kwargs())
                    .rotate([90, 0, 0])
                    .translate([w / 2.0, l_dim, h])
                )
                body = body - front_scoop - back_scoop

        self._reject_stackable(spec)
        from pyboxbuilder.box.features import apply_stackable_body

        return apply_stackable_body(body, spec)

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Card trays are lidless open-top trays."""
        return None
