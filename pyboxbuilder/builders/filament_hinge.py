# SPDX-License-Identifier: Apache-2.0
"""FilamentHingeBoxBuilder — typed builder for living-hinge lid boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType, HingeCatchType


@dataclass(frozen=True)
class FilamentHingeBoxBuilder(BoxBuilder):
    """Builder for filament (living) hinge lid box type.

    Example:
        .. pythonscad-example::

            project = Project("FilamentHingeDemo")
            project.box(
                BoxType.FILAMENT_HINGE,
                "PinBox",
                size=(60.0, 50.0, 22.0),
                hinge_catch_type=HingeCatchType.RIDGE,
                lid=LidBuilder(text="GEAR"),
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.FILAMENT_HINGE
    hinge_catch_type: HingeCatchType = HingeCatchType.RIDGE
    """Catch type for hinged boxes (FR-106); HingeCatchType.RIDGE, BUMP, or NONE."""

    def __post_init__(self) -> None:
        """Coerce hinge_catch_type string or validate enum instance."""
        if isinstance(self.hinge_catch_type, str):
            try:
                object.__setattr__(
                    self, "hinge_catch_type", HingeCatchType(self.hinge_catch_type.lower())
                )
            except ValueError:
                valid = [e.value for e in HingeCatchType]
                raise ValueError(
                    f"Invalid hinge_catch_type '{self.hinge_catch_type}'. "
                    f"Must be HingeCatchType enum member: {valid}"
                ) from None
        elif not isinstance(self.hinge_catch_type, HingeCatchType):
            raise TypeError(
                f"hinge_catch_type must be a HingeCatchType enum, got {type(self.hinge_catch_type).__name__}"
            )
        super().__post_init__()

