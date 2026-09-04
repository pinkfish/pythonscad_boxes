# SPDX-License-Identifier: Apache-2.0
"""Tests for the stackable hexes organizers."""

import unittest

from boxes.stackable_hexes.stackable_hexes import project


class TestStackableHexes(unittest.TestCase):
    """Test suite for stackable hexes project build."""

    def test_build_completes(self) -> None:
        """Verify the project builds all pieces without errors."""
        build = project.build()
        self.assertGreater(len(build.pieces), 5)

    def test_box_labels_present(self) -> None:
        """Verify hex cups are defined."""
        labels = {b.label for b in project._boxes}
        self.assertGreaterEqual(len(labels), 5)
