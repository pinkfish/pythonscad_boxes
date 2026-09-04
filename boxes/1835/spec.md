# 1835 Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **1835** (Prussia / Germany 18xx) board game organizer, ported from `examples/1835.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `216.0mm (Width) x 298.0mm (Length) x 50.0mm (Height)`
* **Board & Charter Reserve**: `15.0mm` (Map board and player company charters sit atop insert at `Z = 35.0 .. 50.0mm`)
* **Main Insert Usable Height**: `35.0mm` (`Z = 0.0 .. 35.0mm`)
* **Wall Thickness**: `2.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Hex Track Tile Diameter**: `40.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Hex Track Tiles | Yellow, green, brown track tiles (`40mm`) | `HexBox_1` .. `HexBox_3` (3 tiers) | Sliding Lid | Color-coded Framed lids |
| Bank Money Bills | 8 Denominations (1, 5, 10, 20, 50, 100, 200, 500) | `MoneyBox_1` .. `MoneyBox_3` (3 tiers) | Sliding Lid | Framed "Bank 1-5-10 / 20-50-100 / 200-500" |
| Company Shares & Private Certificates | Prussian, Bavarian, Saxon railroad shares | `SharesBox_1`, `SharesBox_2` | Sliding Lid | Framed "Company Shares" (Dark Red) |
| Priority Deal & Station Tokens | Large wooden priority cylinder & tokens | `MarkerBox` | Sliding Lid | Framed "Markers" (Navy) |
| Board & Charters | Mounted map and national charters | Sits atop insert (`Z = 35.0 .. 50.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Hex Track Tiles & Banknotes (Column 0, `X = 0.0 .. 135.0mm`)
* **`HexBox_1` .. `HexBox_3`**: `135.0mm x 107.5mm x 11.66mm` each, stacked 3 high at `Y = 0.0 .. 107.5mm`.
* **`MoneyBox_1` .. `MoneyBox_3`**: `135.0mm x 107.5mm x 11.66mm` each, stacked 3 high at `Y = 107.5 .. 215.0mm`.

### 3.2 Company Shares & Markers (Column 1, `X = 135.0 .. 216.0mm`)
* **`SharesBox_1` & `SharesBox_2`**: `81.0mm x 138.0mm x 17.5mm` each, stacked 2 high at `Y = 0.0 .. 138.0mm`.
* **`MarkerBox`**: `81.0mm x 77.0mm x 17.5mm` at `Y = 138.0 .. 215.0mm`.

---

## 4. 3D Spatial Layout Map

```
+------------------------------------+------------------------------------+
| HexBox_1 / HexBox_2 / HexBox_3     | SharesBox_1 / SharesBox_2          |
| (Stacked 3-high, 11.66mm each)     | (Stacked 2-high, 17.5mm each)      |
| (135.0 x 107.5mm)                  | (81.0 x 138.0mm)                   |
+------------------------------------+------------------------------------+
| MoneyBox_1 / MoneyBox_2 / Money_3  | MarkerBox                          |
| (Stacked 3-high, 11.66mm each)     | (81.0 x 77.0 x 17.5mm)             |
| (135.0 x 107.5mm)                  |                                    |
+------------------------------------+------------------------------------+
|                               Automatic 3D Void Spacers                 |
|                         (Y = 215.0..298mm, Z = 0..35.0mm)               |
+-------------------------------------------------------------------------+
|<-------------- 135.0mm ----------->|<-------------- 81.0mm ------------>|
```
