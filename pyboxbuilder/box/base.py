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
    from pybosl2.shapes3d import Bosl2Solid

    from pyboxbuilder.box.spec import BoxSpec
    from pyboxbuilder.enums import ScoopSide

__all__ = ["BoxTypeBase", "Interior"]


class BoxTypeBase:
    """Base for every box type implementation.

    A subclass must provide :meth:`build_body`, and :meth:`build_lid` unless it
    is a lidless type. Everything else has a default that suits a plain box
    with a lid sitting on top of it.
    """

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
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

    def lid_rounded_edges(self, spec: BoxSpec) -> list:
        """Which of this box type's lid edges may be rounded.

        Args:
            spec: The box's resolved description.

        Returns:
            A pybosl2 ``edges=`` selector. The default — four vertical corners
            and the top face — suits a lid that sits on top of the box, where
            all of that is on the outside. A lid that slides into the box
            overrides it (FR-044i).

        """
        from pyboxbuilder.rounding import vertical_and_top_edges

        return vertical_and_top_edges()

    def wall_tops(self, spec: BoxSpec) -> dict:
        """Return the sides whose walls do not end at this box's default top.

        Args:
            spec: The box's resolved description.

        Returns:
            ``{ScoopSide: z}`` for the sides this type raises or lowers; empty
            when all four end level (FR-070/FR-071).

        """
        return {}

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
