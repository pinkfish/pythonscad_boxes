# SPDX-License-Identifier: Apache-2.0
"""BoxExporter — writes per-box and per-spacer 3MF files (T068a/T068b/T070/T072).

Output layout (FR-025):

    {out_dir}/{game}/mmu/{label}_body.3mf
    {out_dir}/{game}/mmu/{label}_lid.3mf
    {out_dir}/{game}/single/{label}_body_single.3mf
    {out_dir}/{game}/single/{label}_lid_single.3mf

The `mmu` pass keeps positive inserts (labels, accents) as separate coloured
solids so the slicer can assign them their own material; the `single` pass fuses
everything into one body. Writes are gated on each piece's fingerprint — the
description it was built from — so re-exporting an unchanged project rewrites
nothing (see `pyboxbuilder.export.fingerprint`).

Geometry export runs through PythonSCAD. When it is unavailable this **raises**:
it used to create the file tree anyway, writing a 0-byte 3MF per piece and
reporting every one as written, so a broken install looked exactly like a
successful export until the files reached a slicer (FR-000h).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING

from pyboxbuilder.deps import require
from pyboxbuilder.export import fingerprint as fp
from pyboxbuilder.export.geometry import (
    mesh_geometry,
    read_3mf_geometry,
    same_geometry,
)

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid

MMU = "mmu"
SINGLE = "single"


@dataclass(frozen=True)
class PieceBounds:
    """Measured bounding box of one exported piece (T068b / FR-027)."""

    label: str
    """Piece name, e.g. "PlayerBoxBlack_body"."""
    size: tuple[float, float, float]
    """(width, length, height) in mm."""
    mode: str
    """"mmu" or "single"."""

    def fits_bed(self, bed: tuple[float, float, float]) -> bool:
        """Return True when the piece fits a printer bed of the given size."""
        return all(s <= b + 1e-6 for s, b in zip(self.size, bed, strict=False))

    def __str__(self) -> str:
        """Return the piece as ``label [mode]: W x L x H mm``."""
        w, l, h = self.size
        return f"{self.label} [{self.mode}]: {w:.1f} x {l:.1f} x {h:.1f} mm"


@dataclass
class ExporterState:
    """Files written / skipped so far, plus the bounding boxes measured."""

    written: list[str] = field(default_factory=list)
    skipped: list[str] = field(default_factory=list)
    bounds: list[PieceBounds] = field(default_factory=list)


class BoxExporter:
    """Writes the 3MF tree for one project.

    Args:
        out_dir: Root output directory.
        game: Project name; becomes the subdirectory under `out_dir`.

    """

    def __init__(self, out_dir: str | Path, game: str) -> None:
        self.root = Path(out_dir) / game
        self.game = game
        self.state = ExporterState()

    # ------------------------------------------------------------- filenames

    def path_for(self, label: str, part: str, mode: str) -> Path:
        """Path of one piece. `part` is "body" or "lid"."""
        suffix = "_single" if mode == SINGLE else ""
        return self.root / mode / f"{label}_{part}{suffix}.3mf"

    def relative(self, path: Path) -> str:
        """Path as recorded in `ExportResult`, relative to the output root."""
        return f"{self.game}/{path.relative_to(self.root).as_posix()}"

    # ----------------------------------------------------------------- write

    def is_current(self, label: str, part: str, mode: str, fingerprint: str) -> bool:
        """Return True when the file on disk was built from this exact description.

        Asked **before** the geometry is built, so an unchanged box costs
        nothing: the digest covers everything that shapes the piece, and none of
        it needs the mesh (FR-031).

        Args:
            label: Box label.
            part: "body" or "lid".
            mode: "mmu" or "single".
            fingerprint: Digest of the description the piece would be built
                from. Empty always reports stale.

        Returns:
            Whether the write can be skipped.

        """
        return fp.matches(self.path_for(label, part, mode), fingerprint)

    def note_unchanged(
        self, label: str, part: str, mode: str,
        size: tuple[float, float, float] | None = None,
    ) -> None:
        """Record a piece that was skipped without being built.

        Its bounding box is the declared size rather than a measured one, since
        measuring would mean building the thing this skipped (FR-027).

        Args:
            label: Box label.
            part: "body" or "lid".
            mode: "mmu" or "single".
            size: The piece's declared size, recorded as its bounds.

        """
        self.state.skipped.append(self.relative(self.path_for(label, part, mode)))
        if size is not None:
            self.state.bounds.append(
                PieceBounds(label=f"{label}_{part}", size=size, mode=mode)
            )

    def write_piece(
        self,
        label: str,
        part: str,
        mode: str,
        solid: Bosl2Solid | None = None,
        inserts: list[Bosl2Solid] | None = None,
        size: tuple[float, float, float] | None = None,
        fingerprint: str = "",
        force: bool = False,
    ) -> str | None:
        """Export one piece, skipping the write when nothing about it changed.

        Args:
            label: Box label.
            part: "body" or "lid".
            mode: "mmu" or "single".
            solid: The main geometry. There must be some: see Raises.
            inserts: Positive coloured inserts. Kept as separate objects in mmu
                mode and unioned into `solid` in single mode (T068a).
            size: Bounding box to record when it cannot be measured from `solid`.
            fingerprint: Digest of the description this piece was built from,
                recorded beside the file for the next run to compare against.
            force: Rewrite even when the geometry on disk already matches.

        Returns:
            The relative path if written, None if skipped.

        Raises:
            RuntimeError: If the piece has no geometry to write, or if the
                backend accepts it and produces no file.
            MissingDependencyError: If the geometry backend is not installed.

        Note:
            Whether a write is *needed* is :meth:`is_current`'s decision, taken
            before the geometry is built. This writes what it is given — but it
            also re-measures the geometry on disk first, so a piece whose bytes
            changed without its shape changing is not rewritten.

        """
        path = self.path_for(label, part, mode)
        path.parent.mkdir(parents=True, exist_ok=True)

        payload = self._compose(solid, inserts, mode)
        measured = _measure(payload) or size
        if measured is not None:
            self.state.bounds.append(
                PieceBounds(label=f"{label}_{part}", size=measured, mode=mode)
            )

        # The fingerprint is the fast path; this is the honest one. The bytes
        # OpenSCAD writes are not deterministic, so compare the shape itself —
        # bounding box and volume — against the file already on disk and leave
        # it alone when they agree.
        if (
            not force
            and path.exists()
            and same_geometry(mesh_geometry(payload), read_3mf_geometry(path))
        ):
            fp.record(path, fingerprint)
            self.state.skipped.append(self.relative(path))
            return None

        # Keep the .3mf suffix on the temp file — the exporter picks its format
        # from the extension and silently falls back to STL without it.
        candidate = path.with_name(f".{path.stem}.tmp.3mf")
        wrote_candidate = _export_3mf(payload, candidate)

        if not wrote_candidate:
            # Nothing to write. This used to touch an empty file and report it
            # as exported, which is the failure mode a user cannot see: a tree
            # full of 0-byte 3MFs and an export that said it succeeded
            # (FR-000h). A lidless box never gets here — `write_box` guards the
            # lid on `has_lid` — so an empty piece is a box that failed to build.
            candidate.unlink(missing_ok=True)
            raise RuntimeError(
                f"{label} {part} built no geometry, so {path.name} would be an "
                "empty file. A box that cannot be built must say so rather than "
                "exporting nothing."
            )

        candidate.replace(path)
        fp.record(path, fingerprint)
        self.state.written.append(self.relative(path))
        return self.relative(path)

    def write_box(
        self,
        label: str,
        body: Bosl2Solid | None = None,
        lid: Bosl2Solid | None = None,
        body_inserts: list[Bosl2Solid] | None = None,
        lid_inserts: list[Bosl2Solid] | None = None,
        size: tuple[float, float, float] | None = None,
        has_lid: bool = True,
    ) -> list[str]:
        """Export a box's body and (optionally) lid in both colour modes."""
        out = []
        for mode in (MMU, SINGLE):
            written = self.write_piece(label, "body", mode, body, body_inserts, size)
            if written:
                out.append(written)
            if has_lid:
                written = self.write_piece(label, "lid", mode, lid, lid_inserts, size)
                if written:
                    out.append(written)
        return out

    def delete_stale(self, prefix: str, keep_labels: set[str]) -> list[str]:
        """Delete `{prefix}*` files whose label is no longer generated (T126)."""
        removed = []
        for mode in (MMU, SINGLE):
            mode_dir = self.root / mode
            if not mode_dir.exists():
                continue
            for f in mode_dir.glob(f"{prefix}*"):
                if f.name == fp.SIDECAR_NAME:
                    continue
                label = _label_from_filename(f.name, mode)
                if label not in keep_labels:
                    fp.forget(f)
                    f.unlink(missing_ok=True)
                    removed.append(self.relative(f))
        return removed

    # -------------------------------------------------------------- internals

    @staticmethod
    def _compose(
        solid: Bosl2Solid | None,
        inserts: list[Bosl2Solid] | None,
        mode: str,
    ) -> Bosl2Solid | list[Bosl2Solid] | None:
        """Combine a piece with its coloured inserts for the given mode."""
        if not inserts:
            return solid
        if mode == MMU:
            # Keep the inserts as distinct objects so each keeps its material.
            return ([solid] if solid is not None else []) + list(inserts)
        merged = solid
        for insert in inserts:
            merged = insert if merged is None else merged + insert
        return merged


def _label_from_filename(name: str, mode: str) -> str:
    """Recover a box label from an exported filename."""
    stem = name[:-4] if name.endswith(".3mf") else name
    for suffix in ("_body_single", "_lid_single", "_body", "_lid"):
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return stem


def _measure(payload: Bosl2Solid | list[Bosl2Solid] | None) -> tuple[float, float, float] | None:
    """Measure a solid's bounding box, or None if it cannot be measured.

    PythonSCAD computes `.size` by meshing, so this only works inside the app.
    """
    if payload is None:
        return None
    solids = payload if isinstance(payload, list) else [payload]

    boxes = []
    for solid in solids:
        box = _solid_bounds(solid)
        if box is not None:
            boxes.append(box)
    if not boxes:
        return None

    lo = [min(p[i] for p, _ in boxes) for i in range(3)]
    hi = [max(p[i] + s[i] for p, s in boxes) for i in range(3)]
    return (hi[0] - lo[0], hi[1] - lo[1], hi[2] - lo[2])


def _solid_bounds(solid: Bosl2Solid) -> tuple[tuple[float, ...], tuple[float, ...]] | None:
    """(origin, size) of one solid's AABB, or None if it exposes neither.

    `Bosl2Solid.bounds()` already answers in (position, size) form and is the
    reliable source; the raw `.position` / `.size` attributes are only meaningful
    on native objects — on a pybosl2 wrapper they are bound methods, not triples.

    A solid that *has* one of those and cannot produce a number from it raises,
    rather than measuring as ``None``: the bounds are what a user checks a piece
    against their print bed with, and a piece silently missing from that report
    reads as a piece that fits (FR-000h).
    """
    bounds = getattr(solid, "bounds", None)
    if callable(bounds):
        origin, size = bounds()
        return (tuple(float(v) for v in origin), tuple(float(v) for v in size))

    position, size = getattr(solid, "position", None), getattr(solid, "size", None)
    if position is None or size is None:
        return None
    return (tuple(float(v) for v in position), tuple(float(v) for v in size))


def _export_3mf(payload: Bosl2Solid | list[Bosl2Solid] | None, path: Path) -> bool:
    """Write a 3MF file.

    Args:
        payload: The solid, or the list of them that make up one piece.
        path: Where to write it.

    Returns:
        ``False`` when there was **nothing to write** — a lidless type's lid,
        or a piece whose geometry came back empty. That is the only false this
        returns: a backend that is missing, or a write that fails, raises.

    Raises:
        MissingDependencyError: If the geometry backend is not installed.
        RuntimeError: If the write is attempted and produces no file.

    """
    if payload is None:
        return False

    solids = payload if isinstance(payload, list) else [payload]
    if not solids:
        return False

    # Not imported at module scope: the FFI is only needed once there is
    # something to write, and a project that builds but never exports should
    # not require it. Missing at this point is fatal, though — the caller asked
    # for a file, and the alternative was reporting success having written none.
    export = require("openscad", f"write {path.name}").export

    combined = solids[0]
    for solid in solids[1:]:
        combined = combined | solid
    # `export` only takes native PyOpenSCAD objects; `.shape` is how a
    # pybosl2 wrapper crosses that boundary.
    export(getattr(combined, "shape", combined), str(path))
    if not path.exists():
        raise RuntimeError(
            f"exporting {path} reported success but wrote no file. "
            "The geometry backend accepted the solid and produced nothing."
        )
    return True
