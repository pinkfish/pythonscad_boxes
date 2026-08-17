# SPDX-License-Identifier: Apache-2.0
"""BoxBuilder base class and registry stub."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, ClassVar

from pybosl2 import Color

from pyboxbuilder.enums import BoxType, FingerCut, MagnetType, ScoopSide, StackableMode

if TYPE_CHECKING:
    from pyboxbuilder.lid.builder import LidBuilder
    from pyboxbuilder.compartments.builder import CompartmentBuilder
    from pyboxbuilder.compartments.element import CompartmentElement



@dataclass(frozen=True)
class BoxBuilder:
    """Base builder for all box types.

    Carries common fields shared by every box type. Subclassed by
    type-specific builders that add their own typed fields.
    """

    box_type: ClassVar[BoxType]
    label: str
    """Box identifier, used for file naming."""
    box_id: str | None = None
    """Unique instance identifier; defaults to label."""
    size: tuple[float, float, float] | None = None
    """Box dimensions [W, L, H] in mm. None = auto-compute from compartments."""
    position: tuple[float, float, float] | None = None
    """Manual packing position override [X, Y, Z] in mm."""
    stackable: StackableMode | None = None
    """Interlocking rim mode for no-lid boxes; ``None`` means not stackable."""
    stackable_thickness: float | None = None
    """Interlocking rim thickness for stackable boxes."""
    magnet_type: MagnetType | None = None
    """Magnet slot shape; ``None`` or :attr:`MagnetType.NONE` means no magnets."""
    magnet_size: tuple[float, float, float] | None = None
    """Magnet slot dimensions [diameter_or_width, length, depth]."""
    final_size: tuple[float, float, float] | None = None
    """Resolved size after packing; set-once frozen during export."""
    expandable: bool = True
    """Box can be auto-sized larger during packing."""
    expandable_width: bool = True
    """Width axis can expand."""
    expandable_length: bool = True
    """Length axis can expand."""
    no_rotate: bool = False
    """Prevent 3D packer from rotating the box (keeps compartment layout directional)."""
    wall_thickness: float | None = None
    """Per-box wall thickness override; None uses project default."""
    floor_thickness: float | None = None
    """Per-box floor thickness override."""
    lid_thickness: float | None = None
    """Per-box lid thickness override."""
    rounding: float | None = None
    """Edge radius for this box's exposed edges; None uses the project default."""
    inner_rounding: float | None = None
    """Edge radius where a partial lid grips this body; None uses half the outer radius."""
    lid: LidBuilder | None = None
    """Lid decoration configuration."""
    color: Color | None = None
    """Body colour, as a :class:`pybosl2.Color` (webcolor names welcome).

    Used as the box's material colour on export and as its colour in
    :meth:`Project.show`. When unset, a preview assigns a stable pseudo-random
    hue derived from the label so adjacent boxes stay distinguishable; that
    fallback is view-time only and never reaches the exported geometry.
    """
    finger_holes: tuple[FingerHoleBuilder, ...] = ()
    """Finger holes on box exterior walls."""
    auto_finger_holes: bool = True
    """Let a lidless box cut its own default finger holes (FR-047).

    Only the no-lid and path types read this: when there are no explicit
    ``finger_holes``, they add a finger hole to each wall of their longer side,
    sized after the original. ``False`` opts out and leaves the walls plain.
    Lidded types ignore it.
    """
    compartments: tuple[CompartmentBuilder, ...] = ()
    """Interior compartments."""

    def __post_init__(self) -> None:
        """Reject bare strings where the API takes an enum.

        Type selections are enums throughout, so a stray ``"inside"`` or
        ``"round"`` is a mistake worth naming at construction rather than a
        silent no-match deep inside the geometry code.

        Raises:
            TypeError: If ``stackable`` or ``magnet_type`` is not its enum.
        """
        for name, enum_cls in (("stackable", StackableMode), ("magnet_type", MagnetType)):
            value = getattr(self, name)
            if value is not None and not isinstance(value, enum_cls):
                members = ", ".join(f"{enum_cls.__name__}.{m.name}" for m in enum_cls)
                raise TypeError(
                    f"Box '{self.label}': {name} must be a {enum_cls.__name__} "
                    f"({members}) or None; got {value!r}"
                )

    def compartment(
        self,
        label: str,
        *,
        size: tuple[float, float] | None = None,
        width_ratio: float | None = None,
        length_ratio: float | None = None,
        depth: float | None = None,
        rounded_corners: float = 0.0,
        cut: "Cut | FingerCut | None" = None,
        no_rotate: bool = False,
        shape_file: str | None = None,
        position: tuple[float, float] | None = None,
        elements: tuple[CompartmentElement, ...] = (),
        element_margin: float = 0.0,
    ) -> CompartmentBuilder:
        """Add a compartment to this box.

        Args:
            cut: How its contents come out — a :class:`FingerCut` for "this
                kind, everything else derived", a :class:`Cut` when something
                needs saying, or ``None`` for no cut at all (FR-006).
        """
        from pyboxbuilder.compartments.builder import CompartmentBuilder

        cb = CompartmentBuilder(
            label=label,
            size=size,
            width_ratio=width_ratio,
            length_ratio=length_ratio,
            depth=depth,
            rounded_corners=rounded_corners,
            cut=Cut.of(cut),
            no_rotate=no_rotate,
            shape_file=shape_file,
            position=position,
            elements=elements,
            element_margin=element_margin,
        )
        object.__setattr__(self, "compartments", self.compartments + (cb,))
        return cb

    def finger_hole(
        self,
        side: "ScoopSide",
        *,
        width: float = 28.0,
        depth: float | None = None,
        offset: float = 0.0,
        base_radius: float | None = None,
        mouth_flare: float | None = None,
        roll_rise: float | None = None,
        face_fillet: float | None = None,
        radius: float | None = None,
    ) -> "FingerHoleBuilder":
        """Add a finger hole to one of this box's exterior walls (FR-006).

        The hole hangs from the top of the **interior** (FR-064) — not from
        the outer rim, which on a lidded box is a lid band above it — so a
        finger reaches in over the wall rather than through its middle. It is
        cut with the same smoothing as a compartment scoop: a mouth rolled
        into the wall's top and a fillet where it emerges on each face.

        Args:
            side: Which exterior wall to cut.
            width: The cut's full width in mm; 28mm is adult fingertip sizing.
            base_radius: How the base curves into the sides. ``None`` takes
                **half the width**, which makes the base one round curve rather
                than a flat pan (FR-054); it is independent of the width
                (FR-055), so a narrow grip can still have a fully round base
                and a wide one a tight-cornered base.
            mouth_flare: How far the mouth rolls out at the rim; ``None`` uses
                3mm.
            face_fillet: The roundover where the cut emerges on a face;
                ``None`` uses ``wall_thickness / 2``, the largest the wall has
                room for.
            radius: **Deprecated.** The same measurement as `width`, halved.
                Two names for one dimension, one of them half the other, is a
                foot-gun in a signature this size; `width` is what the
                requirements state (FR-051). Passing it still works and warns.
            depth: How far the cut reaches below the wall's top, measured to
                the deepest point of the material it removes (FR-006b).
                ``None`` uses the radius. Capped at the interior depth so the
                cut cannot open the box's base.
            offset: Shift along the wall from its midpoint, in mm.
            roll_rise: How far the mouth roll reaches down. ``None`` derives it
                from the flare. The fourth of the numbers that define the
                outline (FR-051): width and gentleness are separate, so a
                shallow wall can take a gentler curve without a wider mouth.

        Returns:
            The :class:`FingerHoleBuilder` that was added, so it can be
            inspected; it is already registered on the box.

        Raises:
            TypeError: If ``side`` is not a :class:`ScoopSide`.
            ValueError: If ``radius`` or ``depth`` is not positive.
        """
        if radius is not None:
            import warnings

            warnings.warn(
                "finger_hole(radius=...) is deprecated; pass width= instead, "
                "which is twice it and is what the requirements state.",
                DeprecationWarning, stacklevel=2,
            )
            width = radius * 2.0
        hole = FingerHoleBuilder(
            side=side,
            radius=width / 2.0,
            bottom_radius=base_radius,
            depth=depth,
            offset=offset,
            rounding_radius=mouth_flare,
            rounding_edge=face_fillet,
            roll_rise=roll_rise,
        )
        object.__setattr__(self, "finger_holes", self.finger_holes + (hole,))
        return hole


@dataclass(frozen=True)
class Cut:
    """How a compartment gets its contents out (FR-006, FR-060).

    One record rather than a flag to turn a cut on, a second to choose which
    kind, a third for the side and half a dozen loose measurements. Those were
    four separate decisions spread across a fifteen-parameter call, and two of
    them meant the same thing: `finger_scoop=True, finger_cut=SCOOP` said
    "cut one" twice.

    Every measurement is ``None`` for "derive it", because the right value
    depends on the well's own proportions and on the box's wall — which the
    builder knows and the person describing a game does not (FR-000, FR-059).

    Typical use is the shorthand::

        box.compartment("Cards", size=..., depth=..., cut=FingerCut.THROUGH_FLOOR)

    and the record itself only when something needs saying::

        cut=Cut.scoop(side=ScoopSide.LEFT, width=30)
    """

    kind: FingerCut = FingerCut.THROUGH_FLOOR
    """Which cut. A hole through the base for a stack, a side dip for loose
    pieces (:class:`FingerCut`)."""
    side: ScoopSide | None = None
    """Which wall it goes in. ``None`` derives it — the shorter wall, or a
    sliding lid's exit wall (FR-068/b6)."""
    width: float | None = None
    """How wide the cut is. ``None`` uses a fingertip."""
    depth: float | None = None
    """How far down it reaches, measured to the deepest point of the material
    it removes (FR-006b). ``None`` runs it to the well's floor."""
    offset: float = 0.0
    """Shift along the wall from its midpoint, in mm."""
    base_radius: float | None = None
    """How the base curves into the sides; ``None`` derives it (FR-054)."""
    mouth_flare: float | None = None
    """How far the mouth rolls out at the rim; ``None`` derives it."""
    roll_rise: float | None = None
    """How far that roll reaches down — its gentleness (FR-057)."""
    face_fillet: float | None = None
    """The roundover where the cut emerges on a face; ``None`` uses half the
    wall."""

    @classmethod
    def scoop(cls, **fields) -> "Cut":
        """A dip in the side of the well, leaving its base solid."""
        return cls(kind=FingerCut.SCOOP, **fields)

    @classmethod
    def through_floor(cls, **fields) -> "Cut":
        """A hole through the box's base, for a well something is stacked in."""
        return cls(kind=FingerCut.THROUGH_FLOOR, **fields)

    @classmethod
    def of(cls, value: "Cut | FingerCut | None") -> "Cut | None":
        """Normalise what a caller passed as `cut=` into a record or ``None``.

        The enum on its own is the common case and reads better at a call site
        than a constructor does, so it is accepted as shorthand for "this kind,
        everything else derived".
        """
        if value is None or isinstance(value, cls):
            return value
        if isinstance(value, FingerCut):
            return cls(kind=value)
        raise TypeError(
            f"cut must be a Cut, a FingerCut or None; got {value!r}"
        )


@dataclass(frozen=True)
class FingerHoleBuilder:
    """A finger hole on a box's exterior wall (FR-006).

    Cut with the same builder as a compartment's wall scoop, so it gets the
    same mouth flare and face fillets: see
    :func:`pyboxbuilder.compartments.finger_cuts.build_wall_scoop`.
    """

    side: ScoopSide
    """Which exterior wall the hole is cut through."""
    radius: float = 14.0
    """Throat half-width in mm — adult fingertip sizing by default.

    `BoxBuilder.finger_hole` also takes a `width`, which is twice this and the
    way the requirement states it (FR-051); they are the same number.
    """
    bottom_radius: float | None = None
    """How the base curves into the sides; ``None`` uses half the width.

    Independent of the width (FR-055), and **kept** rather than shrunk to fit
    (FR-054): where the depth cannot hold the circle the mouth's roll gives
    first, and the straight run between the two circles absorbs the rest.
    """
    depth: float | None = None
    """How far down from the interior's top the cut reaches.

    ``None`` uses the radius, which is how the original sizes it: the height of
    a finger cut follows the finger, not the wall. A fixed default made every
    hole a shallow nick regardless of how big a finger it was cut for.
    """
    offset: float = 0.0
    """Shift along the wall from its midpoint, in mm."""
    rounding_radius: float | None = None
    """Mouth flare where the cut meets the rim; ``None`` uses the default 3mm."""
    rounding_edge: float | None = None
    """Fillet where the cut emerges on a face; ``None`` uses ``wall_thickness / 2``."""
    roll_rise: float | None = None
    """How far the mouth roll reaches down; ``None`` derives it from the flare.

    The gentleness of the curve, as against `rounding_radius`'s width of it
    (FR-051/FR-057). Settable because on a shallow wall the rise is the only
    one of the two that can give: there is height to spare for the curve and no
    width to spare for the mouth."""

    def __post_init__(self) -> None:
        """Validate the hole.

        Raises:
            TypeError: If ``side`` is not a :class:`ScoopSide` — a bare string
                would silently match no wall.
            ValueError: If ``radius`` or ``depth`` is not positive.
        """
        if not isinstance(self.side, ScoopSide):
            sides = ", ".join(f"ScoopSide.{m.name}" for m in ScoopSide)
            raise TypeError(f"finger hole side must be a ScoopSide ({sides}); got {self.side!r}")
        if self.radius <= 0:
            raise ValueError(f"finger hole radius must be > 0; got {self.radius}")
        if self.depth is not None and self.depth <= 0:
            raise ValueError(f"finger hole depth must be > 0; got {self.depth}")
