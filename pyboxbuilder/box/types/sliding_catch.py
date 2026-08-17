# SPDX-License-Identifier: Apache-2.0
"""SlidingCatchBox — sliding-catch lid box type."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from pyboxbuilder.box.spec import BoxSpec

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


from pyboxbuilder.box.base import BoxTypeBase, Interior

DEFAULT_CATCH_RADIUS_MM = 1.0
"""The bump a sliding-catch box clicks shut on, when none is given (FR-002e3).

A plain sliding box defaults to *no* catch — its dovetail already stops the lid
lifting out — so `BoxSpec.catch_radius` is `None` there. This type is the one
that always carries one, so it supplies the size the spec leaves open.
"""


class SlidingCatchBox(BoxTypeBase):
    """Sliding-catch lid box type."""

    @staticmethod
    def _catch_radius(spec: BoxSpec) -> float:
        """This box's catch size — its own, or the type's default."""
        return spec.catch_radius if spec.catch_radius is not None else DEFAULT_CATCH_RADIUS_MM

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

    def preferred_scoop_side(self, spec: BoxSpec):
        """A finger scoop belongs in the wall the lid leaves by.

        The other three carry the lid — two hold its grooves — and a scoop cut
        into a groove takes away the bearing that keeps the lid straight.
        """
        from pyboxbuilder.enums import ScoopSide

        return ScoopSide.RIGHT

    def lid_rounded_edges(self, spec: BoxSpec) -> list:
        """Only the end that finishes outside the box: its top edge and the two
        vertical corners there. The rest of the plate lives in the channel."""
        from pybosl2 import Anchor

        return [Anchor.TOP_RIGHT, Anchor.FRONT_RIGHT, Anchor.BACK_RIGHT]

    def build_body(self, spec: BoxSpec) -> "Bosl2Solid":
        """Sliding grooves, plus a dimple beside the outlet for the catch."""
        from pyboxbuilder.box.features import sliding_catch, sliding_track
        from pyboxbuilder.box.shell import build_shell, sliding_rim_rounding

        if spec.rim_rounding is None:
            spec = replace(spec, rim_rounding=sliding_rim_rounding(spec))
        body = build_shell(spec) - sliding_track(spec).body
        return body - sliding_catch(spec, self._catch_radius(spec), "x").body

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> "Bosl2Solid":
        """The sliding plate with a bump that clicks into the body's dimple."""
        from pyboxbuilder.box.features import sliding_catch, sliding_track

        return sliding_track(spec).lid | sliding_catch(spec, self._catch_radius(spec), "x").lid
