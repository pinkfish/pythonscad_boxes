# SPDX-License-Identifier: Apache-2.0
"""Hard dependencies, and what to say when one is missing.

The library used to answer a missing dependency by producing **nothing**: an
absent geometry backend returned ``None`` from the builders, ``False`` from the
exporter, and an export that wrote no files and reported success. A user with a
broken install got a silent no-op and no way to tell it from "this project has
nothing in it" (FR-000h).

None of these are optional. pybosl2 and openscad are how every solid in the
library is built and written; fpdf is how the layout sheet is drawn. So a
missing one raises here, naming the package, what it was needed for, and how to
install it — the three things a user needs to fix it.
"""

from __future__ import annotations

import importlib
from types import ModuleType

__all__ = ["MissingDependencyError", "require"]


INSTALL_HINTS = {
    "pybosl2": "pip install pybosl2",
    "openscad": (
        "run this through the PythonSCAD application, which provides it — "
        "it is not a PyPI package"
    ),
    "fpdf": "pip install fpdf2",
}
"""How to get each dependency. A package whose import name is not its install
name, or which is not on PyPI at all, is exactly where a user gets stuck."""


class MissingDependencyError(ImportError):
    """A dependency the library cannot work without is not installed.

    Subclasses :class:`ImportError` so existing ``except ImportError`` handlers
    still catch it, and carries a message that says how to fix it.
    """


def require(module: str, purpose: str) -> ModuleType:
    """Import a hard dependency, or explain what is missing.

    Args:
        module: The import name, e.g. ``"pybosl2"``.
        purpose: What the caller needed it for, as a verb phrase — it finishes
            the sentence "pyboxbuilder needs *module* to …". This is what tells
            a user which part of their project stopped working.

    Returns:
        The imported module.

    Raises:
        MissingDependencyError: If it is not installed.

    """
    try:
        return importlib.import_module(module)
    except ImportError as exc:
        hint = INSTALL_HINTS.get(module, f"pip install {module}")
        raise MissingDependencyError(
            f"pyboxbuilder needs {module} to {purpose}, and it is not "
            f"installed. To fix: {hint}."
        ) from exc
