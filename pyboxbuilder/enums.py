# SPDX-License-Identifier: Apache-2.0
"""Public enums for the pyboxbuilder box library."""

from enum import Enum


class BoxType(Enum):
    """Box lid mechanism type."""

    SLIDING = "sliding"
    CAP = "cap"
    FILAMENT_HINGE = "filament_hinge"
    MAGNETIC_HINGE = "magnetic_hinge"
    MAGNETIC = "magnetic"
    INSET = "inset"
    SLIDING_CATCH = "sliding_catch"
    SLIPOVER = "slipover"
    SLIPOVER_PATH = "slipover_path"
    CAP_PATH = "cap_path"
    NO_LID = "no_lid"
    PATH = "path"
    CARD_LIBRARY = "card_library"
    SNAP_FIT = "snap_fit"
    BAYONET = "bayonet"
    THREADED = "threaded"
    DISPENSER = "dispenser"
    CARD_SHOE = "card_shoe"
    DICE_TRAY = "dice_tray"
    SLEEVE_DRAWER = "sleeve_drawer"
    CLAMSHELL = "clamshell"
    MODULAR_INTERLOCK = "modular_interlock"
    PRINT_IN_PLACE_HINGE = "print_in_place_hinge"
    INSET_HINGE = "inset_hinge"
    SLIDING_HINGE = "sliding_hinge"


class CatchType(Enum):
    """Retention catch mechanism for box lids (FR-099)."""

    NONE = "none"
    """No positive retention catch (friction fit or plain track)."""
    BUMP = "bump"
    """Spherical / hemispherical detent bumps and matching dimples."""
    LOOP = "loop"
    """Resilient strap / loop tab that snaps over an opposing stud or hook."""
    WEDGE = "wedge"
    """Asymmetric ramped wedge ridge / barb with positive locking shoulder."""
    MAGNET = "magnet"
    """Paired blind cylindrical pockets sized for neodymium disc magnets."""
    LEAF_SPRING = "leaf_spring"
    """Compliant cantilever flexure arm backed by an elastic relief slot."""
    SLIDE_ACROSS = "slide_across"
    """Captive print-in-place horizontal dovetail sliding bolt catch (card-library style)."""
    SLIDE_UP = "slide_up"
    """Captive print-in-place vertical dovetail slider on the front wall that slides up to lock."""
    SPIN = "spin"
    """Print-in-place rotary cam / turn-button catch that hooks the lid when spun up and releases when spun down."""
    PUSH_BUTTON = "push_button"
    """Compliant thumb-press flexure button on the front wall that deflects inward to release the lid."""
    TOGGLE_LATCH = "toggle_latch"
    """Print-in-place articulated over-center draw latch bail on the front wall."""
    PINCH_SLIDE = "pinch_slide"
    """Dual opposing captive dovetail sliders that pinch toward the center to release both bolts."""
    ROTARY_BOLT = "rotary_bolt"
    """Flush print-in-place quarter-turn rotary cam disk inside the lid."""


class InterlockType(Enum):
    """Interlocking joint type for modular play trays and grid boxes (FR-089, FR-102)."""

    DOVETAIL = "dovetail"
    MAGNET = "magnet"
    CLIP = "clip"
    GRIDFINITY = "gridfinity"
    NONE = "none"


class LabelMode(Enum):
    """Label decoration style."""

    FRAMED = "framed"
    """Raised frame border around label text."""
    FRAMELESS = "frameless"
    """Direct label text without a raised frame."""


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
    SOLID = "solid"
    """Explicitly solid lid surface — no through-holes or inlays."""

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
    DICE = "dice"
    """Gaming dice (D6) faces with pips on a grid."""
    RING = "ring"
    """Circular rings / washers with an inner hole."""
    CHECKER = "checker"
    """Alternating checkerboard tiles on a square grid."""
    STEPPED_CUBE = "stepped_cube"
    """Stepped 3D cube and diamond rhombic tessellation (4-color isometric cube & peak diamond tiling)."""
    TUMBLING_BLOCKS = "tumbling_blocks"
    """Classic 3-rhombus isometric cube tessellation (tumbling blocks)."""
    CHEVRON = "chevron"
    """Interlocking 60°/120° herringbone chevron rhombus tessellation."""
    PENROSE = "penrose"
    """Ten-fold quasiperiodic Penrose rhombus tessellation (de Bruijn multigrid)."""
    AMMANN_BEENKER = "ammann_beenker"
    """Eight-fold quasiperiodic Ammann–Beenker rhombus tessellation (de Bruijn multigrid)."""


class StackableMode(Enum):
    """How a box mates vertically with its neighbour (FR-038, FR-101).

    Supports open trays and lidded boxes:
    - INSIDE: Stepped inner recess in the top rim that the box above nests into.
    - OUTSIDE: A ridge around the outside base that fits over the box below.
    - FEET: Protruding locator feet on the bottom floor, matching socket indents on the lid/top.
    - INDENTS: Recessed socket indents on the bottom floor, matching locator feet on the lid/top.
    - FEET: Corner locator pads/pyramids, matching socket indents.
    - INDENTS: Recessed socket indents on bottom floor, matching locator bosses on lid/top.
    - PYRAMID: 3D-printer-safe single 45-degree pyramid sockets on bottom, matching pyramids on top.
    - PYRAMIDS: 3D-printer-safe multi-pyramid grid (45-degree pyramids) on bottom, matching grid on top.
    - PATTERN: Pattern-matched stacking where the box bottom matches the lid's decorative pattern.
    - PERIMETER: Continuous or segmented perimeter foot/V-ridge rim, matching perimeter channel on lid/top.
    """

    INSIDE = "inside"
    """A recess in the top rim that the box above nests down into."""
    OUTSIDE = "outside"
    """A ridge around the outside that fits over the box below."""
    FEET = "feet"
    """Protruding locator feet on the bottom floor (or top when printer-safe), matching socket indents."""
    INDENTS = "indents"
    """Recessed socket indents on the bottom floor, matching locator feet on the lid/top."""
    PYRAMID = "pyramid"
    """Single 45-degree pyramid socket indents on the bottom floor, matching 45-degree pyramids on top."""
    PYRAMIDS = "pyramids"
    """Set/grid of 45-degree pyramid socket indents on the bottom floor, matching pyramid grid on top."""
    PATTERN = "pattern"
    """Pattern-matched stacking: recessed pattern lattice on the bottom floor, matching pattern ridge on the lid/top."""
    PERIMETER = "perimeter"
    """Perimeter foot/V-ridge rim and matching recessed perimeter channel."""


class StackableShape(Enum):
    """3D-printable geometry profile for stacking feet and socket indents."""

    PYRAMIDS = "pyramids"
    """Grid/set of 45-degree square pyramids filling each corner pad (3D-printer safe, shallow depth)."""
    PYRAMID = "pyramid"
    """Single 45-degree square pyramid per corner pad (or 45-degree V-ridge for perimeter)."""
    CONE = "cone"
    """45-degree conical boss and socket profile (or grid of 45-degree cones)."""
    PATTERN = "pattern"
    """Pattern-matched stacking profile matching the lid's decorative pattern."""
    FLAT = "flat"
    """Classic flat-topped/flat-bottomed rectangular pad with edge chamfer."""


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


class DispenserExtractionMode(Enum):
    """How tiles/tokens are extracted from a gravity dispenser (FR-084).

    * ``SCOOP``: Front finger scoop + floor notch so the bottom tile can be
      pinched and pulled forward (default).
    * ``TRAY``: Forward-extending landing tray/lip where the bottom tile slides
      out ahead of the tower for direct pickup.
    * ``REAR_PUSH``: Rear push slot on the back wall allowing a finger to slide
      the bottom tile forward through the front slot.
    * ``ARCH``: Open front archway for direct finger access to the bottom tiles.
    """

    SCOOP = "scoop"
    TRAY = "tray"
    REAR_PUSH = "rear_push"
    ARCH = "arch"


class DrawerHandleStyle(Enum):
    """Handle style for sleeve drawers (FR-087)."""

    HANDLE = "handle"
    """Centered ergonomic pull knob/handle."""
    LIP = "lip"
    """Forward-projecting lip across the drawer front."""
    NONE = "none"
    """Flush front face with no protruding handle."""


class HingeCatchType(Enum):
    """Catch mechanism for hinged box closures."""

    RIDGE = "ridge"
    """Ridge / wedge barb catch."""
    WEDGE = "wedge"
    """Asymmetric ramped wedge ridge / barb catch."""
    BUMP = "bump"
    """Detent bump catch."""
    LOOP = "loop"
    """Resilient strap / loop tab catch."""
    MAGNET = "magnet"
    """Paired blind cylindrical magnet pockets."""
    LEAF_SPRING = "leaf_spring"
    """Compliant cantilever flexure arm catch."""
    SLIDE_ACROSS = "slide_across"
    """Captive print-in-place horizontal dovetail sliding bolt catch."""
    SLIDE_UP = "slide_up"
    """Captive print-in-place vertical dovetail slider catch on the front wall."""
    SPIN = "spin"
    """Print-in-place rotary cam / turn-button catch on the front wall."""
    PUSH_BUTTON = "push_button"
    """Compliant thumb-press flexure release catch on the front wall."""
    TOGGLE_LATCH = "toggle_latch"
    """Print-in-place articulated over-center draw latch bail on the front wall."""
    PINCH_SLIDE = "pinch_slide"
    """Dual opposing captive dovetail sliders that pinch together to release."""
    ROTARY_BOLT = "rotary_bolt"
    """Flush print-in-place quarter-turn rotary cam disk inside the lid."""
    NONE = "none"
    """No positive catch."""


class LatchAxis(Enum):
    """Axis on whose opposing walls cantilever latch arms sit (FR-081)."""

    X = "x"
    """Latches on the left and right walls parallel to the X axis."""
    Y = "y"
    """Latches on the front and back walls parallel to the Y axis."""


class ColorMode(Enum):
    """Multi-material color mode for lids and decorations."""

    MMU = "mmu"
    """Multi-material printing with discrete colored inserts."""
    SINGLE = "single"
    """Single material printing (engraved labels, through-hole cuts)."""

