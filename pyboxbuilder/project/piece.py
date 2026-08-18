# SPDX-License-Identifier: Apache-2.0
"""Piece, ResolvedBox and Build class definitions."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pyboxbuilder.builders._base import BoxBuilder
    from pyboxbuilder.packing.layout import BoxPacking


@dataclass(frozen=True)
class Piece:
    """One printable piece of a project.

    Both :meth:`~pyboxbuilder.project.Project.show` and :meth:`~pyboxbuilder.project.Project.export` consume these, so a
    piece previewed and the same piece printed are the same solid.

    **The geometry is built on demand.** Everything that identifies a piece —
    its label, its size, where it sits, and the description it would be built
    from — is known without building it, and that is what decides whether an
    export needs to write it at all (FR-031). Building eagerly meant a re-export
    with nothing changed still paid for every box: 15 of Emberleaf's 21 seconds
    at draft precision, and minutes at the 256 facets an export actually uses,
    all spent on geometry the fingerprint was about to discard.
    """

    label: str
    """The box label this piece belongs to; a lid keeps its body's label."""
    kind: str
    """One of ``"body"``, ``"lid"`` or ``"spacer"``."""
    size: tuple[float, float, float]
    """The piece's declared ``(width, length, height)`` in mm."""
    position: tuple[float, float, float]
    """Where the piece sits inside the game box, in mm."""
    _build: Callable[[], Any | None]
    """Builds this piece's geometry. Call :attr:`solid` rather than this."""
    builder: BoxBuilder | None = None
    """The box builder this piece came from; ``None`` for a spacer tray."""

    @property
    def solid(self) -> Any | None:
        """The built geometry, in the piece's own local frame.

        Built on first use and kept, so asking twice costs once. ``None`` when
        the geometry backend was unavailable.

        Typed loosely because pybosl2 ships no `py.typed`, so a solid is
        untyped from here on however it is declared.
        """
        return self._build()

    @property
    def is_spacer(self) -> bool:
        """True when this piece is an auto-generated spacer tray."""
        return self.kind == "spacer"


@dataclass(frozen=True)
class ResolvedBox:
    """A box after validation and layout, before any geometry is cut.

    Split out so the checks run when the project is built and the CSG runs when
    something asks for it: a project that cannot be built must say so at
    :meth:`Project.build`, not later, when a caller happens to touch a solid.
    """

    builder: BoxBuilder
    """The box this came from."""
    box: Any | None
    """Its type implementation, or ``None`` for a type with no geometry."""
    spec: Any
    """The :class:`~pyboxbuilder.box.spec.BoxSpec` it will be built from."""
    interior: Any
    """Its interior frame."""
    compartments: Any | None
    """The resolved compartment layout, or ``None`` when it has none."""


@dataclass(frozen=True)
class Build:
    """Everything a project resolves to: its pieces and its packing."""

    pieces: tuple[Piece, ...]
    """Every body, lid and spacer, in project order."""
    packing: BoxPacking | None = None
    """The resolved :class:`BoxPacking`, or ``None`` for a standalone project."""

    def of_kind(self, *kinds: str) -> list[Piece]:
        """Return the pieces whose ``kind`` is any of ``kinds``."""
        return [p for p in self.pieces if p.kind in kinds]
