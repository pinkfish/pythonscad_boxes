# Contracts: Board Game Box Library

**Hard constraint**: All geometry uses `pybosl2.shapes3d` / `pybosl2.shapes2d`. Native `pythonscad` or OpenSCAD built-ins MUST NOT be imported in `pyboxbuilder/`.

Package: `pyboxbuilder/` | Import: `from pyboxbuilder import Project, BoxType, ...`

## Import Contract

```python
from pyboxbuilder import (
    Project,                        # Top-level entry point
    BoxType,                        # Enum: SLIDING, CAP, HINGE, ...
    LabelMode,                      # Enum: FRAMED, FRAMELESS
    PatternType,                    # Enum: HEX, SQUARE, VORONOI, ...
    ScoopSide,                      # Enum: FRONT, BACK, LEFT, RIGHT
    FingerCut,                      # Enum: THROUGH_FLOOR, SCOOP
    Cut,                            # Record: how a compartment's contents come out
    Color,                          # pybosl2.Color, re-exported
    LidBuilder,                     # Lid decoration builder
    PatternBuilder,                 # Through-hole pattern builder
    ExportResult,                   # Result of Project.export()
    columns, rows, stack,           # Declarative layout
    run,                            # Example entry point: preview, or export
)
```

## Project (`pyboxbuilder/project.py`)

```
Project(
    name: str,
    *,
    game_box_size: tuple[float, float, float] | None = None,   # None → standalone
    wall_thickness: float = 2.0,
    floor_thickness: float = 1.6,
    lid_thickness: float = 2.0,
    rounding: float | None = None,          # None → wall / 2
    inner_rounding: float | None = None,    # None → half the outer radius
    gap_threshold: float = 10.0,
    min_spacer_dim: float = 15.0,
    min_spacer_height: float = 5.0,
    clearance_slack: float = 1.0,
    board_thickness: float = 0.0,
    generate_spacers: bool = True,
    box_defaults: dict | None = None,       # applied to every .box() call
)
```

`box_defaults` carries any keyword `.box()` accepts, so a value every box shares
is written once (FR-000b). A keyword given to `.box()` wins over it; a keyword a
particular builder does not have is ignored there rather than being an error.

### `.build() -> Build`

**The only thing in the library that builds geometry** (FR-046c). Resolves the
layout, sizes every box, and returns every body, lid and spacer as a `Piece`.
`show()` renders what it returns; `export()` writes what it returns. Nothing
else may build a second time.

```
Build(pieces: tuple[Piece, ...], packing: BoxPacking | None)
Piece(label, kind, size, position, builder)   # kind: "body" | "lid" | "spacer"
Piece.solid                                  # built on first use (FR-031a)
```

### `.box(box_type, label, *, size=None, **fields) -> BoxBuilder`

Returns the builder registered for `box_type`. Every keyword must be a field of
that builder: an unknown one raises `TypeError` naming it and listing the valid
fields (FR-000f). `size` axes may individually be `None`, and are then derived
from the box's contents.

| box_type | Returns | Type-specific fields |
|----------|---------|---------------------|
| `BoxType.SLIDING` | `SlidingBoxBuilder` | `catch_radius` |
| `BoxType.CAP` | `CapBoxBuilder` | `cap_height` |
| `BoxType.HINGE` | `HingeBoxBuilder` | `hinge_count`, `hinge_pin_diameter` |
| `BoxType.FILAMENT_HINGE` | `FilamentHingeBoxBuilder` | — |
| `BoxType.MAGNETIC` | `MagneticBoxBuilder` | `magnet_diameter`, `magnet_height`, `magnet_count_width`, `magnet_count_length` |
| `BoxType.INSET` | `InsetBoxBuilder` | — |
| `BoxType.SLIDING_CATCH` | `SlidingCatchBoxBuilder` | — |
| `BoxType.SLIPOVER` | `SlipoverBoxBuilder` | `foot`, `slip` |
| `BoxType.SLIPOVER_PATH` | `SlipoverPathBoxBuilder` | — |
| `BoxType.CAP_PATH` | `CapPathBoxBuilder` | — |
| `BoxType.NO_LID` | `NoLidBoxBuilder` | — |
| `BoxType.PATH` | `PathBoxBuilder` | `path`, `hollow` |
| `BoxType.CARD_LIBRARY` | `CardLibraryBoxBuilder` | — |

Every field listed is read by the geometry. A field that is not is a defect, not
a placeholder (FR-000f) — `two_layer`, `two_layer_top_lid_ratio`,
`two_layer_vee_shape`, `hinge_diameter`, `finger_hold_height`,
`finger_hold_len`, `lid_wall_thickness`, `hinge_gap` and `hinge_length` were all
once documented here and read nowhere.

All builders share: `size`, `position`, `expandable`, `expandable_width`,
`expandable_length`, `no_rotate`, `stackable`, `stackable_thickness`,
`magnet_type`, `magnet_size`, `wall_thickness`, `floor_thickness`,
`lid_thickness`, `rounding`, `inner_rounding`, `lid`, `color`,
`auto_finger_holes`.

**A placed box is not the packer's.** Giving a box a `position` — directly or
through `arrange()` — is what keeps the packer off it; `expandable` and
`no_rotate` then have no effect and need not be set.

### `.arrange(layout, origin=(0, 0, 0)) -> Arrangement`

Resolves a `columns`/`rows`/`stack` tree into a position per box. Every box is
sized first, including the ones sized from their contents, so a box described by
what goes in it can be arranged.

### `.export(out_dir, fn=None, fa=None, fs=None, only=None, force=False) -> ExportResult`

Writes what `build()` returns. Each piece's write is gated on a digest of the
description it was built from (FR-031), recorded in `.fingerprints.json` beside
the files — and a piece that is current is **not built**, so an unchanged box
costs nothing (FR-031a).

- `only` — one label or several; everything else is left alone on disk, neither
  rewritten nor deleted.
- `force` — rebuild and rewrite everything.

### `.show(show_lids=False, remove_layers=0, only=None, lids_only=False, fn=None, fa=None, fs=None)`

Renders what `build()` returns. A shown lid carries its decoration.

- `only` — show just these boxes, and build only those (FR-046d).
- `lids_only` — the lids without their bodies, for looking at a label or a
  pattern the body would otherwise hide. Implies `show_lids`.

### `Piece.solid`

Built on first use, and kept. Everything that *identifies* a piece — its label,
size, position, and the description it would be built from — is available
without building it, which is what lets an export decide before it pays.

## Commands

```sh
pybox export boxes/emberleaf/emberleaf.py     # print quality, only what changed
pybox export --all --out output/
pybox export boxes/earth/earth.py --box EarthCardBox1
pybox export boxes/earth/earth.py --force
pybox list --all                              # every insert's boxes

make export                                   # every insert
make export-emberleaf                         # one insert
make export FORCE=1
make show-emberleaf ARGS="--box CommonBox --lids"
```

An example script takes the same arguments directly:

```sh
python3 boxes/emberleaf/emberleaf.py --box CommonBox --lids
python3 boxes/emberleaf/emberleaf.py --lids-only
python3 boxes/emberleaf/emberleaf.py --export --box CommonBox
```

Producing print-quality files is always a command you run (FR-031b). Nothing
does it as a side effect: at 256 facets a full insert takes tens of seconds to
minutes.

## LidBuilder (`pyboxbuilder/lid/builder.py`)

```
LidBuilder(
    text: str | None = None,
    label_mode: LabelMode | None = None,      # None → FRAMED
    diagonal: bool | None = None,             # None → False
    text_color: Color | None = None,
    frame_color: Color | None = None,
    pattern: PatternBuilder | None = None,
    pattern_color: Color | None = None,
    min_text_height_mm: float | None = None,  # None → 4.0
    border_margin_mm: float | None = None,    # None → border + 2mm inset
    label_clearance_mm: float | None = None,  # margin round the glyphs; None → 0
    mmu_label: LidBuilder | None = None,      # override for MMU export
    single_label: LidBuilder | None = None,   # override for single-colour export
)
```

`.titled(text, **overrides)` returns a copy carrying one box's text, so a lid
*style* is written once and worn by many boxes.

**Every field defaults to `None`** so "not mentioned" is representable, which is
what a per-mode override needs: `.for_mode(mode)` applies only the fields the
override actually names. The resolved values are read through `.mode`,
`.is_diagonal`, `.min_text_height` and `.border_margin`. Deciding intent by
comparing against a field's default instead — which `resolve_for_mode()` did —
meant an override could not state `FRAMED`, could not turn `diagonal` off, and
always imposed its own margins.

**A label is inlaid, not embossed** (FR-022a). The lettering and, in framed
mode, the striped grid behind it are cut into the lid to a top-layer depth and
filled flush, so the lid's top face stays flat and only the *colour* of the top
layer changes. Only what changes colour is cut: the plate between them is left
alone, which is what makes it the box's own material with no insert of its own.

Accent defaults (FR-022): lettering **black**, striped grid **light grey**,
backing the **box's material**. Fixed rather than derived from the body, because
a hue shifted off the box's own colour is no more legible against it. An unset
accent is *no colour*, not a subtle default, so they are resolved rather than
passed through.

A single-colour export has no second material to inlay, so it engraves the text
instead (FR-036).

`decorate_lid` returns `DecoratedLid(solid, inserts)`, where each insert is a
`LidInsert(solid, color)` — the colour travels **beside** the geometry, because
a pybosl2 solid has none to read back (`.color` is the method that sets one).
`DecoratedLid.solids` is the geometry alone, for a caller that only writes it
out.

Where a pattern meets a frameless label, holes stop at the glyphs themselves;
`label_clearance_mm` adds a margin round them and defaults to `0`.

## PatternBuilder (`pyboxbuilder/lid/builder.py`)

```
PatternBuilder(
    type: PatternType = PatternType.HEX,
    colors: tuple[Color, ...] = (),
    spacing: float | None = None,      # pitch; None → shorter side / 8, min 5mm
    web: float | None = None,          # material between holes; None → 1.6mm
    border: float | None = None,       # solid margin all round; None → 8mm
)
```

A pattern is specified by the **pitch** and the **web** between holes; the hole
size follows. The web is the one with a right answer — it is what prints and
what carries the lid. `border` is the lid's solid margin — `LID_BORDER_MM`, 8mm — the band the lid is
picked up by and, on a sliding lid, the band that rides in the grooves. The
label measures from the same border and then sits `LABEL_INSET_MM` (2mm)
further in, so `LidBuilder.border_margin` is 10mm: one band of plain lid, with
the pattern stopping at it and the text set inside it.

The pattern **reaches** that border rather than stopping short of it: the
lattice is anchored on the area's centre, run out a full cell past every edge,
and clipped to it — so the holes at the edge are partial and opposite edges are
cut alike. Holes also stop at the label's own shape — its shape, not its
bounding box, since a diagonal label's box covers most of the lid (FR-023).

`PatternType` contains only patterns the library draws: `NONE`, `SQUARE`,
`CIRCLE`, `HEX`, `DENSE_HEX`, `TRIANGLE`, `DENSE_TRIANGLE`, `OCTAGON`,
`VORONOI`. A member with no fill raises rather than substituting another
member's shape (FR-000g).

## Compartments (`BoxBuilder.compartment`, `BoxBuilder.cards`)

```
box.compartment(
    label: str,
    *,
    size: tuple[float, float] | None = None,   # None → fill the interior
    width_ratio: float | None = None,          # share of the room the wells have
    length_ratio: float | None = None,
    depth: float | None = None,                # None → run to the floor
    holds_pieces: bool = False,                # tray: round corners and floor
    rounded_corners: float = 0.0,
    cut: Cut | FingerCut | None = None,
    no_rotate: bool = False,
    shape_file: str | None = None,
    position: tuple[float, float] | None = None,
    elements: tuple[CompartmentElement, ...] = (),
    element_margin: float = 0.0,
) -> CompartmentBuilder
```

```
box.cards(
    label: str,
    *,
    count: int,
    size: tuple[float, float],        # one card
    thickness: float = 0.6,           # sleeved cards run nearer 0.8
    slack: float = 1.0,
    cut = FingerCut.THROUGH_FLOOR,
    **compartment_kwargs,
) -> CompartmentBuilder
```

A card box is described by its cards: the well's footprint and depth follow, and
so does the box's height if its `size` leaves that axis `None` (FR-003b).

A **ratio is a share of the room the wells actually have** — the interior less
the spacing the layout puts before, between and after them — so N wells at `1/N`
fit (FR-003c). A well whose size was derived that way is never rotated by the
layout (FR-003d).

`cut` is **one** field for a decision that used to be spread over three
(`finger_scoop`, `finger_cut`, `scoop_side`) which had to be kept in agreement.
`None` means no cut; anything else asks for one and says what it is:

```
cut = FingerCut.SCOOP                        # widened by Cut.of
cut = Cut.scoop(side=ScoopSide.FRONT)
cut = Cut.through_floor(width=30.0)
cut = Cut(kind=FingerCut.SCOOP, base_radius=6.0, mouth_flare=3.0)
```

**THROUGH_FLOOR** — the default for a card stack — is a hole through the box's
base at the wall, so a thumb pushes the contents up from underneath: what a
stack needs, since a stack that fills its well leaves no side for a finger to
reach down (FR-060). **SCOOP** is the dip in the side, for loose pieces, and it
leaves the base solid.

`side` defaults to **None**, not to a member: it is derived — the compartment's
shorter wall (FR-068), overridden to the lid's exit wall on a sliding box
(FR-069).

## Finger holes on a box (`BoxBuilder.finger_hole`)

```
box.finger_hole(
    side: ScoopSide,                       # which exterior wall
    *,
    width: float = 28.0,                   # the cut's full width — adult fingertip
    depth: float | None = None,            # reach below the wall top; None → half the width
    offset: float = 0.0,                   # shift along the wall from its midpoint
    base_radius: float | None = None,      # base curve; None → half the width
    mouth_flare: float | None = None,      # roll at the rim; None → 3mm
    roll_rise: float | None = None,        # how far the roll reaches down; None → 1.6 x flare
    face_fillet: float | None = None,      # face roundover; None → wall_thickness / 2
    radius: float | None = None,           # DEPRECATED — half the width; warns
) -> FingerHoleBuilder
```

**These are the names `FingerHoleBuilder` uses too** (FR-006a). They were
`radius`, `bottom_radius`, `rounding_radius` and `rounding_edge` on the record
while the method took the four above, so every number in a finger cut had two
names and one of the pairs differed by a factor of two.

Every dimension here is a **full width or a radius of curvature**, never a half
of something else. The cut hangs from the top of the **interior** (FR-064), and
`depth` is read to the deepest point of the material removed (FR-006b). `width`
and `base_radius` are independent (FR-055), and the radius given is the radius
built (FR-054). A no-lid box gets a pair of these automatically (FR-047);
`box(..., auto_finger_holes=False)` or naming any hole of your own suppresses
them (FR-047b), as does a polygon footprint (FR-047c).

## BoxSpec (`pyboxbuilder/box/spec.py`)

The frozen record a box type is built from, and **the one place every geometric
default is declared** (FR-000e). A box type reads `spec.wall_thickness`; it does
not carry a fallback of its own. Derive a variant with `dataclasses.replace`.

Assembled only by `build_spec(project, builder, size)`.

## BoxTypeBase (`pyboxbuilder/box/base.py`)

Every box type inherits it. `build_body` is required; `build_lid`, `interior`,
`preferred_scoop_side`, `lid_rounded_edges`, `wall_tops` and `interior_mask` have
defaults a subclass overrides. These were discovered with `getattr` — a protocol
no reader can see and no checker can verify, where a misspelled override is a
method that never runs and never complains.

## Color (`pybosl2.Color`, re-exported from `pyboxbuilder`)

```
Color([r, g, b])        # list/tuple of floats 0.0–1.0
Color("white")          # webcolor name
Color("darkgreen")
```

No presets: use `Color("name")` at the call site.

## File Naming

```
{out_dir}/{project.name}/mmu/{label}_body.3mf
{out_dir}/{project.name}/mmu/{label}_lid.3mf
{out_dir}/{project.name}/mmu/spacer_{N}_body.3mf
{out_dir}/{project.name}/single/{label}_body_single.3mf
{out_dir}/{project.name}/single/{label}_lid_single.3mf
{out_dir}/{project.name}/single/spacer_{N}_body_single.3mf
{out_dir}/{project.name}/layout.pdf
```

No-lid box types skip `_lid` files. Each directory also carries a
`.fingerprints.json` recording what each file was built from.

## Error Contract

| Condition | Error | Message includes |
|-----------|-------|-----------------|
| Invalid BoxType | `KeyError` | The unregistered type |
| Unknown type-specific kwarg | `TypeError` | Builder name, the unknown field, valid field names |
| Compartment ratio out of (0, 1] | `ValueError` | Compartment label, the ratio |
| Ratios summing above 1.0 | `ValueError` | Box label, the sum, each contributor |
| Compartments overflow the interior | `ValueError` | Box label, the interior size |
| Box with no size and only filling wells | `ValueError` | Box label, its wells, what to set |
| Boxes overflow container | `PackingError` | Which boxes overflow, by how much |
| Arrangement larger than the game box | `LayoutError` | Both sizes |
| Cap box too short for its finger cutouts | `ValueError` | Height, minimum, each term, the slipover alternative |
| Standalone project asked to pack | `ValueError` | Project name |
| Pattern with no registered fill | `ValueError` | The member, the available ones |
| Empty mesh (0 facets) | Warning (not error) | Box label, skipped |
