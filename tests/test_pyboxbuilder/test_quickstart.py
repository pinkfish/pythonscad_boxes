# SPDX-License-Identifier: Apache-2.0
"""Every code block in the quickstart runs.

The quickstart is the first thing a new user copies, and it had drifted from
the library it documents: it offered `Color.WHITE()`, which the plan explicitly
bans, and `two_layer=True`, which nothing read. Neither was caught, because
nothing ran it. This runs it.

Exports are redirected to a temporary directory and previews are built rather
than shown, so the test writes nothing outside its own tmpdir and needs no
render window — but the geometry is really built.
"""

from __future__ import annotations

import re
import tempfile
import unittest
from pathlib import Path

QUICKSTART = (
    Path(__file__).resolve().parents[2]
    / "spec" / "specs" / "001-board-game-box-library" / "quickstart.md"
)

#: Blocks that are fragments rather than programs: the import list, and the
#: `__main__` guard, which has no project in scope by design.
_FRAGMENTS = ("if __name__", "from pyboxbuilder import (\n    Project,\n")


def _scenarios() -> list[tuple[int, str]]:
    """Every runnable python block in the quickstart, with its block number."""
    blocks = re.findall(r"```python\n(.*?)```", QUICKSTART.read_text(), re.S)
    return [
        (i, b) for i, b in enumerate(blocks, 1)
        if not any(f in b for f in _FRAGMENTS)
    ]


class QuickstartTests(unittest.TestCase):
    def test_the_quickstart_has_scenarios_to_run(self) -> None:
        """Guards the extraction itself: a regex that matches nothing passes."""
        self.assertGreaterEqual(len(_scenarios()), 5)

    def test_every_scenario_runs(self) -> None:
        for number, block in _scenarios():
            with self.subTest(scenario=number):
                with tempfile.TemporaryDirectory() as out:
                    code = (
                        block.replace('"output/"', repr(out))
                        # `show()` wants a render window; the build behind it
                        # is what the scenario is demonstrating.
                        .replace("project.show()", "project.preview_pieces()")
                    )
                    exec(compile(code, f"<quickstart {number}>", "exec"), {})


if __name__ == "__main__":
    unittest.main()
