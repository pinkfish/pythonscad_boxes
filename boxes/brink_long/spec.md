# Brink: Long Box Variant Organizer Specification

This document details the layout, component inventory, sub-box specifications, and 3D packing configuration for the **Brink: Long Box Variant** board game organizer (2–5 players), ported from `examples/brink_long.scad` to PythonSCAD (`pyboxbuilder`).

---

## 1. Game Box Dimensions & Constraints

* **Game Box Footprint**: `215.0mm (Width) x 307.0mm (Length) x 96.0mm (Height)`
* **Board & Player Mat Reserve**: `18.0mm` (Map board and player shields sit atop insert at `Z = 78.0 .. 96.0mm`)
* **Main Insert Usable Height**: `78.0mm` (`Z = 0.0 .. 78.0mm`)
* **Wall Thickness**: `3.0mm`
* **Floor Thickness**: `2.0mm`
* **Lid Thickness**: `2.0mm`
* **Clearance Slack**: `0.0mm`

---

## 2. Component Inventory & Storage Strategy

| Component | Quantity / Dimension | Storage Location | Box Type | Lid Style / Decoration |
|---|---|---|---|---|
| Long Player Trays (5 Players) | Upgrade board, Class I/II/III ships, 3 cargo + nubs, 3 railguns + nubs, player tokens, voting board + 5 bays | `PlayerBox_Yellow`, `Orange`, `Purple`, `Blue`, `Green` (`106 x 305 x 19mm`, 3 left + 2 right) | Cap Lid | Color-coded Framed "Player" |
| Primary Faction Resource Cubes | Komek, Ventus, Henko, Magnomi cubes (28+ each) | `ResourceBox_Komek` .. `ResourceBox_Magnomi` (`53 x 93.5 x 21mm`, 2x2 grid at `Z=57..78mm`) | Cap Lid | Faction SVG logos (color-coded) |
| Sorelia Cubes & UA Extras | Sorelia cubes + UA cubes, Flagship, Fusion Drive, First Player token | `ResourceBox_Sorelia`, `ResourceBox_UA` (`53 x 119.5 x 19mm`, leveling right side under `HexBox`) | Cap Lid | Faction / UA SVG logos (Purple, Crimson) |
| Small Card Decks | 52 Action cards, 20 Rider cards (2-column wells) | `CardBox_Actions` (`26mm`), `CardBox_Riders` (`14mm`) (`106 x 77.5mm`, flush at `Z=78mm`) | Sliding Lid (`lid_slide_axis="y"`) | Framed "Actions" / "Riders" |
| Standard Card Decks | 25 Ambassador, 5 Faction, 4 Rival + Guide cards | `CardBox_Ambassadors` (`23.5mm`), `Factions` (`8mm`), `Rivals` (`8.5mm`) (`106 x 77.5mm`) | Sliding Lid (`lid_slide_axis="x"`) | Color-coded Framed labels |
| Hex Sectors | Full 3-stack sector hex tray (`18mm` inner = 27 hexes: 25 map hexes + starting tile) | `HexBox` (`212 x 119.5 x 21mm` at `Z=57..78mm`) | Cap Lid | Framed "Hexes" (Dim Gray) |
| Board & Player Shields | Folded map board & player shields | Sits atop insert (`Z = 78.0 .. 96.0mm`) | Board Layer | Flat storage beneath box lid |
| Automatic Spacers | Remaining 3D void volume | Derived automatically | No-Lid Trays | Auto finger scoops |
