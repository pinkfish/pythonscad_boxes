# SPDX-License-Identifier: Apache-2.0
"""A `BoxSpec` for tests that only care about a few of its fields.

`BoxSpec` requires a size, because a box without one is not a box. Most tests
here are about one derived number — a rounding radius, a wall's top — and the
size is noise, so this supplies a plausible one.
"""

from __future__ import annotations

from pyboxbuilder.box.spec import BoxSpec


def spec(**overrides) -> BoxSpec:
    """A 100 x 80 x 40mm box, with any field overridden.

    Args:
        **overrides: Any :class:`BoxSpec` field.

    Returns:
        The assembled spec.
    """
    return BoxSpec(**{"width": 100.0, "length": 80.0, "height": 40.0, **overrides})
