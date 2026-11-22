# SPDX-License-Identifier: Apache-2.0
"""Tests for the Earth board game insert."""

import unittest

from boxes.earth.earth import (
    box_height,
    box_length,
    box_width,
    project,
)


class TestEarth(unittest.TestCase):
    """Test suite for Earth project build and layout."""

    def test_build_completes(self) -> None:
        """Verify the project builds all pieces without errors."""
        build = project.build()
        self.assertGreaterEqual(len(project._boxes), 26)
        self.assertGreater(len(build.pieces), 26)

    def test_box_labels_present(self) -> None:
        """Verify all 26 boxes from earth.scad are defined."""
        labels = {b.label for b in project._boxes}
        expected = {
            "CardBox_Flora",
            "CardBox_Terrain",
            "CardBox_Events",
            "CardBox_Abundance",
            "EarthCardBoxSmall",
            "CompostBox_1",
            "CompostBox_2",
            "SeedBox",
            "TopSpacedBox",
            "EcosystemCardBox",
            "FaunaCardBox",
            "IslandCardBox",
            "ClimateCardBox",
            "SoloCardBox",
            "SeasonCardBox",
            "AbundanceOtherCardBox",
            "StartBox",
            "PlayerBox_Red",
            "PlayerBox_Green",
            "PlayerBox_Yellow",
            "PlayerBox_Blue",
            "PlayerBox_Purple",
            "PlayerBox_Pink",
            "CanopyBox",
            "ScorePadBox",
            "SproutBox",
        }
        for name in expected:
            self.assertIn(name, labels)

    def test_all_pieces_fit_within_box_bounds(self) -> None:
        """Verify no piece overflows the physical box dimensions."""
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
                z + h, box_height + tol, f"{piece.label} overflows box height ({z + h} > {box_height})"
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
