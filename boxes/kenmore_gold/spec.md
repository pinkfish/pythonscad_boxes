# Kenmore Gold Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Kenmore Gold** board game organizer, ported from `examples/kenmore_gold.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `130.0mm (Width) x 120.0mm (Length) x 77.0mm (Height)`
* **Main Insert Usable Height**: `69.0mm` (`Z = 0.0 .. 69.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Square Dungeon Tile Width**: `58.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Square Dungeon Tiles | Double-stack of 58mm dungeon passage tiles | `SquareTileBox` | Cap Lid | Framed "Kenmore Gold" (Goldenrod) |
| Start Cave Tile | Elongated start cave tile | `StartCaveBox` | Cap Lid | Framed "Start Cave" (Saddle Brown) |
| Loot & Gold Tokens | Gold nuggets and loot tokens | `LootBox` | Cap Lid | Framed "Loot" (Gold) |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Dungeon Tile Storage (Row 0, `Y = 0.0 .. 64.0mm`)
* **Dimensions**: `124.0mm x 64.0mm x 69.0mm`.
* **Arrangement**: Dual vertical wells for square 58mm dungeon tiles.

### 3.2 Cave & Loot Storage (Row 1, `Y = 64.0 .. 114.0mm`)
* **`StartCaveBox`** (`124.0mm x 50.0mm x 21.0mm`): Lower tier at `Z = 0.0mm`.
* **`LootBox`** (`124.0mm x 50.0mm x 48.0mm`): Upper tier stacked at `Z = 21.0mm`.

---

## 4. 3D Spatial Layout Map

```
+---------------------------------------------------------------+
| SquareTileBox (124.0mm x 64.0mm x 69.0mm)                     |
+---------------------------------------------------------------+
| StartCaveBox (124.0mm x 50.0mm, Z: 0..21.0mm)                 |
| LootBox      (124.0mm x 50.0mm, Z: 21..69.0mm)                |
+---------------------------------------------------------------+
|                   Automatic 3D Void Spacers                   |
|               (X = 124..130mm, Y = 114..120mm)                |
+---------------------------------------------------------------+
```
