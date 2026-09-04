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
| Athlete Character Cards | Full deck of athlete cards (`67 x 90mm`) | `AthleteCardsBox` | Sliding Lid | Framed "Athlete Cards" (Dark Blue) |
| Large Dice | Custom racing dice (`21mm`) | `DiceBox` | Cap Lid | Framed "Dice" (Crimson) |
| Gold & Silver Medal Tokens | Gold, Silver, Bronze award tokens | `AwardMedalBox` | Cap Lid | Framed "Medals" (Gold) |
| Athlete Standee Pieces | Character standees (11mm thick pieces) | `AthletePiecesBox_1` & `AthletePiecesBox_2` | Cap Lid | Framed "Athletes 1/2" (Orange) |
| Big Baby Standee | Oversized figure (`39 x 35.5 x 32mm`) | `BigBabyBox` | Cap Lid | Framed "Big Baby" (Purple) |
| Race Track & Board | Folded track board | Sits on top of insert (`Z = 38.0 .. 45.0mm`) | Board Layer | Flat storage under box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Card & Dice Column (Row 1, `Y = 0.0 .. 73.0mm`)
* **`AthleteCardsBox`** (`96.0mm x 73.0mm x 38.0mm`): Sized for standard sleeved athlete cards with side finger scoop.
* **`DiceBox`** (`88.0mm x 73.0mm x 26.0mm`): Holds racing dice.
* **`AwardMedalBox`** (`88.0mm x 73.0mm x 12.0mm`): Stacks on top of the dice box at `Z = 26.0mm`.

### 3.2 Athlete Standee Trays (Row 2 & 3, `Y = 73.0 .. 248.0mm`)
* **`AthletePiecesBox_1`** and **`AthletePiecesBox_2`** (`184.0mm x 87.5mm x 19.0mm`):
  * Span the full 184mm width of the box.
  * 4 partitioned slots per box for organizing athlete standees by team.

### 3.3 Big Baby Box (Row 4, `Y = 248.0 .. 294.0mm`)
* **`BigBabyBox`** (`61.5mm x 46.0mm x 38.0mm`): Deep well accommodating the oversized Big Baby miniature.

---

## 4. 3D Spatial Layout Map

```
+-----------------------------------+-------------------------------------------+
| AthleteCardsBox (96.0 x 73.0mm)   | DiceBox (88.0 x 73.0 x 26.0mm, Z: 0..26)  |
| (Height: 38.0mm, Z: 0..38mm)      | [ AwardMedalBox atop DiceBox, Z: 26..38 ] |
+-----------------------------------+-------------------------------------------+
| AthletePiecesBox_1 (Full width: 184.0mm, Length: 87.5mm, Height: 19.0mm)     |
+-------------------------------------------------------------------------------+
| AthletePiecesBox_2 (Full width: 184.0mm, Length: 87.5mm, Height: 19.0mm)     |
+-----------------------------------+-------------------------------------------+
| BigBabyBox (61.5 x 46.0 x 38.0mm) | Automatic Void Spacers                    |
+-----------------------------------+-------------------------------------------+
```
