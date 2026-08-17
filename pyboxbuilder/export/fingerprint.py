# SPDX-License-Identifier: Apache-2.0
"""Conditional write, gated on the description a piece was built from (FR-031).

Re-exporting an unchanged box should not rewrite its 3MF — a rewritten file
looks modified to the slicer and to git even when the geometry is identical.
What decides that is whether the *description* changed, and that is knowable
exactly: the box's fields, its compartments, its lid, the project's
thicknesses, the curve precision. This module records that fingerprint beside
the file and compares it on the next run.

It replaces a mesh comparison (a Hausdorff distance from pymeshlab, over 10,000
surface samples in each direction, per file). That measured the wrong thing.
OpenSCAD's boolean solver does not promise to triangulate a complex CSG tree
identically between runs, so nine of Emberleaf's pieces — the SVG player boxes,
the element-pack common box and the three spacers — measured as *changed* on
every single export and were rewritten every time, while the tolerance that
would have absorbed that was far above the 0.1mm the library promises to
resolve. A description hash is exact, costs nothing, and needs no dependency.
"""

from __future__ import annotations

import json
from pathlib import Path

SIDECAR_NAME = ".fingerprints.json"
"""Per-directory record of what each file in it was built from."""


def _sidecar(path: Path) -> Path:
    """The fingerprint record covering ``path``."""
    return path.parent / SIDECAR_NAME


def _load(path: Path) -> dict[str, str]:
    """Read a directory's fingerprints, treating any damage as a cache miss."""
    record = _sidecar(path)
    if not record.exists():
        return {}
    try:
        data = json.loads(record.read_text())
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def matches(path: Path, fingerprint: str) -> bool:
    """True when ``path`` on disk was built from this exact description.

    Args:
        path: The file that would be written.
        fingerprint: The digest of everything that decides its geometry.

    Returns:
        True only when the file exists, is not empty, and its recorded
        fingerprint is the one given. An unrecorded file is a miss, so a tree
        exported by an older version rewrites once and then settles.
    """
    if not fingerprint or not path.exists():
        return False
    return _load(path).get(path.name) == fingerprint


def record(path: Path, fingerprint: str) -> None:
    """Note what ``path`` was built from, for the next run to compare against.

    Args:
        path: The file just written.
        fingerprint: The digest of everything that decided its geometry.
    """
    if not fingerprint:
        return
    data = _load(path)
    data[path.name] = fingerprint
    try:
        _sidecar(path).write_text(json.dumps(data, indent=2, sort_keys=True))
    except OSError:
        pass  # A cache that cannot be written is a cache miss next time.


def forget(path: Path) -> None:
    """Drop ``path``'s fingerprint, so a deleted file is not remembered.

    Args:
        path: The file being removed.
    """
    data = _load(path)
    if data.pop(path.name, None) is not None:
        try:
            _sidecar(path).write_text(json.dumps(data, indent=2, sort_keys=True))
        except OSError:
            pass
