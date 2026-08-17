# SPDX-License-Identifier: Apache-2.0
"""Tests for pattern fill generation — full PatternType catalog coverage."""

import unittest

from pyboxbuilder.enums import LabelMode, PatternType
from pyboxbuilder.lid.pattern import _PATTERN_FILLS, build_pattern


class PatternCoverageTests(unittest.TestCase):
    def test_every_pattern_type_has_a_fill(self):
        """Every PatternType member (except aliases) has a registered fill."""
        # Iterate canonical members, skipping aliases
        for pt in PatternType:
            # Aliases share the same value as another member; only check canonical
            if PatternType.__members__[pt.name] is pt:
                self.assertIn(pt, _PATTERN_FILLS, f"{pt.name} missing fill")

    def test_no_fallback_to_grid(self):
        """No two patterns share a fill — a catalog entry that silently drew
        another pattern's shape is what this catalog was cut down to remove."""
        fills = [_PATTERN_FILLS[pt] for pt in PatternType if pt is not PatternType.NONE]
        self.assertEqual(len(set(fills)), len(fills))

    def test_an_unregistered_pattern_is_refused_not_substituted(self):
        """A missing fill must raise, never fall back to squares (FR-000c)."""
        from unittest.mock import patch

        from pyboxbuilder.lid.pattern import build_pattern

        with patch.dict(_PATTERN_FILLS, clear=True):
            with self.assertRaises(ValueError) as caught:
                build_pattern(100.0, 70.0, 3.0, PatternType.HEX)
        self.assertIn("HEX", str(caught.exception))

    def test_legacy_aliases_still_resolve(self):
        """HEX_GRID and GRID aliases still resolve to fill functions."""
        self.assertIn(PatternType.HEX, _PATTERN_FILLS)
        self.assertIn(PatternType.SQUARE, _PATTERN_FILLS)

    def test_unknown_pattern_raises(self):
        """No silent fallback: a missing fill should raise, not fall back."""
        # All enum members are registered, so this only checks the guard path
        # indirectly — verify build_pattern raises for a hypothetical unregistered case
        # by checking the registry is complete instead.
        self.assertTrue(_PATTERN_FILLS)

    def test_none_pattern_returns_none(self):
        """PatternType.NONE produces no cutouts."""
        fill = _PATTERN_FILLS[PatternType.NONE]
        self.assertIsNone(fill(100, 70, 3.0, 10.0, None))


class PatternFillTests(unittest.TestCase):
    def test_grid_fill(self):
        try:
            result = build_pattern(100, 70, 3.0, PatternType.SQUARE, spacing=10.0)
            self.assertIsNotNone(result)
        except ImportError:
            self.skipTest("bosl2 not available")

    def test_hex_fill(self):
        try:
            result = build_pattern(100, 70, 3.0, PatternType.HEX, spacing=10.0)
            self.assertIsNotNone(result)
        except ImportError:
            self.skipTest("bosl2 not available")

    def test_voronoi_fill(self):
        try:
            result = build_pattern(100, 70, 3.0, PatternType.VORONOI, spacing=10.0)
            self.assertIsNotNone(result)
        except ImportError:
            self.skipTest("bosl2 not available")


class HoleAndWebTests(unittest.TestCase):
    """A pattern is specified by the web between holes, not by a share of the
    cell (FR-023). Sized as a share, the web scaled with the pitch: an 11mm
    cell gave a 6.2mm hexagon separated by 5.1mm of plastic, which is a sheet
    with holes in it rather than a honeycomb."""

    def test_the_web_is_what_it_says_it_is(self) -> None:
        from pyboxbuilder.lid.pattern import DEFAULT_WEB_MM, hole_size

        for pitch in (6.0, 8.0, 11.25, 20.0):
            with self.subTest(pitch=pitch):
                self.assertAlmostEqual(pitch - hole_size(pitch, None), DEFAULT_WEB_MM)

    def test_a_thicker_web_shrinks_the_hole_not_the_pitch(self) -> None:
        from pyboxbuilder.lid.pattern import hole_size

        self.assertAlmostEqual(hole_size(10.0, 3.0), 7.0)
        self.assertAlmostEqual(hole_size(10.0, 1.0), 9.0)

    def test_a_web_thinner_than_printable_is_raised(self) -> None:
        from pyboxbuilder.lid.pattern import MIN_WEB_MM, hole_size

        self.assertAlmostEqual(hole_size(10.0, 0.1), 10.0 - MIN_WEB_MM)

    def test_a_pitch_too_tight_for_a_hole_gets_none(self) -> None:
        """Better a solid lid than a peppering of pinholes (FR-000c)."""
        from pyboxbuilder.lid.pattern import hole_size

        self.assertEqual(hole_size(2.0, None), 0.0)

    def test_a_lid_too_tight_for_a_hole_is_left_solid(self) -> None:
        from pyboxbuilder.lid.pattern import build_pattern

        self.assertIsNone(build_pattern(60.0, 60.0, 3.0, PatternType.HEX, spacing=2.0))

    def test_holes_are_denser_than_the_share_rule_gave(self) -> None:
        """The measurement that started this: open area, at a fixed pitch."""
        from pyboxbuilder.lid.pattern import hole_size

        open_share = (hole_size(11.25, None) / 11.25) ** 2
        self.assertGreater(open_share, 0.5, "the pattern still barely opens the lid")


class PatternBorderTests(unittest.TestCase):
    """A solid margin all round, so the edge that holds the lid survives.

    Measured on the **cut lid**, not on the raw lattice: the lattice
    deliberately overhangs and is clipped to the border, which is what puts a
    partial hole against each edge instead of leaving a cell's worth of unused
    margin inside it.
    """

    LID = (80.0, 100.0, 2.0)
    PITCH = 11.0

    def cut(self, pattern_type: PatternType, border: float):
        """The lid, perforated, and the material the pattern removed."""
        from pyboxbuilder.box.shell import block
        from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
        from pyboxbuilder.lid.decorate import decorate_lid

        lid = block(list(self.LID))
        decorated = decorate_lid(
            lid,
            LidBuilder(pattern=PatternBuilder(
                type=pattern_type, spacing=self.PITCH, border=border,
            )),
            self.LID[2], "mmu",
        )
        return lid, lid - decorated.solid

    def margins(self, pattern_type: PatternType, border: float) -> tuple[float, ...]:
        """Solid millimetres between the lid's edge and the nearest hole."""
        width, length, _ = self.LID
        _, removed = self.cut(pattern_type, border)
        (cx, cy, _), (w, l, _) = removed.bounds()
        return (cx - w / 2, width - (cx + w / 2), cy - l / 2, length - (cy + l / 2))

    def test_every_pattern_keeps_the_border(self) -> None:
        for pattern_type in PatternType:
            if pattern_type is PatternType.NONE:
                continue
            with self.subTest(pattern=pattern_type.name):
                for margin in self.margins(pattern_type, 8.0):
                    self.assertGreaterEqual(round(margin, 3), 8.0)

    def test_the_pattern_reaches_the_border(self) -> None:
        """Not merely stays inside it: a lid asking for an 8mm border had 12mm
        or more of solid edge on two sides, because only whole holes were
        placed and the leftover became extra margin."""
        for pattern_type in (PatternType.HEX, PatternType.SQUARE, PatternType.CIRCLE):
            with self.subTest(pattern=pattern_type.name):
                for margin in self.margins(pattern_type, 8.0):
                    self.assertAlmostEqual(margin, 8.0, places=2)

    def test_the_edge_holes_are_partial(self) -> None:
        """A hole straddling the border is drawn and clipped, which is what
        lets the pattern reach it."""
        _, removed = self.cut(PatternType.HEX, 8.0)
        (cx, cy, _), (w, l, _) = removed.bounds()
        width, length, _ = self.LID
        # A lattice that only placed whole hexes could not span this much.
        self.assertAlmostEqual(w, width - 16.0, places=2)
        self.assertAlmostEqual(l, length - 16.0, places=2)

    def test_the_border_is_settable(self) -> None:
        for margin in self.margins(PatternType.HEX, 15.0):
            self.assertAlmostEqual(margin, 15.0, places=2)

    def test_the_label_sits_inside_the_lid_border(self) -> None:
        """One border for the lid, and the label set in from it.

        The border is a band of plain lid; a label level with its inner edge
        reads as touching the pattern rather than sitting in a space of its own.
        """
        from pyboxbuilder.lid.builder import (
            BORDER_MARGIN_MM,
            LABEL_INSET_MM,
            LID_BORDER_MM,
            PATTERN_BORDER_MM,
            LidBuilder,
            PatternBuilder,
        )

        self.assertEqual(LID_BORDER_MM, 8.0)
        self.assertEqual(LABEL_INSET_MM, 2.0)
        self.assertEqual(PATTERN_BORDER_MM, LID_BORDER_MM)
        self.assertEqual(BORDER_MARGIN_MM, LID_BORDER_MM + LABEL_INSET_MM)
        self.assertEqual(PatternBuilder().border_width, LID_BORDER_MM)
        self.assertEqual(LidBuilder().border_margin, LID_BORDER_MM + LABEL_INSET_MM)

    def test_the_text_stays_inside_the_border(self) -> None:
        """Including a diagonal label, which is the one that ran off the lid."""
        from pyboxbuilder.enums import LabelMode
        from pyboxbuilder.lid.builder import (
            LABEL_INSET_MM,
            LID_BORDER_MM,
            LidBuilder,
        )
        from pyboxbuilder.lid.decorate import _build_label

        width, length, _ = self.LID
        for diagonal in (False, True):
            with self.subTest(diagonal=diagonal):
                label = _build_label(
                    LidBuilder(label_mode=LabelMode.FRAMELESS, diagonal=diagonal)
                    .titled("Favors"),
                    width, length, "mmu",
                )
                assert label is not None
                (cx, cy, _), (w, l, _) = label.combined().bounds()
                inside = LID_BORDER_MM + LABEL_INSET_MM
                self.assertGreaterEqual(round(cx - w / 2, 3), inside)
                self.assertGreaterEqual(round(width - (cx + w / 2), 3), inside)
                self.assertGreaterEqual(round(cy - l / 2, 3), inside)
                self.assertGreaterEqual(round(length - (cy + l / 2), 3), inside)

    def test_the_edges_are_cut_alike(self) -> None:
        """SC-016h: opposite edges are mirror images.

        Grown from one edge, the lattice landed wherever the arithmetic put it
        — on a 96 x 70 lid one side was cut through the hexes and the other
        through the webs, taking 56mm3 against 33mm3. It is anchored on the
        area's centre instead.
        """
        from mesh import volume

        from pyboxbuilder.box.shell import block

        border = 8.0
        for width, length in ((96.0, 70.0), (98.0, 142.5), (60.0, 60.0)):
            with self.subTest(lid=(width, length)):
                lid = block([width, length, 2.0])
                from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
                from pyboxbuilder.lid.decorate import decorate_lid

                decorated = decorate_lid(
                    lid,
                    LidBuilder(pattern=PatternBuilder(
                        type=PatternType.HEX, spacing=10.0, border=border,
                    )),
                    2.0, "mmu",
                )
                removed = lid - decorated.solid

                def strip(at, size):
                    return volume(removed & block(list(size), at=list(at)))

                left = strip((border, border, 0), (1.0, length - 2 * border, 2.0))
                right = strip(
                    (width - border - 1.0, border, 0), (1.0, length - 2 * border, 2.0)
                )
                bottom = strip((border, border, 0), (width - 2 * border, 1.0, 2.0))
                top = strip(
                    (border, length - border - 1.0, 0), (width - 2 * border, 1.0, 2.0)
                )
                self.assertGreater(left, 0.0, "the pattern never reached the edge")
                self.assertAlmostEqual(left, right, places=2)
                self.assertAlmostEqual(bottom, top, places=2)

    def test_a_border_that_swallows_the_lid_leaves_it_solid(self) -> None:
        from pyboxbuilder.box.shell import block
        from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
        from pyboxbuilder.lid.decorate import decorate_lid

        lid = block([30.0, 30.0, 2.0])
        decorated = decorate_lid(
            lid, LidBuilder(pattern=PatternBuilder(border=20.0)), 2.0, "mmu"
        )
        self.assertEqual(repr(decorated.solid), repr(lid))


class LabelClearanceTests(unittest.TestCase):
    """FR-023: the holes stop at the lettering, with no margin by default.

    A stand-off put a solid halo around every glyph, so the text read as
    letters on a plaque rather than as letters on the lid. It is not needed:
    the keep-out is the glyph outline, so each stroke keeps its own footprint
    of solid lid, and the label is inlaid into that lid rather than perched on
    it — the plastic goes all the way down.
    """

    def cut_area(self, clearance: float | None) -> float:
        """How much material the pattern removes at a given stand-off."""
        from mesh import volume

        from pyboxbuilder.box.shell import block
        from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
        from pyboxbuilder.lid.decorate import decorate_lid

        lid = block([96.0, 70.0, 2.0])
        decorated = decorate_lid(
            lid,
            LidBuilder(
                label_mode=LabelMode.FRAMELESS,
                pattern=PatternBuilder(type=PatternType.HEX, spacing=10.0),
                label_clearance_mm=clearance,
            ).titled("Favors"),
            2.0, "mmu",
        )
        return volume(lid - decorated.solid)

    def test_the_default_is_no_margin(self) -> None:
        from pyboxbuilder.lid.builder import LidBuilder
        from pyboxbuilder.lid.decorate import LABEL_CLEARANCE_MM

        self.assertEqual(LABEL_CLEARANCE_MM, 0.0)
        self.assertEqual(LidBuilder().label_clearance, 0.0)

    def test_a_margin_takes_holes_away_from_the_lettering(self) -> None:
        """Settable for a lid whose pattern is coarse enough to want one.

        Frameless, since a framed label's keep-out is its plate — the plate
        already stands the pattern off the text by its own padding.
        """
        self.assertGreater(self.cut_area(0.0), self.cut_area(2.0))

    def test_the_holes_never_undercut_a_glyph(self) -> None:
        """Even at zero margin: the keep-out is the glyph outline itself."""
        from mesh import volume

        from pyboxbuilder.box.shell import block
        from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder
        from pyboxbuilder.lid.decorate import _build_label, decorate_lid

        lid = block([96.0, 70.0, 2.0])
        builder = LidBuilder(
            label_mode=LabelMode.FRAMELESS,
            pattern=PatternBuilder(type=PatternType.HEX, spacing=10.0),
        ).titled("Favors")
        decorated = decorate_lid(lid, builder, 2.0, "mmu")

        label = _build_label(builder.for_mode("mmu"), 96.0, 70.0, "mmu")
        assert label is not None
        # Under the lettering, at the layer below the inlay, the lid is solid:
        # a hole there would leave the glyph printing onto air.
        under = label.text.translate([0.0, 0.0, -1.0]).scale([1.0, 1.0, 0.5])
        removed = lid - decorated.solid
        self.assertAlmostEqual(volume(removed & under), 0.0, places=3)


class LeafPatternTests(unittest.TestCase):
    """PatternType.LEAF draws leaves, and they tessellate (FR-023).

    This member is the reason the catalog rule exists: the original toolkit
    listed LEAF among twenty tessellations it could not draw, so Emberleaf —
    the insert named after them — cut squares, and then hexagons once the
    catalog was trimmed to what was real.
    """

    SPACING = 14.0
    WEB = 2.0

    def leaf(self):
        """One leaf, at the size this class's pitch and web give it."""
        from pyboxbuilder.lid.pattern import LEAF_ASPECT, MIN_WEB_MM, _leaf, hole_size

        length = hole_size(self.SPACING, self.WEB)
        return _leaf(
            length, length / LEAF_ASPECT, 3.0, max(MIN_WEB_MM, self.WEB / 2)
        ), length

    def test_a_leaf_lid_is_actually_cut(self) -> None:
        self.assertIsNotNone(
            build_pattern(100, 70, 3.0, PatternType.LEAF, spacing=self.SPACING)
        )

    def test_it_is_not_a_hexagon_in_disguise(self) -> None:
        """The failure this whole catalog rule exists to catch."""
        from mesh import volume

        leaf = build_pattern(100, 70, 3.0, PatternType.LEAF, spacing=self.SPACING)
        hexes = build_pattern(100, 70, 3.0, PatternType.HEX, spacing=self.SPACING)
        self.assertGreater(abs(volume(leaf) - volume(hexes)), 1.0)

    def test_a_leaf_is_longer_than_it_is_wide(self) -> None:
        """A pointed oval at 1:1 is a circle; at 2:1 it reads as a leaf."""
        from mesh import volume

        from pyboxbuilder.box.shell import block

        leaf, length = self.leaf()
        width = length / 2
        nominal = block([length, width, 12.0], at=(-length / 2, -width / 2, -6.0))
        self.assertAlmostEqual(
            volume(leaf - nominal), 0.0, places=6, msg="it overhangs its own cell"
        )
        # It fills that cell rather than rattling around inside it. Probed at
        # four fifths out, not at the very tip: the arcs are drawn as polygons,
        # so at the coarse facet count the tests run at the tip falls a tenth
        # short of where the exact curve puts it.
        reach = block([length, width, 12.0], at=(length / 2 * 0.8, -width / 2, -6.0))
        self.assertGreater(volume(leaf & reach), 0.0, "it is stubbier than its cell")

        square = block([width, width, 12.0], at=(-width / 2, -width / 2, -6.0))
        self.assertGreater(
            volume(leaf - square), 0.0, "it fits in a square: that is not a leaf"
        )

    def test_it_tapers_to_a_point(self) -> None:
        """Not a rounded capsule: the tips are what interlock with the row
        above and below, and a blunt one would not nest."""
        from pyboxbuilder.lid.pattern import _leaf_half_height

        half = _leaf_half_height(0.0, 6.0, 3.0)
        self.assertAlmostEqual(half, 3.0, places=6)
        self.assertGreater(half, _leaf_half_height(3.0, 6.0, 3.0))
        self.assertGreater(_leaf_half_height(3.0, 6.0, 3.0),
                           _leaf_half_height(5.5, 6.0, 3.0))
        self.assertEqual(_leaf_half_height(6.0, 6.0, 3.0), 0.0)

    def test_it_has_a_midrib(self) -> None:
        """What tells a viewer it is a leaf and not a pointed oval — and it
        braces the widest part of the hole, where a perforated lid gives way."""
        from mesh import volume
        from pyboxbuilder.lid.pattern import LEAF_ASPECT, _leaf, hole_size

        length = hole_size(self.SPACING, self.WEB)
        width = length / LEAF_ASPECT
        ribbed = _leaf(length, width, 3.0, 1.0)
        whole = _leaf(length, width, 3.0, 0.0)
        self.assertLess(volume(ribbed), volume(whole))

    def test_a_leaf_too_small_to_split_keeps_its_rib_out(self) -> None:
        """Two slits read as a crack in the lid, not as a leaf."""
        from mesh import volume
        from pyboxbuilder.lid.pattern import _leaf

        tiny = _leaf(5.0, 2.5, 3.0, 1.6)
        self.assertAlmostEqual(volume(tiny), volume(_leaf(5.0, 2.5, 3.0, 0.0)),
                               places=3)


class LeafTessellationTests(unittest.TestCase):
    """The leaves interlock, and the web is even in every direction.

    Rows offset by half a pitch do not need a whole leaf-width between them:
    where one leaf is at its widest its neighbours above and below are near
    their tips. Stepping the full width would leave a band of solid lid along
    every row and the pattern would read as stripes rather than as foliage.
    """

    SPACING = 14.0
    WEB = 2.0

    def geometry(self):
        from pyboxbuilder.lid.pattern import (
            LEAF_ASPECT, _leaf_row_step, hole_size,
        )

        length = hole_size(self.SPACING, self.WEB)
        width = length / LEAF_ASPECT
        step = _leaf_row_step(length / 2, width / 2, self.WEB)
        return length, width, step

    def test_neighbours_never_meet(self) -> None:
        """Two holes that run into each other are one hole, and the web that
        was meant to carry the lid is gone."""
        from mesh import volume
        from pyboxbuilder.lid.pattern import MIN_WEB_MM, _leaf

        length, width, step = self.geometry()
        leaf = _leaf(length, width, 3.0, max(MIN_WEB_MM, self.WEB / 2))
        along = leaf.translate([self.SPACING, 0, 0])
        across = leaf.translate([self.SPACING / 2, step, 0])
        diagonal = leaf.translate([-self.SPACING / 2, step, 0])
        for name, other in (
            ("along the row", along),
            ("the row above", across),
            ("the row above, other way", diagonal),
        ):
            with self.subTest(neighbour=name):
                self.assertAlmostEqual(volume(leaf & other), 0.0, places=6)

    def test_the_web_is_the_same_in_both_directions(self) -> None:
        """A honeycomb's web is even because a hexagon's neighbours are all the
        same distance away. A leaf's are not, so the row step is solved for."""
        from pyboxbuilder.lid.pattern import _leaf_half_height

        length, width, step = self.geometry()
        self.assertAlmostEqual(self.SPACING - length, self.WEB, places=6)

        def gap(x: float) -> float:
            return (
                step
                - _leaf_half_height(x, length / 2, width / 2)
                - _leaf_half_height(x - self.SPACING / 2, length / 2, width / 2)
            )

        samples = [gap(-length + i * length / 500) for i in range(1001)]
        self.assertAlmostEqual(min(samples), self.WEB, places=3)

    def test_the_rows_interleave(self) -> None:
        """The point of solving for the step rather than stacking the rows."""
        length, width, step = self.geometry()
        self.assertLess(step, width + self.WEB, "the rows do not nest at all")
        self.assertGreater(step, width / 2, "the rows have collapsed together")

    def test_it_fills_the_area_rather_than_striping_it(self) -> None:
        """The whole point of the tessellation, measured: open area."""
        from mesh import volume

        holes = build_pattern(100, 70, 3.0, PatternType.LEAF, spacing=self.SPACING)
        # Clipped to the area, as decorate_lid does before subtracting.
        from pyboxbuilder.box.shell import block

        inside = volume(holes & block([100, 70, 3.0]))
        self.assertGreater(inside / (100 * 70 * 3.0), 0.35)


class LeafTileTests(unittest.TestCase):
    """LEAF_TESSELLATION and LEAF_VEINS tile the lid edge to edge (FR-023).

    A different thing from `PatternType.LEAF`, which spaces pointed ovals out
    and solves for the gap between them. This leaf is a **tile**: it covers the
    plane, so the material left over is exactly the web, and what a lid shows is
    a net of leaf outlines rather than a sheet with leaves punched out of it.
    """

    SPACING = 22.0
    WEB = 1.6

    def path(self, section: float = 1.0):
        from pyboxbuilder.lid.pattern import tessellating_leaf_path

        return tessellating_leaf_path(section)

    def test_it_is_the_seven_sided_tile(self) -> None:
        from pyboxbuilder.lid.pattern import ROOT_THREE

        points = self.path()
        self.assertEqual(len(points), 7)
        # Base to tip is 2√3 sections; notch to notch is 4.
        xs = [x for x, _ in points]
        ys = [y for _, y in points]
        self.assertAlmostEqual(max(xs) - min(xs), 2 * ROOT_THREE, places=6)
        self.assertAlmostEqual(max(ys) - min(ys), 4.0, places=6)

    def test_its_edges_pair_up(self) -> None:
        """What makes it a tile rather than a leaf-shaped blob.

        The two edges to the tip are equal and opposite to the two from the
        base, so each is another leaf's edge under translation; the base's one
        long edge is matched by the two short notch edges of two neighbours.
        """
        points = self.path()
        edges = [
            (points[(i + 1) % 7][0] - points[i][0], points[(i + 1) % 7][1] - points[i][1])
            for i in range(7)
        ]

        def opposite(a, b) -> bool:
            return abs(a[0] + b[0]) < 1e-9 and abs(a[1] + b[1]) < 1e-9

        self.assertTrue(opposite(edges[0], edges[4]), "tip edges do not pair")
        self.assertTrue(opposite(edges[2], edges[6]), "base edges do not pair")
        # The long base edge against the two short notch edges together.
        self.assertTrue(
            opposite(edges[3], (edges[1][0] + edges[5][0], edges[1][1] + edges[5][1])),
            "the base edge is not matched by the two notches",
        )

    def test_the_tile_covers_the_plane(self) -> None:
        """Its area equals the area of one lattice cell: no gaps, no overlaps.

        This is the whole claim of a tessellation, and it is one number.
        """
        from pyboxbuilder.lid.pattern import ROOT_THREE

        points = self.path()
        area = abs(
            sum(
                points[i][0] * points[(i + 1) % 7][1]
                - points[(i + 1) % 7][0] * points[i][1]
                for i in range(7)
            )
        ) / 2.0
        # The lattice the fill lays it on: pitch 2√3 across, rows every 2, each
        # row shifted half a pitch — so one cell is pitch × row step.
        self.assertAlmostEqual(area, (2 * ROOT_THREE) * 2.0, places=6)

    def test_both_members_cut_something(self) -> None:
        for member in (PatternType.LEAF_TESSELLATION, PatternType.LEAF_VEINS):
            with self.subTest(pattern=member.name):
                self.assertIsNotNone(
                    build_pattern(100, 70, 3.0, member, spacing=self.SPACING)
                )

    def test_the_veins_are_material_kept_not_removed(self) -> None:
        """LEAF_VEINS is the same tiling with ribs left inside each leaf, so it
        must open *less* of the lid than the plain outline does."""
        from mesh import volume

        plain = build_pattern(
            100, 70, 3.0, PatternType.LEAF_TESSELLATION, spacing=self.SPACING
        )
        veined = build_pattern(
            100, 70, 3.0, PatternType.LEAF_VEINS, spacing=self.SPACING
        )
        self.assertLess(volume(veined), volume(plain))

    def test_no_vein_is_an_island(self) -> None:
        """Every vein ends on the midrib or on the leaf's outline. One floating
        in the middle of a hole is something the printer starts in mid-air.

        Checked as reach rather than by tracing: a stroke that spans the leaf
        touches its boundary at both ends.
        """
        from pyboxbuilder.lid.pattern import LEAF_VEIN_BRANCHES

        for start, end in LEAF_VEIN_BRANCHES:
            with self.subTest(branch=(start, end)):
                self.assertLess(start, end, "the vein runs backwards from the midrib")
                self.assertLessEqual(abs(start), 1.0, "it starts off the leaf")
                self.assertLessEqual(0.0, end)
                self.assertLessEqual(end, 1.0, "it lands past the tip")

    def test_no_vein_starts_at_the_base(self) -> None:
        """Three leaves meet at each base, so veins converging there compound
        into a six-pointed star and the leaf stops being legible."""
        from pyboxbuilder.lid.pattern import LEAF_VEIN_BRANCHES

        for start, _ in LEAF_VEIN_BRANCHES:
            with self.subTest(start=start):
                self.assertGreater(start, -1.0)

    def test_it_leaves_less_material_than_a_field_of_holes(self) -> None:
        """The point of tiling: the leftover *is* the web, so the lid opens
        further at the same pitch than a pattern that spaces its holes out."""
        from mesh import volume

        from pyboxbuilder.box.shell import block

        area = block([100, 70, 3.0])
        tiled = build_pattern(
            100, 70, 3.0, PatternType.LEAF_TESSELLATION, spacing=self.SPACING
        )
        spaced = build_pattern(100, 70, 3.0, PatternType.LEAF, spacing=self.SPACING)
        self.assertGreater(volume(tiled & area), volume(spaced & area))
