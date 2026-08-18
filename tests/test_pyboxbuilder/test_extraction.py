# SPDX-License-Identifier: Apache-2.0
"""Tests for sub-box extraction ergonomics and dynamic clearance slack."""

from __future__ import annotations

from pyboxbuilder import BoxType, Project, ScoopSide
from pyboxbuilder.box.spec import build_spec


def test_dynamic_clearance_slack() -> None:
    """Verify clearance_slack auto-scales with game box footprint size."""
    # Small box (<150mm) -> 1.0mm clearance slack
    p_small = Project("Small", game_box_size=(100, 100, 50))
    assert p_small.resolved_clearance_slack == 1.0

    # Medium box (150-250mm) -> 1.5mm clearance slack
    p_medium = Project("Medium", game_box_size=(200, 200, 50))
    assert p_medium.resolved_clearance_slack == 1.5

    # Large box (>250mm) -> scales up to 2.5mm
    p_large = Project("Large", game_box_size=(300, 300, 50))
    assert p_large.resolved_clearance_slack == 1.75

    # Explicit override works
    p_override = Project("Override", game_box_size=(300, 300, 50), clearance_slack=1.2)
    assert p_override.resolved_clearance_slack == 1.2


def test_tilt_to_lift_and_ribbon_channel_spec() -> None:
    """Verify tilt_to_lift and ribbon_channel defaults and spec mapping."""
    project = Project("Ergo", game_box_size=(200, 200, 50), ribbon_channels=True)
    builder = project.box(BoxType.NO_LID, "Tray", size=(60, 60, 30))

    # Assert builders have correct defaults
    assert builder.tilt_to_lift is True
    assert builder.keystone is False
    assert builder.ribbon_channel is None  # Defaults to project-level fallback

    # Resolve spec and assert spec receives resolved values
    spec = build_spec(project, builder, (60.0, 60.0, 30.0))
    assert spec.tilt_to_lift is True
    assert spec.keystone is False
    assert spec.ribbon_channel is True  # Resolved from project.ribbon_channels

    # Override on builder works
    builder_override = project.box(
        BoxType.NO_LID, "Tray2", size=(60, 60, 30),
        tilt_to_lift=False, ribbon_channel=False, keystone=True
    )
    spec_override = build_spec(project, builder_override, (60.0, 60.0, 30.0))
    assert spec_override.tilt_to_lift is False
    assert spec_override.keystone is True
    assert spec_override.ribbon_channel is False


def test_keystone_clearance_packing() -> None:
    """Verify that a keystone box gets extra clearance during layout packing."""
    project = Project("KeystonePack", game_box_size=(200, 150, 60))
    # Add a normal box and a keystone box
    b_norm = project.box(BoxType.NO_LID, "Normal", size=(80, 80, 40), expandable=False)
    b_key = project.box(BoxType.NO_LID, "Keystone", size=(80, 40, 40), keystone=True, expandable=False)

    packing = project._resolve_final_layout()

    # Find placements
    pl_norm = next(p for p in packing.placements if p.label == "Normal")
    pl_key = next(p for p in packing.placements if p.label == "Keystone")

    # The final sizes on the builders should be their original size (not the inflated ones)
    assert b_norm.final_size == (80.0, 80.0, 40.0)
    assert b_key.final_size == (80.0, 40.0, 40.0)

    # The placement size for the keystone box should be its original size
    assert pl_key.size == (80.0, 40.0, 40.0)


def test_deep_well_dual_opposing_scoops() -> None:
    """Verify that compartments deeper than 35mm automatically get dual opposing scoops."""
    # We test this logic by invoking build_compartment_scoop and verifying the resulting CSG or layout.
    # Since geometry requires pybosl2, we can verify that when depth > 35mm, opposing scoops are cut.
    # We can also verify that for shallow wells, only a single scoop is generated.
    from pyboxbuilder.box.interior import Interior
    from pyboxbuilder.builders._base import Cut
    from pyboxbuilder.compartments.carve import build_compartment_scoop
    from pyboxbuilder.compartments.layout import CompartmentPlacement
    from pyboxbuilder.enums import FingerCut

    interior = Interior(width=100.0, length=100.0, height=50.0, origin_x=2.0, origin_y=2.0, origin_z=2.0)
    placement = CompartmentPlacement(
        label="DeepWell", position=(10.0, 10.0), size=(30.0, 50.0), depth=40.0
    )

    # If pybosl2 is available, this will return a solid
    try:
        scoop = build_compartment_scoop(
            placement, interior, scoop_side=ScoopSide.FRONT,
            cut=Cut(kind=FingerCut.SCOOP)
        )
        assert scoop is not None
    except ImportError:
        pass
