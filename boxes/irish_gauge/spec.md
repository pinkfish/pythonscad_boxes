# Irish Gauge Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Irish Gauge** board game organizer, ported from `examples/irish_gauge.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `214.0mm (Width) x 302.0mm (Length) x 39.0mm (Height)`
* **Board Reserve**: `10.5mm` (Folded map board sits atop insert at `Z = 28.5 .. 39.0mm`)
* **Main Insert Usable Height**: `28.5mm` (`Z = 0.0 .. 28.5mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Small Cards**: `49.0mm x 71.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Railway Companies (5 Lines) | Belfast, Cork, Midland, Waterford, Great Southern (trains & shares) | `CompanyBox_Belfast` .. `CompanyBox_GreatSouthern` | Sliding Lid | Color-coded Framed lids |
| Bank Money Cards & Dividends | Banknotes (£1, £5, £10) & 30 dividend cubes | `MoneyAndDividendsBox` | Sliding Lid | Framed "Bank & Dividends" (Forest Green) |
| Map Board | Iron Rails folding map board | Sits atop insert (`Z = 28.5 .. 39.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Railway Company Section (Row 0, `Y = 0.0 .. 133.8mm`)
* **Dimensions**: `53.5mm x 133.8mm x 14.25mm` each.
* **Arrangement**: 4 slots across X, stacked 2 high (`Z = 0.0` and `Z = 14.25mm`).

### 3.2 Bank Money & Dividends Section (Row 1, `Y = 133.8 .. 210.8mm`)
* **Dimensions**: `214.0mm x 77.0mm x 28.5mm`.
* **Arrangement**: Full width tray with 4 dedicated wells.

---

## 4. 3D Spatial Layout Map

```
+----------------+----------------+----------------+----------------+
| Company_Belfast| Company_Cork   | Company_Midland| Company_Waterf.|
| (53.5 x 133.8, | (53.5 x 133.8, | (53.5 x 133.8, | (53.5 x 133.8, |
|  Z: 0..14.2mm) |  Z: 0..14.2mm) |  Z: 0..14.2mm) |  Z: 0..14.2mm) |
+----------------+----------------+----------------+----------------+
| Co_GreatSouth  |                |                |                |
| (Z: 14..28.5)  |                |                |                |
+----------------+----------------+----------------+----------------+
| MoneyAndDividendsBox (Full width: 214.0mm x 77.0mm x 28.5mm)       |
+-------------------------------------------------------------------+
|                     Automatic 3D Void Spacers                     |
|                  (Y = 210.8..302mm, Z = 0..28.5mm)                |
+-------------------------------------------------------------------+
```
