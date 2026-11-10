#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""Generate STL meshes and Sphinx documentation pages for all board-game inserts.

For each ``boxes/<game>/<game>.py`` project, this script:
1. Exports Magics-colored binary STL meshes for every piece (each box's body,
   each box's decorated lid, and each spacer tray) into
   ``docs/_extra/_stl/boxes/<game>/``.
2. Generates ``docs/boxes/<game>.rst`` with interactive 3-D STL viewers and
   STL download links for:
   - Full Box Packing (all boxes, lids, and spacers in their packed layout)
   - Each Box Individually (assembled body + lid)
   - All Individual Parts (each body, each lid, and each spacer tray)
   plus cross-reference ``:ref:`` links to the ``BoxType`` documentation.
3. Generates ``docs/boxes/index.rst`` indexing all 39 board-game inserts.
"""

from __future__ import annotations

import ast
import struct
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import openscad  # noqa: E402

import pyboxbuilder.rounding as _rounding  # noqa: E402
from pyboxbuilder import BoxType, StackableMode, precision  # noqa: E402

BOXES_DIR = REPO_ROOT / "boxes"
DOCS_BOXES_DIR = REPO_ROOT / "docs" / "boxes"
STL_BOXES_DIR = REPO_ROOT / "docs" / "_extra" / "_stl" / "boxes"

BOX_TYPE_REF_SLUG: dict[BoxType, str] = {
    BoxType.SLIDING: "box-type-sliding",
    BoxType.SLIDING_CATCH: "box-type-sliding-catch",
    BoxType.CAP: "box-type-cap",
    BoxType.CAP_PATH: "box-type-cap-path",
    BoxType.SLIPOVER: "box-type-slipover",
    BoxType.SLIPOVER_PATH: "box-type-slipover-path",
    BoxType.FILAMENT_HINGE: "box-type-filament-hinge",
    BoxType.MAGNETIC_HINGE: "box-type-magnetic-hinge",
    BoxType.MAGNETIC: "box-type-magnetic",
    BoxType.INSET: "box-type-inset",
    BoxType.NO_LID: "box-type-no-lid",
    BoxType.CARD_LIBRARY: "box-type-card-library",
    BoxType.PATH: "box-type-path",
    BoxType.SNAP_FIT: "box-type-snap-fit",
    BoxType.BAYONET: "box-type-bayonet",
    BoxType.THREADED: "box-type-threaded",
    BoxType.DISPENSER: "box-type-dispenser",
    BoxType.CARD_SHOE: "box-type-card-shoe",
    BoxType.DICE_TRAY: "box-type-dice-tray",
    BoxType.SLEEVE_DRAWER: "box-type-sleeve-drawer",
    BoxType.CLAMSHELL: "box-type-clamshell",
    BoxType.MODULAR_INTERLOCK: "box-type-modular-interlock",
    BoxType.PRINT_IN_PLACE_HINGE: "box-type-print-in-place-hinge",
    BoxType.INSET_HINGE: "box-type-inset-hinge",
    BoxType.SLIDING_HINGE: "box-type-sliding-hinge",
}


def box_type_ref(bt: BoxType) -> str:
    """Return a Sphinx :ref: link to the BoxType's documentation section."""
    slug = BOX_TYPE_REF_SLUG.get(bt, f"box-type-{bt.value.replace('_', '-')}")
    return f":ref:`BoxType.{bt.name} <{slug}>`"


def color_to_magics_attr(color: Any) -> int:
    """Convert a pybosl2 Color or hex string to a 15-bit Materialise Magics facet attribute."""
    hex_str = "#6f9ac9"
    if color is not None:
        raw = getattr(color, "value", str(color))
        if isinstance(raw, str) and raw.startswith("#") and len(raw) >= 7:
            hex_str = raw
    r = int(hex_str[1:3], 16)
    g = int(hex_str[3:5], 16)
    b = int(hex_str[5:7], 16)
    r5 = min(31, max(0, round((r / 255.0) * 31)))
    g5 = min(31, max(0, round((g / 255.0) * 31)))
    b5 = min(31, max(0, round((b / 255.0) * 31)))
    # Note: Three.js STLLoader with 'COLOR=' header reads bits 0-4 as R, 5-9 as G, 10-14 as B
    return r5 | (g5 << 5) | (b5 << 10)


def write_colored_stl(
    out_path: Path,
    colored_solids: list[tuple[Any, Any]],
) -> int:
    """Extract meshes from ``(solid, color)`` pairs and write a Magics binary STL.

    Returns the number of triangles written.
    """
    header = (
        b"COLOR="
        + bytes([200, 200, 200, 255])
        + b"MATERIAL="
        + b"\x00" * (80 - 19)
    )
    faces_data = bytearray()
    total_tris = 0

    for solid, color in colored_solids:
        attr = color_to_magics_attr(color)
        raw_shape = getattr(solid, "shape", solid)
        vertices, faces = openscad.mesh(raw_shape)
        for face in faces:
            if len(face) < 3:
                continue
            pt1 = vertices[face[0]]
            for i in range(1, len(face) - 1):
                pt2 = vertices[face[i]]
                pt3 = vertices[face[i + 1]]
                ax, ay, az = pt2[0] - pt1[0], pt2[1] - pt1[1], pt2[2] - pt1[2]
                bx, by, bz = pt3[0] - pt1[0], pt3[1] - pt1[1], pt3[2] - pt1[2]
                nx = ay * bz - az * by
                ny = az * bx - ax * bz
                nz = ax * by - ay * bx
                length = (nx * nx + ny * ny + nz * nz) ** 0.5
                if length > 1e-9:
                    nx, ny, nz = nx / length, ny / length, nz / length
                else:
                    nx, ny, nz = 0.0, 0.0, 0.0
                faces_data.extend(
                    struct.pack(
                        "<ffffffffffffH",
                        nx,
                        ny,
                        nz,
                        pt1[0],
                        pt1[1],
                        pt1[2],
                        pt2[0],
                        pt2[1],
                        pt2[2],
                        pt3[0],
                        pt3[1],
                        pt3[2],
                        attr,
                    )
                )
                total_tris += 1

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "wb") as f:
        f.write(header)
        f.write(struct.pack("<I", total_tris))
        f.write(faces_data)
    return total_tris


def fmt_dim(size: tuple[float, float, float] | None) -> str:
    """Format a 3D dimension tuple neatly."""
    if size is None:
        return "auto"
    return f"{size[0]:g} × {size[1]:g} × {size[2]:g} mm"


def fmt_pos(pos: tuple[float, float, float] | None) -> str:
    """Format a 3D position tuple neatly."""
    if pos is None:
        return "(0, 0, 0)"
    return f"({pos[0]:g}, {pos[1]:g}, {pos[2]:g})"


def html_download_single(uri: str, filename: str, label: str) -> str:
    """Return raw HTML for a direct single-file STL download link."""
    return (
        f'.. raw:: html\n\n'
        f'   <p><a href="{uri}" download="{filename}">'
        f'⬇ {label} (<code>{filename}</code>)</a></p>\n'
    )


def html_download_combined(uris: list[str], filename: str, label: str) -> str:
    """Return raw HTML for a combined multi-part STL download link."""
    if len(uris) == 1:
        return html_download_single(uris[0], filename, label)
    joined = ",".join(uris)
    return (
        f'.. raw:: html\n\n'
        f'   <p><a href="{uris[0]}" data-stl-combine="{joined}" download="{filename}">'
        f'⬇ {label} (<code>{filename}</code>)</a></p>\n'
    )


def process_game(game_slug: str) -> dict[str, Any]:
    """Build STL files and RST page for a single game insert."""
    t0 = time.time()
    script_path = BOXES_DIR / game_slug / f"{game_slug}.py"
    source = script_path.read_text(encoding="utf-8")

    # Extract module docstring if present
    tree = ast.parse(source)
    docstring = ast.get_docstring(tree) or ""
    first_line = docstring.strip().splitlines()[0] if docstring.strip() else game_slug

    # Execute project definition without running __main__ CLI
    _rounding.MIN_ROUNDING_FACETS = 8
    with precision.use(fn=8):
        ns: dict[str, Any] = {"__file__": str(script_path), "__name__": "__docgen__"}
        exec(compile(source, str(script_path), "exec"), ns)
        proj = ns["project"]
        build = proj.build()

        out_stl_dir = STL_BOXES_DIR / game_slug
        out_stl_dir.mkdir(parents=True, exist_ok=True)

        expected_files: list[tuple[tuple[str, str], str, Path]] = []
        for piece in build.pieces:
            fname = f"{piece.label}.stl" if piece.kind == "spacer" else f"{piece.label}_{piece.kind}.stl"
            expected_files.append(((piece.label, piece.kind), fname, out_stl_dir / fname))

        part_uris: dict[tuple[str, str], str] = {}
        part_filenames: dict[tuple[str, str], str] = {}
        total_tris = 0

        missing_keys: set[tuple[str, str]] = set()
        for key, fname, stl_path in expected_files:
            part_uris[key] = f"../_stl/boxes/{game_slug}/{fname}"
            part_filenames[key] = fname
            if stl_path.is_file() and stl_path.stat().st_size > 84:
                with open(stl_path, "rb") as f:
                    hdr = f.read(84)
                    total_tris += struct.unpack("<I", hdr[80:84])[0]
            else:
                missing_keys.add(key)

        if missing_keys:
            only_lids_missing = all(kind == "lid" for _, kind in missing_keys)
            missing_labels = {label for label, _ in missing_keys}
            if only_lids_missing:
                from pyboxbuilder.rounding import lid_rounding, round_edges

                def _build_lid_only(builder: Any) -> tuple[Any, Any, Any, list[Any]]:
                    resolved = proj.pipeline._resolve_box(proj._manifest, builder)
                    size = builder.final_size
                    assert size is not None
                    box, spec = resolved.box, resolved.spec
                    if box is None:
                        return None, None, size, []
                    lid = box.build_lid(spec)
                    if lid is not None:
                        lid = round_edges(
                            lid, list(size), lid_rounding(spec), box.lid_rounded_edges(spec)
                        )
                    return None, lid, size, []

                preview_list = proj.pipeline.preview_pieces(
                    proj._manifest,
                    show_lids=True,
                    lids_only=True,
                    only=missing_labels,
                    build_box_solids_fn=_build_lid_only,
                )
            else:
                preview_list = proj.preview_pieces(show_lids=True)

            grouped: dict[tuple[str, str], list[tuple[Any, Any]]] = {}
            for p in preview_list:
                grouped.setdefault((p.label, p.kind), []).append((p.solid, p.color))

            for (label, kind), solids in grouped.items():
                if (label, kind) not in missing_keys:
                    continue
                fname = f"{label}.stl" if kind == "spacer" else f"{label}_{kind}.stl"
                stl_path = out_stl_dir / fname
                total_tris += write_colored_stl(stl_path, solids)

    # Collect box and spacer metadata from build.pieces
    body_pieces = {p.label: p for p in build.of_kind("body")}
    spacer_pieces = list(build.of_kind("spacer"))

    box_types_used: list[BoxType] = []
    seen_bt: set[BoxType] = set()
    for b in proj.boxes:
        if b.box_type not in seen_bt:
            seen_bt.add(b.box_type)
            box_types_used.append(b.box_type)
    if spacer_pieces and BoxType.NO_LID not in seen_bt:
        seen_bt.add(BoxType.NO_LID)
        box_types_used.append(BoxType.NO_LID)

    # Build RST content
    title = f"{proj.name} ({game_slug})"
    rst_lines: list[str] = [
        f".. _box-insert-{game_slug.replace('_', '-')}:",
        "",
        title,
        "=" * len(title),
        "",
    ]

    if first_line:
        rst_lines.extend([f"{first_line}", ""])

    gsize = proj.game_box_size
    eff_size = proj.effective_game_box_size
    bt_links = ", ".join(box_type_ref(bt) for bt in box_types_used)

    rst_lines.extend([
        f"- **Source Script**: ``boxes/{game_slug}/{game_slug}.py``",
        f"- **Game Box Dimensions**: ``{fmt_dim(gsize)}``"
        + (
            f" (usable height ``{eff_size[2]:g} mm`` with ``{proj.board_thickness:g} mm`` board storage)"
            if proj.board_thickness and eff_size
            else ""
        ),
        f"- **Boxes**: {len(proj.boxes)} sub-box(es)"
        + (f", {len(spacer_pieces)} spacer tray(s)" if spacer_pieces else ""),
        f"- **Box Types Used**: {bt_links}",
        "",
    ])

    # 1. Full Box Packing viewer + download
    all_uris = list(part_uris.values())
    rst_lines.extend([
        "Full Box Packing",
        "----------------",
        "",
        "Interactive 3-D view of all boxes, lids, and spacers packed inside the game box:",
        "",
        f".. stl:: {','.join(all_uris)}",
        "   :height: 440px",
        "",
        html_download_combined(
            all_uris,
            f"{proj.name}_full_packing.stl",
            "Download Full Box Packing STL",
        ),
    ])

    # 2. Summary table of all pieces
    rst_lines.extend([
        "Parts Overview",
        "--------------",
        "",
        ".. list-table::",
        "   :header-rows: 1",
        "   :widths: 26 24 20 18 12",
        "",
        "   * - Box / Spacer",
        "     - Box Type",
        "     - Dimensions (W × L × H)",
        "     - Packed Position",
        "     - Compartments",
    ])
    for b in proj.boxes:
        bp = body_pieces.get(b.label)
        size_str = fmt_dim(bp.size if bp else b.final_size)
        pos_str = fmt_pos(bp.position if bp else b.position)
        rst_lines.extend([
            f"   * - :ref:`{b.label} <box-{game_slug}-{b.label.lower()}>`",
            f"     - {box_type_ref(b.box_type)}",
            f"     - ``{size_str}``",
            f"     - ``{pos_str}``",
            f"     - {len(b.compartments)}",
        ])
    for sp in spacer_pieces:
        rst_lines.extend([
            f"   * - :ref:`{sp.label} <spacer-{game_slug}-{sp.label.lower()}>`",
            f"     - {box_type_ref(BoxType.NO_LID)} (spacer)",
            f"     - ``{fmt_dim(sp.size)}``",
            f"     - ``{fmt_pos(sp.position)}``",
            "     - —",
        ])
    rst_lines.append("")

    # 3. Individual Boxes & Their Parts
    rst_lines.extend([
        "Individual Boxes & Parts",
        "------------------------",
        "",
    ])

    for b in proj.boxes:
        bp = body_pieces.get(b.label)
        size_str = fmt_dim(bp.size if bp else b.final_size)
        pos_str = fmt_pos(bp.position if bp else b.position)
        body_uri = part_uris.get((b.label, "body"))
        lid_uri = part_uris.get((b.label, "lid"))
        body_fname = part_filenames.get((b.label, "body"), f"{b.label}_body.stl")
        lid_fname = part_filenames.get((b.label, "lid"), f"{b.label}_lid.stl")

        rst_lines.extend([
            f".. _box-{game_slug}-{b.label.lower()}:",
            "",
            f"{b.label}",
            "^" * len(b.label),
            "",
            f"- **Box Type**: {box_type_ref(b.box_type)}",
            f"- **Outer Dimensions**: ``{size_str}``",
            f"- **Packed Position**: ``{pos_str}``",
        ])
        stackable = getattr(b, "stackable", None)
        if isinstance(stackable, StackableMode):
            rst_lines.append(f"- **Stackable Mode**: ``StackableMode.{stackable.name}``")
            top_active = getattr(b, "stackable_top", True)
            bot_active = getattr(b, "stackable_bottom", True)
            top_cfg = getattr(b, "stackable_top_pyramid_count", None) or getattr(
                b, "stackable_pyramid_count", None
            )
            bot_cfg = getattr(b, "stackable_bottom_pyramid_count", None) or getattr(
                b, "stackable_pyramid_count", None
            )
            if not top_active or not bot_active or top_cfg is not None or bot_cfg is not None:
                top_desc = (
                    f"pyramids={top_cfg!r}"
                    if (top_active and top_cfg is not None)
                    else ("enabled" if top_active else "flat (top of stack)")
                )
                bot_desc = (
                    f"pyramids={bot_cfg!r}"
                    if (bot_active and bot_cfg is not None)
                    else ("enabled" if bot_active else "flat (bottom of stack)")
                )
                rst_lines.append(
                    f"- **Stacking Order Key**: bottom ``{bot_desc}``, top ``{top_desc}``"
                )
        elif stackable is True:
            rst_lines.append("- **Stackable**: ``True``")

        if b.compartments:
            comp_items = []
            for c in b.compartments:
                dims = []
                if c.size is not None:
                    dims.append(f"{c.size[0]:g} × {c.size[1]:g} mm")
                else:
                    if c.width_ratio is not None:
                        dims.append(f"W={c.width_ratio:.0%}")
                    if c.length_ratio is not None:
                        dims.append(f"L={c.length_ratio:.0%}")
                if c.depth is not None:
                    dims.append(f"D={c.depth:g} mm")
                if c.elements:
                    dims.append(f"{len(c.elements)} elements")
                dim_info = f" ({', '.join(dims)})" if dims else " (full interior)"
                comp_items.append(f"``{c.label}``{dim_info}")
            rst_lines.append(f"- **Compartments ({len(b.compartments)})**: {', '.join(comp_items)}")
        rst_lines.append("")

        # Assembled box viewer (Body + Lid)
        box_uris = [u for u in (body_uri, lid_uri) if u is not None]
        if box_uris:
            if lid_uri is not None:
                rst_lines.extend([
                    f"**Assembled Box ({b.label} — Body + Lid)**",
                    "",
                    f".. stl:: {','.join(box_uris)}",
                    "   :height: 320px",
                    "",
                    html_download_combined(
                        box_uris,
                        f"{b.label}_assembled.stl",
                        f"Download Assembled {b.label} STL",
                    ),
                ])

            # Body part viewer + download
            if body_uri is not None:
                rst_lines.extend([
                    f"**Part: {b.label} Body**",
                    "",
                    f".. stl:: {body_uri}",
                    "   :height: 280px",
                    "",
                    html_download_single(
                        body_uri,
                        body_fname,
                        f"Download {b.label} Body STL",
                    ),
                ])

            # Lid part viewer + download
            if lid_uri is not None:
                rst_lines.extend([
                    f"**Part: {b.label} Lid**",
                    "",
                    f".. stl:: {lid_uri}",
                    "   :height: 280px",
                    "",
                    html_download_single(
                        lid_uri,
                        lid_fname,
                        f"Download {b.label} Lid STL",
                    ),
                ])

    # 4. Spacer Trays
    if spacer_pieces:
        rst_lines.extend([
            "Spacer Trays",
            "------------",
            "",
        ])
        for sp in spacer_pieces:
            sp_uri = part_uris.get((sp.label, "spacer"))
            sp_fname = part_filenames.get((sp.label, "spacer"), f"{sp.label}.stl")
            rst_lines.extend([
                f".. _spacer-{game_slug}-{sp.label.lower()}:",
                "",
                f"{sp.label}",
                "^" * len(sp.label),
                "",
                f"- **Type**: {box_type_ref(BoxType.NO_LID)} filler spacer tray",
                f"- **Outer Dimensions**: ``{fmt_dim(sp.size)}``",
                f"- **Packed Position**: ``{fmt_pos(sp.position)}``",
                "",
            ])
            if sp_uri is not None:
                rst_lines.extend([
                    f".. stl:: {sp_uri}",
                    "   :height: 280px",
                    "",
                    html_download_single(
                        sp_uri,
                        sp_fname,
                        f"Download {sp.label} STL",
                    ),
                ])

    DOCS_BOXES_DIR.mkdir(parents=True, exist_ok=True)
    rst_path = DOCS_BOXES_DIR / f"{game_slug}.rst"
    rst_path.write_text("\n".join(rst_lines), encoding="utf-8")

    return {
        "slug": game_slug,
        "name": proj.name,
        "game_box_size": gsize,
        "num_boxes": len(proj.boxes),
        "num_spacers": len(spacer_pieces),
        "box_types": box_types_used,
        "tris": total_tris,
        "elapsed": time.time() - t0,
    }


def write_index_rst(results: list[dict[str, Any]]) -> None:
    """Write ``docs/boxes/index.rst`` indexing all 39 game box inserts."""
    lines = [
        ".. _board-game-inserts-gallery:",
        "",
        "Board-Game Insert Gallery",
        "=========================",
        "",
        "Complete gallery of all board-game insert projects included in ``boxes/``.",
        "Each page provides interactive 3-D STL viewers and downloadable STL meshes for:",
        "",
        "- **Full Box Packing** — all sub-boxes, lids, and spacer trays positioned inside the game box,",
        "- **Each Box Individually** — assembled view of each box with its lid, and",
        "- **All Individual Parts** — separate printable body, lid, and spacer STL meshes,",
        "  with cross-reference links to each :doc:`../box_types` mechanism.",
        "",
        ".. list-table:: All Board-Game Inserts",
        "   :header-rows: 1",
        "   :widths: 24 20 12 12 32",
        "",
        "   * - Game Insert",
        "     - Game Box Size",
        "     - Boxes",
        "     - Spacers",
        "     - Box Types Used",
    ]

    for r in sorted(results, key=lambda x: x["slug"]):
        slug = r["slug"]
        name = r["name"]
        gsize = fmt_dim(r["game_box_size"])
        bt_links = ", ".join(box_type_ref(bt) for bt in r["box_types"])
        lines.extend([
            f"   * - :doc:`{name} ({slug}) <{slug}>`",
            f"     - ``{gsize}``",
            f"     - {r['num_boxes']}",
            f"     - {r['num_spacers']}",
            f"     - {bt_links}",
        ])

    lines.extend([
        "",
        ".. toctree::",
        "   :maxdepth: 1",
        "   :caption: Game Box Inserts",
        "",
    ])
    for r in sorted(results, key=lambda x: x["slug"]):
        lines.append(f"   {r['slug']}")
    lines.append("")

    (DOCS_BOXES_DIR / "index.rst").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """Entry point to generate STLs and RST documentation for all game inserts."""
    t_start = time.time()
    game_slugs = sorted(
        p.parent.name
        for p in BOXES_DIR.glob("*/*.py")
        if p.stem == p.parent.name
    )
    print(f"Generating STLs and docs pages for {len(game_slugs)} games...")
    results: list[dict[str, Any]] = []
    with ProcessPoolExecutor(max_workers=8) as pool:
        futs = {pool.submit(process_game, slug): slug for slug in game_slugs}
        for fut in as_completed(futs):
            slug = futs[fut]
            res = fut.result()
            results.append(res)
            print(
                f"  [{len(results):2d}/{len(game_slugs)}] {slug:30s}: "
                f"{res['num_boxes']:2d} boxes, {res['num_spacers']:2d} spacers, "
                f"{res['tris']:7d} tris in {res['elapsed']:.1f}s"
            )

    write_index_rst(results)
    total_tris = sum(r["tris"] for r in results)
    print(
        f"Done! {len(results)} games, {total_tris:,} triangles (~{total_tris * 50 / 1e6:.1f} MB) "
        f"in {time.time() - t_start:.1f}s"
    )


if __name__ == "__main__":
    main()
