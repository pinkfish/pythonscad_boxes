# Maglev Metro Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Maglev Metro** board game organizer, ported faithfully from `boxes/maglev_metro/maglev_metro.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `286.0mm (Width) x 286.0mm (Length) x 65.0mm (Height)`
* **Board Reserve**:
  * Over `X = 45..73mm`: `17.2mm` (2 game board bases `8.4mm` + 4 player boards `8.8mm`, usable height `47.8mm`)
  * Over `X = 79..286mm`: `25.6mm` (+ 2 game boards `8.4mm`, usable height `39.4mm`)
  * Over `X = 0..45mm`: full `65.0mm` height beside the boards
* **Wall / Floor / Lid Thickness**: `3.0mm` / `2.0mm` / `2.0mm` (`4.0mm` lid on card boxes, `2.0mm` wall on `StartTokenBox`)

---

## 2. Complete Component Inventory (25 Boxes)

| Component | Dimensions (`W x L x H` mm) | Position (`X, Y, Z` mm) | Box Type | Storage |
|---|---|---|---|---|
| `CardBox_Connections` | `73.0 x 96.0 x 23.9` | `(0.0, 0.0, 0.0)` | Sliding | Connection cards (`67 x 90mm`) |
| `CardBox_Tracks` | `73.0 x 96.0 x 23.9` | `(0.0, 0.0, 23.9)` | Sliding | Track cards |
| `CardBox_Passengers` | `73.0 x 96.0 x 23.9` | `(0.0, 96.0, 0.0)` | Sliding | Passenger cards |
| `CardBox_PlayerObjectives` | `73.0 x 96.0 x 23.9` | `(0.0, 96.0, 23.9)` | Sliding | Player board cards |
| `RobotBox_Silver` | `63.0 x 94.0 x 11.95` | `(10.0, 192.0, 0.0)` | Cap | Silver robots |
| `RobotBox_Gold` | `63.0 x 94.0 x 11.95` | `(10.0, 192.0, 11.95)` | Cap | Gold robots |
| `RobotBox_Orange` | `63.0 x 94.0 x 11.95` | `(10.0, 192.0, 23.9)` | Cap | Orange robots |
| `CommuterBox_Pink` | `63.0 x 47.0 x 11.95` | `(10.0, 192.0, 35.85)` | Cap | Pink commuters |
| `CommuterBox_Aqua` | `63.0 x 47.0 x 11.95` | `(10.0, 239.0, 35.85)` | Cap | Aqua commuters |
| `CommuterBoxSmall_Purple` | `45.0 x 67.5 x 17.2` | `(0.0, 0.0, 47.8)` | Cap | Purple commuters (side strip) |
| `CommuterBoxSmall_Coral` | `45.0 x 67.5 x 17.2` | `(0.0, 67.5, 47.8)` | Cap | Coral commuters (side strip) |
| `SpacerTop` | `45.0 x 57.0 x 17.2` | `(0.0, 135.0, 47.8)` | No-Lid | Hollow side-strip spacer |
| `StartTokenBox` | `10.0 x 94.0 x 65.0` | `(0.0, 192.0, 0.0)` | No-Lid | Start token (`45.5mm` dia, `4mm` thick) |
| `PlayerBox_green` | `61.5 x 143.0 x 19.7` | `(73.0, 0.0, 0.0)` | Sliding | Green player hexes & train |
| `PlayerBox_deeppink` | `61.5 x 143.0 x 19.7` | `(73.0, 143.0, 0.0)` | Sliding | Pink player hexes & train |
| `PlayerBox_cyan` | `61.5 x 143.0 x 19.7` | `(73.0, 0.0, 19.7)` | Sliding | Cyan player hexes & train |
| `PlayerBox_darkorange` | `61.5 x 143.0 x 19.7` | `(73.0, 143.0, 19.7)` | Sliding | Orange player hexes & train |
| `FactoryBox_Factories` | `75.75 x 71.5 x 19.7` | `(134.5, 0.0, 0.0)` | Sliding | Factory station hexes |
| `FactoryBox_Warehouses` | `75.75 x 71.5 x 19.7` | `(210.25, 0.0, 0.0)` | Sliding | Warehouse station hexes |
| `FactoryBox_Labs` | `75.75 x 71.5 x 19.7` | `(134.5, 71.5, 0.0)` | Sliding | Lab station hexes |
| `FactoryBox_Offices` | `75.75 x 71.5 x 19.7` | `(210.25, 71.5, 0.0)` | Sliding | Office station hexes |
| `FactoryBox_Stores` | `75.75 x 71.5 x 19.7` | `(134.5, 0.0, 19.7)` | Sliding | Store station hexes |
| `FactoryBox_Embassies` | `75.75 x 71.5 x 19.7` | `(210.25, 0.0, 19.7)` | Sliding | Embassy station hexes |
| `MetroTileBox` | `151.5 x 143.0 x 19.7` | `(134.5, 143.0, 0.0)` | Sliding | Metro & Studios tri-hex tiles |
| `SpacerBox` | `151.5 x 212.5 x 19.7` | `(134.5, 71.5, 19.7)` | No-Lid | Hollow spacer above MetroTileBox & Labs/Offices |
