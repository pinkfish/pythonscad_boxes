# SPDX-License-Identifier: Apache-2.0
"""GeometryPipeline — executes CSG construction, previewing, and export (FR-093)."""

from __future__ import annotations

from collections.abc import Iterable
from functools import cache, partial
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pyboxbuilder.enums import BoxType
from pyboxbuilder.project.piece import Build, Piece, ResolvedBox

if TYPE_CHECKING:
    from pybosl2 import Color
    from pybosl2.shapes3d import Bosl2Solid

    from pyboxbuilder.builders._base import BoxBuilder
    from pyboxbuilder.export.exporter import BoxExporter
    from pyboxbuilder.export.result import ExportResult
    from pyboxbuilder.packing.layout import Placement
    from pyboxbuilder.preview import PreviewPiece
    from pyboxbuilder.project.compiler import LayoutCompiler
    from pyboxbuilder.project.manifest import ProjectManifest

STANDALONE_GAP_MM = 10.0
"""Gap left between standalone boxes when they are lined up for a preview."""


class GeometryPipeline:
    """Executes CSG construction, lid decoration, previewing, and 3MF exporting (FR-093)."""

    def build(
        self,
        manifest: ProjectManifest,
        compiler: LayoutCompiler | None = None,
        build_box_solids_fn: Any = None,
    ) -> Build:
        """Resolve the layout and describe every piece of this project.

        The one build path. Previewing renders what this returns and export writes it.
        """
        from pyboxbuilder.project.compiler import LayoutCompiler

        comp = compiler or LayoutCompiler()
        comp.resolve_shared_compartments(manifest)

        pieces: list[Piece] = []

        if manifest.game_box_size is None:
            # Standalone: nothing is packed, so line the boxes up side by side
            # for a preview. There are no layers and no spacers.
            x = 0.0
            for builder in manifest.boxes:
                size = comp.standalone_size(manifest, builder)
                pieces.extend(
                    self._box_pieces(
                        manifest,
                        builder,
                        (x, 0.0, 0.0),
                        build_box_solids_fn=build_box_solids_fn,
                    )
                )
                x += size[0] + STANDALONE_GAP_MM
            return Build(pieces=tuple(pieces))

        packing = comp.resolve_final_layout(manifest)
        positions = {p.label: p.position for p in packing.placements}

        for builder in manifest.boxes:
            at = positions.get(builder.label, builder.position or (0.0, 0.0, 0.0))
            pieces.extend(
                self._box_pieces(
                    manifest,
                    builder,
                    at,
                    build_box_solids_fn=build_box_solids_fn,
                )
            )

        spacers = comp.spacer_placements(manifest, packing) if manifest.generate_spacers else []
        packing.spacer_placements = spacers

        for spacer in spacers:
            pieces.append(
                Piece(
                    label=spacer.label,
                    kind="spacer",
                    size=spacer.size,
                    position=spacer.position,
                    _build=cache(partial(self._build_spacer_solid, manifest, spacer)),
                )
            )

        return Build(pieces=tuple(pieces), packing=packing)

    def _box_pieces(
        self,
        manifest: ProjectManifest,
        builder: BoxBuilder,
        at: tuple[float, float, float],
        build_box_solids_fn: Any = None,
    ) -> list[Piece]:
        """Return the body and lid pieces for one box, at the position it packs to."""
        size = builder.final_size
        assert size is not None
        # Validate now, build later: pre-CSG validation runs here eagerly (FR-092).
        self._resolve_box(manifest, builder)
        build_fn = build_box_solids_fn or partial(self._build_box_solids, manifest)
        build_once = cache(partial(build_fn, builder))

        pieces = [
            Piece(
                label=builder.label,
                kind="body",
                size=size,
                position=at,
                builder=builder,
                _build=lambda: build_once()[0],
                _build_inserts=lambda: build_once()[3],
            )
        ]
        if self._has_lid(builder):
            pieces.append(
                Piece(
                    label=builder.label,
                    kind="lid",
                    size=size,
                    position=at,
                    builder=builder,
                    _build=lambda: build_once()[1],
                )
            )
        return pieces

    @staticmethod
    def _has_lid(builder: BoxBuilder) -> bool:
        """Return True when this box type produces a lid file at all."""
        from pyboxbuilder.box.registry import LIDLESS_BOX_TYPES

        return builder.box_type not in LIDLESS_BOX_TYPES

    def _resolve_box(
        self, manifest: ProjectManifest, builder: BoxBuilder
    ) -> ResolvedBox:
        """Everything about a box that is decided before any geometry is cut."""
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
        from pyboxbuilder.box.spec import build_spec
        from pyboxbuilder.box.validation import GeometryValidator
        from pyboxbuilder.compartments.layout import layout_compartments
        from pyboxbuilder.project.compiler import LayoutCompiler

        LayoutCompiler.check_ratios(builder)

        size = builder.final_size
        assert size is not None
        spec = build_spec(manifest, builder, size)

        # Pre-CSG physical invariant validation (FR-092 / SC-092)
        GeometryValidator.validate(spec)

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
            no_rotate_labels = {
                cb.label
                for cb in builder.compartments
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
            builder=builder,
            box=box,
            spec=spec,
            interior=interior,
            compartments=comp_layout,
        )

    def _build_box_solids(
        self, manifest: ProjectManifest, builder: BoxBuilder
    ) -> tuple[
        Bosl2Solid | None,
        Bosl2Solid | None,
        tuple[float, float, float],
        list[tuple[Any, Any]],
    ]:
        """Build a box's body and lid geometry."""
        resolved = self._resolve_box(manifest, builder)
        size = builder.final_size
        assert size is not None
        box, spec = resolved.box, resolved.spec
        if box is None:
            return None, None, size, []

        body = box.build_body(spec)
        lid = box.build_lid(spec)

        if lid is not None:
            from pyboxbuilder.rounding import lid_rounding, round_edges

            lid = round_edges(
                lid, list(size), lid_rounding(spec), box.lid_rounded_edges(spec)
            )

        if resolved.compartments is not None and body is not None:
            from pyboxbuilder.box.features import hinge_intrusion
            from pyboxbuilder.box.types.cap import CapBox
            from pyboxbuilder.box.types.cap_path import CapPathBox
            from pyboxbuilder.box.types.filament_hinge import FilamentHingeBox
            from pyboxbuilder.box.types.hinge import HingeBox
            from pyboxbuilder.box.types.sliding_catch import SlidingCatchBox
            from pyboxbuilder.box.types.slipover import SlipoverBox
            from pyboxbuilder.box.types.slipover_path import SlipoverPathBox
            from pyboxbuilder.compartments.carve import build_contents, build_inserts

            hinge_solid = None
            if isinstance(box, (HingeBox, FilamentHingeBox)):
                fd = (
                    spec.hinge_pin_diameter
                    if isinstance(box, HingeBox)
                    else spec.filament_diameter
                )
                hinge_solid = hinge_intrusion(resolved.spec, fd)

            suppress_scoops = False
            if isinstance(
                box,
                (
                    CapBox,
                    CapPathBox,
                    SlipoverBox,
                    SlipoverPathBox,
                    SlidingCatchBox,
                ),
            ) or (
                isinstance(box, (HingeBox, FilamentHingeBox))
                and spec.hinge_catch_type not in (None, "none")
            ):
                suppress_scoops = True

            contents = build_contents(
                resolved.compartments.placements,
                resolved.interior,
                {cb.label: cb for cb in builder.compartments},
                top_z=size[2],
                default_side=box.preferred_scoop_side(spec),
                wall_tops=spec.wall_tops,
                mask=box.interior_mask(spec),
                hinge_intrusion=hinge_solid,
                suppress_scoops=suppress_scoops,
            )
            if contents is not None:
                body = body - contents

            inserts = build_inserts(resolved.compartments.placements, resolved.interior)
        else:
            inserts = []

        return body, lid, size, inserts

    def _build_spacer_solid(
        self, manifest: ProjectManifest, spacer: Placement
    ) -> Bosl2Solid | None:
        """Build one spacer tray's geometry in its own local frame."""
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
        from pyboxbuilder.box.spec import BoxSpec

        box_type = BoxType.PATH if spacer.path else BoxType.NO_LID
        spacer_cls = BOX_IMPL_REGISTRY.get(box_type)
        if spacer_cls is None:
            raise LookupError(
                f"spacer {spacer.label} needs a {box_type.value} box and the "
                "registry has none, so it would be left out of the export."
            )
        spec = BoxSpec(
            label=spacer.label,
            width=spacer.size[0],
            length=spacer.size[1],
            height=spacer.size[2],
            wall_thickness=manifest.wall_thickness,
            floor_thickness=manifest.floor_thickness,
            lid_thickness=0.0,
            path=tuple(spacer.path or ()),
            rounding=manifest.rounding,
            rim_free=True,
            auto_finger_holes=True,
        )
        return spacer_cls().build_body(spec)

    def _decorated_lid(
        self, manifest: ProjectManifest, piece: Piece, mode: str
    ) -> tuple[Any | None, list[Bosl2Solid] | None]:
        """One lid as it prints in a colour mode."""
        from pyboxbuilder.lid.decorate import decorate_lid

        builder = piece.builder
        if piece.solid is None or builder is None or builder.lid is None:
            return piece.solid, None
        decorated = decorate_lid(
            piece.solid,
            builder.lid,
            builder.lid_thickness or manifest.lid_thickness,
            mode,
            body_color=builder.color,
            reserved=self._lid_keepouts(manifest, builder),
        )
        return decorated.solid, decorated.inserts or None

    def _lid_keepouts(
        self, manifest: ProjectManifest, builder: BoxBuilder
    ) -> list[tuple[float, float, float]]:
        """Patches of a box's lid its own type needs left solid."""
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
        from pyboxbuilder.box.spec import build_spec

        box_cls = BOX_IMPL_REGISTRY.get(builder.box_type)
        if box_cls is None or builder.final_size is None:
            return []
        return box_cls().lid_keepouts(build_spec(manifest, builder, builder.final_size))

    def _selected(
        self, manifest: ProjectManifest, only: str | Iterable[str] | None
    ) -> set[str] | None:
        """Which box labels a caller asked for, checked against the project."""
        if only is None:
            return None
        wanted = {only} if isinstance(only, str) else set(only)

        known = {b.label for b in manifest.boxes}
        unknown = sorted(wanted - known)
        if unknown:
            raise ValueError(
                f"Project '{manifest.name}' has no box(es) named "
                f"{', '.join(unknown)}. It has: {', '.join(sorted(known))}"
            )
        return wanted

    def preview_pieces(
        self,
        manifest: ProjectManifest,
        compiler: LayoutCompiler | None = None,
        show_lids: bool = False,
        remove_layers: int = 0,
        only: str | Iterable[str] | None = None,
        lids_only: bool = False,
        build_box_solids_fn: Any = None,
        decorated_lid_fn: Any = None,
    ) -> list[PreviewPiece]:
        """Build the list of separately-coloured solids show renders."""
        from pyboxbuilder.preview import (
            PreviewPiece,
            lid_color,
            remove_top_layers,
            spacer_color,
            stable_color,
        )

        if remove_layers < 0:
            raise ValueError(f"remove_layers must be >= 0; got {remove_layers}")

        wanted = self._selected(manifest, only)
        show_lids = show_lids or lids_only

        build = self.build(
            manifest, compiler, build_box_solids_fn=build_box_solids_fn
        )
        bodies_and_spacers = build.of_kind("body", "spacer")
        kept = {p.label for p in remove_top_layers(bodies_and_spacers, remove_layers)}
        if wanted is not None:
            kept &= wanted

        def colour_for(piece: Piece) -> Color:
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
                dec_fn = decorated_lid_fn or partial(self._decorated_lid, manifest)
                decorated, inserts = dec_fn(piece, "mmu")
                solid = decorated or solid

            colour = colour_for(piece)
            if piece.kind == "lid":
                colour = lid_color(colour)
            out.append(
                PreviewPiece(
                    piece.label, solid.translate(list(piece.position)), colour, piece.kind
                )
            )

            for insert in inserts or ():
                out.append(
                    PreviewPiece(
                        piece.label,
                        insert.solid.translate(list(piece.position)),
                        insert.color if insert.color is not None else colour,
                        "lid",
                    )
                )

            for solid_insert, color in piece.inserts:
                out.append(
                    PreviewPiece(
                        piece.label,
                        solid_insert.translate(list(piece.position)),
                        color,
                        "body",
                    )
                )
        return out

    def show(
        self,
        manifest: ProjectManifest,
        compiler: LayoutCompiler | None = None,
        show_lids: bool = False,
        remove_layers: int = 0,
        only: str | Iterable[str] | None = None,
        lids_only: bool = False,
        fn: int | None = None,
        fa: float | None = None,
        fs: float | None = None,
    ) -> None:
        """Preview the packed box layout interactively."""
        from pyboxbuilder.precision import use

        with use(fn=fn, fa=fa, fs=fs):
            pieces = self.preview_pieces(
                manifest,
                compiler=compiler,
                show_lids=show_lids,
                remove_layers=remove_layers,
                only=only,
                lids_only=lids_only,
            )

        for piece in pieces:
            solid = piece.solid
            if piece.color is not None:
                solid = solid.color(piece.color)
            solid.show()

    def export(
        self,
        manifest: ProjectManifest,
        compiler: LayoutCompiler | None = None,
        out_dir: str | Path = ".",
        fn: int | None = None,
        fa: float | None = None,
        fs: float | None = None,
        only: str | Iterable[str] | None = None,
        force: bool = False,
        build_box_solids_fn: Any = None,
        decorated_lid_fn: Any = None,
        fingerprint_fn: Any = None,
    ) -> ExportResult:
        """Write every piece of this project, and the layout PDF."""
        from pyboxbuilder.export.exporter import BoxExporter
        from pyboxbuilder.export.result import ExportResult
        from pyboxbuilder.precision import export_facets, use

        with use(fn=export_facets() if fn is None else fn, fa=fa, fs=fs):
            build = self.build(
                manifest, compiler, build_box_solids_fn=build_box_solids_fn
            )
            wanted = self._selected(manifest, only)

            exporter = BoxExporter(out_dir, manifest.name)
            if wanted is None:
                exporter.delete_stale(
                    "spacer_", {p.label for p in build.of_kind("spacer")}
                )

            for piece in build.pieces:
                if wanted is not None and piece.label not in wanted:
                    continue
                for mode in ("mmu", "single"):
                    fp_fn = fingerprint_fn or partial(self._fingerprint, manifest)
                    fingerprint = fp_fn(piece, mode)
                    part = "body" if piece.is_spacer else piece.kind

                    if not force and exporter.is_current(
                        piece.label, part, mode, fingerprint
                    ):
                        exporter.note_unchanged(
                            piece.label, part, mode, piece.size
                        )
                        continue

                    dec_fn = decorated_lid_fn or partial(self._decorated_lid, manifest)
                    solid, inserts = (
                        dec_fn(piece, mode)
                        if piece.kind == "lid"
                        else (piece.solid, None)
                    )
                    parts = [x.solid for x in inserts] if inserts else None
                    if piece.kind != "lid":
                        body_inserts = piece.inserts
                        parts = (
                            [s.color(c) for s, c in body_inserts]
                            if body_inserts
                            else None
                        )
                    geometry_check = not force
                    exporter.write_piece(
                        piece.label,
                        part,
                        mode,
                        solid,
                        parts,
                        size=piece.size,
                        fingerprint=fingerprint,
                        force=force,
                        geometry_check=geometry_check,
                    )

            if build.packing is not None and wanted is None:
                self._write_layout_pdf(manifest, build, out_dir, exporter)

        manifest.piece_bounds = tuple(exporter.state.bounds)
        return ExportResult(
            written=tuple(exporter.state.written),
            skipped=tuple(exporter.state.skipped),
            total_files=len(exporter.state.written) + len(exporter.state.skipped),
        )

    def _fingerprint(
        self, manifest: ProjectManifest, piece: Piece, mode: str
    ) -> str:
        """Return a hash of everything that decides this piece's geometry."""
        from pyboxbuilder.box.spec import describe
        from pyboxbuilder.packing.cache import cache_key
        from pyboxbuilder.precision import describe as describe_precision

        box = describe(piece.builder) if piece.builder is not None else None
        if box is not None:
            box.pop("position", None)
            box.pop("lid" if piece.kind == "body" else "compartments", None)

        key = cache_key({
            "kind": piece.kind,
            "label": piece.label,
            "mode": mode,
            "size": list(piece.size),
            "precision": describe_precision(),
            "project": {
                "wall_thickness": manifest.wall_thickness,
                "floor_thickness": manifest.floor_thickness,
                "lid_thickness": manifest.lid_thickness,
                "rounding": manifest.rounding,
                "inner_rounding": manifest.inner_rounding,
            },
            "box": box,
        })
        return f"sha256:{key}"

    def _delete_stale_spacers(
        self,
        manifest: ProjectManifest,
        out_dir: str | Path,
        spacer_placements: list[Placement],
    ) -> None:
        """Delete orphaned spacer 3MF files that no longer match a spacer."""
        from pyboxbuilder.export.exporter import BoxExporter

        BoxExporter(out_dir, manifest.name).delete_stale(
            "spacer_", {sp.label for sp in spacer_placements}
        )

    def _write_layout_pdf(
        self,
        manifest: ProjectManifest,
        build: Build,
        out_dir: str | Path,
        exporter: BoxExporter,
    ) -> None:
        """Generate the packing guide PDF, if the layout changed (FR-034)."""
        if not manifest.boxes or build.packing is None or manifest.game_box_size is None:
            return
        from pyboxbuilder.export.layout_pdf import (
            generate_layout_pdf,
            should_regenerate_layout,
        )

        pdf_path = Path(out_dir) / manifest.name / "layout.pdf"
        if should_regenerate_layout(build.packing, pdf_path):
            generate_layout_pdf(
                build.packing,
                pdf_path,
                manifest.name,
                manifest.game_box_size,
                box_builders=manifest.boxes,
            )
            exporter.state.written.append(f"{manifest.name}/layout.pdf")
