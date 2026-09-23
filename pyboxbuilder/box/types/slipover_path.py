# SPDX-License-Identifier: Apache-2.0
"""SlipoverPathBox — slipover-path lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyboxbuilder.box.spec import BoxSpec

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.builders.slipover_path import SlipoverPathBoxBuilder
from pyboxbuilder.enums import BoxType


@register_box(BoxType.SLIPOVER_PATH, builder=SlipoverPathBoxBuilder)
class SlipoverPathBox(BoxTypeBase):
    """Slipover-path lid box type."""

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
        """Return a hollow tray on a polygon footprint, for a sleeve to slip over."""
        from pyboxbuilder.box.features import (
            extrude_footprint,
            offset_footprint,
            path_body_metrics,
        )

        path = spec.path or ()
        if not path:
            from pyboxbuilder.box.types.slipover import SlipoverBox

            return SlipoverBox().build_body(spec)

        # Set in all round and stopping short, so the sleeve that wraps it comes
        # back out to the declared outline and height.
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        inset, body_height = path_body_metrics(spec)

        body_path = offset_footprint(path, inset)
        outer = extrude_footprint(body_path, body_height)
        if not spec.hollow:
            body = outer
        else:
            inner = extrude_footprint(
                offset_footprint(body_path, wt), body_height - ft, ft
            )
            body = outer - inner
        from pyboxbuilder.box.features import apply_stackable_body

        return apply_stackable_body(body, spec)

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Return a sleeve following the body's outline, stopping at the foot."""
        from pyboxbuilder.box.features import (
            apply_stackable_lid,
            path_sleeve,
        )

        path = spec.path or ()
        if not path:
            from pyboxbuilder.box.types.slipover import SlipoverBox

            return SlipoverBox().build_lid(spec, decoration)
        lid = path_sleeve(spec, path, spec.slip, spec.foot)
        notches = self._finger_notches(spec, path)
        if notches is not None:
            lid = lid - notches
        return apply_stackable_lid(lid, spec)

    def _finger_notches(
        self, spec: BoxSpec, path: tuple[tuple[float, float], ...]
    ) -> Bosl2Solid | None:
        """Corner notches at opposite corners of the polygon sleeve so it can be pulled off."""
        from pybosl2.constants import Anchor
        from pybosl2.shapes3d import cyl

        from pyboxbuilder.box.types.slipover import (
            SLIPOVER_FINGER_MAX_MM,
            SLIPOVER_FINGER_MIN_RADIUS_MM,
        )
        from pyboxbuilder.compartments.element import union_all
        from pyboxbuilder.paths import polygon_opposite_corners

        foot = spec.foot
        skirt = spec.height - foot
        requested = spec.slipover_finger_height
        height = (
            min(SLIPOVER_FINGER_MAX_MM, skirt / 2) if requested is None
            else float(requested)
        )
        height = max(0.0, min(height, skirt))
        if height <= 0:
            return None

        corner_indices = polygon_opposite_corners(path)
        if not corner_indices:
            return None

        n = len(path)
        base_z = foot
        notches = []
        for idx in corner_indices:
            p = path[idx]
            p_prev = path[(idx - 1) % n]
            p_next = path[(idx + 1) % n]
            d_prev = ((p[0] - p_prev[0]) ** 2 + (p[1] - p_prev[1]) ** 2) ** 0.5
            d_next = ((p[0] - p_next[0]) ** 2 + (p[1] - p_next[1]) ** 2) ** 0.5
            max_r = max(SLIPOVER_FINGER_MIN_RADIUS_MM, min(d_prev, d_next) * 0.45)
            r = min(max(height, SLIPOVER_FINGER_MIN_RADIUS_MM), max_r)
            notches.append(
                cyl(
                    radius=r,
                    height=height + 0.5,
                    rounding2=min(r / 2, height / 2),
                    anchor=Anchor.BOTTOM,
                ).translate([p[0], p[1], base_z - 0.5])
            )
        return union_all(notches)

