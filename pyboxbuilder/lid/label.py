# SPDX-License-Identifier: Apache-2.0
"""Label generation — framed, frameless, and diagonal text.

Everything here is built in the lid's own frame: (0, 0) is the lid's lower-left
corner and z = 0 is the face the label sits on, so a caller only has to move the
result onto the lid's top.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyboxbuilder.enums import LabelMode, LabelShape
from pyboxbuilder.lid.builder import BORDER_MARGIN_MM, MAX_TEXT_HEIGHT_MM

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid

TEXT_HEIGHT_MM = 0.6
"""How far the text stands off the face it is written on."""

BACKING_HEIGHT_MM = 0.4
"""Thickness of the framed backing plate the text sits on."""

HATCH_WIDTH_MM = 2.0
"""Width of a hatching line."""

LABEL_BORDER_MM = 1.5
"""Default outer border width of the label backing plate."""

LABEL_TEXT_GAP_MM = 1.5
"""Default clearance around the highest and longest text edges inside the border."""


@dataclass(frozen=True)
class Label:
    """A built label, split by the colour each part prints in.

    Keeping the parts separate is what lets the multi-material pass inlay each
    in its own colour while the single-colour pass fuses them.

    Three parts, and only two of them are coloured. The **plate** is the box's
    own material — it is never cut, so nothing is inlaid into it (FR-022) —
    which is why it is here only to say where the label sits, not what to print.
    """

    text: Bosl2Solid
    """The lettering. Inlaid in the text colour, black by default."""
    hatching: Bosl2Solid | None = None
    """Framed mode only — the striped grid behind the text, inlaid light grey."""
    plate: Bosl2Solid | None = None
    """Framed mode only — the area the label occupies.

    Not a coloured part — it stays lid material. Carried so the pattern knows
    what to keep clear of and the single-colour pass knows what to engrave.
    """
    frame: Bosl2Solid | None = None
    """Framed mode only — the outer border ring around the label perimeter."""
    background: Bosl2Solid | None = None
    """Framed mode with solid background only — the interior plaque inside the border."""

    @property
    def backing(self) -> Bosl2Solid | None:
        """The plate and its striped grid, as one solid."""
        if self.plate is None:
            return self.hatching
        return self.plate if self.hatching is None else self.plate | self.hatching

    def combined(self) -> Bosl2Solid:
        """Return every part of the label fused into one solid."""
        backing = self.backing
        return self.text if backing is None else backing | self.text


NOMINAL_SIZE_MM = 10.0
"""Cap height the text is first set at, before being measured and scaled."""

FONT = "Liberation Sans:style=Bold"

LINE_SPACING_FACTOR = 1.35
"""Line-to-line vertical baseline spacing multiplier relative to cap height."""


def _set_text(text: str, diagonal: bool, width: float, length: float) -> Bosl2Solid:
    """Extrude the label text at the nominal size, centered line-by-line and rotated if diagonal."""
    from pybosl2 import text as bosl2_text

    from pyboxbuilder.compartments.element import union_all

    lines = text.splitlines()
    if len(lines) <= 1:
        line = lines[0] if lines else text
        solid = bosl2_text(text=line, size=NOMINAL_SIZE_MM, font=FONT).linear_extrude(
            height=TEXT_HEIGHT_MM
        )
    else:
        line_step = NOMINAL_SIZE_MM * LINE_SPACING_FACTOR
        parts: list[Bosl2Solid] = []
        for idx, line in enumerate(lines):
            if not line.strip():
                continue
            part = bosl2_text(text=line, size=NOMINAL_SIZE_MM, font=FONT).linear_extrude(
                height=TEXT_HEIGHT_MM
            )
            pb = part.bounds()
            pcx = float(pb.center[0]) if hasattr(pb, "center") else float(pb[0][0])
            parts.append(part.translate([-pcx, -idx * line_step, 0.0]))
        solid = union_all(parts) if parts else bosl2_text(
            text=text, size=NOMINAL_SIZE_MM, font=FONT
        ).linear_extrude(height=TEXT_HEIGHT_MM)

    if diagonal:
        sb = solid.bounds()
        scx = float(sb.center[0]) if hasattr(sb, "center") else float(sb[0][0])
        scy = float(sb.center[1]) if hasattr(sb, "center") else float(sb[0][1])
        solid = solid.translate([-scx, -scy, 0.0]).rotate(
            [0.0, 0.0, math.degrees(math.atan2(length, width))]
        )
    return solid


def text_height_for(
    width: float,
    length: float,
    text: str,
    border_margin_mm: float = BORDER_MARGIN_MM,
    diagonal: bool = False,
    label_mode: LabelMode = LabelMode.FRAMED,
    label_border_mm: float = LABEL_BORDER_MM,
    label_text_gap_mm: float = LABEL_TEXT_GAP_MM,
    max_text_height_mm: float | None = MAX_TEXT_HEIGHT_MM,
) -> float:
    """Cap height the label text will be set at, in mm.

    Measured rather than estimated. Guessing the width from the character count
    is off by enough to matter — "Cards" at the guessed size came out 102mm wide
    on a 100mm lid — because the advance per glyph depends on the font and on
    which letters they are.
    """
    label_w = width - 2 * border_margin_mm
    label_l = length - 2 * border_margin_mm
    if label_mode is LabelMode.FRAMED:
        pad = label_border_mm + label_text_gap_mm
        label_w = max(label_w - 2 * pad, 0.0)
        label_l = max(label_l - 2 * pad, 0.0)

    if label_w <= 0 or label_l <= 0 or not text or not text.strip():
        return 0.0

    is_vertical = (length > width) and not diagonal
    target_w = label_l if is_vertical else label_w
    target_l = label_w if is_vertical else label_l

    b = _set_text(text, diagonal, width, length).bounds()
    set_w = float(b.size[0]) if hasattr(b, "size") else float(b[1][0])
    set_l = float(b.size[1]) if hasattr(b, "size") else float(b[1][1])
    if set_w <= 0 or set_l <= 0:
        return 0.0
    raw = NOMINAL_SIZE_MM * min(target_w / set_w, target_l / set_l)
    return min(raw, max_text_height_mm) if max_text_height_mm is not None else raw


def build_label(
    width: float,
    length: float,
    thickness: float,
    text: str,
    label_mode: LabelMode = LabelMode.FRAMED,
    diagonal: bool = False,
    min_text_height_mm: float = 4.0,
    border_margin_mm: float = BORDER_MARGIN_MM,
    label_border_mm: float | None = None,
    label_text_gap_mm: float | None = None,
    label_rounding_mm: float | None = None,
    center_x: float | None = None,
    center_y: float | None = None,
    max_text_height_mm: float | None = MAX_TEXT_HEIGHT_MM,
    solid_background: bool = False,
    label_shape: LabelShape = LabelShape.RECT,
) -> Label | None:
    """Build a label for a lid face, or None if it would be illegible.

    Args:
        width: Lid width in mm.
        length: Lid length in mm.
        thickness: Lid thickness in mm — unused for the geometry, kept so
            callers can pass the whole lid spec through.
        text: The label text.
        label_mode: Framed adds a backing plate and hatching; frameless is
            text alone.
        diagonal: Run the text corner to corner instead of along the width.
        min_text_height_mm: Skip the label below this cap height (FR-023).
        border_margin_mm: Margin kept clear at the lid edges.
        label_border_mm: Solid outer border width of the backing plate.
        label_text_gap_mm: Gap between text and inside of the border.
        label_rounding_mm: Corner rounding radius of the backing plate in mm.
        center_x: Explicit X center for the label in the face frame (defaults to width / 2).
        center_y: Explicit Y center for the label in the face frame (defaults to length / 2).
        max_text_height_mm: Maximum cap height for the label text in mm.
        solid_background: Keep the framed label's interior solid rather than
            cutting diagonal hatching slots.
        label_shape: Plaque silhouette for framed labels (defaults to ``LabelShape.RECT``).

    Returns:
        A `Label`, or None when the text would come out under the minimum.

    """
    from pyboxbuilder.box.shell import corner

    border = label_border_mm if label_border_mm is not None else LABEL_BORDER_MM
    gap = label_text_gap_mm if label_text_gap_mm is not None else LABEL_TEXT_GAP_MM
    pad = border + gap

    label_w = width - 2 * border_margin_mm
    label_l = length - 2 * border_margin_mm
    if label_w <= 0 or label_l <= 0 or not text or not text.strip():
        return None

    size = text_height_for(
        width,
        length,
        text,
        border_margin_mm,
        diagonal,
        label_mode,
        border,
        gap,
        max_text_height_mm=max_text_height_mm,
    )
    if size < min_text_height_mm:
        return None

    # Set at the nominal size and scale to fit, so the result is exactly as
    # large as the label area allows whatever the font does.
    solid = _set_text(text, diagonal, width, length)
    is_vertical = (length > width) and not diagonal
    if is_vertical:
        solid = solid.rotate([0.0, 0.0, 90.0])
    scale = size / NOMINAL_SIZE_MM
    solid = solid.scale([scale, scale, 1.0])

    # `text` sets its own origin from the baseline, so centre it by measurement
    # rather than assuming where it landed.
    b = solid.bounds()
    cx, cy = (float(b.center[0]), float(b.center[1])) if hasattr(b, "center") else (float(b[0][0]), float(b[0][1]))
    tw, tl = (float(b.size[0]), float(b.size[1])) if hasattr(b, "size") else (float(b[1][0]), float(b[1][1]))
    tx = center_x if center_x is not None else width / 2
    ty = center_y if center_y is not None else length / 2
    solid = solid.translate([tx - cx, ty - cy, 0.0])

    if label_mode is LabelMode.FRAMELESS:
        return Label(text=solid)

    # Framed: a backing plaque behind the text. It hugs the text rather than
    # filling the label area, so a lid can carry both a frame and a through-hole
    # pattern — a plate the size of the whole area would simply cover the pattern up.
    b = solid.bounds()
    tcx, tcy = (float(b.center[0]), float(b.center[1])) if hasattr(b, "center") else (float(b[0][0]), float(b[0][1]))
    tw, tl = (float(b.size[0]), float(b.size[1])) if hasattr(b, "size") else (float(b[1][0]), float(b[1][1]))
    rounding_val = label_rounding_mm if label_rounding_mm is not None else 5.0

    if label_shape is not LabelShape.RECT:
        return _build_decorative_label(
            text_solid=solid,
            tcx=tcx,
            tcy=tcy,
            tw=tw,
            tl=tl,
            label_w=label_w,
            label_l=label_l,
            is_vertical=is_vertical,
            border=border,
            gap=gap,
            rounding=rounding_val,
            solid_background=solid_background,
            shape=label_shape,
        )

    plate_w = min(tw + 2 * pad, label_w)
    plate_l = min(tl + 2 * pad, label_l)
    plate_x = tcx - plate_w / 2
    plate_y = tcy - plate_l / 2

    from pybosl2 import cuboid

    from pyboxbuilder.rounding import vertical_edges

    plate_solid = cuboid([plate_w, plate_l, BACKING_HEIGHT_MM], rounding=rounding_val, edges=vertical_edges())
    plate = corner(plate_solid, [plate_w, plate_l, BACKING_HEIGHT_MM], at=(plate_x, plate_y, 0.0))
    clip_cut = _build_clip_solid(
        plate_w,
        plate_l,
        border=border,
        rounding=rounding_val,
        text_gap=gap,
        height=BACKING_HEIGHT_MM + 2.0,
    )
    frame_ring = corner(
        plate_solid - clip_cut if clip_cut is not None else plate_solid,
        [plate_w, plate_l, BACKING_HEIGHT_MM],
        at=(plate_x, plate_y, 0.0),
    )
    if solid_background:
        clip_solid = _build_clip_solid(
            plate_w,
            plate_l,
            border=border,
            rounding=rounding_val,
            text_gap=gap,
        )
        bg_solid = (
            corner(clip_solid, [plate_w, plate_l, BACKING_HEIGHT_MM], at=(plate_x, plate_y, 0.0))
            if clip_solid is not None
            else None
        )
        return Label(
            text=solid,
            hatching=None,
            plate=plate,
            frame=frame_ring,
            background=bg_solid - solid if bg_solid is not None else None,
        )

    raw_hatching = _build_hatching(plate_w, plate_l, border=border, rounding=rounding_val, text_gap=gap)
    hatching = (
        corner(raw_hatching, [plate_w, plate_l, BACKING_HEIGHT_MM], at=(plate_x, plate_y, 0.0))
        if raw_hatching is not None
        else None
    )
    # The striped grid stops at the lettering: the two are inlaid side by side
    # into one face, so a stripe running under a glyph would be competing with
    # it for the same top layer.
    return Label(
        text=solid,
        hatching=hatching - solid if hatching is not None else None,
        plate=plate,
        frame=frame_ring,
    )


def _build_clip_solid(
    width: float,
    length: float,
    border: float = 1.5,
    rounding: float = 5.0,
    text_gap: float | None = None,
    height: float = BACKING_HEIGHT_MM,
) -> Bosl2Solid | None:
    """Interior cutout cuboid inside the label frame's outer border."""
    from pybosl2 import cuboid

    from pyboxbuilder.rounding import vertical_edges

    clip_w = max(width - 2 * border, 0.0)
    clip_l = max(length - 2 * border, 0.0)
    if clip_w <= 0.0 or clip_l <= 0.0:
        return None
    clip_rounding = max(rounding - border, 0.0)
    if text_gap is not None:
        max_safe_rounding = max(0.0, max(0.0, text_gap) * (2.0 + math.sqrt(2.0)) - 0.1)
        clip_rounding = min(clip_rounding, max_safe_rounding)
    clip_rounding = min(clip_rounding, max(0.0, min(clip_w, clip_l) / 2.0 - 0.01))
    return cuboid([clip_w, clip_l, height], rounding=clip_rounding, edges=vertical_edges())


def _build_hatching(
    width: float,
    length: float,
    spacing: float = 4.0,
    border: float = 1.5,
    rounding: float = 5.0,
    text_gap: float | None = None,
) -> Bosl2Solid | None:
    """Diagonal hatching lines, centred on the origin and clipped to the area.

    The lines are cropped to the label rectangle so the hatching cannot spill
    past the backing plate it decorates. Corner rounding is bounded so the solid
    border never encroaches into the text bounding box.
    """
    from pybosl2 import cuboid

    clip_solid = _build_clip_solid(width, length, border=border, rounding=rounding, text_gap=text_gap)
    if clip_solid is None:
        return None

    diagonal = math.hypot(width, length)
    angle = 45.0
    count = max(int(diagonal / spacing), 1)

    lines = []
    for i in range(count + 1):
        offset = i * spacing - diagonal / 2
        line = cuboid([diagonal, HATCH_WIDTH_MM, BACKING_HEIGHT_MM])
        lines.append(line.translate([0.0, offset, 0.0]).rotate([0.0, 0.0, angle]))

    from pyboxbuilder.compartments.element import union_all

    hatching = union_all(lines)
    assert hatching is not None
    return hatching & clip_solid


def _centered_cuboid(
    width: float,
    length: float,
    height: float,
    rounding: float = 0.0,
) -> Bosl2Solid:
    """Create a cuboid centered at (0, 0) in XY with base at z=0."""
    from pybosl2 import cuboid

    from pyboxbuilder.rounding import vertical_edges

    r = max(0.0, min(rounding, min(width, length) / 2.0 - 0.01))
    solid = (
        cuboid([width, length, height], rounding=r, edges=vertical_edges())
        if r > 0.01
        else cuboid([width, length, height])
    )
    return solid.translate([0.0, 0.0, height / 2.0])


def _chamfered_prism(width: float, length: float, chamfer: float, height: float) -> Bosl2Solid:
    """Extrude an 8-vertex octagonal prism with 45° corner chamfers, base at z=0."""
    from pybosl2 import Path2D, polygon

    hw = width / 2.0
    hl = length / 2.0
    c = max(0.0, min(chamfer, hw - 0.05, hl - 0.05))
    pts = [
        (-hw + c, -hl),
        (hw - c, -hl),
        (hw, -hl + c),
        (hw, hl - c),
        (hw - c, hl),
        (-hw + c, hl),
        (-hw, hl - c),
        (-hw, -hl + c),
    ]
    return polygon(Path2D(pts)).linear_extrude(height=height)


def _hex_lozenge_prism(width: float, length: float, tip: float, height: float) -> Bosl2Solid:
    """Extrude a pointed elongated hexagon centered at (0, 0) with base at z=0."""
    from pybosl2 import Path2D, polygon

    hw = width / 2.0
    hl = length / 2.0
    t = max(0.0, min(tip, hw - 0.2))
    pts = [
        (-hw, 0.0),
        (-hw + t, -hl),
        (hw - t, -hl),
        (hw, 0.0),
        (hw - t, hl),
        (-hw + t, hl),
    ]
    return polygon(Path2D(pts)).linear_extrude(height=height)


def _ribbon_prism(width: float, length: float, notch: float, height: float) -> Bosl2Solid:
    """Extrude a swallowtail-notched banner centered at (0, 0) with base at z=0."""
    from pybosl2 import Path2D, polygon

    hw = width / 2.0
    hl = length / 2.0
    n = max(0.0, min(notch, hw - 0.5))
    pts = [
        (-hw, -hl),
        (hw, -hl),
        (hw - n, 0.0),
        (hw, hl),
        (-hw, hl),
        (-hw + n, 0.0),
    ]
    return polygon(Path2D(pts)).linear_extrude(height=height)


def _notched_prism(width: float, length: float, notch_radius: float, height: float) -> Bosl2Solid:
    """Extrude a rectangle with concave quarter-circle corner notches, base at z=0."""
    from pybosl2 import cylinder

    from pyboxbuilder.compartments.element import union_all

    base = _centered_cuboid(width, length, height)
    nr = max(0.0, min(notch_radius, min(width, length) / 2.0 - 0.2))
    if nr <= 0.1:
        return base
    hw = width / 2.0
    hl = length / 2.0
    corners = union_all(
        [
            cylinder(height=height + 2.0, radius=nr).translate([sx * hw, sy * hl, height / 2.0])
            for sx in (-1.0, 1.0)
            for sy in (-1.0, 1.0)
        ]
    )
    assert corners is not None
    return base - corners


def _build_shape_parts(
    shape: LabelShape,
    rtw: float,
    rtl: float,
    avail_rw: float,
    avail_rl: float,
    border: float,
    gap: float,
    rounding: float,
) -> tuple[Bosl2Solid, Bosl2Solid | None, Bosl2Solid | None, float, float]:
    """Build (plate, frame, background, rw, rl) in local reading coordinates with base at z=0."""
    h = BACKING_HEIGHT_MM
    cut_h = h + 2.0
    pad = border + gap
    base_rw = rtw + 2.0 * pad
    base_rl = rtl + 2.0 * pad

    def _fit_rw(extra_per_side: float) -> float:
        return min(base_rw + 2.0 * max(0.0, extra_per_side), avail_rw)

    if shape is LabelShape.PILL:
        rl = min(base_rl + 1.0, avail_rl)
        rw = _fit_rw(rl * 0.28)
        r_out = min(rl / 2.0 - 0.01, rw / 2.0 - 0.01)
        plate = _centered_cuboid(rw, rl, h, rounding=r_out)
        iw, il = rw - 2.0 * border, rl - 2.0 * border
        if iw > 0.5 and il > 0.5:
            r_in = max(0.0, min(il / 2.0 - 0.01, iw / 2.0 - 0.01))
            bg = _centered_cuboid(iw, il, h, rounding=r_in)
            cut = _centered_cuboid(iw, il, cut_h, rounding=r_in).translate([0.0, 0.0, -1.0])
            return plate, plate - cut, bg, rw, rl
        return plate, plate, None, rw, rl

    if shape is LabelShape.CHAMFERED:
        rl = min(base_rl + 1.0, avail_rl)
        c_est = min(rl * 0.28, 6.0)
        rw = _fit_rw(c_est * 0.65)
        c = min(rl * 0.28, rw * 0.18, 6.0)
        plate = _chamfered_prism(rw, rl, c, h)
        iw, il = rw - 2.0 * border, rl - 2.0 * border
        if iw > 0.5 and il > 0.5:
            ic = max(0.0, c - border * (2.0 - math.sqrt(2.0)))
            bg = _chamfered_prism(iw, il, ic, h)
            cut = _chamfered_prism(iw, il, ic, cut_h).translate([0.0, 0.0, -1.0])
            return plate, plate - cut, bg, rw, rl
        return plate, plate, None, rw, rl

    if shape is LabelShape.HEXAGON:
        rl = min(base_rl + 1.0, avail_rl)
        tip = min(rl * 0.42, 10.0)
        rw = _fit_rw(tip * 0.85)
        tip = min(tip, max(1.0, rw * 0.22))
        plate = _hex_lozenge_prism(rw, rl, tip, h)
        hl = rl / 2.0
        il = rl - 2.0 * border
        edge_len = math.hypot(tip, hl)
        dx_tip = border * edge_len / hl if hl > 0.1 else border
        iw = rw - 2.0 * dx_tip
        if iw > 1.0 and il > 0.5:
            x_shoulder = rw / 2.0 - (tip * (hl - border) + border * edge_len) / hl
            i_tip = max(0.2, (iw / 2.0) - x_shoulder)
            bg = _hex_lozenge_prism(iw, il, i_tip, h)
            cut = _hex_lozenge_prism(iw, il, i_tip, cut_h).translate([0.0, 0.0, -1.0])
            return plate, plate - cut, bg, rw, rl
        return plate, plate, None, rw, rl

    if shape is LabelShape.NOTCHED:
        rl = min(base_rl + 1.0, avail_rl)
        nr = min(rl * 0.24, 4.5)
        rw = _fit_rw(nr * 0.7)
        nr = min(nr, rw * 0.14)
        plate = _notched_prism(rw, rl, nr, h)
        iw, il = rw - 2.0 * border, rl - 2.0 * border
        if iw > 1.0 and il > 1.0:
            # Concentric corner cylinders at (±rw/2, ±rl/2) with radius nr + border
            # keep an exact uniform border thickness around the concave arcs.
            from pybosl2 import cylinder

            from pyboxbuilder.compartments.element import union_all

            hw, hl = rw / 2.0, rl / 2.0
            corner_cuts = union_all(
                [
                    cylinder(height=cut_h + 2.0, radius=nr + border).translate(
                        [sx * hw, sy * hl, h / 2.0]
                    )
                    for sx in (-1.0, 1.0)
                    for sy in (-1.0, 1.0)
                ]
            )
            assert corner_cuts is not None
            bg = _centered_cuboid(iw, il, h) - corner_cuts
            cut = _centered_cuboid(iw, il, cut_h).translate([0.0, 0.0, -1.0]) - corner_cuts
            return plate, plate - cut, bg, rw, rl
        return plate, plate, None, rw, rl

    if shape is LabelShape.RIBBON:
        rl = min(base_rl + 1.0, avail_rl)
        notch = min(rl * 0.28, 6.0)
        rw = _fit_rw(notch + 1.0)
        notch = min(notch, max(1.0, rw * 0.16))
        plate = _ribbon_prism(rw, rl, notch, h)
        hl = rl / 2.0
        il = rl - 2.0 * border
        edge_len = math.hypot(notch, hl)
        x_tip_in = rw / 2.0 - notch - (border * edge_len / hl if hl > 0.1 else border)
        x_corner_in = rw / 2.0 - (border * (notch + edge_len) / hl if hl > 0.1 else border)
        if x_tip_in > 0.5 and x_corner_in > x_tip_in + 0.2 and il > 0.5:
            iw = 2.0 * x_corner_in
            i_notch = x_corner_in - x_tip_in
            bg = _ribbon_prism(iw, il, i_notch, h)
            cut = _ribbon_prism(iw, il, i_notch, cut_h).translate([0.0, 0.0, -1.0])
            return plate, plate - cut, bg, rw, rl
        return plate, plate, None, rw, rl

    if shape is LabelShape.DOUBLE_FRAME:
        ring_gap = min(1.2, max(0.8, border * 0.8))
        b_in = min(0.9, max(0.7, border * 0.6))
        extra = ring_gap + b_in
        rl = min(base_rl + 2.0 * extra, avail_rl)
        rw = _fit_rw(extra + 1.0)
        r0 = min(rounding, min(rw, rl) / 2.0 - 0.01)
        plate = _centered_cuboid(rw, rl, h, rounding=r0)

        w1, l1 = rw - 2.0 * border, rl - 2.0 * border
        if w1 <= 0.5 or l1 <= 0.5:
            return plate, plate, None, rw, rl
        r1 = max(0.0, r0 - border)
        cut1 = _centered_cuboid(w1, l1, cut_h, rounding=r1).translate([0.0, 0.0, -1.0])
        outer_ring = plate - cut1

        w2, l2 = w1 - 2.0 * ring_gap, l1 - 2.0 * ring_gap
        w3, l3 = w2 - 2.0 * b_in, l2 - 2.0 * b_in
        if w3 > 0.5 and l3 > 0.5:
            r2 = max(0.0, r1 - ring_gap)
            r3 = max(0.0, r2 - b_in)
            ring2_outer = _centered_cuboid(w2, l2, h, rounding=r2)
            cut3 = _centered_cuboid(w3, l3, cut_h, rounding=r3).translate([0.0, 0.0, -1.0])
            inner_ring = ring2_outer - cut3
            frame = outer_ring | inner_ring
            bg = _centered_cuboid(w1, l1, h, rounding=r1) - (
                _centered_cuboid(w2, l2, cut_h, rounding=r2).translate([0.0, 0.0, -1.0]) - cut3
            )
            return plate, frame, bg, rw, rl
        bg = _centered_cuboid(w1, l1, h, rounding=r1)
        return plate, outer_ring, bg, rw, rl

    # LabelShape.UNDERLINE: clean minimalist header with a bold pill accent bar underneath
    bar_h = max(border, 1.6)
    bar_gap = max(gap * 0.85, 1.2)
    bar_w = min(rtw + 2.0 * gap, max(rtw, avail_rw - 2.0 * gap))
    bar_y = -rtl / 2.0 - bar_gap - bar_h / 2.0
    top_y = rtl / 2.0 + gap + border
    bot_y = bar_y - bar_h / 2.0 - gap
    rl = min(top_y - bot_y, avail_rl)
    rw = min(max(rtw, bar_w) + 2.0 * (gap + border), avail_rw)
    plate_cy = (top_y + bot_y) / 2.0
    plate_r = min(rounding, min(rw, rl) / 2.0 - 0.01)
    plate = _centered_cuboid(rw, rl, h, rounding=plate_r).translate([0.0, plate_cy, 0.0])
    bar = _centered_cuboid(bar_w, bar_h, h, rounding=bar_h / 2.0 - 0.01).translate([0.0, bar_y, 0.0])
    bar_cut = _centered_cuboid(bar_w, bar_h, cut_h, rounding=bar_h / 2.0 - 0.01).translate([0.0, bar_y, -1.0])
    bg = plate - bar_cut
    return plate, bar, bg, rw, rl


def _build_decorative_label(
    *,
    text_solid: Bosl2Solid,
    tcx: float,
    tcy: float,
    tw: float,
    tl: float,
    label_w: float,
    label_l: float,
    is_vertical: bool,
    border: float,
    gap: float,
    rounding: float,
    solid_background: bool,
    shape: LabelShape,
) -> Label:
    """Build a framed label using one of the decorative :class:`LabelShape` plaques."""
    rtw, rtl = (tl, tw) if is_vertical else (tw, tl)
    avail_rw, avail_rl = (label_l, label_w) if is_vertical else (label_w, label_l)

    plate_local, frame_local, bg_local, rw, rl = _build_shape_parts(
        shape=shape,
        rtw=rtw,
        rtl=rtl,
        avail_rw=avail_rw,
        avail_rl=avail_rl,
        border=border,
        gap=gap,
        rounding=rounding,
    )

    def _place(s: Bosl2Solid | None) -> Bosl2Solid | None:
        if s is None:
            return None
        if is_vertical:
            s = s.rotate([0.0, 0.0, 90.0])
        return s.translate([tcx, tcy, 0.0])

    plate = _place(plate_local)
    frame = _place(frame_local)

    if solid_background or shape is LabelShape.UNDERLINE:
        bg = _place(bg_local)
        return Label(
            text=text_solid,
            hatching=None,
            plate=plate,
            frame=frame,
            background=bg - text_solid if bg is not None else None,
        )

    # Explicit opt-in to diagonal through-hole hatching inside a decorative shape
    hatching_local: Bosl2Solid | None = None
    if bg_local is not None:
        from pybosl2 import cuboid

        from pyboxbuilder.compartments.element import union_all

        diagonal = math.hypot(rw, rl)
        spacing = 4.0
        count = max(int(diagonal / spacing), 1)
        bars = [
            cuboid([diagonal, HATCH_WIDTH_MM, BACKING_HEIGHT_MM])
            .translate([0.0, i * spacing - diagonal / 2.0, BACKING_HEIGHT_MM / 2.0])
            .rotate([0.0, 0.0, 45.0])
            for i in range(count + 1)
        ]
        bars_union = union_all(bars)
        if bars_union is not None:
            hatching_local = bars_union & bg_local

    hatching = _place(hatching_local)
    return Label(
        text=text_solid,
        hatching=hatching - text_solid if hatching is not None else None,
        plate=plate,
        frame=frame,
    )
