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

from pyboxbuilder.enums import LabelMode

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

LABEL_TEXT_GAP_MM = 0.5
"""Default gap between label text and the inside of the border."""


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


def _set_text(text: str, diagonal: bool, width: float, length: float) -> Bosl2Solid:
    """Extrude the label text at the nominal size, rotated if diagonal."""
    from pybosl2 import text as bosl2_text

    solid = bosl2_text(text=text, size=NOMINAL_SIZE_MM, font=FONT).linear_extrude(
        height=TEXT_HEIGHT_MM
    )
    if diagonal:
        solid = solid.rotate([0.0, 0.0, math.degrees(math.atan2(length, width))])
    return solid


def text_height_for(
    width: float,
    length: float,
    text: str,
    border_margin_mm: float = 5.0,
    diagonal: bool = False,
    label_mode: LabelMode = LabelMode.FRAMED,
    label_border_mm: float = LABEL_BORDER_MM,
    label_text_gap_mm: float = LABEL_TEXT_GAP_MM,
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

    if label_w <= 0 or label_l <= 0 or not text:
        return 0.0

    is_vertical = (length > width) and not diagonal
    target_w = label_l if is_vertical else label_w
    target_l = label_w if is_vertical else label_l

    b = _set_text(text, diagonal, width, length).bounds()
    set_w = float(b.size[0]) if hasattr(b, "size") else float(b[1][0])
    set_l = float(b.size[1]) if hasattr(b, "size") else float(b[1][1])
    if set_w <= 0 or set_l <= 0:
        return 0.0
    return NOMINAL_SIZE_MM * min(target_w / set_w, target_l / set_l)


def build_label(
    width: float,
    length: float,
    thickness: float,
    text: str,
    label_mode: LabelMode = LabelMode.FRAMED,
    diagonal: bool = False,
    min_text_height_mm: float = 4.0,
    border_margin_mm: float = 5.0,
    label_border_mm: float | None = None,
    label_text_gap_mm: float | None = None,
    label_rounding_mm: float | None = None,
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

    Returns:
        A `Label`, or None when the text would come out under the minimum.

    """
    from pyboxbuilder.box.shell import corner

    border = label_border_mm if label_border_mm is not None else LABEL_BORDER_MM
    gap = label_text_gap_mm if label_text_gap_mm is not None else LABEL_TEXT_GAP_MM
    pad = border + gap

    label_w = width - 2 * border_margin_mm
    label_l = length - 2 * border_margin_mm
    if label_w <= 0 or label_l <= 0 or not text:
        return None

    size = text_height_for(
        width, length, text, border_margin_mm, diagonal,
        label_mode, border, gap
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
    solid = solid.translate([width / 2 - cx, length / 2 - cy, 0.0])

    if label_mode is LabelMode.FRAMELESS:
        return Label(text=solid)

    # Framed: a hatched backing plate behind the text. It hugs the text rather
    # than filling the label area, so a lid can carry both a frame and a
    # through-hole pattern — a plate the size of the whole area would simply
    # cover the pattern up.
    b = solid.bounds()
    tcx, tcy = (float(b.center[0]), float(b.center[1])) if hasattr(b, "center") else (float(b[0][0]), float(b[0][1]))
    tw, tl = (float(b.size[0]), float(b.size[1])) if hasattr(b, "size") else (float(b[1][0]), float(b[1][1]))
    plate_w = min(tw + 2 * pad, label_w)
    plate_l = min(tl + 2 * pad, label_l)
    plate_x = tcx - plate_w / 2
    plate_y = tcy - plate_l / 2

    rounding_val = label_rounding_mm if label_rounding_mm is not None else 5.0

    from pybosl2 import cuboid

    from pyboxbuilder.rounding import vertical_edges
    plate_solid = cuboid([plate_w, plate_l, BACKING_HEIGHT_MM], rounding=rounding_val, edges=vertical_edges())
    plate = corner(plate_solid, [plate_w, plate_l, BACKING_HEIGHT_MM], at=(plate_x, plate_y, 0.0))
    hatching = corner(
        _build_hatching(plate_w, plate_l, border=border, rounding=rounding_val),
        [plate_w, plate_l, BACKING_HEIGHT_MM],
        at=(plate_x, plate_y, 0.0),
    )
    # The striped grid stops at the lettering: the two are inlaid side by side
    # into one face, so a stripe running under a glyph would be competing with
    # it for the same top layer.
    return Label(text=solid, hatching=hatching - solid, plate=plate)


def _build_hatching(
    width: float,
    length: float,
    spacing: float = 4.0,
    border: float = 1.5,
    rounding: float = 5.0,
) -> Bosl2Solid:
    """Diagonal hatching lines, centred on the origin and clipped to the area.

    The lines are cropped to the label rectangle so the hatching cannot spill
    past the backing plate it decorates.
    """
    from pybosl2 import cuboid

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
    clip_w = max(width - 2 * border, 0.0)
    clip_l = max(length - 2 * border, 0.0)
    from pyboxbuilder.rounding import vertical_edges
    clip_rounding = max(rounding - border, 0.0)
    clip_solid = cuboid([clip_w, clip_l, BACKING_HEIGHT_MM], rounding=clip_rounding, edges=vertical_edges())
    return hatching & clip_solid
