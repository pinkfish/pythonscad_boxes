# Moonrakers Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Moonrakers** board game organizer, ported from `examples/moonrakers.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `213.0mm (Width) x 303.0mm (Length) x 93.0mm (Height)`
* **Board & Player Mat Reserve**: `24.0mm` (`9.0mm` main board + `15.0mm` player command consoles, matching `BoxLayout` in `moonrakers.scad`)
* **Main Insert Usable Height**: `69.0mm` (`Z = 0.0 .. 69.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Card Dimensions**: `67.0mm x 90.0mm` (`0.6mm` per card)

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Height | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Thrusters Cards | 25 cards (`21.0mm`) | `CardBox_Thrusters` | Sliding Lid | Framed "Thrusters" (Gold) |
| Damage Cards | 35 cards (`27.0mm`) | `CardBox_Damage` | Sliding Lid | Framed "Damage" (Dark Red) |
| Reactor Cards | 30 cards (`22.5mm`) | `CardBox_Reactor` | Sliding Lid | Framed "Reactor" (Royal Blue) |
| Miss Cards | 15 cards (`13.5mm`) | `CardBox_Miss` | Sliding Lid | Framed "Miss" (Gray) |
| Shield Cards | 25 cards (`20.5mm`) | `CardBox_Shield` | Sliding Lid | Framed "Shield" (Forest Green) |
| Reference Cards | 10 cards (`10.0mm`) | `CardBox_Reference` | Sliding Lid | Framed "Reference" (Slate Gray) |
| Crew Cards (Base + Binding Ties) | 20 + 10 cards (`23.0mm`) | `CardBox_Crew` | Sliding Lid | Framed "Crew" (Dark Orange) |
| Contract Cards (Base + Binding Ties) | 40 + 10 cards (`35.0mm`) | `CardBox_Contracts` | Sliding Lid | Framed "Contracts" (Purple) |
| Ship Part Cards (Base + Binding Ties) | 37 + 10 cards (`33.2mm`) | `CardBox_Ships` | Sliding Lid | Framed "Ship Parts" (Navy) |
| Objective Cards (Base + Binding Ties) | 23 + 10 cards (`24.8mm`) | `CardBox_Objectives` | Sliding Lid | Framed "Objectives" (Teal) |
| Hazard Dice & Tokens | `17mm` dice (`22.0mm`) | `DiceAndTokensBox` | Cap Lid | Framed "Hazard Dice" (Firebrick) |
| Command Consoles & Boards | Main board + player consoles (`24.0mm`) | Sits atop insert (`Z = 69.0 .. 93.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

All 10 card boxes and the dice box share the `96.0mm x 73.0mm` footprint (`X = 0.0 .. 96.0mm`, 4 rows along `Y = 0.0 .. 292.0mm`), stacked to match `moonrakers.scad`:

* **Stack 1 (`Y = 0.0 .. 73.0mm`, `Z = 0.0 .. 69.0mm`)**: `CardBox_Reactor` (`22.5mm`) + `CardBox_Miss` (`13.5mm`) + `CardBox_Crew` (`23.0mm`) + `CardBox_Reference` (`10.0mm`) = `69.0mm`.
* **Stack 2 (`Y = 73.0 .. 146.0mm`, `Z = 0.0 .. 68.5mm`)**: `CardBox_Thrusters` (`21.0mm`) + `CardBox_Damage` (`27.0mm`) + `CardBox_Shield` (`20.5mm`) = `68.5mm`.
* **Stack 3 (`Y = 146.0 .. 219.0mm`, `Z = 0.0 .. 68.2mm`)**: `CardBox_Contracts` (`35.0mm`) + `CardBox_Ships` (`33.2mm`) = `68.2mm`.
* **Stack 4 (`Y = 219.0 .. 292.0mm`, `Z = 0.0 .. 46.8mm`)**: `CardBox_Objectives` (`24.8mm`) + `DiceAndTokensBox` (`22.0mm`) = `46.8mm`, topped by an automatic spacer (`22.2mm`).

---

## 4. 3D Spatial Layout Map

```
+------------------------------------------+------------------------------+
| Reactor (22.5) / Miss (13.5)             |                              |
| Crew (23.0) / Reference (10.0) [69.0mm]  |                              |
+------------------------------------------+                              |
| Thrusters (21.0) / Damage (27.0)         |   Automatic 3D Void Spacer   |
| Shield (20.5)                  [68.5mm]  |   (117.0 x 303.0 x 69.0mm)   |
+------------------------------------------+                              |
| Contracts (35.0) / Ships (33.2) [68.2mm] |                              |
+------------------------------------------+                              |
| Objectives (24.8) / Dice (22.0) [46.8mm] |                              |
| [ Auto Spacer atop, 22.2mm ]             |                              |
+------------------------------------------+------------------------------+
| Auto Spacer (96.0 x 11.0 x 46.8mm)       |                              |
+------------------------------------------+------------------------------+
```
