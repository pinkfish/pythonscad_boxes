# SPDX-License-Identifier: Apache-2.0
"""InsetHingeBox — print-in-place inset-hinge box type based on hinge_box.scad."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pybosl2.constants import Anchor
from pybosl2.shapes3d import cuboid, cylinder, wedge

from pyboxbuilder.box.base import BoxTypeBase, Interior
from pyboxbuilder.box.registry import register_box
from pyboxbuilder.box.shell import block, body_rounding
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders.inset_hinge import InsetHingeBoxBuilder
from pyboxbuilder.enums import BoxType, CatchType
from pyboxbuilder.precision import kwargs as precision_kwargs

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid


def _hinge_cone(r: float, offset: float) -> Bosl2Solid:
    """Build the 45° hollow conical pivot shell (HingeCone in hinge_box.scad)."""
    outer = cylinder(height=r, radius1=r, radius2=0.0, **precision_kwargs()).translate([
        0.0,
        0.0,
        r / 2.0,
    ])
    inner_r = max(0.1, r - offset)
    inner = cylinder(height=inner_r, radius1=inner_r, radius2=0.0, **precision_kwargs()).translate([
        0.0,
        0.0,
        inner_r / 2.0 - 0.01,
    ])
    return outer - inner


def _hinge_line_with_spacing_and_num(
    diameter: float,
    num: int,
    spacing: float,
    offset: float,
    spin: float = 90.0,
    gap: float | None = None,
) -> Bosl2Solid:
    """Build a single conical print-in-place hinge line (HingeLineWithSpacingAndNum in hinge_box.scad)."""
    length = num * spacing
    r = diameter / 2.0
    effective_gap = offset * 2.0 if gap is None else max(offset * 2.0, gap)

    # Base cylinder from z = 0 to z = length
    core = cylinder(height=length, radius=r, **precision_kwargs()).translate([0.0, 0.0, length / 2.0])

    # Subtract conical separations and odd-segment outer clearance rings
    cuts: list[Bosl2Solid] = []
    for i in range(1, num + 1):
        cone = _hinge_cone(r - 0.01, offset)
        if i % 2 == 1:
            cone = cone.mirror([0, 0, 1])
        cuts.append(cone.translate([0.0, 0.0, spacing * i]))

        if i % 2 == 1:
            ring_outer = cylinder(
                height=spacing + 0.04,
                radius=diameter,
                **precision_kwargs(),
            ).translate([0.0, 0.0, spacing * i + spacing / 2.0])
            ring_inner = cylinder(
                height=spacing + 0.06,
                radius=max(0.2, r - offset),
                **precision_kwargs(),
            ).translate([0.0, 0.0, spacing * i + spacing / 2.0])
            cuts.append(ring_outer - ring_inner)

    for c in cuts:
        core = core - c

    # Add alternating link arms and mounting brackets for i = 0 .. num
    additions: list[Bosl2Solid] = [core]
    for i in range(num + 1):
        z_base = spacing * i
        if i % 2 == 1:
            c_seg = cylinder(
                height=max(0.2, spacing - offset),
                radius=r,
                **precision_kwargs(),
            ).translate([0.0, 0.0, z_base + spacing / 2.0])
            arm_h = r + effective_gap + 0.01
            arm_seg = (
                cuboid(
                    [spacing - offset, diameter, arm_h],
                    anchor=Anchor.BOTTOM,
                )
                .rotate([0, 90, 0])
                .translate([0.0, 0.0, z_base + spacing / 2.0])
            )
            spun = (c_seg | arm_seg).rotate([0, 0, spin])

            b_outer = cuboid([1.0 + r, diameter, spacing + offset * 3.0])
            b_cyl = cylinder(
                height=length,
                radius=r + offset,
                **precision_kwargs(),
            ).translate([r / 2.0 + offset, 0.0, length / 2.0 - (spacing / 4.0 + r)])
            b_back = cuboid([1.0 + r, diameter, spacing + offset * 3.0]).translate([
                offset * 1.5,
                r,
                0.0,
            ])
            bracket = (b_outer - b_cyl - b_back).translate([
                -r / 2.0 - offset * 1.5,
                0.0,
                z_base + spacing / 2.0,
            ])
            additions.append(spun | bracket)
        else:
            b_chamfer = cuboid(
                [1.0, diameter, spacing + offset * 3.0],
                chamfer=min(0.4, offset * 2.0),
                edges=[Anchor.TOP + Anchor.RIGHT, Anchor.BOTTOM + Anchor.RIGHT],
            ).translate([-r - offset * 1.5, 0.0, z_base + spacing / 2.0])

            b_block = block(
                [r + offset, diameter, spacing],
                at=(-r - offset, -r, z_base),
            )
            b_bore = cylinder(
                height=spacing * 4.0,
                radius=max(0.2, r - 0.01),
                **precision_kwargs(),
            ).translate([0.0, 0.0, z_base + spacing * 2.0 - offset * 2.0])
            additions.append(b_chamfer | (b_block - b_bore))

    total = additions[0]
    for a in additions[1:]:
        total = total | a

    shifted = total.translate([0.0, 0.0, -length / 2.0])
    bound_span = max(diameter * 2.0, diameter + effective_gap * 2.0)
    bound_box = cuboid([bound_span, bound_span, length])
    return (bound_box & shifted).rotate([0, 270, 0])


def _inset_hinge(
    length: float,
    width: float,
    diameter: float,
    offset: float,
) -> Bosl2Solid:
    """Build the double-barrel print-in-place inset hinge assembly without a center sliver bar."""
    num = max(2, round(length / diameter))
    spacing = length / num
    gap = max(0.0, width - diameter * 2.0)

    line1 = _hinge_line_with_spacing_and_num(
        diameter=diameter,
        offset=offset,
        spin=90.0,
        num=num,
        spacing=spacing,
        gap=gap,
    ).translate([0.0, diameter / 2.0, 0.0])

    line2 = (
        _hinge_line_with_spacing_and_num(
            diameter=diameter,
            offset=offset,
            spin=90.0,
            num=num,
            spacing=spacing,
            gap=gap,
        )
        .mirror([0, 1, 0])
        .translate([0.0, width - diameter / 2.0, 0.0])
    )

    return (line1 | line2).translate([0.0, -width / 2.0, 0.0])


def _make_lid_tab(
    length: float,
    height: float,
    lid_thickness: float,
    prism_width: float,
    wall_thickness: float,
    offset: float = 0.0,
) -> Bosl2Solid:
    """Build the cantilevered latch tab or its clearance cutout (MakeLidTab in lids_base.scad)."""
    L = length + offset * 2.0
    wt = wall_thickness
    lt = lid_thickness
    h = height

    base_part = block(
        [L, wt + offset * 2.0, lt + offset * 2.0],
        at=(-offset, -offset, -offset),
    )
    stalk = block(
        [L, wt / 2.0 + offset * 2.0, max(0.2, h - wt + 0.1) + offset * 2.0],
        at=(-offset, -offset, -offset),
    )

    barb = wedge(
        size=[
            L,
            wt * prism_width + offset * 2.0,
            wt + offset * 2.0,
        ],
        anchor=Anchor.BOTTOM + Anchor.FRONT + Anchor.LEFT,
    ).translate([-offset, -offset, h - wt - offset])

    return (base_part | stalk | barb).mirror([0, 0, 1])


@register_box(BoxType.INSET_HINGE, builder=InsetHingeBoxBuilder)
class InsetHingeBox(BoxTypeBase):
    """Print-in-place inset-hinge box based on MakeBoxAndLidWithInsetHinge (hinge_box.scad)."""

    @staticmethod
    def _effective_gap(spec: BoxSpec) -> float:
        """Return the print-in-place bed gap between the two box halves (2 * hinge_offset)."""
        hinge_offset = spec.pip_radial_clearance
        raw_gap = getattr(spec, "pip_gap_mm", 0.0)
        if raw_gap <= 0.0 or abs(raw_gap - 1.0) < 1e-6:
            return hinge_offset * 2.0
        return raw_gap

    @classmethod
    def _hinge_metrics(cls, spec: BoxSpec) -> tuple[float, float, float, float, float]:
        """Return (hinge_diameter, hinge_width, side_gap, hinge_length, hinge_offset)."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        half_h = spec.height / 2.0
        gap = cls._effective_gap(spec)
        hinge_diameter = min(
            2.0 * spec.pip_hinge_radius,
            max(3.0, (spec.width - 2.0 * wt - gap) / 2.5),
            max(3.0, half_h - ft - 0.5),
        )
        hinge_width = hinge_diameter * 2.0 + gap
        side_gap = min(
            getattr(spec, "inset_hinge_side_gap", 3.0),
            spec.length * 0.2,
        )
        hinge_length = max(6.0, spec.length - 2.0 * side_gap)
        hinge_offset = spec.pip_radial_clearance
        return hinge_diameter, hinge_width, side_gap, hinge_length, hinge_offset

    def interior(self, spec: BoxSpec) -> Interior:
        """Return the usable interior volume of the base half clear of the inset hinge."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        half_h = spec.height / 2.0
        _, hinge_width, _, _, _ = self._hinge_metrics(spec)
        inner_w = max(4.0, spec.width - wt - hinge_width)
        inner_l = max(4.0, spec.length - 2.0 * wt)
        inner_h = max(2.0, half_h - ft)
        return Interior(
            width=inner_w,
            length=inner_l,
            height=inner_h,
            origin_x=wt,
            origin_y=wt,
            origin_z=ft,
        )

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Return the monolithic side-by-side print with inset hinge, rim, and latch tab."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        lt = spec.lid_thickness
        half_h = spec.height / 2.0
        gap = self._effective_gap(spec)
        offset = spec.size_spacing
        print_in_place_offset = 0.2
        print_layer_height = 0.2

        hinge_diameter, hinge_width, side_gap, hinge_length, hinge_offset = (
            self._hinge_metrics(spec)
        )
        hinge_sink = max(hinge_offset, gap / 2.0)

        r_body = min(body_rounding(spec), wt, half_h / 3.0)
        outer_edges = [
            Anchor.LEFT + Anchor.FRONT,
            Anchor.RIGHT + Anchor.FRONT,
            Anchor.LEFT + Anchor.BACK,
            Anchor.RIGHT + Anchor.BACK,
            Anchor.BOTTOM,
        ]
        vertical_edges = [
            Anchor.LEFT + Anchor.FRONT,
            Anchor.RIGHT + Anchor.FRONT,
            Anchor.LEFT + Anchor.BACK,
            Anchor.RIGHT + Anchor.BACK,
        ]

        # 1. Base half outer shell & alignment rabbet around top perimeter
        box_half = cuboid(
            [spec.width, spec.length, half_h],
            anchor=Anchor.BOTTOM + Anchor.FRONT + Anchor.LEFT,
            rounding=r_body,
            edges=outer_edges,
        )
        rabbet_outer = cuboid(
            [spec.width - wt, spec.length - wt, wt],
            anchor=Anchor.BOTTOM + Anchor.FRONT + Anchor.LEFT,
            rounding=wt / 2.0,
            edges=vertical_edges,
        ).translate([wt / 2.0, wt / 2.0, half_h - wt / 2.0])
        rabbet_inner = cuboid(
            [
                spec.width - wt * 2.0 - offset * 2.0,
                spec.length - wt * 2.0 - offset * 2.0,
                wt + 1.0,
            ],
            anchor=Anchor.BOTTOM + Anchor.FRONT + Anchor.LEFT,
            rounding=wt / 2.0,
            edges=vertical_edges,
        ).translate([wt + offset, wt + offset, half_h - wt / 2.0 - 0.5])
        box_half = box_half - (rabbet_outer - rabbet_inner)

        # 2. Lid half outer shell (at x = spec.width + gap) & raised alignment rim
        lid_x = spec.width + gap
        lid_half = cuboid(
            [spec.width, spec.length, half_h],
            anchor=Anchor.BOTTOM + Anchor.FRONT + Anchor.LEFT,
            rounding=r_body,
            edges=outer_edges,
        ).translate([lid_x, 0.0, 0.0])

        lid_rim_outer = cuboid(
            [spec.width - wt, spec.length - wt, wt],
            anchor=Anchor.BOTTOM + Anchor.FRONT + Anchor.LEFT,
            rounding=wt / 2.0,
            edges=[
                Anchor.LEFT + Anchor.FRONT,
                Anchor.RIGHT + Anchor.FRONT,
                Anchor.LEFT + Anchor.BACK,
                Anchor.RIGHT + Anchor.BACK,
                Anchor.TOP,
            ],
        ).translate([lid_x + wt / 2.0, wt / 2.0, half_h - wt / 2.0])
        lid_rim_inner = cuboid(
            [
                spec.width - wt * 2.0 - offset * 2.0,
                spec.length - wt * 2.0 - offset * 2.0,
                wt * 4.0,
            ],
            anchor=Anchor.BOTTOM + Anchor.FRONT + Anchor.LEFT,
            rounding=wt / 2.0,
            edges=vertical_edges,
        ).translate([lid_x + wt + offset, wt + offset, half_h - wt * 2.0])
        lid_half = lid_half | (lid_rim_outer - lid_rim_inner)

        shell = box_half | lid_half

        # 3. Interior cavities for base half and lid half
        cav_w = max(4.0, spec.width - wt - hinge_width)
        cav_l = max(4.0, spec.length - 2.0 * wt)
        r_cav = min(wt / 2.0, cav_w / 4.0, cav_l / 4.0)

        if spec.hollow:
            base_cav = cuboid(
                [cav_w, cav_l, half_h + 1.0],
                anchor=Anchor.BOTTOM + Anchor.FRONT + Anchor.LEFT,
                rounding=r_cav,
                edges=outer_edges,
            ).translate([wt, wt, ft])
            shell = shell - base_cav

        # Always hollow the lid half so the lid tray is ready to fold over the base
        lid_cav = cuboid(
            [cav_w, cav_l, half_h + wt],
            anchor=Anchor.BOTTOM + Anchor.FRONT + Anchor.LEFT,
            rounding=r_cav,
            edges=outer_edges,
        ).translate([lid_x + hinge_width, wt, lt])
        shell = shell - lid_cav

        # 4. Cut the recessed hinge pocket and union the InsetHinge
        hinge_pocket = block(
            [
                hinge_width + print_in_place_offset * 2.0 + 0.02,
                hinge_length + print_in_place_offset * 2.0,
                hinge_diameter + 5.0 + hinge_sink + 1.0,
            ],
            at=(
                spec.width - hinge_diameter - 0.01 - print_in_place_offset,
                side_gap - print_in_place_offset,
                half_h - hinge_diameter - print_layer_height - hinge_sink,
            ),
        )
        shell = shell - hinge_pocket

        hinge_asm = (
            _inset_hinge(
                length=hinge_length,
                width=hinge_width,
                diameter=hinge_diameter,
                offset=hinge_offset,
            )
            .rotate([0, 0, 90])
            .translate([
                spec.width + gap / 2.0,
                hinge_length / 2.0 + side_gap,
                half_h - hinge_diameter / 2.0 - hinge_sink,
            ])
        )
        monolithic = shell | hinge_asm

        # 5. Front latch tab on base outer wall (x=0) and matching catch cutout on lid outer wall
        if (
            spec.pip_snap_catch
            and spec.resolved_catch_type(CatchType.WEDGE) != CatchType.NONE
        ):
            tab_length = min(spec.pip_snap_width, spec.length * 0.4)
            tab_height = min(
                getattr(spec, "inset_hinge_tab_height", 6.0),
                max(2.5, half_h - ft - 1.0),
            )
            lid_tab = (
                _make_lid_tab(
                    length=tab_length,
                    height=tab_height,
                    lid_thickness=lt,
                    prism_width=0.75,
                    wall_thickness=wt,
                )
                .mirror([0, 0, 1])
                .rotate([0, 0, 270])
                .translate([
                    0.0,
                    spec.length / 2.0 + tab_length / 2.0,
                    half_h - lt,
                ])
            )
            lid_catch_cut = (
                _make_lid_tab(
                    length=tab_length,
                    height=tab_height,
                    lid_thickness=lt,
                    prism_width=0.75,
                    wall_thickness=wt,
                    offset=offset,
                )
                .mirror([0, 1, 0])
                .rotate([0, 0, 270])
                .translate([
                    spec.width * 2.0 + gap - wt / 2.0,
                    spec.length / 2.0 + tab_length / 2.0,
                    half_h + lt,
                ])
            )
            monolithic = (monolithic | lid_tab) - lid_catch_cut

        from pyboxbuilder.box.features import apply_stackable_body

        return apply_stackable_body(monolithic, spec)

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid | None:
        """Return None since INSET_HINGE is a monolithic 1-piece print."""
        return None
