# SPDX-License-Identifier: Apache-2.0
"""DiceTrayBoxBuilder — typed builder for dice tray and rolling arena boxes."""

from dataclasses import dataclass
from typing import Any, ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType


@dataclass(frozen=True)
class DiceTrayBoxBuilder(BoxBuilder):
    """Builder for dice tray & rolling arena box type (FR-086).

    A dual-purpose container where the body stores dice or components and the
    deep nesting lid doubles as an active tabletop dice rolling arena.
    Features 25mm+ arena walls, 45° corner deflector fillets to bounce dice back
    toward the center, and a recessed felt pad pocket.

    Example:
        .. pythonscad-example::

            project = Project("DiceTrayDemo")
            project.box(
                BoxType.DICE_TRAY,
                "RollingArena",
                size=(180.0, 130.0, 45.0),
                arena_wall_height=28.0,
                felt_pocket_depth=1.2,
                corner_deflectors=True,
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.DICE_TRAY
    arena_wall_height: float = 28.0
    """Height of the rolling arena walls in mm (MUST be >= 25.0mm)."""
    felt_pocket_depth: float = 1.2
    """Depth of the acoustic felt/leatherette pad recess in mm."""
    corner_deflectors: bool = True
    """Add 45° corner deflector fillets to bounce rolling dice inward."""

    def __post_init__(self) -> None:
        """Configure default lid with multi-material text title and inlaid dice pattern."""
        if self.lid is None:
            from pybosl2 import Color

            from pyboxbuilder.enums import LabelMode, PatternType
            from pyboxbuilder.lid.builder import LidBuilder, PatternBuilder

            object.__setattr__(
                self,
                "lid",
                LidBuilder(
                    text=self.label,
                    text_color=Color("gold"),
                    label_mode=LabelMode.FRAMELESS,
                    label_clearance_mm=3.0,
                    pattern=PatternBuilder(PatternType.DICE, spacing=14.0, inlay=True),
                    pattern_color=Color("white"),
                ),
            )
        else:
            from dataclasses import replace

            from pybosl2 import Color

            updates: dict[str, Any] = {}
            if self.lid.text is None:
                updates["text"] = self.label
            if self.lid.text_color is None:
                updates["text_color"] = Color("gold")
            if self.lid.pattern is not None and not self.lid.pattern.inlay:
                updates["pattern"] = replace(self.lid.pattern, inlay=True)
            if self.lid.pattern_color is None:
                updates["pattern_color"] = Color("white")
            if updates:
                object.__setattr__(self, "lid", replace(self.lid, **updates))
