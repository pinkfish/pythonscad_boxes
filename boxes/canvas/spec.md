# Canvas Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Canvas** board game organizer, ported from `boxes/canvas/canvas.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `200.0mm (Width) x 250.0mm (Length) x 50.0mm (Height)`
* **Center Playmat Channel**: `50.0mm` wide running the full length of the box (`X = 73.0 .. 123.0mm`, `Y = 0.0 .. 247.0mm`) holding the open-ended, stepped-wall `PlaymatSpacer` cradle for the rolled-up cloth playmat
* **Wall Thickness**: `3.0mm` (`1.5mm` on `ArtCardsBox_*`, `2.0mm` on `PlaymatSpacer`)
* **Floor Thickness**: `2.0mm` (`1.5mm` on `ArtCardsBox_*` and `PlaymatSpacer`)
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Transparent Art Cards & Scoring Cards | Two `70 x 120mm` Tarot card stacks | `ArtCardsBox_Left` & `ArtCardsBox_Right` (`73 x 124 x 30mm` each, independent boxes) | Sliding Lid | Pill-framed darkslateblue lids (Circle pattern) |
| Rolled Cloth Playmat | Rolled cloth mat (~45mm diameter) | `PlaymatSpacer` (`50 x 247 x 29mm` at `X = 73..123mm`) | No-Lid Cradle | Open front/back ends, 50% mid-wall height (`14.5mm`), full-height (`29mm`) 30mm end walls |
| Ribbon Tokens (6 Types) | Red, Green, Grey, Blue, Purple, Palette ribbon award tokens | `RibbonBox_Red` .. `RibbonBox_Palette` (`73 x 41 x 29mm`, 3 left + 3 right) | Cap Lid | Pill-framed color-coded lids (Circle pattern) |

---

## 3. 3D Spatial Layout Map

```
|<--------- 73mm --------->|<--- 50mm --->|<--------- 73mm --------->|
+--------------------------+--------------+--------------------------+  Y = 0mm
|                          | [Full H end] |                          |
|    ArtCardsBox_Left      |              |    ArtCardsBox_Right     |
|     (73 x 124 x 30mm,    | PlaymatSpacer|     (73 x 124 x 30mm,    |  Y = 124mm
|      independent box)    | (open ends,  |      independent box)    |
+--------------------------+  50% wall H  +--------------------------+
| RibbonBox_Red   (73x41)  |  in middle,  | RibbonBox_Blue   (73x41) |  Y = 165mm
+--------------------------+  full H at   +--------------------------+
| RibbonBox_Green (73x41)  |  both ends)  | RibbonBox_Purple (73x41) |  Y = 206mm
+--------------------------+              +--------------------------+
| RibbonBox_Grey  (73x41)  | [Full H end] | RibbonBox_Palette(73x41) |  Y = 247mm
+--------------------------+--------------+--------------------------+
|<---------------------------- 196.0mm ----------------------------->|
```
