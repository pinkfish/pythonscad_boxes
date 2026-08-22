# SPDX-License-Identifier: Apache-2.0
"""The Crew: Mission Deep Sea — insert fidelity tests.

The numbers asserted here are the game's real components (the card sizes, the
token diameters, the diver's 86 mm height) and the layout the example derives
from them, so these fail if the insert drifts from the game it stores.
"""

from __future__ import annotations

import runpy
import unittest
from pathlib import Path

from pyboxbuilder.compartments.element import elements_bounding_box, elements_overlap
from pyboxbuilder.enums import BoxType, ElementShape

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXAMPLE = REPO_ROOT / "boxes" / "the_crew" / "the_crew.py"


def load_example() -> dict:
    """Run the example module and hand back its namespace."""
    return runpy.run_path(str(EXAMPLE))


class GameBoxTests(unittest.TestCase):
    """The game box is the retail box's inside dimensions."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_example()

    def test_game_box(self) -> None:
        self.assertEqual(self.mod["project"].game_box_size, (172.0, 122.0, 26.0))

    def test_box_inventory(self) -> None:
        boxes = {b.label for b in self.mod["project"]._boxes}
        self.assertEqual(boxes, {"Deck", "Tasks1", "Tasks2", "Accessories"})


class CardBoxTests(unittest.TestCase):
    """Three sliding boxes hold the 45 large and 96 small cards."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_example()
        cls.mod["project"].build()  # resolves each card box's height
        cls.boxes = {b.label: b for b in cls.mod["project"]._boxes}

    def test_all_card_boxes_slide(self) -> None:
        for label in ("Deck", "Tasks1", "Tasks2"):
            self.assertEqual(self.boxes[label].box_type, BoxType.SLIDING, label)

    def test_deck_is_full_height(self) -> None:
        """The main card box spans the box's full 26 mm interior height."""
        self.assertEqual(self.mod["DECK_SIZE"], (61.0, 93.0))
        self.assertEqual(self.boxes["Deck"].final_size[2], self.mod["BOX_HEIGHT"])

    def test_deck_holds_45_cards(self) -> None:
        (well,) = self.boxes["Deck"].compartments
        self.assertEqual(well.depth, 45 * self.mod["CARD_THICKNESS"] + self.mod["CARD_SLACK"])

    def test_task_cards_split_into_two_48_card_stacks(self) -> None:
        for label in ("Tasks1", "Tasks2"):
            (well,) = self.boxes[label].compartments
            self.assertEqual(well.depth, 48 * self.mod["CARD_THICKNESS"] + self.mod["CARD_SLACK"])
            self.assertEqual(self.mod["TASK_SIZE"], (49.0, 73.0))

    def test_task_heights_follow_the_cards(self) -> None:
        """A task box's height is the stack plus floor and lid — never typed by hand."""
        task_h = 48 * self.mod["CARD_THICKNESS"] + self.mod["CARD_SLACK"]
        floor, lid = self.mod["FLOOR"], self.mod["LID"]
        self.assertAlmostEqual(self.boxes["Tasks1"].final_size[2], task_h + floor + lid + 0.5)


class AccessoryTests(unittest.TestCase):
    """The top tray holds the diver, its base, the sonar stack and the distress token."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_example()
        cls.boxes = {b.label: b for b in cls.mod["project"]._boxes}
        (compartment,) = cls.boxes["Accessories"].compartments
        cls.elements = compartment.elements

    def labels(self) -> list[str]:
        return [e.label or "" for e in self.elements]

    def test_accessory_tray_is_lidless(self) -> None:
        self.assertEqual(self.boxes["Accessories"].box_type, BoxType.NO_LID)

    def test_diver_and_base_use_their_svgs(self) -> None:
        diver = next(e for e in self.elements if e.label == "diver")
        base = next(e for e in self.elements if e.label == "base")
        self.assertEqual(diver.shape, ElementShape.SVG)
        self.assertEqual(base.shape, ElementShape.SVG)
        self.assertTrue((REPO_ROOT / diver.shape_file).exists())
        self.assertTrue((REPO_ROOT / base.shape_file).exists())

    def test_diver_width_follows_the_86mm_height(self) -> None:
        """The SVG is scaled uniformly: height is stated, width is derived."""
        vb_w, vb_h = self.mod["DIVER_VIEWBOX"]
        self.assertAlmostEqual(self.mod["DIVER_WIDTH"], vb_w * 86.0 / vb_h, places=6)

    def test_token_thickness_is_205(self) -> None:
        self.assertEqual(self.mod["TOKEN_THICKNESS"], 2.05)

    def test_standee_pieces_are_deeper_than_the_tokens(self) -> None:
        """The 2.5 mm standee is thicker than the 2.05 mm tokens, so its well is
        cut deeper."""
        diver = next(e for e in self.elements if e.label == "diver")
        distress = next(e for e in self.elements if e.label == "distress")
        self.assertGreater(diver.depth, distress.depth)
        self.assertGreater(diver.depth, self.mod["DIVER_THICKNESS"])
        self.assertGreater(distress.depth, self.mod["TOKEN_THICKNESS"])

    def test_every_well_has_half_a_mm_of_top_slack(self) -> None:
        """A well is cut deeper than its piece, leaving slack for a fingertip."""
        for label, thickness in (
            ("diver", self.mod["DIVER_THICKNESS"]),
            ("base", self.mod["DIVER_THICKNESS"]),
            ("distress", self.mod["TOKEN_THICKNESS"]),
        ):
            piece = next(e for e in self.elements if e.label == label)
            self.assertGreaterEqual(piece.depth, thickness + self.mod["TOP_SLACK"], label)

    def test_sonar_pockets_and_distress_are_present(self) -> None:
        labels = self.labels()
        self.assertEqual(sum(1 for name in labels if name in ("sonar_3", "sonar_2")), 2)
        self.assertEqual(sum(1 for name in labels if name == "distress"), 1)

    def test_sonar_pockets_are_round_wells(self) -> None:
        for label in ("sonar_3", "sonar_2"):
            sonar = next(e for e in self.elements if e.label == label)
            self.assertEqual(sonar.shape, ElementShape.CIRCLE, label)
            self.assertAlmostEqual(sonar.size[0], self.mod["SONAR_DIAMETER"] + 0.5)

    def test_sonar_pockets_hold_their_share_of_the_stack(self) -> None:
        """Three tokens stack in the deep well, two in the shallow one — each cut
        to that many times the token's 2.05 mm thickness plus a little slack."""
        thickness = self.mod["TOKEN_THICKNESS"]
        deep = next(e for e in self.elements if e.label == "sonar_3")
        shallow = next(e for e in self.elements if e.label == "sonar_2")
        self.assertGreater(deep.depth, 3 * thickness)
        self.assertGreater(shallow.depth, 2 * thickness)
        self.assertGreater(deep.depth, shallow.depth)

    def test_sonar_pockets_are_deeper_than_the_flat_pieces(self) -> None:
        """Stacked sonar tokens need a deeper well than the single flat pieces."""
        for label in ("sonar_3", "sonar_2"):
            sonar = next(e for e in self.elements if e.label == label)
            for flat_label in ("diver", "base", "distress"):
                flat = next(e for e in self.elements if e.label == flat_label)
                self.assertGreater(sonar.depth, flat.depth, f"{label} vs {flat_label}")

    def test_every_slot_sits_inside_the_tray(self) -> None:
        min_x, min_y, max_x, max_y = elements_bounding_box(self.elements)
        self.assertGreaterEqual(min_x, 0.0)
        self.assertGreaterEqual(min_y, 0.0)
        self.assertLessEqual(max_x, self.mod["ACCESSORY_INNER_W"])
        self.assertLessEqual(max_y, self.mod["ACCESSORY_INNER_L"])

    def test_no_two_slots_collide(self) -> None:
        self.assertEqual(elements_overlap(self.elements, tolerance=0.5), [])

    def test_no_slot_pokes_out_of_the_tray_depth(self) -> None:
        for element in self.elements:
            self.assertLess(element.depth, self.mod["ACCESSORY_INNER_H"] + 0.6)
            self.assertLess(element.z_offset, self.mod["ACCESSORY_INNER_H"])


class LayoutTests(unittest.TestCase):
    """The deck fills one corner; the tasks and tray stack beside it."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_example()
        cls.mod["project"].build()  # populates final_size for the card boxes
        cls.boxes = {b.label: b for b in cls.mod["project"]._boxes}

    def test_positions_fall_out_of_the_arrangement(self) -> None:
        self.assertEqual(self.boxes["Deck"].position, (0.0, 0.0, 0.0))
        self.assertEqual(self.boxes["Tasks1"].position, (61.0, 0.0, 0.0))
        self.assertEqual(self.boxes["Tasks2"].position, (110.0, 0.0, 0.0))
        ax, ay, az = self.boxes["Accessories"].position
        self.assertEqual(ax, 61.0)
        self.assertEqual(ay, 0.0)
        self.assertAlmostEqual(az, self.mod["TASK_HEIGHT"], places=6)

    def test_everything_fits_the_game_box(self) -> None:
        w, l, h = self.mod["project"].game_box_size
        for label, builder in self.boxes.items():
            x, y, z = builder.position
            bw, bl, bh = builder.final_size
            self.assertLessEqual(x + bw, w + 1e-6, f"{label} overhangs in X")
            self.assertLessEqual(y + bl, l + 1e-6, f"{label} overhangs in Y")
            self.assertLessEqual(z + bh, h + 1e-6, f"{label} overhangs in Z")

    def test_no_two_boxes_occupy_the_same_space(self) -> None:
        placed = [(label, b.position, b.final_size) for label, b in self.boxes.items()]
        for i, (label_a, pos_a, size_a) in enumerate(placed):
            for label_b, pos_b, size_b in placed[i + 1 :]:
                overlaps = all(
                    pos_a[axis] + 1e-6 < pos_b[axis] + size_b[axis]
                    and pos_b[axis] + 1e-6 < pos_a[axis] + size_a[axis]
                    for axis in range(3)
                )
                self.assertFalse(overlaps, f"{label_a} overlaps {label_b}")


class ExportTests(unittest.TestCase):
    def test_export_writes_a_body_and_lid_for_every_lidded_box(self) -> None:
        import tempfile

        mod = load_example()
        project = mod["project"]
        with tempfile.TemporaryDirectory() as tmp:
            result = project.export(tmp)

            root = Path(tmp) / "TheCrewMissionDeepSea"
            self.assertTrue((root / "layout.pdf").exists())
            for builder in project._boxes:
                self.assertTrue((root / "mmu" / f"{builder.label}_body.3mf").exists())
                has_lid = builder.box_type is not BoxType.NO_LID
                self.assertEqual(
                    (root / "mmu" / f"{builder.label}_lid.3mf").exists(),
                    has_lid,
                    f"{builder.label} lid presence is wrong",
                )
            # The leftover space beside the cards becomes spacers (mmu + single).
            spacer_files = [f for f in result.written if "spacer" in f]
            self.assertGreater(len(spacer_files), 0)
            self.assertEqual(len(result.skipped), 0)

    def test_re_export_rewrites_nothing(self) -> None:
        import tempfile

        mod = load_example()
        project = mod["project"]
        with tempfile.TemporaryDirectory() as tmp:
            project.export(tmp)
            project.export(tmp)  # settles the PDF hash written on the first run
            again = project.export(tmp)
            self.assertEqual(list(again.written), [])
            self.assertGreater(len(again.skipped), 0)


if __name__ == "__main__":
    unittest.main()
