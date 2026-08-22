# SPDX-License-Identifier: Apache-2.0
"""Mesh geometry — bounding box and volume — for comparing exported pieces.

The 3MF bytes are not a stable signal: OpenSCAD's solver retriangulates a CSG
tree differently between runs, so an identical piece can produce different
bytes. Its *geometry* is stable, though — the vertices land on the same surface
and the volume is invariant to how that surface is triangulated. So the "is this
actually different" test measures the bounding box and the volume of the
geometry already on disk and of what would be written, and skips the write when
they agree.

A bounding box on its own is not enough: two pieces can share a box but differ
inside it (a card slot cut 5 mm deeper changes no wall). Volume catches that,
and the pair is exact where the file bytes are not.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from pyboxbuilder.deps import require

if TYPE_CHECKING:
    from pybosl2.shapes3d import Bosl2Solid

BBOX_TOLERANCE_MM = 0.05
"""Two bounding boxes within this per axis count as the same box."""

VOLUME_RELATIVE_TOLERANCE = 1e-4
"""Two volumes within 0.01% of each other count as the same volume."""


@dataclass(frozen=True)
class Geometry:
    """A piece's bounding box and volume, measured in its own frame."""

    bbox: tuple[float, float, float]
    """(width, length, height) in mm."""
    volume: float
    """Solid volume in mm³."""


def same_geometry(a: Geometry | None, b: Geometry | None) -> bool:
    """Return True when two measured geometries agree.

    ``None`` never agrees with anything — an unmeasurable piece on either side
    is treated as different, so the caller writes rather than discards work.
    """
    if a is None or b is None:
        return False
    if any(
        abs(x - y) > BBOX_TOLERANCE_MM for x, y in zip(a.bbox, b.bbox, strict=False)
    ):
        return False
    scale = max(a.volume, b.volume, 1.0)
    return abs(a.volume - b.volume) <= VOLUME_RELATIVE_TOLERANCE * scale


def mesh_geometry(payload: Bosl2Solid | list[Bosl2Solid] | None) -> Geometry | None:
    """Mesh a payload and measure its bounding box and volume.

    A payload of several solids (an mmu piece keeps its inserts separate) is
    unioned first, matching what the 3MF export writes.
    """
    if payload is None:
        return None
    solids = payload if isinstance(payload, list) else [payload]
    if not solids:
        return None

    combined = solids[0]
    for solid in solids[1:]:
        combined = combined | solid

    openscad = require("openscad", "measure a piece's geometry")
    vertices, faces = openscad.mesh(getattr(combined, "shape", combined))
    return _from_mesh(vertices, faces)


def read_3mf_geometry(path: Path) -> Geometry | None:
    """Measure the geometry inside an existing 3MF, or None when unreadable.

    Every object's mesh is read, so a multi-material mmu piece measures as the
    union of its parts — the same thing :func:`mesh_geometry` measures.
    """
    import xml.etree.ElementTree as ET
    import zipfile

    try:
        with zipfile.ZipFile(path) as archive:
            model = archive.read("3D/3dmodel.model")
    except (KeyError, zipfile.BadZipFile, OSError):
        return None

    root = ET.fromstring(model)
    ns = "{http://schemas.microsoft.com/3dmanufacturing/core/2015/02}"
    vertices: list[tuple[float, float, float]] = []
    triangles: list[tuple[int, int, int]] = []
    for mesh in root.iter(ns + "mesh"):
        vertex_el = mesh.find(ns + "vertices")
        if vertex_el is None:
            continue
        base = len(vertices)
        vertices.extend(
            (float(v.get("x", 0)), float(v.get("y", 0)), float(v.get("z", 0)))
            for v in vertex_el.findall(ns + "vertex")
        )
        triangle_el = mesh.find(ns + "triangles")
        if triangle_el is None:
            continue
        for t in triangle_el.findall(ns + "triangle"):
            triangles.append(
                (
                    base + int(t.get("v1", 0)),
                    base + int(t.get("v2", 0)),
                    base + int(t.get("v3", 0)),
                )
            )
    return _from_mesh(vertices, triangles)


def _from_mesh(
    vertices: list[tuple[float, float, float]],
    faces: Sequence[Sequence[int]],
) -> Geometry | None:
    """Bounding box and volume of a mesh, or None for an empty one."""
    if not vertices or not faces:
        return None

    xs = [v[0] for v in vertices]
    ys = [v[1] for v in vertices]
    zs = [v[2] for v in vertices]
    bbox = (max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs))

    volume = 0.0
    for face in faces:
        # Fan-triangulate n-gons so meshes that return quads measure the same
        # as the all-triangle 3MF. Both diagonals of a planar quad contribute
        # the same signed volume, so the split does not change the total.
        for i in range(1, len(face) - 1):
            a, b, c = vertices[face[0]], vertices[face[i]], vertices[face[i + 1]]
            volume += (
                a[0] * (b[1] * c[2] - b[2] * c[1])
                - a[1] * (b[0] * c[2] - b[2] * c[0])
                + a[2] * (b[0] * c[1] - b[1] * c[0])
            ) / 6.0
    return Geometry(bbox=bbox, volume=abs(volume))
