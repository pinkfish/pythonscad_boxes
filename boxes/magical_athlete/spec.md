# Magical Athlete Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Magical Athlete** board game organizer, ported from `examples/magical_athlete.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `184.0mm (Width) x 294.0mm (Length) x 45.0mm (Height)`
* **Board Thickness**: `7.0mm` (Game track board sits atop the insert at `Z = 38.0 .. 45.0mm`)
* **Main Insert Usable Height**: `38.0mm` (`Z = 0.0 .. 38.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Card Dimensions**: `67.0mm x 90.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Athlete Character Cards | Full deck of athlete cards (`67 x 90mm`) | `AthleteCardsBox` | Sliding Lid | Framed "Athletes" (Dark Blue) |
| Large Dice | Custom racing dice (`21mm`) | `DiceBox` | Cap Lid | Framed "Dice" (Crimson) |
| Gold & Silver Medal Tokens | Gold, Silver, Bronze award tokens | `AwardMedalBox` | Slipover Lid | Framed "Awards" (Gold) |
| Athlete Standee Pieces | Character standees (11mm thick pieces) | `AthletePiecesBox_1` & `AthletePiecesBox_2` | Cap Lid | Framed "Athletes 1/2" (Orange) |
| Big Baby Standee | Oversized figure (`39 x 35.5 x 32mm`) | `BigBabyBox` | Cap Lid | Framed "Big Baby" (Purple) |
| Award Value Tokens (1 & 3) | 1-point and 3-point award tokens | `AwardTokensBox_1` & `AwardTokensBox_3` | Cap Lid | Framed "Awards 1/3" (Saddle Brown) |
| Race Track & Board | Folded track board | Sits on top of insert (`Z = 38.0 .. 45.0mm`) | Board Layer | Flat storage under box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Athlete Standee Trays (`Y = 0.0 .. 175.0mm`)
* **`AthletePiecesBox_1`** and **`AthletePiecesBox_2`** (`184.0mm x 175.0mm x 19.0mm`):
  * Span the full 184mm width and 175mm length, stacked 2-high (`Z = 0.0..19.0mm` and `Z = 19.0..38.0mm`).
  * 4 partitioned slots per box for organizing athlete standees and tall pieces.

### 3.2 Card, Dice & Award Medal Row (`Y = 175.0 .. 248.0mm`)
* **`AthleteCardsBox`** (`96.0mm x 73.0mm x 38.0mm`): Sized for standard athlete cards with side finger scoop.
* **`DiceBox`** (`88.0mm x 73.0mm x 26.0mm`): Holds racing dice.
* **`AwardMedalBox`** (`88.0mm x 73.0mm x 12.0mm`, Slipover Lid): Stacks on top of the dice box at `Z = 26.0..38.0mm`.

### 3.3 Big Baby & Award Tokens Row (`Y = 248.0 .. 294.0mm`)
* **`BigBabyBox`** (`61.5mm x 46.0mm x 38.0mm`): Deep well accommodating the oversized Big Baby miniature.
* **`AwardTokensBox_1`** and **`AwardTokensBox_3`** (`50.0mm x 46.0mm x 19.0mm` each): Stacked 2-high (`Z = 0.0..19.0mm` and `Z = 19.0..38.0mm`) for the 1-point and 3-point award tokens.
* **Automatic Spacers**: Fill the remaining `72.5mm x 46.0mm x 38.0mm` void along this row.

---

## 4. 3D Spatial Layout Map

```
+-------------------------------------------------------------------------------+
| AthletePiecesBox_1 (184.0 x 175.0 x 19.0mm, Z: 0..19mm)                       |
| [ AthletePiecesBox_2 stacked atop, Z: 19..38mm ]                              |
+-----------------------------------+-------------------------------------------+
| AthleteCardsBox (96.0 x 73.0mm)   | DiceBox (88.0 x 73.0 x 26.0mm, Z: 0..26)  |
| (Height: 38.0mm, Z: 0..38mm)      | [ AwardMedalBox atop DiceBox, Z: 26..38 ] |
+--------------------+--------------+---------------------+---------------------+
| BigBabyBox         | Auto Spacer  | AwardTokensBox_1    | Auto Spacer         |
| (61.5 x 46 x 38mm) | (34.5x46x38) | [ AwardTokensBox_3  | (38.0 x 46 x 38mm)  |
|                    |              |   50 x 46 x 19mm ]  |                     |
+--------------------+--------------+---------------------+---------------------+
```
