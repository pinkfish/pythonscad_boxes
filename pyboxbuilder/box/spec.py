# SPDX-License-Identifier: Apache-2.0
"""BoxSpec — the one description a box type is built from.

Every geometric default in the library is declared **once**, here, as a field
default. Nothing downstream restates one: a function that needs the wall
thickness reads ``spec.wall_thickness`` and gets the default from this file,
rather than carrying a fallback of its own — so there is no second copy to fall
out of step with the first.

This replaces a plain ``dict`` that was assembled in two places with two
different exclusion lists, and whose defaults were restated at 170 call sites —
``wall_thickness`` alone at 36 of them. That is how a hinge came to be built
with five knuckles by the geometry and three by the builder that configured it.
"""

from __future__ import annotations

from dataclasses import dataclass, field, fields, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pyboxbuilder.enums import MagnetType, ScoopSide, StackableMode

if TYPE_CHECKING:
    from pyboxbuilder.box.interior import Interior
    from pyboxbuilder.builders._base import BoxBuilder
    from pyboxbuilder.project import Project

WIGGLE_MM = 0.2
"""Default clearance between two printed parts that have to fit together."""


@dataclass(frozen=True)
class BoxSpec:
    """Everything a box type needs to build its body and lid.

    Frozen, so a type cannot reach back and change the description it was
    handed. Derive a variant with :func:`dataclasses.replace`::

        body_spec = replace(spec, height=spec.height - spec.lid_thickness)
    """

    # ── Identity and envelope ────────────────────────────────────────────
    width: float
    """Outer width (X) in mm."""
    length: float
    """Outer length (Y) in mm."""
    height: float
    """Outer height (Z) in mm."""
    label: str = "box"
    """The box's name, used for file naming and in error messages."""

    # ── Material thicknesses ─────────────────────────────────────────────
    wall_thickness: float = 2.0
    """Side wall thickness in mm."""
    floor_thickness: float = 1.6
    """Base thickness in mm."""
    lid_thickness: float = 2.0
    """Lid plate thickness in mm; ``0`` for a lidless type."""

    # ── Interior ─────────────────────────────────────────────────────────
    hollow: bool = True
    """Hollow the whole interior. ``False`` where compartments define the
    cavities instead, or for a solid block."""
    path: tuple[tuple[float, float], ...] = ()
    """Closed polygon footprint for a path box; empty means the rectangle
    implied by ``width`` and ``length`` (FR-018)."""
    interior_top: float | None = None
    """Explicit z of the interior's ceiling; ``None`` derives it as the box top
    less any band the lid occupies (FR-064)."""
    wall_tops: dict[ScoopSide, float] = field(default_factory=dict)
    """The z of each wall's top, per side (FR-070). Filled in by
    :meth:`with_wall_tops`; empty until then."""

    # ── Rounding (FR-043/FR-044) ─────────────────────────────────────────
    rounding: float | None = None
    """Radius for this body's exposed edges; ``None`` uses half the wall."""
    inner_rounding: float | None = None
    """Radius where a partial lid grips the body; ``None`` uses half the
    outer radius (FR-044b)."""
    rim_free: bool = False
    """True when nothing mates with the top rim, so the rim rounds too
    (FR-043f)."""
    rim_rounding: float | None = None
    """Radius for a top edge that stays exposed with the lid on — a sliding
    box's rails (FR-043f1). ``None`` means none."""
    lid_corner_rounding: float | None = None
    """Radius of a sliding lid's vertical corners; ``None`` derives it from the
    wall, capped at the dovetail depth (FR-002e4)."""

    # ── Finger cuts ──────────────────────────────────────────────────────
    finger_holes: tuple[Any, ...] = ()
    """Explicit exterior finger holes on this box's walls."""
    auto_finger_holes: bool = True
    """Let a lidless box cut its own default pair of grips (FR-047/FR-047b)."""

    # ── Fits ─────────────────────────────────────────────────────────────
    size_spacing: float = WIGGLE_MM
    """General clearance between two mating printed parts, in mm."""
    sliding_slack: float = 0.1
    """Clearance per side between a sliding lid and its groove (FR-002f)."""
    cap_slack: float = WIGGLE_MM
    """Clearance between a cap lid's skirt and the body band it grips."""
    slip_slack: float = WIGGLE_MM
    """Clearance between a slipover sleeve and the body it wraps."""

    # ── Sliding family ───────────────────────────────────────────────────
    lid_slide_axis: str | None = None
    """Override sliding axis: 'x' to slide along width, 'y' to slide along length, None for default."""
    dovetail: bool = True
    """Cut the lid's retaining dovetail; ``False`` leaves a plain channel."""
    lead_chamfer: float | None = None
    """Chamfer on the lid's leading end; ``None`` uses a quarter of the lid
    thickness (FR-002d)."""
    catch_radius: float | None = None
    """Bump-catch radius; ``None`` is no catch, which is a plain sliding box's
    default (FR-002e3)."""
    latch_radius: float = 1.2
    """Catch radius for the card-library type, which always carries one."""
    fingernail_catch: bool = True
    """Cut the dish a nail starts a sliding lid with (FR-002e5).

    On by default: a seated sliding lid is a flush plate with nothing to grip,
    so the dish is part of the type rather than an option. Only the sliding
    family reads this."""
    fingernail_radius: float | None = None
    """Opening radius of that dish; ``None`` derives it from the lid's narrow
    dimension."""
    fingernail_depth: float | None = None
    """How deep it sinks; ``None`` uses half the lid's thickness, which is also
    the cap — the dish must never pierce the plate."""

    # ── Cap and slipover ─────────────────────────────────────────────────
    cap_height: float | None = None
    """Skirt height of a cap lid; ``None`` derives it from the box height."""
    cap_finger_cutouts: bool = True
    """Cut the four corner finger recesses in a cap body (FR-002i)."""
    cap_finger_radius: float | None = None
    """Corner cutout radius; ``None`` derives it from the height available."""
    cap_finger_length: float | None = None
    """How far a corner cutout runs along each side; ``None`` derives it
    between 10mm and a sixth of the side (FR-002m)."""
    cap_finger_height: float | None = None
    """Height of a corner cutout; ``None`` derives it from the skirt."""
    foot: float = 0.0
    """Height of exposed base a slipover sleeve stops above (FR-002p)."""
    slip: float = 1.6
    """Slipover sleeve wall thickness."""
    slipover_gap: float | None = None
    """Band of body left showing below the sleeve; ``None`` derives it as a
    quarter of the covered height, held between 3mm and 6mm (FR-002p)."""
    slipover_finger_height: float | None = None
    """Height of the sleeve's corner notches; ``None`` uses half the skirt,
    capped at 20mm (FR-002h)."""
    inset: float = 1.0
    """Rabbet depth for an inset lid."""

    # ── Hinges ───────────────────────────────────────────────────────────
    hinge_count: int = 5
    """Number of knuckles along the hinge."""
    hinge_pin_diameter: float = 3.0
    """Diameter of the hinge pin, in mm."""
    filament_diameter: float = 1.75
    """Diameter of the filament a living hinge is printed around."""
    hinge_catch_type: str = "ridge"
    """Catch type for hinged boxes; 'ridge' or 'bump'."""

    # ── Magnets (FR-039) ─────────────────────────────────────────────────
    magnet_type: MagnetType | None = None
    """Magnet slot shape; ``None`` means no magnets."""
    magnet_size: tuple[float, float, float] | None = None
    """Slot dimensions ``(diameter_or_width, length, depth)``."""
    magnet_diameter: float = 6.0
    """Round magnet diameter, in mm."""
    magnet_height: float = 3.0
    """Round magnet slot depth, in mm."""
    magnet_count_width: int = 2
    """Magnets per wall on the width axis."""
    magnet_count_length: int = 2
    """Magnets per wall on the length axis."""

    # ── Stacking (FR-038) ────────────────────────────────────────────────
    stackable: StackableMode | None = None
    """Interlocking rim mode; ``None`` means not stackable."""
    stackable_thickness: float | None = None
    """Interlocking rim thickness; ``None`` derives it from the wall."""
    stackable_fit_offset: float = 0.1
    """Clearance between a stacked box's rim and the one below it."""

    # ── Extraction (Phase 3) ─────────────────────────────────────────────
    tilt_to_lift: bool = False
    """Subtle bottom bevel to rock box up for easy extraction."""
    keystone: bool = False
    """Make this the first-out box with extra clearance and a finger scoop."""
    ribbon_channel: bool = False
    """Cut bottom groove for lifting ribbon."""

    def interior(self) -> Interior:
        """Return the usable volume inside this box.

        Returns:
            An :class:`~pyboxbuilder.box.interior.Interior` in the box's own
            frame, inset by the wall on the sides and the floor below.

        """
        from pyboxbuilder.box.interior import Interior

        return Interior(
            width=self.width - 2 * self.wall_thickness,
            length=self.length - 2 * self.wall_thickness,
            height=self.height - self.lid_thickness - self.floor_thickness,
            origin_x=self.wall_thickness,
            origin_y=self.wall_thickness,
            origin_z=self.floor_thickness,
        )

    def default_wall_top(self) -> float:
        """How high a wall stands when the box type says nothing about it.

        The box's own top face, less any band a lid occupies — so a cut merges
        into the surface a hand actually touches rather than into a plane
        buried under the lid.

        Returns:
            The z of the wall's top.

        """
        if self.interior_top is not None:
            return float(self.interior_top)
        return self.height - (0.0 if self.rim_free else self.lid_thickness)

    def wall_top(self, side: ScoopSide) -> float:
        """One wall's top z (FR-070).

        Args:
            side: Which wall.

        Returns:
            That wall's top, or :meth:`default_wall_top` if this spec carries
            no per-side map yet.

        """
        return float(self.wall_tops.get(side, self.default_wall_top()))

    def with_wall_tops(self, box: object) -> BoxSpec:
        """Return this spec with each wall's top resolved for a box type.

        The four walls of a box do **not** have to end at the same height, and
        assuming they do is how a scoop ends up hanging in space: a sliding
        box's exit wall stops a lid thickness below the others, because that is
        where its channel runs out through it.

        Args:
            box: The box type implementation, whose ``wall_tops`` hook may
                raise or lower individual sides.

        Returns:
            A copy carrying a complete ``wall_tops`` map.

        """
        fallback = self.default_wall_top()
        tops = dict.fromkeys(ScoopSide, fallback)
        hook = getattr(box, "wall_tops", None)
        if hook is not None:
            for side, z in (hook(self) or {}).items():
                tops[side] = float(z)
        return replace(self, wall_tops=tops)


#: Fields on a `BoxBuilder` that describe the project or the packing rather
#: than the geometry, so they never reach a `BoxSpec`.
_NOT_GEOMETRY = frozenset({
    "box_type", "label", "box_id", "size", "final_size", "position",
    "expandable", "expandable_width", "expandable_length", "no_rotate",
    "lid", "compartments", "color",
    # Passed explicitly below, after falling back to the project's own.
    "wall_thickness", "floor_thickness", "lid_thickness",
    "rounding", "inner_rounding", "ribbon_channel",
})

_SPEC_FIELDS = frozenset(f.name for f in fields(BoxSpec))


def build_spec(
    project: Project, builder: BoxBuilder, size: tuple[float, float, float]
) -> BoxSpec:
    """Assemble the one description this box is built from.

    The single place a `BoxSpec` is made, so a previewed box and an exported
    box cannot be built from different descriptions.

    Args:
        project: The owning :class:`~pyboxbuilder.project.Project`, read for
            the thicknesses and rounding a box does not override.
        builder: The box's :class:`~pyboxbuilder.builders._base.BoxBuilder`.
        size: The box's resolved ``(width, length, height)`` in mm.

    Returns:
        The assembled :class:`BoxSpec`.

    """
    from pyboxbuilder.box.registry import LIDLESS_BOX_TYPES

    wt = builder.wall_thickness or project.wall_thickness
    ft = builder.floor_thickness or project.floor_thickness
    lt = builder.lid_thickness or project.lid_thickness
    rc = builder.ribbon_channel if builder.ribbon_channel is not None else project.ribbon_channels

    overrides = {
        name: value
        for name, value in (
            (f, getattr(builder, f)) for f in builder.__dataclass_fields__
        )
        if name in _SPEC_FIELDS and name not in _NOT_GEOMETRY and value is not None
    }

    return BoxSpec(
        label=builder.label,
        width=size[0], length=size[1], height=size[2],
        wall_thickness=wt, floor_thickness=ft, lid_thickness=lt,
        ribbon_channel=rc,
        # Hollow the whole interior only when nothing else defines the
        # cavities; with compartments, they are the cavities.
        hollow=not builder.compartments,
        # Per-box override beats the project default, which in turn falls back
        # to half the wall (FR-044).
        rounding=(
            builder.rounding if builder.rounding is not None else project.rounding
        ),
        inner_rounding=(
            builder.inner_rounding if builder.inner_rounding is not None
            else project.inner_rounding
        ),
        # A lidless box's rim is exposed on both faces, so it rounds too.
        rim_free=builder.box_type in LIDLESS_BOX_TYPES,
        **overrides,
    )


def describe(builder: BoxBuilder) -> dict[str, object]:
    """Return a JSON-serialisable description of everything that shapes a box.

    Used to fingerprint an exported piece (FR-031): two runs of an unchanged
    project describe their boxes identically, so nothing is rewritten.

    Args:
        builder: The box builder to describe.

    Returns:
        A dict of the builder's geometry-bearing fields, its compartments and
        its lid decoration.

    """
    def plain(value: Any, field_name: str = "") -> Any:
        """Reduce a value to something `json.dumps(default=str)` compares."""
        if field_name == "shape_file" and value:
            # A silhouette's *contents* shape the box, not the path to it.
            # Named by path alone, editing the SVG changed nothing about the
            # description and the well was never re-cut.
            return {"path": str(value), "sha256": _file_digest(value)}
        if hasattr(value, "__dataclass_fields__"):
            return {f: plain(getattr(value, f), f) for f in value.__dataclass_fields__}
        if isinstance(value, (list, tuple)):
            return [plain(v) for v in value]
        if isinstance(value, dict):
            return {str(k): plain(v) for k, v in value.items()}
        return value

    return {
        name: plain(getattr(builder, name), name)
        for name in builder.__dataclass_fields__
        if name not in ("box_id", "final_size")
    } | {"box_type": builder.box_type.value}


def _file_digest(path: str) -> str:
    """SHA-256 of a file a box's geometry is cut from, or why it could not be read.

    Args:
        path: The file, usually an SVG silhouette.

    Returns:
        A hex digest, or a marker naming the problem — which still differs from
        the digest, so a file that appears later counts as a change.

    """
    import hashlib

    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError as exc:
        return f"unreadable:{type(exc).__name__}"
