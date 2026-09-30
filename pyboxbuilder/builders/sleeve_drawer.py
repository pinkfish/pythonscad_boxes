# SPDX-License-Identifier: Apache-2.0
"""SleeveDrawerBoxBuilder — typed builder for matchbox-style sleeve & drawer boxes."""

from dataclasses import dataclass
from typing import ClassVar

from pyboxbuilder.builders._base import BoxBuilder
from pyboxbuilder.enums import BoxType, DrawerHandleStyle


@dataclass(frozen=True)
class SleeveDrawerBoxBuilder(BoxBuilder):
    """Builder for matchbox / sleeve & drawer box type (FR-087).

    A two-piece assembly consisting of a hollow 4-sided outer perimeter sleeve
    and an inner sliding compartment drawer. Enables horizontal drawer access
    without lifting stacked trays above it.

    Example:
        .. pythonscad-example::

            project = Project("SleeveDrawerDemo")
            project.box(
                BoxType.SLEEVE_DRAWER,
                "ResourceDrawer",
                size=(80.0, 70.0, 35.0),
                drawer_handle_style=DrawerHandleStyle.HANDLE,
                drawer_handle_length=4.0,
            )
            project.show(show_lids=True)
    """

    box_type: ClassVar[BoxType] = BoxType.SLEEVE_DRAWER
    push_hole_radius: float = 0.0
    """Radius of the finger push-through hole on the sleeve back wall in mm, default 0.0 for solid back."""
    drawer_handle_style: DrawerHandleStyle = DrawerHandleStyle.HANDLE
    """Handle style on the front drawer face -- DrawerHandleStyle.HANDLE, LIP, or NONE (FR-106)."""
    drawer_handle_length: float = 4.0
    """Forward extension length of the drawer front handle in mm."""
    drawer_pull_lip: float = 4.0
    """Backward-compatible alias for drawer_handle_length in mm."""
    sleeve_slack: float = 0.25
    """Clearance between outer sleeve and inner sliding drawer in mm."""
    sleeve_wall_thickness: float | None = None
    """Wall thickness of the outer sleeve in mm (defaults to max(1.2, wall_thickness / 2.0))."""

    def __post_init__(self) -> None:
        """Synchronize drawer_handle_length, drawer_pull_lip, and coerce drawer_handle_style."""
        if isinstance(self.drawer_handle_style, str):
            try:
                object.__setattr__(
                    self, "drawer_handle_style", DrawerHandleStyle(self.drawer_handle_style.lower())
                )
            except ValueError:
                valid = [e.value for e in DrawerHandleStyle]
                raise ValueError(
                    f"Invalid drawer_handle_style '{self.drawer_handle_style}'. "
                    f"Must be DrawerHandleStyle enum member: {valid}"
                ) from None
        elif not isinstance(self.drawer_handle_style, DrawerHandleStyle):
            raise TypeError(
                f"drawer_handle_style must be a DrawerHandleStyle enum, got {type(self.drawer_handle_style).__name__}"
            )

        # If caller passed non-default drawer_pull_lip and left drawer_handle_length default, sync it
        if self.drawer_pull_lip != 4.0 and self.drawer_handle_length == 4.0:
            object.__setattr__(self, "drawer_handle_length", self.drawer_pull_lip)
        elif self.drawer_handle_length != 4.0 and self.drawer_pull_lip == 4.0:
            object.__setattr__(self, "drawer_pull_lip", self.drawer_handle_length)
        super().__post_init__()

