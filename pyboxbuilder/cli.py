# SPDX-License-Identifier: Apache-2.0
"""`pybox` — build the printable files for one insert, or all of them.

The manually-triggered, print-quality path. `export()` defaults to 256 facets
per circle because that is the geometry that gets printed (FR-046), and at that
precision a full build is minutes rather than seconds — so this is a command you
run when you want files, not something a preview does behind your back.

It is incremental the way make is, and for the same reason: a box whose
description has not changed is not rebuilt at all. The digest that decides that
(FR-031) is known before any geometry is cut, so a repeat run over an insert
with one edited box pays for that box and nothing else.

    pybox export boxes/emberleaf/emberleaf.py
    pybox export --all --out output/
    pybox export boxes/earth/earth.py --box EarthCardBox1
    pybox list boxes/emberleaf/emberleaf.py
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING, Iterator, Sequence

if TYPE_CHECKING:
    from pyboxbuilder.project import Project

EXAMPLES_DIR = "boxes"
"""Where `--all` looks for inserts, relative to the working directory."""


def load_project(path: Path) -> "Project":
    """Import an insert script and hand back the `Project` it defines.

    The script builds its project at import time and guards its own entry point
    with ``if __name__ == "__main__"``, so importing it is enough — and does not
    trigger an export of its own (see *Examples Must Run In Both Plain Python
    and Jupyter* in the plan).

    Args:
        path: The insert script.

    Returns:
        The project it defines.

    Raises:
        ValueError: If the module defines no `Project`, or more than one, so
            there is nothing (or no one thing) to build.
        ImportError: If the module cannot be imported.
    """
    from pyboxbuilder.project import Project

    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"{path} is not an importable Python module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    found = [v for v in vars(module).values() if isinstance(v, Project)]
    if not found:
        raise ValueError(f"{path} defines no Project")
    if len(found) > 1:
        names = ", ".join(sorted(p.name for p in found))
        raise ValueError(f"{path} defines more than one Project: {names}")
    return found[0]


def find_examples(root: Path) -> Iterator[Path]:
    """Every insert script under `root`, in a stable order.

    A directory's script is the one named after it — `boxes/earth/earth.py` —
    which is the convention every example already follows, and it keeps helper
    modules beside an insert from being mistaken for one.

    Args:
        root: The directory to search, usually `boxes/`.

    Yields:
        Each insert script.
    """
    for directory in sorted(p for p in root.iterdir() if p.is_dir()):
        if directory.name.startswith((".", "_")):
            continue
        script = directory / f"{directory.name}.py"
        if script.exists():
            yield script


def _export(args: argparse.Namespace) -> int:
    """Run the export for every named insert."""
    paths = list(_targets(args))
    if not paths:
        print("nothing to export", file=sys.stderr)
        return 1

    failures = 0
    for path in paths:
        started = time.monotonic()
        try:
            project = load_project(path)
            result = project.export(
                args.out, fn=args.fn,
                only=args.box or None, force=args.force,
            )
        except Exception as exc:  # noqa: BLE001 — one bad insert must not stop the rest
            print(f"{path}: {type(exc).__name__}: {exc}", file=sys.stderr)
            failures += 1
            continue

        elapsed = time.monotonic() - started
        print(
            f"{project.name}: {len(result.written)} written, "
            f"{len(result.skipped)} unchanged  ({elapsed:.1f}s)"
        )
        if args.verbose:
            for written in result.written:
                print(f"  + {written}")

    return 1 if failures else 0


def _list(args: argparse.Namespace) -> int:
    """Print each insert's boxes, so `--box` has something to name."""
    for path in _targets(args):
        project = load_project(path)
        print(f"{project.name}  ({path})")
        for builder in project._boxes:
            size = builder.size or ("auto", "auto", "auto")
            shown = " x ".join(
                "auto" if v is None or v == "auto" else f"{float(v):g}" for v in size
            )
            print(f"  {builder.label:<28} {builder.box_type.value:<16} {shown}")
    return 0


def _targets(args: argparse.Namespace) -> Iterator[Path]:
    """The insert scripts this invocation names."""
    if args.all:
        yield from find_examples(Path(args.examples))
    for name in args.script:
        yield Path(name)


def build_parser() -> argparse.ArgumentParser:
    """The `pybox` command line."""
    parser = argparse.ArgumentParser(
        prog="pybox",
        description="Build printable files for a board game insert.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p: argparse.ArgumentParser) -> None:
        p.add_argument("script", nargs="*", help="insert script(s) to build")
        p.add_argument(
            "--all", action="store_true",
            help=f"every insert under {EXAMPLES_DIR}/",
        )
        p.add_argument(
            "--examples", default=EXAMPLES_DIR, metavar="DIR",
            help=f"where --all looks (default: {EXAMPLES_DIR})",
        )

    export = sub.add_parser(
        "export",
        help="write 3MF files and the layout guide, at print quality",
        description=(
            "Writes at 256 facets per circle by default — the precision an "
            "export is for. Only the boxes whose description changed are "
            "rebuilt, so running it again after one edit is quick."
        ),
    )
    common(export)
    export.add_argument("--out", default="output/", metavar="DIR", help="output directory")
    export.add_argument(
        "--box", action="append", default=[], metavar="LABEL",
        help="only this box; repeat for several",
    )
    export.add_argument(
        "--force", action="store_true",
        help="rebuild every piece, changed or not",
    )
    export.add_argument(
        "--fn", type=int, default=None, metavar="FACETS",
        help="facets per circle (default: 256, print quality)",
    )
    export.add_argument("-v", "--verbose", action="store_true", help="list every file written")
    export.set_defaults(func=_export)

    listing = sub.add_parser("list", help="list an insert's boxes")
    common(listing)
    listing.set_defaults(func=_list)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point for the `pybox` console script.

    Args:
        argv: Arguments; ``None`` reads ``sys.argv``.

    Returns:
        A process exit status: 0 when every insert built.
    """
    args = build_parser().parse_args(argv)
    if not args.script and not args.all:
        print("name an insert script, or pass --all", file=sys.stderr)
        return 1
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
