# March of the Ants Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **March of the Ants** board game organizer (including *Minions of the Meadow* expansion), ported from `boxes/march_of_the_ants/march_of_the_ants.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `195.0mm (Width) x 275.0mm (Length) x 65.0mm (Height)`
* **Board & Score Track Reserve**: `6.0mm` (Score tracks, colony boards, and rules sit atop insert at `Z = 59.0 .. 65.0mm`)
* **Main Insert Usable Height**: `59.0mm` (`Z = 0.0 .. 59.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Hex Territory Width**: `84.0mm` (vertex-to-vertex diameter `96.995mm`)
* **Sleeved Card Dimensions**: `66.0mm x 91.0mm`
* **Expandable**: `False` (`box_defaults={"expandable": False}`)

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Territory Hex Tiles | 25 base game hex tiles (`84.0mm` flat-to-flat) | `HexTileBox` | Cap Lid | Framed "Tiles" (Saddle Brown) |
| Base Evolution Cards | 66 sleeved cards (`66.0 x 91.0mm`) | `CardBox_Base` | Cap Lid | Framed "Cards" (Royal Blue) |
| Minions Expansion Cards | 49 sleeved cards (`66.0 x 91.0mm`) | `CardBox_Expansion` | Cap Lid | Framed "Minions Cards" (Purple) |
| Minions Expansion Hex Tiles | 6 expansion hex tiles (4 aphid, 1 empress, 1 spring) | `MinionsOfTheMeadowBox` | Cap Lid | Framed "Minions Hexes" (Olive) |
| Food, Centipede, Day/Night & Leaf Tokens | 30 food tokens, 15 centipede tokens, day/night & active player leaf | `FoodTokensBox` | Cap Lid | Framed "Food" (Forest Green) |
| Predator Meeples | Spider, mantis, ladybird, fungus, centipede predators | `PredatorsBox` | Cap Lid | Framed "Predator" (Dark Red) |
| Player Ant Colonies (5 Players) | Red, Blue, Yellow, Green, Black cubes, markers & major workers | `PlayerBox_Red` .. `PlayerBox_Black` (5 boxes) | Cap Lid | Color-coded Framed lids |
| Aphids | 36 wooden aphid tokens | `AphidBox` | Cap Lid | Framed "Aphids" (YellowGreen) |
| Score Track & Helper Boards | Score track + 5 player helper boards + rules | Sits atop insert (`Z = 59.0 .. 65.0mm`) | Board Layer | Flat storage beneath box lid |

---

## 3. Sub-Box Specifications

### 3.1 Row 0: Territory Hexes (`Y = 0.0 .. 103.5mm`)
* **`HexTileBox`**: `194.0mm x 103.5mm x 59.0mm` dual-well hex box.

### 3.2 Row 1: Cards, Minions Hexes, Food & Predators (`Y = 103.5 .. 201.5mm`)
* **Left column (`X = 0.0 .. 73.0mm`)**:
  * `CardBox_Base`: `73.0mm x 98.0mm x 33.05mm` (`Z = 0.0 .. 33.05mm`).
  * `CardBox_Expansion`: `73.0mm x 98.0mm x 25.58mm` (`Z = 33.05 .. 58.63mm`).
* **Right column (`X = 73.0 .. 194.0mm`)**:
  * `MinionsOfTheMeadowBox`: `121.0mm x 98.0mm x 16.0mm` (`Z = 0.0 .. 16.0mm`).
  * `FoodTokensBox`: `121.0mm x 98.0mm x 23.5mm` (`Z = 16.0 .. 39.5mm`).
  * `PredatorsBox`: `121.0mm x 98.0mm x 18.5mm` (`Z = 39.5 .. 58.0mm`).

### 3.3 Row 2: Player Ant Colonies & Aphids (`Y = 201.5 .. 274.0mm`)
* **Dimensions**: `97.0mm x 72.5mm x 19.67mm` each, 2 columns x 3 stacked layers (`Z = 0.0 .. 59.0mm`).
  * Left column (`X = 0.0mm`): `PlayerBox_Red`, `PlayerBox_Yellow`, `PlayerBox_Black`.
  * Right column (`X = 97.0mm`): `PlayerBox_Blue`, `PlayerBox_Green`, `AphidBox`.
