# SPDX-License-Identifier: Apache-2.0
"""Root board game insert — pyboxbuilder port of `examples/root.scad`."""

import math
import sys
from pathlib import Path
from typing import Any, Literal


# Repo root on sys.path
def _find_repo_root() -> Path:
    if "__file__" in globals():
        return Path(__file__).resolve().parents[2]
    curr = Path.cwd().resolve()
    for parent in [curr, *list(curr.parents)]:
        if (parent / "pyproject.toml").exists() or (parent / "boxes" / "root" / "svg").exists():
            return parent
    return curr

REPO_ROOT = _find_repo_root()
sys.path.insert(0, str(REPO_ROOT))
for _sp in REPO_ROOT.glob(".venv/lib/*/site-packages"):
    sys.path.insert(0, str(_sp))
for _sp in REPO_ROOT.glob("venv/*/lib/*/site-packages"):
    sys.path.insert(0, str(_sp))

from collections.abc import Iterable
from dataclasses import dataclass, replace
from enum import StrEnum

from pyboxbuilder import (
    BoxType,
    Color,
    LidBuilder,
    PatternBuilder,
    PatternType,
    Project,
    StackableMode,
    centered,
    pack_into_compartment,
    run,
)
from pyboxbuilder.compartments import CompartmentElement
from pyboxbuilder.enums import ElementShape


class RootBoxCategory(StrEnum):
    """Functional box category used by the Root expansion & box-type selector."""

    CARDS = "cards"
    FACTIONS = "factions"
    ITEMS_AND_DICE = "items_and_dice"
    SPACERS = "spacers"


ROOT_BOARD_BAY_HEIGHT_MM = 28.0
ROOT_BOX_TOTAL_HEIGHT_MM = 67.0


@dataclass(frozen=True)
class RootExpansionSpec:
    """Metadata describing a Root game module/expansion (implemented or planned)."""

    key: str
    name: str
    status: Literal["available", "planned"]
    description: str
    required: bool = False
    subgroups: tuple[str, ...] = ()
    board_thickness_mm: float = 0.0
    boards_summary: str = ""
    notes: str = ""


@dataclass(frozen=True)
class RootBoardStatus:
    """Board-stack space assessment for a given Root expansion combination."""

    expansions: tuple[str, ...]
    boards_mm: float
    capacity_mm: float
    top_gap_mm: float
    overflow_mm: float
    status: Literal["thin_top_gap", "exact_fit", "external_box_required"]
    summary: str


@dataclass(frozen=True)
class RootSubgroupSpec:
    """Selectable component/faction group within a Root expansion."""

    key: str
    name: str
    expansion: str
    description: str


@dataclass(frozen=True)
class RootBoxMeta:
    """Metadata classifying each printable Root sub-box."""

    label: str
    expansion: str
    subgroup: str
    category: RootBoxCategory
    description: str


ROOT_EXPANSIONS: tuple[RootExpansionSpec, ...] = (
    RootExpansionSpec(
        key="base",
        name="Base Game",
        status="available",
        required=True,
        description=(
            "Core 4 factions (Marquise de Cat, Eyrie Dynasties, Woodland Alliance, "
            "Vagabond), shared & overview decks, starting/craftable items, Winter "
            "clearing markers, and dice."
        ),
        subgroups=(
            "shared_cards",
            "items",
            "dice",
            "marquise",
            "eyrie",
            "alliance",
            "vagabond1",
        ),
        board_thickness_mm=22.0,
        boards_summary="Main folded map board, 4 Base faction boards, and Base rulebooks (~22 mm)",
    ),
    RootExpansionSpec(
        key="riverfolk",
        name="The Riverfolk Expansion",
        status="available",
        required=False,
        description=(
            "Adds Lizard Cult, Riverfolk Company, and a 2nd Vagabond tray "
            "(extra Vagabond quest/character cards and items already fit in the Base trays)."
        ),
        subgroups=("lizard_cult", "riverfolk_company", "vagabond2"),
        board_thickness_mm=6.0,
        boards_summary="Lizard Cult & Riverfolk faction boards + expansion rulebook (~6 mm)",
    ),
    RootExpansionSpec(
        key="underworld",
        name="The Underworld Expansion",
        status="planned",
        description="Underground Duchy & Corvid Conspiracy factions, landmarks, and extra maps.",
        subgroups=("underground_duchy", "corvid_conspiracy"),
        board_thickness_mm=11.0,
        boards_summary="Extra Underground/Lake map board + Duchy & Corvid boards (~11 mm)",
        notes=(
            "Beyond single-box board capacity: requires moving all boards out to a separate box. "
            "Warrior SVGs (duchy_warrior.svg, corvid_warrior.svg) exist in boxes/root/svg/."
        ),
    ),
    RootExpansionSpec(
        key="marauder",
        name="The Marauder Expansion",
        status="planned",
        description="Lord of the Hundreds & Keepers in Iron factions, advance setup, and hirelings.",
        subgroups=("lord_of_the_hundreds", "keepers_in_iron"),
        board_thickness_mm=7.0,
        boards_summary="Hundreds & Keepers faction boards + setup/rule sheets (~7 mm)",
        notes=(
            "Beyond single-box board capacity: requires moving all boards out to a separate box. "
            "Warrior SVGs (hundreds_warrior.svg, keepers_warrior.svg) exist in boxes/root/svg/."
        ),
    ),
    RootExpansionSpec(
        key="exiles_and_partisans",
        name="Exiles & Partisans Deck",
        status="planned",
        description="Alternative 54-card shared deck storage.",
        board_thickness_mm=0.0,
        boards_summary="Cards only (no extra boards)",
    ),
    RootExpansionSpec(
        key="hirelings_landmarks",
        name="Hirelings & Landmarks",
        status="planned",
        description="Modular trays for Hirelings and Landmarks packs.",
        board_thickness_mm=2.0,
        boards_summary="Hirelings & Landmarks rule/reference sheets (~2 mm)",
    ),
)

ROOT_SUBGROUPS: tuple[RootSubgroupSpec, ...] = (
    RootSubgroupSpec(
        "shared_cards",
        "Shared & Overview Cards",
        "base",
        "54-card main deck & overview/reference cards",
    ),
    RootSubgroupSpec(
        "items",
        "Items, Winter & Extra Tokens",
        "base",
        "Vagabond item stacks, ruin loot, Winter clearing markers, and spare token slots",
    ),
    RootSubgroupSpec("dice", "Combat Dice", "base", "2 Root combat dice"),
    RootSubgroupSpec("marquise", "Marquise de Cat", "base", "25 warriors, wood, keep, and buildings"),
    RootSubgroupSpec("eyrie", "Eyrie Dynasties", "base", "20 warriors, 7 roosts, leader & vizier cards"),
    RootSubgroupSpec("alliance", "Woodland Alliance", "base", "10 warriors, 3 bases, 10 sympathy tokens"),
    RootSubgroupSpec(
        "vagabond1",
        "Vagabond #1 & Quests",
        "base",
        "1st Vagabond meeple, items, score, relations & quest/character cards",
    ),
    RootSubgroupSpec("lizard_cult", "Lizard Cult", "riverfolk", "25 warriors, 15 gardens, outcast & score markers"),
    RootSubgroupSpec(
        "riverfolk_company",
        "Riverfolk Company",
        "riverfolk",
        "15 warriors, 9 trade posts, 3 glass gems, score & faction markers",
    ),
    RootSubgroupSpec(
        "vagabond2",
        "2nd Vagabond",
        "riverfolk",
        "2nd Vagabond meeple, score marker & 6 relationship markers",
    ),
)

ROOT_BOX_CATALOG: tuple[RootBoxMeta, ...] = (
    RootBoxMeta("BaseCardBox", "base", "shared_cards", RootBoxCategory.CARDS, "Shared 54-card main deck"),
    RootBoxMeta("OverviewCardBox", "base", "shared_cards", RootBoxCategory.CARDS, "Faction overview cards"),
    RootBoxMeta("ErieCardBox", "base", "eyrie", RootBoxCategory.CARDS, "Eyrie leader & vizier cards"),
    RootBoxMeta("VagabondCardBox", "base", "vagabond1", RootBoxCategory.CARDS, "Vagabond quest & character cards"),
    RootBoxMeta(
        "ItemsBoxBottom", "base", "items", RootBoxCategory.ITEMS_AND_DICE, "Starting Vagabond items & ruins"
    ),
    RootBoxMeta(
        "ItemsBoxMiddle", "base", "items", RootBoxCategory.ITEMS_AND_DICE, "Craftable items & extra ruin slots"
    ),
    RootBoxMeta("ItemsBoxWinter", "base", "items", RootBoxCategory.ITEMS_AND_DICE, "Winter Map clearing markers"),
    RootBoxMeta(
        "ItemsBoxExtras", "base", "items", RootBoxCategory.ITEMS_AND_DICE, "8 generic scenario/extra token pockets"
    ),
    RootBoxMeta("DiceBox", "base", "dice", RootBoxCategory.ITEMS_AND_DICE, "2 combat dice"),
    RootBoxMeta("MarquisBoxBottom", "base", "marquise", RootBoxCategory.FACTIONS, "Marquise warriors (25 meeples)"),
    RootBoxMeta(
        "MarquisBoxTop", "base", "marquise", RootBoxCategory.FACTIONS, "Marquise wood, keep, buildings & score"
    ),
    RootBoxMeta("ErieBoxBottom", "base", "eyrie", RootBoxCategory.FACTIONS, "Eyrie warriors (20 meeples)"),
    RootBoxMeta("ErieBoxTop", "base", "eyrie", RootBoxCategory.FACTIONS, "Eyrie roosts, faction & score"),
    RootBoxMeta(
        "AllianceBoxBottom", "base", "alliance", RootBoxCategory.FACTIONS, "Woodland Alliance warriors (10 meeples)"
    ),
    RootBoxMeta(
        "AllianceBoxTop", "base", "alliance", RootBoxCategory.FACTIONS, "Alliance bases, sympathy, faction & score"
    ),
    RootBoxMeta(
        "VagabondBox", "base", "vagabond1", RootBoxCategory.FACTIONS, "1st Vagabond meeple, score & relation tokens"
    ),
    RootBoxMeta(
        "LizardBoxBottom", "riverfolk", "lizard_cult", RootBoxCategory.FACTIONS, "Lizard Cult warriors (25 meeples)"
    ),
    RootBoxMeta(
        "LizardBoxTop",
        "riverfolk",
        "lizard_cult",
        RootBoxCategory.FACTIONS,
        "Lizard gardens, outcast, faction & score",
    ),
    RootBoxMeta(
        "RiverfolkBoxBottom",
        "riverfolk",
        "riverfolk_company",
        RootBoxCategory.FACTIONS,
        "Riverfolk warriors (15 meeples)",
    ),
    RootBoxMeta(
        "RiverfolkBoxTop",
        "riverfolk",
        "riverfolk_company",
        RootBoxCategory.FACTIONS,
        "Riverfolk trade posts, gems & score",
    ),
    RootBoxMeta(
        "VagabondBox2",
        "riverfolk",
        "vagabond2",
        RootBoxCategory.FACTIONS,
        "2nd Vagabond meeple, score & relation tokens",
    ),
)

_EXPANSION_BY_KEY: dict[str, RootExpansionSpec] = {spec.key: spec for spec in ROOT_EXPANSIONS}
_SUBGROUP_KEYS: set[str] = {spec.key for spec in ROOT_SUBGROUPS}
_BOX_META_BY_LABEL: dict[str, RootBoxMeta] = {meta.label: meta for meta in ROOT_BOX_CATALOG}


def resolve_root_subgroups(
    expansions: Iterable[str] | None = None,
    *,
    subgroups: Iterable[str] | None = None,
) -> set[str]:
    """Resolve active Root subgroups from expansion keys and/or explicit subgroup keys."""
    if subgroups is not None:
        resolved = set(subgroups)
        unknown = resolved - _SUBGROUP_KEYS
        if unknown:
            raise ValueError(f"Unknown Root subgroup(s): {sorted(unknown)}")
        return resolved

    exp_list = list(expansions) if expansions is not None else ["base", "riverfolk"]
    resolved_groups: set[str] = set()
    for key in exp_list:
        spec = _EXPANSION_BY_KEY.get(key)
        if spec is None:
            raise ValueError(f"Unknown Root expansion: '{key}'")
        if spec.status != "available":
            raise NotImplementedError(
                f"Root expansion '{key}' ({spec.name}) is planned but not yet implemented."
            )
        resolved_groups.update(spec.subgroups)
    return resolved_groups


def pack_in_columns(
    items: list[dict[str, Any]],
    comp_size: tuple[float, float],
    column_width: float,
    spacing_x: float = 2.0,
    spacing_y: float = 2.0,
    comp_depth: float = 5.0,
) -> list[CompartmentElement]:
    comp_w, _comp_l = comp_size
    cols = max(1, int((comp_w + spacing_x) / (column_width + spacing_x)))
    col_y = [spacing_y] * cols
    col_x = [spacing_x + i * (column_width + spacing_x) for i in range(cols)]

    elements = []
    for item in items:
        c = col_y.index(min(col_y))
        w, l = item.get("size", (column_width, column_width))
        shape = item.get("shape", ElementShape.RECT)
        depth = item.get("depth", 4.0)
        svg = item.get("svg")
        rotation = item.get("rotation", 0.0)

        # Calculate rotated footprint size
        fw, fl = (l, w) if abs(rotation) == 90 else (w, l)

        cx = col_x[c] + fw / 2
        cy = col_y[c] + fl / 2

        pull_out = item.get("pull_out", True)
        pull_out_width = item.get("pull_out_width")

        has_custom_scoop = False
        if depth == 2.0:
            pull_out = False
            has_custom_scoop = True

        elements.append(
            centered(
                svg,
                (cx, cy),
                (w, l),
                shape=shape,
                rotation=rotation,
                depth=depth,
                pull_out=pull_out,
                pull_out_width=pull_out_width,
            )
        )
        if has_custom_scoop:
            # Cut a vertical cylinder notch with a rounded floor transition on the
            # bottom edge of the pocket pointing towards the interior to avoid outer wall intrusion.
            elements.append(
                centered(
                    None,
                    (cx, cy - l / 2),
                    (12.0, 12.0),
                    shape=ElementShape.CIRCLE,
                    depth=depth,
                    bottom_rounding=min(0.8, depth * 0.4),
                    pull_out=False,
                )
            )
        insert_svg = item.get("insert_svg", svg)
        insert_text = item.get("text")
        if "insert_color" in item and (
            insert_svg is not None or insert_text is not None
        ):
            if item.get("is_winter"):
                # Offset the stamp center to the circular cap (unrotated x=1.5, y=0)
                rad = math.radians(rotation)
                ox = 1.5 * math.cos(rad)
                oy = 1.5 * math.sin(rad)
                rot = rotation - 90.0
                stamp_size = (4.0, 4.0)
            else:
                ox = 0.0
                oy = 0.0
                rot = rotation
                stamp_size = (w * 0.35, l * 0.35)

            if insert_text is not None:
                stamp_shape = ElementShape.TEXT
                stamp_content = insert_text
            else:
                stamp_shape = ElementShape.SVG
                stamp_content = insert_svg

            elements.append(
                centered(
                    stamp_content,
                    (cx + ox, cy + oy),
                    stamp_size,
                    shape=stamp_shape,
                    rotation=rot,
                    depth=0.6,
                    z_offset=comp_depth - depth,
                    color=item["insert_color"],
                    pull_out=False,
                )
            )
        col_y[c] += fl + spacing_y
    return elements


# SVG Assets directory path (relative to project root for sandbox compatibility)
SVG_DIR = Path("boxes/root/svg")

# Active build helpers: build_root_project() creates a fresh Project for any
# expansion / subgroup selection; module-level `project` keeps the full default layout.
def summarize_board_storage(expansions: Iterable[str] | None = None) -> RootBoardStatus:
    """Evaluate whether the selected expansions' boards fit inside the main box."""
    exp_keys = tuple(expansions) if expansions is not None else ("base", "riverfolk")
    total_mm = 0.0
    for key in exp_keys:
        spec = _EXPANSION_BY_KEY.get(key)
        if spec is None:
            raise ValueError(f"Unknown Root expansion: '{key}'")
        total_mm += spec.board_thickness_mm

    capacity = ROOT_BOARD_BAY_HEIGHT_MM
    gap = max(0.0, capacity - total_mm)
    overflow = max(0.0, total_mm - capacity)
    if overflow > 1e-6:
        status: Literal["thin_top_gap", "exact_fit", "external_box_required"] = (
            "external_box_required"
        )
        summary = (
            f"Boards total ~{total_mm:g} mm ({overflow:g} mm over the {capacity:g} mm bay): "
            "store all game/map & faction boards in a separate box, freeing the full "
            f"{ROOT_BOX_TOTAL_HEIGHT_MM:g} mm main box height for trays."
        )
    elif gap > 1e-6:
        status = "thin_top_gap"
        summary = (
            f"Boards total ~{total_mm:g} mm inside the {capacity:g} mm bay, leaving a thin "
            f"~{gap:g} mm top space where expansion boards would sit (pad lightly on top or "
            "keep open for future expansion boards)."
        )
    else:
        status = "exact_fit"
        summary = (
            f"Boards fill the {capacity:g} mm bottom bay (~{total_mm:g} / {capacity:g} mm) "
            "flush beneath the 39 mm insert boxes."
        )
    return RootBoardStatus(
        expansions=exp_keys,
        boards_mm=total_mm,
        capacity_mm=capacity,
        top_gap_mm=gap,
        overflow_mm=overflow,
        status=status,
        summary=summary,
    )


def _make_root_project(*, boards_external: bool = False) -> Project:
    board_reserve = 0.0 if boards_external else ROOT_BOARD_BAY_HEIGHT_MM
    return Project(
        "Root",
        game_box_size=(214.0, 278.0, ROOT_BOX_TOTAL_HEIGHT_MM),
        board_thickness=board_reserve,
        clearance_slack=0.0,
        board_on_bottom=not boards_external,
        generate_spacers=True,
        box_defaults={"expandable": False},
    )

from pybosl2.shapes3d.base import CsgSolid


class MultiColorSolid(CsgSolid):
    def color(self, color_val):
        return self

def _measure_logo(solid):
    b = solid.bounds()
    if hasattr(b, "center"):
        cx, cy, cz = (float(b.center[0]), float(b.center[1]), float(b.center[2]))
    else:
        cx, cy, cz = (float(b[0][0]), float(b[0][1]), float(b[0][2]))
    span_x, span_y = (float(b.size[0]), float(b.size[1])) if hasattr(b, "size") else (float(b[1][0]), float(b[1][1]))
    return (cx, cy, cz), (span_x, span_y)

def make_marquis_mmu_logo(w, l, depth):
    from pyboxbuilder.compartments.element import _svg_region
    black_raw = _svg_region(str(SVG_DIR / "marquis_multicolor_black.svg")).linear_extrude(height=depth)
    orange_raw = _svg_region(str(SVG_DIR / "marquis_multicolor_orange.svg")).linear_extrude(height=depth)
    white_raw = _svg_region(str(SVG_DIR / "marquis_multicolor_white.svg")).linear_extrude(height=depth)
    (cx, cy, cz), (span_x, span_y) = _measure_logo(black_raw | orange_raw | white_raw)
    black_centered = black_raw.translate([-cx, -cy, -cz])
    orange_centered = orange_raw.translate([-cx, -cy, -cz])
    white_centered = white_raw.translate([-cx, -cy, -cz])
    orange_non_overlap = (orange_centered - black_centered - white_centered).color("#ea7d27")
    white_non_overlap = (white_centered - black_centered).color("white")
    black_non_overlap = black_centered.color("black")
    logo_solid = black_non_overlap | orange_non_overlap | white_non_overlap
    logo_solid = logo_solid.translate([0.0, 0.0, depth / 2])
    scale_val = min(w / max(float(span_x), 1e-9), l / max(float(span_y), 1e-9))
    logo_scaled = logo_solid.scale([scale_val, scale_val, 1.0])
    return MultiColorSolid(logo_scaled.shape)

def make_lizard_mmu_logo(w, l, depth):
    from pyboxbuilder.compartments.element import _svg_region
    black_raw = _svg_region(str(SVG_DIR / "lizard_multicolor_black.svg")).linear_extrude(height=depth)
    yellow_raw = _svg_region(str(SVG_DIR / "lizard_multicolor_yellow.svg")).linear_extrude(height=depth)
    (cx, cy, cz), (span_x, span_y) = _measure_logo(black_raw | yellow_raw)
    black_centered = black_raw.translate([-cx, -cy, -cz])
    yellow_centered = yellow_raw.translate([-cx, -cy, -cz])
    yellow_non_overlap = (yellow_centered - black_centered).color("#f2e45f")
    black_non_overlap = black_centered.color("black")
    logo_solid = black_non_overlap | yellow_non_overlap
    logo_solid = logo_solid.translate([0.0, 0.0, depth / 2])
    scale_val = min(w / max(float(span_x), 1e-9), l / max(float(span_y), 1e-9))
    logo_scaled = logo_solid.scale([scale_val, scale_val, 1.0])
    return MultiColorSolid(logo_scaled.shape)

def make_riverfolk_mmu_logo(w, l, depth):
    from pyboxbuilder.compartments.element import _svg_region
    black_raw = _svg_region(str(SVG_DIR / "riverfolk_multicolor_black.svg")).linear_extrude(height=depth)
    green_raw = _svg_region(str(SVG_DIR / "riverfolk_multicolor_green.svg")).linear_extrude(height=depth)
    white_raw = _svg_region(str(SVG_DIR / "riverfolk_multicolor_white.svg")).linear_extrude(height=depth)
    (cx, cy, cz), (span_x, span_y) = _measure_logo(black_raw | green_raw | white_raw)
    black_centered = black_raw.translate([-cx, -cy, -cz])
    green_centered = green_raw.translate([-cx, -cy, -cz])
    white_centered = white_raw.translate([-cx, -cy, -cz])
    green_non_overlap = (green_centered - black_centered - white_centered).color("#4db6af")
    white_non_overlap = (white_centered - black_centered).color("white")
    black_non_overlap = black_centered.color("black")
    logo_solid = black_non_overlap | green_non_overlap | white_non_overlap
    logo_solid = logo_solid.translate([0.0, 0.0, depth / 2])
    scale_val = min(w / max(float(span_x), 1e-9), l / max(float(span_y), 1e-9))
    logo_scaled = logo_solid.scale([scale_val, scale_val, 1.0])
    return MultiColorSolid(logo_scaled.shape)

def make_erie_mmu_logo(w, l, depth):
    from pyboxbuilder.compartments.element import _svg_region
    black_raw = _svg_region(str(SVG_DIR / "erie_multicolor_black.svg")).linear_extrude(height=depth)
    blue_raw = _svg_region(str(SVG_DIR / "erie_multicolor_blue.svg")).linear_extrude(height=depth)
    lightblue_raw = _svg_region(str(SVG_DIR / "erie_multicolor_lightblue.svg")).linear_extrude(height=depth)
    white_raw = _svg_region(str(SVG_DIR / "erie_multicolor_white.svg")).linear_extrude(height=depth)
    (cx, cy, cz), (span_x, span_y) = _measure_logo(black_raw | blue_raw | lightblue_raw | white_raw)
    black_centered = black_raw.translate([-cx, -cy, -cz])
    blue_centered = blue_raw.translate([-cx, -cy, -cz])
    lightblue_centered = lightblue_raw.translate([-cx, -cy, -cz])
    white_centered = white_raw.translate([-cx, -cy, -cz])
    blue_non_overlap = (blue_centered - black_centered - lightblue_centered - white_centered).color("#5690c7")
    lightblue_non_overlap = (lightblue_centered - black_centered - white_centered).color("#8ab3d5")
    white_non_overlap = (white_centered - black_centered).color("white")
    black_non_overlap = black_centered.color("black")
    logo_solid = black_non_overlap | blue_non_overlap | lightblue_non_overlap | white_non_overlap
    logo_solid = logo_solid.translate([0.0, 0.0, depth / 2])
    scale_val = min(w / max(float(span_x), 1e-9), l / max(float(span_y), 1e-9))
    logo_scaled = logo_solid.scale([scale_val, scale_val, 1.0])
    return MultiColorSolid(logo_scaled.shape)

def make_vagabond_mmu_logo(w, l, depth):
    from pyboxbuilder.compartments.element import _svg_region
    black_raw = _svg_region(str(SVG_DIR / "vagabond_multicolor_black.svg")).linear_extrude(height=depth)
    grey_raw = _svg_region(str(SVG_DIR / "vagabond_multicolor_grey.svg")).linear_extrude(height=depth)
    white_raw = _svg_region(str(SVG_DIR / "vagabond_multicolor_white.svg")).linear_extrude(height=depth)
    (cx, cy, cz), (span_x, span_y) = _measure_logo(black_raw | grey_raw | white_raw)
    black_centered = black_raw.translate([-cx, -cy, -cz])
    grey_centered = grey_raw.translate([-cx, -cy, -cz])
    white_centered = white_raw.translate([-cx, -cy, -cz])
    grey_non_overlap = (grey_centered - black_centered - white_centered).color("#9b9b9b")
    white_non_overlap = (white_centered - black_centered).color("white")
    black_non_overlap = black_centered.color("black")
    logo_solid = black_non_overlap | grey_non_overlap | white_non_overlap
    logo_solid = logo_solid.translate([0.0, 0.0, depth / 2])
    scale_val = min(w / max(float(span_x), 1e-9), l / max(float(span_y), 1e-9))
    logo_scaled = logo_solid.scale([scale_val, scale_val, 1.0])
    return MultiColorSolid(logo_scaled.shape)

def make_alliance_mmu_logo(w, l, depth):
    from pyboxbuilder.compartments.element import _svg_region
    black_raw = _svg_region(str(SVG_DIR / "alliance_multicolor_black.svg")).linear_extrude(height=depth)
    green_raw = _svg_region(str(SVG_DIR / "alliance_multicolor_green.svg")).linear_extrude(height=depth)
    white_raw = _svg_region(str(SVG_DIR / "alliance_multicolor_white.svg")).linear_extrude(height=depth)
    (cx, cy, cz), (span_x, span_y) = _measure_logo(black_raw | green_raw | white_raw)
    black_centered = black_raw.translate([-cx, -cy, -cz])
    green_centered = green_raw.translate([-cx, -cy, -cz])
    white_centered = white_raw.translate([-cx, -cy, -cz])
    green_non_overlap = (green_centered - black_centered - white_centered).color("#1da85e")
    white_non_overlap = (white_centered - black_centered).color("white")
    black_non_overlap = black_centered.color("black")
    logo_solid = black_non_overlap | green_non_overlap | white_non_overlap
    logo_solid = logo_solid.translate([0.0, 0.0, depth / 2])
    scale_val = min(w / max(float(span_x), 1e-9), l / max(float(span_y), 1e-9))
    logo_scaled = logo_solid.scale([scale_val, scale_val, 1.0])
    return MultiColorSolid(logo_scaled.shape)

# Base Lid configuration using SQUARE pattern matching original SCAD lids
LID_BASE = LidBuilder(pattern=PatternBuilder(PatternType.DENSE_HEX))

LID_MARQUIS = replace(
    LID_BASE, logo=make_marquis_mmu_logo, logo_color=Color("#ea7d27")
)
LID_ERIE = replace(LID_BASE, logo=make_erie_mmu_logo, logo_color=Color("#5690c7"))
LID_ALLIANCE = replace(
    LID_BASE, logo=make_alliance_mmu_logo, logo_color=Color("#1da85e")
)

LID_LIZARD = replace(
    LID_BASE, logo=make_lizard_mmu_logo, logo_color=Color("#f5d033")
)
LID_RIVERFOLK = replace(
    LID_BASE, logo=make_riverfolk_mmu_logo, logo_color=Color("#4db6af")
)
LID_VAGABOND = replace(
    LID_BASE, logo=make_vagabond_mmu_logo, logo_color=Color("black")
)

# ── Boxes ─────────────────────────────────────────────────────────────────

def _populate_root_boxes(project: Project) -> None:
    """Register every implemented Root sub-box on *project*."""

    # Card Boxes
    card_size = (79.875, 98.5, 39.0)
    project.card_box(
        "BaseCardBox",
        card_size=(74.875, 93.5),
        size=card_size,
        lid=replace(LID_BASE, text="Shared"),
    )

    card_erie_size = (79.875, 98.5, 8.6)
    project.card_box(
        "ErieCardBox",
        card_size=(74.875, 93.5),
        size=card_erie_size,
        lid=LID_ERIE,
    )

    card_vagabond_size = (79.875, 98.5, 19.4)
    project.card_box(
        "VagabondCardBox",
        card_size=(74.875, 93.5),
        size=card_vagabond_size,
        lid=LID_VAGABOND,
        color=Color("green"),
    )

    card_overview_size = (79.875, 98.5, 11.0)
    project.card_box(
        "OverviewCardBox",
        card_size=(74.875, 93.5),
        size=card_overview_size,
        lid=LID_BASE.titled("Overview"),
    )

    # Stacked Item Boxes
    item_box_length = 103.5
    item_comp_size = (49.25, 99.5)

    # ItemsBoxBottom (comp_depth = 6.0)
    project.box(
        BoxType.SLIDING,
        "ItemsBoxBottom",
        size=(53.25, item_box_length, 10.0),
        lid=LID_BASE.titled("Items Bot"),
    ).compartment(
        "Items",
        depth=6.0,
        elements=pack_in_columns(
            items=[
                {"svg": str(SVG_DIR / "torch.svg"), "depth": 4.0, "insert_color": "black"},
                {"svg": str(SVG_DIR / "boot.svg"), "depth": 6.0, "insert_color": "black"},
                {
                    "svg": str(SVG_DIR / "crossbow.svg"),
                    "depth": 4.0,
                    "insert_color": "black",
                },
                {"svg": str(SVG_DIR / "sword.svg"), "depth": 6.0, "insert_color": "black"},
                {"svg": str(SVG_DIR / "teapot.svg"), "depth": 4.0, "insert_color": "black"},
                {"svg": str(SVG_DIR / "ruins.svg"), "depth": 6.0, "insert_color": "black"},
                {"svg": str(SVG_DIR / "ruins.svg"), "depth": 6.0, "insert_color": "black"},
                {"svg": str(SVG_DIR / "ruins.svg"), "depth": 4.0, "insert_color": "black"},
                {"svg": str(SVG_DIR / "coins.svg"), "depth": 2.0, "insert_color": "black"},
                {"svg": str(SVG_DIR / "bag.svg"), "depth": 2.0, "insert_color": "black"},
            ],
            comp_size=item_comp_size,
            column_width=18.5,
            spacing_x=4.08,
            spacing_y=1.16,
            comp_depth=6.0,
        ),
    )

    # ItemsBoxMiddle (comp_depth = 5.0)
    project.box(
        BoxType.SLIDING,
        "ItemsBoxMiddle",
        size=(53.25, item_box_length, 9.0),
        lid=LID_BASE.titled("Items Mid"),
    ).compartment(
        "Items",
        depth=5.0,
        elements=pack_in_columns(
            items=[
                {"svg": str(SVG_DIR / "bag.svg"), "depth": 4.0, "insert_color": "black"},
                {"svg": str(SVG_DIR / "boot.svg"), "depth": 4.0, "insert_color": "black"},
                {"svg": str(SVG_DIR / "sword.svg"), "depth": 4.0, "insert_color": "black"},
                {"svg": str(SVG_DIR / "teapot.svg"), "depth": 4.0, "insert_color": "black"},
                {"svg": str(SVG_DIR / "coins.svg"), "depth": 4.0, "insert_color": "black"},
                {"svg": str(SVG_DIR / "ruins.svg"), "depth": 4.0, "insert_color": "black"},
                {"svg": str(SVG_DIR / "ruins.svg"), "depth": 4.0, "insert_color": "black"},
                {
                    "svg": str(SVG_DIR / "crossbow.svg"),
                    "depth": 2.0,
                    "insert_color": "black",
                },
                {"svg": str(SVG_DIR / "anvil.svg"), "depth": 2.0, "insert_color": "black"},
            ],
            comp_size=item_comp_size,
            column_width=18.5,
            spacing_x=4.08,
            spacing_y=1.16,
            comp_depth=5.0,
        ),
    )

    # ItemsBoxWinter (comp_depth = 5.0)
    project.box(
        BoxType.SLIDING,
        "ItemsBoxWinter",
        size=(53.25, item_box_length, 9.0),
        lid=LID_BASE.titled("Winter"),
    ).compartment(
        "WinterTokens",
        depth=5.0,
        elements=pack_in_columns(
            items=[
                # 2 slots for Fox (4 tokens)
                {
                    "svg": str(SVG_DIR / "winter_token.svg"),
                    "insert_svg": str(SVG_DIR / "fox.svg"),
                    "shape": ElementShape.SVG,
                    "depth": 5.0,
                    "size": (15.5, 29.5),
                    "rotation": 90,
                    "insert_color": "black",
                    "pull_out_width": 12.0,  # Smaller finger scoop to avoid wall intrusion
                    "is_winter": True,
                },
                {
                    "svg": str(SVG_DIR / "winter_token.svg"),
                    "insert_svg": str(SVG_DIR / "fox.svg"),
                    "shape": ElementShape.SVG,
                    "depth": 5.0,
                    "size": (15.5, 29.5),
                    "rotation": 90,
                    "insert_color": "black",
                    "is_winter": True,
                },
                # 2 slots for Rabbit (4 tokens)
                {
                    "svg": str(SVG_DIR / "winter_token.svg"),
                    "insert_svg": str(SVG_DIR / "rabbit.svg"),
                    "shape": ElementShape.SVG,
                    "depth": 5.0,
                    "size": (15.5, 29.5),
                    "rotation": 90,
                    "insert_color": "black",
                    "is_winter": True,
                },
                {
                    "svg": str(SVG_DIR / "winter_token.svg"),
                    "insert_svg": str(SVG_DIR / "rabbit.svg"),
                    "shape": ElementShape.SVG,
                    "depth": 5.0,
                    "size": (15.5, 29.5),
                    "rotation": 90,
                    "insert_color": "black",
                    "is_winter": True,
                },
                # 2 slots for Mouse (4 tokens)
                {
                    "svg": str(SVG_DIR / "winter_token.svg"),
                    "insert_svg": str(SVG_DIR / "mouse.svg"),
                    "shape": ElementShape.SVG,
                    "depth": 5.0,
                    "size": (15.5, 29.5),
                    "rotation": 90,
                    "insert_color": "black",
                    "is_winter": True,
                },
                {
                    "svg": str(SVG_DIR / "winter_token.svg"),
                    "insert_svg": str(SVG_DIR / "mouse.svg"),
                    "shape": ElementShape.SVG,
                    "depth": 5.0,
                    "size": (15.5, 29.5),
                    "rotation": 90,
                    "insert_color": "black",
                    "pull_out_width": 12.0,  # Smaller finger scoop to avoid wall intrusion
                    "is_winter": True,
                },
            ],
            comp_size=item_comp_size,
            column_width=29.5,
            spacing_x=7.875,
            spacing_y=1.0,
            comp_depth=5.0,
        ),
    )

    # ItemsBoxExtras (comp_depth = 7.0)
    project.box(
        BoxType.SLIDING,
        "ItemsBoxExtras",
        size=(53.25, item_box_length, 11.0),
        lid=LID_BASE.titled("Extras"),
    ).compartment(
        "Extras",
        depth=7.0,
        elements=pack_in_columns(
            items=[
                {
                    "shape": ElementShape.CIRCLE,
                    "size": (21.0, 21.0),
                    "depth": 5.0,
                    "text": "a/b",
                    "insert_color": "black",
                },
                {
                    "shape": ElementShape.CIRCLE,
                    "size": (21.0, 21.0),
                    "depth": 5.0,
                    "text": "c/d",
                    "insert_color": "black",
                },
                {
                    "shape": ElementShape.CIRCLE,
                    "size": (21.0, 21.0),
                    "depth": 5.0,
                    "text": "e/f",
                    "insert_color": "black",
                },
                {
                    "shape": ElementShape.RECT,
                    "size": (18.5, 18.5),
                    "depth": 5.0,
                    "text": "g/h",
                    "insert_color": "black",
                },
                {
                    "shape": ElementShape.RECT,
                    "size": (18.5, 18.5),
                    "depth": 5.0,
                    "text": "i/j",
                    "insert_color": "black",
                },
                {
                    "shape": ElementShape.RECT,
                    "size": (18.5, 18.5),
                    "depth": 5.0,
                    "text": "k/l",
                    "insert_color": "black",
                },
                {
                    "shape": ElementShape.RECT,
                    "size": (18.5, 18.5),
                    "depth": 5.0,
                    "text": "m/n",
                    "insert_color": "black",
                },
                {
                    "shape": ElementShape.RECT,
                    "size": (18.5, 18.5),
                    "depth": 5.0,
                    "text": "o/p",
                    "insert_color": "black",
                },
            ],
            comp_size=item_comp_size,
            column_width=21.0,
            spacing_x=2.41,
            spacing_y=3.3,
            comp_depth=7.0,
        ),
    )

    def _pack_pockets(
        box_size: tuple[float, float, float],
        items: list[Any],
        *,
        min_spacing: float = 1.5,
        allow_rotate: bool = False,
    ) -> tuple[CompartmentElement, ...]:
        return pack_into_compartment(
            items,
            (box_size[0] - 4.0, box_size[1] - 4.0),
            spacing=2.0,
            min_spacing=min_spacing,
            allow_rotate=allow_rotate,
        )

    def _pocket_with_inlay(
        size: tuple[float, float],
        *,
        depth: float,
        comp_depth: float,
        inlay: str | None = None,
        inlay_size: tuple[float, float] = (12.0, 12.0),
        shape: ElementShape = ElementShape.RECT,
        inlay_shape: ElementShape = ElementShape.SVG,
        inlay_z_offset: float | None = None,
        pull_out_width: float | None = None,
        pull_out_depth: float | None = None,
    ) -> tuple[CompartmentElement, ...]:
        pocket = centered(
            None,
            (0.0, 0.0),
            size,
            shape=shape,
            depth=depth,
            pull_out=True,
            pull_out_width=pull_out_width,
            pull_out_depth=pull_out_depth,
        )
        if inlay is None:
            return (pocket,)
        stamp = centered(
            inlay,
            (0.0, 0.0),
            inlay_size,
            shape=inlay_shape,
            depth=0.6,
            z_offset=(comp_depth - depth) if inlay_z_offset is None else inlay_z_offset,
            color="black",
            pull_out=False,
        )
        return (pocket, stamp)

    # Marquis Box Bottom
    marquis_bottom_size = (106.5, 59.833, 24.5)
    project.box(
        BoxType.CAP,
        "MarquisBoxBottom",
        size=marquis_bottom_size,
        lid=LID_MARQUIS,
        color=Color("orange"),
    ).compartment(
        "Warriors",
        elements=_pack_pockets(
            marquis_bottom_size,
            [
                # 3 horizontal channels for 25 cat meeples (8 + 8 + 9)
                _pocket_with_inlay(
                    (width, 14.5),
                    depth=18.0,
                    comp_depth=21.9,
                    inlay=str(SVG_DIR / "marquis_warrior.svg"),
                    inlay_z_offset=3.9,
                    pull_out_width=p_w,
                    pull_out_depth=9.0,
                )
                for width, p_w in ((73.0, 65.0), (73.0, 65.0), (82.0, 75.0))
            ],
        ),
    )

    # Marquis Box Top
    marquis_top_size = (106.5, 59.833, 14.5)
    marquis_top_comp_depth = 12.9
    project.box(
        BoxType.SLIDING,
        "MarquisBoxTop",
        size=marquis_top_size,
        lid=LID_MARQUIS,
        color=Color("orange"),
    ).compartment(
        "WoodAndBuildings",
        elements=_pack_pockets(
            marquis_top_size,
            [
                *[
                    _pocket_with_inlay(
                        (15.0, 15.0),
                        depth=8.0,
                        comp_depth=marquis_top_comp_depth,
                        inlay=str(SVG_DIR / "log.svg"),
                        inlay_size=(15.0 * 0.35, 15.0 * 0.35),
                        shape=ElementShape.CIRCLE,
                    )
                    for _ in range(2)
                ],
                _pocket_with_inlay(
                    (18.5, 18.5),
                    depth=2.0,
                    comp_depth=marquis_top_comp_depth,
                    inlay=str(SVG_DIR / "keep.svg"),
                    inlay_size=(18.5 * 0.35, 18.5 * 0.35),
                    shape=ElementShape.CIRCLE,
                ),
                *[
                    _pocket_with_inlay(
                        (18.5, 18.5),
                        depth=6.0,
                        comp_depth=marquis_top_comp_depth,
                        inlay=str(SVG_DIR / "handshake.svg"),
                        inlay_size=(18.5 * 0.35, 18.5 * 0.35),
                    )
                    for _ in range(2)
                ],
                *[
                    _pocket_with_inlay(
                        (18.5, 18.5),
                        depth=6.0,
                        comp_depth=marquis_top_comp_depth,
                        inlay=str(SVG_DIR / "anvil.svg"),
                        inlay_size=(18.5 * 0.35, 18.5 * 0.35),
                    )
                    for _ in range(2)
                ],
                _pocket_with_inlay(
                    (18.5, 18.5),
                    depth=2.0,
                    comp_depth=marquis_top_comp_depth,
                    inlay=str(SVG_DIR / "laurel_wreath.svg"),
                    inlay_size=(18.5 * 0.35, 18.5 * 0.35),
                ),
                *[
                    _pocket_with_inlay(
                        (18.5, 18.5),
                        depth=6.0,
                        comp_depth=marquis_top_comp_depth,
                        inlay=str(SVG_DIR / "saw.svg"),
                        inlay_size=(18.5 * 0.35, 18.5 * 0.35),
                    )
                    for _ in range(2)
                ],
            ],
        ),
    )

    # Erie Box Bottom
    erie_bottom_size = (106.5, 59.833, 24.5)
    project.box(
        BoxType.CAP,
        "ErieBoxBottom",
        size=erie_bottom_size,
        lid=LID_ERIE,
        color=Color("blue"),
    ).compartment(
        "Warriors",
        elements=_pack_pockets(
            erie_bottom_size,
            [
                # 2 horizontal channels for 20 bird meeples (10 + 10)
                _pocket_with_inlay(
                    (91.0, 21.0),
                    depth=18.0,
                    comp_depth=21.9,
                    inlay=str(SVG_DIR / "erie_warrior.svg"),
                    inlay_z_offset=3.9,
                    pull_out_width=80.0,
                    pull_out_depth=9.0,
                )
                for _ in range(2)
            ],
        ),
    )

    # Erie Box Top
    erie_top_size = (53.25, 59.833, 14.5)
    erie_top_comp_depth = 12.9
    project.box(
        BoxType.SLIDING,
        "ErieBoxTop",
        size=erie_top_size,
        lid=LID_ERIE,
        color=Color("blue"),
    ).compartment(
        "Roosts",
        elements=_pack_pockets(
            erie_top_size,
            [
                *[
                    _pocket_with_inlay(
                        (18.5, 18.5),
                        depth=8.0,
                        comp_depth=erie_top_comp_depth,
                        inlay=str(SVG_DIR / "tree.svg"),
                        inlay_size=(18.5 * 0.35, 18.5 * 0.35),
                    )
                    for _ in range(2)
                ],
                _pocket_with_inlay(
                    (18.5, 18.5),
                    depth=2.0,
                    comp_depth=erie_top_comp_depth,
                    inlay=str(SVG_DIR / "laurel_wreath.svg"),
                    inlay_size=(18.5 * 0.35, 18.5 * 0.35),
                ),
            ],
        ),
    )

    # Alliance Box Bottom
    alliance_bottom_size = (53.25, 59.833, 24.5)
    project.box(
        BoxType.CAP,
        "AllianceBoxBottom",
        size=alliance_bottom_size,
        lid=LID_ALLIANCE,
        color=Color("green"),
    ).compartment(
        "Warriors",
        elements=_pack_pockets(
            alliance_bottom_size,
            [
                # 2 horizontal channels for 10 alliance meeples (5 + 5)
                _pocket_with_inlay(
                    (46.0, 19.5),
                    depth=18.0,
                    comp_depth=20.9,
                    inlay=str(SVG_DIR / "alliance_warrior.svg"),
                    pull_out_width=40.0,
                    pull_out_depth=9.0,
                )
                for _ in range(2)
            ],
        ),
    )

    # Alliance Box Top (4 pockets: Score, 3 Bases, 2x5 Sympathy)
    alliance_top_size = (53.25, 59.833, 14.5)
    alliance_top_comp_depth = 14.5 - 1.6 - 2.0  # 10.9mm
    project.box(
        BoxType.SLIDING,
        "AllianceBoxTop",
        size=alliance_top_size,
        lid=LID_ALLIANCE,
        color=Color("green"),
    ).compartment(
        "BasesAndSympathy",
        elements=_pack_pockets(
            alliance_top_size,
            [
                _pocket_with_inlay(
                    (18.5, 18.5),
                    depth=3.0,
                    comp_depth=alliance_top_comp_depth,
                    inlay=str(SVG_DIR / "laurel_wreath.svg"),
                ),
                _pocket_with_inlay(
                    (18.5, 18.5),
                    depth=10.5,
                    comp_depth=alliance_top_comp_depth,
                    inlay=str(SVG_DIR / "fist.svg"),
                    shape=ElementShape.CIRCLE,
                ),
                _pocket_with_inlay(
                    (18.5, 18.5),
                    depth=7.0,
                    comp_depth=alliance_top_comp_depth,
                    inlay=str(SVG_DIR / "camp.svg"),
                ),
                _pocket_with_inlay(
                    (18.5, 18.5),
                    depth=10.5,
                    comp_depth=alliance_top_comp_depth,
                    inlay=str(SVG_DIR / "fist.svg"),
                    shape=ElementShape.CIRCLE,
                ),
            ],
        ),
    )

    # Lizard Box Bottom
    lizard_bottom_size = (106.5, 59.833, 26.5)
    project.box(
        BoxType.CAP,
        "LizardBoxBottom",
        size=lizard_bottom_size,
        lid=LID_LIZARD,
        color=Color("yellow"),
    ).compartment(
        "Warriors",
        elements=_pack_pockets(
            lizard_bottom_size,
            [
                # 5 rows of 5 individual lizard warrior slots (25 total)
                centered(
                    None,
                    (0.0, 0.0),
                    (18.0, 9.0),
                    depth=20.0,
                    pull_out=True,
                    pull_out_depth=10.0,
                )
                for _ in range(25)
            ],
        ),
    )

    # Lizard Box Top
    lizard_top_size = (79.875, 59.833, 12.5)
    lizard_top_comp_depth = 8.9
    project.box(
        BoxType.SLIDING,
        "LizardBoxTop",
        size=lizard_top_size,
        lid=LID_LIZARD,
        color=Color("yellow"),
    ).compartment(
        "Gardens",
        elements=_pack_pockets(
            lizard_top_size,
            [
                *[
                    _pocket_with_inlay(
                        (18.5, 18.5),
                        depth=8.0,
                        comp_depth=lizard_top_comp_depth,
                        inlay=str(SVG_DIR / suit_svg),
                        inlay_size=(10.0, 10.0),
                    )
                    for suit_svg in ("fox.svg", "rabbit.svg", "mouse.svg")
                ],
                _pocket_with_inlay(
                    (18.5, 18.5),
                    depth=3.0,
                    comp_depth=lizard_top_comp_depth,
                    inlay=str(SVG_DIR / "laurel_wreath.svg"),
                ),
                _pocket_with_inlay(
                    (18.5, 18.5),
                    depth=4.0,
                    comp_depth=lizard_top_comp_depth,
                    inlay=str(SVG_DIR / "lizard_faction.svg"),
                    inlay_size=(10.0, 10.0),
                ),
                _pocket_with_inlay(
                    (18.5, 18.5),
                    depth=2.0,
                    comp_depth=lizard_top_comp_depth,
                    inlay=str(SVG_DIR / "outcast.svg"),
                    inlay_size=(10.0, 10.0),
                ),
            ],
        ),
    )

    # Riverfolk Box Bottom
    riverfolk_bottom_size = (53.25, 59.833, 26.5)
    project.box(
        BoxType.CAP,
        "RiverfolkBoxBottom",
        size=riverfolk_bottom_size,
        lid=LID_RIVERFOLK,
        color=Color("teal"),
    ).compartment(
        "Warriors",
        elements=_pack_pockets(
            riverfolk_bottom_size,
            [
                # 3 horizontal channels for 15 otter meeples (5 + 5 + 5)
                _pocket_with_inlay(
                    (46.0, 15.0),
                    depth=18.0,
                    comp_depth=22.9,
                    inlay=str(SVG_DIR / "riverfolk_warrior.svg"),
                    inlay_z_offset=4.9,
                    pull_out_width=40.0,
                    pull_out_depth=9.0,
                )
                for _ in range(3)
            ],
        ),
    )

    # Riverfolk Box Top (7 pockets: Score + 3 Glass Gems + 3 Trade Post suits)
    riverfolk_top_size = (79.875, 59.833, 12.5)
    riverfolk_top_comp_depth = 12.5 - 1.6 - 2.0  # 8.9mm
    project.box(
        BoxType.SLIDING,
        "RiverfolkBoxTop",
        size=riverfolk_top_size,
        lid=LID_RIVERFOLK,
        color=Color("teal"),
    ).compartment(
        "TradePosts",
        elements=_pack_pockets(
            riverfolk_top_size,
            [
                _pocket_with_inlay(
                    (18.5, 18.5),
                    depth=3.0,
                    comp_depth=riverfolk_top_comp_depth,
                    inlay=str(SVG_DIR / "laurel_wreath.svg"),
                ),
                *[
                    _pocket_with_inlay(
                        (17.0, 17.0),
                        depth=8.5,
                        comp_depth=riverfolk_top_comp_depth,
                        inlay=str(SVG_DIR / "gem.svg"),
                        inlay_size=(11.0, 11.0),
                        shape=ElementShape.CIRCLE,
                    )
                    for _ in range(3)
                ],
                *[
                    _pocket_with_inlay(
                        (18.5, 18.5),
                        depth=7.0,
                        comp_depth=riverfolk_top_comp_depth,
                        inlay=str(SVG_DIR / "sign.svg"),
                        shape=ElementShape.CIRCLE,
                    )
                    for _ in range(3)
                ],
            ],
        ),
    )

    # Vagabond Boxes (2 stacked boxes: Base + Riverfolk 2nd Vagabond)
    def _add_vagabond_box(label: str) -> None:
        vagabond_size = (53.25, 59.833, 19.5)
        vagabond_comp_depth = 19.5 - 1.6 - 2.0  # 15.9mm
        elements = _pack_pockets(
            vagabond_size,
            [
                # Vagabond meeple cutout (9mm thick + 1mm clearance)
                centered(
                    str(SVG_DIR / "vagabond_warrior.svg"),
                    (0.0, 0.0),
                    (21.0, 22.0),
                    depth=10.0,
                    pull_out=True,
                ),
                # Score marker well + laurel wreath inlay
                _pocket_with_inlay(
                    (18.5, 18.5),
                    depth=3.0,
                    comp_depth=vagabond_comp_depth,
                    inlay=str(SVG_DIR / "laurel_wreath.svg"),
                ),
                # Relationship marker wells (3 tokens each = 6 per Vagabond)
                *[
                    _pocket_with_inlay(
                        (18.5, 18.5),
                        depth=7.0,
                        comp_depth=vagabond_comp_depth,
                        inlay="Relation",
                        inlay_size=(15.0, 15.0),
                        inlay_shape=ElementShape.TEXT,
                    )
                    for _ in range(2)
                ],
            ],
        )
        project.box(
            BoxType.SLIDING,
            label,
            size=vagabond_size,
            lid=LID_VAGABOND,
            color=Color("green"),
        ).compartment("ItemsAndScore", elements=elements)

    _add_vagabond_box("VagabondBox")
    _add_vagabond_box("VagabondBox2")

    # Dice Box (placed behind the Items stack in the right column)
    dice_box_size = (53.25, 59.833, 39.0)
    project.box(
        BoxType.SLIDING,
        "DiceBox",
        size=dice_box_size,
        lid=LID_BASE.titled("Dice"),
    ).compartment(
        "Dice",
        elements=_pack_pockets(
            dice_box_size,
            [
                centered(
                    None,
                    (0.0, 0.0),
                    (22.0, 22.0),
                    shape=ElementShape.CIRCLE,
                    depth=22.0,
                    pull_out=True,
                )
                for _ in range(2)
            ],
        ),
    )


_STACK_GROUPS: tuple[tuple[str, ...], ...] = (
    ("ErieCardBox", "VagabondCardBox", "OverviewCardBox"),
    ("ItemsBoxBottom", "ItemsBoxMiddle", "ItemsBoxWinter", "ItemsBoxExtras"),
    ("VagabondBox", "VagabondBox2"),
)


def build_root_project(
    expansions: Iterable[str] | None = None,
    *,
    subgroups: Iterable[str] | None = None,
    boards_external: bool = False,
) -> Project:
    """Build a Root Project containing only the selected expansions or subgroups.

    Defaults to all implemented expansions (``("base", "riverfolk")``).
    Set ``boards_external=True`` when moving all game/faction boards out to a
    separate board box (e.g., for expansions beyond Riverfolk), freeing the
    entire 67 mm height.
    """
    active_subgroups = resolve_root_subgroups(expansions, subgroups=subgroups)
    root_project = _make_root_project(boards_external=boards_external)
    _populate_root_boxes(root_project)

    unknown_boxes = {
        b.label for b in root_project._manifest.boxes if b.label not in _BOX_META_BY_LABEL
    }
    if unknown_boxes:
        raise ValueError(f"Unclassified Root boxes: {sorted(unknown_boxes)}")

    root_project._manifest.boxes[:] = [
        b
        for b in root_project._manifest.boxes
        if _BOX_META_BY_LABEL[b.label].subgroup in active_subgroups
    ]
    present = {b.label for b in root_project._manifest.boxes}
    for group in _STACK_GROUPS:
        active_stack = [label for label in group if label in present]
        if len(active_stack) >= 2:
            root_project.stack_order(*active_stack, mode=StackableMode.PYRAMIDS)

    return root_project


_BOX_TYPE_LABELS: dict[BoxType, str] = {
    BoxType.SLIDING: "Sliding Lid",
    BoxType.CAP: "Cap Lid",
    BoxType.NO_LID: "No Lid",
}

ROOT_CATEGORY_LABELS: dict[RootBoxCategory, tuple[str, str]] = {
    RootBoxCategory.CARDS: ("Card Boxes", "Sleeved card storage boxes"),
    RootBoxCategory.FACTIONS: ("Faction Boxes", "Faction warrior, building & token trays"),
    RootBoxCategory.ITEMS_AND_DICE: (
        "Items & Dice Boxes",
        "Shared Vagabond items, clearing markers & dice",
    ),
    RootBoxCategory.SPACERS: ("Spacer Trays", "Filler trays for unoccupied box space"),
}

ROOT_PRESETS: tuple[dict[str, Any], ...] = (
    {
        "key": "base_only",
        "name": "Base Game Only (No Expansions)",
        "description": (
            "16 core boxes (4 base factions, cards, items, dice) + Base-only spacer trays"
        ),
        "subgroups": list(ROOT_EXPANSIONS[0].subgroups),
        "spacerPresetKey": "base",
    },
    {
        "key": "base_riverfolk",
        "name": "Base + Riverfolk Expansion (Current Layout)",
        "description": (
            "All 21 boxes including Lizard Cult, Riverfolk Company & 2nd Vagabond + Full spacers"
        ),
        "subgroups": [
            sg for exp in ROOT_EXPANSIONS if exp.status == "available" for sg in exp.subgroups
        ],
        "spacerPresetKey": "base+riverfolk",
    },
)


def _fmt_dims(dims: tuple[float, float, float] | None) -> str:
    if dims is None:
        return "\u2014"
    return f"{dims[0]:g} \u00d7 {dims[1]:g} \u00d7 {dims[2]:g} mm"


def _fmt_pos(pos: tuple[float, float, float] | None) -> str:
    if pos is None:
        return "(0, 0, 0)"
    return f"({pos[0]:g}, {pos[1]:g}, {pos[2]:g})"


def _spacer_geom_key(sp: Any) -> str:
    """Stable short geometry signature for deduplicating identical variant spacer STLs."""
    import hashlib

    pos = tuple(round(float(v), 2) for v in (sp.position or (0.0, 0.0, 0.0)))
    size = tuple(round(float(v), 2) for v in (sp.size or (0.0, 0.0, 0.0)))
    raw_path = getattr(sp, "path", None)
    path_key = tuple((round(float(x), 2), round(float(y), 2)) for x, y in raw_path) if raw_path else None
    payload = repr((pos, size, path_key)).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:12]


def build_doc_selector(
    *,
    game_slug: str,
    proj: Project,
    build: Any,
    out_stl_dir: Path,
    part_uris: dict[tuple[str, str], str],
    part_filenames: dict[tuple[str, str], str],
    body_pieces: dict[str, Any],
    write_colored_stl_fn: Any,
) -> dict[str, Any]:
    """Generate exact variant spacer STLs for every Riverfolk subset and return selector metadata."""
    import hashlib
    import itertools
    import shutil

    # Clean up legacy un-deduplicated base_spacers dir if present.
    legacy_base_dir = out_stl_dir / "base_spacers"
    if legacy_base_dir.exists():
        shutil.rmtree(legacy_base_dir)

    variant_dir = out_stl_dir / "variant_spacers"
    variant_dir.mkdir(parents=True, exist_ok=True)

    full_spacers = [p for p in build.pieces if p.kind == "spacer"]
    full_spacer_entries = []
    for sp in full_spacers:
        fname = part_filenames.get((sp.label, "spacer"), f"{sp.label}.stl")
        uri = part_uris.get((sp.label, "spacer"))
        if uri is None:
            continue
        full_spacer_entries.append({
            "label": sp.label,
            "dimensions": _fmt_dims(sp.size),
            "position": _fmt_pos(sp.position),
            "files": [{"uri": uri, "filename": fname, "kind": "spacer"}],
        })

    base_sgs = list(ROOT_EXPANSIONS[0].subgroups)
    rf_sgs = sorted(ROOT_EXPANSIONS[1].subgroups)

    spacer_sets: dict[str, list[dict[str, Any]]] = {"base+riverfolk": full_spacer_entries}
    keep_variant_files: set[str] = set()

    for r in range(len(rf_sgs)):
        for combo in itertools.combinations(rf_sgs, r):
            combo_key = "+".join(["base", *combo])
            sub_proj = build_root_project(subgroups=[*base_sgs, *combo])
            packing = sub_proj._compiler.resolve_final_layout(sub_proj._manifest)
            sp_placements = sub_proj._compiler.spacer_placements(sub_proj._manifest, packing)

            missing_labels: set[str] = set()
            geom_hashes: dict[str, str] = {}
            for sp in sp_placements:
                ghash = _spacer_geom_key(sp)
                vname = f"spacer_{ghash}.stl"
                geom_hashes[sp.label] = ghash
                keep_variant_files.add(vname)
                vpath = variant_dir / vname
                if not (vpath.is_file() and vpath.stat().st_size > 84):
                    missing_labels.add(sp.label)

            if missing_labels:
                preview_list = sub_proj.preview_pieces(show_lids=True)
                grouped: dict[str, list[tuple[Any, Any]]] = {}
                for piece in preview_list:
                    if piece.kind == "spacer" and piece.label in missing_labels:
                        grouped.setdefault(piece.label, []).append((piece.solid, piece.color))
                for sp_label, solids in grouped.items():
                    vname = f"spacer_{geom_hashes[sp_label]}.stl"
                    write_colored_stl_fn(variant_dir / vname, solids)

            entries: list[dict[str, Any]] = []
            for sp in sp_placements:
                vname = f"spacer_{geom_hashes[sp.label]}.stl"
                vpath = variant_dir / vname
                digest = hashlib.sha256(vpath.read_bytes()).hexdigest()[:8] if vpath.is_file() else "0"
                entries.append({
                    "label": sp.label,
                    "dimensions": _fmt_dims(sp.size),
                    "position": _fmt_pos(sp.position),
                    "files": [
                        {
                            "uri": f"../_stl/boxes/{game_slug}/variant_spacers/{vname}?v={digest}",
                            "filename": f"{sp.label}.stl",
                            "kind": "spacer",
                        }
                    ],
                })
            spacer_sets[combo_key] = entries

    for existing in variant_dir.glob("spacer_*.stl"):
        if existing.name not in keep_variant_files:
            existing.unlink()

    box_entries = []
    for b in proj.boxes:
        meta = _BOX_META_BY_LABEL[b.label]
        bp = body_pieces.get(b.label)
        dims = _fmt_dims(bp.size if bp else b.final_size)
        pos = _fmt_pos(bp.position if bp else b.position)
        files = []
        for kind in ("body", "lid"):
            uri = part_uris.get((b.label, kind))
            fname = part_filenames.get((b.label, kind), f"{b.label}_{kind}.stl")
            if uri is not None:
                files.append({"uri": uri, "filename": fname, "kind": kind})
        box_entries.append({
            "label": b.label,
            "anchor": f"box-{game_slug}-{b.label.lower()}",
            "expansion": meta.expansion,
            "subgroup": meta.subgroup,
            "category": meta.category.value,
            "categoryName": ROOT_CATEGORY_LABELS[meta.category][0],
            "boxType": b.box_type.name,
            "boxTypeLabel": _BOX_TYPE_LABELS.get(b.box_type, f"BoxType.{b.box_type.name}"),
            "dimensions": dims,
            "position": pos,
            "compartments": len(b.compartments),
            "description": meta.description,
            "files": files,
        })

    return {
        "projectName": proj.name,
        "defaultPreset": "base_riverfolk",
        "boardStorage": {
            "capacityMm": ROOT_BOARD_BAY_HEIGHT_MM,
            "totalBoxHeightMm": ROOT_BOX_TOTAL_HEIGHT_MM,
            "thinTopSpaceHint": (
                "Base Game boards (~22 mm) leave a thin ~6 mm space at the top where "
                "Riverfolk's 2 faction boards and rules would go. Place a thin ~6 mm "
                "foam/cardboard pad on top of the trays to keep lids snug, or leave "
                "open to fit Riverfolk boards later."
            ),
            "exactFitHint": (
                "Base + Riverfolk boards (~28 mm) fill the 28 mm bottom bay flush "
                "beneath the 39 mm insert trays."
            ),
            "externalBoxHint": (
                "Expansions beyond Riverfolk exceed the 28 mm board bay in this box: "
                "move all game/map and faction boards into a separate dedicated board box, "
                "freeing the full 67 mm height of the Base box for expansion insert trays."
            ),
        },
        "presets": list(ROOT_PRESETS),
        "expansions": [
            {
                "key": spec.key,
                "name": spec.name,
                "status": spec.status,
                "required": spec.required,
                "description": spec.description,
                "subgroups": list(spec.subgroups),
                "boardThicknessMm": spec.board_thickness_mm,
                "boardsSummary": spec.boards_summary,
                "notes": spec.notes,
            }
            for spec in ROOT_EXPANSIONS
        ],
        "subgroups": [
            {
                "key": sg.key,
                "name": sg.name,
                "expansion": sg.expansion,
                "description": sg.description,
            }
            for sg in ROOT_SUBGROUPS
        ],
        "categories": [
            {
                "key": cat.value,
                "name": ROOT_CATEGORY_LABELS[cat][0],
                "description": ROOT_CATEGORY_LABELS[cat][1],
            }
            for cat in RootBoxCategory
        ],
        "boxes": box_entries,
        "spacerSets": spacer_sets,
    }


project = build_root_project()

if __name__ == "__main__":
    run(project, show_lids=False, remove_layers=1)
