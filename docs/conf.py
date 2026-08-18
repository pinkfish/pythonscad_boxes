# SPDX-License-Identifier: Apache-2.0
"""Sphinx configuration for the pyboxbuilder documentation.

The docs are generated from the docstrings (autodoc + autosummary), so there is
no hand-maintained API reference. The ``sphinx_immaterial`` theme provides the
left-hand site navigation and the right-hand "on this page" table of contents.
"""

import os
import sys
from pathlib import Path

_DOCS_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _DOCS_DIR.parent

# Let autodoc import the package from the repo root, and Sphinx import the
# local extensions (stl_viewer, pyboxbuilder_example) from docs/_ext.
sys.path.insert(0, str(_REPO_ROOT))
sys.path.insert(0, str(_DOCS_DIR / "_ext"))

project = "pyboxbuilder"
author = "pinkfish"
copyright = "pyboxbuilder contributors"

# The version comes from the tag (setuptools_scm) when installed, or from the
# PYBOXBUILDER_VERSION env var set by the docs workflow (release tag vs "dev").
def _release() -> str:
    env = os.environ.get("PYBOXBUILDER_VERSION")
    if env:
        return env
    try:
        from importlib.metadata import version as _distribution_version

        return _distribution_version("pyboxbuilder")
    except Exception:
        return "dev"


release = _release()
version = release.split("+")[0]

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx.ext.autosectionlabel",
    # The theme itself must be listed as an extension (not just html_theme) so
    # its apidoc integrations — which monkey-patch the Python domain's
    # `initial_data` for synopses — run before the domain is instantiated.
    "sphinx_immaterial",
    "stl_viewer",
    "pyboxbuilder_example",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "_extra"]

# The Material-for-MkDocs-style theme: left nav + right "on this page".
html_theme = "sphinx_immaterial"
html_title = "pyboxbuilder"
html_static_path = ["_static"]
# The exported STL meshes live in _extra/_stl/; listing the parent copies the
# whole _stl/ subdir verbatim to the output root, keeping `_stl/<hash>.stl` URIs valid.
html_extra_path = ["_extra"]
html_theme_options = {
    "features": [
        "navigation.top",
        "content.code.copy",
        "search.highlight",
        "toc.follow",
        "toc.sticky",
    ],
    "repo_url": "https://github.com/pinkfish/pythonscad_boxes",
    "repo_name": "pinkfish/pythonscad_boxes",
    "icon": {
        "repo": "fontawesome/brands/github",
    },
    "toc_title": "On this page",
    # No Google Fonts: the docs must build offline and without font downloads.
    "font": False,
}

# Which autodoc objects appear in the right-hand "on this page" TOC. Methods,
# functions and classes are the navigation the user asked for; parameters,
# attributes, data and modules would only add noise.
object_description_options = [
    ("py:parameter", {"include_in_toc": False}),
    ("py:.*Param", {"include_in_toc": False}),
    ("py:attribute", {"include_in_toc": False}),
    ("py:data", {"include_in_toc": False}),
    ("py:exception", {"include_in_toc": False}),
    ("py:module", {"include_in_toc": False}),
    ("py:class", {"include_in_toc": True}),
    ("py:function", {"include_in_toc": True}),
    ("py:method", {"include_in_toc": True}),
]

# --- autodoc ---------------------------------------------------------------
# Types go in the signature, not a separate line, and members are grouped by
# kind (methods together) so the right-hand TOC reads naturally.
autodoc_typehints = "signature"
autodoc_member_order = "groupwise"
autoclass_content = "both"
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}

# --- autosummary -----------------------------------------------------------
# Generate one page per module/class/function so the right sidebar lists links
# to each method.
autosummary_generate = True
autosummary_imported_members = False

# --- napoleon --------------------------------------------------------------
# The codebase documents with Google-style Args:/Returns: sections.
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True

# --- intersphinx -----------------------------------------------------------
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}

# --- suppress warnings -----------------------------------------------------
# Names re-exported at the package top level (``pyboxbuilder.ScoopSide``) and
# at their defining module (``pyboxbuilder.enums.ScoopSide``) are documented
# twice, so a short-name reference resolves to two targets. Sphinx picks one
# and the doc is correct; the ambiguity is noise. Broken references are a
# different warning type (``ref.class``/``ref.meth``/…), so they are still
# caught by the build's "reference target not found" check.
suppress_warnings = ["ref.python"]

# --- linkcheck -------------------------------------------------------------
# The ``pythonscad-example`` blocks emit relative ``_stl/<hash>.stl`` download
# links to meshes generated at build time; those are assets, not links to
# verify, so linkcheck must not try to resolve them.
linkcheck_ignore = [r"_stl/"]

# --- nitpicky --------------------------------------------------------------
# Make every unresolved cross-reference an error, so a broken :class:/:meth:/
# :ref: link in a docstring fails the build instead of slipping by as a warning.
nitpicky = True

# References that can never resolve — pybosl2/fpdf ship no inventory, pathlib
# and fpdf types are external, and the builders in the private ``_base`` module
# are not part of the documented API — are whitelisted so a real typo in a link
# to the public API still fails the build.
nitpick_ignore = [
    # pybosl2 geometry types (no py.typed, no intersphinx inventory).
    ("py:class", "Bosl2Solid"),
    ("py:class", "Bosl2Shape2D"),
    ("py:class", "Anchor"),
    ("py:class", "OSProfile"),
    ("py:class", "pybosl2.Color"),
    ("py:meth", "Path2D.offset_sweep"),
    # External stdlib / third-party types.
    ("py:class", "Path"),
    ("py:class", "FPDF"),
    # Builders in the private builders._base module are not documented.
    ("py:class", "BoxBuilder"),
    ("py:class", "pyboxbuilder.builders._base.BoxBuilder"),
    ("py:class", "FingerHoleBuilder"),
    ("py:class", "pyboxbuilder.builders._base.SlidingLidFields"),
    # Module-level constants referenced by name, not part of the API reference.
    ("py:data", "DEFAULT_THROAT_RADIUS_MM"),
    ("py:data", "MIN_TEXT_HEIGHT_MM"),
    ("py:data", "BORDER_MARGIN_MM"),
    ("py:data", "PATTERN_BORDER_MM"),
    # Short type-annotation names — classes imported under TYPE_CHECKING so
    # autodoc has no runtime name to link them to.
    ("py:class", "CompartmentPlacement"),
    ("py:class", "pyboxbuilder.compartments.layout.CompartmentPlacement"),
    ("py:obj", "pyboxbuilder.compartments.layout.CompartmentPlacement"),
    ("py:class", "Node"),
    ("py:class", "Build"),
    ("py:class", "ExportResult"),
    ("py:class", "CutProfile"),
    ("py:class", "CompartmentBuilder"),
    ("py:class", "BoxPacking"),
    ("py:attr", "Piece.solid"),
]
