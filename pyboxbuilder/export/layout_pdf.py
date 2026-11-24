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
) -> None:
    """Render the Box Summary & Piece Count inventory table at the start of the PDF."""
    from pyboxbuilder.project.inventory import summarize_project

    inv = summarize_project(manifest, spacer_count=len(packing.spacer_placements))
    placements_by_label = {p.label: p for p in packing.placements}

    def _ascii_safe(text: str) -> str:
        return (
            text.replace("\u00d7", "x")
            .replace("\u2014", "-")
            .replace("\u2013", "-")
            .encode("latin-1", "replace")
            .decode("latin-1")
        )

    def _start_page(continued: bool = False) -> None:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 14)
        suffix = " (continued)" if continued else ""
        pdf.cell(
            0,
            8,
            _ascii_safe(f"Packing Guide: {project_name} - Box Summary & Piece Counts{suffix}"),
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.set_font("Helvetica", "", 9)
        summary_bits = [
            f"Game box: {game_box_size[0]:.0f}x{game_box_size[1]:.0f}x{game_box_size[2]:.0f}mm",
            (
                f"Printed parts: {inv.printed_bodies} bodies, {inv.printed_lids} lids, "
                f"{inv.printed_spacers} spacers ({inv.total_printed_parts} total)"
            ),
        ]
        if inv.total_board_count > 0:
            summary_bits.append(f"Boards/non-printed: {inv.total_board_count}")
        if inv.total_counted_pieces > 0:
            summary_bits.append(f"Counted pieces: {inv.total_counted_pieces}")
        pdf.cell(
            0,
            5,
            _ascii_safe("   |   ".join(summary_bits)),
            align="C",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.ln(3)
        # Table header
        pdf.set_fill_color(55, 70, 90)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(10, 6, "#", border=1, align="C", fill=True)
        pdf.cell(58, 6, "Box / Component", border=1, fill=True)
        pdf.cell(36, 6, "Dimensions (mm)", border=1, align="C", fill=True)
        pdf.cell(36, 6, "Position (X,Y,Z)", border=1, align="C", fill=True)
        pdf.cell(137, 6, "Pieces / Contents", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(20, 20, 20)
        pdf.set_font("Helvetica", "", 7.5)

    _start_page(continued=False)
    row_idx = 0

    def _draw_row(
        idx_str: str,
        name: str,
        dims: str,
        pos: str,
        contents: str,
        *,
        tint: tuple[int, int, int] | None = None,
    ) -> None:
        nonlocal row_idx
        if pdf.get_y() > 192:
            _start_page(continued=True)
        if tint is not None:
            pdf.set_fill_color(*tint)
        elif row_idx % 2 == 1:
            pdf.set_fill_color(246, 248, 250)
        else:
            pdf.set_fill_color(255, 255, 255)
        pdf.cell(10, 5.5, _ascii_safe(idx_str), border=1, align="C", fill=True)
        pdf.cell(58, 5.5, _ascii_safe(name[:34]), border=1, fill=True)
        pdf.cell(36, 5.5, _ascii_safe(dims), border=1, align="C", fill=True)
        pdf.cell(36, 5.5, _ascii_safe(pos), border=1, align="C", fill=True)
        pdf.cell(137, 5.5, _ascii_safe(contents[:88]), border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
        row_idx += 1

    for summary in inv.box_summaries:
        pl = placements_by_label.get(summary.label)
        dims = f"{pl.size[0]:.1f}x{pl.size[1]:.1f}x{pl.size[2]:.1f}" if pl else "-"
        pos = f"({pl.position[0]:.0f}, {pl.position[1]:.0f}, {pl.position[2]:.0f})" if pl else "-"
        idx_num = str(orig_index_map[summary.label] + 1) if summary.label in orig_index_map else "-"
        _draw_row(idx_num, summary.label, dims, pos, summary.format_contents(max_items=6))

    for sp in packing.spacer_placements:
        dims = f"{sp.size[0]:.1f}x{sp.size[1]:.1f}x{sp.size[2]:.1f}"
        pos = f"({sp.position[0]:.0f}, {sp.position[1]:.0f}, {sp.position[2]:.0f})"
        _draw_row("S", f"{sp.label} (spacer)", dims, pos, "Printed spacer tray", tint=(240, 240, 240))

    for gb in inv.boards:
        dims = f"{gb.size[0]:.1f}x{gb.size[1]:.1f}x{gb.size[2]:.1f}"
        pos = f"({gb.position[0]:.0f}, {gb.position[1]:.0f}, {gb.position[2]:.0f})"
        desc = f"{gb.count}x {gb.label}" + (f" ({gb.notes})" if gb.notes else "") + " [non-printed]"
        _draw_row("B", gb.label, dims, pos, desc, tint=(248, 241, 224))


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
    library_version: str = "1.1.0",
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
