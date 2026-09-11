# SPDX-License-Identifier: Apache-2.0
"""CardShoeBox — angled draw & discard card shoe type (FR-085)."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from pybosl2.shapes3d import cyl

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.shell import block, body_rounding, build_shell
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.card_shoe import CardShoeBoxBuilder
from pyboxbuilder.enums import BoxType
from pyboxbuilder.rounding import round_edges, vertical_edges

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


@register_box(BoxType.CARD_SHOE, builder=CardShoeBoxBuilder)
class CardShoeBox(BoxTypeBase):
    """Tabletop utility tray with angled draw well and flat discard well (FR-085)."""

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
        """Return the card shoe body with slanted draw well and finger scoops."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        body_h = spec.height - spec.lid_thickness

        body = build_shell(self._body_spec(spec))

        if spec.discard_well:
            # Divider separating draw and discard wells (clearing the lid plug)
            plug_h = min(4.0, spec.lid_thickness * 1.5)
            divider_x = spec.width * 0.55
            divider_h = max(0.0, body_h - ft - plug_h - 0.2)
            divider = block(
                [wt, spec.length - 2 * wt, divider_h],
                at=(divider_x - wt / 2.0, wt, ft),
            )
            body = body | divider

            # Lower the front wall of the draw well to the retaining lip height
            draw_w = divider_x - wt * 1.5
            lip_h = spec.retaining_lip_height
            front_cut_h = max(0.0, body_h - (ft + lip_h))
            if front_cut_h > 0:
                front_cut = block(
                    [draw_w + wt, wt * 2, front_cut_h],
                    at=(0, -wt, ft + lip_h),
                )
                body = body - front_cut

            # Discard well finger scoops (front and back walls)
            discard_w = spec.width - divider_x - wt * 1.5
            discard_center_x = divider_x + wt * 0.5 + discard_w / 2.0
            scoop_r = 14.0
            front_scoop = cyl(height=wt * 3, radius=scoop_r).rotate([90, 0, 0]).translate(
                [discard_center_x, 0, body_h]
            )
            back_scoop = cyl(height=wt * 3, radius=scoop_r).rotate([90, 0, 0]).translate(
                [discard_center_x, spec.length, body_h]
            )
            body = body - front_scoop - back_scoop
        else:
            # Single draw well: lower the entire front wall to the retaining lip height
            lip_h = spec.retaining_lip_height
            front_cut_h = max(0.0, body_h - (ft + lip_h))
            if front_cut_h > 0:
                front_cut = block(
                    [spec.width, wt * 2, front_cut_h],
                    at=(0, -wt, ft + lip_h),
                )
                body = body - front_cut

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
        """Return the protective cover lid."""
        wt = spec.wall_thickness
        lt = spec.lid_thickness
        body_h = spec.height - lt

        lid = block([spec.width, spec.length, lt], at=(0, 0, body_h))

        # Downward plug flange fitting inside the top rim
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
