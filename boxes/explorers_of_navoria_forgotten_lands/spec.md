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
| 5th Player Pieces (White) | White trading posts, explorers, markers | `PlayerBox_White`, `PlayerBox_White_2` | Cap Lid | Framed "Player (White 1/2)" |
| Solo & Contract Tokens | Solo mode and contract tokens | `SpeciesTokensBox`, `ContractTokensBox` | Sliding Lid | Framed "Solo" (Peru) & "Contract" (Sienna) |
| Faction Skill Boards | Large cardboard faction power tiles | `FactionSkillBox` | Sliding Lid | Framed "Faction Skills" (Purple) |
| Exploration Bits | Bonus exploration markers and bits | `ExplorationBitsBox` | Cap Lid | Framed "Exploration Bits" (Orange) |
| Forgotten Lands Cards | Expansion adventure and quest cards | `ExpansionCardsBox` | Sliding Lid | Framed "Forgotten Cards" (Navy) |
| Automatic Spacers | Remaining 3D void volume (`44 x 150 x 23mm`) | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 5th Player & Token Column (Column 0, Width `98.0mm`)
* **`PlayerBox_White` & `PlayerBox_White_2`**: `98.0mm x 133.0mm x 23.0mm` each.
* **`SpeciesTokensBox` & `ContractTokensBox`**: `98.0mm x 133.0mm x 23.0mm` each, stacked 2 high (`Z = 0.0` and `Z = 23.0mm`).

### 3.2 Skills, Bits & Cards Column (Column 1, Width `111.0mm`)
* **`ExplorationBitsBox`**: `111.0mm x 150.0mm x 23.0mm` (lower tier).
* **`FactionSkillBox`**: `67.0mm x 150.0mm x 23.0mm` (upper tier, with `44.0mm x 150.0mm x 23.0mm` auto-spacer beside it).
* **`ExpansionCardsBox`**: `111.0mm x 116.0mm x 46.0mm`.

---

## 4. 3D Spatial Layout Map

```
+------------------------------------+------------------------------------+
| ExpansionCardsBox                  | PlayerBox_White / PlayerBox_White_2|
| (111.0 x 116.0 x 46.0mm)           | (98.0 x 133.0 x 23.0mm, Z: 0..46)  |
+------------------------------------+------------------------------------+
| ExplorationBitsBox (111 x 150,     | SpeciesTokensBox / ContractTokens  |
|  Z: 0..23mm)                       | (98.0 x 133.0 x 23.0mm, Z: 0..46)  |
| FactionSkillBox (67 x 150, Z:23..46|                                    |
|  + Auto-Spacer 44 x 150, Z:23..46) |                                    |
+------------------------------------+------------------------------------+
|<-------------- 111.0mm ----------->|<-------------- 98.0mm ------------>|
```
