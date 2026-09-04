# 18Cuba Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **18Cuba** board game organizer, ported from `examples/18cuba.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `225.0mm (Width) x 314.0mm (Length) x 68.0mm (Height)`
* **Board & Hex Track Reserve**: `26.0mm` (Board and hex tile punchboards sit atop the insert at `Z = 42.0 .. 68.0mm`)
* **Main Insert Usable Height**: `42.0mm` (`Z = 0.0 .. 42.0mm`)
* **Wall Thickness**: `2.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Paper Currency | 8 Denominations (1, 2, 5, 10, 20, 50, 100, 500) | `MoneyBox_1`, `MoneyBox_2` | Slipover Lid | Framed "18Cuba Money" (Gold) |
| Train & Wagon Cards | 36 Train cards + 18 Wagon cards (`40 x 60mm`) | `TrainBox` | Slipover Lid | Framed "Trains" (Blue) |
| Major & Minor Company Shares | 8 Major + 6 Minor railway corporations | `SharesBox_1`, `SharesBox_2` | Slipover Lid | Framed "Shares" (Royal Blue) |
| Board & Track Hexes | Folded boards and track hexes | Sits atop insert (`Z = 42.0 .. 68.0mm`) | Board Layer | Flat storage beneath game box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Money Trays (`MoneyBox_1`, `MoneyBox_2`)
* **Dimensions**: `111.5mm x 98.0mm x 21.0mm` each.
* **Arrangement**: Side-by-side at `Y = 0.0mm`.
* **Compartments**: 4 currency pockets per box with thumb indent scoops.

### 3.2 Train Card Box (`TrainBox`)
* **Dimensions**: `223.0mm x 68.0mm x 21.0mm`.
* **Arrangement**: Spans the box width at `Y = 98.0mm`.
* **Compartments**: 5 distinct train card pockets.

### 3.3 Share Certificate Trays (`SharesBox_1`, `SharesBox_2`)
* **Dimensions**: `111.5mm x 68.0mm x 21.0mm` each.
* **Arrangement**: Side-by-side at `Y = 166.0mm`.
* **Compartments**: 4 corporate stock certificate pockets per box.

---

## 4. 3D Spatial Layout Map

```
+---------------------------------------+---------------------------------------+
| MoneyBox_1 (111.5 x 98.0 x 21.0mm)    | MoneyBox_2 (111.5 x 98.0 x 21.0mm)    |
+---------------------------------------+---------------------------------------+
| TrainBox (Full width: 223.0mm x 68.0mm x 21.0mm)                              |
+---------------------------------------+---------------------------------------+
| SharesBox_1 (111.5 x 68.0 x 21.0mm)   | SharesBox_2 (111.5 x 68.0 x 21.0mm)   |
+---------------------------------------+---------------------------------------+
|                       Automatic 3D Void Spacers                               |
|                     (Y = 234.0mm .. 314.0mm, Z = 0 .. 42.0mm)                 |
+-------------------------------------------------------------------------------+
```
