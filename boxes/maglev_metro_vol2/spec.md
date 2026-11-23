# Maglev Metro: Volume 2 Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Maglev Metro: Volume 2** expansion organizer, ported faithfully from `boxes/maglev_metro_vol2/maglev_metro_vol2.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `286.0mm (Width) x 286.0mm (Length) x 65.0mm (Height)`
* **Board Reserve**:
  * Top game board (`280 x 281 x 17mm`) at `Z = 48.0 .. 65.0mm`
  * Game board base (`242 x 272 x 17mm`) at `X = 44..286mm, Z = 31.0 .. 48.0mm`
  * 4 Player boards (`145 x 162 x 2.5mm` each = `10mm`) at `X = 0..145mm, Y = 0..162mm, Z = 21.0 .. 31.0mm`
* **Main Insert Usable Height**: `31.0mm` (`Z = 0.0 .. 31.0mm`, with 4 `CommuterBox`es beside the base board at `X = 0..44mm, Z = 31.0 .. 48.0mm`)
* **Wall / Floor / Lid Thickness**: `3.0mm` / `2.0mm` / `3.0mm`

---

## 2. Complete Component Inventory (18 Boxes)

| Component | Dimensions (`W x L x H` mm) | Position (`X, Y, Z` mm) | Box Type | Storage |
|---|---|---|---|---|
| `ExtraTilesBox` | `166.84 x 122.0 x 21.0` | `(0.0, 0.0, 0.0)` | Cap | Loop & Outback small tiles |
| `UpgradeTileBox` | `73.0 x 126.0 x 14.0` | `(0.0, 122.0, 0.0)` | Cap | Upgrade tiles (3 bays) |
| `ExpansionCardsBox` | `73.0 x 96.0 x 14.0` | `(73.0, 122.0, 0.0)` | Sliding | Maps 2 expansion cards (`67 x 90mm`) |
| `MiddleBoxSpacer` | `20.84 x 126.0 x 14.0` | `(146.0, 122.0, 0.0)` | No-Lid | Hollow spacer beside cards |
| `SummonBox` | `166.84 x 38.0 x 14.0` | `(0.0, 248.0, 0.0)` | Cap | Summon tiles (2 bays) |
| `PlayerBoxSpacer` | `166.84 x 39.0 x 7.0` | `(0.0, 122.0, 14.0)` | No-Lid | Hollow spacer beneath player boards |
| `RobotBox_Silver` | `55.61 x 66.2 x 17.0` | `(0.0, 162.0, 14.0)` | Cap | Silver robots |
| `RobotBox_Gold` | `55.61 x 66.2 x 17.0` | `(55.61, 162.0, 14.0)` | Cap | Gold robots |
| `RobotBox_Orange` | `55.61 x 66.2 x 17.0` | `(111.23, 162.0, 14.0)` | Cap | Orange robots |
| `NanobotBox_1` | `55.61 x 57.8 x 17.0` | `(0.0, 228.2, 14.0)` | Cap | Nanobots (set 1) |
| `NanobotBox_2` | `55.61 x 57.8 x 17.0` | `(55.61, 228.2, 14.0)` | Cap | Nanobots (set 2) |
| `NanobotBox_3` | `55.61 x 57.8 x 17.0` | `(111.23, 228.2, 14.0)` | Cap | Nanobots (set 3) |
| `OutbackGhostTilesBox` | `116.16 x 227.0 x 31.0` | `(166.84, 0.0, 0.0)` | No-Lid | Outback & Ghost hex tiles |
| `MetroTokenBox` | `116.16 x 58.0 x 31.0` | `(166.84, 227.0, 0.0)` | Cap | Metro tickets (`25mm` dia) |
| `CommuterBox_Pink` | `44.0 x 71.5 x 17.0` | `(0.0, 0.0, 31.0)` | Cap | Pink commuters |
| `CommuterBox_Aqua` | `44.0 x 71.5 x 17.0` | `(0.0, 71.5, 31.0)` | Cap | Aqua commuters |
| `CommuterBox_Coral` | `44.0 x 71.5 x 17.0` | `(0.0, 143.0, 31.0)` | Cap | Coral commuters |
| `CommuterBox_Purple` | `44.0 x 71.5 x 17.0` | `(0.0, 214.5, 31.0)` | Cap | Purple commuters |
