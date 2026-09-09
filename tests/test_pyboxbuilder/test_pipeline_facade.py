# SPDX-License-Identifier: Apache-2.0
"""Tests for ProjectManifest, LayoutCompiler, GeometryPipeline, and Project facade (FR-093)."""

import unittest

from pyboxbuilder.box.validation import GeometryValidationError
from pyboxbuilder.builders.sliding import SlidingBoxBuilder
from pyboxbuilder.enums import BoxType
from pyboxbuilder.layout import columns
from pyboxbuilder.project import (
    GeometryPipeline,
    LayoutCompiler,
    Project,
    ProjectManifest,
)


class ProjectManifestTests(unittest.TestCase):
    def test_manifest_creation_and_lookup(self) -> None:
        manifest = ProjectManifest("ManifestTest", game_box_size=(200, 150, 60))
        self.assertEqual(manifest.name, "ManifestTest")
        self.assertEqual(len(manifest), 0)

        box = SlidingBoxBuilder(label="Cards", size=(100, 60, 40))
        manifest.add_box(box)
        self.assertEqual(len(manifest), 1)
        self.assertIs(manifest.by_label("Cards"), box)
        self.assertIs(manifest.get_by_label("Cards"), box)
        self.assertIsNone(manifest.get_by_label("NonExistent"))

        with self.assertRaises(ValueError):
            manifest.by_label("NonExistent")

    def test_effective_size_and_slack(self) -> None:
        manifest = ProjectManifest(
            "SlackTest", game_box_size=(300, 200, 70), board_thickness=5.0
        )
        self.assertEqual(manifest.effective_game_box_size, (300, 200, 65.0))
        # max_dim = 300 > 250 -> scaled slack
        self.assertGreater(manifest.resolved_clearance_slack, 1.5)


class LayoutCompilerTests(unittest.TestCase):
    def test_check_ratios_overflow(self) -> None:
        compiler = LayoutCompiler()
        box = SlidingBoxBuilder(label="Overflow", size=(100, 60, 40))
        box.compartment("A", width_ratio=0.6)
        box.compartment("B", width_ratio=0.5)  # 0.6 + 0.5 = 1.1 > 1.0

        with self.assertRaises(ValueError) as ctx:
            compiler.check_ratios(box)
        self.assertIn("ratios sum to 1.10", str(ctx.exception))

    def test_arrange_and_min_size(self) -> None:
        compiler = LayoutCompiler()
        manifest = ProjectManifest("ArrangeTest", game_box_size=(250, 200, 60))
        b1 = SlidingBoxBuilder(label="B1", size=(100, 80, 50))
        b2 = SlidingBoxBuilder(label="B2", size=(100, 80, 50))
        manifest.add_box(b1)
        manifest.add_box(b2)

        arrangement = compiler.arrange(manifest, columns("B1", "B2"))
        self.assertIsNotNone(arrangement)
        self.assertEqual(b1.position, (0.0, 0.0, 0.0))
        self.assertEqual(b2.position, (100.0, 0.0, 0.0))


class GeometryPipelineTests(unittest.TestCase):
    def test_standalone_build(self) -> None:
        pipeline = GeometryPipeline()
        manifest = ProjectManifest("Standalone", game_box_size=None)
        box = SlidingBoxBuilder(label="Deck", size=(90, 60, 30))
        manifest.add_box(box)

        build = pipeline.build(manifest)
        self.assertIsNone(build.packing)
        labels = [p.label for p in build.pieces]
        self.assertIn("Deck", labels)

    def test_invalid_geometry_pre_csg_validation(self) -> None:
        pipeline = GeometryPipeline()
        # Wall thickness below 0.8mm should fail pre-CSG validation (FR-092)
        manifest = ProjectManifest(
            "InvalidGeom", game_box_size=(100, 100, 50), wall_thickness=0.3
        )
        box = SlidingBoxBuilder(label="ThinBox", size=(50, 50, 30))
        manifest.add_box(box)

        with self.assertRaises(GeometryValidationError) as ctx:
            pipeline.build(manifest)
        self.assertIn(
            "Wall thickness 0.3mm is below the minimum printable threshold",
            str(ctx.exception),
        )


class ProjectFacadeTests(unittest.TestCase):
    def test_facade_delegation_and_sync(self) -> None:
        p = Project("FacadeTest", game_box_size=(200, 150, 60))
        b = p.box(BoxType.SLIDING, "Tokens", size=(80, 60, 30))

        # Check manifest access
        self.assertIsInstance(p.manifest, ProjectManifest)
        self.assertIsInstance(p.compiler, LayoutCompiler)
        self.assertIsInstance(p.pipeline, GeometryPipeline)

        # Check box collections
        self.assertIn(b, p.boxes)
        self.assertIn(b, p._boxes)
        self.assertEqual(len(p.boxes), 1)

        # Attribute mutation sync
        p.wall_thickness = 3.0
        self.assertEqual(p.manifest.wall_thickness, 3.0)

        # Build execution via facade
        build = p.build()
        self.assertIsNotNone(build)
        self.assertTrue(any(piece.label == "Tokens" for piece in build.pieces))

        # Preview pieces execution via facade
        previews = p.preview_pieces(show_lids=True)
        self.assertTrue(len(previews) >= 1)
        self.assertTrue(any(pp.label == "Tokens" for pp in previews))
