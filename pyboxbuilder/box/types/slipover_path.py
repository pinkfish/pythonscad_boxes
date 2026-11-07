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
        if spec.foot > 0:
            outer = outer | extrude_footprint(path, spec.foot, 0.0)
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
        import math

        from pyboxbuilder.box.features import slipover_gap
        from pyboxbuilder.box.types.slipover import (
            SLIPOVER_FINGER_MAX_MM,
            SLIPOVER_FINGER_MAX_RADIUS_MM,
            SLIPOVER_FINGER_MIN_RADIUS_MM,
        )
        from pyboxbuilder.compartments.element import union_all
        from pyboxbuilder.compartments.finger_cuts import build_wall_scoop
        from pyboxbuilder.compartments.finger_outline import CutProfile
        from pyboxbuilder.compartments.finger_sweep import FaceTreatment
        from pyboxbuilder.enums import ScoopSide
        from pyboxbuilder.paths import polygon_area, polygon_opposite_corners

        wt = spec.wall_thickness
        lt = spec.lid_thickness
        foot = spec.foot
        gap = min(slipover_gap(spec), spec.height - foot - lt)
        skirt = spec.height - foot - gap
        requested = spec.slipover_finger_height
        height = (
            min(SLIPOVER_FINGER_MAX_MM, skirt / 3) if requested is None
            else float(requested)
        )
        height = max(0.0, min(height, skirt))
        if height <= 0:
            return None

        corner_indices = polygon_opposite_corners(path)
        if not corner_indices:
            return None

        n = len(path)
        ccw = polygon_area(path) >= 0.0
        base_z = foot + gap
        radius_cap = (
            SLIPOVER_FINGER_MAX_RADIUS_MM
            if requested is None
            else max(height, SLIPOVER_FINGER_MAX_RADIUS_MM)
        )
        notches = []
        for idx in corner_indices:
            p = path[idx]
            p_prev = path[(idx - 1) % n]
            p_next = path[(idx + 1) % n]
            d_prev = math.hypot(p[0] - p_prev[0], p[1] - p_prev[1])
            d_next = math.hypot(p[0] - p_next[0], p[1] - p_next[1])
            max_r = max(3.5, min(d_prev, d_next) * 0.22)
            r = min(max(height, SLIPOVER_FINGER_MIN_RADIUS_MM), radius_cap, max_r)
            top_rounding = min(2.0, r * 0.3)
            span = max(4.0 * r, 4.0 * wt)
            base_scoop = (
                build_wall_scoop(
                    span,
                    span,
                    height,
                    ScoopSide.FRONT,
                    radius=r,
                    wall_thickness=wt,
                    profile=CutProfile(mouth_flare=top_rounding),
                    faces=FaceTreatment(
                        fillet=wt / 4,
                        breach_floor=True,
                        top_limit=height,
                    ),
                )
                .translate([-span / 2, wt, 0.0])
                .mirror([0, 0, 1])
                .translate([0.0, 0.0, base_z + height])
            )
            edges = (
                (p[0] - p_prev[0], p[1] - p_prev[1])
                if ccw
                else (p_prev[0] - p[0], p_prev[1] - p[1]),
                (p_next[0] - p[0], p_next[1] - p[1])
                if ccw
                else (p[0] - p_next[0], p[1] - p_next[1]),
            )
            for dx, dy in edges:
                if math.hypot(dx, dy) <= 1e-9:
                    continue
                angle = math.degrees(math.atan2(dy, dx))
                notches.append(
                    base_scoop.rotate([0.0, 0.0, angle]).translate([p[0], p[1], 0.0])
                )
        return union_all(notches)

