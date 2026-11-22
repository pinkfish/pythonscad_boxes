# SPDX-License-Identifier: Apache-2.0
"""Tests for the Railway Boom board game insert."""

import unittest

from boxes.railway_boom.railway_boom import (
    box_length,
    box_width,
    full_usable_height,
    project,
)


class TestRailwayBoom(unittest.TestCase):
    """Test suite for Railway Boom project build and layout."""

    def test_build_completes(self) -> None:
        """Verify the project builds all pieces without errors."""
        build = project.build()
        self.assertGreaterEqual(len(project._boxes), 21)
        self.assertGreater(len(build.pieces), 21)

    def test_box_labels_present(self) -> None:
        """Verify all 21 boxes from railway_boom.scad are defined."""
        labels = {b.label for b in project._boxes}
        expected = {
            "PlayerBox_Red",
            "PlayerBox_Yellow",
            "PlayerBox_Blue",
            "PlayerBox_Green",
            "SpacerPlayerBoardBox",
            "StationCardBox",
            "ObjectiveCardBox",
            "RouteCardBox",
            "TouristTileBox",
            "SmallCardBox_Locomotives",
            "SmallCardBox_Carriages",
            "SmallCardBox_CityTiles",
            "FrontSpacerBox",
            "DevelopmentCardBox_1",
            "DevelopmentCardBox_2",
            "ResourceBox_Materials",
            "ResourceBox_VP",
            "ResourceBox_Tech",
            "ResourceBox_Coal",
            "IndicatorBox",
            "ResourceBox_Money",
        }
        for name in expected:
            self.assertIn(name, labels)

    def test_all_pieces_fit_within_usable_bounds(self) -> None:
        """Verify no piece overflows the physical box dimensions or usable height."""
        build = project.build()
        tol = 1e-3
        for piece in build.pieces:
            if piece.position is None or piece.size is None:
                continue
            x, y, z = piece.position
            w, l, h = piece.size
            self.assertGreaterEqual(x, -tol, f"{piece.label} X < 0")
            self.assertGreaterEqual(y, -tol, f"{piece.label} Y < 0")
            self.assertGreaterEqual(z, -tol, f"{piece.label} Z < 0")
            self.assertLessEqual(x + w, box_width + tol, f"{piece.label} overflows box width ({x + w} > {box_width})")
            self.assertLessEqual(
                y + l, box_length + tol, f"{piece.label} overflows box length ({y + l} > {box_length})"
            )
            self.assertLessEqual(
                z + h,
                full_usable_height + tol,
                f"{piece.label} overflows usable height ({z + h} > {full_usable_height})",
            )

    def test_no_box_overlaps(self) -> None:
        """Verify distinct box bases do not overlap in 3D space."""
        build = project.build()
        bases = [p for p in build.pieces if p.kind == "box" and p.position is not None and p.size is not None]
        tol = 1e-3
        for i, a in enumerate(bases):
            ax, ay, az = a.position  # type: ignore[misc]
            aw, al, ah = a.size  # type: ignore[misc]
            for b in bases[i + 1 :]:
                bx, by, bz = b.position  # type: ignore[misc]
                bw, bl, bh = b.size  # type: ignore[misc]
                overlaps = (
                    ax < bx + bw - tol
                    and bx < ax + aw - tol
                    and ay < by + bl - tol
                    and by < ay + al - tol
                    and az < bz + bh - tol
                    and bz < az + ah - tol
                )
                self.assertFalse(overlaps, f"{a.label} overlaps {b.label}")
