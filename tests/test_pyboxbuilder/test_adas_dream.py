# SPDX-License-Identifier: Apache-2.0
"""Tests for the Ada's Dream board game insert."""

import unittest

from boxes.adas_dream.adas_dream import (
    box_length,
    box_width,
    project,
    usable_height,
)


class TestAdasDream(unittest.TestCase):
    """Test suite for Ada's Dream project build and layout."""

    def test_build_completes(self) -> None:
        """Verify the project builds all pieces without errors."""
        build = project.build()
        self.assertGreaterEqual(len(project._boxes), 26)
        self.assertGreater(len(build.pieces), 26)

    def test_box_labels_present(self) -> None:
        """Verify all 26 boxes from adas_dream.scad are defined."""
        labels = {b.label for b in project._boxes}
        expected = {
            "PlayerBox_Red",
            "PlayerBox_Blue",
            "PlayerBox_Green",
            "PlayerBox_Purple",
            "ScoringBox",
            "VisitorBox",
            "MoneyBox",
            "OtherCardBox",
            "TierCardBox",
            "AssignmentCardBox",
            "BookBox",
            "AssignmentBox",
            "DiceBox",
            "FirstPlayerBox",
            "AlternativeObjectiveBox",
            "BreakthroughBox",
            "ScorePadBox",
            "ProgramBox",
            "UniversityBox",
            "ResourceBox_Brass",
            "ResourceBox_Coal",
            "GearBox_AddGears",
            "GearBox_SubGears",
            "GearBox_MulGears",
            "SpacerSide",
            "ObjectiveBox",
        }
        for name in expected:
            self.assertIn(name, labels)

    def test_automatic_spacers_generated(self) -> None:
        """Verify automatic spacers are generated from leftover volume."""
        build = project.build()
        spacers = [p for p in build.pieces if "spacer" in p.label.lower() or p.kind == "spacer"]
        self.assertGreater(len(spacers), 0)

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
                z + h, usable_height + tol, f"{piece.label} overflows usable height ({z + h} > {usable_height})"
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
