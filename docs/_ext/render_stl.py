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
import shutil
import struct
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile
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
    which_bin = shutil.which("pythonscad")
    if which_bin:
        return which_bin
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


def convert_3mf_to_colored_stl(threemf_path: Path, stl_out_path: Path) -> bool:
    """Convert a multi-material 3MF file to a Magics-compatible binary STL with embedded facet colors."""
    try:
        with zipfile.ZipFile(threemf_path, "r") as z:
            xml_data = z.read("3D/3dmodel.model")
        root = ET.fromstring(xml_data)

        material_maps: dict[str, list[int]] = {}
        default_colors: list[int] = []
        for basemats in root.iter():
            if basemats.tag.endswith("basematerials"):
                mat_id = basemats.attrib.get("id", "1")
                m_list: list[int] = []
                for base in basemats:
                    if base.tag.endswith("base"):
                        disp = base.attrib.get("displaycolor", "#CCCCCCFF")
                        r = int(disp[1:3], 16)
                        g = int(disp[3:5], 16)
                        b = int(disp[5:7], 16)
                        r5 = min(31, max(0, round((r / 255.0) * 31)))
                        g5 = min(31, max(0, round((g / 255.0) * 31)))
                        b5 = min(31, max(0, round((b / 255.0) * 31)))
                        # In Magics STL format: bit 15 is 0 for facet color, bits 0-4 R, 5-9 G, 10-14 B
                        packed = r5 | (g5 << 5) | (b5 << 10)
                        m_list.append(packed)
                material_maps[mat_id] = m_list
                if not default_colors:
                    default_colors = m_list

        all_triangles: list[
            tuple[
                tuple[float, float, float],
                tuple[float, float, float],
                tuple[float, float, float],
                int,
            ]
        ] = []
        for mesh in root.iter():
            if not mesh.tag.endswith("mesh"):
                continue
            v_elems = [e for e in mesh if e.tag.endswith("vertices")]
            t_elems = [e for e in mesh if e.tag.endswith("triangles")]
            if not v_elems or not t_elems:
                continue

            vertices: list[tuple[float, float, float]] = []
            for v in v_elems[0]:
                if v.tag.endswith("vertex"):
                    vertices.append(
                        (
                            float(v.attrib["x"]),
                            float(v.attrib["y"]),
                            float(v.attrib["z"]),
                        )
                    )

            for t in t_elems[0]:
                if t.tag.endswith("triangle"):
                    v1 = int(t.attrib["v1"])
                    v2 = int(t.attrib["v2"])
                    v3 = int(t.attrib["v3"])
                    pid = t.attrib.get("pid", "1")
                    p1 = int(t.attrib.get("p1", 0))

                    mat_list = material_maps.get(pid, default_colors)
                    attr = mat_list[p1] if (p1 < len(mat_list)) else 0
                    all_triangles.append(
                        (vertices[v1], vertices[v2], vertices[v3], attr)
                    )

        if not all_triangles:
            return False

        header = (
            b"COLOR="
            + bytes([200, 200, 200, 255])
            + b"MATERIAL="
            + b"\x00" * (80 - 19)
        )
        faces_data = bytearray()

        for pt1, pt2, pt3, attr in all_triangles:
            ax, ay, az = pt2[0] - pt1[0], pt2[1] - pt1[1], pt2[2] - pt1[2]
            bx, by, bz = pt3[0] - pt1[0], pt3[1] - pt1[1], pt3[2] - pt1[2]
            nx, ny, nz = ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx
            length = (nx * nx + ny * ny + nz * nz) ** 0.5
            if length > 1e-9:
                nx, ny, nz = nx / length, ny / length, nz / length
            else:
                nx, ny, nz = 0.0, 0.0, 0.0
            faces_data.extend(
                struct.pack(
                    "<ffffffffffffH",
                    nx,
                    ny,
                    nz,
                    pt1[0],
                    pt1[1],
                    pt1[2],
                    pt2[0],
                    pt2[1],
                    pt2[2],
                    pt3[0],
                    pt3[1],
                    pt3[2],
                    attr,
                )
            )

        stl_data = header + struct.pack("<I", len(all_triangles)) + faces_data
        with open(stl_out_path, "wb") as f:
            f.write(stl_data)
        return True
    except Exception:
        return False


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

    # First attempt: Export to .3mf and convert to multi-color Magics binary STL if possible
    temp_3mf = out_stl.with_name(f".{out_stl.stem}.tmp.3mf")
    try:
        proc_3mf = subprocess.run(
            [
                binary,
                "--trust-python",
                "--enable",
                "python-engine",
                "-o",
                str(temp_3mf),
                "--backend",
                "Manifold",
                str(script_path),
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if (
            proc_3mf.returncode == 0
            and temp_3mf.is_file()
            and temp_3mf.stat().st_size > 0
            and convert_3mf_to_colored_stl(temp_3mf, out_stl)
        ):
            return StlResult(True, out_stl, None, proc_3mf.stderr or "")
    except Exception:
        pass
    finally:
        temp_3mf.unlink(missing_ok=True)

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
