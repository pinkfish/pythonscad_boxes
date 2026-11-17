# SPDX-License-Identifier: Apache-2.0
"""Declarative layout — say how the boxes are arranged, not where they sit (T186).

There is a gap between the two ways of placing boxes. Free-form packing works
below roughly 70% fill and gives up above it; explicit coordinates always work
but have to be recomputed by hand whenever a box changes size. Real inserts sit
in that gap: they are densely packed *and* highly structured — three columns of
stacked trays, not an arbitrary arrangement.

This module lets the structure be written down and the coordinates derived::

    project.arrange(columns(
        rows(                                        # left column
            stack("PlayerBoxBlack", "PlayerBoxYellow"),
            stack("PlayerBoxRed", "PlayerBoxBlue"),
        ),
        rows("CardBoxFavor", "CardBoxHero"),         # middle column
    ))

`columns` runs along X, `rows` along Y, `stack` along Z. Groups nest freely, so
a stack can end in a pair of rows. Each child starts where the previous one
ended; a group is as wide as its widest child on the axes it does not consume.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from pyboxbuilder.builders._base import BoxBuilder

X, Y, Z = 0, 1, 2
AXIS_NAMES = ("columns", "rows", "stack")

Node = Union["Group", "PolygonGrid", str]


class LayoutError(ValueError):
    """Raised when a layout tree cannot be resolved into positions."""


@dataclass(frozen=True)
class PolygonGrid:
    """A tessellated regular-polygon lattice (e.g., hexagonal honeycomb) of boxes."""

    children: tuple[Node, ...]
    cols: int
    sides: int = 6
    apothem: float = 20.0
    gap: float = 0.0

    def labels(self) -> list[str]:
        """Every box label in this subtree, in layout order."""
        found: list[str] = []
        for child in self.children:
            found.extend([child] if isinstance(child, str) else child.labels())
        return found

    def __repr__(self) -> str:
        """Return the polygon grid representation."""
        return (
            f"polygon_grid({', '.join(map(repr, self.children))}, "
            f"cols={self.cols}, sides={self.sides}, apothem={self.apothem})"
        )


@dataclass(frozen=True)
class Group:
    """A run of boxes or sub-groups laid end to end along one axis."""

    axis: int
    children: tuple[Node, ...]
    gap: float = 0.0
    """Clearance inserted between adjacent children, in mm."""

    def labels(self) -> list[str]:
        """Every box label in this subtree, in layout order."""
        found: list[str] = []
        for child in self.children:
            found.extend([child] if isinstance(child, str) else child.labels())
        return found

    def __repr__(self) -> str:
        """Return the layout tree in ``Axis(child, ...)`` form."""
        return f"{AXIS_NAMES[self.axis]}({', '.join(map(repr, self.children))})"


def columns(*children: Node, gap: float = 0.0) -> Group:
    """Lay children out left to right along X."""
    return Group(axis=X, children=tuple(children), gap=gap)


def rows(*children: Node, gap: float = 0.0) -> Group:
    """Lay children out front to back along Y."""
    return Group(axis=Y, children=tuple(children), gap=gap)


def stack(*children: Node, gap: float = 0.0) -> Group:
    """Lay children out bottom to top along Z."""
    return Group(axis=Z, children=tuple(children), gap=gap)


def polygon_grid(
    *children: Node,
    cols: int,
    sides: int = 6,
    apothem: float,
    gap: float = 0.0,
) -> PolygonGrid:
    """Lay regular-polygon boxes out in a tessellated honeycomb/triangle/square grid."""
    if cols <= 0:
        raise LayoutError(f"polygon_grid cols must be >= 1; got {cols}")
    if sides < 3:
        raise LayoutError(f"polygon_grid sides must be >= 3; got {sides}")
    return PolygonGrid(
        children=tuple(children),
        cols=cols,
        sides=sides,
        apothem=float(apothem),
        gap=float(gap),
    )


@dataclass(frozen=True)
class Arrangement:
    """The result of resolving a layout tree."""

    positions: dict[str, tuple[float, float, float]]
    size: tuple[float, float, float]
    """Overall extent of the arranged boxes."""

    def fits(self, container: Sequence[float], tolerance: float = 1e-6) -> bool:
        """Whether this arrangement fits within a container, within tolerance."""
        return all(s <= c + tolerance for s, c in zip(self.size, container, strict=False))


def measure(node: Node, sizes: dict[str, tuple[float, float, float]]) -> tuple[float, float, float]:
    """Extent of a node: children sum along its axis and max on the other two."""
    if isinstance(node, str):
        if node not in sizes:
            raise LayoutError(f"Layout names a box that is not in the project: {node!r}")
        return sizes[node]

    if not node.children:
        return (0.0, 0.0, 0.0)

    if isinstance(node, PolygonGrid):
        from pyboxbuilder.box.features import polygon_grid_position

        max_x = max_y = max_z = 0.0
        for idx, child in enumerate(node.children):
            ext = measure(child, sizes)
            dx, dy = polygon_grid_position(
                row=idx // node.cols,
                col=idx % node.cols,
                sides=node.sides,
                apothem=node.apothem,
                spacing=node.gap,
                origin=(0.0, 0.0),
            )
            max_x = max(max_x, dx + ext[0])
            max_y = max(max_y, dy + ext[1])
            max_z = max(max_z, ext[2])
        return (max_x, max_y, max_z)

    extents = [measure(child, sizes) for child in node.children]
    gaps = node.gap * (len(extents) - 1)
    return tuple(  # type: ignore[return-value]
        sum(e[axis] for e in extents) + gaps if axis == node.axis
        else max(e[axis] for e in extents)
        for axis in (X, Y, Z)
    )


def arrange(
    node: Node,
    sizes: dict[str, tuple[float, float, float]],
    origin: Sequence[float] = (0.0, 0.0, 0.0),
) -> Arrangement:
    """Resolve a layout tree into a position per box.

    Args:
        node: The root group, or a single box label.
        sizes: {label: (width, length, height)} for every box named in the tree.
        origin: Where the arrangement's minimum corner goes.

    Returns:
        The positions and the overall extent.

    Raises:
        LayoutError: If the tree names an unknown box, or names one twice.

    """
    positions: dict[str, tuple[float, float, float]] = {}
    _place(
        node,
        sizes,
        (float(origin[0]), float(origin[1]), float(origin[2])),
        positions,
    )
    return Arrangement(positions=positions, size=measure(node, sizes))


def _place(
    node: Node,
    sizes: dict[str, tuple[float, float, float]],
    at: tuple[float, float, float],
    positions: dict[str, tuple[float, float, float]],
) -> None:
    if isinstance(node, str):
        if node in positions:
            raise LayoutError(f"Layout places box {node!r} more than once")
        positions[node] = at
        return

    if isinstance(node, PolygonGrid):
        from pyboxbuilder.box.features import polygon_grid_position

        for idx, child in enumerate(node.children):
            dx, dy = polygon_grid_position(
                row=idx // node.cols,
                col=idx % node.cols,
                sides=node.sides,
                apothem=node.apothem,
                spacing=node.gap,
                origin=(0.0, 0.0),
            )
            _place(child, sizes, (at[0] + dx, at[1] + dy, at[2]), positions)
        return

    cursor = at[node.axis]
    for child in node.children:
        child_at = list(at)
        child_at[node.axis] = cursor
        _place(child, sizes, (child_at[0], child_at[1], child_at[2]), positions)
        cursor += measure(child, sizes)[node.axis] + node.gap


def check_complete(node: Node, builders: Iterable[BoxBuilder]) -> list[str]:
    """Return the labels of boxes the project has but the layout leaves out."""
    named = set(node.labels() if isinstance(node, (Group, PolygonGrid)) else [node])
    return sorted(b.label for b in builders if b.label not in named)
