# Maglev Metro Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Maglev Metro** board game organizer, ported from `examples/maglev_metro.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `286.0mm (Width) x 286.0mm (Length) x 65.0mm (Height)`
* **Board Reserve**: `17.2mm` (Acrylic recessed player boards + dual game board bases sit atop insert at `Z = 47.8 .. 65.0mm`)
* **Main Insert Usable Height**: `47.8mm` (`Z = 0.0 .. 47.8mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Hex Station Width**: `56.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Connection & Objective Cards | 4 Card decks (`67 x 90mm`) | `CardBox_Connections` .. `CardBox_PlayerObjectives` | Sliding Lid | Framed deck names (Royal Blue) |
| Player Track Hexes & Trains (4 Colors) | Green, Pink, Cyan, Orange | `PlayerBox_green` .. `PlayerBox_darkorange` | Sliding Lid | Color-coded Framed lids |
| Factory Station Hexes (6 Types) | Factories, Warehouses, Labs, Offices, Stores, Embassies | `FactoryBox_Factories` .. `FactoryBox_Embassies` | Sliding Lid | Framed station types (Goldenrod) |
| Robot Workers & Commuters | Metal / wooden passenger meeples | Handled in player & commuter compartments | Compartments | Precision recessed pockets |
| Player Boards & Maps | 4 Recessed acrylic player boards + 2-piece map board | Sits atop insert (`Z = 47.8 .. 65.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Card Library Boxes (Column 1, `X = 0.0 .. 73.0mm`)
* **Dimensions**: `73.0mm x 96.0mm x 23.9mm` each.
* **Arrangement**: 2 columns of 2 rows stacked 2 high across `Y = 0.0 .. 192.0mm`.

### 3.2 Player Boxes (Column 2, `X = 73.0 .. 134.5mm`)
* **Dimensions**: `61.5mm x 143.0mm x 23.9mm` each.
* **Arrangement**: Stored in 2 tiers (`Z = 0.0` and `Z = 23.9mm`) across `Y = 0.0 .. 286.0mm`.

### 3.3 Factory Station Hex Tile Boxes (Columns 3 & 4, `X = 134.5 .. 286.0mm`)
* **Dimensions**: `75.75mm x 71.5mm x 23.9mm` each.
* **Arrangement**: 2x3 grid of sliding boxes.

---

## 4. 3D Spatial Layout Map

```
+-------------------+-----------------------+-----------------------+-----------------------+
| CardBox_Conn.     | PlayerBox_green       | FactoryBox_Factories  | FactoryBox_Warehouses |
| (73.0 x 96.0mm)   | (61.5 x 143.0mm)      | (75.75 x 71.5mm)      | (75.75 x 71.5mm)      |
+-------------------+                       +-----------------------+-----------------------+
| CardBox_Pass.     | [ Stacked 2-high:     | FactoryBox_Labs       | FactoryBox_Offices    |
| (73.0 x 96.0mm)   |   green/pink/cyan/    | (75.75 x 71.5mm)      | (75.75 x 71.5mm)      |
+-------------------+   darkorange ]        +-----------------------+-----------------------+
| Automatic 3D      |                       | FactoryBox_Stores     | FactoryBox_Embassies  |
| Void Spacers      |                       | (75.75 x 71.5mm)      | (75.75 x 71.5mm)      |
+-------------------+-----------------------+-----------------------+-----------------------+
|<----- 73.0mm ---->|<------- 61.5mm ------>|<-------------------- 151.5mm ---------------->|
```
