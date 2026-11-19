# SPDX-License-Identifier: Apache-2.0
"""Tests for compartment element packing (FR-004a / FR-004b)."""

from __future__ import annotations

import math
import unittest

from pyboxbuilder.compartments.builder import CompartmentBuilder
from pyboxbuilder.compartments.element import (
    CompartmentElement,
    elements_bounding_box,
    elements_footprint,
    elements_overlap,
    grid_pack,
    normalize_elements,
    pack_into_compartment,
)
from pyboxbuilder.enums import ElementShape

SVG = "examples/svg/emberleaf/owl worker.svg"


class ElementValidationTests(unittest.TestCase):
    def test_svg_element_requires_a_file(self) -> None:
        with self.assertRaises(ValueError):
            CompartmentElement(size=(10, 10))

    def test_element_requires_a_size(self) -> None:
        with self.assertRaises(ValueError):
            CompartmentElement(shape=ElementShape.RECT, size=None)

    def test_parametric_element_needs_no_file(self) -> None:
        element = CompartmentElement(shape=ElementShape.CIRCLE, size=(10, 10))
        self.assertEqual(element.footprint, (10.0, 10.0))


class FootprintTests(unittest.TestCase):
    def test_unrotated_footprint_is_the_size(self) -> None:
        element = CompartmentElement(SVG, size=(23.0, 12.0))
        self.assertEqual(element.footprint, (23.0, 12.0))

    def test_ninety_degree_rotation_swaps_axes(self) -> None:
        element = CompartmentElement(SVG, size=(23.0, 12.0), rotation=90.0)
        w, l = element.footprint
        self.assertAlmostEqual(w, 12.0)
        self.assertAlmostEqual(l, 23.0)

    def test_forty_five_degree_rotation_grows_both_axes(self) -> None:
        element = CompartmentElement(SVG, size=(10.0, 10.0), rotation=45.0)
        w, l = element.footprint
        self.assertAlmostEqual(w, 10 * math.sqrt(2), places=5)
        self.assertAlmostEqual(l, 10 * math.sqrt(2), places=5)

    def test_hexagon_measures_across_the_points(self) -> None:
        """size[0] is flat-to-flat, so the other axis is wider by 1/cos(30)."""
        element = CompartmentElement(shape=ElementShape.HEXAGON, size=(38.5, 38.5))
        w, l = element.footprint
        self.assertAlmostEqual(w, 38.5 / math.cos(math.radians(30)), places=5)
        self.assertAlmostEqual(l, 38.5, places=5)

    def test_rotating_a_hexagon_thirty_degrees_swaps_its_axes(self) -> None:
        element = CompartmentElement(
            shape=ElementShape.HEXAGON, size=(38.5, 38.5), rotation=30.0
        )
        w, l = element.footprint
        self.assertAlmostEqual(w, 38.5, places=5)
        self.assertAlmostEqual(l, 38.5 / math.cos(math.radians(30)), places=5)

    def test_rotating_a_circle_changes_nothing(self) -> None:
        element = CompartmentElement(
            shape=ElementShape.CIRCLE, size=(16.5, 16.5), rotation=37.0
        )
        self.assertEqual(element.footprint, (16.5, 16.5))


class PackTests(unittest.TestCase):
    def test_grid_pack_repeats_at_the_given_pitch(self) -> None:
        proto = CompartmentElement(SVG, size=(23.0, 12.0), label="owl")
        pack = grid_pack(proto, 5, origin=(0.5, 2.0), pitch=(0.0, 12.0))

        self.assertEqual(len(pack), 5)
        self.assertEqual([e.offset for e in pack], [
            (0.5, 2.0), (0.5, 14.0), (0.5, 26.0), (0.5, 38.0), (0.5, 50.0),
        ])
        self.assertEqual([e.label for e in pack], [f"owl_{i}" for i in range(5)])

    def test_alternate_rotation_flips_every_other_copy(self) -> None:
        proto = CompartmentElement(SVG, size=(23.0, 14.0))
        pack = grid_pack(proto, 4, pitch=(0.0, 12.0), alternate_rotation=180.0)
        self.assertEqual([e.rotation for e in pack], [0.0, 180.0, 0.0, 180.0])

    def test_footprint_spans_from_the_compartment_corner(self) -> None:
        """The pack's footprint keeps authored offsets rather than shrink-wrapping."""
        pack = (
            CompartmentElement(SVG, offset=(10.0, 5.0), size=(20.0, 10.0)),
            CompartmentElement(SVG, offset=(40.0, 5.0), size=(20.0, 10.0)),
        )
        self.assertEqual(elements_footprint(pack), (60.0, 15.0))

    def test_footprint_adds_the_margin(self) -> None:
        pack = (CompartmentElement(SVG, offset=(0.0, 0.0), size=(20.0, 10.0)),)
        self.assertEqual(elements_footprint(pack, margin=2.5), (22.5, 12.5))

    def test_empty_pack_has_no_footprint(self) -> None:
        self.assertEqual(elements_footprint(()), (0.0, 0.0))
        self.assertEqual(elements_bounding_box(()), (0.0, 0.0, 0.0, 0.0))

    def test_normalize_shrink_wraps_to_the_origin(self) -> None:
        pack = (
            CompartmentElement(SVG, offset=(10.0, 5.0), size=(20.0, 10.0)),
            CompartmentElement(SVG, offset=(40.0, 5.0), size=(20.0, 10.0)),
        )
        normalized = normalize_elements(pack, margin=1.0)
        self.assertEqual(normalized[0].offset, (1.0, 1.0))
        self.assertEqual(elements_footprint(normalized), (51.0, 11.0))

    def test_overlap_reports_intersecting_pairs(self) -> None:
        pack = (
            CompartmentElement(SVG, offset=(0.0, 0.0), size=(20.0, 20.0), label="a"),
            CompartmentElement(SVG, offset=(10.0, 10.0), size=(20.0, 20.0), label="b"),
            CompartmentElement(SVG, offset=(50.0, 0.0), size=(20.0, 20.0), label="c"),
        )
        self.assertEqual(elements_overlap(pack), [("a", "b")])

    def test_tolerance_forgives_a_graze(self) -> None:
        pack = (
            CompartmentElement(SVG, offset=(0.0, 0.0), size=(20.0, 20.0), label="a"),
            CompartmentElement(SVG, offset=(19.5, 0.0), size=(20.0, 20.0), label="b"),
        )
        self.assertEqual(elements_overlap(pack), [("a", "b")])
        self.assertEqual(elements_overlap(pack, tolerance=1.0), [])


class ElementPackCompartmentTests(unittest.TestCase):
    """A compartment carrying elements sizes itself from the pack (FR-004b)."""

    def test_compartment_derives_its_size_from_its_elements(self) -> None:
        comp = CompartmentBuilder(
            label="Workers",
            depth=9.0,
            elements=(
                CompartmentElement(SVG, offset=(0.0, 0.0), size=(23.0, 12.0)),
                CompartmentElement(SVG, offset=(24.0, 0.0), size=(23.0, 12.0)),
            ),
        )
        self.assertEqual(comp.resolve_size(200.0, 150.0), (47.0, 12.0))

    def test_element_margin_pads_the_derived_size(self) -> None:
        comp = CompartmentBuilder(
            label="Workers",
            depth=9.0,
            element_margin=1.5,
            elements=(CompartmentElement(SVG, offset=(0.0, 0.0), size=(23.0, 12.0)),),
        )
        self.assertEqual(comp.resolve_size(200.0, 150.0), (24.5, 13.5))

    def test_explicit_size_wins_over_the_pack(self) -> None:
        comp = CompartmentBuilder(
            label="Workers",
            size=(85.0, 75.0),
            depth=9.0,
            elements=(CompartmentElement(SVG, offset=(0.0, 0.0), size=(23.0, 12.0)),),
        )
        self.assertEqual(comp.resolve_size(200.0, 150.0), (85.0, 75.0))

    def test_a_compartment_with_no_elements_or_size_fills_the_interior(self) -> None:
        """An element pack is sized by its elements; a bare well by the box."""
        bare = CompartmentBuilder(label="Nothing", depth=9.0)
        self.assertTrue(bare.fills_interior)
        self.assertEqual(bare.resolve_size(80.0, 60.0), (80.0, 60.0))


class CompartmentAutoLayoutTests(unittest.TestCase):
    """Fixed-size compartment inside-box auto-layout preserves box size & finger clearance."""

    def test_distributes_wells_symmetrically_with_paired_inlays(self) -> None:
        pocket = CompartmentElement(shape=ElementShape.RECT, size=(20.0, 20.0), label="slot")
        inlay = CompartmentElement(
            shape=ElementShape.CIRCLE, size=(10.0, 10.0), z_offset=3.0, depth=0.6, color="black", label="icon",
        )
        packed = pack_into_compartment([(pocket, inlay), (pocket, inlay)], (80.0, 40.0))
        self.assertEqual(len(packed), 4)
        cutouts = [e for e in packed if e.color is None]
        self.assertEqual(elements_overlap(cutouts, tolerance=0.5), [])
        min_x, min_y, max_x, max_y = elements_bounding_box(cutouts)
        self.assertGreaterEqual(min_x, 10.0)
        self.assertAlmostEqual(80.0 - max_x, min_x, places=3)
        self.assertAlmostEqual(min_y, 10.0, places=3)
        self.assertAlmostEqual(40.0 - max_y, 10.0, places=3)
        # Each icon sits centered on its paired slot
        for parent, child in zip(packed[0::2], packed[1::2], strict=True):
            px0, py0, px1, py1 = parent.bounds()
            cx0, cy0, cx1, cy1 = child.bounds()
            self.assertAlmostEqual((px0 + px1) / 2, (cx0 + cx1) / 2, places=3)
            self.assertAlmostEqual((py0 + py1) / 2, (cy0 + cy1) / 2, places=3)

    def test_rotates_children_along_with_rotated_parent(self) -> None:
        tall = CompartmentElement(shape=ElementShape.RECT, size=(40.0, 15.0), label="tall")
        inlay = CompartmentElement(
            shape=ElementShape.RECT, size=(12.0, 6.0), z_offset=2.0, depth=0.6, color="black", label="stamp",
        )
        packed = pack_into_compartment([(tall, inlay)], (20.0, 50.0), allow_rotate=True)
        parent, child = packed
        self.assertEqual(parent.rotation, 90.0)
        self.assertEqual(child.rotation, 90.0)
        self.assertAlmostEqual(child.footprint[0], 6.0, places=6)
        self.assertAlmostEqual(child.footprint[1], 12.0, places=6)

    def test_maxrects_fallback_handles_heterogeneous_elements(self) -> None:
        packed = pack_into_compartment(
            [
                CompartmentElement(shape=ElementShape.RECT, size=(60.0, 80.0), label="tall"),
                CompartmentElement(shape=ElementShape.RECT, size=(55.0, 20.0), label="base"),
                CompartmentElement(shape=ElementShape.RECT, size=(40.0, 28.0), label="wide"),
                CompartmentElement(shape=ElementShape.CIRCLE, size=(28.0, 28.0), label="tok1"),
                CompartmentElement(shape=ElementShape.CIRCLE, size=(28.0, 28.0), label="tok2"),
            ],
            (100.0, 110.0),
        )
        self.assertEqual(len(packed), 5)
        self.assertEqual(elements_overlap(packed, tolerance=0.5), [])
        min_x, min_y, max_x, max_y = elements_bounding_box(packed)
        self.assertGreaterEqual(min_x, 0.0)
        self.assertGreaterEqual(min_y, 0.0)
        self.assertLessEqual(max_x, 100.0 + 1e-6)
        self.assertLessEqual(max_y, 110.0 + 1e-6)

    def test_raises_when_elements_cannot_fit_interior(self) -> None:
        with self.assertRaises(ValueError):
            pack_into_compartment(
                [CompartmentElement(shape=ElementShape.RECT, size=(60.0, 60.0))],
                (50.0, 50.0),
            )

    def test_build_pull_out_smooth_all_bottom_edges(self) -> None:
        """Pull-out scoops curve smoothly along all bottom edges on both axes at fn=48."""
        from pyboxbuilder import precision
        from pyboxbuilder.compartments.element import build_pull_out

        slot = CompartmentElement(
            shape=ElementShape.RECT, size=(20.0, 20.0), offset=(10.0, 10.0), depth=10.0, pull_out=True,
        )
        with precision.use(fn=48):
            for axis in ("y", "x"):
                solid = build_pull_out(slot, 10.0, (40.0, 40.0), force_axis=axis)
                assert solid is not None
                _verts, faces = solid.shape.mesh()
                self.assertGreater(len(faces), 1000, f"expected smooth faceted scoop for axis={axis}")

    def test_balanced_shelf_packs_mixed_widths_in_aligned_rows(self) -> None:
        """Mixed widths that exceed 5-wide on one row balance across 2 aligned shelf rows."""
        items = [
            *(
                CompartmentElement(shape=ElementShape.CIRCLE, size=(15.0, 15.0), depth=8.0, label=f"s{i}")
                for i in range(2)
            ),
            *(
                CompartmentElement(shape=ElementShape.RECT, size=(18.5, 18.5), depth=6.0, label=f"b{i}")
                for i in range(8)
            ),
        ]
        packed = pack_into_compartment(items, (102.5, 55.833))
        self.assertEqual(elements_overlap(packed, tolerance=0.5), [])
        row_ys = sorted({round(el.bounds()[1] + el.footprint[1] / 2.0, 2) for el in packed})
        self.assertEqual(len(row_ys), 2)
        # Front and back Y margins match symmetrically (~6.28mm)
        min_x, min_y, max_x, max_y = elements_bounding_box(packed)
        self.assertAlmostEqual(min_y, 55.833 - max_y, places=2)
        self.assertGreaterEqual(min_x, 2.0 - 1e-3)
        self.assertAlmostEqual(min_x, 102.5 - max_x, places=2)

    def test_inlay_z_offset_defaults_to_parent_pocket_floor(self) -> None:
        """A coloured inlay with z_offset=None sits flush on its shallower parent pocket floor."""
        from pyboxbuilder.compartments.element import build_element_pack_inserts

        pocket = CompartmentElement(
            shape=ElementShape.RECT, offset=(5.0, 5.0), size=(18.5, 18.5), depth=2.0,
        )
        svg_inlay = CompartmentElement(
            shape=ElementShape.SVG,
            shape_file="boxes/root/svg/laurel_wreath.svg",
            offset=(10.0, 10.0),
            size=(6.5, 6.5),
            depth=0.6,
            z_offset=None,
            color="black",
        )
        txt_inlay = CompartmentElement(
            shape=ElementShape.TEXT,
            shape_file="VP",
            offset=(10.0, 10.0),
            size=(6.5, 6.5),
            depth=0.6,
            z_offset=None,
            color="black",
        )
        for inlay in (svg_inlay, txt_inlay):
            inserts = build_element_pack_inserts((pocket, inlay), default_depth=10.9)
            self.assertEqual(len(inserts), 1)
            bounds = inserts[0][0].bounds()
            # Pocket floor is at default_depth - pocket.depth = 10.9 - 2.0 = 8.9
            self.assertAlmostEqual(float(bounds.min_z), 8.9, places=2)
            self.assertAlmostEqual(float(bounds.max_z), 9.5, places=2)

    def test_pull_outs_respect_neighbors_and_never_hull_mixed_depths(self) -> None:
        """Adjacent pockets of different depths never hull across and stay within bounds."""
        from pybosl2 import cuboid

        from pyboxbuilder.compartments.element import build_element_pack_pull_outs

        deep = CompartmentElement(
            shape=ElementShape.RECT, offset=(10.0, 10.0), size=(18.5, 18.5), depth=6.0, pull_out=True,
        )
        shallow = CompartmentElement(
            shape=ElementShape.RECT, offset=(30.75, 10.0), size=(18.5, 18.5), depth=2.0, pull_out=True,
        )
        comp_size = (60.0, 55.8)
        po = build_element_pack_pull_outs((deep, shallow), 10.9, comp_size)
        assert po is not None
        pb = po.bounds()
        self.assertGreaterEqual(float(pb.min_x), -1e-3)
        self.assertGreaterEqual(float(pb.min_y), -1e-3)
        self.assertLessEqual(float(pb.max_x), comp_size[0] + 1e-3)
        self.assertLessEqual(float(pb.max_y), comp_size[1] + 1e-3)

        # Pull-out cutout beneath shallow pocket's center must never dip below its 8.9mm floor
        shallow_probe = cuboid([4.0, 4.0, 10.9]).translate([40.0, 19.25, 10.9 / 2.0])
        carved_under_shallow = po & shallow_probe
        self.assertGreaterEqual(float(carved_under_shallow.bounds().min_z), 8.9 - 0.05)

    def test_thick_area_cutout_and_full_depth_shallow_finger_bay(self) -> None:
        """Contiguous thick pockets open an upper half-depth area while thin tokens carve down to their base."""
        from pybosl2 import cuboid

        from pyboxbuilder.compartments.element import build_element_pack_pull_outs

        comp_d = 10.9
        comp_size = (90.0, 56.0)
        elements = (
            # 2x2 thick d=6.0 group at X=[10..50], Y=[10..50] (gap 3mm between rows/cols)
            CompartmentElement(shape=ElementShape.RECT, offset=(10.0, 10.0), size=(18.5, 18.5), depth=6.0),
            CompartmentElement(shape=ElementShape.RECT, offset=(31.0, 10.0), size=(18.5, 18.5), depth=6.0),
            CompartmentElement(shape=ElementShape.RECT, offset=(10.0, 31.0), size=(18.5, 18.5), depth=6.0),
            CompartmentElement(shape=ElementShape.RECT, offset=(31.0, 31.0), size=(18.5, 18.5), depth=6.0),
            # Separate shallow d=2.0 cardboard slot at right end with 10mm open front/back margin
            CompartmentElement(shape=ElementShape.RECT, offset=(60.0, 10.0), size=(18.5, 18.5), depth=2.0),
        )
        po = build_element_pack_pull_outs(elements, comp_d, comp_size)
        assert po is not None

        # Center gap between the 2x2 thick slots ((29.75, 29.75)) is carved down to half-depth (10.9 - 3.0 = 7.9)
        mid_probe = cuboid([1.0, 1.0, comp_d]).translate([29.75, 29.75, comp_d / 2.0])
        mid_cut = po & mid_probe
        self.assertAlmostEqual(float(mid_cut.bounds().min_z), comp_d - 3.0, places=1)

        # Open margin in front of the shallow 2.0mm token (y=5.5, 4.5mm past front edge) is cut down to the base (8.9mm)
        bay_probe = cuboid([4.0, 2.0, comp_d]).translate([69.25, 5.5, comp_d / 2.0])
        bay_cut = po & bay_probe
        self.assertAlmostEqual(float(bay_cut.bounds().min_z), comp_d - 2.0, places=2)

    def test_explicit_full_depth_cardboard_tokens_cut_to_base_and_keep_walls(self) -> None:
        """Stacked cardboard pockets (depth > 3.5mm) with pull_out_depth=depth cut to the base."""
        from pybosl2 import cuboid

        from pyboxbuilder.compartments.element import (
            _choose_pull_out_axis,
            _extract_thick_area_groups,
            _neighbor_clearances,
            build_element_pack_pull_outs,
            build_pull_out,
        )

        comp_d = 10.9
        comp_size = (60.0, 56.0)
        # Two adjacent 8mm stacked cardboard pockets separated by 2mm in X, wide open in Y.
        left = CompartmentElement(
            shape=ElementShape.RECT,
            offset=(10.0, 10.0),
            size=(18.5, 18.5),
            depth=8.0,
            pull_out_depth=8.0,
        )
        right = CompartmentElement(
            shape=ElementShape.RECT,
            offset=(30.5, 10.0),
            size=(18.5, 18.5),
            depth=8.0,
            pull_out_depth=8.0,
        )

        # Must NOT be grouped into a half-depth thick-token area cutout.
        areas, handled = _extract_thick_area_groups((left, right), (left, right), *comp_size, comp_d)
        self.assertEqual(areas, [])
        self.assertEqual(handled, set())

        # Front open margin (y=8.0, 2mm in front of pocket) reaches the 8mm pocket floor (10.9 - 8.0 = 2.9).
        po = build_element_pack_pull_outs((left, right), comp_d, comp_size)
        assert po is not None
        bay_probe = cuboid([4.0, 2.0, comp_d]).translate([19.25, 8.0, comp_d / 2.0])
        bay_cut = po & bay_probe
        self.assertAlmostEqual(float(bay_cut.bounds().min_z), comp_d - 8.0, places=2)

        # Individual left & right pull-outs stay inside their pockets in X, keeping the 2mm divider intact.
        clr_left = _neighbor_clearances(left, (left, right), *comp_size, comp_d)
        clr_right = _neighbor_clearances(right, (left, right), *comp_size, comp_d)
        left_bay = build_pull_out(left, comp_d, comp_size, clearances=clr_left)
        right_bay = build_pull_out(right, comp_d, comp_size, clearances=clr_right)
        assert left_bay is not None and right_bay is not None
        self.assertLessEqual(float(left_bay.bounds().max_x), 28.5 + 1e-3)
        self.assertGreaterEqual(float(right_bay.bounds().min_x), 30.5 - 1e-3)

        # Oblong pocket blocked tightly in Y (gap=1.0) must pick X and keep the 1mm Y wall solid.
        blocked_y_a = CompartmentElement(
            shape=ElementShape.RECT,
            offset=(10.0, 1.0),
            size=(29.5, 15.5),
            depth=5.0,
            pull_out_depth=5.0,
        )
        blocked_y_b = CompartmentElement(
            shape=ElementShape.RECT,
            offset=(10.0, 17.5),
            size=(29.5, 15.5),
            depth=5.0,
            pull_out_depth=5.0,
        )
        ob_clr = _neighbor_clearances(blocked_y_b, (blocked_y_a, blocked_y_b), 50.0, 34.0, 5.0)
        self.assertFalse(
            _choose_pull_out_axis(29.5, 15.5, 16.0, ob_clr, is_full_depth=True)
        )
        ob_bay = build_pull_out(blocked_y_b, 5.0, (50.0, 34.0), clearances=ob_clr)
        assert ob_bay is not None
        ob_bounds = ob_bay.bounds()
        self.assertAlmostEqual(float(ob_bounds.min_z), 0.0, places=2)
        self.assertAlmostEqual(float(ob_bounds.min_x), 3.0, places=2)
        self.assertGreaterEqual(float(ob_bounds.min_y), 17.5 - 1e-3)

        # Curved bottom edge on full-depth bays rises smoothly above pocket floor near outer tip.
        tip_probe = cuboid([1.0, 0.5, comp_d]).translate([19.25, 3.5, comp_d / 2.0])
        tip_cut = po & tip_probe
        self.assertGreater(float(tip_cut.bounds().min_z), comp_d - 8.0 + 0.2)


if __name__ == "__main__":
    unittest.main()
