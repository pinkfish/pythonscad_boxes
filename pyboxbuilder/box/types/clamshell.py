# SPDX-License-Identifier: Apache-2.0
"""ClamshellBox — bifold / clamshell book box type (FR-088)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pybosl2.shapes3d import cyl

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.shell import block, body_rounding
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.clamshell import ClamshellBoxBuilder
from pyboxbuilder.enums import BoxType
from pyboxbuilder.rounding import round_edges, vertical_edges

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


@register_box(BoxType.CLAMSHELL, builder=ClamshellBoxBuilder)
class ClamshellBox(BoxTypeBase):
    """Bifold clamshell book box with active compartments in both halves (FR-088)."""

    def interior(self, spec: BoxSpec) -> Interior:
        """Return the usable interior volume of the base tray half."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        half_h = spec.height / 2.0
        return Interior(
            width=spec.width - 2 * wt,
            length=spec.length - 2 * wt,
            height=half_h - ft,
            origin_x=wt,
            origin_y=wt,
            origin_z=ft,
        )

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the base half with spine hinge knuckles, reliefs, and front catch."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        half_h = spec.height / 2.0

        # Tray half outer
        tray_outer = block([spec.width, spec.length, half_h], at=(0, 0, 0))

        # Interior cavity
        inner_w = spec.width - 2 * wt
        inner_l = spec.length - 2 * wt
        inner_h = half_h - ft + 1.0
        cavity = block([inner_w, inner_l, inner_h], at=(wt, wt, ft))
        body = tray_outer - cavity

        hr = spec.clamshell_hinge_radius
        knuckle_len = spec.length / 5.0

        # Relief cutouts for the lid's knuckles (i=1, 3)
        for i in (1, 3):
            y_start = i * knuckle_len
            body = body - block(
                [hr * 2.0 + 0.5, knuckle_len + 0.2, hr + 1.0],
                at=(-0.1, y_start - 0.1, half_h - hr),
            )

        # Spine hinge knuckles along X for the body (i=0, 2, 4)
        for i in (0, 2, 4):
            y_start = i * knuckle_len
            knuckle = cyl(height=knuckle_len - 0.4, radius=hr).rotate([90, 0, 0]).translate(
                [hr, y_start + knuckle_len / 2.0, half_h]
            )
            body = body | knuckle

        # Perimeter closure ridge catch on front rim (X=spec.width)
        if spec.closure_latch:
            ridge_w = 1.0
            ridge_h = 1.5
            catch_len = min(20.0, spec.length * 0.4)
            ridge = block(
                [ridge_w, catch_len, ridge_h],
                at=(
                    spec.width - wt,
                    (spec.length - catch_len) / 2.0,
                    half_h,
                ),
            )
            body = body | ridge

        radius = body_rounding(spec)
        if radius > 0:
            body = round_edges(
                body,
                [spec.width, spec.length, half_h],
                radius,
                list(vertical_edges()),
            )
        return body

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Return the upper tray half with interleaving spine knuckles and catch groove."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        half_h = spec.height / 2.0

        # Upper tray half (mirrored/stacked at z=half_h)
        tray_outer = block([spec.width, spec.length, half_h], at=(0, 0, half_h))

        inner_w = spec.width - 2 * wt
        inner_l = spec.length - 2 * wt
        inner_h = half_h - ft + 1.0
        cavity = block([inner_w, inner_l, inner_h], at=(wt, wt, half_h))
        lid = tray_outer - cavity

        hr = spec.clamshell_hinge_radius
        knuckle_len = spec.length / 5.0

        # Relief cutouts for the body's knuckles (i=0, 2, 4)
        for i in (0, 2, 4):
            y_start = i * knuckle_len
            lid = lid - block(
                [hr * 2.0 + 0.5, knuckle_len + 0.2, hr + 1.0],
                at=(-0.1, y_start - 0.1, half_h - 0.1),
            )

        # Interleaving knuckles along X for the lid (i=1, 3)
        for i in (1, 3):
            y_start = i * knuckle_len
            knuckle = cyl(height=knuckle_len - 0.4, radius=hr).rotate([90, 0, 0]).translate(
                [hr, y_start + knuckle_len / 2.0, half_h]
            )
            lid = lid | knuckle

        # Perimeter closure catch groove on front rim (X=spec.width)
        if spec.closure_latch:
            ridge_w = 1.0
            ridge_h = 1.5
            catch_len = min(20.0, spec.length * 0.4)
            groove = block(
                [ridge_w + 0.4, catch_len + 0.4, ridge_h + 0.4],
                at=(
                    spec.width - wt - 0.2,
                    (spec.length - catch_len - 0.4) / 2.0,
                    half_h - 0.1,
                ),
            )
            lid = lid - groove

        radius = body_rounding(spec)
        if radius > 0:
            lid = round_edges(
                lid,
                [spec.width, spec.length, half_h],
                radius,
                list(vertical_edges()),
            )
        return lid
