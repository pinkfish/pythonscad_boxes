# SPDX-License-Identifier: Apache-2.0
"""Box packing layout — constraint-aware 3D box packing into game box interior."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from itertools import pairwise
from typing import Any


class PackingError(ValueError):
    """Raised when the sub-boxes cannot be arranged inside the game box.

    Note that the packer is a bounded search, so this does not prove the
    layout is impossible — only that the solver could not find it.
    """


@dataclass
class Placement:
    """Position and size of one box in the nested layout."""

    label: str
    position: tuple[float, float, float]
    size: tuple[float, float, float]
    rotation: bool = False
    path: tuple[tuple[float, float], ...] | None = None
    """Footprint outline relative to `position`, when it is not a rectangle.

    Set on spacers whose leftover region is L-, T- or U-shaped (FR-018); such a
    spacer is built as a `PathBox` rather than a plain tray. None means the
    footprint is just `size`."""


@dataclass
class BoxPacking:
    """Computed nested layout of sub-boxes inside a container."""

    container_size: tuple[float, float, float]
    placements: list[Placement] = field(default_factory=list)
    row_lengths: list[float] = field(default_factory=list)
    row_widths: list[float] = field(default_factory=list)
    spacer_placements: list[Placement] = field(default_factory=list)


HEIGHT_ABSORB_MM = 3.0
"""A gap above an expandable box no deeper than this is absorbed into it (FR-012)."""


def _intervals_cover(
    intervals: list[tuple[float, float]], lo: float, hi: float, eps: float = 1e-5
) -> bool:
    """Return True when ``[lo, hi]`` is continuously covered by ``intervals``."""
    if hi <= lo + eps:
        return True
    relevant = sorted(
        (max(lo, a), min(hi, b)) for a, b in intervals if b > lo + eps and a < hi - eps
    )
    if not relevant or relevant[0][0] > lo + eps:
        return False
    reach = relevant[0][1]
    for a, b in relevant[1:]:
        if a > reach + eps:
            return False
        reach = max(reach, b)
    return reach >= hi - eps


def _max_supported_wall(
    p: Placement,
    all_placements: Sequence[Placement],
    limit: float,
    axis: int,
) -> float:
    """Return the furthest ``+X`` (axis=0) or ``+Y`` (axis=1) coordinate supported beneath ``p``."""
    x, y, z = p.position
    w, l, _ = p.size
    cur_end = (x + w) if axis == 0 else (y + l)
    if z <= 1e-5 or limit <= cur_end + 1e-6:
        return limit

    supporters = [
        o
        for o in all_placements
        if o is not p and abs((o.position[2] + o.size[2]) - z) <= 1e-4
    ]
    if not supporters:
        return cur_end

    if axis == 0:
        cuts = sorted({
            cur_end,
            limit,
            *(
                v
                for o in supporters
                for v in (o.position[0], o.position[0] + o.size[0])
                if cur_end + 1e-6 < v < limit - 1e-6
            ),
        })
        supported_end = cur_end
        for xa, xb in pairwise(cuts):
            y_spans = [
                (o.position[1], o.position[1] + o.size[1])
                for o in supporters
                if o.position[0] <= xa + 1e-5 and o.position[0] + o.size[0] >= xb - 1e-5
            ]
            if _intervals_cover(y_spans, y, y + l):
                supported_end = xb
            else:
                break
        return supported_end

    cuts_y = sorted({
        cur_end,
        limit,
        *(
            v
            for o in supporters
            for v in (o.position[1], o.position[1] + o.size[1])
            if cur_end + 1e-6 < v < limit - 1e-6
        ),
    })
    supported_end = cur_end
    for ya, yb in pairwise(cuts_y):
        x_spans = [
            (o.position[0], o.position[0] + o.size[0])
            for o in supporters
            if o.position[1] <= ya + 1e-5 and o.position[1] + o.size[1] >= yb - 1e-5
        ]
        if _intervals_cover(x_spans, x, x + w):
            supported_end = yb
        else:
            break
    return supported_end


def _pack_guillotine(
    container_size: tuple[float, float, float],
    boxes: list[dict[str, Any]],
    obstacles: Sequence[tuple[float, float, float, float, float, float]] = (),
) -> list[Placement] | None:
    """Try the guillotine solver, returning None if it finds nothing."""
    from pyboxbuilder.packing.guillotine import Item, pack_guillotine

    placed = pack_guillotine(
        container_size,
        [
            Item(
                label=b["label"],
                size=tuple(float(v) for v in b["size"]),  # type: ignore[arg-type]
                no_rotate=bool(b.get("no_rotate", False)),
                size_options=tuple(
                    (float(s[0]), float(s[1]), float(s[2]))
                    for s in b.get("size_options", ())
                ),
                stack_members=tuple(
                    (str(m[0]), (float(m[1][0]), float(m[1][1]), float(m[1][2])))
                    for m in b.get("stack_members", ())
                ),
            )
            for b in boxes
        ],
        obstacles=obstacles,
    )
    if placed is None:
        return None
    return [
        Placement(
            label=p.label,
            position=p.position,
            size=p.size,
            rotation=p.rotated,
        )
        for p in placed
    ]


def _pack_extreme_points_supported(
    container_size: tuple[float, float, float],
    boxes: list[dict[str, Any]],
    obstacles: Sequence[tuple[float, float, float, float, float, float]] = (),
) -> list[Placement] | None:
    """Non-guillotine extreme-point fallback (e.g. 4-box pinwheels) with strict 100% support."""
    cw, cl, ch = container_size
    placed: list[Placement] = [
        Placement(f"__obs_{i}", (ox, oy, oz), (ow, ol, oh))
        for i, (ox, oy, oz, ow, ol, oh) in enumerate(obstacles)
    ]
    n_obs = len(placed)

    eps: set[tuple[float, float, float]] = {(0.0, 0.0, 0.0)}
    for ox, oy, oz, ow, ol, oh in obstacles:
        eps.update({
            (ox + ow, oy, oz),
            (ox, oy + ol, oz),
            (ox, oy, oz + oh),
        })

    # Flatten stack_members if any
    flat_boxes: list[dict[str, Any]] = []
    for b in boxes:
        if b.get("stack_members"):
            for mlbl, msz in b["stack_members"]:
                flat_boxes.append({
                    "label": mlbl,
                    "size": msz,
                    "no_rotate": b.get("no_rotate", False),
                })
        else:
            flat_boxes.append(b)

    ordered = sorted(
        flat_boxes,
        key=lambda b: b["size"][0] * b["size"][1] * b["size"][2],
        reverse=True,
    )

    for b in ordered:
        bw0, bl0, bh = float(b["size"][0]), float(b["size"][1]), float(b["size"][2])
        orients = [(bw0, bl0, False)]
        if not b.get("no_rotate", False) and abs(bw0 - bl0) > 1e-6:
            orients.append((bl0, bw0, True))

        best_pos: tuple[float, float, float, float, float, bool] | None = None
        for px, py, pz in sorted(eps, key=lambda pt: (pt[2], pt[1], pt[0])):
            for bw, bl, rot in orients:
                if px + bw > cw + 1e-6 or py + bl > cl + 1e-6 or pz + bh > ch + 1e-6:
                    continue
                # Overlap test
                if any(
                    px < o.position[0] + o.size[0] - 1e-6
                    and px + bw > o.position[0] + 1e-6
                    and py < o.position[1] + o.size[1] - 1e-6
                    and py + bl > o.position[1] + 1e-6
                    and pz < o.position[2] + o.size[2] - 1e-6
                    and pz + bh > o.position[2] + 1e-6
                    for o in placed
                ):
                    continue
                # Full base support test
                probe = Placement(b["label"], (px, py, pz), (bw, bl, 0.0))
                if _max_supported_wall(probe, placed, px + bw, axis=0) < px + bw - 1e-5:
                    continue
                best_pos = (px, py, pz, bw, bl, rot)
                break
            if best_pos is not None:
                break

        if best_pos is None:
            return None

        px, py, pz, bw, bl, rot = best_pos
        placed.append(Placement(b["label"], (px, py, pz), (bw, bl, bh), rotation=rot))
        eps.discard((px, py, pz))
        eps.update({
            (px + bw, py, pz),
            (px, py + bl, pz),
            (px, py, pz + bh),
        })

    return placed[n_obs:]


def _expand_in_place(
    placements: list[Placement],
    container_size: tuple[float, float, float],
    boxes: list[dict[str, Any]],
    gap_threshold: float = 10.0,
    obstacles: Sequence[tuple[float, float, float, float, float, float]] = (),
) -> None:
    """Grow expandable boxes into adjacent slack while preserving 100% base support (FR-012)."""
    container_w, container_l, container_h = container_size
    axes: dict[str, tuple[bool, bool, bool]] = {}
    for b in boxes:
        exp = bool(b.get("expandable"))
        exp_w = exp and bool(b.get("expandable_width", True))
        exp_l = exp and bool(b.get("expandable_length", True))
        if b.get("stack_members"):
            for mlbl, _ in b["stack_members"]:
                axes[str(mlbl)] = (exp, exp_w, exp_l)
        else:
            axes[b["label"]] = (exp, exp_w, exp_l)

    obs_placements = [
        Placement(f"__obs_{i}", (ox, oy, oz), (ow, ol, oh))
        for i, (ox, oy, oz, ow, ol, oh) in enumerate(obstacles)
    ]

    def sized(
        placement: Placement,
        width: float | None = None,
        length: float | None = None,
        height: float | None = None,
    ) -> Placement:
        w, l, h = placement.size
        return Placement(
            label=placement.label,
            position=placement.position,
            size=(
                width if width is not None else w,
                length if length is not None else l,
                height if height is not None else h,
            ),
            rotation=placement.rotation,
            path=placement.path,
        )

    # 1. Close sub-3mm headroom gaps above expandable boxes
    for index, p in enumerate(placements):
        if not axes.get(p.label, (False, False, False))[0]:
            continue
        x, y, z = p.position
        w, l, h = p.size
        ceiling = float(container_h)
        for other in (*placements, *obs_placements):
            if other is p:
                continue
            ox, oy, oz = other.position
            ow, ol, _oh = other.size
            if (
                x < ox + ow - 1e-6
                and x + w > ox + 1e-6
                and y < oy + ol - 1e-6
                and y + l > oy + 1e-6
                and oz >= z + h - 1e-6
            ):
                ceiling = min(ceiling, oz)
        if 0.0 < (ceiling - z) - h < HEIGHT_ABSORB_MM:
            placements[index] = sized(p, height=ceiling - z)

    # 2. Grow along container +X (respecting rotation mapping and 100% base support!)
    for index, p in enumerate(placements):
        exp_h, exp_w, exp_l = axes.get(p.label, (False, False, False))
        can_grow_x = exp_l if p.rotation else exp_w
        if not (exp_h and can_grow_x):
            continue
        x, y, z = p.position
        w, l, h = p.size
        wall = float(container_w)
        for other in (*placements, *obs_placements):
            if other is p:
                continue
            ox, oy, oz = other.position
            _ow, ol, oh = other.size
            if (
                y < oy + ol - 1e-6
                and y + l > oy + 1e-6
                and z < oz + oh - 1e-6
                and z + h > oz + 1e-6
                and ox >= x + w - 1e-6
            ):
                wall = min(wall, ox)
        wall = _max_supported_wall(p, (*placements, *obs_placements), wall, axis=0)
        if wall > x + w + 1e-6:
            placements[index] = sized(p, width=wall - x)

    # 3. Absorb shallow +Y slivers up to `gap_threshold` (with 100% base support)
    if gap_threshold > 0:
        for index, p in enumerate(placements):
            exp_h, exp_w, exp_l = axes.get(p.label, (False, False, False))
            can_grow_y = exp_w if p.rotation else exp_l
            if not (exp_h and can_grow_y):
                continue
            x, y, z = p.position
            w, l, h = p.size
            wall_y = float(container_l)
            for other in (*placements, *obs_placements):
                if other is p:
                    continue
                ox, oy, oz = other.position
                ow, _ol, oh = other.size
                if (
                    x < ox + ow - 1e-6
                    and x + w > ox + 1e-6
                    and z < oz + oh - 1e-6
                    and z + h > oz + 1e-6
                    and oy >= y + l - 1e-6
                ):
                    wall_y = min(wall_y, oy)
            wall_y = _max_supported_wall(p, (*placements, *obs_placements), wall_y, axis=1)
            gap_y = wall_y - (y + l)
            if 1e-6 < gap_y <= gap_threshold + 1e-6:
                placements[index] = sized(p, length=wall_y - y)


def pack_boxes(
    container_size: tuple[float, float, float],
    boxes: list[dict[str, Any]],
    gap_threshold: float = 10.0,
    min_spacer_dim: float = 15.0,
    obstacles: Sequence[tuple[float, float, float, float, float, float]] = (),
) -> BoxPacking:
    """Pack sub-boxes into a container using 3D Guillotine + Extreme-Point fallback.

    Args:
        container_size: (width, length, height) of the outer box interior.
        boxes: List of dicts with keys: label, size (w, l, h), expandable, etc.
        gap_threshold: Shallow Y gaps <= this are absorbed into expandable boxes.
        min_spacer_dim: Minimum spacer dimension before absorption.
        obstacles: Pinned ``(x, y, z, w, l, h)`` regions already occupied.

    Returns:
        BoxPacking with placements assigned.

    """
    from pyboxbuilder.packing.cache import cache_key, get_memory_cached, set_memory_cached

    packing = BoxPacking(container_size=container_size)
    if not boxes:
        return packing

    ckey = cache_key({
        "container": list(container_size),
        "boxes": boxes,
        "gap_threshold": gap_threshold,
        "obstacles": [list(o) for o in obstacles],
    })
    cached = get_memory_cached(ckey)
    if cached is not None:
        packing.placements = [
            Placement(
                label=d["label"],
                position=(float(d["position"][0]), float(d["position"][1]), float(d["position"][2])),
                size=(float(d["size"][0]), float(d["size"][1]), float(d["size"][2])),
                rotation=bool(d["rotation"]),
            )
            for d in cached
        ]
        return packing

    placed = _pack_guillotine(container_size, boxes, obstacles=obstacles)
    if placed is None:
        placed = _pack_extreme_points_supported(container_size, boxes, obstacles=obstacles)

    if placed is None:
        box_volume = sum(b["size"][0] * b["size"][1] * b["size"][2] for b in boxes)
        obs_volume = sum(o[3] * o[4] * o[5] for o in obstacles)
        container_volume = container_size[0] * container_size[1] * container_size[2]
        fill = 100 * (box_volume + obs_volume) / container_volume if container_volume > 0 else 0.0
        too_tall = [
            b["label"] for b in boxes if b["size"][2] > container_size[2] + 1e-6
        ]
        detail = (
            f" Boxes taller than the container: {', '.join(too_tall)}."
            if too_tall
            else f" At {fill:.0f}% fill no valid supported arrangement was found — "
            f"give the boxes explicit positions, or make them smaller."
        )
        raise PackingError(
            f"Could not pack {len(boxes)} boxes into "
            f"{container_size[0]:.1f} x {container_size[1]:.1f} x "
            f"{container_size[2]:.1f} mm.{detail}"
        )

    packing.placements = placed
    _expand_in_place(
        packing.placements,
        container_size,
        boxes,
        gap_threshold=gap_threshold,
        obstacles=obstacles,
    )

    set_memory_cached(
        ckey,
        [
            {
                "label": p.label,
                "position": list(p.position),
                "size": list(p.size),
                "rotation": p.rotation,
            }
            for p in packing.placements
        ],
    )
    return packing
