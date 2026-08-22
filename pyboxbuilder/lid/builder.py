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

LID_BORDER_MM = 8.0
"""Solid margin around everything on a lid — its pattern and its label alike.

The border is what the lid is picked up and located by, and on a sliding lid it
is what rides in the grooves, so it has to survive whatever is put on the face.
**One number** covers both: a label set to a different margin from the pattern
reads as a mistake, because what a viewer sees is a single band of plain lid
and one thing crossing it.
"""

LABEL_INSET_MM = 2.0
"""How far the label sits *inside* the lid's border, beyond the border itself.

The border is a band of plain lid, and a label that runs to its inner edge
reads as though it is touching the pattern rather than sitting in a space of
its own. Two millimetres is enough to separate them without shrinking the text
noticeably — on a card lid it costs about half a millimetre of cap height.
"""

BORDER_MARGIN_MM = LID_BORDER_MM + LABEL_INSET_MM
"""Margin an auto-sized label keeps clear of the lid's edge.

The lid's border plus the label's own inset, so the text sits inside the band
the pattern stops at rather than level with it."""

PATTERN_BORDER_MM = LID_BORDER_MM
"""Solid margin left around a lid's pattern, when nothing else says."""


@dataclass(frozen=True)
class PatternBuilder:
    """Through-hole pattern configuration for a lid.

    A pattern is specified by the **pitch** between holes and the **web** left
    between them. The web is the one with a right answer — it is what prints,
    and what carries the lid — so it is the one to state; the hole size follows
    from the two.
    """

    type: PatternType = PatternType.HEX
    """Which pattern to cut. See :class:`~pyboxbuilder.enums.PatternType`."""
    colors: tuple[Color, ...] = ()
    """Accent colours for the pattern's top layer, if any."""
    spacing: float | None = None
    """Centre-to-centre distance between holes, in mm.

    ``None`` derives it from the area being filled — an eighth of its shorter
    side, never below 5mm — so the same pattern reads the same on a token lid
    and a card lid."""
    web: float | None = None
    """Material left between neighbouring holes, in mm.

    ``None`` uses :data:`~pyboxbuilder.lid.pattern.DEFAULT_WEB_MM`. Raising it
    thickens the ribs without changing the pitch; the holes shrink to make
    room."""
    border: float | None = None
    """Solid margin around the whole pattern, in mm.

    ``None`` uses :data:`PATTERN_BORDER_MM`. ``0`` runs the pattern to the
    lid's edge, which is rarely what a lid wants — see that constant."""

    @property
    def border_width(self) -> float:
        """The border, resolved."""
        return PATTERN_BORDER_MM if self.border is None else max(0.0, self.border)


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

    Examples:
        A frameless diagonal label on a hex-patterned lid:

        .. pythonscad-example::

            project = Project("FancyGame", game_box_size=(300, 200, 80))
            STYLE = LidBuilder(
                label_mode=LabelMode.FRAMELESS,
                diagonal=True,
                pattern=PatternBuilder(PatternType.HEX, spacing=10.0),
            )
            project.box(
                BoxType.SLIDING, "Treasure", size=(90, 70, 40),
                lid=STYLE.titled("Treasure", text_color=Color("gold")),
            )
            project.show(only="Treasure")

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
    """Colour the lettering is inlaid in; ``None`` uses black (FR-022).

    A label is read against a lid whose colour is the game's choice, so the
    default is the one colour that reads against all of them."""
    frame_color: Color | None = None
    """Colour the framed label's **striped grid** is inlaid in; ``None`` uses
    light grey.

    The grid is a texture behind the lettering, not a second label. What sits
    *behind* both is the box's own material — it is never cut, so it needs no
    colour here (FR-022)."""
    pattern: PatternBuilder | None = None
    """Through-hole pattern, or ``None`` for a plain lid."""
    pattern_color: Color | None = None
    """Colour of the pattern's top layer; ``None`` contrasts with the body."""
    logo: Any | None = None
    """Path to the SVG logo, a Bosl2Solid, or a callable representing the custom lid logo."""
    logo_color: Color | None = None
    """Colour the logo is inlaid in; ``None`` uses black."""
    min_text_height_mm: float | None = None
    """Below this the label is skipped rather than printed illegibly (FR-020).

    ``None`` uses :data:`MIN_TEXT_HEIGHT_MM`."""
    border_margin_mm: float | None = None
    """Margin the auto-sized label keeps clear of the lid's edge; ``None`` uses
    :data:`BORDER_MARGIN_MM`."""
    label_clearance_mm: float | None = None
    """Solid margin kept around the **lettering** where a pattern meets it.

    ``None`` uses :data:`~pyboxbuilder.lid.decorate.LABEL_CLEARANCE_MM`, which
    is ``0``: the holes stop at the glyphs, so the letters read as letters and
    not as letters on a plaque. They keep their support either way — the
    keep-out is the glyph outline, and the label is inlaid into the lid rather
    than perched on it. Raise it for a lid whose pattern is coarse enough that
    a stroke would otherwise finish on the very edge of a hole."""
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
    def label_clearance(self) -> float:
        """The margin kept around the lettering, resolved."""
        from pyboxbuilder.lid.decorate import LABEL_CLEARANCE_MM

        return (
            self.label_clearance_mm
            if self.label_clearance_mm is not None else LABEL_CLEARANCE_MM
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
