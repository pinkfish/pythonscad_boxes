# Ada's Dream Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Ada's Dream** board game organizer, ported from `examples/adas_dream.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `212.0mm (Width) x 291.0mm (Length) x 90.0mm (Height)`
* **Board & Player Mat Reserve**: `31.0mm` (Main game board + player mats sit atop insert at `Z = 59.0 .. 90.0mm`)
* **Main Insert Usable Height**: `59.0mm` (`Z = 0.0 .. 59.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Standard Cards**: `66.0mm x 91.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Player Pieces (4 Colors) | Red, Blue, Green, Purple figures, discs, steam tokens | `PlayerBox_Red` .. `PlayerBox_Purple` (4 boxes) | Sliding Lid | Color-coded Framed lids |
| Scoring & Coins | Scoring markers, silver coins | `ScoringBox`, `MoneyBox` | Sliding Lid | Framed "Scoring" & "Money" |
| Standard Playing Cards | Partner, exhibitor, tier cards (`66 x 91mm`) | `OtherCardBox`, `TierCardBox` | Sliding Lid | Framed "Cards" & "Tiers" |
| Mechanical Gears (Cogs) | Addition, subtraction, multiplication gear tokens | `GearBox_AddGears` .. `GearBox_MulGears` | Cap Lid | Framed "Gears" (Peru) |
| Wooden Dice | 50 colored engine dice (`14.5mm`) | `DiceBox` | Cap Lid | Framed "Dice" (Firebrick) |
| Book & Program Tokens | Book tokens, universities, programs | `BookBox` | Cap Lid | Framed "Books" (Teal) |
| Board & Player Aids | Folded game board + player boards | Sits atop insert (`Z = 59.0 .. 90.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Player & Currency Section (Columns 0 & 1, `Y = 0.0 .. 97.0mm`)
* **Dimensions**: `72.0mm x 97.0mm x 19.66mm` each.
* **Arrangement**: Stored in 2 columns of 3 tiers (`Z = 0.0 .. 59.0mm`):
  * Left Column (`X = 0`): `PlayerBox_Red`, `PlayerBox_Green`, `ScoringBox`.
  * Right Column (`X = 72mm`): `PlayerBox_Blue`, `PlayerBox_Purple`, `MoneyBox`.

### 3.2 Cards & Dice Section (`Y = 97.0 .. 194.0mm`)
* **`OtherCardBox` & `TierCardBox`**: `72.0mm x 97.0mm x 29.5mm` each, stacked at `X = 72mm`.
* **`DiceBox` & `BookBox`**: `72.0mm x 48.5mm x 29.5mm` each at `X = 0mm`.

### 3.3 Gear Section (`Y = 194.0 .. 274.0mm`)
* **`GearBox_AddGears` .. `GearBox_MulGears`**: `72.0mm x 80.0mm x 19.66mm`, stacked 3 high.

---

## 4. 3D Spatial Layout Map

```
+------------------------------------+------------------------------------+
| PlayerBox_Red / Green / Scoring    | PlayerBox_Blue / Purple / Money    |
| (Stacked 3-high, 19.66mm each)     | (Stacked 3-high, 19.66mm each)     |
| (72.0 x 97.0mm)                    | (72.0 x 97.0mm)                    |
+------------------------------------+------------------------------------+
| DiceBox (72.0 x 48.5mm)            | OtherCardBox / TierCardBox         |
+------------------------------------+ (Stacked 2-high, 29.5mm each)       |
| BookBox (72.0 x 48.5mm)            | (72.0 x 97.0mm)                    |
+------------------------------------+------------------------------------+
| Automatic 3D Void Spacers          | GearBox_Add / Sub / Mul            |
| (Remaining volume to X: 212mm,     | (Stacked 3-high, 19.66mm each)     |
|  Y: 291mm)                         | (72.0 x 80.0mm)                    |
+------------------------------------+------------------------------------+
```
