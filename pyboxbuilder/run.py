# SPDX-License-Identifier: Apache-2.0
"""One entry point for an example script: preview it, or export it.

Every example under `boxes/` ended with the same twelve lines — read
``FROM_MAKE``, branch, call ``export`` or ``show``, print the written files —
copied verbatim seven times. That is the "no extra steps between describe,
build, preview and export" rule (FR-000d) being met by repetition rather than
by the library, and it drifted: some examples printed their piece bounds and
some did not, some counted skipped files and some did not.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyboxbuilder.project import Project

FROM_MAKE_ENV = "FROM_MAKE"
"""Set to ``1`` by the build to ask for files rather than a preview."""

DEFAULT_OUT_DIR = "output/"
"""Where :func:`run` writes when the caller names no directory."""


def run(
    project: "Project",
    out_dir: str | Path = DEFAULT_OUT_DIR,
    *,
    show_lids: bool = False,
) -> None:
    """Preview a project, or export it when the build asks for files.

    Put this under an example's ``if __name__ == "__main__":`` and the same
    file does the right thing in the PythonSCAD GUI, in a notebook and under
    make::

        if __name__ == "__main__":
            run(project)

    Args:
        project: The project to preview or export.
        out_dir: Where an export writes; files land under
            ``{out_dir}/{project name}/``.
        show_lids: Include the lids in a preview. Off by default, since a lid
            covers the compartments a packing preview exists to show.
    """
    if os.environ.get(FROM_MAKE_ENV) != "1":
        project.show(show_lids=show_lids)
        return

    result = project.export(out_dir)
    print(
        f"{project.name}: {result.total_files} files "
        f"({len(result.written)} written, {len(result.skipped)} unchanged)"
    )
    for path in result.written:
        print(f"  + {path}")
    for bounds in project.piece_bounds:
        print(f"    {bounds}")
