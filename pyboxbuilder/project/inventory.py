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
    from pyboxbuilder.project.manifest import GameBoard, ProjectManifest


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

_NO_LID_TYPES = frozenset({BoxType.NO_LID, BoxType.PATH})


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
    """Result of verifying that all declared game components are allocated into boxes/boards."""

    declared: dict[str, int]
    allocated: dict[str, int]
    missing: dict[str, int]
    over_allocated: dict[str, int]
    unknown: dict[str, int]

    @property
    def is_valid(self) -> bool:
        """True when every declared component is allocated with exact count and no unknowns."""
        return not (self.missing or self.over_allocated or self.unknown)

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
        return "; ".join(lines)


def verify_inventory(
    manifest: ProjectManifest,
    *,
    strict: bool = False,
) -> InventoryVerification:
    """Check that boxes and boards account for 100% of the declared game component inventory."""
    declared: dict[str, int] = {}
    for comp in manifest.components:
        declared[comp.name] = declared.get(comp.name, 0) + comp.count

    allocated: dict[str, int] = {}

    def _add(name: str, qty: int) -> None:
        if qty > 0:
            allocated[name] = allocated.get(name, 0) + qty

    for builder in manifest.boxes:
        for name, qty in getattr(builder, "allocates", ()):
            _add(name, qty)
        for comp_b in builder.compartments:
            if comp_b.allocates:
                for name, qty in comp_b.allocates:
                    _add(name, qty)
            elif comp_b.component is not None:
                _add(comp_b.component, comp_b.count if comp_b.count is not None else 1)
            for elem in comp_b.elements:
                if elem.component is not None:
                    _add(elem.component, elem.count if elem.count is not None else 1)

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

    result = InventoryVerification(
        declared=declared,
        allocated=allocated,
        missing=missing,
        over_allocated=over_allocated,
        unknown=unknown,
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
