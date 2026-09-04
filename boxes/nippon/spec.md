# Nippon Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Nippon** board game organizer, ported from `examples/nippon.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `303.0mm (Width) x 380.0mm (Length) x 70.0mm (Height)`
* **Board & Player Mat Reserve**: `32.2mm` (Main game board `9.0mm`, 4 player boards `17.2mm`, player handbook `6.0mm` sit atop the insert)
* **Main Insert Usable Height**: `37.8mm` (`Z = 0.0 .. 37.8mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Player Trains, Ships & Discs (4 Colors) | White, Yellow, Red, Purple (Trains, ships, track cylinders, scoring markers) | `PlayerBox_white`, `PlayerBox_yellow`, `PlayerBox_red`, `PlayerBox_purple` (4 boxes) | Cap Lid | Color-coded Framed "Player" |
| Factory Tiles (Types I & II) | Early & late factory cardboard tiles (`51 x 55.5mm`) | `FactoryTiles_1`, `FactoryTiles_2` | Sliding Lid | Framed "Factories I" & "Factories II" |
| Demand & City Tiles | City demand tiles (`42 x 42mm`) | `DemandTiles` | Sliding Lid | Framed "Demand" |
| Starting Tiles & Old Factory Tiles | Starting bonus tiles (`32 x 42mm`) | `StartingTiles` | Sliding Lid | Framed "Starting" |
| Resource Cubes (Silk, Paper, Coal, Copper) | 10.5mm wooden resource cubes | `ResourceCubes_SilkPaper`, `ResourceCubes_CoalCopper` | Cap Lid | Framed "Silk & Paper", "Coal & Copper" |
| Paper Money, Contracts & Favor Tiles | Money tokens, contract tokens, favor tokens | `MoneyAndContracts` | Cap Lid | Framed "Money & Contracts" (Gold) |
| Player Mats & Main Map Board | 4 Layered player boards + main map | Sits on top of insert (`Z = 37.8 .. 70.0mm`) | Board Layer | Flat storage under game box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Player Boxes (Row 1, `Y = 0.0 .. 92.0mm`)
* **Dimensions**: `75.75mm x 92.0mm x 18.9mm` each.
* **Arrangement**: 4 boxes side-by-side across the 303.0mm width.
* **Compartments**: Dual-compartment split (60% trains/ships, 40% discs/markers) with curved finger scoops.

### 3.2 Factory & Demand Tile Boxes (Row 2, `Y = 92.0 .. 154.5mm`)
* **Dimensions**: `75.75mm x 62.5mm x 37.8mm` each.
* **Arrangement**: 4 sliding-lid dispenser columns across the width.

### 3.3 Resource & Currency Trays (Row 3, `Y = 154.5 .. 234.5mm`)
* **Dimensions**: `101.0mm x 80.0mm x 18.9mm` each.
* **Arrangement**: 3 trays across the width (`3 x 101.0mm = 303.0mm`).

---

## 4. 3D Spatial Layout Map

```
+--------------------+--------------------+--------------------+--------------------+
| PlayerBox_white    | PlayerBox_yellow   | PlayerBox_red      | PlayerBox_purple   |
| (75.75 x 92mm)     | (75.75 x 92mm)     | (75.75 x 92mm)     | (75.75 x 92mm)     |
+--------------------+--------------------+--------------------+--------------------+
| FactoryTiles_1     | FactoryTiles_2     | DemandTiles        | StartingTiles      |
| (75.75 x 62.5mm)   | (75.75 x 62.5mm)   | (75.75 x 62.5mm)   | (75.75 x 62.5mm)   |
+--------------------+--------------------+--------------------+--------------------+
| ResourceCubes_SilkPaper (101 x 80mm)    | ResourceCubes_CoalCopper (101 x 80mm)   |
+-----------------------------------------+-----------------------------------------+
| MoneyAndContracts (101 x 80mm)          | Automatic Void Spacers (to Y: 380mm)    |
+-----------------------------------------+-----------------------------------------+
```
