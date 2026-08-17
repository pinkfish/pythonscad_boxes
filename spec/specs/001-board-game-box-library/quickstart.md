# Quickstart: Board Game Box Library

**Package**: `pyboxbuilder/` | **Import**: `from pyboxbuilder import ...`

Every scenario below is executable as written. That is the point of the file:
it drifted from the code once — advertising `Color.WHITE()`, which the plan
explicitly bans, and `two_layer=True`, which the library read nowhere — and a
quickstart that does not run is worse than none.

## Prerequisites

- Python 3.12+
- PythonSCAD dev build (for geometry; the layout and packing run without it)
- pybosl2 >= 0.7.7, numpy, fpdf2

```sh
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
```

## The Single Import

```python
from pyboxbuilder import (
    Project,
    BoxType, LabelMode, PatternType, ScoopSide, FingerCut, Cut,
    Color, LidBuilder, PatternBuilder,
    columns, rows, stack, run,
)
```

## Scenario 1: A card box, described by its cards

```python
from pyboxbuilder import BoxType, Color, LabelMode, LidBuilder, Project

project = Project("CardGame", game_box_size=(200, 150, 90))

cards = project.box(
    BoxType.SLIDING, "Cards",
    size=(70, 100, None),                  # height follows from the cards
    lid=LidBuilder(label_mode=LabelMode.FRAMED,
                   frame_color=Color("gold")).titled("Cards"),
)
cards.cards("Deck", count=120, size=(63.5, 88.0))   # 120 x 0.6mm = a 72mm stack

project.export("output/")
```

**Expected**: the well is the card plus its slack; the box's height is the
stack plus the floor and the lid. Nothing in the file computes either.

## Scenario 2: A tray of loose pieces

```python
from pyboxbuilder import BoxType, FingerCut, Project

project = Project("Tokens", game_box_size=(200, 150, 60))

tokens = project.box(BoxType.NO_LID, "Tokens", size=(80, 60, 25))
tokens.compartment("Wood", holds_pieces=True, cut=FingerCut.SCOOP)

project.show()
```

**Expected**: one well filling the interior, its corners and floor rounded so a
finger sweeps a piece out, and the tray's own pair of lifting holes in its
longer walls. No size, no depth and no radius are given: each has a default that
suits the box it is in.

## Scenario 3: Dividing a box evenly

```python
from pyboxbuilder import BoxType, Project

project = Project("Divided", game_box_size=(200, 150, 60))

box = project.box(BoxType.NO_LID, "Sorted", size=(100, 80, 30))
for i in range(4):
    box.compartment(f"Slot{i + 1}", width_ratio=0.25)

project.show()
```

**Expected**: four equal wells that fit. A ratio is a share of the room the
wells actually have, so four quarters fit rather than overflowing by the three
dividing walls between them.

## Scenario 4: A lid style worn by many boxes

```python
from pyboxbuilder import (
    BoxType, Color, LabelMode, LidBuilder, PatternBuilder, PatternType, Project,
)

project = Project("FancyGame", game_box_size=(300, 200, 80))

STYLE = LidBuilder(
    label_mode=LabelMode.FRAMELESS,
    diagonal=True,
    pattern=PatternBuilder(type=PatternType.HEX, spacing=10.0),
)

for name, colour in (("Treasure", "gold"), ("Traps", "crimson"), ("Loot", "teal")):
    project.box(
        BoxType.SLIDING, name, size=(90, 70, 40),
        lid=STYLE.titled(name, text_color=Color(colour)),
    )

project.export("output/")
```

**Expected**: three lids sharing a frame, a pattern and a text angle, differing
only where they should. The accent colours the style does not name are derived
to contrast with the body.

## Scenario 5: The minimum text height guard

```python
from pyboxbuilder import BoxType, LidBuilder, Project

project = Project("TinyGame", game_box_size=(100, 80, 30))
project.box(BoxType.SLIDING, "Tiny", size=(30, 20, 20),
            lid=LidBuilder(text="A"))

project.export("output/")
```

**Expected**: the lid exports with no text. "A" on a 30 × 20mm lid computes
below the 4mm minimum, so the label is skipped rather than printed as a smudge.

## Scenario 6: An arrangement, written down

```python
from pyboxbuilder import BoxType, Project, columns, rows, stack

project = Project("BigGame", game_box_size=(300, 200, 80))

project.box(BoxType.SLIDING, "CardBox", size=(110, 75, 50))
project.box(BoxType.CAP, "TokenBox", size=(60, 50, 30))
project.box(BoxType.CAP, "DiceBox", size=(60, 50, 30))
project.box(BoxType.FILAMENT_HINGE, "BitBox", size=(80, 60, 40))

project.arrange(columns(
    "CardBox",
    stack("TokenBox", "DiceBox"),
    "BitBox",
))

result = project.export("output/")
assert result.written

# Exported again, unchanged, nothing is rewritten.
assert not project.export("output/").written
```

**Expected**: positions fall out of the sizes, and a second export writes zero
files. A placed box is not the packer's, so neither `expandable` nor
`no_rotate` needs setting.

## Scenario 7: A box sized entirely by its contents

```python
from pyboxbuilder import BoxType, FingerCut, Project

project = Project("ComputedBox", game_box_size=(200, 150, 60))

cards = project.box(BoxType.SLIDING, "CardBox")     # no size at all
cards.compartment("Deck", size=(90, 65), depth=45, cut=FingerCut.THROUGH_FLOOR)
cards.compartment("SideSlot", size=(55, 45), depth=25)

project.export("output/")
```

**Expected**: the box's footprint and height are computed from its wells, then
expanded to fill its row during packing. A box whose wells *all* fill — nothing
to derive from — is refused with a message naming them.

## Scenario 8: An example's entry point

```python
if __name__ == "__main__":
    run(project)
```

Previews in the PythonSCAD GUI or a notebook; exports under the make build,
which sets `FROM_MAKE=1`.

## Checks

```sh
PYBOXBUILDER_EXPORT_FN=12 python3 -m pytest tests/test_pyboxbuilder/ -q
ruff check pyboxbuilder/ boxes/
mypy pyboxbuilder/
```

All three are blocking in CI.
