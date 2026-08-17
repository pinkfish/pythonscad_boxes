# SPDX-License-Identifier: Apache-2.0
"""Compartment builder dataclass."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyboxbuilder.builders._base import Cut
from pyboxbuilder.compartments.element import CompartmentElement


@dataclass(frozen=True)
class CompartmentBuilder:
    """Configuration for a single interior compartment.

    Size can be specified as absolute millimetres (size=) or as
    ratios of the box interior (width_ratio=, length_ratio=). Ratios
    must be in range (0.0, 1.0]. At least one sizing mode is required.
    """

    label: str
    """Compartment identifier."""
    size: tuple[float, float] | None = None
    """Footprint [W, L] in mm. Required if width_ratio/length_ratio not set."""
    width_ratio: float | None = None
    """Fraction of box interior width (0.0 < ratio <= 1.0)."""
    length_ratio: float | None = None
    """Fraction of box interior length (0.0 < ratio <= 1.0)."""
    depth: float | None = None
    """Well depth in mm. ``None`` runs the well to the box's floor.

    Filling the interior is what a well normally does, so it is what happens
    when nothing is said (FR-000). The alternative was a fixed 10mm, which is
    right for no box in particular and quietly wrong for every deep one.
    """
    rounded_corners: float = 0.0
    """Corner radius in mm. Prefer `holds_pieces`, which derives it."""
    holds_pieces: bool = False
    """Whether this well holds loose pieces that have to be picked out.

    Off by default, which means **square corners and a square floor**. Rounding
    is opt-in rather than opt-out because most wells are shaped by what they
    hold — a card slot, a token silhouette, a board recess — and softening
    those changes a fit rather than improving it. Setting this marks the well
    as a tray: its corners and floor round to ``depth × 2/3`` so a finger can
    sweep a piece up the curve and out (FR-044f).
    """
    cut: "Cut | None" = None
    """How this compartment's contents come out; ``None`` means no cut.

    One setting rather than three (FR-006). It used to be a flag to ask for a
    cut, a second to choose its kind and a third for its side — and the first
    two said the same thing twice, so `finger_scoop=True, finger_cut=SCOOP`
    was the way to ask for one scoop.
    """
    no_rotate: bool = False
    """Prevent the layout algorithm from rotating this compartment (e.g. directional card slots)."""
    shape_file: str | None = None
    """Path to an SVG file defining the custom shape of the compartment cutout."""
    position: tuple[float, float] | None = None
    """Manual coordinate override (x, y) in mm within the interior frame."""
    elements: tuple[CompartmentElement, ...] = ()
    """Physical game components nested inside this compartment (FR-004b).

    A compartment carrying elements is an *element pack*: the elements are laid
    out in the compartment's local frame and the pack's bounding box is what the
    box-level layout engine sees, so it packs like any other rectangle."""
    element_margin: float = 0.0
    """Clearance added around an element pack's bounding box when `size` is
    derived from the elements."""

    def __post_init__(self) -> None:
        for name, val in [("width_ratio", self.width_ratio), ("length_ratio", self.length_ratio)]:
            if val is not None and not (0.0 < val <= 1.0):
                raise ValueError(
                    f"Compartment '{self.label}' {name}={val} "
                    f"must be in range (0.0, 1.0]."
                )

    @property
    def fills_interior(self) -> bool:
        """True when this well takes whatever footprint the box has left.

        A well with no size, no ratio and no elements is one the user did not
        want to measure — the common case of "one well, the whole box".
        """
        return (
            self.size is None
            and self.width_ratio is None
            and self.length_ratio is None
            and not self.elements
        )

    @property
    def derives_size(self) -> bool:
        """True when this well's footprint comes from the box, not the caller.

        A ratio or a bare fill is measured on the interior's own axes, so the
        layout must not rotate it afterwards — that would ask the length to
        hold a number worked out for the width.
        """
        return (
            self.fills_interior
            or self.width_ratio is not None
            or self.length_ratio is not None
        )

    def min_footprint(self) -> tuple[str, float, float, float] | None:
        """What this compartment demands of a box that has no size yet.

        Returns:
            ``(label, width, length, depth)`` in mm, or ``None`` when the well
            fills whatever it is given and so demands nothing — a box whose
            wells all fill needs an explicit size, and says so.
        """
        if self.fills_interior or self.size is None:
            return None
        return (self.label, self.size[0], self.size[1], self.depth or 0.0)

    def resolved(
        self, interior_w: float, interior_l: float, interior_h: float,
        siblings: int = 1,
    ) -> tuple:
        """This compartment as the layout engine takes it.

        Args:
            interior_w: Box interior width in mm.
            interior_l: Box interior length in mm.
            interior_h: Box interior height in mm, used when ``depth`` is
                ``None`` — the well then runs to the box's floor.
            siblings: How many compartments share the interior, so a ratio can
                be read against the room left once the dividing walls are taken
                out (see :meth:`resolve_size`).

        Returns:
            ``(label, width, length, depth, shape_file, position, elements)``.
        """
        width, length = self.resolve_size(interior_w, interior_l, siblings)
        return (
            self.label, width, length, self.resolve_depth(interior_h),
            self.shape_file, self.position, self.elements,
        )

    def resolve_depth(self, interior_h: float) -> float:
        """How deep this well is cut.

        Args:
            interior_h: The box interior's height in mm.

        Returns:
            The declared depth, or the full interior height when none was
            given — a well with nothing said about it goes to the floor.
        """
        return float(self.depth) if self.depth is not None else float(interior_h)

    def resolve_size(
        self, interior_w: float, interior_l: float, siblings: int = 1
    ) -> tuple[float, float]:
        """Resolve absolute size from ratios and/or absolute dimensions.

        A **ratio is a share of the room compartments actually have**, not of
        the raw interior: the auto-layout puts a wall's worth of spacing before,
        between and after them, so two wells asking for half each have to share
        `interior - 3 × spacing`. Read against the raw interior instead, ratios
        summing to exactly 1.0 — which FR-003a explicitly permits — overflowed
        every time, and the only way to make them fit was to guess the layout's
        spacing at the call site (FR-000b).

        Args:
            interior_w: Box interior width in mm.
            interior_l: Box interior length in mm.
            siblings: How many compartments share the interior. One well takes
                the interior whole, since the layout gives a lone compartment no
                spacing at all.

        Returns:
            (width, length) in mm.
        """
        from pyboxbuilder.compartments.layout import WALL_SPACING_MM

        # The layout runs compartments along the width, so that axis carries a
        # gutter before, between and after them — `siblings + 1` of them. The
        # length axis only ever has the two outer gutters, whatever the count.
        # A lone compartment gets none at all: the layout sits it flush.
        gutter = 0.0 if siblings <= 1 else WALL_SPACING_MM
        room_w = max(0.0, interior_w - gutter * (siblings + 1))
        room_l = max(0.0, interior_l - gutter * 2)
        if self.size is not None:
            w, l = self.size
        elif self.elements:
            # Element pack: the bounding box of the pack IS the compartment (FR-004b).
            from pyboxbuilder.compartments.element import elements_footprint

            w, l = elements_footprint(self.elements, margin=self.element_margin)
        else:
            # No size given: fill the room there is, sharing the width with any
            # siblings so a row of unsized wells divides the box evenly.
            w = room_w / max(1, siblings)
            l = room_l

        if self.width_ratio is not None:
            w = room_w * self.width_ratio
        if self.length_ratio is not None:
            l = room_l * self.length_ratio
        elif self.width_ratio is not None and self.size is None:
            # Sized by width alone: the length is whatever is left.
            l = room_l

        return (round(w, 1), round(l, 1))
