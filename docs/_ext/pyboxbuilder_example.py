# SPDX-License-Identifier: Apache-2.0
"""Sphinx ``.. pythonscad-example::`` directive for pyboxbuilder.

The directive's content is a short pyboxbuilder-using Python snippet ending in
``<obj>.show()`` (the same convention as a real PythonSCAD python-mode file).
At build time it is prepended with a preamble (repo root on ``sys.path``,
common imports) and rendered with the *real* PythonSCAD binary, and the docs
show, side by side: the snippet's source, an interactive 3-D STL viewer, and a
download link to the exported STL mesh.

Exported STLs are cached in ``docs/_extra/_stl/`` keyed by a hash of the
snippet, so unchanged examples are not re-rendered. When no PythonSCAD binary
is available (or a render fails), the directive degrades gracefully — it emits
a build warning and still shows the source, without the viewer, instead of
failing the whole build.
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import Directive
from render_stl import find_pythonscad_binary, host_site_packages, render_stl_script
from sphinx.util import logging
from stl_viewer import stl_viewer_html

_DOCS_DIR = Path(__file__).resolve().parent.parent
# Exported meshes live under _extra/_stl/ so html_extra_path=["_extra"] copies the
# whole _stl/ subdir to the output root, keeping the ``_stl/<hash>.stl`` URIs valid.
_STL_DIR = _DOCS_DIR / "_extra" / "_stl"
_REPO_ROOT = _DOCS_DIR.parent

_logger = logging.getLogger(__name__)

# Prepended to every snippet: put the repo root on sys.path and import the common
# names, so examples can be terse and mirror how the toolkit is actually used.
_PREAMBLE = (
    "import sys, math, site, os, traceback\n"
    f"sys.path.insert(0, {str(_REPO_ROOT)!r})\n"
    # The app bundles its own Python; hand it the host's site-packages so the
    # dependencies the docs interpreter installed (pybosl2, shapely) are visible.
    f"for p in {host_site_packages()!r}:\n"
    "    if p not in sys.path:\n"
    "        sys.path.append(p)\n"
    "for p in site.getsitepackages():\n"
    "    if p not in sys.path:\n"
    "        sys.path.append(p)\n"
    "usp = site.getusersitepackages()\n"
    "if os.path.isdir(usp) and usp not in sys.path:\n"
    "    sys.path.insert(0, usp)\n"
    "host_sp = os.environ.get('pythonLocation', '')\n"
    "if host_sp:\n"
    "    for entry in os.listdir(os.path.join(host_sp, 'lib')):\n"
    "        if entry.startswith('python3.'):\n"
    "            sp = os.path.join(host_sp, 'lib', entry, 'site-packages')\n"
    "            if os.path.isdir(sp) and sp not in sys.path:\n"
    "                sys.path.insert(0, sp)\n"
    "import numpy as np\n"
    "import pyboxbuilder\n"
    "from pyboxbuilder import (\n"
    "    BoxType, Color, CompartmentElement, ElementShape, LabelMode,\n"
    "    MagnetType, PatternType, Project, ScoopSide, StackableMode,\n"
    "    columns, grid_pack, rows, stack,\n"
    ")\n"
    "\n"
    "try:\n"
)

_POSTAMBLE = (
    "except Exception as e:\n"
    '    print("An error occurred during model generation:")\n'
    "    traceback.print_exc()\n"
)


class PyboxbuilderExampleDirective(Directive):
    """``.. pythonscad-example::`` — render a pyboxbuilder snippet to an STL viewer."""

    has_content = True

    def run(self) -> list[nodes.Node]:
        code_str = "\n".join(self.content)
        lines = code_str.splitlines()
        indented_str = "\n".join(f"    {line}" if line else "" for line in lines)

        script = _PREAMBLE + indented_str + "\n" + _POSTAMBLE

        out: list[nodes.Node] = []
        code_node = nodes.literal_block(code_str, code_str)
        code_node["language"] = "python"
        out.append(code_node)

        # Show an interactive 3-D STL viewer; if no STL was produced (no binary,
        # or a 2-D object), show the source only.
        stl_uri = self._render_stl(script, code_str)
        if stl_uri is not None:
            out.append(nodes.raw("", stl_viewer_html(stl_uri), format="html"))
            para = nodes.paragraph()
            para += nodes.reference("", "⬇ Download STL mesh", refuri=stl_uri)
            out.append(para)
        return out

    def _render_stl(self, script: str, code: str) -> str | None:
        digest = hashlib.sha256(f"stl\n{code}".encode()).hexdigest()[:16]
        out_stl = _STL_DIR / f"{digest}.stl"
        if out_stl.is_file():
            return f"_stl/{out_stl.name}"
        if find_pythonscad_binary() is None:
            _logger.info(
                "pythonscad-example: no PythonSCAD binary found, skipping STL render"
            )
            return None
        _STL_DIR.mkdir(parents=True, exist_ok=True)
        try:
            result = render_stl_script(
                script, out_stl, timeout=300.0, export_format="binstl"
            )
        except subprocess.TimeoutExpired:
            _logger.warning(
                f"pythonscad-example: STL export timed out after 300s for:\n{code[:200]}"
            )
            return None
        except Exception as exc:
            _logger.error(
                f"pythonscad-example: unexpected error rendering STL: {exc}"
            )
            return None
        if not result.ok:
            _logger.warning(
                f"pythonscad-example STL render FAILED: {result.error}\n"
                f"--- code ---\n{code}\n"
                f"--- stderr ---\n{result.stderr}\n"
                f"---"
            )
            return None
        return f"_stl/{out_stl.name}"


def setup(app) -> dict:
    # ``pythonscad-example`` matches the name pybosl2's docstrings already use;
    # ``pyboxbuilder-example`` is kept as an alias.
    app.add_directive("pythonscad-example", PyboxbuilderExampleDirective)
    app.add_directive("pyboxbuilder-example", PyboxbuilderExampleDirective)
    return {"version": "0.1", "parallel_read_safe": True, "parallel_write_safe": True}
