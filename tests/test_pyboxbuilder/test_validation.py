# SPDX-License-Identifier: Apache-2.0
"""Tests for pre-CSG geometric validation (FR-092 / SC-092)."""

import unittest

from pyboxbuilder.box.spec import BoxSpec, ResolvedBoxSpec
from pyboxbuilder.box.validation import GeometryValidationError, GeometryValidator


class GeometryValidatorTests(unittest.TestCase):
    """Verify fail-fast invariant checks on ResolvedBoxSpec."""

    def test_valid_box_passes_validation(self) -> None:
        spec = ResolvedBoxSpec(width=50.0, length=60.0, height=25.0)
        # Should not raise
        GeometryValidator.validate(spec)

    def test_zero_or_negative_envelope_dimension_raises(self) -> None:
        spec = BoxSpec(width=0.0, length=50.0, height=20.0)
        with self.assertRaises(GeometryValidationError) as ctx:
            GeometryValidator.validate(spec)
        self.assertIn("positive_finite_envelope", str(ctx.exception))

        spec_neg = BoxSpec(width=50.0, length=-10.0, height=20.0)
        with self.assertRaises(GeometryValidationError) as ctx:
            GeometryValidator.validate(spec_neg)
        self.assertIn("positive_finite_envelope", str(ctx.exception))

    def test_wall_thickness_below_printable_minimum_raises(self) -> None:
        spec = BoxSpec(width=50.0, length=50.0, height=20.0, wall_thickness=0.5)
        with self.assertRaises(GeometryValidationError) as ctx:
            GeometryValidator.validate(spec)
        self.assertIn("min_wall_thickness", str(ctx.exception))

    def test_floor_thickness_below_printable_minimum_raises(self) -> None:
        spec = BoxSpec(width=50.0, length=50.0, height=20.0, floor_thickness=0.4)
        with self.assertRaises(GeometryValidationError) as ctx:
            GeometryValidator.validate(spec)
        self.assertIn("min_floor_thickness", str(ctx.exception))

    def test_width_smaller_than_two_walls_raises(self) -> None:
        # wall_thickness = 5.0, width = 8.0 < 2 * 5.0 + 1.0 = 11.0
        spec = BoxSpec(width=8.0, length=50.0, height=20.0, wall_thickness=5.0)
        with self.assertRaises(GeometryValidationError) as ctx:
            GeometryValidator.validate(spec)
        self.assertIn("envelope_width_sanity", str(ctx.exception))

    def test_length_smaller_than_two_walls_raises(self) -> None:
        spec = BoxSpec(width=50.0, length=8.0, height=20.0, wall_thickness=5.0)
        with self.assertRaises(GeometryValidationError) as ctx:
            GeometryValidator.validate(spec)
        self.assertIn("envelope_length_sanity", str(ctx.exception))

    def test_height_cannot_contain_floor_and_lid_raises(self) -> None:
        # floor = 2.0, lid = 3.0, height = 4.0 <= 5.0
        spec = BoxSpec(width=50.0, length=50.0, height=4.0, floor_thickness=2.0, lid_thickness=3.0)
        with self.assertRaises(GeometryValidationError) as ctx:
            GeometryValidator.validate(spec)
        self.assertIn("envelope_height_sanity", str(ctx.exception))

    def test_negative_clearance_raises(self) -> None:
        spec = BoxSpec(width=50.0, length=50.0, height=20.0, sliding_slack=-0.1)
        with self.assertRaises(GeometryValidationError) as ctx:
            GeometryValidator.validate(spec)
        self.assertIn("non_negative_clearance", str(ctx.exception))

    def test_catch_radius_exceeding_wall_raises(self) -> None:
        spec = BoxSpec(width=50.0, length=50.0, height=20.0, wall_thickness=2.0, catch_radius=2.5)
        with self.assertRaises(GeometryValidationError) as ctx:
            GeometryValidator.validate(spec)
        self.assertIn("catch_radius_fits_wall", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
