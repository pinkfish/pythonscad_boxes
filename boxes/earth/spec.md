# Earth Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Earth** board game organizer, ported from `examples/earth.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `288.0mm (Width) x 288.0mm (Length) x 72.0mm (Height)`
* **Board & Player Mat Reserve**: `16.8mm` (6 player mats + 2 central board tracks sit atop insert at `Z = 55.2 .. 72.0mm`)
* **Main Insert Usable Height**: `55.2mm` (`Z = 0.0 .. 55.2mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Earth Cards**: `62.0mm x 93.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Flora Cards | 179 Plant & tree cards | `CardBox_Flora` | Sliding Lid | Framed "Flora Cards" (Forest Green) |
| Terrain Cards | 66 Terrain cards | `CardBox_Terrain` | Sliding Lid | Framed "Terrain Cards" (Sienna) |
| Event Cards | 38 Event cards | `CardBox_Events` | Sliding Lid | Framed "Event Cards" (Royal Blue) |
| Abundance Cards | Expansion cards | `CardBox_Abundance` | Sliding Lid | Framed "Abundance" (Dark Goldenrod) |
| Wooden Canopies & Trunks | Stackable tree pieces | `CanopyBox` | Cap Lid | Framed "Canopies" (Peru) |
| Wooden Sprout Cubes | Green sprout cubes (~195 cubes) | `SproutBox` | Cap Lid | Framed "Sprouts" (Lime Green) |
| Player Leaf Tokens (6 Colors) | Red, Green, Yellow, Blue, Purple, Pink | `PlayerBox_Red` .. `PlayerBox_Pink` (6 boxes) | Cap Lid | Color-coded Framed lids |
| Player Boards & Maps | 6 Double-sided player boards | Sits atop insert (`Z = 55.2 .. 72.0mm`) | Board Layer | Flat storage beneath game lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Card Library (Row 0, `Y = 0.0 .. 99.0mm`)
* **Dimensions**: `68.0mm x 99.0mm x 55.2mm` each.
* **Arrangement**: 4 card wells across width (`X = 0.0 .. 272.0mm`).

### 3.2 Tree & Sprout Storage (Row 1, `Y = 99.0 .. 189.0mm`)
* **`CanopyBox`** (`75.0mm x 90.0mm x 55.2mm`): Tree trunks and canopy toppers.
* **`SproutBox`** (`75.0mm x 90.0mm x 55.2mm`): Resource cubes.

### 3.3 Player Leaf Token Trays (`X = 150.0 .. 288.0mm`, `Y = 99.0 .. 189.0mm`)
* **Dimensions**: `69.0mm x 90.0mm x 18.4mm` each.
* **Arrangement**: 2 columns across X, stacked 3 high (`Z = 0.0 .. 55.2mm`).

---

## 4. 3D Spatial Layout Map

```
+----------------+----------------+----------------+----------------+-----------+
| CardBox_Flora  | CardBox_Terrain| CardBox_Events | CardBox_Abund. | Auto      |
| (68 x 99x55mm) | (68 x 99x55mm) | (68 x 99x55mm) | (68 x 99x55mm) | Spacer    |
+----------------+----------------+----------------+----------------+-----------+
| CanopyBox      | SproutBox      | PlayerBox_Red / Green / Yellow (Stacked)    |
| (75 x 90x55mm) | (75 x 90x55mm) | PlayerBox_Blue / Purple / Pink (Stacked)    |
|                |                | (69.0 x 90.0 x 18.4mm each)                 |
+----------------+----------------+---------------------------------------------+
|                           Automatic 3D Void Spacers                           |
|                    (Y = 189..288mm, Z = 0..55.2mm)                            |
+-------------------------------------------------------------------------------+
```
