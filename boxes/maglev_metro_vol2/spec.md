# Maglev Metro: Volume 2 Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Maglev Metro: Volume 2** expansion organizer, ported from `examples/maglev_metro_vol2.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `286.0mm (Width) x 286.0mm (Length) x 65.0mm (Height)`
* **Board & Player Mat Reserve**: `27.0mm` (Map boards and punchboards sit atop insert at `Z = 38.0 .. 65.0mm`)
* **Main Insert Usable Height**: `38.0mm` (`Z = 0.0 .. 38.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Expansion Cards | Map 2 & connection cards (`67 x 90mm`) | `ExpansionCardsBox` | Sliding Lid | Framed "Maps 2" (Dark Orange) |
| Upgrade Tiles | Player upgrade tiles with cutouts | `UpgradeTileBox` | Cap Lid | Framed "Upgrades" (Seagreen) |
| Outback & Ghost Station Hexes | Expansion station hexes | `OutbackGhostTilesBox` | Cap Lid | Framed "Outback & Ghost" (Dark Violet) |
| Metro Tickets & Nanobots | Metal/cardboard ticket tokens, nanobot figures | `MetroTokenBox` | Cap Lid | Framed "Tokens & Nanobots" (Gold) |
| Expansion Game Boards | Moon and Mars map boards | Sits atop insert (`Z = 38.0 .. 65.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Card & Upgrade Column (`X = 0.0 .. 73.0mm`)
* **`ExpansionCardsBox`** (`73.0mm x 96.0mm x 19.0mm`): Positioned at `Y = 0.0mm`.
* **`UpgradeTileBox`** (`73.0mm x 126.0mm x 19.0mm`): Positioned at `Y = 96.0mm`.

### 3.2 Hex & Token Column (`X = 73.0 .. 183.0mm`)
* **`OutbackGhostTilesBox`** (`110.0mm x 140.0mm x 19.0mm`): Bottom tier at `Z = 0.0mm`.
* **`MetroTokenBox`** (`110.0mm x 140.0mm x 19.0mm`): Upper tier at `Z = 19.0mm`.

---

## 4. 3D Spatial Layout Map

```
+-------------------+-----------------------------------------------------------+
| ExpansionCardsBox | OutbackGhostTilesBox (110.0 x 140.0 x 19.0mm, Z: 0..19mm) |
| (73.0 x 96.0mm)   | [ MetroTokenBox stacked atop, Z: 19..38mm, H: 19.0mm ]    |
+-------------------+                                                           |
| UpgradeTileBox    |                                                           |
| (73.0 x 126.0mm)  |                                                           |
+-------------------+-----------------------------------------------------------+
|                            Automatic 3D Void Spacers                          |
|                     (X = 0..286mm, Y = 222..286mm, Z = 0..38mm)               |
+-------------------------------------------------------------------------------+
```
