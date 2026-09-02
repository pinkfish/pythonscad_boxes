# First Class: All Aboard the Orient Express Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **First Class: All Aboard the Orient Express** board game organizer, ported from `examples/first_class.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `217.0mm (Width) x 307.0mm (Length) x 70.0mm (Height)`
* **Board & Rulebook Reserve**: `5.5mm` (`board_thickness = 2.5mm`, `rule_book_thickness = 3.0mm`)
* **Main Insert Usable Height**: `64.5mm` (`Z = 0.0 .. 64.5mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Card Dimensions**: `47.0mm x 70.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Player Meeples, Trains & Cubes (4 Colors) | Yellow, Blue, Red, Green (Meeples, train tokens, scoring cubes) | `PlayerBox_yellow`, `PlayerBox_blue`, `PlayerBox_red`, `PlayerBox_green` (4 boxes) | Cap Lid | Color-coded Framed "Player" |
| Module Cards (Modules A–E) | 5 Module decks (24 cards each) | `CardBox_ModuleA` .. `CardBox_ModuleE` | Sliding Lid | Framed "Module A" .. "Module E" |
| Railroad Base Decks | 94 Railroad cards | `CardBox_RailroadCards` | Sliding Lid | Framed "Railroads" |
| Locomotive Tiles | Locomotive cardboard tiles (`68.5 x 64.5mm`) | `LocomotiveTileBox` | Cap Lid | Framed "Locomotives" (Gold) |
| Score Boards & Player Mats | Main scoreboard + 4 player boards | Sits on top of insert (`Z = 64.5 .. 70.0mm`) | Board Layer | Flat storage beneath game box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Player Boxes (4 Colors, 2x2 Grid)
* **Dimensions**: `108.5mm x 53.0mm x 21.5mm`.
* **Arrangement**: 2 columns of 2 boxes at `Y = 0.0 .. 106.0mm`.
* **Compartments**: Dual-well layout (60% meeples/trains, 40% cubes) with side finger scoops.

### 3.2 Modular Card Boxes (Modules A–E & Railroads)
* **Dimensions**: `54.25mm x 76.0mm x 21.5mm` each.
* **Arrangement**: 4-wide row at `Y = 106.0mm` and `Y = 182.0mm`.
* **Lid Mechanism**: `BoxType.SLIDING`.

### 3.3 Locomotive Tile Box
* **Dimensions**: `74.5mm x 70.5mm x 32.25mm`.
* **Arrangement**: Positioned at `X = 0.0mm`, `Y = 258.0mm`.

---

## 4. 3D Spatial Layout Map

```
+--------------------------------------+----------------------------------------+
| PlayerBox_yellow (108.5 x 53 x 21.5) | PlayerBox_blue (108.5 x 53 x 21.5mm)   |
+--------------------------------------+----------------------------------------+
| PlayerBox_red (108.5 x 53 x 21.5mm)  | PlayerBox_green (108.5 x 53 x 21.5mm)  |
+-------------------+------------------+--------------------+-------------------+
| CardBox_ModuleA   | CardBox_ModuleB  | CardBox_ModuleC    | CardBox_ModuleD   |
| (54.25 x 76mm)    | (54.25 x 76mm)   | (54.25 x 76mm)     | (54.25 x 76mm)    |
+-------------------+------------------+--------------------+-------------------+
| CardBox_ModuleE   | CardBox_Railroad | Automatic Void Spacers                 |
+-------------------+------------------+----------------------------------------+
| LocomotiveTileBox (74.5 x 70.5mm)    | Automatic Void Spacers                 |
+--------------------------------------+----------------------------------------+
```
