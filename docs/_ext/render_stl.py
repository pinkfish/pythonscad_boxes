# SPDX-License-Identifier: Apache-2.0
"""STL export through the real PythonSCAD binary, for the docs example directive.

The ``.. pythonscad-example::`` directive shells out to the real PythonSCAD
binary to build a snippet and export it to a binary STL; this module is the
low-level "run a complete script, export STL" plumbing behind it. It is
deliberately separate from the Sphinx directive so the render can be reused and
tested on its own.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

# PythonSCAD-dev is preferred: the plain app's hardened runtime can reject the
# host numpy. AppImage paths cover a Linux render (e.g. a docs CI job).
_CANDIDATE_BINARIES = [
    "/Applications/PythonSCAD-dev.app/Contents/MacOS/PythonSCAD",
    "/Applications/PythonSCAD.app/Contents/MacOS/PythonSCAD",
    "/usr/local/bin/pythonscad",
    "/opt/pythonscad/AppRun",
    "squashfs-root/AppRun",
]


def find_pythonscad_binary() -> str | None:
    """The PythonSCAD binary to render with: ``$PYTHONSCAD_BIN``, else a known install."""
    override = os.environ.get("PYTHONSCAD_BIN")
    if override:
        return override if Path(override).is_file() else None
    for candidate in _CANDIDATE_BINARIES:
        if Path(candidate).is_file():
            return candidate
    return None


def host_site_packages() -> list[str]:
    """This interpreter's site-packages, to hand to the app's embedded Python.

    The app bundles its own Python, whose ``site.getsitepackages()`` returns
    paths inside the bundle, so a dependency installed for the host interpreter
    (pybosl2, shapely) is invisible to it and the render dies with
    ``ModuleNotFoundError`` before drawing anything. These paths are injected
    into the app's ``sys.path`` from the host side so the embedded interpreter
    can import them.
    """
    import site as _site

    found = list(_site.getsitepackages())
    user = _site.getusersitepackages()
    if isinstance(user, str):
        found.append(user)
    else:
        found.extend(user)
    return [p for p in found if Path(p).is_dir()]


@dataclass
class StlResult:
    ok: bool
    path: Path | None
    error: str | None
    stderr: str


def render_stl_script(
    script_source: str,
    out_stl: Path,
    timeout: float = 300.0,
    export_format: str = "binstl",
) -> StlResult:
    """Run a full python-mode *script_source* (ending in ``.show()``), exporting an STL.

    *script_source* must already be a complete script (imports, ``sys.path``
    setup, and a trailing ``.show()``). Returns a :class:`StlResult` and never
    raises for a render failure; it raises only if no binary can be located.
    """
    binary = find_pythonscad_binary()
    if binary is None:
        raise FileNotFoundError(
            "no PythonSCAD binary found (set PYTHONSCAD_BIN or install to /Applications)"
        )

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, dir=tempfile.gettempdir()
    ) as f:
        f.write(script_source)
        script_path = Path(f.name)

    try:
        proc = subprocess.run(
            [
                binary,
                "--trust-python",
                "--enable",
                "python-engine",
                "-o",
                str(out_stl),
                "--backend",
                "Manifold",
                *(["--export-format", export_format] if export_format else []),
                str(script_path),
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return StlResult(False, None, f"render timed out after {timeout:.0f}s", "")
    finally:
        script_path.unlink(missing_ok=True)

    stderr = proc.stderr or ""
    if "Traceback (most recent call last):" in stderr:
        return StlResult(False, None, "script raised", stderr)
    if proc.returncode != 0:
        return StlResult(
            False, None, f"PythonSCAD exited {proc.returncode}", stderr
        )
    if not out_stl.is_file() or out_stl.stat().st_size == 0:
        return StlResult(False, None, "no STL produced", stderr)
    return StlResult(True, out_stl, None, stderr)
