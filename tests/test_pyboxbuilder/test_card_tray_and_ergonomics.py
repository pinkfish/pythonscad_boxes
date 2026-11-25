# SPDX-License-Identifier: Apache-2.0
"""Tests for BoxType.CARD_TRAY, sleeved-mode toggle, and 3D-printing ergonomics."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from pyboxbuilder import (
    BoxType,
    CardSize,
    CardTrayBoxBuilder,
    Project,
    SleeveType,
    find_sleeve,
    resolve_sleeved_card,
)
from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY, LIDLESS_BOX_TYPES
from pyboxbuilder.box.spec import build_spec
from pyboxbuilder.project.manifest import GameComponent

# ── Milestone 1: Vertical & Angled Card Tray + Divider Slots ─────────────────


class TestCardTrayBox:
    """Geometry, registry, and fit verification for BoxType.CARD_TRAY."""

    def test_card_tray_is_registered_and_lidless(self) -> None:
        assert BoxType.CARD_TRAY in LIDLESS_BOX_TYPES
        assert BoxType.CARD_TRAY in BOX_IMPL_REGISTRY

        p = Project("CardTrayReg")
        b = p.box(
            BoxType.CARD_TRAY,
            "UprightCards",
            size=(72.0, 150.0, 95.0),
            divider_slots=3,
        )
        assert isinstance(b, CardTrayBoxBuilder)
        assert b.divider_slots == 3
        assert b.card_tilt_angle == 0.0

        inv = p.inventory(spacer_count=0)
        assert inv.printed_bodies == 1
        assert inv.printed_lids == 0

    def test_card_tray_upright_and_angled_build_geometry(self) -> None:
        p = Project("CardTrayGeo")
        upright = p.box(
            BoxType.CARD_TRAY,
            "UprightTray",
            size=(72.0, 140.0, 94.0),
            divider_slots=2,
            front_cutout=True,
        )
        angled = p.box(
            BoxType.CARD_TRAY,
            "AngledTray",
            size=(72.0, 160.0, 78.0),
            card_tilt_angle=25.0,
            divider_positions=(45.0, 100.0),
            front_cutout=False,
        )

        impl = BOX_IMPL_REGISTRY[BoxType.CARD_TRAY]()

        spec_u = build_spec(p.manifest, upright, (72.0, 140.0, 94.0))
        interior_u = impl.interior(spec_u)
        assert interior_u.width == pytest.approx(68.0)
        assert interior_u.length == pytest.approx(136.0)
        assert interior_u.height == pytest.approx(92.4)
        assert impl.outer_size_for_interior(spec_u, 68.0, 136.0, 92.4) == pytest.approx(
            (72.5, 140.5, 94.5)
        )
        body_u = impl.build_body(spec_u)
        assert body_u is not None
        assert impl.build_lid(spec_u) is None

        spec_a = build_spec(p.manifest, angled, (72.0, 160.0, 78.0))
        body_a = impl.build_body(spec_a)
        assert body_a is not None
        assert impl.build_lid(spec_a) is None

    def test_vertical_and_angled_card_fit_verification(self) -> None:
        # 100 standard 63.5x88mm cards at 0.5mm = 50mm row; angled at 25 deg:
        # tilted height = 88 * cos(25°) ≈ 79.8mm; row = 50 / cos(25°) + 88 * sin(25°) ≈ 92.4mm
        p = Project("AngledFitOk")
        cards = p.define_cards(
            "Market",
            100,
            size=(63.5, 88.0),
            thickness=0.5,
            orientation="angled",
            tilt_angle=25.0,
        )
        tray = p.box(
            BoxType.CARD_TRAY,
            "MarketTray",
            size=(70.0, 110.0, 84.0),
            card_tilt_angle=25.0,
            divider_slots=2,
        )
        tray.allocate(cards, 100)
        res = p.verify_inventory(strict=True)
        assert res.is_valid

        # Now test a tray that is too short vertically (60mm < 79.8mm)
        p_short = Project("AngledFitTooShort")
        cards_s = p_short.define_cards(
            "Market",
            100,
            size=(63.5, 88.0),
            thickness=0.5,
            orientation="angled",
            tilt_angle=25.0,
        )
        tray_s = p_short.box(
            BoxType.CARD_TRAY,
            "ShortTray",
            size=(70.0, 110.0, 60.0),
            card_tilt_angle=25.0,
        )
        tray_s.allocate(cards_s, 100)
        res_s = p_short.verify_inventory(strict=False)
        assert not res_s.is_valid
        assert len(res_s.fit_warnings) == 1
        assert "angled" in res_s.fit_warnings[0]

    def test_store_vertical_cards_auto_sizes_compartment(self) -> None:
        p = Project("StoreVertical")
        cards = p.define_cards(
            "Actions",
            60,
            size=(63.5, 88.0),
            thickness=0.5,
            orientation="vertical",
        )
        box = p.box(BoxType.CARD_TRAY, "ActionTray", size=(72.0, 60.0, 94.0))
        comp = box.store(cards)
        assert comp.size is not None
        assert comp.size[0] == pytest.approx(64.5)
        assert comp.size[1] == pytest.approx(31.0)
        assert comp.depth == pytest.approx(89.0)
        assert p.verify_inventory(strict=True).is_valid

        # Compartment-level vertical fit failure when box is too shallow
        p_bad = Project("StoreVerticalTooShallow")
        cards_b = p_bad.define_cards(
            "Actions",
            60,
            size=(63.5, 88.0),
            thickness=0.5,
            orientation="vertical",
        )
        box_b = p_bad.box(BoxType.CARD_TRAY, "ShallowTray", size=(72.0, 60.0, 50.0))
        box_b.store(cards_b)
        res_b = p_bad.verify_inventory(strict=False)
        assert not res_b.is_valid
        assert res_b.fit_warnings

    def test_invalid_card_orientation_or_tilt_raises(self) -> None:
        with pytest.raises(ValueError, match="card_orientation"):
            GameComponent("BadOrient", 10, card_orientation="diagonal")
        with pytest.raises(ValueError, match="card_tilt_angle"):
            GameComponent("BadTilt", 10, card_tilt_angle=65.0)


# ── Milestone 2: First-Class Sleeved-Mode Toggle ─────────────────────────────


class TestSleevedModeToggle:
    """Tests for resolve_sleeved_card and Project/define_cards sleeved mode."""

    def test_resolve_sleeved_card_variants(self) -> None:
        # Auto-match standard card (63.5x88)
        sz, thick, matched = resolve_sleeved_card((63.5, 88.0), 0.35)
        assert matched is not None
        assert sz[0] >= 66.0 and sz[1] >= 91.0
        assert thick > 0.35

        # Rotated orientation preserved
        sz_rot, _, _ = resolve_sleeved_card((88.0, 63.5), 0.35)
        assert sz_rot[0] > sz_rot[1]
        assert sz_rot == (sz[1], sz[0])

        # Explicit Sleeve instance
        sk_prem = find_sleeve("Sleeve Kings", "Standard Card Game", "Premium")
        assert sk_prem is not None
        sz_sk, thick_sk, matched_sk = resolve_sleeved_card((63.5, 88.0), 0.35, sleeve=sk_prem)
        assert matched_sk == sk_prem
        assert sz_sk == (66.0, 91.0)
        assert thick_sk == pytest.approx(0.55)

        # SKU lookup
        _sz_sku, thick_sku, matched_sku = resolve_sleeved_card((63.5, 88.0), 0.35, sleeve="SKS-8810")
        assert matched_sku is not None and matched_sku.sku == "SKS-8810"
        assert thick_sku == pytest.approx(0.47)

        # Brand lookup
        _, _, matched_brand = resolve_sleeved_card((63.5, 88.0), 0.35, sleeve="Gamegenic")
        assert matched_brand is not None and matched_brand.brand == "Gamegenic"

        # Grade lookup
        _, _, matched_grade = resolve_sleeved_card((63.5, 88.0), 0.35, sleeve="Premium")
        assert matched_grade is not None and matched_grade.grade == "Premium"

        # Generic size name lookup
        _, _, matched_name = resolve_sleeved_card((44.0, 68.0), 0.35, sleeve="Mini European")
        assert matched_name is not None and matched_name.name == "Mini European"

        # Custom oversized card fallback
        sz_fb, thick_fb, matched_fb = resolve_sleeved_card((120.0, 180.0), 0.4)
        assert matched_fb is None
        assert sz_fb == pytest.approx((122.5, 183.0))
        assert thick_fb == pytest.approx(0.6)

    def test_project_sleeved_mode_and_overrides(self) -> None:
        p = Project("SleevedGame", sleeved=True, sleeve="Gamegenic")
        sleeved_deck = p.define_cards("MainDeck", 50, size=(63.5, 88.0), thickness=0.35)
        unsleeved_deck = p.define_cards("Reference", 4, size=(63.5, 88.0), thickness=0.35, sleeved=False)
        custom_sku_deck = p.define_cards("MiniDeck", 20, size=(41.0, 63.0), thickness=0.35, sleeve="SKS-8801")

        assert sleeved_deck.sleeved is True
        assert "Gamegenic" in sleeved_deck.sleeve_name
        assert sleeved_deck.size == (66.0, 91.0)
        assert sleeved_deck.thickness == pytest.approx(0.55)

        assert unsleeved_deck.sleeved is False
        assert unsleeved_deck.size == (63.5, 88.0)
        assert unsleeved_deck.thickness == pytest.approx(0.35)

        assert custom_sku_deck.sleeved is True
        assert "SKS-8801" in custom_sku_deck.sleeve_name
        assert custom_sku_deck.size == (44.0, 66.0)
        assert custom_sku_deck.thickness == pytest.approx(0.47)


# ── Milestone 3: 3D-Printing & Shelf-Storage Ergonomics ──────────────────────


class TestErgonomicsAndChecks:
    """Tests for base_chamfer propagation, bed_size, vertical storage, and near-square lids."""

    def test_base_chamfer_and_base_rounding_propagate_from_project(self) -> None:
        p = Project("ChamferTest", base_chamfer=0.4, base_rounding=1.0)
        assert p.manifest.base_chamfer == 0.4
        assert p.manifest.base_rounding == 1.0

        b = p.box(BoxType.NO_LID, "Tray", size=(60.0, 60.0, 25.0))
        spec = build_spec(p.manifest, b, (60.0, 60.0, 25.0))
        assert spec.base_chamfer == 0.4
        assert spec.base_rounding == 1.0

        # Ensure shell geometry builds cleanly with project-level base_chamfer
        impl = BOX_IMPL_REGISTRY[BoxType.NO_LID]()
        body = impl.build_body(spec)
        assert body is not None

    def test_print_bed_size_validation(self) -> None:
        p = Project("BedCheck", bed_size=(220.0, 180.0))
        # Fits rotated 90 degrees (175 <= 180 and 215 <= 220)
        p.box(BoxType.NO_LID, "FitsRotated", size=(175.0, 215.0, 30.0))
        assert p.verify_inventory(strict=True).is_valid

        # Exceeds bed in both orientations
        p.box(BoxType.NO_LID, "TooWide", size=(240.0, 100.0, 30.0))
        res = p.verify_inventory(strict=False)
        assert not res.is_valid
        assert len(res.bed_warnings) == 1
        assert "TooWide" in res.bed_warnings[0]
        assert "Print-bed size errors" in res.format_errors()

        with pytest.raises(ValueError, match="Print-bed size errors"):
            p.verify_inventory(strict=True)

    def test_vertical_storage_kallax_spill_check(self) -> None:
        # 1. Uncapped NO_LID tray with loose tokens -> spill warning
        p = Project("KallaxRisk", game_box_size=(200.0, 200.0, 60.0))
        tokens = p.define_piece("Coins", 30, bulk=True)
        tray = p.box(BoxType.NO_LID, "CoinTray", size=(80.0, 80.0, 25.0), position=(0.0, 0.0, 0.0))
        tray.store(tokens)

        # Without check_vertical_storage, passes
        assert p.verify_inventory(strict=True).is_valid

        # With check_vertical_storage=True, flags uncapped tray
        res = p.verify_inventory(strict=False, check_vertical_storage=True)
        assert not res.is_valid
        assert len(res.spill_warnings) == 1
        assert "CoinTray" in res.spill_warnings[0]
        assert "Vertical-storage spill risks" in res.format_errors()

        # 2. Capped by another box stacked directly above -> passes
        p.box(BoxType.SLIDING, "TopBox", size=(80.0, 80.0, 35.0), position=(0.0, 0.0, 25.0))
        assert p.verify_inventory(strict=True, check_vertical_storage=True).is_valid

        # 3. Capped by a GameBoard resting directly above -> passes
        p_gb = Project("KallaxBoardCap", game_box_size=(200.0, 200.0, 60.0))
        tok2 = p_gb.define_piece("Gems", 20, bulk=True)
        tray2 = p_gb.box(BoxType.NO_LID, "GemTray", size=(80.0, 80.0, 40.0), position=(0.0, 0.0, 0.0))
        tray2.store(tok2)
        p_gb.board("MainBoard", size=(190.0, 190.0, 10.0), position=(0.0, 0.0, 41.0))
        assert p_gb.verify_inventory(strict=True, check_vertical_storage=True).is_valid

        # 4. Capped by game box lid / board_thickness via packing object -> passes
        p_ceil = Project("KallaxCeilCap", game_box_size=(200.0, 200.0, 50.0), board_thickness=5.0)
        tok3 = p_ceil.define_piece("Cubes", 15, bulk=True)
        tray3 = p_ceil.box(BoxType.NO_LID, "CubeTray", size=(80.0, 80.0, 44.0))
        tray3.store(tok3)
        fake_packing = SimpleNamespace(
            placements=(SimpleNamespace(label="CubeTray", position=(0.0, 0.0, 0.0), size=(80.0, 80.0, 44.0)),)
        )
        assert p_ceil.verify_inventory(strict=True, check_vertical_storage=True, packing=fake_packing).is_valid

    def test_near_square_cap_and_slipover_advisory(self) -> None:
        p = Project("NearSquareCheck")
        p.box(BoxType.CAP, "NearSquareCap", size=(80.0, 82.0, 30.0))
        p.box(BoxType.SLIPOVER, "NearSquareSlip", size=(70.0, 73.0, 30.0))
        p.box(BoxType.CAP, "ExactSquareCap", size=(80.0, 80.0, 30.0))
        p.box(BoxType.CAP, "RectCap", size=(80.0, 100.0, 30.0))
        p.box(BoxType.SLIDING, "NearSquareSliding", size=(80.0, 82.0, 30.0))

        res = p.verify_inventory(strict=True)
        assert res.is_valid  # Advisory only; does not fail strict inventory
        assert len(res.near_square_warnings) == 2
        joined = " ".join(res.near_square_warnings)
        assert "NearSquareCap" in joined
        assert "NearSquareSlip" in joined
        assert "ExactSquareCap" not in joined
        assert "RectCap" not in joined
        assert "NearSquareSliding" not in joined


# ── Inventory-Free Normal Boxes & Card Boxes ─────────────────────────────────


class TestInventoryFreeWorkflow:
    """Verify normal boxes and card boxes work cleanly without declaring components."""

    def test_simple_normal_and_card_boxes_build_without_inventory(self) -> None:
        p = Project("SimpleStandalone")
        # Plain normal box
        p.box(BoxType.NO_LID, "PlainTray", size=(70.0, 50.0, 22.0))
        # Flat sliding card box with no component declaration
        flat = p.card_box("StandardDeck", card_size=CardSize.STANDARD_GAME, count=54)
        assert flat.box_type is BoxType.SLIDING
        assert flat.compartments[0].count == 54
        # Angled card tray auto-selected by orientation
        angled = p.card_box(
            "AngledMarket",
            card_size=(63.5, 88.0),
            count=80,
            orientation="angled",
            tilt_angle=25.0,
            divider_slots=3,
        )
        assert isinstance(angled, CardTrayBoxBuilder)
        assert angled.card_tilt_angle == 25.0
        assert angled.divider_slots == 3
        # Explicit BoxType.CARD_TRAY infers vertical orientation automatically
        upright = p.card_box(
            "UprightRow",
            card_size=(63.5, 88.0),
            count=50,
            box_type=BoxType.CARD_TRAY,
        )
        assert isinstance(upright, CardTrayBoxBuilder)
        assert upright.compartments[0].depth == pytest.approx(89.0)

        assert p.components == []
        assert p.verify_inventory(strict=True).is_valid
        build = p.build()
        assert len(build.pieces) == 5  # 4 bodies + 1 sliding lid

    def test_sleeved_card_box_and_direct_cards_without_inventory(self) -> None:
        p = Project("SleevedNoInventory", sleeved=True, sleeve="Gamegenic")
        deck = p.card_box("SleevedDeck", card_size=(63.5, 88.0), count=60)
        comp = deck.compartments[0]
        assert comp.size is not None
        assert comp.size[0] >= 67.0 and comp.size[1] >= 92.0

        # Override back to unsleeved on a single deck
        plain = p.card_box("UnsleevedDeck", card_size=(63.5, 88.0), count=60, sleeved=False)
        plain_comp = plain.compartments[0]
        assert plain_comp.size is not None
        assert plain_comp.size[0] < comp.size[0]

        # Direct box.cards() with SleeveType, SKU, and vertical orientation
        b = p.box(BoxType.SLIDING, "DirectCards")
        c_sku = b.cards("SkuDeck", count=40, size=CardSize.MINI_EUROPEAN, sleeve="SKS-8803")
        assert c_sku.size is not None
        assert c_sku.size[0] >= 47.0
        c_legacy = b.cards("LegacyDeck", count=30, size=(63.5, 88.0), sleeve=SleeveType.PREMIUM_100MY)
        expected_legacy = (
            30 * SleeveType.PREMIUM_100MY.card_thickness + SleeveType.PREMIUM_100MY.footprint_margin
        )
        assert c_legacy.depth == pytest.approx(expected_legacy)

        b_vert = p.box(BoxType.CARD_TRAY, "DirectVert")
        c_vert = b_vert.cards("VertDeck", count=50, size=(63.5, 88.0), orientation="vertical")
        assert c_vert.depth == pytest.approx(89.0)

        with pytest.raises(ValueError, match="card orientation"):
            b.cards("Bad", count=10, size=(63.5, 88.0), orientation="sideways")
        with pytest.raises(ValueError, match="tilt_angle"):
            b.cards("BadTilt", count=10, size=(63.5, 88.0), orientation="angled", tilt_angle=70.0)

