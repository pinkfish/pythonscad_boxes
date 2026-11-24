# SPDX-License-Identifier: Apache-2.0
"""Tests for partial GameBoard modeling, automatic piece inventory, and PDF packing summaries."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pyboxbuilder import (
    BoxType,
    CompartmentElement,
    ElementShape,
    GameBoard,
    Project,
    summarize_box_pieces,
)
from pyboxbuilder.export.layout_pdf import generate_layout_pdf


class TestPartialBoardsAndInventory(unittest.TestCase):
    """Verify partial GameBoard obstacles, spacer exclusion, piece counts, and PDF output."""

    def test_partial_board_blocks_auto_packing_and_spacers(self) -> None:
        """Auto-packed boxes and auto-generated spacers must not overlap a partial GameBoard."""
        proj = Project(
            "PartialBoardTest",
            game_box_size=(200.0, 100.0, 40.0),
            clearance_slack=0.0,
            generate_spacers=True,
            box_defaults={"expandable": False},
        )
        # Reserve the left half (X = 0..100, Y = 0..100, Z = 0..40) for standing player boards
        proj.board(
            "Standing Player Boards",
            size=(100.0, 100.0, 40.0),
            position=(0.0, 0.0, 0.0),
            count=4,
            notes="Standing on edge on the left",
        )
        proj.box(BoxType.CAP, "Tokens", size=(80.0, 80.0, 40.0)).compartment("Tokens", count=30)

        build = proj.build()
        assert build.packing is not None

        # Only the Tokens box should be in printed placements — NOT the GameBoard
        self.assertEqual([p.label for p in build.packing.placements], ["Tokens"])
        tok = build.packing.placements[0]
        self.assertGreaterEqual(tok.position[0], 100.0 - 1e-3)

        # No auto-generated spacer may intrude into X < 100
        for sp in build.packing.spacer_placements:
            self.assertGreaterEqual(
                sp.position[0],
                100.0 - 1e-3,
                f"Spacer {sp.label} intrudes into GameBoard region: {sp.position}",
            )

        # No STL piece is emitted for the GameBoard
        self.assertTrue(all(p.label != "Standing Player Boards" for p in build.pieces))

        inv = proj.inventory(spacer_count=len(build.packing.spacer_placements))
        self.assertEqual(inv.printed_bodies, 1)
        self.assertEqual(inv.printed_lids, 1)
        self.assertEqual(inv.total_board_count, 4)
        self.assertEqual(inv.total_counted_pieces, 30)

    def test_element_piece_counts_exclude_helper_bites_and_inlays(self) -> None:
        """summarize_box_pieces counts real piece wells and ignores finger bites, scoops, and inlays."""
        proj = Project("CountTest", game_box_size=(150.0, 150.0, 40.0))
        box = proj.box(BoxType.CAP, "Gears", size=(120.0, 80.0, 20.0))
        box.compartment(
            "Gears",
            size=(114.0, 74.0),
            position=(0.0, 0.0),
            elements=(
                CompartmentElement(
                    shape=ElementShape.CIRCLE, size=(26.0, 26.0), offset=(2.0, 2.0), label="Gear_0"
                ),
                CompartmentElement(
                    shape=ElementShape.CIRCLE, size=(20.0, 20.0), offset=(15.0, 5.0), label="GearBite_0"
                ),
                CompartmentElement(
                    shape=ElementShape.CIRCLE, size=(26.0, 26.0), offset=(40.0, 2.0), label="Gear_1"
                ),
                CompartmentElement(
                    shape=ElementShape.CIRCLE, size=(20.0, 20.0), offset=(53.0, 5.0), label="GearBite_1"
                ),
                CompartmentElement(
                    shape=ElementShape.CIRCLE,
                    size=(10.0, 10.0),
                    offset=(10.0, 10.0),
                    color="black",
                    label="FloorIcon",
                ),
            ),
        )
        summary = summarize_box_pieces(box)
        self.assertEqual(summary.counted_pieces, 2)
        self.assertEqual(summary.format_contents(), "2x Gear")

    def test_brink_partial_boards_do_not_duplicate_implicit_board_slab(self) -> None:
        """Explicit partial boards overlapping board_thickness suppress the generic fallback slab."""
        from boxes.brink.brink import project as brink

        inv = brink.inventory()
        labels = [gb.label for gb in inv.boards]
        self.assertIn("Player Screens", labels)
        self.assertIn("Main Board & Rulebooks", labels)
        self.assertNotIn("Game Board / Manuals", labels)
        self.assertEqual(inv.total_board_count, 6)

    def test_packing_pdf_renders_summary_and_board_step(self) -> None:
        """generate_packing_pdf produces a valid PDF containing inventory and board pages."""
        proj = Project(
            "PdfBoardTest",
            game_box_size=(200.0, 150.0, 50.0),
            clearance_slack=0.0,
            generate_spacers=False,
        )
        proj.board(
            "Player Boards",
            size=(200.0, 100.0, 10.0),
            position=(0.0, 50.0, 40.0),
            count=4,
            notes="Top back",
        )
        proj.box(BoxType.SLIDING, "Cards", size=(70.0, 95.0, 35.0), position=(0.0, 0.0, 0.0)).compartment(
            "ActionCards", count=50
        )
        build = proj.build()
        assert build.packing is not None

        with tempfile.TemporaryDirectory() as tmp:
            out_pdf = Path(tmp) / "test_packing_guide.pdf"
            result = generate_layout_pdf(
                build.packing,
                out_pdf,
                "PdfBoardTest",
                (200.0, 150.0, 50.0),
                box_builders=proj.boxes,
                manifest=proj.manifest,
                pipeline=proj.pipeline,
            )
            self.assertIsNotNone(result)
            assert result is not None
            self.assertTrue(result.exists())
            self.assertGreater(result.stat().st_size, 1000)

    def test_game_board_validation(self) -> None:
        """GameBoard rejects non-positive dimensions or count < 1."""
        with self.assertRaises(ValueError):
            GameBoard("Bad", size=(0.0, 10.0, 5.0), position=(0.0, 0.0, 0.0))
        with self.assertRaises(ValueError):
            GameBoard("BadCount", size=(10.0, 10.0, 5.0), position=(0.0, 0.0, 0.0), count=0)
