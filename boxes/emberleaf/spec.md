# Emberleaf Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Emberleaf** board game organizer, ported from `boxes/emberleaf/emberleaf.scad` to PythonSCAD (`pyboxbuilder`).

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
* **Expandable**: `False` (`box_defaults={"expandable": False}`)

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Player Animal Workers & Heroes (5 Colors) | Black, Red, Yellow, Blue, Grey (owls, rabbits, frogs, rats, hero, markers, hexes, victory tokens) | `PlayerBoxBlack`, `PlayerBoxRed`, `PlayerBoxYellow`, `PlayerBoxBlue`, `PlayerBoxGrey` (5 boxes) | Cap Lid | Color-coded Framed lids |
| Material Resource Tokens (4 Types) | Food, Stone, Honey, Wood tokens | `MaterialBoxFood`, `MaterialBoxStone`, `MaterialBoxHoney`, `MaterialBoxWood` (4 boxes) | Cap Lid | Color-coded Framed "Food", "Stone", "Honey", "Wood" |
| Main Card Decks | Favor, Hero, and Solo decks (`66.0 x 91.0mm`) | `CardBoxFavor`, `CardBoxHero`, `CardBoxSolo` (3 boxes) | Sliding Lid | Framed "Favors", "Heroes", "Solo" |
| Player Starting Decks (5 Colors) | Black, Blue, Yellow, Grey, Red player decks (`66.0 x 91.0mm`) | `CardBoxPlayerBlack`, `CardBoxPlayerBlue`, `CardBoxPlayerYellow`, `CardBoxPlayerGrey`, `CardBoxPlayerRed` (5 boxes) | Sliding Lid | Color-coded Framed player deck lids |
| Common Hexes & Trophies | 5 common hex stacks (`38.5mm`) + trophy tiles (`26.0 x 36.0mm`) + marker | `CommonBox` | Cap Lid | Framed "Trophy" (Saddle Brown) |
| Game Boards & Mats | Village boards and player mats | Sits atop insert (`Z = 52.5 .. 79.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | 3 leftover voids (`SpacerFront`, `SpacerSide`, `SpacerPlayer`) | Derived automatically | No-Lid Trays | Auto-generated |

---

## 3. Sub-Box Specifications

### 3.1 Column 0: Player & Material Boxes (`X = 0.0 .. 98.0mm`)
* **Player Boxes (x5)**: `98.0mm x 142.5mm x 13.125mm` each (`BoxType.CAP`), occupying 5 of the 8 half-length slots across 4 stacked layers (`Z = 0.0 .. 52.5mm`).
* **Material Boxes (x4)**: `98.0mm x 71.25mm x 13.125mm` each (`BoxType.CAP`), occupying 2 of the remaining 3 half-length slots (`Food` & `Stone` on layer 2, `Honey` & `Wood` on layer 3).
* **Remaining Slot**: Layer 3 back half (`Y = 142.5 .. 287.0mm`) filled by automatic `spacer_3`.

### 3.2 Column 1: Main Card Boxes (`X = 98.0 .. 196.0mm`)
* **`CardBoxFavor`, `CardBoxHero`, `CardBoxSolo`**: `98.0mm x 73.0mm x 52.5mm` each (`BoxType.SLIDING`) along `Y = 0.0 .. 219.0mm`.
* **Remaining Length**: `Y = 219.0 .. 287.0mm` filled by automatic `spacer_2`.

### 3.3 Column 2: Player Decks & Common Box (`X = 196.0 .. 286.0mm`)
* **Player Card Boxes (x5)**: `90.0mm x 98.0mm x 10.5mm` each (`BoxType.SLIDING`), stacked 5 high (`Z = 0.0 .. 52.5mm`) at `Y = 0.0 .. 98.0mm`.
* **`CommonBox`**: `90.0mm x 188.0mm x 25.0mm` (`BoxType.CAP`) at `Y = 98.0 .. 286.0mm, Z = 0.0 .. 25.0mm`.
* **Remaining Height Above CommonBox**: `Z = 25.0 .. 52.5mm` filled by automatic `spacer_1`.
