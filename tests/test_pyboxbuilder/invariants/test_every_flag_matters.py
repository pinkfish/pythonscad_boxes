# SPDX-License-Identifier: Apache-2.0
"""Every switch on a cut has to change the cut.

A flag that is always passed the same way is untested by construction, and this
file exists because one of them was *wrong* from the day it was written:
`round_outer` decorated the compartment-side face rather than the box's outside,
and nothing noticed for as long as every caller rounded both faces, because with
both rounded the two are indistinguishable.

So each switch is toggled and the geometry measured. A flag that stops mattering
fails here rather than quietly becoming decoration — and if it *should* stop
mattering, this is the test that says so out loud.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT / "tests") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "tests"))

from render_app import measure_python, render_available  # noqa: E402


@unittest.skipUnless(render_available(), "PythonSCAD binary not available")
class EveryFlagChangesTheCutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        body = '''
from dataclasses import replace
from pyboxbuilder.compartments.finger_hole import (
    CutProfile, FaceTreatment, build_wall_scoop,
)
from pyboxbuilder.enums import ScoopSide
from pybosl2 import cuboid

def cut(**faces):
    return build_wall_scoop(
        60, 40, 20, ScoopSide.FRONT, radius=10, wall_thickness=3.0,
        faces=FaceTreatment(**faces),
    )

base = cut()
report("base", "%.3f" % volume(base))
for flag, flipped in (("round_outer", False), ("round_inner", False),
                      ("breach_floor", True), ("inner_overshoot", 1.5)):
    report(flag, "%.3f" % volume(cut(**{flag: flipped})))

# the two shape switches live on the builder rather than the faces
report("keep_flat_bottom", "%.3f" % volume(build_wall_scoop(
    60, 40, 20, ScoopSide.FRONT, radius=10, wall_thickness=3.0,
    keep_flat_bottom=False)))
report("closed_top", "%.3f" % volume(build_wall_scoop(
    60, 40, 20, ScoopSide.FRONT, radius=10, wall_thickness=3.0,
    closed_top=True)))
report("floor_clearance", "%.3f" % volume(build_wall_scoop(
    60, 40, 20, ScoopSide.FRONT, radius=10, wall_thickness=3.0,
    faces=FaceTreatment(floor_clearance=2.0))))
report("top_limit", "%.3f" % volume(build_wall_scoop(
    60, 40, 20, ScoopSide.FRONT, radius=10, wall_thickness=3.0,
    faces=FaceTreatment(top_limit=15.0))))
report("mouth_flare", "%.3f" % volume(build_wall_scoop(
    60, 40, 20, ScoopSide.FRONT, radius=10, wall_thickness=3.0,
    profile=CutProfile(mouth_flare=6.0))))
report("base_radius", "%.3f" % volume(build_wall_scoop(
    60, 40, 20, ScoopSide.FRONT, radius=10, wall_thickness=3.0,
    profile=CutProfile(base_radius=2.0))))
# 3.0 rather than 8.0: at radius 10 the derived rise *is* 8.0, so the first
# version of this line asserted a flag mattered by passing it its own default.
report("roll_rise", "%.3f" % volume(build_wall_scoop(
    60, 40, 20, ScoopSide.FRONT, radius=10, wall_thickness=3.0,
    profile=CutProfile(roll_rise=3.0))))
cuboid([1, 1, 1]).show()
'''
        cls.result = measure_python(body)
        if not cls.result.ok:
            raise AssertionError(f"measurement run failed: {cls.result.error}")

    def test_each_switch_changes_the_cut(self) -> None:
        base = float(self.result.reports["base"])
        for flag in ("round_outer", "round_inner", "breach_floor", "inner_overshoot",
                     "keep_flat_bottom", "closed_top", "floor_clearance",
                     "top_limit", "mouth_flare", "base_radius", "roll_rise"):
            with self.subTest(flag=flag):
                self.assertNotAlmostEqual(
                    float(self.result.reports[flag]), base, delta=0.01,
                    msg=f"{flag} no longer changes the cut — it is decoration",
                )

    def test_the_two_faces_are_not_the_same_switch(self) -> None:
        """The bug this file is named for: rounding one face is not the same as
        rounding the other, and if it measures the same they are wired to one
        end of the sweep."""
        self.assertNotAlmostEqual(
            float(self.result.reports["round_outer"]),
            float(self.result.reports["round_inner"]),
            delta=0.01,
        )


if __name__ == "__main__":
    unittest.main()
