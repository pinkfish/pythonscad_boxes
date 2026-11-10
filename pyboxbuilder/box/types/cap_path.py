# SPDX-License-Identifier: Apache-2.0
"""CapPathBox — cap-path lid box type."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyboxbuilder.box.spec import BoxSpec

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.builders.cap_path import CapPathBoxBuilder
from pyboxbuilder.enums import BoxType, InterlockType


@register_box(BoxType.CAP_PATH, builder=CapPathBoxBuilder)
class CapPathBox(BoxTypeBase):
    """Cap-path lid box type."""

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
        """Return a hollow tray on a polygon footprint, sized for a cap to fit over."""
        from pyboxbuilder.box.features import (
            extrude_rounded_footprint,
            offset_footprint,
            path_body_metrics,
        )
        from pyboxbuilder.box.shell import base_rounding, body_rounding, build_shell  # noqa: F401
        from pyboxbuilder.rounding import mating_rounding

        path = spec.path or ()
        if not path:
            from pyboxbuilder.box.types.cap import CapBox

            return CapBox().build_body(spec)

        wt = spec.wall_thickness
        ft = spec.floor_thickness
        inset, body_height = path_body_metrics(spec)
        cap_h = spec.cap_height or min(10.0, spec.height / 2)
        band_z = spec.height - cap_h
        body_path = offset_footprint(path, inset)
        r_body = body_rounding(spec)
        r_mating = max(mating_rounding(spec), r_body * 0.75)
        r_base = min(
            base_rounding(spec),
            band_z * 0.45 if band_z > 0 else wt * 0.45,
            wt * 0.45,
        )

        if band_z >= body_height:
            outer = extrude_rounded_footprint(
                path, body_height, 0.0, r_corner=r_body, r_bottom=r_base
            )
        elif band_z > 0:
            lower = extrude_rounded_footprint(
                path, band_z, 0.0, r_corner=r_body, r_bottom=r_base
            )
            if spec.cap_finger_cutouts:
                cutouts = self._finger_cutouts(
                    spec, path, band_z, inset, r_mating
                )
                if cutouts is not None:
                    lower = lower - cutouts
            outer = lower | extrude_rounded_footprint(
                body_path, body_height, 0.0, r_corner=r_mating, r_bottom=r_base
            )
        else:
            outer = extrude_rounded_footprint(
                body_path, body_height, 0.0, r_corner=r_mating, r_bottom=r_base
            )

        if not spec.hollow:
            body = outer
        else:
            r_inner = min(r_body, wt * 0.35, max(0.0, (body_height - ft) / 4.0))
            inner = extrude_rounded_footprint(
                offset_footprint(path, wt),
                body_height - ft + 0.1,
                ft,
                r_corner=max(0.6, r_mating),
                r_bottom=r_inner,
            )
            body = outer - inner
        if spec.interlock_type not in (None, InterlockType.NONE):
            from pyboxbuilder.box.features import apply_horizontal_interlock

            body = apply_horizontal_interlock(body, spec)
        self._reject_stackable(spec)
        from pyboxbuilder.box.features import apply_stackable_body

        return apply_stackable_body(body, spec)

    def _finger_cutouts(
        self,
        spec: BoxSpec,
        path: tuple[tuple[float, float], ...],
        band_z: float,
        inset: float,
        r_mating: float = 0.0,
    ) -> Bosl2Solid | None:
        """Corner finger cutouts below the cap skirt on outer convex polygon corners."""
        import math

        from pyboxbuilder.box.features import (
            CAP_FINGER_CURVE_MAX_MM,
            CAP_FINGER_CURVE_TOTAL_MM,
            CAP_FINGER_FOOT_MM,
            CAP_FINGER_MAX_LENGTH_SHARE,
            CAP_FINGER_MIN_LENGTH_MM,
            CAP_FINGER_MIN_RADIUS_MM,
        )
        from pyboxbuilder.compartments.element import union_all
        from pyboxbuilder.compartments.finger_cuts import build_wall_scoop
        from pyboxbuilder.compartments.finger_outline import CutProfile
        from pyboxbuilder.compartments.finger_sweep import FaceTreatment
        from pyboxbuilder.enums import ScoopSide
        from pyboxbuilder.paths import (
            polygon_area,
            polygon_opposite_corners,
        )

        available = band_z - CAP_FINGER_FOOT_MM
        if available < CAP_FINGER_CURVE_TOTAL_MM - 1e-9:
            return None

        explicit_r = spec.cap_finger_radius
        if explicit_r is None:
            curves = min(
                CAP_FINGER_CURVE_MAX_MM, max(CAP_FINGER_CURVE_TOTAL_MM, available)
            )
            radius = curves / 2.0
        else:
            radius = max(float(explicit_r), CAP_FINGER_MIN_RADIUS_MM)
            curves = 2.0 * radius
        if available < curves - 1e-9:
            return None

        height = spec.cap_finger_height
        if height is None:
            height = curves
        height = min(max(float(height), curves), available)
        base_z = band_z - height

        n = len(path)
        ccw = polygon_area(path) >= 0.0
        min_x = min(pt[0] for pt in path)
        max_x = max(pt[0] for pt in path)
        min_y = min(pt[1] for pt in path)
        max_y = max(pt[1] for pt in path)
        corner_set = set(polygon_opposite_corners(path))
        for idx in range(n):
            p = path[idx]
            p_prev = path[(idx - 1) % n]
            p_next = path[(idx + 1) % n]
            e1 = (
                (p[0] - p_prev[0], p[1] - p_prev[1])
                if ccw
                else (p_prev[0] - p[0], p_prev[1] - p[1])
            )
            e2 = (
                (p_next[0] - p[0], p_next[1] - p[1])
                if ccw
                else (p[0] - p_next[0], p[1] - p_next[1])
            )
            if min(math.hypot(*e1), math.hypot(*e2)) < 2.0 * CAP_FINGER_MIN_LENGTH_MM:
                continue
            cross = e1[0] * e2[1] - e1[1] * e2[0]
            if cross <= 1e-6:
                continue
            on_front_or_back = (
                abs(p[1] - min_y) < 1e-6 or abs(p[1] - max_y) < 1e-6
            )
            near_side = p[0] <= min_x + 16.0 or p[0] >= max_x - 16.0
            if on_front_or_back and near_side:
                corner_set.add(idx)

        if not corner_set:
            return None

        fillet = inset / 2.0

        parts = []
        for idx in sorted(corner_set):
            p = path[idx]
            p_prev = path[(idx - 1) % n]
            p_next = path[(idx + 1) % n]
            d_prev = math.hypot(p[0] - p_prev[0], p[1] - p_prev[1])
            d_next = math.hypot(p[0] - p_next[0], p[1] - p_next[1])
            min_side = min(d_prev, d_next)
            run = (
                float(spec.cap_finger_length)
                if spec.cap_finger_length is not None
                else max(
                    CAP_FINGER_MIN_LENGTH_MM, min_side * CAP_FINGER_MAX_LENGTH_SHARE
                )
            )
            run = min(run, min_side * 0.35)
            cut_wt = inset + r_mating + fillet + 0.4
            span = max(4.0 * run, 4.0 * cut_wt)
            base_scoop = build_wall_scoop(
                span,
                span,
                height,
                ScoopSide.FRONT,
                radius=run,
                wall_thickness=cut_wt,
                profile=CutProfile(mouth_flare=radius, base_radius=radius),
                faces=FaceTreatment(
                    fillet=0.0,
                    round_inner=False,
                    round_outer=False,
                    breach_floor=True,
                    top_limit=height + 0.1,
                ),
            ).translate([-span / 2.0, cut_wt, base_z])
            edges = (
                (p[0] - p_prev[0], p[1] - p_prev[1])
                if ccw
                else (p_prev[0] - p[0], p_prev[1] - p[1]),
                (p_next[0] - p[0], p_next[1] - p[1])
                if ccw
                else (p[0] - p_next[0], p[1] - p_next[1]),
            )
            for dx, dy in edges:
                length = math.hypot(dx, dy)
                if length <= 1e-9:
                    continue
                angle = math.degrees(math.atan2(dy, dx))
                parts.append(
                    base_scoop.rotate([0.0, 0.0, angle]).translate([p[0], p[1], 0.0])
                )
        return union_all(parts)

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Return a cap whose skirt follows the same outline as the body."""
        from pyboxbuilder.box.features import path_cap

        self._reject_stackable(spec)
        path = spec.path or ()
        if not path:
            from pyboxbuilder.box.types.cap import CapBox

            return CapBox().build_lid(spec)
        return path_cap(spec, path, spec.cap_height or min(10.0, spec.height / 2))
