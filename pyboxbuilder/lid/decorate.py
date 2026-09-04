# SPDX-License-Identifier: Apache-2.0
"""Apply a `LidBuilder` to a lid's geometry (T161 / US9).

Every box type produces a bare lid; this is where it gets its label, its
through-hole pattern and its colours. Doing it here rather than in each box type
means all thirteen types decorate identically, and a new type gets decoration
for free.

The decoratable face is derived from the lid's own bounding box — its top, inset
by the border margin — so no box type has to declare where its flat area is.

Colour handling differs by export mode, which is the whole reason this returns a
pair rather than one solid:

* **mmu** — the label stays a separate coloured object so the slicer can give it
  its own material.
* **single** — the label is engraved into the lid instead, because a raised
  label in one colour is invisible.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pyboxbuilder.enums import LabelMode

if TYPE_CHECKING:
    from pybosl2 import Color
    from pybosl2.shapes3d import Bosl2Solid

    from pyboxbuilder.lid.builder import LidBuilder
    from pyboxbuilder.lid.label import Label

ENGRAVE_DEPTH_MM = 0.4
"""How deep a single-colour label is cut into the lid."""

INLAY_DEPTH_MM = 0.6
"""How deep a multi-material label is inlaid into the lid (FR-022a).

Three layers at the 0.2mm this library assumes, which is enough for the accent
to cover the material under it. Deeper only costs filament and print time: the
colour is a surface, and nothing about the label is structural.
"""


@dataclass(frozen=True)
class LidInsert:
    """One part of a lid that prints in its own material.

    Carries the colour **alongside** the solid rather than only baked into it.
    A pybosl2 solid has no readable colour — `.color` is the method that sets
    one — so a caller that wanted to know what an insert prints in had no way
    to ask, and the preview drew every one of them in the lid's own colour.
    The label was there; it was just the same colour as the lid.
    """

    solid: Bosl2Solid
    """The geometry, already carrying its colour for export."""
    color: Color | None = None
    """What it prints in, for a caller that needs to know rather than render."""


@dataclass
class DecoratedLid:
    """A decorated lid, plus any parts that print in their own colour."""

    solid: Bosl2Solid
    inserts: list[LidInsert] = field(default_factory=list)
    """Coloured positives, kept separate in mmu mode and fused in single mode."""

    skipped_label: bool = False
    """True when the label was dropped for being under the minimum text height."""

    @property
    def solids(self) -> list[Bosl2Solid]:
        """Just the insert geometry, for a caller that only writes it out."""
        return [insert.solid for insert in self.inserts]


def decorate_lid(
    lid: Bosl2Solid,
    builder: LidBuilder | None,
    lid_thickness: float,
    mode: str = "mmu",
    body_color: Color | None = None,
    reserved: Sequence[tuple[float, float, float]] = (),
) -> DecoratedLid:
    """Apply a lid's label, pattern and colours to its geometry.

    Args:
        lid: The bare lid from a box type's `build_lid`.
        builder: The lid configuration; None leaves the lid untouched.
        lid_thickness: Thickness of the plate the decoration goes into.
        mode: "mmu" or "single".
        body_color: The box's own colour, which the accents are derived to
            contrast with when the caller names none (FR-022).
        reserved: ``(x, y, radius)`` circles on the lid that the pattern must
            leave solid — a box type's own lid features, such as a sliding
            lid's fingernail dish (FR-002e5).

    Returns:
        The decorated lid and its coloured inserts.

    """
    if lid is None or builder is None:
        return DecoratedLid(solid=lid)

    resolved = _with_accent_colors(builder.for_mode(mode), body_color)
    face = _top_face(lid)
    if face is None:
        return DecoratedLid(solid=lid)

    width, length, origin_x, origin_y, top_z = face
    result = DecoratedLid(solid=lid)

    # The label is built first even though it is applied last, because the
    # pattern has to know where it lands: holes under the lettering leave it
    # printing onto air, and in MMU mode the text is a separate object that
    # would simply fall through. The label takes precedence and the pattern
    # stops at its boundary (FR-023).
    label = _build_label(resolved, width, length, mode) if resolved.text else None
    if resolved.text and label is None:
        result.skipped_label = True

    logo_solid = _build_logo(resolved, width, length, mode) if resolved.logo else None

    if resolved.pattern is not None:
        result.solid = _cut_pattern(
            result.solid, resolved, width, length,
            origin_x, origin_y, top_z, lid_thickness,
            keep_clear=label,
            logo_keepout=logo_solid,
            label_clearance=resolved.label_clearance,
            reserved=reserved,
        )

    if label is not None:
        _apply_label(result, resolved, label, origin_x, origin_y, top_z, mode, lid_thickness)

    if logo_solid is not None:
        _apply_logo(result, resolved, logo_solid, origin_x, origin_y, top_z, mode)

    return result


LABEL_CLEARANCE_MM = 0.0
"""How far the pattern stands off the lettering, all round.

**Zero**, so the holes stop at the glyphs themselves and the letters read as
letters rather than as letters on a plaque. The pattern still cannot undercut
them: the keep-out is the glyph outline, so every stroke keeps its own footprint
of solid lid, and the label is inlaid into that lid rather than perched on it —
the plastic goes all the way down.

A margin is settable per lid (`LidBuilder.label_clearance_mm`) for a lid whose
pattern is coarse enough that a stroke would otherwise finish on the very edge
of a hole.
"""


def _build_label(
    builder: LidBuilder, width: float, length: float, mode: str
) -> Label | None:
    """Build the label for this face, or ``None`` if it would be illegible."""
    from pyboxbuilder.lid.label import build_label

    assert builder.text is not None
    # A frame is a colour feature: in one material there is nothing to
    # distinguish the backing plate from the lid, so a framed label degenerates
    # to engraved text. Asking for the frame anyway would also lift the text
    # clear of the face and engrave nothing at all.
    label_mode = builder.mode if mode != "single" else LabelMode.FRAMELESS

    return build_label(
        width=width,
        length=length,
        thickness=0.0,
        text=builder.text,
        label_mode=label_mode,
        diagonal=builder.is_diagonal,
        min_text_height_mm=builder.min_text_height,
        border_margin_mm=builder.border_margin,
        label_border_mm=builder.label_border_mm,
        label_text_gap_mm=builder.label_text_gap_mm,
        label_rounding_mm=builder.label_rounding_mm,
    )


def _bounds_center_size(
    solid: Bosl2Solid,
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    b = solid.bounds()
    if hasattr(b, "center") and hasattr(b, "size"):
        cz_val = float(b.size[2]) if len(b.size) > 2 else 0.0
        return (
            (float(b.center[0]), float(b.center[1]), float(b.center[2])),
            (float(b.size[0]), float(b.size[1]), cz_val),
        )
    return (
        (float(b[0][0]), float(b[0][1]), float(b[0][2])),
        (float(b[1][0]), float(b[1][1]), float(b[1][2]) if len(b[1]) > 2 else 0.0),
    )


def _build_logo(
    builder: LidBuilder, width: float, length: float, mode: str
) -> Bosl2Solid | None:
    """Build the logo solid, centered on the lid face."""
    if not builder.logo:
        return None

    margin = builder.border_margin_mm or 10.0
    logo_w = width - 2 * margin
    logo_l = length - 2 * margin
    if logo_w <= 0 or logo_l <= 0:
        return None

    depth = INLAY_DEPTH_MM
    if isinstance(builder.logo, str):
        from pyboxbuilder.compartments.element import _svg_region
        raw = _svg_region(builder.logo).linear_extrude(height=depth)
        (cx, cy, cz), (span_x, span_y, _) = _bounds_center_size(raw)
        raw = raw.translate([-float(cx), -float(cy), -float(cz) + depth / 2])
        scale_val = min(logo_w / max(float(span_x), 1e-9), logo_l / max(float(span_y), 1e-9))
        solid = raw.scale([scale_val, scale_val, 1.0])
    elif callable(builder.logo):
        solid = builder.logo(logo_w, logo_l, depth)
    else:
        solid = builder.logo
        (cx, cy, cz), (w, l, h) = _bounds_center_size(solid)
        if w > 0 and l > 0 and h > 0:
            scale_val = min(logo_w / w, logo_l / l)
            scale_z = depth / h
            solid = solid.translate([-cx, -cy, -cz + h / 2]).scale([scale_val, scale_val, scale_z])

    offset_x = width / 2
    offset_y = length / 2
    return solid.translate([offset_x, offset_y, 0.0])


def _apply_logo(
    result: DecoratedLid,
    builder: LidBuilder,
    logo_solid: Bosl2Solid,
    origin_x: float,
    origin_y: float,
    top_z: float,
    mode: str,
) -> None:
    """Inlay or engrave the logo into the lid."""
    def onto_face(solid: Bosl2Solid) -> Bosl2Solid:
        return solid.translate([origin_x, origin_y, top_z - INLAY_DEPTH_MM])

    if mode == "single":
        cut = onto_face(logo_solid).translate([0.0, 0.0, INLAY_DEPTH_MM - ENGRAVE_DEPTH_MM])
        result.solid = result.solid - cut
        return

    inlay = onto_face(logo_solid) & result.solid
    result.solid = result.solid - inlay
    result.inserts.append(LidInsert(_coloured(inlay, builder.logo_color), builder.logo_color))


KEEPOUT_DIRECTIONS = 12
"""How many directions the label is smeared in to grow its keep-out.

A cheap stand-in for a true offset: the label is unioned with copies of itself
shifted a clearance in a ring of directions, which grows its outline by that
clearance to within the ring's own resolution. Twelve is close enough at 1.5mm
that no glyph shows a facet, and it costs a dozen unions rather than a
Minkowski sum over every letter.
"""


def _label_keepout(
    label: Label | None, depth: float, clearance: float = LABEL_CLEARANCE_MM
) -> Bosl2Solid | None:
    """Return the volume a label needs kept solid, in the face's own frame.

    Follows the label's **shape**, not its bounding box. A box is right for a
    framed label, whose plate is a rectangle, and badly wrong for a diagonal
    one: "Favors" set corner to corner on a 96 x 70 lid has a bounding box
    covering 71% of it, so keeping that clear suppressed nearly every hole and
    the lid came out looking solid. What has to stay solid is the lettering and
    a margin around it — not the rectangle it happens to span.

    Args:
        label: The built label, or ``None``.
        depth: How tall to make the keep-out, so it spans the holes it blocks.
        clearance: Solid margin to keep around the lettering. ``0`` — the
            default — stops the holes at the glyphs themselves.

    Returns:
        The solid to keep clear of, or ``None`` when there is no label.

    """
    if label is None:
        return None

    # A framed label's plate really is a rectangle, and it already stands off
    # the text by its own padding, so it is its own keep-out.
    if label.plate is not None:
        return _as_depth(label.plate, depth)

    if clearance <= 0:
        # The glyphs themselves: the holes stop where the letters do.
        return _as_depth(label.text, depth)
    return _as_depth(_grown(label.text, clearance), depth)


def _grown(solid: Bosl2Solid, by: float) -> Bosl2Solid:
    """Return `solid` widened in the face's plane by roughly `by` millimetres."""
    import math

    grown = solid
    for i in range(KEEPOUT_DIRECTIONS):
        angle = 2 * math.pi * i / KEEPOUT_DIRECTIONS
        grown = grown | solid.translate([by * math.cos(angle), by * math.sin(angle), 0.0])
    return grown


def _as_depth(solid: Bosl2Solid, depth: float) -> Bosl2Solid:
    """Return `solid` stretched in z to `depth`, with its base at z = 0."""
    b = solid.bounds()
    cz = float(b.center[2]) if hasattr(b, "center") else float(b[0][2])
    h = float(b.size[2]) if hasattr(b, "size") else float(b[1][2])
    if h <= 0:
        return solid
    return solid.translate([0.0, 0.0, -(cz - h / 2)]).scale([1.0, 1.0, depth / h])


def _top_face(lid: Bosl2Solid) -> tuple[float, float, float, float, float] | None:
    """(width, length, origin_x, origin_y, top_z) of the lid's upper surface.

    A lid that cannot be measured raises rather than measuring as ``None``:
    ``None`` meant the caller skipped the whole decoration, so a lid came out
    with no label and no pattern and nothing said why (FR-000h).
    """
    (cx, cy, cz), (w, l, h) = _bounds_center_size(lid)
    if w <= 0 or l <= 0:
        return None
    return (float(w), float(l), float(cx - w / 2), float(cy - l / 2), float(cz + h / 2))


def _cut_pattern(
    lid: Bosl2Solid,
    builder: LidBuilder,
    width: float,
    length: float,
    origin_x: float,
    origin_y: float,
    top_z: float,
    lid_thickness: float,
    keep_clear: Label | None = None,
    logo_keepout: Bosl2Solid | None = None,
    label_clearance: float = LABEL_CLEARANCE_MM,
    reserved: Sequence[tuple[float, float, float]] = (),
) -> Bosl2Solid:
    """Cut the through-hole pattern into the lid, clear of its border.

    Args:
        lid: The lid to perforate.
        builder: The resolved lid configuration, read for its pattern.
        width: The face's width in mm.
        length: The face's length in mm.
        origin_x: The face's minimum x, in the lid's frame.
        origin_y: The face's minimum y.
        top_z: The face's z.
        lid_thickness: How deep the holes must reach to break through.
        keep_clear: The label whose shape must stay solid. Holes under the
            lettering would leave it printing onto air (FR-023).
        logo_keepout: The logo solid whose shape must stay solid.
        label_clearance: Solid margin kept around the lettering.
        reserved: ``(x, y, radius)`` circles the pattern must leave solid.

    Returns:
        The perforated lid.

    """
    from pyboxbuilder.box.shell import block
    from pyboxbuilder.lid.pattern import build_pattern

    assert builder.pattern is not None
    # The pattern's border is its own, not the label's: one keeps text off the
    # edge, the other keeps *material* there — the band the lid is picked up
    # by, and on a sliding lid the band that rides in the grooves.
    margin = builder.pattern.border_width
    area_w = width - 2 * margin
    area_l = length - 2 * margin
    if area_w <= 0 or area_l <= 0:
        return lid

    # Overshoot above and below so the holes go all the way through — a pattern
    # that stops short of the top face leaves a skin and shows nothing.
    depth = lid_thickness + 2.0
    base = (origin_x + margin, origin_y + margin, top_z - lid_thickness - 1.0)

    holes = build_pattern(
        area_w, area_l, depth, builder.pattern.type,
        builder.pattern.spacing, builder.pattern.web,
    )
    if holes is None:
        # No hole fits — too small an area, or a pitch that cannot hold a hole
        # and a printable web at once. A solid lid is the right answer; a
        # peppering of pinholes is not (FR-000c).
        return lid

    # The fills lay their lattice out in the area's own frame, deliberately
    # overhanging every edge, so it is *moved* into place and not re-anchored.
    # Re-anchoring by bounding box — which this used to do — threw the centring
    # away and pushed the whole overhang to one side: on a 96 x 70 lid the
    # right edge lost 56mm³ of material to the border strip and the left only
    # 33mm³, so one side was cut through the hexes and the other through the
    # webs. Trimming to the area is what keeps the border solid.
    holes = holes.translate([base[0], base[1], base[2]])
    holes = holes & block([area_w, area_l, depth], at=base)

    keepout = _label_keepout(keep_clear, depth, label_clearance)
    if keepout is not None:
        holes = holes - keepout.translate([origin_x, origin_y, base[2]])

    if logo_keepout is not None:
        # Stretch the logo keepout in z and subtract it
        stretched_logo = _as_depth(logo_keepout, depth)
        holes = holes - stretched_logo.translate([origin_x, origin_y, base[2]])

    # A box type's own lid features — a sliding lid's fingernail dish — are
    # already cut into the plate. The pattern keeps off them and off the ring
    # of material they are pulled against (FR-002e5); these arrive in the
    # lid's own frame, not the face's.
    for x, y, radius in reserved:
        holes = holes - _disc(x, y, base[2], radius, depth)
    return lid - holes


def _disc(x: float, y: float, z: float, radius: float, depth: float) -> Bosl2Solid:
    """Return a cylinder at ``(x, y)``, for reserving a round patch of lid."""
    from pybosl2 import cylinder

    from pyboxbuilder.precision import kwargs as precision_kwargs

    return cylinder(height=depth, radius=radius, **precision_kwargs()).translate(
        [x, y, z + depth / 2]
    )


def _apply_label(
    result: DecoratedLid,
    builder: LidBuilder,
    label: Label,
    origin_x: float,
    origin_y: float,
    top_z: float,
    mode: str,
    lid_thickness: float,
) -> None:
    """Inlay the label into `result`, or engrave it for a single-colour print.

    Args:
        result: The lid being decorated; modified in place.
        builder: The resolved lid configuration, read for its accent colours.
        label: The built label.
        origin_x: The face's minimum x, in the lid's frame.
        origin_y: The face's minimum y.
        top_z: The face's z.
        mode: ``"mmu"`` or ``"single"``.

    """

    def onto_face(solid: Bosl2Solid) -> Bosl2Solid:
        """Place a label part so it fills the inlay recess, flush with the face."""
        return solid.translate([origin_x, origin_y, top_z - INLAY_DEPTH_MM])

    if mode == "single":
        # One material, so there is nothing to inlay — depth is the only thing
        # that can make the label visible. Engraving the plate too would just
        # cut a rectangular recess and take the lettering with it.
        cut = onto_face(label.text).translate([0.0, 0.0, INLAY_DEPTH_MM - ENGRAVE_DEPTH_MM])
        result.solid = result.solid - cut
        return

    # If frame_color is None, hatching is cut as a through-hole.
    # Otherwise, it is inlaid as a second color.
    if builder.frame_color is None and label.hatching is not None:
        hatching_cut = _as_depth(label.hatching, lid_thickness + 2.0)
        hatching_cut = hatching_cut.translate([origin_x, origin_y, top_z - lid_thickness - 1.0])
        result.solid = result.solid - hatching_cut

    # Inlaid, not embossed (FR-022a): each coloured part is cut out of the lid
    # and put back in its own colour, exactly as deep as the recess, so the
    # lid's top face stays flat. Only the parts that change colour are cut —
    # the plate between them is left alone, which is what makes it the box's
    # own material without an insert of its own (FR-022).
    for part, colour in (
        (label.text, builder.text_color),
        (label.hatching, builder.frame_color),
    ):
        if part is None or colour is None:
            continue
        # Clipped to the lid as it stands, so an inlay only ever fills material
        # that was actually there. Where the label crosses something already
        # cut — a pattern hole, or a sliding lid's fingernail dish — the
        # unclipped inlay would hang in the gap with nothing under it, and the
        # lid would no longer give up exactly the volume the insert fills.
        inlay = onto_face(_to_depth(part)) & result.solid
        result.solid = result.solid - inlay
        result.inserts.append(LidInsert(_coloured(inlay, colour), colour))


def _to_depth(part: Bosl2Solid) -> Bosl2Solid:
    """Return a label part as a solid exactly :data:`INLAY_DEPTH_MM` tall.

    The parts are built at their own heights — the lettering one thickness, the
    striped grid another — because until now they sat on top of each other.
    Inlaid they all occupy the same recess, so they are all cut to it.

    Args:
        part: One of the label's coloured parts.

    Returns:
        The part, scaled in z to the inlay depth with its base at z = 0.

    """
    b = part.bounds()
    cz = float(b.center[2]) if hasattr(b, "center") else float(b[0][2])
    h = float(b.size[2]) if hasattr(b, "size") else float(b[1][2])
    if h <= 0:
        return part
    return part.translate([0.0, 0.0, -(cz - h / 2)]).scale([1.0, 1.0, INLAY_DEPTH_MM / h])


def _with_accent_colors(builder: LidBuilder, body_color: Color | None) -> LidBuilder:
    """Fill in the accent colours the caller left unset (FR-022).

    An unset accent is not a subtle default — it is no colour at all, so the
    insert prints in whatever the slicer picks and the three-colour lid the
    requirement describes needs all three set before it works at all.

    Args:
        builder: The resolved lid configuration.
        body_color: The box's colour, or ``None`` for the neutral default.

    Returns:
        The configuration with text, frame and pattern colours resolved.

    """
    from dataclasses import replace

    from pybosl2 import Color

    from pyboxbuilder.lid.color_layers import resolve_colors

    colors = resolve_colors(
        body_color if body_color is not None else Color("gray"),
        builder.text_color, builder.frame_color, builder.pattern_color,
    )
    logo_color = builder.logo_color
    if logo_color is None:
        logo_color = colors.text_color

    return replace(
        builder,
        text_color=colors.text_color,
        frame_color=colors.frame_color,
        pattern_color=colors.pattern_color,
        logo_color=logo_color,
    )


def _coloured(solid: Bosl2Solid, colour: Color | None) -> Bosl2Solid:
    """Tint a solid when a colour is set; pybosl2 wrappers carry their own.

    An uncolourable solid raises. Returning it untinted instead produced a
    single-material print from a description that asked for several, which is
    exactly the failure a user does not see until it comes off the bed.
    """
    if colour is None:
        return solid
    return solid.color(colour)
