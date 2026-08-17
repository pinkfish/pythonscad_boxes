# SPDX-License-Identifier: Apache-2.0
"""Project class — top-level API entry point.

**One build path.** :meth:`Project.build` resolves the layout and builds every
body, lid and spacer. :meth:`Project.show` renders what it returns and
:meth:`Project.export` writes what it returns; neither builds geometry of its
own. That is the whole difference between the two — render or write — and it is
structural rather than a convention, because the alternative was two copies of
the build that drifted: the exported parts silently lost their rounding, their
per-side wall tops and their interior masks while the preview kept all three.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pyboxbuilder.enums import BoxType

if TYPE_CHECKING:
    from pybosl2 import Color

    from pyboxbuilder.builders._base import BoxBuilder
    from pyboxbuilder.export.result import ExportResult
    from pyboxbuilder.packing.layout import BoxPacking


@dataclass(frozen=True)
class Piece:
    """One printable piece of a project, built once.

    Both :meth:`Project.show` and :meth:`Project.export` consume these, so a
    piece previewed and the same piece printed are the same solid.
    """

    label: str
    """The box label this piece belongs to; a lid keeps its body's label."""
    kind: str
    """One of ``"body"``, ``"lid"`` or ``"spacer"``."""
    solid: Any | None
    """The built geometry in the piece's own local frame, or ``None`` when the
    geometry backend was unavailable.

    Typed loosely because pybosl2 ships no `py.typed`, so a solid is untyped
    from here on however it is declared."""
    size: tuple[float, float, float]
    """The piece's declared ``(width, length, height)`` in mm."""
    position: tuple[float, float, float]
    """Where the piece sits inside the game box, in mm."""
    builder: "BoxBuilder | None" = None
    """The box builder this piece came from; ``None`` for a spacer tray."""

    @property
    def is_spacer(self) -> bool:
        """True when this piece is an auto-generated spacer tray."""
        return self.kind == "spacer"


@dataclass(frozen=True)
class Build:
    """Everything a project resolves to: its pieces and its packing."""

    pieces: tuple[Piece, ...]
    """Every body, lid and spacer, in project order."""
    packing: "BoxPacking | None" = None
    """The resolved :class:`BoxPacking`, or ``None`` for a standalone project."""

    def of_kind(self, *kinds: str) -> list[Piece]:
        """The pieces whose ``kind`` is any of ``kinds``."""
        return [p for p in self.pieces if p.kind in kinds]


@dataclass
class Project:
    """Top-level game insert description.

    The single-import entry point for defining a board game insert.
    """

    name: str
    """Game name; becomes the output subdirectory."""
    game_box_size: tuple[float, float, float] | None = None
    """Outer game box dimensions [W, L, H] in mm. None = standalone boxes (no game box)."""
    wall_thickness: float = 2.0
    """Default wall thickness for all sub-boxes."""
    floor_thickness: float = 1.6
    """Default floor thickness."""
    lid_thickness: float = 2.0
    """Default lid thickness."""
    rounding: float | None = None
    """Edge radius for every box's exposed edges (FR-043/FR-044).

    ``None`` derives it per box as ``wall_thickness / 2``. ``0`` leaves
    every edge square.
    """
    inner_rounding: float | None = None
    """Edge radius where a partial lid grips the body (FR-044b).

    Applies to a cap's band and skirt cavity, and a slipover's body and sleeve
    cavity — both halves of the grip, so they nest. ``None`` derives it as half
    the outer radius.
    """
    gap_threshold: float = 10.0
    """Gaps <= this are absorbed by adjacent boxes."""
    min_spacer_dim: float = 15.0
    """Minimum spacer width/length before absorption."""
    min_spacer_height: float = 5.0
    """A spacer tray thinner than this on any axis is dropped as unprintable (FR-014)."""
    clearance_slack: float = 1.0
    """Clearance slack on each side of the game box in the X/Y directions (mm)."""
    board_thickness: float = 0.0
    """Thickness of the game board (mm).

    Reserved at the TOP of the box: the board sits on top of the sub-boxes and
    is the first thing out, so this is not a spacer gap."""
    generate_spacers: bool = True
    """Whether to automatically generate spacer boxes/trays to fill layout gaps."""
    box_defaults: dict | None = None
    """Defaults applied to every :meth:`box` call that does not say otherwise.

    Every keyword :meth:`box` accepts may be given here once instead of on each
    box — ``wall_thickness``, ``no_rotate``, ``color`` and the rest. An insert
    whose boxes all share a wall thickness or all decline rotation says so once
    (FR-000b)::

        Project("Earth", ..., box_defaults={"wall_thickness": 3.0})

    A value passed to :meth:`box` always wins over the default.
    """

    _boxes: list[BoxBuilder] = field(default_factory=list, init=False)
    _shared_groups: list = field(default_factory=list, init=False)
    piece_bounds: tuple = field(default_factory=tuple, init=False)
    """Bounding box of every exported piece, populated by `export()` (FR-027)."""

    def box(
        self,
        box_type: BoxType,
        label: str,
        *,
        size: tuple[float, float, float] | None = None,
        **kwargs,
    ) -> BoxBuilder:
        """Add a sub-box to the project.

        Args:
            box_type: Which lid mechanism the box uses. Selects the builder
                class, so the type-specific keywords available here follow from
                it.
            label: The box's name; used for file naming and by
                :meth:`arrange`.
            size: ``(width, length, height)`` in mm. ``None`` derives it from
                the compartments.
            **kwargs: Any field of the box's builder. Anything not given falls
                back to :attr:`box_defaults`, then to the field's own default.

        Returns:
            The type-specific :class:`BoxBuilder`, already registered on the
            project, so compartments and finger holes can be added to it.

        Raises:
            KeyError: If ``box_type`` has no registered builder.
            TypeError: If a keyword is not a field of that builder.
        """
        from pyboxbuilder.box.registry import BOX_TYPE_REGISTRY

        builder_cls = BOX_TYPE_REGISTRY[box_type]

        from dataclasses import fields as dataclass_fields

        known = {f.name for f in dataclass_fields(builder_cls)}
        values: dict[str, Any] = {"size": size}
        for name, value in (self.box_defaults or {}).items():
            if name in known:
                values[name] = value
        values.update(kwargs)

        unknown = sorted(set(values) - known)
        if unknown:
            valid = ", ".join(sorted(known))
            raise TypeError(
                f"{builder_cls.__name__} has no field(s) {', '.join(unknown)}. "
                f"Valid fields: {valid}"
            )

        builder = builder_cls(label=label, **values)
        self._boxes.append(builder)
        return builder

    def arrange(self, layout, origin: tuple[float, float, float] = (0.0, 0.0, 0.0)):
        """Position boxes from a declarative layout tree (T186).

        The alternative to hand-typed coordinates for densely packed inserts,
        where the packer cannot help: describe the structure with
        `columns`/`rows`/`stack` and let the sizes decide the positions.

        A box placed here is placed, so it is neither expanded nor rotated by
        the packer — the arrangement's arithmetic assumed the size it was given
        (FR-013c).

        Args:
            layout: A `pyboxbuilder.layout` group, or a single box label.
            origin: Where the arrangement's minimum corner goes.

        Returns:
            The `Arrangement`, so a caller can inspect the resolved extent.

        Raises:
            LayoutError: If the tree names an unknown box or places one twice.
            ValueError: If a named box has no explicit size, or the arrangement
                does not fit the game box.
        """
        from pyboxbuilder.layout import LayoutError
        from pyboxbuilder.layout import arrange as resolve

        # Size every box first, including the ones sized from their contents.
        # Those used to be skipped here, and the arrangement then reported them
        # as "not in the project" — so a box described by what goes in it,
        # which is how the library asks you to describe one, could not be
        # arranged at all.
        sizes = {b.label: self._min_size(b) for b in self._boxes}

        arrangement = resolve(layout, sizes, origin)

        if self.game_box_size is not None and not arrangement.fits(self.game_box_size):
            raise LayoutError(
                f"Arrangement is {arrangement.size[0]:.1f} x "
                f"{arrangement.size[1]:.1f} x {arrangement.size[2]:.1f} mm, "
                f"which does not fit the {self.game_box_size[0]:.1f} x "
                f"{self.game_box_size[1]:.1f} x {self.game_box_size[2]:.1f} mm game box."
            )

        by_label = {b.label: b for b in self._boxes}
        for label, position in arrangement.positions.items():
            object.__setattr__(by_label[label], "position", position)
        return arrangement

    # ------------------------------------------------------------------ build

    def build(self) -> Build:
        """Resolve the layout and build every piece of this project.

        The one build path. :meth:`show` renders what this returns and
        :meth:`export` writes it, so a previewed part and a printed part are
        the same solid — there is no second assembly of the geometry for one of
        them to fall behind in.

        Returns:
            A :class:`Build` carrying every body, lid and spacer, each in its
            own local frame with the position it occupies in the game box.

        Raises:
            ValueError: If a box can be sized neither explicitly nor from its
                compartments, if its compartments overflow its interior, or if
                its compartment ratios overflow.
            PackingError: If the boxes cannot be packed into the game box.
        """
        self._resolve_shared_compartments()

        pieces: list[Piece] = []

        if self.game_box_size is None:
            # Standalone: nothing is packed, so line the boxes up side by side
            # for a preview. There are no layers and no spacers.
            x = 0.0
            for builder in self._boxes:
                size = self._standalone_size(builder)
                pieces.extend(self._box_pieces(builder, (x, 0.0, 0.0)))
                x += size[0] + STANDALONE_GAP_MM
            return Build(pieces=tuple(pieces))

        packing = self._resolve_final_layout()
        positions = {p.label: tuple(p.position) for p in packing.placements}

        for builder in self._boxes:
            at = positions.get(builder.label, builder.position or (0.0, 0.0, 0.0))
            pieces.extend(self._box_pieces(builder, tuple(at)))

        spacers = self._spacer_placements(packing) if self.generate_spacers else []
        # The PDF draws the spacers alongside the boxes, so the packing carries
        # them: it is the one description of what ends up in the game box.
        packing.spacer_placements = spacers

        for spacer in spacers:
            pieces.append(
                Piece(
                    label=spacer.label,
                    kind="spacer",
                    solid=self._build_spacer_solid(spacer),
                    size=tuple(spacer.size),
                    position=tuple(spacer.position),
                )
            )

        return Build(pieces=tuple(pieces), packing=packing)

    def _box_pieces(self, builder, at: tuple[float, float, float]) -> list[Piece]:
        """The body and lid pieces for one box, at the position it packs to."""
        body, lid, size = self._build_box_solids(builder)
        pieces = [
            Piece(label=builder.label, kind="body", solid=body, size=size,
                  position=at, builder=builder)
        ]
        if self._has_lid(builder):
            pieces.append(
                Piece(label=builder.label, kind="lid", solid=lid, size=size,
                      position=at, builder=builder)
            )
        return pieces

    @staticmethod
    def _has_lid(builder) -> bool:
        """True when this box type produces a lid file at all."""
        from pyboxbuilder.box.registry import LIDLESS_BOX_TYPES

        return builder.box_type not in LIDLESS_BOX_TYPES

    def _resolve_shared_compartments(self) -> None:
        """Partition each shared compartment group across its boxes (FR-008a).

        Runs before anything is sized, so a preview and an export see the same
        compartments in the same boxes.

        Raises:
            ValueError: If a group cannot be partitioned across its boxes.
        """
        from pyboxbuilder.builders._base import Cut
        from pyboxbuilder.compartments.builder import CompartmentBuilder
        from pyboxbuilder.compartments.layout import pack_compartments_across_bins
        from pyboxbuilder.enums import FingerCut, ScoopSide

        for box_labels, comps in self._shared_groups:
            builders = [b for b in (self._by_label(x) for x in box_labels) if b is not None]
            if len(builders) < 2:
                continue

            bin_sizes = []
            for b in builders:
                wt = b.wall_thickness or self.wall_thickness
                if b.size is not None and b.size[0] is not None and b.size[1] is not None:
                    bin_sizes.append((b.size[0] - 2 * wt, b.size[1] - 2 * wt))
                else:
                    container = self.game_box_size or (0.0, 0.0, 0.0)
                    bin_sizes.append((container[0] - 2 * wt, container[1] - 2 * wt))

            packed_bins = pack_compartments_across_bins(comps, bin_sizes)
            if not packed_bins:
                raise ValueError(
                    f"Failed to partition shared compartments across boxes: {box_labels}"
                )

            for b, bin_items in zip(builders, packed_bins):
                object.__setattr__(b, "compartments", tuple(
                    CompartmentBuilder(
                        label=name, size=(w, l), depth=d,
                        cut=Cut(kind=FingerCut.THROUGH_FLOOR, side=ScoopSide.FRONT),
                    )
                    for name, w, l, d in bin_items
                ))

    def _by_label(self, label: str):
        """The builder with this label, or ``None``."""
        return next((b for b in self._boxes if b.label == label), None)

    # ------------------------------------------------------------------- show

    def show(
        self,
        show_lids: bool = False,
        remove_layers: int = 0,
        fn: int | None = None,
        fa: float | None = None,
        fs: float | None = None,
    ) -> None:
        """Preview the packed box layout interactively.

        Renders exactly what :meth:`export` writes — same build, same geometry
        — as separate solids at their packed positions. Each box is shown as
        its **own** solid, because a union carries one colour and would fuse
        touching boxes into an indivisible blob, hiding the seams a packing
        preview exists to show.

        Writes no files, and generates no layout PDF.

        Args:
            show_lids: Place each lid in its seated position as well. Off by
                default because lids cover the compartments and their
                neighbours. A shown lid carries its decoration and is drawn
                semi-transparent in a lighter shade of its box's colour so it
                reads as a separate piece.
            remove_layers: Omit the top N vertical layers of the packed
                layout, revealing what sits underneath — the live equivalent
                of the exploded PDF view. A box is removed when its top
                surface rises above the cut.
            fn: Fixed facets per circle for every curve in the preview.
                ``None`` (the default) defers to fa/fs, which sizes facets by
                how large each curve actually is — that is what keeps a preview
                responsive. Unlike :meth:`export`, this does *not* jump to
                export precision.
            fa: Minimum angle per fragment, in degrees (default 12).
            fs: Minimum fragment size, in mm (default 2).

        Raises:
            ValueError: If ``remove_layers`` is negative, or a precision
                setting is out of range.
        """
        from pyboxbuilder.precision import use

        with use(fn=fn, fa=fa, fs=fs):
            pieces = self.preview_pieces(show_lids=show_lids, remove_layers=remove_layers)

        for piece in pieces:
            solid = piece.solid
            try:
                solid = solid.color(piece.color)
            except (AttributeError, TypeError):
                pass  # Uncolourable geometry still previews, just uncoloured.
            solid.show()

    def preview_pieces(self, show_lids: bool = False, remove_layers: int = 0) -> list:
        """Build the list of separately-coloured solids :meth:`show` renders.

        Public because it is the cheap way to exercise the geometry: it packs
        the layout and builds every body, lid and spacer, but writes nothing
        and needs no render binary. A CI pass wants exactly that — the build
        path without the printable output — where :meth:`export` would spend
        its time tessellating 3MFs no one is going to print.

        Args:
            show_lids: Include each box's lid, lightened and semi-transparent.
            remove_layers: Number of top layers to omit.

        Returns:
            A list of :class:`pyboxbuilder.preview.PreviewPiece`, one per body,
            lid and spacer — never unioned together.

        Raises:
            ValueError: If ``remove_layers`` is negative.
        """
        from pyboxbuilder.preview import (
            PreviewPiece,
            lid_color,
            remove_top_layers,
            spacer_color,
            stable_color,
        )

        if remove_layers < 0:
            raise ValueError(f"remove_layers must be >= 0; got {remove_layers}")

        build = self.build()
        bodies_and_spacers = build.of_kind("body", "spacer")
        kept = {p.label for p in remove_top_layers(bodies_and_spacers, remove_layers)}

        def colour_for(piece: Piece) -> "Color":
            """A box's own colour when it declares one, else a stable hue."""
            if piece.is_spacer:
                return spacer_color(piece.label)
            declared = getattr(piece.builder, "color", None)
            return declared if declared is not None else stable_color(piece.label)

        out: list[PreviewPiece] = []
        for piece in build.pieces:
            if piece.label not in kept or piece.solid is None:
                continue
            if piece.kind == "lid" and not show_lids:
                continue

            solid = piece.solid
            if piece.kind == "lid":
                # Show the lid as it prints, decoration and all.
                solid = self._decorated_lid(piece, "mmu")[0] or solid

            colour = colour_for(piece)
            if piece.kind == "lid":
                colour = lid_color(colour)
            out.append(
                PreviewPiece(piece.label, solid.translate(list(piece.position)), colour, piece.kind)
            )
        return out

    # ------------------------------------------------------------------ sizing

    def _container(self) -> tuple[float, float, float]:
        """The game box's size, for the paths that require one.

        Returns:
            ``(width, length, height)`` in mm.

        Raises:
            ValueError: If this is a standalone project. Packing, spacers and
                the layout guide all need a container; without one they were
                indexing ``None`` and failing with a TypeError from three
                different lines.
        """
        if self.game_box_size is None:
            raise ValueError(
                f"Project '{self.name}' has no game_box_size, so there is "
                f"nothing to pack into. Standalone boxes export directly."
            )
        return self.game_box_size

    def _resolve_final_layout(self):
        """Resolve each box's final size and packed position.

        Computes minimum sizes (from an explicit size or the compartments),
        runs the 3D packer, and sets ``final_size`` on every builder. Returns
        the :class:`BoxPacking`, whose placements carry the final positions.
        """
        from pyboxbuilder.packing.layout import Placement, pack_boxes

        box_data = []
        resolved_min_sizes = {}
        manual_placements = []
        for builder in self._boxes:
            size = self._min_size(builder)
            resolved_min_sizes[builder.label] = size
            if builder.position is not None:
                # A box that has been placed — by hand or by `arrange()` — is
                # not the packer's to move, grow or turn. Expanding it would
                # push it into its neighbour, and rotating it would leave the
                # arrangement's arithmetic describing a box that no longer
                # exists. So placement decides both, and neither has to be
                # switched off at every call site (FR-000b).
                manual_placements.append(
                    Placement(label=builder.label, position=builder.position, size=size, rotation=False)
                )
            else:
                box_data.append({
                    "label": builder.label,
                    "size": size,
                    # `expandable` is the master switch: off means the box keeps
                    # the size it was given. The per-axis flags only narrow it.
                    "expandable": builder.expandable,
                    "expandable_width": builder.expandable and builder.expandable_width,
                    "no_rotate": builder.no_rotate,
                })

        # The board sits on top of the sub-boxes, so the packer only gets the
        # height below it — otherwise auto-placed boxes climb into the space
        # the board needs.
        slack = self.clearance_slack
        container = self._container()
        packing_container = (
            container[0] - 2 * slack,
            container[1] - 2 * slack,
            container[2] - self.board_thickness,
        )
        packing = pack_boxes(packing_container, box_data)

        shifted_placements = [
            Placement(
                label=p.label,
                position=(p.position[0] + slack, p.position[1] + slack, p.position[2]),
                size=p.size,
                rotation=p.rotation,
            )
            for p in packing.placements
        ]
        shifted_placements.extend(manual_placements)
        packing.placements = shifted_placements

        resolved_sizes = {p.label: p.size for p in packing.placements}
        for builder in self._boxes:
            val = resolved_sizes.get(builder.label) or resolved_min_sizes[builder.label]
            object.__setattr__(builder, "final_size", val)

        self._packing = packing
        return packing

    def _min_size(self, builder) -> tuple[float, float, float]:
        """The smallest this box may be: its explicit size, or its contents.

        Args:
            builder: The box to size. An explicit ``size`` wins; any axis left
                ``None`` there is filled in from the compartments.

        Returns:
            ``(width, length, height)`` in mm.

        Raises:
            ValueError: If the box has neither an explicit size nor
                compartments to derive one from.
        """
        from pyboxbuilder.compartments.layout import compute_min_box_size

        wt = builder.wall_thickness or self.wall_thickness
        ft = builder.floor_thickness or self.floor_thickness
        lt = builder.lid_thickness or self.lid_thickness

        def from_compartments() -> tuple[float, float, float]:
            measured = [
                fp for fp in (cb.min_footprint() for cb in builder.compartments)
                if fp is not None
            ]
            if not measured:
                fills = ", ".join(cb.label for cb in builder.compartments)
                raise ValueError(
                    f"Box '{builder.label}' has no size, and its compartments "
                    f"({fills}) all fill whatever they are given — so there is "
                    f"nothing to derive one from. Give the box a size=(w, l, h), "
                    f"or give a compartment a size=(w, l)."
                )
            bounds = {}
            if self.game_box_size is not None:
                bounds = {
                    "max_w": self.game_box_size[0] - 2 * wt,
                    "max_l": self.game_box_size[1] - 2 * wt,
                }  # narrowed by the check above
            return compute_min_box_size(measured, wt, ft, lt, **bounds)

        if builder.size is not None:
            size = list(builder.size)
            if None in size:
                derived = from_compartments()
                size = [axis if axis is not None else derived[i] for i, axis in enumerate(size)]
            return tuple(size)
        if builder.compartments:
            return from_compartments()
        raise ValueError(
            f"Box '{builder.label}' has no explicit size and no "
            f"compartments — at least one is required."
        )

    def _standalone_size(self, builder) -> tuple[float, float, float]:
        """Resolve a standalone box's size and record it as its ``final_size``.

        Standalone boxes are never packed, so nothing else would set
        ``final_size``.

        Args:
            builder: The box builder to size.

        Returns:
            The resolved ``(width, length, height)`` in mm.

        Raises:
            ValueError: If the box has neither an explicit size nor
                compartments to derive one from.
        """
        size = self._min_size(builder)
        object.__setattr__(builder, "final_size", size)
        return size

    # -------------------------------------------------------------- geometry

    def _build_box_solids(self, builder):
        """Build a box's body and lid solids from its resolved final size.

        Returns ``(body, lid, size)``; ``body``/``lid`` are ``None`` when the
        box type produced no geometry (or pybosl2 is unavailable).

        Raises:
            ValueError: If the compartments overflow the interior, or their
                ratios do.
        """
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
        from pyboxbuilder.box.spec import build_spec
        from pyboxbuilder.compartments.layout import layout_compartments

        size = builder.final_size
        spec = build_spec(self, builder, size)
        interior = spec.interior()

        self._check_ratios(builder)

        siblings = len(builder.compartments)
        comp_data = [
            cb.resolved(interior.width, interior.length, interior.height, siblings)
            for cb in builder.compartments
        ]

        box_cls = BOX_IMPL_REGISTRY.get(builder.box_type)
        if box_cls is None:
            return None, None, size

        box = box_cls()
        spec = spec.with_wall_tops(box)

        comp_layout = None
        if comp_data:
            # A well sized *from* the interior must not then be turned against
            # it: its width was derived on the box's width axis, so rotating it
            # asks the length to hold a number computed for the width.
            no_rotate_labels = {
                cb.label for cb in builder.compartments
                if cb.no_rotate or cb.derives_size
            }
            comp_layout = layout_compartments(
                interior, comp_data, no_rotate_labels=no_rotate_labels
            )
            if comp_layout.overflow:
                raise ValueError(
                    f"Compartments do not fit in box '{builder.label}' "
                    f"interior ({interior.width}x{interior.length})"
                )

        body = lid = None
        try:
            body = box.build_body(spec)
            lid = box.build_lid(spec)

            # A lidded box leaves its rim square so the lid can seal against
            # it; the lid carries the rounding for the closed box's top and
            # upper corners instead (FR-043). Only the edges this type leaves
            # on the outside, and never more than half the lid's thickness —
            # the rest is what the lid is supported and located by.
            if lid is not None:
                from pyboxbuilder.rounding import lid_rounding, round_edges

                lid = round_edges(
                    lid, list(size), lid_rounding(spec), box.lid_rounded_edges(spec)
                )

            if comp_layout is not None and body is not None:
                from pyboxbuilder.compartments.carve import build_contents

                contents = build_contents(
                    comp_layout.placements, interior,
                    {cb.label: cb for cb in builder.compartments},
                    top_z=size[2],
                    default_side=box.preferred_scoop_side(spec),
                    wall_tops=spec.wall_tops,
                    mask=box.interior_mask(spec),
                )
                if contents is not None:
                    body = body - contents
        except ImportError:
            pass

        return body, lid, size

    def _check_ratios(self, builder) -> None:
        """Reject compartment ratios that overflow the interior (FR-003a).

        Raises:
            ValueError: If the width or length ratios sum above 1.0, naming
                each compartment that contributed.
        """
        for axis, attr in (("width", "width_ratio"), ("length", "length_ratio")):
            total = sum(getattr(cb, attr) or 0 for cb in builder.compartments)
            if total > 1.0:
                over = ", ".join(
                    f"{cb.label}: {getattr(cb, attr)}"
                    for cb in builder.compartments if getattr(cb, attr)
                )
                raise ValueError(
                    f"Box '{builder.label}' compartment {axis} ratios sum to "
                    f"{total:.2f} (> 1.0): {over}"
                )

    def _spacer_placements(self, packing) -> list:
        """Derive the spacer trays that fill the gaps in a packed layout.

        Args:
            packing: The resolved :class:`BoxPacking` whose placements the
                leftover space is measured around.

        Returns:
            The spacer placements, after the sweep → merge → shrink → filter
            pass (FR-014a/b/c). Empty when no gap survives the minimums.
        """
        from pyboxbuilder.packing.spacer import generate_spacer_placements

        # Effective container: subtract the board thickness from the height so
        # the board area stays reserved rather than being filled with a spacer.
        container = self._container()
        effective_container = (
            container[0],
            container[1],
            container[2] - self.board_thickness,
        )
        return generate_spacer_placements(
            effective_container,
            packing.placements,
            clearance=self.clearance_slack,
            min_dim=self.min_spacer_height,
        )

    def _build_spacer_solid(self, spacer):
        """Build one spacer tray's geometry in its own local frame.

        Args:
            spacer: A spacer placement carrying ``label``, ``size`` and an
                optional rectilinear ``path`` footprint.

        Returns:
            The built solid, or ``None`` when the geometry could not be built
            (pybosl2 unavailable, or a degenerate footprint).
        """
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
        from pyboxbuilder.box.spec import BoxSpec

        try:
            # An L/T/U-shaped leftover is a PathBox; a plain rectangle is a
            # NoLidBox tray.
            spacer_cls = BOX_IMPL_REGISTRY.get(BoxType.PATH if spacer.path else BoxType.NO_LID)
            if spacer_cls is None:
                return None
            spec = BoxSpec(
                label=spacer.label,
                width=spacer.size[0],
                length=spacer.size[1],
                height=spacer.size[2],
                wall_thickness=self.wall_thickness,
                floor_thickness=self.floor_thickness,
                lid_thickness=0.0,
                path=tuple(spacer.path or ()),
                rounding=self.rounding,
                rim_free=True,
                # A spacer is dead fill: it has no contents to reach into, so
                # it takes none of the automatic grips a tray gets.
                auto_finger_holes=False,
            )
            return spacer_cls().build_body(spec)
        except Exception:
            return None

    def _decorated_lid(self, piece: Piece, mode: str):
        """One lid as it prints in a colour mode.

        Args:
            piece: The lid piece to decorate.
            mode: ``"mmu"`` or ``"single"``.

        Returns:
            ``(solid, inserts)`` — the decorated lid and its coloured positive
            inserts, or ``(piece.solid, None)`` when there is nothing to apply.
        """
        from pyboxbuilder.lid.decorate import decorate_lid

        builder = piece.builder
        if piece.solid is None or builder is None or builder.lid is None:
            return piece.solid, None
        try:
            decorated = decorate_lid(
                piece.solid, builder.lid,
                builder.lid_thickness or self.lid_thickness, mode,
                body_color=builder.color,
            )
            return decorated.solid, decorated.inserts or None
        except ImportError:
            return piece.solid, None

    # ----------------------------------------------------------------- export

    def export(
        self,
        out_dir: str | Path,
        fn: int | None = None,
        fa: float | None = None,
        fs: float | None = None,
    ) -> ExportResult:
        """Write every piece of this project, and the layout PDF.

        Writes exactly what :meth:`show` renders — the same :meth:`build` —
        so the only difference between previewing and exporting is that this
        one puts the result on disk.

        Args:
            out_dir: Directory to write into; files land under
                ``{out_dir}/{project name}/mmu/`` and ``.../single/``.
            fn: Fixed facets per circle for every curve in the exported
                geometry. ``None`` (the default) uses
                :data:`~pyboxbuilder.precision.EXPORT_FN` — an export is what
                gets printed, so it is built at full precision. Pass a smaller
                value for a quick throwaway build.
            fa: Minimum angle per fragment, in degrees (default 12).
            fs: Minimum fragment size, in mm (default 2).

        Returns:
            An :class:`ExportResult` listing the files written and skipped.

        Raises:
            ValueError: If a box cannot be sized, or a precision setting is
                out of range.
            PackingError: If the boxes cannot be packed into the game box.
        """
        from pyboxbuilder.export.exporter import BoxExporter
        from pyboxbuilder.export.result import ExportResult
        from pyboxbuilder.precision import export_facets, use

        with use(fn=export_facets() if fn is None else fn, fa=fa, fs=fs):
            build = self.build()

            exporter = BoxExporter(out_dir, self.name)
            exporter.delete_stale(
                "spacer_", {p.label for p in build.of_kind("spacer")}
            )

            for piece in build.pieces:
                for mode in ("mmu", "single"):
                    solid, inserts = (
                        self._decorated_lid(piece, mode)
                        if piece.kind == "lid" else (piece.solid, None)
                    )
                    exporter.write_piece(
                        piece.label,
                        "body" if piece.is_spacer else piece.kind,
                        mode, solid, inserts, size=piece.size,
                        fingerprint=self._fingerprint(piece, mode),
                    )

            if build.packing is not None:
                self._write_layout_pdf(build, out_dir, exporter)

        self.piece_bounds = tuple(exporter.state.bounds)
        return ExportResult(
            written=tuple(exporter.state.written),
            skipped=tuple(exporter.state.skipped),
            total_files=len(exporter.state.written) + len(exporter.state.skipped),
        )

    def _fingerprint(self, piece: Piece, mode: str) -> str:
        """A hash of everything that decides this piece's geometry.

        What makes a file worth rewriting is a change in the description it was
        built from, and that is knowable exactly — where comparing the meshes
        is not. Two runs of an unchanged project produce identical fingerprints
        and no writes; a boolean solver that retriangulates a complex mesh
        differently between runs no longer reads as a change (FR-031).

        Args:
            piece: The piece being written.
            mode: ``"mmu"`` or ``"single"`` — the two differ in geometry, so
                they fingerprint separately.

        Returns:
            A hex SHA-256 digest.
        """
        from pyboxbuilder.box.spec import describe
        from pyboxbuilder.packing.cache import cache_key
        from pyboxbuilder.precision import describe as describe_precision

        return cache_key({
            "kind": piece.kind,
            "label": piece.label,
            "mode": mode,
            "size": list(piece.size),
            "precision": describe_precision(),
            "project": {
                "wall_thickness": self.wall_thickness,
                "floor_thickness": self.floor_thickness,
                "lid_thickness": self.lid_thickness,
                "rounding": self.rounding,
                "inner_rounding": self.inner_rounding,
            },
            "box": describe(piece.builder) if piece.builder is not None else None,
        })

    def _delete_stale_spacers(self, out_dir: str | Path, spacer_placements: list) -> None:
        """Delete orphaned spacer 3MF files that no longer match a spacer.

        Args:
            out_dir: Root output directory.
            spacer_placements: The current set of spacer placements.
        """
        from pyboxbuilder.export.exporter import BoxExporter

        BoxExporter(out_dir, self.name).delete_stale(
            "spacer_", {sp.label for sp in spacer_placements}
        )

    def _write_layout_pdf(self, build: Build, out_dir: str | Path, exporter) -> None:
        """Generate the packing guide PDF, if the layout changed (FR-034)."""
        if not self._boxes or build.packing is None:
            return
        try:
            from pyboxbuilder.export.layout_pdf import (
                generate_layout_pdf,
                should_regenerate_layout,
            )

            pdf_path = Path(out_dir) / self.name / "layout.pdf"
            if should_regenerate_layout(build.packing, pdf_path):
                result = generate_layout_pdf(
                    build.packing, pdf_path, self.name, self._container(),
                    box_builders=self._boxes,
                )
                if result:
                    exporter.state.written.append(f"{self.name}/layout.pdf")
        except Exception:
            pass  # PDF is best-effort; don't block export

    # ------------------------------------------------------------ compartments

    def pack_compartments_across_bins(
        self,
        compartments: list[tuple[str, float, float, float]],
        bin_sizes: list[tuple[float, float]],
        wall_spacing: float = 2.0,
    ) -> list[list[tuple[str, float, float, float]]] | None:
        """Partitions compartments across multiple bin interior footprints using backtracking shelf packing."""
        from pyboxbuilder.compartments.layout import pack_compartments_across_bins

        return pack_compartments_across_bins(compartments, bin_sizes, wall_spacing)

    def share_compartments(
        self,
        boxes: list[str],
        compartments: list[tuple[str, float, float, float]],
    ) -> None:
        """Registers a group of compartments to be dynamically partitioned across the given box labels."""
        self._shared_groups.append((boxes, compartments))


STANDALONE_GAP_MM = 10.0
"""Gap left between standalone boxes when they are lined up for a preview."""
