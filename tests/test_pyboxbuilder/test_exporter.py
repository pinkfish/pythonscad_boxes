# SPDX-License-Identifier: Apache-2.0
"""Tests for the export pipeline: BoxExporter, fingerprint gating, sizing."""

from __future__ import annotations

import tempfile
import unittest
import zipfile
from pathlib import Path

from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY, BOX_TYPE_REGISTRY, LIDLESS_BOX_TYPES
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.compartments.sizing import RowItem, distribute_row_width, rows_from_placements
from pyboxbuilder.enums import BoxType
from pyboxbuilder.export import fingerprint as fp
from pyboxbuilder.export.exporter import BoxExporter, PieceBounds


class BoxExporterTests(unittest.TestCase):
    def test_file_names_follow_the_documented_scheme(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            exporter = BoxExporter(tmp, "MyGame")
            self.assertEqual(
                exporter.path_for("Cards", "body", "mmu").name, "Cards_body.3mf"
            )
            self.assertEqual(
                exporter.path_for("Cards", "lid", "single").name, "Cards_lid_single.3mf"
            )

    def test_write_box_produces_both_modes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            exporter = BoxExporter(tmp, "MyGame")
            written = exporter.write_box("Cards", size=(100.0, 70.0, 50.0))
            self.assertEqual(written, [
                "MyGame/mmu/Cards_body.3mf",
                "MyGame/mmu/Cards_lid.3mf",
                "MyGame/single/Cards_body_single.3mf",
                "MyGame/single/Cards_lid_single.3mf",
            ])

    def test_lidless_boxes_get_a_body_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            exporter = BoxExporter(tmp, "MyGame")
            written = exporter.write_box("Tray", size=(50.0, 50.0, 20.0), has_lid=False)
            self.assertEqual(len(written), 2)
            self.assertTrue(all("_body" in path for path in written))

    def test_bounding_boxes_are_recorded_for_every_piece(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            exporter = BoxExporter(tmp, "MyGame")
            exporter.write_box("Cards", size=(100.0, 70.0, 50.0), has_lid=False)
            self.assertEqual(len(exporter.state.bounds), 2)
            self.assertEqual(exporter.state.bounds[0].size, (100.0, 70.0, 50.0))

    def test_stale_files_are_deleted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            exporter = BoxExporter(tmp, "MyGame")
            exporter.write_box("spacer_1", size=(10.0, 10.0, 10.0), has_lid=False)
            exporter.write_box("spacer_2", size=(10.0, 10.0, 10.0), has_lid=False)

            removed = exporter.delete_stale("spacer_", {"spacer_1"})
            self.assertEqual(len(removed), 2)  # both modes of spacer_2
            self.assertTrue(exporter.path_for("spacer_1", "body", "mmu").exists())
            self.assertFalse(exporter.path_for("spacer_2", "body", "mmu").exists())

    def test_real_geometry_is_exported_as_a_3mf(self) -> None:
        from pyboxbuilder.box.shell import build_shell
        from pyboxbuilder.box.spec import BoxSpec

        spec = BoxSpec(label="Tray", width=60.0, length=40.0, height=20.0,
                       wall_thickness=2.0, floor_thickness=1.6)
        with tempfile.TemporaryDirectory() as tmp:
            exporter = BoxExporter(tmp, "MyGame")
            exporter.write_box("Tray", body=build_shell(spec), has_lid=False)

            path = exporter.path_for("Tray", "body", "mmu")
            self.assertTrue(zipfile.is_zipfile(path), "3MF should be a zip container")
            model = zipfile.ZipFile(path).read("3D/3dmodel.model").decode()
            self.assertIn("<triangle", model)


class PieceBoundsTests(unittest.TestCase):
    def test_fits_bed_compares_every_axis(self) -> None:
        piece = PieceBounds("Cards_body", (200.0, 200.0, 180.0), "mmu")
        self.assertTrue(piece.fits_bed((256.0, 256.0, 256.0)))
        self.assertFalse(piece.fits_bed((180.0, 180.0, 180.0)))

    def test_str_reports_the_measured_size(self) -> None:
        self.assertEqual(
            str(PieceBounds("Cards_body", (100.0, 70.0, 50.0), "mmu")),
            "Cards_body [mmu]: 100.0 x 70.0 x 50.0 mm",
        )


class FingerprintGateTests(unittest.TestCase):
    """An unchanged piece must not be rewritten (FR-031 / SC-012)."""

    SIZE = (60.0, 40.0, 20.0)

    def _spec(self):
        from pyboxbuilder.box.spec import BoxSpec

        return BoxSpec(label="Tray", width=60.0, length=40.0, height=20.0)

    def _write(self, exporter, fingerprint: str):
        from pyboxbuilder.box.shell import build_shell

        return exporter.write_piece(
            "Tray", "body", "mmu", build_shell(self._spec()),
            size=self.SIZE, fingerprint=fingerprint,
        )

    def _current(self, exporter, fingerprint: str) -> bool:
        return exporter.is_current("Tray", "body", "mmu", fingerprint)

    def test_the_same_description_is_recognised(self) -> None:
        """`is_current` answers **before** the geometry is built, which is what
        makes an unchanged box free rather than merely quiet."""
        with tempfile.TemporaryDirectory() as tmp:
            exporter = BoxExporter(tmp, "MyGame")
            self.assertFalse(self._current(exporter, "abc"))
            self._write(exporter, "abc")
            self.assertTrue(self._current(exporter, "abc"))

    def test_a_changed_description_is_stale(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            exporter = BoxExporter(tmp, "MyGame")
            self._write(exporter, "abc")
            self.assertFalse(self._current(exporter, "def"))

    def test_an_unfingerprinted_file_is_always_stale(self) -> None:
        """A tree exported by an older version rewrites once, then settles."""
        with tempfile.TemporaryDirectory() as tmp:
            exporter = BoxExporter(tmp, "MyGame")
            self._write(exporter, "")
            self.assertFalse(self._current(exporter, ""))

    def test_a_missing_file_is_stale_however_it_was_fingerprinted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            exporter = BoxExporter(tmp, "MyGame")
            self._write(exporter, "abc")
            exporter.path_for("Tray", "body", "mmu").unlink()
            self.assertFalse(self._current(exporter, "abc"))

    def test_a_corrupt_record_is_a_cache_miss_not_a_crash(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            exporter = BoxExporter(tmp, "MyGame")
            self._write(exporter, "abc")
            sidecar = exporter.root / "mmu" / fp.SIDECAR_NAME
            sidecar.write_text("{not json")
            self.assertFalse(self._current(exporter, "abc"))

    def test_a_skipped_piece_is_reported_with_its_bounds(self) -> None:
        """It is still one of the project's pieces, and FR-027 still wants its
        size — the declared one, since measuring means building it."""
        with tempfile.TemporaryDirectory() as tmp:
            exporter = BoxExporter(tmp, "MyGame")
            exporter.note_unchanged("Tray", "body", "mmu", self.SIZE)
            self.assertEqual(exporter.state.skipped, ["MyGame/mmu/Tray_body.3mf"])
            self.assertEqual(exporter.state.bounds[0].size, self.SIZE)

    def test_deleting_a_stale_file_forgets_its_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            exporter = BoxExporter(tmp, "MyGame")
            exporter.write_piece(
                "spacer_9", "body", "mmu", size=self.SIZE, fingerprint="abc"
            )
            path = exporter.path_for("spacer_9", "body", "mmu")
            exporter.delete_stale("spacer_", set())
            self.assertFalse(fp.matches(path, "abc"))


class RowSizingTests(unittest.TestCase):
    """T052a — compartments grow to fill the row they sit in."""

    def test_slack_is_shared_in_proportion_to_width(self) -> None:
        row = [RowItem("wide", 60.0, 40.0), RowItem("narrow", 20.0, 40.0)]
        # 200 available, 80 used, 6 of gap → 114 of slack, split 3:1.
        resolved = distribute_row_width(row, 200.0, gap=2.0)
        self.assertEqual(resolved[0][1], 145.5)
        self.assertEqual(resolved[1][1], 48.5)
        self.assertEqual(sum(w for _, w, _ in resolved) + 6.0, 200.0)

    def test_pinned_items_keep_their_width(self) -> None:
        row = [RowItem("card", 66.0, 91.0, growable=False), RowItem("tokens", 30.0, 91.0)]
        resolved = distribute_row_width(row, 150.0, gap=2.0)
        self.assertEqual(resolved[0][1], 66.0)
        self.assertEqual(resolved[1][1], 78.0)

    def test_a_row_with_no_slack_is_left_alone(self) -> None:
        row = [RowItem("a", 48.0, 40.0), RowItem("b", 48.0, 40.0)]
        self.assertEqual(
            distribute_row_width(row, 102.0, gap=2.0),
            [("a", 48.0, 40.0), ("b", 48.0, 40.0)],
        )

    def test_an_overfull_row_is_rejected_by_name(self) -> None:
        row = [RowItem("huge", 200.0, 40.0)]
        with self.assertRaises(ValueError) as ctx:
            distribute_row_width(row, 100.0, gap=2.0)
        self.assertIn("huge", str(ctx.exception))

    def test_an_empty_row_resolves_to_nothing(self) -> None:
        self.assertEqual(distribute_row_width([], 100.0), [])

    def test_placements_group_into_rows_by_y(self) -> None:
        from pyboxbuilder.compartments.layout import CompartmentPlacement

        placements = [
            CompartmentPlacement("a", (20, 20), 10, (0, 0)),
            CompartmentPlacement("b", (20, 20), 10, (25, 0)),
            CompartmentPlacement("c", (20, 20), 10, (0, 30)),
        ]
        self.assertEqual(rows_from_placements(placements), [["a", "b"], ["c"]])


class PathBoxTests(unittest.TestCase):
    """T028/T032 — the lidless polygon-footprint box type."""

    def test_path_is_registered_as_a_box_type(self) -> None:
        self.assertIn(BoxType.PATH, BOX_TYPE_REGISTRY)
        self.assertIn(BoxType.PATH, BOX_IMPL_REGISTRY)

    def test_path_boxes_are_lidless(self) -> None:
        self.assertEqual(LIDLESS_BOX_TYPES, frozenset({BoxType.NO_LID, BoxType.PATH}))
        box = BOX_IMPL_REGISTRY[BoxType.PATH]()
        self.assertIsNone(box.build_lid(BoxSpec(width=50, length=50, height=20)))

    def test_a_path_box_with_no_path_is_a_plain_tray(self) -> None:
        box = BOX_IMPL_REGISTRY[BoxType.PATH]()
        from pyboxbuilder.box.spec import BoxSpec

        spec = BoxSpec(label="Tray", width=60.0, length=40.0, height=20.0,
                       wall_thickness=2.0, floor_thickness=1.6)
        _, size = box.build_body(spec).bounds()
        # Sizes carry the rounding's 0.002mm faceting tolerance: a fillet is
        # an inscribed polygon, so it pulls its faces in by the sagitta.
        self.assertAlmostEqual(size[0], 60.0, delta=0.01)
        self.assertAlmostEqual(size[1], 40.0, delta=0.01)
        self.assertAlmostEqual(size[2], 20.0, delta=0.01)

    def test_a_polygon_footprint_is_extruded_from_the_bed_up(self) -> None:
        box = BOX_IMPL_REGISTRY[BoxType.PATH]()
        spec = BoxSpec(width=60.0, length=40.0, height=20.0,
            wall_thickness=2.0, floor_thickness=1.6,
            path=((0.0, 0.0), (60.0, 0.0), (60.0, 25.0), (30.0, 40.0), (0.0, 25.0)))
        centre, size = box.build_body(spec).bounds()
        self.assertAlmostEqual(size[2], 20.0, places=3)
        self.assertAlmostEqual(centre[2] - size[2] / 2, 0.0, places=3)

    def test_interior_reserves_the_walls_and_floor(self) -> None:
        box = BOX_IMPL_REGISTRY[BoxType.PATH]()
        interior = box.interior(BoxSpec(width=60.0, length=40.0, height=20.0,
            wall_thickness=2.0, floor_thickness=1.6))
        self.assertEqual(
            (interior.width, interior.length, interior.height), (56.0, 36.0, 18.4)
        )


if __name__ == "__main__":
    unittest.main()
