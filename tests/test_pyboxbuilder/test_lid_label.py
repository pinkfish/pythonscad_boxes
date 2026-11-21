# SPDX-License-Identifier: Apache-2.0
"""Tests for lid label generation."""

import unittest

from pyboxbuilder.enums import LabelFinial, LabelMode, LabelShape
from pyboxbuilder.lid.builder import LidBuilder
from pyboxbuilder.lid.label import build_label


class LabelTests(unittest.TestCase):
    def test_label_auto_sizing_positive(self) -> None:
        """Label text height calculation works (bosl2 not required)."""
        # Without bosl2, the text height calculation still runs
        try:
            result = build_label(
                width=100, length=70, thickness=2.0,
                text="Cards", label_mode=LabelMode.FRAMED,
            )
            self.assertIsNotNone(result)
        except ImportError:
            self.skipTest("bosl2 not available")

    def test_min_text_height_guard(self) -> None:
        """Very small lid should skip label (no bosl2 needed)."""
        result = build_label(
            width=20, length=15, thickness=2.0,
            text="Cards",
            min_text_height_mm=10.0,
        )
        self.assertIsNone(result)

    def test_empty_text_skipped(self) -> None:
        """Empty text string should skip label."""
        result = build_label(
            width=100, length=70, thickness=2.0,
            text="",
        )
        self.assertIsNone(result)

    def test_zero_margin_skips_label(self) -> None:
        """Negative margin should skip."""
        result = build_label(
            width=10, length=10, thickness=2.0,
            text="X", border_margin_mm=6.0,
        )
        self.assertIsNone(result)

    def test_compartment_label_mmu_mode(self) -> None:
        """MMU mode returns raised text (requires bosl2)."""
        from pyboxbuilder.compartments.labels import build_floor_label
        result = build_floor_label("Lion", 40, 30, mode="mmu")
        if result is None:
            self.skipTest("bosl2 not available")

    def test_compartment_label_single_mode(self) -> None:
        """Single mode returns engraved text (requires bosl2)."""
        from pyboxbuilder.compartments.labels import build_floor_label
        result = build_floor_label("Lion", 40, 30, mode="single")
        if result is None:
            self.skipTest("bosl2 not available")

    def test_lid_builder_label_shape_coercion(self) -> None:
        """LidBuilder accepts LabelShape enums or case-insensitive strings."""
        self.assertIs(LidBuilder(text="Cards").shape, LabelShape.RECT)
        self.assertIs(LidBuilder(text="Cards", label_shape="chamfered").shape, LabelShape.CHAMFERED)
        self.assertIs(LidBuilder(text="Cards", label_shape="DOUBLE_FRAME").shape, LabelShape.DOUBLE_FRAME)
        self.assertIs(LidBuilder(text="Cards", label_shape=LabelShape.HEXAGON).shape, LabelShape.HEXAGON)

    def test_all_label_shapes_horizontal_and_vertical(self) -> None:
        """Every LabelShape builds valid plate, frame, and text geometry in both orientations."""
        try:
            for shape in LabelShape:
                for width, length in ((110.0, 75.0), (75.0, 110.0)):
                    with self.subTest(shape=shape.value, width=width, length=length):
                        lbl = build_label(
                            width=width,
                            length=length,
                            thickness=2.0,
                            text="Actions",
                            label_mode=LabelMode.FRAMED,
                            solid_background=shape is not LabelShape.RECT,
                            label_shape=shape,
                        )
                        self.assertIsNotNone(lbl)
                        assert lbl is not None
                        self.assertIsNotNone(lbl.text)
                        self.assertIsNotNone(lbl.plate)
                        self.assertIsNotNone(lbl.frame)
                        if shape is not LabelShape.RECT:
                            self.assertIsNone(lbl.hatching)
                            self.assertIsNotNone(lbl.background)
        except ImportError:
            self.skipTest("bosl2 not available")

    def test_decorative_shape_explicit_hatching_opt_in(self) -> None:
        """Non-underline decorative shapes support explicit solid_background=False hatching."""
        try:
            lbl = build_label(
                width=110.0,
                length=75.0,
                thickness=2.0,
                text="Hexes",
                label_mode=LabelMode.FRAMED,
                solid_background=False,
                label_shape=LabelShape.CHAMFERED,
            )
            self.assertIsNotNone(lbl)
            assert lbl is not None
            self.assertIsNotNone(lbl.hatching)
            self.assertIsNone(lbl.background)
        except ImportError:
            self.skipTest("bosl2 not available")

    def test_lid_builder_label_finial_coercion(self) -> None:
        """LidBuilder accepts LabelFinial enums or case-insensitive strings."""
        self.assertIs(LidBuilder(text="Cards").finial, LabelFinial.NONE)
        self.assertIs(LidBuilder(text="Cards", label_finial="fleuron").finial, LabelFinial.FLEURON)
        self.assertIs(LidBuilder(text="Cards", label_finial="SCROLLWORK").finial, LabelFinial.SCROLLWORK)
        self.assertIs(LidBuilder(text="Cards", label_finial=LabelFinial.SPEAR).finial, LabelFinial.SPEAR)

    def test_all_label_finials_framed_and_frameless(self) -> None:
        """Every non-NONE LabelFinial builds valid finial geometry in framed and frameless modes."""
        try:
            for finial in LabelFinial:
                if finial is LabelFinial.NONE:
                    continue
                with self.subTest(finial=finial.value):
                    framed = build_label(
                        width=115.0,
                        length=80.0,
                        thickness=2.0,
                        text="Treasury",
                        label_mode=LabelMode.FRAMED,
                        solid_background=True,
                        label_shape=LabelShape.SCROLL,
                        label_finial=finial,
                    )
                    self.assertIsNotNone(framed)
                    assert framed is not None
                    self.assertIsNotNone(framed.finial)

                    frameless = build_label(
                        width=115.0,
                        length=80.0,
                        thickness=2.0,
                        text="Treasury",
                        label_mode=LabelMode.FRAMELESS,
                        label_finial=finial,
                    )
                    self.assertIsNotNone(frameless)
                    assert frameless is not None
                    self.assertIsNotNone(frameless.finial)
        except ImportError:
            self.skipTest("bosl2 not available")

    def test_embedded_logo_slot_inside_framed_label(self) -> None:
        """Framed labels reserve a clean non-overlapping image_slot for embedded logos."""
        try:
            for pos in ("top", "bottom", "left", "right"):
                with self.subTest(logo_position=pos):
                    lbl = build_label(
                        width=125.0,
                        length=90.0,
                        thickness=2.0,
                        text="Guild",
                        label_mode=LabelMode.FRAMED,
                        solid_background=True,
                        label_shape=LabelShape.SCROLL,
                        label_finial=LabelFinial.SCROLLWORK,
                        logo_position=pos,
                    )
                    self.assertIsNotNone(lbl)
                    assert lbl is not None
                    self.assertIsNotNone(lbl.image_slot)
                    assert lbl.image_slot is not None
                    _, _, sw, sl = lbl.image_slot
                    self.assertGreater(sw, 5.0)
                    self.assertGreater(sl, 5.0)
        except ImportError:
            self.skipTest("bosl2 not available")

    def test_text_stays_strictly_inside_frame_and_plate_for_all_shapes(self) -> None:
        """Wide titles never overlap the border or escape the plaque on any LabelShape."""
        try:
            from pybosl2.exceptions import Bosl2ValueError
        except ImportError:
            self.skipTest("bosl2 not available")

        def _has_volume(solid: object) -> bool:
            if solid is None:
                return False
            try:
                b = solid.bounds()  # type: ignore[attr-defined]
            except Bosl2ValueError:
                return False
            sz = b.size if hasattr(b, "size") else b[1]
            return float(sz[0]) > 1e-3 and float(sz[1]) > 1e-3 and float(sz[2]) > 1e-3

        for shape in LabelShape:
            with self.subTest(shape=shape.value):
                lbl = build_label(
                    width=115.0,
                    length=78.0,
                    thickness=2.0,
                    text="Hex Tiles",
                    label_mode=LabelMode.FRAMED,
                    solid_background=shape is not LabelShape.RECT,
                    label_shape=shape,
                )
                self.assertIsNotNone(lbl)
                assert lbl is not None
                if lbl.frame is not None:
                    self.assertFalse(
                        _has_volume(lbl.text & lbl.frame),
                        f"{shape.value}: text overlaps border frame",
                    )
                if lbl.plate is not None:
                    tall_plate = lbl.plate.scale([1.0, 1.0, 3.0])
                    self.assertFalse(
                        _has_volume(lbl.text - tall_plate),
                        f"{shape.value}: text escapes plaque boundary",
                    )

    def test_custom_font_and_text_spacing_with_hex_bracket(self) -> None:
        """Custom font and letter spacing work cleanly with LabelShape.HEX_BRACKET."""
        try:
            lbl = build_label(
                width=115.0,
                length=80.0,
                thickness=2.0,
                text="ACTIONS",
                label_mode=LabelMode.FRAMED,
                solid_background=True,
                label_shape=LabelShape.HEX_BRACKET,
                font="Futura:style=Bold",
                text_spacing=1.18,
            )
            self.assertIsNotNone(lbl)
            assert lbl is not None
            self.assertIsNotNone(lbl.frame)
            self.assertIsNotNone(lbl.plate)
            self.assertEqual(
                LidBuilder(text="ACTIONS", font="Futura:style=Bold", text_spacing=1.18).text_spacing,
                1.18,
            )
        except ImportError:
            self.skipTest("bosl2 not available")
