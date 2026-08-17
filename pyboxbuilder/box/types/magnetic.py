# SPDX-License-Identifier: Apache-2.0
"""MagneticBox — magnetic-closure lid box type."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.precision import kwargs as precision_kwargs

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


from pyboxbuilder.box.base import BoxTypeBase, Interior


class MagneticBox(BoxTypeBase):
    """Magnetic-closure lid box type."""

    def interior(self, spec: BoxSpec) -> Interior:
        """Return the frame the box's contents may occupy."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        lt = spec.lid_thickness
        return Interior(
            width=spec.width - 2 * wt,
            length=spec.length - 2 * wt,
            height=spec.height - lt - ft,
            origin_x=wt, origin_y=wt, origin_z=ft,
        )

    @staticmethod
    def _body_height(spec: BoxSpec) -> float:
        """Return the body stops a lid's thickness short of the declared height.

        The lid closes onto the rim, so the two together come to `height` — the
        size the packer reserved. Building the walls full height would make the
        closed box a lid thicker than it was asked to be.
        """
        return spec.height - spec.lid_thickness

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Build the tray with blind magnet pockets in its top rim."""
        from pybosl2 import cylinder

        from pyboxbuilder.box.shell import build_shell

        spec = replace(spec, height=self._body_height(spec))
        body = build_shell(spec)

        # Magnet cavities in walls
        md = spec.magnet_diameter
        mh = spec.magnet_height
        nw = spec.magnet_count_width
        nl = spec.magnet_count_length
        # Blind pockets in the top rim: open upward, closed at the bottom so the
        # magnet cannot fall through.
        depth = mh + 0.2
        for xi in range(nw):
            mx = spec.width * (xi + 1) / (nw + 1)
            for yi in range(nl):
                my = spec.length * (yi + 1) / (nl + 1)
                pocket = cylinder(height=depth, radius=md / 2 + 0.1, **precision_kwargs())
                pocket = pocket.translate([mx, my, spec.height - depth / 2])
                body = body - pocket

        return body

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Return a plate that closes onto the rim, finishing at the declared height."""
        from pyboxbuilder.box.shell import block

        lt = spec.lid_thickness
        return block(
            [spec.width, spec.length, lt],
            at=(0, 0, self._body_height(spec)),
        )
