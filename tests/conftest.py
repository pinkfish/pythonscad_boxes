# SPDX-License-Identifier: Apache-2.0
"""pytest configuration and hooks."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

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
    "test_presets.py",
}


@lru_cache(maxsize=1)
def get_box_example_names() -> set[str]:
    """Return the set of game directory names in the boxes/ folder."""
    repo_root = Path(__file__).resolve().parent.parent
    boxes_dir = repo_root / "boxes"
    if not boxes_dir.is_dir():
        return set()
    return {d.name for d in boxes_dir.iterdir() if d.is_dir() and not d.name.startswith("_")}


def is_box_example_path(path: str | Path) -> bool:
    """Return True if path represents a game box insert test suite."""
    p = Path(str(path))
    if not p.name.endswith(".py"):
        return False
    if p.name in ("test_ci_smoke.py", "test_quickstart.py"):
        return True
    box_names = get_box_example_names()
    cand = p.stem.replace("test_", "")
    return cand in box_names


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register custom CLI options."""
    parser.addoption(
        "--base-only",
        action="store_true",
        default=False,
        help="Run only pyboxbuilder base tests, skipping game box insert tests in boxes/ and test_ci_smoke.py",
    )


def pytest_ignore_collect(collection_path: Path, config: pytest.Config) -> bool | None:
    """Skip game box insert tests when --base-only is active."""
    if config.getoption("--base-only", default=False) and is_box_example_path(collection_path):
        return True
    return None


def pytest_collection_modifyitems(config: pytest.Config, items: list[pytest.Item]) -> None:
    """Dynamically assign markers to tests based on whitelist and box detection."""
    base_only = config.getoption("--base-only", default=False)
    deselected = []
    selected = []
    for item in items:
        filename = os.path.basename(item.fspath.strpath)
        if filename in FAST_FILES:
            item.add_marker(pytest.mark.fast)
        else:
            item.add_marker(pytest.mark.render)
        if is_box_example_path(item.fspath.strpath):
            item.add_marker(pytest.mark.box_example)
            if base_only:
                deselected.append(item)
                continue
        selected.append(item)

    if deselected:
        config.hook.pytest_deselected(items=deselected)
        items[:] = selected
