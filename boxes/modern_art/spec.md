# Modern Art Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Modern Art** board game organizer, ported from `examples/modern_art.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `154.0mm (Width) x 208.0mm (Length) x 44.0mm (Height)`
* **Board & Screen Reserve**: `6.0mm` (Auction valuation board and player screens sit atop insert at `Z = 38.0 .. 44.0mm`)
* **Main Insert Usable Height**: `38.0mm` (`Z = 0.0 .. 38.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Painting Cards**: `61.0mm x 93.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Painting Cards | 70 Art cards (`61 x 93mm`) in dual wells | `CardBox` | Cap Lid | Framed "Modern Art Cards" (Royal Blue) |
| Money & Value Tokens | Cardboard money coins and artist valuation chips | `TokensBox` | Cap Lid | Framed "Money & Chips" (Gold) |
| Valuation Board & Screens | Board and screens | Sits atop insert (`Z = 38.0 .. 44.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Art Cards Box (Row 0, `Y = 0.0 .. 99.0mm`)
* **Dimensions**: `151.0mm x 99.0mm x 38.0mm`.
* **Arrangement**: Full width tray with dual card wells.

### 3.2 Auction Money & Chips Box (Row 1, `Y = 99.0 .. 205.0mm`)
* **Dimensions**: `151.0mm x 106.0mm x 38.0mm`.
* **Arrangement**: 2 compartments for coins and valuation markers.

---

## 4. 3D Spatial Layout Map

```
+---------------------------------------------------------------+
| CardBox (Dual card wells: 151.0mm x 99.0mm x 38.0mm)          |
+---------------------------------------------------------------+
| TokensBox (Money & Chips: 151.0mm x 106.0mm x 38.0mm)         |
+---------------------------------------------------------------+
|                   Automatic 3D Void Spacers                   |
|              (X = 151..154mm, Y = 205..208mm)                 |
+---------------------------------------------------------------+
```
