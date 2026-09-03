# Explorers of Navoria: Forgotten Lands Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Explorers of Navoria: Forgotten Lands** expansion organizer, ported from `examples/explorers_of_navoria_forgotten_lands.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `211.0mm (Width) x 268.0mm (Length) x 50.0mm (Height)`
* **Board & Overlay Reserve**: `4.0mm` (Faction boards and player overlays sit atop insert at `Z = 46.0 .. 50.0mm`)
* **Main Insert Usable Height**: `46.0mm` (`Z = 0.0 .. 46.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Expansion Cards**: `68.0mm x 92.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| 5th Player Pieces (White) | White trading posts, explorers, markers | `PlayerBox_White` | Cap Lid | Framed "Player (White)" |
| Species Tokens | Wooden species scoring tokens | `SpeciesTokensBox` | Cap Lid | Framed "Species Tokens" (Peru) |
| Faction Skill Boards | Large cardboard faction power tiles | `FactionSkillBox` | Cap Lid | Framed "Faction Skills" (Purple) |
| Exploration Bits | Bonus exploration markers and bits | `ExplorationBitsBox` | Cap Lid | Framed "Exploration Bits" (Orange) |
| Forgotten Lands Cards | Expansion adventure and quest cards | `ExpansionCardsBox` | Sliding Lid | Framed "Forgotten Cards" (Navy) |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 5th Player & Species Column (Column 0, `X = 0.0 .. 98.0mm`)
* **`PlayerBox_White` & `SpeciesTokensBox`**: `98.0mm x 133.0mm x 23.0mm` each, stacked 2 high (`Z = 0.0` and `Z = 23.0mm`).

### 3.2 Skills, Bits & Cards Column (Column 1, `X = 98.0 .. 209.0mm`)
* **`FactionSkillBox` & `ExplorationBitsBox`**: `111.0mm x 150.0mm x 23.0mm` each, stacked 2 high at `Y = 0.0 .. 150.0mm`.
* **`ExpansionCardsBox`**: `111.0mm x 116.0mm x 46.0mm` at `Y = 150.0 .. 266.0mm`.

---

## 4. 3D Spatial Layout Map

```
+------------------------------------+------------------------------------+
| PlayerBox_White (98.0 x 133.0mm,   | FactionSkillBox (111.0 x 150.0mm,  |
|  Z: 0..23.0mm)                     |  Z: 0..23.0mm)                     |
+------------------------------------+------------------------------------+
| SpeciesTokensBox (98.0 x 133.0mm,  | ExplorationBitsBox (111.0 x 150.0, |
|  Z: 23..46.0mm)                    |  Z: 23..46.0mm)                    |
+------------------------------------+------------------------------------+
| Automatic 3D Void Spacers          | ExpansionCardsBox                  |
| (Y = 133..268mm, Z = 0..46.0mm)    | (111.0 x 116.0 x 46.0mm)           |
+------------------------------------+------------------------------------+
|<-------------- 98.0mm ------------>|<-------------- 111.0mm ----------->|
```
