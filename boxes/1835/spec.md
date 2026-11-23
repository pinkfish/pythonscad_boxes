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
| Bank Money Bills | 8 Denominations (`1, 5, 10, 20` & `50, 100, 200, 500`) | `MoneyBox_1`, `MoneyBox_2` | Cap Lid | Framed "Money 1-5-10-20" / "Money 50-100-200-500" (Dark Green) |
| Station Tokens, Trains & Private Cards | 33 train cards, 6 private cards, 14 token groups | `MiddleBox` | Cap Lid | Framed "Tokens/Trains" (Dark Slate Blue) |
| Hex Track Tiles | Yellow, green, brown, gray track tiles (`40mm`) | `HexBox_1` .. `HexBox_4` (4 tiers) | Inset Lid | Color-coded Framed "Tiles 1..4" |
| Company Shares | 8 railroad company share decks (2 per box) | `SharesBox_1` .. `SharesBox_4` (4 tiers) | Slipover Lid | Framed "Shares 1..4" (Dark Red) |
| First Player Marker | Large wooden priority cylinder (`20 x 41mm`) | `FirstPlayerBox` | Slipover Lid | Framed "First" (Navy) |
| Board & Charters | Mounted map and national charters | Sits atop insert (`Z = 35.0 .. 50.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacer | Void above `FirstPlayerBox` (`11.0mm` tall) | Derived automatically | No-Lid Tray | Auto spacer matching `SpacerBox` |

---

## 3. Sub-Box Specifications

### 3.1 Hex Track Tile Trays (`Y = 0.0 .. 142.56mm`)
* **`HexBox_1` .. `HexBox_4`**: `215.0mm x 142.56mm x 8.75mm` each, stacked 4-high (`Z = 0.0 .. 35.0mm`).
* 5 partitioned columns per tray for 40mm hex track tiles.

### 3.2 Bank Money & Middle Box (`Y = 142.56 .. 244.56mm`)
* **`MoneyBox_1`**: `215.0mm x 102.0mm x 9.5mm` (`Z = 0.0 .. 9.5mm`), 4 pockets for denominations `1, 5, 10, 20`.
* **`MoneyBox_2`**: `215.0mm x 102.0mm x 8.5mm` (`Z = 9.5 .. 18.0mm`), 4 pockets for denominations `50, 100, 200, 500`.
* **`MiddleBox`**: `215.0mm x 102.0mm x 17.0mm` (`Z = 18.0 .. 35.0mm`), compartments for station tokens, train cards, and private railroad cards.

### 3.3 Company Shares & First Player Row (`Y = 244.56 .. 297.0mm`)
* **`SharesBox_1` .. `SharesBox_4`**: `138.0mm x 52.44mm x 8.75mm` each, stacked 4-high (`X = 0.0 .. 138.0mm`, `Z = 0.0 .. 35.0mm`), 2 share pockets per box.
* **`FirstPlayerBox`**: `77.0mm x 52.44mm x 24.0mm` (`X = 138.0 .. 215.0mm`, `Z = 0.0 .. 24.0mm`).
* **Automatic Spacer**: `78.0mm x 53.44mm x 11.0mm` stacked atop `FirstPlayerBox` (`Z = 24.0 .. 35.0mm`).

---

## 4. 3D Spatial Layout Map

```
+-------------------------------------------------------------------------+
| HexBox_1 / HexBox_2 / HexBox_3 / HexBox_4                               |
| (215.0 x 142.56mm, stacked 4-high, 8.75mm each, Z: 0..35.0mm)           |
+-------------------------------------------------------------------------+
| MoneyBox_1 (9.5mm) / MoneyBox_2 (8.5mm) / MiddleBox (17.0mm)            |
| (215.0 x 102.0mm, stacked 3-high, Z: 0..35.0mm)                         |
+-------------------------------------------+-----------------------------+
| SharesBox_1 .. SharesBox_4                | FirstPlayerBox (Z: 0..24)   |
| (138.0 x 52.44mm, 4-high, 8.75mm each)    | [ Auto Spacer, Z: 24..35 ]  |
+-------------------------------------------+-----------------------------+
|<---------------- 138.0mm ---------------->|<---------- 77.0mm --------->|
```
