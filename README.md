# pyboxbuilder

Board game box and insert design library for PythonSCAD.

`pyboxbuilder` turns a declarative description of what goes in a game box — the
outer size, the boxes, and the compartments inside each — into the CSG geometry
PythonSCAD renders and the 3MF files a slicer prints. Every solid and shape is
built on [`pybosl2`](https://github.com/pinkfish/pybosl2).

The library's governing principle is **good defaults, not options**: in the
ordinary case you describe the storage and get printable files, without tuning
geometry you did not ask about.

## Features

- **Box types** — sliding lid, cap (friction-fit), hinged, filament-hinge,
  magnetic, and no-lid trays, each with its correct mating geometry between
  body and lid.
- **Compartments** — sized absolutely or as ratios of the interior, laid out
  automatically in rows or at explicit coordinates, including non-rectangular
  (hex, circular, silhouette) shapes.
- **Finger cuts** — scoops into compartment walls or floors, and rolled holes in
  the exterior walls, so every piece is easy to lift out.
- **Nested inserts** — sub-boxes auto-packed into the game box, auto-sized to
  fill their rows, with leftover gaps absorbed or turned into hollow spacer
  trays.
- **Lid decoration** — auto-sized labels (framed, frameless, diagonal), cut-through
  patterns (hex, grid, Voronoi, tessellation), and three accent colours per lid.
- **Export** — per-piece multi-colour and single-colour 3MF, a 3D packing-guide
  PDF, and content-based caching so unchanged files are never rewritten.

## Quick example

```python
from pyboxbuilder import BoxType, Color, LabelMode, LidBuilder, Project

project = Project("CardGame", game_box_size=(200, 150, 90))

cards = project.box(
    BoxType.SLIDING, "Cards",
    size=(70, 100, None),                 # height follows from the cards
    lid=LidBuilder(label_mode=LabelMode.FRAMED,
                   frame_color=Color("gold")).titled("Cards"),
)
cards.cards("Deck", count=120, size=(63.5, 88.0))

project.export("output/")
```

More runnable examples live in
[`spec/specs/001-board-game-box-library/quickstart.md`](spec/specs/001-board-game-box-library/quickstart.md)
and under [`boxes/`](boxes/).

## Install

Requires Python 3.12+ and [PythonSCAD](https://www.pythonscad.org/) for
geometry; the layout and packing logic run without it.

```sh
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## Documentation

The API reference is generated from the docstrings with Sphinx and the
sphinx-immaterial theme (left-hand site nav, right-hand "on this page" method
links), and every `pythonscad-example` block renders its example box through the
real PythonSCAD binary.

- **Stable docs** — https://pinkfish.github.io/pythonscad_boxes/stable/
- **Dev docs** — https://pinkfish.github.io/pythonscad_boxes/dev/

## Checks

```sh
PYBOXBUILDER_EXPORT_FN=12 python3 -m pytest tests/test_pyboxbuilder/ -q
ruff check pyboxbuilder/ boxes/
mypy pyboxbuilder/
```

All three are blocking in CI. Ruff also runs locally as a pre-commit hook:

```sh
pre-commit install
```

## License

[Apache-2.0](LICENSE)
