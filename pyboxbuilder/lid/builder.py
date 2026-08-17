# SPDX-License-Identifier: Apache-2.0
"""Lid decoration builders."""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from typing import TYPE_CHECKING, Any

from pyboxbuilder.enums import LabelMode, PatternType

if TYPE_CHECKING:
    from pyboxbuilder import Color


MIN_TEXT_HEIGHT_MM = 4.0
"""Shortest a label may print before it is skipped instead (FR-020).

Below this an FDM printer cannot hold the strokes of a letter apart, so the
label comes out as a smudge; skipping it leaves a clean lid instead.
"""

BORDER_MARGIN_MM = 5.0
"""Margin an auto-sized label keeps clear of the lid's edge."""


@dataclass(frozen=True)
class PatternBuilder:
    """Through-hole pattern configuration for a lid."""

    type: PatternType = PatternType.HEX
    """Which pattern to cut. See :class:`~pyboxbuilder.enums.PatternType`."""
    colors: tuple[Color, ...] = ()
    """Accent colours for the pattern's top layer, if any."""
    spacing: float | None = None
    """Cell size in mm; ``None`` derives it from the lid's shorter side."""


@dataclass(frozen=True)
class LidBuilder:
    """Lid decoration configuration.

    One of these usually describes a *style* rather than a single lid — the
    same frame, pattern and colours across a whole insert — so
    :meth:`titled` makes a copy carrying one box's text instead of repeating
    the style at every box (FR-000b)::

        LEAF = LidBuilder(label_mode=LabelMode.FRAMELESS, diagonal=True,
                          pattern=PatternBuilder(PatternType.HEX))
        ...
        project.box(BoxType.SLIDING, "Favor", lid=LEAF.titled("Favors"))
    """

    text: str | None = None
    """Label text; ``None`` leaves the lid unlabelled."""
    label_mode: LabelMode | None = None
    """Framed (border + hatching behind the text) or frameless (text only).

    ``None`` means :attr:`~pyboxbuilder.enums.LabelMode.FRAMED`. It is spelled
    as ``None`` rather than defaulted directly so a per-mode override can tell
    "I want framed" from "I said nothing about the frame" — see
    :meth:`for_mode`."""
    diagonal: bool | None = None
    """Run the text corner to corner rather than along the lid; ``None`` is no."""
    text_color: Color | None = None
    """Colour of the label text; ``None`` uses white."""
    frame_color: Color | None = None
    """Colour of the frame's top layer; ``None`` contrasts with the body."""
    pattern: PatternBuilder | None = None
    """Through-hole pattern, or ``None`` for a plain lid."""
    pattern_color: Color | None = None
    """Colour of the pattern's top layer; ``None`` contrasts with the body."""
    min_text_height_mm: float | None = None
    """Below this the label is skipped rather than printed illegibly (FR-020).

    ``None`` uses :data:`MIN_TEXT_HEIGHT_MM`."""
    border_margin_mm: float | None = None
    """Margin the auto-sized label keeps clear of the lid's edge; ``None`` uses
    :data:`BORDER_MARGIN_MM`."""
    mmu_label: LidBuilder | None = None
    """Fields to override for the multi-material export (see :meth:`for_mode`)."""
    single_label: LidBuilder | None = None
    """Fields to override for the single-colour export."""

    def titled(self, text: str, **overrides: Any) -> LidBuilder:
        """Return this lid style, carrying a particular box's text.

        Args:
            text: The label for this box.
            **overrides: Any other field to change for this box — usually a
                colour.

        Returns:
            A copy; the style it was made from is unchanged.

        """
        return replace(self, text=text, **overrides)

    @property
    def mode(self) -> LabelMode:
        """The label style, resolved."""
        return self.label_mode if self.label_mode is not None else LabelMode.FRAMED

    @property
    def is_diagonal(self) -> bool:
        """Whether the text runs corner to corner, resolved."""
        return bool(self.diagonal)

    @property
    def min_text_height(self) -> float:
        """The shortest printable label, resolved."""
        return (
            self.min_text_height_mm
            if self.min_text_height_mm is not None else MIN_TEXT_HEIGHT_MM
        )

    @property
    def border_margin(self) -> float:
        """The margin kept clear at the lid's edge, resolved."""
        return (
            self.border_margin_mm
            if self.border_margin_mm is not None else BORDER_MARGIN_MM
        )

    def for_mode(self, mode: str) -> LidBuilder:
        """Return this lid as it prints in one colour mode.

        A per-mode override carries **only the fields it sets**. That has to be
        decided by what the caller passed rather than by comparing against the
        field's default, which is what this used to do: a `single_label` asking
        for `LabelMode.FRAMED` was indistinguishable from one that said nothing,
        `diagonal=False` could not turn off a diagonal, and the margins were
        taken from the override whether it mentioned them or not.

        Args:
            mode: ``"mmu"`` or ``"single"``.

        Returns:
            The effective configuration; ``self`` when that mode sets nothing.

        """
        override = self.mmu_label if mode == "mmu" else self.single_label
        if override is None:
            return self
        return replace(self, **override._stated(), mmu_label=None, single_label=None)

    def _stated(self) -> dict[str, Any]:
        """Return the fields this override actually names.

        A `LidBuilder` used as an override is a sparse record: every field
        defaults to ``None``, so "not mentioned" is representable and distinct
        from every value the field can take. That is why `label_mode`,
        `diagonal` and the two margins are ``| None`` rather than carrying
        their defaults directly — the defaults live in the properties above.
        """
        return {
            f.name: getattr(self, f.name)
            for f in fields(self)
            if f.name not in ("mmu_label", "single_label")
            and getattr(self, f.name) is not None
        }

    def resolve_for_mode(self, mode: str) -> LidBuilder:
        """Return the deprecated alias for :meth:`for_mode`."""
        import warnings

        warnings.warn(
            "LidBuilder.resolve_for_mode() is deprecated; use for_mode().",
            DeprecationWarning, stacklevel=2,
        )
        return self.for_mode(mode)
