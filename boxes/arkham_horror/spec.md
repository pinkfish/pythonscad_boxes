# Arkham Horror LCG Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Arkham Horror: The Card Game** organizer, ported from `examples/arkham_horror_tcg.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `242.0mm (Width) x 283.0mm (Length) x 75.0mm (Height)`
* **Main Insert Usable Height**: `73.0mm` (`Z = 0.0 .. 73.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `3.0mm`
* **Clearance Slack**: `0.0mm`
* **Card Dimensions**: `66.0mm x 92.0mm` (Sleeved standard cards)

---

## 2. Component Inventory & Storage Strategy

| Component | Count / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Core Set Investigator & Class Decks | ~250 cards (5 investigators, 6 classes, neutral/weaknesses) | `CorePlayerCards` | Sliding Lid | Framed "Core Investigators" (Teal, Voronoi) |
| Core Set Campaign Scenario Cards | ~120 cards (3 scenarios, 6 encounter sets) | `CoreScenarioCards` | Sliding Lid | Framed "Core Campaign" (Midnight Blue, Voronoi) |
| Chaos Tokens | Full chaos token bag set (~44 tokens) | `TokenTray1_ChaosTokens` | Cap Lid | Framed "Chaos Tokens" (Dark Red) |
| Damage & Horror Tokens | Cardboard damage/horror tokens | `TokenTray2_DamageAndHorror` | Cap Lid | Framed "Damage & Horror" (Dark Red) |
| Clue & Resource Tokens | Cardboard clue/resource tokens | `TokenTray3_CluesAndResources` | Cap Lid | Framed "Clues & Resources" (Dark Red) |
| Threat Dials & Investigator Mini Cards | Mini cards, dials, stands | `AccessoryTray` | Cap Lid | Framed "Accessories" (Voronoi) |
| Automatic Spacers | Residual volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Card Library Boxes
* **`CorePlayerCards`** (`100.0mm x 140.0mm x 73.0mm`):
  * Sized for sleeved player decks with side finger scoop.
* **`CoreScenarioCards`** (`100.0mm x 140.0mm x 73.0mm`):
  * Positioned end-to-end with the player card box along the left side (`Y = 140.0mm`).

### 3.2 Token Trays (Stacked 3-High)
* **`TokenTray1_ChaosTokens`**, **`TokenTray2_DamageAndHorror`**, **`TokenTray3_CluesAndResources`**:
  * Dimensions: `140.0mm x 140.0mm x 24.33mm` each.
  * Arranged in a vertical 3-tier stack from `Z = 0.0mm` to `Z = 73.0mm` at `X = 100.0mm`.
  * Each tray features 4 equal-width recessed pockets with curved finger scoops.

### 3.3 Accessory Tray
* **`AccessoryTray`** (`140.0mm x 140.0mm x 36.5mm`):
  * Positioned at `X = 100.0mm`, `Y = 140.0mm` holding dials, mini cards, and standees.

---

## 4. 3D Spatial Layout Map

```
+-----------------------------------+-------------------------------------------+
| CorePlayerCards (100.0 x 140.0)   | TokenTray1..3 (Stacked 3-high, Z: 0..73)  |
| (Height: 73.0mm, Z: 0..73mm)      | (140.0 x 140.0 x 24.33mm)                 |
+-----------------------------------+-------------------------------------------+
| CoreScenarioCards (100.0 x 140.0) | AccessoryTray (140.0 x 140.0 x 36.5mm)    |
| (Height: 73.0mm, Z: 0..73mm)      | + Automatic Void Spacers above/beside     |
+-----------------------------------+-------------------------------------------+
|<------------ 100mm -------------->|<---------------- 140mm ------------------>|
```
