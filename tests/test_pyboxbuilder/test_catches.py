# SPDX-License-Identifier: Apache-2.0
"""Tests for configurable catch types (CatchType.BUMP, WEDGE, LOOP, NONE) (FR-099)."""

from __future__ import annotations

import unittest

from pyboxbuilder import (
    BoxSpec,
    BoxType,
    CatchType,
    SlidingBoxBuilder,
    CapBoxBuilder,
    SlipoverBoxBuilder,
    HingeBoxBuilder,
    SnapFitBoxBuilder,
)
from pyboxbuilder.box.features import (
    build_bump_detent,
    build_wedge_detent,
    build_loop_detent,
    sliding_catch,
    cap_slipover_catch,
    hinge_catch,
)
from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
from pyboxbuilder.box.validation import GeometryValidationError, GeometryValidator

SPEC = BoxSpec(
    width=80.0,
    length=60.0,
    height=30.0,
    wall_thickness=2.0,
    floor_thickness=2.0,
    lid_thickness=2.0,
)


class DetentGeometryTests(unittest.TestCase):
    """Geometric primitive detent tests (FR-099)."""

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


class SpecCatchResolutionTests(unittest.TestCase):
    """Tests for BoxSpec and Builder catch resolution (FR-099)."""

    def test_default_resolution(self) -> None:
        s = BoxSpec(width=50, length=50, height=20)
        self.assertEqual(s.resolved_catch_type(CatchType.BUMP), CatchType.BUMP)
        self.assertEqual(s.resolved_catch_type(CatchType.NONE), CatchType.NONE)

    def test_explicit_enum_and_string(self) -> None:
        s1 = BoxSpec(width=50, length=50, height=20, catch_type=CatchType.WEDGE)
        self.assertEqual(s1.resolved_catch_type(), CatchType.WEDGE)

        s2 = BoxSpec(width=50, length=50, height=20, catch_type="loop")
        self.assertEqual(s2.resolved_catch_type(), CatchType.LOOP)

        s3 = BoxSpec(width=50, length=50, height=20, catch_type="none")
        self.assertEqual(s3.resolved_catch_type(), CatchType.NONE)

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

    def test_builder_catch_fields(self) -> None:
        from pyboxbuilder.box.spec import build_spec

        b = SlidingBoxBuilder(label="Tokens", catch_type=CatchType.WEDGE, catch_size=0.9)
        self.assertEqual(b.catch_type, CatchType.WEDGE)
        self.assertEqual(b.catch_size, 0.9)
        s = build_spec(None, b, (60.0, 40.0, 20.0))
        self.assertEqual(s.catch_type, CatchType.WEDGE)
        self.assertEqual(s.catch_size, 0.9)

    def test_builder_catch_validation(self) -> None:
        with self.assertRaises(TypeError):
            SlidingBoxBuilder(label="Tokens", catch_type="not_an_enum")


class SlidingCatchTests(unittest.TestCase):
    """Tests for sliding catches across all CatchTypes (FR-099)."""

    def test_sliding_catch_types(self) -> None:
        for ct in (CatchType.BUMP, CatchType.WEDGE, CatchType.LOOP):
            with self.subTest(catch_type=ct.value):
                spec = BoxSpec(
                    width=80.0,
                    length=60.0,
                    height=30.0,
                    wall_thickness=2.0,
                    lid_thickness=2.0,
                    catch_type=ct,
                )
                closure = sliding_catch(spec)
                self.assertIsNotNone(closure.body)
                self.assertIsNotNone(closure.lid)

    def test_sliding_catch_none(self) -> None:
        spec = BoxSpec(
            width=80.0,
            length=60.0,
            height=30.0,
            wall_thickness=2.0,
            lid_thickness=2.0,
            catch_type=CatchType.NONE,
        )
        closure = sliding_catch(spec)
        self.assertIsNone(closure.body)
        self.assertIsNone(closure.lid)


class CapSlipoverCatchTests(unittest.TestCase):
    """Tests for cap and slipover catches across all CatchTypes (FR-099)."""

    def test_cap_catch_types(self) -> None:
        for ct in (CatchType.BUMP, CatchType.WEDGE, CatchType.LOOP):
            with self.subTest(catch_type=ct.value):
                spec = BoxSpec(
                    width=80.0,
                    length=60.0,
                    height=30.0,
                    wall_thickness=2.0,
                    lid_thickness=2.0,
                    catch_type=ct,
                )
                closure = cap_slipover_catch(spec, is_slipover=False)
                self.assertIsNotNone(closure.body)
                self.assertIsNotNone(closure.lid)

    def test_slipover_catch_types(self) -> None:
        for ct in (CatchType.BUMP, CatchType.WEDGE, CatchType.LOOP):
            with self.subTest(catch_type=ct.value):
                spec = BoxSpec(
                    width=80.0,
                    length=60.0,
                    height=30.0,
                    wall_thickness=2.0,
                    lid_thickness=2.0,
                    catch_type=ct,
                )
                closure = cap_slipover_catch(spec, is_slipover=True)
                self.assertIsNotNone(closure.body)
                self.assertIsNotNone(closure.lid)

    def test_cap_slipover_catch_none(self) -> None:
        spec = BoxSpec(
            width=80.0,
            length=60.0,
            height=30.0,
            wall_thickness=2.0,
            lid_thickness=2.0,
            catch_type=CatchType.NONE,
        )
        closure_cap = cap_slipover_catch(spec, is_slipover=False)
        self.assertIsNone(closure_cap.body)
        self.assertIsNone(closure_cap.lid)

        closure_slip = cap_slipover_catch(spec, is_slipover=True)
        self.assertIsNone(closure_slip.body)
        self.assertIsNone(closure_slip.lid)


class HingeCatchTests(unittest.TestCase):
    """Tests for hinged front catches across all CatchTypes (FR-099)."""

    def test_hinge_catch_types(self) -> None:
        for ct in (CatchType.WEDGE, CatchType.BUMP, CatchType.LOOP):
            with self.subTest(catch_type=ct.value):
                spec = BoxSpec(
                    width=80.0,
                    length=60.0,
                    height=30.0,
                    wall_thickness=2.0,
                    lid_thickness=2.0,
                    catch_type=ct,
                )
                closure = hinge_catch(spec)
                self.assertIsNotNone(closure.body_cut)
                self.assertIsNotNone(closure.lid)

    def test_hinge_catch_none(self) -> None:
        spec = BoxSpec(
            width=80.0,
            length=60.0,
            height=30.0,
            wall_thickness=2.0,
            lid_thickness=2.0,
            catch_type=CatchType.NONE,
        )
        closure = hinge_catch(spec)
        self.assertIsNone(closure.body_cut)
        self.assertIsNone(closure.lid)


class SnapFitCatchTests(unittest.TestCase):
    """Tests for SnapFitBox cantilever latch arms across all CatchTypes (FR-099)."""

    def test_snap_fit_box_build(self) -> None:
        impl = BOX_IMPL_REGISTRY[BoxType.SNAP_FIT]()
        for ct in (CatchType.WEDGE, CatchType.BUMP, CatchType.LOOP, CatchType.NONE):
            with self.subTest(catch_type=ct.value):
                spec = BoxSpec(
                    width=80.0,
                    length=60.0,
                    height=30.0,
                    wall_thickness=2.0,
                    floor_thickness=2.0,
                    lid_thickness=2.0,
                    catch_type=ct,
                )
                body = impl.build_body(spec)
                lid = impl.build_lid(spec)
                self.assertIsNotNone(body)
                self.assertIsNotNone(lid)


class PreCsgValidationTests(unittest.TestCase):
    """Tests for pre-CSG catch boundary validation (FR-099)."""

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


if __name__ == "__main__":
    unittest.main()
