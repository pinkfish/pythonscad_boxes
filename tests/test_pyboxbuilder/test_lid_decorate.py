# SPDX-License-Identifier: Apache-2.0
"""Tests for applying a LidBuilder to lid geometry (T161 / US9)."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mesh import volume  # the shared measurer; see tests/mesh.py

from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
from pyboxbuilder.box.spec import BoxSpec
from pyboxbuilder.enums import BoxType, LabelMode, PatternType
from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
from pyboxbuilder.lid.decorate import decorate_lid
from pyboxbuilder.lid.label import build_label, text_height_for

SPEC = BoxSpec(width=100.0, length=70.0, height=30.0,
    wall_thickness=2.0, floor_thickness=2.0, lid_thickness=2.0)


def bare_lid():
    return BOX_IMPL_REGISTRY[BoxType.SLIDING]().build_lid(SPEC)


def _bounds_cs(solid):
    b = solid.bounds()
    return (b.center, b.size) if hasattr(b, "center") else b




class LabelSizingTests(unittest.TestCase):
    def test_text_fills_the_lid_minus_its_margin(self) -> None:
        """SC-014 — a label on a 100x70 lid is set well above the 4mm floor."""
        height = text_height_for(100.0, 70.0, "Cards", border_margin_mm=5.0)
        self.assertGreaterEqual(height, 4.0)
        self.assertLessEqual(height, 60.0 * 0.9)

    def test_a_long_string_is_set_smaller(self) -> None:
        short = text_height_for(100.0, 70.0, "Cat")
        long = text_height_for(100.0, 70.0, "Animal Cards Box")
        self.assertGreater(short, long)

    def test_an_illegible_label_is_skipped(self) -> None:
        """SC-015 — a single letter on a 30x20 lid produces no geometry."""
        self.assertIsNone(build_label(30.0, 20.0, 2.0, "A" * 20))

    def test_no_text_produces_no_label(self) -> None:
        self.assertIsNone(build_label(100.0, 70.0, 2.0, ""))

    def test_frameless_is_text_alone(self) -> None:
        label = build_label(100.0, 70.0, 2.0, "Cards", label_mode=LabelMode.FRAMELESS)
        assert label is not None
        self.assertIsNone(label.backing)

    def test_framed_adds_a_backing_that_hugs_the_text(self) -> None:
        """A plate the size of the whole label area would cover the pattern."""
        label = build_label(100.0, 70.0, 2.0, "Cards", label_mode=LabelMode.FRAMED)
        assert label is not None
        self.assertIsNotNone(label.backing)

        (_, _, _), (text_w, text_l, _) = _bounds_cs(label.text)
        (_, _, _), (back_w, back_l, _) = _bounds_cs(label.backing)
        self.assertGreaterEqual(back_w, text_w)
        self.assertGreaterEqual(back_l, text_l)
        # "Cards" fills the width exactly, so only the length shows the hug.
        self.assertLessEqual(back_w, 90.0, "backing must stay inside the margin")
        self.assertLess(back_l, 60.0, "backing should not fill the label area")

    def test_the_text_never_runs_past_the_margin(self) -> None:
        """Sizing is measured, not guessed — the guess put 102mm of text on a
        100mm lid."""
        for text in ("Cards", "A", "Animal Cards", "Wood"):
            label = build_label(100.0, 70.0, 2.0, text, label_mode=LabelMode.FRAMELESS)
            assert label is not None, text
            (cx, cy, _), (w, l, _) = _bounds_cs(label.text)
            self.assertLessEqual(round(w, 3), 90.0, f"{text} is too wide")
            self.assertLessEqual(round(l, 3), 60.0, f"{text} is too tall")
            self.assertAlmostEqual(cx, 50.0, places=3, msg=f"{text} off-centre")
            self.assertAlmostEqual(cy, 35.0, places=3, msg=f"{text} off-centre")


class DecorationTests(unittest.TestCase):
    def test_no_builder_leaves_the_lid_alone(self) -> None:
        lid = bare_lid()
        self.assertAlmostEqual(
            volume(decorate_lid(lid, None, 2.0).solid), volume(lid), places=3
        )

    def test_mmu_keeps_the_label_as_a_separate_insert(self) -> None:
        """The text is its own solid so the slicer can give it its own
        material (T068a) — and it is inlaid, so the lid gives up exactly the
        volume the insert fills (FR-022a)."""
        lid = bare_lid()
        decorated = decorate_lid(
            lid, LidBuilder(text="Animals", label_mode=LabelMode.FRAMELESS, pattern=None), 2.0, "mmu"
        )
        self.assertEqual(len(decorated.inserts), 1)
        self.assertGreater(volume(decorated.inserts[0].solid), 0.0)
        self.assertAlmostEqual(
            volume(decorated.solid) + volume(decorated.inserts[0].solid),
            volume(lid), places=3,
            msg="the inlay should fill exactly the recess cut for it",
        )

    def test_framed_mmu_yields_text_and_backing_separately(self) -> None:
        from pybosl2 import Color
        decorated = decorate_lid(
            bare_lid(),
            LidBuilder(text="Animals", label_mode=LabelMode.FRAMED, pattern=None, frame_color=Color("white")),
            2.0, "mmu",
        )
        self.assertEqual(len(decorated.inserts), 2)

    def test_logo_inlay_mmu(self) -> None:
        import pybosl2
        logo_solid = pybosl2.shapes3d.cube([10.0, 10.0, 10.0])
        lid = bare_lid()
        decorated = decorate_lid(
            lid, LidBuilder(logo=logo_solid, pattern=None), 2.0, "mmu"
        )
        self.assertEqual(len(decorated.inserts), 1)
        self.assertGreater(volume(decorated.inserts[0].solid), 0.0)
        self.assertAlmostEqual(
            volume(decorated.solid) + volume(decorated.inserts[0].solid),
            volume(lid), places=3,
        )

    def test_logo_engrave_single(self) -> None:
        import pybosl2
        logo_solid = pybosl2.shapes3d.cube([10.0, 10.0, 10.0])
        lid = bare_lid()
        decorated = decorate_lid(
            lid, LidBuilder(logo=logo_solid), 2.0, "single"
        )
        self.assertEqual(decorated.inserts, [])
        self.assertLess(volume(decorated.solid), volume(lid))

    def test_single_engraves_the_label_into_the_lid(self) -> None:
        """One material, so the text is sunk rather than raised."""
        lid = bare_lid()
        decorated = decorate_lid(
            lid, LidBuilder(text="Animals", label_mode=LabelMode.FRAMELESS),
            2.0, "single",
        )
        self.assertEqual(decorated.inserts, [])
        self.assertLess(volume(decorated.solid), volume(lid))

    def test_single_engraves_the_text_not_the_backing(self) -> None:
        """Sinking the backing plate too would cut a rectangle and lose the
        lettering with it."""
        framed = decorate_lid(
            bare_lid(), LidBuilder(text="Hi", label_mode=LabelMode.FRAMED),
            2.0, "single",
        )
        frameless = decorate_lid(
            bare_lid(), LidBuilder(text="Hi", label_mode=LabelMode.FRAMELESS),
            2.0, "single",
        )
        self.assertAlmostEqual(volume(framed.solid), volume(frameless.solid), places=3)

    def test_a_skipped_label_is_reported(self) -> None:
        decorated = decorate_lid(
            bare_lid(), LidBuilder(text="A" * 60), 2.0, "mmu"
        )
        self.assertTrue(decorated.skipped_label)
        self.assertEqual(decorated.inserts, [])

    def test_a_pattern_cuts_all_the_way_through(self) -> None:
        """A pattern that stops short of the top face leaves a skin and shows
        nothing — the lid must actually lose volume."""
        lid = bare_lid()
        decorated = decorate_lid(
            lid,
            LidBuilder(pattern=PatternBuilder(type=PatternType.HEX, spacing=9.0)),
            2.0, "mmu",
        )
        self.assertLess(volume(decorated.solid), volume(lid) * 0.95)

    def test_a_pattern_stays_clear_of_the_lid_border(self) -> None:
        lid = bare_lid()
        decorated = decorate_lid(
            lid,
            LidBuilder(
                pattern=PatternBuilder(type=PatternType.HEX, spacing=9.0),
                border_margin_mm=8.0,
            ),
            2.0, "mmu",
        )
        (bare_c, bare_s) = _bounds_cs(lid)
        (deco_c, deco_s) = _bounds_cs(decorated.solid)
        # Cutting holes inside the border must not change the lid's outline.
        for got, want in zip(deco_s, bare_s):
            self.assertAlmostEqual(got, want, places=3)

    def test_pattern_and_label_coexist(self) -> None:
        from pybosl2 import Color
        lid = bare_lid()
        decorated = decorate_lid(
            lid,
            LidBuilder(
                text="Animals",
                label_mode=LabelMode.FRAMED,
                pattern=PatternBuilder(type=PatternType.HEX, spacing=9.0),
                frame_color=Color("white"),
            ),
            2.0, "mmu",
        )
        self.assertEqual(len(decorated.inserts), 2)
        self.assertLess(volume(decorated.solid), volume(lid) * 0.95)


class ExportIntegrationTests(unittest.TestCase):
    def test_a_decorated_lid_differs_between_the_two_modes(self) -> None:
        """The mmu lid keeps its face; the single lid has the label sunk in."""
        import zipfile
        from pathlib import Path

        from pyboxbuilder.project import Project

        project = Project("Deco", game_box_size=(200, 150, 60), clearance_slack=0.0)
        project.box(
            BoxType.SLIDING, "Cards", size=(100, 70, 40), expandable=False,
            position=(0.0, 0.0, 0.0),
            lid=LidBuilder(text="Cards", label_mode=LabelMode.FRAMED),
        )
        with tempfile.TemporaryDirectory() as tmp:
            project.export(tmp)
            root = Path(tmp) / "Deco"
            mmu = zipfile.ZipFile(root / "mmu" / "Cards_lid.3mf").read(
                "3D/3dmodel.model"
            )
            single = zipfile.ZipFile(root / "single" / "Cards_lid_single.3mf").read(
                "3D/3dmodel.model"
            )
        self.assertNotEqual(
            mmu.count(b"<vertex "), single.count(b"<vertex "),
            "a decorated lid should not be identical in both colour modes",
        )


if __name__ == "__main__":
    unittest.main()


class InlaidLabelTests(unittest.TestCase):
    """FR-022a: a label is cut into the lid and filled flush, not raised on it."""

    def lid(self):
        from pyboxbuilder.box.shell import block

        return block([90.0, 60.0, 2.0])

    def decorated(self, mode: str = "mmu", **lid_kwargs):
        from pyboxbuilder.lid.builder import LidBuilder
        from pyboxbuilder.lid.decorate import decorate_lid

        kwargs = {"pattern": None}
        kwargs.update(lid_kwargs)
        return decorate_lid(
            self.lid(), LidBuilder(**kwargs).titled("Tokens"), 2.0, mode
        )

    @staticmethod
    def _top(solid) -> float:
        (_, _, cz), (_, _, h) = _bounds_cs(solid)
        return cz + h / 2

    def test_nothing_stands_above_the_lid_face(self) -> None:
        """A raised label is knocked off, stops the lid sitting flush under a
        board, and on a sliding lid fouls the mouth of the channel."""
        plain = self.lid()
        result = self.decorated()
        self.assertAlmostEqual(self._top(result.solid), self._top(plain), places=6)
        for insert in result.inserts:
            self.assertLessEqual(self._top(insert.solid), self._top(plain) + 1e-6)

    def test_each_inlay_is_exactly_the_recess_deep(self) -> None:
        from pyboxbuilder.lid.decorate import INLAY_DEPTH_MM

        for insert in self.decorated().inserts:
            (_, _, _), (_, _, h) = _bounds_cs(insert.solid)
            self.assertAlmostEqual(h, INLAY_DEPTH_MM, places=6)

    def test_the_recess_is_cut_out_of_the_lid(self) -> None:
        """The inlay fills a hole; it does not sit on the surface."""
        result = self.decorated()
        self.assertNotEqual(repr(result.solid), repr(self.lid()))

    def test_a_framed_label_inlays_its_text_and_its_striped_grid(self) -> None:
        from pybosl2 import Color
        from pyboxbuilder.enums import LabelMode

        result = self.decorated(label_mode=LabelMode.FRAMED, frame_color=Color("white"))
        self.assertEqual(len(result.inserts), 2)

    def test_a_frameless_label_inlays_only_its_text(self) -> None:
        from pyboxbuilder.enums import LabelMode

        result = self.decorated(label_mode=LabelMode.FRAMELESS)
        self.assertEqual(len(result.inserts), 1)

    def test_the_plate_between_them_is_never_cut(self) -> None:
        """That is what makes it the box's own material, with no insert of its
        own and no colour to choose (FR-022).

        Measured as material surviving in the label's own area: if the plate
        were recessed too, the top layer there would be empty.
        """
        from pyboxbuilder.enums import LabelMode
        from pyboxbuilder.lid.decorate import INLAY_DEPTH_MM
        from pyboxbuilder.lid.label import build_label

        label = build_label(90.0, 60.0, 0.0, "Tokens", label_mode=LabelMode.FRAMED)
        assert label is not None and label.plate is not None
        (px, py, _), (pw, pl, _) = _bounds_cs(label.plate)

        from pyboxbuilder.box.shell import block

        result = self.decorated(label_mode=LabelMode.FRAMED)
        top_layer = block(
            [pw, pl, INLAY_DEPTH_MM],
            at=(px - pw / 2, py - pl / 2, 2.0 - INLAY_DEPTH_MM),
        )
        self.assertGreater(
            volume(result.solid & top_layer), 0.0,
            "the plate was recessed along with the text and the grid",
        )

    def test_a_single_colour_label_is_still_engraved(self) -> None:
        """No second material to inlay, so depth is all there is (FR-036)."""
        from pyboxbuilder.lid.decorate import ENGRAVE_DEPTH_MM

        result = self.decorated(mode="single")
        self.assertEqual(result.inserts, [])
        cut = self.lid() - result.solid
        (_, _, _), (_, _, h) = _bounds_cs(cut)
        self.assertAlmostEqual(h, ENGRAVE_DEPTH_MM, places=6)


class LabelColorTests(unittest.TestCase):
    """FR-022: legible without setting anything."""

    def test_text_defaults_to_black(self) -> None:
        from pybosl2 import Color

        from pyboxbuilder.lid.color_layers import resolve_colors

        self.assertEqual(
            resolve_colors(Color("darkgreen")).text_color.rgba[:3], (0.0, 0.0, 0.0)
        )

    def test_the_striped_grid_defaults_to_none_as_hole(self) -> None:
        from pybosl2 import Color

        from pyboxbuilder.lid.color_layers import resolve_colors

        self.assertIsNone(resolve_colors(Color("darkgreen")).frame_color)

    def test_the_defaults_do_not_follow_the_body(self) -> None:
        """A hue shifted off the box's colour is no more legible against it."""
        from pybosl2 import Color

        from pyboxbuilder.lid.color_layers import resolve_colors

        for body in ("darkgreen", "white", "crimson"):
            with self.subTest(body=body):
                colors = resolve_colors(Color(body))
                self.assertEqual(colors.text_color.rgba[:3], (0.0, 0.0, 0.0))

    def test_an_explicit_colour_still_wins(self) -> None:
        from pybosl2 import Color

        from pyboxbuilder.lid.color_layers import resolve_colors

        colors = resolve_colors(Color("darkgreen"), text_color=Color("gold"))
        self.assertNotEqual(colors.text_color.rgba[:3], (0.0, 0.0, 0.0))


class InsertColourTests(unittest.TestCase):
    """An insert must be able to say what it prints in (FR-022).

    A pybosl2 solid has no readable colour — `.color` is the *method* that sets
    one — so asking a solid what colour it is returns a bound method, and code
    that fell back when it could not read one drew every insert in the lid's
    own colour. The label was there; it was the same colour as the lid.
    """

    def project(self, **lid_kwargs):
        from pyboxbuilder import BoxType, LidBuilder, Project

        p = Project("Ink", game_box_size=(300, 200, 80), generate_spacers=False)
        box = p.box(
            BoxType.SLIDING, "Deck", size=(90, 120, 40), position=(0, 0, 0),
            lid=LidBuilder(**lid_kwargs).titled("Cards"),
        )
        box.compartment("W", size=(70, 100), depth=30)
        return p

    def test_an_insert_carries_the_colour_it_prints_in(self) -> None:
        decorated = decorate_lid(
            bare_lid(), LidBuilder(text="Cards", label_mode=LabelMode.FRAMED),
            2.0, "mmu",
        )
        for insert in decorated.inserts:
            self.assertIsNotNone(insert.color, "an insert with no colour of its own")

    def test_the_preview_draws_the_label_in_its_own_colour(self) -> None:
        """Not in the lid's, which is what made it invisible."""
        from pybosl2 import Color
        pieces = self.project(label_mode=LabelMode.FRAMED, frame_color=Color("white")).preview_pieces(
            show_lids=True, only="Deck"
        )
        lids = [p for p in pieces if p.kind == "lid"]
        self.assertEqual(len(lids), 3, "lid, lettering and striped grid")

        colours = [tuple(round(v, 3) for v in p.color.rgba[:3]) for p in lids]
        self.assertIn((0.0, 0.0, 0.0), colours, "the lettering should be black")
        self.assertEqual(len(set(colours)), 3, "two parts came out the same colour")

    def test_an_explicit_colour_reaches_the_preview(self) -> None:
        from pybosl2 import Color

        pieces = self.project(
            label_mode=LabelMode.FRAMELESS, text_color=Color("red")
        ).preview_pieces(show_lids=True, only="Deck")
        colours = [tuple(round(v, 2) for v in p.color.rgba[:3]) for p in pieces]
        self.assertIn((1.0, 0.0, 0.0), colours)

    def test_the_exported_file_keeps_the_materials_apart(self) -> None:
        """The 3MF must carry one base material per colour, or the slicer has
        nothing to assign."""
        import re
        import zipfile

        from pyboxbuilder.export.exporter import _export_3mf

        decorated = decorate_lid(
            bare_lid(), LidBuilder(text="Cards", label_mode=LabelMode.FRAMED),
            2.0, "mmu",
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lid.3mf"
            if not _export_3mf([decorated.solid, *decorated.solids], path):
                self.skipTest("no geometry backend")
            model = zipfile.ZipFile(path).read("3D/3dmodel.model").decode()

        self.assertGreaterEqual(
            len(re.findall(r"<base ", model)), 3,
            "the lid, the lettering and the grid should be three materials",
        )
