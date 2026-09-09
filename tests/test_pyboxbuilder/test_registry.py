# SPDX-License-Identifier: Apache-2.0
"""Tests for decorator-based box type registry (FR-094 / SC-094)."""

import unittest

from pyboxbuilder.box.base import BoxTypeBase
from pyboxbuilder.box.registry import (
    BOX_IMPL_REGISTRY,
    BOX_TYPE_REGISTRY,
    LIDLESS_BOX_TYPES,
    ensure_registered,
    register_box,
)
from pyboxbuilder.enums import BoxType


class RegistryTests(unittest.TestCase):
    """Verify registry discovery, decorator registration, and completeness."""

    def test_all_23_box_types_are_registered(self) -> None:
        ensure_registered()
        self.assertEqual(len(BoxType), 23)
        for b_type in BoxType:
            with self.subTest(box_type=b_type):
                self.assertIn(b_type, BOX_TYPE_REGISTRY)
                self.assertIn(b_type, BOX_IMPL_REGISTRY)
                self.assertTrue(issubclass(BOX_IMPL_REGISTRY[b_type], BoxTypeBase))

    def test_custom_box_decorator_registration(self) -> None:
        class DummyBuilder:
            pass

        # Use an arbitrary string-based mock or dynamically registered type
        dummy_type = "custom_test_box"  # type: ignore[assignment]

        @register_box(dummy_type, builder=DummyBuilder)
        class CustomBox(BoxTypeBase):
            pass

        self.assertIn(dummy_type, BOX_IMPL_REGISTRY)
        self.assertIn(dummy_type, BOX_TYPE_REGISTRY)
        self.assertIs(BOX_IMPL_REGISTRY[dummy_type], CustomBox)
        self.assertIs(BOX_TYPE_REGISTRY[dummy_type], DummyBuilder)

    def test_lidless_box_types_set(self) -> None:
        self.assertEqual(
            LIDLESS_BOX_TYPES,
            frozenset({BoxType.NO_LID, BoxType.PATH, BoxType.PRINT_IN_PLACE_HINGE}),
        )


if __name__ == "__main__":
    unittest.main()
