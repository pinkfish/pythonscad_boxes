Getting Started
===============

Welcome to ``pyboxbuilder``! This guide introduces the core concepts and walks you through:

1. **Creating your very first box** and previewing it in 3D.
2. **Designing standalone boxes** (such as dice boxes or modular token trays) without an enclosing game box.
3. **Building a complete game insert** that packs multiple boxes, trays, and automatic spacer trays into a publisher's game box.
4. **Exporting and 3D printing** your designs using the built-in CLI runner.

.. note::
   All example code below uses the interactive 3D WebGL viewer. You can rotate, pan, and zoom the rendered models directly in your browser.

Creating Your First Box
-----------------------

Every box in ``pyboxbuilder`` belongs to a :class:`~pyboxbuilder.project.core.Project`. A project defines project-wide defaults (such as wall thickness, floor thickness, and edge rounding) and holds all the boxes you create.

Here is a minimal script that creates a simple dice or token box with a sliding lid:

.. pythonscad-example::

    from pyboxbuilder import BoxType, Project

    # Create a project. Setting game_box_size=None indicates a standalone box.
    project = Project("Quickstart", game_box_size=None)

    # Add a sliding-lid box
    project.box(
        BoxType.SLIDING,
        "DiceBox",
        size=(65.0, 45.0, 25.0),
        wall_thickness=2.0,
    )

    # In PythonSCAD, preview the box and its lid
    project.show(show_lids=True)

In this snippet:

* :class:`~pyboxbuilder.project.core.Project` initializes the project. Specifying ``game_box_size=None`` tells ``pyboxbuilder`` that this box is standalone and does not need to be packed inside a board game's cardboard box.
* :meth:`~pyboxbuilder.project.core.Project.box` registers a new box. We choose ``BoxType.SLIDING``, give it a label (``"DiceBox"``), and assign it an outer size of 65 mm × 45 mm × 25 mm.
* :meth:`~pyboxbuilder.project.core.Project.show` renders the pieces in PythonSCAD. Passing ``show_lids=True`` displays both the box body and its sliding lid side-by-side.

Designing Standalone Boxes
--------------------------

Standalone boxes are ideal when you want to print individual tabletop organizers, such as:

* Bit trays and token holders used during gameplay.
* Dice vaults and miniature boxes.
* Modular organizer bins with magnetic or interlocking lids.

When ``game_box_size=None``, each box is exported independently without constraints from an enclosing game box.

Dividing into Compartments
~~~~~~~~~~~~~~~~~~~~~~~~~~

Rather than calculating internal wall widths and floor offsets by hand, you can define compartments using relative width and length ratios via ``box.compartment(...)``:

.. pythonscad-example::

    from pyboxbuilder import BoxType, Project

    project = Project("TokenOrganizer", game_box_size=None)

    tray = project.box(
        BoxType.NO_LID,
        "ResourceTray",
        size=(85.0, 55.0, 22.0),
        wall_thickness=2.0,
    )

    # Divide into two equal wells across the width (50% each)
    # holds_pieces=True rounds the bottom corners into an ergonomic scoop
    tray.compartment("Wood", width_ratio=0.5, holds_pieces=True)
    tray.compartment("Stone", width_ratio=0.5, holds_pieces=True)

    project.show()

Key features used here:

* ``width_ratio=0.5``: Divides the usable interior into two equal wells. The library calculates divider wall thickness and floor spacing automatically.
* ``holds_pieces=True``: Shapes the bottom corners into smooth ergonomic scoops so tokens can be swept out easily with a fingertip.

Adding Lids, Patterns, and Labels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can customize lids with geometric patterns, finger grips, or text labels:

.. code-block:: python

    from pyboxbuilder import BoxType, PatternType, Project

    project = Project("FancyBox", game_box_size=None)

    fancy = project.box(
        BoxType.SLIDING,
        "Gems",
        size=(70.0, 50.0, 30.0),
    )

    # Decorate the sliding lid with a hex pattern
    fancy.lid.pattern(PatternType.HEX, border_margin_mm=4.0)

See the :doc:`box_types` guide for full details on each lid style and parameter options.

Box Types & Closure Mechanisms
------------------------------

``pyboxbuilder`` supports 23 specialized box closure and utility types (:class:`~pyboxbuilder.enums.BoxType`). Every type can be created via ``project.box(BoxType.<TYPE>, ...)`` or its corresponding typed builder in :mod:`pyboxbuilder.builders`.

Below are working examples for all 23 box types:

Sliding & Friction Closures
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Sliding Lid (``BoxType.SLIDING``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A sliding dovetail lid that glides along side rails with no loose parts:

.. pythonscad-example::

   project = Project("SlidingDemo", game_box_size=(80.0, 80.0, 30.0))
   project.box(
       BoxType.SLIDING,
       "Tokens",
       size=(60.0, 60.0, 22.0),
       lid=LidBuilder(
           pattern=PatternBuilder(PatternType.HEX),
           text="TOKENS",
       ),
   )
   project.show(show_lids=True)


Sliding Catch Lid (``BoxType.SLIDING_CATCH``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A sliding dovetail lid with an integrated detent bump catch at the leading edge to lock the lid closed:

.. pythonscad-example::

   project = Project("CatchDemo", game_box_size=(80.0, 80.0, 30.0))
   project.box(
       BoxType.SLIDING_CATCH,
       "CatchBox",
       size=(60.0, 60.0, 22.0),
       lid=LidBuilder(text="LOCKED"),
   )
   project.show(show_lids=True)


Drop-On Cap Lid (``BoxType.CAP``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A friction-fit cap lid that drops straight onto the box body from above with side finger cutouts:

.. pythonscad-example::

   project = Project("CapDemo", game_box_size=(80.0, 80.0, 30.0))
   box = project.box(
       BoxType.CAP,
       "PlayerTray",
       size=(60.0, 60.0, 22.0),
       lid=LidBuilder(text="PLAYER 1"),
   )
   box.compartment("LeftWell", width_ratio=0.5)
   box.compartment("RightWell", width_ratio=0.5)
   project.show(show_lids=True)


Telescoping Slipover Lid (``BoxType.SLIPOVER``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A full-depth outer sleeve that envelopes the inner body tray completely:

.. pythonscad-example::

   project = Project("SlipoverDemo", game_box_size=(80.0, 80.0, 30.0))
   project.box(
       BoxType.SLIPOVER,
       "CardsBox",
       size=(60.0, 60.0, 22.0),
       lid=LidBuilder(text="DECK"),
   )
   project.show(show_lids=True)


Inset Flush Lid (``BoxType.INSET``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A flush drop-in lid that seats onto an internal stepped perimeter rabbet:

.. pythonscad-example::

   project = Project("InsetDemo", game_box_size=(80.0, 80.0, 30.0))
   project.box(
       BoxType.INSET,
       "InsetBox",
       size=(60.0, 60.0, 22.0),
       lid=LidBuilder(text="INSET"),
   )
   project.show(show_lids=True)


Matchbox Sleeve & Drawer (``BoxType.SLEEVE_DRAWER``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A 4-sided outer sleeve enclosing an inner drawer tray with a pull lip and rear push-through hole:

.. pythonscad-example::

   project = Project("DrawerDemo", game_box_size=(80.0, 80.0, 30.0))
   project.box(
       BoxType.SLEEVE_DRAWER,
       "MatchboxDrawer",
       size=(60.0, 50.0, 22.0),
       drawer_pull_lip=4.0,
   )
   project.show(show_lids=True)


Hinged & Folding Closures
~~~~~~~~~~~~~~~~~~~~~~~~~

Monolithic Print-In-Place Hinge Box (``BoxType.PRINT_IN_PLACE_HINGE``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A zero-assembly 1-piece print laid flat at 180° on the print bed with interlocking captive pin knuckles and front snap catches from ``pybosl2``:

.. pythonscad-example::

   project = Project("PIPHingeDemo", game_box_size=(160.0, 100.0, 40.0))
   project.box(
       BoxType.PRINT_IN_PLACE_HINGE,
       "MiniDeckBox",
       size=(70.0, 50.0, 25.0),
       pip_radial_clearance=0.35,
       pip_axial_clearance=0.40,
   )
   project.show(show_lids=True)


Bifold Clamshell Book Box (``BoxType.CLAMSHELL``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A book-fold box with active compartments in both halves that opens flat 180° on the tabletop:

.. pythonscad-example::

   project = Project("ClamshellDemo", game_box_size=(80.0, 80.0, 30.0))
   project.box(
       BoxType.CLAMSHELL,
       "DiceBook",
       size=(60.0, 50.0, 24.0),
       clamshell_hinge_radius=2.5,
   )
   project.show(show_lids=True)


Print-in-Place Pin Hinge (``BoxType.HINGE``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

An integrated captive-pin knuckle hinge connecting body and lid:

.. pythonscad-example::

   project = Project("HingeDemo", game_box_size=(80.0, 80.0, 30.0))
   project.box(
       BoxType.HINGE,
       "HingedChest",
       size=(60.0, 60.0, 22.0),
       hinge_count=3,
   )
   project.show(show_lids=True)


Filament Pin Hinge (``BoxType.FILAMENT_HINGE``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Interleaving knuckles precision-bored to accept a standard 1.75mm 3D printer filament strand as the hinge pin:

.. pythonscad-example::

   project = Project("FilamentHingeDemo", game_box_size=(80.0, 80.0, 30.0))
   project.box(
       BoxType.FILAMENT_HINGE,
       "PinBox",
       size=(60.0, 50.0, 22.0),
       lid=LidBuilder(text="GEAR"),
   )
   project.show(show_lids=True)


Mechanical, Magnetic & Threaded Closures
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Snap-Fit Cantilever Latch (``BoxType.SNAP_FIT``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A lid with integrated cantilever spring arms and 45° lead-in retention detents mating into recessed body pockets:

.. pythonscad-example::

   project = Project("SnapFitDemo", game_box_size=(80.0, 80.0, 30.0))
   project.box(
       BoxType.SNAP_FIT,
       "LatchBox",
       size=(60.0, 50.0, 25.0),
       cantilever_width=12.0,
       detent_height=1.5,
   )
   project.show(show_lids=True)


Twist-Lock Bayonet Container (``BoxType.BAYONET``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Quarter-turn twist-lock container with vertical entry keyways and horizontal locking channels:

.. pythonscad-example::

   project = Project("BayonetDemo", game_box_size=(80.0, 80.0, 50.0))
   project.box(
       BoxType.BAYONET,
       "TokenCanister",
       size=(60.0, 60.0, 40.0),
       lug_count=4,
       turn_angle=90.0,
   )
   project.show(show_lids=True)


Threaded Screw Box (``BoxType.THREADED``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Coarse 3.0mm pitch modified trapezoidal screw threads with 0.25mm clearance for effortless opening:

.. pythonscad-example::

   project = Project("ThreadedDemo", game_box_size=(80.0, 80.0, 50.0))
   project.box(
       BoxType.THREADED,
       "ScrewCanister",
       size=(55.0, 55.0, 40.0),
       thread_pitch=3.0,
       thread_turns=2.0,
   )
   project.show(show_lids=True)


Magnetic Closure Lid (``BoxType.MAGNETIC``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Concealed cylindrical magnet pockets in corners of the body and lid for a tactile magnetic snap:

.. pythonscad-example::

   project = Project("MagneticDemo", game_box_size=(80.0, 80.0, 30.0))
   project.box(
       BoxType.MAGNETIC,
       "Vault",
       size=(60.0, 60.0, 22.0),
       magnet_type=MagnetType.ROUND,
       magnet_diameter=6.0,
       magnet_height=3.0,
       lid=LidBuilder(text="VAULT"),
   )
   project.show(show_lids=True)


Tabletop & Game Play Trays
~~~~~~~~~~~~~~~~~~~~~~~~~~

Gravity Tile & Token Dispenser (``BoxType.DISPENSER``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A gravity dispenser tower featuring a 40° internal slide floor feeding a single-token extraction slot:

.. pythonscad-example::

   project = Project("DispenserDemo", game_box_size=(70.0, 70.0, 80.0))
   project.box(
       BoxType.DISPENSER,
       "TileTower",
       size=(55.0, 55.0, 70.0),
       chute_angle=40.0,
       token_thickness=3.0,
   )
   project.show(show_lids=True)


Angled Draw & Discard Card Shoe (``BoxType.CARD_SHOE``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A dealer shoe tray with a 20° slanted draw well, retaining lip, and flat discard well with thumb cutouts:

.. pythonscad-example::

   project = Project("CardShoeDemo", game_box_size=(100.0, 80.0, 40.0))
   project.box(
       BoxType.CARD_SHOE,
       "DealerShoe",
       size=(85.0, 65.0, 30.0),
       draw_angle=20.0,
       retaining_lip_height=10.0,
   )
   project.show(show_lids=True)


Dice Tray & Rolling Arena (``BoxType.DICE_TRAY``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Deep 25mm+ arena lid with 45° corner deflector fillets and felt pocket that functions as a tabletop dice arena:

.. pythonscad-example::

   project = Project("DiceTrayDemo", game_box_size=(90.0, 90.0, 40.0))
   project.box(
       BoxType.DICE_TRAY,
       "RollingArena",
       size=(75.0, 75.0, 32.0),
       arena_wall_height=28.0,
       corner_deflectors=True,
   )
   project.show(show_lids=True)


Modular Interlocking Play Trays (``BoxType.MODULAR_INTERLOCK``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Tabletop organization trays with perimeter sliding dovetails or Gridfinity-compatible tiered base profiles:

.. pythonscad-example::

   project = Project("ModularDemo", game_box_size=(150.0, 150.0, 40.0))
   project.box(
       BoxType.MODULAR_INTERLOCK,
       "DashboardTray",
       size=(84.0, 84.0, 25.0),
       interlock_type=InterlockType.DOVETAIL,
       dovetail_clearance=0.15,
   )
   project.show(show_lids=True)


Open & Stackable Trays (``BoxType.NO_LID``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Open organizer trays with stepped stacking ledges and ergonomic fingertip scoops:

.. pythonscad-example::

   project = Project("StackDemo", game_box_size=(80.0, 80.0, 40.0))
   project.box(
       BoxType.NO_LID,
       "BaseTray",
       size=(60.0, 60.0, 16.0),
       position=(10.0, 10.0, 0.0),
   )
   project.box(
       BoxType.NO_LID,
       "TopTray",
       size=(60.0, 60.0, 16.0),
       position=(10.0, 10.0, 16.0),
   )
   project.show()


Card Library Box (``BoxType.CARD_LIBRARY``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

High-capacity card tray with finger pull-out scoops and angled card support wedges:

.. pythonscad-example::

   project = Project("CardLibraryDemo", game_box_size=(120.0, 80.0, 40.0))
   project.box(
       BoxType.CARD_LIBRARY,
       "DeckLibrary",
       size=(100.0, 65.0, 32.0),
       wall_thickness=2.0,
   )
   project.show(show_lids=True)


Custom Footprints & Polygon Shapes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Polygon Footprint Path Box (``BoxType.PATH``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Open custom-profile tray whose exterior footprint follows any arbitrary 2D polygon path:

.. pythonscad-example::

   project = Project("PathDemo", game_box_size=(80.0, 80.0, 30.0))
   l_path = (
       (0.0, 0.0),
       (55.0, 0.0),
       (55.0, 25.0),
       (25.0, 25.0),
       (25.0, 55.0),
       (0.0, 55.0),
   )
   project.box(
       BoxType.PATH,
       "LShapedTray",
       size=(55.0, 55.0, 20.0),
       path=l_path,
       wall_thickness=2.0,
   )
   project.show()


Cap Lid on Polygon Footprint (``BoxType.CAP_PATH``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Drop-on friction cap lid over an arbitrary 2D polygon path footprint:

.. pythonscad-example::

   project = Project("CapPathDemo", game_box_size=(80.0, 80.0, 30.0))
   l_path = (
       (0.0, 0.0),
       (55.0, 0.0),
       (55.0, 25.0),
       (25.0, 25.0),
       (25.0, 55.0),
       (0.0, 55.0),
   )
   project.box(
       BoxType.CAP_PATH,
       "CapPathTray",
       size=(55.0, 55.0, 20.0),
       path=l_path,
       lid=LidBuilder(text="L-TRAY"),
   )
   project.show(show_lids=True)


Slipover on Polygon Footprint (``BoxType.SLIPOVER_PATH``)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Full-depth telescoping slipover sleeve over an arbitrary 2D polygon path footprint:

.. pythonscad-example::

   project = Project("SlipoverPathDemo", game_box_size=(80.0, 80.0, 30.0))
   t_path = (
       (15.0, 0.0),
       (40.0, 0.0),
       (40.0, 30.0),
       (55.0, 30.0),
       (55.0, 55.0),
       (0.0, 55.0),
       (0.0, 30.0),
       (15.0, 30.0),
   )
   project.box(
       BoxType.SLIPOVER_PATH,
       "SlipoverPathTray",
       size=(55.0, 55.0, 20.0),
       path=t_path,
       lid=LidBuilder(text="T-TRAY"),
   )
   project.show(show_lids=True)

Building a Game Box Insert
--------------------------

When designing an insert for a retail board game, the goal is to pack multiple sub-boxes snugly into the publisher's cardboard box, leaving room at the top for folded boards and rulebooks.

To build a full insert:

1. Measure the inside dimensions of the cardboard game box ``(width, length, height)`` in mm.
2. Pass ``game_box_size=(W, L, H)`` to :class:`~pyboxbuilder.project.core.Project`.
3. Set ``board_thickness`` to reserve height at the top for the game board and rulebook.
4. Set ``generate_spacers=True`` to automatically fill leftover voids with custom-fit spacer trays.

Arranging Boxes & Generating Spacers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can position boxes declaratively using :func:`~pyboxbuilder.layout.columns`, :func:`~pyboxbuilder.layout.rows`, and :func:`~pyboxbuilder.layout.stack`, or explicit coordinates, and let the spacer generator compute the rest:

.. pythonscad-example::

    from pyboxbuilder import BoxType, Project

    # Define the game box interior: 100mm x 90mm x 28mm
    project = Project(
        "GameInsertDemo",
        game_box_size=(100.0, 90.0, 28.0),
        board_thickness=6.0,   # Leaves 6mm at the top for the board
        generate_spacers=True, # Auto-fills dead space with open trays
    )

    # Box 1: An open card caddy
    project.box(
        BoxType.NO_LID,
        "Cards",
        size=(46.0, 50.0, 20.0),
        position=(2.0, 2.0, 0.0),
    )

    # Box 2: A sliding token box
    project.box(
        BoxType.SLIDING,
        "Tokens",
        size=(46.0, 50.0, 20.0),
        position=(50.0, 2.0, 0.0),
    )

    project.show(show_lids=True)

In this preview:

* The **Cards** and **Tokens** boxes are placed side-by-side.
* The remaining void along the back of the game box is automatically detected and filled with a custom-fitted spacer tray (``Spacer_...``).
* When packed into the game box, the components and spacers lock together to prevent shifting when the game is stored vertically.

Exporting and 3D Printing with CLI
----------------------------------

Every script can be run through the unified CLI entrypoint :func:`~pyboxbuilder.run`:

.. code-block:: python

    from pyboxbuilder import BoxType, Project, run

    project = Project("MyInsert", game_box_size=(295.0, 295.0, 70.0))
    # ... define boxes ...

    if __name__ == "__main__":
        run(project)

Command-Line Usage
~~~~~~~~~~~~~~~~~~

Preview in PythonSCAD:

.. code-block:: bash

    python my_insert.py

Preview with all lids included:

.. code-block:: bash

    python my_insert.py --lids

Preview only a specific box:

.. code-block:: bash

    python my_insert.py --box Tokens

Export printable 3MF / STL files:

.. code-block:: bash

    python my_insert.py --export --out ./output/

Next Steps
----------

* Explore all available lid mechanisms and box styles in :doc:`box_types`.
* Learn advanced multi-column layouts and custom spacer options in :doc:`layout_and_spacers`.
* Browse the full class and method documentation in the :doc:`api`.
