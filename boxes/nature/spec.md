# Nature Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Nature** board game organizer, ported from `examples/nature.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `210.0mm (Width) x 210.0mm (Length) x 75.0mm (Height)`
* **Board & Player Mat Reserve**: `7.0mm` (Central climate board and species mats sit atop insert at `Z = 68.0 .. 75.0mm`)
* **Main Insert Usable Height**: `68.0mm` (`Z = 0.0 .. 68.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Cards**: `67.0mm x 92.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Nature Cards | 99 Evolution / trait cards (`67 x 92mm`) | `NatureCardsBox` | Sliding Lid | Framed "Nature Cards" (Forest Green) |
| Hunter Cards & Solo Cards | 10 Hunter cards and solo event cards | `HunterCardsBox`, `SoloCardsBox` | Sliding Lid | Framed "Hunters" (Red) & "Solo" (Blue) |
| Population Dials | Rotating cardboard player population wheels | `DialBox` | Cap Lid | Framed "Population Dials" (Gold) |
| Apex Predator | Wooden leopard predator meeple | `LeopardBox` | Cap Lid | Framed "Apex Leopard" (Peru) |
| Food Resources (Grass & Meat) | Green plant tokens, red meat tokens | `ResourceBox_Grass`, `ResourceBox_Meat` | Cap Lid | Framed "Grass" & "Meat" |
| Climate Board & Mats | Game board and player mats | Sits atop insert (`Z = 68.0 .. 75.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Card Library (Row 0, `Y = 0.0 .. 73.0mm`)
* **`NatureCardsBox`**: `104.0mm x 73.0mm x 68.0mm` (full usable depth).
* **`HunterCardsBox` & `SoloCardsBox`**: `104.0mm x 73.0mm x 20.0mm` each, stacked 2 high (`Z = 0.0` and `Z = 20.0mm`).

### 3.2 Dials, Predators & Food (Row 1, `Y = 73.0 .. 177.0mm`)
* **`DialBox` & `LeopardBox`**: `107.0mm x 52.0mm x 51.0mm` each at `X = 0.0mm`.
* **`ResourceBox_Grass` & `ResourceBox_Meat`**: `101.0mm x 67.5mm x 25.5mm` each at `X = 107.0mm`.

---

## 4. 3D Spatial Layout Map

```
+------------------------------------+------------------------------------+
| NatureCardsBox                     | HunterCardsBox (Z: 0..20.0mm)      |
| (104.0 x 73.0 x 68.0mm)            | SoloCardsBox   (Z: 20..40.0mm)     |
|                                    | (104.0 x 73.0mm)                   |
+------------------------------------+------------------------------------+
| DialBox (107.0 x 52.0 x 51.0mm)    | ResourceBox_Grass                  |
+------------------------------------+ (101.0 x 67.5 x 25.5mm)              |
| LeopardBox (107.0 x 52.0 x 51.0mm) +------------------------------------+
|                                    | ResourceBox_Meat                   |
|                                    | (101.0 x 67.5 x 25.5mm)            |
+------------------------------------+------------------------------------+
|                           Automatic 3D Void Spacers                     |
|                    (Y = 177..210mm, Z = 0..68.0mm)                      |
+-------------------------------------------------------------------------+
```
