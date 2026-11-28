# SPDX-License-Identifier: Apache-2.0
"""Tests verifying pyboxbuilder box types build cleanly under pybosl2's SDF backend."""

from __future__ import annotations

import pybosl2
import pytest

from pyboxbuilder import (
    BoxType,
    LidBuilder,
    MagnetType,
    PatternBuilder,
    PatternType,
    Project,
)

_L_PATH = (
    (0.0, 0.0),
    (55.0, 0.0),
    (55.0, 25.0),
    (25.0, 25.0),
    (25.0, 55.0),
    (0.0, 55.0),
)


@pytest.mark.parametrize("box_type", list(BoxType), ids=lambda bt: bt.value)
def test_every_box_type_builds_on_sdf_backend(box_type: BoxType) -> None:
    """Every BoxType produces SdfSolid geometry when pybosl2's 'sdf' backend is active."""
    kw: dict[str, object] = {"size": (65.0, 55.0, 26.0)}
    if box_type in (BoxType.PATH, BoxType.CAP_PATH, BoxType.SLIPOVER_PATH):
        kw["path"] = _L_PATH
    if box_type is BoxType.MAGNETIC:
        kw["magnet_type"] = MagnetType.ROUND
    if box_type not in (
        BoxType.NO_LID,
        BoxType.PATH,
        BoxType.CARD_TRAY,
        BoxType.PRINT_IN_PLACE_HINGE,
        BoxType.INSET_HINGE,
        BoxType.SLEEVE_DRAWER,
    ):
        # 2D text() is CSG-only in pybosl2; omit lid text so SDF builds cleanly
        kw["lid"] = LidBuilder(text="", pattern=PatternBuilder(PatternType.SOLID))

    with pybosl2.use_backend("sdf"):
        p = Project("SdfAllTypes")
        p.box(box_type, "B", **kw)
        build = p.build()
        assert build.pieces
        for piece in build.pieces:
            solid = piece.solid
            if piece.kind == "lid":
                dec, _ = p._decorated_lid(piece, "single")
                solid = dec if dec is not None else solid
            assert solid is not None
            assert type(solid).__name__ == "SdfSolid"


def test_sdf_compartments_cards_and_hex_lid() -> None:
    """Compartments, holds_pieces scoops, card push-through holes, and hex lids work on SDF."""
    with pybosl2.use_backend("sdf"):
        p = Project("SdfFeatures")
        tray = p.box(BoxType.NO_LID, "Tokens", size=(80.0, 60.0, 25.0))
        tray.compartment("A", width_ratio=0.5, holds_pieces=True)
        tray.compartment("B", width_ratio=0.5, holds_pieces=True)

        deck = p.box(
            BoxType.SLIDING,
            "Cards",
            size=(70.0, 96.0, 35.0),
            lid=LidBuilder(pattern=PatternBuilder(PatternType.HEX)),
        )
        deck.cards("Deck", count=50, size=(63.5, 88.0))

        p.box(
            BoxType.CARD_TRAY,
            "AngledTray",
            size=(72.0, 100.0, 60.0),
            card_tilt_angle=20.0,
            divider_slots=2,
        )

        build = p.build()
        assert len(build.pieces) == 4
        for piece in build.pieces:
            solid = piece.solid
            if piece.kind == "lid":
                dec, _ = p._decorated_lid(piece, "single")
                solid = dec if dec is not None else solid
            assert solid is not None
            assert type(solid).__name__ == "SdfSolid"
