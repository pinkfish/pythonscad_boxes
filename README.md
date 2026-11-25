# pyboxbuilder

[![PyPI version](https://img.shields.io/pypi/v/pyboxbuilder.svg)](https://pypi.org/project/pyboxbuilder/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyboxbuilder.svg)](https://pypi.org/project/pyboxbuilder/)
[![License](https://img.shields.io/pypi/l/pyboxbuilder.svg)](https://github.com/pinkfish/pythonscad_boxes/blob/main/LICENSE)
[![Documentation](https://img.shields.io/badge/docs-stable-blue.svg)](https://pinkfish.github.io/pythonscad_boxes/stable/)

Declarative 3D board game box and insert design library for
[PythonSCAD](https://pythonscad.org/) and [`pybosl2`](https://pypi.org/project/pybosl2/).

`pyboxbuilder` turns a high-level description of what goes inside a board game
box — outer dimensions, non-printed boards, component inventory, sub-boxes, and
compartments — into printable multi-material 3MF/STL geometry and a color-coded
3D packing guide PDF.

The library's governing principle is **good defaults, not options**: describe
the storage you want and get printable files without tuning geometry you did not
ask about.

## Features

- **22 Box Types** — sliding lid, friction-fit cap, slipover, inset, snap-fit,
  threaded, bayonet, magnetic, print-in-place & filament hinges, clamshell,
  card shoe/library, dispenser, dice tray, sleeve drawer, modular interlock, and
  no-lid trays — each with matched body/lid mating geometry.
- **Smart Compartments & Finger Access** — absolute or proportional layouts,
  circular/hex/SVG-silhouette wells, smooth curved finger scoops, rolled wall
  holes, and automatic neighbor clearance.
- **3D Auto-Packing, Gap Absorption & Partial Boards** — auto-packs sub-boxes
  inside the game box, avoids non-printed `GameBoard` regions (folded boards,
  player screens, playmats), absorbs small vertical gaps (`<= 10 mm`) into box
  height, and fills remaining voids with hollow spacer trays.
- **Component Inventories & Packing Guide PDFs** — declare the game's piece
  inventory (`project.define_inventory(...)`) to verify 100% allocation across
  boxes, boards, and spacers, and generate a two-column color-coded packing
  guide PDF with a Box Summary, Master Component Checklist, and exploded 3D
  layer diagrams.
- **Thematic Lid Decoration** — auto-sized plaques, finials, SVG icons, custom
  fonts, cut-through patterns (hex, grid, Voronoi, Ammann-Beenker, tilings), and
  multi-color accent layers.
- **Export & Caching** — multi-color and single-color 3MF/STL export with
  content-based fingerprinting so unchanged parts are never rebuilt.

## Installation

Requires Python 3.11+ and [PythonSCAD](https://pythonscad.org/) (`pythonscad>=1.2.0`)
for 3D geometry export (layout and packing logic run in pure Python).

```sh
# Core library
pip install pyboxbuilder

# With packing guide PDF support (fpdf2 + Pillow)
pip install "pyboxbuilder[pdf]"

# Everything (PythonSCAD + PDF + Shapely)
pip install "pyboxbuilder[all]"
```

## Quick Example

```python
from pyboxbuilder import BoxType, Color, LabelMode, LidBuilder, Project

project = Project("CardGame", game_box_size=(200, 150, 90))
project.define_inventory({"Action Cards": 120, "Victory Tokens": 40})

cards = project.box(
    BoxType.SLIDING,
    "Cards",
    size=(70, 100, None),  # height follows from the cards
    lid=LidBuilder(
        label_mode=LabelMode.FRAMED,
        frame_color=Color("gold"),
    ).titled("Cards"),
)
cards.cards("Deck", component="Action Cards", count=120, size=(63.5, 88.0))

tokens = project.box(BoxType.CAP, "Tokens", size=(80, 70, 30))
tokens.compartment("Tokens", component="Victory Tokens", count=40)

project.verify_inventory(strict=True)
project.export("output/")
```

Browse 39 complete board game inserts in the
[example catalog](https://github.com/pinkfish/pythonscad_boxes/tree/main/boxes)
and the [Quickstart guide](https://pinkfish.github.io/pythonscad_boxes/stable/quickstart.html).

## Documentation

- **Stable docs** — https://pinkfish.github.io/pythonscad_boxes/stable/
- **Dev docs** — https://pinkfish.github.io/pythonscad_boxes/dev/
- **Release notes** — https://github.com/pinkfish/pythonscad_boxes/releases

## Development

```sh
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install

# Quality checks (blocking in CI)
ruff check pyboxbuilder/ boxes/
mypy pyboxbuilder/
PYTHONPATH=".:tests" pytest tests/test_pyboxbuilder/ --base-only --ignore=tests/test_pyboxbuilder/render -k "not export" -n auto -q
```

## License

[Apache-2.0](https://github.com/pinkfish/pythonscad_boxes/blob/main/LICENSE)
