# Railroad Tiles Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Railroad Tiles** board game organizer, ported from `examples/railroad_tiles.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `230.0mm (Width) x 230.0mm (Length) x 63.0mm (Height)`
* **Punchboard & Rules Reserve**: `2.5mm`
* **Main Insert Usable Height**: `60.5mm` (`Z = 0.0 .. 60.5mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Track Tile Width**: `46.0mm` square

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| General Resource & Game Tokens | Car/train/passenger tokens | `Tokens_1_Tier1` .. `Tokens_4_Tier2` (8 boxes) | Cap Lid | Framed token boxes (Navy) |
| Player Markers & Standees | Hat/shoulder silhouette wooden markers | `PlayerMarkersBox` | Cap Lid | Framed "Player Markers" (Dark Green) |
| Starting Clocks | Round clock face starting tiles (`32mm` dia) | `StartingClocksBox` | Cap Lid | Framed "Clocks" (Gold) |
| Objective Cards & Tiles | 46mm square objective tiles | `ObjectiveBox_1` .. `ObjectiveBox_5` (5 boxes) | Cap Lid | Framed "Objectives" (Dark Orange) |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Token & Player Section (`Y = 0.0 .. 38.0mm`)
* **`Tokens_1` .. `Tokens_4`** (`57.0mm x 38.0mm x 24.25mm`): 4 columns across width, stacked 2 high (`Z = 0.0 .. 48.5mm`).
* **`PlayerMarkersBox`** & **`StartingClocksBox`** (`114.0mm x 38.0mm x 12.0mm`): Stacked atop the token boxes at `Z = 48.5mm`.

### 3.2 Objective Tile Trays (`Y = 38.0 .. 90.0mm`)
* **`ObjectiveBox_1` .. `ObjectiveBox_5`** (`114.0mm x 52.0mm x 12.1mm` each): Stacked 5 high from `Z = 0.0` to `Z = 60.5mm`. Dual 46mm square tile pockets per tray.

---

## 4. 3D Spatial Layout Map

```
+------------------------------------+------------------------------------+
| Tokens_1 .. 4 (Stacked 2-high)     | ObjectiveBox_1 .. 5                |
| [ Atop tokens: PlayerMarkersBox &  | (Stacked 5-high, Z: 0..60.5mm)     |
|   StartingClocksBox, Z: 48.5..60.5]| (114.0 x 52.0 x 12.1mm each)       |
+------------------------------------+------------------------------------+
|                       Automatic 3D Void Spacers                         |
|                 (X = 0..230mm, Y = 90..230mm, Z = 0..60.5mm)            |
+-------------------------------------------------------------------------+
```
