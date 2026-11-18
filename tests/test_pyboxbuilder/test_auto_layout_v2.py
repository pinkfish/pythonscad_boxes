# SPDX-License-Identifier: Apache-2.0
"""Comprehensive unit tests for Auto-Layout Engine v2 (Phases 1-3)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pyboxbuilder import (
    BoxType,
    CompartmentElement,
    DispenserExtractionMode,
    ElementShape,
    LidBuilder,
    Project,
    StackableMode,
    columns,
    pack_elements,
    polygon_grid,
)
from pyboxbuilder.box.features import SLIPOVER_SLEEVE_WALL_SHARE
from pyboxbuilder.box.spec import build_spec
from pyboxbuilder.box.types.slipover import SlipoverBox
from pyboxbuilder.compartments.element import elements_footprint, elements_overlap
from pyboxbuilder.compartments.layout import (
    Interior,
    candidate_box_sizes,
    layout_compartments,
)
from pyboxbuilder.export.layout_pdf import _compute_layer_pages, generate_layout_pdf
from pyboxbuilder.packing.guillotine import Item, pack_guillotine
from pyboxbuilder.packing.layout import Placement, _expand_in_place
from pyboxbuilder.packing.spacer import generate_spacer_placements, generate_spacer_voids
from pyboxbuilder.project.manifest import ProjectManifest


def _placement_overlaps(placements: list[Placement]) -> list[tuple[str, str]]:
    hits: list[tuple[str, str]] = []
    for i, a in enumerate(placements):
        ax, ay, az = a.position
        aw, al, ah = a.size
        for b in placements[i + 1 :]:
            bx, by, bz = b.position
            bw, bl, bh = b.size
            if (
                ax < bx + bw - 1e-5
                and ax + aw > bx + 1e-5
                and ay < by + bl - 1e-5
                and ay + al > by + 1e-5
                and az < bz + bh - 1e-5
                and az + ah > bz + 1e-5
            ):
                hits.append((a.label, b.label))
    return hits


class TestBoxTypeEnvelopesAndFactories(unittest.TestCase):
    """Phase 1.1 & 1.2: BoxType interior/outer envelopes and high-level factories."""

    def test_slipover_interior_preserves_full_wall_thickness(self) -> None:
        manifest = ProjectManifest(name="SlipTest", wall_thickness=2.0)
        p = Project("SlipTest")
        b = p.box(BoxType.SLIPOVER, "Slip", size=(60.0, 80.0, 30.0))
        spec = build_spec(manifest, b, (60.0, 80.0, 30.0))
        interior = SlipoverBox().interior(spec)

        expected_inset = spec.wall_thickness * SLIPOVER_SLEEVE_WALL_SHARE + spec.size_spacing
        self.assertAlmostEqual(interior.origin_x, expected_inset + spec.wall_thickness)
        self.assertAlmostEqual(interior.origin_y, expected_inset + spec.wall_thickness)
        self.assertAlmostEqual(
            interior.width, 60.0 - 2.0 * (expected_inset + spec.wall_thickness)
        )
        self.assertEqual(interior.wall_thickness, spec.wall_thickness)

    def test_unsized_special_box_types_autosize_and_build(self) -> None:
        for btype in (
            BoxType.SLEEVE_DRAWER,
            BoxType.CLAMSHELL,
            BoxType.NO_LID,
            BoxType.SLIPOVER,
            BoxType.INSET_HINGE,
        ):
            with self.subTest(box_type=btype):
                p = Project("AutoType", game_box_size=(220.0, 220.0, 80.0), generate_spacers=False)
                b = p.box(btype, f"Box_{btype.name}")
                b.compartment("C1", size=(40.0, 55.0), depth=18.0, no_rotate=True)
                build = p.build()
                self.assertTrue(len(build.pieces) >= 1)

    def test_high_level_factories_token_tray_card_box_hex_tile_box(self) -> None:
        p = Project("FactorySuite", game_box_size=(260.0, 260.0, 80.0), generate_spacers=False)
        p.token_tray("Tokens2x3", size=(120.0, 90.0, 25.0), rows=2, cols=3)
        p.card_box("TarotCards", card_size=(70.0, 120.0), count=60)
        p.hex_tile_box("MapHexes", tile_width=45.0, count=12, tile_thickness=2.2)

        build = p.build()
        by_label = {pc.label: pc for pc in build.pieces if pc.kind == "body"}
        self.assertIn("Tokens2x3", by_label)
        self.assertIn("TarotCards", by_label)
        self.assertIn("MapHexes", by_label)
        # Hex tile depth derived from 12 * 2.2 = 26.4mm -> box height > 28mm
        self.assertGreater(by_label["MapHexes"].size[2], 28.0)


class TestCompartmentLayoutAndElements(unittest.TestCase):
    """Phase 1.2, 2.2 & 3.3: Ratio stacks, 2D MaxRects, growable slack & element packing."""

    def test_length_ratio_only_uses_full_interior_width(self) -> None:
        p = Project("LengthStack")
        b = p.box(BoxType.CAP, "Tray", size=(100.0, 120.0, 30.0))
        b.compartment("Front", length_ratio=0.4)
        b.compartment("Back", length_ratio=0.6)

        p.build()
        resolved = p._pipeline._resolve_box(p._manifest, b)
        assert resolved.compartments is not None
        pls = {pl.label: pl for pl in resolved.compartments.placements}
        # Interior width = 100 - 2*2 = 96; usable width = 96 - 2*2 = 92
        self.assertAlmostEqual(pls["Front"].size[0], 92.0, places=3)
        self.assertAlmostEqual(pls["Back"].size[0], 92.0, places=3)
        self.assertLess(pls["Front"].position[1], pls["Back"].position[1])

    def test_2d_maxrects_packs_around_manual_obstacle_and_l_space(self) -> None:
        interior = Interior(width=100.0, length=100.0, height=30.0, origin_x=2.0, origin_y=2.0)
        # Manual compartment pinned in the center; 4 auto compartments pack around it
        comps = [
            ("Pinned", 30.0, 30.0, 20.0, None, (35.0, 35.0), ()),
            ("A", 28.0, 90.0, 20.0, None, None, ()),
            ("B", 28.0, 90.0, 20.0, None, None, ()),
            ("C", 28.0, 28.0, 20.0, None, None, ()),
            ("D", 28.0, 28.0, 20.0, None, None, ()),
        ]
        res = layout_compartments(interior, comps, no_rotate_labels={"A", "B"})
        self.assertFalse(res.overflow)
        self.assertEqual(len(res.placements), 5)

        # Verify zero pairwise overlap (including 2mm wall spacing)
        pts = res.placements
        for i in range(len(pts)):
            for j in range(i + 1, len(pts)):
                ax, ay = pts[i].position
                aw, al = pts[i].size
                bx, by = pts[j].position
                bw, bl = pts[j].size
                sep = (
                    ax + aw <= bx + 1e-5
                    or bx + bw <= ax + 1e-5
                    or ay + al <= by + 1e-5
                    or by + bl <= ay + 1e-5
                )
                self.assertTrue(sep, f"Overlap between {pts[i].label} and {pts[j].label}")

    def test_growable_compartment_expands_into_row_slack(self) -> None:
        p = Project("GrowRow")
        b = p.box(BoxType.CAP, "RowBox", size=(120.0, 60.0, 25.0))
        b.compartment("Fixed", size=(30.0, 48.0), no_rotate=True, growable=False)
        b.compartment("Flex", size=(30.0, 48.0), no_rotate=True, growable=True)

        p.build()
        resolved = p._pipeline._resolve_box(p._manifest, b)
        assert resolved.compartments is not None
        pls = {pl.label: pl for pl in resolved.compartments.placements}
        self.assertAlmostEqual(pls["Fixed"].size[0], 30.0, places=3)
        # Interior width = 116; 3 gutters of 2mm = 6mm -> total item width = 110 -> Flex = 80mm
        self.assertAlmostEqual(pls["Flex"].size[0], 80.0, places=3)

    def test_elements_negative_offset_footprint_and_pack_elements(self) -> None:
        shifted = (
            CompartmentElement(ElementShape.CIRCLE, size=(20.0, 20.0), offset=(-5.0, -5.0)),
            CompartmentElement(ElementShape.CIRCLE, size=(20.0, 20.0), offset=(20.0, 15.0)),
        )
        fw, fl = elements_footprint(shifted, margin=2.0)
        # Span X: -5..40 -> 45 + margin(2) = 47; Span Y: -5..35 -> 40 + margin(2) = 42
        self.assertAlmostEqual(fw, 47.0)
        self.assertAlmostEqual(fl, 42.0)

        loose = [
            CompartmentElement(ElementShape.RECT, label="R1", size=(30.0, 20.0)),
            CompartmentElement(ElementShape.CIRCLE, label="C1", size=(24.0, 24.0)),
            CompartmentElement(ElementShape.HEXAGON, label="H1", size=(24.0, 24.0)),
            CompartmentElement(
                ElementShape.ROUNDED_RECT,
                label="RR",
                size=(26.0, 16.0),
                corner_radius=5.0,
                rotation=45.0,
            ),
        ]
        packed = pack_elements(loose, spacing=3.0)
        self.assertEqual(len(packed), 4)
        self.assertEqual(elements_overlap(packed), [])

    def test_layout_compartments_centers_and_distributes_non_growable_slots(self) -> None:
        interior = Interior(width=120.0, length=100.0, height=30.0, origin_x=2.0, origin_y=2.0)
        comps = [
            ("A", 30.0, 30.0, 20.0),
            ("B", 30.0, 30.0, 20.0),
            ("C", 30.0, 30.0, 20.0),
        ]
        res = layout_compartments(interior, comps, no_rotate_labels={"A", "B", "C"})
        self.assertFalse(res.overflow)
        by_lbl = {p.label: p for p in res.placements}
        # All 3 fit in 1 row of width 90 -> slack 30 -> 7.5mm equal left/inner/right X gaps
        for idx, lbl in enumerate(("A", "B", "C")):
            self.assertAlmostEqual(by_lbl[lbl].position[0], 2.0 + 7.5 + idx * 37.5, places=3)
            # Vertically centered inside 100mm -> (100 - 30)/2 = 35mm
            self.assertAlmostEqual(by_lbl[lbl].position[1], 2.0 + 35.0, places=3)


class TestGuillotine3DAndProjectPacking(unittest.TestCase):
    """Phase 1.3, 2.1 & 3.1: 3D Guillotine v2, obstacles, protrusions, Pareto sizing & support."""

    def test_exact_fractional_third_height_splits(self) -> None:
        h = 70.0
        items = [
            Item(f"B{i}", (90.0, 90.0, h / 3.0))
            for i in range(3)
        ]
        res = pack_guillotine((90.0, 90.0, h), items)
        self.assertIsNotNone(res)
        assert res is not None
        self.assertEqual(len(res), 3)

    def test_slab_layer_bridge_and_stack_order_chain(self) -> None:
        p = Project("StackChain", game_box_size=(105.0, 105.0, 60.0), generate_spacers=False)
        p.box(BoxType.NO_LID, "Bottom", size=(50.0, 100.0, 20.0), stackable=StackableMode.INSIDE)
        p.box(BoxType.NO_LID, "Middle", size=(50.0, 100.0, 20.0), stackable=StackableMode.INSIDE)
        p.box(BoxType.SLIDING, "Top", size=(50.0, 100.0, 20.0), stackable=StackableMode.INSIDE)
        p.box(BoxType.CAP, "SideTower", size=(50.0, 100.0, 60.0))
        p.stack_order("Bottom", "Middle", "Top")

        build = p.build()
        assert build.packing is not None
        pos = {pl.label: pl.position for pl in build.packing.placements}
        self.assertAlmostEqual(pos["Bottom"][2], 0.0)
        self.assertAlmostEqual(pos["Middle"][2], 20.0)
        self.assertAlmostEqual(pos["Top"][2], 40.0)
        self.assertEqual(pos["Bottom"][:2], pos["Middle"][:2])
        self.assertEqual(pos["Middle"][:2], pos["Top"][:2])

    def test_mixed_manual_obstacles_and_auto_boxes_do_not_collide(self) -> None:
        p = Project("MixedPinned", game_box_size=(200.0, 200.0, 50.0), generate_spacers=False)
        p.box(BoxType.CAP, "CenterPin", size=(80.0, 80.0, 50.0), position=(60.0, 60.0, 0.0))
        p.box(BoxType.CAP, "Auto1", size=(55.0, 180.0, 50.0))
        p.box(BoxType.CAP, "Auto2", size=(55.0, 180.0, 50.0))
        p.box(BoxType.CAP, "Auto3", size=(75.0, 55.0, 50.0))

        build = p.build()
        assert build.packing is not None
        self.assertEqual(_placement_overlaps(build.packing.placements), [])
        pin = next(pl for pl in build.packing.placements if pl.label == "CenterPin")
        self.assertEqual(pin.position, (60.0, 60.0, 0.0))

    def test_pareto_candidate_sizing_picks_fitting_aspect_ratio(self) -> None:
        # Container has a narrow ~52x197 strip left alongside a 145x194 block.
        # A 4-compartment unsized box arranged 2x2 (~82.5x82.5) CANNOT fit, whereas
        # its 1x4 Pareto candidate (~44.5x158.5) fits cleanly!
        p = Project("ParetoFit", game_box_size=(200.0, 200.0, 40.0), generate_spacers=False)
        p.box(BoxType.CAP, "BigBlock", size=(145.0, 194.0, 40.0))
        flex = p.box(BoxType.CAP, "FlexTray")
        for i in range(4):
            flex.compartment(f"W{i}", size=(36.0, 36.0), depth=25.0)

        cands = candidate_box_sizes(
            [(f"W{i}", 36.0, 36.0, 25.0) for i in range(4)],
            wall_thickness=2.0,
        )
        self.assertGreaterEqual(len(cands), 2)

        build = p.build()
        assert build.packing is not None
        self.assertEqual(_placement_overlaps(build.packing.placements), [])

    def test_exterior_protrusions_offset_drawer_and_dispenser(self) -> None:
        p = Project("Protrusions", game_box_size=(180.0, 150.0, 60.0), generate_spacers=False)
        p.box(
            BoxType.SLEEVE_DRAWER,
            "Drawer",
            size=(70.0, 90.0, 40.0),
            drawer_pull_lip=8.0,
        )
        p.box(
            BoxType.DISPENSER,
            "Tower",
            size=(70.0, 90.0, 55.0),
            dispenser_mode=DispenserExtractionMode.TRAY,
            tray_depth=18.0,
        )
        build = p.build()
        assert build.packing is not None
        by_lbl = {pl.label: pl for pl in build.packing.placements}
        # Unrotated boxes protrude in -Y, so position[1] >= protrusion depth
        for lbl, min_clear in (("Drawer", 8.0), ("Tower", 18.0)):
            pl = by_lbl[lbl]
            if not pl.rotation:
                self.assertGreaterEqual(pl.position[1], min_clear - 1e-6)
            else:
                self.assertGreaterEqual(pl.position[0], min_clear - 1e-6)

    def test_expand_in_place_clamps_z_overhang_to_supported_base(self) -> None:
        placements = [
            Placement(label="BaseSupport", position=(0.0, 0.0, 0.0), size=(120.0, 100.0, 25.0)),
            Placement(label="UpperGrow", position=(0.0, 0.0, 25.0), size=(80.0, 92.0, 25.0)),
        ]
        boxes = [
            {"label": "BaseSupport", "expandable": False},
            {"label": "UpperGrow", "expandable": True, "expandable_width": True, "expandable_length": True},
        ]
        _expand_in_place(placements, (200.0, 100.0, 50.0), boxes, gap_threshold=10.0)
        upper = next(pl for pl in placements if pl.label == "UpperGrow")
        # Must stop at BaseSupport's X=120 edge (NOT overhang into empty X=120..200 air!)
        self.assertAlmostEqual(upper.size[0], 120.0)
        # Y gap is 8mm (<= 10mm threshold) and BaseSupport covers Y=0..100, so Y grows to 100!
        self.assertAlmostEqual(upper.size[1], 100.0)

    def test_rotated_packed_box_preserves_unrotated_no_rotate_compartment(self) -> None:
        # Container is 130 wide x 85 long, while card compartment is 66x105 no_rotate=True:
        # the box itself must rotate 90 deg in the game box while keeping local final_size ~(75, 114)!
        p = Project("RotCard", game_box_size=(130.0, 85.0, 40.0), generate_spacers=False)
        p.card_box("Deck", card_size=(66.0, 105.0), count=50)

        build = p.build()
        assert build.packing is not None
        pl = build.packing.placements[0]
        self.assertTrue(pl.rotation)
        deck_builder = p._manifest.boxes[0]
        assert deck_builder.final_size is not None
        # Local builder width < length (unrotated), while packed container footprint is rotated!
        self.assertLess(deck_builder.final_size[0], deck_builder.final_size[1])
        self.assertAlmostEqual(pl.size[0], deck_builder.final_size[1], places=3)


class TestSpacersPolygonGridAndPdf(unittest.TestCase):
    """Phase 1.3, 2.3 & 3.2-3.3: Donut spacer hole splitting, Z support, polygon_grid & PDF."""

    def test_donut_ring_void_splits_without_colliding_with_centered_box(self) -> None:
        container = (200.0, 200.0, 40.0)
        center = Placement(label="CenterBox", position=(60.0, 60.0, 0.0), size=(80.0, 80.0, 40.0))
        spacers = generate_spacer_placements(container, [center], min_dim=15.0, clearance=1.0)
        self.assertGreaterEqual(len(spacers), 2)

        # Verify no spacer sub-point ever enters CenterBox's [60, 140] x [60, 140] footprint!
        for sp in spacers:
            sx, sy, _sz = sp.position
            sw, sl, _sh = sp.size
            if sp.path is None:
                overlaps_center = (
                    sx < 140.0 - 1e-4
                    and sx + sw > 60.0 + 1e-4
                    and sy < 140.0 - 1e-4
                    and sy + sl > 60.0 + 1e-4
                )
                self.assertFalse(overlaps_center, f"Cuboid spacer {sp} overlaps CenterBox!")
            else:
                from pyboxbuilder.export.layout_pdf import _point_in_rectilinear_poly

                # Center of CenterBox (100, 100) in local coords (100 - sx, 100 - sy) MUST be outside!
                self.assertFalse(
                    _point_in_rectilinear_poly(100.0 - sx, 100.0 - sy, list(sp.path)),
                    "Polygon spacer covered the centered box!",
                )

    def test_compute_voids_filters_unsupported_midair_voids(self) -> None:
        placed = [
            Placement(label="Tall", position=(0.0, 0.0, 0.0), size=(100.0, 100.0, 50.0)),
            # Tiny 10x10 pillar at (100, 0, 0) height 20 leaves elevated z=20..50 unsupported if floor sliver dropped
            Placement(label="Pillar", position=(100.0, 0.0, 0.0), size=(10.0, 100.0, 20.0)),
        ]
        voids = generate_spacer_voids((120.0, 100.0, 50.0), placed, min_dim=15.0)
        # X=110..120 floor sliver is 10mm wide (< min_dim=15mm) so it is dropped;
        # the 20mm upper void across X=100..120 at Z=20..50 has only 50% support and MUST be filtered!
        for v in voids:
            self.assertLess(v.position[2], 0.5, f"Unsupported elevated spacer leaked: {v}")

    def test_polygon_grid_honeycomb_saves_space_vs_orthogonal_columns(self) -> None:
        p_hex = Project("HexPods", game_box_size=(220.0, 200.0, 40.0), generate_spacers=False)
        for i in range(4):
            p_hex.box(
                BoxType.CAP,
                f"Pod{i}",
                size=(69.3, 60.0, 30.0),
                polygon_sides=6,
                polygon_apothem=30.0,
            )
        p_hex.arrange(
            polygon_grid("Pod0", "Pod1", "Pod2", "Pod3", cols=2, sides=6, apothem=30.0, gap=2.0)
        )
        build = p_hex.build()
        pos = {pc.label: pc.position for pc in build.pieces if pc.kind == "body"}
        # Row 1 (Pod2/Pod3) is staggered in +X and nested tighter in +Y than 2*apothem + gap = 62mm
        self.assertGreater(pos["Pod2"][0], pos["Pod0"][0])

        # Also verify nesting inside columns(...)
        p_nested = Project("NestedHex", game_box_size=(280.0, 200.0, 40.0), generate_spacers=False)
        for i in range(3):
            p_nested.box(
                BoxType.CAP,
                f"H{i}",
                size=(57.8, 50.0, 25.0),
                polygon_sides=6,
                polygon_apothem=25.0,
            )
        p_nested.box(BoxType.CAP, "Side", size=(50.0, 120.0, 25.0), lid=LidBuilder(text="SIDE"))
        p_nested.arrange(
            columns(
                polygon_grid("H0", "H1", "H2", cols=2, sides=6, apothem=25.0, gap=2.0),
                "Side",
                gap=3.0,
            )
        )
        b2 = p_nested.build()
        self.assertEqual(len([pc for pc in b2.pieces if pc.kind == "body"]), 4)

    def test_layout_pdf_board_on_bottom_and_polygon_spacers(self) -> None:
        p = Project(
            "PdfBoardBottom",
            game_box_size=(180.0, 180.0, 70.0),
            board_thickness=20.0,
            board_on_bottom=True,
            generate_spacers=True,
        )
        b1 = p.box(BoxType.SLIPOVER, "SlipCards", size=(80.0, 100.0, 45.0), position=(50.0, 40.0, 20.0))
        b1.compartment("Deck", length_ratio=0.5)
        b1.compartment("Discard", length_ratio=0.5)

        build = p.build()
        assert build.packing is not None
        pages = _compute_layer_pages(build.packing)
        self.assertGreaterEqual(len(pages), 1)
        self.assertEqual(pages[0].name, "Base Layer")
        self.assertTrue(all(pl.position[2] >= 20.0 - 1e-6 for pl in pages[0].active_placements))

        with tempfile.TemporaryDirectory() as tmp:
            pdf_out = Path(tmp) / "layout.pdf"
            res = generate_layout_pdf(
                build.packing,
                pdf_out,
                p.name,
                (180.0, 180.0, 70.0),
                box_builders=p._manifest.boxes,
                manifest=p._manifest,
            )
            self.assertIsNotNone(res)
            self.assertTrue(pdf_out.exists())
            self.assertTrue(pdf_out.read_bytes().startswith(b"%PDF-"))


if __name__ == "__main__":
    unittest.main()
