# SPDX-License-Identifier: Apache-2.0
"""Polygon helpers for the rectilinear outlines the packer produces.

Leftover space between axis-aligned boxes is always rectilinear — every edge
runs along X or Y — which makes exact offsetting a few lines of arithmetic
rather than a job for a general polygon-offset library. Both the spacer pass
(clearance around a tray) and `PathBox` (a tray's inner cavity) need it.
"""

from __future__ import annotations

from collections.abc import Sequence

EPSILON = 0.01

Point = tuple[float, float]
Path = tuple[Point, ...]


def polygon_area(path: Sequence[Point]) -> float:
    """Shoelace area of a closed outline."""
    return abs(signed_area(path)) / 2


def signed_area(path: Sequence[Point]) -> float:
    """Twice the signed area — positive when the outline runs counter-clockwise."""
    total = 0.0
    for i, (x0, y0) in enumerate(path):
        x1, y1 = path[(i + 1) % len(path)]
        total += x0 * y1 - x1 * y0
    return total


def is_rectilinear(path: Sequence[Point]) -> bool:
    """Return True when every edge is axis-aligned."""
    for i, (x0, y0) in enumerate(path):
        x1, y1 = path[(i + 1) % len(path)]
        if abs(x0 - x1) > EPSILON and abs(y0 - y1) > EPSILON:
            return False
    return True


def inset_rectilinear(path: Sequence[Point], distance: float) -> Path:
    """Pull a rectilinear outline inward by `distance`.

    Every corner joins one horizontal and one vertical edge, so its new position
    is the old one moved by `distance` along each incident edge's inward normal.
    That is exact for convex and reflex corners alike — an L stays an L, with all
    six of its sides moved in, which a centroid scale would not manage. A reflex
    corner correctly moves *out* into the notch, keeping the arm's width right.

    Which way is inward depends on the direction the outline is traversed, not on
    where a corner's neighbours happen to sit, so the normals come from the
    directed edges: for a counter-clockwise ring, edge `(dx, dy)` points inward
    along `(-dy, dx)`.

    Args:
        path: A closed rectilinear outline.
        distance: How far to move each edge inward. Negative grows the outline.

    Returns:
        The inset outline, with the same number of points.

    """
    if distance == 0 or len(path) < 4:
        return tuple(path)

    winding = 1.0 if signed_area(path) > 0 else -1.0
    count = len(path)

    moved: list[Point] = []
    for n, point in enumerate(path):
        incoming = (path[n - 1], point)
        outgoing = (point, path[(n + 1) % count])

        shift_x = shift_y = 0.0
        for (ax, ay), (bx, by) in (incoming, outgoing):
            edge_x, edge_y = bx - ax, by - ay
            # Axis-aligned, so exactly one component of the normal is non-zero.
            shift_x += -edge_y * winding
            shift_y += edge_x * winding

        moved.append((
            point[0] + distance * _sign(shift_x),
            point[1] + distance * _sign(shift_y),
        ))
    return tuple(moved)


def bounds(path: Sequence[Point]) -> tuple[Point, Point]:
    """(min corner, max corner) of an outline."""
    xs = [x for x, _ in path]
    ys = [y for _, y in path]
    return ((min(xs), min(ys)), (max(xs), max(ys)))


def _sign(value: float) -> float:
    if value > EPSILON:
        return 1.0
    if value < -EPSILON:
        return -1.0
    return 0.0


def point_in_polygon(x: float, y: float, poly: Sequence[Point]) -> bool:
    """Return True if point (x, y) is inside the polygon by ray casting."""
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1) + x1):
            inside = not inside
    return inside


def largest_inscribed_rectangle(path: Sequence[Point]) -> tuple[float, float, float, float]:
    """Find the largest axis-aligned inscribed rectangle in a simple polygon.

    Returns:
        `(x, y, width, length)` in the polygon's local frame.
    """
    if len(path) < 3:
        return (0.0, 0.0, 0.0, 0.0)

    if is_rectilinear(path):
        xs = sorted({p[0] for p in path})
        ys = sorted({p[1] for p in path})
        if len(xs) < 2 or len(ys) < 2:
            return (0.0, 0.0, 0.0, 0.0)

        ncols = len(xs) - 1
        nrows = len(ys) - 1

        grid = [
            [
                point_in_polygon((xs[c] + xs[c + 1]) / 2.0, (ys[r] + ys[r + 1]) / 2.0, path)
                for c in range(ncols)
            ]
            for r in range(nrows)
        ]

        best_area = -1.0
        best_rect = (0.0, 0.0, 0.0, 0.0)

        for c1 in range(ncols):
            for c2 in range(c1, ncols):
                width = xs[c2 + 1] - xs[c1]
                r_start: int | None = None
                for r in range(nrows):
                    all_inside = all(grid[r][c] for c in range(c1, c2 + 1))
                    if all_inside:
                        if r_start is None:
                            r_start = r
                        length = ys[r + 1] - ys[r_start]
                        area = width * length
                        if area > best_area or (abs(area - best_area) < 1e-6 and width > best_rect[2]):
                            best_area = area
                            best_rect = (xs[c1], ys[r_start], width, length)
                    else:
                        r_start = None

        return best_rect

    # Non-rectilinear polygon: grid discretization with histogram method
    min_x = min(p[0] for p in path)
    max_x = max(p[0] for p in path)
    min_y = min(p[1] for p in path)
    max_y = max(p[1] for p in path)

    w = max_x - min_x
    l = max_y - min_y
    if w <= 0 or l <= 0:
        return (0.0, 0.0, 0.0, 0.0)

    n_samples = 60
    dx = w / n_samples
    dy = l / n_samples

    grid_non_rect = []
    for r in range(n_samples):
        row = []
        y0 = min_y + r * dy
        y1 = y0 + dy
        ymid = (y0 + y1) / 2.0
        for c in range(n_samples):
            x0 = min_x + c * dx
            x1 = x0 + dx
            xmid = (x0 + x1) / 2.0
            inside = (
                point_in_polygon(xmid, ymid, path)
                and point_in_polygon(x0, y0, path)
                and point_in_polygon(x1, y0, path)
                and point_in_polygon(x0, y1, path)
                and point_in_polygon(x1, y1, path)
            )
            row.append(inside)
        grid_non_rect.append(row)

    best_area = -1.0
    best_rect = (0.0, 0.0, 0.0, 0.0)

    heights = [0] * n_samples
    for r in range(n_samples):
        for c in range(n_samples):
            heights[c] = heights[c] + 1 if grid_non_rect[r][c] else 0

        stack: list[int] = []
        for c in range(n_samples + 1):
            h = heights[c] if c < n_samples else 0
            while stack and heights[stack[-1]] >= h:
                top = stack.pop()
                width_cells = c if not stack else c - stack[-1] - 1
                length_cells = heights[top]
                col_start = stack[-1] + 1 if stack else 0
                row_start = r - length_cells + 1

                actual_w = width_cells * dx
                actual_l = length_cells * dy
                area = actual_w * actual_l
                if area > best_area:
                    best_area = area
                    best_rect = (min_x + col_start * dx, min_y + row_start * dy, actual_w, actual_l)
            stack.append(c)

    return best_rect
