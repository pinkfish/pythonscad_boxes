# SPDX-License-Identifier: Apache-2.0
"""SlidingHingeBoxBuilder — typed builder for hinged lid boxes with sliding/rotary catches."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType, CatchType, HingeCatchType


@dataclass(frozen=True)
class SlidingHingeBoxBuilder(BoxBuilder):
    """Builder for hinged lid box with a captive sliding or rotary spin catch (``BoxType.SLIDING_HINGE``).

    Combines a filament-pin knuckle hinge along the back edge with a print-in-place
    mechanical retention catch — defaulting to a captive horizontal dovetail sliding
    bolt (``CatchType.SLIDE_ACROSS``), with support for ``CatchType.SLIDE_UP``,
    ``CatchType.SPIN`` (rotary turn-button cam catch), ``CatchType.PUSH_BUTTON``,
    ``CatchType.TOGGLE_LATCH``, ``CatchType.PINCH_SLIDE``, and ``CatchType.ROTARY_BOLT``,
    as well as dual side-wall card-library sliding latches (``slide_catch_style="card_library"``).

    Example:
        .. pythonscad-example::

            project = Project("SlidingHingeDemo")
            project.box(
                BoxType.SLIDING_HINGE,
                "SlidingHingeDeck",
                size=(70.0, 55.0, 26.0),
                catch_type=CatchType.SLIDE_ACROSS,
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.SLIDING_HINGE
    hinge_count: int | None = None
    """Knuckles across the rear filament hinge; ``None`` uses default (5)."""
    filament_diameter: float | None = None
    """Pin/filament stock diameter in mm; ``None`` uses default (1.75mm)."""
    catch_type: CatchType | None = CatchType.SLIDE_ACROSS
    """Retention catch mechanism (SLIDE_ACROSS, SLIDE_UP, SPIN, PUSH_BUTTON, TOGGLE_LATCH, PINCH_SLIDE, ROTARY_BOLT)."""
    hinge_catch_type: HingeCatchType = HingeCatchType.SLIDE_ACROSS
    """Hinge catch mechanism enum fallback."""
    slide_catch_style: str = "front"
    """Placement style for ``SLIDE_ACROSS`` (``'front'`` single front bolt or ``'card_library'`` dual side bolts)."""
    pip_radial_clearance: float = 0.28
    """Print-in-place clearance in mm for captive sliding or spinning catch parts."""

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
        if self.slide_catch_style not in ("front", "card_library", "up"):
            raise ValueError(
                f"Invalid slide_catch_style '{self.slide_catch_style}'. "
                "Must be 'front', 'card_library', or 'up'."
            )
        if (
            self.slide_catch_style == "up"
            and self.catch_type == CatchType.SLIDE_ACROSS
        ):
            object.__setattr__(self, "catch_type", CatchType.SLIDE_UP)
        super().__post_init__()
