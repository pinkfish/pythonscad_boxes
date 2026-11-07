# SPDX-License-Identifier: Apache-2.0
"""SnapFitBox — cantilever snap-fit latch box type (FR-081)."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Any

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.shell import block, body_rounding, build_shell
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.snap_fit import SnapFitBoxBuilder
from pyboxbuilder.enums import BoxType, CatchType, LatchAxis
from pyboxbuilder.rounding import round_edges, vertical_edges

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


def _extrude_profile(
    pts_tz: list[tuple[float, float]],
    s0: float,
    s_len: float,
    is_y: bool,
) -> Bosl2Solid:
    """Extrude a 2D ``(wall_normal_t, z)`` profile along the latch wall span."""
    from pybosl2 import Path2D
    from pybosl2.shapes2d import polygon

    poly = polygon(path=Path2D(pts_tz))
    if is_y:
        return poly.linear_extrude(height=s_len).rotate([90, 0, 90]).translate([s0, 0.0, 0.0])
    return (
        poly.linear_extrude(height=s_len)
        .rotate([90, 0, 0])
        .scale([1, -1, 1])
        .translate([0.0, s0, 0.0])
    )


@register_box(BoxType.SNAP_FIT, builder=SnapFitBoxBuilder)
class SnapFitBox(BoxTypeBase):
    """Cantilever latch box with positive detents and thumb releases (FR-081)."""

    def interior(self, spec: BoxSpec) -> Interior:
        """Return the usable volume inside the box."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        lt = spec.lid_thickness
        return Interior(
            width=spec.width - 2 * wt,
            length=spec.length - 2 * wt,
            height=spec.height - lt - ft,
            origin_x=wt,
            origin_y=wt,
            origin_z=ft,
        )

    def _body_spec(self, spec: BoxSpec) -> BoxSpec:
        """Return the body spec stopped below the lid plate."""
        return replace(spec, height=spec.height - spec.lid_thickness)

    def _latch_metrics(self, spec: BoxSpec) -> dict[str, Any]:
        """Compute calibrated cantilever arm, detent, and backing boss dimensions."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        lt = spec.lid_thickness
        body_h = spec.height - lt
        catch_type = spec.resolved_catch_type(CatchType.WEDGE)
        is_y = (
            spec.latch_axis == LatchAxis.Y
            or getattr(spec.latch_axis, "value", spec.latch_axis) == "y"
        )

        wall_span = spec.width if is_y else spec.length
        wall_dist = spec.length if is_y else spec.width
        s_c = wall_span / 2.0

        c_w = min(spec.cantilever_width, max(6.0, wall_span - 2 * wt - 4.0))
        c_t = max(1.6, spec.cantilever_thickness)
        clr = spec.deflection_clearance
        raw_d_h = spec.resolved_catch_size(spec.detent_height)

        if catch_type in (CatchType.WEDGE, CatchType.BUMP, CatchType.LEAF_SPRING):
            eff_d_h = min(raw_d_h, 0.9)
        elif catch_type in (CatchType.LOOP, CatchType.MAGNET):
            eff_d_h = min(raw_d_h, 1.1)
        else:
            eff_d_h = 0.0

        # Short, stocky cantilever arm (optimal ~5.5-6.5mm drop) for low bending strain
        avail_h = max(4.2, body_h - ft - 1.5)
        arm_drop = min(max(4.8, avail_h * 0.45), 6.5, avail_h)
        z_arm_bot = body_h - arm_drop

        det_h = max(1.8, eff_d_h * 2.4) if eff_d_h > 0 else 1.8
        pocket_z = z_arm_bot + 0.45
        pocket_h = max(2.2, det_h + 2 * clr)
        pocket_w = c_w + 2 * clr

        root_gusset = min(0.85, max(0.5, eff_d_h), max(0.3, (body_h - (pocket_z + det_h)) * 0.45))
        tip_bevel = min(0.75, c_t * 0.38)

        max_cut_depth = c_t + eff_d_h + clr
        back_skin = max(1.2, wt * 0.6)
        boss_t = max(wt, max_cut_depth + back_skin)
        boss_w = min(wall_span - 2 * wt, pocket_w + 2 * back_skin)
        z_boss_flat = max(ft, min(z_arm_bot, pocket_z) - clr - 0.8)
        z_boss_bot = max(ft, z_boss_flat - (boss_t - wt))

        return {
            "is_y": is_y,
            "catch_type": catch_type,
            "wt": wt,
            "ft": ft,
            "lt": lt,
            "body_h": body_h,
            "wall_span": wall_span,
            "wall_dist": wall_dist,
            "s_c": s_c,
            "c_w": c_w,
            "c_t": c_t,
            "clr": clr,
            "eff_d_h": eff_d_h,
            "arm_drop": arm_drop,
            "z_arm_bot": z_arm_bot,
            "det_h": det_h,
            "pocket_z": pocket_z,
            "pocket_h": pocket_h,
            "pocket_w": pocket_w,
            "root_gusset": root_gusset,
            "tip_bevel": tip_bevel,
            "boss_t": boss_t,
            "boss_w": boss_w,
            "z_boss_flat": z_boss_flat,
            "z_boss_bot": z_boss_bot,
        }

    def _build_backing_bosses(self, spec: BoxSpec) -> Bosl2Solid | None:
        """Return support-free 45°-tapered internal backing ribs behind the latch pockets."""
        m = self._latch_metrics(spec)
        wt = float(m["wt"])
        boss_t = float(m["boss_t"])
        if boss_t <= wt + 0.05:
            return None

        is_y = bool(m["is_y"])
        wall_dist = float(m["wall_dist"])
        s_c = float(m["s_c"])
        boss_w = float(m["boss_w"])
        body_h = float(m["body_h"])
        z_flat = float(m["z_boss_flat"])
        z_bot = float(m["z_boss_bot"])

        s0 = s_c - boss_w / 2.0
        pts_neg = [
            (wt * 0.5, z_bot),
            (wt, z_bot),
            (boss_t, z_flat),
            (boss_t, body_h),
            (wt * 0.5, body_h),
        ]
        pts_pos = [(wall_dist - t, z) for t, z in reversed(pts_neg)]
        return _extrude_profile(pts_neg, s0, boss_w, is_y) | _extrude_profile(
            pts_pos, s0, boss_w, is_y
        )

    def interior_mask(self, spec: BoxSpec) -> Bosl2Solid:
        """Subtract internal latch backing bosses so compartments keep full wall integrity."""
        mask = super().interior_mask(spec)
        m = self._latch_metrics(spec)
        wt = float(m["wt"])
        boss_t = float(m["boss_t"])
        if boss_t <= wt + 0.05:
            return mask

        is_y = bool(m["is_y"])
        wall_dist = float(m["wall_dist"])
        s_c = float(m["s_c"])
        boss_w = float(m["boss_w"])
        body_h = float(m["body_h"])
        z_bot = float(m["z_boss_bot"])

        pad = wt * 0.5
        keepout_w = boss_w + 2 * pad
        keepout_t = boss_t + pad
        s0 = s_c - keepout_w / 2.0
        h_k = body_h - z_bot + 1.0

        if is_y:
            k_neg = block([keepout_w, keepout_t, h_k], at=(s0, 0.0, z_bot))
            k_pos = block([keepout_w, keepout_t, h_k], at=(s0, wall_dist - keepout_t, z_bot))
        else:
            k_neg = block([keepout_t, keepout_w, h_k], at=(0.0, s0, z_bot))
            k_pos = block([keepout_t, keepout_w, h_k], at=(wall_dist - keepout_t, s0, z_bot))
        return mask - k_neg - k_pos

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the box body with reinforced internal backing bosses and recessed latch pockets."""
        from pybosl2 import cylinder
        from pybosl2.shapes3d import sphere

        from pyboxbuilder.precision import kwargs as precision_kwargs

        body_spec = self._body_spec(spec)
        body = build_shell(body_spec)

        bosses = self._build_backing_bosses(spec)
        if bosses is not None:
            body = body | bosses

        m = self._latch_metrics(spec)
        is_y = bool(m["is_y"])
        catch_type = m["catch_type"]
        body_h = float(m["body_h"])
        wall_dist = float(m["wall_dist"])
        s_c = float(m["s_c"])
        c_w = float(m["c_w"])
        c_t = float(m["c_t"])
        clr = float(m["clr"])
        eff_d_h = float(m["eff_d_h"])
        z_arm_bot = float(m["z_arm_bot"])
        det_h = float(m["det_h"])
        pocket_z = float(m["pocket_z"])
        pocket_h = float(m["pocket_h"])
        pocket_w = float(m["pocket_w"])
        root_gusset = float(m["root_gusset"])

        s0_chan = s_c - pocket_w / 2.0
        t_chan = c_t + clr
        g_chan = root_gusset + clr

        # Outer channel recess with top 45° bevel clearing the lid arm's root gusset
        chan_pts_neg = [
            (-0.1, z_arm_bot - clr),
            (t_chan, z_arm_bot - clr),
            (t_chan, body_h - g_chan),
            (t_chan + g_chan + 0.1, body_h + 0.1),
            (-0.1, body_h + 0.1),
        ]
        chan_pts_pos = [(wall_dist - t, z) for t, z in reversed(chan_pts_neg)]
        body = (
            body
            - _extrude_profile(chan_pts_neg, s0_chan, pocket_w, is_y)
            - _extrude_profile(chan_pts_pos, s0_chan, pocket_w, is_y)
        )

        t_pocket = c_t + eff_d_h + clr
        if catch_type in (CatchType.WEDGE, CatchType.LEAF_SPRING):
            if is_y:
                pocket_neg = block(
                    [pocket_w, t_pocket + 0.1, pocket_h],
                    at=(s0_chan, -0.1, pocket_z - clr),
                )
                pocket_pos = block(
                    [pocket_w, t_pocket + 0.1, pocket_h],
                    at=(s0_chan, wall_dist - t_pocket, pocket_z - clr),
                )
            else:
                pocket_neg = block(
                    [t_pocket + 0.1, pocket_w, pocket_h],
                    at=(-0.1, s0_chan, pocket_z - clr),
                )
                pocket_pos = block(
                    [t_pocket + 0.1, pocket_w, pocket_h],
                    at=(wall_dist - t_pocket, s0_chan, pocket_z - clr),
                )
            body = body - pocket_neg - pocket_pos

        elif catch_type == CatchType.BUMP:
            r_bump = min(eff_d_h, c_w / 3.0) + clr
            z_b = pocket_z + det_h / 2.0
            if is_y:
                dimple_neg = sphere(radius=r_bump, **precision_kwargs()).translate([s_c, c_t, z_b])
                dimple_pos = sphere(radius=r_bump, **precision_kwargs()).translate(
                    [s_c, wall_dist - c_t, z_b]
                )
            else:
                dimple_neg = sphere(radius=r_bump, **precision_kwargs()).translate([c_t, s_c, z_b])
                dimple_pos = sphere(radius=r_bump, **precision_kwargs()).translate(
                    [wall_dist - c_t, s_c, z_b]
                )
            body = body - dimple_neg - dimple_pos

        elif catch_type == CatchType.LOOP:
            ap_w = c_w * 0.6
            ap_h = max(2.2, eff_d_h * 1.8)
            stud_w = ap_w - 2 * clr
            stud_h = ap_h * 0.65
            if is_y:
                pocket_neg = block(
                    [pocket_w, t_pocket + 0.1, pocket_h],
                    at=(s0_chan, -0.1, pocket_z - clr),
                )
                pocket_pos = block(
                    [pocket_w, t_pocket + 0.1, pocket_h],
                    at=(s0_chan, wall_dist - t_pocket, pocket_z - clr),
                )
                stud_neg = block([stud_w, eff_d_h, stud_h], at=(s_c - stud_w / 2.0, c_t, pocket_z))
                stud_pos = block(
                    [stud_w, eff_d_h, stud_h],
                    at=(s_c - stud_w / 2.0, wall_dist - c_t - eff_d_h, pocket_z),
                )
            else:
                pocket_neg = block(
                    [t_pocket + 0.1, pocket_w, pocket_h],
                    at=(-0.1, s0_chan, pocket_z - clr),
                )
                pocket_pos = block(
                    [t_pocket + 0.1, pocket_w, pocket_h],
                    at=(wall_dist - t_pocket, s0_chan, pocket_z - clr),
                )
                stud_neg = block([eff_d_h, stud_w, stud_h], at=(c_t, s_c - stud_w / 2.0, pocket_z))
                stud_pos = block(
                    [eff_d_h, stud_w, stud_h],
                    at=(wall_dist - c_t - eff_d_h, s_c - stud_w / 2.0, pocket_z),
                )
            body = body - (pocket_neg - stud_neg) - (pocket_pos - stud_pos)

        elif catch_type == CatchType.MAGNET:
            r_m = min(eff_d_h, c_w / 3.0) + clr
            z_m = pocket_z + det_h / 2.0
            if is_y:
                cyl_neg = (
                    cylinder(height=eff_d_h + 0.2, radius=r_m, **precision_kwargs())
                    .rotate([90, 0, 0])
                    .translate([s_c, c_t + eff_d_h / 2.0, z_m])
                )
                cyl_pos = (
                    cylinder(height=eff_d_h + 0.2, radius=r_m, **precision_kwargs())
                    .rotate([90, 0, 0])
                    .translate([s_c, wall_dist - c_t - eff_d_h / 2.0, z_m])
                )
            else:
                cyl_neg = (
                    cylinder(height=eff_d_h + 0.2, radius=r_m, **precision_kwargs())
                    .rotate([0, 90, 0])
                    .translate([c_t + eff_d_h / 2.0, s_c, z_m])
                )
                cyl_pos = (
                    cylinder(height=eff_d_h + 0.2, radius=r_m, **precision_kwargs())
                    .rotate([0, 90, 0])
                    .translate([wall_dist - c_t - eff_d_h / 2.0, s_c, z_m])
                )
            body = body - cyl_neg - cyl_pos

        radius = body_rounding(spec)
        if radius > 0:
            body = round_edges(
                body,
                [spec.width, spec.length, body_h],
                radius,
                list(vertical_edges()),
            )
        from pyboxbuilder.box.features import apply_stackable_body

        return apply_stackable_body(body, spec)

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Return the lid plate with root-filleted cantilever arms and ramped retention detents."""
        from pybosl2 import cylinder
        from pybosl2.shapes3d import sphere

        from pyboxbuilder.precision import kwargs as precision_kwargs

        lt = spec.lid_thickness
        body_h = spec.height - lt
        lid = block([spec.width, spec.length, lt], at=(0, 0, body_h))

        m = self._latch_metrics(spec)
        is_y = bool(m["is_y"])
        catch_type = m["catch_type"]
        wall_dist = float(m["wall_dist"])
        s_c = float(m["s_c"])
        c_w = float(m["c_w"])
        c_t = float(m["c_t"])
        eff_d_h = float(m["eff_d_h"])
        arm_drop = float(m["arm_drop"])
        z_arm_bot = float(m["z_arm_bot"])
        det_h = float(m["det_h"])
        pocket_z = float(m["pocket_z"])
        root_gusset = float(m["root_gusset"])
        tip_bevel = float(m["tip_bevel"])

        s0_arm = s_c - c_w / 2.0

        # Base cantilever arm profile with 45° outer tip chamfer and 45° inner root gusset
        arm_pts_neg = [
            (0.0, z_arm_bot + tip_bevel),
            (tip_bevel, z_arm_bot),
            (c_t, z_arm_bot),
            (c_t, body_h - root_gusset),
            (c_t + root_gusset, body_h),
            (c_t + root_gusset, body_h + lt * 0.5),
            (0.0, body_h + lt * 0.5),
        ]
        arm_pts_pos = [(wall_dist - t, z) for t, z in reversed(arm_pts_neg)]
        arm_neg = _extrude_profile(arm_pts_neg, s0_arm, c_w, is_y)
        arm_pos = _extrude_profile(arm_pts_pos, s0_arm, c_w, is_y)

        if catch_type in (CatchType.WEDGE, CatchType.LEAF_SPRING):
            # Ramped wedge detent: 45° bottom lead-in ramp + flat crest + sloped top release ramp
            lead_ramp = min(eff_d_h, det_h * 0.45)
            rel_ramp = min(eff_d_h * 0.85, det_h * 0.35)
            det_pts_neg = [
                (c_t - 0.1, pocket_z),
                (c_t + eff_d_h, pocket_z + lead_ramp),
                (c_t + eff_d_h, pocket_z + det_h - rel_ramp),
                (c_t - 0.1, pocket_z + det_h),
            ]
            det_pts_pos = [(wall_dist - t, z) for t, z in reversed(det_pts_neg)]
            detent_neg = _extrude_profile(det_pts_neg, s0_arm, c_w, is_y)
            detent_pos = _extrude_profile(det_pts_pos, s0_arm, c_w, is_y)

            if catch_type == CatchType.LEAF_SPRING:
                waist_h = max(1.2, (arm_drop - det_h) * 0.45)
                waist_d = c_t * 0.3
                z_w = pocket_z + det_h + 0.1
                if is_y:
                    waist_neg = block(
                        [c_w + 0.2, waist_d + 0.1, waist_h],
                        at=(s0_arm - 0.1, -0.1, z_w),
                    )
                    waist_pos = block(
                        [c_w + 0.2, waist_d + 0.1, waist_h],
                        at=(s0_arm - 0.1, wall_dist - waist_d, z_w),
                    )
                else:
                    waist_neg = block(
                        [waist_d + 0.1, c_w + 0.2, waist_h],
                        at=(-0.1, s0_arm - 0.1, z_w),
                    )
                    waist_pos = block(
                        [waist_d + 0.1, c_w + 0.2, waist_h],
                        at=(wall_dist - waist_d, s0_arm - 0.1, z_w),
                    )
                lid = lid | (arm_neg - waist_neg) | detent_neg | (arm_pos - waist_pos) | detent_pos
            else:
                lid = lid | arm_neg | detent_neg | arm_pos | detent_pos

        elif catch_type == CatchType.BUMP:
            r_bump = min(eff_d_h, c_w / 3.0)
            z_b = pocket_z + det_h / 2.0
            if is_y:
                bump_neg = sphere(radius=r_bump, **precision_kwargs()).translate([s_c, c_t, z_b])
                bump_pos = sphere(radius=r_bump, **precision_kwargs()).translate(
                    [s_c, wall_dist - c_t, z_b]
                )
            else:
                bump_neg = sphere(radius=r_bump, **precision_kwargs()).translate([c_t, s_c, z_b])
                bump_pos = sphere(radius=r_bump, **precision_kwargs()).translate(
                    [wall_dist - c_t, s_c, z_b]
                )
            lid = lid | arm_neg | bump_neg | arm_pos | bump_pos

        elif catch_type == CatchType.LOOP:
            ap_w = c_w * 0.6
            ap_h = max(2.2, eff_d_h * 1.8)
            if is_y:
                ap_neg = block([ap_w, c_t + 0.3, ap_h], at=(s_c - ap_w / 2.0, -0.1, pocket_z))
                ap_pos = block(
                    [ap_w, c_t + 0.3, ap_h],
                    at=(s_c - ap_w / 2.0, wall_dist - c_t - 0.2, pocket_z),
                )
            else:
                ap_neg = block([c_t + 0.3, ap_w, ap_h], at=(-0.1, s_c - ap_w / 2.0, pocket_z))
                ap_pos = block(
                    [c_t + 0.3, ap_w, ap_h],
                    at=(wall_dist - c_t - 0.2, s_c - ap_w / 2.0, pocket_z),
                )
            lid = lid | (arm_neg - ap_neg) | (arm_pos - ap_pos)

        elif catch_type == CatchType.MAGNET:
            r_m = min(eff_d_h, c_w / 3.0)
            z_m = pocket_z + det_h / 2.0
            if is_y:
                cyl_neg = (
                    cylinder(height=c_t + 0.2, radius=r_m, **precision_kwargs())
                    .rotate([90, 0, 0])
                    .translate([s_c, c_t / 2.0, z_m])
                )
                cyl_pos = (
                    cylinder(height=c_t + 0.2, radius=r_m, **precision_kwargs())
                    .rotate([90, 0, 0])
                    .translate([s_c, wall_dist - c_t / 2.0, z_m])
                )
            else:
                cyl_neg = (
                    cylinder(height=c_t + 0.2, radius=r_m, **precision_kwargs())
                    .rotate([0, 90, 0])
                    .translate([c_t / 2.0, s_c, z_m])
                )
                cyl_pos = (
                    cylinder(height=c_t + 0.2, radius=r_m, **precision_kwargs())
                    .rotate([0, 90, 0])
                    .translate([wall_dist - c_t / 2.0, s_c, z_m])
                )
            lid = lid | (arm_neg - cyl_neg) | (arm_pos - cyl_pos)

        else:
            lid = lid | arm_neg | arm_pos

        radius = body_rounding(spec)
        if radius > 0:
            lid = round_edges(
                lid,
                [spec.width, spec.length, lt],
                radius,
                list(vertical_edges()),
            )
        from pyboxbuilder.box.features import apply_stackable_lid

        return apply_stackable_lid(lid, spec)
