# SPDX-License-Identifier: Apache-2.0
"""PathBox — lidless tray with an arbitrary polygon footprint."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from pyboxbuilder.box.spec import BoxSpec

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.builders.path import PathBoxBuilder
from pyboxbuilder.enums import BoxType, InterlockType


@register_box(BoxType.PATH, builder=PathBoxBuilder)
class PathBox(BoxTypeBase):
    """Open tray whose footprint is a 2D polygon path rather than a rectangle.

    Produces a body only — a path box has no lid, so `build_lid` returns None
    and the exporter writes no `_lid.3mf` for it.
    """

    def interior(self, spec: BoxSpec) -> Interior:
        """Return the frame the box's contents may occupy."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        return Interior(
            width=spec.width - 2 * wt,
            length=spec.length - 2 * wt,
            height=spec.height - ft,
            origin_x=wt, origin_y=wt, origin_z=ft,
        )

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Build an open tray on a polygon footprint, with no lid."""
        wt = spec.wall_thickness
        path = spec.path or ()

        from pyboxbuilder.box.shell import (
            apply_finger_holes,
            build_shell,
            with_no_lid_finger_holes,
        )

        # Lidless, whoever built the spec — see `NoLidBox._build_shell`. The
        # automatic holes decline themselves on a polygon footprint (FR-047c),
        # so this path needs no special case.
        spec = with_no_lid_finger_holes(replace(spec, rim_free=True))

        if not path:
            body = build_shell(spec)
        else:
            outer = self._extrude_outer(path, spec)
            if not spec.hollow:
                body = apply_finger_holes(outer, spec)
            else:
                inner = self._extrude_inner(_inset_path(path, wt), spec)
                body = outer - inner
                body = self._round_inner_rim(body, path, spec)
                body = apply_finger_holes(body, spec)
            indents = self._path_finger_indents(spec, path)
            if indents is not None:
                body = body - indents

        if spec.interlock_type not in (None, InterlockType.NONE):
            from pyboxbuilder.box.features import apply_horizontal_interlock

            body = apply_horizontal_interlock(body, spec)
        return body

    @staticmethod
    def _extrude(path: tuple[tuple[float, float], ...], height: float) -> Bosl2Solid:
        """Extrude a polygon outline with its base at z = 0."""
        from pybosl2 import Path2D

        profile = Path2D([(float(x), float(y)) for x, y in path], closed=True)
        return profile.linear_extrude(height=height)

    @classmethod
    def _extrude_outer(
        cls, path: tuple[tuple[float, float], ...], spec: BoxSpec
    ) -> Bosl2Solid:
        """Extrude the outer polygon shell with rounded top and bottom rims."""
        import math

        from pybosl2 import Path2D
        from pybosl2.shapes3d.base import CsgSolid
        from pybosl2.skin import os_profile

        from pyboxbuilder.box.shell import body_rounding
        from pyboxbuilder.paths import is_rectilinear
        from pyboxbuilder.rounding import rounding_facets

        wt = spec.wall_thickness
        r_body = body_rounding(spec)
        r_outer = min(r_body, wt * 0.45, spec.height / 4.0)
        if r_outer <= 0.05 or len(path) < 3:
            return cls._extrude(path, spec.height)

        try:
            steps = max(8, rounding_facets()["fn"] // 4)
            fn = rounding_facets()["fn"]
            outer_2d = Path2D([(float(x), float(y)) for x, y in path], closed=True)
            if is_rectilinear(path):
                min_edge = min(
                    math.hypot(
                        path[(i + 1) % len(path)][0] - path[i][0],
                        path[(i + 1) % len(path)][1] - path[i][1],
                    )
                    for i in range(len(path))
                )
                r_corner = min(r_body, min_edge * 0.2)
                if r_corner > 0.05:
                    outer_2d = outer_2d.round_corners(radius=r_corner, fn=fn)
            outer_base = outer_2d.offset(delta=-r_outer)
            prof_pts = [
                [
                    -r_outer * math.sin((math.pi / 2) * i / steps),
                    r_outer * (1.0 - math.cos((math.pi / 2) * i / steps)),
                ]
                for i in range(steps + 1)
            ]
            prof = os_profile(Path2D(prof_pts))
            swept = outer_base.offset_sweep(
                height=spec.height, bottom=prof, top=prof, steps=steps
            )
            return CsgSolid(swept.polyhedron()) if hasattr(swept, "polyhedron") else swept
        except Exception:
            return cls._extrude(path, spec.height)

    @classmethod
    def _extrude_inner(
        cls, inner_path: tuple[tuple[float, float], ...], spec: BoxSpec
    ) -> Bosl2Solid:
        """Extrude the inner polygon cavity with a rounded floor fillet."""
        import math

        from pybosl2 import Path2D
        from pybosl2.shapes3d.base import CsgSolid
        from pybosl2.skin import os_profile

        from pyboxbuilder.box.shell import body_rounding
        from pyboxbuilder.paths import is_rectilinear
        from pyboxbuilder.rounding import rounding_facets

        wt = spec.wall_thickness
        ft = spec.floor_thickness
        cav_h = spec.height - ft
        r_body = body_rounding(spec)
        r_inner = min(r_body, wt * 0.35, cav_h / 4.0)
        if r_inner <= 0.05 or len(inner_path) < 3:
            return cls._extrude(inner_path, cav_h).translate([0.0, 0.0, ft])

        try:
            steps = max(8, rounding_facets()["fn"] // 4)
            fn = rounding_facets()["fn"]
            inner_2d = Path2D([(float(x), float(y)) for x, y in inner_path], closed=True)
            if is_rectilinear(inner_path):
                min_edge = min(
                    math.hypot(
                        inner_path[(i + 1) % len(inner_path)][0] - inner_path[i][0],
                        inner_path[(i + 1) % len(inner_path)][1] - inner_path[i][1],
                    )
                    for i in range(len(inner_path))
                )
                r_corner = min(r_inner, min_edge * 0.2)
                if r_corner > 0.05:
                    inner_2d = inner_2d.round_corners(radius=r_corner, fn=fn)
            inner_base = inner_2d.offset(delta=-r_inner)
            prof_pts = [
                [
                    -r_inner * math.sin((math.pi / 2) * i / steps),
                    r_inner * (1.0 - math.cos((math.pi / 2) * i / steps)),
                ]
                for i in range(steps + 1)
            ]
            prof = os_profile(Path2D(prof_pts))
            swept = inner_base.offset_sweep(
                height=cav_h + 0.1, bottom=prof, steps=steps
            )
            solid = CsgSolid(swept.polyhedron()) if hasattr(swept, "polyhedron") else swept
            return solid.translate([0.0, 0.0, ft])
        except Exception:
            return cls._extrude(inner_path, cav_h).translate([0.0, 0.0, ft])

    @staticmethod
    def _round_inner_rim(
        body: Bosl2Solid, path: tuple[tuple[float, float], ...], spec: BoxSpec
    ) -> Bosl2Solid:
        """Round the inner top edge of the polygon rim."""
        import math

        from pybosl2 import Path2D
        from pybosl2.shapes3d.base import CsgSolid

        from pyboxbuilder.box.shell import block, body_rounding
        from pyboxbuilder.paths import is_rectilinear
        from pyboxbuilder.rounding import rounding_facets, roundover_profile

        wt = spec.wall_thickness
        ft = spec.floor_thickness
        cav_h = spec.height - ft
        r_body = body_rounding(spec)
        r_inner = min(r_body, wt * 0.35, cav_h / 4.0)
        if r_inner <= 0.05 or len(path) < 3:
            return body

        try:
            inner_pts = _inset_path(path, wt)
            steps = max(8, rounding_facets()["fn"] // 4)
            fn = rounding_facets()["fn"]
            inner_2d = Path2D([(float(x), float(y)) for x, y in inner_pts], closed=True)
            if is_rectilinear(inner_pts):
                min_edge = min(
                    math.hypot(
                        inner_pts[(i + 1) % len(inner_pts)][0] - inner_pts[i][0],
                        inner_pts[(i + 1) % len(inner_pts)][1] - inner_pts[i][1],
                    )
                    for i in range(len(inner_pts))
                )
                r_corner = min(r_inner, min_edge * 0.2)
                if r_corner > 0.05:
                    inner_2d = inner_2d.round_corners(radius=r_corner, fn=fn)
            widened = inner_2d.offset(delta=r_inner)
            swept = widened.offset_sweep(
                height=2.0 * r_inner,
                bottom=roundover_profile(r_inner, steps),
                steps=steps,
            )
            swept_solid = (
                CsgSolid(swept.polyhedron()) if hasattr(swept, "polyhedron") else swept
            )
            min_x = min(p[0] for p in path) - 4.0 * r_inner
            min_y = min(p[1] for p in path) - 4.0 * r_inner
            max_x = max(p[0] for p in path) + 4.0 * r_inner
            max_y = max(p[1] for p in path) + 4.0 * r_inner
            keep = block(
                [max_x - min_x, max_y - min_y, r_inner + 1.0],
                at=(min_x, min_y, -1.0),
            )
            ring = (swept_solid & keep).mirror([0, 0, 1])
            return body - ring.translate([0.0, 0.0, spec.height])
        except Exception:
            return body

    @staticmethod
    def _path_finger_indents(
        spec: BoxSpec, path: tuple[tuple[float, float], ...]
    ) -> Bosl2Solid | None:
        """Build subtle top-rim finger indents on opposing edges of a polygon path box."""
        import math

        from pyboxbuilder.compartments.element import union_all
        from pyboxbuilder.compartments.finger_cuts import build_wall_scoop
        from pyboxbuilder.compartments.finger_outline import CutProfile
        from pyboxbuilder.compartments.finger_sweep import (
            DEFAULT_FLOOR_DIP_MM,
            FaceTreatment,
        )
        from pyboxbuilder.enums import ScoopSide
        from pyboxbuilder.paths import polygon_area

        if not spec.auto_finger_holes or spec.finger_holes or len(path) < 3:
            return None

        wt = spec.wall_thickness
        ft = spec.floor_thickness
        deepest = spec.height - ft - 5.0
        reach = min(6.0, spec.height * 0.32, deepest)
        if reach < 3.0:
            return None

        pts = list(path)
        if polygon_area(path) < 0.0:
            pts.reverse()

        n = len(pts)
        candidates = []
        for i in range(n):
            p0 = pts[i]
            p1 = pts[(i + 1) % n]
            dx = p1[0] - p0[0]
            dy = p1[1] - p0[1]
            length = math.hypot(dx, dy)
            span = length - 2.0 * wt
            if span < 16.0:
                continue
            radius = min(8.0, max(5.0, reach * 1.25), span * 0.22)
            mouth_flare = min(2.5, radius * 0.35)
            if 2.0 * (radius + mouth_flare) > span * 0.75:
                continue
            tx, ty = dx / length, dy / length
            nx, ny = ty, -tx
            mx, my = (p0[0] + p1[0]) / 2.0, (p0[1] + p1[1]) / 2.0
            angle = math.degrees(math.atan2(dy, dx))
            candidates.append(
                {
                    "idx": i,
                    "length": length,
                    "span": span,
                    "radius": radius,
                    "mouth_flare": mouth_flare,
                    "nx": nx,
                    "ny": ny,
                    "mx": mx,
                    "my": my,
                    "angle": angle,
                }
            )

        if not candidates:
            return None

        selected = []
        if len(candidates) == 1:
            selected = [candidates[0]]
        else:
            best_pair = None
            best_score = -1e9
            for a_idx in range(len(candidates)):
                for b_idx in range(a_idx + 1, len(candidates)):
                    ca = candidates[a_idx]
                    cb = candidates[b_idx]
                    dot = ca["nx"] * cb["nx"] + ca["ny"] * cb["ny"]
                    if dot > -0.2:
                        continue
                    score = (-dot) * 10.0 + min(ca["length"], cb["length"]) + 0.5 * (
                        ca["length"] + cb["length"]
                    )
                    if score > best_score:
                        best_score = score
                        best_pair = (ca, cb)
            if best_pair is not None:
                selected = [best_pair[0], best_pair[1]]
            else:
                by_len = sorted(candidates, key=lambda c: c["length"], reverse=True)
                selected = by_len[:2]

        flare = min(wt / 4.0, reach / 4.0)
        outline_height = max(1.0, reach - flare)
        indents = []
        for c in selected:
            throat = min(c["radius"], outline_height)
            span = c["span"]
            scoop = (
                build_wall_scoop(
                    span,
                    span,
                    outline_height,
                    ScoopSide.FRONT,
                    radius=throat,
                    wall_thickness=wt,
                    profile=CutProfile(mouth_flare=c["mouth_flare"]),
                    faces=FaceTreatment(
                        fillet=flare,
                        top_limit=None,
                        floor_clearance=flare + DEFAULT_FLOOR_DIP_MM,
                    ),
                    keep_flat_bottom=False,
                    closed_top=False,
                )
                .translate([-span / 2.0, wt, spec.height - outline_height])
                .rotate([0.0, 0.0, c["angle"]])
                .translate([c["mx"], c["my"], 0.0])
            )
            indents.append(scoop)

        return union_all(indents)

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> None:
        """Path boxes have no lid."""
        return None


def _inset_path(
    path: tuple[tuple[float, float], ...], distance: float
) -> tuple[tuple[float, float], ...]:
    """Shrink a footprint by `distance` to get the tray's inner cavity.

    Leftover regions from the packer are rectilinear, and those get an exact
    edge-wise inset — a centroid scale would pull an L's reflex corner the wrong
    way and thin one arm while fattening the other. Anything else falls back to
    the centroid scale, which is fine for the convex outlines a caller is likely
    to hand-write and never self-intersects.
    """
    from pyboxbuilder.paths import inset_rectilinear, is_rectilinear

    if is_rectilinear(path):
        return inset_rectilinear(path, distance)

    cx = sum(p[0] for p in path) / len(path)
    cy = sum(p[1] for p in path) / len(path)
    out = []
    for x, y in path:
        dx, dy = x - cx, y - cy
        span = max((dx * dx + dy * dy) ** 0.5, 1e-9)
        scale = max(0.0, (span - distance) / span)
        out.append((cx + dx * scale, cy + dy * scale))
    return tuple(out)
