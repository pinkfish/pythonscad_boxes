# SPDX-License-Identifier: Apache-2.0
"""HingeBox — pin-hinge lid box type."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from pyboxbuilder.box.spec import BoxSpec

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid

    from pyboxbuilder.box.features import Closure


from pyboxbuilder.box.base import BoxTypeBase, Interior


class HingeBox(BoxTypeBase):
    """Pin-hinge lid box type."""

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
    def _body_spec(spec: BoxSpec) -> BoxSpec:
        """Return the body stops a lid's thickness short, so the closed lid seats on it."""
        lt = spec.lid_thickness
        return replace(spec, height=spec.height - lt)

    def _closure(self, spec: BoxSpec) -> Closure:
        """Both halves of the knuckle hinge, on one shared pin axis."""
        from pyboxbuilder.box.features import filament_hinge

        return filament_hinge(
            self._body_spec(spec),
            filament_diameter=spec.hinge_pin_diameter,
            knuckles=spec.hinge_count,
            lid_thickness=spec.lid_thickness,
        )

    def interior_mask(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the interior, less the room the hinge takes up inside it.

        The hinge sits within the box's outline, so its barrel and webs stand
        in the back of the interior. Compartments are clipped to what is left
        rather than being allowed to collide with it.

        Args:
            spec: The box's spec dict.

        Returns:
            The usable interior volume.

        """
        from pyboxbuilder.box.features import hinge_intrusion
        from pyboxbuilder.box.shell import block

        wt = spec.wall_thickness
        ft = spec.floor_thickness
        available = block(
            [spec.width - 2 * wt, spec.length - 2 * wt, spec.height],
            at=(wt, wt, ft),
        )
        return available - hinge_intrusion(
            self._body_spec(spec), spec.hinge_pin_diameter
        )

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the shell carrying every other knuckle of the hinge."""
        from pyboxbuilder.box.shell import build_shell, body_rounding
        from pyboxbuilder.rounding import round_edges, vertical_edges

        body = build_shell(self._body_spec(spec))
        closure = self._closure(spec)
        # The relief comes off before the body's own knuckles go on, so the
        # cut cannot eat into them.
        if closure.body_cut is not None:
            body = body - closure.body_cut
        body = body if closure.body is None else body | closure.body
        if closure.pin is not None:
            body = body - closure.pin

        radius = body_rounding(spec)
        if radius > 0:
            body = round_edges(
                body,
                [spec.width, spec.length, spec.height],
                radius,
                list(vertical_edges()),
            )
        return body

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Return the lid carrying the interleaving knuckles, bored for the same pin.

        The knuckles alternate along one axis with a print gap between them, so
        the two halves come off the bed as separate parts and articulate once
        the pin is fitted.
        """
        from pyboxbuilder.box.shell import block

        lt = spec.lid_thickness
        lid = block(
            [spec.width, spec.length, lt],
            at=(0, 0, self._body_spec(spec).height),
        )
        closure = self._closure(spec)
        if closure.lid_cut is not None:
            lid = lid - closure.lid_cut
        lid = lid if closure.lid is None else lid | closure.lid
        if closure.pin is not None:
            lid = lid - closure.pin
        return lid
