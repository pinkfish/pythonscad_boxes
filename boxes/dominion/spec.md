# Dominion Big Box Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Dominion (Big Box)** organizer, ported from `examples/dominion.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `470.0mm (Width) x 290.0mm (Length) x 90.0mm (Height)`
* **Main Insert Usable Height**: `75.0mm` (`Z = 0.0 .. 75.0mm`, with 15mm board reserve)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `3.0mm`
* **Clearance Slack**: `0.0mm`
* **Card Dimensions**: `62.0mm x 93.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Base Game Kingdom Cards | 26 Decks x 10 cards = 260 cards | `BaseKingdomCards` | Sliding Lid | Framed "Dominion: Kingdom Cards" (Royal Blue) |
| Treasure & Victory Supply Cards | Copper, Silver, Gold, Platinum, Potion, Estate, Duchy, Province, Colony, Curse (~250 cards) | `TreasureAndVictoryCards` | Sliding Lid | Framed "Treasure & Victory" (Gold) |
| Alchemy & Expansion Kingdom Cards | 12 Decks x 10 cards = 120 cards | `AlchemyExpansionCards` | Sliding Lid | Framed "Alchemy & Expansions" (Purple) |
| Metal Coins & Debt Tokens | Metal coin tokens, debt tokens | `TokenTray1_CoinAndDebtTokens` | Cap Lid | Framed "Coin & Debt Tokens" |
| Player Mats & Special Tokens | Tavern mats, Coffers/Villagers mats, tokens | `TokenTray2_MatsAndSpecialTokens` | Cap Lid | Framed "Mats & Special Tokens" |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |

---

## 3. Sub-Box Specifications

### 3.1 Card Storage Columns (Width: `101.0mm`)
* **`BaseKingdomCards`** (`101.0mm x 230.0mm x 75.0mm`):
  * Positioned in Column 1 (`X = 0.0mm`, `Y = 0.0mm`).
  * Features a full-length channel with finger scoops for quick deck access.
* **`TreasureAndVictoryCards`** (`101.0mm x 200.0mm x 75.0mm`):
  * Positioned in Column 2 (`X = 101.0mm`, `Y = 0.0mm`).
* **`AlchemyExpansionCards`** (`101.0mm x 80.0mm x 75.0mm`):
  * Positioned end-to-end with the treasure cards in Column 2 (`X = 101.0mm`, `Y = 200.0mm`).

### 3.2 Token & Mat Trays (Column 3)
* **`TokenTray1_CoinAndDebtTokens`** & **`TokenTray2_MatsAndSpecialTokens`** (`101.0mm x 140.0mm x 37.5mm`):
  * Stacked in Column 3 at `X = 202.0mm`.
  * Dual-compartment trays with curved side scoops.

---

## 4. 3D Spatial Layout Map

```
+------------------------+-------------------------------+------------------------------+---------------------------+
| BaseKingdomCards       | TreasureAndVictoryCards       | TokenTray1_CoinAndDebtTokens |                           |
| (101.0 x 230.0 x 75mm) | (101.0 x 200.0 x 75mm)        | (101.0 x 140.0 x 37.5mm)     |                           |
|                        +-------------------------------+------------------------------+ Automatic 3D Spacers      |
|                        | AlchemyExpansionCards         | TokenTray2_MatsAndSpecial    | (Fills remaining width to |
|                        | (101.0 x 80.0 x 75mm)         | (101.0 x 140.0 x 37.5mm)     |  470mm and length 290mm)  |
+------------------------+-------------------------------+------------------------------+---------------------------+
|<------ 101mm --------->|<---------- 101mm ------------>|<---------- 101mm ----------->|<--------- 167mm --------->|
```
