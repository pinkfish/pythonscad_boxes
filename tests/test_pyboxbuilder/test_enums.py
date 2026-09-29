# SPDX-License-Identifier: Apache-2.0
"""Tests for pyboxbuilder enums."""

import unittest
from dataclasses import replace

from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.enums import (
    BoxType,
    ColorMode,
    DrawerHandleStyle,
    HingeCatchType,
    InterlockType,
    LabelMode,
    LatchAxis,
    MagnetType,
    PatternType,
    ScoopSide,
    StackableMode,
)
from pyboxbuilder.project import Project


class EnumTests(unittest.TestCase):
    def test_box_type_has_all_members(self) -> None:
        types = {t for t in BoxType}
        self.assertIn(BoxType.SLIDING, types)
        self.assertIn(BoxType.CAP, types)
        self.assertIn(BoxType.HINGE, types)
        self.assertIn(BoxType.FILAMENT_HINGE, types)
        self.assertIn(BoxType.MAGNETIC, types)
        self.assertIn(BoxType.INSET, types)
        self.assertIn(BoxType.SLIDING_CATCH, types)
        self.assertIn(BoxType.SLIPOVER, types)
        self.assertIn(BoxType.SLIPOVER_PATH, types)
        self.assertIn(BoxType.CAP_PATH, types)
        self.assertIn(BoxType.NO_LID, types)
        self.assertIn(BoxType.CARD_LIBRARY, types)

    def test_box_type_values_are_strings(self) -> None:
        for bt in BoxType:
            self.assertIsInstance(bt.value, str)

    def test_label_mode_values(self) -> None:
        self.assertEqual(LabelMode.FRAMED.value, "framed")
        self.assertEqual(LabelMode.FRAMELESS.value, "frameless")

    def test_pattern_type_values(self) -> None:
        self.assertEqual(PatternType.HEX.value, "hex")
        self.assertEqual(PatternType.SQUARE.value, "square")
        self.assertEqual(PatternType.VORONOI.value, "voronoi")

    def test_scoop_side_values(self) -> None:
        self.assertEqual(ScoopSide.FRONT.value, "front")
        self.assertEqual(ScoopSide.BACK.value, "back")
        self.assertEqual(ScoopSide.LEFT.value, "left")
        self.assertEqual(ScoopSide.RIGHT.value, "right")


class StackableAndMagnetEnumTests(unittest.TestCase):
    """T259–T261: type selections are enums, never bare strings."""

    def test_stackable_members(self) -> None:
        self.assertEqual(
            {m.name for m in StackableMode},
            {"INSIDE", "OUTSIDE", "FEET", "INDENTS", "PERIMETER"},
        )
        self.assertEqual(StackableMode.INSIDE.value, "inside")
        self.assertEqual(StackableMode.OUTSIDE.value, "outside")
        self.assertEqual(StackableMode.FEET.value, "feet")
        self.assertEqual(StackableMode.INDENTS.value, "indents")
        self.assertEqual(StackableMode.PERIMETER.value, "perimeter")

    def test_magnet_members(self) -> None:
        self.assertEqual({m.name for m in MagnetType}, {"NONE", "ROUND", "RECT"})

    def test_interlock_members(self) -> None:
        self.assertEqual(
            {m.name for m in InterlockType},
            {"DOVETAIL", "MAGNET", "CLIP", "GRIDFINITY", "NONE"},
        )
        self.assertEqual(InterlockType.DOVETAIL.value, "dovetail")
        self.assertEqual(InterlockType.MAGNET.value, "magnet")
        self.assertEqual(InterlockType.CLIP.value, "clip")
        self.assertEqual(InterlockType.GRIDFINITY.value, "gridfinity")
        self.assertEqual(InterlockType.NONE.value, "none")

    def test_builder_accepts_the_enums(self) -> None:
        p = Project("EnumTest")
        box = p.box(
            BoxType.NO_LID, "Hex", size=(40, 40, 20),
            stackable=StackableMode.OUTSIDE, magnet_type=MagnetType.RECT,
        )
        self.assertIs(box.stackable, StackableMode.OUTSIDE)
        self.assertIs(box.magnet_type, MagnetType.RECT)

    def test_builder_defaults_are_none(self) -> None:
        p = Project("EnumTest")
        box = p.box(BoxType.NO_LID, "Plain", size=(40, 40, 20))
        self.assertIsNone(box.stackable)
        self.assertIsNone(box.magnet_type)

    def test_bare_string_is_rejected(self) -> None:
        p = Project("EnumTest")
        for field, value in (("stackable", "inside"), ("magnet_type", "round")):
            with self.subTest(field=field):
                with self.assertRaises(TypeError) as caught:
                    p.box(BoxType.NO_LID, "Hex", size=(40, 40, 20), **{field: value})
                message = str(caught.exception)
                self.assertIn("Hex", message)      # names the box
                self.assertIn(field, message)      # names the field
                self.assertIn(value, message)      # shows what was passed

    def test_geometry_reads_the_enum(self) -> None:
        """A stackable box with magnets must differ from a plain one."""
        from pyboxbuilder.box.types.no_lid import NoLidBox

        base = BoxSpec(label="Hex", width=40, length=40, height=20,
                    wall_thickness=2.0, floor_thickness=2.0, lid_thickness=0.0)
        plain = repr(NoLidBox().build_body(base))
        featured = repr(NoLidBox().build_body(
            replace(base, stackable=StackableMode.INSIDE, magnet_type=MagnetType.ROUND,
                 magnet_size=(6, 6, 3))
        ))
        self.assertNotEqual(plain, featured)

    def test_magnet_none_means_no_magnets(self) -> None:
        from pyboxbuilder.box.types.no_lid import NoLidBox

        base = BoxSpec(label="Hex", width=40, length=40, height=20,
                    wall_thickness=2.0, floor_thickness=2.0, lid_thickness=0.0)
        plain = repr(NoLidBox().build_body(base))
        explicit_none = repr(NoLidBox().build_body(replace(base, magnet_type=MagnetType.NONE)))
        self.assertEqual(plain, explicit_none)


class CategoricalEnumTests(unittest.TestCase):
    """FR-106: Tests for HingeCatchType, LatchAxis, DrawerHandleStyle, and ColorMode enums."""

    def test_enum_members_and_values(self) -> None:
        self.assertEqual({m.name for m in HingeCatchType}, {"RIDGE", "BUMP", "NONE"})
        self.assertEqual(HingeCatchType.RIDGE.value, "ridge")
        self.assertEqual(HingeCatchType.BUMP.value, "bump")
        self.assertEqual(HingeCatchType.NONE.value, "none")

        self.assertEqual({m.name for m in LatchAxis}, {"X", "Y"})
        self.assertEqual(LatchAxis.X.value, "x")
        self.assertEqual(LatchAxis.Y.value, "y")

        self.assertEqual({m.name for m in DrawerHandleStyle}, {"HANDLE", "LIP", "NONE"})
        self.assertEqual(DrawerHandleStyle.HANDLE.value, "handle")
        self.assertEqual(DrawerHandleStyle.LIP.value, "lip")
        self.assertEqual(DrawerHandleStyle.NONE.value, "none")

        self.assertEqual({m.name for m in ColorMode}, {"MMU", "SINGLE"})
        self.assertEqual(ColorMode.MMU.value, "mmu")
        self.assertEqual(ColorMode.SINGLE.value, "single")

    def test_box_spec_string_coercion(self) -> None:
        spec = BoxSpec(
            width=50,
            length=50,
            height=20,
            hinge_catch_type="bump",
            latch_axis="y",
            drawer_handle_style="lip",
        )
        self.assertIs(spec.hinge_catch_type, HingeCatchType.BUMP)
        self.assertIs(spec.latch_axis, LatchAxis.Y)
        self.assertIs(spec.drawer_handle_style, DrawerHandleStyle.LIP)

    def test_invalid_string_raises_value_error(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            BoxSpec(width=50, length=50, height=20, latch_axis="z")
        self.assertIn("latch_axis", str(ctx.exception))
        self.assertIn("LatchAxis", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            BoxSpec(width=50, length=50, height=20, hinge_catch_type="magnetic")
        self.assertIn("hinge_catch_type", str(ctx.exception))
        self.assertIn("HingeCatchType", str(ctx.exception))

        with self.assertRaises(ValueError) as ctx:
            BoxSpec(width=50, length=50, height=20, drawer_handle_style="knob")
        self.assertIn("drawer_handle_style", str(ctx.exception))
        self.assertIn("DrawerHandleStyle", str(ctx.exception))

    def test_non_string_non_enum_raises_type_error(self) -> None:
        with self.assertRaises(TypeError) as ctx:
            BoxSpec(width=50, length=50, height=20, latch_axis=123)  # type: ignore[arg-type]
        self.assertIn("latch_axis", str(ctx.exception))

        with self.assertRaises(TypeError) as ctx:
            BoxSpec(width=50, length=50, height=20, hinge_catch_type=456)  # type: ignore[arg-type]
        self.assertIn("hinge_catch_type", str(ctx.exception))

    def test_color_mode_in_lid_builder_and_decorate(self) -> None:
        from pybosl2.shapes3d import cube
        from pyboxbuilder.lid.builder import LidBuilder
        from pyboxbuilder.lid.decorate import decorate_lid

        builder = LidBuilder(text="TEST", mmu_label=LidBuilder(text="MMU_LABEL"))
        mmu_resolved = builder.for_mode(ColorMode.MMU)
        self.assertEqual(mmu_resolved.text, "MMU_LABEL")

        single_resolved = builder.for_mode(ColorMode.SINGLE)
        self.assertEqual(single_resolved.text, "TEST")

        lid_solid = cube([40, 40, 2])
        dec_mmu = decorate_lid(lid_solid, builder, lid_thickness=2.0, mode=ColorMode.MMU)
        self.assertIsNotNone(dec_mmu.solid)

        dec_single = decorate_lid(lid_solid, builder, lid_thickness=2.0, mode=ColorMode.SINGLE)
        self.assertIsNotNone(dec_single.solid)

