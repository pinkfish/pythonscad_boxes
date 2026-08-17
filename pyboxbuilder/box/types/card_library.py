# SPDX-License-Identifier: Apache-2.0
"""CardLibraryBox — card-library box type."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from pyboxbuilder.box.spec import BoxSpec

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


from pyboxbuilder.box.base import BoxTypeBase, Interior


class CardLibraryBox(BoxTypeBase):
    """Card-library box type."""

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

    def preferred_scoop_side(self, spec: BoxSpec):
        """Return a finger scoop belongs in the wall the lid leaves by.

        The other three carry the lid — two hold its grooves — and a scoop cut
        into a groove takes away the bearing that keeps the lid straight.
        """
        from pyboxbuilder.enums import ScoopSide

        return ScoopSide.RIGHT

    def lid_rounded_edges(self, spec: BoxSpec) -> list:
        """Return only the end that finishes outside the box.

        Its top edge and the two vertical corners there. The rest of the plate
        lives in the channel.
        """
        from pybosl2 import Anchor

        return [Anchor.TOP_RIGHT, Anchor.FRONT_RIGHT, Anchor.BACK_RIGHT]

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Return a sleeve-fed card box: sliding channel plus a latch dimple."""
        from pyboxbuilder.box.features import sliding_catch, sliding_track
        from pyboxbuilder.box.shell import build_shell, sliding_rim_rounding

        if spec.rim_rounding is None:
            spec = replace(spec, rim_rounding=sliding_rim_rounding(spec))
        body = build_shell(spec) - sliding_track(spec).body
        return body - sliding_catch(spec, spec.latch_radius, "x").body

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Return the sliding face, latched shut so the cards cannot spill."""
        from pyboxbuilder.box.features import sliding_catch, sliding_track

        return sliding_track(spec).require_lid() | sliding_catch(
            spec, spec.latch_radius, "x"
        ).require_lid()
