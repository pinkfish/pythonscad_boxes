# SPDX-License-Identifier: Apache-2.0
"""Public enums for the pyboxbuilder box library."""

from enum import Enum


class BoxType(Enum):
    """Box lid mechanism type."""

    SLIDING = "sliding"
    CAP = "cap"
    HINGE = "hinge"
    FILAMENT_HINGE = "filament_hinge"
    MAGNETIC = "magnetic"
    INSET = "inset"
    SLIDING_CATCH = "sliding_catch"
    SLIPOVER = "slipover"
    SLIPOVER_PATH = "slipover_path"
    CAP_PATH = "cap_path"
    NO_LID = "no_lid"
    PATH = "path"
    CARD_LIBRARY = "card_library"


class LabelMode(Enum):
    """Label decoration style."""

    FRAMED = "framed"
    FRAMELESS = "frameless"


class PatternType(Enum):
    """Lid through-hole pattern (FR-023).

    Every member here is a shape the library actually draws. It listed 47 and
    drew three: the tessellations and pentagon tilings wrapped an import of a
    package this repo does not contain, inside a bare `except`, and fell back to
    square holes — so a lid asking for LEAF got squares and nothing said so.
    A member is added when the geometry to draw it is (FR-000c).
    """

    NONE = "none"
    """No pattern — a solid lid."""

    SQUARE = "square"
    """Square holes on a square grid."""
    CIRCLE = "circle"
    """Round holes on a square grid."""
    HEX = "hex"
    """Hexagonal holes in staggered rows — a honeycomb."""
    DENSE_HEX = "dense_hex"
    """The honeycomb at a tighter pitch."""
    TRIANGLE = "triangle"
    """Triangular holes, alternating point-up and point-down."""
    DENSE_TRIANGLE = "dense_triangle"
    """The triangle grid at a tighter pitch."""
    OCTAGON = "octagon"
    """Octagonal holes, leaving small square webs between them."""
    VORONOI = "voronoi"
    """Round holes of varying size on a jittered grid — an organic scatter."""
    LEAF = "leaf"
    """Pointed-oval leaves, each with a midrib, interlocking in offset rows."""
    LEAF_TESSELLATION = "leaf_tessellation"
    """Leaves that tile the lid edge to edge, leaving a net of their outlines."""
    LEAF_VEINS = "leaf_veins"
    """That tessellation with a midrib and branching veins left in each leaf."""


class StackableMode(Enum):
    """How a no-lid box's interlocking rim mates with its neighbour (FR-038).

    Both modes stack securely; the choice decides whether the rim sits inside
    the box above or wraps around the box below.
    """

    INSIDE = "inside"
    """A recess in the top rim that the box above nests down into."""
    OUTSIDE = "outside"
    """A ridge around the outside that fits over the box below."""


class MagnetType(Enum):
    """Shape of a magnet cavity in a box side wall (FR-039)."""

    NONE = "none"
    """No magnets."""
    ROUND = "round"
    """A cylindrical cavity — e.g. a 6mm diameter x 3mm deep disc magnet."""
    RECT = "rect"
    """A box-shaped cavity — e.g. a 10 x 5 x 2mm block magnet."""


class ScoopSide(Enum):
    """Finger scoop placement side."""

    FRONT = "front"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"


class FingerCut(Enum):
    """How a compartment's finger cutout gets the contents out (FR-060).

    The two answer different situations, and which one a well wants is about
    what is *in* it rather than how big it is:

    ``THROUGH_FLOOR``
        A hole through the box's base at one wall, so a thumb pushes the
        contents up from underneath. What a **stack** needs — a card stack
        fills its well, leaving no side for a finger to reach down. The
        original toolkit cuts every card box this way.
    ``SCOOP``
        A dip in the side of the well, for loose pieces a finger goes in
        beside: tokens, a bag, a board. It leaves the base solid.
    """

    THROUGH_FLOOR = "through_floor"
    SCOOP = "scoop"


class ElementShape(Enum):
    """Silhouette kind for a `CompartmentElement` (FR-004a/FR-004b).

    SVG elements take their outline from `shape_file`; the rest are
    parametric and need only the element's bounding size.
    """

    SVG = "svg"
    RECT = "rect"
    ROUNDED_RECT = "rounded_rect"
    CIRCLE = "circle"
    HEXAGON = "hexagon"
    SPHERE_SCOOP = "sphere_scoop"
    TEXT = "text"
