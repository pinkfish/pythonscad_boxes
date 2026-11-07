# SPDX-License-Identifier: Apache-2.0
"""DiceTrayBox — dice tray & rolling arena box type (FR-086)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyboxbuilder.box.features import slipover_gap, slipover_metrics
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.shell import block
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.box.types.slipover import SLIPOVER_FINGER_MAX_MM, SlipoverBox
from pyboxbuilder.builders.dice_tray import DiceTrayBoxBuilder
from pyboxbuilder.compartments.element import union_all
from pyboxbuilder.enums import BoxType

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


def _corner_triangles(
    x0: float,
    y0: float,
    x1: float,
    y1: float,
    d: float,
    z0: float,
    h: float,
    pad: float = 0.0,
) -> Bosl2Solid:
    """Return 45° triangular prisms at the four corners of ``[x0..x1, y0..y1]``."""
    from pybosl2 import Path2D
    from pybosl2.shapes2d import polygon

    tris = [
        [(x0 - pad, y0 - pad), (x0 + d, y0 - pad), (x0 - pad, y0 + d)],
        [(x1 + pad, y0 - pad), (x1 + pad, y0 + d), (x1 - d, y0 - pad)],
        [(x0 - pad, y1 + pad), (x0 - pad, y1 - d), (x0 + d, y1 + pad)],
        [(x1 + pad, y1 + pad), (x1 - d, y1 + pad), (x1 + pad, y1 - d)],
    ]
    return union_all([
        polygon(path=Path2D(pts)).linear_extrude(height=h).translate([0.0, 0.0, z0])
        for pts in tris
    ])


@register_box(BoxType.DICE_TRAY, builder=DiceTrayBoxBuilder)
class DiceTrayBox(SlipoverBox):
    """Dual-purpose slipover storage box and tabletop dice rolling arena (FR-086)."""

    def _deflector_metrics(self, spec: BoxSpec) -> tuple[float, float, float, float, float]:
        """Return ``(inset, body_height, z_deflect_bot, d_lid, d_body)`` for corner deflectors."""
        lt = spec.lid_thickness
        foot = spec.foot
        slack = spec.slip_slack
        inset, body_height = slipover_metrics(spec)
        gap = min(slipover_gap(spec), spec.height - foot - lt)
        skirt = spec.height - foot - gap
        base_z = foot + gap

        requested = spec.slipover_finger_height
        notch_h = (
            min(SLIPOVER_FINGER_MAX_MM, skirt / 3.0)
            if requested is None
            else float(requested)
        )
        notch_h = max(0.0, min(notch_h, skirt))

        # Keep lower rim clear for slipover corner finger notches and side catches
        z_deflect_bot = min(body_height - 1.0, base_z + max(notch_h + 1.0, skirt * 0.3))
        inner_w = spec.width - 2 * inset
        inner_l = spec.length - 2 * inset
        d_lid = min(10.0, min(inner_w, inner_l) * 0.14)
        d_body = d_lid + slack + 0.15
        return inset, body_height, z_deflect_bot, d_lid, d_body

    def interior_mask(self, spec: BoxSpec) -> Bosl2Solid:
        """Keep compartments clear of the inset slipover body walls and 45° corner deflectors."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        inset, body_height, _z_def, _d_lid, d_body = self._deflector_metrics(spec)
        mask = block(
            [
                spec.width - 2 * (inset + wt),
                spec.length - 2 * (inset + wt),
                body_height - ft + 1.0,
            ],
            at=(inset + wt, inset + wt, ft),
        )
        if spec.corner_deflectors and body_height > ft + 2.0:
            corner_keepout = _corner_triangles(
                inset,
                inset,
                spec.width - inset,
                spec.length - inset,
                d_body + wt * 1.5,
                ft,
                body_height - ft + 1.0,
            )
            mask = mask - corner_keepout
        return mask

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the slipover tray body with matching upper corner bevels for the arena deflectors."""
        body = super().build_body(spec)
        if not spec.corner_deflectors:
            return body

        wt = spec.wall_thickness
        ft = spec.floor_thickness
        slack = spec.slip_slack
        inset, body_height, z_deflect_bot, _d_lid, d_body = self._deflector_metrics(spec)
        z_cut_bot = max(spec.foot + 0.2, z_deflect_bot - slack)
        cut_h = body_height - z_cut_bot
        if cut_h <= 0.5:
            return body

        # Reinforce inner corners behind the 45° bevel before cutting outer corners
        z_wall_bot = max(ft, z_cut_bot - wt)
        inner_fill = _corner_triangles(
            inset,
            inset,
            spec.width - inset,
            spec.length - inset,
            d_body + wt * 1.4,
            z_wall_bot,
            body_height - z_wall_bot,
        ) & block(
            [spec.width - 2 * inset, spec.length - 2 * inset, body_height - z_wall_bot],
            at=(inset, inset, z_wall_bot),
        )
        if spec.hollow:
            inner_cavity = block(
                [
                    spec.width - 2 * (inset + wt),
                    spec.length - 2 * (inset + wt),
                    body_height - ft + 0.2,
                ],
                at=(inset + wt, inset + wt, ft),
            ) - _corner_triangles(
                inset,
                inset,
                spec.width - inset,
                spec.length - inset,
                d_body + wt * 1.4,
                z_wall_bot,
                body_height - z_wall_bot + 0.2,
            )
            body = (body | inner_fill) - inner_cavity
        else:
            body = body | inner_fill

        outer_bevel = _corner_triangles(
            inset,
            inset,
            spec.width - inset,
            spec.length - inset,
            d_body,
            z_cut_bot,
            cut_h + 0.2,
            pad=0.1,
        )
        return body - outer_bevel

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Return the slipover sleeve lid with side catches/notches, felt recess, and 45° corner deflectors."""
        sleeve = super().build_lid(spec, decoration)

        lt = spec.lid_thickness
        slack = spec.slip_slack
        inset, _body_height, z_deflect_bot, d_lid, _d_body = self._deflector_metrics(spec)

        # Recessed felt pad pocket on the arena floor (inner roof of the slipover sleeve)
        pocket_d = min(spec.felt_pocket_depth, max(0.0, lt * 0.4))
        if pocket_d > 0.05:
            margin = 1.5
            x0_f = inset - slack + margin
            y0_f = inset - slack + margin
            felt_w = spec.width - 2 * x0_f
            felt_l = spec.length - 2 * y0_f
            if felt_w > 4.0 and felt_l > 4.0:
                felt_pocket = block(
                    [felt_w, felt_l, pocket_d + 0.05],
                    at=(x0_f, y0_f, spec.height - lt - 0.05),
                )
                sleeve = sleeve - felt_pocket

        # 45° triangular corner deflector fillets inside the arena floor corners
        def_h = (spec.height - lt) - z_deflect_bot
        if spec.corner_deflectors and def_h > 0.5:
            x0_c = inset - slack
            y0_c = inset - slack
            x1_c = spec.width - inset + slack
            y1_c = spec.length - inset + slack
            deflectors = _corner_triangles(
                x0_c, y0_c, x1_c, y1_c, d_lid, z_deflect_bot, def_h
            ) & block(
                [x1_c - x0_c, y1_c - y0_c, def_h],
                at=(x0_c, y0_c, z_deflect_bot),
            )
            sleeve = sleeve | deflectors
            notches = self._finger_notches(spec)
            if notches is not None:
                sleeve = sleeve - notches

        return sleeve
