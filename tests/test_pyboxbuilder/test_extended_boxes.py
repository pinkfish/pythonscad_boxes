# SPDX-License-Identifier: Apache-2.0
"""Unit tests for the 10 extended box types and closure mechanisms (FR-081–FR-090)."""

import tempfile
import unittest
from pathlib import Path

from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY, LIDLESS_BOX_TYPES
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.builders import (
    BayonetBoxBuilder,
    CardShoeBoxBuilder,
    ClamshellBoxBuilder,
    DiceTrayBoxBuilder,
    DispenserBoxBuilder,
    ModularInterlockBoxBuilder,
    PrintInPlaceHingeBoxBuilder,
    SleeveDrawerBoxBuilder,
    SnapFitBoxBuilder,
    ThreadedBoxBuilder,
)
from pyboxbuilder.enums import BoxType, DispenserExtractionMode, InterlockType
from pyboxbuilder.project import Project


class ExtendedBoxBuildersTests(unittest.TestCase):
    """Test builder instantiation, fields, and project integration."""

    def test_snap_fit_builder(self) -> None:
        p = Project("TestSnapFit")
        b = p.box(
            BoxType.SNAP_FIT,
            "SnapBox",
            size=(80, 60, 30),
            cantilever_thickness=1.8,
            cantilever_width=14.0,
            deflection_clearance=0.35,
            detent_height=1.6,
            latch_axis="y",
        )
        self.assertIsInstance(b, SnapFitBoxBuilder)
        self.assertEqual(b.cantilever_thickness, 1.8)
        self.assertEqual(b.cantilever_width, 14.0)
        self.assertEqual(b.deflection_clearance, 0.35)
        self.assertEqual(b.detent_height, 1.6)
        self.assertEqual(b.latch_axis, "y")

    def test_bayonet_builder(self) -> None:
        p = Project("TestBayonet")
        b = p.box(
            BoxType.BAYONET,
            "BayonetCanister",
            size=(50, 50, 40),
            lug_count=3,
            turn_angle=45.0,
            lug_height=3.0,
            lug_depth=1.5,
            bayonet_slack=0.25,
            round_footprint=True,
        )
        self.assertIsInstance(b, BayonetBoxBuilder)
        self.assertEqual(b.lug_count, 3)
        self.assertEqual(b.turn_angle, 45.0)
        self.assertEqual(b.lug_height, 3.0)
        self.assertEqual(b.lug_depth, 1.5)
        self.assertEqual(b.bayonet_slack, 0.25)
        self.assertTrue(b.round_footprint)

    def test_threaded_builder(self) -> None:
        p = Project("TestThreaded")
        b = p.box(
            BoxType.THREADED,
            "ScrewBox",
            size=(45, 45, 35),
            thread_pitch=3.5,
            thread_turns=2.5,
            thread_clearance=0.3,
            thread_depth=1.2,
        )
        self.assertIsInstance(b, ThreadedBoxBuilder)
        self.assertEqual(b.thread_pitch, 3.5)
        self.assertEqual(b.thread_turns, 2.5)
        self.assertEqual(b.thread_clearance, 0.3)
        self.assertEqual(b.thread_depth, 1.2)

    def test_dispenser_builder(self) -> None:
        p = Project("TestDispenser")
        b = p.box(
            BoxType.DISPENSER,
            "Tower",
            size=(55, 55, 80),
            chute_angle=38.0,
            token_thickness=2.5,
            dispense_slot_clearance=0.7,
            sight_slot_width=9.0,
        )
        self.assertIsInstance(b, DispenserBoxBuilder)
        self.assertEqual(b.chute_angle, 38.0)
        self.assertEqual(b.token_thickness, 2.5)
        self.assertEqual(b.dispense_slot_clearance, 0.7)
        self.assertEqual(b.sight_slot_width, 9.0)
        self.assertIsNone(b.sight_slot_start)
        self.assertEqual(b.dispenser_mode, DispenserExtractionMode.SCOOP)
        self.assertEqual(b.scoop_radius, 14.0)
        self.assertEqual(b.floor_scoop_depth, 12.0)
        self.assertEqual(b.floor_scoop_width, 24.0)
        self.assertEqual(b.tray_depth, 20.0)
        self.assertEqual(b.rear_push_width, 22.0)

    def test_card_shoe_builder(self) -> None:
        p = Project("TestCardShoe")
        b = p.box(
            BoxType.CARD_SHOE,
            "Shoe",
            size=(140, 95, 45),
            draw_angle=22.0,
            retaining_lip_height=12.0,
            discard_well=True,
        )
        self.assertIsInstance(b, CardShoeBoxBuilder)
        self.assertEqual(b.draw_angle, 22.0)
        self.assertEqual(b.retaining_lip_height, 12.0)
        self.assertTrue(b.discard_well)

    def test_dice_tray_builder(self) -> None:
        p = Project("TestDiceTray")
        b = p.box(
            BoxType.DICE_TRAY,
            "Arena",
            size=(160, 120, 40),
            arena_wall_height=30.0,
            felt_pocket_depth=1.5,
            corner_deflectors=True,
        )
        self.assertIsInstance(b, DiceTrayBoxBuilder)
        self.assertEqual(b.arena_wall_height, 30.0)
        self.assertEqual(b.felt_pocket_depth, 1.5)
        self.assertTrue(b.corner_deflectors)
        # FR-086 / MMU rolling area lid enhancements
        self.assertIsNotNone(b.lid)
        assert b.lid is not None
        self.assertEqual(b.lid.text, "Arena")
        self.assertIsNotNone(b.lid.pattern)
        assert b.lid.pattern is not None
        self.assertTrue(b.lid.pattern.inlay)
        # Preview in MMU generates body, lid, pattern insert, and text insert
        pieces = p.preview_pieces(show_lids=True)
        self.assertEqual(len(pieces), 4)


    def test_sleeve_drawer_builder(self) -> None:
        p = Project("TestSleeveDrawer")
        b = p.box(
            BoxType.SLEEVE_DRAWER,
            "Matchbox",
            size=(75, 65, 30),
            push_hole_radius=10.0,
            drawer_pull_lip=5.0,
            sleeve_slack=0.25,
        )
        self.assertIsInstance(b, SleeveDrawerBoxBuilder)
        self.assertEqual(b.push_hole_radius, 10.0)
        self.assertEqual(b.drawer_pull_lip, 5.0)
        self.assertEqual(b.drawer_handle_length, 5.0)
        self.assertEqual(b.sleeve_slack, 0.25)

    def test_sleeve_drawer_solid_and_handle(self) -> None:
        """Sleeve drawer defaults to solid back wall, front handle, and intact front wall."""
        from mesh import volume

        p = Project("MatchboxSolidTest")
        box = p.box(
            BoxType.SLEEVE_DRAWER,
            "SolidDrawer",
            size=(70.0, 60.0, 28.0),
            drawer_handle_style="handle",
            drawer_handle_length=4.0,
        )
        self.assertEqual(box.push_hole_radius, 0.0)
        box.compartment("Cards", holds_pieces=True)

        pieces = p.preview_pieces(show_lids=True)
        self.assertEqual(len(pieces), 2)
        drawer_piece = [pc for pc in pieces if pc.label == "SolidDrawer"][0]
        sleeve_piece = [pc for pc in pieces if pc.label == "SolidDrawer"][1]

        # Drawer handle extends in -Y by 4mm
        b_box = drawer_piece.solid.bounds()
        min_y = float(b_box[0][1]) if isinstance(b_box, tuple) else float(b_box.min[1])
        self.assertAlmostEqual(min_y, 28.0, delta=1.5)  # in preview packed layout

        # Compare solid back sleeve vs pierced back sleeve
        p_hole = Project("MatchboxHoleTest")
        box_hole = p_hole.box(
            BoxType.SLEEVE_DRAWER,
            "HoleDrawer",
            size=(70.0, 60.0, 28.0),
            push_hole_radius=10.0,
        )
        pieces_hole = p_hole.preview_pieces(show_lids=True)
        sleeve_hole_piece = [pc for pc in pieces_hole if pc.label == "HoleDrawer"][1]
        self.assertGreater(volume(sleeve_piece.solid), volume(sleeve_hole_piece.solid))

    def test_clamshell_builder(self) -> None:
        p = Project("TestClamshell")
        b = p.box(
            BoxType.CLAMSHELL,
            "Book",
            size=(110, 75, 36),
            spine_gap=1.2,
            clamshell_hinge_radius=2.8,
            closure_latch=True,
        )
        self.assertIsInstance(b, ClamshellBoxBuilder)
        self.assertEqual(b.spine_gap, 1.2)
        self.assertEqual(b.clamshell_hinge_radius, 2.8)
        self.assertTrue(b.closure_latch)

    def test_modular_interlock_builder(self) -> None:
        p = Project("TestModular")
        b = p.box(
            BoxType.MODULAR_INTERLOCK,
            "Tray",
            size=(84, 84, 25),
            interlock_type=InterlockType.GRIDFINITY,
            dovetail_clearance=0.2,
            gridfinity_pitch=42.0,
        )
        self.assertIsInstance(b, ModularInterlockBoxBuilder)
        self.assertEqual(b.interlock_type, InterlockType.GRIDFINITY)
        self.assertEqual(b.dovetail_clearance, 0.2)
        self.assertEqual(b.gridfinity_pitch, 42.0)

    def test_pip_hinge_builder(self) -> None:
        p = Project("TestPIPHinge")
        b = p.box(
            BoxType.PRINT_IN_PLACE_HINGE,
            "HingedBox",
            size=(65, 45, 22),
            pip_radial_clearance=0.38,
            pip_axial_clearance=0.45,
            pip_cone_angle=45.0,
            pip_hinge_radius=3.2,
        )
        self.assertIsInstance(b, PrintInPlaceHingeBoxBuilder)
        self.assertEqual(b.pip_radial_clearance, 0.38)
        self.assertEqual(b.pip_axial_clearance, 0.45)
        self.assertEqual(b.pip_cone_angle, 45.0)
        self.assertEqual(b.pip_hinge_radius, 3.2)


class ExtendedBoxGeometryTests(unittest.TestCase):
    """Test geometric build for all 10 new box implementations."""

    def test_all_10_geometry_solids(self) -> None:
        box_types = [
            BoxType.SNAP_FIT,
            BoxType.BAYONET,
            BoxType.THREADED,
            BoxType.DISPENSER,
            BoxType.CARD_SHOE,
            BoxType.DICE_TRAY,
            BoxType.SLEEVE_DRAWER,
            BoxType.CLAMSHELL,
            BoxType.MODULAR_INTERLOCK,
            BoxType.PRINT_IN_PLACE_HINGE,
        ]

        for bt in box_types:
            impl_cls = BOX_IMPL_REGISTRY[bt]
            impl = impl_cls()
            spec = BoxSpec(label="Test", width=60.0, length=50.0, height=30.0)

            interior = impl.interior(spec)
            self.assertGreater(interior.width, 0)
            self.assertGreater(interior.length, 0)
            self.assertGreater(interior.height, 0)

            body = impl.build_body(spec)
            self.assertIsNotNone(body)

            lid = impl.build_lid(spec)
            if bt in LIDLESS_BOX_TYPES:
                self.assertIsNone(lid)
            else:
                self.assertIsNotNone(lid)

    def test_export_all_10_types(self) -> None:
        """Verify all 10 new types export to 3MF properly and PIP hinge produces no lid file."""
        p = Project("ExtendedExport", game_box_size=(600, 600, 100))

        p.box(BoxType.SNAP_FIT, "Snap", size=(60, 50, 25))
        p.box(BoxType.BAYONET, "Bayo", size=(50, 50, 30))
        p.box(BoxType.THREADED, "Thrd", size=(45, 45, 30))
        p.box(BoxType.DISPENSER, "Disp", size=(50, 50, 70))
        p.box(BoxType.CARD_SHOE, "Shoe", size=(120, 80, 40))
        p.box(BoxType.DICE_TRAY, "Tray", size=(100, 80, 35))
        p.box(BoxType.SLEEVE_DRAWER, "Slv", size=(65, 55, 28))
        p.box(BoxType.CLAMSHELL, "Clam", size=(80, 60, 30))
        p.box(BoxType.MODULAR_INTERLOCK, "Mod", size=(70, 70, 25))
        p.box(BoxType.PRINT_IN_PLACE_HINGE, "PIP", size=(60, 40, 20))

        with tempfile.TemporaryDirectory() as tmpdir:
            result = p.export(tmpdir)
            self.assertGreater(result.total_files, 0)

            mmu_dir = Path(tmpdir) / "ExtendedExport" / "mmu"

            # All 10 bodies must exist
            self.assertTrue((mmu_dir / "Snap_body.3mf").exists())
            self.assertTrue((mmu_dir / "Bayo_body.3mf").exists())
            self.assertTrue((mmu_dir / "Thrd_body.3mf").exists())
            self.assertTrue((mmu_dir / "Disp_body.3mf").exists())
            self.assertTrue((mmu_dir / "Shoe_body.3mf").exists())
            self.assertTrue((mmu_dir / "Tray_body.3mf").exists())
            self.assertTrue((mmu_dir / "Slv_body.3mf").exists())
            self.assertTrue((mmu_dir / "Clam_body.3mf").exists())
            self.assertTrue((mmu_dir / "Mod_body.3mf").exists())
            self.assertTrue((mmu_dir / "PIP_body.3mf").exists())

            # 9 lidded types must have lid files
            self.assertTrue((mmu_dir / "Snap_lid.3mf").exists())
            self.assertTrue((mmu_dir / "Bayo_lid.3mf").exists())
            self.assertTrue((mmu_dir / "Thrd_lid.3mf").exists())
            self.assertTrue((mmu_dir / "Disp_lid.3mf").exists())
            self.assertTrue((mmu_dir / "Shoe_lid.3mf").exists())
            self.assertTrue((mmu_dir / "Tray_lid.3mf").exists())
            self.assertTrue((mmu_dir / "Slv_lid.3mf").exists())
            self.assertTrue((mmu_dir / "Clam_lid.3mf").exists())
            self.assertTrue((mmu_dir / "Mod_lid.3mf").exists())

            # Monolithic PIP hinge produces NO lid file (FR-090)
            self.assertFalse((mmu_dir / "PIP_lid.3mf").exists())

    def test_pip_hinge_split_halfway(self) -> None:
        """Verify PIP hinge box splits halfway up the side (FR-090)."""
        impl = BOX_IMPL_REGISTRY[BoxType.PRINT_IN_PLACE_HINGE]()
        spec = BoxSpec(label="PIP50", width=60.0, length=40.0, height=30.0)
        solid = impl.build_body(spec)
        self.assertIsNotNone(solid)

        # Interior height of the base tray must be half the total height minus floor
        interior = impl.interior(spec)
        self.assertAlmostEqual(interior.height, 15.0 - spec.floor_thickness)

        # The monolithic build spans from z=0 up to half_h + hr
        b = solid.bounds()
        centre, size = (b.center, b.size) if hasattr(b, "center") else b
        z_min = centre[2] - size[2] / 2.0
        z_max = centre[2] + size[2] / 2.0
        self.assertAlmostEqual(z_min, 0.0, delta=0.5)
        # Top of the snap catch tabs reaches half_h + ~4.7mm (or half_h + hr without catches)
        self.assertAlmostEqual(z_max, 15.0 + 4.71, delta=0.5)

    def test_dispenser_lower_cover(self) -> None:
        """Verify gravity tile dispenser has a solid front cover over the lower half (FR-084)."""
        from pyboxbuilder.box.shell import block
        from tests.mesh import volume

        impl = BOX_IMPL_REGISTRY[BoxType.DISPENSER]()
        spec = BoxSpec(
            label="Chute",
            width=55.0,
            length=55.0,
            height=70.0,
            chute_angle=40.0,
            token_thickness=3.0,
        )
        body = impl.build_body(spec)
        self.assertIsNotNone(body)

        # In the lower half (z = 20..30mm), the front wall (y = 0..wt, x across the center)
        # must be solid (covered over the gap), NOT cut through all the way down.
        # Probe a 15mm wide slice across the center where the sight slot is positioned.
        probe_w = 15.0
        probe_h = 10.0
        probe = block(
            [probe_w, spec.wall_thickness, probe_h],
            at=((spec.width - probe_w) / 2.0, 0.0, 20.0),
        )
        wall_vol = volume(body & probe)
        expected_vol = probe_w * spec.wall_thickness * probe_h  # 15 * 2 * 10 = 300 mm³
        self.assertAlmostEqual(wall_vol, expected_vol, delta=1.0)

    def test_dispenser_extraction_modes(self) -> None:
        """Test all 4 extraction mechanisms: SCOOP, TRAY, REAR_PUSH, ARCH."""
        from pyboxbuilder.box.shell import block
        from tests.mesh import volume

        impl = BOX_IMPL_REGISTRY[BoxType.DISPENSER]()
        base_spec = BoxSpec(
            label="Chute",
            width=55.0,
            length=55.0,
            height=70.0,
            chute_angle=35.0,
            token_thickness=3.0,
        )

        # 1. SCOOP (default): verify floor cutout allows pinching under the tile
        scoop_body = impl.build_body(base_spec)
        self.assertIsNotNone(scoop_body)
        floor_probe = block([20.0, 10.0, base_spec.floor_thickness], at=((55.0 - 20.0) / 2.0, 0.0, 0.0))
        # Floor notch cuts through the floor at the front center
        self.assertAlmostEqual(volume(scoop_body & floor_probe), 0.0, delta=1.0)

        # 2. TRAY mode: protruding front shelf expands bounding box in -Y
        tray_spec = BoxSpec(
            label="TrayDisp",
            width=55.0,
            length=55.0,
            height=70.0,
            dispenser_mode=DispenserExtractionMode.TRAY,
            tray_depth=20.0,
        )
        tray_body = impl.build_body(tray_spec)
        self.assertIsNotNone(tray_body)
        tray_probe = block([50.0, 15.0, base_spec.floor_thickness], at=(2.5, -18.0, 0.0))
        self.assertGreater(volume(tray_body & tray_probe), 200.0)

        # 3. REAR_PUSH mode: rear push cutout through the back wall at floor level
        rear_spec = BoxSpec(
            label="RearDisp",
            width=55.0,
            length=55.0,
            height=70.0,
            dispenser_mode=DispenserExtractionMode.REAR_PUSH,
            rear_push_width=20.0,
        )
        rear_body = impl.build_body(rear_spec)
        self.assertIsNotNone(rear_body)
        rear_probe = block([18.0, base_spec.wall_thickness, 8.0], at=((55.0 - 18.0) / 2.0, 55.0 - base_spec.wall_thickness, base_spec.floor_thickness))
        self.assertAlmostEqual(volume(rear_body & rear_probe), 0.0, delta=1.0)

        # 4. ARCH mode: front wall is open through archway
        arch_spec = BoxSpec(
            label="ArchDisp",
            width=55.0,
            length=55.0,
            height=70.0,
            dispenser_mode=DispenserExtractionMode.ARCH,
            arch_height=40.0,
        )
        arch_body = impl.build_body(arch_spec)
        self.assertIsNotNone(arch_body)
        arch_probe = block([20.0, base_spec.wall_thickness, 15.0], at=((55.0 - 20.0) / 2.0, 0.0, 20.0))
        self.assertAlmostEqual(volume(arch_body & arch_probe), 0.0, delta=1.0)


