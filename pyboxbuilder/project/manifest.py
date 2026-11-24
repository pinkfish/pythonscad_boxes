# SPDX-License-Identifier: Apache-2.0
"""ProjectManifest — declarative catalog of insert boxes, metadata, and presets (FR-093)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pyboxbuilder.builders._base import BoxBuilder
    from pyboxbuilder.export.exporter import PieceBounds


@dataclass(frozen=True)
class GameComponent:
    """One declared physical component type in the board game's inventory."""

    name: str
    """Component name (e.g. ``"Action Cards"``, ``"Coal Cubes"``, ``"Player Boards"``)."""
    count: int
    """Total number of physical pieces of this component included in the game."""
    category: str = ""
    """Optional grouping category (e.g. ``"Cards"``, ``"Tokens"``, ``"Boards"``)."""
    notes: str = ""
    """Optional note."""
    location: str = ""
    """Optional loose storage location (e.g. ``"Inside spacer_1"``) for items without their own box."""

    def __post_init__(self) -> None:
        """Validate non-empty name and positive piece count."""
        if not self.name.strip():
            raise ValueError("GameComponent name must be non-empty")
        if self.count < 1:
            raise ValueError(f"GameComponent {self.name!r} count must be >= 1, got {self.count}")


@dataclass(frozen=True)
class GameBoard:
    """A non-printed board, rulebook, screen, or playmat placed inside the game box.

    Unlike ``board_thickness`` (which reserves a full-footprint slab across the
    entire top or bottom of the game box), a ``GameBoard`` occupies a specific
    3-D region ``(size, position)`` inside the game box. Auto-packed boxes and
    auto-generated spacers avoid it, no STL is exported for it, and both the
    packing guide PDF and box summary docs render and count it explicitly.
    """

    label: str
    """Human-readable name (e.g. ``"Main Board & Rulebooks"``, ``"Player Screens"``)."""
    size: tuple[float, float, float]
    """Outer dimensions ``(W, L, H)`` in mm."""
    position: tuple[float, float, float]
    """Packed origin ``(X, Y, Z)`` in mm within the game box frame."""
    count: int = 1
    """How many physical boards/screens/mats occupy this reserved region."""
    notes: str = ""
    """Optional packing note shown in summaries and packing sheets."""
    component: str | None = None
    """Optional declared inventory component name satisfied by this board."""
    allocates: tuple[tuple[str, int], ...] = ()
    """Optional explicit ``((component_name, qty), ...)`` allocations satisfied by this board."""

    def __post_init__(self) -> None:
        """Validate positive board dimensions and non-negative piece count."""
        if any(d <= 0 for d in self.size):
            raise ValueError(f"GameBoard {self.label!r} dimensions must be positive, got {self.size}")
        if self.count < 1:
            raise ValueError(f"GameBoard {self.label!r} count must be >= 1, got {self.count}")


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
    min_spacer_height: float = 10.0
    """A spacer tray shorter than this in Z is dropped rather than printed as a thin wafer (FR-014)."""
    max_height_absorb: float = 10.0
    """Maximum vertical gap (mm) absorbed by growing a top-exposed box instead of adding a small spacer."""
    clearance_slack: float | None = None
    """Clearance slack on each side of the game box in the X/Y directions (mm)."""

    board_thickness: float = 0.0
    """Thickness of the game board (mm) reserved at the top (or bottom if ``board_on_bottom``)."""
    board_on_bottom: bool = False
    """Whether reserved board space sits at the bottom (``z = 0..board_thickness``)."""
    ribbon_channels: bool = False
    """Cut bottom groove for lifting ribbon on all sub-boxes by default."""
    generate_spacers: bool = True
    """Whether to automatically generate spacer boxes/trays to fill layout gaps."""
    box_defaults: dict[str, Any] | None = None
    """Defaults applied to every box that does not say otherwise."""

    boxes: list[BoxBuilder] = field(default_factory=list)
    """Registered sub-box builders in definition order."""
    boards: list[GameBoard] = field(default_factory=list)
    """Registered non-printed game boards / screens / playmats occupying partial box space."""
    components: list[GameComponent] = field(default_factory=list)
    """Declared physical game component inventory that boxes and boards must account for."""
    shared_groups: list[tuple[list[str], list[tuple[str, float, float, float]]]] = field(
        default_factory=list
    )
    stack_groups: list[tuple[str, ...]] = field(default_factory=list)
    """Ordered bottom-to-top box label chains registered via Project.stack_order()."""
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
    def board_z_offset(self) -> float:
        """Starting Z height (mm) of usable insert space above bottom-stored boards."""
        return self.board_thickness if self.board_on_bottom else 0.0

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

    def add_board(self, board: GameBoard) -> GameBoard:
        """Register a non-printed game board region into the manifest."""
        self.boards.append(board)
        return board

    def add_component(self, component: GameComponent) -> GameComponent:
        """Register a declared game component into the manifest inventory."""
        self.components.append(component)
        return component

    def __len__(self) -> int:
        """Return the number of registered boxes."""
        return len(self.boxes)

    def __iter__(self) -> Any:
        """Iterate over registered boxes."""
        return iter(self.boxes)
