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


@dataclass(frozen=True)
class RootExpansionSpec:
    """Metadata describing a Root game module/expansion (implemented or planned)."""

    key: str
    name: str
    status: Literal["available", "planned"]
    description: str
    required: bool = False
    subgroups: tuple[str, ...] = ()
    notes: str = ""


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
    ),
    RootExpansionSpec(
        key="underworld",
        name="The Underworld Expansion",
        status="planned",
        description="Underground Duchy & Corvid Conspiracy factions, landmarks, and extra maps.",
        subgroups=("underground_duchy", "corvid_conspiracy"),
        notes="Warrior SVGs (duchy_warrior.svg, corvid_warrior.svg) exist in boxes/root/svg/.",
    ),
    RootExpansionSpec(
        key="marauder",
        name="The Marauder Expansion",
        status="planned",
        description="Lord of the Hundreds & Keepers in Iron factions, advance setup, and hirelings.",
        subgroups=("lord_of_the_hundreds", "keepers_in_iron"),
        notes="Warrior SVGs (hundreds_warrior.svg, keepers_warrior.svg) exist in boxes/root/svg/.",
    ),
    RootExpansionSpec(
        key="exiles_and_partisans",
        name="Exiles & Partisans Deck",
        status="planned",
        description="Alternative 54-card shared deck storage.",
    ),
    RootExpansionSpec(
        key="hirelings_landmarks",
        name="Hirelings & Landmarks",
        status="planned",
        description="Modular trays for Hirelings and Landmarks packs.",
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
            # Cut a vertical cylinder notch on the bottom edge of the pocket
            # pointing towards the interior (Row 3) to avoid outer wall intrusion
            elements.append(
                centered(
                    None,
                    (cx, cy - l / 2),
                    (12.0, 12.0),
                    shape=ElementShape.CIRCLE,
                    depth=depth,
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
def _make_root_project() -> Project:
    return Project(
        "Root",
        game_box_size=(214.0, 278.0, 67.0),
        board_thickness=28.0,
        board_on_bottom=True,
        generate_spacers=True,
        box_defaults={"no_rotate": True},
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
        position=(0.0, 0.0, 28.0),
    )

    card_erie_size = (79.875, 98.5, 8.6)
    project.card_box(
        "ErieCardBox",
        card_size=(74.875, 93.5),
        size=card_erie_size,
        lid=LID_ERIE,
        position=(79.875, 0.0, 28.0),
    )

    card_vagabond_size = (79.875, 98.5, 19.4)
    project.card_box(
        "VagabondCardBox",
        card_size=(74.875, 93.5),
        size=card_vagabond_size,
        lid=LID_VAGABOND,
        color=Color("green"),
        position=(79.875, 0.0, 28.0 + 8.6),
    )

    card_overview_size = (79.875, 98.5, 11.0)
    project.card_box(
        "OverviewCardBox",
        card_size=(74.875, 93.5),
        size=card_overview_size,
        lid=LID_BASE.titled("Overview"),
        position=(79.875, 0.0, 28.0 + 8.6 + 19.4),
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
        position=(159.75, 0.0, 28.0),
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
        position=(159.75, 0.0, 28.0 + 10.0),
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
        position=(159.75, 0.0, 28.0 + 10.0 + 9.0),
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
        position=(159.75, 0.0, 28.0 + 10.0 + 9.0 + 9.0),
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

    # Marquis Box Bottom
    marquis_bottom_size = (106.5, 59.833, 24.5)
    project.box(
        BoxType.CAP,
        "MarquisBoxBottom",
        size=marquis_bottom_size,
        lid=LID_MARQUIS,
        color=Color("orange"),
        position=(0.0, 98.5, 28.0),
    ).compartment(
        "Warriors",
        elements=[
            # 3 horizontal channels for 25 cat meeples (8 + 8 + 9) with wide divider walls and long finger pulls
            centered(
                None,
                (51.25, 9.5),
                (73.0, 14.5),
                depth=18.0,
                pull_out=True,
                pull_out_width=65.0,
                pull_out_depth=9.0,
            ),
            centered(
                None,
                (51.25, 27.9),
                (73.0, 14.5),
                depth=18.0,
                pull_out=True,
                pull_out_width=65.0,
                pull_out_depth=9.0,
            ),
            centered(
                None,
                (51.25, 46.3),
                (82.0, 14.5),
                depth=18.0,
                pull_out=True,
                pull_out_width=75.0,
                pull_out_depth=9.0,
            ),
            # Stamps/Inlays at the bottom of the channels
            centered(
                str(SVG_DIR / "marquis_warrior.svg"),
                (51.25, 9.5),
                (12.0, 12.0),
                depth=0.6,
                z_offset=3.9,
                color="black",
                pull_out=False,
            ),
            centered(
                str(SVG_DIR / "marquis_warrior.svg"),
                (51.25, 27.9),
                (12.0, 12.0),
                depth=0.6,
                z_offset=3.9,
                color="black",
                pull_out=False,
            ),
            centered(
                str(SVG_DIR / "marquis_warrior.svg"),
                (51.25, 46.3),
                (12.0, 12.0),
                depth=0.6,
                z_offset=3.9,
                color="black",
                pull_out=False,
            ),
        ],
    )

    # Marquis Box Top
    project.box(
        BoxType.SLIDING,
        "MarquisBoxTop",
        size=(106.5, 59.833, 14.5),
        lid=LID_MARQUIS,
        color=Color("orange"),
        position=(0.0, 98.5, 28.0 + 24.5),
    ).compartment(
        "WoodAndBuildings",
        elements=[
            # --- Wood Logs (2 slots, stacked 4-high, depth 8.0) ---
            centered(
                None,
                (10.91, 9.25),
                (15.0, 15.0),
                shape=ElementShape.CIRCLE,
                depth=8.0,
                pull_out=True,
            ),
            centered(
                None,
                (31.07, 9.25),
                (15.0, 15.0),
                shape=ElementShape.CIRCLE,
                depth=8.0,
                pull_out=True,
            ),
            # --- Recruiters / Handshake (2 slots, stacked 3-high, depth 6.0) ---
            centered(
                None,
                (71.39, 9.25),
                (18.5, 18.5),
                shape=ElementShape.RECT,
                depth=6.0,
                pull_out=True,
            ),
            centered(
                None,
                (91.55, 9.25),
                (18.5, 18.5),
                shape=ElementShape.RECT,
                depth=6.0,
                pull_out=True,
            ),
            # --- Workshops / Anvil (2 slots, stacked 3-high, depth 6.0) ---
            centered(
                None,
                (10.91, 46.583),
                (18.5, 18.5),
                shape=ElementShape.RECT,
                depth=6.0,
                pull_out=True,
            ),
            centered(
                None,
                (31.07, 46.583),
                (18.5, 18.5),
                shape=ElementShape.RECT,
                depth=6.0,
                pull_out=True,
            ),
            # --- Sawmills / Saw (2 slots, stacked 3-high, depth 6.0) ---
            centered(
                None,
                (71.39, 46.583),
                (18.5, 18.5),
                shape=ElementShape.RECT,
                depth=6.0,
                pull_out=True,
            ),
            centered(
                None,
                (91.55, 46.583),
                (18.5, 18.5),
                shape=ElementShape.RECT,
                depth=6.0,
                pull_out=True,
            ),
            # --- Keep (1 slot, stacked 1-high, depth 2.0) ---
            centered(
                None,
                (51.23, 11.25),
                (18.5, 18.5),
                shape=ElementShape.CIRCLE,
                depth=2.0,
                pull_out=True,
            ),
            # --- Score Laurel (1 slot, stacked 1-high, depth 2.0) ---
            centered(
                None,
                (51.23, 41.583),
                (18.5, 18.5),
                shape=ElementShape.RECT,
                depth=2.0,
                pull_out=True,
            ),
            # --- Wood Stamps ---
            centered(
                str(SVG_DIR / "log.svg"),
                (10.91, 9.25),
                (15.0 * 0.35, 15.0 * 0.35),
                depth=0.6,
                z_offset=12.9 - 8.0,
                color="black",
                pull_out=False,
            ),
            centered(
                str(SVG_DIR / "log.svg"),
                (31.07, 9.25),
                (15.0 * 0.35, 15.0 * 0.35),
                depth=0.6,
                z_offset=12.9 - 8.0,
                color="black",
                pull_out=False,
            ),
            # --- Recruiter Stamps ---
            centered(
                str(SVG_DIR / "handshake.svg"),
                (71.39, 9.25),
                (18.5 * 0.35, 18.5 * 0.35),
                depth=0.6,
                z_offset=12.9 - 6.0,
                color="black",
                pull_out=False,
            ),
            centered(
                str(SVG_DIR / "handshake.svg"),
                (91.55, 9.25),
                (18.5 * 0.35, 18.5 * 0.35),
                depth=0.6,
                z_offset=12.9 - 6.0,
                color="black",
                pull_out=False,
            ),
            # --- Workshop Stamps ---
            centered(
                str(SVG_DIR / "anvil.svg"),
                (10.91, 46.583),
                (18.5 * 0.35, 18.5 * 0.35),
                depth=0.6,
                z_offset=12.9 - 6.0,
                color="black",
                pull_out=False,
            ),
            centered(
                str(SVG_DIR / "anvil.svg"),
                (31.07, 46.583),
                (18.5 * 0.35, 18.5 * 0.35),
                depth=0.6,
                z_offset=12.9 - 6.0,
                color="black",
                pull_out=False,
            ),
            # --- Sawmill Stamps ---
            centered(
                str(SVG_DIR / "saw.svg"),
                (71.39, 46.583),
                (18.5 * 0.35, 18.5 * 0.35),
                depth=0.6,
                z_offset=12.9 - 6.0,
                color="black",
                pull_out=False,
            ),
            centered(
                str(SVG_DIR / "saw.svg"),
                (91.55, 46.583),
                (18.5 * 0.35, 18.5 * 0.35),
                depth=0.6,
                z_offset=12.9 - 6.0,
                color="black",
                pull_out=False,
            ),
            # --- Keep Stamp ---
            centered(
                str(SVG_DIR / "keep.svg"),
                (51.23, 11.25),
                (18.5 * 0.35, 18.5 * 0.35),
                depth=0.6,
                z_offset=12.9 - 2.0,
                color="black",
                pull_out=False,
            ),
            # --- Score Laurel Stamp ---
            centered(
                str(SVG_DIR / "laurel_wreath.svg"),
                (51.23, 41.583),
                (18.5 * 0.35, 18.5 * 0.35),
                depth=0.6,
                z_offset=12.9 - 2.0,
                color="black",
                pull_out=False,
            ),
        ],
    )

    # Erie Box Bottom
    erie_bottom_size = (106.5, 59.833, 24.5)
    project.box(
        BoxType.CAP,
        "ErieBoxBottom",
        size=erie_bottom_size,
        lid=LID_ERIE,
        color=Color("blue"),
        position=(0.0, 158.333, 28.0),
    ).compartment(
        "Warriors",
        elements=[
            # 2 horizontal channels for 20 bird meeples (10 + 10)
            centered(
                None,
                (51.25, 15.0),
                (91.0, 21.0),
                depth=18.0,
                pull_out=True,
                pull_out_width=80.0,
                pull_out_depth=9.0,
            ),
            centered(
                None,
                (51.25, 40.8),
                (91.0, 21.0),
                depth=18.0,
                pull_out=True,
                pull_out_width=80.0,
                pull_out_depth=9.0,
            ),
            # Stamps/Inlays at the bottom of the channels
            centered(
                str(SVG_DIR / "erie_warrior.svg"),
                (51.25, 15.0),
                (12.0, 12.0),
                depth=0.6,
                z_offset=3.9,
                color="black",
                pull_out=False,
            ),
            centered(
                str(SVG_DIR / "erie_warrior.svg"),
                (51.25, 40.8),
                (12.0, 12.0),
                depth=0.6,
                z_offset=3.9,
                color="black",
                pull_out=False,
            ),
        ],
    )

    # Erie Box Top
    project.box(
        BoxType.SLIDING,
        "ErieBoxTop",
        size=(53.25, 59.833, 14.5),
        lid=LID_ERIE,
        color=Color("blue"),
        position=(0.0, 158.333, 28.0 + 24.5),
    ).compartment(
        "Roosts",
        elements=[
            # Roost slots (stacked 4-high, depth 8.0)
            centered(
                None,
                (15.0, 20.0),
                (18.5, 18.5),
                shape=ElementShape.RECT,
                depth=8.0,
                pull_out=True,
            ),
            centered(
                None,
                (35.0, 20.0),
                (18.5, 18.5),
                shape=ElementShape.RECT,
                depth=8.0,
                pull_out=True,
            ),
            # Score marker (laurel wreath)
            centered(
                None,
                (25.0, 45.0),
                (18.5, 18.5),
                shape=ElementShape.RECT,
                depth=2.0,
                pull_out=True,
            ),
            # Floor Stamps
            centered(
                str(SVG_DIR / "tree.svg"),
                (15.0, 20.0),
                (18.5 * 0.35, 18.5 * 0.35),
                depth=0.6,
                z_offset=12.9 - 8.0,
                color="black",
                pull_out=False,
            ),
            centered(
                str(SVG_DIR / "tree.svg"),
                (35.0, 20.0),
                (18.5 * 0.35, 18.5 * 0.35),
                depth=0.6,
                z_offset=12.9 - 8.0,
                color="black",
                pull_out=False,
            ),
            centered(
                str(SVG_DIR / "laurel_wreath.svg"),
                (25.0, 45.0),
                (18.5 * 0.35, 18.5 * 0.35),
                depth=0.6,
                z_offset=12.9 - 2.0,
                color="black",
                pull_out=False,
            ),
        ],
    )

    # Alliance Box Bottom
    alliance_bottom_size = (53.25, 59.833, 24.5)
    project.box(
        BoxType.CAP,
        "AllianceBoxBottom",
        size=alliance_bottom_size,
        lid=LID_ALLIANCE,
        color=Color("green"),
        position=(106.5, 98.5, 28.0),
    ).compartment(
        "Warriors",
        elements=[
            # 2 horizontal channels for 10 alliance meeples (5 + 5)
            centered(
                None,
                (24.625, 15.0),
                (46.0, 19.5),
                depth=18.0,
                pull_out=True,
                pull_out_width=40.0,
                pull_out_depth=9.0,
            ),
            centered(
                None,
                (24.625, 39.8),
                (46.0, 19.5),
                depth=18.0,
                pull_out=True,
                pull_out_width=40.0,
                pull_out_depth=9.0,
            ),
            # Stamps/Inlays at the bottom of the channels (comp_depth = 20.9)
            centered(
                str(SVG_DIR / "alliance_warrior.svg"),
                (24.625, 15.0),
                (12.0, 12.0),
                depth=0.6,
                z_offset=20.9 - 18.0,
                color="black",
                pull_out=False,
            ),
            centered(
                str(SVG_DIR / "alliance_warrior.svg"),
                (24.625, 39.8),
                (12.0, 12.0),
                depth=0.6,
                z_offset=20.9 - 18.0,
                color="black",
                pull_out=False,
            ),
        ],
    )

    # Alliance Box Top (4 pockets: Score, 3 Bases, 2x5 Sympathy)
    alliance_top_comp_depth = 14.5 - 1.6 - 2.0  # 10.9mm
    project.box(
        BoxType.SLIDING,
        "AllianceBoxTop",
        size=(53.25, 59.833, 14.5),
        lid=LID_ALLIANCE,
        color=Color("green"),
        position=(106.5, 98.5, 28.0 + 24.5),
    ).compartment(
        "BasesAndSympathy",
        elements=[
            # Score marker (front-left, depth 3.0)
            centered(
                None,
                (13.5, 15.0),
                (18.5, 18.5),
                shape=ElementShape.RECT,
                depth=3.0,
                pull_out=True,
            ),
            # Sympathy / Fist #1 (front-right, 5 tokens, depth 10.5)
            centered(
                None,
                (35.75, 15.0),
                (18.5, 18.5),
                shape=ElementShape.CIRCLE,
                depth=10.5,
                pull_out=True,
            ),
            # Alliance Camp / Bases (back-left, 3 tokens, depth 7.0)
            centered(
                None,
                (13.5, 41.0),
                (18.5, 18.5),
                shape=ElementShape.RECT,
                depth=7.0,
                pull_out=True,
            ),
            # Sympathy / Fist #2 (back-right, 5 tokens, depth 10.5)
            centered(
                None,
                (35.75, 41.0),
                (18.5, 18.5),
                shape=ElementShape.CIRCLE,
                depth=10.5,
                pull_out=True,
            ),
            # Stamps/Inlays at the bottom of the pockets
            centered(
                str(SVG_DIR / "laurel_wreath.svg"),
                (13.5, 15.0),
                (12.0, 12.0),
                depth=0.6,
                z_offset=alliance_top_comp_depth - 3.0,
                color="black",
                pull_out=False,
            ),
            centered(
                str(SVG_DIR / "fist.svg"),
                (35.75, 15.0),
                (12.0, 12.0),
                depth=0.6,
                z_offset=alliance_top_comp_depth - 10.5,
                color="black",
                pull_out=False,
            ),
            centered(
                str(SVG_DIR / "camp.svg"),
                (13.5, 41.0),
                (12.0, 12.0),
                depth=0.6,
                z_offset=alliance_top_comp_depth - 7.0,
                color="black",
                pull_out=False,
            ),
            centered(
                str(SVG_DIR / "fist.svg"),
                (35.75, 41.0),
                (12.0, 12.0),
                depth=0.6,
                z_offset=alliance_top_comp_depth - 10.5,
                color="black",
                pull_out=False,
            ),
        ],
    )

    # Lizard Box Bottom
    lizard_bottom_size = (106.5, 59.833, 26.5)
    project.box(
        BoxType.CAP,
        "LizardBoxBottom",
        size=lizard_bottom_size,
        lid=LID_LIZARD,
        color=Color("yellow"),
        position=(0.0, 218.166, 28.0),
    ).compartment(
        "Warriors",
        elements=[
            # 5 rows of 5 individual lizard warrior slots (25 total)
            *[
                centered(
                    None,
                    (11.65 + 19.8 * i, 7.916 + 10.0 * j),
                    (18.0, 9.0),
                    depth=20.0,
                    pull_out=True,
                    pull_out_depth=10.0,
                )
                for i in range(5)
                for j in range(5)
            ]
        ],
    )

    # Lizard Box Top
    project.box(
        BoxType.SLIDING,
        "LizardBoxTop",
        size=(79.875, 59.833, 12.5),
        lid=LID_LIZARD,
        color=Color("yellow"),
        position=(0.0, 218.166, 28.0 + 26.5),
    ).compartment(
        "Gardens",
        elements=[
            # Rectangular Pockets (3x2 Grid)
            centered(
                None,
                (16.34, 17.5),
                (18.5, 18.5),
                shape=ElementShape.RECT,
                depth=8.0,
                pull_out=True,
            ),
            centered(
                None,
                (39.93, 17.5),
                (18.5, 18.5),
                shape=ElementShape.RECT,
                depth=8.0,
                pull_out=True,
            ),
            centered(
                None,
                (63.52, 17.5),
                (18.5, 18.5),
                shape=ElementShape.RECT,
                depth=8.0,
                pull_out=True,
            ),
            centered(
                None,
                (16.34, 42.333),
                (18.5, 18.5),
                shape=ElementShape.RECT,
                depth=3.0,
                pull_out=True,
            ),
            centered(
                None,
                (39.93, 42.333),
                (18.5, 18.5),
                shape=ElementShape.RECT,
                depth=4.0,
                pull_out=True,
            ),
            centered(
                None,
                (63.52, 42.333),
                (18.5, 18.5),
                shape=ElementShape.RECT,
                depth=2.0,
                pull_out=True,
            ),
            # Stamps/Inlays at the bottom of the pockets (depth=0.6, comp_depth = 8.9)
            # Gardens (z_offset = 8.9 - 8.0 = 0.9)
            centered(
                str(SVG_DIR / "fox.svg"),
                (16.34, 17.5),
                (10.0, 10.0),
                depth=0.6,
                z_offset=0.9,
                color="black",
                pull_out=False,
            ),
            centered(
                str(SVG_DIR / "rabbit.svg"),
                (39.93, 17.5),
                (10.0, 10.0),
                depth=0.6,
                z_offset=0.9,
                color="black",
                pull_out=False,
            ),
            centered(
                str(SVG_DIR / "mouse.svg"),
                (63.52, 17.5),
                (10.0, 10.0),
                depth=0.6,
                z_offset=0.9,
                color="black",
                pull_out=False,
            ),
            # Score Laurel (z_offset = 8.9 - 3.0 = 5.9)
            centered(
                str(SVG_DIR / "laurel_wreath.svg"),
                (16.34, 42.333),
                (12.0, 12.0),
                depth=0.6,
                z_offset=5.9,
                color="black",
                pull_out=False,
            ),
            # Faction (z_offset = 8.9 - 4.0 = 4.9)
            centered(
                str(SVG_DIR / "lizard_faction.svg"),
                (39.93, 42.333),
                (10.0, 10.0),
                depth=0.6,
                z_offset=4.9,
                color="black",
                pull_out=False,
            ),
            # Outcast (z_offset = 8.9 - 2.0 = 6.9)
            centered(
                str(SVG_DIR / "outcast.svg"),
                (63.52, 42.333),
                (10.0, 10.0),
                depth=0.6,
                z_offset=6.9,
                color="black",
                pull_out=False,
            ),
        ],
    )

    # Riverfolk Box Bottom
    riverfolk_bottom_size = (53.25, 59.833, 26.5)
    project.box(
        BoxType.CAP,
        "RiverfolkBoxBottom",
        size=riverfolk_bottom_size,
        lid=LID_RIVERFOLK,
        color=Color("teal"),
        position=(106.5, 218.166, 28.0),
    ).compartment(
        "Warriors",
        elements=[
            # 3 horizontal channels for 15 otter meeples (5 + 5 + 5)
            centered(
                None,
                (24.625, 11.5),
                (46.0, 15.0),
                depth=18.0,
                pull_out=True,
                pull_out_width=40.0,
                pull_out_depth=9.0,
            ),
            centered(
                None,
                (24.625, 27.9),
                (46.0, 15.0),
                depth=18.0,
                pull_out=True,
                pull_out_width=40.0,
                pull_out_depth=9.0,
            ),
            centered(
                None,
                (24.625, 44.3),
                (46.0, 15.0),
                depth=18.0,
                pull_out=True,
                pull_out_width=40.0,
                pull_out_depth=9.0,
            ),
            # Stamps/Inlays at the bottom of the channels
            centered(
                str(SVG_DIR / "riverfolk_warrior.svg"),
                (24.625, 11.5),
                (12.0, 12.0),
                depth=0.6,
                z_offset=4.9,
                color="black",
                pull_out=False,
            ),
            centered(
                str(SVG_DIR / "riverfolk_warrior.svg"),
                (24.625, 27.9),
                (12.0, 12.0),
                depth=0.6,
                z_offset=4.9,
                color="black",
                pull_out=False,
            ),
            centered(
                str(SVG_DIR / "riverfolk_warrior.svg"),
                (24.625, 44.3),
                (12.0, 12.0),
                depth=0.6,
                z_offset=4.9,
                color="black",
                pull_out=False,
            ),
        ],
    )

    # Riverfolk Box Top (7 pockets: Score + 3 Glass Gems + 3 Trade Post suits)
    riverfolk_top_comp_depth = 12.5 - 1.6 - 2.0  # 8.9mm
    project.box(
        BoxType.SLIDING,
        "RiverfolkBoxTop",
        size=(79.875, 59.833, 12.5),
        lid=LID_RIVERFOLK,
        color=Color("teal"),
        position=(79.875, 218.166, 28.0 + 26.5),
    ).compartment(
        "TradePosts",
        elements=[
            # Row 1 (front): Score marker + 3 Glass Gems (17mm diameter)
            centered(
                None,
                (10.25, 14.5),
                (18.5, 18.5),
                shape=ElementShape.RECT,
                depth=3.0,
                pull_out=True,
            ),
            *[
                centered(
                    None,
                    (gem_x, 14.5),
                    (17.0, 17.0),
                    shape=ElementShape.CIRCLE,
                    depth=8.5,
                    pull_out=True,
                )
                for gem_x in (29.5, 48.0, 66.5)
            ],
            # Row 2 (back): 3 Trade Post suits (Fox, Rabbit, Mouse - 3 tokens each)
            *[
                centered(
                    None,
                    (sign_x, 41.5),
                    (18.5, 18.5),
                    shape=ElementShape.CIRCLE,
                    depth=7.0,
                    pull_out=True,
                )
                for sign_x in (15.5, 37.9, 60.3)
            ],
            # Stamps/Inlays at pocket bottoms
            centered(
                str(SVG_DIR / "laurel_wreath.svg"),
                (10.25, 14.5),
                (12.0, 12.0),
                depth=0.6,
                z_offset=riverfolk_top_comp_depth - 3.0,
                color="black",
                pull_out=False,
            ),
            *[
                centered(
                    str(SVG_DIR / "gem.svg"),
                    (gem_x, 14.5),
                    (11.0, 11.0),
                    depth=0.6,
                    z_offset=riverfolk_top_comp_depth - 8.5,
                    color="black",
                    pull_out=False,
                )
                for gem_x in (29.5, 48.0, 66.5)
            ],
            *[
                centered(
                    str(SVG_DIR / "sign.svg"),
                    (sign_x, 41.5),
                    (12.0, 12.0),
                    depth=0.6,
                    z_offset=riverfolk_top_comp_depth - 7.0,
                    color="black",
                    pull_out=False,
                )
                for sign_x in (15.5, 37.9, 60.3)
            ],
        ],
    )

    # Vagabond Boxes (2 stacked boxes: Base + Riverfolk 2nd Vagabond)
    def _add_vagabond_box(label: str, position: tuple[float, float, float]) -> None:
        vagabond_comp_depth = 19.5 - 1.6 - 2.0  # 15.9mm
        elements = [
            # Front-left: Vagabond meeple cutout (9mm thick + 1mm clearance)
            centered(
                str(SVG_DIR / "vagabond_warrior.svg"),
                (14.5, 16.0),
                (21.0, 22.0),
                depth=10.0,
                pull_out=True,
            ),
            # Front-right: Score marker well + laurel wreath inlay
            centered(
                None,
                (37.5, 16.0),
                (18.5, 18.5),
                shape=ElementShape.RECT,
                depth=3.0,
                pull_out=True,
            ),
            centered(
                str(SVG_DIR / "laurel_wreath.svg"),
                (37.5, 16.0),
                (12.0, 12.0),
                depth=0.6,
                z_offset=vagabond_comp_depth - 3.0,
                color="black",
                pull_out=False,
            ),
        ]
        # Back row: Two relationship marker wells (3 tokens each = 6 per Vagabond)
        for rel_x in (13.5, 36.0):
            elements.extend([
                centered(
                    None,
                    (rel_x, 43.0),
                    (18.5, 18.5),
                    shape=ElementShape.RECT,
                    depth=7.0,
                    pull_out=True,
                ),
                centered(
                    "Relation",
                    (rel_x, 43.0),
                    (15.0, 15.0),
                    shape=ElementShape.TEXT,
                    depth=0.6,
                    z_offset=vagabond_comp_depth - 7.0,
                    color="black",
                    pull_out=False,
                ),
            ])
        project.box(
            BoxType.SLIDING,
            label,
            size=(53.25, 59.833, 19.5),
            lid=LID_VAGABOND,
            color=Color("green"),
            position=position,
        ).compartment("ItemsAndScore", elements=elements)


    _add_vagabond_box("VagabondBox", (106.5, 158.333, 28.0))
    _add_vagabond_box("VagabondBox2", (106.5, 158.333, 28.0 + 19.5))

    # Dice Box (placed behind the Items stack in the right column)
    project.box(
        BoxType.SLIDING,
        "DiceBox",
        size=(53.25, 59.833, 39.0),
        lid=LID_BASE.titled("Dice"),
        position=(159.75, 103.5, 28.0),
    ).compartment(
        "Dice",
        elements=[
            centered(
                None,
                (14.0, 14.0),
                (22.0, 22.0),
                shape=ElementShape.CIRCLE,
                depth=22.0,
                pull_out=True,
            ),
            centered(
                None,
                (35.25, 41.833),
                (22.0, 22.0),
                shape=ElementShape.CIRCLE,
                depth=22.0,
                pull_out=True,
            ),
        ],
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
) -> Project:
    """Build a Root Project containing only the selected expansions or subgroups.

    Defaults to all implemented expansions (``("base", "riverfolk")``).
    """
    active_subgroups = resolve_root_subgroups(expansions, subgroups=subgroups)
    root_project = _make_root_project()
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
        "presets": list(ROOT_PRESETS),
        "expansions": [
            {
                "key": spec.key,
                "name": spec.name,
                "status": spec.status,
                "required": spec.required,
                "description": spec.description,
                "subgroups": list(spec.subgroups),
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
