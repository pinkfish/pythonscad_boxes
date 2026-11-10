# SPDX-License-Identifier: Apache-2.0
"""BoxTypeBase — what every box type implementation inherits.

The hooks below used to be discovered with ``getattr(box, "wall_tops", None)``,
which is a protocol nobody can read off the code and a typo nobody can catch.
They are ordinary methods with ordinary defaults now: a type overrides the ones
it has an opinion about and inherits the rest.

:class:`~pyboxbuilder.box.interior.Interior` is re-exported here because the
types import it alongside this module; it is defined once, in `interior.py`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from pyboxbuilder.box.interior import Interior

if TYPE_CHECKING:
    from pybosl2 import Anchor
    from pybosl2.shapes3d import Bosl2Solid

    from pyboxbuilder.box.features import FingernailCatch
    from pyboxbuilder.box.spec import BoxSpec, ResolvedBoxSpec
    from pyboxbuilder.enums import ScoopSide

__all__ = ["BoxTypeBase", "Interior"]


class BoxTypeBase:
    """Base for every box type implementation.

    A subclass must provide :meth:`build_body`, and :meth:`build_lid` unless it
    is a lidless type. Everything else has a default that suits a plain box
    with a lid sitting on top of it.
    """

    def build_body(self, spec: ResolvedBoxSpec) -> Bosl2Solid:
        """Build the box body geometry.

        Args:
            spec: The box's resolved description.

        Returns:
            The body solid, in the box's own frame with its minimum corner at
            the origin.

        Raises:
            NotImplementedError: If the subclass does not provide one.

        """
        raise NotImplementedError(f"{type(self).__name__} must implement build_body()")

    def build_lid(
        self, spec: BoxSpec, decoration: object = None
    ) -> Bosl2Solid | None:
        """Build the lid geometry, in its seated position.

        Args:
            spec: The box's resolved description.
            decoration: Unused by the geometry — decoration is applied by the
                exporter, once per colour mode.

        Returns:
            The lid solid, or ``None`` for a lidless type.

        """
        return None

    def interior(self, spec: BoxSpec) -> Interior:
        """Return the volume inside this box.

        Args:
            spec: The box's resolved description.

        Returns:
            The interior frame. The default is the spec's own — walls on four
            sides, floor below, lid above — which types that shorten the body
            for their lid override.

        """
        return spec.interior()

    def preferred_scoop_side(self, spec: BoxSpec) -> ScoopSide | None:
        """Which wall this box type wants a finger scoop in.

        A hook rather than a rule, because only the type knows: on a sliding
        box the cut has to be in the wall the lid leaves by — the other three
        carry the lid, two of them holding the grooves it rides in (FR-069).

        Args:
            spec: The box's resolved description.

        Returns:
            A :class:`~pyboxbuilder.enums.ScoopSide`, or ``None`` for "no
            preference", which leaves the compartment's own shape to decide.

        """
        return None

    def lid_rounded_edges(self, spec: BoxSpec) -> list[Anchor]:
        """Which of this box type's lid edges may be rounded.

        Args:
            spec: The box's resolved description.

        Returns:
            A pybosl2 ``edges=`` selector. The default — four vertical corners
            and the top face — suits a lid that sits on top of the box, where
            all of that is on the outside. A lid that slides into the box
            overrides it (FR-044i).

        """
        if spec.path:
            return []
        from pyboxbuilder.rounding import vertical_and_top_edges

        return vertical_and_top_edges()

    def wall_tops(self, spec: BoxSpec) -> dict[ScoopSide, float]:
        """Return the sides whose walls do not end at this box's default top.

        Args:
            spec: The box's resolved description.

        Returns:
            ``{ScoopSide: z}`` for the sides this type raises or lowers; empty
            when all four end level (FR-070/FR-071).

        """
        return {}

    def slide_axis(self, spec: BoxSpec) -> str | None:
        """Return which axis this type's lid slides along, if it slides at all.

        Args:
            spec: The box's resolved description.

        Returns:
            ``"x"`` or ``"y"``, or ``None`` for a lid that lifts off rather
            than sliding. Everything that follows from sliding — the fingernail
            catch below — asks this rather than each type answering it again.

        """
        return None

    def cut_fingernail_catch(self, lid: Bosl2Solid, spec: BoxSpec) -> Bosl2Solid:
        """Sink the dish a nail starts a sliding lid with (FR-002e5).

        A seated sliding lid is a plate flush with the box's top: its only
        exposed surfaces are an end face one lid thickness tall and a smooth
        top, so there is nothing to grip. The dish is what gets it moving. A
        lid that lifts off has its own way open and takes no dish.

        Args:
            lid: The lid to cut.
            spec: The box's resolved description.

        Returns:
            The lid, dished — or unchanged for a non-sliding type, a box that
            declines a catch, or a lid too small to carry one.

        """
        catch = self._fingernail_catch(spec)
        if catch is None:
            return lid

        from pyboxbuilder.box.features import fingernail_dish

        return lid - fingernail_dish(spec, catch)

    def lid_keepouts(self, spec: BoxSpec) -> list[tuple[float, float, float]]:
        """Return circles on the lid that decoration must leave solid.

        A type declares these when its lid carries a feature of its own that a
        pattern would otherwise cut into — a sliding lid's fingernail dish is
        the case (FR-002e5): it is a thinned spot that gets pulled on, so it
        needs whole material around it to pull against. Corner stacking pads
        are likewise kept solid so through-hole lid patterns do not undercut
        the 4 corner locator pyramids/indents.

        Args:
            spec: The box's resolved description.

        Returns:
            ``(x, y, radius)`` in the lid's own frame; empty when the type's
            lid is a plain plate.

        """
        keepouts: list[tuple[float, float, float]] = []
        catch = self._fingernail_catch(spec)
        if catch is not None:
            keepouts.append((catch.centre[0], catch.centre[1], catch.keepout_radius))

        from pyboxbuilder.box.features import (
            _has_active_top_stackable,
            _resolve_corner_pyramid_grids,
        )
        from pyboxbuilder.enums import StackableMode, StackableShape

        if (
            spec.stackable
            in (
                StackableMode.FEET,
                StackableMode.INDENTS,
                StackableMode.PYRAMID,
                StackableMode.PYRAMIDS,
            )
            and spec.stackable_shape is not StackableShape.PATTERN
            and _has_active_top_stackable(spec)
        ):
            import math

            wt = spec.wall_thickness
            foot_size = spec.stackable_foot_size or max(6.0, wt * 2.5)
            foot_inset = (
                spec.stackable_foot_inset if spec.stackable_foot_inset is not None else (wt + 1.0)
            )
            top_pyr = (
                spec.stackable_top_pyramid_count
                if getattr(spec, "stackable_top_pyramid_count", None) is not None
                else getattr(spec, "stackable_pyramid_count", None)
            )
            corner_grids = _resolve_corner_pyramid_grids(
                foot_size,
                spec.stackable_foot_height,
                pyramid_count=top_pyr,
                single_pyramid=(spec.stackable is StackableMode.PYRAMID),
            )
            r_pad = (foot_size * math.sqrt(2.0)) / 2.0 + 0.5
            corners = (
                (foot_inset, foot_inset),
                (spec.width - foot_inset - foot_size, foot_inset),
                (foot_inset, spec.length - foot_inset - foot_size),
                (spec.width - foot_inset - foot_size, spec.length - foot_inset - foot_size),
            )
            for (x0, y0), (nx, ny) in zip(corners, corner_grids, strict=False):
                if nx > 0 and ny > 0:
                    keepouts.append((x0 + foot_size / 2.0, y0 + foot_size / 2.0, r_pad))

        return keepouts

    def _fingernail_catch(self, spec: BoxSpec) -> FingernailCatch | None:
        """Return this type's fingernail dish, or ``None`` if it has none."""
        axis = self.slide_axis(spec)
        if axis is None:
            return None

        from pyboxbuilder.box.features import fingernail_catch

        return fingernail_catch(spec, axis)

    def _reject_stackable(
        self,
        spec: BoxSpec,
        reason: str | None = None,
        *,
        allow_slide_latch: bool = True,
    ) -> None:
        """Raise ValueError if passive top-boss stacking is requested on a flipped-lid box type."""
        if spec.stackable is not None:
            from pyboxbuilder.box.registry import LATCH_STACKABLE_MODES, STACKABLE_BOX_TYPES

            if allow_slide_latch and spec.stackable in LATCH_STACKABLE_MODES:
                return

            allowed = ", ".join(
                f"BoxType.{m.name}"
                for m in sorted(STACKABLE_BOX_TYPES, key=lambda x: x.value)
            )
            why = reason or (
                f"{type(self).__name__} has a lid with downward walls/features that must be "
                "printed upside down on the build plate"
            )
            raise ValueError(
                f"Box '{spec.label}': stackable ({spec.stackable.value!r}) is not supported because "
                f"{why} (use StackableMode.SLIDE_LATCH for side-wall push-up stacking latches). "
                f"Supported passive stackable box types are: {allowed}."
            )

    def interior_mask(self, spec: BoxSpec) -> Bosl2Solid | None:
        """Return the volume inside the box that contents may actually occupy.

        Usually the whole interior, and a type only says otherwise when
        something of its own stands in there. A hinge box is the case that
        needs it: keeping the hinge inside the box's outline puts the barrel
        and its leaf webs in the back of the interior, exactly where a
        compartment would go (FR-002s).

        Args:
            spec: The box's resolved description.

        Returns:
            A solid the contents must stay within, or ``None`` when the whole
            interior is available.

        """
        return None
