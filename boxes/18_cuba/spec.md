# 18Cuba Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **18Cuba** board game organizer, ported from `examples/18cuba.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `225.0mm (Width) x 314.0mm (Length) x 68.0mm (Height)`
* **Board & Hex Track Reserve**: `46.0mm` (`26.0mm` game boards + `20.0mm` hex tile trays sit beneath/atop the insert)
* **Main Insert Usable Height**: `22.0mm` (`rest_height = 68.0 - 26.0 - 20.0`)
* **Wall Thickness**: `1.5mm`
* **Floor Thickness**: `1.0mm`
* **Lid Thickness**: `1.0mm`
* **Clearance Slack**: `0.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Paper Currency | 8 Denominations (`1, 2, 5, 10` & `20, 50, 100, 500`) | `MoneyBox_1`, `MoneyBox_2` | Slipover Lid | Framed "18Cuba" (Gold) |
| Train & Wagon Cards | 36 Train cards + 18 Wagon cards (`40 x 60mm`) | `TrainBox` | Slipover Lid | Framed "Trains" (Blue) |
| Corporate Shares | 10 company stock stacks (5 per box) | `SharesBox_1`, `SharesBox_2` | Slipover Lid | Framed "Shares" (Royal Blue) |
| Concessions, Minor Tokens & Rails | Concession cards, minor/Green/Brown tokens, rail pieces | `LastBox` | Slipover Lid | Framed "Machine/Minor" (Teal) |
| Major Company Tokens | 8 major railroad station token rows | `LargeTokensBox` | Slipover Lid | Framed "Major Tokens" (Dark Blue) |
| Ferrocarril Central & Yellow Tokens | Nested upper token tray | `InsideTokenTray` | No-Lid Tray | Nested above `LargeTokensBox` |
| Board & Track Hexes | Folded boards (`26mm`) and hex trays (`20mm`) | Board Layer (`46.0mm`) | Board Layer | Flat storage in game box |

---

## 3. Sub-Box Specifications

### 3.1 Money Trays (`MoneyBox_1`, `MoneyBox_2`)
* **Dimensions**: `224.0mm x 96.0mm x 11.0mm` each.
* **Arrangement**: Stacked 2-high (`Z = 0.0..11.0mm` and `Z = 11.0..22.0mm`) at `Y = 0.0..96.0mm`.
* **Compartments**: 4 currency pockets per box with thumb indent scoops.

### 3.2 Large Tokens Section (`LargeTokensBox`, `InsideTokenTray`)
* **Dimensions**: `224.0mm x 85.0mm x 11.0mm` each.
* **Arrangement**: Stacked 2-high (`Z = 0.0..11.0mm` and `Z = 11.0..22.0mm`) at `Y = 96.0..181.0mm`.
* **Compartments**: 4 major company token rows in `LargeTokensBox`, 2 token sections in `InsideTokenTray`.

### 3.3 Train Card & Shares Row (`TrainBox`, `SharesBox_1`)
* **Dimensions**: `224.0mm x 66.0mm x 11.0mm` each.
* **Arrangement**: Stacked 2-high (`Z = 0.0..11.0mm` and `Z = 11.0..22.0mm`) at `Y = 181.0..247.0mm`.
* **Compartments**: 5 pockets each (3 train + 2 wagon pockets in `TrainBox`; 5 company share pockets in `SharesBox_1`).

### 3.4 Shares & Machine/Minor Row (`SharesBox_2`, `LastBox`)
* **Dimensions**: `224.0mm x 66.0mm x 11.0mm` each.
* **Arrangement**: Stacked 2-high (`Z = 0.0..11.0mm` and `Z = 11.0..22.0mm`) at `Y = 247.0..313.0mm`.
* **Compartments**: 5 company share pockets in `SharesBox_2`; Concession cards, minor/phase tokens, and rails in `LastBox`.

---

## 4. 3D Spatial Layout Map

```
+-------------------------------------------------------------------------------+
| MoneyBox_1 (224.0 x 96.0 x 11.0mm, Z: 0..11)                                  |
| [ MoneyBox_2 stacked atop, Z: 11..22 ]                                        |
+-------------------------------------------------------------------------------+
| LargeTokensBox (224.0 x 85.0 x 11.0mm, Z: 0..11)                              |
| [ InsideTokenTray stacked atop, Z: 11..22 ]                                   |
+-------------------------------------------------------------------------------+
| TrainBox (224.0 x 66.0 x 11.0mm, Z: 0..11)                                    |
| [ SharesBox_1 stacked atop, Z: 11..22 ]                                       |
+-------------------------------------------------------------------------------+
| SharesBox_2 (224.0 x 66.0 x 11.0mm, Z: 0..11)                                 |
| [ LastBox stacked atop, Z: 11..22 ]                                           |
+-------------------------------------------------------------------------------+
```
