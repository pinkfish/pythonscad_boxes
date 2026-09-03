# Cascadero Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Cascadero** board game organizer, ported from `examples/cascadero.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `212.0mm (Width) x 304.0mm (Length) x 40.0mm (Height)`
* **Board Reserve**: `14.0mm` (Folded map board sits atop insert at `Z = 26.0 .. 40.0mm`)
* **Main Insert Usable Height**: `26.0mm` (`Z = 0.0 .. 26.0mm`)
* **Wall Thickness**: `2.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Player Pieces (4 Colors) | Wooden envoys, scoring cylinders | `PlayerBox_1` .. `PlayerBox_4` (4 boxes) | Sliding Lid | Color-coded Framed lids |
| Royal Seals | Cardboard seal award tokens | `SealsBox` | Sliding Lid | Framed "Seals" (Firebrick) |
| Heralds | Wooden herald figures | `HeraldBox` | Sliding Lid | Framed "Herald" (Goldenrod) |
| Farmers | Wooden farmer figures | `FarmerBox` | Sliding Lid | Framed "Farmer" (Seagreen) |
| Main Map Board | Mounted game board | Sits atop insert (`Z = 26.0 .. 40.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Player Envoy Section (Rows 0 & 1, `Y = 0.0 .. 210.0mm`)
* **Dimensions**: `105.0mm x 105.0mm x 26.0mm` each.
* **Arrangement**: 2x2 grid of sliding lid boxes across the width and front 210mm of length.

### 3.2 Neutral Figure & Token Section (Row 2, `Y = 210.0 .. 304.0mm`)
* **`SealsBox`** (`85.0mm x 94.0mm x 26.0mm`): Left slot.
* **`HeraldBox`** (`40.0mm x 94.0mm x 26.0mm`): Center narrow slot.
* **`FarmerBox`** (`85.0mm x 94.0mm x 26.0mm`): Right slot.

---

## 4. 3D Spatial Layout Map

```
+---------------------------------------+---------------------------------------+
| PlayerBox_1 (105.0 x 105.0 x 26.0mm)  | PlayerBox_2 (105.0 x 105.0 x 26.0mm)  |
+---------------------------------------+---------------------------------------+
| PlayerBox_3 (105.0 x 105.0 x 26.0mm)  | PlayerBox_4 (105.0 x 105.0 x 26.0mm)  |
+-------------------+-------------------+---------------------------------------+
| SealsBox          | HeraldBox         | FarmerBox                             |
| (85.0 x 94.0mm)   | (40.0 x 94.0mm)   | (85.0 x 94.0mm)                       |
+-------------------+-------------------+---------------------------------------+
|<------------------------------ 212.0mm -------------------------------------->|
```
