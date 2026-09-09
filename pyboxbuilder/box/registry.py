# SPDX-License-Identifier: Apache-2.0
"""Box type registry — maps BoxType enum to implementation classes (FR-094)."""

from __future__ import annotations

import importlib
import pkgutil
from typing import TYPE_CHECKING, Any

from pyboxbuilder.enums import BoxType

if TYPE_CHECKING:
    from pyboxbuilder.box.base import BoxTypeBase

_DISCOVERED = False


def ensure_registered() -> None:
    """Discover and register all box type implementations in pyboxbuilder.box.types."""
    global _DISCOVERED
    if _DISCOVERED:
        return
    _DISCOVERED = True
    import pyboxbuilder.box.types as types_pkg

    for _, module_name, _ in pkgutil.iter_modules(types_pkg.__path__):
        importlib.import_module(f"pyboxbuilder.box.types.{module_name}")


class _RegistryDict(dict[Any, Any]):
    """Dictionary that triggers package discovery on first lookup."""

    def __getitem__(self, key: Any) -> Any:
        ensure_registered()
        return super().__getitem__(key)

    def __contains__(self, key: Any) -> bool:
        ensure_registered()
        return super().__contains__(key)

    def get(self, key: Any, default: Any = None) -> Any:
        ensure_registered()
        return super().get(key, default)

    def items(self) -> Any:
        ensure_registered()
        return super().items()

    def values(self) -> Any:
        ensure_registered()
        return super().values()

    def keys(self) -> Any:
        ensure_registered()
        return super().keys()

    def __iter__(self) -> Any:
        ensure_registered()
        return super().__iter__()

    def __len__(self) -> int:
        ensure_registered()
        return super().__len__()


BOX_TYPE_REGISTRY: dict[BoxType, type] = _RegistryDict()
"""Maps BoxType enum members to their BoxBuilder subclass."""

BOX_IMPL_REGISTRY: dict[BoxType, type[BoxTypeBase]] = _RegistryDict()
"""Maps BoxType enum members to their BoxTypeBase implementation."""


def register_box(
    box_type: BoxType,
    builder: type | None = None,
    box_class: type | None = None,
) -> Any:
    """Register a box type with its builder and implementation class (FR-094).

    Supports decorator usage::

        @register_box(BoxType.CAP, builder=CapBoxBuilder)
        class CapBox(BoxTypeBase):
            ...

    Or direct invocation::

        register_box(BoxType.CAP, builder=CapBoxBuilder, box_class=CapBox)

    Args:
        box_type: The :class:`~pyboxbuilder.enums.BoxType` enum member.
        builder: The :class:`~pyboxbuilder.builders._base.BoxBuilder` subclass.
        box_class: The :class:`~pyboxbuilder.box.base.BoxTypeBase` implementation class.

    Returns:
        A class decorator if ``box_class`` is not provided, or None.
    """
    def decorator(cls: type) -> type:
        dict.__setitem__(BOX_IMPL_REGISTRY, box_type, cls)
        if builder is not None:
            dict.__setitem__(BOX_TYPE_REGISTRY, box_type, builder)
        return cls

    if box_class is not None:
        dict.__setitem__(BOX_IMPL_REGISTRY, box_type, box_class)
        if builder is not None:
            dict.__setitem__(BOX_TYPE_REGISTRY, box_type, builder)
        return None

    return decorator


LIDLESS_BOX_TYPES: frozenset[BoxType] = frozenset({
    BoxType.NO_LID,
    BoxType.PATH,
    BoxType.PRINT_IN_PLACE_HINGE,
})
"""Box types that produce a body file only — no lid geometry, no `_lid.3mf`."""
