# SPDX-License-Identifier: Apache-2.0
"""SlidingBoxBuilder — typed builder for sliding lid boxes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder, SlidingLidFields
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class SlidingBoxBuilder(SlidingLidFields, BoxBuilder):
    """Builder for sliding-lid box type.

    Example:
        .. pythonscad-example::

            project = Project("SlidingDemo", game_box_size=(80.0, 80.0, 30.0))
            project.box(
                BoxType.SLIDING,
                "Tokens",
                size=(60.0, 60.0, 22.0),
                lid=LidBuilder(
                    pattern=PatternBuilder(PatternType.HEX),
                    text="TOKENS",
                ),
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.SLIDING

    catch_radius: float | None = None
    """Bump-catch radius, or `None` for a plain sliding lid (FR-002e3).

    A sliding box has no catch by default — the dovetail already stops the lid
    lifting out, and it can only leave by being slid. Set this to add the
    bump-and-dimple detent at the outlet (never a wedge at the stop end); a
    box that wants one as standard is a `SLIDING_CATCH` instead.
    """
