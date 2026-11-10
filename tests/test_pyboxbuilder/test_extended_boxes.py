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
    InsetHingeBoxBuilder,
    ModularInterlockBoxBuilder,
    PrintInPlaceHingeBoxBuilder,
    SleeveDrawerBoxBuilder,
    SlidingHingeBoxBuilder,
    SnapFitBoxBuilder,
    ThreadedBoxBuilder,
)
from pyboxbuilder.enums import (
    BoxType,
    CatchType,
    DispenserExtractionMode,
    InterlockType,
    LatchAxis,
)
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
        self.assertEqual(b.latch_axis, LatchAxis.Y)

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
        b_default = p.box(BoxType.DISPENSER, "DefaultTower", size=(55, 55, 80))
        self.assertIsInstance(b_default, DispenserBoxBuilder)
        self.assertEqual(b_default.chute_angle, 0.0)
        self.assertEqual(b_default.dispenser_mode, DispenserExtractionMode.SCOOP)

        b_angled = p.box(
            BoxType.DISPENSER,
            "AngledTower",
            size=(55, 55, 80),
            tile_angle=25.0,
        )
        self.assertEqual(b_angled.chute_angle, 25.0)
        self.assertEqual(b_angled.tile_angle, 25.0)

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
        from pyboxbuilder.enums import PatternType

        self.assertEqual(b.lid.pattern.backing_pattern, PatternType.HEX)
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
        center_y = (
            float(b_box.center[1]) if hasattr(b_box, "center") else float(b_box[0][1])
        )
        self.assertAlmostEqual(center_y, 28.0, delta=1.5)  # in preview packed layout

        # Verify drawer front wall (y=0..wt) is 100% solid behind handle (compartment does not breach front wall)
        from pyboxbuilder.box.shell import block

        sw = 1.2
        slack = 0.25
        wt = 2.0
        drawer_w = 70.0 - 2 * (sw + slack)
        drawer_h = 28.0 - 2 * (sw + slack)
        front_wall_probe = block(
            [drawer_w, wt, drawer_h], at=(sw + slack, 0.0, sw + slack)
        )
        actual_front = volume(drawer_piece.solid & front_wall_probe)
        expected_front = drawer_w * wt * drawer_h
        self.assertAlmostEqual(
            actual_front, expected_front, delta=15.0
        )  # delta accounts for corner rounding

        # Verify outer sleeve has no through-hole hex pattern (remains solid)
        sleeve_top_probe = block([60.0, 50.0, sw], at=(5.0, 5.0, 28.0 - sw))
        actual_sleeve_top = volume(sleeve_piece.solid & sleeve_top_probe)
        expected_sleeve_top = 60.0 * 50.0 * sw
        self.assertAlmostEqual(actual_sleeve_top, expected_sleeve_top, delta=15.0)

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
        self.assertEqual(b.pip_bridge_width, 0.4)
        self.assertEqual(b.pip_bridge_thickness, 0.4)

        b2 = p.box(
            BoxType.PRINT_IN_PLACE_HINGE,
            "CustomBridgeBox",
            size=(50, 40, 20),
            pip_bridge_width=0.6,
            pip_bridge_thickness=0.5,
        )
        self.assertEqual(b2.pip_bridge_width, 0.6)
        self.assertEqual(b2.pip_bridge_thickness, 0.5)

    def test_inset_hinge_builder(self) -> None:
        p = Project("TestInsetHinge")
        b = p.box(
            BoxType.INSET_HINGE,
            "InsetBox",
            size=(65, 50, 26),
            pip_hinge_radius=3.0,
            pip_radial_clearance=0.30,
            inset_hinge_side_gap=3.5,
            inset_hinge_tab_height=5.0,
        )
        self.assertIsInstance(b, InsetHingeBoxBuilder)
        self.assertEqual(b.pip_hinge_radius, 3.0)
        self.assertEqual(b.pip_radial_clearance, 0.30)
        self.assertEqual(b.inset_hinge_side_gap, 3.5)
        self.assertEqual(b.inset_hinge_tab_height, 5.0)

    def test_sliding_hinge_builder(self) -> None:
        p = Project("TestSlidingHinge")
        b = p.box(
            BoxType.SLIDING_HINGE,
            "SlideHingeBox",
            size=(70, 55, 28),
            catch_type=CatchType.SLIDE_ACROSS,
            slide_catch_style="card_library",
            pip_radial_clearance=0.30,
        )
        self.assertIsInstance(b, SlidingHingeBoxBuilder)
        self.assertEqual(b.catch_type, CatchType.SLIDE_ACROSS)
        self.assertEqual(b.slide_catch_style, "card_library")
        self.assertEqual(b.pip_radial_clearance, 0.30)


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

        # The monolithic build spans from z=0 up to half_h + snap_h
        b = solid.bounds()
        centre, size = (b.center, b.size) if hasattr(b, "center") else b
        z_min = centre[2] - size[2] / 2.0
        z_max = centre[2] + size[2] / 2.0
        self.assertAlmostEqual(z_min, 0.0, delta=0.5)
        self.assertAlmostEqual(z_max, 19.0, delta=0.5)

    def test_pip_hinge_middle_knuckles_and_clean_catch(self) -> None:
        """Verify knuckle hinge is placed along the 1.0mm shared mating rim and front walls have a clean snap catch."""
        from pyboxbuilder.box.shell import block
        from tests.mesh import volume

        impl = BOX_IMPL_REGISTRY[BoxType.PRINT_IN_PLACE_HINGE]()
        spec = BoxSpec(label="KnucklePIPBox", width=60.0, length=40.0, height=30.0)
        body = impl.build_body(spec)
        self.assertIsNotNone(body)

        hr = spec.pip_hinge_radius
        gap = spec.pip_gap_mm
        self.assertAlmostEqual(gap, 1.0)
        y_pivot = spec.length + gap / 2.0
        half_h = spec.height / 2.0

        # Middle section: knuckle barrel must be present and solid at y=y_pivot, z=half_h
        barrel_probe = block(
            [spec.width, 2 * hr, 2 * hr], at=(0.0, y_pivot - hr, half_h - hr)
        )
        v_barrel = volume(body & barrel_probe)
        self.assertGreater(v_barrel, 1000.0)

        # Front wall: clean snap catch tab on lid front wall
        lid_front_y = spec.length + gap + spec.length
        tab_probe = block([spec.width, 2.0, 4.0], at=(0.0, lid_front_y - 2.0, half_h))
        v_tab = volume(body & tab_probe)
        self.assertGreater(v_tab, 20.0)

        # Monolithic bounds: length must be 2 * spec.length + gap (81.0mm), no 14mm chasm
        _centre, size = (
            body.bounds()
            if isinstance(body.bounds(), tuple)
            else (body.bounds().center, body.bounds().size)
        )
        self.assertAlmostEqual(size[1], 2 * spec.length + gap, delta=0.2)

        # Conforming edge: wall under knuckle barrel hugs the round profile without rectangular voids
        wall_probe = block(
            [10.0, spec.wall_thickness, 1.0],
            at=(15.0, spec.length - spec.wall_thickness, half_h - hr - 1.0),
        )
        v_wall = volume(body & wall_probe)
        self.assertGreater(v_wall, 15.0)

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
        floor_probe = block(
            [20.0, 10.0, base_spec.floor_thickness], at=((55.0 - 20.0) / 2.0, 0.0, 0.0)
        )
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
        tray_probe = block(
            [50.0, 15.0, base_spec.floor_thickness], at=(2.5, -18.0, 0.0)
        )
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
        rear_probe = block(
            [18.0, base_spec.wall_thickness, 8.0],
            at=(
                (55.0 - 18.0) / 2.0,
                55.0 - base_spec.wall_thickness,
                base_spec.floor_thickness,
            ),
        )
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
        arch_probe = block(
            [20.0, base_spec.wall_thickness, 15.0], at=((55.0 - 20.0) / 2.0, 0.0, 20.0)
        )
        self.assertAlmostEqual(volume(arch_body & arch_probe), 0.0, delta=1.0)

    def test_dispenser_floor_notch_cuts_cleanly_through_ramp(self) -> None:
        """Verify the floor notch cuts completely through the bottom and slide ramp (no thin layer on top)."""
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
            floor_thickness=2.0,
        )
        body = impl.build_body(spec)
        self.assertIsNotNone(body)

        # Probe in the notch above the 2.0mm floor (z = 2.5..4.5mm) where the slide ramp slopes upward
        probe = block(
            [12.0, 6.0, 2.0],
            at=((spec.width - 12.0) / 2.0, spec.wall_thickness + 2.0, 2.5),
        )
        self.assertAlmostEqual(volume(body & probe), 0.0, delta=0.01)

    def test_dispenser_stackable(self) -> None:
        """Verify dispenser rejects stackable because its lid has a downward plug flange."""
        from pyboxbuilder.enums import StackableMode

        impl = BOX_IMPL_REGISTRY[BoxType.DISPENSER]()
        spec = BoxSpec(
            label="StackChute",
            width=55.0,
            length=55.0,
            height=70.0,
            stackable=StackableMode.FEET,
        )
        with self.assertRaises(ValueError):
            impl.build_body(spec)
        with self.assertRaises(ValueError):
            impl.build_lid(spec)

    def test_dispenser_default_flat_and_configurable_angle(self) -> None:
        """Verify dispenser defaults to a flat floor with finger cutouts and supports configurable tile_angle."""
        from pyboxbuilder.box.shell import block
        from tests.mesh import volume

        impl = BOX_IMPL_REGISTRY[BoxType.DISPENSER]()
        flat_spec = BoxSpec(label="FlatDisp", width=55.0, length=55.0, height=70.0)
        self.assertEqual(flat_spec.chute_angle, 0.0)
        flat_body = impl.build_body(flat_spec)

        # Back interior above floor (y = 35..50, z = ft + 1.0..ft + 10.0) should be completely open on a flat floor
        back_cavity_probe = block(
            [20.0, 15.0, 9.0],
            at=((55.0 - 20.0) / 2.0, 35.0, flat_spec.floor_thickness + 1.0),
        )
        self.assertAlmostEqual(volume(flat_body & back_cavity_probe), 0.0, delta=0.05)

        # Front finger-pinch floor cutout should still be open for pulling out the bottom tile
        front_notch_probe = block(
            [16.0, 8.0, flat_spec.floor_thickness],
            at=((55.0 - 16.0) / 2.0, 0.0, 0.0),
        )
        self.assertAlmostEqual(volume(flat_body & front_notch_probe), 0.0, delta=0.05)

        # Configuring tile_angle=35.0 adds the angled ramp in the back interior
        angled_spec = BoxSpec(
            label="AngledDisp",
            width=55.0,
            length=55.0,
            height=70.0,
            tile_angle=35.0,
        )
        angled_body = impl.build_body(angled_spec)
        self.assertGreater(volume(angled_body & back_cavity_probe), 500.0)

    def test_dice_tray_slipover_lid_features(self) -> None:
        """Verify DiceTrayBox inherits SlipoverBox body/lid sleeve features (foot, gap, corner finger notches, catches)."""
        from dataclasses import replace

        from pyboxbuilder.box.features import slipover_gap, slipover_metrics
        from pyboxbuilder.box.shell import block
        from pyboxbuilder.box.types.slipover import SlipoverBox
        from tests.mesh import volume

        impl = BOX_IMPL_REGISTRY[BoxType.DICE_TRAY]()
        self.assertIsInstance(impl, SlipoverBox)

        spec = BoxSpec(label="Arena", width=100.0, length=80.0, height=35.0)
        body = impl.build_body(spec)
        lid = impl.build_lid(spec)
        self.assertLess(volume(body & lid), 0.05)

        # Body extends full slipover height (height - lt - size_spacing = 32.8mm)
        _inset, body_h = slipover_metrics(spec)
        b_body = body.bounds()
        c_b, s_b = (b_body.center, b_body.size) if hasattr(b_body, "center") else b_body
        self.assertAlmostEqual(c_b[2] + s_b[2] / 2.0, body_h, delta=0.1)

        # Lid sleeve starts at foot + gap and has diagonal corner finger cutouts at (0, 0) and (width, length)
        base_z = spec.foot + min(
            slipover_gap(spec), spec.height - spec.foot - spec.lid_thickness
        )
        b_lid = lid.bounds()
        c_l, s_l = (b_lid.center, b_lid.size) if hasattr(b_lid, "center") else b_lid
        self.assertAlmostEqual(c_l[2] - s_l[2] / 2.0, base_z, delta=0.1)

        lid_no_notches = impl.build_lid(replace(spec, slipover_finger_height=0.0))
        self.assertGreater(volume(lid_no_notches), volume(lid) + 5.0)

    def test_clamshell_filament_hinge_and_pin_bore(self) -> None:
        """Verify ClamshellBox uses a bored filament pin hinge at z=height/2 and front snap catch."""
        from pybosl2 import cylinder

        from pyboxbuilder.precision import kwargs as precision_kwargs
        from tests.mesh import volume

        p = Project("TestClamshellFilament")
        b = p.box(
            BoxType.CLAMSHELL,
            "SpellBook",
            size=(80.0, 60.0, 30.0),
            filament_diameter=1.75,
            hinge_count=5,
        )
        self.assertAlmostEqual(b.filament_diameter, 1.75)
        self.assertEqual(b.hinge_count, 5)

        impl = BOX_IMPL_REGISTRY[BoxType.CLAMSHELL]()
        spec = BoxSpec(label="SpellBook", width=80.0, length=60.0, height=30.0)
        body = impl.build_body(spec)
        lid = impl.build_lid(spec)
        self.assertLess(volume(body & lid), 0.05)

        # Verify the filament pin bore at (y = length - radius, z = height / 2) is completely clear through both body and lid
        radius_h = max(spec.wall_thickness, spec.filament_diameter)
        axis_y = spec.length - radius_h
        axis_z = spec.height / 2.0
        pin_probe = (
            cylinder(
                height=spec.width,
                radius=spec.filament_diameter / 2.0,
                **precision_kwargs(),
            )
            .rotate([0, 90, 0])
            .translate([spec.width / 2.0, axis_y, axis_z])
        )
        self.assertAlmostEqual(volume(body & pin_probe), 0.0, delta=0.02)
        self.assertAlmostEqual(volume(lid & pin_probe), 0.0, delta=0.02)

        # Verify odd lid knuckles (index=1, 3) connect vertically upward (+Z) into the upper tray back wall
        from pyboxbuilder.box.shell import block

        pitch = spec.width / spec.hinge_count
        for odd_idx in (1, 3):
            cx = (odd_idx + 0.5) * pitch
            upper_wall_probe = block(
                [pitch * 0.5, radius_h * 0.8, radius_h * 0.8],
                at=(cx - pitch * 0.25, axis_y + radius_h * 0.1, axis_z + 0.15),
            )
            self.assertGreater(volume(lid & upper_wall_probe), 5.0)

    def test_snap_fit_cantilever_proportions_and_backing_wall(self) -> None:
        """Verify cantilever latch has compact, sturdy proportions and an unbroken internal backing wall."""
        from pyboxbuilder.box.shell import block
        from tests.mesh import volume

        p = Project("SnapFitStrength")
        box = p.box(BoxType.SNAP_FIT, "SturdySnap", size=(60.0, 50.0, 26.0))
        box.compartment("Tokens", holds_pieces=True)

        self.assertAlmostEqual(box.cantilever_thickness, 2.0)
        self.assertAlmostEqual(box.cantilever_width, 14.0)
        self.assertAlmostEqual(box.detent_height, 0.8)
        self.assertAlmostEqual(box.deflection_clearance, 0.25)

        impl = BOX_IMPL_REGISTRY[BoxType.SNAP_FIT]()
        spec = BoxSpec(label="SturdySnap", width=60.0, length=50.0, height=26.0)
        body = impl.build_body(spec)
        lid = impl.build_lid(spec)
        self.assertLess(volume(body & lid), 0.05)

        # Lid cantilever arm drop should be compact (~6.5mm below lid underside at z=24, so z_min >= 17.0)
        b = lid.bounds()
        centre, size = (b.center, b.size) if hasattr(b, "center") else b
        z_min = centre[2] - size[2] / 2.0
        z_max = centre[2] + size[2] / 2.0
        self.assertAlmostEqual(z_max, 26.0, delta=0.1)
        arm_drop = (26.0 - spec.lid_thickness) - z_min
        self.assertGreaterEqual(arm_drop, 4.8)
        self.assertLessEqual(arm_drop, 6.6)

        # Verify the built body (including compartment cut) has solid internal backing wall behind the pocket
        pieces = p.preview_pieces(show_lids=True)
        body_piece = [pc for pc in pieces if pc.label == "SturdySnap"][0]
        m = impl._latch_metrics(spec)
        pocket_depth = float(m["c_t"]) + float(m["eff_d_h"]) + float(m["clr"])
        boss_t = float(m["boss_t"])
        backing_thickness = boss_t - pocket_depth
        self.assertGreaterEqual(backing_thickness, 1.2)

        backing_probe = block(
            [backing_thickness * 0.8, 10.0, 3.0],
            at=(pocket_depth + 0.1, (50.0 - 10.0) / 2.0, float(m["pocket_z"])),
        )
        expected_vol = (backing_thickness * 0.8) * 10.0 * 3.0
        self.assertAlmostEqual(
            volume(body_piece.solid & backing_probe), expected_vol, delta=0.5
        )

    def test_inset_hinge_geometry_and_features(self) -> None:
        """Verify InsetHingeBox side-by-side layout, recessed conical hinge, rim, and latch tab."""
        from pyboxbuilder.box.shell import block
        from tests.mesh import volume

        impl = BOX_IMPL_REGISTRY[BoxType.INSET_HINGE]()
        spec = BoxSpec(label="InsetHingeTest", width=60.0, length=50.0, height=28.0)
        body = impl.build_body(spec)
        lid = impl.build_lid(spec)
        self.assertIsNotNone(body)
        self.assertIsNone(lid)

        # Unfolded X span is 2 * width + gap (2 * pip_radial_clearance), Y span is length (50.0mm)
        expected_gap = 2.0 * spec.pip_radial_clearance
        b = body.bounds()
        centre, size = (b.center, b.size) if hasattr(b, "center") else b
        self.assertAlmostEqual(size[0], 2 * spec.width + expected_gap, delta=0.2)
        self.assertAlmostEqual(size[1], spec.length, delta=0.2)
        half_h = spec.height / 2.0
        z_min = centre[2] - size[2] / 2.0
        z_max = centre[2] + size[2] / 2.0
        self.assertAlmostEqual(z_min, 0.0, delta=0.2)
        # Front latch tab rises above half_h - lt by tab_height (6.0mm -> z_max = 18.0mm)
        self.assertAlmostEqual(
            z_max, half_h - spec.lid_thickness + spec.inset_hinge_tab_height, delta=0.2
        )

        # Recessed InsetHinge sits across the gap at x = width + gap/2
        hinge_probe = block(
            [12.0, spec.length - 6.0, 6.0],
            at=(spec.width + expected_gap / 2.0 - 6.0, 3.0, half_h - 6.0),
        )
        self.assertGreater(volume(body & hinge_probe), 1500.0)

        # No center sliver bar down the middle gap in even hinge segments (i = 2)
        hinge_diameter = 2.0 * spec.pip_hinge_radius
        hinge_length = spec.length - 2.0 * spec.inset_hinge_side_gap
        num_segs = max(2, round(hinge_length / hinge_diameter))
        seg_spacing = hinge_length / num_segs
        even_seg_y = spec.inset_hinge_side_gap + 2.5 * seg_spacing
        even_gap_probe = block(
            [expected_gap * 0.5, seg_spacing * 0.3, hinge_diameter],
            at=(
                spec.width + expected_gap * 0.25,
                even_seg_y - seg_spacing * 0.15,
                half_h - hinge_diameter - spec.pip_radial_clearance,
            ),
        )
        self.assertAlmostEqual(volume(body & even_gap_probe), 0.0, delta=1e-3)

        # Odd hinge segments (i = 1) bridge cleanly across the middle gap
        odd_seg_y = spec.inset_hinge_side_gap + 1.5 * seg_spacing
        odd_gap_probe = block(
            [expected_gap * 0.5, seg_spacing * 0.3, hinge_diameter * 0.5],
            at=(
                spec.width + expected_gap * 0.25,
                odd_seg_y - seg_spacing * 0.15,
                half_h - hinge_diameter * 0.75 - spec.pip_radial_clearance,
            ),
        )
        self.assertGreater(volume(body & odd_gap_probe), 0.1)

        # Front latch tab on base outer wall (x = 0 .. wt/2) rises above z = half_h - lt
        tab_probe = block(
            [spec.wall_thickness, 12.0, 6.0],
            at=(0.0, spec.length / 2.0 - 6.0, half_h - spec.lid_thickness - 4.0),
        )
        self.assertGreater(volume(body & tab_probe), 20.0)

        # Interior reserves hinge_width along X on the base half
        interior = impl.interior(spec)
        hinge_width = 2.0 * (2.0 * spec.pip_hinge_radius) + expected_gap
        self.assertAlmostEqual(
            interior.width, spec.width - spec.wall_thickness - hinge_width
        )
        self.assertAlmostEqual(interior.length, spec.length - 2.0 * spec.wall_thickness)
        self.assertAlmostEqual(interior.height, half_h - spec.floor_thickness)

    def test_sliding_hinge_box_geometry_and_catches(self) -> None:
        """Verify SlidingHingeBox defaults to SLIDE_ACROSS and supports slide_up, spin, and card_library catches."""
        from dataclasses import replace

        from pyboxbuilder.box.shell import block
        from tests.mesh import volume

        impl = BOX_IMPL_REGISTRY[BoxType.SLIDING_HINGE]()
        base_spec = BoxSpec(
            label="SlidingHingeTest", width=70.0, length=55.0, height=28.0
        )

        # 1. Default SLIDE_ACROSS ("front" style)
        body_front = impl.build_body(base_spec)
        lid_front = impl.build_lid(base_spec)
        self.assertIsNotNone(body_front)
        self.assertIsNotNone(lid_front)
        self.assertLess(volume(body_front & lid_front), 0.05)

        # Front catch assembly adds L-hook stalk material inside y=0..6 on lid below z=body_h
        front_lid_probe = block([30.0, 6.0, 4.0], at=(20.0, 0.5, 22.0))
        self.assertGreater(volume(lid_front & front_lid_probe), 5.0)

        # 2. SLIDE_ACROSS with "card_library" dual-side style
        spec_cl = replace(base_spec, slide_catch_style="card_library")
        body_cl = impl.build_body(spec_cl)
        lid_cl = impl.build_lid(spec_cl)
        self.assertIsNotNone(body_cl)
        self.assertIsNotNone(lid_cl)
        self.assertLess(volume(body_cl & lid_cl), 0.05)

        # 3. SLIDE_UP catch on body front wall
        spec_up = replace(base_spec, catch_type=CatchType.SLIDE_UP)
        body_up = impl.build_body(spec_up)
        lid_up = impl.build_lid(spec_up)
        self.assertIsNotNone(body_up)
        self.assertIsNotNone(lid_up)
        self.assertLess(volume(body_up & lid_up), 0.05)
        front_body_probe = block([24.0, 4.0, 14.0], at=(23.0, 0.0, 14.0))
        self.assertGreater(volume(body_up & front_body_probe), 30.0)

        # 4. SPIN catch (print-in-place rotary cam)
        spec_spin = replace(base_spec, catch_type=CatchType.SPIN)
        body_spin = impl.build_body(spec_spin)
        lid_spin = impl.build_lid(spec_spin)
        self.assertIsNotNone(body_spin)
        self.assertIsNotNone(lid_spin)
        self.assertLess(volume(body_spin & lid_spin), 0.05)
        self.assertGreater(volume(body_spin & front_body_probe), 25.0)
