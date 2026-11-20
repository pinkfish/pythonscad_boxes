# Brink Board Game Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Brink** board game organizer (2–5 players), ported from `examples/brink.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `215.0mm (Width) x 307.0mm (Length) x 96.0mm (Height)`
* **Board & Player Mat Reserve**: `18.0mm` (Map board and player shields sit atop insert at `Z = 78.0 .. 96.0mm`)
* **Main Insert Usable Height**: `78.0mm` (`Z = 0.0 .. 78.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`
* **Hex Sector Diameter**: `72.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Sector Hex Tiles | 25 map hexes + starting/bonus hexes | `HexBox` (`22mm`), `HexBonusBox` (`10mm`) | Cap Lid | Framed "Hexes" / "Bonus Hexes" (Dim Gray) |
| Player Trays (5 Players) | Upgrade board, Class I/II/III ships, 3 cargo + nubs, 3 railguns + nubs, 2 player tokens | `PlayerBox_Yellow`, `Orange`, `Purple`, `Blue`, `Green` (`106 x 110 x 21mm`) | Cap Lid | Color-coded Framed "Player" |
| Primary Faction Resource Cubes | 4 primary factions (Komek, Ventus, Henko, Magnomi) | `ResourceBox_Komek` .. `ResourceBox_Magnomi` (`53.25 x 119.5 x 26mm`) | Cap Lid | Faction SVG logos (color-coded) |
| Sorelia Cubes & UA / Extra Bits | Sorelia cubes + 15 UA cubes, UA Flagship, Fusion Drive, First Player token | `ResourceBox_Sorelia`, `ResourceBox_UA` (`53 x 110 x 21mm`) | Cap Lid | Faction / UA SVG logos (Purple, Crimson) |
| Small Card Decks | 52 Action cards, 20 Rider cards (2-column wells) | `CardBox_Actions`, `CardBox_Riders` (`106.5 x 77.5mm`) | Sliding Lid (`lid_slide_axis="y"`) | Framed "Actions" / "Riders" |
| Standard Card Decks | 25 Ambassador, 5 Faction, 4 Rival, Community, Holo | `CardBox_Ambassadors`, `Factions`, `Rivals`, `Community`, `Holo` (`106.5 x 77.5mm`) | Sliding Lid (`lid_slide_axis="x"`) | Color-coded Framed labels |
| Main Map Board & Shields | Mounted game board + voting tracks + player shields | Sits atop insert (`Z = 78.0 .. 96.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |
