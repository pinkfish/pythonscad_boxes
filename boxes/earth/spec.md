# Earth (+ Abundance) Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Earth** (+ Abundance expansion) board game organizer, ported faithfully from `boxes/earth/earth.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `288.0mm (Width) x 288.0mm (Length) x 72.0mm (Height)`
* **Board Reserve**: `16.8mm` (6 player boards `12.6mm` + 2 middle boards `4.2mm` at `Z = 55.2 .. 72.0mm`)
* **Standing Abundance Boards**: 6 boards (`12.6mm` total width x `241mm` length x `57mm` height) along the right wall (`X = 275.4 .. 288.0mm, Y = 46 .. 287mm`)
* **Main Insert Usable Height**: `55.2mm` (`Z = 0.0 .. 55.2mm`)
* **Wall / Floor / Lid Thickness**: `3.0mm` / `2.0mm` / `2.0mm` (`2.0mm` walls on narrow `SeedBox`)
* **Earth Cards**: `62.0mm x 93.0mm` (`0.6mm` per card)

---

## 2. Complete Component Inventory (26 Boxes)

| Component | Dimensions (`W x L x H` mm) | Position (`X, Y, Z` mm) | Box Type | Storage |
|---|---|---|---|---|
| `CardBox_Flora` | `68.0 x 99.0 x 55.2` | `(0.0, 0.0, 0.0)` | Sliding | Earth deck #1 |
| `CardBox_Terrain` | `68.0 x 99.0 x 55.2` | `(68.0, 0.0, 0.0)` | Sliding | Earth deck #2 |
| `CardBox_Events` | `68.0 x 99.0 x 55.2` | `(136.0, 0.0, 0.0)` | Sliding | Earth deck #3 |
| `CardBox_Abundance` | `68.0 x 99.0 x 55.2` | `(136.0, 99.0, 0.0)` | Sliding | Earth deck #4 / Abundance |
| `EarthCardBoxSmall` | `68.0 x 99.0 x 18.4` | `(204.0, 0.0, 0.0)` | Sliding | Small Earth card overflow |
| `CompostBox_1` | `68.0 x 99.0 x 18.4` | `(204.0, 0.0, 18.4)` | Filament Hinge | Compost / soil tokens (tray 1) |
| `CompostBox_2` | `68.0 x 99.0 x 18.4` | `(204.0, 0.0, 36.8)` | Filament Hinge | Compost / soil tokens (tray 2) |
| `SeedBox` | `16.0 x 46.0 x 72.0` | `(272.0, 0.0, 0.0)` | Cap | Seed tokens (full-height corner) |
| `TopSpacedBox` | `46.0 x 240.5 x 15.0` | `(242.0, 46.0, 57.0)` | No-Lid | Hollow spacer above Abundance boards |
| `EcosystemCardBox` | `68.0 x 99.0 x 24.2` | `(0.0, 99.0, 0.0)` | Sliding | 32 Ecosystem cards |
| `FaunaCardBox` | `68.0 x 99.0 x 18.8` | `(0.0, 99.0, 24.2)` | Sliding | 23 Fauna cards |
| `IslandCardBox` | `68.0 x 99.0 x 12.2` | `(0.0, 99.0, 43.0)` | Sliding | 10 Island cards |
| `ClimateCardBox` | `68.0 x 99.0 x 11.0` | `(68.0, 99.0, 0.0)` | Sliding | 10 Climate cards |
| `SoloCardBox` | `68.0 x 99.0 x 8.6` | `(68.0, 99.0, 11.0)` | Sliding | 6 Solo cards |
| `SeasonCardBox` | `68.0 x 99.0 x 12.2` | `(68.0, 99.0, 19.6)` | Sliding | 12 Season cards |
| `AbundanceOtherCardBox` | `68.0 x 99.0 x 11.0` | `(68.0, 99.0, 31.8)` | Sliding | 10 Abundance other cards |
| `StartBox` | `68.0 x 99.0 x 12.4` | `(68.0, 99.0, 42.8)` | Cap | Start disk, active token, score override |
| `PlayerBox_Red` .. `PlayerBox_Pink` (6) | `68.0 x 99.0 x 9.2` each | `(204.0, 99.0, 0..46.0)` | Slipover | Readiness token + 5 leaf tokens per player |
| `CanopyBox` | `163.9 x 89.0 x 55.2` | `(0.0, 198.0, 0.0)` | Filament Hinge | Tree trunks & canopies |
| `ScorePadBox` | `111.0 x 89.0 x 7.0` | `(163.9, 198.0, 0.0)` | No-Lid | Score pads (`81 x 99 x 5mm`) |
| `SproutBox` | `111.0 x 89.0 x 48.2` | `(163.9, 198.0, 7.0)` | Filament Hinge | 195 Sprout cubes (`8mm`) |
