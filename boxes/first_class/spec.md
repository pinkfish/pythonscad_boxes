# First Class: All Aboard the Orient Express Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **First Class: All Aboard the Orient Express** board game organizer, ported from `boxes/first_class/first_class.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `217.0mm (Width) x 307.0mm (Length) x 70.0mm (Height)`
* **Board & Rulebook Reserve**: `5.5mm` (`board_thickness = 2.5mm`, `rule_book_thickness = 3.0mm`)
* **Main Insert Usable Height**: `64.5mm` (`Z = 0.0 .. 64.5mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Card Dimensions**: `47.0mm x 70.0mm`
* **Expandable**: `False` (`box_defaults={"expandable": False}`)

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Player Meeples, Trains, Cards & Cubes (4 Colors) | Yellow, Blue, Red, Green | `PlayerBox_yellow`, `PlayerBox_blue`, `PlayerBox_red`, `PlayerBox_green` (4 boxes) | Sliding Lid | Color-coded Framed "Player" |
| Money Coins | 18.5mm diameter coins | `MoneyBox` | Sliding Lid | Framed "Money" (LightGrey) |
| Evidence Tokens | `22.0 x 18.5mm` evidence tokens | `EvidenceBox` | Sliding Lid | Framed "Evidence" (LightSalmon) |
| Module Cards (Modules A–E) & Base/Mail/Evidence Decks | 8 decks (`47.0 x 70.0mm` cards) | `CardBox_ModuleA` .. `CardBox_ModuleE`, `CardBox_BaseCards_1`, `CardBox_BaseCards_2`, `CardBox_EvidenceAndMail` (8 boxes) | Sliding Lid | Framed "Module A" .. "Mail & Ev." |
| Railroad Cards (0–1, 2–4, 7–12) | 50 / 24 / 20 cards | `CardBox_Railroad01`, `CardBox_Railroad24`, `CardBox_Railroad712` (3 boxes) | Sliding Lid | Framed "0-1", "2-4", "7-12" (Cyan) |
| Whodunit Cards | 4 whodunit cards | `CardBox_Whodunit` | Sliding Lid | Framed "Whodunit" |
| Game End Cards | 21 game-end cards | `CardBox_GameEnd` | Sliding Lid | Framed "End" (DeepSkyBlue) |
| Start Player Tile | `44.5 x 68.0mm` start tile | `StartTileCardBox` | Sliding Lid | Framed "Start" (Khaki) |
| Locomotive Tiles | 9 locomotive tiles (`68.5 x 64.5mm`) | `LocomotiveTileBox` | Sliding Lid | Framed "Locomotive" (Aquamarine) |
| Score Board & Rulebook | Main scoreboard + rulebook | Sits on top of insert (`Z = 64.5 .. 70.0mm`) | Board Layer | Flat storage beneath game box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto-generated |

---

## 3. Sub-Box Specifications

### 3.1 Row 1: Player, Money & Evidence Boxes (`Y = 0.0 .. 53.0mm`)
* **Dimensions**: `108.5mm x 53.0mm x 21.5mm` each (`BoxType.SLIDING`).
* **Arrangement**: 2 columns x 3 stacked layers (`3 x 21.5mm = 64.5mm`).
  * Left column (`X = 0.0mm`): `PlayerBox_yellow`, `PlayerBox_blue`, `PlayerBox_red`.
  * Right column (`X = 108.5mm`): `PlayerBox_green`, `MoneyBox`, `EvidenceBox`.

### 3.2 Row 2: Card Boxes (`Y = 53.0 .. 129.0mm`)
* **Footprint**: `54.25mm x 76.0mm` each (`BoxType.SLIDING`), 4 columns across `217.0mm`.
* **Columns 0–2**: 8 `ModuleCardBox`-sized decks (`21.5mm` tall) + `CardBox_Railroad712` (`21.5mm` tall) at `(col=2, layer=2)`.
* **Column 3 (`X = 162.75mm`)**: `CardBox_Railroad01` (`35.0mm`) + `CardBox_Railroad24` (`19.4mm`) + `CardBox_Whodunit` (`10.1mm`) = `64.5mm`.

### 3.3 Row 3: Game End, Start Tile & Locomotive Boxes (`Y = 129.0 .. 205.0mm`)
* **CardBox_GameEnd**: `54.25mm x 76.0mm x 20.0mm` at `(0.0, 129.0, 0.0)`.
* **StartTileCardBox**: `54.25mm x 76.0mm x 7.5mm` stacked at `(0.0, 129.0, 20.0)`.
* **LocomotiveTileBox**: `74.5mm x 76.0mm x 27.5mm` at `(54.25, 129.0, 0.0)`.
