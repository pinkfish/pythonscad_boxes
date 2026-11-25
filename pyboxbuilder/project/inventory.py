# SPDX-License-Identifier: Apache-2.0
"""Automatic piece-count and component inventory extraction for projects and boxes."""

from __future__ import annotations

import re
from collections import OrderedDict
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyboxbuilder.enums import BoxType, ElementShape

if TYPE_CHECKING:
    from pyboxbuilder.builders._base import BoxBuilder
    from pyboxbuilder.compartments.element import CompartmentElement
    from pyboxbuilder.project.manifest import GameBoard, GameComponent, ProjectManifest


_HELPER_TOKENS = frozenset({
    "bite",
    "bites",
    "grab",
    "grabs",
    "scoop",
    "scoops",
    "finger",
    "relief",
    "shelf",
    "shelves",
    "channel",
    "trough",
    "dish",
    "basin",
    "recess",
    "dip",
    "indent",
    "indents",
    "notch",
    "notches",
    "cutout",
    "cutouts",
    "clearance",
    "terrace",
    "pinch",
    "access",
    "rim",
    "inlay",
    "slot_relief",
    "lift",
})

_NO_LID_TYPES = frozenset({BoxType.NO_LID, BoxType.PATH, BoxType.CARD_TRAY})


def _split_tokens(text: str) -> list[str]:
    """Split snake_case, kebab-case, and CamelCase identifiers into lowercase tokens."""
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", text)
    spaced = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", spaced)
    return [tok.lower() for tok in re.split(r"[^A-Za-z0-9]+", spaced) if tok]


def _is_helper_element(elem: CompartmentElement) -> bool:
    """Return True if an element is a finger-bite, scoop, grab shelf, or floor inlay."""
    if elem.count is not None:
        return elem.count <= 0
    if elem.color is not None:
        return True
    if elem.shape is ElementShape.SPHERE_SCOOP:
        return True
    if elem.label:
        tokens = set(_split_tokens(elem.label))
        if tokens & _HELPER_TOKENS:
            return True
    return False


def _normalize_item_name(raw: str) -> str:
    """Turn a compartment/element label into a clean group name (stripping trailing indices)."""
    cleaned = raw.strip()
    # Strip trailing row/col/index suffixes: _0_1, _r0_c2, _1, #2, -3, (1)
    cleaned = re.sub(r"(?:[_\-\s]+(?:r\d+[_\-]?c\d+|\d+|[A-Z]))+$", "", cleaned)
    cleaned = re.sub(r"\s*#\d+$", "", cleaned)
    cleaned = cleaned.strip("_- ") or raw.strip()
    # Insert spaces in CamelCase and replace underscores
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", cleaned)
    spaced = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", spaced)
    spaced = re.sub(r"[_\-]+", " ", spaced)
    return " ".join(spaced.split())


@dataclass(frozen=True)
class PieceEntry:
    """One grouped item entry stored inside a box."""

    name: str
    """Human-readable piece or compartment name."""
    count: int | None
    """Exact count of pieces/wells if known, or ``None`` for an uncounted bulk compartment."""

    def format_short(self) -> str:
        """Format as ``'5× Gear'`` when counted, or ``'Cards'`` when bulk."""
        if self.count is not None:
            return f"{self.count}x {self.name}"
        return self.name


@dataclass(frozen=True)
class BoxPieceSummary:
    """Extracted piece-count and printed-part summary for one sub-box."""

    label: str
    box_type: BoxType
    printed_bodies: int
    printed_lids: int
    compartment_count: int
    entries: tuple[PieceEntry, ...]
    counted_pieces: int

    def format_contents(self, max_items: int = 5) -> str:
        """Return a concise single-line description of what goes inside this box."""
        if not self.entries:
            return "—"
        shown = [e.format_short() for e in self.entries[:max_items]]
        if len(self.entries) > max_items:
            shown.append(f"+{len(self.entries) - max_items} more")
        return ", ".join(shown)


@dataclass(frozen=True)
class ComponentChecklistRow:
    """One row in the master game-component checklist showing total count and where pieces pack."""

    name: str
    count: int
    locations: tuple[tuple[str, int], ...]

    def format_locations(self, max_items: int = 4) -> str:
        """Format packing locations concisely, e.g. ``'HexBox_1 (45)'`` or ``'4 boxes (16 each)'``."""
        if not self.locations:
            return "—"
        if len(self.locations) > max_items:
            qty_set = {qty for _, qty in self.locations}
            if len(qty_set) == 1:
                only_qty = next(iter(qty_set))
                return f"{len(self.locations)} boxes ({only_qty} each)"
        shown = [
            f"{loc} ({qty})" if len(self.locations) > 1 or qty != self.count else loc
            for loc, qty in self.locations[:max_items]
        ]
        if len(self.locations) > max_items:
            shown.append(f"+{len(self.locations) - max_items} more")
        return ", ".join(shown)


@dataclass(frozen=True)
class ProjectInventory:
    """Complete printed-part, board, and stored-piece inventory for a project."""

    project_name: str
    printed_bodies: int
    printed_lids: int
    printed_spacers: int
    boards: tuple[GameBoard, ...]
    box_summaries: tuple[BoxPieceSummary, ...]
    checklist: tuple[ComponentChecklistRow, ...] = ()

    @property
    def total_printed_parts(self) -> int:
        """Total 3-D printed STL parts (bodies + lids + spacers)."""
        return self.printed_bodies + self.printed_lids + self.printed_spacers

    @property
    def total_board_count(self) -> int:
        """Total physical boards / screens / playmats tracked on the project."""
        return sum(b.count for b in self.boards)

    @property
    def total_counted_pieces(self) -> int:
        """Sum of all explicitly/structurally counted game pieces across all boxes."""
        return sum(s.counted_pieces for s in self.box_summaries)

    def by_label(self, label: str) -> BoxPieceSummary | None:
        """Look up one box's piece summary by label."""
        for s in self.box_summaries:
            if s.label == label:
                return s
        return None


def summarize_box_pieces(builder: BoxBuilder) -> BoxPieceSummary:
    """Extract piece counts and contents automatically from a BoxBuilder definition."""
    has_lid = builder.box_type not in _NO_LID_TYPES
    counted_groups: OrderedDict[str, int] = OrderedDict()
    bulk_names: list[str] = []

    # Box-level explicit allocations (e.g. hollow no-lid trays holding a score pad)
    for comp_name, qty in getattr(builder, "allocates", ()):
        if qty > 0:
            counted_groups[comp_name] = counted_groups.get(comp_name, 0) + qty

    for comp in builder.compartments:
        if comp.allocates:
            for comp_name, qty in comp.allocates:
                if qty > 0:
                    counted_groups[comp_name] = counted_groups.get(comp_name, 0) + qty
            continue
        if comp.component is not None and comp.count is not None:
            counted_groups[comp.component] = counted_groups.get(comp.component, 0) + comp.count
            continue
        if comp.count is not None:
            name = _normalize_item_name(comp.label)
            counted_groups[name] = counted_groups.get(name, 0) + comp.count
        elif comp.elements:
            found_any = False
            for elem in comp.elements:
                if _is_helper_element(elem):
                    continue
                found_any = True
                qty = elem.count if elem.count is not None else 1
                raw_name = elem.component or elem.label or comp.label
                name = elem.component if elem.component else _normalize_item_name(raw_name)
                counted_groups[name] = counted_groups.get(name, 0) + qty
            if not found_any:
                name = _normalize_item_name(comp.label)
                if name not in bulk_names:
                    bulk_names.append(name)
        else:
            name = comp.component if comp.component else _normalize_item_name(comp.label)
            if name not in bulk_names:
                bulk_names.append(name)

    entries: list[PieceEntry] = [
        PieceEntry(name=name, count=qty) for name, qty in counted_groups.items()
    ]
    for name in bulk_names:
        if name not in counted_groups:
            entries.append(PieceEntry(name=name, count=None))

    return BoxPieceSummary(
        label=builder.label,
        box_type=builder.box_type,
        printed_bodies=1,
        printed_lids=1 if has_lid else 0,
        compartment_count=len(builder.compartments),
        entries=tuple(entries),
        counted_pieces=sum(counted_groups.values()),
    )


@dataclass(frozen=True)
class InventoryVerification:
    """Result of verifying declared game components against boxes, boards, SVGs, and physical fit."""

    declared: dict[str, int]
    allocated: dict[str, int]
    missing: dict[str, int]
    over_allocated: dict[str, int]
    unknown: dict[str, int]
    missing_svgs: tuple[str, ...] = ()
    fit_warnings: tuple[str, ...] = ()
    bed_warnings: tuple[str, ...] = ()
    spill_warnings: tuple[str, ...] = ()
    near_square_warnings: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        """True when counts, SVG shapes, physical fit, print-bed, and spill checks all pass."""
        return not (
            self.missing
            or self.over_allocated
            or self.unknown
            or self.missing_svgs
            or self.fit_warnings
            or self.bed_warnings
            or self.spill_warnings
        )

    def format_errors(self) -> str:
        """Return a human-readable summary of all inventory mismatches."""
        lines: list[str] = []
        if self.missing:
            lines.append(
                "Missing (unallocated) pieces: "
                + ", ".join(f"{k} (need {v} more)" for k, v in self.missing.items())
            )
        if self.over_allocated:
            lines.append(
                "Over-allocated pieces: "
                + ", ".join(f"{k} (+{v} extra)" for k, v in self.over_allocated.items())
            )
        if self.unknown:
            lines.append(
                "Unknown (undeclared) components: "
                + ", ".join(f"{k} ({v})" for k, v in self.unknown.items())
            )
        if self.missing_svgs:
            lines.append("Missing SVG cutouts: " + "; ".join(self.missing_svgs))
        if self.fit_warnings:
            lines.append("Physical fit errors: " + "; ".join(self.fit_warnings))
        if self.bed_warnings:
            lines.append("Print-bed size errors: " + "; ".join(self.bed_warnings))
        if self.spill_warnings:
            lines.append("Vertical-storage spill risks: " + "; ".join(self.spill_warnings))
        return "; ".join(lines)


def _check_vertical_card_fit(
    spec: GameComponent,
    qty: int,
    avail_w: float,
    avail_l: float,
    avail_h: float,
    tilt_deg: float,
    location_label: str,
) -> str | None:
    """Return a fit error string if vertical/angled cards do not fit inside ``(avail_w, avail_l, avail_h)``."""
    import math

    fp = spec.footprint
    if fp is None:
        return None
    card_w, card_h = fp
    rad = math.radians(max(0.0, min(59.0, tilt_deg)))
    thickness = spec.piece_height or 0.6

    # Allow either portrait (card_w across, card_h standing) or landscape (card_h across, card_w standing),
    # and allow the card row to run along either Y (avail_l) or X (avail_w).
    for stand_w, stand_h in ((card_w, card_h), (card_h, card_w)):
        req_h = stand_h * math.cos(rad)
        req_row = qty * thickness / math.cos(rad) + stand_h * math.sin(rad)
        if req_h <= avail_h + 0.5:
            fits_y = stand_w <= avail_w + 0.2 and req_row <= avail_l + 0.5
            fits_x = stand_w <= avail_l + 0.2 and req_row <= avail_w + 0.5
            if fits_y or fits_x:
                return None

    # Compute the primary orientation requirement for a clear error message
    req_h = card_h * math.cos(rad)
    req_row = qty * thickness / math.cos(rad) + card_h * math.sin(rad)
    return (
        f"{location_label}: {qty}x {spec.name} ({spec.card_orientation}, tilt={tilt_deg:.0f}°) "
        f"needs {card_w:.1f}x{req_row:.1f}x{req_h:.1f}mm, "
        f"only has {avail_w:.1f}x{avail_l:.1f}x{avail_h:.1f}mm usable"
    )


def _xy_covered_by(
    box_x: float,
    box_y: float,
    box_w: float,
    box_l: float,
    cover_x: float,
    cover_y: float,
    cover_w: float,
    cover_l: float,
    tol: float = 2.0,
) -> bool:
    """Return True if the XY rectangle ``(cover_x, cover_y, cover_w, cover_l)`` covers the box."""
    return (
        cover_x <= box_x + tol
        and cover_y <= box_y + tol
        and (cover_x + cover_w) >= (box_x + box_w) - tol
        and (cover_y + cover_l) >= (box_y + box_l) - tol
    )


def verify_inventory(
    manifest: ProjectManifest,
    *,
    strict: bool = False,
    check_fit: bool = True,
    check_vertical_storage: bool = False,
    packing: object = None,
) -> InventoryVerification:
    """Check that boxes and boards account for 100% of declared components, SVGs, and physical fit."""
    from pathlib import Path

    from pyboxbuilder.box.registry import LIDLESS_BOX_TYPES

    declared: dict[str, int] = {}
    comp_by_name: dict[str, GameComponent] = {}
    for comp in manifest.components:
        declared[comp.name] = declared.get(comp.name, 0) + comp.count
        comp_by_name[comp.name] = comp

    allocated: dict[str, int] = {}
    # Track which SVG filenames are actually carved in boxes holding each component
    svgs_by_component: dict[str, set[str]] = {}
    fit_warnings: list[str] = []
    bed_warnings: list[str] = []
    spill_warnings: list[str] = []
    near_square_warnings: list[str] = []

    def _add(name: str, qty: int) -> None:
        if qty > 0:
            allocated[name] = allocated.get(name, 0) + qty

    # Build a lookup of placed box (x, y, z, w, l, h) from packing or builder attributes
    placed_boxes: dict[str, tuple[float, float, float, float, float, float]] = {}
    if packing is not None and hasattr(packing, "placements"):
        for pl in getattr(packing, "placements", ()):
            px, py, pz = pl.position
            pw, pl_dim, ph = pl.size
            placed_boxes[pl.label] = (
                float(px),
                float(py),
                float(pz),
                float(pw),
                float(pl_dim),
                float(ph),
            )
    for b in manifest.boxes:
        if b.label not in placed_boxes:
            sz = b.final_size or b.size
            if (
                b.position is not None
                and sz is not None
                and len(sz) == 3
                and all(d is not None for d in sz)
            ):
                placed_boxes[b.label] = (
                    float(b.position[0]),
                    float(b.position[1]),
                    float(b.position[2]),
                    float(sz[0]),
                    float(sz[1]),
                    float(sz[2]),
                )

    for builder in manifest.boxes:
        box_svg_names: set[str] = set()
        for comp_b in builder.compartments:
            if comp_b.shape_file:
                box_svg_names.add(Path(comp_b.shape_file).name)
            for elem in comp_b.elements:
                if elem.shape == ElementShape.SVG and elem.shape_file:
                    box_svg_names.add(Path(elem.shape_file).name)

        box_components: set[str] = set()
        wall_t = builder.wall_thickness if builder.wall_thickness is not None else manifest.wall_thickness
        floor_t = builder.floor_thickness if builder.floor_thickness is not None else manifest.floor_thickness
        bt = getattr(builder, "box_type", None)
        lid_t = (
            0.0
            if bt in LIDLESS_BOX_TYPES
            else (builder.lid_thickness if builder.lid_thickness is not None else manifest.lid_thickness)
        )
        eff_size = builder.final_size or builder.size
        box_w: float | None = None
        box_l: float | None = None
        box_h: float | None = None
        if eff_size is not None and len(eff_size) == 3:
            if eff_size[0] is not None:
                box_w = float(eff_size[0])
            if eff_size[1] is not None:
                box_l = float(eff_size[1])
            if eff_size[2] is not None:
                box_h = float(eff_size[2])

        # Print-bed size validation
        if manifest.bed_size is not None and box_w is not None and box_l is not None:
            bed_w, bed_l = float(manifest.bed_size[0]), float(manifest.bed_size[1])
            fits_bed = (box_w <= bed_w + 0.1 and box_l <= bed_l + 0.1) or (
                box_l <= bed_w + 0.1 and box_w <= bed_l + 0.1
            )
            if not fits_bed:
                bed_warnings.append(
                    f"{builder.label}: footprint {box_w:.1f}x{box_l:.1f}mm exceeds "
                    f"print bed {bed_w:.1f}x{bed_l:.1f}mm"
                )

        # Near-square lid jam advisory for CAP / SLIPOVER boxes
        if bt in (BoxType.CAP, BoxType.SLIPOVER) and box_w is not None and box_l is not None:
            diff = abs(box_w - box_l)
            if 0.5 < diff < 4.0:
                near_square_warnings.append(
                    f"{builder.label}: near-square {bt.value} box ({box_w:.1f}x{box_l:.1f}mm, "
                    f"diff={diff:.1f}mm) can jam if lid is rotated 90°"
                )

        for name, qty in getattr(builder, "allocates", ()):
            _add(name, qty)
            if qty > 0:
                box_components.add(name)
                if check_fit and name in comp_by_name and box_w is not None and box_l is not None and box_h is not None:
                    spec = comp_by_name[name]
                    if spec.kind == "cards" and spec.card_orientation in ("vertical", "angled"):
                        tilt = spec.card_tilt_angle
                        if spec.card_orientation == "angled" and tilt == 0.0:
                            tilt = float(getattr(builder, "card_tilt_angle", 20.0)) or 20.0
                        err = _check_vertical_card_fit(
                            spec,
                            qty,
                            box_w - 2.0 * wall_t,
                            box_l - 2.0 * wall_t,
                            box_h - floor_t - lid_t,
                            tilt,
                            builder.label,
                        )
                        if err is not None:
                            fit_warnings.append(err)

        for comp_b in builder.compartments:
            if comp_b.allocates:
                for name, qty in comp_b.allocates:
                    _add(name, qty)
                    if qty > 0:
                        box_components.add(name)
            elif comp_b.component is not None:
                qty = comp_b.count if comp_b.count is not None else 1
                _add(comp_b.component, qty)
                if qty > 0:
                    box_components.add(comp_b.component)
                if check_fit and comp_b.component in comp_by_name:
                    spec = comp_by_name[comp_b.component]
                    if spec.kind == "cards" and spec.card_orientation in ("vertical", "angled"):
                        if box_h is not None:
                            avail_w = comp_b.size[0] if comp_b.size is not None else (
                                (box_w - 2.0 * wall_t) if box_w is not None else None
                            )
                            avail_l = comp_b.size[1] if comp_b.size is not None else (
                                (box_l - 2.0 * wall_t) if box_l is not None else None
                            )
                            if avail_w is not None and avail_l is not None:
                                tilt = spec.card_tilt_angle
                                if spec.card_orientation == "angled" and tilt == 0.0:
                                    tilt = float(getattr(builder, "card_tilt_angle", 20.0)) or 20.0
                                err = _check_vertical_card_fit(
                                    spec,
                                    qty,
                                    avail_w,
                                    avail_l,
                                    box_h - floor_t - lid_t,
                                    tilt,
                                    f"{builder.label}/{comp_b.label}",
                                )
                                if err is not None:
                                    fit_warnings.append(err)
                    else:
                        # Footprint fit check (allowing 90-degree rotation)
                        fp = spec.footprint
                        if fp is not None and comp_b.size is not None and not spec.bulk:
                            pw, pl = fp
                            cw, cl = comp_b.size
                            fits_normal = pw <= cw + 0.1 and pl <= cl + 0.1
                            fits_rot = pl <= cw + 0.1 and pw <= cl + 0.1
                            if not (fits_normal or fits_rot):
                                fit_warnings.append(
                                    f"{builder.label}/{comp_b.label}: {spec.name} ({pw:.1f}x{pl:.1f}mm) "
                                    f"does not fit compartment ({cw:.1f}x{cl:.1f}mm)"
                                )
                        # Vertical stack height fit check (cards & non-bulk stacked pieces)
                        if (spec.kind == "cards" or not spec.bulk) and box_h is not None:
                            req_h = spec.stack_height(qty)
                            avail_h = box_h - floor_t - lid_t
                            if req_h is not None and req_h > avail_h + 0.5:
                                fit_warnings.append(
                                    f"{builder.label}/{comp_b.label}: {qty}x {spec.name} needs "
                                    f"{req_h:.1f}mm height, box only has {avail_h:.1f}mm usable"
                                )

            for elem in comp_b.elements:
                if elem.component is not None:
                    qty = elem.count if elem.count is not None else 1
                    _add(elem.component, qty)
                    if qty > 0:
                        box_components.add(elem.component)
                        if elem.shape == ElementShape.SVG and elem.shape_file:
                            svgs_by_component.setdefault(elem.component, set()).add(Path(elem.shape_file).name)

        for comp_name in box_components:
            svgs_by_component.setdefault(comp_name, set()).update(box_svg_names)

        # Vertical-storage ("Kallax-safe") spill check for open/lidless boxes
        if check_vertical_storage and bt in LIDLESS_BOX_TYPES:
            holds_spillable = any(
                comp_by_name[n].bulk or comp_by_name[n].kind != "board"
                for n in box_components
                if n in comp_by_name
            ) or bool(builder.compartments) or bool(getattr(builder, "allocates", ()))
            if holds_spillable:
                capped = False
                if builder.label in placed_boxes:
                    bx, by, bz, bw, bl, bh = placed_boxes[builder.label]
                    z_top = bz + bh
                    # 1. Capped by game box lid or top-stored board_thickness
                    if manifest.game_box_size is not None:
                        gh = float(manifest.game_box_size[2])
                        ceiling_z = gh if manifest.board_on_bottom else (gh - manifest.board_thickness)
                        if ceiling_z - z_top <= 1.5:
                            capped = True
                    # 2. Capped by a GameBoard resting directly above
                    if not capped:
                        for gb in manifest.boards:
                            gb_z = float(gb.position[2])
                            if -0.5 <= (gb_z - z_top) <= 1.5 and _xy_covered_by(
                                bx, by, bw, bl,
                                float(gb.position[0]), float(gb.position[1]),
                                float(gb.size[0]), float(gb.size[1]),
                            ):
                                capped = True
                                break
                    # 3. Capped by another box stacked directly above
                    if not capped:
                        for other_lbl, (ox, oy, oz, ow, ol, _oh) in placed_boxes.items():
                            if other_lbl == builder.label:
                                continue
                            if -0.5 <= (oz - z_top) <= 1.5 and _xy_covered_by(
                                bx, by, bw, bl, ox, oy, ow, ol
                            ):
                                capped = True
                                break
                if not capped:
                    spill_warnings.append(
                        f"{builder.label}: open {bt.value} tray is not capped within 1.5mm by a lid, "
                        f"board, or stacked box (spill risk in vertical storage)"
                    )

    for gb in manifest.boards:
        if gb.allocates:
            for name, qty in gb.allocates:
                _add(name, qty)
        elif gb.component is not None:
            _add(gb.component, gb.count)
        elif gb.label in declared:
            _add(gb.label, gb.count)

    # Loose items explicitly assigned a storage location (e.g. "Inside spacer_1")
    for comp in manifest.components:
        if comp.location:
            _add(comp.name, comp.count)

    missing: dict[str, int] = {}
    over_allocated: dict[str, int] = {}
    unknown: dict[str, int] = {}

    for name, req in declared.items():
        got = allocated.get(name, 0)
        if got < req:
            missing[name] = req - got
        elif got > req:
            over_allocated[name] = got - req

    for name, got in allocated.items():
        if name not in declared:
            unknown[name] = got

    missing_svgs: list[str] = []
    for comp in manifest.components:
        if comp.svg is not None and not comp.bulk:
            svg_path = Path(comp.svg)
            if not svg_path.exists():
                missing_svgs.append(f"{comp.name}: SVG file not found ({comp.svg})")
            elif svg_path.name not in svgs_by_component.get(comp.name, set()):
                missing_svgs.append(
                    f"{comp.name}: declares SVG '{svg_path.name}' but no box includes a matching SVG cutout"
                )

    result = InventoryVerification(
        declared=declared,
        allocated=allocated,
        missing=missing,
        over_allocated=over_allocated,
        unknown=unknown,
        missing_svgs=tuple(missing_svgs),
        fit_warnings=tuple(fit_warnings),
        bed_warnings=tuple(bed_warnings),
        spill_warnings=tuple(spill_warnings),
        near_square_warnings=tuple(near_square_warnings),
    )
    if strict and not result.is_valid:
        raise ValueError(f"Inventory mismatch in {manifest.name!r}: {result.format_errors()}")
    return result


def _build_component_checklist(manifest: ProjectManifest) -> tuple[ComponentChecklistRow, ...]:
    """Map every declared component in the manifest to the box(es), board(s), or spacer(s) holding it."""
    if not manifest.components:
        return ()

    declared: OrderedDict[str, int] = OrderedDict()
    loc_map: dict[str, OrderedDict[str, int]] = {}
    for comp in manifest.components:
        declared[comp.name] = declared.get(comp.name, 0) + comp.count
        loc_map.setdefault(comp.name, OrderedDict())
        if comp.location:
            loc_map[comp.name][comp.location] = (
                loc_map[comp.name].get(comp.location, 0) + comp.count
            )

    def _record(name: str, where: str, qty: int) -> None:
        if qty <= 0 or name not in loc_map:
            return
        loc_map[name][where] = loc_map[name].get(where, 0) + qty

    for builder in manifest.boxes:
        for name, qty in getattr(builder, "allocates", ()):
            _record(name, builder.label, qty)
        for comp_b in builder.compartments:
            if comp_b.allocates:
                for name, qty in comp_b.allocates:
                    _record(name, builder.label, qty)
            elif comp_b.component is not None:
                _record(comp_b.component, builder.label, comp_b.count if comp_b.count is not None else 1)
            for elem in comp_b.elements:
                if elem.component is not None:
                    _record(elem.component, builder.label, elem.count if elem.count is not None else 1)

    for gb in manifest.boards:
        where = f"{gb.label} ({gb.notes})" if gb.notes else gb.label
        if gb.allocates:
            for name, qty in gb.allocates:
                _record(name, where, qty)
        elif gb.component is not None:
            _record(gb.component, where, gb.count)
        elif gb.label in declared:
            _record(gb.label, where, gb.count)

    return tuple(
        ComponentChecklistRow(
            name=name,
            count=total,
            locations=tuple(loc_map[name].items()),
        )
        for name, total in declared.items()
    )


def summarize_project(
    manifest: ProjectManifest,
    *,
    spacer_count: int = 0,
) -> ProjectInventory:
    """Extract the full printed-part, board, and stored-piece inventory for a manifest."""
    from pyboxbuilder.project.manifest import GameBoard

    box_summaries = tuple(summarize_box_pieces(b) for b in manifest.boxes)
    boards = list(manifest.boards)

    # If the project reserves full-footprint board_thickness > 0 and no explicit
    # GameBoard already represents that full-footprint slab, include it so counts
    # and packing sheets reflect it too.
    if manifest.board_thickness > 0 and manifest.game_box_size is not None:
        gw, gl, gh = manifest.game_box_size
        bz0 = 0.0 if manifest.board_on_bottom else (gh - manifest.board_thickness)
        bz1 = bz0 + manifest.board_thickness
        already_modeled = any(
            gb.position[2] < bz1 - 0.5 and (gb.position[2] + gb.size[2]) > bz0 + 0.5
            for gb in boards
        )
        if not already_modeled:
            boards.append(
                GameBoard(
                    label="Game Board / Manuals",
                    size=(gw, gl, manifest.board_thickness),
                    position=(0.0, 0.0, bz0),
                    count=1,
                    notes="Bottom of box" if manifest.board_on_bottom else "On top of insert",
                )
            )

    return ProjectInventory(
        project_name=manifest.name,
        printed_bodies=sum(s.printed_bodies for s in box_summaries),
        printed_lids=sum(s.printed_lids for s in box_summaries),
        printed_spacers=spacer_count,
        boards=tuple(boards),
        box_summaries=box_summaries,
        checklist=_build_component_checklist(manifest),
    )
