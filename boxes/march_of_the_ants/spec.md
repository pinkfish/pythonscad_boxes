# March of the Ants Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **March of the Ants** board game organizer, ported from `examples/march_of_the_ants.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `195.0mm (Width) x 275.0mm (Length) x 65.0mm (Height)`
* **Board & Score Track Reserve**: `6.0mm` (Score tracks and colony player boards sit atop insert at `Z = 59.0 .. 65.0mm`)
* **Main Insert Usable Height**: `59.0mm` (`Z = 0.0 .. 59.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Hex Territory Width**: `84.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Territory Hex Tiles | Base game & expansion meadow hexes | `HexTileBox` | Cap Lid | Framed "Territory Hexes" (Saddle Brown) |
| Evolution Cards (Base & Minions) | 66 Base cards + 49 Minions cards | `CardBox_Base`, `CardBox_Expansion` | Sliding Lid | Framed "Base Cards" & "Minions Cards" |
| Food & Aphids | Wooden food tokens, aphids | `FoodTokensBox` | Cap Lid | Framed "Food & Aphids" (Forest Green) |
| Predator Meeples & Tokens | Spiders, centipedes, mantis predators | `PredatorsBox` | Cap Lid | Framed "Predators" (Dark Red) |
| Player Ant Colonies (5 Players) | Red, Blue, Yellow, Green, Black ant cubes | `PlayerBox_Red` .. `PlayerBox_Black` | Cap Lid | Color-coded Framed lids |
| Board & Mats | Score track and colony boards | Sits atop insert (`Z = 59.0 .. 65.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Territory Hexes (Row 0, `Y = 0.0 .. 100.0mm`)
* **Dimensions**: `194.0mm x 100.0mm x 59.0mm`.
* **Arrangement**: Full width dual-hex well box.

### 3.2 Cards & Resource Trays (Row 1, `Y = 100.0 .. 198.0mm`)
* **`CardBox_Base` & `CardBox_Expansion`**: `73.0mm x 98.0mm x 29.5mm` each, stacked 2 high at `X = 0.0mm`.
* **`FoodTokensBox` & `PredatorsBox`**: `121.0mm x 98.0mm x 29.5mm` each, stacked 2 high at `X = 73.0mm`.

### 3.3 Player Ant Colonies (Row 2, `Y = 198.0 .. 274.0mm`)
* **Dimensions**: `97.0mm x 76.0mm x 19.66mm` each.
* **Arrangement**: 2 columns across X, stacked 3 high.

---

## 4. 3D Spatial Layout Map

```
+-------------------------------------------------------------------------------+
| HexTileBox (Full width: 194.0mm x 100.0mm x 59.0mm)                           |
+---------------------------------------+---------------------------------------+
| CardBox_Base (Z: 0..29.5mm)           | FoodTokensBox (Z: 0..29.5mm)          |
| CardBox_Expansion (Z: 29.5..59.0mm)   | PredatorsBox  (Z: 29.5..59.0mm)       |
| (73.0 x 98.0mm)                       | (121.0 x 98.0mm)                      |
+---------------------------------------+---------------------------------------+
| PlayerBox_Red / Yellow / Black        | PlayerBox_Blue / Green                |
| (Stacked 3-high, 19.66mm each)        | (Stacked 2-high, 19.66mm each)        |
| (97.0 x 76.0mm)                       | (97.0 x 76.0mm)                       |
+---------------------------------------+---------------------------------------+
```
