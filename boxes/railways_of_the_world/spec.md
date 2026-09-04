# Railways of the World Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Railways of the World** board game organizer, ported from `examples/railways_of_the_world.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `310.0mm (Width) x 385.0mm (Length) x 100.0mm (Height)`
* **Board Thickness**: `22.0mm` (Map boards sit underneath the insert at `Z = 0.0 .. 22.0mm`)
* **Main Insert Usable Height**: `73.0mm` (`Z = 22.0 .. 95.0mm`, total box height 95mm with 5mm top clearance)
* **Wall Thickness**: `2.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `3.0mm`
* **Clearance Slack**: `0.0mm`

---

## 2. Component Inventory & Storage Strategy

Railways of the World is one of the most complex board game inserts due to multi-expansion support (Eastern US, Mexico, Europe, Western US, Great Britain, North America, Portugal, Australia, Sweden), three distinct card sizes, miniature plastic trains, wood/plastic tokens, paper currency, and multi-tier expansion stacking.

| Component / Expansion | Quantity / Dimension | Storage Location | Box Type | Lid Style / Inlay |
|---|---|---|---|---|
| Eastern US Operations Cards | 51 cards (`68 x 92mm`) | `CardBoxEasternUS` (Card Well) | Sliding Lid | Framed "Eastern US" label + US Flag |
| Debt / Bond Cards | 1 deck (`59 x 78 x 17mm`) | `CardBoxEasternUS` (Bond Well) | Sliding Lid | (Integrated in Eastern US box) |
| Australia Expansion Cards | 84 cards (`68 x 92mm`) | `CardBoxAustralia` | Sliding Lid | Framed "Australia" label + Australia SVG |
| Sweden Expansion Cards | 55 cards (`68 x 92mm`) | `CardBoxSweden` | Sliding Lid | Framed "Sweden" label + Sweden SVG |
| Mexico Expansion Cards | 59 cards (`68 x 92mm`) | `CardBoxMexico` | Sliding Lid | Framed "Mexico" label |
| Portugal Expansion Cards | 48 cards (`68 x 92mm`) | `CardBoxPortugal` | Sliding Lid | Framed "Portugal" label + Castle SVG |
| Empty City Markers | Full set (~30 cylindrical markers) | `EmptyCityBox1` & `EmptyCityBox2` | Sliding Lid | Framed "Empty City" label |
| Player Train Miniatures (6 Colors) | Red, Blue, Green, Yellow, Black, Purple | `PlayerBoxTrains_<color>` (6 boxes) | Sliding Lid | Color-coded Framed "Trains" label |
| Player Locomotive Cards & Score Markers | 6 Colors (Cards: `58 x 90mm`, Markers: `15.5mm`) | `PlayerBox_<color>` (6 boxes) | Cap Lid | Color-coded Framed "Player" label |
| Track Hex Tiles | Full base set (`29mm` apothem-to-apothem) | `HexBox1` & `HexBox2` (2 stacked) | Cap Lid | Framed "Tracks" label (4x5 hex grid) |
| Paper Currency | Full bank (`62 x 134mm` bills) | `MoneyBox` | Sliding Lid | Framed "Money" label |
| New City Hex Tiles & Markers | Full set | `NewCityBox` | Cap Lid | Framed "New Cities" label |
| Australia Expansion Track & Tokens | Hexes, 4 Switch Track Tokens & Bonus Tiles | `AustraliaBox` (Upper Tier) | Cap Lid | "Australia" label + Australia Map Inlay |
| Sweden Expansion Track & Tokens | Hexes & 2 Bonus Tiles | `SwedenBox` (Upper Tier) | Cap Lid | "Sweden" label + Sweden Flag/Map Inlay |
| Automatic Gap Spacers | Remaining 3D void volumes | `spacer_1`, `spacer_2`, etc. | No-Lid Spacers | Auto finger scoops on longer walls (FR-014f) |

---

## 3. Sub-Box Specifications

### 3.1 Card Boxes (Sliding Lids, Height: `73.0mm`, Width: `97.0mm`)
* **`CardBoxEasternUS`** (`53.6mm x 97.0mm x 73.0mm`):
  * Dual-well design holding 51 operations cards (`30.6 x 93.0 x 68.0mm`) and debt/bond cards (`17.0 x 78.0 x 59.0mm`).
  * Features an integrated internal divider wall (`1.5mm`) and central finger scoop.
  * Lid engraved with "Eastern US" label.
* **`CardBoxAustralia`** (`54.4mm x 97.0mm x 73.0mm`):
  * Sized for 84 cards with side finger scoop.
  * Lid engraved with "Australia" and Australian emblem inlay.
* **`CardBoxSweden`** (`37.0mm x 97.0mm x 73.0mm`):
  * Sized for 55 cards with side finger scoop.
  * Lid engraved with "Sweden" and Swedish flag emblem inlay.
* **`CardBoxMexico`** (`39.4mm x 97.0mm x 73.0mm`):
  * Sized for 59 cards with side finger scoop.
  * Lid engraved with "Mexico".
* **`CardBoxPortugal`** (`32.8mm x 97.0mm x 73.0mm`):
  * Sized for 48 cards with side finger scoop.
  * Lid engraved with "Portugal" and castle emblem inlay.

### 3.2 Empty City Marker Boxes (`47.0mm x 142.5mm x 56.0mm`)
* Two identical sliding-lid boxes positioned end-to-end along the Y axis (`Y = 97.0mm` and `Y = 239.5mm`).
* Designed to dispense cylindrical Empty City markers directly on the game table during setup.

### 3.3 Player Miniature & Card Boxes (6 Player Colors)
* **Train Miniature Boxes** (`PlayerBoxTrains_<color>`, 6 boxes):
  * Dimensions: `70.0mm x 95.33mm x 28.0mm`.
  * Arranged in two vertical tiers of 3 boxes along the Y axis (`Z = 22.0mm` and `Z = 50.0mm`).
  * Color-coded per player (Red, Blue, Green, Yellow, Black, Purple).
* **Player Locomotive & Marker Boxes** (`PlayerBox_<color>`, 6 boxes):
  * Dimensions: `69.4mm x 95.33mm x 18.67mm`.
  * Low-profile cap-lid boxes stacked 3-high in 2 columns (`X = 117.0mm` and `X = 186.4mm`).
  * Tiered wells for locomotive cards (`58.0 x 90.0 x 11.0mm`, depth 11mm) and recessed player disc marker (`16.0mm dia x 7.0mm`).

### 3.4 Track & Component Boxes
* **`HexBox1` & `HexBox2`** (`139.5mm x 149.0mm x 19.5mm`, 2 stacked boxes):
  * Holds base track tiles in a 4x5 hex layout (`tile_width = 29.0mm`).
  * Cap lid labeled "Tracks".
* **`MoneyBox`** (`69.75mm x 149.0mm x 17.0mm`):
  * Sized for paper currency (`62.0 x 134.0mm bills`) with sliding lid labeled "Money".
* **`NewCityBox`** (`69.75mm x 149.0mm x 17.0mm`):
  * Cap lid labeled "New Cities" with dedicated hex pockets for New City tiles and rectangular compartment for markers.

### 3.5 Expansion Boxes (Upper Tier, `Z = 78.0mm`)
* **`AustraliaBox`** (`47.0mm x 142.0mm x 17.0mm`):
  * Sits above `EmptyCityBox1`.
  * Cap lid labeled "Australia" with Australia map inlay.
  * Internal pockets for 5x4 hexes, 4 switch track tokens, and bonus tiles.
* **`SwedenBox`** (`47.0mm x 142.5mm x 17.0mm`):
  * Sits above `EmptyCityBox2`.
  * Cap lid labeled "Sweden" with Sweden outline inlay.
  * Internal pockets for 6x3 hexes and 2 bonus tiles.

### 3.6 Automatic Spacers
* All leftover voids are automatically partitioned, sized, and generated by `pyboxbuilder` without hard-coded polygon paths (FR-014, FR-014f).
* Each spacer box is automatically fitted with finger scoops on its longer walls to ensure effortless removal.

---

## 4. 3D Spatial Layout & Layering Map

```
+---------------------------------------------------------------------------------------------------------+
| CardBoxEasternUS (53.6) | CardBoxAustralia (54.4) | CardBoxSweden (37.0) | CardBoxMexico (39.4) | CardBoxPortugal (32.8) |
| (X: 0..53.6, Y: 0..97)  | (X: 53.6..108, Y: 0..97)| (X: 108..145, Y:0..97)| (X: 145..184.4)      | (X: 184.4..217.2)      |
+-------------------------+-------------------------+----------------------+----------------------+------------------------+
| EmptyCityBox1           | PlayerBoxTrains (Col 0) | PlayerBox (Col 1)    | HexBox1 / HexBox2 / Money / NewCity           |
| (X: 0..47, Y: 97..239.5)| (X: 47..117, Y: 97..192)| (X: 117..186.4, Y:97)| (X: 117..256.5, Y: 192.3..341.3)               |
| [AustraliaBox at Z=78]  | (Stacked 2 high)        | (Stacked 3 high)     | [Z: 22..41.5, 41.5..61, 61..78]               |
+-------------------------+-------------------------+----------------------+-----------------------------------------------+
| EmptyCityBox2           | PlayerBoxTrains (Col 1) | PlayerBox (Col 2)    | Automatic Side & Top Spacers                  |
| (X: 0..47, Y: 239.5..382| (X: 47..117, Y: 192..287| (X: 186.4..255.8, Y:9| (Fills remaining volume to X:310, Y:385, Z:95) |
| [SwedenBox at Z=78]     | (Stacked 2 high)        | (Stacked 3 high)     |                                               |
+-------------------------+-------------------------+----------------------------------------------------------------------+
```
