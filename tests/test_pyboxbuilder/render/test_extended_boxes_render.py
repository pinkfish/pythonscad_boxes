# SPDX-License-Identifier: Apache-2.0
"""Geometric validation and render tests for extended box types."""

import tempfile
import unittest
from pathlib import Path

from pyboxbuilder.enums import BoxType, InterlockType
from pyboxbuilder.project import Project


class ExtendedBoxesRenderTests(unittest.TestCase):
    """Test geometric export and render-readiness for extended box types."""

    def test_render_export_snap_fit(self) -> None:
        p = Project("RenderSnapFit")
        p.box(
            BoxType.SNAP_FIT,
            "SnapLidded",
            size=(70.0, 50.0, 25.0),
            cantilever_thickness=1.6,
            cantilever_width=12.0,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            res = p.export(tmpdir)
            self.assertGreater(res.total_files, 0)
            mmu = Path(tmpdir) / "RenderSnapFit" / "mmu"
            self.assertTrue((mmu / "SnapLidded_body.3mf").exists())
            self.assertTrue((mmu / "SnapLidded_lid.3mf").exists())

    def test_render_export_bayonet(self) -> None:
        p = Project("RenderBayonet")
        p.box(
            BoxType.BAYONET,
            "TwistCan",
            size=(50.0, 50.0, 35.0),
            lug_count=4,
            turn_angle=90.0,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            res = p.export(tmpdir)
            self.assertGreater(res.total_files, 0)
            mmu = Path(tmpdir) / "RenderBayonet" / "mmu"
            self.assertTrue((mmu / "TwistCan_body.3mf").exists())
            self.assertTrue((mmu / "TwistCan_lid.3mf").exists())

    def test_render_export_threaded(self) -> None:
        p = Project("RenderThreaded")
        p.box(
            BoxType.THREADED,
            "ScrewJar",
            size=(45.0, 45.0, 30.0),
            thread_pitch=3.0,
            thread_turns=2.0,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            res = p.export(tmpdir)
            self.assertGreater(res.total_files, 0)
            mmu = Path(tmpdir) / "RenderThreaded" / "mmu"
            self.assertTrue((mmu / "ScrewJar_body.3mf").exists())
            self.assertTrue((mmu / "ScrewJar_lid.3mf").exists())

    def test_render_export_dispenser(self) -> None:
        p = Project("RenderDispenser")
        p.box(
            BoxType.DISPENSER,
            "TokenChute",
            size=(55.0, 55.0, 75.0),
            chute_angle=40.0,
            token_thickness=3.0,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            res = p.export(tmpdir)
            self.assertGreater(res.total_files, 0)
            mmu = Path(tmpdir) / "RenderDispenser" / "mmu"
            self.assertTrue((mmu / "TokenChute_body.3mf").exists())
            self.assertTrue((mmu / "TokenChute_lid.3mf").exists())

    def test_render_export_card_shoe(self) -> None:
        p = Project("RenderCardShoe")
        p.box(
            BoxType.CARD_SHOE,
            "DealerShoe",
            size=(130.0, 85.0, 45.0),
            draw_angle=20.0,
            retaining_lip_height=10.0,
            discard_well=True,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            res = p.export(tmpdir)
            self.assertGreater(res.total_files, 0)
            mmu = Path(tmpdir) / "RenderCardShoe" / "mmu"
            self.assertTrue((mmu / "DealerShoe_body.3mf").exists())
            self.assertTrue((mmu / "DealerShoe_lid.3mf").exists())

    def test_render_export_dice_tray(self) -> None:
        p = Project("RenderDiceTray")
        p.box(
            BoxType.DICE_TRAY,
            "RollingBox",
            size=(120.0, 90.0, 35.0),
            arena_wall_height=28.0,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            res = p.export(tmpdir)
            self.assertGreater(res.total_files, 0)
            mmu = Path(tmpdir) / "RenderDiceTray" / "mmu"
            self.assertTrue((mmu / "RollingBox_body.3mf").exists())
            self.assertTrue((mmu / "RollingBox_lid.3mf").exists())

    def test_render_export_sleeve_drawer(self) -> None:
        p = Project("RenderSleeveDrawer")
        p.box(
            BoxType.SLEEVE_DRAWER,
            "MatchboxDrawer",
            size=(70.0, 60.0, 28.0),
            push_hole_radius=12.0,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            res = p.export(tmpdir)
            self.assertGreater(res.total_files, 0)
            mmu = Path(tmpdir) / "RenderSleeveDrawer" / "mmu"
            self.assertTrue((mmu / "MatchboxDrawer_body.3mf").exists())
            self.assertTrue((mmu / "MatchboxDrawer_lid.3mf").exists())

    def test_render_export_clamshell(self) -> None:
        p = Project("RenderClamshell")
        p.box(
            BoxType.CLAMSHELL,
            "BifoldBook",
            size=(90.0, 65.0, 32.0),
            spine_gap=1.0,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            res = p.export(tmpdir)
            self.assertGreater(res.total_files, 0)
            mmu = Path(tmpdir) / "RenderClamshell" / "mmu"
            self.assertTrue((mmu / "BifoldBook_body.3mf").exists())
            self.assertTrue((mmu / "BifoldBook_lid.3mf").exists())

    def test_render_export_modular_interlock(self) -> None:
        p = Project("RenderModular")
        p.box(
            BoxType.MODULAR_INTERLOCK,
            "DovetailTray",
            size=(65.0, 65.0, 24.0),
            interlock_type=InterlockType.DOVETAIL,
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            res = p.export(tmpdir)
            self.assertGreater(res.total_files, 0)
            mmu = Path(tmpdir) / "RenderModular" / "mmu"
            self.assertTrue((mmu / "DovetailTray_body.3mf").exists())
            self.assertTrue((mmu / "DovetailTray_lid.3mf").exists())

    def test_render_export_pip_hinge(self) -> None:
        p = Project("RenderPIPHinge")
        p.box(
            BoxType.PRINT_IN_PLACE_HINGE,
            "MonolithicBox",
            size=(60.0, 45.0, 20.0),
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            res = p.export(tmpdir)
            self.assertGreater(res.total_files, 0)
            mmu = Path(tmpdir) / "RenderPIPHinge" / "mmu"
            self.assertTrue((mmu / "MonolithicBox_body.3mf").exists())
            self.assertFalse((mmu / "MonolithicBox_lid.3mf").exists())
