# Emberleaf Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D hierarchical packing for the **Emberleaf** board game organizer, ported from `examples/emberleaf.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `287.0mm (Width) x 287.0mm (Length) x 79.0mm (Height)`
* **Board Thickness**: `26.5mm` (Player mats, main board, and score tracks sit on top at `Z = 52.5 .. 79.0mm`)
* **Main Insert Usable Height**: `52.5mm` (`Z = 0.0 .. 52.5mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.5mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Player Workers & Hero Standees | 5 Colors (Owl, Rabbit, Frog, Rat SVG silhouettes + Hero leader) | `PlayerBoxBlack`, `PlayerBoxRed`, `PlayerBoxYellow`, `PlayerBoxBlue`, `PlayerBoxGrey` (5 boxes) | Cap Lid | Framed "Player" (Voronoi leaf pattern) |
| Player Wooden Markers & Hexes | Wooden discs (`16.5mm`), victory tokens, 2 hex tiles | (Integrated in each `PlayerBox<Colour>`) | Cap Lid | (Multi-depth tiered pockets) |
| Resource Material Tokens | Food (Red), Stone (Grey), Honey (Yellow), Wood (Brown) | `MaterialBoxFood`, `MaterialBoxStone`, `MaterialBoxHoney`, `MaterialBoxWood` (4 boxes) | Token Tray | Framed material label + Color accents |
| Shared Cards (Favor, Hero, Solo) | 3 full decks (`66 x 91mm` cards) | `CardBoxFavor`, `CardBoxHero`, `CardBoxSolo` | Sliding Lid | Framed Deck Name (Voronoi leaf pattern) |
| Player Starter Card Decks | 5 decks (`66 x 91mm` cards) | `CardBoxPlayer<Colour>` (5 boxes) | Sliding Lid | Framed "Player" |
| Trophy Cards, Hexes & Trophy Marker | Trophy tiles (`26 x 36mm`), marker (`16.5mm`), 5 hex stacks | `CommonBox` | Cap Lid | Framed "Trophy" (Voronoi leaf pattern) |
| Automatic Spacers | Remaining 3D void volumes | Derived automatically by `pyboxbuilder` | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Custom Element-Pack Player Boxes (`PlayerBox<Colour>`)
* **Dimensions**: `98.0mm (Width) x 142.5mm (Length) x 13.125mm (Height)` (`PLAYER_INNER_H = 9.125mm`).
* **Lid Mechanism**: `BoxType.CAP` with Voronoi leaf patterns.
* **Internal Multi-Level Element Architecture**:
  * **Species Silhouettes**: 5 Owls, 5 Rabbits (alternating 180°), 5 Frogs, and 5 Rats precision-routed from SVG silhouettes.
  * **Color-Specific Leader**: Distinct SVG hero silhouette routed per player color.
  * **Wooden Markers**: 3 round token pockets (`16.5mm` diameter) with non-interfering grip scoops.
  * **Victory & Hex Wells**: Layered victory token pockets beneath 2 hexagonal tile wells (`38.5mm` hex size).
  * **Dual Pull-Out Dishes**: Wide (`92.0 x 80.0mm`) and tall (`50.0 x 96.0mm`) shallow rounded depressions (r = 5.0mm) spanning over the elements for instant finger extraction.

### 3.2 Resource Material Trays (`MaterialBox<Type>`)
* **Dimensions**: `98.0mm x 71.25mm x 13.125mm`.
* **Four Varieties**: Food (Red text), Stone (Grey text), Honey (Yellow text), Wood (Brown text).
* Sized as half-length companion trays to stack directly atop the player boxes.

### 3.3 Full-Height Shared Card Boxes (`CardBox<Type>`)
* **Dimensions**: `98.0mm x 73.0mm x 52.5mm`.
* **Three Varieties**: `CardBoxFavor`, `CardBoxHero`, `CardBoxSolo` (with keystone alignment).
* **Lid Mechanism**: `BoxType.SLIDING`.

### 3.4 Player Card Boxes (`CardBoxPlayer<Colour>`)
* **Dimensions**: `90.0mm x 98.0mm x 10.5mm`.
* **Arrangement**: Stacked 5-high (`5 x 10.5mm = 52.5mm`) to span the full insert height.

### 3.5 Common Trophy & Hex Box (`CommonBox`)
* **Dimensions**: `90.0mm x 188.0mm x 25.0mm`.
* **Compartment Elements**:
  * 5 Hexagonal tile columns (`38.5mm` apothem) holding 10 tiles each.
  * Rectangular trophy tile well (`26.0 x 36.0mm`) with dual spherical scoops (`30.0mm` dia).
  * Circular trophy marker well (`16.5mm` dia) with dual spherical grip scoops (`20.0mm` dia).

---

## 4. 3D Spatial Layout Map

```
+-------------------------------------------------------------+-----------------------+
| Column 1 (Width: 98.0mm)        | Column 2 (Width: 98.0mm)  | Column 3 (Width: 90.0)|
| [ PlayerBoxBlack / Yellow / ...]| [ CardBoxFavor ]          | [ 5 Player Card Boxes]|
| [ + MaterialBoxHoney / Wood ]   | (98 x 73 x 52.5mm)        | (90 x 98 x 10.5mm     |
| (Z: 0..52.5mm, 142.5mm length)  +---------------------------+  Stacked 5-high)      |
+---------------------------------+ [ CardBoxHero ]           +-----------------------+
| [ PlayerBoxRed / Blue / ...]    | (98 x 73 x 52.5mm)        | [ CommonBox ]         |
| [ + MaterialBoxFood / Stone ]   +---------------------------+ (90 x 188 x 25.0mm)   |
| (Z: 0..52.5mm, 142.5mm length)  | [ CardBoxSolo ]           |                       |
|                                 | (98 x 73 x 52.5mm)        |                       |
+---------------------------------+---------------------------+-----------------------+
```
