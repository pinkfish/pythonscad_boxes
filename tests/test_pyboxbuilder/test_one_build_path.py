# SPDX-License-Identifier: Apache-2.0
"""FR-046c / SC-033a: a previewed part and a printed part are the same solid.

Asserted by building one box through each path and comparing the descriptions
they were built from, rather than by reading the code. The two used to be
assembled separately, and what the export's copy was missing — its rounding,
its `rim_free`, its `inner_rounding`, its per-side wall tops — was invisible in
every test, because the geometry tests all go through the preview (FR-046b).
"""

from __future__ import annotations

import tempfile
import unittest

from pyboxbuilder import BoxType, FingerCut, Project


class OneBuildPathTests(unittest.TestCase):
    """The preview and the export must build from the same `BoxSpec`."""

    LABEL = "Tray"

    def project(self, box_type: BoxType) -> Project:
        p = Project("OneBuild", game_box_size=(300, 200, 80), generate_spacers=False)
        box = p.box(box_type, self.LABEL, size=(90, 70, 40), position=(0, 0, 0))
        box.compartment("Well", size=(60, 40), depth=20, cut=FingerCut.SCOOP)
        return p

    def specs_from_both_paths(self, box_type: BoxType) -> tuple:
        """The spec the preview builds with, and the one the export builds with."""
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY

        impl = BOX_IMPL_REGISTRY[box_type]
        seen: dict[str, list] = {}
        original = impl.build_body

        def spy(self, spec):
            if spec.label == OneBuildPathTests.LABEL:
                seen.setdefault(phase, []).append(spec)
            return original(self, spec)

        impl.build_body = spy
        try:
            project = self.project(box_type)
            phase = "preview"
            project.preview_pieces()
            phase = "export"
            with tempfile.TemporaryDirectory() as tmp:
                project.export(tmp)
        finally:
            impl.build_body = original

        return seen["preview"][0], seen["export"][0]

    def test_every_walled_type_builds_the_same_description(self) -> None:
        for box_type in (BoxType.NO_LID, BoxType.SLIDING, BoxType.CAP,
                         BoxType.SLIPOVER, BoxType.INSET):
            with self.subTest(box_type=box_type.value):
                preview, export = self.specs_from_both_paths(box_type)
                self.assertEqual(preview, export)

    def test_the_rounding_reaches_the_exported_part(self) -> None:
        """The specific loss this rule exists to prevent (FR-043/FR-044).

        Equality alone would not catch a field dropped from *both* paths, so
        this also asserts the value is the one the rule asks for: a lidless
        box's rim is exposed on both faces, so it rounds (FR-043f).
        """
        preview, export = self.specs_from_both_paths(BoxType.NO_LID)
        for field in ("rounding", "rim_free", "inner_rounding"):
            with self.subTest(field=field):
                self.assertEqual(getattr(preview, field), getattr(export, field))
        self.assertTrue(export.rim_free, "a lidless box's rim must round")

    def test_a_lidded_box_keeps_its_rim_square_on_both_paths(self) -> None:
        """The other half of FR-043d, so `rim_free` is not simply always True."""
        preview, export = self.specs_from_both_paths(BoxType.CAP)
        self.assertFalse(preview.rim_free)
        self.assertFalse(export.rim_free)

    def test_the_wall_tops_reach_the_exported_part(self) -> None:
        """Per-side tops decide where a scoop's roll lands (FR-070/FR-071)."""
        preview, export = self.specs_from_both_paths(BoxType.SLIDING)
        self.assertTrue(preview.wall_tops, "the preview resolved no wall tops")
        self.assertEqual(preview.wall_tops, export.wall_tops)

    @staticmethod
    def _standalone(with_well: bool) -> Project:
        p = Project("Standalone")
        box = p.box(BoxType.NO_LID, "Tray", size=(90, 70, 40))
        if with_well:
            box.compartment("Well", size=(60, 40), depth=20)
        return p

    def test_a_standalone_box_carves_its_compartments(self) -> None:
        """FR-037: standalone export used to build a plain shell.

        It assembled a six-field spec of its own and never called the carve at
        all, so a standalone box exported as an empty box whatever was put in
        it. Measured as a difference against the same box with no well, since
        the carve is the only thing that differs between them.
        """
        empty = self._standalone(with_well=False).build().pieces[0]
        carved = self._standalone(with_well=True).build().pieces[0]
        self.assertNotEqual(
            repr(empty.solid), repr(carved.solid),
            "the well was not carved out of the standalone body",
        )

    def test_a_standalone_box_is_sized_and_placed(self) -> None:
        """Its `final_size` is resolved, so the exporter records real bounds."""
        piece = self._standalone(with_well=True).build().pieces[0]
        self.assertEqual(piece.size, (90.0, 70.0, 40.0))
        self.assertEqual(piece.builder.final_size, (90.0, 70.0, 40.0))


if __name__ == "__main__":
    unittest.main()
