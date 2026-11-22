# Nippon Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Nippon** board game organizer, ported from `boxes/nippon/nippon.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `303.0mm (Width) x 380.0mm (Length) x 70.0mm (Height)`
* **Board & Player Mat Reserve**: `32.2mm` (Main game board `9.0mm`, 4 player boards `17.2mm`, player handbook `6.0mm` sit atop the insert)
* **Main Insert Usable Height**: `37.8mm` (`Z = 0.0 .. 37.8mm`)
* **Wall Thickness**: `2.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Expandable**: `False` (`box_defaults={"expandable": False}`)

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Player Ships, Trains & Track Cylinders (4 Colors) | Purple, Yellow, Green, Red | `PlayerBox_purple`, `PlayerBox_yellow`, `PlayerBox_green`, `PlayerBox_red` (4 boxes) | Cap Lid | Color-coded Framed "Ships & Trains" |
| Player Bits (Machine Disks, Influence/Favour/Contract Tokens, Scoring Disks) | 4 Player sets | `PlayerBoxBits_purple`, `PlayerBoxBits_yellow`, `PlayerBoxBits_green`, `PlayerBoxBits_red` (4 boxes) | Cap Lid | Color-coded Framed "Player" |
| Factory Tiles | Early factory cardboard tiles (`51.0 x 55.5mm`) | `FactoryTiles_1`, `FactoryTiles_2` (2 boxes) | Sliding Lid | Framed "Factories I" & "Factories II" |
| Demand Tiles | City demand tiles (`42.0 x 42.0mm`) | `DemandTiles` | Sliding Lid | Framed "Demand" |
| Starting & Old Factory Tiles | Starting tiles (`32.0 x 42.0mm`) & old factory tiles (`51.0 x 57.0mm`) | `StartingTiles` | Sliding Lid | Framed "Start" |
| Upgrade Tiles | 12 upgrade tokens (`16.0 x 16.0mm`) | `UpgradeTiles` | Sliding Lid | Framed "Upgraded" |
| Money Tokens | Money tokens (`32.0 x 17.0mm`) | `MoneyBox` | Cap Lid | Framed "Money" (Gold) |
| Solo Goal & Action Tokens | Solo goal (`22.0 x 31.0mm`) & solo action (`25.5 x 38.0mm`) tokens | `SoloBox` | Cap Lid | Framed "Solo" |
| Late-Game Factory Tiles | Late-game factory tiles (`51.0 x 55.5mm`) | `LateGameFactoryBox` | Sliding Lid | Framed "Late Game" |
| Round Markers | Round marker cylinders (`12.0mm dia x 16.0mm`) | `RoundMarkerBox` | Sliding Lid | Framed "Round" |
| Worker Meeples & Expert Workers (6 Colors) | White, Blue, Grey, Yellow, Red, Black | `WorkerBox_white`, `WorkerBox_blue`, `WorkerBox_grey`, `WorkerBox_yellow`, `WorkerBox_red`, `WorkerBox_black` (6 boxes) | Cap Lid | Color-coded Framed "Workers" |
| Resource Cubes (Single Width) | 10.5mm wooden cubes (Silk & Paper) | `ResourceBox_silk`, `ResourceBox_paper` (2 boxes) | Sliding Lid | Framed "Resources" |
| Resource Cubes (Double Width) | 10.5mm wooden cubes (Coal & Copper) | `ResourceDoubleBox_coal`, `ResourceDoubleBox_copper` (2 boxes) | Sliding Lid | Framed "Resources" |
| Player Mats, Main Map Board & Handbook | 4 player boards + main map + handbook | Sits on top of insert (`Z = 37.8 .. 70.0mm`) | Board Layer | Flat storage under game box lid |
| Front Void Spacer | Remaining `303.0 x 129.5 x 37.8mm` void | Automatic spacer (`spacer_1`) | No-Lid Tray | Auto-generated |

---

## 3. Sub-Box Specifications

### 3.1 Row 1: Player Boxes & Player Bits (`Y = 0.0 .. 92.0mm`)
* **PlayerBox (x4)**: `75.75mm x 92.0mm x 15.0mm` at `Z = 0.0mm` across the 303.0mm width.
* **PlayerBoxBits (x4)**: `151.5mm x 92.0mm x 11.4mm`, stacked 2x2 atop the player boxes (`Z = 15.0mm` and `Z = 26.4mm`).

### 3.2 Row 2: Factory, Demand, Starting, Upgrade & Money (`Y = 92.0 .. 152.5mm`)
* **FactoryTiles_1 & FactoryTiles_2**: `56.0mm x 60.5mm x 37.8mm` each.
* **DemandTiles**: `47.0mm x 60.5mm x 37.8mm`.
* **StartingTiles**: `56.0mm x 60.5mm x 37.8mm`.
* **UpgradeTiles**: `88.0mm x 60.5mm x 6.5mm` at `Z = 0.0mm`.
* **MoneyBox**: `88.0mm x 60.5mm x 31.3mm` stacked atop `UpgradeTiles` at `Z = 6.5mm`.

### 3.3 Row 3: Solo, Late Game, Round Marker & Workers (`Y = 152.5 .. 213.0mm`)
* **SoloBox**: `93.0mm x 60.5mm x 17.5mm` at `X = 0.0mm, Z = 0.0mm`.
* **LateGameFactoryBox**: `56.0mm x 60.5mm x 20.3mm` stacked at `X = 0.0mm, Z = 17.5mm`.
* **RoundMarkerBox**: `36.5mm x 60.5mm x 20.3mm` stacked at `X = 56.0mm, Z = 17.5mm`.
* **WorkerBox (x6)**: `69.67mm x 60.5mm x 18.9mm`, 3 wide x 2 high at `X = 93.0 .. 302.0mm`.

### 3.4 Row 4: Resource Cube Boxes (`Y = 213.0 .. 250.5mm`)
* **ResourceBox (x2)**: `112.0mm x 37.5mm x 18.9mm`, 2 stacked at `X = 0.0mm`.
* **ResourceDoubleBox (x2)**: `191.0mm x 37.5mm x 18.9mm`, 2 stacked at `X = 112.0mm`.

### 3.5 Row 5: Front Spacer (`Y = 250.5 .. 380.0mm`)
* Automatically filled by `generate_spacers=True` (`303.0mm x 129.5mm x 37.8mm`).
