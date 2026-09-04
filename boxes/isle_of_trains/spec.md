# Isle of Trains: All Aboard Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Isle of Trains: All Aboard** board game organizer, ported from `examples/isle_of_trains.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `130.0mm (Width) x 180.0mm (Length) x 38.0mm (Height)`
* **Main Insert Usable Height**: `37.0mm` (`Z = 0.0 .. 37.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Card Dimensions**: `62.5mm x 89.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Destination & Track Tiles | 6 Destination tiles + 2 Track tiles | `DestinationBox` | Cap Lid | Framed "Destinations" (Dark Green) |
| Victory Hex Tokens | 1, 3, 5, 10 Victory tokens (26 hexes) | `VictoryBox` | Cap Lid | Framed "Victory" (Gold) |
| Island & Train Cards | 7 Island cards + 71 Train cards | `CardBox` | Cap Lid | Framed "Cards" (Navy) |
| Passenger Meeples & Cargo | Wooden passenger meeples | `MiddleBox` | Cap Lid | Framed "Passengers" (Dark Slate) |
| Ticket Tiles & Train Marker | 10 Ticket tiles + train token | `TicketBox` | Cap Lid | Framed "Tickets" (Firebrick) |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Stacked Tile Section (`Y = 0.0 .. 45.5mm`)
* **`DestinationBox`** (`129.0mm x 45.5mm x 16.5mm`): Lower box holding destination and track tiles.
* **`VictoryBox`** (`129.0mm x 45.5mm x 21.0mm`): Upper box stacked atop `DestinationBox` at `Z = 16.5mm`. Holds 4 victory hex compartments.

### 3.2 Main Compartment Columns (`Y = 45.5 .. 180.0mm`)
* **Left Column (`X = 0.0 .. 98.0mm`)**:
  * `MiddleBox` (`98.0mm x 64.5mm x 37.0mm`): Passenger meeple storage.
  * `CardBox` (`98.0mm x 69.0mm x 37.0mm`): Full card deck pocket with side finger scoop.
* **Right Column (`X = 98.0 .. 129.0mm`)**:
  * `TicketBox` (`31.0mm x 133.5mm x 37.0mm`): Longitudinal tray for ticket tiles and starting train marker.

---

## 4. 3D Spatial Layout Map

```
+-------------------------------------------------------------------------------+
| DestinationBox (129.0 x 45.5 x 16.5mm, Z: 0..16.5mm)                          |
| [ VictoryBox stacked atop DestinationBox, Z: 16.5..37.5mm, Height: 21.0mm ]   |
+-------------------------------------------------------+-----------------------+
| MiddleBox (98.0 x 64.5 x 37.0mm)                      | TicketBox             |
| [ Holds Passenger Meeples & Cargo ]                   | (31.0 x 133.5 x 37mm) |
+-------------------------------------------------------+                       |
| CardBox (98.0 x 69.0 x 37.0mm)                        | [ Holds Ticket Tiles  |
| [ Holds 78 Train & Island Playing Cards ]             |   & Train Marker ]    |
+-------------------------------------------------------+-----------------------+
|<---------------------- 98.0mm ----------------------->|<------- 31.0mm ------>|
```
