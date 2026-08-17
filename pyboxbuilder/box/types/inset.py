# SPDX-License-Identifier: Apache-2.0
"""InsetBox — inset lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyboxbuilder.box.spec import BoxSpec

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


from pyboxbuilder.box.base import BoxTypeBase, Interior


class InsetBox(BoxTypeBase):
    """Inset lid box type."""

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

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the shell with a ledge cut into its top rim for the lid to sit in."""
        from pyboxbuilder.box.features import rabbet
        from pyboxbuilder.box.shell import build_shell

        closure = rabbet(spec, inset=spec.inset)
        return build_shell(spec) - closure.body

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Return a plate that drops into the rabbet and finishes flush with the rim."""
        from pyboxbuilder.box.features import rabbet

        return rabbet(spec, inset=spec.inset).lid
