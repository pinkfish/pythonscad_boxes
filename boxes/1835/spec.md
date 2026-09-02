# 1835 Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **1835** board game insert, ported from `examples/1835.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `216.0mm (Width) x 298.0mm (Length) x 50.0mm (Height)`
* **Board Thickness**: `15.0mm` (Map board and player mats sit on top at `Z = 35.0 .. 50.0mm`)
* **Main Insert Usable Height**: `35.0mm` (`Z = 0.0 .. 35.0mm`)
* **Wall Thickness**: `2.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Label |
|---|---|---|---|---|
| Track Hex Tiles | 60 tiles (`40mm` width, `23.09mm` radius) | `HexBox1` .. `HexBox4` (4 stacked boxes, 15 tiles each) | Inset Tabbed | Framed "Tiles" label |
| Paper Currency | 8 Denominations (1, 5, 10, 20, 50, 100, 200, 500) | `MoneyBox1` (1-20) & `MoneyBox2` (50-500) | Slipover Sleeve | Framed "Money" label |
| Company Share Certificates | 8 Major German Railroad Companies | `ShareBox1` .. `ShareBox4` (4 stacked boxes, 2 companies each) | Slipover Sleeve | Framed "Shares" label |
| Station & Destination Tokens | 14 Token Groups / Markers (`6mm` dia x `2mm`) | `MiddleBox` (14 token wells) | Cap Lid | Framed "Tokens/Trains" label |
| Train Cards & Private Companies | Full decks (`44 x 64mm`) | `MiddleBox` (Trains & Private wells) | Cap Lid | Framed "Tokens/Trains" label |
| First Player & Large Markers | Large wooden markers (`20mm` dia x `41mm` length) | `FirstPlayer` | Slipover Sleeve | Framed "First" label |
| Automatic Spacers | Leftover volume | Derived automatically by `pyboxbuilder` | No-Lid Spacers | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Hex Tile Boxes (`HexBox1` .. `HexBox4`)
* **Dimensions**: `215.0mm (Width) x 142.56mm (Length) x 8.75mm (Height)`.
* **Arrangement**: 4 boxes stacked vertically from `Z = 0.0mm` to `Z = 35.0mm` at `Y = 102.0mm`.
* **Lid Mechanism**: `BoxType.INSET` tabbed lids.
* **Compartment**: 3x5 hexagonal grid cutouts holding 15 tiles per layer (60 hex tiles total).

### 3.2 Money Boxes (`MoneyBox1` & `MoneyBox2`)
* **Dimensions**:
  * `MoneyBox1`: `215.0mm x 102.0mm x 9.5mm` (placed at `Z = 0.0mm`).
  * `MoneyBox2`: `215.0mm x 102.0mm x 8.5mm` (placed at `Z = 9.5mm`).
* **Lid Mechanism**: `BoxType.SLIPOVER` sleeve (handles low profile while providing corner finger release).
* **Compartments**: 4 card slots per box (`50.0 x 94.0 x 5.0mm`) with side scoops (`FingerCut.SCOOP`).
  * `MoneyBox1`: Denominations "1", "5", "10", "20".
  * `MoneyBox2`: Denominations "50", "100", "200", "500".

### 3.3 Share Certificate Boxes (`ShareBox1` .. `ShareBox4`)
* **Dimensions**: `138.0mm x 52.45mm x 8.75mm`.
* **Arrangement**: 4 boxes stacked vertically at `X = 0.0mm`, `Y = 244.56mm`, `Z = 0.0 .. 35.0mm`.
* **Lid Mechanism**: `BoxType.SLIPOVER`.
* **Compartments**: 2 share card wells per box (`44.0 x 64.0 x 8.75mm`) with through-floor cutouts (`FingerCut.THROUGH_FLOOR`).
  * `ShareBox1`: Bayerische Eisenbahn, Sächsische Eisenbahn.
  * `ShareBox2`: Badische Eisenbahn, Württembergische.
  * `ShareBox3`: Hessische Eisenbahn, Preußische Eisenbahn.
  * `ShareBox4`: Mecklenburg-Schwerin, Oldenburgische.

### 3.4 Middle Box (Tokens, Trains, Private Company Cards)
* **Dimensions**: `215.0mm x 102.0mm x 17.0mm`.
* **Arrangement**: Floats above the two money boxes at `Z = 18.0mm .. 35.0mm`, `Y = 0.0 .. 102.0mm`.
* **Lid Mechanism**: `BoxType.CAP`.
* **Compartments**:
  * 14 progressive token wells for station and track markers with through-floor push cutouts.
  * Dedicated "Trains" card well (`44.0 x 64.0mm`).
  * Dedicated "Private" company card well (`44.0 x 64.0mm`).

### 3.5 First Player Marker Box (`FirstPlayer`)
* **Dimensions**: `77.0mm x 52.45mm x 24.0mm`.
* **Arrangement**: Placed beside the Share Boxes at `X = 138.0mm`, `Y = 244.56mm`, `Z = 0.0mm`.
* **Lid Mechanism**: `BoxType.SLIPOVER`.
* **Compartment**: Rounded cutout (`20.0 x 33.0 x 20.0mm`) for cylindrical markers.

---

## 4. 3D Spatial Packing Layout

```
+-------------------------------------------------------------------------------+
| MoneyBox1 / MoneyBox2 (Z: 0..18)     | HexBox1..4 (Stacked 4-high, Z: 0..35)  |
| MiddleBox (Z: 18..35)                | (X: 0..215, Y: 102..244.56)            |
| (X: 0..215, Y: 0..102)               |                                        |
+--------------------------------------+----------------------------------------+
| ShareBox1..4 (Stacked 4-high, Z:0..35) | FirstPlayer (Z: 0..24) + Auto Spacer |
| (X: 0..138, Y: 244.56..297)            | (X: 138..215, Y: 244.56..297)        |
+----------------------------------------+--------------------------------------+
```
