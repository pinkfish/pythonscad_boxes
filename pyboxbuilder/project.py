# SPDX-License-Identifier: Apache-2.0
"""Project class — top-level API entry point.

**One build path.** :meth:`Project.build` resolves the layout and builds every
body, lid and spacer. :meth:`~pyboxbuilder.project.Project.show` renders what it returns and
:meth:`~pyboxbuilder.project.Project.export` writes what it returns; neither builds geometry of its
own. That is the whole difference between the two — render or write — and it is
structural rather than a convention, because the alternative was two copies of
the build that drifted: the exported parts silently lost their rounding, their
per-side wall tops and their interior masks while the preview kept all three.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from contextlib import suppress
from dataclasses import dataclass, field
from functools import cache, partial
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pyboxbuilder.enums import BoxType

if TYPE_CHECKING:
    from pybosl2 import Color
    from pybosl2.shapes3d import Bosl2Solid

    from pyboxbuilder.builders._base import BoxBuilder
    from pyboxbuilder.export.exporter import BoxExporter, PieceBounds
    from pyboxbuilder.export.result import ExportResult
    from pyboxbuilder.layout import Arrangement, Node
    from pyboxbuilder.packing.layout import BoxPacking, Placement
    from pyboxbuilder.preview import PreviewPiece


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


@dataclass
class Project:
    """Top-level game insert description.

    The single-import entry point for defining a board game insert.

    Examples:
        A two-box insert previewed as separate solids:

        .. pythonscad-example::

            p = Project("Cards", game_box_size=(300, 300, 80))
            p.box(BoxType.SLIDING, "Cards", size=(120, 70, 50))
            p.box(BoxType.NO_LID, "Tokens", size=(80, 60, 30))
            p.show()

        Four equal wells sharing a box's room, sized by ratio:

        .. pythonscad-example::

            p = Project("Divided", game_box_size=(200, 150, 60))
            box = p.box(BoxType.NO_LID, "Sorted", size=(100, 80, 30))
            for i in range(4):
                box.compartment(f"Slot{i + 1}", width_ratio=0.25)
            p.show()

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
    box_defaults: dict[str, Any] | None = None
    """Defaults applied to every :meth:`box` call that does not say otherwise.

    Every keyword :meth:`box` accepts may be given here once instead of on each
    box — ``wall_thickness``, ``no_rotate``, ``color`` and the rest. An insert
    whose boxes all share a wall thickness or all decline rotation says so once
    (FR-000b)::

        Project("Earth", ..., box_defaults={"wall_thickness": 3.0})

    A value passed to :meth:`box` always wins over the default.
    """

    _boxes: list[BoxBuilder] = field(default_factory=list, init=False)
    _shared_groups: list[tuple[list[str], list[tuple[str, float, float, float]]]] = (
        field(default_factory=list, init=False)
    )
    piece_bounds: tuple[PieceBounds, ...] = field(default_factory=tuple, init=False)
    """Bounding box of every exported piece, populated by `export()` (FR-027)."""

    def box(
        self,
        box_type: BoxType,
        label: str,
        *,
        size: tuple[float, float, float] | None = None,
        **kwargs: Any,
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

        Examples:
            Add a sliding card box, then preview it on its own:

            .. pythonscad-example::

                p = Project("Cards", game_box_size=(300, 300, 80))
                p.box(BoxType.SLIDING, "Cards", size=(120, 70, 50))
                p.show(only="Cards")

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

    def arrange(
        self, layout: Node, origin: tuple[float, float, float] = (0.0, 0.0, 0.0)
    ) -> Arrangement:
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

        Examples:
            An arrangement written down instead of measured:

            .. pythonscad-example::

                project = Project("BigGame", game_box_size=(300, 200, 80))
                project.box(BoxType.SLIDING, "CardBox", size=(110, 75, 50))
                project.box(BoxType.CAP, "TokenBox", size=(60, 50, 30))
                project.box(BoxType.CAP, "DiceBox", size=(60, 50, 30))
                project.box(BoxType.FILAMENT_HINGE, "BitBox", size=(80, 60, 40))
                project.arrange(columns(
                    "CardBox",
                    stack("TokenBox", "DiceBox"),
                    "BitBox",
                ))
                project.show()

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
        """Resolve the layout and describe every piece of this project.

        The one build path. :meth:`show` renders what this returns and
        :meth:`export` writes it, so a previewed part and a printed part are
        the same solid — there is no second assembly of the geometry for one of
        them to fall behind in.

        Resolving the layout is eager, because every piece's size and position
        depend on every other's. The **geometry** is built per piece on first
        use (:attr:`Piece.solid`), so a caller that only needs some of it — an
        export skipping the boxes whose description has not changed, a preview
        of one box — pays for what it asks for.

        Returns:
            A :class:`Build` carrying every body, lid and spacer, each with the
            position it occupies in the game box.

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
        positions = {p.label: p.position for p in packing.placements}

        for builder in self._boxes:
            at = positions.get(builder.label, builder.position or (0.0, 0.0, 0.0))
            pieces.extend(self._box_pieces(builder, at))

        spacers = self._spacer_placements(packing) if self.generate_spacers else []
        # The PDF draws the spacers alongside the boxes, so the packing carries
        # them: it is the one description of what ends up in the game box.
        packing.spacer_placements = spacers

        for spacer in spacers:
            pieces.append(
                Piece(
                    label=spacer.label,
                    kind="spacer",
                    size=spacer.size,
                    position=spacer.position,
                    _build=cache(partial(self._build_spacer_solid, spacer)),
                )
            )

        return Build(pieces=tuple(pieces), packing=packing)

    def _box_pieces(
        self, builder: BoxBuilder, at: tuple[float, float, float]
    ) -> list[Piece]:
        """Return the body and lid pieces for one box, at the position it packs to.

        The two share one build — a box type makes its body and its lid from
        the same measurements, and doing it twice would let them disagree — so
        the shared call is memoised and each piece takes its half of the result.
        Neither runs until something asks for the geometry.
        """
        size = builder.final_size
        assert size is not None
        # Validate now, build later: a project that cannot be built says so
        # when it is built, and only the CSG waits to be asked for.
        self._resolve_box(builder)
        build_once = cache(partial(self._build_box_solids, builder))

        pieces = [
            Piece(label=builder.label, kind="body", size=size, position=at,
                  builder=builder, _build=lambda: build_once()[0])
        ]
        if self._has_lid(builder):
            pieces.append(
                Piece(label=builder.label, kind="lid", size=size, position=at,
                      builder=builder, _build=lambda: build_once()[1])
            )
        return pieces

    @staticmethod
    def _has_lid(builder: BoxBuilder) -> bool:
        """Return True when this box type produces a lid file at all."""
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

            for b, bin_items in zip(builders, packed_bins, strict=False):
                object.__setattr__(b, "compartments", tuple(
                    CompartmentBuilder(
                        label=name, size=(w, l), depth=d,
                        cut=Cut(kind=FingerCut.THROUGH_FLOOR, side=ScoopSide.FRONT),
                    )
                    for name, w, l, d in bin_items
                ))

    def _by_label(self, label: str) -> BoxBuilder | None:
        """Return the builder with this label, or ``None``."""
        return next((b for b in self._boxes if b.label == label), None)

    def _selected(self, only: str | Iterable[str] | None) -> set[str] | None:
        """Which box labels a caller asked for, checked against the project.

        Args:
            only: One label, several, or ``None`` for all of them.

        Returns:
            The set of labels, or ``None`` when everything was asked for.

        Raises:
            ValueError: If a label is not in this project. A silent miss here
                would look exactly like a box that failed to build — an empty
                preview, or an export that wrote nothing — with nothing to say
                which it was.

        """
        if only is None:
            return None
        wanted = {only} if isinstance(only, str) else set(only)

        known = {b.label for b in self._boxes}
        unknown = sorted(wanted - known)
        if unknown:
            raise ValueError(
                f"Project '{self.name}' has no box(es) named "
                f"{', '.join(unknown)}. It has: {', '.join(sorted(known))}"
            )
        return wanted

    # ------------------------------------------------------------------- show

    def show(
        self,
        show_lids: bool = False,
        remove_layers: int = 0,
        only: str | Iterable[str] | None = None,
        lids_only: bool = False,
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
            only: Show just these boxes, by label. One box on its own is the
                usual way to look at a box you are working on, and it is also
                the cheap one: nothing else is built.
            lids_only: Show the lids without their bodies — for looking at a
                label or a lid pattern, which the body would otherwise sit
                under. Implies ``show_lids``.
            fn: Fixed facets per circle for every curve in the preview.
                ``None`` (the default) defers to fa/fs, which sizes facets by
                how large each curve actually is — that is what keeps a preview
                responsive. Unlike :meth:`export`, this does *not* jump to
                export precision.
            fa: Minimum angle per fragment, in degrees (default 12).
            fs: Minimum fragment size, in mm (default 2).

        Raises:
            ValueError: If ``remove_layers`` is negative, ``only`` names a box
                this project does not have, or a precision setting is out of
                range.

        """
        from pyboxbuilder.precision import use

        with use(fn=fn, fa=fa, fs=fs):
            pieces = self.preview_pieces(
                show_lids=show_lids, remove_layers=remove_layers,
                only=only, lids_only=lids_only,
            )

        for piece in pieces:
            solid = piece.solid
            # Uncolourable geometry still previews, just uncoloured.
            with suppress(AttributeError, TypeError):
                solid = solid.color(piece.color)
            solid.show()

    def preview_pieces(
        self,
        show_lids: bool = False,
        remove_layers: int = 0,
        only: str | Iterable[str] | None = None,
        lids_only: bool = False,
    ) -> list[PreviewPiece]:
        """Build the list of separately-coloured solids :meth:`show` renders.

        Public because it is the cheap way to exercise the geometry: it packs
        the layout and builds every body, lid and spacer, but writes nothing
        and needs no render binary. A CI pass wants exactly that — the build
        path without the printable output — where :meth:`export` would spend
        its time tessellating 3MFs no one is going to print.

        Args:
            show_lids: Include each box's lid, lightened and semi-transparent.
            remove_layers: Number of top layers to omit.
            only: Restrict to these box labels.
            lids_only: Leave the bodies out; implies ``show_lids``.

        Returns:
            A list of :class:`pyboxbuilder.preview.PreviewPiece`, one per body,
            lid and spacer — never unioned together.

        Raises:
            ValueError: If ``remove_layers`` is negative, or ``only`` names a
                box this project does not have.

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

        wanted = self._selected(only)
        show_lids = show_lids or lids_only

        build = self.build()
        bodies_and_spacers = build.of_kind("body", "spacer")
        kept = {p.label for p in remove_top_layers(bodies_and_spacers, remove_layers)}
        if wanted is not None:
            kept &= wanted

        def colour_for(piece: Piece) -> Color:
            """Return a box's own colour when it declares one, else a stable hue."""
            if piece.is_spacer:
                return spacer_color(piece.label)
            declared = getattr(piece.builder, "color", None)
            return declared if declared is not None else stable_color(piece.label)

        out: list[PreviewPiece] = []
        for piece in build.pieces:
            if piece.label not in kept:
                continue
            if piece.kind == "lid" and not show_lids:
                continue
            if piece.kind != "lid" and lids_only:
                continue
            if piece.solid is None:
                continue

            solid, inserts = piece.solid, None
            if piece.kind == "lid":
                # Show the lid as it prints, decoration and all.
                decorated, inserts = self._decorated_lid(piece, "mmu")
                solid = decorated or solid

            colour = colour_for(piece)
            if piece.kind == "lid":
                colour = lid_color(colour)
            out.append(
                PreviewPiece(piece.label, solid.translate(list(piece.position)), colour, piece.kind)
            )

            # A lid's label and frame are *inserts* — separate solids, so the
            # slicer can give each its own material (FR-025). Dropping them
            # here left every previewed lid blank while the exported one
            # carried its label, which is the divergence FR-046c exists to
            # prevent: what is previewed must be what is printed. Each keeps
            # its own colour rather than being fused into the lid's, since
            # that is the whole reason it is a separate object.
            for insert in inserts or ():
                out.append(
                    PreviewPiece(
                        piece.label, insert.solid.translate(list(piece.position)),
                        insert.color if insert.color is not None else colour, "lid",
                    )
                )
        return out

    # ------------------------------------------------------------------ sizing

    def _container(self) -> tuple[float, float, float]:
        """Return the game box's size, for the paths that require one.

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

    def _resolve_final_layout(self) -> BoxPacking:
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

    def _min_size(self, builder: BoxBuilder) -> tuple[float, float, float]:
        """Return the smallest this box may be: its explicit size, or its contents.

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
            return (size[0], size[1], size[2])
        if builder.compartments:
            return from_compartments()
        raise ValueError(
            f"Box '{builder.label}' has no explicit size and no "
            f"compartments — at least one is required."
        )

    def _standalone_size(self, builder: BoxBuilder) -> tuple[float, float, float]:
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

    def _resolve_box(self, builder: BoxBuilder) -> ResolvedBox:
        """Everything about a box that is decided before any geometry is cut.

        Kept separate from the geometry so it can run **eagerly**, during
        :meth:`build`, while the CSG waits to be asked for. A project that
        cannot be built has to say so when it is built, not later when
        something happens to look at a solid — and the validation is what
        decides that, not the geometry.

        Args:
            builder: The box to resolve, already carrying its ``final_size``.

        Returns:
            Its :class:`ResolvedBox`.

        Raises:
            ValueError: If the compartments overflow the interior, or their
                ratios do.

        """
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
        from pyboxbuilder.box.spec import build_spec
        from pyboxbuilder.compartments.layout import layout_compartments

        self._check_ratios(builder)

        size = builder.final_size
        assert size is not None
        spec = build_spec(self, builder, size)
        interior = spec.interior()

        siblings = len(builder.compartments)
        comp_data = [
            cb.resolved(interior.width, interior.length, interior.height, siblings)
            for cb in builder.compartments
        ]

        box_cls = BOX_IMPL_REGISTRY.get(builder.box_type)
        box = box_cls() if box_cls is not None else None
        if box is not None:
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

        return ResolvedBox(
            builder=builder, box=box, spec=spec, interior=interior,
            compartments=comp_layout,
        )

    def _build_box_solids(
        self, builder: BoxBuilder
    ) -> tuple[Bosl2Solid | None, Bosl2Solid | None, tuple[float, float, float]]:
        """Build a box's body and lid geometry.

        Returns ``(body, lid, size)``; ``body``/``lid`` are ``None`` when the
        box type produced no geometry (or pybosl2 is unavailable).
        """
        resolved = self._resolve_box(builder)
        size = builder.final_size
        assert size is not None
        box, spec = resolved.box, resolved.spec
        if box is None:
            return None, None, size

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

            if resolved.compartments is not None and body is not None:
                from pyboxbuilder.compartments.carve import build_contents

                contents = build_contents(
                    resolved.compartments.placements, resolved.interior,
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

    def _check_ratios(self, builder: BoxBuilder) -> None:
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

    def _spacer_placements(self, packing: BoxPacking) -> list[Placement]:
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

    def _build_spacer_solid(self, spacer: Placement) -> Bosl2Solid | None:
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

    def _decorated_lid(
        self, piece: Piece, mode: str
    ) -> tuple[Any | None, list[Bosl2Solid] | None]:
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
                reserved=self._lid_keepouts(builder),
            )
            return decorated.solid, decorated.inserts or None
        except ImportError:
            return piece.solid, None

    def _lid_keepouts(self, builder: BoxBuilder) -> list[tuple[float, float, float]]:
        """Patches of a box's lid its own type needs left solid.

        A sliding lid's fingernail dish is the case (FR-002e5): the type cuts
        it, and the decoration has to know so its pattern does not open a hole
        onto the rim the dish is pulled against.

        Args:
            builder: The box whose lid is being decorated.

        Returns:
            ``(x, y, radius)`` circles in the lid's own frame.

        """
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
        from pyboxbuilder.box.spec import build_spec

        box_cls = BOX_IMPL_REGISTRY.get(builder.box_type)
        if box_cls is None or builder.final_size is None:
            return []
        return box_cls().lid_keepouts(build_spec(self, builder, builder.final_size))

    # ----------------------------------------------------------------- export

    def export(
        self,
        out_dir: str | Path,
        fn: int | None = None,
        fa: float | None = None,
        fs: float | None = None,
        only: str | Iterable[str] | None = None,
        force: bool = False,
    ) -> ExportResult:
        """Write every piece of this project, and the layout PDF.

        Writes exactly what :meth:`show` renders — the same :meth:`build` —
        so the only difference between previewing and exporting is that this
        one puts the result on disk.

        **A box whose description has not changed is not rebuilt.** The digest
        that decides whether a file needs writing (FR-031) is known before any
        geometry is cut, so an unchanged box costs nothing at all rather than
        being built and then discarded. That is what makes a repeat export at
        print precision practical: it is the difference between minutes and a
        second.

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
            only: Export just these box labels. Everything else is left alone
                on disk — not deleted, not rewritten.
            force: Rebuild and rewrite every piece, whether its description
                changed or not.

        Returns:
            An :class:`ExportResult` listing the files written and skipped.

        Raises:
            ValueError: If a box cannot be sized, a precision setting is out of
                range, or ``only`` names a box this project does not have.
            PackingError: If the boxes cannot be packed into the game box.

        """
        from pyboxbuilder.export.exporter import BoxExporter
        from pyboxbuilder.export.result import ExportResult
        from pyboxbuilder.precision import export_facets, use

        with use(fn=export_facets() if fn is None else fn, fa=fa, fs=fs):
            build = self.build()
            wanted = self._selected(only)

            exporter = BoxExporter(out_dir, self.name)
            if wanted is None:
                # A partial export knows nothing about the pieces it was not
                # asked for, so it must not conclude they are stale.
                exporter.delete_stale(
                    "spacer_", {p.label for p in build.of_kind("spacer")}
                )

            for piece in build.pieces:
                if wanted is not None and piece.label not in wanted:
                    continue
                for mode in ("mmu", "single"):
                    fingerprint = self._fingerprint(piece, mode)
                    part = "body" if piece.is_spacer else piece.kind

                    if not force and exporter.is_current(piece.label, part, mode, fingerprint):
                        exporter.note_unchanged(piece.label, part, mode, piece.size)
                        continue

                    solid, inserts = (
                        self._decorated_lid(piece, mode)
                        if piece.kind == "lid" else (piece.solid, None)
                    )
                    parts = [x.solid for x in inserts] if inserts else None
                    exporter.write_piece(
                        piece.label, part, mode, solid, parts,
                        size=piece.size, fingerprint=fingerprint,
                    )

            if build.packing is not None and wanted is None:
                self._write_layout_pdf(build, out_dir, exporter)

        self.piece_bounds = tuple(exporter.state.bounds)
        return ExportResult(
            written=tuple(exporter.state.written),
            skipped=tuple(exporter.state.skipped),
            total_files=len(exporter.state.written) + len(exporter.state.skipped),
        )

    def _fingerprint(self, piece: Piece, mode: str) -> str:
        """Return a hash of everything that decides this piece's geometry.

        What makes a file worth rewriting is a change in the description it was
        built from, and that is knowable exactly — where comparing the meshes
        is not. Two runs of an unchanged project produce identical fingerprints
        and no writes; a boolean solver that retriangulates a complex mesh
        differently between runs no longer reads as a change (FR-031).

        It covers what shapes **this piece**, and no more. Two things are
        deliberately left out, because including them rebuilds parts whose
        geometry has not changed:

        - **Where the piece sits.** A 3MF holds the piece in its own frame, so
          moving a box in the game box does not alter the file. Without this,
          shortening one box in a stack rebuilt every box above it.
        - **The other half of the box.** A body does not change when its lid's
          label does, so a body's fingerprint leaves the lid decoration out and
          a lid's leaves the compartments out.

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

        box = describe(piece.builder) if piece.builder is not None else None
        if box is not None:
            box.pop("position", None)
            box.pop("lid" if piece.kind == "body" else "compartments", None)

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
            "box": box,
        })

    def _delete_stale_spacers(
        self, out_dir: str | Path, spacer_placements: list[Placement]
    ) -> None:
        """Delete orphaned spacer 3MF files that no longer match a spacer.

        Args:
            out_dir: Root output directory.
            spacer_placements: The current set of spacer placements.

        """
        from pyboxbuilder.export.exporter import BoxExporter

        BoxExporter(out_dir, self.name).delete_stale(
            "spacer_", {sp.label for sp in spacer_placements}
        )

    def _write_layout_pdf(
        self, build: Build, out_dir: str | Path, exporter: BoxExporter
    ) -> None:
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
        """Register a group of compartments to be dynamically partitioned across the given box labels."""
        self._shared_groups.append((boxes, compartments))


STANDALONE_GAP_MM = 10.0
"""Gap left between standalone boxes when they are lined up for a preview."""
