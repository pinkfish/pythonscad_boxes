# SPDX-License-Identifier: Apache-2.0
"""Card sleeve catalog: the actual sleeve sizes, by brand.

A table of the distinct board-game sleeve *sizes* (not game sets) sold by
Sleeve Kings, Gamegenic and Mayday Games. Each row carries the three figures
that matter for building a box:

* **max card size** — the largest card (mm) that slides into the sleeve;
* **outside dimensions** — the sleeve's own width x length (mm);
* **thickness/weight** — the sleeve film in microns (µm), per grade.

Game-specific sets (Sleeve Kings "Space Base", "Yucatan", "Kingdom Death
Monster", "Wyrmspan", "Betrayal…", "Tiny Epic", the "XL/Super Large" family,
and Mayday "Tribune", "Sails of Glory", "Police Precinct", "Dwarf King", etc.)
are omitted: they are the same handful of sizes above relabelled per game, not
distinct sleeve sizes. The oversized sizes that are only ever marketed under a
game name are given size names instead: "7 Wonders" (65x100) is "Magnum",
"Lost Cities" (70x110) is "Lost Cities Magnum", and "Dixit" (80x120) is
"Oversized"; "Catan" (54x80) is listed by its card dimensions.

Data notes (gathered 2026-08 from the manufacturers' sites):

* **Gamegenic** publishes both the sleeve size and the max card size, so its
  rows use the published figures.
* **Sleeve Kings** and **Mayday Games** publish only the card size a sleeve
  fits. Their *outside dimensions* below are the FFG-compatible nominal sleeve
  size for that card size (the industry standard these "FFG compatible" sleeves
  match), since the manufacturers do not state a sleeve size.
* Thickness: Sleeve Kings Standard = 60 µm, Premium = 100 µm; Mayday Standard =
  40 µm, Premium = 90 µm; Gamegenic Prime/Matte = 100 µm. Gamegenic Retro is an
  FFG-grey-style sleeve whose micron rating is not published.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

#: A typical playing card is ~0.30 mm thick; a sleeve adds its film thickness.
BASE_CARD_THICKNESS = 0.30

#: Micron rating assumed when a manufacturer does not state one.
_DEFAULT_MICRONS = 100

#: Fallback footprint margin (mm) if a sleeve's outer size is somehow unknown.
_DEFAULT_MARGIN = 3.0


@dataclass(frozen=True, slots=True)
class Sleeve:
    """A sleeve size sold by a brand in a particular thickness grade.

    Attributes:
        brand: Manufacturer name.
        name: The generic size name (``"Mini European"``, ``"Standard"``, ...).
        card_size: ``(width, length)`` of the largest card that fits — the
            "inner card size max".
        sleeve_size: ``(width, length)`` of the sleeve itself — the outside
            dimensions.
        thickness_microns: Sleeve film thickness in microns (µm), when known.
        pack_count: Sleeves per pack, when known.
        sku: Manufacturer's product/SKU code, when known.
        grade: Thickness tier — ``"Standard"`` or ``"Premium"`` (Mayday,
            Sleeve Kings), ``"Prime / Matte"`` or ``"Retro"`` (Gamegenic).

    """

    brand: str
    name: str
    card_size: tuple[float, float]
    sleeve_size: tuple[float, float]
    thickness_microns: int | None = None
    pack_count: int | None = None
    sku: str | None = None
    grade: str | None = None

    @property
    def card_width(self) -> float:
        """Max card width that fits (mm)."""
        return self.card_size[0]

    @property
    def card_length(self) -> float:
        """Max card length that fits (mm)."""
        return self.card_size[1]

    def fits(self, card_width: float, card_length: float) -> bool:
        """Return True if a card of the given size slides into this sleeve."""
        return card_width <= self.card_width and card_length <= self.card_length

    @property
    def footprint_margin(self) -> float:
        """Extra the sleeve adds around a card (mm), applied to both axes.

        The larger of the two per-axis differences, so a single margin covers
        both when sizing a well.
        """
        if self.sleeve_size is not None:
            return max(
                self.sleeve_size[0] - self.card_size[0],
                self.sleeve_size[1] - self.card_size[1],
            )
        return _DEFAULT_MARGIN

    @property
    def card_thickness(self) -> float:
        """Thickness of one sleeved card (mm): the card plus the sleeve film."""
        microns = self.thickness_microns if self.thickness_microns is not None else _DEFAULT_MICRONS
        return BASE_CARD_THICKNESS + microns / 1000.0


# ── Catalog data ────────────────────────────────────────────────────────────
# Row order: brand, name, card_w, card_l, sleeve_w, sleeve_l, microns, pack,
#            sku, grade.
_SK = "Sleeve Kings"
_GG = "Gamegenic"
_MD = "Mayday Games"

_ROWS: tuple[tuple[Any, ...], ...] = (
    # ── Sleeve Kings ─────────────────────────────────────────────────────────
    (_SK, "Mini American", 41.0, 63.0, 44.0, 66.0, 60, 110, "SKS-8801", "Standard"),
    (_SK, "Mini American", 41.0, 63.0, 44.0, 66.0, 100, 55, "SKS-9901", "Premium"),
    (_SK, "Mini Chimera", 43.0, 65.0, 46.0, 68.0, 60, 110, "SKS-8802", "Standard"),
    (_SK, "Mini European", 45.0, 68.0, 46.0, 71.0, 60, 110, "SKS-8803", "Standard"),
    (_SK, "Mini European", 44.0, 68.0, 46.0, 71.0, 100, 55, "SKS-9902", "Premium"),
    (_SK, "Standard American", 57.0, 89.0, 59.0, 91.0, 100, 55, "SKS-9903", "Premium"),
    (_SK, "Chimera", 57.5, 89.0, 60.0, 92.0, 60, 110, "SKS-8808", "Standard"),
    (_SK, "Standard European", 59.0, 92.0, 62.0, 94.0, 60, 110, "SKS-8809", "Standard"),
    (_SK, "Standard European", 59.0, 92.0, 62.0, 94.0, 100, 55, "SKS-9904", "Premium"),
    (_SK, "Standard Card Game", 63.5, 88.0, 66.0, 91.0, 60, 110, "SKS-8810", "Standard"),
    (_SK, "Standard Card Game", 63.5, 88.0, 66.0, 91.0, 100, 55, "SKS-9905", "Premium"),
    (_SK, "Square", 70.0, 70.0, 73.0, 73.0, 60, 110, "SKS-8812", "Standard"),
    (_SK, "Square", 70.0, 70.0, 73.0, 73.0, 100, 55, "SKS-9965", "Premium"),
    (_SK, "Square Large", 80.0, 80.0, 82.0, 82.0, 60, 110, "SKS-8815", "Standard"),
    (_SK, "Tarot", 70.0, 120.0, 73.0, 123.0, 60, 110, "SKS-8814", "Standard"),
    (_SK, "Tarot", 70.0, 120.0, 73.0, 123.0, 100, 55, "SKS-9966", "Premium"),
    (_SK, "Magnum", 65.0, 100.0, 67.0, 103.0, 60, 110, "SKS-8811", "Standard"),
    (_SK, "Magnum", 65.0, 100.0, 67.0, 103.0, 100, 55, "SKS-9967", "Premium"),
    (_SK, "Lost Cities Magnum", 70.0, 110.0, 72.0, 112.0, 60, 110, "SKS-8813", "Standard"),
    (_SK, "Oversized", 80.0, 120.0, 82.0, 122.0, 60, 110, "SKS-8816", "Standard"),

    # ── Gamegenic ────────────────────────────────────────────────────────────
    (_GG, "Standard Card Game", 64.0, 89.0, 66.0, 91.0, 100, 50, None, "Prime / Matte"),
    (_GG, "Standard American", 57.0, 89.0, 59.0, 91.0, 100, 50, None, "Prime / Matte"),
    (_GG, "Standard European", 60.0, 92.0, 62.0, 94.0, 100, 50, None, "Prime / Matte"),
    (_GG, "Mini American", 42.0, 65.0, 44.0, 67.0, 100, 50, None, "Prime / Matte"),
    (_GG, "Mini European", 44.0, 69.0, 46.0, 71.0, 100, 50, None, "Prime / Matte"),
    (_GG, "Tarot", 71.0, 120.0, 73.0, 122.0, 100, 50, None, "Prime / Matte"),
    (_GG, "Square", 71.0, 71.0, 73.0, 73.0, 100, 50, None, "Prime / Matte"),
    (_GG, "Square Large", 80.0, 80.0, 82.0, 82.0, 100, 50, None, "Prime / Matte"),
    (_GG, "Magnum", 65.0, 101.0, 67.0, 103.0, 100, 80, None, "Prime / Matte"),
    (_GG, "Lost Cities Magnum", 70.0, 110.0, 72.0, 112.0, 100, 60, None, "Prime / Matte"),
    (_GG, "Oversized", 80.0, 120.0, 81.0, 122.0, 100, 90, None, "Prime / Matte"),
    (_GG, "54x80", 54.0, 80.0, 56.0, 82.0, 100, 60, None, "Prime / Matte"),
    (_GG, "Retro", 63.5, 88.0, 66.5, 94.0, None, 50, None, "Retro"),

    # ── Mayday Games ─────────────────────────────────────────────────────────
    (_MD, "Mini American", 41.0, 63.0, 44.0, 66.0, 40, 100, "MDG-7039", "Standard"),
    (_MD, "Mini American", 41.0, 63.0, 44.0, 66.0, 90, 50, "MDG-7075", "Premium"),
    (_MD, "Mini Chimera", 43.0, 65.0, 46.0, 68.0, 40, 100, "MDG-7045", "Standard"),
    (_MD, "Mini Chimera", 43.0, 65.0, 46.0, 68.0, 90, 50, "MDG-7079", "Premium"),
    (_MD, "Mini European", 45.0, 68.0, 46.0, 71.0, 40, 100, "MDG-7035", "Standard"),
    (_MD, "Mini European", 45.0, 68.0, 46.0, 71.0, 90, 50, "MDG-7080", "Premium"),
    (_MD, "Chimera", 57.5, 89.0, 60.0, 92.0, 40, 100, "MDG-7044", "Standard"),
    (_MD, "Chimera", 57.5, 89.0, 60.0, 92.0, 90, 50, "MDG-7078", "Premium"),
    (_MD, "Standard European", 59.0, 92.0, 62.0, 94.0, 40, 100, "MDG-7028", "Standard"),
    (_MD, "Standard European", 59.0, 92.0, 62.0, 94.0, 90, 50, "MDG-7029", "Premium"),
    (_MD, "Standard Card Game", 63.5, 88.0, 66.0, 91.0, 40, 100, "MDG-7041", "Standard"),
    (_MD, "Standard Card Game", 63.5, 88.0, 66.0, 91.0, 90, 50, "MDG-7077", "Premium"),
    (_MD, "Square", 70.0, 70.0, 73.0, 73.0, 40, 100, "MDG-7124", "Standard"),
    (_MD, "Square", 70.0, 70.0, 73.0, 73.0, 90, 50, "MDG-7134", "Premium"),
    (_MD, "Square Large", 80.0, 80.0, 82.0, 82.0, 40, 100, "MDG-7125", "Standard"),
    (_MD, "Square Large", 80.0, 80.0, 82.0, 82.0, 90, 50, "MDG-7145", "Premium"),
    (_MD, "Tarot", 70.0, 120.0, 73.0, 123.0, 40, 100, "MDG-7152", "Standard"),
    (_MD, "Tarot", 70.0, 120.0, 73.0, 123.0, 90, 75, "MDG-7100", "Premium"),
    (_MD, "Magnum", 65.0, 100.0, 67.0, 103.0, 40, 100, "MDG-7102", "Standard"),
    (_MD, "Magnum", 65.0, 100.0, 67.0, 103.0, 90, 80, "MDG-7106", "Premium"),
    (_MD, "Lost Cities Magnum", 70.0, 110.0, 72.0, 112.0, 40, 100, "MDG-7103", "Standard"),
    (_MD, "Lost Cities Magnum", 70.0, 110.0, 72.0, 112.0, 90, 50, "MDG-7144", "Premium"),
    (_MD, "Oversized", 80.0, 120.0, 82.0, 122.0, 40, 100, "MDG-7104", "Standard"),
    (_MD, "Oversized", 80.0, 120.0, 82.0, 122.0, 90, 50, "MDG-7146", "Premium"),
)


def _build() -> tuple[Sleeve, ...]:
    sleeves = []
    for row in _ROWS:
        brand, name, cw, cl, sw, sl, microns, pack, sku, grade = row
        sleeves.append(
            Sleeve(
                brand=brand,
                name=name,
                card_size=(float(cw), float(cl)),
                sleeve_size=(float(sw), float(sl)),
                thickness_microns=microns,
                pack_count=pack,
                sku=sku,
                grade=grade,
            )
        )
    return tuple(sleeves)


#: The full sleeve catalog, one :class:`Sleeve` per brand/size/grade.
SLEEVE_CATALOG: tuple[Sleeve, ...] = _build()

#: The manufacturers covered by the catalog.
BRANDS: tuple[str, ...] = tuple(dict.fromkeys(s.brand for s in SLEEVE_CATALOG))


def sleeves_for_card(
    card_width: float,
    card_length: float,
    *,
    brand: str | None = None,
    grade: str | None = None,
) -> tuple[Sleeve, ...]:
    """Return every sleeve size that fits a card, sorted by brand then name.

    Args:
        card_width: Card width in mm.
        card_length: Card length in mm.
        brand: Optional brand filter (case-insensitive).
        grade: Optional grade filter (``"Standard"``, ``"Premium"``, ...).

    """
    results = []
    for sleeve in SLEEVE_CATALOG:
        if brand is not None and sleeve.brand.lower() != brand.lower():
            continue
        if grade is not None and sleeve.grade != grade:
            continue
        if sleeve.fits(card_width, card_length):
            results.append(sleeve)
    return tuple(sorted(results, key=lambda s: (s.brand, s.name)))


def sleeve_by_sku(sku: str) -> Sleeve | None:
    """Return the sleeve with the given SKU, or ``None`` if it is not present."""
    for sleeve in SLEEVE_CATALOG:
        if sleeve.sku == sku:
            return sleeve
    return None


def find_sleeve(brand: str, name: str, grade: str | None = None) -> Sleeve | None:
    """Return the first sleeve matching ``brand``, ``name`` and ``grade``.

    ``grade`` is optional because a brand usually sells one size under one grade
    per product line; pass it to disambiguate when a size exists in several
    thicknesses (e.g. Mayday "Standard" vs "Premium").

    Returns ``None`` when no sleeve matches, so callers can fall back or raise
    as they see fit.
    """
    for sleeve in SLEEVE_CATALOG:
        if sleeve.brand == brand and sleeve.name == name and (grade is None or sleeve.grade == grade):
            return sleeve
    return None
