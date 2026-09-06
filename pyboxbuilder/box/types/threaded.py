# SPDX-License-Identifier: Apache-2.0
"""ThreadedBox — screw-thread container type (FR-083)."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from pybosl2.parts.threading import trapezoidal_threaded_rod
from pybosl2.shapes3d import cyl

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.shell import block, body_rounding, build_shell
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.rounding import round_edges, vertical_edges

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


class ThreadedBox(BoxTypeBase):
    """Container with coarse modified trapezoidal screw threads (FR-083)."""

    def interior(self, spec: BoxSpec) -> Interior:
        """Return the usable interior volume."""
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

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the cylindrical container with threaded male neck and seating shoulder."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        lt = spec.lid_thickness
        body_h = spec.height - lt
        d = min(spec.width, spec.length)
        r = d / 2.0
        x_c = spec.width / 2.0
        y_c = spec.length / 2.0

        if not spec.round_footprint:
            body_spec = self._body_spec(spec)
            body = build_shell(body_spec)
            radius = body_rounding(spec)
            if radius > 0:
                body = round_edges(
                    body,
                    [spec.width, spec.length, body_h],
                    radius,
                    list(vertical_edges()),
                )
            return body

        pitch = spec.thread_pitch
        turns = spec.thread_turns
        neck_h = max(6.0, pitch * turns)
        shoulder_z = body_h - neck_h

        # Base body cylinder up to shoulder
        base_cyl = cyl(height=shoulder_z, radius=r).translate(
            [x_c, y_c, shoulder_z / 2.0]
        )

        # Male threaded neck
        thread_d = max(10.0, d - 2 * wt)
        rod = trapezoidal_threaded_rod(
            d=thread_d,
            l=neck_h,
            pitch=pitch,
            thread_angle=45,
            thread_depth=spec.thread_depth,
        ).shape().translate([x_c, y_c, shoulder_z + neck_h / 2.0])

        body = base_cyl | rod

        # Hollow cavity
        inner_r = max(2.0, thread_d / 2.0 - spec.thread_depth - 1.0)
        inner_h = body_h - ft + 1.0
        cavity = cyl(height=inner_h, radius=inner_r).translate(
            [x_c, y_c, ft + inner_h / 2.0]
        )
        body = body - cavity

        return body

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Return the female threaded cap with flush seating rim."""
        wt = spec.wall_thickness
        lt = spec.lid_thickness
        body_h = spec.height - lt

        if not spec.round_footprint:
            lid = block([spec.width, spec.length, lt], at=(0, 0, body_h))
            radius = body_rounding(spec)
            if radius > 0:
                lid = round_edges(
                    lid,
                    [spec.width, spec.length, lt],
                    radius,
                    list(vertical_edges()),
                )
            return lid

        d = min(spec.width, spec.length)
        r = d / 2.0
        x_c = spec.width / 2.0
        y_c = spec.length / 2.0

        pitch = spec.thread_pitch
        turns = spec.thread_turns
        neck_h = max(6.0, pitch * turns)
        shoulder_z = body_h - neck_h
        total_lid_h = neck_h + lt

        lid_cyl = cyl(height=total_lid_h, radius=r).translate(
            [x_c, y_c, shoulder_z + total_lid_h / 2.0]
        )

        # Threaded internal tap with clearance
        thread_d = max(10.0, d - 2 * wt)
        tap_d = thread_d + 2 * spec.thread_clearance
        tap = trapezoidal_threaded_rod(
            d=tap_d,
            l=neck_h + 1.0,
            pitch=pitch,
            thread_angle=45,
            thread_depth=spec.thread_depth,
        ).shape().translate([x_c, y_c, shoulder_z + (neck_h + 1.0) / 2.0 - 0.5])

        lid = lid_cyl - tap
        return lid
