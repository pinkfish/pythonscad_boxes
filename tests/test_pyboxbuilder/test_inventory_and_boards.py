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

    def test_packing_pdf_renders_two_column_summary_and_checklist(self) -> None:
        """Two-column Box Summary and Component Checklist handle wrapping, spacers, and loose items."""
        proj = Project(
            "TwoColPdfTest",
            game_box_size=(240.0, 200.0, 50.0),
            clearance_slack=0.0,
            generate_spacers=True,
            box_defaults={"expandable": False},
        )
        proj.define_inventory(
            {
                "Action Cards": 50,
                "Event Cards": 30,
                "Gold Coins": 40,
                "Silver Coins": 40,
                "Wood Cubes": 24,
                "Stone Cubes": 24,
                "Player Boards": 4,
            }
        )
        proj.component("Cloth Draw Bag", 1, location="Inside spacer_1")
        proj.board(
            "Player Boards",
            size=(240.0, 200.0, 10.0),
            position=(0.0, 0.0, 40.0),
            count=4,
            component="Player Boards",
            notes="Stacked flat on top of the printed insert trays inside the game box",
        )
        for idx, (label, comp_a, qty_a, comp_b, qty_b) in enumerate(
            [
                ("PlayerBox_Red", "Action Cards", 25, "Wood Cubes", 12),
                ("PlayerBox_Blue", "Action Cards", 25, "Wood Cubes", 12),
                ("MarketBox_A", "Event Cards", 15, "Stone Cubes", 12),
                ("MarketBox_B", "Event Cards", 15, "Stone Cubes", 12),
                ("BankBox_Gold", "Gold Coins", 40, "Silver Coins", 20),
                ("BankBox_Silver", "Silver Coins", 20, "Gold Coins", 0),
            ]
        ):
            bx = proj.box(
                BoxType.CAP,
                label,
                size=(70.0, 60.0, 35.0),
                position=((idx % 3) * 72.0, (idx // 3) * 65.0, 0.0),
            )
            bx.compartment(comp_a, component=comp_a, count=qty_a)
            if qty_b > 0:
                bx.compartment(comp_b, component=comp_b, count=qty_b)

        build = proj.build()
        assert build.packing is not None

        with tempfile.TemporaryDirectory() as tmp:
            out_pdf = Path(tmp) / "two_col_guide.pdf"
            result = generate_layout_pdf(
                build.packing,
                out_pdf,
                "TwoColPdfTest",
                (240.0, 200.0, 50.0),
                box_builders=proj.boxes,
                manifest=proj.manifest,
                pipeline=proj.pipeline,
            )
            self.assertIsNotNone(result)
            assert result is not None
            self.assertTrue(result.exists())
            self.assertGreater(result.stat().st_size, 2000)

    def test_game_board_validation(self) -> None:
        """GameBoard rejects non-positive dimensions or count < 1."""
        with self.assertRaises(ValueError):
            GameBoard("Bad", size=(0.0, 10.0, 5.0), position=(0.0, 0.0, 0.0))
        with self.assertRaises(ValueError):
            GameBoard("BadCount", size=(10.0, 10.0, 5.0), position=(0.0, 0.0, 0.0), count=0)

    def test_small_vertical_gap_absorbed_into_box_height(self) -> None:
        """A <= 10mm vertical gap above a box grows the box height instead of adding a thin spacer."""
        proj = Project(
            "HeightAbsorbTest",
            game_box_size=(120.0, 100.0, 48.0),
            clearance_slack=0.0,
            generate_spacers=True,
            box_defaults={"expandable": False},
        )
        # 8mm gap below the 48mm ceiling -> should grow from 40mm to 48mm with 0 spacers
        box = proj.box(BoxType.CAP, "Tokens", size=(120.0, 100.0, 40.0))
        box.compartment("Tokens", count=10)
        build = proj.build()
        assert build.packing is not None
        self.assertEqual(len(build.packing.spacer_placements), 0)
        self.assertAlmostEqual(build.packing.placements[0].size[2], 48.0, places=3)
        assert box.final_size is not None
        self.assertAlmostEqual(box.final_size[2], 48.0, places=3)

        # Opting out via max_height_absorb=0.0 keeps exact 40mm height
        proj_optout = Project(
            "HeightAbsorbOptOut",
            game_box_size=(120.0, 100.0, 48.0),
            clearance_slack=0.0,
            generate_spacers=True,
            max_height_absorb=0.0,
            box_defaults={"expandable": False},
        )
        proj_optout.box(BoxType.CAP, "Tokens", size=(120.0, 100.0, 40.0)).compartment("Tokens")
        b2 = proj_optout.build()
        assert b2.packing is not None
        self.assertAlmostEqual(b2.packing.placements[0].size[2], 40.0, places=3)

    def test_every_example_game_declares_and_allocates_full_inventory(self) -> None:
        """Every game in boxes/ declares a piece inventory and allocates 100% of its pieces."""
        import importlib.util

        repo_root = Path(__file__).resolve().parents[2]
        game_files = sorted(
            p
            for p in (repo_root / "boxes").glob("*/*.py")
            if not p.parent.name.startswith("_") and p.stem == p.parent.name
        )
        self.assertGreaterEqual(len(game_files), 39)

        for path in game_files:
            game = path.parent.name
            with self.subTest(game=game):
                spec = importlib.util.spec_from_file_location(f"_inv_check_{game}", path)
                assert spec is not None and spec.loader is not None
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                proj = mod.project
                self.assertGreater(
                    len(proj.components),
                    0,
                    f"{game} is missing project.define_inventory(...)",
                )
                ver = proj.verify_inventory(strict=False)
                self.assertTrue(
                    ver.is_valid,
                    f"{game} inventory mismatch: {ver.format_errors()}",
                )

    def test_loose_item_location_passes_strict_inventory_and_appears_in_checklist(self) -> None:
        """Loose items with an explicit location (e.g. inside a spacer) satisfy strict inventory."""
        proj = Project(
            "LooseItemTest",
            game_box_size=(200.0, 150.0, 45.0),
            clearance_slack=0.0,
            generate_spacers=True,
        )
        proj.component("Coins", 30)
        proj.component("Cloth Draw Bag", 1, location="Inside spacer_1")
        proj.box(BoxType.CAP, "Bank", size=(90.0, 70.0, 40.0)).compartment("Coins", component="Coins", count=30)

        ver = proj.verify_inventory(strict=True)
        self.assertTrue(ver.is_valid, ver.format_errors())

        inv = proj.inventory()
        rows = {row.name: row for row in inv.checklist}
        self.assertIn("Coins", rows)
        self.assertEqual(rows["Coins"].count, 30)
        self.assertEqual(rows["Coins"].format_locations(), "Bank")
        self.assertIn("Cloth Draw Bag", rows)
        self.assertEqual(rows["Cloth Draw Bag"].count, 1)
        self.assertEqual(rows["Cloth Draw Bag"].format_locations(), "Inside spacer_1")

    def test_exact_tile_and_banknote_counts_in_checklist(self) -> None:
        """18_cuba and 1835 expose exact individual tile and banknote counts in their checklists."""
        import importlib.util

        repo_root = Path(__file__).resolve().parents[2]
        for game, expected_items in (
            (
                "18_cuba",
                {
                    "Yellow Track Hex Tiles": 45,
                    "Green Track Hex Tiles": 47,
                    "Brown Track Hex Tiles": 25,
                    "Grey Track Hex Tiles": 6,
                    "Red Track Hex Tile": 1,
                    "Paper Banknotes": 200,
                },
            ),
            (
                "1835",
                {
                    "Yellow Track Hex Tiles": 53,
                    "Green Track Hex Tiles": 46,
                    "Brown Track Hex Tiles": 34,
                    "Grey Track Hex Tiles": 4,
                    "Banknotes": 200,
                },
            ),
        ):
            path = repo_root / "boxes" / game / f"{game}.py"
            spec = importlib.util.spec_from_file_location(f"_checklist_{game}", path)
            assert spec is not None and spec.loader is not None
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            inv = mod.project.inventory()
            rows = {row.name: row for row in inv.checklist}
            for name, expected_count in expected_items.items():
                self.assertIn(name, rows, f"{game} checklist missing {name!r}")
                self.assertEqual(rows[name].count, expected_count)
                self.assertTrue(rows[name].locations, f"{game} checklist row {name!r} has no location")

    def test_component_first_api_store_well_svg_and_fit(self) -> None:
        """define_cards/define_piece/define_loose + box.store()/box.well() enforce counts, SVGs, and fit."""
        brink_svg = Path(__file__).resolve().parents[2] / "boxes" / "brink" / "svg" / "class_iii_ship.svg"
        self.assertTrue(brink_svg.exists())

        proj = Project("ComponentFirstTest", game_box_size=(220.0, 180.0, 60.0))
        actions = proj.define_cards("Action Cards", count=50, size=(63.5, 88.0), thickness=0.6)
        ships = proj.define_piece("Class III Ships", count=2, size=(43.0, 37.2, 10.0), svg=brink_svg)
        coins = proj.define_piece("Coins", count=20, diameter=20.0, thickness=2.0, bulk=True)
        hexes = proj.define_tile("Map Hexes", count=10, size=(40.0, 40.0, 2.0))
        proj.define_loose("Cloth Bag", count=1, location="Inside spacer_1")

        # Card box derives height automatically from 50 x 0.6mm = 30mm
        cbox = proj.box(BoxType.SLIDING, "Cards", size=(70.0, 96.0, None))
        cbox.store(actions)

        # Piece box uses box.well() for SVG ships and box.store() for bulk coins + tiles
        pbox = proj.box(BoxType.CAP, "Pieces", size=(120.0, 110.0, 28.0))
        pbox.compartment(
            "Ships",
            size=(95.0, 45.0),
            elements=(
                pbox.well(ships, count=1, offset=(2.0, 2.0)),
                pbox.well(ships, count=1, offset=(48.0, 2.0)),
            ),
        )
        pbox.store(coins, size=(50.0, 42.0))
        pbox.store(hexes, size=(42.0, 42.0))

        ver = proj.verify_inventory(strict=True)
        self.assertTrue(ver.is_valid)
        self.assertEqual(ver.missing_svgs, ())
        self.assertEqual(ver.fit_warnings, ())

        # Checklist includes all 5 declared component types
        inv = proj.inventory()
        names = [r.name for r in inv.checklist]
        self.assertEqual(names, ["Action Cards", "Class III Ships", "Coins", "Map Hexes", "Cloth Bag"])

    def test_verify_inventory_catches_missing_svg_and_fit_violations(self) -> None:
        """verify_inventory flags missing SVG cutouts, missing SVG files, and undersized boxes."""
        brink_svg = Path(__file__).resolve().parents[2] / "boxes" / "brink" / "svg" / "class_iii_ship.svg"

        # 1. Non-bulk piece declares SVG, but box only adds a plain rectangle compartment
        proj_svg = Project("MissingSvgTest", game_box_size=(200.0, 150.0, 50.0))
        ships = proj_svg.define_piece("Ships", count=2, size=(43.0, 37.2, 10.0), svg=brink_svg)
        proj_svg.box(BoxType.CAP, "Tray", size=(100.0, 80.0, 25.0)).compartment(
            "Ships", component=ships, count=2, size=(50.0, 45.0)
        )
        v_svg = proj_svg.verify_inventory(strict=False)
        self.assertFalse(v_svg.is_valid)
        self.assertEqual(len(v_svg.missing_svgs), 1)
        self.assertIn("class_iii_ship.svg", v_svg.format_errors())

        # 2. Missing SVG file on disk
        proj_missing_file = Project("MissingFileTest", game_box_size=(200.0, 150.0, 50.0))
        ghost = proj_missing_file.define_piece(
            "Ghost", count=1, size=(20.0, 20.0, 5.0), svg="/nonexistent/ghost.svg"
        )
        proj_missing_file.box(BoxType.CAP, "Tray", size=(60.0, 60.0, 20.0)).store(ghost)
        v_file = proj_missing_file.verify_inventory(strict=False)
        self.assertFalse(v_file.is_valid)
        self.assertIn("SVG file not found", v_file.format_errors())

        # 3. Card box too short & compartment footprint too narrow
        proj_fit = Project("FitFailTest", game_box_size=(200.0, 150.0, 50.0))
        deck = proj_fit.define_cards("BigDeck", count=100, size=(63.5, 88.0), thickness=0.6)
        proj_fit.box(BoxType.SLIDING, "TooSmall", size=(70.0, 95.0, 20.0)).compartment(
            "BigDeck", component=deck, count=100, size=(50.0, 80.0)
        )
        v_fit = proj_fit.verify_inventory(strict=False)
        self.assertFalse(v_fit.is_valid)
        self.assertEqual(len(v_fit.fit_warnings), 2)
        self.assertIn("does not fit compartment", v_fit.format_errors())
        self.assertIn("needs 60.0mm height", v_fit.format_errors())
        with self.assertRaises(ValueError):
            proj_fit.verify_inventory(strict=True)

