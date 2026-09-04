# Moonrakers Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Moonrakers** board game organizer, ported from `examples/moonrakers.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `213.0mm (Width) x 303.0mm (Length) x 93.0mm (Height)`
* **Board & Player Mat Reserve**: `37.5mm` (Main game board + 5 command consoles + Binding Ties board sit atop insert at `Z = 55.5 .. 93.0mm`)
* **Main Insert Usable Height**: `55.5mm` (`Z = 0.0 .. 55.5mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Card Dimensions**: `67.0mm x 90.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Action Command Cards | Thrusters, Damage, Reactor, Shield, Miss cards | `CardBox_Thrusters` .. `CardBox_Miss` | Sliding Lid | Color-coded Framed lids |
| Market & Ship Cards | Crew members, Contracts, Ship Parts | `CardBox_Crew` .. `CardBox_Ships` | Sliding Lid | Framed deck names |
| Secret Objectives | Base & expansion secret objective cards | `CardBox_Objectives` | Sliding Lid | Framed "Objectives" (Teal) |
| Hazard Dice & Tokens | Custom hazard dice, prestige coins | `DiceAndTokensBox` | Cap Lid | Framed "Hazard Dice" (Firebrick) |
| Command Consoles & Boards | Player boards and game board | Sits atop insert (`Z = 55.5 .. 93.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Command & Market Decks (`X = 0.0 .. 192.0mm`, `Y = 0.0 .. 292.0mm`)
* **Dimensions**: `96.0mm x 73.0mm x 27.75mm` each.
* **Arrangement**: 2 columns across X, 4 rows along Y, stacked 2 high (`Z = 0.0` and `Z = 27.75mm`).

### 3.2 Objectives & Hazard Dice (`Z = 27.75 .. 55.5mm`)
* **`CardBox_Objectives`**: Stacked atop column 0 at `Y = 0.0mm`.
* **`DiceAndTokensBox`**: Stacked atop column 1 at `Y = 0.0mm`.

---

## 4. 3D Spatial Layout Map

```
+------------------------------------+------------------------------------+
| CardBox_Thrusters (Z: 0..27.7mm)   | CardBox_Damage (Z: 0..27.7mm)      |
| CardBox_Objectives (Z: 27.7..55.5) | DiceAndTokensBox (Z: 27.7..55.5)   |
| (96.0 x 73.0mm)                    | (96.0 x 73.0mm)                    |
+------------------------------------+------------------------------------+
| CardBox_Reactor (96.0 x 73.0mm)    | CardBox_Shield (96.0 x 73.0mm)     |
+------------------------------------+------------------------------------+
| CardBox_Miss (96.0 x 73.0mm)       | CardBox_Crew (96.0 x 73.0mm)       |
+------------------------------------+------------------------------------+
| CardBox_Contracts (96.0 x 73.0mm)  | CardBox_Ships (96.0 x 73.0mm)      |
+------------------------------------+------------------------------------+
|                           Automatic 3D Void Spacers                     |
|                    (X = 192..213mm, Y = 292..303mm)                     |
+-------------------------------------------------------------------------+
```
