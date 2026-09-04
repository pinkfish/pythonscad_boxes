# Pioneer Rails Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Pioneer Rails** board game organizer, ported from `examples/pioneer_rails.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `209.0mm (Width) x 209.0mm (Length) x 38.0mm (Height)`
* **Score Sheet Pad Reserve**: `16.0mm` (Pad of player map sheets sits atop insert at `Z = 22.0 .. 38.0mm`)
* **Main Insert Usable Height**: `22.0mm` (`Z = 0.0 .. 22.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Card Dimensions**: `66.5mm x 90.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Pencils, Eraser & Dealer Token | 4 Pencils, eraser, round poker chip | `PencilBox` | Cap Lid | Framed "Pencils" (Peru) |
| Goal Cards | Mission goal deck (`66.5 x 90mm`) | `CardBox_GoalCards` | Sliding Lid | Frameless "Goal" (Dark Orange) |
| Playing Cards | Hand cards deck (`66.5 x 90mm`) | `CardBox_PlayingCards` | Sliding Lid | Frameless "Playing" (Navy) |
| Forest Cards | Forest bonus deck (`66.5 x 90mm`) | `CardBox_ForestCards` | Sliding Lid | Frameless "Forest" (Forest Green) |
| Company Owner Cards | Corporate charter cards (`66.5 x 90mm`) | `CardBox_CompanyCards` | Sliding Lid | Frameless "Company" (Gold) |
| Map Score Pad | Full pad of double-sided player sheets | Sits atop insert (`Z = 22.0 .. 38.0mm`) | Board Layer | Flat storage beneath game box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Pencils & Dealer Box (`PencilBox`)
* **Dimensions**: `60.0mm x 115.0mm x 22.0mm`.
* **Arrangement**: Positioned at `X = 0.0mm`, `Y = 0.0mm`.
* **Compartment**: Longitudinal pencil wells and cutout for the round dealer token.

### 3.2 Modular Card Boxes (Row 1, `X = 60.0 .. 148.0mm`)
* **Dimensions**: `22.0mm x 96.0mm x 22.0mm` each.
* **Boxes**: `CardBox_GoalCards`, `CardBox_PlayingCards`, `CardBox_ForestCards`, `CardBox_CompanyCards`.
* **Arrangement**: Stored side-by-side on edge with through-wall thumb pulls.

---

## 4. 3D Spatial Layout Map

```
+--------------------+----------------------------------------------------------+
| PencilBox          | CardBox_GoalCards (22.0 x 96.0 x 22.0mm)                 |
| (60.0 x 115.0mm)   | CardBox_PlayingCards (22.0 x 96.0 x 22.0mm)              |
| (Height: 22.0mm)   | CardBox_ForestCards (22.0 x 96.0 x 22.0mm)               |
|                    | CardBox_CompanyCards (22.0 x 96.0 x 22.0mm)              |
+--------------------+----------------------------------------------------------+
|                               Automatic 3D Void Spacers                       |
|                       (Residual volume to X: 209mm, Y: 209mm)                 |
+-------------------------------------------------------------------------------+
```
