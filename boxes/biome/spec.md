# Biome Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Biome** board game organizer, ported from `examples/biome.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `285.0mm (Width) x 285.0mm (Length) x 73.0mm (Height)`
* **Board & Score Pad Reserve**: `20.0mm` (Main game board + player mats sit atop insert at `Z = 53.0 .. 73.0mm`)
* **Main Insert Usable Height**: `53.0mm` (`Z = 0.0 .. 53.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Card Dimensions**: `66.0mm x 91.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Nest Player Boards | 4 Long cardboard nest strips (`45 x 180mm`) | `NestBox` | Cap Lid | Framed "Nests" (Peru) |
| Player Bits (4 Colors) | Red, Blue, Green, Yellow wooden cubes & tokens | `PlayerBox_Red` .. `PlayerBox_Yellow` | Cap Lid | Color-coded Framed lids |
| Food & Animal Tokens (8 Types) | Mice, Sun, Fish, Leaves, Spiders, Berries, Chicks, Rabbits | `Resource_Mouse` .. `Resource_Rabbits` | Cap Lid | Color-coded Framed lids |
| Animal & Plant Cards | Main card decks (`66 x 91mm`) | `CardBox_MainDeck1`, `CardBox_MainDeck2` | Cap Lid | Framed deck names (Forest Green) |
| Board & Climate Spinner | Folding game board and seasonal spinner | Sits atop insert (`Z = 53.0 .. 73.0mm`) | Board Layer | Flat storage beneath game lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Nest Strip Tray (Column 0, `X = 0.0 .. 51.0mm`)
* **Dimensions**: `51.0mm x 283.0mm x 53.0mm`.
* **Arrangement**: Longitudinal tray spanning nearly the full length of the box.

### 3.2 Resource & Player Matrix (Column 1, `X = 51.0 .. 108.0mm`)
* **Dimensions**: `57.0mm x 70.75mm x 17.66mm` each.
* **Arrangement**: 4 longitudinal columns, stacked 3 high (`Z = 0.0 .. 53.0mm`), total of 12 modular component bins.

### 3.3 Playing Card Dispensers (Column 2, `X = 108.0 .. 181.0mm`)
* **Dimensions**: `73.0mm x 98.0mm x 53.0mm` each.
* **Arrangement**: 2 deep card wells stored sequentially along Y.

---

## 4. 3D Spatial Layout Map

```
+---------------+-------------------------------+-----------------------+-----------------------+
| NestBox       | Player / Resource Trays       | CardBox_MainDeck1     |                       |
| (51.0 x 283.0 | (12 bins stacked 3-high,      | (73.0 x 98.0 x 53mm)  |                       |
|   x 53.0mm)   |  4 columns across Y)          +-----------------------+     Automatic 3D      |
|               | (57.0 x 70.75 x 17.66mm each) | CardBox_MainDeck2     |     Void Spacers      |
|               |                               | (73.0 x 98.0 x 53mm)  | (X = 181..285mm,      |
|               |                               +-----------------------+  Y = 0..285mm)        |
|               |                               | Automatic 3D Spacers  |                       |
+---------------+-------------------------------+-----------------------+-----------------------+
|<--- 51.0mm -->|<----------- 57.0mm ---------->|<------- 73.0mm ------>|<------ 104.0mm ------>|
```
