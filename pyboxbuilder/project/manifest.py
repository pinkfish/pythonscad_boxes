# SPDX-License-Identifier: Apache-2.0
"""ProjectManifest — declarative catalog of insert boxes, metadata, and presets (FR-093)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pyboxbuilder.builders._base import BoxBuilder
    from pyboxbuilder.export.exporter import PieceBounds


@dataclass
class ProjectManifest:
    """Catalog of registered boxes, metadata, and configuration options (FR-093)."""

    name: str
    """Game name; becomes the output subdirectory."""
    game_box_size: tuple[float, float, float] | None = None
    """Outer game box dimensions [W, L, H] in mm. None = standalone boxes (no game box)."""
    wall_thickness: float = 2.0
    """Default wall thickness for all sub-boxes."""
    floor_thickness: float = 1.6
    """Default floor thickness."""
    lid_thickness: float = 2.0
    """Default lid thickness."""
    rounding: float | None = None
    """Edge radius for every box's exposed edges (FR-043/FR-044)."""
    inner_rounding: float | None = None
    """Edge radius where a partial lid grips the body (FR-044b)."""
    gap_threshold: float = 10.0
    """Gaps <= this are absorbed by adjacent boxes."""
    min_spacer_dim: float = 15.0
    """Minimum spacer width/length before absorption."""
    min_spacer_height: float = 5.0
    """A spacer tray thinner than this on any axis is dropped as unprintable (FR-014)."""
    clearance_slack: float | None = None
    """Clearance slack on each side of the game box in the X/Y directions (mm)."""

    board_thickness: float = 0.0
    """Thickness of the game board (mm) reserved at the top of the game box."""
    ribbon_channels: bool = False
    """Cut bottom groove for lifting ribbon on all sub-boxes by default."""
    generate_spacers: bool = True
    """Whether to automatically generate spacer boxes/trays to fill layout gaps."""
    box_defaults: dict[str, Any] | None = None
    """Defaults applied to every box that does not say otherwise."""

    boxes: list[BoxBuilder] = field(default_factory=list)
    """Registered sub-box builders in definition order."""
    shared_groups: list[tuple[list[str], list[tuple[str, float, float, float]]]] = field(
        default_factory=list
    )
    piece_bounds: tuple[PieceBounds, ...] = field(default_factory=tuple)
    """Bounding box of every exported piece, populated by export."""

    @property
    def resolved_clearance_slack(self) -> float:
        """Return the resolved clearance slack, scaling with game box size if None."""
        if self.clearance_slack is not None:
            return self.clearance_slack
        if self.game_box_size is None:
            return 1.0
        max_dim = max(self.game_box_size[0], self.game_box_size[1])
        if max_dim < 150.0:
            return 1.0
        elif max_dim <= 250.0:
            return 1.5
        else:
            return min(2.5, 1.5 + (max_dim - 250.0) / 100.0 * 0.5)

    @property
    def effective_game_box_size(self) -> tuple[float, float, float] | None:
        """Dimensions available for sub-boxes, accounting for board thickness."""
        if self.game_box_size is None:
            return None
        w, length_val, h = self.game_box_size
        return (w, length_val, h - self.board_thickness)

    def by_label(self, label: str) -> BoxBuilder:
        """Find a sub-box builder by label.

        Args:
            label: The label of the box to find.

        Returns:
            The matching BoxBuilder.

        Raises:
            ValueError: If no box with that label exists.
        """
        for b in self.boxes:
            if b.label == label:
                return b
        raise ValueError(f"No box with label '{label}' in project '{self.name}'")

    def get_by_label(self, label: str) -> BoxBuilder | None:
        """Find a sub-box builder by label, or None if not found."""
        for b in self.boxes:
            if b.label == label:
                return b
        return None

    def add_box(self, builder: BoxBuilder) -> BoxBuilder:
        """Register a box builder into the manifest."""
        self.boxes.append(builder)
        return builder

    def __len__(self) -> int:
        """Return the number of registered boxes."""
        return len(self.boxes)

    def __iter__(self) -> Any:
        """Iterate over registered boxes."""
        return iter(self.boxes)
