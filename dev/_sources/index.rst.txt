pyboxbuilder
=============

**High-Precision Board Game Inserts & Parametric 3D Printable Box Toolkit for PythonSCAD**

``pyboxbuilder`` is a declarative 3D modeling and board game insert design framework. Built on top of `PythonSCAD <https://github.com/pythonscad/pythonscad>`__ and `pybosl2 <https://github.com/pinkfish/pybosl2>`__, it transforms high-level descriptions of games, boxes, and game pieces into production-ready CSG geometry, interactive 3D WebGL models, multi-material 3MF files, and exploded assembly layout PDFs.

The library's governing principle is **good defaults, not options**: you describe the physical storage you need — the game box footprint, card counts, token divisions, scoops, and lid patterns — without manually calculating wall offsets, sliding dovetail tolerances, 3D printing nozzle clearances, or draft angles.

.. pythonscad-example::

   project = Project(
       "Showcase",
       game_box_size=(100.0, 90.0, 28.0),
       board_thickness=6.0,
       generate_spacers=True,
   )
   project.box(
       BoxType.SLIDING,
       "Tokens",
       size=(46.0, 50.0, 20.0),
       position=(2.0, 2.0, 0.0),
       color=Color("midnightblue"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.HEX, spacing=8.0),
       ).titled("TOKENS"),
   )
   tray = project.box(
       BoxType.NO_LID,
       "Dice",
       size=(46.0, 50.0, 20.0),
       position=(50.0, 2.0, 0.0),
       color=Color("coral"),
   )
   tray.compartment("D6", width_ratio=0.5, holds_pieces=True)
   tray.compartment("D20", width_ratio=0.5, holds_pieces=True)
   project.show(show_lids=True)

Why pyboxbuilder?
-----------------

Designing board game inserts by hand in traditional CAD requires tedious trial-and-error math: subtracting wall thicknesses, offsetting dovetail channels, computing lid clearances, and laying out rectangular coordinates. When a box size or card count changes, the entire model must be manually recalculated.

``pyboxbuilder`` replaces manual arithmetic with declarative constraints:

* **Specify What You Need, Not the Booleans**: Define box types, dimensions, card counts, token divisions, and lid decorations. The library derives all mating clearances, corner roundings, draft angles, and boolean carve-outs automatically.
* **Guaranteed Printability**: Every geometric parameter has defaults derived from the box's scale and 3D printing physics (0.4mm nozzle standards, 45° overhang limits, ergonomic reach).
* **Multi-Color Interactive 3D Previews**: Inspect models in PythonSCAD's GUI or embed interactive WebGL viewers directly in documentation and web pages, with multi-color visual separation between bodies, lids, inlays, and spacers.
* **Production 3MF & PDF Pipelines**: Export multi-color (MMU) or single-color 3MF files with geometric change detection (unchanged boxes build in milliseconds) alongside multi-page exploded 3D assembly guides (``layout.pdf``).

Core Design Workflow
--------------------

Creating a custom game insert with ``pyboxbuilder`` follows seven declarative steps:

1. Declare the Project & Game Box Constraints
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Start by declaring a :class:`~pyboxbuilder.project.core.Project` with the inside dimensions of the game box:

.. code-block:: python

   from pyboxbuilder import Project

   project = Project(
       "TerraformingMars",
       game_box_size=(290.0, 290.0, 70.0),
       board_thickness=12.0,       # reserves vertical clearance for folded boards
       generate_spacers=True,      # sweeps empty voids into snug removable trays
   )

2. Choose Box Types & Closure Mechanics
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``pyboxbuilder`` supports **25 specialized box types** spanning 6 closure families (see the :doc:`Box Types Guide & Gallery <box_types>`):

* **Sliding & Friction**: Dovetail sliding lids (:ref:`BoxType.SLIDING <box-type-sliding>`), snap-lock sliding catches (:ref:`BoxType.SLIDING_CATCH <box-type-sliding-catch>`), drop-on friction caps (:ref:`BoxType.CAP <box-type-cap>`), telescoping slipovers (:ref:`BoxType.SLIPOVER <box-type-slipover>`), internal rabbet insets (:ref:`BoxType.INSET <box-type-inset>`), and matchbox sleeves (:ref:`BoxType.SLEEVE_DRAWER <box-type-sleeve-drawer>`).
* **Hinges & Bifolds**: Monolithic 1-piece print-in-place hinged boxes (:ref:`BoxType.PRINT_IN_PLACE_HINGE <box-type-print-in-place-hinge>` and :ref:`BoxType.INSET_HINGE <box-type-inset-hinge>`), dual-tray clamshell book boxes (:ref:`BoxType.CLAMSHELL <box-type-clamshell>`), precision filament-pin knuckle hinges (:ref:`BoxType.FILAMENT_HINGE <box-type-filament-hinge>`), magnetic-catch filament-hinged boxes (:ref:`BoxType.MAGNETIC_HINGE <box-type-magnetic-hinge>`), and sliding/spin-catch hinged boxes (:ref:`BoxType.SLIDING_HINGE <box-type-sliding-hinge>`).
* **Mechanical & Magnetic**: Cantilever snap-fit latches (:ref:`BoxType.SNAP_FIT <box-type-snap-fit>`), quarter-turn bayonets (:ref:`BoxType.BAYONET <box-type-bayonet>`), coarse screw threads (:ref:`BoxType.THREADED <box-type-threaded>`), and concealed neodymium magnet vaults (:ref:`BoxType.MAGNETIC <box-type-magnetic>`).
* **Tabletop Utilities**: Dedicated card deck libraries (:ref:`BoxType.CARD_LIBRARY <box-type-card-library>`), gravity-slide token dispensers (:ref:`BoxType.DISPENSER <box-type-dispenser>`), angled card dealer shoes (:ref:`BoxType.CARD_SHOE <box-type-card-shoe>`), deep dice rolling arenas (:ref:`BoxType.DICE_TRAY <box-type-dice-tray>`), and modular interlocking trays (:ref:`BoxType.MODULAR_INTERLOCK <box-type-modular-interlock>`).
* **Open & Stackable Trays**: Lidless open and nesting trays (:ref:`BoxType.NO_LID <box-type-no-lid>`).
* **Custom Polygons**: Arbitrary 2D footprint extrusions with open rims or matching cap/slipover lids (:ref:`BoxType.PATH <box-type-path>`, :ref:`BoxType.CAP_PATH <box-type-cap-path>`, :ref:`BoxType.SLIPOVER_PATH <box-type-slipover-path>`).

3. Divide into Ergonomic Compartments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Subdivide box interiors by ratio without tedious wall arithmetic. Set ``holds_pieces=True`` to generate smooth cylindrical corner fillets, allowing small chits, cubes, and tokens to scoop effortlessly into fingertips:

.. code-block:: python

   tokens = project.box(BoxType.CAP, "ResourceTray", size=(120.0, 80.0, 24.0))
   tokens.compartment("Credits", width_ratio=0.33, holds_pieces=True)
   tokens.compartment("Steel", width_ratio=0.33, holds_pieces=True)
   tokens.compartment("Titanium", width_ratio=0.34, holds_pieces=True)

4. Auto-Size from Real Game Pieces & Cards
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Never guess well dimensions. Specify card counts, dimensions, and sleeve allowances, and let ``pyboxbuilder`` compute the required box footprint and height:

.. code-block:: python

   cards = project.box(BoxType.SLIDING, "CorporationCards")
   cards.cards("Corporations", count=40, size=(63.5, 88.0), sleeved=True)

5. Style Lids with Patterns & Multi-Color Inlays
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Decorate lids with open ventilation/saving patterns, framed borders, and contrasting multi-color text labels using :class:`~pyboxbuilder.lid.builder.LidBuilder`:

.. code-block:: python

   from pyboxbuilder import Color, LabelMode, LidBuilder, PatternBuilder, PatternType

   lid_style = LidBuilder(
       label_mode=LabelMode.FRAMED,
       frame_color=Color("gold"),
       pattern=PatternBuilder(type=PatternType.HEX, spacing=10.0),
   ).titled("CARDS", text_color=Color("white"))

6. Relative Layout & 3D Packing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Organize boxes cleanly inside the game box using declarative relative layouts (:func:`~pyboxbuilder.layout.columns`, :func:`~pyboxbuilder.layout.rows`, :func:`~pyboxbuilder.layout.stack`) or automated 3D skyline bin packing:

.. code-block:: python

   from pyboxbuilder import columns, stack

   project.arrange(columns(
       "CorporationCards",
       stack("ResourceTray", "DiceTray"),
   ))

7. Production Export & Assembly Guides
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Export per-piece 3MF models ready for single-color or multi-material slicers (Bambu Studio, PrusaSlicer, OrcaSlicer) and an exploded assembly layout guide:

.. code-block:: python

   project.export("output/")

Interactive Feature Showcase
----------------------------

Here are interactive examples highlighting key capabilities of the toolkit. Each example renders an interactive 3D model with multi-color visual separation between box bodies, lids, labels, and accents.

Example 1: Deck Box Sized from Cards with Framed Accent Lid
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This example defines a sliding card box where the internal height and depth are calculated automatically from the card deck dimensions and thickness. The lid features a framed contrasting label:

.. pythonscad-example::

   project = Project("CardGame")
   cards = project.box(
       BoxType.SLIDING,
       "Cards",
       size=(75.0, 105.0, None),
       color=Color("darkslateblue"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.DENSE_HEX),
       ).titled("CARDS"),
   )
   cards.cards("Deck", count=100, size=(63.5, 88.0))
   project.show(show_lids=True)

Example 2: Token Organizer with Ergonomic Piece Scoops
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This 4-compartment token organizer uses ratio-based dividers and rounded interior bottoms (``holds_pieces=True``) so wooden meeples, plastic cubes, and cardboard tokens slide smoothly out into your hand:

.. pythonscad-example::

   project = Project("TokenOrganizer")
   tokens = project.box(
       BoxType.CAP,
       "Tokens",
       size=(120.0, 70.0, 26.0),
       color=Color("darkgreen"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.OCTAGON),
       ).titled("RESOURCES"),
   )
   tokens.compartment("Coins", width_ratio=0.25, holds_pieces=True)
   tokens.compartment("Gems", width_ratio=0.25, holds_pieces=True)
   tokens.compartment("Wood", width_ratio=0.25, holds_pieces=True)
   tokens.compartment("Ore", width_ratio=0.25, holds_pieces=True)
   project.show(show_lids=True)

Example 3: Monolithic Print-in-Place Hinged Box
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This box prints flat in a single operation with zero assembly required. It joins body and lid along their shared rim with a 3D-printable flexible bridge hinge and integrated front tactile snap catches:

.. pythonscad-example::

   project = Project("HingeCase")
   box = project.box(
       BoxType.PRINT_IN_PLACE_HINGE,
       "Tools",
       size=(90.0, 60.0, 24.0),
       color=Color("teal"),
       pip_bridge_width=0.40,
       pip_bridge_thickness=0.40,
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("goldenrod"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.HEX, spacing=8.0),
       ).titled("KIT"),
   )
   box.compartment("Bits", width_ratio=0.5, holds_pieces=True)
   box.compartment("Drivers", width_ratio=0.5, holds_pieces=True)
   project.show(show_lids=True)

Core System Architecture
------------------------

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Subsystem
     - Description & Capabilities
   * - **Box Builders**
     - 25 typed builders in :mod:`pyboxbuilder.builders` (see :doc:`box_types`) supporting sliding dovetails (:ref:`SLIDING <box-type-sliding>`, :ref:`SLIDING_CATCH <box-type-sliding-catch>`), friction caps (:ref:`CAP <box-type-cap>`), telescoping slipovers (:ref:`SLIPOVER <box-type-slipover>`), print-in-place, filament-pin, magnetic-catch, and sliding-catch hinges (:ref:`PRINT_IN_PLACE_HINGE <box-type-print-in-place-hinge>`, :ref:`INSET_HINGE <box-type-inset-hinge>`, :ref:`CLAMSHELL <box-type-clamshell>`, :ref:`FILAMENT_HINGE <box-type-filament-hinge>`, :ref:`MAGNETIC_HINGE <box-type-magnetic-hinge>`, :ref:`SLIDING_HINGE <box-type-sliding-hinge>`), mechanical/magnetic closures (:ref:`SNAP_FIT <box-type-snap-fit>`, :ref:`BAYONET <box-type-bayonet>`, :ref:`THREADED <box-type-threaded>`, :ref:`MAGNETIC <box-type-magnetic>`, :ref:`INSET <box-type-inset>`, :ref:`SLEEVE_DRAWER <box-type-sleeve-drawer>`), stackable open bins (:ref:`NO_LID <box-type-no-lid>`), tabletop utilities (:ref:`CARD_LIBRARY <box-type-card-library>`, :ref:`DISPENSER <box-type-dispenser>`, :ref:`CARD_SHOE <box-type-card-shoe>`, :ref:`DICE_TRAY <box-type-dice-tray>`, :ref:`MODULAR_INTERLOCK <box-type-modular-interlock>`), and polygon path footprints (:ref:`PATH <box-type-path>`, :ref:`CAP_PATH <box-type-cap-path>`, :ref:`SLIPOVER_PATH <box-type-slipover-path>`).
   * - **Compartments & Ergonomics**
     - Ratio-based compartment division (``box.compartment(...)``), ergonomic rounded token scoops (``holds_pieces=True``), full-depth push-through holes, hex grids, and arbitrary SVG pocket silhouettes.
   * - **Lid Decoration**
     - 20 surface patterns and multi-color tessellations (hex, dense hex, triangles, octagons, voronoi, leaf tessellations, dice, rings, checkerboards, stepped 3D cubes, tumbling blocks, chevrons, Penrose, and Ammann–Beenker tilings — see :doc:`lid_patterns`), thin multi-color MMU inlays with a selectable backing lattice, and embossed/engraved labels with automatic font scaling (:class:`~pyboxbuilder.lid.builder.LidBuilder`).
   * - **Layout & 3D Packing**
     - Declarative relative layout trees (:func:`~pyboxbuilder.layout.columns`, :func:`~pyboxbuilder.layout.rows`, :func:`~pyboxbuilder.layout.stack`) or automated 3D skyline bin packing within the declared :attr:`~pyboxbuilder.project.core.Project.game_box_size`.
   * - **Automatic Spacers**
     - 3D void sweep, merge, and generation of custom-fit open spacer trays (``generate_spacers=True``) to secure components during vertical shelf storage.
   * - **Card & Sleeve Support**
     - Built-in card dimension catalog and sleeve clearance formulas for standard board game card sizes and premium sleeves.

Installation & Quickstart
-------------------------

``pyboxbuilder`` requires Python 3.12+ and `PythonSCAD <https://www.pythonscad.org/>`__ for geometry evaluation:

.. code-block:: sh

   python3 -m venv .venv && source .venv/bin/activate
   pip install -e ".[dev]"

To verify your installation and run the test suite:

.. code-block:: sh

   PYBOXBUILDER_EXPORT_FN=12 python3 -m pytest tests/test_pyboxbuilder/ -q
   ruff check pyboxbuilder/ boxes/
   mypy pyboxbuilder/

Documentation Index
-------------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   quickstart
   getting_started
   box_types
   lid_patterns
   layout_and_spacers
   boxes/index

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api
