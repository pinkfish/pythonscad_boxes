Quickstart Guide
================

Welcome to ``pyboxbuilder``! This quickstart provides runnable, copy-pasteable examples for getting up and running quickly with parametric board game inserts and 3D printable boxes.

.. note::
   All 3D interactive views below are rendered directly by PythonSCAD via the ``.. pythonscad-example::`` directive. You can click and drag to rotate, right-click to pan, and scroll to zoom.

Prerequisites & Installation
----------------------------

``pyboxbuilder`` requires Python 3.12+ and PythonSCAD:

.. code-block:: sh

   python3 -m venv .venv && source .venv/bin/activate
   pip install -e ".[dev]"

The Single Import
-----------------

Every primary tool in the library can be imported from the top-level package:

.. code-block:: python

   from pyboxbuilder import (
       BoxType, Color, Cut, FingerCut, LabelMode, LidBuilder,
       PatternBuilder, PatternType, Project, ScoopSide,
       columns, rows, stack, run,
   )

Core Scenarios
--------------

Scenario 1: Sizing a Card Box from its Cards
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Instead of calculating internal wall allowances and stack heights by hand, define the card dimensions and count. The library automatically derives the compartment well dimensions, wall clearances, floor thickness, and box height:

.. pythonscad-example::

   project = Project("CardGame", game_box_size=(200.0, 150.0, 90.0))
   cards = project.box(
       BoxType.SLIDING,
       "Cards",
       size=(70.0, 100.0, None),
       lid=LidBuilder(label_mode=LabelMode.FRAMED, frame_color=Color("gold")).titled("Cards"),
   )
   cards.cards("Deck", count=120, size=(63.5, 88.0))
   project.show(show_lids=True)

Scenario 2: Tabletop Token Tray with Rounded Scoops
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create an open token tray for loose pieces during play. Specifying ``holds_pieces=True`` and ``cut=FingerCut.SCOOP`` rounds the bottom corners into ergonomic scoops so tokens can be swept out with a fingertip:

.. pythonscad-example::

   project = Project("Tokens", game_box_size=(200.0, 150.0, 60.0))
   tokens = project.box(BoxType.NO_LID, "Tokens", size=(80.0, 60.0, 25.0))
   tokens.compartment("Wood", holds_pieces=True, cut=FingerCut.SCOOP)
   project.show()

Scenario 3: Dividing a Box Evenly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Divide a tray interior evenly using relative width ratios (``width_ratio=0.25``). The library computes dividing walls and floor spacing without overflowing:

.. pythonscad-example::

   project = Project("Divided", game_box_size=(200.0, 150.0, 60.0))
   box = project.box(BoxType.NO_LID, "Sorted", size=(100.0, 80.0, 30.0))
   for i in range(4):
       box.compartment(f"Slot{i + 1}", width_ratio=0.25)
   project.show()

Scenario 4: Reusable Lid Styles with Surface Patterns
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Define a single :class:`~pyboxbuilder.lid.builder.LidBuilder` style with geometric patterns and labels, then apply it consistently across multiple boxes:

.. pythonscad-example::

   project = Project("FancyGame", game_box_size=(300.0, 200.0, 80.0))
   style = LidBuilder(
       label_mode=LabelMode.FRAMELESS,
       diagonal=True,
       pattern=PatternBuilder(type=PatternType.HEX, spacing=10.0),
   )
   for name, colour in (("Treasure", "gold"), ("Traps", "crimson"), ("Loot", "teal")):
       project.box(
           BoxType.SLIDING,
           name,
           size=(90.0, 70.0, 40.0),
           lid=style.titled(name, text_color=Color(colour)),
       )
   project.show(show_lids=True)

Scenario 5: Minimum Text Height Guard
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If a box lid is too small for readable text (under 4mm font height), the label is safely omitted rather than printed as an unreadable smudge:

.. pythonscad-example::

   project = Project("TinyGame", game_box_size=(100.0, 80.0, 30.0))
   project.box(BoxType.SLIDING, "Tiny", size=(30.0, 20.0, 20.0), lid=LidBuilder(text="A"))
   project.show(show_lids=True)

Scenario 6: Manual Spatial Arrangement
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Compose relative spatial layouts using :func:`~pyboxbuilder.layout.columns`, :func:`~pyboxbuilder.layout.rows`, and :func:`~pyboxbuilder.layout.stack`:

.. pythonscad-example::

   project = Project("BigGame", game_box_size=(300.0, 200.0, 80.0))
   project.box(BoxType.SLIDING, "CardBox", size=(110.0, 75.0, 50.0))
   project.box(BoxType.CAP, "TokenBox", size=(60.0, 50.0, 30.0))
   project.box(BoxType.CAP, "DiceBox", size=(60.0, 50.0, 30.0))
   project.box(BoxType.FILAMENT_HINGE, "BitBox", size=(80.0, 60.0, 40.0))
   project.arrange(columns("CardBox", stack("TokenBox", "DiceBox"), "BitBox"))
   project.show(show_lids=True)

Scenario 7: Box Sized Entirely by its Contents
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Omit the outer size entirely and let the box's footprint and height follow automatically from internal compartment dimensions and push-through holes:

.. pythonscad-example::

   project = Project("ComputedBox", game_box_size=(200.0, 150.0, 60.0))
   cards = project.box(BoxType.SLIDING, "CardBox")
   cards.compartment("Deck", size=(90.0, 65.0), depth=45.0, cut=FingerCut.THROUGH_FLOOR)
   cards.compartment("SideSlot", size=(55.0, 45.0), depth=25.0)
   project.show(show_lids=True)

Scenario 8: Script Entry Point
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make scripts executable directly via PythonSCAD GUI or batch command line:

.. code-block:: python

   if __name__ == "__main__":
       run(project)

Quick Start by Box Type
-----------------------

Below is a simple, copy-pasteable quick start for all 23 box types in ``pyboxbuilder``:

Sliding Lid (``BoxType.SLIDING``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. pythonscad-example::

   project = Project("DrawerDemo", game_box_size=(80.0, 80.0, 30.0))
   project.box(
       BoxType.SLEEVE_DRAWER,
       "MatchboxDrawer",
       size=(60.0, 50.0, 22.0),
       drawer_pull_lip=4.0,
   )
   project.show(show_lids=True)

Print-In-Place Hinge Box (``BoxType.PRINT_IN_PLACE_HINGE``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. pythonscad-example::

   project = Project("FilamentHingeDemo", game_box_size=(80.0, 80.0, 30.0))
   project.box(
       BoxType.FILAMENT_HINGE,
       "PinBox",
       size=(60.0, 50.0, 22.0),
       lid=LidBuilder(text="GEAR"),
   )
   project.show(show_lids=True)

Snap-Fit Cantilever Latch (``BoxType.SNAP_FIT``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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

Gravity Tile & Token Dispenser (``BoxType.DISPENSER``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. pythonscad-example::

   project = Project("StackDemo", game_box_size=(80.0, 80.0, 40.0))
   b1 = project.box(
       BoxType.NO_LID,
       "TrayLower",
       size=(60.0, 60.0, 16.0),
       position=(0.0, 0.0, 0.0),
       stackable=StackableMode.INSIDE,
   )
   b2 = project.box(
       BoxType.NO_LID,
       "TrayUpper",
       size=(60.0, 60.0, 16.0),
       position=(0.0, 0.0, 16.0),
       stackable=StackableMode.INSIDE,
   )
   project.show()

Modular Vertical Card Divider Library (``BoxType.CARD_LIBRARY``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. pythonscad-example::

   project = Project("CardLibDemo", game_box_size=(80.0, 100.0, 35.0))
   project.box(
       BoxType.CARD_LIBRARY,
       "Deck",
       size=(55.0, 80.0, 25.0),
   )
   project.show(show_lids=True)

Custom Polygonal Footprint (``BoxType.PATH``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
       "CornerTray",
       size=(55.0, 55.0, 20.0),
       path=l_path,
   )
   project.show()

Custom Footprint with Drop-On Cap (``BoxType.CAP_PATH``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

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
   )
   project.show(show_lids=True)

Custom Footprint with Slipover Sleeve (``BoxType.SLIPOVER_PATH``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. pythonscad-example::

   project = Project("SlipPathDemo", game_box_size=(80.0, 80.0, 30.0))
   l_path = (
       (0.0, 0.0),
       (55.0, 0.0),
       (55.0, 25.0),
       (25.0, 25.0),
       (25.0, 55.0),
       (0.0, 55.0),
   )
   project.box(
       BoxType.SLIPOVER_PATH,
       "SlipPathTray",
       size=(55.0, 55.0, 20.0),
       path=l_path,
   )
   project.show(show_lids=True)
