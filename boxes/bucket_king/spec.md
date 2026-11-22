# Bucket King 3D Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Bucket King 3D** board game organizer, ported from `examples/bucket_king.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `140.0mm (Width) x 288.0mm (Length) x 70.0mm (Height)`
* **Main Insert Usable Height**: `68.0mm` (`Z = 0.0 .. 68.0mm`)
* **Wall Thickness**: `2.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Card Dimensions**: `68.0mm x 92.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Card Deck | Animal suit cards (`68 x 92mm`) | `CardBox` (`138 x 73 x 68mm`, single well + left finger hole) | Cap Lid | Double-framed "Bucket King" (Royal Blue) |
| Player Bucket Tokens (6 Players) | 15 Cardboard buckets per player (`3 + 4 + 4 + 4` bucket-shaped wells) | `PlayerBox_1` .. `PlayerBox_6` (`69 x 71 x 34.5mm`, 2×3 grid) | Cap Lid | Pill-framed "Buckets" (6 player colors) |
| Automatic Spacers | Upper layer above `PlayerBox_1..6` | Derived automatically | No-Lid Tray | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Card Box (Row 0, `Y = 0.0 .. 73.0mm`)
* **Dimensions**: `138.0mm x 73.0mm x 68.0mm` (`134.0 x 69.0 x 64.0mm` interior).
* **Arrangement**: Single full-width card well holding the `68 x 92mm` deck cleanly with a `20mm` left-wall finger hole for easy lifting.

### 3.2 Player Bucket Boxes (Rows 1–3, `Y = 73.0 .. 286.0mm`)
* **Dimensions**: `69.0mm x 71.0mm x 34.5mm` each (`65.0 x 67.0 x 30.5mm` interior).
* **Arrangement**: 2 columns across X × 3 rows along Y, each carved with a 2×2 grid of `28 x 32mm` bucket-shaped wells (`3 + 4 + 4 + 4 = 15` tiles) and finger-pinch slots.

---

## 4. 3D Spatial Layout Map

```
+-------------------------------------------------------------------------------+
| CardBox (Full width: 138.0mm x 73.0mm x 68.0mm, single well + left scoop)     |
+---------------------------------------+---------------------------------------+
| PlayerBox_1 (69.0 x 71.0 x 34.5mm)    | PlayerBox_2 (69.0 x 71.0 x 34.5mm)    |
+---------------------------------------+---------------------------------------+
| PlayerBox_3 (69.0 x 71.0 x 34.5mm)    | PlayerBox_4 (69.0 x 71.0 x 34.5mm)    |
+---------------------------------------+---------------------------------------+
| PlayerBox_5 (69.0 x 71.0 x 34.5mm)    | PlayerBox_6 (69.0 x 71.0 x 34.5mm)    |
+---------------------------------------+---------------------------------------+
|<------------------------------ 140.0mm -------------------------------------->|
```
