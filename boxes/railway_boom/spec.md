# Railway Boom Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Railway Boom** board game organizer, ported faithfully from `boxes/railway_boom/railway_boom.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `209.0mm (Width) x 300.0mm (Length) x 46.0mm (Height)`
* **Board Reserve**:
  * Main game board (`10.0mm`) at `Z = 36.0 .. 46.0mm` (`full_usable_height = 36.0mm`)
  * 4 Player boards (`161 x 228 x 8.0mm`) at `X = 0..161mm, Y = 0..228mm, Z = 28.0 .. 36.0mm` (`usable_height = 28.0mm` beneath player boards)
* **Wall / Floor / Lid Thickness**: `3.0mm` / `2.0mm` / `2.0mm` (`1.5mm` walls on narrow `TouristTileBox`, `IndicatorBox`, `ResourceBox_Money`)
* **Standard Cards**: `67.0mm x 92.0mm` (`0.7mm` per card)
* **Small Cards**: `46.0mm x 66.0mm`

---

## 2. Complete Component Inventory (21 Boxes)

| Component | Dimensions (`W x L x H` mm) | Position (`X, Y, Z` mm) | Box Type | Storage |
|---|---|---|---|---|
| `PlayerBox_Green` | `103.5 x 108.0 x 14.0` | `(0.0, 0.0, 0.0)` | Cap | Green trains, stations, cubes, discs |
| `PlayerBox_Blue` | `103.5 x 108.0 x 14.0` | `(0.0, 0.0, 14.0)` | Cap | Blue trains, stations, cubes, discs |
| `PlayerBox_Red` | `103.5 x 108.0 x 14.0` | `(103.5, 0.0, 0.0)` | Cap | Red trains, stations, cubes, discs |
| `PlayerBox_Yellow` | `103.5 x 108.0 x 14.0` | `(103.5, 0.0, 14.0)` | Cap | Yellow trains, stations, cubes, discs |
| `SpacerPlayerBoardBox` | `47.0 x 108.0 x 8.0` | `(161.0, 0.0, 28.0)` | No-Lid | Hollow spacer beside player boards |
| `StationCardBox` | `98.0 x 73.0 x 28.0` | `(0.0, 108.0, 0.0)` | Sliding | 36 Station cards (`67 x 92mm`) |
| `ObjectiveCardBox` | `98.0 x 73.0 x 17.6` | `(98.0, 108.0, 0.0)` | Sliding | 18 Objective cards |
| `RouteCardBox` | `98.0 x 73.0 x 9.9` | `(98.0, 108.0, 17.6)` | Sliding | 7 Route cards |
| `TouristTileBox` | `13.0 x 73.0 x 36.0` | `(196.0, 108.0, 0.0)` | Sliding | 14 Tourist city tiles |
| `SmallCardBox_Carriages` | `72.0 x 52.0 x 28.0` | `(0.0, 181.0, 0.0)` | Sliding | 30 Carriage cards (`46 x 66mm`) |
| `SmallCardBox_Locomotives` | `72.0 x 52.0 x 28.0` | `(72.0, 181.0, 0.0)` | Sliding | 26 Locomotive cards |
| `SmallCardBox_CityTiles` | `52.0 x 52.0 x 28.0` | `(144.0, 181.0, 0.0)` | Sliding | 36 Regular city tiles |
| `FrontSpacerBox` | `13.0 x 52.0 x 36.0` | `(196.0, 181.0, 0.0)` | No-Lid | Hollow spacer beside city tiles |
| `DevelopmentCardBox_1` | `72.0 x 52.0 x 36.0` | `(0.0, 233.0, 0.0)` | Sliding | Development cards (deck 1 of 2) |
| `DevelopmentCardBox_2` | `72.0 x 52.0 x 36.0` | `(72.0, 233.0, 0.0)` | Sliding | Development cards (deck 2 of 2) |
| `ResourceBox_Materials` | `65.0 x 33.5 x 18.0` | `(144.0, 233.0, 0.0)` | Cap | Material resource tokens |
| `ResourceBox_VP` | `65.0 x 33.5 x 18.0` | `(144.0, 233.0, 18.0)` | Cap | Victory point tokens |
| `ResourceBox_Tech` | `65.0 x 33.5 x 18.0` | `(144.0, 266.5, 0.0)` | Cap | Technology tokens |
| `ResourceBox_Coal` | `65.0 x 33.5 x 18.0` | `(144.0, 266.5, 18.0)` | Cap | Coal tokens |
| `IndicatorBox` | `77.27 x 14.0 x 36.0` | `(0.0, 285.0, 0.0)` | Sliding | 4 Octagonal indicator tokens |
| `ResourceBox_Money` | `66.73 x 14.0 x 36.0` | `(77.27, 285.0, 0.0)` | Cap | Money tokens |
