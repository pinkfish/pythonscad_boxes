# SPDX-License-Identifier: Apache-2.0
"""pytest configuration and hooks."""

import os
import pytest

FAST_FILES = {
    "test_builders.py",
    "test_helpers.py",
    "test_layout.py",
    "test_packing.py",
    "test_precision.py",
    "test_enums.py",
    "test_project.py",
    "test_project_coverage.py",
    "test_outline_invariants.py",
}

def pytest_collection_modifyitems(config, items):
    """Dynamically assign markers to tests based on whitelist."""
    for item in items:
        filename = os.path.basename(item.fspath.strpath)
        if filename in FAST_FILES:
            item.add_marker(pytest.mark.fast)
        else:
            item.add_marker(pytest.mark.render)
