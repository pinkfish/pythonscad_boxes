# The Crew: Mission Deep Sea Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 2-tier hierarchical arrangement for **The Crew: Mission Deep Sea** board game organizer, ported to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `172.0mm (Width) x 122.0mm (Length) x 26.0mm (Height)`
* **Wall Thickness**: `2.0mm`
* **Floor Thickness**: `1.6mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Playing Card Dimensions**: `56.0mm x 88.0mm` (45 cards)
* **Task Card Dimensions**: `44.0mm x 68.0mm` (96 cards)

---

## 2. Component Inventory & Storage Strategy

| Component | Count / Dimension | Storage Box | Box Type | Lid Style / Pattern |
|---|---|---|---|---|
| Playing & Reminder Cards | 45 cards (`56 x 88mm`) | `Deck` | Sliding Lid | Framed "Deck" (Voronoi Bubble pattern) |
| Task Cards (Stack 1) | 48 cards (`44 x 68mm`) | `Tasks1` | Sliding Lid | Framed "Tasks" (Voronoi Bubble pattern) |
| Task Cards (Stack 2) | 48 cards (`44 x 68mm`) | `Tasks2` | Sliding Lid | Framed "Tasks" (Voronoi Bubble pattern) |
| Diver Standee & Standee Base | 1 Diver (`86mm` tall) + 1 Base (`58mm` wide) | `Accessories` | Sliding Lid | Framed "Captain" (Voronoi Bubble pattern) |
| Sonar Tokens & Distress Token | 5 Sonar tokens (`29.5mm` dia) + 1 Distress token | `Accessories` | Sliding Lid | Multi-color inlays (Green sonar, Blue radio tower) |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Main Playing Deck Box (`Deck`)
* **Dimensions**: `61.0mm (Width) x 93.0mm (Length) x 26.0mm (Height)`.
* **Arrangement**: Sits vertically along the left corner spanning the entire 26.0mm box height.
* **Lid Mechanism**: `BoxType.SLIDING`.
* **Compartment**: Precision card pocket (`56.0 x 88.0mm`) with through-floor thumb cut.

### 3.2 Small Task Card Boxes (`Tasks1` & `Tasks2`)
* **Dimensions**: `49.0mm x 73.0mm x 14.7mm` each.
* **Arrangement**: Placed side-by-side on the bottom tier at `Z = 0.0mm` in the remaining 111.0mm wide column.
* **Compartment**: Sized for 48 unsleeved task cards (`44.0 x 68.0mm`).

### 3.3 Accessories & Standee Tray (`Accessories`)
* **Dimensions**: `111.0mm x 118.0mm x 11.0mm`.
* **Arrangement**: Stacks directly atop `Tasks1` and `Tasks2` (`14.7mm + 11.0mm = 25.7mm`), spanning the entire accessory column.
* **Lid Mechanism**: `BoxType.SLIDING` labeled "Captain".
* **Internal Precision Element Architecture**:
  * **Diver Standee**: SVG silhouette routed from the source vector artwork (`86.0mm` height, `2.5mm` thickness).
  * **Standee Base**: Custom SVG silhouette nestled beneath the diver (`58.0mm` width).
  * **Sonar Token Wells**: Dual circular wells (`29.5mm` dia) holding stacks of 3 and 2 tokens. Floors feature an embossed multi-color green sonar icon.
  * **Distress Token Well**: Rounded rectangular well (`44.0 x 29.0mm`) with an embossed multi-color blue distress antenna icon.

---

## 4. 3D Spatial Layout Map

```
+---------------------+---------------------------------------------------------+
| Deck (Full Height)  | Accessories Tray (Z: 14.7 .. 25.7mm, Height: 11.0mm)    |
| (61.0 x 93.0 x 26mm)| [ Holds Diver Standee, Base, Sonar & Distress Tokens ]  |
|                     +---------------------------+-----------------------------+
|                     | Tasks1 (Z: 0 .. 14.7mm)   | Tasks2 (Z: 0 .. 14.7mm)     |
|                     | (49.0 x 73.0 x 14.7mm)    | (49.0 x 73.0 x 14.7mm)      |
+---------------------+---------------------------+-----------------------------+
|<----- 61.0mm ------>|<------------------------ 111.0mm ---------------------->|
```
