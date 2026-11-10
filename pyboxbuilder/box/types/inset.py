# SPDX-License-Identifier: Apache-2.0
"""InsetBox — inset lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyboxbuilder.box.spec import BoxSpec

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.builders.inset import InsetBoxBuilder
from pyboxbuilder.enums import BoxType


@register_box(BoxType.INSET, builder=InsetBoxBuilder)
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
        from pyboxbuilder.box.features import (
            FIT_SLACK_MM,
            apply_stackable_body,
            hinge_catch,
            rabbet,
        )
        from pyboxbuilder.box.shell import block, build_shell
        from pyboxbuilder.enums import CatchType

        closure = rabbet(spec, inset=spec.inset)
        body = build_shell(spec) - closure.body
        if spec.resolved_catch_type(CatchType.NONE) != CatchType.NONE:
            self._reject_stackable(
                spec,
                reason=(
                    "InsetBox with an active catch_type adds downward lid features "
                    "that require printing the lid upside down"
                ),
            )
            wt = spec.wall_thickness
            lt = spec.lid_thickness
            ledge = max(wt - spec.inset, 0.0)
            front_notch = block(
                [spec.width - 2 * wt, ledge + FIT_SLACK_MM + 0.1, lt + 0.2],
                at=(wt, -0.05, spec.height - lt - 0.1),
            )
            body = body - front_notch
            catch = hinge_catch(spec)
            if catch.body_cut is not None:
                body = body - catch.body_cut
            if catch.body is not None:
                body = body | catch.body

        return apply_stackable_body(body, spec)

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Return a plate that drops into the rabbet and finishes flush with the rim."""
        from pyboxbuilder.box.features import (
            FIT_SLACK_MM,
            apply_stackable_lid,
            hinge_catch,
            rabbet,
        )
        from pyboxbuilder.box.shell import block
        from pyboxbuilder.enums import CatchType

        lid = rabbet(spec, inset=spec.inset).lid
        if spec.resolved_catch_type(CatchType.NONE) != CatchType.NONE:
            self._reject_stackable(
                spec,
                reason=(
                    "InsetBox with an active catch_type adds downward lid features "
                    "that require printing the lid upside down"
                ),
            )
            wt = spec.wall_thickness
            lt = spec.lid_thickness
            ledge = max(wt - spec.inset, 0.0)
            front_tab = block(
                [spec.width - 2 * wt - 2 * FIT_SLACK_MM, ledge + FIT_SLACK_MM + 0.1, lt],
                at=(wt + FIT_SLACK_MM, 0.0, spec.height - lt),
            )
            lid = lid | front_tab
            catch = hinge_catch(spec)
            if catch.lid_cut is not None:
                lid = lid - catch.lid_cut
            if catch.lid is not None:
                lid = lid | catch.lid
        return apply_stackable_lid(lid, spec)
