# Canvas Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Canvas** board game organizer, ported from `examples/canvas.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `200.0mm (Width) x 250.0mm (Length) x 50.0mm (Height)`
* **Center Playmat Channel**: `50.0mm` wide running the full length of the box (`X = 73.0 .. 123.0mm`, `Y = 0.0 .. 250.0mm`) for the rolled-up cloth playmat (matching `divider_middle_width = 50` in `canvas.scad`)
* **Wall Thickness**: `3.0mm` (`2.0mm` on `PlaymatDivider`)
* **Floor Thickness**: `2.0mm` (`1.5mm` on `PlaymatDivider`)
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Transparent Art Cards & Scoring Cards | Two `70 x 120mm` Tarot card stacks | `PlaymatDivider` (`196 x 124 x 30mm`, left & right bays) | No-Lid Divider | Front & back open U-channel for playmat |
| Rolled Cloth Playmat | Rolled cloth mat (~45mm diameter) | Open `50mm` center channel (`X = 73..123mm`, full box length) | Open Channel | Cradled between divider walls & ribbon columns |
| Ribbon Tokens (6 Types) | Red, Green, Grey, Blue, Purple, Palette ribbon award tokens | `RibbonBox_Red` .. `RibbonBox_Palette` (`73 x 41 x 29mm`, 3 left + 3 right) | Cap Lid | Pill-framed color-coded lids (Circle pattern) |

---

## 3. 3D Spatial Layout Map

```
|<--------- 73mm --------->|<--- 50mm --->|<--------- 73mm --------->|
+--------------------------+--------------+--------------------------+  Y = 0mm
|                          |              |                          |
|      ArtCards_Left       |   OPEN       |      ArtCards_Right      |
|    (PlaymatDivider       |  PLAYMAT     |    (PlaymatDivider       |  Y = 124mm
|     196 x 124 x 30mm)    |  CHANNEL     |     196 x 124 x 30mm)    |
+--------------------------+              +--------------------------+
| RibbonBox_Red   (73x41)  |  (rolled-up  | RibbonBox_Blue   (73x41) |  Y = 165mm
+--------------------------+   cloth mat  +--------------------------+
| RibbonBox_Green (73x41)  |   runs full  | RibbonBox_Purple (73x41) |  Y = 206mm
+--------------------------+   length!)   +--------------------------+
| RibbonBox_Grey  (73x41)  |              | RibbonBox_Palette(73x41) |  Y = 247mm
+--------------------------+--------------+--------------------------+
|<---------------------------- 196.0mm ----------------------------->|
```
