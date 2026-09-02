# The Crew: Mission Deep Sea (Sleeved Edition) Organizer Specification

This document details the layout, sleeve sizing, sub-box specifications, and 2-tier hierarchical arrangement for the sleeved edition of **The Crew: Mission Deep Sea** board game organizer, ported to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Sleeve Parameters

* **Game Box Footprint**: `172.0mm (Width) x 122.0mm (Length) x 36.0mm (Height)` (Expanded depth to accommodate 100-micron premium sleeves)
* **Wall Thickness**: `2.0mm`
* **Floor Thickness**: `1.6mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `1.0mm`
* **Playing Card Sleeves**: Gamegenic Standard American (`59.0mm x 91.0mm`, 100μm Prime, `0.32mm` thickness per card)
* **Task Card Sleeves**: Gamegenic Mini European (`46.0mm x 71.0mm`, 100μm Prime, `0.32mm` thickness per card)

---

## 2. Component Inventory & Storage Strategy

| Component | Count / Sleeve Type | Storage Box | Box Type | Lid Style / Pattern |
|---|---|---|---|---|
| Sleeved Playing Cards | 45 cards (Gamegenic Standard American) | `Deck` | Sliding Lid | Framed "Deck" (Voronoi Bubble pattern) |
| Sleeved Task Cards (Stack 1) | 48 cards (Gamegenic Mini European) | `Tasks1` | Sliding Lid | Framed "Tasks1" (Voronoi Bubble pattern) |
| Sleeved Task Cards (Stack 2) | 48 cards (Gamegenic Mini European) | `Tasks2` | Sliding Lid | Framed "Tasks2" (Voronoi Bubble pattern) |
| Diver Standee & Base | 1 Diver (`86mm` tall) + 1 Base (`58mm` wide) | `Accessories` | Sliding Lid | Framed "Captain" (Voronoi Bubble pattern) |
| Sonar Tokens & Distress Token | 5 Sonar tokens (`29.5mm` dia) + 1 Distress token | `Accessories` | Sliding Lid | Multi-color inlays (Green sonar, Blue radio tower) |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Sleeved Deck Box (`Deck`)
* **Dimensions**: `64.0mm (Width) x 96.0mm (Length) x 36.0mm (Height)`.
* **Arrangement**: Sits vertically along the left corner spanning the entire 36.0mm height.
* **Lid Mechanism**: `BoxType.SLIDING`.
* **Compartment**: Precision sleeved card well (`60.0 x 92.0mm`) with through-floor thumb cut.

### 3.2 Sleeved Task Card Boxes (`Tasks1` & `Tasks2`)
* **Dimensions**: `54.0mm x 76.0mm x 20.0mm` each.
* **Arrangement**: Placed side-by-side on the bottom tier at `Z = 0.0mm`.
* **Compartment**: Sized for 48 sleeved Gamegenic Mini European cards (`47.0 x 72.0mm`).

### 3.3 Accessories & Standee Tray (`Accessories`)
* **Dimensions**: `108.0mm x 118.0mm x 11.0mm`.
* **Arrangement**: Stacks directly atop `Tasks1` and `Tasks2` (`20.0mm + 11.0mm = 31.0mm`), fitting comfortably under the 36.0mm ceiling.
* **Lid Mechanism**: `BoxType.SLIDING` labeled "Captain".
* **Internal Precision Element Architecture**:
  * **Diver Standee**: SVG silhouette routed from the source vector artwork (`86.0mm` height, `2.5mm` thickness).
  * **Standee Base**: Custom SVG silhouette nestled beneath the diver (`58.0mm` width).
  * **Sonar Token Wells**: Dual circular wells (`29.5mm` dia) holding stacks of 3 and 2 tokens with embossed multi-color green sonar icons on their floors.
  * **Distress Token Well**: Rounded rectangular well (`44.0 x 29.0mm`, rotated 90°) with an embossed multi-color blue distress antenna icon.

---

## 4. 3D Spatial Layout Map

```
+---------------------+---------------------------------------------------------+
| Deck (Full Height)  | Accessories Tray (Z: 20.0 .. 31.0mm, Height: 11.0mm)    |
| (64.0 x 96.0 x 36mm)| [ Holds Diver Standee, Base, Sonar & Distress Tokens ]  |
|                     +---------------------------+-----------------------------+
|                     | Tasks1 (Z: 0 .. 20.0mm)   | Tasks2 (Z: 0 .. 20.0mm)     |
|                     | (54.0 x 76.0 x 20.0mm)    | (54.0 x 76.0 x 20.0mm)      |
+---------------------+---------------------------+-----------------------------+
|<----- 64.0mm ------>|<------------------------ 108.0mm ---------------------->|
```
