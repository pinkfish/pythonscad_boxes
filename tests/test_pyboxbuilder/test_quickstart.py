# SPDX-License-Identifier: Apache-2.0
"""Every code block in the quickstart runs.

The quickstart is the first thing a new user copies, and it lives in the
official Sphinx documentation tree at ``docs/quickstart.rst``.

Exports are redirected to a temporary directory and previews are built rather
than shown, so the test writes nothing outside its own tmpdir and needs no
render window — but the geometry is really built.
"""

from __future__ import annotations

import pathlib
import re
import tempfile
import unittest

import pyboxbuilder
from pyboxbuilder import *

QUICKSTART = pathlib.Path(__file__).resolve().parents[2] / "docs" / "quickstart.rst"

#: Blocks that are fragments rather than programs: the import list, and the
#: `__main__` guard, which has no project in scope by design.
_FRAGMENTS = ("if __name__", "from pyboxbuilder import (\n    BoxType,")


def _deindent(raw: str) -> str:
    lines = []
    for line in raw.splitlines():
        if line.startswith("   "):
            lines.append(line[3:])
        elif not line.strip():
            lines.append("")
        else:
            break
    return "\n".join(lines).strip()


def _scenarios() -> list[tuple[int, str]]:
    """Every runnable python block in the quickstart, with its block number."""
    text = QUICKSTART.read_text()
    raw_blocks = re.findall(
        r"\.\. (?:pythonscad-example|code-block:: python)::\n\n((?:   [^\n]*\n|\n)+)",
        text,
    )
    blocks = [_deindent(b) for b in raw_blocks]
    return [
        (i, b)
        for i, b in enumerate(blocks, 1)
        if not any(f in b for f in _FRAGMENTS)
    ]


class QuickstartTests(unittest.TestCase):
    def test_the_quickstart_has_scenarios_to_run(self) -> None:
        """Guards the extraction itself: a regex that matches nothing passes."""
        self.assertGreaterEqual(len(_scenarios()), 20)

    def test_every_scenario_runs(self) -> None:
        for number, block in _scenarios():
            with self.subTest(scenario=number):
                with tempfile.TemporaryDirectory() as out:
                    code = (
                        block.replace('"output/"', repr(out))
                        .replace("project.show(show_lids=True)", "project.preview_pieces(show_lids=True)")
                        .replace("project.show()", "project.preview_pieces()")
                    )
                    env: dict[str, object] = {
                        "Project": Project,
                        "BoxType": BoxType,
                        "Color": Color,
                        "LidBuilder": LidBuilder,
                        "PatternBuilder": PatternBuilder,
                        "PatternType": PatternType,
                        "LabelMode": LabelMode,
                        "FingerCut": FingerCut,
                        "Cut": Cut,
                        "MagnetType": MagnetType,
                        "StackableMode": StackableMode,
                        "InterlockType": InterlockType,
                        "columns": columns,
                        "rows": rows,
                        "stack": stack,
                        "run": run,
                    }
                    exec(compile(code, f"<quickstart {number}>", "exec"), env)


if __name__ == "__main__":
    unittest.main()
