# SPDX-License-Identifier: Apache-2.0
"""PrintInPlaceHingeBox — monolithic print-in-place hinged box type (FR-090)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pybosl2.parts.hinges import SnapLock, SnapSocket

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.shell import block, body_rounding
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.pip_hinge import PrintInPlaceHingeBoxBuilder
from pyboxbuilder.enums import BoxType, CatchType
from pyboxbuilder.rounding import round_edges

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


def _to_solid(obj: object) -> Bosl2Solid:
    """Extract the underlying Bosl2Solid across different pybosl2 versions."""
    from typing import cast

    shape_attr = getattr(obj, "shape", None)
    if callable(shape_attr):
        return cast("Bosl2Solid", shape_attr())
    if hasattr(obj, "_solid"):
        return cast("Bosl2Solid", obj._solid)
    if hasattr(obj, "translate"):
        return cast("Bosl2Solid", obj)
    return cast("Bosl2Solid", shape_attr)


@register_box(BoxType.PRINT_IN_PLACE_HINGE, builder=PrintInPlaceHingeBoxBuilder)
class PrintInPlaceHingeBox(BoxTypeBase):
    """Monolithic 180° flat print-in-place captive hinge box (FR-090)."""

    def interior(self, spec: BoxSpec) -> Interior:
        """Return the usable interior volume of the base tray half."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        half_h = spec.height / 2.0
        inner_w = spec.width - 2 * wt
        inner_l = spec.length - 2 * wt
        inner_h = half_h - ft
        return Interior(
            width=inner_w,
            length=inner_l,
            height=inner_h,
            origin_x=wt,
            origin_y=wt,
            origin_z=ft,
        )

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the monolithic print containing body tray, lid tray, 3D-printable bridge hinge, and snap catches."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        lt = spec.lid_thickness
        half_h = spec.height / 2.0
        bridge_w = max(0.4, float(getattr(spec, "pip_bridge_width", 0.4)))
        bridge_t = max(0.2, float(getattr(spec, "pip_bridge_thickness", 0.4)))

        # 1. Main Box Body (tray of height half_h)
        inner_w = spec.width - 2 * wt
        inner_l = spec.length - 2 * wt
        body_outer = block([spec.width, spec.length, half_h], at=(0, 0, 0))
        body_cavity = block([inner_w, inner_l, half_h - ft + 1.0], at=(wt, wt, ft))
        body = body_outer - body_cavity

        # 2. Lid tray of height half_h unfolded flat 180° behind the body along Y
        lid_origin_y = spec.length + bridge_w
        lid_outer = block(
            [spec.width, spec.length, half_h],
            at=(0, lid_origin_y, 0),
        )
        lid_cavity = block(
            [inner_w, inner_l, half_h - lt + 1.0],
            at=(wt, lid_origin_y + wt, lt),
        )
        lid = lid_outer - lid_cavity

        # Apply corner rounding only to the front outer corners of body and lid,
        # preserving the square hinge interface along the back wall so the bridge
        # joins flush from side wall to side wall without disconnected edges.
        from pybosl2 import Anchor

        radius = body_rounding(spec)
        if radius > 0:
            body = round_edges(
                body,
                [spec.width, spec.length, half_h],
                radius,
                [Anchor.FRONT_LEFT, Anchor.FRONT_RIGHT],
                at=(0.0, 0.0, 0.0),
            )
            lid = round_edges(
                lid,
                [spec.width, spec.length, half_h],
                radius,
                [Anchor.BACK_LEFT, Anchor.BACK_RIGHT],
                at=(0.0, lid_origin_y, 0.0),
            )

        # 3. 3D-printable bridge joining the two halves at the shared rim level (z = half_h)
        # Small overlap (fudge) into body and lid walls prevents coincident-surface artifacts
        fudge = 0.01
        bridge = block(
            [spec.width, bridge_w + 2 * fudge, bridge_t],
            at=(0.0, spec.length - fudge, half_h - bridge_t),
        )

        monolithic = body | lid | bridge

        # 4. SnapLock & SnapSocket catches from pybosl2.parts.hinges
        if spec.pip_snap_catch and spec.resolved_catch_type(CatchType.WEDGE) != CatchType.NONE:
            catch_w = min(spec.pip_snap_width, spec.width * 0.4)
            snap_diam = spec.pip_snap_diameter
            sock_obj = SnapSocket(
                thick=wt,
                snaplen=catch_w,
                snapdiam=snap_diam,
                foldangle=180,
            )
            sock = _to_solid(sock_obj)
            sock_placed = sock.translate([spec.width / 2.0, wt / 2.0, half_h])

            lock_obj = SnapLock(
                thick=wt,
                snaplen=catch_w,
                snapdiam=snap_diam,
                foldangle=180,
            )
            lock = _to_solid(lock_obj)
            lock_placed = lock.translate(
                [spec.width / 2.0, lid_origin_y + spec.length - wt / 2.0, half_h]
            )
            monolithic = monolithic | sock_placed | lock_placed

        from pyboxbuilder.box.features import apply_stackable_body

        return apply_stackable_body(monolithic, spec)

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid | None:
        """Return None since PRINT_IN_PLACE_HINGE is a monolithic 1-piece print."""
        return None
