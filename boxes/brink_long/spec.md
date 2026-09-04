# Brink: Long Box Variant Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Brink: Long Box Variant** board game organizer, ported from `examples/brink_long.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `215.0mm (Width) x 307.0mm (Length) x 96.0mm (Height)`
* **Board & Player Mat Reserve**: `18.0mm` (Map board and voting track sit atop insert at `Z = 78.0 .. 96.0mm`)
* **Main Insert Usable Height**: `78.0mm` (`Z = 0.0 .. 78.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Player Fleets (Long Format) | Full-length fleet trays for ships and upgrade boards | `FleetSolari`, `FleetHorizon` (2 boxes) | Cap Lid | Color-coded Framed lids |
| Action & Rider Cards | Small-card action and rider decks | `CardBox_Actions`, `CardBox_Riders` | Sliding Lid | Framed "Actions" (Gold) & "Riders" (Firebrick) |
| Ambassador Cards | Ambassador character cards | `CardBox_Ambassadors` | Sliding Lid | Framed "Ambassadors" (Navy) |
| Hex Sectors | Sector hex tiles | `HexBox` | Cap Lid | Framed "Hex Sectors" (Dim Gray) |
| Board & Player Aids | Folded map board & voting board | Sits atop insert (`Z = 78.0 .. 96.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Longitudinal Player Fleets (Column 0, `X = 0.0 .. 106.0mm`)
* **Dimensions**: `106.0mm x 305.0mm x 24.0mm` each.
* **Arrangement**: Full length trays stacked 2 high (`Z = 0.0` and `Z = 24.0mm`).

### 3.2 Cards & Hex Sectors (Column 1, `X = 106.0 .. 212.5mm`)
* **`CardBox_Actions` .. `CardBox_Ambassadors`**: `106.5mm x 77.5mm x 24.0mm` each, sequential along Y (`Y = 0.0 .. 232.5mm`).
* **`HexBox`**: `106.5mm x 72.5mm x 24.0mm` at `Y = 232.5 .. 305.0mm`.

---

## 4. 3D Spatial Layout Map

```
+------------------------------------+------------------------------------+
| FleetSolari / FleetHorizon         | CardBox_Actions (106.5 x 77.5mm)   |
| (Stacked 2-high, 24.0mm each)      +------------------------------------+
| (106.0 x 305.0mm)                  | CardBox_Riders (106.5 x 77.5mm)    |
|                                    +------------------------------------+
|                                    | CardBox_Ambassadors (106.5 x 77.5) |
|                                    +------------------------------------+
|                                    | HexBox                             |
|                                    | (106.5 x 72.5 x 24.0mm)            |
+------------------------------------+------------------------------------+
|<-------------- 106.0mm ----------->|<-------------- 106.5mm ----------->|
```
