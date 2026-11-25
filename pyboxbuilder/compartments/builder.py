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
    cut: Cut | None = None
    """How this compartment's contents come out; ``None`` means no cut.

    One setting rather than three (FR-006). It used to be a flag to ask for a
    cut, a second to choose its kind and a third for its side — and the first
    two said the same thing twice, so `finger_scoop=True, finger_cut=SCOOP`
    was the way to ask for one scoop.
    """
    no_rotate: bool = False
    """Prevent the layout algorithm from rotating this compartment (e.g. directional card slots)."""
    is_card: bool = False
    """Whether this compartment holds cards, enforcing short-wall finger cutouts (FR-068)."""
    shape_file: str | None = None
    """Path to an SVG file defining the custom shape of the compartment cutout."""
    position: tuple[float, float] | None = None
    """Manual coordinate override (x, y) in mm within the interior frame."""
    count: int | None = None
    """Optional explicit count of game pieces stored in this compartment (for summaries & packing sheets)."""
    component: str | None = None
    """Optional declared inventory component name stored in this compartment."""
    allocates: tuple[tuple[str, int], ...] = ()
    """Optional explicit ``((component_name, qty), ...)`` allocations from the project inventory."""
    elements: tuple[CompartmentElement, ...] = ()
    """Physical game components nested inside this compartment (FR-004b).

    A compartment carrying elements is an *element pack*: the elements are laid
    out in the compartment's local frame and the pack's bounding box is what the
    box-level layout engine sees, so it packs like any other rectangle."""
    element_margin: float = 0.0
    """Clearance added around an element pack's bounding box when `size` is
    derived from the elements."""
    growable: bool = False
    """Whether this well's width/length may expand into leftover row slack (FR-004)."""

    def __post_init__(self) -> None:
        """Validate the ratio fields lie in (0.0, 1.0]."""
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
        """Return what this compartment demands of a box that has no size yet.

        Returns:
            ``(label, width, length, depth)`` in mm, or ``None`` when the well
            fills whatever it is given and so demands nothing — a box whose
            wells all fill needs an explicit size, and says so.

        """
        if self.fills_interior:
            return None
        if self.size is not None and self.size[0] is not None and self.size[1] is not None:
            return (self.label, float(self.size[0]), float(self.size[1]), self.depth or 0.0)
        if self.elements:
            from pyboxbuilder.compartments.element import elements_footprint

            ew, el = elements_footprint(self.elements, margin=self.element_margin)
            return (self.label, ew, el, self.depth or 0.0)
        return None

    def resolved(
        self,
        interior_w: float,
        interior_l: float,
        interior_h: float,
        siblings: int = 1,
        *,
        x_tracks: int | None = None,
        y_tracks: int | None = None,
    ) -> tuple[
        str, float, float, float,
        str | None, tuple[float, float] | None, tuple[CompartmentElement, ...],
    ]:
        """Return this compartment as the layout engine takes it.

        Args:
            interior_w: Box interior width in mm.
            interior_l: Box interior length in mm.
            interior_h: Box interior height in mm, used when ``depth`` is
                ``None`` — the well then runs to the box's floor.
            siblings: How many compartments share the interior, so a ratio can
                be read against the room left once the dividing walls are taken
                out (see :meth:`resolve_size`).
            x_tracks: Number of horizontal columns across the width (optional).
            y_tracks: Number of vertical rows along the length (optional).

        Returns:
            ``(label, width, length, depth, shape_file, position, elements)``.

        """
        width, length = self.resolve_size(
            interior_w, interior_l, siblings, x_tracks=x_tracks, y_tracks=y_tracks
        )
        return (
            self.label, width, length, self.resolve_depth(interior_h),
            self.shape_file, self.position, self.elements,
        )

    def resolve_depth(self, interior_h: float) -> float:
        """How deep this well is cut.

        Card compartments (``is_card=True``) always expand to fill ``interior_h``
        when the box grows taller (e.g. via vertical gap absorption), giving more
        room for cards/sleeves. Fixed-depth piece wells always keep their exact
        declared ``depth`` regardless of how tall the box becomes.

        Args:
            interior_h: The box interior's height in mm.

        Returns:
            Resolved well depth in mm.

        """
        if self.depth is None:
            return float(interior_h)
        if self.is_card:
            return max(float(self.depth), float(interior_h))
        return float(self.depth)

    def resolve_size(
        self,
        interior_w: float,
        interior_l: float,
        siblings: int = 1,
        *,
        x_tracks: int | None = None,
        y_tracks: int | None = None,
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
            x_tracks: Explicit column count across width; inferred from siblings when None.
            y_tracks: Explicit row count along length; inferred as 1 (or siblings for
                length-only ratios) when None.

        Returns:
            (width, length) in mm.

        """
        from pyboxbuilder.compartments.layout import WALL_SPACING_MM

        if x_tracks is None and y_tracks is None:
            if self.length_ratio is not None and self.width_ratio is None and self.size is None:
                xt, yt = 1, max(1, siblings)
            else:
                xt, yt = max(1, siblings), 1
        else:
            xt = max(1, x_tracks if x_tracks is not None else siblings)
            yt = max(1, y_tracks if y_tracks is not None else 1)

        total_cells = max(siblings, xt * yt)
        gutter = 0.0 if total_cells <= 1 else WALL_SPACING_MM
        room_w = max(0.0, interior_w - gutter * (xt + 1))
        room_l = max(0.0, interior_l - gutter * (yt + 1))

        if self.size is not None:
            raw_w, raw_l = self.size
            w = float(raw_w) if raw_w is not None else (room_w / xt)
            l = float(raw_l) if raw_l is not None else (room_l / yt)
        elif self.elements:
            # Element pack: the bounding box of the pack IS the compartment (FR-004b).
            from pyboxbuilder.compartments.element import elements_footprint

            w, l = elements_footprint(self.elements, margin=self.element_margin)
        else:
            # No size given: fill the room there is, sharing tracks across siblings.
            w = room_w / xt
            l = room_l / yt

        if self.width_ratio is not None:
            w = room_w * self.width_ratio
        if self.length_ratio is not None:
            l = room_l * self.length_ratio
            if self.width_ratio is None and self.size is None and not self.elements:
                w = max(0.0, interior_w - gutter * 2)
        elif self.width_ratio is not None and self.size is None:
            # Sized by width alone: the length is whatever is left across Y.
            l = max(0.0, interior_l - gutter * 2)

        import math

        return (
            math.floor((w + 1e-9) * 10.0) / 10.0,
            math.floor((l + 1e-9) * 10.0) / 10.0,
        )


def infer_ratio_tracks(compartments: tuple[CompartmentBuilder, ...] | list[CompartmentBuilder]) -> tuple[int, int]:
    """Infer ``(x_tracks, y_tracks)`` grid dimensions for a box's auto-placed compartments."""
    auto_comps = [cb for cb in compartments if cb.position is None]
    n = len(auto_comps)
    if n <= 1:
        return (1, 1)

    has_w = [cb for cb in auto_comps if cb.width_ratio is not None]
    has_l = [cb for cb in auto_comps if cb.length_ratio is not None]
    both = [cb for cb in auto_comps if cb.width_ratio is not None and cb.length_ratio is not None]

    if both and len(both) == n:
        w_sum = sum(cb.width_ratio for cb in both if cb.width_ratio is not None)
        l_sum = sum(cb.length_ratio for cb in both if cb.length_ratio is not None)
        return (max(1, round(l_sum)), max(1, round(w_sum)))

    if has_l and not has_w:
        return (1, n)

    return (n, 1)
