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
            extrude_rounded_footprint,
            offset_footprint,
            path_body_metrics,
        )
        from pyboxbuilder.box.shell import base_rounding, body_rounding
        from pyboxbuilder.rounding import mating_rounding

        path = spec.path or ()
        if not path:
            from pyboxbuilder.box.types.slipover import SlipoverBox

            return SlipoverBox().build_body(spec)

        # Set in all round and stopping short, so the sleeve that wraps it comes
        # back out to the declared outline and height.
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        inset, body_height = path_body_metrics(spec)
        r_body = body_rounding(spec)
        r_mating = max(mating_rounding(spec), r_body * 0.75)
        r_base = min(
            base_rounding(spec),
            spec.foot * 0.45 if spec.foot > 0 else wt * 0.45,
            wt * 0.45,
        )

        body_path = offset_footprint(path, inset)
        outer = extrude_rounded_footprint(
            body_path,
            body_height,
            0.0,
            r_corner=r_mating,
            r_bottom=0.0 if spec.foot > 0 else r_base,
        )
        if spec.foot > 0:
            outer = outer | extrude_rounded_footprint(
                path, spec.foot, 0.0, r_corner=r_body, r_bottom=r_base
            )
        if not spec.hollow:
            body = outer
        else:
            r_inner = min(r_body, wt * 0.35, max(0.0, (body_height - ft) / 4.0))
            inner = extrude_rounded_footprint(
                offset_footprint(body_path, wt),
                body_height - ft + 0.1,
                ft,
                r_corner=max(0.6, r_mating),
                r_bottom=r_inner,
            )
            body = outer - inner
        self._reject_stackable(spec)
        from pyboxbuilder.box.features import apply_stackable_body

        return apply_stackable_body(body, spec, anchor_top_z=spec.foot - 0.1)

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Return a sleeve following the body's outline, stopping at the foot."""
        from pyboxbuilder.box.features import path_sleeve

        self._reject_stackable(spec)
        path = spec.path or ()
        if not path:
            from pyboxbuilder.box.types.slipover import SlipoverBox

            return SlipoverBox().build_lid(spec, decoration)
        lid = path_sleeve(spec, path, spec.slip, spec.foot)
        notches = self._finger_notches(spec, path)
        if notches is not None:
            lid = lid - notches
        return lid

    def _finger_notches(
        self, spec: BoxSpec, path: tuple[tuple[float, float], ...]
    ) -> Bosl2Solid | None:
        """Corner notches at outer corners of the polygon sleeve so it can be pulled off."""
        import math

        from pybosl2 import cylinder

        from pyboxbuilder.box.features import path_body_metrics, slipover_gap
        from pyboxbuilder.box.shell import block, body_rounding
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
        from pyboxbuilder.paths import (
            is_rectilinear,
            polygon_area,
            polygon_opposite_corners,
        )
        from pyboxbuilder.precision import kwargs as precision_kwargs
        from pyboxbuilder.rounding import mating_rounding

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

        opp_indices = polygon_opposite_corners(path)
        if not opp_indices:
            return None

        n = len(path)
        ccw = polygon_area(path) >= 0.0
        min_x = min(pt[0] for pt in path)
        max_x = max(pt[0] for pt in path)
        min_y = min(pt[1] for pt in path)
        max_y = max(pt[1] for pt in path)
        corner_set = set(opp_indices)
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
            d1 = math.hypot(*e1)
            d2 = math.hypot(*e2)
            if min(d1, d2) < 2.5 * SLIPOVER_FINGER_MIN_RADIUS_MM:
                continue
            cross = e1[0] * e2[1] - e1[1] * e2[0]
            if cross <= 1e-6:
                continue
            on_front_or_back = (
                abs(p[1] - min_y) < 1e-6 or abs(p[1] - max_y) < 1e-6
            )
            near_side = (
                p[0] <= min_x + 16.0 or p[0] >= max_x - 16.0
            )
            if on_front_or_back and near_side:
                corner_set.add(idx)

        corner_indices = sorted(corner_set)
        base_z = foot + gap
        inset, _ = path_body_metrics(spec)
        r_body = body_rounding(spec)
        r_mating = max(mating_rounding(spec), r_body * 0.75)
        min_edge = min(
            math.hypot(
                path[(i + 1) % n][0] - path[i][0],
                path[(i + 1) % n][1] - path[i][1],
            )
            for i in range(n)
        )
        rc = min(r_body, min_edge * 0.2) if is_rectilinear(path) else 0.0
        cut_wt = max(wt, inset + r_mating + 0.2)
        fillet = wt / 4
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
            span = max(4.0 * r, 4.0 * cut_wt)
            base_scoop = (
                build_wall_scoop(
                    span,
                    span,
                    height,
                    ScoopSide.FRONT,
                    radius=r,
                    wall_thickness=cut_wt,
                    profile=CutProfile(mouth_flare=top_rounding),
                    faces=FaceTreatment(
                        fillet=fillet,
                        round_inner=False,
                        breach_floor=True,
                        top_limit=height,
                    ),
                )
                .translate([-span / 2, cut_wt, 0.0])
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
            unit_edges = []
            for dx, dy in edges:
                length = math.hypot(dx, dy)
                if length <= 1e-9:
                    continue
                unit_edges.append((dx / length, dy / length))
                angle = math.degrees(math.atan2(dy, dx))
                notches.append(
                    base_scoop.rotate([0.0, 0.0, angle]).translate([p[0], p[1], 0.0])
                )
            if (
                len(unit_edges) == 2
                and rc > fillet > 0.0
                and abs(unit_edges[0][0] * unit_edges[1][0] + unit_edges[0][1] * unit_edges[1][1]) < 0.05
            ):
                u1, u2 = unit_edges[0], unit_edges[1]
                cx = p[0] - u1[0] * rc + u2[0] * rc
                cy = p[1] - u1[1] * rc + u2[1] * rc
                c_box = block(
                    [rc * 2.0, rc * 2.0, fillet],
                    at=(p[0] - rc, p[1] - rc, base_z + height),
                )
                c_cone = cylinder(
                    height=fillet + 0.04,
                    radius1=max(0.1, rc - fillet),
                    radius2=rc,
                    **precision_kwargs(),
                ).translate([cx, cy, base_z + height + fillet / 2.0])
                notches.append(c_box - c_cone)
        return union_all(notches)

