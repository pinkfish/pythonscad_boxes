# SPDX-License-Identifier: Apache-2.0
"""SlidingBox — sliding lid box type implementation."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING

from pyboxbuilder.box.spec import BoxSpec

if TYPE_CHECKING:
    from pybosl2 import Anchor
    from pybosl2.shapes3d import Bosl2Solid

    from pyboxbuilder.enums import ScoopSide

from pyboxbuilder.box.base import BoxTypeBase, Interior


class SlidingBox(BoxTypeBase):
    """Sliding lid box type.

    Produces a box body with dovetail grooves on two walls where the lid
    slides in, and a sliding lid that mates with those grooves.
    """

    def interior(self, spec: BoxSpec) -> Interior:
        """Return the frame the box's contents may occupy."""
        wt = spec.wall_thickness
        ft = spec.floor_thickness
        lt = spec.lid_thickness
        return Interior(
            width=spec.width - 2 * wt,
            length=spec.length - 2 * wt,
            height=spec.height - lt - ft,
            origin_x=wt,
            origin_y=wt,
            origin_z=ft,
        )

    def _build_shell(self, spec: BoxSpec) -> Bosl2Solid:
        """Build the hollow box body shell."""
        from pyboxbuilder.box.shell import build_shell, sliding_rim_rounding

        # The lid lies down in the channel, so the rails' top edges are on the
        # outside of the closed box and get rounded (FR-043f1).
        if spec.rim_rounding is None:
            spec = replace(spec, rim_rounding=sliding_rim_rounding(spec))
        return build_shell(spec)

    def slides_along_length(self, spec: BoxSpec) -> bool:
        """Whether the lid slides along Y rather than X."""
        if spec.lid_slide_axis == "x":
            return False
        if spec.lid_slide_axis == "y":
            return True
        return True

    def open_end_side(self, spec: BoxSpec) -> ScoopSide:
        """Return the wall the lid slides out through.

        Args:
            spec: Needs `width` and `length`.

        Returns:
            `BACK` when the lid slides along the length, else `RIGHT`.

        """
        from pyboxbuilder.enums import ScoopSide

        return ScoopSide.BACK if self.slides_along_length(spec) else ScoopSide.RIGHT

    def wall_tops(self, spec: BoxSpec) -> dict[ScoopSide, float]:
        """Where each wall ends, which is not the same height all round.

        The channel is cut out of the top band across the whole box and runs
        out through the exit wall, so the entry side wall stops a lid
        thickness below the box's top (its material is gone). The other three
        sides go all the way to the top of the box itself.

        Args:
            spec: Needs `height`; reads `lid_thickness`.

        Returns:
            ``{ScoopSide: z}`` for all four sides.

        """
        from pyboxbuilder.enums import ScoopSide

        open_side = self.open_end_side(spec)
        top = spec.height - (spec.lid_thickness or 0.0)
        return {side: (top if side == open_side else spec.height) for side in ScoopSide}

    def preferred_scoop_side(self, spec: BoxSpec) -> ScoopSide:
        """Put a finger scoop in the wall the lid comes out of.

        On a sliding box the cards leave the same way the lid does, so the cut
        belongs in that wall — and only that wall will do. The other three
        carry the lid: two hold the grooves it rides in, and cutting a scoop
        into a groove takes away the bearing that keeps the lid straight.

        Args:
            spec: Needs `width` and `length`.

        Returns:
            The open end's side.

        """
        return self.open_end_side(spec)

    def lid_rounded_edges(self, spec: BoxSpec) -> list[Anchor]:
        """Which of the lid's edges may be rounded.

        Only the end that ends up **outside** the box: its top edge and its two
        vertical corners. The other three sides of the plate live in the
        channel — two in the grooves, one against the stop — and rounding them
        would round away the very surfaces that support and locate the lid.

        Args:
            spec: Needs `width` and `length`.

        Returns:
            A pybosl2 ``edges=`` selector for the exposed end.

        """
        from pybosl2 import Anchor

        if self.slides_along_length(spec):
            return [Anchor.TOP_BACK, Anchor.BACK_LEFT, Anchor.BACK_RIGHT]
        return [Anchor.TOP_RIGHT, Anchor.FRONT_RIGHT, Anchor.BACK_RIGHT]

    def _along_axis(self, spec: BoxSpec) -> str:
        """Which axis the lid slides along, for the dovetail geometry.

        Args:
            spec: Needs `width` and `length`.

        Returns:
            ``"y"`` when the lid slides along the length, else ``"x"``.

        """
        return "y" if self.slides_along_length(spec) else "x"

    def _cut_lid_channel(
        self, body: Bosl2Solid, spec: BoxSpec
    ) -> Bosl2Solid:
        """Cut the dovetailed slot the lid slides along, open at one end.

        One subtraction does both halves of the job, because they are the same
        slot: it bites the dovetail into each side wall to make the grooves,
        and it runs out through the far end wall so the lid has somewhere to
        enter. Cutting only the grooves leaves a box with a solid wall across
        the front of its own track — a lid that can be dropped in but never
        slid, which is the entire point of the type.

        The near end keeps its wall: that is the stop the lid closes against.

        Args:
            body: The box body to cut.
            spec: Needs `width`, `length`, `height`, `wall_thickness`,
                `lid_thickness`.

        Returns:
            The body with the dovetail channel cut.

        """
        from pyboxbuilder.box.features import dovetail_track

        return body - dovetail_track(spec, self._along_axis(spec)).body

    def _catch_radius(self, spec: BoxSpec) -> float:
        """Return the bump catch's radius, or 0 for no catch (FR-002e3).

        Both sliding box and sliding-catch box carry this catch by default,
        with a default radius of 1.0mm, so the lid does not fall out on its own.
        Setting `catch_radius` to 0 turns it off.

        Args:
            spec: Reads `catch_radius`.

        Returns:
            The bump radius in mm; ``0`` for no catch.

        """
        return 1.0 if spec.catch_radius is None else spec.catch_radius

    def build_body(self, spec: BoxSpec) -> Bosl2Solid:
        """Build the complete box body with dovetail grooves."""
        body = self._build_shell(spec)
        if spec.dovetail:
            body = self._cut_lid_channel(body, spec)
        radius = self._catch_radius(spec)
        if radius > 0:
            from pyboxbuilder.box.features import sliding_catch

            body = body - sliding_catch(spec, radius, self._along_axis(spec)).body
        return body

    def build_lid(self, spec: BoxSpec, decoration: object = None) -> Bosl2Solid:
        """Build the sliding lid — a dovetailed plate, chamfered at its leading end."""
        from pyboxbuilder.box.features import dovetail_track

        closure = dovetail_track(spec, self._along_axis(spec))
        assert closure.lid is not None
        lid = closure.lid
        radius = self._catch_radius(spec)
        if radius > 0:
            from pyboxbuilder.box.features import sliding_catch

            lid = lid | sliding_catch(spec, radius, self._along_axis(spec)).lid
        return self.cut_fingernail_catch(lid, spec)

    def slide_axis(self, spec: BoxSpec) -> str:
        """Return the axis this lid slides along — the long one (FR-002b)."""
        return self._along_axis(spec)
