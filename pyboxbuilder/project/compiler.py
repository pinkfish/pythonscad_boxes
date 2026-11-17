# SPDX-License-Identifier: Apache-2.0
"""LayoutCompiler — resolves layout combinators, compartment sizing, and 3D bin packing (FR-093)."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pyboxbuilder.builders._base import BoxBuilder
    from pyboxbuilder.compartments.layout import OuterSizerFn
    from pyboxbuilder.layout import Arrangement, Node
    from pyboxbuilder.packing.layout import BoxPacking, Placement
    from pyboxbuilder.project.manifest import ProjectManifest


class LayoutCompiler:
    """Evaluates relative layout combinators, ratios, and 3D bin packing (FR-093)."""

    @staticmethod
    def check_ratios(builder: BoxBuilder) -> None:
        """Reject ratio allocations that cannot fit in the box.

        Supports 1D width-ratio rows, 1D length-ratio stacks, and 2D ``(width_ratio, length_ratio)``
        grids (such as :meth:`~pyboxbuilder.project.core.Project.token_tray`), where cell area
        shares sum to <= 1.0.
        """
        auto_comps = [cb for cb in builder.compartments if cb.position is None]
        if not auto_comps:
            return

        both = [
            cb for cb in auto_comps
            if cb.width_ratio is not None and cb.length_ratio is not None
        ]
        if len(both) > 1 and len(both) == len(auto_comps):
            area_sum = sum(
                (cb.width_ratio or 0.0) * (cb.length_ratio or 0.0) for cb in both
            )
            if area_sum > 1.0 + 1e-6:
                raise ValueError(
                    f"Box '{builder.label}' compartment grid area ratios sum to {area_sum:.2f} > 1.0"
                )
            return

        w_sum = sum(cb.width_ratio for cb in auto_comps if cb.width_ratio is not None)
        l_sum = sum(cb.length_ratio for cb in auto_comps if cb.length_ratio is not None)
        if w_sum > 1.0 + 1e-6:
            raise ValueError(
                f"Box '{builder.label}' compartment width ratios sum to {w_sum:.2f} > 1.0"
            )
        if l_sum > 1.0 + 1e-6:
            raise ValueError(
                f"Box '{builder.label}' compartment length ratios sum to {l_sum:.2f} > 1.0"
            )

    @staticmethod
    def _box_outer_sizer(manifest: ProjectManifest, builder: BoxBuilder) -> OuterSizerFn:
        """Return a BoxType-aware ``(inner_w, inner_l, inner_h) -> (W, L, H)`` sizer."""
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
        from pyboxbuilder.box.spec import UnresolvedBoxSpec

        unresolved = UnresolvedBoxSpec.from_builder(builder, manifest)
        box_cls = BOX_IMPL_REGISTRY.get(builder.box_type)
        if box_cls is None:
            wt = unresolved.wall_thickness
            ft = unresolved.floor_thickness
            lt = unresolved.lid_thickness
            return lambda iw, il, ih: (iw + 2 * wt + 0.5, il + 2 * wt + 0.5, ih + ft + lt + 0.5)
        box_impl = box_cls()
        return lambda iw, il, ih: box_impl.outer_size_for_interior(unresolved, iw, il, ih)

    @staticmethod
    def _exterior_protrusions(
        manifest: ProjectManifest, builder: BoxBuilder
    ) -> tuple[float, float, float, float, float, float]:
        """Return ``(neg_x, pos_x, neg_y, pos_y, neg_z, pos_z)`` exterior protrusions in mm."""
        from pyboxbuilder.box.registry import BOX_IMPL_REGISTRY
        from pyboxbuilder.box.spec import UnresolvedBoxSpec

        unresolved = UnresolvedBoxSpec.from_builder(builder, manifest)
        box_cls = BOX_IMPL_REGISTRY.get(builder.box_type)
        if box_cls is None:
            return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        return box_cls().exterior_protrusions(unresolved)

    @classmethod
    def candidate_sizes(
        cls, manifest: ProjectManifest, builder: BoxBuilder
    ) -> list[tuple[float, float, float]]:
        """Return Pareto-optimal ``(W, L, H)`` envelopes for an unsized compartment box."""
        from pyboxbuilder.compartments.layout import candidate_box_sizes

        if builder.size is not None:
            return [cls.min_size(manifest, builder)]

        if (
            builder.polygon_sides is not None
            and builder.polygon_sides >= 3
            and builder.polygon_apothem is not None
        ):
            return [cls.min_size(manifest, builder)]

        measured = [
            fp for fp in (cb.min_footprint() for cb in builder.compartments)
            if fp is not None
        ]
        if not measured:
            return [cls.min_size(manifest, builder)]

        wt = builder.wall_thickness or manifest.wall_thickness
        ft = builder.floor_thickness or manifest.floor_thickness
        lt = builder.lid_thickness or manifest.lid_thickness
        sizer = cls._box_outer_sizer(manifest, builder)
        no_rot = {
            cb.label
            for cb in builder.compartments
            if cb.no_rotate or cb.derives_size
        }

        max_w: float | None = None
        max_l: float | None = None
        if manifest.game_box_size is not None:
            slack = manifest.resolved_clearance_slack
            base_outer = sizer(0.0, 0.0, 0.0)
            overhead_w = base_outer[0] - 0.5
            overhead_l = base_outer[1] - 0.5
            max_w = max(10.0, manifest.game_box_size[0] - 2 * slack - overhead_w)
            max_l = max(10.0, manifest.game_box_size[1] - 2 * slack - overhead_l)

        return candidate_box_sizes(
            measured,
            wt,
            ft,
            lt,
            max_w=max_w,
            max_l=max_l,
            no_rotate_labels=no_rot,
            outer_sizer=sizer,
        )

    @classmethod
    def min_size(
        cls, manifest: ProjectManifest, builder: BoxBuilder
    ) -> tuple[float, float, float]:
        """Return the smallest compact envelope this box may take."""
        from pyboxbuilder.compartments.layout import compute_min_box_size

        wt = builder.wall_thickness or manifest.wall_thickness
        ft = builder.floor_thickness or manifest.floor_thickness
        lt = builder.lid_thickness or manifest.lid_thickness
        sizer = cls._box_outer_sizer(manifest, builder)

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
            no_rot = {
                cb.label
                for cb in builder.compartments
                if cb.no_rotate or cb.derives_size
            }
            max_w: float | None = None
            max_l: float | None = None
            if manifest.game_box_size is not None:
                slack = manifest.resolved_clearance_slack
                base_outer = sizer(0.0, 0.0, 0.0)
                max_w = max(10.0, manifest.game_box_size[0] - 2 * slack - (base_outer[0] - 0.5))
                max_l = max(10.0, manifest.game_box_size[1] - 2 * slack - (base_outer[1] - 0.5))
            return compute_min_box_size(
                measured,
                wt,
                ft,
                lt,
                max_w=max_w,
                max_l=max_l,
                no_rotate_labels=no_rot,
                outer_sizer=sizer,
            )

        if builder.size is not None:
            size: list[float | None] = list(builder.size)
            if None in size:
                derived = from_compartments()
                resolved_axes = [
                    float(axis) if axis is not None else derived[i]
                    for i, axis in enumerate(size)
                ]
                return (resolved_axes[0], resolved_axes[1], resolved_axes[2])
            return (float(size[0]), float(size[1]), float(size[2]))  # type: ignore[arg-type]

        if (
            builder.polygon_sides is not None
            and builder.polygon_sides >= 3
            and builder.polygon_apothem is not None
        ):
            from pyboxbuilder.box.features import regular_polygon_path

            poly_pts = regular_polygon_path(
                builder.polygon_sides, apothem=builder.polygon_apothem
            )
            pw = max(p[0] for p in poly_pts)
            pl = max(p[1] for p in poly_pts)
            ph = from_compartments()[2] if builder.compartments else sizer(0.0, 0.0, 15.0)[2]
            return (pw, pl, ph)

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
        from pyboxbuilder.compartments.layout import WALL_SPACING_MM, pack_compartments_across_bins
        from pyboxbuilder.enums import FingerCut, ScoopSide

        for box_labels, comps in manifest.shared_groups:
            if not comps:
                continue
            builders = [
                b for b in (manifest.get_by_label(x) for x in box_labels) if b is not None
            ]
            if len(builders) < 2:
                continue

            # Idempotency guard: skip if shared labels were already attached on a prior build()
            shared_names = {c[0] for c in comps}
            if any(cb.label in shared_names for b in builders for cb in b.compartments):
                continue

            n_bins = len(builders)
            total_comp_area = sum(
                (c[1] + WALL_SPACING_MM) * (c[2] + WALL_SPACING_MM) for c in comps
            )
            per_bin_side = max(
                max(max(c[1], c[2]) for c in comps) + 2 * WALL_SPACING_MM,
                math.sqrt(total_comp_area / n_bins) * 1.25,
            )

            bin_sizes: list[tuple[float, float]] = []
            for b in builders:
                wt = b.wall_thickness or manifest.wall_thickness
                if b.size is not None and b.size[0] is not None and b.size[1] is not None:
                    bin_sizes.append((float(b.size[0]) - 2 * wt, float(b.size[1]) - 2 * wt))
                elif manifest.game_box_size is not None:
                    cap_w = min(manifest.game_box_size[0] - 2 * wt, per_bin_side)
                    cap_l = min(manifest.game_box_size[1] - 2 * wt, per_bin_side)
                    bin_sizes.append((cap_w, cap_l))
                else:
                    bin_sizes.append((per_bin_side, per_bin_side))

            packed_bins = pack_compartments_across_bins(comps, bin_sizes)
            if not packed_bins and manifest.game_box_size is not None:
                # Widen unsized bins up to container size if conservative split was too tight
                fallback_sizes = [
                    (float(b.size[0]) - 2 * (b.wall_thickness or manifest.wall_thickness),
                     float(b.size[1]) - 2 * (b.wall_thickness or manifest.wall_thickness))
                    if (b.size is not None and b.size[0] is not None and b.size[1] is not None)
                    else (
                        manifest.game_box_size[0] - 2 * (b.wall_thickness or manifest.wall_thickness),
                        manifest.game_box_size[1] - 2 * (b.wall_thickness or manifest.wall_thickness),
                    )
                    for b in builders
                ]
                packed_bins = pack_compartments_across_bins(comps, fallback_sizes)

            if not packed_bins:
                raise ValueError(
                    f"Failed to partition shared compartments across boxes: {box_labels}"
                )

            for b, bin_items in zip(builders, packed_bins, strict=False):
                added = tuple(
                    CompartmentBuilder(
                        label=name,
                        size=(w, length_val),
                        depth=d,
                        cut=Cut(kind=FingerCut.THROUGH_FLOOR, side=ScoopSide.FRONT),
                    )
                    for name, w, length_val, d in bin_items
                )
                object.__setattr__(b, "compartments", (*b.compartments, *added))

    @classmethod
    def arrange(
        cls,
        manifest: ProjectManifest,
        layout: Node,
        origin: tuple[float, float, float] | None = None,
    ) -> Arrangement:
        """Position boxes from a declarative layout tree."""
        from pyboxbuilder.layout import LayoutError
        from pyboxbuilder.layout import arrange as resolve

        resolved_origin = (
            origin if origin is not None else (0.0, 0.0, manifest.board_z_offset)
        )
        sizes = {b.label: cls.min_size(manifest, b) for b in manifest.boxes}
        arrangement = resolve(layout, sizes, resolved_origin)

        if manifest.game_box_size is not None:
            usable_z_top = (
                manifest.game_box_size[2]
                if manifest.board_on_bottom
                else manifest.game_box_size[2] - manifest.board_thickness
            )
            available = (
                manifest.game_box_size[0] - resolved_origin[0],
                manifest.game_box_size[1] - resolved_origin[1],
                usable_z_top - resolved_origin[2],
            )
            if not arrangement.fits(available):
                raise LayoutError(
                    f"Arrangement is {arrangement.size[0]:.1f} x "
                    f"{arrangement.size[1]:.1f} x {arrangement.size[2]:.1f} mm, "
                    f"which does not fit the {available[0]:.1f} x "
                    f"{available[1]:.1f} x {available[2]:.1f} mm usable game box space."
                )

        by_label = {b.label: b for b in manifest.boxes}
        for label, position in arrangement.positions.items():
            object.__setattr__(by_label[label], "position", position)
        return arrangement

    @classmethod
    def resolve_final_layout(cls, manifest: ProjectManifest) -> BoxPacking:
        """Resolve each box's final size and packed position inside the game box."""
        from pyboxbuilder.packing.layout import BoxPacking, Placement, pack_boxes

        if manifest.game_box_size is None:
            raise ValueError(
                f"Project '{manifest.name}' has no game_box_size, so there is nothing to pack into."
            )

        slack = manifest.resolved_clearance_slack
        z_offset = manifest.board_z_offset
        container = manifest.game_box_size
        packing_container = (
            container[0] - 2 * slack,
            container[1] - 2 * slack,
            container[2] - manifest.board_thickness,
        )

        resolved_min_sizes: dict[str, tuple[float, float, float]] = {}
        protrusions_map: dict[str, tuple[float, float, float, float, float, float]] = {}
        manual_placements: list[Placement] = []
        unplaced_builders: list[BoxBuilder] = []

        for builder in manifest.boxes:
            size = cls.min_size(manifest, builder)
            resolved_min_sizes[builder.label] = size
            if builder.position is not None:
                manual_placements.append(
                    Placement(
                        label=builder.label,
                        position=builder.position,
                        size=size,
                        rotation=False,
                    )
                )
            else:
                protrusions_map[builder.label] = cls._exterior_protrusions(manifest, builder)
                unplaced_builders.append(builder)

        if not unplaced_builders:
            packing = BoxPacking(container_size=packing_container, placements=list(manual_placements))
            for builder in manifest.boxes:
                object.__setattr__(builder, "final_size", resolved_min_sizes[builder.label])
            cls._apply_stacking_order_configs(manifest, packing.placements)
            return packing

        def pack_envelope(
            label: str, raw_size: tuple[float, float, float], is_keystone: bool
        ) -> tuple[float, float, float]:
            nx, px, ny, py, nz, pz = protrusions_map.get(label, (0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
            kw = 3.0 if is_keystone else 0.0
            return (
                raw_size[0] + nx + px + kw,
                raw_size[1] + ny + py + kw,
                raw_size[2] + nz + pz,
            )

        # Group explicit `project.stack_order(...)` chains whose members are unpositioned
        # and share a matching footprint so the packer keeps them stacked in exact order.
        unplaced_by_label = {b.label: b for b in unplaced_builders}
        grouped_labels: set[str] = set()
        box_data: list[dict[str, Any]] = []

        for chain in manifest.stack_groups:
            if any(lbl not in unplaced_by_label or lbl in grouped_labels for lbl in chain):
                continue
            members = [unplaced_by_label[lbl] for lbl in chain]
            envs = [
                pack_envelope(m.label, resolved_min_sizes[m.label], m.keystone)
                for m in members
            ]
            w0, l0, _ = envs[0]
            if all(abs(e[0] - w0) <= 0.1 and abs(e[1] - l0) <= 0.1 for e in envs):
                grouped_labels.update(chain)
                box_data.append({
                    "label": "+".join(chain),
                    "size": (w0, l0, sum(e[2] for e in envs)),
                    "expandable": all(m.expandable for m in members),
                    "expandable_width": all(m.expandable and m.expandable_width for m in members),
                    "expandable_length": all(m.expandable and m.expandable_length for m in members),
                    "no_rotate": any(m.no_rotate for m in members),
                    "stack_members": [
                        (m.label, env) for m, env in zip(members, envs, strict=True)
                    ],
                })

        for builder in unplaced_builders:
            if builder.label in grouped_labels:
                continue
            base_size = resolved_min_sizes[builder.label]
            p_env = pack_envelope(builder.label, base_size, builder.keystone)
            opts: list[tuple[float, float, float]] = []
            if builder.size is None and len(builder.compartments) >= 2:
                cands = cls.candidate_sizes(manifest, builder)
                if len(cands) > 1:
                    opts = [pack_envelope(builder.label, c, builder.keystone) for c in cands]

            box_data.append({
                "label": builder.label,
                "size": p_env,
                "size_options": opts,
                "expandable": builder.expandable,
                "expandable_width": builder.expandable and builder.expandable_width,
                "expandable_length": builder.expandable and builder.expandable_length,
                "no_rotate": builder.no_rotate,
            })

        # Convert pinned manual placements into packing-frame obstacles so auto-packed
        # boxes pack around (and on top of) pinned boxes without colliding!
        obstacles = [
            (
                mp.position[0] - slack,
                mp.position[1] - slack,
                mp.position[2] - z_offset,
                mp.size[0],
                mp.size[1],
                mp.size[2],
            )
            for mp in manual_placements
        ]

        packing = pack_boxes(
            packing_container,
            box_data,
            gap_threshold=manifest.gap_threshold,
            min_spacer_dim=manifest.min_spacer_dim,
            obstacles=obstacles,
        )

        shifted_placements: list[Placement] = []
        local_final_sizes: dict[str, tuple[float, float, float]] = {}

        for p in packing.placements:
            b = manifest.get_by_label(p.label)
            is_keystone = b.keystone if b else False
            nx, px, ny, py, nz, pz = protrusions_map.get(
                p.label, (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
            )
            kw = 3.0 if is_keystone else 0.0
            k_off = 1.5 if is_keystone else 0.0

            if p.rotation:
                # Rotated +90 deg around Z: local +X maps to container +Y, local +Y maps to container -X
                eff_container_w = max(0.1, p.size[0] - ny - py - kw)
                eff_container_l = max(0.1, p.size[1] - nx - px - kw)
                pos_off_x = py + k_off
                pos_off_y = nx + k_off
                local_final_sizes[p.label] = (
                    eff_container_l,
                    eff_container_w,
                    max(0.1, p.size[2] - nz - pz),
                )
            else:
                eff_container_w = max(0.1, p.size[0] - nx - px - kw)
                eff_container_l = max(0.1, p.size[1] - ny - py - kw)
                pos_off_x = nx + k_off
                pos_off_y = ny + k_off
                local_final_sizes[p.label] = (
                    eff_container_w,
                    eff_container_l,
                    max(0.1, p.size[2] - nz - pz),
                )

            shifted_placements.append(
                Placement(
                    label=p.label,
                    position=(
                        p.position[0] + slack + pos_off_x,
                        p.position[1] + slack + pos_off_y,
                        p.position[2] + z_offset + nz,
                    ),
                    size=(eff_container_w, eff_container_l, max(0.1, p.size[2] - nz - pz)),
                    rotation=p.rotation,
                )
            )

        shifted_placements.extend(manual_placements)
        packing.placements = shifted_placements

        for builder in manifest.boxes:
            val = local_final_sizes.get(builder.label) or resolved_min_sizes[builder.label]
            object.__setattr__(builder, "final_size", val)

        cls._apply_stacking_order_configs(manifest, packing.placements)
        return packing

    @classmethod
    def _apply_stacking_order_configs(
        cls, manifest: ProjectManifest, placements: list[Placement]
    ) -> None:
        """Suppress top/bottom stack ends and assign keyed pyramid configs to vertical stacks."""
        from pyboxbuilder.box.features import stacking_order_pyramid_config
        from pyboxbuilder.enums import StackableMode

        by_footprint: dict[tuple[float, float, float, float], list[tuple[float, BoxBuilder]]] = {}
        stackable_placements: list[tuple[Placement, BoxBuilder]] = []

        for p in placements:
            b = manifest.get_by_label(p.label)
            if b is None or b.stackable is None:
                continue
            stackable_placements.append((p, b))
            key = (
                round(p.position[0], 1),
                round(p.position[1], 1),
                round(p.size[0], 1),
                round(p.size[1], 1),
            )
            by_footprint.setdefault(key, []).append((p.position[2], b))

        handled_in_column: set[str] = set()
        for items in by_footprint.values():
            if len(items) < 2:
                continue
            ordered = [b for _z, b in sorted(items, key=lambda x: x[0])]
            for b in ordered:
                handled_in_column.add(b.label)

            object.__setattr__(ordered[0], "stackable_bottom", False)
            object.__setattr__(ordered[-1], "stackable_top", False)
            for idx in range(len(ordered) - 1):
                object.__setattr__(ordered[idx], "stackable_top", True)
                object.__setattr__(ordered[idx + 1], "stackable_bottom", True)

            if all(b.stackable is StackableMode.PYRAMIDS for b in ordered) and not any(
                b.stackable_top_pyramid_count is not None
                or b.stackable_bottom_pyramid_count is not None
                for b in ordered
            ):
                for idx in range(len(ordered) - 1):
                    cfg = stacking_order_pyramid_config(idx)
                    object.__setattr__(ordered[idx], "stackable_top_pyramid_count", cfg)
                    object.__setattr__(ordered[idx + 1], "stackable_bottom_pyramid_count", cfg)

        # In enclosed game-box mode, also suppress top/bottom bosses on solo or bridged
        # stackable boxes where nothing stackable sits above/below them!
        if manifest.game_box_size is not None:
            for p, b in stackable_placements:
                if b.label in handled_in_column:
                    continue
                px, py, pz = p.position
                pw, pl, ph = p.size
                has_below = any(
                    op is not p
                    and abs((op.position[2] + op.size[2]) - pz) <= 0.5
                    and px < op.position[0] + op.size[0] - 0.5
                    and px + pw > op.position[0] + 0.5
                    and py < op.position[1] + op.size[1] - 0.5
                    and py + pl > op.position[1] + 0.5
                    for op, _ob in stackable_placements
                )
                has_above = any(
                    op is not p
                    and abs(op.position[2] - (pz + ph)) <= 0.5
                    and px < op.position[0] + op.size[0] - 0.5
                    and px + pw > op.position[0] + 0.5
                    and py < op.position[1] + op.size[1] - 0.5
                    and py + pl > op.position[1] + 0.5
                    for op, _ob in stackable_placements
                )
                object.__setattr__(b, "stackable_bottom", has_below)
                object.__setattr__(b, "stackable_top", has_above)

    @staticmethod
    def _shift_placements_z(
        placements: list[Placement], dz: float
    ) -> list[Placement]:
        """Translate placements along Z when shifting between box and effective board frames."""
        if not dz:
            return placements
        from pyboxbuilder.packing.layout import Placement

        return [
            Placement(
                label=p.label,
                position=(p.position[0], p.position[1], p.position[2] + dz),
                size=p.size,
                rotation=p.rotation,
                path=p.path,
            )
            for p in placements
        ]

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
        z_offset = manifest.board_z_offset
        spacers = generate_spacer_placements(
            effective_box,
            cls._shift_placements_z(packing.placements, -z_offset),
            clearance=manifest.resolved_clearance_slack,
            min_dim=manifest.min_spacer_height,
        )
        return cls._shift_placements_z(spacers, z_offset)
