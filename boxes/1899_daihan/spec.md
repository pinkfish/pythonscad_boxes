# 1899: Daihan Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **1899: Daihan** board game organizer, ported from `examples/1899daihan.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `225.0mm (Width) x 305.0mm (Length) x 63.0mm (Height)`
* **Board Reserve**: `13.0mm` (Map board and player mats sit atop insert at `Z = 50.0 .. 63.0mm`)
* **Main Insert Usable Height**: `50.0mm` (`Z = 0.0 .. 50.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Hex Tile Width**: `40.0mm` (`tile_radius = 23.09mm`, `thickness = 2.5mm`)

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Track Hex Tiles | 40mm yellow, green, brown, grey tiles | `HexBox_1` .. `HexBox_4` (4 boxes) | Cap Lid | Framed "1899 Daihan" (Dark Green) |
| Corporate Share Certificates | 8 Corporations (Small cards: `48 x 71mm`) | `ShareBox_1`, `ShareBox_2` | Cap Lid | Framed "Shares" (Navy) |
| Paper Currency | 5 Denominations (1, 5, 20, 100, 500) | `MoneyBox` | Cap Lid | Framed "Money" (Gold) |
| Company Charter Markers | Corporate station tokens & discs | `CompanyMarkerBox_1`, `CompanyMarkerBox_2` | Slipover Lid | Framed "Company" |
| Private Company Cards | Full-size cards (`66 x 91mm`) | `PrivateCompanyCards` | Sliding Lid | Framed "Privates" |
| Extra Markers & Round Token | Priority deal marker, phase discs | `ExtraBitsBox` | Slipover Lid | Framed "Extra" |
| Train Cards | Train decks (2, 3, 4, 5, 6, D) | `TrainCardBox` | Sliding Lid | Framed "Trains" (Dark Red) |
| Board & Stock Market | Mounted game board | Sits atop insert (`Z = 50.0 .. 63.0mm`) | Board Layer | Flat storage beneath game lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Hex Tile Storage (`HexBox_1` .. `HexBox_4`)
* **Dimensions**: `147.56mm x 129.0mm x 16.0mm` each.
* **Arrangement**: Stored in 2 columns at `Y = 0.0` and `Y = 129.0mm`, stacked 2 high (`Z = 0.0` and `Z = 16.0mm`).

### 3.2 Share & Money Bank Column (`X = 147.56mm`)
* **Dimensions**: `76.44mm x 258.0mm x 16.66mm` each.
* **Arrangement**: Stacked 3 high from `Z = 0.0` to `Z = 50.0mm`:
  * Tier 1 & 2: `ShareBox_1` & `ShareBox_2` (4 share certificate wells each).
  * Tier 3: `MoneyBox` (5 currency wells).

### 3.3 Upper Accessories (atop HexBoxes, `Z = 32.0 .. 50.0mm`)
* **`CompanyMarkerBox_1` & `CompanyMarkerBox_2`**: `147.56mm x 43.0mm x 18.0mm`.
* **`PrivateCompanyCards`**: `97.0mm x 72.0mm x 18.0mm`.
* **`ExtraBitsBox`**: `50.56mm x 72.0mm x 18.0mm`.

### 3.4 Train Card Box (`Y = 258.0 .. 305.0mm`)
* **Dimensions**: `77.0mm x 54.0mm x 32.8mm`.

---

## 4. 3D Spatial Layout Map

```
+-------------------------------------------------------+-------------------------------+
| HexBox_1 / HexBox_2 (Stacked 2-high, Z: 0..32mm)      | ShareBox_1 (Z: 0..16.6mm)     |
| [ Upper Z: 32..50mm: CompanyMarkerBox_1 & 2,          | ShareBox_2 (Z: 16.6..33.3mm)  |
|   PrivateCompanyCards, ExtraBitsBox ]                 | MoneyBox   (Z: 33.3..50.0mm)  |
+-------------------------------------------------------+                               |
| HexBox_3 / HexBox_4 (Stacked 2-high, Z: 0..32mm)      | (76.4 x 258 x 16.6mm each)    |
+-----------------------------------+-------------------+-------------------------------+
| TrainCardBox (77.0 x 54.0mm)      | Automatic 3D Void Spacers                         |
+-----------------------------------+---------------------------------------------------+
|<------------ 147.6mm ------------>|<--------------------- 77.4mm -------------------->|
```
