# SPDX-License-Identifier: Apache-2.0
"""Root board game insert — pyboxbuilder port of `examples/root.scad`."""

import sys
from pathlib import Path
from typing import Any

# Repo root on sys.path
REPO_ROOT = Path(__file__).resolve().parents[2] if "__file__" in globals() else Path.cwd()
sys.path.insert(0, str(REPO_ROOT))
for _sp in REPO_ROOT.glob(".venv/lib/*/site-packages"):
    sys.path.insert(0, str(_sp))
for _sp in REPO_ROOT.glob("venv/*/lib/*/site-packages"):
    sys.path.insert(0, str(_sp))

from pyboxbuilder import (
    BoxType,
    Color,
    LidBuilder,
    Project,
    run,
)
from pyboxbuilder.compartments import CompartmentElement
from pyboxbuilder.enums import ElementShape


def centered(
    shape_file: str | None,
    center: tuple[float, float],
    size: tuple[float, float],
    *,
    shape: ElementShape = ElementShape.SVG,
    rotation: float = 0.0,
    label: str | None = None,
    pull_out: bool = False,
    **pocket_kwargs,
) -> CompartmentElement:
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
    **kwargs,
) -> CompartmentElement:
    interior_w = box_size[0] - 2 * wall_thickness
    interior_l = box_size[1] - 2 * wall_thickness
    return centered(shape_file, (interior_w / 2, interior_l / 2), element_size, **kwargs)


def pack_in_columns(
    items: list[dict[str, Any]],
    comp_size: tuple[float, float],
    column_width: float,
    spacing_x: float = 2.0,
    spacing_y: float = 2.0,
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

        elements.append(
            centered(
                svg,
                (cx, cy),
                (w, l),
                shape=shape,
                rotation=rotation,
                depth=depth,
                pull_out=True,
            )
        )
        col_y[c] += fl + spacing_y
    return elements


# SVG Assets directory path
SVG_DIR = REPO_ROOT / "boxes" / "root" / "svg"

# Project Setup
project = Project("Root", game_box_size=(214.0, 278.0, 67.0))

# Faction Lid configurations using static SVG files
LID_MARQUIS = LidBuilder(logo=str(SVG_DIR / "marquis_eyes.svg"), logo_color=Color("black"))
LID_ERIE = LidBuilder(logo=str(SVG_DIR / "erie_eyes.svg"), logo_color=Color("black"))
LID_ALLIANCE = LidBuilder(logo=str(SVG_DIR / "alliance_eyes.svg"), logo_color=Color("black"))
LID_LIZARD = LidBuilder(logo=str(SVG_DIR / "lizard_eyes.svg"), logo_color=Color("black"))
LID_RIVERFOLK = LidBuilder(logo=str(SVG_DIR / "riverfolk_eyes.svg"), logo_color=Color("black"))
LID_VAGABOND = LidBuilder(logo=str(SVG_DIR / "vagabond_eyes.svg"), logo_color=Color("black"))

# ── Boxes ─────────────────────────────────────────────────────────────────

# Card Boxes
card_size = (79.875, 98.5, 39.0)
project.card_box(
    "BaseCardBox",
    card_size=(69.0, 92.5),
    size=card_size,
    lid=LidBuilder(text="Shared"),
    position=(0.0, 0.0, 28.0),
    no_rotate=True,
)

card_erie_size = (79.875, 98.5, 8.6)
project.card_box(
    "ErieCardBox",
    card_size=(69.0, 92.5),
    size=card_erie_size,
    lid=LidBuilder(text="Erie"),
    position=(79.875, 0.0, 28.0),
    no_rotate=True,
)

card_vagabond_size = (79.875, 98.5, 19.4)
project.card_box(
    "VagabondCardBox",
    card_size=(69.0, 92.5),
    size=card_vagabond_size,
    lid=LidBuilder(text="Vagabond"),
    position=(79.875, 0.0, 28.0 + 8.6),
    no_rotate=True,
)

card_overview_size = (79.875, 98.5, 11.0)
project.card_box(
    "OverviewCardBox",
    card_size=(69.0, 92.5),
    size=card_overview_size,
    lid=LidBuilder(text="Overview"),
    position=(79.875, 0.0, 28.0 + 8.6 + 19.4),
    no_rotate=True,
)

# Stacked Item Boxes
item_box_length = 103.5
item_comp_size = (49.25, 99.5)

# ItemsBoxBottom (comp_depth = 6.0)
project.box(
    BoxType.SLIDING,
    "ItemsBoxBottom",
    size=(53.25, item_box_length, 10.0),
    lid=LidBuilder(text="Items Bot"),
    position=(159.75, 0.0, 28.0),
    no_rotate=True,
).compartment(
    "Items",
    depth=6.0,
    elements=pack_in_columns(
        items=[{"depth": d} for d in [4.0, 6.0, 2.0, 4.0, 6.0, 2.0, 4.0, 6.0, 6.0, 4.0]],
        comp_size=item_comp_size,
        column_width=18.5,
        spacing_x=4.08,
        spacing_y=1.16,
    ),
)

# ItemsBoxMiddle (comp_depth = 5.0)
project.box(
    BoxType.SLIDING,
    "ItemsBoxMiddle",
    size=(53.25, item_box_length, 9.0),
    lid=LidBuilder(text="Items Mid"),
    position=(159.75, 0.0, 28.0 + 10.0),
    no_rotate=True,
).compartment(
    "Items",
    depth=5.0,
    elements=pack_in_columns(
        items=[{"depth": d} for d in [4.0, 4.0, 2.0, 2.0, 4.0, 4.0, 4.0, 4.0, 4.0]],
        comp_size=item_comp_size,
        column_width=18.5,
        spacing_x=4.08,
        spacing_y=1.16,
    ),
)

# ItemsBoxWinter (comp_depth = 5.0)
project.box(
    BoxType.SLIDING,
    "ItemsBoxWinter",
    size=(53.25, item_box_length, 9.0),
    lid=LidBuilder(text="Winter"),
    position=(159.75, 0.0, 28.0 + 10.0 + 9.0),
    no_rotate=True,
).compartment(
    "WinterTokens",
    depth=5.0,
    elements=pack_in_columns(
        items=[
            {
                "svg": str(SVG_DIR / "winter_token.svg"),
                "shape": ElementShape.SVG,
                "depth": 5.0,
                "size": (15.5, 29.5),
                "rotation": 90,
            }
            for _ in range(6)
        ],
        comp_size=item_comp_size,
        column_width=29.5,
        spacing_x=7.875,
        spacing_y=1.0,
    ),
)

# ItemsBoxExtras (comp_depth = 7.0)
project.box(
    BoxType.SLIDING,
    "ItemsBoxExtras",
    size=(53.25, item_box_length, 11.0),
    lid=LidBuilder(text="Extras"),
    position=(159.75, 0.0, 28.0 + 10.0 + 9.0 + 9.0),
    no_rotate=True,
).compartment(
    "Extras",
    depth=7.0,
    elements=pack_in_columns(
        items=[
            {"shape": ElementShape.CIRCLE, "size": (21.0, 21.0), "depth": 5.0},
            {"shape": ElementShape.CIRCLE, "size": (21.0, 21.0), "depth": 5.0},
            {"shape": ElementShape.CIRCLE, "size": (21.0, 21.0), "depth": 5.0},
            {"shape": ElementShape.RECT, "size": (18.5, 18.5), "depth": 5.0},
            {"shape": ElementShape.RECT, "size": (18.5, 18.5), "depth": 5.0},
            {"shape": ElementShape.RECT, "size": (18.5, 18.5), "depth": 5.0},
            {"shape": ElementShape.RECT, "size": (18.5, 18.5), "depth": 5.0},
            {"shape": ElementShape.RECT, "size": (18.5, 18.5), "depth": 5.0},
        ],
        comp_size=item_comp_size,
        column_width=21.0,
        spacing_x=2.41,
        spacing_y=3.3,
    ),
)

# Marquis Box Bottom
marquis_bottom_size = (106.5, 59.833, 29.0)
project.box(
    BoxType.CAP,
    "MarquisBoxBottom",
    size=marquis_bottom_size,
    lid=LID_MARQUIS,
    color=Color("orange"),
    position=(0.0, 98.5, 28.0),
    no_rotate=True,
).compartment(
    "Warriors",
    elements=[
        # 3 horizontal channels for cat tokens
        centered(None, (20.0, 27.916), (22.0, 46.0), depth=18.0, pull_out=True),
        centered(None, (50.0, 27.916), (22.0, 46.0), depth=18.0, pull_out=True),
        centered(None, (80.0, 27.916), (22.0, 46.0), depth=18.0, pull_out=True),
    ],
)

# Marquis Box Top
project.box(
    BoxType.SLIDING,
    "MarquisBoxTop",
    size=(106.5, 59.833, 10.0),
    lid=LID_MARQUIS,
    color=Color("orange"),
    position=(0.0, 98.5, 28.0 + 29.0),
    no_rotate=True,
).compartment(
    "WoodAndBuildings",
    elements=[
        # Wood logs
        centered(str(SVG_DIR / "log.svg"), (15.0, 15.0), (18.5, 18.5), pull_out=True),
        centered(str(SVG_DIR / "log.svg"), (35.0, 15.0), (18.5, 18.5), pull_out=True),
        # Keep
        centered(str(SVG_DIR / "keep.svg"), (55.0, 15.0), (18.5, 18.5), pull_out=True),
        # Buildings: Anvil, Saw, Handshake
        centered(str(SVG_DIR / "anvil.svg"), (15.0, 40.0), (18.5, 18.5), pull_out=True),
        centered(str(SVG_DIR / "saw.svg"), (35.0, 40.0), (18.5, 18.5), pull_out=True),
        centered(str(SVG_DIR / "handshake.svg"), (55.0, 40.0), (18.5, 18.5), pull_out=True),
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
    no_rotate=True,
).compartment(
    "Warriors",
    elements=[
        # 2 horizontal channels for bird tokens
        centered(None, (30.0, 27.916), (22.0, 46.0), depth=18.0, pull_out=True),
        centered(None, (70.0, 27.916), (22.0, 46.0), depth=18.0, pull_out=True),
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
    no_rotate=True,
).compartment(
    "Roosts",
    elements=[
        # Roosts (Erie tree icon)
        centered(str(SVG_DIR / "tree.svg"), (15.0, 20.0), (18.5, 18.5), pull_out=True),
        centered(str(SVG_DIR / "tree.svg"), (35.0, 20.0), (18.5, 18.5), pull_out=True),
        # Score marker (laurel wreath)
        centered(
            str(SVG_DIR / "laurel_wreath.svg"),
            (25.0, 45.0),
            (18.5, 18.5),
            pull_out=True,
        ),
    ],
)

# Alliance Box Bottom
alliance_bottom_size = (53.25, 59.833, 25.5)
project.box(
    BoxType.CAP,
    "AllianceBoxBottom",
    size=alliance_bottom_size,
    lid=LID_ALLIANCE,
    color=Color("green"),
    position=(106.5, 98.5, 28.0),
    no_rotate=True,
).compartment(
    "Warriors",
    elements=[
        # 2 horizontal channels for alliance tokens
        centered(None, (15.0, 27.916), (19.5, 46.0), depth=18.0, pull_out=True),
        centered(None, (34.25, 27.916), (19.5, 46.0), depth=18.0, pull_out=True),
    ],
)

# Alliance Box Top
project.box(
    BoxType.SLIDING,
    "AllianceBoxTop",
    size=(53.25, 59.833, 13.5),
    lid=LID_ALLIANCE,
    color=Color("green"),
    position=(106.5, 98.5, 28.0 + 25.5),
    no_rotate=True,
).compartment(
    "BasesAndSympathy",
    elements=[
        # Alliance Camp (Bases)
        centered(str(SVG_DIR / "camp.svg"), (15.0, 15.0), (18.5, 18.5), pull_out=True),
        # Sympathy (Fist)
        centered(str(SVG_DIR / "fist.svg"), (35.0, 15.0), (18.5, 18.5), pull_out=True),
        centered(str(SVG_DIR / "fist.svg"), (25.0, 40.0), (18.5, 18.5), pull_out=True),
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
    no_rotate=True,
).compartment(
    "Warriors",
    elements=[
        # 5 rows of 5 individual lizard warrior slots
        *[
            centered(
                None,
                (10.0 + 19.8 * i, 7.0 + 10.0 * j),
                (18.0, 9.0),
                depth=20.0,
                pull_out=True,
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
    size=(106.5, 59.833, 12.5),
    lid=LID_LIZARD,
    color=Color("yellow"),
    position=(0.0, 218.166, 28.0 + 26.5),
    no_rotate=True,
).compartment(
    "Gardens",
    elements=[
        # Outcast markers & gardens
        centered(str(SVG_DIR / "camp.svg"), (20.0, 20.0), (18.5, 18.5), pull_out=True),
        centered(str(SVG_DIR / "camp.svg"), (50.0, 20.0), (18.5, 18.5), pull_out=True),
        centered(str(SVG_DIR / "camp.svg"), (80.0, 20.0), (18.5, 18.5), pull_out=True),
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
    no_rotate=True,
).compartment(
    "Warriors",
    elements=[
        # 3 horizontal channels
        centered(None, (10.0, 27.916), (16.0, 46.0), depth=18.0, pull_out=True),
        centered(None, (24.625, 27.916), (16.0, 46.0), depth=18.0, pull_out=True),
        centered(None, (39.25, 27.916), (16.0, 46.0), depth=18.0, pull_out=True),
    ],
)

# Riverfolk Box Top
project.box(
    BoxType.SLIDING,
    "RiverfolkBoxTop",
    size=(106.5, 59.833, 12.5),
    lid=LID_RIVERFOLK,
    color=Color("teal"),
    position=(106.5, 218.166, 28.0 + 26.5),
    no_rotate=True,
).compartment(
    "TradePosts",
    elements=[
        # Trade Posts (Signs)
        centered(str(SVG_DIR / "sign.svg"), (20.0, 20.0), (18.5, 18.5), pull_out=True),
        centered(str(SVG_DIR / "sign.svg"), (50.0, 20.0), (18.5, 18.5), pull_out=True),
        # Glass gems (Egg shapes)
        centered(str(SVG_DIR / "fist.svg"), (80.0, 20.0), (18.5, 18.5), pull_out=True),
    ],
)

# Vagabond Box
project.box(
    BoxType.SLIDING,
    "VagabondBox",
    size=(53.25, 59.833, 16.0),
    lid=LID_VAGABOND,
    color=Color("grey"),
    position=(106.5, 158.333, 28.0),
    no_rotate=True,
).compartment(
    "ItemsAndScore",
    elements=[
        centered(str(SVG_DIR / "vagabond_warrior.svg"), (15.0, 20.0), (21.0, 22.0), depth=9.0),
        # Relations
        centered(
            str(SVG_DIR / "laurel_wreath.svg"),
            (35.0, 20.0),
            (18.5, 18.5),
            pull_out=True,
        ),
    ],
)

# Spacer Box (actual size of remaining box area, acting as the placeholder/boards spacer)
project.box(
    BoxType.NO_LID,
    "SpacerBox",
    size=(53.25, 172.5, 39.0),
    position=(159.75, 103.5, 28.0),
    no_rotate=True,
)

# Dice Box
project.box(
    BoxType.SLIDING,
    "DiceBox",
    size=(53.25, 59.833, 26.0),
    lid=LidBuilder(text="Dice"),
    position=(106.5, 158.333, 28.0 + 16.0),
    no_rotate=True,
).compartment("Dice", elements=[centered(None, (26.625, 29.916), (22.0, 22.0), pull_out=True)])

if __name__ == "__main__":
    run(project, show_lids=False, remove_layers=1)
