# SPDX-License-Identifier: Apache-2.0
"""Accent colours for multi-material lids (FR-022).

Three colours are settable independently — the label text, the frame's top
layer and the pattern's top layer — and each has a default derived from the
body colour rather than left unset. That matters: an unset accent is not a
subtle default, it is *no colour*, so the feature only worked for a caller who
already knew to set all three (FR-000a).
"""

from __future__ import annotations

from dataclasses import dataclass

from pybosl2 import Color

TEXT_COLOR = "black"
"""Default colour of a lid's lettering (FR-022).

A label is read against a lid whose colour is the game's choice, so the text
needs the one colour that reads against all of them. The previous default was
white, which vanishes on any pale box.
"""

STRIPED_GRID_COLOR = "lightgrey"
"""Default colour of a framed label's striped grid (FR-022).

It is a texture behind the lettering, not a second label: it has to separate
the text from the lid without competing with it, which a light neutral does and
a saturated accent does not.
"""


@dataclass(frozen=True)
class ColorLayerAssignment:
    """Maps geometry components to their accent colors."""

    body_color: Color
    """The base box body color."""
    text_color: Color | None = None
    """Label text color (None = no label)."""
    frame_color: Color | None = None
    """Frame top layer color (None = no frame)."""
    pattern_color: Color | None = None
    """Pattern top layer color (None = no pattern)."""




def resolve_colors(
    body_color: Color,
    text_color: Color | None = None,
    frame_color: Color | None = None,
    pattern_color: Color | None = None,
) -> ColorLayerAssignment:
    """Resolve accent colors with sensible defaults (FR-022).

    The defaults are fixed rather than derived from the body, because what a
    label has to do is be *read*, and a hue shifted off the box's own colour is
    no more legible against it than the colour it came from.

    Args:
        body_color: The base box body color.
        text_color: Label text color. Defaults to :data:`TEXT_COLOR`.
        frame_color: The striped grid's top layer. Defaults to
            :data:`STRIPED_GRID_COLOR`.
        pattern_color: Pattern top layer color. Defaults to a contrasting hue.

    Returns:
        ColorLayerAssignment with all colors resolved.

    """
    if text_color is None:
        text_color = Color(TEXT_COLOR)

    if frame_color is None:
        frame_color = Color(STRIPED_GRID_COLOR)

    if pattern_color is None:
        # A through-hole pattern has no top layer of its own, so this only
        # matters to a caller who has given the pattern something to colour.
        pattern_color = _contrast_hue(body_color, shift=0.67)

    return ColorLayerAssignment(
        body_color=body_color,
        text_color=text_color,
        frame_color=frame_color,
        pattern_color=pattern_color,
    )


def _contrast_hue(base: Color, shift: float) -> Color:
    """Shift the hue of a color for contrast."""
    import colorsys
    r, g, b, _ = base.rgba
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    h = (h + shift) % 1.0
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return Color([r, g, b])
