# SPDX-License-Identifier: Apache-2.0
"""One entry point for an example script: preview it, or export it.

Every example under `boxes/` ended with the same twelve lines — read
``FROM_MAKE``, branch, call ``export`` or ``show``, print the written files —
copied verbatim seven times. That is the "no extra steps between describe,
build, preview and export" rule (FR-000d) being met by repetition rather than
by the library, and it drifted: some examples printed their piece bounds and
some did not, some counted skipped files and some did not.

It also takes the arguments you want while working on one box::

    python3 boxes/emberleaf/emberleaf.py --box CommonBox --lids
    python3 boxes/emberleaf/emberleaf.py --box CardBoxFavor --lids-only
    python3 boxes/emberleaf/emberleaf.py --export --box CommonBox
"""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyboxbuilder.export.result import ExportResult
    from pyboxbuilder.project import Project

FROM_MAKE_ENV = "FROM_MAKE"
"""Set to ``1`` by the build to ask for files rather than a preview."""

DEFAULT_OUT_DIR = "output/"
"""Where :func:`run` writes when the caller names no directory."""


def _parser(default_out: str) -> argparse.ArgumentParser:
    """Return the arguments an example accepts."""
    parser = argparse.ArgumentParser(
        description="Preview this insert, or export its printable files.",
    )
    parser.add_argument(
        "--export", action="store_true",
        help="write files instead of previewing (implied by FROM_MAKE=1)",
    )
    parser.add_argument(
        "--out", default=default_out, metavar="DIR",
        help=f"where an export writes (default: {default_out})",
    )
    parser.add_argument(
        "--box", action="append", default=[], metavar="LABEL",
        help="only this box; repeat for several",
    )
    parser.add_argument(
        "--lids", action="store_true",
        help="show the lids as well as the bodies",
    )
    parser.add_argument(
        "--lids-only", action="store_true",
        help="show the lids without their bodies — for checking a label",
    )
    parser.add_argument(
        "--remove-layers", type=int, default=0, metavar="N",
        help="omit the top N layers, to see underneath",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="on export, rebuild every piece even if nothing changed",
    )
    parser.add_argument(
        "--fn", type=int, default=None, metavar="FACETS",
        help="facets per circle; export defaults to print quality (256)",
    )
    return parser


def run(
    project: Project,
    out_dir: str | Path = DEFAULT_OUT_DIR,
    *,
    show_lids: bool = False,
    argv: Sequence[str] | None = None,
) -> None:
    """Preview a project, or export it when asked for files.

    Put this under an example's ``if __name__ == "__main__":`` and the same
    file does the right thing in the PythonSCAD GUI, in a notebook, under make,
    and on the command line::

        if __name__ == "__main__":
            run(project)

    Args:
        project: The project to preview or export.
        out_dir: Where an export writes; files land under
            ``{out_dir}/{project name}/``. ``--out`` overrides it.
        show_lids: Show lids by default in a preview. Off by default, since a
            lid covers the compartments a packing preview exists to show;
            ``--lids`` turns it on for one run.
        argv: Command-line arguments; ``None`` reads ``sys.argv``.

    Raises:
        SystemExit: If the arguments are malformed, as argparse does.

    """
    args = _parser(str(out_dir)).parse_args(sys.argv[1:] if argv is None else argv)
    only = args.box or None

    if args.export or os.environ.get(FROM_MAKE_ENV) == "1":
        result = project.export(args.out, fn=args.fn, only=only, force=args.force)
        _report(project, result)
        return

    project.show(
        show_lids=show_lids or args.lids,
        lids_only=args.lids_only,
        remove_layers=args.remove_layers,
        only=only,
        fn=args.fn,
    )


def _report(project: Project, result: ExportResult) -> None:
    """Print what an export did."""
    print(
        f"{project.name}: {result.total_files} files "
        f"({len(result.written)} written, {len(result.skipped)} unchanged)"
    )
    for path in result.written:
        print(f"  + {path}")
    for bounds in project.piece_bounds:
        print(f"    {bounds}")
