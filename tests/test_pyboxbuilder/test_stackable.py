# SPDX-License-Identifier: Apache-2.0
"""Unit and integration tests for universal stackable box architecture (FR-101, SC-101)."""

import unittest
from dataclasses import replace

from mesh import volume
from pyboxbuilder.box.features import (
    apply_stackable_body,
    apply_stackable_lid,
    build_perimeter_stacking_foot,
    build_perimeter_stacking_indent,
    build_stacking_feet,
    build_stacking_indents,
)
from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.box.validation import GeometryValidationError, GeometryValidator
from pyboxbuilder.enums import BoxType, StackableMode


class StackingFeaturePrimitivesTests(unittest.TestCase):
    """Test primitive geometry solids for stacking feet and indents."""

    def test_build_stacking_feet(self) -> None:
        feet = build_stacking_feet(
            width=60.0,
            length=80.0,
            foot_size=8.0,
            foot_height=2.0,
            foot_inset=3.0,
            base_z=0.0,
            chamfer=0.6,
        )
        self.assertIsNotNone(feet)
        vol = volume(feet)
        self.assertGreater(vol, 400.0)  # 4 feet * (approx 8*8*2 = 128 minus chamfers)

    def test_build_stacking_indents(self) -> None:
        indents = build_stacking_indents(
            width=60.0,
            length=80.0,
            foot_size=8.0,
            indent_depth=2.0,
            foot_inset=3.0,
            clearance=0.15,
            top_z=30.0,
        )
        self.assertIsNotNone(indents)
        vol = volume(indents)
        self.assertGreater(vol, 400.0)

    def test_build_perimeter_stacking_features(self) -> None:
        foot_rim = build_perimeter_stacking_foot(
            width=60.0,
            length=80.0,
            rim_thickness=2.0,
            foot_height=2.0,
            inset=3.0,
            base_z=0.0,
        )
        self.assertIsNotNone(foot_rim)
        self.assertGreater(volume(foot_rim), 500.0)

        indent_ch = build_perimeter_stacking_indent(
            width=60.0,
            length=80.0,
            rim_thickness=2.0,
            indent_depth=2.0,
            inset=3.0,
            clearance=0.15,
            top_z=30.0,
        )
        self.assertIsNotNone(indent_ch)
        self.assertGreater(volume(indent_ch), 500.0)


class StackablePreCSGValidationTests(unittest.TestCase):
    """Test fail-fast validation for invalid stackable configurations."""

    def test_foot_size_exceeds_half_footprint(self) -> None:
        spec = BoxSpec(
            label="TooBigFoot",
            width=20.0,
            length=20.0,
            height=20.0,
            stackable=StackableMode.FEET,
            stackable_foot_size=12.0,  # >= min(width, length)/2 = 10.0
        )
        with self.assertRaises(GeometryValidationError) as ctx:
            GeometryValidator.validate(spec)
        self.assertEqual(ctx.exception.invariant, "stackable_foot_size_fits_footprint")

    def test_non_positive_foot_height(self) -> None:
        spec = BoxSpec(
            label="ZeroFootH",
            width=50.0,
            length=50.0,
            height=30.0,
            stackable=StackableMode.FEET,
            stackable_foot_height=0.0,
        )
        with self.assertRaises(GeometryValidationError) as ctx:
            GeometryValidator.validate(spec)
        self.assertEqual(ctx.exception.invariant, "positive_stackable_foot_height")


class StackingBoxMatingTests(unittest.TestCase):
    """Test vertical stacking and horizontal constraint across box families."""

    def _assert_stacking_mating(self, box_type: BoxType, spec: BoxSpec) -> None:
        """Verify that Box B stacked on Box A has 0 collision and resists slide."""
        handler = BOX_IMPL_REGISTRY[box_type]()

        body_a = handler.build_body(spec)
        lid_a = handler.build_lid(spec)
        if lid_a is None:
            # Monolithic or open tray
            lower_assembly = body_a
        else:
            lower_assembly = body_a | lid_a

        body_b = handler.build_body(spec)
        lid_b = handler.build_lid(spec)
        upper_assembly = body_b if lid_b is None else (body_b | lid_b)

        # In nominal closed coordinates, place upper box B so its base sits at Z = spec.height
        stacked_b = upper_assembly.translate([0.0, 0.0, spec.height])

        # 1. Verify zero solid collision volume when stacked vertically (SC-101)
        collision_vol = volume(lower_assembly & stacked_b)
        self.assertLess(
            collision_vol,
            0.05,
            f"Box type {box_type.value} mode {spec.stackable.value} has {collision_vol:.4f}mm³ collision volume when stacked",
        )

        # 2. Verify horizontal locking: shifting upper box horizontally by (clearance + 0.2mm)
        # must engage the foot against the indent wall, causing positive collision volume.
        clr = spec.stackable_fit_offset
        displaced_b = upper_assembly.translate([clr + 0.2, 0.0, spec.height])
        displaced_vol = volume(lower_assembly & displaced_b)
        self.assertGreater(
            displaced_vol,
            0.0,
            f"Box type {box_type.value} mode {spec.stackable.value} failed to lock horizontally against sliding",
        )

    def test_sliding_family_stacking(self) -> None:
        for bt in (BoxType.SLIDING, BoxType.SLIDING_CATCH, BoxType.CARD_LIBRARY):
            for mode in (StackableMode.FEET, StackableMode.INDENTS, StackableMode.PERIMETER):
                with self.subTest(box_type=bt.value, mode=mode.value):
                    spec = BoxSpec(
                        label=f"Stack_{bt.value}",
                        width=60.0,
                        length=80.0,
                        height=25.0,
                        wall_thickness=2.0,
                        floor_thickness=1.6,
                        lid_thickness=2.0,
                        stackable=mode,
                        stackable_foot_size=7.0,
                        stackable_foot_height=1.2,
                        stackable_fit_offset=0.15,
                    )
                    self._assert_stacking_mating(bt, spec)

    def test_cap_and_slipover_family_stacking(self) -> None:
        for bt in (BoxType.CAP, BoxType.SLIPOVER):
            for mode in (StackableMode.FEET, StackableMode.INDENTS, StackableMode.PERIMETER):
                with self.subTest(box_type=bt.value, mode=mode.value):
                    spec = BoxSpec(
                        label=f"Stack_{bt.value}",
                        width=60.0,
                        length=70.0,
                        height=30.0,
                        wall_thickness=2.0,
                        floor_thickness=1.6,
                        lid_thickness=2.0,
                        stackable=mode,
                        stackable_foot_size=6.5,
                        stackable_foot_height=1.2,
                        stackable_fit_offset=0.15,
                    )
                    self._assert_stacking_mating(bt, spec)

    def test_hinged_and_clamshell_family_stacking(self) -> None:
        for bt in (BoxType.HINGE, BoxType.FILAMENT_HINGE, BoxType.CLAMSHELL):
            for mode in (StackableMode.FEET, StackableMode.INDENTS, StackableMode.PERIMETER):
                with self.subTest(box_type=bt.value, mode=mode.value):
                    spec = BoxSpec(
                        label=f"Stack_{bt.value}",
                        width=60.0,
                        length=70.0,
                        height=30.0,
                        wall_thickness=2.0,
                        floor_thickness=1.6,
                        lid_thickness=2.0,
                        stackable=mode,
                        stackable_foot_size=6.0,
                        stackable_foot_height=1.2,
                        stackable_fit_offset=0.15,
                    )
                    self._assert_stacking_mating(bt, spec)

    def test_snap_fit_stacking(self) -> None:
        for mode in (StackableMode.FEET, StackableMode.INDENTS, StackableMode.PERIMETER):
            with self.subTest(mode=mode.value):
                spec = BoxSpec(
                    label="Stack_SnapFit",
                    width=60.0,
                    length=70.0,
                    height=30.0,
                    wall_thickness=2.0,
                    floor_thickness=1.6,
                    lid_thickness=2.0,
                    stackable=mode,
                    stackable_foot_size=6.0,
                    stackable_foot_height=1.2,
                    stackable_fit_offset=0.15,
                )
                self._assert_stacking_mating(BoxType.SNAP_FIT, spec)

    def test_open_tray_no_lid_stacking(self) -> None:
        for mode in (StackableMode.FEET, StackableMode.INDENTS, StackableMode.PERIMETER):
            with self.subTest(mode=mode.value):
                spec = BoxSpec(
                    label="Stack_NoLid",
                    width=60.0,
                    length=70.0,
                    height=25.0,
                    wall_thickness=2.0,
                    floor_thickness=1.6,
                    lid_thickness=0.0,
                    stackable=mode,
                    stackable_foot_size=6.0,
                    stackable_foot_height=1.2,
                    stackable_fit_offset=0.15,
                )
                self._assert_stacking_mating(BoxType.NO_LID, spec)


if __name__ == "__main__":
    unittest.main()
