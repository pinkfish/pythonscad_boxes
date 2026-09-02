# Earth Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and dynamic hierarchical arrangement for the **Earth** board game organizer, ported to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `288.0mm (Width) x 288.0mm (Length) x 72.0mm (Height)`
* **Wall Thickness**: `3.0mm` (Enhanced structural thickness for card and component boxes)
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `3.0mm`
* **Clearance Slack**: `0.0mm`
* **Card Dimensions**: `62.0mm x 93.0mm`
* **Standard Footprint**: `68.0mm x 99.0mm` (Shared by all card boxes and player boxes to enable modular column stacking)

---

## 2. Component Inventory & Storage Strategy

| Component / Deck | Count / Dimension | Storage Box | Box Type | Lid Accent / Label |
|---|---|---|---|---|
| Earth Cards (Flora, Terrain, Events) | 283 cards total (split 4 ways ~70 cards each) | `EarthCardBox1` .. `EarthCardBox4` | Sliding Lid | Framed "Earth" (Dark Green) |
| Earth Promo / Extra Cards | 20 cards | `EarthCardBoxSmall` | Sliding Lid | Framed "Earth" (Dark Green) |
| Ecosystem Cards | 32 cards | `EcosystemCardBox` | Sliding Lid | Framed "Ecosystem" (Gold) |
| Fauna Cards | 23 cards | `FaunaCardBox` | Sliding Lid | Framed "Fauna" (Gold) |
| Island Cards | 10 cards | `IslandCardBox` | Sliding Lid | Framed "Island" (Gold) |
| Climate Cards | 10 cards | `ClimateCardBox` | Sliding Lid | Framed "Climate" (Teal) |
| Solo Mode Cards | 6 cards | `SoloCardBox` | Sliding Lid | Framed "Solo" (Teal) |
| Season Cards | 12 cards | `SeasonCardBox` | Sliding Lid | Framed "Season" (Teal) |
| Abundance / Other Cards | 10 cards | `AbundanceOtherCardBox` | Sliding Lid | Framed "Abundance" (Teal) |
| Compost Cards / Tokens | Deck / Pile | `CompostBox` (`36.8mm` height) | Filament Hinge | Framed "Compost" (Brown) |
| First Player & Start Tokens | Start player components | `StartBox` (`12.0mm` height) | Cap Lid | Framed "Start" (Gold) |
| Player Components (6 Colors) | Red, Green, Yellow, Blue, Purple, Pink | `PlayerBox<Colour>` (6 boxes, `9.2mm` height) | Slipover Sleeve | Framed "Player" |
| Wooden Canopy Pieces | Full set of tree canopies | `CanopyBox` (`168.0 x 88.0 x 55.2mm`) | Filament Hinge | Framed "Canopy" (Olive) |
| Sprout Cylinders | Full set of wooden sprouts | `SproutBox` (`107.0 x 88.0 x 48.6mm`) | Filament Hinge | Framed "Sprouts" (Green) |
| Score Pad | 1 Score Pad | `ScorePadBox` (`107.0 x 88.0 x 6.6mm`) | No Lid Tray | (Under player boards) |
| Wooden Seed Tokens | Set of seed pieces | `SeedBox` (`12.0 x 46.0 x 72.0mm`) | Filament Hinge | Framed "Seeds" (Brown) |
| Player & Abundance Boards | 6 Player Mats + Abundance Boards | `PlayerBoards` & `AbundanceBoards` | Open Trays | Flat on top / Side edge |

---

## 3. Sub-Box Specifications

### 3.1 Earth Card Boxes
* **Dimensions**: Footprint `68.0mm x 99.0mm`. Heights automatically calculated by `box.cards(count=...)`.
* **Arrangement**: Front row consists of 4 main `EarthCardBox` sub-boxes side-by-side (`4 x 68.0mm = 272.0mm`).
* **Lid Mechanism**: `BoxType.SLIDING` with framed dark green labels.

### 3.2 Auxiliary Card & Token Columns (Middle Row)
Stacked into 4 uniform columns of equal height (~55.2mm) using the shared `68.0 x 99.0mm` footprint:
1. **Column 1**: `EarthCardBoxSmall` + `CompostBox`
2. **Column 2**: `EcosystemCardBox` + `FaunaCardBox` + `IslandCardBox`
3. **Column 3**: `ClimateCardBox` + `SoloCardBox` + `SeasonCardBox` + `AbundanceOtherCardBox` + `StartBox`
4. **Column 4**: Stack of all 6 `PlayerBox<Colour>` slipover boxes

### 3.3 Large Wooden Resource Boxes (Back Row)
* **`CanopyBox`** (`168.0mm x 88.0mm x 55.2mm`): Filament-hinged trunk for canopy miniatures with side finger scoops.
* **`SproutBox`** (`107.0mm x 88.0mm x 48.6mm`): Filament-hinged box for sprout cylinders.
* **`ScorePadBox`** (`107.0mm x 88.0mm x 6.6mm`): Sits directly atop `SproutBox` to reach the unified 55.2mm row height.

### 3.4 Side Edge & Board Storage
* **`SeedBox`** (`12.0mm x 46.0mm x 72.0mm`): Narrow vertical filament-hinge dispenser standing down the right edge.
* **`AbundanceBoards`** (`12.0mm x 241.0mm x 57.0mm`): Vertical tray securing abundance boards on edge.
* **`PlayerBoards`** (`242.0mm x 288.0mm x 16.8mm`): Open storage tray spanning across the top of all sub-boxes.

---

## 4. Hierarchical Layout Map

```
+-------------------------------------------------------------+-------------------+
| Front Row: 4 Earth Card Boxes                               |                   |
| [ EarthCardBox1 ] [ EarthCardBox2 ] [ EarthCardBox3 ] [...]  |                   |
+-------------------------------------------------------------+ SeedBox           |
| Middle Row: 4 Shared-Footprint Stack Columns (H: 55.2mm)    | (12 x 46 x 72mm)  |
| [ Col 1: Small+Compost ] [ Col 2: Eco+Fauna+Island ] ...     |                   |
+-------------------------------------------------------------+-------------------+
| Back Row: Large Resource Dispensers (H: 55.2mm)             |                   |
| [ CanopyBox (168 x 88mm) ] [ SproutBox + ScorePad (107x88) ] | AbundanceBoards   |
+-------------------------------------------------------------+ (12 x 241 x 57mm) |
| TOP LAYER: PlayerBoards (242 x 288 x 16.8mm) spanning all   |                   |
+-------------------------------------------------------------+-------------------+
```
