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
    """Resolve accent colors with sensible defaults.

    Args:
        body_color: The base box body color.
        text_color: Label text color. Defaults to Color("white").
        frame_color: Frame top layer color. Defaults to a contrasting hue.
        pattern_color: Pattern top layer color. Defaults to a third hue.

    Returns:
        ColorLayerAssignment with all colors resolved.
    """
    if text_color is None:
        text_color = Color("white")

    if frame_color is None:
        # Contrasting hue: shift by 120 degrees
        frame_color = _contrast_hue(body_color, shift=0.33)

    if pattern_color is None:
        # Third contrasting hue: shift by 240 degrees
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
