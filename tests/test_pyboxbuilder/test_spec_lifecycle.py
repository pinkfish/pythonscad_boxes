# SPDX-License-Identifier: Apache-2.0
"""Tests for two-phase box specification lifecycle (FR-091 / SC-091)."""

import unittest
from dataclasses import FrozenInstanceError

from pyboxbuilder.box.spec import BoxSpec, ResolvedBoxSpec, UnresolvedBoxSpec, build_spec
from pyboxbuilder.builders.no_lid import NoLidBoxBuilder
from pyboxbuilder.project import Project


class SpecLifecycleTests(unittest.TestCase):
    """Verify UnresolvedBoxSpec and ResolvedBoxSpec lifecycle transitions."""

    def test_unresolved_spec_permits_none_dimensions(self) -> None:
        unresolved = UnresolvedBoxSpec(label="TestTray", width=None, length=None, height=None)
        self.assertIsNone(unresolved.width)
        self.assertIsNone(unresolved.length)
        self.assertIsNone(unresolved.height)

    def test_resolve_missing_dimensions_raises(self) -> None:
        unresolved = UnresolvedBoxSpec(label="TestTray", width=None, length=50.0, height=20.0)
        with self.assertRaises(ValueError) as ctx:
            unresolved.resolve()
        self.assertIn("must all be non-null", str(ctx.exception))

    def test_resolve_with_explicit_dimensions_succeeds(self) -> None:
        unresolved = UnresolvedBoxSpec(label="TestTray")
        resolved = unresolved.resolve(width=40.0, length=50.0, height=20.0)
        self.assertIsInstance(resolved, ResolvedBoxSpec)
        self.assertEqual(resolved.width, 40.0)
        self.assertEqual(resolved.length, 50.0)
        self.assertEqual(resolved.height, 20.0)
        self.assertEqual(resolved.label, "TestTray")

    def test_resolved_box_spec_is_frozen(self) -> None:
        resolved = ResolvedBoxSpec(width=40.0, length=50.0, height=20.0)
        with self.assertRaises(FrozenInstanceError):
            resolved.width = 60.0  # type: ignore[misc]

    def test_resolved_box_spec_converts_to_unresolved(self) -> None:
        resolved = ResolvedBoxSpec(width=40.0, length=50.0, height=20.0, label="Tray")
        unresolved = resolved.to_unresolved()
        self.assertIsInstance(unresolved, UnresolvedBoxSpec)
        self.assertEqual(unresolved.width, 40.0)
        self.assertEqual(unresolved.label, "Tray")
        # Can modify unresolved
        unresolved.width = 80.0
        r2 = unresolved.resolve()
        self.assertEqual(r2.width, 80.0)

    def test_build_spec_produces_resolved_spec_from_builder(self) -> None:
        p = Project("Game", game_box_size=(100, 100, 50))
        builder = NoLidBoxBuilder("Tray")
        spec = build_spec(p, builder, (40.0, 50.0, 20.0))
        self.assertIsInstance(spec, ResolvedBoxSpec)
        self.assertEqual(spec.width, 40.0)
        self.assertEqual(spec.length, 50.0)
        self.assertEqual(spec.height, 20.0)
        self.assertEqual(spec.label, "Tray")
        self.assertEqual(
            spec,
            BoxSpec(
                width=40.0,
                length=50.0,
                height=20.0,
                label="Tray",
                rim_free=True,
                tilt_to_lift=True,
            ),
        )


if __name__ == "__main__":
    unittest.main()
