# Ada's Dream Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Ada's Dream** board game organizer, ported faithfully from `boxes/adas_dream/adas_dream.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `212.0mm (Width) x 291.0mm (Length) x 90.0mm (Height)`
* **Board & Player Mat Reserve**: `31.0mm` (`Z = 59.0 .. 90.0mm`)
* **Main Insert Usable Height**: `59.0mm` (`Z = 0.0 .. 59.0mm`)
* **Great Exhibition Board Reserve**: `4.0mm` above the mid/back columns
* **Wall / Floor / Lid Thickness**: `3.0mm` / `2.0mm` / `2.0mm` (with `1.2mm` walls on narrow `BreakthroughBox`)
* **Clearance Slack**: `0.0mm`
* **Standard Cards**: `66.0mm x 91.0mm` (`0.6mm` per card)
* **Assignment Cards**: `48.0mm x 70.5mm` (`30` cards)

---

## 2. Complete Component Inventory (26 Boxes)

| Component | Dimensions (`W x L x H` mm) | Position (`X, Y, Z` mm) | Box Type | Storage |
|---|---|---|---|---|
| `PlayerBox_Red` | `97.0 x 72.0 x 22.4` | `(0.0, 0.0, 0.0)` | Sliding | Red player pieces & starting cards |
| `PlayerBox_Blue` | `97.0 x 72.0 x 22.4` | `(97.0, 0.0, 0.0)` | Sliding | Blue player pieces & starting cards |
| `PlayerBox_Green` | `97.0 x 72.0 x 22.4` | `(0.0, 0.0, 22.4)` | Sliding | Green player pieces & starting cards |
| `PlayerBox_Purple` | `97.0 x 72.0 x 22.4` | `(97.0, 0.0, 22.4)` | Sliding | Purple player pieces & starting cards |
| `ScoringBox` | `97.0 x 40.5 x 14.2` | `(0.0, 0.0, 44.8)` | Cap | 4 columns of scoring tiles (`18 x 34.5mm`) |
| `VisitorBox` | `97.0 x 31.5 x 14.2` | `(0.0, 40.5, 44.8)` | Cap | 4 visitor token bays (Yellow/Purple/Blue/Green) |
| `MoneyBox` | `114.0 x 72.0 x 14.2` | `(97.0, 0.0, 44.8)` | Sliding | Silver coins |
| `OtherCardBox` | `97.0 x 72.0 x 18.4` | `(97.0, 72.0, 0.0)` | Sliding | 24 exhibitor/partner cards |
| `TierCardBox` | `97.0 x 72.0 x 28.0` | `(97.0, 72.0, 18.4)` | Sliding | 40 Tier 1 & Tier 2 partner cards |
| `AssignmentCardBox` | `76.5 x 54.0 x 23.0` | `(0.0, 237.0, 16.0)` | Sliding | 30 assignment cards (`48 x 70.5mm`) |
| `BookBox` | `61.0 x 95.0 x 16.0` | `(36.0, 72.0, 0.0)` | Cap | 12 book tokens (3 columns) |
| `AssignmentBox` | `61.0 x 99.5 x 16.0` | `(36.0, 167.0, 0.0)` | Cap | 16 assignment tiles (2 columns) |
| `DiceBox` | `97.0 x 138.0 x 18.5` | `(0.0, 72.0, 16.0)` | Cap | 50 engine dice (`14.5mm`) |
| `FirstPlayerBox` | `97.0 x 27.0 x 18.5` | `(0.0, 210.0, 16.0)` | Sliding | First player token (`25 x 46.5mm`) |
| `AlternativeObjectiveBox` | `97.0 x 164.0 x 19.5` | `(0.0, 72.0, 34.5)` | Cap | 12 alternative objective tiles (`38.5 x 78.5mm`) |
| `BreakthroughBox` | `19.5 x 54.0 x 16.0` | `(76.5, 237.0, 16.0)` | Sliding | 9 breakthrough tiles (`17 x 21mm`) |
| `ScorePadBox` | `97.0 x 102.5 x 10.0` | `(97.0, 144.0, 0.0)` | Sliding | Score pad (`84.5 x 96.5 x 6mm`) |
| `ProgramBox` | `47.0 x 60.0 x 39.0` | `(97.0, 144.0, 10.0)` | Sliding | 28 program tiles (`25.5 x 41mm`, 2 bays) |
| `UniversityBox` | `47.0 x 42.5 x 39.0` | `(97.0, 204.0, 10.0)` | Sliding | 15 university tiles + workshop bonus discs |
| `ResourceBox_Brass` | `48.5 x 102.5 x 22.0` | `(144.0, 144.0, 10.0)` | Sliding | Brass resource tokens |
| `ResourceBox_Coal` | `48.5 x 102.5 x 22.0` | `(144.0, 144.0, 32.0)` | Sliding | Coal resource tokens |
| `GearBox_AddGears` | `115.0 x 44.5 x 18.0` | `(97.0, 246.5, 0.0)` | Cap | Addition gears |
| `GearBox_SubGears` | `115.0 x 44.5 x 18.0` | `(97.0, 246.5, 18.0)` | Cap | Subtraction gears |
| `GearBox_MulGears` | `115.0 x 44.5 x 18.0` | `(97.0, 246.5, 36.0)` | Cap | Multiplier gears |
| `SpacerSide` | `17.0 x 90.5 x 35.8` | `(194.0, 0.0, 9.0)` | No-Lid | Hollow side spacer above assignment tiles |
| `ObjectiveBox` | `17.0 x 156.0 x 35.8` | `(194.0, 90.5, 9.0)` | Sliding | 24 objective tiles standing on edge (3 bays) |
