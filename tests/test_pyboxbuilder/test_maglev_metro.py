# SPDX-License-Identifier: Apache-2.0
"""Tests for the Maglev Metro board game insert."""

import unittest

from boxes.maglev_metro.maglev_metro import (
    box_height,
    box_length,
    box_width,
    project,
)


class TestMaglevMetro(unittest.TestCase):
    """Test suite for Maglev Metro project build and layout."""

    def test_build_completes(self) -> None:
        """Verify the project builds all pieces without errors."""
        build = project.build()
        self.assertGreaterEqual(len(project._boxes), 25)
        self.assertGreater(len(build.pieces), 25)

    def test_box_labels_present(self) -> None:
        """Verify all 25 boxes from maglev_metro.scad are defined."""
        labels = {b.label for b in project._boxes}
        expected = {
            "CardBox_Connections",
            "CardBox_Tracks",
            "CardBox_Passengers",
            "CardBox_PlayerObjectives",
            "RobotBox_Silver",
            "RobotBox_Gold",
            "RobotBox_Orange",
            "CommuterBox_Pink",
            "CommuterBox_Aqua",
            "CommuterBoxSmall_Purple",
            "CommuterBoxSmall_Coral",
            "SpacerTop",
            "StartTokenBox",
            "PlayerBox_green",
            "PlayerBox_deeppink",
            "PlayerBox_cyan",
            "PlayerBox_darkorange",
            "FactoryBox_Factories",
            "FactoryBox_Warehouses",
            "FactoryBox_Labs",
            "FactoryBox_Offices",
            "FactoryBox_Stores",
            "FactoryBox_Embassies",
            "MetroTileBox",
            "SpacerBox",
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
