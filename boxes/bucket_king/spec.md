# Bucket King 3D Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Bucket King 3D** board game organizer, ported from `examples/bucket_king.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `140.0mm (Width) x 288.0mm (Length) x 70.0mm (Height)`
* **Main Insert Usable Height**: `68.0mm` (`Z = 0.0 .. 68.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Card Dimensions**: `68.0mm x 92.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Card Decks | Animal suit cards (`68 x 92mm`) | `CardBox` | Cap Lid | Framed "Bucket King Cards" (Royal Blue) |
| Player Bucket Tokens (6 Players) | 15 Cardboard buckets per player (5 colors x 3) | `PlayerBox_1` .. `PlayerBox_6` (6 boxes) | Cap Lid | Framed "Buckets 1..6" (Dark Orange) |
| Rules & Score Sheet | Rule booklet | Sits atop insert (`Z = 68.0 .. 70.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Card Box (Row 0, `Y = 0.0 .. 75.0mm`)
* **Dimensions**: `138.0mm x 75.0mm x 68.0mm`.
* **Arrangement**: Full width tray with dual card wells.

### 3.2 Player Bucket Boxes (Rows 1–3, `Y = 75.0 .. 286.0mm`)
* **Dimensions**: `69.0mm x 70.33mm x 34.5mm` each.
* **Arrangement**: 2 columns across X, 3 rows along Y.

---

## 4. 3D Spatial Layout Map

```
+-------------------------------------------------------------------------------+
| CardBox (Full width: 138.0mm x 75.0mm x 68.0mm)                               |
+---------------------------------------+---------------------------------------+
| PlayerBox_1 (69.0 x 70.3 x 34.5mm)    | PlayerBox_2 (69.0 x 70.3 x 34.5mm)    |
+---------------------------------------+---------------------------------------+
| PlayerBox_3 (69.0 x 70.3 x 34.5mm)    | PlayerBox_4 (69.0 x 70.3 x 34.5mm)    |
+---------------------------------------+---------------------------------------+
| PlayerBox_5 (69.0 x 70.3 x 34.5mm)    | PlayerBox_6 (69.0 x 70.3 x 34.5mm)    |
+---------------------------------------+---------------------------------------+
|<------------------------------ 140.0mm -------------------------------------->|
```
