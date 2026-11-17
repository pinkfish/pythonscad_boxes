# SPDX-License-Identifier: Apache-2.0
"""Tests for the Root board game insert."""

import unittest

from boxes.root.root import (
    ROOT_BOX_CATALOG,
    ROOT_EXPANSIONS,
    RootBoxCategory,
    build_root_project,
    project,
    summarize_board_storage,
)


class TestRoot(unittest.TestCase):
    """Test suite for Root project build and layout."""

    def test_build_completes(self) -> None:
        """Verify the project builds all pieces without errors."""
        build = project.build()
        self.assertGreater(len(build.pieces), 20)

    def test_box_labels_present(self) -> None:
        """Verify key faction box labels are present."""
        labels = {b.label for b in project._boxes}
        expected = {
            "MarquisBoxBottom",
            "MarquisBoxTop",
            "ErieBoxBottom",
            "ErieBoxTop",
            "AllianceBoxBottom",
            "AllianceBoxTop",
            "RiverfolkBoxBottom",
            "RiverfolkBoxTop",
            "LizardBoxBottom",
            "LizardBoxTop",
            "VagabondBox",
            "VagabondBox2",
            "BaseCardBox",
            "ErieCardBox",
            "VagabondCardBox",
            "OverviewCardBox",
            "ItemsBoxBottom",
            "ItemsBoxMiddle",
            "ItemsBoxWinter",
            "ItemsBoxExtras",
            "DiceBox",
        }
        for name in expected:
            self.assertIn(name, labels)

    def test_all_pieces_fit_within_box_bounds(self) -> None:
        """Verify pieces are placed within game box boundaries."""
        build = project.build()
        tol = 1e-3
        box_width, box_length, box_height = 214.0, 278.0, 67.0
        for piece in build.pieces:
            if piece.position is None or piece.size is None:
                continue
            x, y, z = piece.position
            w, l, h = piece.size
            self.assertGreaterEqual(x, -tol, f"{piece.label} X < 0")
            self.assertGreaterEqual(y, -tol, f"{piece.label} Y < 0")
            self.assertGreaterEqual(z, -tol, f"{piece.label} Z < 0")
            self.assertLessEqual(x + w, box_width + tol, f"{piece.label} overflows box width ({x+w} > {box_width})")
            self.assertLessEqual(y + l, box_length + tol, f"{piece.label} overflows box length ({y+l} > {box_length})")
            self.assertLessEqual(z + h, box_height + tol, f"{piece.label} overflows box height ({z+h} > {box_height})")

    def test_bottom_board_space_reserved_not_spacer(self) -> None:
        """Verify bottom 28mm board bay has no pieces or auto-generated spacers."""
        build = project.build()
        spacers = [piece for piece in build.pieces if piece.kind == "spacer"]
        self.assertGreaterEqual(len(spacers), 2)
        for piece in build.pieces:
            if piece.position is None:
                continue
            self.assertGreaterEqual(
                piece.position[2],
                28.0 - 1e-3,
                f"{piece.label} encroaches on bottom 28mm board bay at z={piece.position[2]}",
            )

    def test_two_vagabond_boxes_with_relation_pockets(self) -> None:
        """Verify both Vagabond boxes are present with warrior, score, and 2 Relation pockets."""
        for label in ("VagabondBox", "VagabondBox2"):
            box = next(b for b in project._boxes if b.label == label)
            elements = box.compartments[0].elements
            texts = [el.shape_file for el in elements if el.shape_file == "Relation"]
            self.assertEqual(len(texts), 2, f"{label} should have two Relation inlays")

    def test_base_only_expansion_selection(self) -> None:
        """Verify Base Game builds cleanly without Riverfolk expansion boxes."""
        base_proj = build_root_project(("base",))
        base_labels = {b.label for b in base_proj._boxes}
        self.assertEqual(len(base_labels), 16)
        for absent in (
            "LizardBoxBottom",
            "LizardBoxTop",
            "RiverfolkBoxBottom",
            "RiverfolkBoxTop",
            "VagabondBox2",
        ):
            self.assertNotIn(absent, base_labels)

        base_build = base_proj.build()
        spacers = [p for p in base_build.pieces if p.kind == "spacer"]
        self.assertGreater(len(spacers), 0)
        for piece in base_build.pieces:
            if piece.position is None:
                continue
            self.assertGreaterEqual(piece.position[2], 28.0 - 1e-3)

    def test_subgroup_filter_and_planned_expansions(self) -> None:
        """Verify custom subgroup filtering, complete box catalog, and planned expansion hooks."""
        custom = build_root_project(subgroups=("shared_cards", "marquise"))
        self.assertEqual(
            {b.label for b in custom._boxes},
            {"BaseCardBox", "OverviewCardBox", "MarquisBoxBottom", "MarquisBoxTop"},
        )

        catalog_labels = {meta.label for meta in ROOT_BOX_CATALOG}
        self.assertEqual(catalog_labels, {b.label for b in project._boxes})
        self.assertEqual(
            {meta.category for meta in ROOT_BOX_CATALOG},
            {RootBoxCategory.CARDS, RootBoxCategory.FACTIONS, RootBoxCategory.ITEMS_AND_DICE},
        )

        planned = {spec.key for spec in ROOT_EXPANSIONS if spec.status == "planned"}
        self.assertTrue({"underworld", "marauder"}.issubset(planned))
        with self.assertRaises(NotImplementedError):
            build_root_project(("base", "underworld"))

    def test_expected_pocket_counts_for_all_boxes(self) -> None:
        """Verify each faction and item tray has the exact expected number of main pockets."""
        expected_pockets = {
            "ItemsBoxBottom": 10,
            "ItemsBoxMiddle": 9,
            "ItemsBoxWinter": 6,
            "ItemsBoxExtras": 8,
            "MarquisBoxBottom": 3,
            "MarquisBoxTop": 10,
            "ErieBoxBottom": 2,
            "ErieBoxTop": 3,
            "AllianceBoxBottom": 2,
            "AllianceBoxTop": 4,
            "LizardBoxBottom": 25,
            "LizardBoxTop": 6,
            "RiverfolkBoxBottom": 3,
            "RiverfolkBoxTop": 7,
            "VagabondBox": 4,
            "VagabondBox2": 4,
            "DiceBox": 2,
        }
        from pyboxbuilder.enums import ElementShape

        boxes_by_label = {b.label: b for b in project._boxes}
        for label, expected in expected_pockets.items():
            elements = boxes_by_label[label].compartments[0].elements
            pockets = [
                el
                for el in elements
                if el.depth > 1.0
                and not (
                    el.shape is ElementShape.CIRCLE
                    and el.footprint == (12.0, 12.0)
                    and not el.pull_out
                )
            ]
            self.assertEqual(
                len(pockets),
                expected,
                f"{label} should have {expected} pockets, got {len(pockets)}",
            )

    def test_all_riverfolk_subset_spacers_fit_without_overlap(self) -> None:
        """Verify every Base + partial Riverfolk combination builds non-overlapping spacers."""
        import itertools

        base_sgs = list(ROOT_EXPANSIONS[0].subgroups)
        rf_sgs = sorted(ROOT_EXPANSIONS[1].subgroups)

        def _box_volume(items: list[object]) -> float:
            total = 0.0
            for item in items:
                s = item.size  # type: ignore[attr-defined]
                total += s[0] * s[1] * s[2]
            return total

        full_proj = build_root_project(("base", "riverfolk"))
        full_spacers = full_proj._compiler.spacer_placements(
            full_proj._manifest, full_proj._compiler.resolve_final_layout(full_proj._manifest)
        )

        for r in range(len(rf_sgs)):
            for combo in itertools.combinations(rf_sgs, r):
                sub_proj = build_root_project(subgroups=[*base_sgs, *combo])
                packing = sub_proj._compiler.resolve_final_layout(sub_proj._manifest)
                spacers = sub_proj._compiler.spacer_placements(sub_proj._manifest, packing)
                self.assertGreater(len(spacers), 0)
                # Omitting any Riverfolk boxes leaves strictly more spacer volume than full layout
                self.assertGreater(_box_volume(spacers), _box_volume(full_spacers))
                for sp in spacers:
                    self.assertGreaterEqual(sp.position[2], 28.0 - 1e-3)
                    self.assertLessEqual(sp.position[2] + sp.size[2], 67.0 + 1e-3)
                    if sp.path is not None:
                        continue
                    for bx in packing.placements:
                        overlap_x = (
                            sp.position[0] < bx.position[0] + bx.size[0] - 1e-2
                            and sp.position[0] + sp.size[0] > bx.position[0] + 1e-2
                        )
                        overlap_y = (
                            sp.position[1] < bx.position[1] + bx.size[1] - 1e-2
                            and sp.position[1] + sp.size[1] > bx.position[1] + 1e-2
                        )
                        overlap_z = (
                            sp.position[2] < bx.position[2] + bx.size[2] - 1e-2
                            and sp.position[2] + sp.size[2] > bx.position[2] + 1e-2
                        )
                        self.assertFalse(
                            overlap_x and overlap_y and overlap_z,
                            f"{sp.label} overlaps {bx.label} in combo {combo}",
                        )

    def test_board_storage_indicator_and_external_boards_option(self) -> None:
        """Verify board storage status for Base-only, Base+Riverfolk, and beyond-Riverfolk."""
        base_status = summarize_board_storage(("base",))
        self.assertEqual(base_status.status, "thin_top_gap")
        self.assertGreater(base_status.top_gap_mm, 0.0)

        full_status = summarize_board_storage(("base", "riverfolk"))
        self.assertEqual(full_status.status, "exact_fit")
        self.assertAlmostEqual(full_status.overflow_mm, 0.0)
        self.assertAlmostEqual(full_status.top_gap_mm, 0.0)

        beyond_status = summarize_board_storage(("base", "riverfolk", "underworld"))
        self.assertEqual(beyond_status.status, "external_box_required")
        self.assertGreater(beyond_status.overflow_mm, 0.0)

        ext_proj = build_root_project(("base", "riverfolk"), boards_external=True)
        self.assertEqual(ext_proj.board_thickness, 0.0)
        self.assertFalse(ext_proj.board_on_bottom)
        self.assertEqual(ext_proj.effective_game_box_size, (214.0, 278.0, 67.0))
