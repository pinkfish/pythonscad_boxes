# Explorers of Navoria Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Explorers of Navoria** board game organizer, ported from `boxes/explorers_of_navoria/explorers_of_navoria.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `211.0mm (Width) x 268.0mm (Length) x 68.0mm (Height)`
* **Board & Player Mat Reserve**: `12.0mm` (Main game board sits atop insert at `Z = 56.0 .. 68.0mm`; 4 player layout boards sit over the right column at `Z = 48.0 .. 56.0mm`)
* **Main Insert Usable Height**: `56.0mm` (`Z = 0.0 .. 56.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Standard Cards**: `68.0mm x 92.0mm`
* **Expandable**: `False` (`box_defaults={"expandable": False}`)

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Player Trading Posts (4 Factions) | Green, Yellow, Purple, Black trading posts | `PlayerBox_Green_One`, `PlayerBox_Yellow_One`, `PlayerBox_Purple_One`, `PlayerBox_Black_One` (4 boxes) | Cap Lid | Color-coded Framed lids |
| Player Explorers & Turn Order Birds (4 Factions) | Green, Yellow, Purple, Black explorer markers & birds | `PlayerBox_Green_Two`, `PlayerBox_Yellow_Two`, `PlayerBox_Purple_Two`, `PlayerBox_Black_Two` (4 boxes) | Cap Lid | Color-coded Framed lids |
| Favour Tiles | 10 cardboard favour tiles (2 stacks of 5) | `FavourBox` | Cap Lid | Framed "Favours" (DarkOrange) |
| Resource Tokens (3 Types) | Swords, Apples, Crystals | `StuffBox_Swords`, `StuffBox_Apples`, `StuffBox_Crystals` (3 boxes) | Sliding Lid | Framed "Swords", "Apples", "Crystals" |
| Adventure & Reference Cards | 60 Adventure cards + 4 reference cards (`68.0 x 92.0mm`) | `CardBox` | Sliding Lid | Framed "Cards" (Navy) |
| Drawing Bag & Large Bits | Cloth drawing bag and round tokens | `BagBox` | No-Lid Tray | Open hollow tray |
| Board & Player Mats | Folded game board + 4 player layout boards | Sits atop insert (`Z = 48.0 .. 68.0mm`) | Board Layer | Flat storage beneath box lid |

---

## 3. Sub-Box Specifications

### 3.1 Column 0: Player Faction Stacks (`X = 0.0 .. 98.0mm`)
* **Dimensions**: `98.0mm x 133.0mm x 14.0mm` each (`BoxType.CAP`).
* **Front Stack (`Y = 0.0 .. 133.0mm`)**: `PlayerBox_Green_One`, `PlayerBox_Yellow_One`, `PlayerBox_Purple_One`, `PlayerBox_Black_One` stacked 4 high (`Z = 0.0 .. 56.0mm`).
* **Back Stack (`Y = 133.0 .. 266.0mm`)**: `PlayerBox_Green_Two`, `PlayerBox_Yellow_Two`, `PlayerBox_Purple_Two`, `PlayerBox_Black_Two` stacked 4 high (`Z = 0.0 .. 56.0mm`).

### 3.2 Column 1: Favours, Stuff, Cards & Bag (`X = 98.0 .. 209.5mm`)
* **`FavourBox`**: `111.5mm x 60.0mm x 14.5mm` at `(98.0, 0.0, 0.0)`.
* **`StuffBox_Swords`, `StuffBox_Apples`, `StuffBox_Crystals`**: `37.17mm x 60.0mm x 32.5mm` each, 3 side-by-side atop `FavourBox` at `Z = 14.5 .. 47.0mm`.
* **`CardBox`**: `111.0mm x 74.5mm x 45.0mm` at `(98.0, 60.0, 0.0)`.
* **`BagBox`**: `111.0mm x 131.5mm x 45.0mm` (`BoxType.NO_LID`) at `(98.0, 134.5, 0.0)`.
