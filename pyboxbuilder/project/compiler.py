# SPDX-License-Identifier: Apache-2.0
"""LayoutCompiler — resolves layout combinators, compartment sizing, and 3D bin packing (FR-093)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyboxbuilder.builders._base import BoxBuilder
    from pyboxbuilder.layout import Arrangement, Node
    from pyboxbuilder.packing.layout import BoxPacking, Placement
    from pyboxbuilder.project.manifest import ProjectManifest


class LayoutCompiler:
    """Evaluates relative layout combinators, ratios, and 3D bin packing (FR-093)."""

    @staticmethod
    def check_ratios(builder: BoxBuilder) -> None:
        """Reject ratio allocations that cannot fit in the box."""
        w_sum = sum(cb.width_ratio for cb in builder.compartments if cb.width_ratio is not None)
        l_sum = sum(cb.length_ratio for cb in builder.compartments if cb.length_ratio is not None)
        if w_sum > 1.0 + 1e-6:
            raise ValueError(
                f"Box '{builder.label}' compartment width ratios sum to {w_sum:.2f} > 1.0"
            )
        if l_sum > 1.0 + 1e-6:
            raise ValueError(
                f"Box '{builder.label}' compartment length ratios sum to {l_sum:.2f} > 1.0"
            )

    @classmethod
    def min_size(
        cls, manifest: ProjectManifest, builder: BoxBuilder
    ) -> tuple[float, float, float]:
        """Return the smallest this box may be: its explicit size, or its contents."""
        from pyboxbuilder.compartments.layout import compute_min_box_size

        wt = builder.wall_thickness or manifest.wall_thickness
        ft = builder.floor_thickness or manifest.floor_thickness
        lt = builder.lid_thickness or manifest.lid_thickness

        def from_compartments() -> tuple[float, float, float]:
            measured = [
                fp for fp in (cb.min_footprint() for cb in builder.compartments)
                if fp is not None
            ]
            if not measured:
                fills = ", ".join(cb.label for cb in builder.compartments)
                raise ValueError(
                    f"Box '{builder.label}' has no size, and its compartments "
                    f"({fills}) all fill whatever they are given — so there is "
                    f"nothing to derive one from. Give the box a size=(w, l, h), "
                    f"or give a compartment a size=(w, l)."
                )
            bounds = {}
            if manifest.game_box_size is not None:
                bounds = {
                    "max_w": manifest.game_box_size[0] - 2 * wt,
                    "max_l": manifest.game_box_size[1] - 2 * wt,
                }
            return compute_min_box_size(measured, wt, ft, lt, **bounds)

        if builder.size is not None:
            size = list(builder.size)
            if None in size:
                derived = from_compartments()
                size = [axis if axis is not None else derived[i] for i, axis in enumerate(size)]
            return (size[0], size[1], size[2])
        if builder.compartments:
            return from_compartments()
        raise ValueError(
            f"Box '{builder.label}' has no explicit size and no compartments — at least one is required."
        )

    @classmethod
    def standalone_size(
        cls, manifest: ProjectManifest, builder: BoxBuilder
    ) -> tuple[float, float, float]:
        """Resolve a standalone box's size and record it as its final_size."""
        size = cls.min_size(manifest, builder)
        object.__setattr__(builder, "final_size", size)
        return size

    @classmethod
    def resolve_shared_compartments(cls, manifest: ProjectManifest) -> None:
        """Partition each shared compartment group across its boxes (FR-008a)."""
        from pyboxbuilder.builders._base import Cut
        from pyboxbuilder.compartments.builder import CompartmentBuilder
        from pyboxbuilder.compartments.layout import pack_compartments_across_bins
        from pyboxbuilder.enums import FingerCut, ScoopSide

        for box_labels, comps in manifest.shared_groups:
            builders = [
                b for b in (manifest.get_by_label(x) for x in box_labels) if b is not None
            ]
            if len(builders) < 2:
                continue

            bin_sizes = []
            for b in builders:
                wt = b.wall_thickness or manifest.wall_thickness
                if b.size is not None and b.size[0] is not None and b.size[1] is not None:
                    bin_sizes.append((b.size[0] - 2 * wt, b.size[1] - 2 * wt))
                else:
                    container = manifest.game_box_size or (0.0, 0.0, 0.0)
                    bin_sizes.append((container[0] - 2 * wt, container[1] - 2 * wt))

            packed_bins = pack_compartments_across_bins(comps, bin_sizes)
            if not packed_bins:
                raise ValueError(
                    f"Failed to partition shared compartments across boxes: {box_labels}"
                )

            for b, bin_items in zip(builders, packed_bins, strict=False):
                object.__setattr__(
                    b,
                    "compartments",
                    tuple(
                        CompartmentBuilder(
                            label=name,
                            size=(w, length_val),
                            depth=d,
                            cut=Cut(kind=FingerCut.THROUGH_FLOOR, side=ScoopSide.FRONT),
                        )
                        for name, w, length_val, d in bin_items
                    ),
                )

    @classmethod
    def arrange(
        cls,
        manifest: ProjectManifest,
        layout: Node,
        origin: tuple[float, float, float] = (0.0, 0.0, 0.0),
    ) -> Arrangement:
        """Position boxes from a declarative layout tree."""
        from pyboxbuilder.layout import LayoutError
        from pyboxbuilder.layout import arrange as resolve

        sizes = {b.label: cls.min_size(manifest, b) for b in manifest.boxes}
        arrangement = resolve(layout, sizes, origin)

        if manifest.game_box_size is not None and not arrangement.fits(manifest.game_box_size):
            raise LayoutError(
                f"Arrangement is {arrangement.size[0]:.1f} x "
                f"{arrangement.size[1]:.1f} x {arrangement.size[2]:.1f} mm, "
                f"which does not fit the {manifest.game_box_size[0]:.1f} x "
                f"{manifest.game_box_size[1]:.1f} x {manifest.game_box_size[2]:.1f} mm game box."
            )

        by_label = {b.label: b for b in manifest.boxes}
        for label, position in arrangement.positions.items():
            object.__setattr__(by_label[label], "position", position)
        return arrangement

    @classmethod
    def resolve_final_layout(cls, manifest: ProjectManifest) -> BoxPacking:
        """Resolve each box's final size and packed position."""
        from pyboxbuilder.packing.layout import Placement, pack_boxes

        box_data = []
        resolved_min_sizes = {}
        manual_placements = []
        for builder in manifest.boxes:
            size = cls.min_size(manifest, builder)
            resolved_min_sizes[builder.label] = size
            if builder.position is not None:
                manual_placements.append(
                    Placement(label=builder.label, position=builder.position, size=size, rotation=False)
                )
            else:
                pack_size = size
                if builder.keystone:
                    pack_size = (size[0] + 3.0, size[1] + 3.0, size[2])
                box_data.append({
                    "label": builder.label,
                    "size": pack_size,
                    "expandable": builder.expandable,
                    "expandable_width": builder.expandable and builder.expandable_width,
                    "no_rotate": builder.no_rotate,
                })

        slack = manifest.resolved_clearance_slack
        if manifest.game_box_size is None:
            raise ValueError(
                f"Project '{manifest.name}' has no game_box_size, so there is nothing to pack into."
            )
        container = manifest.game_box_size
        packing_container = (
            container[0] - 2 * slack,
            container[1] - 2 * slack,
            container[2] - manifest.board_thickness,
        )
        packing = pack_boxes(packing_container, box_data)

        shifted_placements = []
        for p in packing.placements:
            b = manifest.get_by_label(p.label)
            is_keystone = b.keystone if b else False
            p_size = p.size
            pos_offset_x = 0.0
            pos_offset_y = 0.0
            if is_keystone:
                p_size = (max(0.1, p.size[0] - 3.0), max(0.1, p.size[1] - 3.0), p.size[2])
                pos_offset_x = 1.5
                pos_offset_y = 1.5
            shifted_placements.append(
                Placement(
                    label=p.label,
                    position=(
                        p.position[0] + slack + pos_offset_x,
                        p.position[1] + slack + pos_offset_y,
                        p.position[2],
                    ),
                    size=p_size,
                    rotation=p.rotation,
                )
            )
        shifted_placements.extend(manual_placements)
        packing.placements = shifted_placements

        resolved_sizes = {p.label: p.size for p in packing.placements}
        for builder in manifest.boxes:
            val = resolved_sizes.get(builder.label) or resolved_min_sizes[builder.label]
            object.__setattr__(builder, "final_size", val)

        return packing

    @classmethod
    def spacer_placements(
        cls, manifest: ProjectManifest, packing: BoxPacking
    ) -> list[Placement]:
        """Find leftover space in the packed layout and return spacer placements."""
        from pyboxbuilder.packing.spacer import generate_spacer_placements

        if manifest.game_box_size is None:
            return []
        effective_box = (
            manifest.game_box_size[0],
            manifest.game_box_size[1],
            manifest.game_box_size[2] - manifest.board_thickness,
        )
        return generate_spacer_placements(
            effective_box,
            packing.placements,
            clearance=manifest.resolved_clearance_slack,
            min_dim=manifest.min_spacer_height,
        )

