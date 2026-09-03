# Emberleaf Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Emberleaf** board game organizer, ported from `examples/emberleaf.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `287.0mm (Width) x 287.0mm (Length) x 79.0mm (Height)`
* **Board & Player Mat Reserve**: `26.5mm` (Folded map boards and player village mats sit atop insert at `Z = 52.5 .. 79.0mm`)
* **Main Insert Usable Height**: `52.5mm` (`Z = 0.0 .. 52.5mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Standard Cards**: `66.0mm x 91.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Player Animal Workers (4 Colors) | Owls, rabbits, frogs, rats meeples + hero figures | `PlayerBox_Pink` .. `PlayerBox_Green` (4 boxes) | Cap Lid | Color-coded Framed lids |
| Main Card Decks | Village, building, and forest card decks (`66 x 91mm`) | `CardBox_MainDeck1` .. `CardBox_MainDeck3` | Sliding Lid | Framed deck names |
| Hero Card Decks | Player hero & starting cards | `HeroCards_1` .. `HeroCards_5` (5 boxes) | Cap Lid | Framed "Hero Deck" (Purple) |
| Common Material Tokens | Wood, stone, gold, and trophy tokens | `CommonTokensBox` | Cap Lid | Framed "Common Tokens" (Brown) |
| Game Boards & Mats | Village boards and player mats | Sits atop insert (`Z = 52.5 .. 79.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Player Meeple Column (Column 0, `X = 0.0 .. 98.0mm`)
* **Dimensions**: `98.0mm x 142.5mm x 13.12mm` each.
* **Arrangement**: Stacked 4 high (`Z = 0.0 .. 52.5mm`) along the front half of length.

### 3.2 Main Card Library (Column 1, `X = 98.0 .. 196.0mm`)
* **Dimensions**: `98.0mm x 73.0mm x 52.5mm` each.
* **Arrangement**: 3 full-depth sliding card boxes stored sequentially along Y (`Y = 0.0 .. 219.0mm`).

### 3.3 Hero Decks & Common Tokens (Column 2, `X = 196.0 .. 286.0mm`)
* **`HeroCards_1` .. `HeroCards_5`**: `90.0mm x 73.0mm x 10.5mm` each, stacked 5 high at `Y = 0.0 .. 73.0mm`.
* **`CommonTokensBox`**: `90.0mm x 213.0mm x 25.0mm` at `Y = 73.0 .. 286.0mm`.

---

## 4. 3D Spatial Layout Map

```
+------------------------------------+------------------------------------+-----------------------+
| PlayerBox_Pink / Yellow / Blue /   | CardBox_MainDeck1 (98.0 x 73.0mm)  | HeroCards_1 .. 5      |
| Green (Stacked 4-high, 13.1mm each)|                                    | (Stacked 5-high)      |
| (98.0 x 142.5mm)                   +------------------------------------+ (90.0 x 73.0mm)       |
|                                    | CardBox_MainDeck2 (98.0 x 73.0mm)  +-----------------------+
|                                    |                                    | CommonTokensBox       |
+------------------------------------+------------------------------------+ (90.0 x 213.0 x 25mm) |
| Automatic 3D Void Spacers          | CardBox_MainDeck3 (98.0 x 73.0mm)  |                       |
| (Y = 142.5..287mm)                 +------------------------------------+                       |
|                                    | Automatic 3D Spacers               |                       |
+------------------------------------+------------------------------------+-----------------------+
|<-------------- 98.0mm ------------>|<-------------- 98.0mm ------------>|<------- 90.0mm ------>|
```
