# SPDX-License-Identifier: Apache-2.0
"""PDF packing guide — layered exploded breakdown with arrows."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from pyboxbuilder.deps import require
from pyboxbuilder.packing.layout import Placement

if TYPE_CHECKING:
    from fpdf import FPDF

    from pyboxbuilder.builders._base import BoxBuilder
    from pyboxbuilder.packing.layout import BoxPacking
    from pyboxbuilder.project.manifest import ProjectManifest
    from pyboxbuilder.project.pipeline import GeometryPipeline


@dataclass(frozen=True)
class LayerPage:
    """One page of the packing guide: the layer it shows, and what is under it.

    A record rather than a dict, so a typo in a key is an error at the line
    that made it rather than a `KeyError` three hundred lines later — and so
    the placements keep their type on the way through.
    """

    name: str
    """The layer's name, as printed on the page."""
    active_placements: list[Placement]
    """Boxes belonging to this layer, drawn in full colour."""
    lower_placements: list[Placement]
    """Boxes already packed beneath it, drawn in light grey for context."""
    active_spacers: list[Placement]
    """Spacer trays belonging to this layer."""
    lower_spacers: list[Placement]
    """Spacer trays beneath it."""


def _polygon_signed_area(pts: list[tuple[float, float]]) -> float:
    n = len(pts)
    return 0.5 * sum(
        pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1]
        for i in range(n)
    )


def _point_in_rectilinear_poly(
    px: float, py: float, pts: list[tuple[float, float]]
) -> bool:
    inside = False
    n = len(pts)
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        if (y1 > py) != (y2 > py):
            x_int = x1 + (py - y1) * (x2 - x1) / (y2 - y1)
            if px < x_int:
                inside = not inside
    return inside


def _polygon_interior_point(
    pts: list[tuple[float, float]], fallback: tuple[float, float]
) -> tuple[float, float]:
    """Return a well-centered point guaranteed inside a rectilinear polygon."""
    xs = sorted({round(p[0], 4) for p in pts})
    ys = sorted({round(p[1], 4) for p in pts})
    if len(xs) < 2 or len(ys) < 2:
        return fallback

    best_pt = fallback
    best_score = -1.0
    for i in range(len(xs) - 1):
        mx = 0.5 * (xs[i] + xs[i + 1])
        cell_w = xs[i + 1] - xs[i]
        for j in range(len(ys) - 1):
            my = 0.5 * (ys[j] + ys[j + 1])
            cell_h = ys[j + 1] - ys[j]
            if _point_in_rectilinear_poly(mx, my, pts):
                score = cell_w * cell_h
                if score > best_score:
                    best_score = score
                    best_pt = (mx, my)
    return best_pt


def _placement_subrects(
    p: Placement,
) -> list[tuple[float, float, float, float, float, float]]:
    """Decompose a placement (cuboid or rectilinear polygon) into 3D sub-cuboids."""
    x0, y0, z0 = p.position
    bw, bl, bh = p.size
    if not p.path or len(p.path) < 4:
        return [(x0, x0 + bw, y0, y0 + bl, z0, z0 + bh)]

    pts = list(p.path)
    ys = sorted({round(pt[1], 4) for pt in pts})
    xs = sorted({round(pt[0], 4) for pt in pts})
    rects: list[tuple[float, float, float, float, float, float]] = []
    for j in range(len(ys) - 1):
        ya, yb = ys[j], ys[j + 1]
        my = 0.5 * (ya + yb)
        run_start: float | None = None
        for i in range(len(xs) - 1):
            xa, xb = xs[i], xs[i + 1]
            mx = 0.5 * (xa + xb)
            if _point_in_rectilinear_poly(mx, my, pts):
                if run_start is None:
                    run_start = xa
            elif run_start is not None:
                rects.append((x0 + run_start, x0 + xa, y0 + ya, y0 + yb, z0, z0 + bh))
                run_start = None
        if run_start is not None:
            rects.append((x0 + run_start, x0 + xs[-1], y0 + ya, y0 + yb, z0, z0 + bh))
    return rects or [(x0, x0 + bw, y0, y0 + bl, z0, z0 + bh)]


def _rect_behind_oblique(
    a: tuple[float, float, float, float, float, float],
    b: tuple[float, float, float, float, float, float],
    tol: float = 0.05,
) -> bool:
    """Return True if 3D sub-cuboid `a` is strictly behind `b` in Cabinet Oblique.

    Viewer sees Top (+Z), Front (-Y), and Right (+X) faces, so `b` is closer to
    the viewer than `a` when `b` sits above `a` (+Z), in front of `a` (-Y), or
    to the right of `a` (+X).
    """
    _ax0, ax1, ay0, ay1, az0, az1 = a
    bx0, _bx1, by0, by1, bz0, bz1 = b
    if az1 <= bz0 + tol:
        return True
    if bz1 <= az0 + tol:
        return False
    if ay0 >= by1 - tol:
        return True
    if by0 >= ay1 - tol:
        return False
    return ax1 <= bx0 + tol


def _painters_sort(
    items: list[tuple[Placement, bool]],
) -> list[tuple[Placement, bool]]:
    """Topologically sort `(placement, is_spacer)` back-to-front for Cabinet Oblique."""
    n = len(items)
    if n <= 1:
        return list(items)

    subrects = [_placement_subrects(it[0]) for it in items]
    adj: list[list[int]] = [[] for _ in range(n)]
    indeg = [0] * n

    for i in range(n):
        for j in range(i + 1, n):
            i_behind_j = False
            j_behind_i = False
            for ra in subrects[i]:
                for rb in subrects[j]:
                    if _rect_behind_oblique(ra, rb):
                        i_behind_j = True
                    elif _rect_behind_oblique(rb, ra):
                        j_behind_i = True
            if i_behind_j and not j_behind_i:
                adj[i].append(j)
                indeg[j] += 1
            elif j_behind_i and not i_behind_j:
                adj[j].append(i)
                indeg[i] += 1

    def _tie_key(idx: int) -> tuple[float, float, float, int]:
        p, is_sp = items[idx]
        return (
            round(p.position[2], 3),
            round(-p.position[1], 3),
            round(p.position[0], 3),
            0 if is_sp else 1,
        )

    ready = [i for i in range(n) if indeg[i] == 0]
    order: list[int] = []
    visited = [False] * n
    while len(order) < n:
        if not ready:
            # Break rare cyclic L-interlock ties deterministically
            rem = [i for i in range(n) if not visited[i]]
            pick = min(rem, key=_tie_key)
        else:
            ready.sort(key=_tie_key)
            pick = ready.pop(0)
        if visited[pick]:
            continue
        visited[pick] = True
        order.append(pick)
        for nxt in adj[pick]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0 and not visited[nxt]:
                ready.append(nxt)

    return [items[i] for i in order]


def _compute_layer_pages(packing: BoxPacking) -> list[LayerPage]:
    """Partition placements and spacers into clean Z-step pages."""
    all_items = [*packing.placements, *packing.spacer_placements]
    if not all_items:
        return []

    raw_zs = sorted(p.position[2] for p in all_items)
    z_bands: list[tuple[float, float]] = []
    for z_val in raw_zs:
        if not z_bands or z_val - z_bands[-1][1] > 1.0:
            z_bands.append((z_val, z_val))
        else:
            z_bands[-1] = (z_bands[-1][0], z_val)

    while len(z_bands) > 4:
        best_idx = min(
            range(len(z_bands) - 1),
            key=lambda i: z_bands[i + 1][0] - z_bands[i][1],
        )
        z_bands[best_idx : best_idx + 2] = [
            (z_bands[best_idx][0], z_bands[best_idx + 1][1])
        ]

    n_bands = len(z_bands)
    if n_bands == 1:
        band_names = ["Base Layer"]
    elif n_bands == 2:
        band_names = ["Base Layer", "Top Layer"]
    elif n_bands == 3:
        band_names = ["Base Layer", "Middle Layer", "Top Layer"]
    else:
        band_names = [
            "Base Layer",
            "Lower-Middle Layer",
            "Upper-Middle Layer",
            "Top Layer",
        ]

    def _band_for_z(z: float) -> int:
        best_i = 0
        best_dist = float("inf")
        for idx, (z_lo, z_hi) in enumerate(z_bands):
            if z_lo <= z <= z_hi:
                return idx
            dist = min(abs(z - z_lo), abs(z - z_hi))
            if dist < best_dist:
                best_dist = dist
                best_i = idx
        return best_i

    pages: list[LayerPage] = []
    for band_idx, name in enumerate(band_names):
        active_pl = [p for p in packing.placements if _band_for_z(p.position[2]) == band_idx]
        lower_pl = [p for p in packing.placements if _band_for_z(p.position[2]) < band_idx]
        active_sp = [s for s in packing.spacer_placements if _band_for_z(s.position[2]) == band_idx]
        lower_sp = [s for s in packing.spacer_placements if _band_for_z(s.position[2]) < band_idx]
        if active_pl or active_sp:
            pages.append(
                LayerPage(
                    name=name,
                    active_placements=active_pl,
                    lower_placements=lower_pl,
                    active_spacers=active_sp,
                    lower_spacers=lower_sp,
                )
            )
    return pages


def generate_layout_pdf(
    packing: BoxPacking,
    output_path: Path,
    project_name: str,
    game_box_size: tuple[float, float, float],
    box_builders: list[BoxBuilder] | None = None,
    manifest: ProjectManifest | None = None,
    pipeline: GeometryPipeline | None = None,
) -> Path | None:
    """Generate a PDF packing guide with layered step-by-step breakdown.

    Renders each vertical Z layer on a separate page in back-to-front oblique order.

    Args:
        packing: The computed packed layout.
        output_path: Path to write the PDF file (str or Path).
        project_name: Game name for the title.
        game_box_size: Outer game box dimensions (W, L, H).
        box_builders: The project's boxes, keyed by label, for colour and
            label lookups. Optional.
        manifest: Optional ProjectManifest for exact compartment resolution.
        pipeline: Optional GeometryPipeline to reuse cached ResolvedBox instances.

    Returns:
        The output path, or None if generation failed.

    """
    output_path = Path(output_path)
    FPDF = require("fpdf", "draw the layout sheet").FPDF

    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=False)

    box_map = {b.label: b for b in box_builders} if box_builders else {}

    # Page dimensions
    page_w = 297  # A4 landscape
    page_h = 210

    # Projection settings (Cabinet Oblique)
    angle_rad = math.radians(30)
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    alpha = 0.45  # shortening factor for depth Y

    def project(x: float, y: float, z: float) -> tuple[float, float]:
        px = x + y * cos_a * alpha
        py = -z - y * sin_a * alpha
        return px, py

    corners = [
        (0, 0, 0),
        (game_box_size[0], 0, 0),
        (0, game_box_size[1], 0),
        (game_box_size[0], game_box_size[1], 0),
        (0, 0, game_box_size[2]),
        (game_box_size[0], 0, game_box_size[2]),
        (0, game_box_size[1], game_box_size[2]),
        (game_box_size[0], game_box_size[1], game_box_size[2]),
    ]
    projected = [project(x, y, z) for x, y, z in corners]
    min_px = min(p[0] for p in projected)
    max_px = max(p[0] for p in projected)
    min_py = min(p[1] for p in projected)
    max_py = max(p[1] for p in projected)

    proj_w = max_px - min_px
    proj_h = max_py - min_py

    margin = 15
    avail_w = page_w - 2 * margin
    avail_h = page_h - 2 * margin - 20

    scale = min(avail_w / proj_w, avail_h / proj_h)

    offset_x = margin + (avail_w - proj_w * scale) / 2 - min_px * scale
    offset_y = margin + 15 - min_py * scale

    def to_pdf(x: float, y: float, z: float) -> tuple[float, float]:
        px, py = project(x, y, z)
        return offset_x + px * scale, offset_y + py * scale

    colors = [
        (70, 130, 180),
        (220, 140, 70),
        (60, 160, 80),
        (200, 100, 150),
        (100, 160, 200),
        (180, 180, 60),
        (160, 100, 80),
        (120, 140, 160),
    ]

    def _draw_label_badge(
        anchor_x: float,
        anchor_y: float,
        anchor_z: float,
        x: float,
        y: float,
        bw: float,
        bl: float,
        label: str,
        index_str: str | None = None,
        visible_placements: list[Placement] | None = None,
    ) -> None:
        lbl = label[:16] + ".." if len(label) > 16 else label
        pdf.set_font("Helvetica", "B", 7.5)
        tw = pdf.get_string_width(lbl)
        th = 4.0

        cx, cy = to_pdf(anchor_x, anchor_y, anchor_z)

        is_covered = False
        check_list = visible_placements or packing.placements
        for other in check_list:
            if other.label == label:
                continue
            ox, oy, oz = other.position
            ow, ol, _oh = other.size
            sits_above = oz >= anchor_z - 0.5
            overlaps_x = ox < x + bw - 1.0 and ox + ow > x + 1.0
            overlaps_y = oy < y + bl - 1.0 and oy + ol > y + 1.0
            if sits_above and overlaps_x and overlaps_y:
                is_covered = True
                break

        if is_covered:
            shift_dir = -1 if anchor_x < game_box_size[0] / 2 else 1
            cx_shifted = cx + shift_dir * 25
            cy_shifted = cy - 5

            pdf.set_draw_color(200, 50, 50)
            pdf.set_line_width(0.2)
            pdf.set_dash_pattern(dash=1, gap=1)
            pdf.line(cx, cy, cx_shifted, cy_shifted)
            pdf.set_dash_pattern(dash=0, gap=0)

            pdf.set_fill_color(255, 255, 255)
            pdf.set_draw_color(40, 40, 40)
            pdf.set_line_width(0.15)
            pdf.rect(cx_shifted - tw / 2 - 1.5, cy_shifted - th / 2 - 1, tw + 3, th + 2, style="DF")

            pdf.set_text_color(0, 0, 0)
            pdf.text(cx_shifted - tw / 2, cy_shifted + th / 2 - 1.0, lbl)
        else:
            cx_shifted, cy_shifted = cx, cy
            pdf.set_fill_color(255, 255, 255)
            pdf.set_draw_color(40, 40, 40)
            pdf.set_line_width(0.15)
            pdf.rect(cx - tw / 2 - 1.5, cy - th / 2 - 1, tw + 3, th + 2, style="DF")

            pdf.set_text_color(0, 0, 0)
            pdf.text(cx - tw / 2, cy + th / 2 - 1.0, lbl)

        if index_str:
            pdf.set_fill_color(200, 50, 50)
            pdf.set_draw_color(40, 40, 40)
            label_x = cx_shifted if is_covered else cx
            label_y = cy_shifted if is_covered else cy
            pdf.rect(label_x - tw / 2 - 5.5, label_y - th / 2 - 1, 4.5, th + 2, style="DF")
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 7)
            pdf.text(label_x - tw / 2 - 4.5, label_y + th / 2 - 1.0, index_str)

    def draw_placement_3d(
        p: Placement,
        color: tuple[int, int, int],
        label: str | None = None,
        index_str: str | None = None,
        visible_placements: list[Placement] | None = None,
    ) -> None:
        x, y, z = p.position
        bw, bl, bh = p.size

        c_top = color
        c_front = (
            max(0, int(color[0] * 0.85)),
            max(0, int(color[1] * 0.85)),
            max(0, int(color[2] * 0.85)),
        )
        c_right = (
            max(0, int(color[0] * 0.70)),
            max(0, int(color[1] * 0.70)),
            max(0, int(color[2] * 0.70)),
        )

        pdf.set_draw_color(40, 40, 40)
        pdf.set_line_width(0.15)

        if p.path and len(p.path) >= 4:
            verts = list(p.path)
            if _polygon_signed_area(verts) < 0:
                verts.reverse()

            # Collect visible vertical walls (outward normal facing camera (+X, -Y))
            walls: list[tuple[float, float, tuple[int, int, int], list[tuple[float, float]]]] = []
            n_v = len(verts)
            for idx in range(n_v):
                px0, py0 = verts[idx]
                px1, py1 = verts[(idx + 1) % n_v]
                dx = px1 - px0
                dy = py1 - py0
                nx, ny = dy, -dx  # outward normal for CCW polygon
                if nx * (cos_a * alpha) - ny > 1e-6:
                    wall_color = c_front if abs(ny) >= abs(nx) else c_right
                    quad = [
                        to_pdf(x + px0, y + py0, z),
                        to_pdf(x + px1, y + py1, z),
                        to_pdf(x + px1, y + py1, z + bh),
                        to_pdf(x + px0, y + py0, z + bh),
                    ]
                    mid_x = 0.5 * (px0 + px1)
                    mid_y = 0.5 * (py0 + py1)
                    walls.append((-mid_y, mid_x, wall_color, quad))

            walls.sort(key=lambda w: (w[0], w[1]))
            for _my, _mx, w_col, quad in walls:
                pdf.set_fill_color(*w_col)
                pdf.polygon(quad, style="DF")

            p_top = [to_pdf(x + px, y + py, z + bh) for px, py in verts]
            pdf.set_fill_color(*c_top)
            pdf.polygon(p_top, style="DF")

            if label:
                lx, ly = _polygon_interior_point(verts, (bw / 2, bl / 2))
                _draw_label_badge(
                    x + lx,
                    y + ly,
                    z + bh,
                    x,
                    y,
                    bw,
                    bl,
                    label,
                    index_str,
                    visible_placements,
                )
            return

        # Standard cuboid rendering
        p_front = [
            to_pdf(x, y, z),
            to_pdf(x + bw, y, z),
            to_pdf(x + bw, y, z + bh),
            to_pdf(x, y, z + bh),
        ]
        p_right = [
            to_pdf(x + bw, y, z),
            to_pdf(x + bw, y + bl, z),
            to_pdf(x + bw, y + bl, z + bh),
            to_pdf(x + bw, y, z + bh),
        ]
        p_top = [
            to_pdf(x, y, z + bh),
            to_pdf(x + bw, y, z + bh),
            to_pdf(x + bw, y + bl, z + bh),
            to_pdf(x, y + bl, z + bh),
        ]

        pdf.set_fill_color(*c_top)
        pdf.polygon(p_top, style="DF")
        pdf.set_fill_color(*c_front)
        pdf.polygon(p_front, style="DF")
        pdf.set_fill_color(*c_right)
        pdf.polygon(p_right, style="DF")

        if label:
            _draw_label_badge(
                x + bw / 2,
                y + bl / 2,
                z + bh,
                x,
                y,
                bw,
                bl,
                label,
                index_str,
                visible_placements,
            )

    active_pages = _compute_layer_pages(packing)
    orig_index_map = {orig.label: i for i, orig in enumerate(packing.placements)}

    # Draw Page 1: Box Summary & Piece Inventory (when manifest is provided)
    if manifest is not None:
        _draw_inventory_summary_pages(
            pdf,
            project_name=project_name,
            game_box_size=game_box_size,
            packing=packing,
            manifest=manifest,
            orig_index_map=orig_index_map,
            box_colors=colors,
        )

    # Also render non-printed GameBoard regions (partial boards, screens, playmats)
    board_placements: list[Placement] = (
        [
            Placement(
                label=f"{gb.label} ({gb.count}x)" if gb.count > 1 else gb.label,
                position=gb.position,
                size=gb.size,
            )
            for gb in manifest.boards
        ]
        if manifest is not None
        else []
    )

    for step_idx, page in enumerate(active_pages):
        pdf.add_page()

        # Page Header
        pdf.set_font("Helvetica", "B", 14)
        heading = f"Packing Guide: {project_name} - Step {step_idx + 1}: {page.name}"
        pdf.cell(0, 8, heading, align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(
            0,
            5,
            f"Game box: {game_box_size[0]:.0f}x{game_box_size[1]:.0f}x{game_box_size[2]:.0f}mm",
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.ln(3)

        # Draw Game Box Outline
        pdf.set_draw_color(150, 150, 150)
        pdf.set_line_width(0.2)
        p_base = [
            to_pdf(0, 0, 0),
            to_pdf(game_box_size[0], 0, 0),
            to_pdf(game_box_size[0], game_box_size[1], 0),
            to_pdf(0, game_box_size[1], 0),
        ]
        pdf.polygon(p_base, style="D")
        for cx, cy in [
            (0, 0),
            (game_box_size[0], 0),
            (game_box_size[0], game_box_size[1]),
            (0, game_box_size[1]),
        ]:
            pdf.line(*to_pdf(cx, cy, 0), *to_pdf(cx, cy, game_box_size[2]))
        p_top = [
            to_pdf(0, 0, game_box_size[2]),
            to_pdf(game_box_size[0], 0, game_box_size[2]),
            to_pdf(game_box_size[0], game_box_size[1], game_box_size[2]),
            to_pdf(0, game_box_size[1], game_box_size[2]),
        ]
        pdf.polygon(p_top, style="D")

        # 1. Draw Lower Layers (spacers & boxes sorted back-to-front in light grey)
        lower_combined = [
            *((sp, True) for sp in page.lower_spacers),
            *((pl, False) for pl in page.lower_placements),
        ]
        for item, is_sp in _painters_sort(lower_combined):
            draw_placement_3d(item, (240, 240, 240) if is_sp else (220, 220, 220))

        # 2. Draw Active Layer (spacers & boxes interleaved back-to-front)
        active_combined = [
            *((sp, True) for sp in page.active_spacers),
            *((pl, False) for pl in page.active_placements),
        ]
        for item, is_sp in _painters_sort(active_combined):
            if is_sp:
                draw_placement_3d(
                    item,
                    (200, 200, 200),
                    "spacer",
                    visible_placements=page.active_placements,
                )
            else:
                orig_idx = orig_index_map.get(item.label, 0)
                color = colors[orig_idx % len(colors)]
                draw_placement_3d(
                    item,
                    color,
                    item.label,
                    str(orig_idx + 1),
                    visible_placements=page.active_placements,
                )

        # 3. Draw 2D Blueprint inset for Box if it has compartments
        active_compartment_boxes = [
            p
            for p in page.active_placements
            if box_map.get(p.label) and box_map[p.label].compartments
        ]
        if active_compartment_boxes:
            draw_box_blueprint(
                pdf,
                box_map[active_compartment_boxes[0].label],
                230,
                25,
                scale=0.45,
                manifest=manifest,
                pipeline=pipeline,
            )

    # Final step: Boards, Screens & Non-Printed Components (when explicitly modeled)
    if board_placements:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        heading = (
            f"Packing Guide: {project_name} - Step {len(active_pages) + 1}: "
            "Boards & Non-Printed Components"
        )
        pdf.cell(0, 8, heading, align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(
            0,
            5,
            f"Game box: {game_box_size[0]:.0f}x{game_box_size[1]:.0f}x{game_box_size[2]:.0f}mm",
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.ln(3)

        pdf.set_draw_color(150, 150, 150)
        pdf.set_line_width(0.2)
        p_base = [
            to_pdf(0, 0, 0),
            to_pdf(game_box_size[0], 0, 0),
            to_pdf(game_box_size[0], game_box_size[1], 0),
            to_pdf(0, game_box_size[1], 0),
        ]
        pdf.polygon(p_base, style="D")
        for cx, cy in [
            (0, 0),
            (game_box_size[0], 0),
            (game_box_size[0], game_box_size[1]),
            (0, game_box_size[1]),
        ]:
            pdf.line(*to_pdf(cx, cy, 0), *to_pdf(cx, cy, game_box_size[2]))
        p_top = [
            to_pdf(0, 0, game_box_size[2]),
            to_pdf(game_box_size[0], 0, game_box_size[2]),
            to_pdf(game_box_size[0], game_box_size[1], game_box_size[2]),
            to_pdf(0, game_box_size[1], game_box_size[2]),
        ]
        pdf.polygon(p_top, style="D")

        lower_all = [
            *((sp, True) for sp in packing.spacer_placements),
            *((pl, False) for pl in packing.placements),
        ]
        for item, is_sp in _painters_sort(lower_all):
            draw_placement_3d(item, (240, 240, 240) if is_sp else (225, 225, 225))
        for bp_item, _ in _painters_sort([(bp, False) for bp in board_placements]):
            draw_placement_3d(
                bp_item,
                (235, 212, 168),
                bp_item.label,
                "B",
                visible_placements=board_placements,
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    return output_path


def _draw_inventory_summary_pages(
    pdf: FPDF,
    *,
    project_name: str,
    game_box_size: tuple[float, float, float],
    packing: BoxPacking,
    manifest: ProjectManifest,
    orig_index_map: dict[str, int],
    box_colors: list[tuple[int, int, int]] | None = None,
) -> None:
    """Render compact, two-column color-coded Box Summary and Component Checklist pages."""
    from pyboxbuilder.project.inventory import summarize_project

    inv = summarize_project(manifest, spacer_count=len(packing.spacer_placements))
    palette = box_colors or [
        (70, 130, 180),
        (220, 140, 70),
        (60, 160, 80),
        (200, 100, 150),
        (100, 160, 200),
        (180, 180, 60),
        (160, 100, 80),
        (120, 140, 160),
    ]

    margin_x = 10.0
    gutter = 5.0
    col_w = 136.0  # 136 + 5 + 136 = 277 mm on A4 landscape (297 mm - 20 mm)
    col_xs = (margin_x, margin_x + col_w + gutter)
    y_table_top = 31.5
    y_bottom = 199.0
    hdr_h = 6.2
    line_h = 3.4
    single_row_h = 5.4
    max_col_h = y_bottom - (y_table_top + hdr_h)

    def _ascii_safe(text: str) -> str:
        return (
            text.replace("\u00d7", "x")
            .replace("\u2014", "-")
            .replace("\u2013", "-")
            .replace("\u00b7", "|")
            .encode("latin-1", "replace")
            .decode("latin-1")
        )

    def _fit_text(text: str, max_w: float) -> str:
        safe = _ascii_safe(text)
        if pdf.get_string_width(safe) <= max_w:
            return safe
        ellipsis = "..."
        ell_w = pdf.get_string_width(ellipsis)
        lo, hi = 0, len(safe)
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if pdf.get_string_width(safe[:mid]) + ell_w <= max_w:
                lo = mid
            else:
                hi = mid - 1
        return safe[:lo].rstrip() + ellipsis

    def _wrap_lines(text: str, max_w: float, max_lines: int = 2) -> list[str]:
        safe = _ascii_safe(text)
        if pdf.get_string_width(safe) <= max_w or max_lines <= 1:
            return [_fit_text(safe, max_w)]
        words = safe.split(" ")
        lines: list[str] = []
        current = ""
        for idx, word in enumerate(words):
            cand = f"{current} {word}".strip() if current else word
            if pdf.get_string_width(cand) <= max_w:
                current = cand
            else:
                if current:
                    lines.append(current)
                    if len(lines) == max_lines - 1:
                        rest = " ".join(words[idx:])
                        lines.append(_fit_text(rest, max_w))
                        return lines
                    current = word
                else:
                    lines.append(_fit_text(word, max_w))
                    if len(lines) == max_lines:
                        return lines
                    current = ""
        if current:
            lines.append(_fit_text(current, max_w))
        return lines or [""]

    def _paginate_two_cols(
        heights: list[float],
    ) -> list[tuple[list[int], list[int]]]:
        """Group row indices into balanced two-column pages."""
        pages_out: list[tuple[list[int], list[int]]] = []
        idx = 0
        n = len(heights)
        while idx < n:
            # Take as many rows as can fit into two columns of max_col_h
            start = idx
            col_h = 0.0
            col_num = 0
            while idx < n:
                rh = heights[idx]
                if col_h + rh <= max_col_h:
                    col_h += rh
                    idx += 1
                elif col_num == 0:
                    col_num = 1
                    col_h = rh
                    idx += 1
                else:
                    break
            page_indices = list(range(start, idx))
            # Balance left and right columns on this page when >= 4 rows
            if len(page_indices) < 4:
                pages_out.append((page_indices, []))
            else:
                total_h = sum(heights[i] for i in page_indices)
                half_h = total_h / 2.0
                left_ids: list[int] = []
                acc = 0.0
                for i in page_indices:
                    if left_ids and acc + heights[i] > max_col_h:
                        break
                    if left_ids and acc >= half_h:
                        break
                    left_ids.append(i)
                    acc += heights[i]
                right_ids = page_indices[len(left_ids) :]
                # Ensure right column fits within max_col_h
                while right_ids and sum(heights[i] for i in right_ids) > max_col_h:
                    if sum(heights[i] for i in left_ids) + heights[right_ids[0]] <= max_col_h:
                        left_ids.append(right_ids.pop(0))
                    else:
                        break
                pages_out.append((left_ids, right_ids))
        return pages_out

    def _draw_banner(
        title: str,
        subtitle: str,
        banner_rgb: tuple[int, int, int],
        accent_rgb: tuple[int, int, int],
        pills: list[tuple[str, tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]],
    ) -> None:
        pdf.add_page()
        # Top colored banner
        pdf.set_fill_color(*banner_rgb)
        pdf.set_draw_color(*banner_rgb)
        pdf.rect(margin_x, 8.0, 277.0, 12.0, style="F")
        # Thin left accent bar
        pdf.set_fill_color(*accent_rgb)
        pdf.rect(margin_x, 8.0, 3.0, 12.0, style="F")

        pdf.set_xy(margin_x + 6.0, 9.8)
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(175.0, 8.4, _ascii_safe(title), border=0, align="L")

        pdf.set_xy(margin_x + 185.0, 10.2)
        pdf.set_font("Helvetica", "B", 9.5)
        pdf.set_text_color(218, 232, 245)
        pdf.cell(88.0, 7.6, _ascii_safe(subtitle), border=0, align="R")

        # KPI summary pills
        px = margin_x
        py = 22.2
        pdf.set_font("Helvetica", "B", 7.8)
        pdf.set_line_width(0.25)
        for label, fill_c, border_c, text_c in pills:
            txt = _ascii_safe(label)
            pw = pdf.get_string_width(txt) + 7.0
            pdf.set_fill_color(*fill_c)
            pdf.set_draw_color(*border_c)
            pdf.set_text_color(*text_c)
            pdf.rect(px, py, pw, 6.2, style="DF")
            pdf.set_xy(px, py + 0.5)
            pdf.cell(pw, 5.2, txt, border=0, align="C")
            px += pw + 3.0

        pdf.set_draw_color(214, 222, 232)
        pdf.set_line_width(0.2)

    # ------------------------------------------------------------------
    # Section 1: Box Summary & Piece Counts (2 columns, no dims/position)
    # ------------------------------------------------------------------
    # Row tuple: (badge_str, badge_rgb, name, contents, row_bg_override)
    box_rows: list[tuple[str, tuple[int, int, int], str, str, tuple[int, int, int] | None]] = []
    for summary in inv.box_summaries:
        if summary.label in orig_index_map:
            idx_val = orig_index_map[summary.label]
            badge_str = str(idx_val + 1)
            badge_rgb = palette[idx_val % len(palette)]
        else:
            badge_str = "-"
            badge_rgb = (95, 112, 132)
        box_rows.append(
            (badge_str, badge_rgb, summary.label, summary.format_contents(max_items=6), None)
        )

    for sp in packing.spacer_placements:
        box_rows.append(
            ("S", (118, 128, 140), f"{sp.label} (spacer)", "Printed spacer tray", (241, 244, 247))
        )

    for gb in inv.boards:
        desc = f"{gb.count}x {gb.label}" + (f" ({gb.notes})" if gb.notes else "")
        box_rows.append(("B", (192, 142, 54), gb.label, desc, (253, 247, 234)))

    summary_pills: list[tuple[str, tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]] = [
        (
            f"Game Box: {game_box_size[0]:.0f}x{game_box_size[1]:.0f}x{game_box_size[2]:.0f} mm",
            (232, 241, 250),
            (176, 204, 230),
            (32, 68, 104),
        ),
        (
            f"Printed: {inv.printed_bodies} bodies, {inv.printed_lids} lids, {inv.printed_spacers} spacers",
            (231, 246, 239),
            (168, 214, 192),
            (26, 88, 62),
        ),
    ]
    if inv.total_board_count > 0:
        summary_pills.append(
            (
                f"Boards / Non-Printed: {inv.total_board_count}",
                (253, 244, 224),
                (230, 200, 142),
                (128, 86, 22),
            )
        )
    if inv.total_counted_pieces > 0:
        summary_pills.append(
            (
                f"Counted Pieces: {inv.total_counted_pieces}",
                (242, 236, 252),
                (198, 182, 230),
                (78, 48, 126),
            )
        )

    box_col_widths = (9.0, 44.0, 83.0)  # sum = 136.0 mm

    def _draw_box_col_header(x0: float) -> None:
        pdf.set_fill_color(48, 72, 102)
        pdf.set_draw_color(48, 72, 102)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 7.8)
        pdf.set_xy(x0, y_table_top)
        pdf.cell(box_col_widths[0], hdr_h, "#", border=1, align="C", fill=True)
        pdf.cell(box_col_widths[1], hdr_h, "Box / Component", border=1, align="L", fill=True)
        pdf.cell(box_col_widths[2], hdr_h, "Pieces / Contents", border=1, align="L", fill=True)

    # Pre-wrap contents lines and compute exact row heights
    pdf.set_font("Helvetica", "", 7.2)
    box_wrapped: list[list[str]] = [
        _wrap_lines(contents, box_col_widths[2] - 2.4, max_lines=2)
        for (_, _, _, contents, _) in box_rows
    ]
    box_heights: list[float] = [
        single_row_h if len(lines) == 1 else (len(lines) * line_h + 1.8)
        for lines in box_wrapped
    ]
    box_pages = _paginate_two_cols(box_heights) if box_rows else [([], [])]

    for p_idx, (left_ids, right_ids) in enumerate(box_pages):
        suffix = " (continued)" if p_idx > 0 else ""
        _draw_banner(
            f"Packing Guide: {project_name}",
            f"Box Summary & Contents{suffix}",
            banner_rgb=(36, 54, 78),
            accent_rgb=(86, 168, 222),
            pills=summary_pills,
        )
        for col_idx, col_ids in enumerate((left_ids, right_ids)):
            if not col_ids:
                continue
            x0 = col_xs[col_idx]
            _draw_box_col_header(x0)
            y_cur = y_table_top + hdr_h
            for r_idx, item_i in enumerate(col_ids):
                badge_str, badge_rgb, name, _contents, row_bg = box_rows[item_i]
                lines = box_wrapped[item_i]
                rh = box_heights[item_i]
                bg = row_bg if row_bg is not None else ((246, 250, 254) if r_idx % 2 == 1 else (255, 255, 255))
                pdf.set_draw_color(216, 224, 234)
                pdf.set_line_width(0.2)
                # Colored badge cell
                pdf.set_fill_color(*badge_rgb)
                pdf.set_text_color(255, 255, 255)
                pdf.set_font("Helvetica", "B", 7.5)
                pdf.set_xy(x0, y_cur)
                pdf.cell(box_col_widths[0], rh, _ascii_safe(badge_str), border=1, align="C", fill=True)
                # Box name cell
                pdf.set_fill_color(*bg)
                pdf.set_text_color(24, 34, 48)
                pdf.set_font("Helvetica", "B", 7.4)
                pdf.cell(
                    box_col_widths[1],
                    rh,
                    _fit_text(name, box_col_widths[1] - 2.2),
                    border=1,
                    align="L",
                    fill=True,
                )
                # Contents cell (1 or 2 cleanly centered lines)
                cx = x0 + box_col_widths[0] + box_col_widths[1]
                pdf.set_fill_color(*bg)
                pdf.rect(cx, y_cur, box_col_widths[2], rh, style="DF")
                pdf.set_text_color(52, 62, 76)
                pdf.set_font("Helvetica", "", 7.2)
                if len(lines) == 1:
                    pdf.set_xy(cx + 1.0, y_cur)
                    pdf.cell(box_col_widths[2] - 2.0, rh, lines[0], border=0, align="L")
                else:
                    y_text = y_cur + (rh - len(lines) * line_h) / 2.0
                    for li, ln in enumerate(lines):
                        pdf.set_xy(cx + 1.0, y_text + li * line_h)
                        pdf.cell(box_col_widths[2] - 2.0, line_h, ln, border=0, align="L")
                y_cur += rh

    # ------------------------------------------------------------------
    # Section 2: Master Component Checklist (2 columns, color-coded)
    # ------------------------------------------------------------------
    if inv.checklist:
        total_items = sum(row.count for row in inv.checklist)
        checklist_pills = [
            (
                f"{len(inv.checklist)} Component Types",
                (226, 244, 242),
                (156, 208, 202),
                (20, 84, 82),
            ),
            (
                f"{total_items} Total Pieces Accounted For",
                (234, 243, 252),
                (172, 204, 232),
                (30, 68, 108),
            ),
        ]
        chk_col_widths = (13.0, 56.0, 67.0)  # sum = 136.0 mm

        def _draw_checklist_col_header(x0: float) -> None:
            pdf.set_fill_color(30, 96, 94)
            pdf.set_draw_color(30, 96, 94)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 7.8)
            pdf.set_xy(x0, y_table_top)
            pdf.cell(chk_col_widths[0], hdr_h, "Qty", border=1, align="C", fill=True)
            pdf.cell(chk_col_widths[1], hdr_h, "Game Component / Tile", border=1, align="L", fill=True)
            pdf.cell(chk_col_widths[2], hdr_h, "Packed In", border=1, align="L", fill=True)

        checklist_rows = list(inv.checklist)
        pdf.set_font("Helvetica", "", 7.2)
        chk_loc_texts = [row.format_locations(max_items=6) for row in checklist_rows]
        chk_wrapped: list[list[str]] = [
            _wrap_lines(loc, chk_col_widths[2] - 2.4, max_lines=2) for loc in chk_loc_texts
        ]
        chk_heights: list[float] = [
            single_row_h if len(lines) == 1 else (len(lines) * line_h + 1.8)
            for lines in chk_wrapped
        ]
        chk_pages = _paginate_two_cols(chk_heights)

        for p_idx, (left_ids, right_ids) in enumerate(chk_pages):
            suffix = " (continued)" if p_idx > 0 else ""
            _draw_banner(
                f"Packing Guide: {project_name}",
                f"Component Checklist{suffix}",
                banner_rgb=(24, 78, 78),
                accent_rgb=(82, 196, 178),
                pills=checklist_pills,
            )
            for col_idx, col_ids in enumerate((left_ids, right_ids)):
                if not col_ids:
                    continue
                x0 = col_xs[col_idx]
                _draw_checklist_col_header(x0)
                y_cur = y_table_top + hdr_h
                for r_idx, item_i in enumerate(col_ids):
                    row = checklist_rows[item_i]
                    loc_text = chk_loc_texts[item_i]
                    lines = chk_wrapped[item_i]
                    rh = chk_heights[item_i]
                    loc_lower = loc_text.lower()
                    is_spacer_or_board = "spacer" in loc_lower or "board" in loc_lower or "tray" in loc_lower
                    if is_spacer_or_board:
                        bg = (253, 248, 236)
                        qty_bg = (246, 229, 192)
                        qty_fg = (126, 82, 18)
                    else:
                        bg = (245, 250, 250) if r_idx % 2 == 1 else (255, 255, 255)
                        qty_bg = (224, 243, 241)
                        qty_fg = (20, 82, 80)
                    pdf.set_draw_color(214, 226, 226)
                    pdf.set_line_width(0.2)
                    # Qty pill cell
                    pdf.set_fill_color(*qty_bg)
                    pdf.set_text_color(*qty_fg)
                    pdf.set_font("Helvetica", "B", 7.6)
                    pdf.set_xy(x0, y_cur)
                    pdf.cell(chk_col_widths[0], rh, str(row.count), border=1, align="C", fill=True)
                    # Component name cell
                    pdf.set_fill_color(*bg)
                    pdf.set_text_color(24, 34, 44)
                    pdf.set_font("Helvetica", "B", 7.3)
                    pdf.cell(
                        chk_col_widths[1],
                        rh,
                        _fit_text(row.name, chk_col_widths[1] - 2.2),
                        border=1,
                        align="L",
                        fill=True,
                    )
                    # Packed In cell (1 or 2 cleanly centered lines)
                    cx = x0 + chk_col_widths[0] + chk_col_widths[1]
                    pdf.set_fill_color(*bg)
                    pdf.rect(cx, y_cur, chk_col_widths[2], rh, style="DF")
                    pdf.set_text_color(52, 66, 76)
                    pdf.set_font("Helvetica", "", 7.2)
                    if len(lines) == 1:
                        pdf.set_xy(cx + 1.0, y_cur)
                        pdf.cell(chk_col_widths[2] - 2.0, rh, lines[0], border=0, align="L")
                    else:
                        y_text = y_cur + (rh - len(lines) * line_h) / 2.0
                        for li, ln in enumerate(lines):
                            pdf.set_xy(cx + 1.0, y_text + li * line_h)
                            pdf.cell(chk_col_widths[2] - 2.0, line_h, ln, border=0, align="L")
                    y_cur += rh


def draw_box_blueprint(
    pdf: FPDF,
    builder: BoxBuilder,
    x_bp: float,
    y_bp: float,
    scale: float = 0.45,
    manifest: ProjectManifest | None = None,
    pipeline: GeometryPipeline | None = None,
) -> None:
    """Draw a detailed 2D blueprint of the box containing its compartments and shapes."""
    from pyboxbuilder.project.manifest import ProjectManifest as _ProjectManifest
    from pyboxbuilder.project.pipeline import GeometryPipeline as _GeometryPipeline

    final_size = builder.final_size
    assert final_size is not None

    eff_manifest = manifest or _ProjectManifest(
        name="Blueprint",
        wall_thickness=builder.wall_thickness or 2.0,
    )
    eff_pipeline = pipeline or _GeometryPipeline()
    resolved = eff_pipeline._resolve_box(eff_manifest, builder)
    interior = resolved.interior
    comp_layout = resolved.compartments

    # Outer box boundary
    pdf.set_draw_color(50, 50, 50)
    pdf.set_line_width(0.3)
    pdf.set_fill_color(248, 248, 248)
    pdf.rect(x_bp, y_bp, final_size[0] * scale, final_size[1] * scale, style="DF")

    # Interior border (exact BoxType interior envelope, including slipover/hinge insets)
    pdf.set_draw_color(120, 120, 120)
    pdf.set_line_width(0.15)
    pdf.rect(
        x_bp + interior.origin_x * scale,
        y_bp + interior.origin_y * scale,
        interior.width * scale,
        interior.length * scale,
        style="D",
    )

    # Title
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_text_color(50, 50, 50)
    pdf.text(x_bp + 4.0 * scale, y_bp + 10.0 * scale, f"{builder.label} Layout")

    if comp_layout is None:
        return

    pdf.set_font("Helvetica", "", 5)
    for placement in comp_layout.placements:
        cx = x_bp + placement.position[0] * scale
        cy = y_bp + placement.position[1] * scale
        cw = placement.size[0] * scale
        ch = placement.size[1] * scale

        pdf.set_draw_color(180, 180, 180)
        pdf.rect(cx, cy, cw, ch, style="D")
        pdf.text(cx + 1.0 * scale, cy + 4.0 * scale, placement.label)

        if placement.shape_file:
            svg_path = Path(placement.shape_file)
            if not svg_path.is_absolute() and not svg_path.exists():
                repo_root = Path(__file__).resolve().parents[2]
                svg_resolved = repo_root / svg_path
                if svg_resolved.exists():
                    svg_path = svg_resolved
            if svg_path.exists():
                pdf.image(
                    str(svg_path),
                    cx + 1.0 * scale,
                    cy + 5.0 * scale,
                    w=cw - 2.0 * scale,
                    h=ch - 6.0 * scale,
                )

        if placement.elements:
            for elem in placement.elements:
                elem_x = cx + elem.offset[0] * scale
                elem_y = cy + elem.offset[1] * scale

                if not elem.shape_file:
                    fw, fl = elem.footprint
                    pdf.set_draw_color(200, 200, 200)
                    pdf.rect(elem_x, elem_y, fw * scale, fl * scale, style="D")
                    continue

                ew = (elem.size[0] if elem.size else 15.0) * scale
                eh = (elem.size[1] if elem.size else 15.0) * scale
                svg_path = Path(elem.shape_file)
                if not svg_path.is_absolute() and not svg_path.exists():
                    repo_root = Path(__file__).resolve().parents[2]
                    svg_resolved = repo_root / svg_path
                    if svg_resolved.exists():
                        svg_path = svg_resolved
                if svg_path.exists():
                    if elem.rotation != 0.0:
                        rot_cx = elem_x + ew / 2
                        rot_cy = elem_y + eh / 2
                        with pdf.rotation(elem.rotation, rot_cx, rot_cy):
                            pdf.image(str(svg_path), elem_x, elem_y, w=ew, h=eh)
                    else:
                        pdf.image(str(svg_path), elem_x, elem_y, w=ew, h=eh)


def should_regenerate_layout(
    packing: BoxPacking,
    pdf_path: Path,
    library_version: str = "1.4.0",
) -> bool:
    """Check whether the PDF needs regeneration.

    Uses SHA-256 hash of packing layout + library version.
    If the PDF doesn't exist or the hash differs, regeneration is needed.

    Args:
        packing: The current packing layout.
        pdf_path: Path to the existing PDF file.
        library_version: Version string for cache invalidation.

    Returns:
        True if PDF should be regenerated, False if existing is current.

    """
    layout_data = {
        "placements": [
            {
                "label": p.label,
                "position": list(p.position),
                "size": list(p.size),
                "rotation": p.rotation,
            }
            for p in packing.placements
        ],
        "spacers": [
            {
                "position": list(s.position),
                "size": list(s.size),
                "path": [list(pt) for pt in s.path] if s.path else None,
            }
            for s in packing.spacer_placements
        ],
        "version": library_version,
    }
    current_hash = hashlib.sha256(
        json.dumps(layout_data, sort_keys=True, default=str).encode()
    ).hexdigest()

    hash_file = pdf_path.with_suffix(".sha256")
    if (
        pdf_path.exists()
        and hash_file.exists()
        and hash_file.read_text().strip() == current_hash
    ):
        return False

    hash_file.parent.mkdir(parents=True, exist_ok=True)
    hash_file.write_text(current_hash)
    return True
