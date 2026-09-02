# Earth Animal Kingdom Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D hierarchical packing for the **Earth Animal Kingdom** expansion organizer, ported from `examples/earth_animal_kingdom.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `288.0mm (Width) x 158.0mm (Length) x 47.0mm (Height)`
* **Wall Thickness**: `2.0mm` (`1.5mm` for animal token boxes)
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Animal Card Dimensions**: `72.0mm x 123.0mm` (36 cards)
* **Animal Token Thickness**: `8.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Count / Dimension | Storage Box | Box Type | Lid Accent / Pattern |
|---|---|---|---|---|
| Animal Cards | 36 oversized cards (`72 x 123mm`) | `AnimalCardsBox` | Sliding Lid | Framed "Animal Cards" (Maroon, Voronoi) |
| Wooden Sprouts | Set of green sprout pieces | `SproutBox` | Filament Hinge | Framed "Sprouts" (Green, Voronoi) |
| Wooden Tree Canopies | Set of canopy pieces | `CanopyBox` | Filament Hinge | Framed "Canopies" (Cornsilk, Voronoi) |
| Animal Tokens (Tray 1) | 26 Distinct animal shapes | `AnimalBox1` | Slipover Sleeve | Framed "Animals" (Saddlebrown, Voronoi) |
| Animal Tokens (Tray 2) | 30 Distinct animal shapes | `AnimalBox2` | Slipover Sleeve | Framed "Animals" (Saddlebrown, Voronoi) |
| Spacer / Top Tray | Residual void volume | `SpacerBox` | No Lid Tray | (Top of animal box stack) |

---

## 3. Sub-Box Specifications

### 3.1 Animal Cards Box (`AnimalCardsBox`)
* **Dimensions**: `76.0mm x 156.0mm x 23.6mm`.
* **Lid Mechanism**: `BoxType.SLIDING` with Voronoi decorative pattern.
* **Compartment**: Through-floor card well (`72.0 x 123.0 x 19.6mm`) for 36 cards with bottom finger hole.

### 3.2 Sprout Box (`SproutBox`)
* **Dimensions**: `76.0mm x 158.0mm x 22.4mm`.
* **Lid Mechanism**: `BoxType.FILAMENT_HINGE`.
* **Compartment**: Rounded interior well (r = 5.0mm) with 1.0mm wall inset for smooth retrieval.

### 3.3 Canopy Box (`CanopyBox`)
* **Dimensions**: `38.0mm x 158.0mm x 46.0mm`.
* **Lid Mechanism**: `BoxType.FILAMENT_HINGE` (full height trunk spanning down the right edge of the box).
* **Compartment**: Deep storage trough (r = 5.0mm corner rounding).

### 3.4 Animal Token Trays (`AnimalBox1` & `AnimalBox2`)
* **Dimensions**: `174.0mm x 158.0mm x 12.5mm` with `4.0mm` foot and `1.5mm` wall thickness.
* **Lid Mechanism**: `BoxType.SLIPOVER` with corner finger notches.
* **Two-Stage Well Architecture**:
  1. **Access Recess**: A shallow 4.0mm deep pan across the entire interior (`169.0 x 153.0mm`), allowing finger clearance underneath tokens.
  2. **Dedicated Token Pockets**:
     * `AnimalBox1` contains 26 precision token slots (capybara, cow, crocodile, deer, elephant, fly, fox, goat, gophers 1-5, hoopoe, jay, monkey, ornyx, pangolins 1-5, polar bear, rhino).
     * `AnimalBox2` contains 30 precision token slots (beaver, capybaras 1-2, chipmunk, eagle, gazelle, goanna, goose, jaguar, kangaroo, lemur, loon, peacock, pig, platypus, quokka, rabbit, snake, spider monkey, tarsier, termites 1-5, turkeys 1-5).

### 3.5 Spacer Box (`SpacerBox`)
* **Dimensions**: `174.0mm x 158.0mm x 21.0mm`.
* **Purpose**: Stacks atop `AnimalBox1` and `AnimalBox2` to fill the vertical column (`12.5 + 12.5 + 21.0 = 46.0mm`).

---

## 4. 3D Spatial Layout Map

```
+------------------------+------------------------------------+------------------+
| AnimalCardsBox (23.6)  | AnimalBox1 (12.5)                  |                  |
| (76 x 156mm)           | AnimalBox2 (12.5)                  | CanopyBox        |
+------------------------+ SpacerBox  (21.0)                  | (38 x 158 x 46)  |
| SproutBox (22.4)       | (174 x 158mm, Stacked Z: 0..46mm)  |                  |
| (76 x 158mm)           |                                    |                  |
+------------------------+------------------------------------+------------------+
|<------ 76mm ---------->|<------------ 174mm --------------->|<----- 38mm ----->|
```
