# Railway Boom Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Railway Boom** board game organizer, ported from `examples/railway_boom.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `209.0mm (Width) x 300.0mm (Length) x 46.0mm (Height)`
* **Board & Player Mat Reserve**: `18.0mm` (Main game board `10.0mm` + 4 player boards `8.0mm` sit atop insert at `Z = 28.0 .. 46.0mm`)
* **Main Insert Usable Height**: `28.0mm` (`Z = 0.0 .. 28.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Standard Cards**: `67.0mm x 92.0mm`
* **Small Cards**: `46.0mm x 66.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Player Trains, Stations & Cubes (4 Colors) | Red, Yellow, Blue, Green (Trains, houses, cubes, discs) | `PlayerBox_Red` .. `PlayerBox_Green` (4 boxes) | Cap Lid | Color-coded Framed lids |
| Station & Objective Cards | Full decks of station and objective cards (`67 x 92mm`) | `StationCardBox`, `ObjectiveCardBox` | Sliding Lid | Framed "Stations" & "Objectives" |
| Locomotive & Carriage Cards | Mini cards (`46 x 66mm`) | `SmallCardBox_Locomotives`, `SmallCardBox_Carriages` | Sliding Lid | Framed "Locomotives" & "Carriages" |
| City Tiles | Hexagonal/geometric city bonus tiles | `SmallCardBox_CityTiles` | Sliding Lid | Framed "City Tiles" |
| Boards & Player Mats | Folded game board + 4 player boards | Sits atop insert (`Z = 28.0 .. 46.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Player Boxes (Row 1, `Y = 0.0 .. 108.0mm`)
* **Dimensions**: `103.5mm x 108.0mm x 14.0mm` each.
* **Arrangement**: 2 columns across width, stacked 2 high (`Z = 0.0` and `Z = 14.0mm`).
* **Compartments**: Dual-well split (60% trains/stations, 40% cubes/discs) with finger scoops.

### 3.2 Standard Card Boxes (Row 2, `Y = 108.0 .. 181.0mm`)
* **Dimensions**: `98.0mm x 73.0mm x 28.0mm` each.
* **Boxes**: `StationCardBox`, `ObjectiveCardBox`.

### 3.3 Small Card & Tile Boxes (Row 3, `Y = 181.0 .. 233.0mm`)
* **Dimensions**: `72.0mm x 52.0mm x 28.0mm` each.
* **Boxes**: `SmallCardBox_Locomotives`, `SmallCardBox_Carriages`, `SmallCardBox_CityTiles`.

---

## 4. 3D Spatial Layout Map

```
+------------------------------------+------------------------------------+
| PlayerBox_Red / PlayerBox_Blue     | PlayerBox_Yellow / PlayerBox_Green |
| (Stacked 2-high, 14.0mm each)      | (Stacked 2-high, 14.0mm each)      |
| (103.5 x 108.0mm)                  | (103.5 x 108.0mm)                  |
+------------------------------------+------------------------------------+
| StationCardBox (98.0 x 73.0mm)     | ObjectiveCardBox (98.0 x 73.0mm)   |
+-------------------+----------------+---+--------------------------------+
| SmallCardBox_Loco | SmallCardBox_Carr  | SmallCardBox_CityTiles         |
| (72.0 x 52.0mm)   | (72.0 x 52.0mm)    | (72.0 x 52.0mm)                |
+-------------------+--------------------+--------------------------------+
|                       Automatic 3D Void Spacers                         |
|                 (X = 0..209mm, Y = 233..300mm, Z = 0..28.0mm)           |
+-------------------------------------------------------------------------+
```
