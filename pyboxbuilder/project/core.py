# SPDX-License-Identifier: Apache-2.0
"""Project class — top-level API entry point and facade (FR-093).

**One build path.** :meth:`Project.build` resolves the layout and builds every
body, lid and spacer. :meth:`~pyboxbuilder.project.Project.show` renders what it returns and
:meth:`~pyboxbuilder.project.Project.export` writes what it returns; neither builds geometry of its
own. That is the whole difference between the two — render or write — and it is
structural rather than a convention, because the alternative was two copies of
the build that drifted: the exported parts silently lost their rounding, their
per-side wall tops and their interior masks while the preview kept all three.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pyboxbuilder.enums import BoxType, FingerCut, ScoopSide
from pyboxbuilder.helpers import CardSize, SleeveType
from pyboxbuilder.project.compiler import LayoutCompiler
from pyboxbuilder.project.manifest import ProjectManifest
from pyboxbuilder.project.piece import Build, Piece, ResolvedBox
from pyboxbuilder.project.pipeline import GeometryPipeline

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid

    from pyboxbuilder.builders._base import BoxBuilder, Cut
    from pyboxbuilder.export.exporter import BoxExporter, PieceBounds
    from pyboxbuilder.export.result import ExportResult
    from pyboxbuilder.layout import Arrangement, Node
    from pyboxbuilder.packing.layout import BoxPacking, Placement
    from pyboxbuilder.preview import PreviewPiece


@dataclass
class Project:
    """Top-level game insert description.

    The single-import entry point for defining a board game insert.
    Delegates to :class:`~pyboxbuilder.project.manifest.ProjectManifest`,
    :class:`~pyboxbuilder.project.compiler.LayoutCompiler`, and
    :class:`~pyboxbuilder.project.pipeline.GeometryPipeline` (FR-093).

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
    clearance_slack: float | None = None
    """Clearance slack on each side of the game box in the X/Y directions (mm).

    If ``None`` (the default), it auto-scales from 1.0mm to 2.5mm based on the game box size."""
    board_thickness: float = 0.0
    """Thickness of the game board (mm).

    Reserved at the TOP of the box: the board sits on top of the sub-boxes and
    is the first thing out, so this is not a spacer gap."""
    ribbon_channels: bool = False
    """Cut bottom groove for lifting ribbon on all sub-boxes by default."""
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

    _manifest: ProjectManifest = field(init=False, repr=False)
    _compiler: LayoutCompiler = field(init=False, repr=False)
    _pipeline: GeometryPipeline = field(init=False, repr=False)
    _boxes: list[BoxBuilder] = field(init=False, repr=False)
    _shared_groups: list[tuple[list[str], list[tuple[str, float, float, float]]]] = (
        field(init=False, repr=False)
    )
    piece_bounds: tuple[PieceBounds, ...] = field(default_factory=tuple, init=False)
    """Bounding box of every exported piece, populated by `export()` (FR-027)."""

    def __post_init__(self) -> None:
        """Initialize internal manifest, layout compiler, and geometry pipeline."""
        self._manifest = ProjectManifest(
            name=self.name,
            game_box_size=self.game_box_size,
            wall_thickness=self.wall_thickness,
            floor_thickness=self.floor_thickness,
            lid_thickness=self.lid_thickness,
            rounding=self.rounding,
            inner_rounding=self.inner_rounding,
            gap_threshold=self.gap_threshold,
            min_spacer_dim=self.min_spacer_dim,
            min_spacer_height=self.min_spacer_height,
            clearance_slack=self.clearance_slack,
            board_thickness=self.board_thickness,
            ribbon_channels=self.ribbon_channels,
            generate_spacers=self.generate_spacers,
            box_defaults=self.box_defaults,
        )
        self._compiler = LayoutCompiler()
        self._pipeline = GeometryPipeline()
        self._boxes = self._manifest.boxes
        self._shared_groups = self._manifest.shared_groups

    def __setattr__(self, name: str, value: Any) -> None:
        """Set attribute and synchronize with underlying ProjectManifest."""
        super().__setattr__(name, value)
        if hasattr(self, "_manifest") and hasattr(self._manifest, name):
            setattr(self._manifest, name, value)

    @property
    def resolved_clearance_slack(self) -> float:
        """Return the resolved clearance slack, scaling with game box size if None."""
        return self._manifest.resolved_clearance_slack

    @property
    def effective_game_box_size(self) -> tuple[float, float, float] | None:
        """Dimensions available for sub-boxes, accounting for board thickness."""
        return self._manifest.effective_game_box_size

    @property
    def manifest(self) -> ProjectManifest:
        """The underlying ProjectManifest catalog."""
        return self._manifest

    @property
    def compiler(self) -> LayoutCompiler:
        """The underlying LayoutCompiler."""
        return self._compiler

    @property
    def pipeline(self) -> GeometryPipeline:
        """The underlying GeometryPipeline."""
        return self._pipeline

    @property
    def boxes(self) -> list[BoxBuilder]:
        """Registered sub-box builders."""
        return self._manifest.boxes

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
        from dataclasses import fields as dataclass_fields

        from pyboxbuilder.box.registry import BOX_TYPE_REGISTRY

        builder_cls = BOX_TYPE_REGISTRY[box_type]

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
        self._manifest.add_box(builder)
        return builder

    def add_box(self, builder: BoxBuilder) -> BoxBuilder:
        """Register an already instantiated box builder with the project.

        Args:
            builder: The box builder to register.

        Returns:
            The added builder.
        """
        return self._manifest.add_box(builder)

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
        return self._compiler.arrange(self._manifest, layout, origin)

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
        return self._pipeline.build(
            self._manifest,
            self._compiler,
            build_box_solids_fn=self._build_box_solids,
        )

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
        self._pipeline.show(
            self._manifest,
            compiler=self._compiler,
            show_lids=show_lids,
            remove_layers=remove_layers,
            only=only,
            lids_only=lids_only,
            fn=fn,
            fa=fa,
            fs=fs,
        )

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
        return self._pipeline.preview_pieces(
            self._manifest,
            compiler=self._compiler,
            show_lids=show_lids,
            remove_layers=remove_layers,
            only=only,
            lids_only=lids_only,
            build_box_solids_fn=self._build_box_solids,
            decorated_lid_fn=self._decorated_lid,
        )

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
        result = self._pipeline.export(
            self._manifest,
            compiler=self._compiler,
            out_dir=out_dir,
            fn=fn,
            fa=fa,
            fs=fs,
            only=only,
            force=force,
            build_box_solids_fn=self._build_box_solids,
            decorated_lid_fn=self._decorated_lid,
            fingerprint_fn=self._fingerprint,
        )
        self.piece_bounds = self._manifest.piece_bounds
        return result

    # ------------------------------------------------------------------ sizing

    def _container(self) -> tuple[float, float, float]:
        """Return the game box's size, for the paths that require one."""
        if self.game_box_size is None:
            raise ValueError(
                f"Project '{self.name}' has no game_box_size, so there is "
                f"nothing to pack into. Standalone boxes export directly."
            )
        return self.game_box_size

    def _resolve_final_layout(self) -> BoxPacking:
        """Resolve each box's final size and packed position."""
        return self._compiler.resolve_final_layout(self._manifest)

    def _min_size(self, builder: BoxBuilder) -> tuple[float, float, float]:
        """Return the smallest this box may be: its explicit size, or its contents."""
        return self._compiler.min_size(self._manifest, builder)

    def _standalone_size(self, builder: BoxBuilder) -> tuple[float, float, float]:
        """Resolve a standalone box's size and record it as its final_size."""
        return self._compiler.standalone_size(self._manifest, builder)

    # -------------------------------------------------------------- geometry

    def _resolve_box(self, builder: BoxBuilder) -> ResolvedBox:
        """Everything about a box that is decided before any geometry is cut."""
        return self._pipeline._resolve_box(self._manifest, builder)

    def _build_box_solids(
        self, builder: BoxBuilder
    ) -> tuple[
        Bosl2Solid | None,
        Bosl2Solid | None,
        tuple[float, float, float],
        list[tuple[Any, Any]],
    ]:
        """Build a box's body and lid geometry."""
        return self._pipeline._build_box_solids(self._manifest, builder)

    def _check_ratios(self, builder: BoxBuilder) -> None:
        """Reject compartment ratios that overflow the interior."""
        self._compiler.check_ratios(builder)

    def _spacer_placements(self, packing: BoxPacking) -> list[Placement]:
        """Derive the spacer trays that fill the gaps in a packed layout."""
        return self._compiler.spacer_placements(self._manifest, packing)

    def _build_spacer_solid(self, spacer: Placement) -> Bosl2Solid | None:
        """Build one spacer tray's geometry in its own local frame."""
        return self._pipeline._build_spacer_solid(self._manifest, spacer)

    def _box_pieces(
        self, builder: BoxBuilder, at: tuple[float, float, float]
    ) -> list[Piece]:
        """Return the body and lid pieces for one box, at the position it packs to."""
        return self._pipeline._box_pieces(self._manifest, builder, at)

    @staticmethod
    def _has_lid(builder: BoxBuilder) -> bool:
        """Return True when this box type produces a lid file at all."""
        return GeometryPipeline._has_lid(builder)

    def _decorated_lid(
        self, piece: Piece, mode: str
    ) -> tuple[Any | None, list[Bosl2Solid] | None]:
        """One lid as it prints in a colour mode."""
        return self._pipeline._decorated_lid(self._manifest, piece, mode)

    def _lid_keepouts(self, builder: BoxBuilder) -> list[tuple[float, float, float]]:
        """Patches of a box's lid its own type needs left solid."""
        return self._pipeline._lid_keepouts(self._manifest, builder)

    def _selected(self, only: str | Iterable[str] | None) -> set[str] | None:
        """Which box labels a caller asked for, checked against the project."""
        return self._pipeline._selected(self._manifest, only)

    def _fingerprint(self, piece: Piece, mode: str) -> str:
        """Return a hash of everything that decides this piece's geometry."""
        return self._pipeline._fingerprint(self._manifest, piece, mode)

    def _by_label(self, label: str) -> BoxBuilder | None:
        """Return the builder with this label, or None."""
        return self._manifest.get_by_label(label)

    def _resolve_shared_compartments(self) -> None:
        """Partition each shared compartment group across its boxes."""
        self._compiler.resolve_shared_compartments(self._manifest)

    def _delete_stale_spacers(
        self, out_dir: str | Path, spacer_placements: list[Placement]
    ) -> None:
        """Delete orphaned spacer 3MF files that no longer match a spacer."""
        self._pipeline._delete_stale_spacers(self._manifest, out_dir, spacer_placements)

    def _write_layout_pdf(
        self, build: Build, out_dir: str | Path, exporter: BoxExporter
    ) -> None:
        """Generate the packing guide PDF, if the layout changed."""
        self._pipeline._write_layout_pdf(self._manifest, build, out_dir, exporter)

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
        self._manifest.shared_groups.append((boxes, compartments))

    def card_box(
        self,
        label: str,
        *,
        card_size: CardSize | tuple[float, float],
        count: int | None = None,
        sleeve: SleeveType = SleeveType.UNSLEEVED,
        box_type: BoxType = BoxType.SLIDING,
        cut: Cut | FingerCut | None = FingerCut.THROUGH_FLOOR,
        **kwargs: Any,
    ) -> BoxBuilder:
        """Add a box pre-configured for a deck of cards."""
        from pyboxbuilder.helpers import CardSize

        builder = self.box(box_type, label, **kwargs)
        base_size = card_size.value if isinstance(card_size, CardSize) else card_size
        builder.cards(
            "Cards",
            count=count,
            size=base_size,
            thickness=sleeve.card_thickness,
            slack=sleeve.footprint_margin,
            cut=cut,
        )
        return builder

    def token_tray(
        self,
        label: str,
        *,
        rows: int = 1,
        cols: int = 1,
        scoop_side: ScoopSide = ScoopSide.FRONT,
        box_type: BoxType = BoxType.FILAMENT_HINGE,
        **kwargs: Any,
    ) -> BoxBuilder:
        """Add a tray subdivided into a grid of compartments for tokens, with finger scoops."""
        from pyboxbuilder.builders._base import Cut

        builder = self.box(box_type, label, **kwargs)
        for r in range(rows):
            for c in range(cols):
                comp_label = f"{label}_{r}_{c}"
                builder.compartment(
                    comp_label,
                    width_ratio=1.0 / cols,
                    length_ratio=1.0 / rows,
                    holds_pieces=True,
                    cut=Cut.scoop(side=scoop_side),
                )
        return builder

    def hex_tile_box(
        self,
        label: str,
        *,
        tile_width: float,
        count: int,
        box_type: BoxType = BoxType.SLIDING,
        cut: Cut | FingerCut | None = FingerCut.THROUGH_FLOOR,
        **kwargs: Any,
    ) -> BoxBuilder:
        """Add a box with a compartment for a stack of hexagonal tiles."""
        from pyboxbuilder.compartments.element import CompartmentElement
        from pyboxbuilder.enums import ElementShape

        builder = self.box(box_type, label, **kwargs)
        elem = CompartmentElement(
            shape=ElementShape.HEXAGON,
            size=(tile_width, tile_width),
        )
        builder.compartment(
            "Tiles",
            elements=(elem,),
            holds_pieces=False,
            cut=cut,
        )
        return builder
