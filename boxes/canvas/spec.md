# Canvas Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Canvas** board game organizer, ported from `examples/canvas.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `200.0mm (Width) x 250.0mm (Length) x 50.0mm (Height)`
* **Mat Reserve**: `15.0mm` (Cloth canvas mat sits atop insert at `Z = 35.0 .. 50.0mm`)
* **Main Insert Usable Height**: `35.0mm` (`Z = 0.0 .. 35.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Ribbon Tokens (6 Types) | Red, Green, Grey, Blue, Purple, Palette ribbon award tokens | `RibbonBox_Red` .. `RibbonBox_Palette` (6 boxes) | Cap Lid | Color-coded Framed lids |
| Transparent Art Cards | Tarot/large transparent artwork card deck | `CardTray` | Cap Lid | Framed "Art Cards" (Slate) |
| Canvas Cloth Mat | Rolled / folded canvas art display mat | Sits atop insert (`Z = 35.0 .. 50.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Ribbon Token Dispensers (`Y = 0.0 .. 146.0mm`)
* **Dimensions**: `41.0mm x 73.0mm x 29.0mm` each.
* **Arrangement**: 2 rows of 3 boxes across the width (`X = 0.0 .. 123.0mm`).

### 3.2 Art Card Tray (`Y = 146.0 .. 208.0mm`)
* **Dimensions**: `196.0mm x 62.0mm x 30.0mm`.
* **Compartments**: Dual-well card tray with side thumb scoops.

---

## 4. 3D Spatial Layout Map

```
+----------------+----------------+----------------+----------------------------+
| RibbonBox_Red  | RibbonBox_Green| RibbonBox_Grey |                            |
| (41 x 73x29mm) | (41 x 73x29mm) | (41 x 73x29mm) |                            |
+----------------+----------------+----------------+        Automatic 3D        |
| RibbonBox_Blue | RibbonBox_Purp | RibbonBox_Pal  |        Void Spacers        |
| (41 x 73x29mm) | (41 x 73x29mm) | (41 x 73x29mm) |     (X = 123..200mm,       |
+----------------+----------------+----------------+      Y = 0..146mm)         |
| CardTray (196.0mm x 62.0mm x 30.0mm)             |                            |
+--------------------------------------------------+----------------------------+
|                           Automatic 3D Void Spacers                           |
|                    (Y = 208..250mm, Z = 0..35.0mm)                            |
+-------------------------------------------------------------------------------+
```
