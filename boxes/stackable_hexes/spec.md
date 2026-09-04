# Stackable Hexes Modular Organizer Specification

This document details the architecture, parametric specifications, and magnetic interlocking design for the **Stackable Hexes** standalone token tray system, ported from `examples/stackable_hexes.py` to PythonSCAD (`pyboxbuilder`).

---

## 1. System Dimensions & Material Parameters

* **Hexagonal Footprint**: `100.0mm x 100.0mm` (Apothem-to-apothem width: `100.0mm`)
* **Tray Height**: `24.0mm`
* **Wall Thickness**: `4.0mm` (Provides structural rigidity and magnetic wall depth)
* **Floor Thickness**: `4.0mm`
* **Mode**: Standalone Modular System (`game_box_size = None`)

---

## 2. Magnetic & Interlocking Features

### 2.1 Stacking Rim (`StackableMode.INSIDE`)
* Each tray features a precision top recess (`2.0mm` thickness) designed to securely nest the base of another hexagonal tray without sliding or lateral shifting during gameplay.

### 2.2 Side Wall Embedded Magnets (`MagnetType`)
Trays feature side-wall cavities for embedded neodymium magnets on opposing facets:
* **Round Magnets**: Cylindrical pocket sized for disc magnets (`11.0mm` diameter x `2.9mm` depth).
* **Rectangular Magnets**: Prismatic slot sized for block magnets (`12.0mm x 6.0mm x 1.65mm`).

---

## 3. Production Model Catalog

Eight individual models are exported across combinations of internal partitions and magnet types:

| Model Label | Partitions | Magnet Type | Magnet Dimensions |
|---|---|---|---|
| `HexBoxSingle6x3RoundMagnet` | 1 (Open Tray) | `MagnetType.ROUND` | `11.0mm dia x 2.9mm` |
| `HexBoxSingle6x3RoundMagnetWithTwoPartitions` | 2 (Dual Wells) | `MagnetType.ROUND` | `11.0mm dia x 2.9mm` |
| `HexBoxSingle6x3RoundMagnetWithThreePartitions` | 3 (Triple Wells) | `MagnetType.ROUND` | `11.0mm dia x 2.9mm` |
| `HexBoxSingle6x3RoundMagnetWithFourPartitions` | 4 (Quad Wells) | `MagnetType.ROUND` | `11.0mm dia x 2.9mm` |
| `HexBoxSingle10x5x2RectMagnet` | 1 (Open Tray) | `MagnetType.RECT` | `12.0 x 6.0 x 1.65mm` |
| `HexBoxSingle10x5x2RectMagnetWithTwoPartitions` | 2 (Dual Wells) | `MagnetType.RECT` | `12.0 x 6.0 x 1.65mm` |
| `HexBoxSingle10x5x2RectMagnetWithThreePartitions` | 3 (Triple Wells) | `MagnetType.RECT` | `12.0 x 6.0 x 1.65mm` |
| `HexBoxSingle10x5x2RectMagnetWithFourPartitions` | 4 (Quad Wells) | `MagnetType.RECT` | `12.0 x 6.0 x 1.65mm` |
