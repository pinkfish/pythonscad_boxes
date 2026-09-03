# Gulf, Mobile & Ohio Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Gulf, Mobile & Ohio** board game organizer, ported from `examples/gulf_mobile_and_ohio.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `217.0mm (Width) x 307.0mm (Length) x 39.0mm (Height)`
* **Board Reserve**: `9.5mm` (Folded map board sits atop the insert at `Z = 29.5 .. 39.0mm`)
* **Main Insert Usable Height**: `29.5mm` (`Z = 0.0 .. 29.5mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Card Dimensions**: `66.0mm x 91.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Paper Bank Notes | 3 Denominations (1, 5, 20) | `BankMoneyBox` | Sliding Lid | Framed "Bank" (Gold) |
| Company Railroad Cards | 23 Railroads (2 cards each) + 4 player aids | `CompanyCardsBox_1`, `CompanyCardsBox_2` | Sliding Lid | Framed "Companies 1/2" (Navy) |
| Resource Track Cubes (6 Colors) | Red, Yellow, Green, Blue, Black, Purple | `CubeBox_Red` .. `CubeBox_Purple` (6 boxes) | Cap Lid | Color-coded Framed lids |
| Player Share & Round Markers | Discs and cylinder markers | `PlayerTokenBox` | Cap Lid | Framed "Tokens" |
| Game Map Board | Mounted game board | Sits atop insert (`Z = 29.5 .. 39.0mm`) | Board Layer | Flat storage beneath game lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Bank Money Box (`BankMoneyBox`)
* **Dimensions**: `171.0mm x 107.0mm x 29.5mm`.
* **Arrangement**: Front section (`Y = 0.0mm`).
* **Compartments**: 3 equal-width currency slots with curved front thumb scoops.

### 3.2 Company Card Storage (`CompanyCardsBox_1` & `CompanyCardsBox_2`)
* **Dimensions**: `72.0mm x 97.0mm x 29.5mm` each.
* **Arrangement**: Positioned side-by-side at `Y = 107.0mm`.

### 3.3 Resource Cube Trays (6 Boxes, Stacked 2-High)
* **Dimensions**: `54.25mm x 103.0mm x 14.75mm` each.
* **Arrangement**: Occupies 3 columns at `Y = 204.0mm`, stacked 2 high (`Z = 0.0` and `Z = 14.75mm`).

### 3.4 Player Token Box (`PlayerTokenBox`)
* **Dimensions**: `54.25mm x 103.0mm x 29.5mm`.
* **Arrangement**: Occupies column 4 at `X = 162.75mm`, `Y = 204.0mm`.

---

## 4. 3D Spatial Layout Map

```
+-------------------------------------------------------------+-----------------+
| BankMoneyBox (171.0 x 107.0 x 29.5mm)                       |                 |
+------------------------------+------------------------------+                 |
| CompanyCardsBox_1            | CompanyCardsBox_2            |  Automatic 3D   |
| (72.0 x 97.0 x 29.5mm)       | (72.0 x 97.0 x 29.5mm)       |  Void Spacers   |
+----------------+-------------+----+-------------------------+                 |
| CubeBox_Red    | CubeBox_Yellow   | CubeBox_Green   | PlayerTokenBox          |
| / CubeBox_Blue | / CubeBox_Black  | / CubeBox_Purple| (54.25 x 103 x 29.5mm)  |
| (Stacked 2-high, 14.75mm each)    |                 |                         |
+----------------+------------------+-----------------+-------------------------+
|<-------------------------------- 217.0mm ------------------------------------>|
```
