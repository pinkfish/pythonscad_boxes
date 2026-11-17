# SPDX-License-Identifier: Apache-2.0
"""Compartment elements — individual game components nested inside a compartment.

A `CompartmentElement` is one physical piece (a worker meeple, a hero standee, a
hex tile, a wooden marker) with its own silhouette, its own local (x, y) offset
inside the owning compartment, its own rotation and its own depth. A compartment
that carries elements is an *element pack*: the elements are positioned in a local
frame and the pack's bounding box is what the box-level layout engine sees, so the
pack behaves exactly like one ordinary rectangular compartment (FR-004b).

Geometry generation delegates to pybosl2 and is only imported when a cutout is
actually built, so the layout maths stays importable without PythonSCAD.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING, Any

from pyboxbuilder.enums import ElementShape
from pyboxbuilder.precision import kwargs as precision_kwargs
from pyboxbuilder.rounding import vertical_edges

if TYPE_CHECKING:
    from pybosl2 import Color, Region
    from pybosl2.shapes3d import Bosl2Solid


@dataclass(frozen=True)
class CompartmentElement:
    """A physical game component nested inside a compartment's bounding box."""

    shape_file: str | None = None
    """Path to the SVG outline representing the component (ElementShape.SVG only)."""
    offset: tuple[float, float] = (0.0, 0.0)
    """2D offset (x, y) in mm of the element's lower-left corner, relative to the
    compartment's bottom-left origin."""
    rotation: float = 0.0
    """Rotation of the component in degrees, about the centre of its footprint."""
    size: tuple[float, float] | None = None
    """Bounding dimensions (width, length) of the component in mm."""
    shape: ElementShape = ElementShape.SVG
    """Silhouette kind. Defaults to SVG, which requires `shape_file`."""
    depth: float | None = None
    """Cutout depth in mm. None inherits the owning compartment's depth."""
    z_offset: float | None = None
    """Extra lift of the cutout floor above the compartment floor, in mm.
    If None, the pocket automatically aligns flush with the top of the box.
    Used for pieces that sit on top of other pieces (e.g. a tile over a token)."""
    corner_radius: float = 2.0
    """Corner radius for ElementShape.ROUNDED_RECT."""
    corner_rounding: float = 0.5
    """Corner rounding radius for ElementShape.RECT (default 0.5mm, 0 for sharp)."""
    bottom_rounding: float = 0.0
    """Bottom corner fillet radius in mm."""
    label: str | None = None
    """Optional identifier, handy for tests and layout diagnostics."""
    pull_out: bool = True
    """Cut a finger pull-out over this slot so the piece can be lifted out.

    A silhouette slot holds its piece snugly by design — that is the point of
    cutting to the outline — which also means there is nowhere to get a
    fingertip. The pull-out is a dish across the slot, curved in from the
    surrounding floor so a finger slides down it and under the piece.
    """
    pull_out_depth: float | None = None
    """How deep the pull-out dish goes below the slot's own floor.

    ``None`` takes **half the piece's depth**, which is enough to get under a
    piece without letting it drop into the dish and sit crooked.
    """
    pull_out_width: float | None = None
    """Width of the pull-out across the slot. ``None`` uses a fingertip width."""
    color: str | None = None
    """When set, this element is a **positive coloured insert** — a thin icon
    pressed into the bottom of its well — instead of a cutout. The value is a
    web colour name, applied as the insert's own material in mmu mode."""

    def __post_init__(self) -> None:
        """Validate the element's shape and size."""
        if self.shape is ElementShape.SVG and not self.shape_file:
            raise ValueError(
                "CompartmentElement with shape=SVG requires shape_file="
            )
        if self.size is None:
            raise ValueError(
                f"CompartmentElement {self.label or self.shape_file!r} requires size=(w, l)"
            )
        if self.size[0] <= 0 or self.size[1] <= 0:
            raise ValueError(
                f"CompartmentElement {self.label or self.shape_file!r} size must be positive"
            )

    # ---------------------------------------------------------------- geometry

    @property
    def base_footprint(self) -> tuple[float, float]:
        """Axis-aligned (width, length) of the silhouette before rotation.

        For most shapes this is just `size`. A hexagon is the exception: `size[0]`
        is its flat-to-flat width, exactly as `RegularPolygon(width=...)` reads it
        in the original toolkit, so it measures `width / cos(30°)` point-to-point
        across the other axis.
        """
        assert self.size is not None
        w, l = self.size
        if self.shape is ElementShape.HEXAGON:
            return (w / math.cos(math.radians(30)), w)
        if self.shape in (ElementShape.CIRCLE, ElementShape.SPHERE_SCOOP):
            d = min(w, l)
            return (d, d)
        return (w, l)

    @property
    def footprint(self) -> tuple[float, float]:
        """Axis-aligned (width, length) after `rotation` is applied."""
        if self.shape in (ElementShape.CIRCLE, ElementShape.SPHERE_SCOOP):
            return self.base_footprint  # rotating a disc changes nothing
        if self.shape is ElementShape.HEXAGON:
            return _hexagon_footprint(self.base_footprint[0] / 2, self.rotation)

        w, l = self.base_footprint
        rad = math.radians(self.rotation)
        cos_r, sin_r = abs(math.cos(rad)), abs(math.sin(rad))
        if self.shape is ElementShape.ROUNDED_RECT:
            cr = max(0.0, min(self.corner_radius, w / 2.0, l / 2.0))
            iw, il = max(0.0, w - 2.0 * cr), max(0.0, l - 2.0 * cr)
            return (iw * cos_r + il * sin_r + 2.0 * cr, iw * sin_r + il * cos_r + 2.0 * cr)
        return (w * cos_r + l * sin_r, w * sin_r + l * cos_r)

    def bounds(self) -> tuple[float, float, float, float]:
        """Axis-aligned bounds (min_x, min_y, max_x, max_y) in the pack frame."""
        fw, fl = self.footprint
        return (
            self.offset[0],
            self.offset[1],
            self.offset[0] + fw,
            self.offset[1] + fl,
        )

    def translated(self, dx: float, dy: float) -> CompartmentElement:
        """Return a copy shifted by (dx, dy) in the pack frame."""
        return replace(self, offset=(self.offset[0] + dx, self.offset[1] + dy))


def _hexagon_footprint(circumradius: float, rotation: float) -> tuple[float, float]:
    """Exact axis-aligned extent of a regular hexagon rotated by `rotation`.

    A rect-bbox approximation overshoots badly here — at 30 degrees it claims
    36% more width than the hexagon actually occupies.
    """
    angles = [math.radians(rotation + 60 * k) for k in range(6)]
    xs = [circumradius * math.cos(a) for a in angles]
    ys = [circumradius * math.sin(a) for a in angles]
    return (max(xs) - min(xs), max(ys) - min(ys))


def elements_bounding_box(
    elements: Sequence[CompartmentElement],
) -> tuple[float, float, float, float]:
    """Return (min_x, min_y, max_x, max_y) covering every element in the pack."""
    if not elements:
        return (0.0, 0.0, 0.0, 0.0)
    boxes = [e.bounds() for e in elements]
    return (
        min(b[0] for b in boxes),
        min(b[1] for b in boxes),
        max(b[2] for b in boxes),
        max(b[3] for b in boxes),
    )


def elements_footprint(
    elements: Sequence[CompartmentElement], margin: float = 0.0
) -> tuple[float, float]:
    """Size of the rectangular compartment that holds this element pack (FR-004b).

    Offsets are measured from the compartment's own lower-left corner, so the
    footprint spans from that corner out to the furthest element — authored
    offsets are preserved rather than collapsed against the origin. Use
    `normalize_elements` first if you want the pack shrink-wrapped instead.

    Args:
        elements: The elements in the pack, positioned in the compartment frame.
        margin: Extra clearance added past the furthest element, in mm.

    Returns:
        (width, length) of the compartment needed to hold the pack, in mm.

    """
    if not elements:
        return (0.0, 0.0)
    min_x, min_y, max_x, max_y = elements_bounding_box(elements)
    span_x = max_x - min(0.0, min_x)
    span_y = max_y - min(0.0, min_y)
    return (round(span_x + margin, 1), round(span_y + margin, 1))


def normalize_elements(
    elements: Sequence[CompartmentElement], margin: float = 0.0
) -> tuple[CompartmentElement, ...]:
    """Shift a pack so its bounding box starts at (margin, margin).

    Keeps hand-written offsets readable — you can lay elements out in whatever
    coordinates suit the source drawing and let the pack normalise itself.
    """
    min_x, min_y, _, _ = elements_bounding_box(elements)
    dx, dy = margin - min_x, margin - min_y
    return tuple(e.translated(dx, dy) for e in elements)


def grid_pack(
    prototype: CompartmentElement,
    count: int,
    *,
    origin: tuple[float, float] = (0.0, 0.0),
    pitch: tuple[float, float] = (0.0, 0.0),
    alternate_rotation: float = 0.0,
) -> tuple[CompartmentElement, ...]:
    """Repeat one element `count` times along a straight line (FR-004b).

    This is the "five owl workers stacked in a column" case: the same silhouette
    at a fixed pitch, optionally flipping every other copy so the pieces nest.

    Args:
        prototype: The element to repeat; its `offset` is ignored.
        count: How many copies to place.
        origin: Position of the first copy.
        pitch: (dx, dy) step between successive copies.
        alternate_rotation: Extra rotation applied to every odd-indexed copy.

    Returns:
        The placed copies, in order.

    """
    out = []
    for i in range(count):
        rotation = prototype.rotation + (alternate_rotation if i % 2 else 0.0)
        out.append(
            replace(
                prototype,
                offset=(origin[0] + pitch[0] * i, origin[1] + pitch[1] * i),
                rotation=rotation,
                label=f"{prototype.label}_{i}" if prototype.label else None,
            )
        )
    return tuple(out)


def _pack_maxrects_core(
    elements: Sequence[CompartmentElement],
    *,
    usable_w: float,
    usable_l: float,
    spacing: float,
    margin: float,
    allow_rotate: bool,
    sort_mode: str = "area_desc",
    score_mode: str = "skyline",
    keep_unrotated: set[int] | None = None,
    overflow_fallback: bool = True,
) -> tuple[CompartmentElement, ...] | None:
    """Place elements with 2D BSSF MaxRects; return ``None`` if bounded and full."""
    if not elements:
        return ()

    keep_unrotated = keep_unrotated or set()
    indexed = list(enumerate(elements))
    if sort_mode == "area_desc":
        order = sorted(
            indexed,
            key=lambda pair: pair[1].footprint[0] * pair[1].footprint[1],
            reverse=True,
        )
    elif sort_mode == "max_side":
        order = sorted(
            indexed,
            key=lambda pair: (max(pair[1].footprint), pair[1].footprint[0] * pair[1].footprint[1]),
            reverse=True,
        )
    else:
        order = indexed

    free_rects: list[tuple[float, float, float, float]] = [(0.0, 0.0, usable_w, usable_l)]
    placed_by_idx: dict[int, CompartmentElement] = {}

    for orig_idx, el in order:
        fw, fl = el.footprint
        variants: list[tuple[float, float, float]] = [(fw, fl, el.rotation)]
        if (
            allow_rotate
            and orig_idx not in keep_unrotated
            and el.shape not in (ElementShape.CIRCLE, ElementShape.SPHERE_SCOOP)
            and abs(fw - fl) > 1e-6
        ):
            rot_el = replace(el, rotation=el.rotation + 90.0)
            rw, rl = rot_el.footprint
            variants.append((rw, rl, el.rotation + 90.0))

        best_score: tuple[float, float, float, float] | None = None
        best_choice: tuple[float, float, float, float, float] | None = None

        for rx, ry, rw_avail, rl_avail in free_rects:
            for vw, vl, vrot in variants:
                if vw <= rw_avail + 1e-6 and vl <= rl_avail + 1e-6:
                    short_left = min(rw_avail - vw, rl_avail - vl)
                    if score_mode == "bssf":
                        long_left = max(rw_avail - vw, rl_avail - vl)
                        score = (round(short_left, 4), round(long_left, 4), float(vrot != el.rotation), round(ry, 4))
                    else:
                        score = (round(ry + vl, 4), round(ry, 4), round(short_left, 4), float(vrot != el.rotation))
                    if best_score is None or score < best_score:
                        best_score = score
                        best_choice = (rx, ry, vw, vl, vrot)

        if best_choice is None:
            if not overflow_fallback:
                return None
            cur_max_y = max((e.bounds()[3] - margin for e in placed_by_idx.values()), default=0.0)
            y_pos = cur_max_y + (spacing if placed_by_idx else 0.0)
            best_choice = (0.0, y_pos, fw, fl, el.rotation)

        px, py, pw, pl, prot = best_choice
        placed_by_idx[orig_idx] = replace(
            el,
            offset=(round(margin + px, 4), round(margin + py, 4)),
            rotation=prot,
        )

        # Subtract padded box [px - spacing, py - spacing, px + pw + spacing, py + pl + spacing]
        ox0 = px - spacing
        oy0 = py - spacing
        ox1 = px + pw + spacing
        oy1 = py + pl + spacing
        next_free: list[tuple[float, float, float, float]] = []
        for fx, fy, fw_r, fl_r in free_rects:
            fx1, fy1 = fx + fw_r, fy + fl_r
            if ox1 <= fx + 1e-9 or ox0 >= fx1 - 1e-9 or oy1 <= fy + 1e-9 or oy0 >= fy1 - 1e-9:
                next_free.append((fx, fy, fw_r, fl_r))
                continue
            if ox0 > fx + 1e-6:
                next_free.append((fx, fy, ox0 - fx, fl_r))
            if ox1 < fx1 - 1e-6:
                next_free.append((ox1, fy, fx1 - ox1, fl_r))
            if oy0 > fy + 1e-6:
                next_free.append((fx, fy, fw_r, oy0 - fy))
            if oy1 < fy1 - 1e-6:
                next_free.append((fx, oy1, fw_r, fy1 - oy1))

        # Prune dominated free rectangles
        pruned: list[tuple[float, float, float, float]] = []
        for i, a in enumerate(next_free):
            ax0, ay0, aw, al = a
            ax1, ay1 = ax0 + aw, ay0 + al
            dominated = False
            for j, b in enumerate(next_free):
                if i == j:
                    continue
                bx0, by0, bw, bl = b
                if (
                    bx0 <= ax0 + 1e-6
                    and by0 <= ay0 + 1e-6
                    and bx0 + bw >= ax1 - 1e-6
                    and by0 + bl >= ay1 - 1e-6
                    and ((bw * bl > aw * al + 1e-6) or j < i)
                ):
                    dominated = True
                    break
            if not dominated:
                pruned.append(a)
        free_rects = pruned

    return tuple(placed_by_idx[i] for i in range(len(elements)))


def pack_elements(
    elements: Sequence[CompartmentElement],
    *,
    max_width: float | None = None,
    spacing: float = 2.0,
    margin: float = 0.0,
    allow_rotate: bool = True,
) -> tuple[CompartmentElement, ...]:
    """Auto-pack loose ``CompartmentElement`` items into a compact 2D element pack.

    Uses a 2D Best-Short-Side-Fit (BSSF) MaxRects layout, optionally testing a
    90-degree rotation per asymmetric element and reserving room between slots.
    Coloured floor-inlay icons positioned relative to another element should be
    added after packing; every element passed here receives a fresh non-overlapping
    ``offset``.

    Args:
        elements: Elements to place (their existing ``offset`` is replaced).
        max_width: Maximum pack width in mm; ``None`` derives a near-square target.
        spacing: Minimum gap between adjacent element footprints in mm.
        margin: Outer border inset around the entire pack in mm.
        allow_rotate: Allow 90-degree Z rotation when it improves 2D fit.

    Returns:
        Packed ``CompartmentElement`` tuple in the original input order.

    """
    if not elements:
        return ()

    if max_width is None:
        total_area = sum(
            (el.footprint[0] + spacing) * (el.footprint[1] + spacing) for el in elements
        )
        widest = max(min(el.footprint) if allow_rotate else el.footprint[0] for el in elements)
        target_w = max(widest + 2.0 * margin, math.sqrt(total_area) * 1.05 + 2.0 * margin)
    else:
        target_w = float(max_width)

    usable_w = max(1e-3, target_w - 2.0 * margin)
    big_l = sum(max(el.footprint) + spacing for el in elements) + 2.0 * margin + 100.0
    result = _pack_maxrects_core(
        elements,
        usable_w=usable_w,
        usable_l=big_l,
        spacing=spacing,
        margin=margin,
        allow_rotate=allow_rotate,
        sort_mode="area_desc",
        overflow_fallback=True,
    )
    assert result is not None
    return result


ElementGroup = CompartmentElement | Sequence[CompartmentElement]


def _distribute_linear_gap(
    total: float, widths: Sequence[float], min_gap: float, min_margin: float
) -> tuple[float, float] | None:
    """Return ``(outer_margin, inner_gap)`` along one axis, or ``None`` if tight."""
    n = len(widths)
    if n == 0:
        return (0.0, 0.0)
    used = sum(widths)
    extra = total - used
    if extra < -1e-6:
        return None
    extra = max(0.0, extra)
    if n == 1:
        margin = extra / 2.0
        return (margin, 0.0) if margin + 1e-6 >= min_margin else None

    min_inner = min_gap * (n - 1)
    if extra + 1e-6 < min_inner:
        return None
    # When room suffices for >= min_margin on outer walls and >= min_inner between items,
    # distribute slack evenly; otherwise reserve inner divider thickness first.
    even = extra / (n + 1)
    if even + 1e-6 >= min_gap and even + 1e-6 >= min_margin:
        return (even, even)
    inner = min(min_gap, (extra - 2.0 * min_margin) / (n - 1)) if extra >= min_inner + 2.0 * min_margin else min_gap
    inner = max(min_gap, inner)
    margin = max(0.0, (extra - inner * (n - 1)) / 2.0)
    if margin + 1e-6 < min_margin:
        return None
    return (margin, inner)


def _attach_group_children(
    primary: CompartmentElement,
    children: Sequence[CompartmentElement],
    rot_delta: float,
) -> list[CompartmentElement]:
    """Place child elements centered on ``primary`` and rotated by ``rot_delta``."""
    pw, pl = primary.footprint
    cx = primary.offset[0] + pw / 2.0
    cy = primary.offset[1] + pl / 2.0
    out: list[CompartmentElement] = []
    for child in children:
        new_rot = (child.rotation + rot_delta) % 360.0 if rot_delta else child.rotation
        rotated_child = replace(child, rotation=new_rot)
        chw, chl = rotated_child.footprint
        out.append(
            replace(
                rotated_child,
                offset=(round(cx - chw / 2.0, 4), round(cy - chl / 2.0, 4)),
            )
        )
    return out


def _try_shelf_pack_groups(
    groups: Sequence[tuple[CompartmentElement, tuple[CompartmentElement, ...]]],
    comp_w: float,
    comp_l: float,
    spacing: float,
    margin: float,
    *,
    allow_rotate: bool,
    sort_mode: str,
    distribute: bool,
) -> tuple[tuple[CompartmentElement, ...], int] | None:
    """Attempt shelf-row placement of primary elements + attached children inside ``(comp_w, comp_l)``."""
    avail_w = comp_w - 2.0 * margin
    avail_l = comp_l - 2.0 * margin
    if avail_w <= 1e-6 or avail_l <= 1e-6:
        return None

    order = list(range(len(groups)))
    if sort_mode == "area_desc":
        order.sort(
            key=lambda i: groups[i][0].footprint[0] * groups[i][0].footprint[1],
            reverse=True,
        )
    elif sort_mode == "height_desc":
        order.sort(
            key=lambda i: (groups[i][0].footprint[1], groups[i][0].footprint[0]),
            reverse=True,
        )

    rows: list[tuple[list[tuple[int, float, float, float]], float]] = []
    cur_row: list[tuple[int, float, float, float]] = []
    cur_w = 0.0
    cur_h = 0.0
    used_y = 0.0

    for idx in order:
        el = groups[idx][0]
        fw0, fl0 = el.footprint
        choices: list[tuple[float, float, float]] = [(0.0, fw0, fl0)]
        if (
            allow_rotate
            and el.shape not in (ElementShape.CIRCLE, ElementShape.SPHERE_SCOOP)
            and abs(fw0 - fl0) > 1e-6
        ):
            rw, rl = replace(el, rotation=el.rotation + 90.0).footprint
            choices.append((90.0, rw, rl))

        best: tuple[float, int, float, float, float] | None = None
        for drot, w, l in choices:
            needed_w = w + (spacing if cur_row else 0.0)
            new_row_h = max(cur_h, l)
            if (
                cur_w + needed_w <= avail_w + 1e-6
                and used_y + (spacing if rows else 0.0) + new_row_h <= avail_l + 1e-6
            ):
                # Prefer fitting without increasing row height, then keep unrotated orientation.
                cand = (round(new_row_h, 4), int(drot != 0.0), drot, w, l)
                if best is None or cand < best:
                    best = cand

        if best is not None:
            _, _, drot, w, l = best
            cur_row.append((idx, drot, w, l))
            cur_w += (spacing if len(cur_row) > 1 else 0.0) + w
            cur_h = max(cur_h, l)
            continue

        if cur_row:
            rows.append((cur_row, cur_h))
            used_y += (spacing if len(rows) > 1 else 0.0) + cur_h

        best_new: tuple[float, int, float, float, float] | None = None
        for drot, w, l in choices:
            if w <= avail_w + 1e-6 and used_y + (spacing if rows else 0.0) + l <= avail_l + 1e-6:
                cand = (round(l, 4), int(drot != 0.0), drot, w, l)
                if best_new is None or cand < best_new:
                    best_new = cand
        if best_new is None:
            return None
        _, _, drot, w, l = best_new
        cur_row = [(idx, drot, w, l)]
        cur_w = w
        cur_h = l

    if cur_row:
        rows.append((cur_row, cur_h))

    row_heights = [rh for _, rh in rows]
    if distribute:
        y_dist = _distribute_linear_gap(comp_l, row_heights, spacing, margin)
        if y_dist is None:
            return None
        y_cur, y_gap = y_dist
    else:
        y_gap = spacing
        y_cur = margin

    placed_groups: dict[int, list[CompartmentElement]] = {}
    rot_count = 0
    for row_items, rh in rows:
        item_widths = [w for _, _, w, _ in row_items]
        if distribute:
            x_dist = _distribute_linear_gap(comp_w, item_widths, spacing, margin)
            if x_dist is None:
                return None
            x_cur, x_gap = x_dist
        else:
            x_gap = spacing
            x_cur = margin

        for idx, drot, w, l in row_items:
            el, children = groups[idx]
            if drot != 0.0:
                rot_count += 1
            y_item = y_cur + (rh - l) / 2.0
            new_rot = (el.rotation + drot) % 360.0 if drot else el.rotation
            placed_primary = replace(
                el,
                offset=(round(x_cur, 4), round(y_item, 4)),
                rotation=new_rot,
            )
            attached = _attach_group_children(placed_primary, children, drot)
            placed_groups[idx] = [placed_primary, *attached]
            x_cur += w + x_gap
        y_cur += rh + y_gap

    ordered: list[CompartmentElement] = []
    for idx in range(len(groups)):
        ordered.extend(placed_groups[idx])
    return tuple(ordered), rot_count


def _try_maxrects_pack_groups(
    groups: Sequence[tuple[CompartmentElement, tuple[CompartmentElement, ...]]],
    comp_w: float,
    comp_l: float,
    spacing: float,
    margin: float,
    *,
    allow_rotate: bool,
) -> tuple[tuple[CompartmentElement, ...], int] | None:
    """Fallback 2D MaxRects placement centered within ``(comp_w, comp_l)``."""
    usable_w = comp_w - 2.0 * margin
    usable_l = comp_l - 2.0 * margin
    if usable_w <= 1e-6 or usable_l <= 1e-6:
        return None

    primaries = [g[0] for g in groups]
    largest_idx = max(
        range(len(primaries)),
        key=lambda i: primaries[i].footprint[0] * primaries[i].footprint[1],
    )
    pin_sets: tuple[set[int], ...] = (
        ({largest_idx}, set()) if allow_rotate else (set(),)
    )
    for pinned in pin_sets:
        for score_mode in ("bssf", "skyline"):
            for sort_mode in ("area_desc", "max_side", "input"):
                packed = _pack_maxrects_core(
                    primaries,
                    usable_w=usable_w,
                    usable_l=usable_l,
                    spacing=spacing,
                    margin=margin,
                    allow_rotate=allow_rotate,
                    sort_mode=sort_mode,
                    score_mode=score_mode,
                    keep_unrotated=pinned,
                    overflow_fallback=False,
                )
                if packed is None:
                    continue
                min_x, min_y, max_x, max_y = elements_bounding_box(packed)
                span_w = max_x - min_x
                span_l = max_y - min_y
                if span_w > usable_w + 1e-6 or span_l > usable_l + 1e-6:
                    continue
                if elements_overlap(packed, tolerance=0.05):
                    continue

                dx = (comp_w - span_w) / 2.0 - min_x
                dy = (comp_l - span_l) / 2.0 - min_y
                ordered: list[CompartmentElement] = []
                rot_count = 0
                for idx, placed_primary in enumerate(packed):
                    orig_primary, children = groups[idx]
                    drot = (placed_primary.rotation - orig_primary.rotation) % 360.0
                    if drot != 0.0:
                        rot_count += 1
                    centered_primary = replace(
                        placed_primary,
                        offset=(
                            round(placed_primary.offset[0] + dx, 4),
                            round(placed_primary.offset[1] + dy, 4),
                        ),
                    )
                    ordered.append(centered_primary)
                    ordered.extend(_attach_group_children(centered_primary, children, drot))
                return tuple(ordered), rot_count
    return None


def pack_into_compartment(
    items: Sequence[ElementGroup],
    compartment_size: tuple[float, float],
    *,
    spacing: float = 2.0,
    min_spacing: float = 1.5,
    margin: float | None = None,
    allow_rotate: bool = True,
    distribute: bool = True,
) -> tuple[CompartmentElement, ...]:
    """Auto-lay out elements inside a fixed-size compartment interior.

    Preserves the compartment's fixed dimensions (never altering the owning box's
    size) while arranging piece slots with balanced margins, divider gaps and
    room for ``pull_out`` finger access.

    Each entry in ``items`` may be either a standalone :class:`CompartmentElement`
    or a sequence ``(primary, child1, ...)`` whose trailing child elements
    (e.g. floor inlays or stacked Z wells) stay centered on ``primary`` and
    rotate alongside it.
    """
    if not items:
        return ()

    comp_w, comp_l = compartment_size
    groups: list[tuple[CompartmentElement, tuple[CompartmentElement, ...]]] = []
    for item in items:
        if isinstance(item, CompartmentElement):
            groups.append((item, ()))
        else:
            item_seq = tuple(item)
            if not item_seq:
                continue
            groups.append((item_seq[0], item_seq[1:]))
    if not groups:
        return ()

    base_margin = float(spacing if margin is None else margin)
    tiers: list[tuple[float, float]] = [(base_margin, float(spacing))]
    if margin is None:
        if base_margin > 1.0:
            tiers.append((1.0, float(spacing)))
        if base_margin > 0.0:
            tiers.append((0.0, float(spacing)))
        if min_spacing < spacing:
            tiers.append((0.0, float(min_spacing)))

    rot_modes = (False, True) if allow_rotate else (False,)
    for tier_margin, tier_spacing in tiers:
        candidates: list[tuple[tuple[int, int, float], tuple[CompartmentElement, ...]]] = []
        for rot_flag in rot_modes:
            for sort_mode in ("input", "area_desc", "height_desc"):
                res = _try_shelf_pack_groups(
                    groups,
                    comp_w,
                    comp_l,
                    tier_spacing,
                    tier_margin,
                    allow_rotate=rot_flag,
                    sort_mode=sort_mode,
                    distribute=distribute,
                )
                if res is not None:
                    packed, rot_count = res
                    bb = elements_bounding_box([el for el in packed if el.color is None])
                    # Measure smallest edge clearance so pull-outs keep room when possible.
                    min_edge = min(bb[0], bb[1], comp_w - bb[2], comp_l - bb[3])
                    candidates.append(((int(rot_count > 0), rot_count, -round(min_edge, 3)), packed))
            if not candidates:
                mr_res = _try_maxrects_pack_groups(
                    groups,
                    comp_w,
                    comp_l,
                    tier_spacing,
                    tier_margin,
                    allow_rotate=rot_flag,
                )
                if mr_res is not None:
                    packed, rot_count = mr_res
                    bb = elements_bounding_box([el for el in packed if el.color is None])
                    min_edge = min(bb[0], bb[1], comp_w - bb[2], comp_l - bb[3])
                    candidates.append(((int(rot_count > 0), rot_count, -round(min_edge, 3)), packed))
        if candidates:
            candidates.sort(key=lambda pair: pair[0])
            return candidates[0][1]

    raise ValueError(
        f"Cannot pack {len(groups)} elements into compartment size ({comp_w:.2f}, {comp_l:.2f})"
    )


def elements_overlap(
    elements: Sequence[CompartmentElement], tolerance: float = 0.0
) -> list[tuple[str, str]]:
    """Return the pairs of elements whose bounding boxes intersect.

    Bounding-box based, matching how the layout engine reasons about
    non-rectangular shapes (FR-004a). `tolerance` shrinks each box before the
    test, so silhouettes that only graze one another are not reported.
    """
    hits: list[tuple[str, str]] = []
    for i, a in enumerate(elements):
        ax0, ay0, ax1, ay1 = a.bounds()
        for b in elements[i + 1 :]:
            bx0, by0, bx1, by1 = b.bounds()
            if (
                ax0 + tolerance < bx1
                and bx0 + tolerance < ax1
                and ay0 + tolerance < by1
                and by0 + tolerance < ay1
            ):
                hits.append((_name(a), _name(b)))
    return hits


def _name(element: CompartmentElement) -> str:
    return element.label or element.shape_file or element.shape.value


# ------------------------------------------------------------------ geometry


def build_element(
    element: CompartmentElement, default_depth: float
) -> Bosl2Solid:
    """Build the cutout solid for one element, in the compartment's local frame.

    pybosl2 primitives are centre-anchored, so each branch below builds its shape
    around the origin, rotation spins it in place, and one final translate puts
    the element's lower-left corner on its `offset` with its floor at
    `z_offset`. The result can be subtracted from a box body once the compartment
    has been moved into the interior frame.
    """
    from pybosl2 import cuboid, cylinder, regular_prism, sphere

    assert element.size is not None
    w, l = element.size
    depth = element.depth if element.depth is not None else default_depth
    actual_z_offset = element.z_offset if element.z_offset is not None else (default_depth - depth)
    base_w, _ = element.base_footprint

    # A scoop is a ball resting ON the floor, not a well sunk into it, so it
    # lifts by its radius while every other shape lifts by half its depth.
    z_lift = base_w / 2 if element.shape is ElementShape.SPHERE_SCOOP else depth / 2

    if element.shape is ElementShape.SVG:
        assert element.shape_file is not None
        solid = svg_solid(element.shape_file, w, l, depth)
    elif element.shape is ElementShape.TEXT:
        from pybosl2.shapes2d.ops import text
        assert element.shape_file is not None
        font_size = min(w / len(element.shape_file) * 1.5, l * 0.7)
        solid = text(
            element.shape_file,
            font="Liberation Sans:style=Bold",
            size=font_size,
            halign="center",
            valign="center"
        ).linear_extrude(height=depth)
    elif element.shape is ElementShape.CIRCLE:
        if element.bottom_rounding > 0:
            solid = cylinder(
                height=depth, radius=base_w / 2, rounding1=element.bottom_rounding,
                **precision_kwargs()
            )
        else:
            solid = cylinder(height=depth, radius=base_w / 2, **precision_kwargs())
    elif element.shape is ElementShape.HEXAGON:
        # `w` is the flat-to-flat width, as `RegularPolygon(width=...)` reads it.
        solid = regular_prism(
            6, height=depth, radius=w / 2 / math.cos(math.radians(30))
        )
    elif element.shape is ElementShape.SPHERE_SCOOP:
        solid = sphere(radius=base_w / 2, **precision_kwargs())
    elif element.shape is ElementShape.ROUNDED_RECT:
        solid = cuboid([w, l, depth], rounding=element.corner_radius, edges=vertical_edges(),
                       **precision_kwargs())
        if element.bottom_rounding > 0:
            from pybosl2 import Anchor

            from pyboxbuilder.rounding import round_edges
            solid = round_edges(
                solid, [w, l, depth], element.bottom_rounding, [Anchor.BOTTOM],
                at=(-w / 2, -l / 2, -depth / 2),
            )
    else:
        if element.corner_rounding > 0:
            solid = cuboid([w, l, depth], rounding=element.corner_rounding, edges=vertical_edges(),
                           **precision_kwargs())
        else:
            solid = cuboid([w, l, depth])
        if element.bottom_rounding > 0:
            from pybosl2 import Anchor

            from pyboxbuilder.rounding import round_edges
            solid = round_edges(
                solid, [w, l, depth], element.bottom_rounding, [Anchor.BOTTOM],
                at=(-w / 2, -l / 2, -depth / 2),
            )

    if element.rotation:
        solid = solid.rotate([0.0, 0.0, element.rotation])

    footprint_w, footprint_l = element.footprint
    return solid.translate([
        element.offset[0] + footprint_w / 2,
        element.offset[1] + footprint_l / 2,
        actual_z_offset + z_lift,
    ])


def svg_solid(shape_file: str, width: float, length: float, depth: float) -> Bosl2Solid:
    """Extrude an SVG outline and scale it to fill `width` x `length` x `depth`.

    Returned centred on the origin, matching every pybosl2 primitive, so callers
    can place it the same way they place a cuboid.
    """
    solid = _svg_region(shape_file).linear_extrude(height=depth)
    b = solid.bounds()
    if hasattr(b, "center") and hasattr(b, "size"):
        cx, cy, cz = float(b.center[0]), float(b.center[1]), float(b.center[2])
        span_x, span_y = float(b.size[0]), float(b.size[1])
    else:
        cx, cy, cz = float(b[0][0]), float(b[0][1]), float(b[0][2])
        span_x, span_y = float(b[1][0]), float(b[1][1])
    solid = solid.translate([-float(cx), -float(cy), -float(cz)])
    return solid.scale([
        width / max(float(span_x), 1e-9),
        length / max(float(span_y), 1e-9),
        1.0,
    ])


def _svg_region(shape_file: str) -> Region:
    """Parse an SVG once and reuse it — a pack repeats the same file many times.

    ``clip_to_viewbox=False`` is deliberate: pybosl2's default viewport clip
    flattens nested subpaths through a ``unary_union`` before clipping, which
    destroys the holes (windows, ring gaps) a silhouette draws with the
    even-odd rule. Box SVGs size their viewBox to the drawing, so skipping the
    clip loses nothing and keeps the cutouts.
    """
    from pathlib import Path

    from pybosl2.svg import region_from_svg

    path = Path(shape_file)
    if not path.is_absolute() and not path.exists():
        repo_root = Path(__file__).resolve().parents[2]
        resolved = repo_root / path
        if resolved.exists():
            path = resolved
    mtime = path.stat().st_mtime_ns if path.exists() else 0
    cache_key = (str(path), mtime)
    region = _SVG_CACHE.get(cache_key)
    if region is None:
        try:
            region = region_from_svg(str(path), **{"clip_to_viewbox": False})
        except TypeError:
            region = region_from_svg(str(path))
        _SVG_CACHE[cache_key] = region
    return region


_SVG_CACHE: dict[tuple[str, int], Region] = {}


PULL_OUT_DEPTH_SHARE = 0.5
"""How deep a pull-out goes, as a share of the piece's depth.

Half gets a fingertip under the piece while leaving the slot deep enough that
the piece still seats flat in it rather than tipping into the dish.
"""

DEFAULT_PULL_OUT_WIDTH_MM = 16.0
"""Fingertip width for a pull-out dish, when the element names none."""


def build_pull_out(
    element: CompartmentElement,
    default_depth: float,
    comp_size: tuple[float, float] = (1000.0, 1000.0),
    force_axis: str | None = None,
) -> Bosl2Solid | None:
    """Return the finger dish that lets a piece be lifted out of its slot.

    Cut across the slot and **curved in from the surrounding floor** on both
    sides, so a finger slides down into it rather than meeting a step. Without
    it a silhouette slot has no purchase at all: it fits the piece exactly,
    which is what makes it look right and what makes it impossible to empty.

    """
    if not element.pull_out:
        return None

    from pybosl2 import cuboid

    from pyboxbuilder.rounding import rounding_facets

    assert element.size is not None
    width, length = element.footprint
    depth = element.depth or default_depth
    actual_z_offset = element.z_offset if element.z_offset is not None else (default_depth - depth)
    drop = (element.pull_out_depth / 2.0) if element.pull_out_depth is not None else (depth * PULL_OUT_DEPTH_SHARE)
    across = min(element.pull_out_width or DEFAULT_PULL_OUT_WIDTH_MM, max(width, length))

    # Calculate clearances to compartment boundaries to automatically pick the direction with most room
    comp_w, comp_l = comp_size
    clearance_x_left = element.offset[0]
    clearance_x_right = comp_w - (element.offset[0] + width)
    clearance_y_front = element.offset[1]
    clearance_y_back = comp_l - (element.offset[1] + length)

    clearance_x = min(clearance_x_left, clearance_x_right)
    clearance_y = min(clearance_y_front, clearance_y_back)

    use_y = force_axis == "y" if force_axis is not None else clearance_y >= clearance_x

    if use_y:
        # Orient along Y (lengthwise)
        drop_front = max(0.0, min(drop, clearance_y_front))
        drop_back = max(0.0, min(drop, clearance_y_back))
        actual_drop = max(0.1, max(drop_front, drop_back))
        centre_x = element.offset[0] + width / 2
        centre_y = element.offset[1] + length / 2 + (drop_back - drop_front) / 2
        dish_w, dish_l = across, length + drop_front + drop_back
    else:
        # Orient along X (widthwise)
        drop_left = max(0.0, min(drop, clearance_x_left))
        drop_right = max(0.0, min(drop, clearance_x_right))
        actual_drop = max(0.1, max(drop_left, drop_right))
        centre_x = element.offset[0] + width / 2 + (drop_right - drop_left) / 2
        centre_y = element.offset[1] + length / 2
        dish_w, dish_l = width + drop_left + drop_right, across

    radius = min(actual_drop, dish_w / 2 - 0.01, dish_l / 2 - 0.01)
    z = actual_z_offset + depth - actual_drop

    from pybosl2 import Anchor
    # Round all bottom edges (sides plus entry/exit ramps) so a finger slides smoothly
    # down into the trough from any side rather than meeting a square vertical step.
    dish_edges = [Anchor.BOTTOM, *vertical_edges()]
    dish = cuboid(
        [dish_w, dish_l, actual_drop * 2],
        rounding=radius,
        edges=dish_edges,
        **rounding_facets(),
    ) if radius > 0 else cuboid([dish_w, dish_l, actual_drop * 2])
    dish = dish.translate([centre_x, centre_y, z])

    # Extend the pull-out upwards from its center to prevent top tapering, keeping the sides rounded.
    block = cuboid(
        [dish_w, dish_l, 100.0],
        rounding=radius,
        edges=vertical_edges(),
        **rounding_facets(),
    ) if radius > 0 else cuboid([dish_w, dish_l, 100.0])
    block = block.translate([centre_x, centre_y, z + 50.0])
    return union_all([dish, block])


def build_element_pack(
    elements: Iterable[CompartmentElement], default_depth: float
) -> Bosl2Solid | None:
    """Union every element cutout in a pack. Returns None for an empty pack.

    A coloured element is carved *and* filled: it is included here so its
    silhouette is recessed into the well floor, and
    :func:`~pyboxbuilder.compartments.element.build_element_pack_inserts` supplies the coloured solid that fills
    that recess — together they make an inlay flush with the floor rather than
    a bump proud of it.
    """
    pieces = []
    for element in elements:
        pieces.append(build_element(element, default_depth))
    return union_all([p for p in pieces if p is not None])


def build_element_pack_inserts(
    elements: Iterable[CompartmentElement], default_depth: float
) -> list[tuple[Bosl2Solid, Color]]:
    """Build the coloured positive inserts of a pack, one per coloured element.

    Each insert is the element's own silhouette at its own depth and offset,
    returned uncoloured alongside its colour so the caller can print it as a
    separate material (mmu) or draw it in the right colour (preview). A pack
    with no coloured elements yields an empty list.
    """
    from pybosl2 import Color

    inserts: list[tuple[Bosl2Solid, Color]] = []
    for element in elements:
        if element.color is None:
            continue
        solid = build_element(element, default_depth)
        if solid is not None:
            inserts.append((solid, Color(element.color)))
    return inserts


def build_element_pack_pull_outs(
    elements: Iterable[CompartmentElement], default_depth: float, comp_size: tuple[float, float]
) -> Bosl2Solid | None:
    """Union every pull-out scoop in a pack, hulling overlapping scoops to avoid sharp edges."""
    elements_list = [el for el in elements if el.pull_out and el.color is None]
    if not elements_list:
        return None

    comp_w, comp_l = comp_size
    # Align all scoops in the compartment along the overall best axis.
    comp_w, comp_l = comp_size
    sum_clearance_x = 0.0
    sum_clearance_y = 0.0
    for element in elements_list:
        assert element.size is not None
        width, length = element.footprint
        sum_clearance_x += min(element.offset[0], comp_w - (element.offset[0] + width))
        sum_clearance_y += min(element.offset[1], comp_l - (element.offset[1] + length))

    use_y = sum_clearance_y >= sum_clearance_x

    # Map each element to its individual pull_out solid and its footprint bounds
    built_pieces = []
    for element in elements_list:
        solid = build_pull_out(element, default_depth, comp_size, force_axis="y" if use_y else "x")
        if solid is None:
            continue

        assert element.size is not None
        width, length = element.footprint
        depth = element.depth or default_depth
        drop = (element.pull_out_depth / 2.0) if element.pull_out_depth is not None else (depth * PULL_OUT_DEPTH_SHARE)

        if use_y:
            clearance_y_front = element.offset[1]
            clearance_y_back = comp_l - (element.offset[1] + length)
            drop_front = max(0.0, min(drop, clearance_y_front))
            drop_back = max(0.0, min(drop, clearance_y_back))

            min_x = element.offset[0]
            max_x = element.offset[0] + width
            min_y = element.offset[1] - drop_front
            max_y = element.offset[1] + length + drop_back
        else:
            clearance_x_left = element.offset[0]
            clearance_x_right = comp_w - (element.offset[0] + width)
            drop_left = max(0.0, min(drop, clearance_x_left))
            drop_right = max(0.0, min(drop, clearance_x_right))

            min_x = element.offset[0] - drop_left
            max_x = element.offset[0] + width + drop_right
            min_y = element.offset[1]
            max_y = element.offset[1] + length

        built_pieces.append({
            'solid': solid,
            'min_x': min_x, 'max_x': max_x,
            'min_y': min_y, 'max_y': max_y
        })

    # Group overlapping pieces
    groups: list[list[dict[str, Any]]] = []
    for p in built_pieces:
        matched_indices = []
        for idx, g in enumerate(groups):
            overlaps = False
            for other in g:
                tol = 0.5
                if use_y:
                    x_match = abs(p['min_x'] - other['min_x']) < 1.0 and abs(p['max_x'] - other['max_x']) < 1.0
                    y_overlap = p['min_y'] - tol < other['max_y'] and other['min_y'] - tol < p['max_y']
                    overlaps = x_match and y_overlap
                else:
                    y_match = abs(p['min_y'] - other['min_y']) < 1.0 and abs(p['max_y'] - other['max_y']) < 1.0
                    x_overlap = p['min_x'] - tol < other['max_x'] and other['min_x'] - tol < p['max_x']
                    overlaps = y_match and x_overlap
                if overlaps:
                    break
            if overlaps:
                matched_indices.append(idx)

        if not matched_indices:
            groups.append([p])
        else:
            new_group = [p]
            for idx in reversed(matched_indices):
                new_group.extend(groups.pop(idx))
            groups.append(new_group)

    # Hull overlapping groups, union non-overlapping ones
    final_solids = []
    from pybosl2._native import native
    from pybosl2.shapes3d.base import CsgSolid
    hull_fn = native("hull")

    for g in groups:
        if len(g) == 1:
            final_solids.append(g[0]['solid'])
        else:
            raw_shapes = [p['solid'].shape for p in g]
            final_solids.append(CsgSolid(hull_fn(raw_shapes)))

    return union_all([p for p in final_solids if p is not None])


def union_all(solids: list[Bosl2Solid]) -> Bosl2Solid | None:
    """Union a list of solids with a balanced fold.

    A left fold builds a chain as deep as the list, which the mesher pays for on
    every cell of a big pack; halving keeps the tree logarithmic.
    """
    if not solids:
        return None
    while len(solids) > 1:
        solids = [
            a | b if b is not None else a
            for a, b in zip(solids[::2], [*list(solids[1::2]), None], strict=False)
        ]
    return solids[0]


def centered(
    shape_file: str | None,
    center: tuple[float, float],
    size: tuple[float, float],
    *,
    shape: ElementShape = ElementShape.SVG,
    rotation: float = 0.0,
    label: str | None = None,
    pull_out: bool = True,
    **pocket_kwargs: Any,
) -> CompartmentElement:
    """Return a CompartmentElement centered at the given coordinate."""
    from pyboxbuilder.enums import ElementShape

    if shape_file is None and shape == ElementShape.SVG:
        shape = ElementShape.RECT
    proto = CompartmentElement(
        shape_file=shape_file,
        offset=(0.0, 0.0),
        size=size,
        shape=shape,
        rotation=rotation,
        label=label,
        pull_out=pull_out,
        **pocket_kwargs,
    )
    fw, fl = proto.footprint
    return CompartmentElement(
        shape_file=shape_file,
        offset=(center[0] - fw / 2, center[1] - fl / 2),
        size=size,
        shape=shape,
        rotation=rotation,
        label=label,
        pull_out=pull_out,
        **pocket_kwargs,
    )


def centered_in_box(
    shape_file: str | None,
    box_size: tuple[float, float, float],
    element_size: tuple[float, float],
    wall_thickness: float = 2.0,
    **kwargs: Any,
) -> CompartmentElement:
    """Return a CompartmentElement centered exactly in a box's interior frame."""
    interior_w = box_size[0] - 2 * wall_thickness
    interior_l = box_size[1] - 2 * wall_thickness
    return centered(
        shape_file, (interior_w / 2, interior_l / 2), element_size, **kwargs
    )
