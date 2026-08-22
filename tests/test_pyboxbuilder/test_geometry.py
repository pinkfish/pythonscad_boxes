# SPDX-License-Identifier: Apache-2.0
"""Tests for the geometry comparison used to gate 3MF writes.

The 3MF bytes are not deterministic — OpenSCAD retriangulates a CSG tree
differently between runs — but the geometry (bounding box + volume) is. These
tests pin that: a same-shaped piece is recognised and not rewritten, and a
changed one is.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pyboxbuilder.box.shell import block
from pyboxbuilder.export.exporter import BoxExporter
from pyboxbuilder.export.geometry import (
    Geometry,
    mesh_geometry,
    read_3mf_geometry,
    same_geometry,
)


def a_cube(size: tuple[float, float, float] = (10.0, 20.0, 30.0)):
    """A real solid — a cuboid — so meshing and export have geometry to work on."""
    return block(list(size))


class SameGeometryTests(unittest.TestCase):
    def test_identical_geometry_agrees(self) -> None:
        a = Geometry((10.0, 20.0, 30.0), 6000.0)
        self.assertTrue(same_geometry(a, a))

    def test_a_shifted_bounding_box_is_different(self) -> None:
        a = Geometry((10.0, 20.0, 30.0), 6000.0)
        b = Geometry((10.5, 20.0, 30.0), 6000.0)
        self.assertFalse(same_geometry(a, b))

    def test_a_changed_volume_is_different(self) -> None:
        a = Geometry((10.0, 20.0, 30.0), 6000.0)
        b = Geometry((10.0, 20.0, 30.0), 5000.0)
        self.assertFalse(same_geometry(a, b))

    def test_none_never_agrees(self) -> None:
        self.assertFalse(same_geometry(None, Geometry((1.0, 1.0, 1.0), 1.0)))
        self.assertFalse(same_geometry(Geometry((1.0, 1.0, 1.0), 1.0), None))


class MeshGeometryTests(unittest.TestCase):
    def test_a_cube_measures_its_box_and_volume(self) -> None:
        g = mesh_geometry(a_cube())
        self.assertIsNotNone(g)
        self.assertEqual(g.bbox, (10.0, 20.0, 30.0))
        self.assertAlmostEqual(g.volume, 6000.0, delta=0.01)

    def test_a_list_of_solids_measures_their_union(self) -> None:
        g = mesh_geometry([a_cube((10.0, 10.0, 10.0)), a_cube((10.0, 10.0, 10.0))])
        self.assertIsNotNone(g)
        self.assertEqual(g.bbox, (10.0, 10.0, 10.0))
        self.assertAlmostEqual(g.volume, 1000.0, delta=0.01)

    def test_none_is_unmeasurable(self) -> None:
        self.assertIsNone(mesh_geometry(None))
        self.assertIsNone(mesh_geometry([]))


class Read3mfTests(unittest.TestCase):
    def test_a_written_cube_round_trips(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            exporter = BoxExporter(tmp, "MyGame")
            exporter.write_piece(
                "Cube", "body", "mmu", a_cube(), size=(10.0, 20.0, 30.0), fingerprint="abc"
            )
            g = read_3mf_geometry(exporter.path_for("Cube", "body", "mmu"))
            self.assertIsNotNone(g)
            self.assertEqual(g.bbox, (10.0, 20.0, 30.0))
            self.assertAlmostEqual(g.volume, 6000.0, delta=0.01)

    def test_a_missing_file_is_unreadable(self) -> None:
        self.assertIsNone(read_3mf_geometry(Path("/no/such/file.3mf")))

    def test_a_non_zip_is_unreadable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "junk.3mf"
            path.write_text("not a zip archive")
            self.assertIsNone(read_3mf_geometry(path))


class GeometryGateTests(unittest.TestCase):
    """The write is skipped when the geometry on disk already matches."""

    def test_same_geometry_is_not_rewritten_without_a_fingerprint(self) -> None:
        """A fresh clone has no fingerprint record, so the geometry comparison is
        what stops an identical piece being rewritten with different bytes."""
        with tempfile.TemporaryDirectory() as tmp:
            exporter = BoxExporter(tmp, "MyGame")
            self.assertIsNotNone(
                exporter.write_piece(
                    "Cube", "body", "mmu", a_cube(), size=(10.0, 20.0, 30.0), fingerprint="abc"
                )
            )
            # Drop the record, as a fresh clone would not have it.
            (exporter.root / "mmu" / ".fingerprints.json").unlink()

            written = exporter.write_piece(
                "Cube", "body", "mmu", a_cube(), size=(10.0, 20.0, 30.0), fingerprint="abc"
            )
            self.assertIsNone(written)
            self.assertEqual(exporter.state.skipped, ["MyGame/mmu/Cube_body.3mf"])

    def test_different_geometry_is_rewritten(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            exporter = BoxExporter(tmp, "MyGame")
            exporter.write_piece(
                "Cube", "body", "mmu", a_cube((10.0, 20.0, 30.0)),
                size=(10.0, 20.0, 30.0), fingerprint="abc",
            )
            written = exporter.write_piece(
                "Cube", "body", "mmu", a_cube((12.0, 20.0, 30.0)),
                size=(12.0, 20.0, 30.0), fingerprint="abc",
            )
            self.assertIsNotNone(written)
            self.assertEqual(exporter.state.skipped, [])


if __name__ == "__main__":
    unittest.main()
