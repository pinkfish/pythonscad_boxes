# SPDX-License-Identifier: Apache-2.0
"""Comprehensive automated tests for all basic box pieces and catch types (FR-099, FR-100, SC-099, SC-100)."""

from __future__ import annotations

import unittest
from dataclasses import replace

from mesh import volume

from pyboxbuilder import (
    BoxSpec,
    BoxType,
    CatchType,
    CapBoxBuilder,
    CapPathBoxBuilder,
    CardLibraryBoxBuilder,
    ClamshellBoxBuilder,
    FilamentHingeBoxBuilder,
    HingeBoxBuilder,
    PrintInPlaceHingeBoxBuilder,
    SlidingBoxBuilder,
    SlidingCatchBoxBuilder,
    SlipoverBoxBuilder,
    SlipoverPathBoxBuilder,
    SnapFitBoxBuilder,
)
from pyboxbuilder.box.features import (
    build_bump_detent,
    build_wedge_detent,
    build_loop_detent,
    build_magnet_detent,
    build_leaf_spring_detent,
    sliding_catch,
    cap_slipover_catch,
    hinge_catch,
)
from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
from pyboxbuilder.box.spec import build_spec
from pyboxbuilder.box.validation import GeometryValidationError, GeometryValidator

SPEC = BoxSpec(
    width=80.0,
    length=60.0,
    height=30.0,
    wall_thickness=2.0,
    floor_thickness=2.0,
    lid_thickness=2.0,
)

POLY_L = (
    (0.0, 0.0),
    (60.0, 0.0),
    (60.0, 30.0),
    (30.0, 30.0),
    (30.0, 60.0),
    (0.0, 60.0),
)


class DetentGeometryTests(unittest.TestCase):
    """Geometric primitive detent tests (FR-099, FR-100)."""

    def test_build_bump_detent(self) -> None:
        bump, dimple = build_bump_detent(radius=1.2, clearance=0.1)
        self.assertIsNotNone(bump)
        self.assertIsNotNone(dimple)

    def test_build_wedge_detent(self) -> None:
        wedge, groove = build_wedge_detent(depth=0.8, width=5.0, height=2.0, clearance=0.15)
        self.assertIsNotNone(wedge)
        self.assertIsNotNone(groove)

    def test_build_loop_detent(self) -> None:
        tab, cutter = build_loop_detent(depth=1.0, width=8.0, height=6.0, tab_thickness=0.8, clearance=0.15)
        self.assertIsNotNone(tab)
        self.assertIsNotNone(cutter)

    def test_build_magnet_detent(self) -> None:
        p_lid, p_body = build_magnet_detent(diameter=4.0, depth=2.0, clearance=0.1)
        self.assertIsNotNone(p_lid)
        self.assertIsNotNone(p_body)

    def test_build_leaf_spring_detent(self) -> None:
        bead, slot, dimple = build_leaf_spring_detent(radius=1.0, arm_length=8.0, arm_thickness=1.0, slot_width=0.8)
        self.assertIsNotNone(bead)
        self.assertIsNotNone(slot)
        self.assertIsNotNone(dimple)


class SpecCatchResolutionTests(unittest.TestCase):
    """Tests for BoxSpec and Builder catch resolution (FR-099, FR-100)."""

    def test_default_resolution(self) -> None:
        s = BoxSpec(width=50, length=50, height=20)
        self.assertEqual(s.resolved_catch_type(CatchType.BUMP), CatchType.BUMP)
        self.assertEqual(s.resolved_catch_type(CatchType.NONE), CatchType.NONE)

    def test_explicit_enum_and_string(self) -> None:
        s1 = BoxSpec(width=50, length=50, height=20, catch_type=CatchType.WEDGE)
        self.assertEqual(s1.resolved_catch_type(), CatchType.WEDGE)

        s2 = BoxSpec(width=50, length=50, height=20, catch_type="loop")
        self.assertEqual(s2.resolved_catch_type(), CatchType.LOOP)

        s3 = BoxSpec(width=50, length=50, height=20, catch_type="magnet")
        self.assertEqual(s3.resolved_catch_type(), CatchType.MAGNET)

        s4 = BoxSpec(width=50, length=50, height=20, catch_type="leaf_spring")
        self.assertEqual(s4.resolved_catch_type(), CatchType.LEAF_SPRING)

        s5 = BoxSpec(width=50, length=50, height=20, catch_type="none")
        self.assertEqual(s5.resolved_catch_type(), CatchType.NONE)

    def test_legacy_fallbacks(self) -> None:
        s_zero = BoxSpec(width=50, length=50, height=20, catch_radius=0.0)
        self.assertEqual(s_zero.resolved_catch_type(CatchType.BUMP), CatchType.NONE)

        s_bump = BoxSpec(width=50, length=50, height=20, hinge_catch_type="bump")
        self.assertEqual(s_bump.resolved_catch_type(), CatchType.BUMP)

        s_ridge = BoxSpec(width=50, length=50, height=20, hinge_catch_type="ridge")
        self.assertEqual(s_ridge.resolved_catch_type(), CatchType.WEDGE)

        s_pip_no = BoxSpec(width=50, length=50, height=20, pip_snap_catch=False)
        self.assertEqual(s_pip_no.resolved_catch_type(), CatchType.NONE)

    def test_catch_size_resolution(self) -> None:
        s1 = BoxSpec(width=50, length=50, height=20, catch_size=1.5)
        self.assertAlmostEqual(s1.resolved_catch_size(), 1.5)

        s2 = BoxSpec(width=50, length=50, height=20, catch_radius=1.1)
        self.assertAlmostEqual(s2.resolved_catch_size(), 1.1)


class SlidingCatchTests(unittest.TestCase):
    """Tests for sliding catches across all CatchTypes and axes (FR-099, FR-100)."""

    def test_sliding_catch_types_along_y(self) -> None:
        for ct in (CatchType.BUMP, CatchType.WEDGE, CatchType.LOOP, CatchType.MAGNET, CatchType.LEAF_SPRING):
            with self.subTest(catch_type=ct.value):
                spec = replace(SPEC, catch_type=ct, lid_slide_axis="y")
                closure = sliding_catch(spec, along_axis="y")
                self.assertIsNotNone(closure.body)
                if ct == CatchType.MAGNET:
                    self.assertIsNotNone(closure.lid_cut)
                else:
                    self.assertIsNotNone(closure.lid)

    def test_sliding_catch_types_along_x(self) -> None:
        for ct in (CatchType.BUMP, CatchType.WEDGE, CatchType.LOOP, CatchType.MAGNET, CatchType.LEAF_SPRING):
            with self.subTest(catch_type=ct.value):
                spec = replace(SPEC, catch_type=ct, lid_slide_axis="x")
                closure = sliding_catch(spec, along_axis="x")
                self.assertIsNotNone(closure.body)
                if ct == CatchType.MAGNET:
                    self.assertIsNotNone(closure.lid_cut)
                else:
                    self.assertIsNotNone(closure.lid)

    def test_sliding_catch_none(self) -> None:
        spec = replace(SPEC, catch_type=CatchType.NONE)
        closure = sliding_catch(spec)
        self.assertIsNone(closure.body)
        self.assertIsNone(closure.lid)


class CapSlipoverCatchTests(unittest.TestCase):
    """Tests for cap and slipover catches across all CatchTypes (FR-099, FR-100)."""

    def test_cap_catch_types(self) -> None:
        for ct in (CatchType.BUMP, CatchType.WEDGE, CatchType.LOOP, CatchType.MAGNET, CatchType.LEAF_SPRING):
            with self.subTest(catch_type=ct.value):
                spec = replace(SPEC, catch_type=ct)
                closure = cap_slipover_catch(spec, is_slipover=False)
                self.assertIsNotNone(closure.body)
                if ct == CatchType.MAGNET:
                    self.assertIsNotNone(closure.lid_cut)
                else:
                    self.assertIsNotNone(closure.lid)

    def test_slipover_catch_types(self) -> None:
        for ct in (CatchType.BUMP, CatchType.WEDGE, CatchType.LOOP, CatchType.MAGNET, CatchType.LEAF_SPRING):
            with self.subTest(catch_type=ct.value):
                spec = replace(SPEC, catch_type=ct)
                closure = cap_slipover_catch(spec, is_slipover=True)
                self.assertIsNotNone(closure.body)
                if ct == CatchType.MAGNET:
                    self.assertIsNotNone(closure.lid_cut)
                else:
                    self.assertIsNotNone(closure.lid)

    def test_cap_slipover_catch_none(self) -> None:
        spec = replace(SPEC, catch_type=CatchType.NONE)
        closure_cap = cap_slipover_catch(spec, is_slipover=False)
        self.assertIsNone(closure_cap.body)
        self.assertIsNone(closure_cap.lid)

        closure_slip = cap_slipover_catch(spec, is_slipover=True)
        self.assertIsNone(closure_slip.body)
        self.assertIsNone(closure_slip.lid)


class HingeCatchTests(unittest.TestCase):
    """Tests for hinged front catches across all CatchTypes (FR-099, FR-100)."""

    def test_hinge_catch_types(self) -> None:
        for ct in (CatchType.WEDGE, CatchType.BUMP, CatchType.LOOP, CatchType.MAGNET, CatchType.LEAF_SPRING):
            with self.subTest(catch_type=ct.value):
                spec = replace(SPEC, catch_type=ct)
                closure = hinge_catch(spec)
                self.assertIsNotNone(closure.body_cut)
                self.assertIsNotNone(closure.lid)

    def test_hinge_catch_none(self) -> None:
        spec = replace(SPEC, catch_type=CatchType.NONE)
        closure = hinge_catch(spec)
        self.assertIsNone(closure.body_cut)
        self.assertIsNone(closure.lid)


ALL_CATCHES = (
    CatchType.BUMP,
    CatchType.WEDGE,
    CatchType.LOOP,
    CatchType.MAGNET,
    CatchType.LEAF_SPRING,
    CatchType.NONE,
)


class AllBoxTypesCatchMatingMatrixTests(unittest.TestCase):
    """Exhaustive basic piece test: every box type and catch type combination must mate cleanly with 0 collision volume (FR-100, SC-100)."""

    def test_sliding_family_catches(self) -> None:
        for bt in (BoxType.SLIDING, BoxType.SLIDING_CATCH, BoxType.CARD_LIBRARY):
            impl = BOX_IMPL_REGISTRY[bt]()
            for ct in ALL_CATCHES:
                for axis in ("x", "y"):
                    with self.subTest(box_type=bt.value, catch_type=ct.value, axis=axis):
                        spec = replace(SPEC, catch_type=ct, lid_slide_axis=axis)
                        body = impl.build_body(spec)
                        lid = impl.build_lid(spec)
                        self.assertIsNotNone(body)
                        self.assertIsNotNone(lid)
                        self.assertLess(
                            volume(body & lid),
                            0.05,
                            f"{bt.value} ({ct.value}, axis={axis}) closed lid intersects body",
                        )

    def test_cap_and_slipover_catches(self) -> None:
        for bt in (BoxType.CAP, BoxType.SLIPOVER):
            impl = BOX_IMPL_REGISTRY[bt]()
            for ct in ALL_CATCHES:
                with self.subTest(box_type=bt.value, catch_type=ct.value):
                    spec = replace(SPEC, catch_type=ct)
                    body = impl.build_body(spec)
                    lid = impl.build_lid(spec)
                    self.assertIsNotNone(body)
                    self.assertIsNotNone(lid)
                    self.assertLess(
                        volume(body & lid),
                        0.05,
                        f"{bt.value} ({ct.value}) closed lid intersects body",
                    )

    def test_polygon_path_cap_and_slipover_catches(self) -> None:
        for bt in (BoxType.CAP_PATH, BoxType.SLIPOVER_PATH):
            impl = BOX_IMPL_REGISTRY[bt]()
            for ct in ALL_CATCHES:
                with self.subTest(box_type=bt.value, catch_type=ct.value):
                    spec = replace(SPEC, path=POLY_L, catch_type=ct)
                    body = impl.build_body(spec)
                    lid = impl.build_lid(spec)
                    self.assertIsNotNone(body)
                    self.assertIsNotNone(lid)
                    self.assertLess(
                        volume(body & lid),
                        0.05,
                        f"{bt.value} ({ct.value}) closed lid intersects body",
                    )

    def test_hinged_and_clamshell_catches(self) -> None:
        for bt in (BoxType.HINGE, BoxType.FILAMENT_HINGE, BoxType.CLAMSHELL):
            impl = BOX_IMPL_REGISTRY[bt]()
            for ct in ALL_CATCHES:
                with self.subTest(box_type=bt.value, catch_type=ct.value):
                    spec = replace(SPEC, catch_type=ct)
                    body = impl.build_body(spec)
                    lid = impl.build_lid(spec)
                    self.assertIsNotNone(body)
                    self.assertIsNotNone(lid)
                    self.assertLess(
                        volume(body & lid),
                        0.05,
                        f"{bt.value} ({ct.value}) closed lid intersects body",
                    )

    def test_pip_hinge_catches(self) -> None:
        impl = BOX_IMPL_REGISTRY[BoxType.PRINT_IN_PLACE_HINGE]()
        for ct in (CatchType.WEDGE, CatchType.MAGNET, CatchType.LEAF_SPRING, CatchType.NONE):
            with self.subTest(catch_type=ct.value):
                spec = replace(SPEC, catch_type=ct)
                body = impl.build_body(spec)
                self.assertIsNotNone(body)

    def test_snap_fit_axes_and_catches(self) -> None:
        impl = BOX_IMPL_REGISTRY[BoxType.SNAP_FIT]()
        for ct in ALL_CATCHES:
            for axis in ("x", "y"):
                with self.subTest(catch_type=ct.value, latch_axis=axis):
                    spec = replace(SPEC, catch_type=ct, latch_axis=axis)
                    body = impl.build_body(spec)
                    lid = impl.build_lid(spec)
                    self.assertIsNotNone(body)
                    self.assertIsNotNone(lid)
                    self.assertLess(
                        volume(body & lid),
                        0.05,
                        f"SnapFitBox ({ct.value}, axis={axis}) closed lid intersects body",
                    )


class BuilderCatchMatrixTests(unittest.TestCase):
    """Tests verifying every builder exposes catch_type and catch_size correctly (FR-100, SC-100)."""

    def test_all_relevant_builders_accept_catches(self) -> None:
        builders = [
            SlidingBoxBuilder(label="b1", catch_type=CatchType.WEDGE, catch_size=0.8),
            SlidingCatchBoxBuilder(label="b2", catch_type=CatchType.LOOP, catch_size=1.0),
            CardLibraryBoxBuilder(label="b3", catch_type=CatchType.BUMP, catch_size=0.6),
            CapBoxBuilder(label="b4", catch_type=CatchType.MAGNET, catch_size=3.0),
            CapPathBoxBuilder(label="b5", path=POLY_L, catch_type=CatchType.LEAF_SPRING, catch_size=0.7),
            SlipoverBoxBuilder(label="b6", catch_type=CatchType.BUMP, catch_size=0.9),
            SlipoverPathBoxBuilder(label="b7", path=POLY_L, catch_type=CatchType.LOOP, catch_size=1.0),
            HingeBoxBuilder(label="b8", catch_type=CatchType.MAGNET, catch_size=3.0),
            FilamentHingeBoxBuilder(label="b9", catch_type=CatchType.LEAF_SPRING, catch_size=0.8),
            PrintInPlaceHingeBoxBuilder(label="b10", catch_type=CatchType.NONE),
            ClamshellBoxBuilder(label="b11", catch_type=CatchType.BUMP, catch_size=0.9),
            SnapFitBoxBuilder(label="b12", catch_type=CatchType.LOOP, catch_size=1.0),
        ]
        for b in builders:
            with self.subTest(builder=type(b).__name__):
                spec = build_spec(None, b, (80.0, 60.0, 30.0))
                self.assertEqual(spec.catch_type, b.catch_type)
                if b.catch_size is not None:
                    self.assertEqual(spec.catch_size, b.catch_size)

    def test_builder_type_enforcement(self) -> None:
        with self.assertRaises(TypeError):
            SlidingBoxBuilder(label="bad", catch_type="not_an_enum")
        with self.assertRaises(TypeError):
            CapBoxBuilder(label="bad", catch_type=123)


class PreCsgValidationTests(unittest.TestCase):
    """Tests for pre-CSG catch boundary validation (FR-099, FR-100)."""

    def test_catch_radius_exceeds_wall(self) -> None:
        spec = BoxSpec(
            width=80.0,
            length=60.0,
            height=30.0,
            wall_thickness=2.0,
            catch_radius=2.5,
        )
        with self.assertRaises(GeometryValidationError) as ctx:
            GeometryValidator.validate(spec)
        self.assertIn("catch_radius_fits_wall", str(ctx.exception))

    def test_catch_size_exceeds_wall(self) -> None:
        spec = BoxSpec(
            width=80.0,
            length=60.0,
            height=30.0,
            wall_thickness=2.0,
            catch_size=2.2,
        )
        with self.assertRaises(GeometryValidationError) as ctx:
            GeometryValidator.validate(spec)
        self.assertIn("catch_size_fits_wall", str(ctx.exception))

    def test_magnet_catch_size_exceeds_footprint(self) -> None:
        spec = BoxSpec(
            width=20.0,
            length=20.0,
            height=20.0,
            wall_thickness=2.0,
            catch_type=CatchType.MAGNET,
            catch_size=15.0,
        )
        with self.assertRaises(GeometryValidationError) as ctx:
            GeometryValidator.validate(spec)
        self.assertIn("catch_size_fits_wall", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()

