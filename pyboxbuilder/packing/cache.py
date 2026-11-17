# SPDX-License-Identifier: Apache-2.0
"""Two-level layout cache — in-memory LRU + user cache JSON with SHA-256 hash keys."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any


def _default_cache_path() -> Path:
    env_dir = os.environ.get("PYBOXBUILDER_CACHE_DIR")
    if env_dir:
        return Path(env_dir) / "layout_cache.json"
    return Path(tempfile.gettempdir()) / "pyboxbuilder" / "layout_cache.json"


CACHE_FILE = _default_cache_path()
"""Disk cache file path (stored outside the package source tree)."""

BGTK_VERSION = "2.0.0"
"""Version key for global cache invalidation on library changes."""

_MAX_MEMORY_ENTRIES = 256
_memory_cache: dict[str, Any] = {}
"""In-memory cache for instant re-access within a process."""


def cache_key(input_data: dict[str, Any]) -> str:
    """Generate a SHA-256 hash cache key from serialized input."""
    payload = dict(input_data)
    payload["bgtk_version"] = BGTK_VERSION
    serialized = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode()).hexdigest()


def load_cache() -> dict[str, Any]:
    """Load the disk cache into memory."""
    if not CACHE_FILE.exists():
        return {}
    try:
        with open(CACHE_FILE) as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def save_cache(cache: dict[str, Any]) -> None:
    """Save the cache dictionary to disk (best-effort on read-only environments)."""
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2, sort_keys=True)
    except OSError:
        pass


def get_cached(key: str) -> Any | None:
    """Get a cached value by key (checks memory first, then disk)."""
    if key in _memory_cache:
        return _memory_cache[key]

    disk_cache = load_cache()
    if key in disk_cache:
        if len(_memory_cache) >= _MAX_MEMORY_ENTRIES:
            _memory_cache.pop(next(iter(_memory_cache)))
        _memory_cache[key] = disk_cache[key]
        return disk_cache[key]

    return None


def set_cached(key: str, value: Any) -> None:
    """Store a value in both memory and disk cache."""
    if len(_memory_cache) >= _MAX_MEMORY_ENTRIES and key not in _memory_cache:
        _memory_cache.pop(next(iter(_memory_cache)))
    _memory_cache[key] = value

    disk_cache = load_cache()
    disk_cache[key] = value
    save_cache(disk_cache)


def get_memory_cached(key: str) -> Any | None:
    """Fast process-local lookup without disk I/O."""
    return _memory_cache.get(key)


def set_memory_cached(key: str, value: Any) -> None:
    """Fast process-local store without disk I/O."""
    if len(_memory_cache) >= _MAX_MEMORY_ENTRIES and key not in _memory_cache:
        _memory_cache.pop(next(iter(_memory_cache)))
    _memory_cache[key] = value


def layout_cache_clear() -> None:
    """Clear all caches (memory and disk)."""
    _memory_cache.clear()
    try:
        if CACHE_FILE.exists():
            CACHE_FILE.unlink()
    except OSError:
        pass
