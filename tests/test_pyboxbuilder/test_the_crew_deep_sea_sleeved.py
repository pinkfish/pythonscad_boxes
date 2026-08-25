# SPDX-License-Identifier: Apache-2.0
"""The Crew: Mission Deep Sea (sleeved) — insert fidelity tests.

The sleeved variant sizes its wells to specific Gamegenic sleeves and keeps the
sonar tokens flat, so these pin those differences against the unsleeved design.
"""

from __future__ import annotations

import re
import runpy
import unittest
from pathlib import Path

from pyboxbuilder.compartments.element import elements_bounding_box, elements_overlap

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
EXAMPLE = REPO_ROOT / "boxes" / "the_crew_deep_sea_sleeved" / "the_crew_deep_sea_sleeved.py"


def load_example() -> dict:
    return runpy.run_path(str(EXAMPLE))


class SleevedCardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_example()
        cls.mod["project"].build()
        cls.boxes = {b.label: b for b in cls.mod["project"]._boxes}

    def test_game_box_unchanged(self) -> None:
        self.assertEqual(self.mod["project"].game_box_size, (172.0, 122.0, 26.0))

    def test_box_inventory(self) -> None:
        self.assertEqual(
            {b.label for b in self.mod["project"]._boxes},
            {"Deck", "Tasks1", "Tasks2", "Accessories"},
        )

    def test_uses_gamegenic_sleeves(self) -> None:
        """The card boxes are sized to the specific Gamegenic sleeves."""
        large = self.mod["LARGE_SLEEVE"]
        self.assertEqual((large.brand, large.name, large.sleeve_size), ("Gamegenic", "Standard American", (59.0, 91.0)))
        small = self.mod["SMALL_SLEEVE"]
        self.assertEqual((small.brand, small.name, small.sleeve_size), ("Gamegenic", "Mini European", (46.0, 71.0)))

    def test_card_wells_are_sized_to_the_sleeves(self) -> None:
        """A well is the sleeve's outer size plus the card slack."""
        slack = self.mod["CARD_SLACK"]
        (deck,) = self.boxes["Deck"].compartments
        lw, ll = self.mod["LARGE_SLEEVE"].sleeve_size
        self.assertEqual(deck.size, (lw + slack, ll + slack))
        (task,) = self.boxes["Tasks1"].compartments
        sl = self.mod["SMALL_SLEEVE"].sleeve_size[1]
        self.assertEqual(task.size, (self.mod["TASK_BOX_WIDTH"] - 2 * self.mod["WALL"], sl + slack))

    def test_card_boxes_fill_the_box_width(self) -> None:
        """Deck plus the two widened task boxes fill the box width — no spacer."""
        deck_w = self.boxes["Deck"].final_size[0]
        task_w = self.boxes["Tasks1"].final_size[0]
        self.assertAlmostEqual(deck_w + 2 * task_w, self.mod["BOX_WIDTH"])

    def test_card_wells_run_full_height(self) -> None:
        for label in ("Deck", "Tasks1", "Tasks2"):
            (well,) = self.boxes[label].compartments
            self.assertIsNone(well.depth, label)

    def test_sleeved_stacks_fit_their_boxes(self) -> None:
        """The thickest stack — 48 sleeved cards — fits the card box interior."""
        thickness = self.mod["CARD_THICKNESS"]
        interior = self.mod["CARD_BOX_HEIGHT"] - self.mod["FLOOR"] - self.mod["LID"]
        self.assertLess(48 * thickness, interior)
        self.assertLess(45 * thickness, interior)

    def test_accessory_tray_is_shallow(self) -> None:
        """Flat sonar tokens keep the tray shorter than the card boxes."""
        self.assertLess(self.boxes["Accessories"].final_size[2], self.boxes["Deck"].final_size[2])


class AccessoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_example()
        cls.boxes = {b.label: b for b in cls.mod["project"]._boxes}
        (compartment,) = cls.boxes["Accessories"].compartments
        cls.elements = compartment.elements

    def labels(self) -> list[str]:
        return [e.label or "" for e in self.elements]

    def test_five_sonar_lie_flat(self) -> None:
        """The sonar tokens are spread across five shallow wells, not stacked."""
        wells = [n for n in self.labels() if re.fullmatch(r"sonar_\d", n)]
        self.assertEqual(len(wells), 5)

    def test_sonar_wells_are_shallow(self) -> None:
        sonar = next(e for e in self.elements if e.label == "sonar_0")
        self.assertLess(sonar.depth, self.mod["ACCESSORY_INNER_H"] + 0.6)

    def test_every_piece_has_an_icon(self) -> None:
        """Each sonar well and the distress slot carry a second-colour icon."""
        self.assertEqual(sum(1 for n in self.labels() if n.startswith("sonar_icon_")), 5)
        self.assertEqual(sum(1 for n in self.labels() if n == "distress_icon"), 1)

    def test_slots_fit_the_tray_and_do_not_collide(self) -> None:
        cutouts = [e for e in self.elements if e.color is None]
        self.assertEqual(elements_overlap(cutouts, tolerance=0.5), [])
        min_x, min_y, max_x, max_y = elements_bounding_box(self.elements)
        self.assertGreaterEqual(min_x, 0.0)
        self.assertGreaterEqual(min_y, 0.0)
        self.assertLessEqual(max_x, self.mod["ACCESSORY_INNER_W"])
        self.assertLessEqual(max_y, self.mod["ACCESSORY_INNER_L"])


class LayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_example()
        cls.mod["project"].build()
        cls.boxes = {b.label: b for b in cls.mod["project"]._boxes}

    def test_tray_sits_on_top_of_the_cards(self) -> None:
        self.assertEqual(self.boxes["Deck"].position, (0.0, 0.0, 0.0))
        self.assertEqual(self.boxes["Tasks1"].position, (64.0, 0.0, 0.0))
        self.assertAlmostEqual(self.boxes["Accessories"].position[2], self.mod["CARD_BOX_HEIGHT"])

    def test_everything_fits_the_game_box(self) -> None:
        w, l, h = self.mod["project"].game_box_size
        for label, builder in self.boxes.items():
            x, y, z = builder.position
            bw, bl, bh = builder.final_size
            self.assertLessEqual(x + bw, w + 1e-6, f"{label} overhangs in X")
            self.assertLessEqual(y + bl, l + 1e-6, f"{label} overhangs in Y")
            self.assertLessEqual(z + bh, h + 1e-6, f"{label} overhangs in Z")


if __name__ == "__main__":
    unittest.main()
