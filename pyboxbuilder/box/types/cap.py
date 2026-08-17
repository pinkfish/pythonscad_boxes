# SPDX-License-Identifier: Apache-2.0
"""CapBox — friction-fit cap lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyboxbuilder.box.spec import BoxSpec

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid

from pyboxbuilder.box.base import BoxTypeBase, Interior

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


class CapBox(BoxTypeBase):
    """Cap (friction-fit) lid box type."""

    def interior(self, spec: BoxSpec) -> Interior:
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        lt = spec.lid_thickness
        return Interior(
            width=spec.width - 2 * wt,
            length=spec.length - 2 * wt,
            height=spec.height - lt - ft,
            origin_x=wt, origin_y=wt, origin_z=ft,
        )

    def build_body(self, spec: BoxSpec) -> "Bosl2Solid":
        """The tray, stepped in at the top so the cap's skirt finishes flush.

        The body stops short of the declared height and its top band is set in
        by the lid's wall thickness: the declared size is the outside of the
        *closed* box, which is the size the packer reserved for it.
        """
        from pyboxbuilder.box.features import cap_body

        return cap_body(spec)

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> "Bosl2Solid":
        """A cap: a top plate with a skirt that grips the body's stepped-in band."""
        from pyboxbuilder.box.features import cap_lid

        return cap_lid(spec)
