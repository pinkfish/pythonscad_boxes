#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Pre-generate all STL meshes for the documentation.

Finds all ``.. pythonscad-example::`` blocks across doc files and source
docstrings, renders each through PythonSCAD, and saves them to
``docs/_extra/_stl/<digest>.stl``. Only updates an existing STL if its
measured geometry (bounding box and volume) has actually changed.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "docs" / "_ext"))

from pyboxbuilder_example import _POSTAMBLE, _PREAMBLE  # noqa: E402
from render_stl import find_pythonscad_binary, render_stl_script  # noqa: E402

from pyboxbuilder.export.geometry import read_stl_geometry, same_geometry  # noqa: E402

_STL_DIR = ROOT / "docs" / "_extra" / "_stl"


def _extract_blocks_from_text(text: str) -> list[tuple[str, str]]:
    """Extract (digest, code_str) tuples from arbitrary RST/docstring text."""
    lines = text.splitlines()
    i = 0
    blocks: list[tuple[str, str]] = []
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if stripped.startswith(".. pythonscad-example::") or stripped.startswith(".. pyboxbuilder-example::"):
            base_indent = len(line) - len(line.lstrip())
            i += 1
            while i < len(lines) and not lines[i].strip():
                i += 1
            if i >= len(lines):
                break
            body_indent = len(lines[i]) - len(lines[i].lstrip())
            if body_indent <= base_indent:
                continue
            code_lines = []
            while i < len(lines):
                cur = lines[i]
                if not cur.strip():
                    code_lines.append("")
                    i += 1
                    continue
                cur_indent = len(cur) - len(cur.lstrip())
                if cur_indent < body_indent:
                    break
                code_lines.append(cur[body_indent:])
                i += 1
            code_str = "\n".join(code_lines).rstrip()
            digest = hashlib.sha256(f"stl\n{code_str}".encode()).hexdigest()[:16]
            blocks.append((digest, code_str))
        else:
            i += 1
    return blocks


def extract_example_blocks() -> list[tuple[str, str, str]]:
    """Return list of (source_file, digest, code_str)."""
    import ast

    blocks: list[tuple[str, str, str]] = []
    seen_digests: set[str] = set()

    for rst_path in sorted((ROOT / "docs").glob("*.rst")):
        text = rst_path.read_text(encoding="utf-8")
        for digest, code_str in _extract_blocks_from_text(text):
            if digest not in seen_digests:
                seen_digests.add(digest)
                blocks.append((rst_path.relative_to(ROOT).as_posix(), digest, code_str))

    for py_path in sorted((ROOT / "pyboxbuilder").glob("**/*.py")):
        try:
            tree = ast.parse(py_path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        docstrings: list[str] = []
        mod_doc = ast.get_docstring(tree)
        if mod_doc:
            docstrings.append(mod_doc)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                d = ast.get_docstring(node)
                if d:
                    docstrings.append(d)
        for d in docstrings:
            for digest, code_str in _extract_blocks_from_text(d):
                if digest not in seen_digests:
                    seen_digests.add(digest)
                    blocks.append((py_path.relative_to(ROOT).as_posix(), digest, code_str))

    return blocks


def main() -> int:
    """Scan docs, extract code blocks, and render missing/changed STLs."""
    binary = find_pythonscad_binary()
    if binary is None:
        print("ERROR: No PythonSCAD binary found. Set PYTHONSCAD_BIN or install PythonSCAD.app.", file=sys.stderr)
        return 1

    print(f"Using PythonSCAD binary: {binary}")
    _STL_DIR.mkdir(parents=True, exist_ok=True)
    blocks = extract_example_blocks()
    print(f"Found {len(blocks)} unique documentation example blocks.")

    written = 0
    skipped = 0
    failed = 0

    for source_file, digest, code_str in blocks:
        out_stl = _STL_DIR / f"{digest}.stl"
        candidate = out_stl.with_name(f".{out_stl.stem}.tmp.stl")

        indented = "\n".join(f"    {line}" if line else "" for line in code_str.splitlines())
        script = _PREAMBLE + indented + "\n" + _POSTAMBLE

        # If file exists on disk, we still test geometry when candidate renders:
        try:
            res = render_stl_script(script, candidate, timeout=300.0, export_format="binstl")
        except Exception as exc:
            print(f"  FAILED: {digest} from {source_file}: {exc}", file=sys.stderr)
            failed += 1
            candidate.unlink(missing_ok=True)
            continue

        if not res.ok:
            print(f"  FAILED: {digest} from {source_file}: {res.error}", file=sys.stderr)
            if res.stderr:
                print(f"    stderr: {res.stderr.strip()}", file=sys.stderr)
            failed += 1
            candidate.unlink(missing_ok=True)
            continue

        if out_stl.exists() and same_geometry(
            read_stl_geometry(candidate), read_stl_geometry(out_stl)
        ):
            candidate.unlink(missing_ok=True)
            skipped += 1
            print(f"  UNCHANGED: {digest}.stl ({source_file})")
        else:
            candidate.replace(out_stl)
            written += 1
            print(f"  WRITTEN:   {digest}.stl ({source_file}) [{out_stl.stat().st_size} bytes]")

    print(f"\nDone: {written} written, {skipped} unchanged, {failed} failed.")
    return 1 if failed > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
