# Earth: Animal Kingdom Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Earth: Animal Kingdom** expansion organizer, ported from `examples/earth_animal_kingdom.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `288.0mm (Width) x 158.0mm (Length) x 47.0mm (Height)`
* **Main Insert Usable Height**: `45.0mm` (`Z = 0.0 .. 45.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Large Animal Cards**: `72.0mm x 123.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Large Animal Cards | 36 Tarot/oversized animal habitat cards (`72 x 123mm`) | `AnimalCardsBox` | Sliding Lid | Framed "Animal Cards" (Maroon) |
| Wooden Canopies | 20 Extra wooden canopy tree tops | `ExpansionCanopyBox` | Cap Lid | Framed "Canopies" (Peru) |
| Sprout Cubes | 50 Extra green sprout resource cubes | `ExpansionSproutBox` | Cap Lid | Framed "Sprouts" (Forest Green) |
| Animal Habitat Tokens | Cutout wooden animal tokens | `AnimalTokensBox_1`, `AnimalTokensBox_2` | Cap Lid | Framed "Animal Tokens" (Goldenrod) |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Card & Sprout Column (`X = 0.0 .. 78.0mm`)
* **`AnimalCardsBox`** (`78.0mm x 129.0mm x 24.0mm`): Bottom tier at `Z = 0.0mm`.
* **`ExpansionSproutBox`** (`78.0mm x 129.0mm x 21.0mm`): Upper tier stacked at `Z = 24.0mm`.

### 3.2 Canopy Column (`X = 78.0 .. 116.0mm`)
* **`ExpansionCanopyBox`** (`38.0mm x 129.0mm x 45.0mm`): Full-depth canopy dispenser.

### 3.3 Animal Token Trays (`X = 116.0 .. 286.0mm`)
* **`AnimalTokensBox_1` & `AnimalTokensBox_2`** (`170.0mm x 129.0mm x 13.0mm` each): Stacked 2 high (`Z = 0.0` and `Z = 13.0mm`), with 3 species wells per tray.

---

## 4. 3D Spatial Layout Map

```
+--------------------+----------------+-----------------------------------------+
| AnimalCardsBox     | CanopyBox      | AnimalTokensBox_1                       |
| (78.0 x 129.0mm,   | (38.0 x 129.0  | (Stacked 2-high, 13.0mm each)           |
|  Z: 0..24.0mm)     |   x 45.0mm)    | (170.0 x 129.0mm)                       |
+--------------------+                |                                         |
| ExpansionSproutBox |                |                                         |
| (78.0 x 129.0mm,   |                |                                         |
|  Z: 24..45.0mm)    |                |                                         |
+--------------------+----------------+-----------------------------------------+
|                               Automatic 3D Void Spacers                       |
|                        (Y = 129.0..158mm, Z = 0..45.0mm)                      |
+-------------------------------------------------------------------------------+
```
