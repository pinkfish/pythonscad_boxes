# SPDX-License-Identifier: Apache-2.0
"""Tests verifying CI isolation between base library tests and game box insert tests."""

from __future__ import annotations

import unittest

from tests.conftest import get_box_example_names, is_box_example_path


class CiIsolationTests(unittest.TestCase):
    """Tests ensuring that game box inserts are properly recognized and excluded from base tests."""

    def test_box_directory_discovery(self) -> None:
        """Verify that get_box_example_names discovers all active game directories in boxes/."""
        boxes = get_box_example_names()
        self.assertGreaterEqual(len(boxes), 35)
        self.assertIn("cascadero", boxes)
        self.assertIn("1835", boxes)
        self.assertIn("root", boxes)
        self.assertIn("earth", boxes)
        self.assertIn("earth_animal_kingdom", boxes)
        # Template and hidden directories must not be treated as games
        self.assertNotIn("_template", boxes)

    def test_box_example_identification(self) -> None:
        """Verify that test files corresponding to boxes are accurately identified."""
        self.assertTrue(is_box_example_path("tests/test_pyboxbuilder/test_cascadero.py"))
        self.assertTrue(is_box_example_path("tests/test_pyboxbuilder/test_1835.py"))
        self.assertTrue(is_box_example_path("tests/test_pyboxbuilder/test_root.py"))
        self.assertTrue(is_box_example_path("test_ci_smoke.py"))
        self.assertTrue(is_box_example_path("test_quickstart.py"))

    def test_base_library_tests_not_identified_as_boxes(self) -> None:
        """Verify that core base library tests are never marked as box examples."""
        base_test_files = [
            "tests/test_pyboxbuilder/test_builders.py",
            "tests/test_pyboxbuilder/test_closures.py",
            "tests/test_pyboxbuilder/test_validation.py",
            "tests/test_pyboxbuilder/test_spec_lifecycle.py",
            "tests/test_pyboxbuilder/test_layout.py",
            "tests/test_pyboxbuilder/test_project.py",
            "tests/test_pyboxbuilder/test_rounding.py",
            "tests/test_pyboxbuilder/test_finger_smoothing.py",
            "tests/test_pyboxbuilder/test_ci_isolation.py",
        ]
        for path in base_test_files:
            self.assertFalse(
                is_box_example_path(path),
                f"{path} should be recognized as a base library test, not a box example",
            )

    def test_every_box_directory_is_detected(self) -> None:
        """Verify that synthetic test paths for every discovered box directory are recognized as box examples."""
        boxes = get_box_example_names()
        for box_name in boxes:
            test_path = f"tests/test_pyboxbuilder/test_{box_name}.py"
            self.assertTrue(
                is_box_example_path(test_path),
                f"{test_path} should be identified as a box example",
            )
