# Russian Railroads Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Russian Railroads** board game organizer, ported from `examples/russian_railroads.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `219.0mm (Width) x 308.0mm (Length) x 70.0mm (Height)`
* **Board & Player Mat Reserve**: `15.0mm` (Main game board + 4 player factory boards sit atop insert at `Z = 55.0 .. 70.0mm`)
* **Main Insert Usable Height**: `55.0mm` (`Z = 0.0 .. 55.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Player Pieces (4 Colors) | Red, Blue, Green, Yellow workers, pawns, industry markers | `PlayerBox_Red` .. `PlayerBox_Yellow` (4 boxes) | Cap Lid | Color-coded Framed lids |
| Extra Markers & Rubles | Question tokens, doubler tokens, ruble coins | `ExtraTokensBox`, `MoneyBox` | Cap Lid | Framed "Tokens" & "Rubels" |
| Game Cards | Mini European cards (`44 x 68mm`) | `CardBox` | Sliding Lid | Framed "Cards" (Peru) |
| Train Tiles | Locomotive number tiles (1 to 9, etc.) | `TrainBox` | Cap Lid | Framed "Trains" (Dark Red) |
| Engineer Tiles | Recruited engineer tiles | `EngineerBox` | Cap Lid | Framed "Engineers" (Dark Slate) |
| Wooden Tracks | Black, grey, brown, natural, and white wooden track pieces | `TrackBox` | Cap Lid | Framed "Tracks" (Saddle Brown) |
| Board & Player Mats | Folded game board + 4 dual-sided player boards | Sits atop insert (`Z = 55.0 .. 70.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Player & Currency Matrix (`Y = 0.0 .. 80.5mm`)
* **Dimensions**: `108.5mm x 80.5mm x 18.33mm` each.
* **Arrangement**: 2 columns, stacked 3 high (`Z = 0.0 .. 55.0mm`):
  * Left Column: `PlayerBox_Red`, `PlayerBox_Blue`, `ExtraTokensBox`.
  * Right Column: `PlayerBox_Green`, `PlayerBox_Yellow`, `MoneyBox`.

### 3.2 Main Game Component Column (`Y = 80.5 .. 185.5mm`)
* **`CardBox`** (`18.0mm x 105.0mm x 55.0mm`): Stored vertically on edge at `X = 199.0mm`.
* **Stacked Component Trays (`X = 0.0 .. 199.0mm`)**:
  * Tier 1 (`Z = 0.0 .. 17.0mm`): `TrainBox` (`199.0mm x 105.0mm x 17.0mm`).
  * Tier 2 (`Z = 17.0 .. 30.0mm`): `EngineerBox` (`199.0mm x 105.0mm x 13.0mm`).
  * Tier 3 (`Z = 30.0 .. 55.0mm`): `TrackBox` (`199.0mm x 105.0mm x 25.0mm`).

---

## 4. 3D Spatial Layout Map

```
+------------------------------------+------------------------------------+
| PlayerBox_Red / Blue / Tokens      | PlayerBox_Green / Yellow / Money   |
| (Stacked 3-high, 18.33mm each)     | (Stacked 3-high, 18.33mm each)     |
| (108.5 x 80.5mm)                   | (108.5 x 80.5mm)                   |
+------------------------------------+------------------+-----------------+
| TrainBox (Z: 0..17mm)                                 | CardBox         |
| [ EngineerBox stacked atop, Z: 17..30mm, H: 13mm ]    | (18.0 x 105.0   |
| [ TrackBox stacked atop, Z: 30..55mm, H: 25mm ]       |   x 55.0mm)     |
| (199.0 x 105.0mm)                                     |                 |
+-------------------------------------------------------+-----------------+
|                            Automatic 3D Void Spacers                    |
|                 (X = 0..219mm, Y = 185.5..308mm, Z = 0..55.0mm)         |
+-------------------------------------------------------------------------+
```
