# Biome Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Biome** board game organizer, ported from `boxes/biome/biome.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `285.0mm (Width) x 285.0mm (Length) x 73.0mm (Height)`
* **Board & Score Pad Reserve**: `20.0mm` (Main game board + player mats sit atop insert at `Z = 53.0 .. 73.0mm`)
* **Main Insert Usable Height**: `53.0mm` (`52.0mm` insert stack with `1.0mm` vertical slack per `biome.scad`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `3.0mm`
* **Clearance Slack**: `0.0mm`
* **Card Dimensions**: `66.0mm x 91.0mm`
* **Expandable**: `False` (`box_defaults={"expandable": False}`)

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Player Bits (4 Colors) | Red, Blue, Green, Yellow wooden cubes & tokens | `PlayerBox_Red` .. `PlayerBox_Yellow` (4 boxes) | Cap Lid | Color-coded Framed lids |
| Food & Animal Tokens (8 Types) | Mouse, Sun, Fish, Leaf, Spider, Berry, Chicks, Rabbits | `Resource_Mouse` .. `Resource_Rabbits` (8 boxes) | Cap Lid | Color-coded Framed lids |
| Nest Player Boards | 4 cardboard nest strips (`45.0 x 180.0mm`) | `NestBox` | Cap Lid | Framed "Nests" (Peru) |
| Main Plant & Animal Cards | 2 main play decks (`66.0 x 91.0mm`) | `CardBox_MainDeck1`, `CardBox_MainDeck2` (2 boxes) | Sliding Lid | Framed "Play" |
| Starting Cards | 14 starting cards | `CardBox_Starting` | Sliding Lid | Framed "Starting" |
| Achievement Cards | 13 achievement cards | `CardBox_Achievement` | Sliding Lid | Framed "Achievement" |
| Changing Condition Cards | 11 condition cards | `CardBox_ChangingCondition` | Sliding Lid | Framed "Change" |
| Legend Cards | 9 legend cards | `CardBox_Legend` | Sliding Lid | Framed "Legend" |
| Extra Plant & Animal Cards | Overflow plant/animal deck | `CardBox_PlantAnimalExtra` | Sliding Lid | Framed "Play Extra" |
| Big Biome Cards | Full-height rotated deck (`98.0 x 73.0 x 52.0mm`) | `CardBox_BigBiome` | Sliding Lid | Framed "Biome" |
| Climate Spinner | `133.0mm` diameter seasonal spinner (`9.0mm` thick) | `SpinnerHolder` | No-Lid Tray | Open recessed cradle |
| Extra Bits | Phase/year cubes, coin (`26.0mm`), die (`17.0mm`), crescent & leaf tokens | `ExtraBitsBox` | Cap Lid | Framed "Biome" |
| Game Boards | Folding boards (`255.0mm` wide) | Sits atop insert (`Z = 53.0 .. 73.0mm`) | Board Layer | Flat storage beneath game lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto-generated |

---

## 3. Sub-Box Specifications

### 3.1 Column 0: Player & Resource Matrix (`X = 0.0 .. 57.0mm`)
* **Dimensions**: `57.0mm x 70.75mm x 17.33mm` each (`BoxType.CAP`).
* **Arrangement**: 4 longitudinal positions x 3 stacked layers (`Z = 0.0 .. 52.0mm`), 12 boxes total.

### 3.2 Column 1: Nest Strip Tray (`X = 57.0 .. 109.0mm`)
* **Dimensions**: `52.0mm x 283.0mm x 52.0mm` (`BoxType.CAP`).

### 3.3 Columns 2–3: Card Boxes & Spinner Holder (`X = 109.0 .. 255.0mm`)
* **Main Play Decks (`Y = 0.0 .. 98.0mm`)**: `CardBox_MainDeck1` & `CardBox_MainDeck2`, `73.0mm x 98.0mm x 41.0mm` each.
* **Card Stack Left (`X = 109.0, Y = 98.0 .. 196.0mm`)**: `CardBox_Starting` (`14.4mm`) + `CardBox_Achievement` (`13.8mm`) + `CardBox_ChangingCondition` (`12.6mm`) = `40.8mm`.
* **Card Stack Right (`X = 182.0, Y = 98.0 .. 196.0mm`)**: `CardBox_Legend` (`11.4mm`) + `CardBox_PlantAnimalExtra` (`29.6mm`) = `41.0mm`.
* **Big Biome Deck (`X = 109.0, Y = 196.0 .. 269.0mm`)**: `98.0mm x 73.0mm x 52.0mm`.
* **SpinnerHolder (`X = 109.0 .. 283.0mm, Y = 0.0 .. 185.0mm, Z = 41.0 .. 52.0mm`)**: `174.0mm x 185.0mm x 11.0mm` resting atop the card boxes and `ExtraBitsBox`.

### 3.4 Column 4: Extra Bits Box (`X = 255.0 .. 284.0mm`)
* **Dimensions**: `29.0mm x 284.0mm x 41.0mm` (`BoxType.CAP`).
