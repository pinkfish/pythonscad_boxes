# SPDX-License-Identifier: Apache-2.0
"""Unit and integration tests for universal stackable box architecture (FR-101, SC-101)."""

import unittest

from mesh import volume

from pyboxbuilder.box.features import (
    build_perimeter_stacking_foot,
    build_perimeter_stacking_indent,
    build_stacking_feet,
    build_stacking_indents,
    build_stacking_pyramid_indents,
    build_stacking_pyramids,
)
from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.box.validation import GeometryValidationError, GeometryValidator
from pyboxbuilder.enums import BoxType, StackableMode, StackableShape


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

    def test_build_stacking_pyramids_and_indents(self) -> None:
        for single in (False, True):
            for cone in (False, True):
                pyramids = build_stacking_pyramids(
                    width=60.0,
                    length=80.0,
                    foot_size=7.0,
                    foot_height=1.2,
                    foot_inset=3.0,
                    clearance=0.15,
                    base_z=25.0,
                    single_pyramid=single,
                    cone=cone,
                    point_up=True,
                )
                indents = build_stacking_pyramid_indents(
                    width=60.0,
                    length=80.0,
                    foot_size=7.0,
                    indent_depth=1.2,
                    foot_inset=3.0,
                    clearance=0.15,
                    surface_z=0.0,
                    single_pyramid=single,
                    cone=cone,
                    point_up=True,
                )
                self.assertGreater(volume(pyramids), 5.0)
                self.assertGreater(volume(indents), volume(pyramids))


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
        lower_assembly = body_a if lid_a is None else (body_a | lid_a)

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
            (
                f"Box type {box_type.value} mode {spec.stackable.value} "
                f"has {collision_vol:.4f}mm³ collision volume when stacked"
            ),
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
        for bt in (BoxType.FILAMENT_HINGE, BoxType.CLAMSHELL):
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
        for mode in (
            StackableMode.FEET,
            StackableMode.INDENTS,
            StackableMode.PYRAMID,
            StackableMode.PYRAMIDS,
            StackableMode.PERIMETER,
        ):
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

    def test_pyramid_modes_and_shapes_printer_safe_flat_bed(self) -> None:
        """Verify 45-degree pyramid and pyramid-grid modes keep the box floor flat on z=0."""
        from pyboxbuilder.box.shell import block

        below_bed_probe = block([100.0, 100.0, 10.0], at=(-10.0, -10.0, -10.0))
        for mode in (
            StackableMode.PYRAMID,
            StackableMode.PYRAMIDS,
            StackableMode.INDENTS,
            StackableMode.FEET,
            StackableMode.PERIMETER,
        ):
            for shape in (
                StackableShape.PYRAMIDS,
                StackableShape.PYRAMID,
                StackableShape.CONE,
                StackableShape.FLAT,
            ):
                with self.subTest(mode=mode.value, shape=shape.value):
                    spec = BoxSpec(
                        label="PrinterSafeStack",
                        width=60.0,
                        length=70.0,
                        height=25.0,
                        wall_thickness=2.0,
                        floor_thickness=1.6,
                        lid_thickness=2.0,
                        stackable=mode,
                        stackable_shape=shape,
                        stackable_foot_size=6.5,
                        stackable_foot_height=1.2,
                        stackable_fit_offset=0.15,
                    )
                    handler = BOX_IMPL_REGISTRY[BoxType.SLIDING]()
                    body = handler.build_body(spec)
                    # Verify zero material protrudes below the build plate (z < 0)
                    self.assertLess(
                        volume(body & below_bed_probe),
                        1e-4,
                        f"Mode {mode.value} shape {shape.value} protrudes below z=0 build plate",
                    )
                    self._assert_stacking_mating(BoxType.SLIDING, spec)

        # Also verify explicit legacy downward feet when stackable_printer_safe=False
        legacy_spec = BoxSpec(
            label="LegacyBottomFeet",
            width=60.0,
            length=70.0,
            height=25.0,
            wall_thickness=2.0,
            floor_thickness=1.6,
            lid_thickness=2.0,
            stackable=StackableMode.FEET,
            stackable_shape=StackableShape.PYRAMIDS,
            stackable_printer_safe=False,
            stackable_foot_size=6.5,
            stackable_foot_height=1.2,
            stackable_fit_offset=0.15,
        )
        legacy_body = BOX_IMPL_REGISTRY[BoxType.SLIDING]().build_body(legacy_spec)
        self.assertGreater(volume(legacy_body & below_bed_probe), 1.0)
        self._assert_stacking_mating(BoxType.SLIDING, legacy_spec)

    def test_pattern_matched_stacking_across_box_families_and_patterns(self) -> None:
        """Verify StackableMode.PATTERN / StackableShape.PATTERN locks into the lid pattern."""
        from pyboxbuilder.box.shell import block
        from pyboxbuilder.enums import PatternType
        from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
        from pyboxbuilder.lid.decorate import decorate_lid

        below_bed_probe = block([100.0, 100.0, 10.0], at=(-10.0, -10.0, -10.0))

        # 1. Test multiple pattern types on SLIDING box
        for pat_type in (
            PatternType.HEX,
            PatternType.TRIANGLE,
            PatternType.SQUARE,
            PatternType.CIRCLE,
            PatternType.PENROSE,
        ):
            with self.subTest(pattern=pat_type.value):
                spec = BoxSpec(
                    label=f"PatternStack_{pat_type.value}",
                    width=60.0,
                    length=70.0,
                    height=25.0,
                    wall_thickness=2.0,
                    floor_thickness=1.6,
                    lid_thickness=2.0,
                    stackable=StackableMode.PATTERN,
                    stackable_pattern=pat_type,
                    stackable_foot_height=1.2,
                    stackable_fit_offset=0.15,
                )
                handler = BOX_IMPL_REGISTRY[BoxType.SLIDING]()
                body = handler.build_body(spec)
                # Verify flat bed contact at z=0 with zero protrusion below z=0
                self.assertLess(volume(body & below_bed_probe), 1e-4)
                # Verify the pattern tiles and outer border sit on the bed at z in [0, 0.2]
                bed_slice = block([60.0, 70.0, 0.2], at=(0.0, 0.0, 0.0))
                self.assertGreater(volume(body & bed_slice), 60.0 * 70.0 * 0.2 * 0.3)
                self._assert_stacking_mating(BoxType.SLIDING, spec)

        # 2. Test across all box families (including NO_LID and decorated through-hole lids)
        for bt in (
            BoxType.SLIDING,
            BoxType.CAP,
            BoxType.SLIPOVER,
            BoxType.FILAMENT_HINGE,
            BoxType.CLAMSHELL,
            BoxType.SNAP_FIT,
            BoxType.NO_LID,
        ):
            with self.subTest(box_type=bt.value):
                lt = 0.0 if bt is BoxType.NO_LID else 2.0
                spec = BoxSpec(
                    label=f"PatternStack_{bt.value}",
                    width=60.0,
                    length=70.0,
                    height=30.0,
                    wall_thickness=2.0,
                    floor_thickness=1.6,
                    lid_thickness=lt,
                    stackable=StackableMode.PATTERN,
                    stackable_pattern=PatternType.HEX,
                    stackable_foot_height=1.2,
                    stackable_fit_offset=0.15,
                )
                self._assert_stacking_mating(bt, spec)

        # 3. Verify decorated lid with through-hole HEX pattern mates cleanly with box above
        spec_dec = BoxSpec(
            label="DecoratedPatternStack",
            width=60.0,
            length=70.0,
            height=25.0,
            wall_thickness=2.0,
            floor_thickness=1.6,
            lid_thickness=2.0,
            stackable=StackableMode.PATTERN,
            stackable_pattern=PatternType.HEX,
            stackable_foot_height=1.2,
            stackable_fit_offset=0.15,
        )
        handler = BOX_IMPL_REGISTRY[BoxType.SLIDING]()
        body_a = handler.build_body(spec_dec)
        raw_lid_a = handler.build_lid(spec_dec)
        dec_lid_a = decorate_lid(
            raw_lid_a,
            LidBuilder(pattern=PatternBuilder(PatternType.HEX)),
            spec_dec.lid_thickness,
            reserved=handler.lid_keepouts(spec_dec),
            top_z=spec_dec.height,
            face_size=(spec_dec.width, spec_dec.length),
        ).solid
        # Verify the raised pattern ridge above z = spec_dec.height is preserved intact
        above_probe = block([60.0, 70.0, 5.0], at=(0.0, 0.0, spec_dec.height + 0.01))
        self.assertAlmostEqual(
            volume(raw_lid_a & above_probe),
            volume(dec_lid_a & above_probe),
            places=2,
        )
        lower_dec = body_a | dec_lid_a
        upper_b = body_a.translate([0.0, 0.0, spec_dec.height])
        self.assertLess(volume(lower_dec & upper_b), 1e-3)
        shifted_b = upper_b.translate([0.6, 0.0, 0.0])
        self.assertGreater(volume(lower_dec & shifted_b), 0.05)

    def test_builder_propagates_lid_pattern_to_stackable_spec(self) -> None:
        """Verify UnresolvedBoxSpec.from_builder inherits pattern settings for pattern stacking."""
        from pyboxbuilder.box.spec import build_spec
        from pyboxbuilder.enums import PatternType
        from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
        from pyboxbuilder.project import Project

        proj = Project("PatternStackProj")
        b = proj.box(
            BoxType.SLIDING,
            "HexStack",
            size=(60, 70, 25),
            stackable=StackableMode.PATTERN,
            lid=LidBuilder(pattern=PatternBuilder(PatternType.TRIANGLE, spacing=10.0, web=1.8)),
        )
        resolved = build_spec(proj, b, (60.0, 70.0, 25.0))
        self.assertEqual(resolved.stackable, StackableMode.PATTERN)
        self.assertEqual(resolved.stackable_pattern, PatternType.TRIANGLE)
        self.assertEqual(resolved.stackable_pattern_spacing, 10.0)
        self.assertEqual(resolved.stackable_pattern_web, 1.8)


if __name__ == "__main__":
    unittest.main()
