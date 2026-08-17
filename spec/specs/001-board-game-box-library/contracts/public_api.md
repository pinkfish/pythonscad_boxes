# Contracts: Board Game Box Library

**Hard constraint**: All geometry uses `pybosl2.shapes3d` / `pybosl2.shapes2d`. Native `pythonscad` or OpenSCAD built-ins MUST NOT be imported in `pyboxbuilder/`.

Package: `pyboxbuilder/` | Import: `from pyboxbuilder import Project, BoxType, ...`

## Import Contract

```python
from pyboxbuilder import (
    Project,                        # Top-level entry point
    BoxType,                        # Enum: SLIDING, CAP, HINGE, ...
    LabelMode,                      # Enum: FRAMED, FRAMELESS
    PatternType,                    # Enum: HEX_GRID, GRID, VORONOI
    ScoopSide,                      # Enum: FRONT, BACK, LEFT, RIGHT
    FingerCut,                      # Enum: THROUGH_FLOOR, SCOOP
    Color,                          # RGBA dataclass with named presets
    LidBuilder,                     # Lid decoration builder
    PatternBuilder,                 # Through-hole pattern builder
    ExportResult,                   # Result of Project.export()
)
```

## Project (`pyboxbuilder/project.py`)

```
Project(
    name: str,
    *,
    game_box_size: tuple[float, float, float],
    wall_thickness: float = 2.0,
    floor_thickness: float = 1.6,
    lid_thickness: float = 2.0,
    gap_threshold: float = 10.0,
    min_spacer_dim: float = 15.0,
)
```

### `.box(box_type, label, *, size, ...)` → Typed Builder

`@overload` signatures (12 total) — return type depends on `box_type`:

| box_type | Returns | Type-specific kwargs |
|----------|---------|---------------------|
| `BoxType.SLIDING` | `SlidingBoxBuilder` | `two_layer`, `two_layer_top_lid_ratio`, `two_layer_vee_shape` |
| `BoxType.CAP` | `CapBoxBuilder` | `cap_height`, `finger_hold_height`, `finger_hold_len`, `lid_wall_thickness` |
| `BoxType.HINGE` | `HingeBoxBuilder` | (type-specific fields) |
| `BoxType.FILAMENT_HINGE` | `FilamentHingeBoxBuilder` | ... |
| `BoxType.MAGNETIC` | `MagneticBoxBuilder` | `magnet_diameter`, `magnet_height`, `magnet_count_*` |
| `BoxType.INSET` | `InsetBoxBuilder` | ... |
| `BoxType.SLIDING_CATCH` | `SlidingCatchBoxBuilder` | ... |
| `BoxType.SLIPOVER` | `SlipoverBoxBuilder` | ... |
| `BoxType.SLIPOVER_PATH` | `SlipoverPathBoxBuilder` | ... |
| `BoxType.CAP_PATH` | `CapPathBoxBuilder` | ... |
| `BoxType.NO_LID` | `NoLidBoxBuilder` | `stackable` (inside/outside), `stackable_thickness`, `magnet_type` (round/rect), `magnet_size` |
| `BoxType.CARD_LIBRARY` | `CardLibraryBoxBuilder` | ... |

All builders share these base kwargs: `size: tuple[float, float, float] | None = None` (auto-computed from compartments if omitted), `position: tuple[float, float, float] | None = None` (manual packing position), `expandable: bool = True`, `expandable_width: bool = True`, `expandable_length: bool = True`, `no_rotate: bool = False` (prevent 3D packer rotation, FR-013c), `stackable: str | None = None` (`"inside"`/`"outside"`, no-lid only, FR-038), `stackable_thickness: float | None = None`, `magnet_type: str | None = None` (`"round"`/`"rect"`, FR-039), `magnet_size: tuple[float, float, float] | None = None`, `wall_thickness: float | None = None`, `floor_thickness: float | None = None`, `lid_thickness: float | None = None`, `lid: LidBuilder | None = None`.

### `.export(out_dir: str | Path) -> ExportResult`

Builds all geometry, packs boxes, generates spacers, writes 3MF files. Cached layout (SHA-256 hash). Hausdorff-gated file writes.

## LidBuilder (`pyboxbuilder/lid/builder.py`) — Fresh Design

```
LidBuilder(
    text: str | None = None,
    label_mode: LabelMode = LabelMode.FRAMED,
    diagonal: bool = False,
    text_color: Color | None = None,
    frame_color: Color | None = None,
    pattern: PatternBuilder | None = None,
    pattern_color: Color | None = None,
    min_text_height_mm: float = 4.0,
    border_margin_mm: float = 5.0,
    mmu_label: LidBuilder | None = None,      # Override for MMU export mode
    single_label: LidBuilder | None = None,    # Override for single-color export mode
)
```

**Per-mode overrides**: `mmu_label` and `single_label` allow different label specifications per export mode. When set, their fields override the parent LidBuilder for that mode. The common use case is `label_mode=LabelMode.FRAMED` (default) with `mmu_label=LidBuilder(label_mode=LabelMode.FRAMELESS)` — single-color uses a framed recessed label, MMU uses a frameless text-only label. Unset modes fall back to the parent fields.

**Fresh design** — not constrained by legacy `LidPlate`/`build_lid()`.

Default colors when `None`: `text_color` → `Color.WHITE()`, `frame_color` → contrasting hue from body, `pattern_color` → third contrasting hue.

**Compartment labels per mode**: Single-color exports use engraved 0.2mm recessed cutout text (visible by depth contrast). MMU exports use 0.2mm raised second-color text (visible by material color contrast). This is controlled by a `mode` parameter in `build_floor_label()`.

## PatternBuilder (`pyboxbuilder/lid/builder.py`)

```
PatternBuilder(
    type: PatternType = PatternType.HEX_GRID,
    colors: tuple[Color, ...] = (),
    spacing: float | None = None,
)
```

Pattern fills are `Callable[[float, float, float], Bosl2Solid]` — functions from (width, length, thickness) to through-hole cutout solid. Tessellation generators (penrose, pentagon, voronoi) are borrowed from the existing codebase. Multiple `colors` assign different elements within the pattern.

## CompartmentBuilder (`pyboxbuilder/compartments/builder.py`)

```
CompartmentBuilder(
    label: str,
    size: tuple[float, float],
    depth: float,
    rounded_corners: float = 0.0,
    cut: Cut | FingerCut | None = None,    # None → no finger cut
)
```

`cut` is **one** field for a decision that used to be spread over three (`finger_scoop`, `finger_cut`, `scoop_side`) which had to be kept in agreement — `finger_cut=SCOOP` did nothing without `finger_scoop=True`, and a `scoop_side` on a compartment with no scoop was silently dropped. `None` means no cut. Anything else asks for one and says what it is:

```
cut = FingerCut.SCOOP                        # widened by Cut.of
cut = Cut.scoop(side=ScoopSide.FRONT)
cut = Cut.through_floor(width=30.0)
cut = Cut(kind=FingerCut.SCOOP, base_radius=6.0, mouth_flare=3.0)
```

`kind` says what sort of cut it is (FR-060). **THROUGH_FLOOR** — the default — is a hole through the box's base at the wall, so a thumb pushes the contents up from underneath: what a stack needs, since a stack that fills its well leaves no side for a finger to reach down. **SCOOP** is the dip in the side, for loose pieces, and it leaves the base solid.

`side` defaults to **None**, not to a member: it is derived — the compartment's shorter wall (FR-068), overridden to the lid's exit wall on a sliding box (FR-069). Pinning `FRONT` here would put a card box's cut in the long face and, on a sliding box, through the lid's groove. The remaining fields (`width`, `depth`, `offset`, `base_radius`, `mouth_flare`, `roll_rise`, `face_fillet`) name the same numbers as `finger_hole()` below and default to `None`, meaning *derive it*.

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

Every dimension here is a **full width or a radius of curvature**, never a half of something else: the outline is stated as a width (FR-051), and a signature offering `radius` *and* `width`, one of them half the other, invites the caller to set the wrong one. `radius` is kept as a deprecated alias for one release and raises a `DeprecationWarning`.

The cut hangs from the top of the **interior** (FR-064), not the outer rim, and `depth` is read to the deepest point of the material removed (FR-006b). `width` and `base_radius` are independent (FR-055), and the radius given is the radius built — the straight run between the circles is what gives when the depth is tight, not the circle (FR-054). A no-lid box gets a pair of these automatically (FR-047); `box(..., auto_finger_holes=False)` or naming any hole of your own suppresses them (FR-047b).

## Color (`pybosl2.Color`, re-exported from `pyboxbuilder`)

```
Color([r, g, b])        # list/tuple of floats 0.0–1.0
Color("white")          # webcolor name
Color("darkgreen")      # webcolor name
Color("gold")           # webcolor name
# no presets — use Color("name") at the call site
```

## File Naming

```
{out_dir}/{project.name}/mmu/{label}_body.3mf
{out_dir}/{project.name}/mmu/{label}_lid.3mf
{out_dir}/{project.name}/mmu/spacer_{N}.3mf
{out_dir}/{project.name}/single/{label}_body_single.3mf
{out_dir}/{project.name}/single/{label}_lid_single.3mf
{out_dir}/{project.name}/single/spacer_{N}_single.3mf
```

No-lid box types skip `_lid` files.

## Error Contract

| Condition | Error | Message includes |
|-----------|-------|-----------------|
| Invalid BoxType | `ValueError` | Valid enum values |
| Unknown type-specific kwarg | `TypeError` | Builder name, valid field names |
| Duplicate box label | `ValueError` | The duplicate label |
| Compartment depth > interior | `ValueError` | Label, depth, max allowed |
| Boxes overflow container | `ValueError` | Which boxes overflow, by how much |
| Empty mesh (0 facets) | Warning (not error) | Box label, skipped |
