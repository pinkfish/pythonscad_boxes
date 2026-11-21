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

from pyboxbuilder.enums import LabelFinial, LabelMode, LabelShape
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
    finial: Bosl2Solid | None = None
    """Optional decorative typographic ornament placed underneath the text."""
    image_slot: tuple[float, float, float, float] | None = None
    """Reserved ``(cx, cy, width, length)`` bay inside the plaque for an embedded logo/image."""

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
    label_finial: LabelFinial = LabelFinial.NONE,
    logo_position: str | None = None,
    logo_size_mm: float | None = None,
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
        label_finial: Decorative typographic ornament placed underneath the text.
        logo_position: Optional embedded logo placement inside a framed plaque
            (``"top"``, ``"bottom"``, ``"left"``, or ``"right"``).
        logo_size_mm: Optional target size in mm for the embedded logo bay.

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

    has_logo_slot = logo_position in ("top", "bottom", "left", "right")
    has_finial = label_finial is not LabelFinial.NONE

    if label_mode is LabelMode.FRAMELESS:
        if not has_finial:
            return Label(text=solid)
        rtw_fl, rtl_fl = (tl, tw) if is_vertical else (tw, tl)
        avail_rw_fl = label_l if is_vertical else label_w
        finial_h = max(3.2, min(4.8, rtl_fl * 0.34))
        finial_gap = max(1.4, gap * 0.9)
        finial_w = min(max(rtw_fl * 0.88, 16.0), max(10.0, avail_rw_fl - 2.0 * gap))
        finial_local = _build_finial_solid(label_finial, finial_w, finial_h, BACKING_HEIGHT_MM)
        if finial_local is None:
            return Label(text=solid)
        shift_up = (finial_gap + finial_h) / 2.0
        y_finial = -(rtl_fl + finial_gap) / 2.0
        finial_placed = finial_local.translate([0.0, y_finial, 0.0])
        if is_vertical:
            text_shifted = solid.translate([-shift_up, 0.0, 0.0])
            finial_placed = finial_placed.rotate([0.0, 0.0, 90.0]).translate([tx, ty, 0.0])
        else:
            text_shifted = solid.translate([0.0, shift_up, 0.0])
            finial_placed = finial_placed.translate([tx, ty, 0.0])
        return Label(text=text_shifted, finial=finial_placed)

    # Framed: a backing plaque behind the text. It hugs the text rather than
    # filling the label area, so a lid can carry both a frame and a through-hole
    # pattern — a plate the size of the whole area would simply cover the pattern up.
    b = solid.bounds()
    tcx, tcy = (float(b.center[0]), float(b.center[1])) if hasattr(b, "center") else (float(b[0][0]), float(b[0][1]))
    tw, tl = (float(b.size[0]), float(b.size[1])) if hasattr(b, "size") else (float(b[1][0]), float(b[1][1]))
    rounding_val = label_rounding_mm if label_rounding_mm is not None else 5.0

    if label_shape is not LabelShape.RECT or has_finial or has_logo_slot:
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
            finial=label_finial,
            logo_position=logo_position if has_logo_slot else None,
            logo_size_mm=logo_size_mm,
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

    if shape is LabelShape.RECT:
        rl = min(base_rl, avail_rl)
        rw = min(base_rw, avail_rw)
        r0 = min(rounding, min(rw, rl) / 2.0 - 0.01)
        plate = _centered_cuboid(rw, rl, h, rounding=r0)
        iw, il = rw - 2.0 * border, rl - 2.0 * border
        if iw > 0.5 and il > 0.5:
            r_in = max(0.0, r0 - border)
            bg = _centered_cuboid(iw, il, h, rounding=r_in)
            cut = _centered_cuboid(iw, il, cut_h, rounding=r_in).translate([0.0, 0.0, -1.0])
            return plate, plate - cut, bg, rw, rl
        return plate, plate, None, rw, rl

    if shape is LabelShape.OVAL:
        rl = min(max(base_rl * 1.25, rtl * 1.38 + 2.0 * border), avail_rl)
        rw = min(max(base_rw * 1.25, rtw * 1.38 + 2.0 * border), avail_rw)
        plate = _ellipse_prism(rw / 2.0, rl / 2.0, h)
        irx, iry = rw / 2.0 - border, rl / 2.0 - border
        if irx > 0.5 and iry > 0.5:
            bg = _ellipse_prism(irx, iry, h)
            cut = _ellipse_prism(irx, iry, cut_h).translate([0.0, 0.0, -1.0])
            return plate, plate - cut, bg, rw, rl
        return plate, plate, None, rw, rl

    if shape is LabelShape.SCALLOPED:
        rl = min(base_rl + 2.0, avail_rl)
        s_est = min(rl * 0.24, 5.5)
        rw = _fit_rw(s_est * 0.8)
        s = min(rl * 0.24, rw * 0.14, 5.5)
        plate = _scalloped_prism(rw, rl, s, h)
        if rw - 2.0 * border > 1.0 and rl - 2.0 * border > 1.0 and s > border + 0.3:
            bg = _scalloped_inset_prism(rw, rl, s, border, h)
            cut = _scalloped_inset_prism(rw, rl, s, border, cut_h).translate([0.0, 0.0, -1.0])
            return plate, plate - cut, bg, rw, rl
        return plate, plate, None, rw, rl

    if shape is LabelShape.BRACKET:
        rl = min(base_rl + 2.0, avail_rl)
        ear = min(rl * 0.38, 9.0)
        rw = _fit_rw(ear * 0.9)
        ear = min(ear, max(1.5, rw * 0.22))
        plate = _bracket_prism(rw, rl, ear, h)
        iw, il = rw - 2.0 * border * 1.35, rl - 2.0 * border
        if iw > 1.5 and il > 1.0:
            i_ear = max(0.5, ear * (iw / rw))
            bg = _bracket_prism(iw, il, i_ear, h)
            cut = _bracket_prism(iw, il, i_ear, cut_h).translate([0.0, 0.0, -1.0])
            return plate, plate - cut, bg, rw, rl
        return plate, plate, None, rw, rl

    if shape is LabelShape.SHIELD:
        rl = min(max(base_rl * 1.28, base_rl + 6.0), avail_rl)
        rw = min(max(base_rw + 4.0, rl * 0.78), avail_rw)
        plate = _shield_prism(rw, rl, h)
        iw, il = rw - 2.0 * border, rl - 2.0 * border * 1.15
        if iw > 1.5 and il > 1.5:
            bg = _shield_prism(iw, il, h)
            cut = _shield_prism(iw, il, cut_h).translate([0.0, 0.0, -1.0])
            return plate, plate - cut, bg, rw, rl
        return plate, plate, None, rw, rl

    if shape is LabelShape.SCROLL:
        rl = min(base_rl + 2.0, avail_rl)
        roll_w = min(max(4.5, rl * 0.22), 6.5)
        roll_h = min(rl + 3.5, avail_rl)
        body_w = min(base_rw + 2.0, max(base_rw, avail_rw - 2.0 * roll_w))
        rw = min(body_w + 2.0 * roll_w, avail_rw)
        body_w = max(4.0, rw - 2.0 * roll_w)
        return _scroll_parts(body_w, rl, roll_w, roll_h, border, h, cut_h)

    if shape is LabelShape.CORNER_STUD:
        rl = min(base_rl + 2.0, avail_rl)
        rw = _fit_rw(2.5)
        r0 = min(rounding, min(rw, rl) / 2.0 - 0.01)
        plate = _centered_cuboid(rw, rl, h, rounding=r0)
        iw, il = rw - 2.0 * border, rl - 2.0 * border
        if iw > 1.0 and il > 1.0:
            r_in = max(0.0, r0 - border)
            cut = _centered_cuboid(iw, il, cut_h, rounding=r_in).translate([0.0, 0.0, -1.0])
            outer_ring = plate - cut
            stud_r = min(1.35, max(0.8, border * 0.85))
            inset_x = rw / 2.0 - border - stud_r - 1.1
            inset_y = rl / 2.0 - border - stud_r - 1.1
            from pybosl2 import cylinder

            from pyboxbuilder.compartments.element import union_all

            if inset_x > 1.0 and inset_y > 1.0:
                studs = union_all(
                    [
                        cylinder(height=h, radius=stud_r).translate([sx * inset_x, sy * inset_y, h / 2.0])
                        for sx in (-1.0, 1.0)
                        for sy in (-1.0, 1.0)
                    ]
                )
                studs_cut = union_all(
                    [
                        cylinder(height=cut_h, radius=stud_r).translate([sx * inset_x, sy * inset_y, h / 2.0])
                        for sx in (-1.0, 1.0)
                        for sy in (-1.0, 1.0)
                    ]
                )
                assert studs is not None and studs_cut is not None
                bg = _centered_cuboid(iw, il, h, rounding=r_in) - studs_cut
                return plate, outer_ring | studs, bg, rw, rl
            bg = _centered_cuboid(iw, il, h, rounding=r_in)
            return plate, outer_ring, bg, rw, rl
        return plate, plate, None, rw, rl

    if shape is LabelShape.ORNATE_FRAME:
        ring_gap = min(1.2, max(0.8, border * 0.8))
        b_in = min(0.9, max(0.7, border * 0.6))
        extra = ring_gap + b_in
        rl = min(base_rl + 2.0 * extra + 1.0, avail_rl)
        rw = _fit_rw(extra + 1.5)
        r0 = min(max(2.0, rounding * 0.6), min(rw, rl) / 2.0 - 0.01)
        plate = _centered_cuboid(rw, rl, h, rounding=r0)
        w1, l1 = rw - 2.0 * border, rl - 2.0 * border
        if w1 <= 0.5 or l1 <= 0.5:
            return plate, plate, None, rw, rl
        r1 = max(0.0, r0 - border)
        cut1 = _centered_cuboid(w1, l1, cut_h, rounding=r1).translate([0.0, 0.0, -1.0])
        outer_ring = plate - cut1
        frame_solid = outer_ring
        bg_solid = _centered_cuboid(w1, l1, h, rounding=r1)

        w2, l2 = w1 - 2.0 * ring_gap, l1 - 2.0 * ring_gap
        w3, l3 = w2 - 2.0 * b_in, l2 - 2.0 * b_in
        if w3 > 0.5 and l3 > 0.5:
            r2 = max(0.0, r1 - ring_gap)
            r3 = max(0.0, r2 - b_in)
            ring2_outer = _centered_cuboid(w2, l2, h, rounding=r2)
            cut3 = _centered_cuboid(w3, l3, cut_h, rounding=r3).translate([0.0, 0.0, -1.0])
            inner_ring = ring2_outer - cut3
            frame_solid = frame_solid | inner_ring
            bg_solid = bg_solid - (
                _centered_cuboid(w2, l2, cut_h, rounding=r2).translate([0.0, 0.0, -1.0]) - cut3
            )

        # Add 4 crisp corner diamond rosettes at the inner corners
        ros_r = min(2.4, max(1.4, extra * 1.15))
        rx_pos = rw / 2.0 - border - ros_r * 0.65
        ry_pos = rl / 2.0 - border - ros_r * 0.65
        if rx_pos > 1.0 and ry_pos > 1.0:
            from pyboxbuilder.compartments.element import union_all

            rosettes = union_all(
                [
                    _diamond_prism(ros_r * 2.0, ros_r * 2.0, h).translate([sx * rx_pos, sy * ry_pos, 0.0])
                    for sx in (-1.0, 1.0)
                    for sy in (-1.0, 1.0)
                ]
            )
            rosettes_cut = union_all(
                [
                    _diamond_prism(ros_r * 2.0, ros_r * 2.0, cut_h).translate([sx * rx_pos, sy * ry_pos, -1.0])
                    for sx in (-1.0, 1.0)
                    for sy in (-1.0, 1.0)
                ]
            )
            assert rosettes is not None and rosettes_cut is not None
            frame_solid = (frame_solid | rosettes) & plate
            bg_solid = bg_solid - rosettes_cut
        return plate, frame_solid, bg_solid, rw, rl

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


def _diamond_prism(width: float, length: float, height: float) -> Bosl2Solid:
    """Extrude a 4-point diamond centered at (0, 0) with base at z=0."""
    from pybosl2 import Path2D, polygon

    hw, hl = width / 2.0, length / 2.0
    pts = [(0.0, -hl), (hw, 0.0), (0.0, hl), (-hw, 0.0)]
    return polygon(Path2D(pts)).linear_extrude(height=height)


def _ellipse_prism(rx: float, ry: float, height: float, segments: int = 48) -> Bosl2Solid:
    """Extrude a smooth ellipse centered at (0, 0) with base at z=0."""
    from pybosl2 import Path2D, polygon

    pts = [
        (rx * math.cos(2.0 * math.pi * i / segments), ry * math.sin(2.0 * math.pi * i / segments))
        for i in range(segments)
    ]
    return polygon(Path2D(pts)).linear_extrude(height=height)


def _scalloped_prism(width: float, length: float, lobe: float, height: float) -> Bosl2Solid:
    """Extrude a vintage quatrefoil-cornered antique plaque with base at z=0."""
    from pybosl2 import cylinder

    from pyboxbuilder.compartments.element import union_all

    cx, cy = width / 2.0 - lobe, length / 2.0 - lobe
    parts: list[Bosl2Solid] = [
        _centered_cuboid(max(0.5, width - 2.0 * lobe), length, height),
        _centered_cuboid(width, max(0.5, length - 2.0 * lobe), height),
    ]
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            parts.append(cylinder(height=height, radius=lobe).translate([sx * cx, sy * cy, height / 2.0]))
    solid = union_all(parts)
    assert solid is not None
    return solid


def _scalloped_inset_prism(
    width: float, length: float, lobe: float, border: float, height: float
) -> Bosl2Solid:
    """Exact uniform inward offset of ``_scalloped_prism`` by ``border``."""
    from pybosl2 import cylinder

    from pyboxbuilder.compartments.element import union_all

    cx, cy = width / 2.0 - lobe, length / 2.0 - lobe
    r_in = max(0.2, lobe - border)
    parts: list[Bosl2Solid] = [
        _centered_cuboid(max(0.5, width - 2.0 * lobe), max(0.5, length - 2.0 * border), height),
        _centered_cuboid(max(0.5, width - 2.0 * border), max(0.5, length - 2.0 * lobe), height),
    ]
    for sx in (-1.0, 1.0):
        for sy in (-1.0, 1.0):
            parts.append(cylinder(height=height, radius=r_in).translate([sx * cx, sy * cy, height / 2.0]))
    solid = union_all(parts)
    assert solid is not None
    return solid


def _bracket_prism(width: float, length: float, ear: float, height: float) -> Bosl2Solid:
    """Extrude a Victorian bookplate cartouche with pointed ogee bracket ends."""
    from pybosl2 import Path2D, polygon

    hw = width / 2.0
    hl = length / 2.0
    xs = max(0.5, hw - ear)
    # Right ogee curve from (xs, -hl) -> (hw, 0) -> (xs, hl), mirrored on left
    pts = [
        (-xs, -hl),
        (xs, -hl),
        (xs + ear * 0.42, -hl * 0.88),
        (xs + ear * 0.56, -hl * 0.48),
        (xs + ear * 0.80, -hl * 0.18),
        (hw, 0.0),
        (xs + ear * 0.80, hl * 0.18),
        (xs + ear * 0.56, hl * 0.48),
        (xs + ear * 0.42, hl * 0.88),
        (xs, hl),
        (-xs, hl),
        (-(xs + ear * 0.42), hl * 0.88),
        (-(xs + ear * 0.56), hl * 0.48),
        (-(xs + ear * 0.80), hl * 0.18),
        (-hw, 0.0),
        (-(xs + ear * 0.80), -hl * 0.18),
        (-(xs + ear * 0.56), -hl * 0.48),
        (-(xs + ear * 0.42), -hl * 0.88),
    ]
    return polygon(Path2D(pts)).linear_extrude(height=height)


def _shield_prism(width: float, length: float, height: float) -> Bosl2Solid:
    """Extrude a classic heraldic crest / shield centered at (0, 0) with base at z=0."""
    from pybosl2 import Path2D, polygon

    hw = width / 2.0
    hl = length / 2.0
    # Slight top arch, vertical upper sides down to y=0.05*hl, smooth taper to (0, -hl)
    pts: list[tuple[float, float]] = [
        (-hw, hl * 0.86),
        (-hw * 0.5, hl * 0.96),
        (0.0, hl),
        (hw * 0.5, hl * 0.96),
        (hw, hl * 0.86),
        (hw, hl * 0.10),
    ]
    steps = 8
    for i in range(1, steps + 1):
        t = i / steps
        angle = t * (math.pi / 2.0)
        x = hw * math.cos(angle)
        y = hl * 0.10 - (hl * 1.10) * (t**1.35)
        pts.append((x, y))
    for i in range(steps - 1, 0, -1):
        t = i / steps
        angle = t * (math.pi / 2.0)
        x = -hw * math.cos(angle)
        y = hl * 0.10 - (hl * 1.10) * (t**1.35)
        pts.append((x, y))
    pts.append((-hw, hl * 0.10))
    return polygon(Path2D(pts)).linear_extrude(height=height)


def _scroll_parts(
    body_w: float,
    rl: float,
    roll_w: float,
    roll_h: float,
    border: float,
    h: float,
    cut_h: float,
) -> tuple[Bosl2Solid, Bosl2Solid | None, Bosl2Solid | None, float, float]:
    """Build parchment scroll plate, rolled end frames, and clean parchment interior."""
    from pyboxbuilder.compartments.element import union_all

    rw = body_w + 2.0 * roll_w
    roll_x = body_w / 2.0 + roll_w / 2.0 - 0.4
    roll_r = min(roll_w / 2.0 - 0.05, 3.0)

    center_plate = _centered_cuboid(body_w + 1.0, rl, h)
    left_roll = _centered_cuboid(roll_w, roll_h, h, rounding=roll_r).translate([-roll_x, 0.0, 0.0])
    right_roll = _centered_cuboid(roll_w, roll_h, h, rounding=roll_r).translate([roll_x, 0.0, 0.0])
    plate = union_all([center_plate, left_roll, right_roll])
    assert plate is not None

    # Interior parchment bay
    ib_w = max(1.0, body_w - 0.6)
    ib_l = max(1.0, rl - 2.0 * border)
    bg = _centered_cuboid(ib_w, ib_l, h)
    bg_cut = _centered_cuboid(ib_w, ib_l, cut_h).translate([0.0, 0.0, -1.0])

    # Hollow out each rolled scroll curl so it reads as a rolled parchment cylinder
    inner_roll_w = max(0.8, roll_w - 2.0 * max(1.0, border * 0.85))
    inner_roll_h = max(1.0, roll_h - 2.0 * max(1.2, border))
    left_hollow = _centered_cuboid(
        inner_roll_w, inner_roll_h, cut_h, rounding=max(0.0, inner_roll_w / 2.0 - 0.05)
    ).translate([-roll_x, 0.0, -1.0])
    right_hollow = _centered_cuboid(
        inner_roll_w, inner_roll_h, cut_h, rounding=max(0.0, inner_roll_w / 2.0 - 0.05)
    ).translate([roll_x, 0.0, -1.0])

    frame = plate - bg_cut - left_hollow - right_hollow
    # Also include the roll interiors in bg so label_background_color fills the parchment rolls cleanly
    left_roll_bg = _centered_cuboid(
        inner_roll_w, inner_roll_h, h, rounding=max(0.0, inner_roll_w / 2.0 - 0.05)
    ).translate([-roll_x, 0.0, 0.0])
    right_roll_bg = _centered_cuboid(
        inner_roll_w, inner_roll_h, h, rounding=max(0.0, inner_roll_w / 2.0 - 0.05)
    ).translate([roll_x, 0.0, 0.0])
    full_bg = union_all([bg, left_roll_bg, right_roll_bg])
    assert full_bg is not None
    return plate, frame, full_bg, rw, roll_h


def _build_finial_solid(
    finial: LabelFinial,
    width: float,
    height: float,
    thickness: float,
) -> Bosl2Solid | None:
    """Build a decorative typographic finial centered at (0, 0) with base at z=0."""
    if finial is LabelFinial.NONE or width < 6.0 or height < 1.5:
        return None

    from pybosl2 import Path2D, cylinder, polygon

    from pyboxbuilder.compartments.element import union_all

    bar_t = max(0.9, min(1.3, height * 0.28))

    if finial is LabelFinial.DIAMOND:
        d_w = min(height * 1.4, width * 0.22)
        d_h = height
        center = _diamond_prism(d_w, d_h, thickness)
        gap_x = d_w / 2.0 + 1.2
        wing_w = max(0.0, width / 2.0 - gap_x)
        parts = [center]
        if wing_w >= 1.5:
            for sx in (-1.0, 1.0):
                parts.append(
                    _centered_cuboid(wing_w, bar_t, thickness, rounding=bar_t / 2.0 - 0.01).translate(
                        [sx * (gap_x + wing_w / 2.0), 0.0, 0.0]
                    )
                )
        return union_all(parts)

    if finial is LabelFinial.TRIPLE_DOT:
        r_big = min(height * 0.46, 2.0)
        r_small = max(0.75, r_big * 0.65)
        dot_dx = r_big + r_small + 1.3
        parts = [
            cylinder(height=thickness, radius=r_big).translate([0.0, 0.0, thickness / 2.0]),
            cylinder(height=thickness, radius=r_small).translate([-dot_dx, 0.0, thickness / 2.0]),
            cylinder(height=thickness, radius=r_small).translate([dot_dx, 0.0, thickness / 2.0]),
        ]
        gap_x = dot_dx + r_small + 1.4
        wing_w = max(0.0, width / 2.0 - gap_x)
        if wing_w >= 1.5:
            for sx in (-1.0, 1.0):
                parts.append(
                    _centered_cuboid(wing_w, bar_t, thickness, rounding=bar_t / 2.0 - 0.01).translate(
                        [sx * (gap_x + wing_w / 2.0), 0.0, 0.0]
                    )
                )
        return union_all(parts)

    if finial is LabelFinial.FLEURON:
        # 4-point concave compass star fleuron flanked by tapered rules
        r_out = min(height * 0.56, 2.8)
        r_in = r_out * 0.36
        star_pts = [
            (0.0, r_out),
            (r_in, r_in),
            (r_out, 0.0),
            (r_in, -r_in),
            (0.0, -r_out),
            (-r_in, -r_in),
            (-r_out, 0.0),
            (-r_in, r_in),
        ]
        star = polygon(Path2D(star_pts)).linear_extrude(height=thickness)
        parts = [star]
        gap_x = r_out + 1.3
        wing_w = max(0.0, width / 2.0 - gap_x)
        if wing_w >= 2.0:
            for sx in (-1.0, 1.0):
                pts = [
                    (sx * gap_x, -bar_t * 0.55),
                    (sx * (gap_x + wing_w), -bar_t * 0.2),
                    (sx * (gap_x + wing_w), bar_t * 0.2),
                    (sx * gap_x, bar_t * 0.55),
                ]
                if sx < 0:
                    pts.reverse()
                parts.append(polygon(Path2D(pts)).linear_extrude(height=thickness))
        return union_all(parts)

    if finial is LabelFinial.CHEVRON:
        # Opposing sci-fi chevrons + center diamond pip + flanking bars
        pip_r = min(height * 0.34, 1.5)
        parts = [_diamond_prism(pip_r * 2.0, pip_r * 2.0, thickness)]
        chev_x = pip_r + 1.8
        chev_w = min(height * 0.75, 2.8)
        chev_h = height * 0.48
        stroke = max(0.95, bar_t * 0.95)
        for sx in (-1.0, 1.0):
            # V-chevron pointing inward toward the center pip
            pts = [
                (sx * (chev_x + chev_w), -chev_h),
                (sx * (chev_x + chev_w + stroke), -chev_h),
                (sx * (chev_x + stroke), 0.0),
                (sx * (chev_x + chev_w + stroke), chev_h),
                (sx * (chev_x + chev_w), chev_h),
                (sx * chev_x, 0.0),
            ]
            if sx < 0:
                pts.reverse()
            parts.append(polygon(Path2D(pts)).linear_extrude(height=thickness))
        gap_x = chev_x + chev_w + stroke + 1.2
        wing_w = max(0.0, width / 2.0 - gap_x)
        if wing_w >= 1.5:
            for sx in (-1.0, 1.0):
                parts.append(
                    _centered_cuboid(wing_w, bar_t, thickness).translate([sx * (gap_x + wing_w / 2.0), 0.0, 0.0])
                )
        return union_all(parts)

    if finial is LabelFinial.SCROLLWORK:
        # Center diamond flanked by symmetric curled scroll loops and tapered tails
        d_r = min(height * 0.46, 2.0)
        parts = [_diamond_prism(d_r * 2.4, d_r * 2.0, thickness)]
        curl_r = min(height * 0.44, 1.9)
        curl_in = max(0.4, curl_r - bar_t * 0.95)
        curl_x = d_r * 1.2 + curl_r + 0.6
        for sx in (-1.0, 1.0):
            ring = cylinder(height=thickness, radius=curl_r).translate([sx * curl_x, 0.0, thickness / 2.0])
            if curl_in > 0.35:
                hole = cylinder(height=thickness + 2.0, radius=curl_in).translate(
                    [sx * curl_x, 0.0, thickness / 2.0]
                )
                ring = ring - hole
            parts.append(ring)
        gap_x = curl_x + curl_r + 0.5
        wing_w = max(0.0, width / 2.0 - gap_x)
        if wing_w >= 1.5:
            for sx in (-1.0, 1.0):
                parts.append(
                    _centered_cuboid(wing_w, bar_t, thickness, rounding=bar_t / 2.0 - 0.01).translate(
                        [sx * (gap_x + wing_w / 2.0), 0.0, 0.0]
                    )
                )
        return union_all(parts)

    # LabelFinial.SPEAR: double-pointed tapered Victorian rule (◄━━━━━━►)
    hw = width / 2.0
    mid_h = min(height * 0.44, 2.0)
    neck_h = max(0.6, bar_t * 0.55)
    pts = [
        (-hw, 0.0),
        (-hw * 0.72, -neck_h),
        (-hw * 0.14, -neck_h),
        (0.0, -mid_h),
        (hw * 0.14, -neck_h),
        (hw * 0.72, -neck_h),
        (hw, 0.0),
        (hw * 0.72, neck_h),
        (hw * 0.14, neck_h),
        (0.0, mid_h),
        (-hw * 0.14, neck_h),
        (-hw * 0.72, neck_h),
    ]
    return polygon(Path2D(pts)).linear_extrude(height=thickness)


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
    finial: LabelFinial = LabelFinial.NONE,
    logo_position: str | None = None,
    logo_size_mm: float | None = None,
) -> Label:
    """Build a framed label with decorative plaque, optional finial, and optional logo bay."""
    rtw, rtl = (tl, tw) if is_vertical else (tw, tl)
    avail_rw, avail_rl = (label_l, label_w) if is_vertical else (label_w, label_l)
    pad = border + gap

    # 1. Compute text + optional finial block in local reading coordinates
    tf_w, tf_h = rtw, rtl
    text_dx_local, text_dy_local = 0.0, 0.0
    finial_local: Bosl2Solid | None = None
    if finial is not LabelFinial.NONE:
        finial_h = max(3.2, min(4.8, rtl * 0.34))
        finial_gap = max(1.4, gap * 0.9)
        finial_w = min(max(rtw * 0.88, 16.0), max(10.0, avail_rw - 2.0 * pad))
        raw_finial = _build_finial_solid(finial, finial_w, finial_h, BACKING_HEIGHT_MM)
        if raw_finial is not None:
            tf_h = rtl + finial_gap + finial_h
            tf_w = max(rtw, finial_w)
            text_dy_local = (finial_gap + finial_h) / 2.0
            y_finial = -(rtl + finial_gap) / 2.0
            finial_local = raw_finial.translate([0.0, y_finial, 0.0])

    # 2. Reserve optional embedded logo bay inside the plaque and center combined content
    content_w, content_h = tf_w, tf_h
    slot_local: tuple[float, float, float, float] | None = None
    if logo_position in ("top", "bottom", "left", "right"):
        slot_gap = max(2.2, gap * 1.4)
        if logo_position in ("top", "bottom"):
            max_slot_h = avail_rl - 2.0 * pad - tf_h - slot_gap
            if max_slot_h >= 6.0:
                slot_h = min(
                    logo_size_mm if logo_size_mm is not None else max(10.0, rtl * 1.25),
                    max_slot_h,
                )
                slot_w = min(max(tf_w * 0.75, slot_h), max(6.0, avail_rw - 2.0 * pad))
                content_w = max(tf_w, slot_w)
                content_h = tf_h + slot_gap + slot_h
                if logo_position == "top":
                    slot_cy = content_h / 2.0 - slot_h / 2.0
                    tf_shift_y = -(content_h / 2.0 - tf_h / 2.0)
                else:
                    slot_cy = -(content_h / 2.0 - slot_h / 2.0)
                    tf_shift_y = content_h / 2.0 - tf_h / 2.0
                text_dy_local += tf_shift_y
                if finial_local is not None:
                    finial_local = finial_local.translate([0.0, tf_shift_y, 0.0])
                slot_local = (0.0, slot_cy, slot_w, slot_h)
        else:
            max_slot_w = avail_rw - 2.0 * pad - tf_w - slot_gap
            if max_slot_w >= 6.0:
                slot_h = min(
                    logo_size_mm if logo_size_mm is not None else max(tf_h * 1.15, 12.0),
                    max(6.0, avail_rl - 2.0 * pad),
                )
                slot_w = min(slot_h, max_slot_w)
                content_w = tf_w + slot_gap + slot_w
                content_h = max(tf_h, slot_h)
                if logo_position == "left":
                    slot_cx = -(content_w / 2.0 - slot_w / 2.0)
                    tf_shift_x = content_w / 2.0 - tf_w / 2.0
                else:
                    slot_cx = content_w / 2.0 - slot_w / 2.0
                    tf_shift_x = -(content_w / 2.0 - tf_w / 2.0)
                text_dx_local += tf_shift_x
                if finial_local is not None:
                    finial_local = finial_local.translate([tf_shift_x, 0.0, 0.0])
                slot_local = (slot_cx, 0.0, slot_w, slot_h)

    # Shift text_solid in lid coordinates to match local reading-frame shift
    if text_dx_local != 0.0 or text_dy_local != 0.0:
        if is_vertical:
            text_solid = text_solid.translate([-text_dy_local, text_dx_local, 0.0])
        else:
            text_solid = text_solid.translate([text_dx_local, text_dy_local, 0.0])

    plate_local, frame_local, bg_local, rw, rl = _build_shape_parts(
        shape=shape,
        rtw=content_w,
        rtl=content_h,
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
    placed_finial = _place(finial_local)

    image_slot: tuple[float, float, float, float] | None = None
    if slot_local is not None:
        scx, scy, sw, sh = slot_local
        image_slot = (tcx - scy, tcy + scx, sh, sw) if is_vertical else (tcx + scx, tcy + scy, sw, sh)

    if solid_background or shape is LabelShape.UNDERLINE:
        bg = _place(bg_local)
        if bg is not None:
            bg = bg - text_solid
            if placed_finial is not None:
                bg = bg - placed_finial
        return Label(
            text=text_solid,
            hatching=None,
            plate=plate,
            frame=frame,
            background=bg,
            finial=placed_finial,
            image_slot=image_slot,
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
    if hatching is not None:
        hatching = hatching - text_solid
        if placed_finial is not None:
            hatching = hatching - placed_finial
    return Label(
        text=text_solid,
        hatching=hatching,
        plate=plate,
        frame=frame,
        finial=placed_finial,
        image_slot=image_slot,
    )
