# Brink Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Brink** board game organizer, ported from `examples/brink.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `215.0mm (Width) x 307.0mm (Length) x 96.0mm (Height)`
* **Board & Player Mat Reserve**: `18.0mm` (Map board and player mats sit atop insert at `Z = 78.0 .. 96.0mm`)
* **Main Insert Usable Height**: `78.0mm` (`Z = 0.0 .. 78.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Hex Sector Diameter**: `72.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Sector Hex Tiles | 72mm cardboard sector hexes | `HexBox` | Cap Lid | Framed "Hex Tiles" (Dim Gray) |
| Player Ships & Upgrades (4 Factions) | Solari, Vanguard, Eclipse, Horizon | `PlayerBox_Solari` .. `PlayerBox_Horizon` (4 boxes) | Cap Lid | Framed faction names (Royal Blue) |
| Action & Rider Cards | Action deck and rider decks | `CardBox_Actions`, `CardBox_Riders` | Sliding Lid | Framed "Actions" (Gold) & "Riders" (Firebrick) |
| Ambassador & Faction Cards | Ambassador cards and faction charters | `CardBox_Ambassadors`, `CardBox_Factions` | Sliding Lid | Framed "Ambassadors" (Navy) & "Factions" (Green) |
| Main Map Board | Mounted game board + voting tracks | Sits atop insert (`Z = 78.0 .. 96.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Hex Sector Storage (`Y = 0.0 .. 120.0mm`)
* **Dimensions**: `213.0mm x 120.0mm x 26.0mm`.
* **Arrangement**: Full width tray with 3 hexagonal storage wells.

### 3.2 Player Faction Trays (`Y = 120.0 .. 200.0mm`)
* **Dimensions**: `106.0mm x 80.0mm x 26.0mm` each.
* **Arrangement**: 2 columns, stacked 2 high (`Z = 0.0` and `Z = 26.0mm`).

### 3.3 Card Trays (`Y = 200.0 .. 277.5mm`)
* **Dimensions**: `106.5mm x 77.5mm x 26.0mm` each.
* **Arrangement**: 2 columns, stacked 2 high across `Z = 0.0 .. 52.0mm`.

---

## 4. 3D Spatial Layout Map

```
+-------------------------------------------------------------------------------+
| HexBox (Full width: 213.0mm x 120.0mm x 26.0mm)                               |
+---------------------------------------+---------------------------------------+
| PlayerBox_Solari / Eclipse            | PlayerBox_Vanguard / Horizon          |
| (Stacked 2-high, 26.0mm each)         | (Stacked 2-high, 26.0mm each)         |
| (106.0 x 80.0mm)                      | (106.0 x 80.0mm)                      |
+---------------------------------------+---------------------------------------+
| CardBox_Actions / Ambassadors         | CardBox_Riders / Factions             |
| (Stacked 2-high, 26.0mm each)         | (Stacked 2-high, 26.0mm each)         |
| (106.5 x 77.5mm)                      | (106.5 x 77.5mm)                      |
+---------------------------------------+---------------------------------------+
|                           Automatic 3D Void Spacers                           |
|                    (Y = 277.5..307mm, Z = 0..78.0mm)                          |
+-------------------------------------------------------------------------------+
```
