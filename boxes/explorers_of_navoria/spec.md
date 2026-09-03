# Explorers of Navoria Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Explorers of Navoria** board game organizer, ported from `examples/explorers_of_navoria.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `211.0mm (Width) x 268.0mm (Length) x 68.0mm (Height)`
* **Board & Player Mat Reserve**: `12.0mm` (Main game board + player mats sit atop insert at `Z = 56.0 .. 68.0mm`)
* **Main Insert Usable Height**: `56.0mm` (`Z = 0.0 .. 56.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Standard Cards**: `68.0mm x 92.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Player Pieces (4 Factions) | Yellow, Purple, Black, Green trading posts, explorer discs | `PlayerBox_Yellow` .. `PlayerBox_Green` (4 boxes) | Cap Lid | Color-coded Framed lids |
| Adventure Cards | 60 Adventure cards + 4 reference cards (`68 x 92mm`) | `CardBox` | Sliding Lid | Framed "Cards" (Navy) |
| Favour Tiles & Crafting Tokens | Cardboard favour tiles & crafting tokens | `FavourBox_1`, `FavourBox_2` | Cap Lid | Framed "Favour Tiles" & "Tokens" |
| Drawing Bag & Large Bits | Cloth drawing bag and round tokens | `BagBox` | Cap Lid | Framed "Bag & Components" (Peru) |
| Board & Player Mats | Folded game board + player mats | Sits atop insert (`Z = 56.0 .. 68.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Player Faction Column (Column 0, `X = 0.0 .. 98.0mm`)
* **Dimensions**: `98.0mm x 133.0mm x 28.0mm` each.
* **Arrangement**: 2 rows along Y, stacked 2 high (`Z = 0.0` and `Z = 28.0mm`).

### 3.2 Cards, Favours & Bag Column (Column 1, `X = 98.0 .. 209.0mm`)
* **`CardBox`** (`111.0mm x 74.0mm x 56.0mm`): Positioned at `Y = 0.0 .. 74.0mm`.
* **`FavourBox_1` & `FavourBox_2`** (`111.0mm x 60.0mm x 28.0mm` each): Stacked 2 high at `Y = 74.0 .. 134.0mm`.
* **`BagBox`** (`111.0mm x 132.0mm x 56.0mm`): Positioned at `Y = 134.0 .. 266.0mm`.

---

## 4. 3D Spatial Layout Map

```
+------------------------------------+------------------------------------+
| PlayerBox_Yellow / Black           | CardBox (111.0 x 74.0 x 56.0mm)    |
| (Stacked 2-high, 28.0mm each)      +------------------------------------+
| (98.0 x 133.0mm)                   | FavourBox_1 / FavourBox_2          |
+------------------------------------+ (Stacked 2-high, 28.0mm each)       |
| PlayerBox_Purple / Green           | (111.0 x 60.0mm)                   |
| (Stacked 2-high, 28.0mm each)      +------------------------------------+
| (98.0 x 133.0mm)                   | BagBox                             |
|                                    | (111.0 x 132.0 x 56.0mm)           |
+------------------------------------+------------------------------------+
|<-------------- 98.0mm ------------>|<-------------- 111.0mm ----------->|
```
