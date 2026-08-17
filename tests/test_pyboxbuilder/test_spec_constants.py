# SPDX-License-Identifier: Apache-2.0
"""Numbers the spec states must be the numbers the code uses.

The recurring failure in this library is not bad geometry: it is a constant and
a requirement drifting apart, and the geometry then following the constant while
the reviewer reads the requirement. Every case so far was found by eye, late:

* `MIN_WALL_SCOOP_DEPTH_MM` sat at 8mm while the plan's own worked example
  described a 6.5mm well cutting a wall scoop — so every card box got a bore;
* FR-047's reach formula named a term (`finger_hole_size`) that existed nowhere
  and differed from the built one in three places;
* the strip under a tray's grip was a wall thickness and a millimetre in the
  code and "5mm" nowhere until it was measured.

So the numbers the spec *states* are listed here against the constants that
carry them, and the test reads both. It is deliberately a small table: a value
belongs in it when the spec quotes the number itself, because that is when the
two can disagree silently.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SPEC = REPO_ROOT / "spec/specs/001-board-game-box-library/spec.md"


def _constant(module: str, name: str) -> float:
    import importlib

    return float(getattr(importlib.import_module(module), name))


#: (requirement, the phrase the spec states it in, module, constant)
#:
#: The phrase is matched against the requirement's own text, so a spec edit that
#: changes the number fails here rather than in a render three weeks later.
SPEC_NUMBERS = [
    ("FR-061", r"\*\*5mm\*\*", "pyboxbuilder.compartments.finger_cuts",
     "MIN_WALL_SCOOP_DEPTH_MM", 5.0),
    ("FR-072", r"small constant \(0\.2mm\)", "pyboxbuilder.compartments.finger_sweep",
     "DEFAULT_FLOOR_DIP_MM", 0.2),
    ("FR-047", r"\*\*stops 5mm above the tray's floor\*\*", "pyboxbuilder.box.shell",
     "MIN_WALL_BELOW_HOLE_MM", 5.0),
    ("FR-047", r"never past \*\*half the box's height\*\*", "pyboxbuilder.box.shell",
     "MAX_FINGER_HOLE_HEIGHT_SHARE", 0.5),
    ("FR-047a", r"\*\*three quarters\*\*", "pyboxbuilder.box.shell",
     "MAX_FINGER_HOLE_SPAN_SHARE", 0.75),
    ("FR-043f1", r"\*\*quarter\*\* of the wall", "pyboxbuilder.box.shell",
     "SLIDING_RIM_ROUNDING_SHARE", 0.25),
    ("FR-002l", r"\*\*2mm foot\*\*", "pyboxbuilder.box.features",
     "CAP_FINGER_FOOT_MM", 2.0),
    ("FR-002m", r"at least \*\*10mm\*\*", "pyboxbuilder.box.features",
     "CAP_FINGER_MIN_LENGTH_MM", 10.0),
    ("FR-002m1", r"`2 × 10mm`", "pyboxbuilder.box.features",
     "CAP_FINGER_MIN_BAND_MM", 10.0),
    ("FR-002n1", r"skirt MUST be at least 3mm", "pyboxbuilder.box.features",
     "CAP_FINGER_MIN_SKIRT_MM", 3.0),
    ("FR-030", r"", "pyboxbuilder.rounding", "MIN_ROUNDING_FACETS", 48.0),
]


class SpecNumbersMatchTheCodeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.spec = SPEC.read_text()

    def requirement(self, fr: str) -> str:
        """The text of one requirement, up to the next one."""
        match = re.search(rf"^- \*\*{re.escape(fr)}\*\*:(.*?)(?=\n- \*\*(?:FR|SC)-)",
                          self.spec, re.S | re.M)
        self.assertIsNotNone(match, f"{fr} is not in the spec")
        return match.group(1)

    def test_the_code_carries_the_number_the_spec_states(self) -> None:
        for fr, _phrase, module, name, expected in SPEC_NUMBERS:
            with self.subTest(constant=name):
                self.assertAlmostEqual(
                    _constant(module, name), expected, places=6,
                    msg=f"{module}.{name} no longer matches {fr}",
                )

    def test_the_spec_still_states_it(self) -> None:
        """The other direction: an edit that reworded the number away from the
        requirement would leave the constant unanchored."""
        for fr, phrase, _module, name, _expected in SPEC_NUMBERS:
            if not phrase:
                continue
            with self.subTest(requirement=fr, constant=name):
                self.assertRegex(
                    self.requirement(fr), phrase,
                    f"{fr} no longer states the number {name} carries",
                )


if __name__ == "__main__":
    unittest.main()
