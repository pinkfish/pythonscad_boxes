Box Types Guide & Gallery
==========================

``pyboxbuilder`` provides a comprehensive family of 25 box closure mechanisms, tray configurations, and custom footprint types. Each box type (:class:`~pyboxbuilder.enums.BoxType`) is coupled with a dedicated typed builder in :mod:`pyboxbuilder.builders` tailored for specific physical 3D printing requirements, component security, and ease of access during gameplay.

This gallery demonstrates each box type with an interactive 3D STL viewer powered by PythonSCAD. You can rotate, pan, and zoom each model directly in your browser.

.. list-table:: Quick Reference: All 25 Box Types
   :widths: 30 30 40
   :header-rows: 1

   * - Box Type
     - Closure Family
     - Typed Builder
   * - :ref:`BoxType.SLIDING <box-type-sliding>`
     - Sliding & Friction
     - :class:`~pyboxbuilder.builders.sliding.SlidingBoxBuilder`
   * - :ref:`BoxType.SLIDING_CATCH <box-type-sliding-catch>`
     - Sliding & Friction
     - :class:`~pyboxbuilder.builders.sliding_catch.SlidingCatchBoxBuilder`
   * - :ref:`BoxType.CAP <box-type-cap>`
     - Sliding & Friction
     - :class:`~pyboxbuilder.builders.cap.CapBoxBuilder`
   * - :ref:`BoxType.CAP_PATH <box-type-cap-path>`
     - Custom Polygons
     - :class:`~pyboxbuilder.builders.cap_path.CapPathBoxBuilder`
   * - :ref:`BoxType.SLIPOVER <box-type-slipover>`
     - Sliding & Friction
     - :class:`~pyboxbuilder.builders.slipover.SlipoverBoxBuilder`
   * - :ref:`BoxType.SLIPOVER_PATH <box-type-slipover-path>`
     - Custom Polygons
     - :class:`~pyboxbuilder.builders.slipover_path.SlipoverPathBoxBuilder`
   * - :ref:`BoxType.FILAMENT_HINGE <box-type-filament-hinge>`
     - Hinges & Bifolds
     - :class:`~pyboxbuilder.builders.filament_hinge.FilamentHingeBoxBuilder`
   * - :ref:`BoxType.MAGNETIC_HINGE <box-type-magnetic-hinge>`
     - Hinges & Bifolds
     - :class:`~pyboxbuilder.builders.magnetic_hinge.MagneticHingeBoxBuilder`
   * - :ref:`BoxType.MAGNETIC <box-type-magnetic>`
     - Mechanical & Magnetic
     - :class:`~pyboxbuilder.builders.magnetic.MagneticBoxBuilder`
   * - :ref:`BoxType.INSET <box-type-inset>`
     - Sliding & Friction
     - :class:`~pyboxbuilder.builders.inset.InsetBoxBuilder`
   * - :ref:`BoxType.NO_LID <box-type-no-lid>`
     - Open & Stackable Trays
     - :class:`~pyboxbuilder.builders.no_lid.NoLidBoxBuilder`
   * - :ref:`BoxType.CARD_LIBRARY <box-type-card-library>`
     - Tabletop Utilities
     - :class:`~pyboxbuilder.builders.card_library.CardLibraryBoxBuilder`
   * - :ref:`BoxType.PATH <box-type-path>`
     - Custom Polygons
     - :class:`~pyboxbuilder.builders.path.PathBoxBuilder`
   * - :ref:`BoxType.SNAP_FIT <box-type-snap-fit>`
     - Mechanical & Magnetic
     - :class:`~pyboxbuilder.builders.snap_fit.SnapFitBoxBuilder`
   * - :ref:`BoxType.BAYONET <box-type-bayonet>`
     - Mechanical & Magnetic
     - :class:`~pyboxbuilder.builders.bayonet.BayonetBoxBuilder`
   * - :ref:`BoxType.THREADED <box-type-threaded>`
     - Mechanical & Magnetic
     - :class:`~pyboxbuilder.builders.threaded.ThreadedBoxBuilder`
   * - :ref:`BoxType.DISPENSER <box-type-dispenser>`
     - Tabletop Utilities
     - :class:`~pyboxbuilder.builders.dispenser.DispenserBoxBuilder`
   * - :ref:`BoxType.CARD_SHOE <box-type-card-shoe>`
     - Tabletop Utilities
     - :class:`~pyboxbuilder.builders.card_shoe.CardShoeBoxBuilder`
   * - :ref:`BoxType.DICE_TRAY <box-type-dice-tray>`
     - Tabletop Utilities
     - :class:`~pyboxbuilder.builders.dice_tray.DiceTrayBoxBuilder`
   * - :ref:`BoxType.SLEEVE_DRAWER <box-type-sleeve-drawer>`
     - Sliding & Friction
     - :class:`~pyboxbuilder.builders.sleeve_drawer.SleeveDrawerBoxBuilder`
   * - :ref:`BoxType.CLAMSHELL <box-type-clamshell>`
     - Hinges & Bifolds
     - :class:`~pyboxbuilder.builders.clamshell.ClamshellBoxBuilder`
   * - :ref:`BoxType.MODULAR_INTERLOCK <box-type-modular-interlock>`
     - Tabletop Utilities
     - :class:`~pyboxbuilder.builders.modular_interlock.ModularInterlockBoxBuilder`
   * - :ref:`BoxType.PRINT_IN_PLACE_HINGE <box-type-print-in-place-hinge>`
     - Hinges & Bifolds
     - :class:`~pyboxbuilder.builders.pip_hinge.PrintInPlaceHingeBoxBuilder`
   * - :ref:`BoxType.INSET_HINGE <box-type-inset-hinge>`
     - Hinges & Bifolds
     - :class:`~pyboxbuilder.builders.inset_hinge.InsetHingeBoxBuilder`
   * - :ref:`BoxType.SLIDING_HINGE <box-type-sliding-hinge>`
     - Hinges & Bifolds
     - :class:`~pyboxbuilder.builders.sliding_hinge.SlidingHingeBoxBuilder`

.. contents:: On this page
   :local:
   :depth: 2


.. _box-type-sliding:

Sliding Lid (``BoxType.SLIDING``)
---------------------------------

**Builder**: :class:`~pyboxbuilder.builders.sliding.SlidingBoxBuilder`

The sliding dovetail box features integrated side rails along which the lid slides smoothly open and shut. The sliding axis defaults to the length (Y-axis), but can be configured along the width (X-axis) via ``lid_slide_axis="x"``.

It is ideal for token boxes, card decks, and trays where the lid should remain captive without extra hardware.

.. pythonscad-example::

   project = Project("SlidingDemo")
   box = project.box(
       BoxType.SLIDING,
       "Tokens",
       size=(60.0, 60.0, 22.0),
       color=Color("darkslateblue"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.HEX, spacing=8.0),
       ).titled("TOKENS"),
   )
   box.compartment("Gold", width_ratio=0.5, holds_pieces=True)
   box.compartment("Silver", width_ratio=0.5, holds_pieces=True)
   project.show(show_lids=True)


.. _box-type-sliding-catch:

Sliding Catch Lid (``BoxType.SLIDING_CATCH``)
---------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.sliding_catch.SlidingCatchBoxBuilder`

A variant of the sliding dovetail box equipped with a detent bump and fingernail catch at the leading edge. When closed, the lid snaps securely into place, preventing accidental opening inside a game box stored vertically on a shelf.

.. pythonscad-example::

   project = Project("CatchDemo")
   box = project.box(
       BoxType.SLIDING_CATCH,
       "CatchBox",
       size=(60.0, 60.0, 22.0),
       color=Color("crimson"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("silver"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.TRIANGLE, spacing=9.0),
       ).titled("LOCKED"),
   )
   box.compartment("Gems", width_ratio=0.5, holds_pieces=True)
   box.compartment("Crystals", width_ratio=0.5, holds_pieces=True)
   project.show(show_lids=True)


.. _box-type-cap:

Drop-On Cap Lid (``BoxType.CAP``)
---------------------------------

**Builder**: :class:`~pyboxbuilder.builders.cap.CapBoxBuilder`

A friction-fit cap lid that drops straight onto the box body from above. Supports standard rectangular boxes as well as arbitrary polygon footprints via ``path``. The lid incorporates side finger cutouts (:class:`~pyboxbuilder.box.features.CapFingerMetrics`) that reveal the box body beneath, allowing easy removal by pinching the sides.

Cap boxes are well-suited for player trays, resource banks, and modular organizers where components are unpacked immediately onto the table.

.. pythonscad-example::

   project = Project("CapDemo")
   box = project.box(
       BoxType.CAP,
       "PlayerTray",
       size=(60.0, 60.0, 22.0),
       color=Color("darkgreen"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.OCTAGON, spacing=8.0),
       ).titled("PLAYER 1"),
   )
   box.compartment("LeftWell", width_ratio=0.5, holds_pieces=True)
   box.compartment("RightWell", width_ratio=0.5, holds_pieces=True)
   project.show(show_lids=True)


.. _box-type-cap-path:

Cap Lid on Polygon Footprint (``BoxType.CAP_PATH``)
---------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.cap_path.CapPathBoxBuilder`

Combines the drop-on friction cap lid with an arbitrary 2D polygon footprint. The cap's skirt wraps around the outer perimeter of the polygonal tray, providing a clean friction-fit closure for L-shaped, T-shaped, or irregular spaces.

.. pythonscad-example::

   project = Project("CapPathDemo")
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
       color=Color("teal"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           text_color=Color("white"),
           frame_color=Color("silver"),
           border_margin_mm=3.0,
           pattern=PatternBuilder(PatternType.HEX, spacing=8.0),
       ).titled("PARTS"),
   )
   project.show(show_lids=True)


.. _box-type-slipover:

Telescoping Slipover Lid (``BoxType.SLIPOVER``)
-----------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.slipover.SlipoverBoxBuilder`

A classic two-piece shoebox closure where the lid walls telescope down over the full height of the body. Supports standard rectangular boxes as well as arbitrary polygon footprints via ``path``. Internal air-release clearances ensure a smooth slide fit without vacuum resistance.

Slipover lids provide high structural rigidity and a clean exterior finish.

.. pythonscad-example::

   project = Project("SlipoverDemo")
   box = project.box(
       BoxType.SLIPOVER,
       "MiniDeck",
       size=(55.0, 70.0, 26.0),
       color=Color("midnightblue"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("cornflowerblue"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.CIRCLE, spacing=8.0),
       ).titled("CARDS"),
   )
   box.compartment("Deck", holds_pieces=True)
   project.show(show_lids=True)


.. _box-type-slipover-path:

Slipover on Polygon Footprint (``BoxType.SLIPOVER_PATH``)
---------------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.slipover_path.SlipoverPathBoxBuilder`

A polygonal sleeve enclosure designed to slide over a custom 2D polygon body tray. It stops against a configurable base foot, creating a full-height outer sleeve for irregular modular organizers.

.. pythonscad-example::

   project = Project("SlipPathDemo")
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
       color=Color("darkcyan"),
   )
   project.show(show_lids=True)


.. _box-type-filament-hinge:

Filament Pin Hinge (``BoxType.FILAMENT_HINGE``)
-----------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.filament_hinge.FilamentHingeBoxBuilder`

A compact, durable two-piece hinged box whose interleaving rear knuckles are bored to accept a short length of standard 1.75 mm 3D printing filament (or configurable pin diameter via ``filament_diameter`` and ``hinge_count``) as the hinge pin, paired with a front snap catch. Because the pin is inserted post-print, the hinge barrels can be smaller and tighter than print-in-place tolerances permit.

.. pythonscad-example::

   project = Project("FilamentHingeDemo")
   box = project.box(
       BoxType.FILAMENT_HINGE,
       "PinBox",
       size=(60.0, 50.0, 22.0),
       color=Color("indigo"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("mediumpurple"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.SQUARE, spacing=8.0),
       ).titled("GEAR"),
   )
   box.compartment("Dice", holds_pieces=True)
   project.show(show_lids=True)


.. _box-type-magnetic-hinge:

Magnetic Pin Hinge (``BoxType.MAGNETIC_HINGE``)
-----------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.magnetic_hinge.MagneticHingeBoxBuilder`

Combines a rear filament pin hinge with a support-free front magnet boss and matching blind magnet sockets in the front body rim and lid underside (``magnet_diameter`` default 4.0 mm, ``magnet_height`` default 2.0 mm) so the hinged lid snaps and stays closed magnetically.

.. pythonscad-example::

   project = Project("MagneticHingeDemo")
   box = project.box(
       BoxType.MAGNETIC_HINGE,
       "MagChest",
       size=(60.0, 50.0, 22.0),
       color=Color("saddlebrown"),
       magnet_diameter=4.0,
       magnet_height=2.0,
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.VORONOI, spacing=8.0),
       ).titled("CHEST"),
   )
   box.compartment("Coins", width_ratio=0.5, holds_pieces=True)
   box.compartment("Loot", width_ratio=0.5, holds_pieces=True)
   project.show(show_lids=True)


.. _box-type-magnetic:

Magnetic Closure Lid (``BoxType.MAGNETIC``)
-------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.magnetic.MagneticBoxBuilder`

Recesses precision magnet cavities (:class:`~pyboxbuilder.enums.MagnetType`) into the walls of both the box body and lid. Small cylindrical (e.g. 6x3 mm) or rectangular neodymium magnets glued into the sockets provide a snap closure with a flush perimeter.

.. pythonscad-example::

   project = Project("MagneticDemo")
   box = project.box(
       BoxType.MAGNETIC,
       "Vault",
       size=(60.0, 60.0, 22.0),
       color=Color("darkslategray"),
       magnet_type=MagnetType.ROUND,
       magnet_diameter=6.0,
       magnet_height=3.0,
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("coral"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.HEX, spacing=8.0),
       ).titled("VAULT"),
   )
   box.compartment("Relics", width_ratio=0.5, holds_pieces=True)
   box.compartment("Keys", width_ratio=0.5, holds_pieces=True)
   project.show(show_lids=True)


.. _box-type-inset:

Inset Flush Lid (``BoxType.INSET``)
-----------------------------------

**Builder**: :class:`~pyboxbuilder.builders.inset.InsetBoxBuilder`

The inset lid sits flush with the top lip of the box, resting on a stepped internal rabbet shelf carved into the interior perimeter wall. A finger cutout allows the lid to be levered or lifted out.

Inset boxes maximize usable height in tight game boxes where external lid rims would consume too much vertical clearance.

.. pythonscad-example::

   project = Project("InsetDemo")
   box = project.box(
       BoxType.INSET,
       "FlushTray",
       size=(60.0, 60.0, 22.0),
       color=Color("maroon"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.TRIANGLE, spacing=8.0),
       ).titled("TILES"),
   )
   box.compartment("Tiles", holds_pieces=True)
   project.show(show_lids=True)


.. _box-type-no-lid:

Open & Stackable Trays (``BoxType.NO_LID``)
-------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.no_lid.NoLidBoxBuilder`

Open organizer trays without a lid. Supports standard rectangular boxes as well as arbitrary polygon footprints via ``path``. When ``stackable`` is enabled (:class:`~pyboxbuilder.enums.StackableMode`), an interlocking step rim is added:

- ``StackableMode.INSIDE``: A stepped inner recess in the top rim that the tray above nests down into.
- ``StackableMode.OUTSIDE``: A perimeter skirt around the outside base that fits over the tray below.

Stacked trays cannot slide off each other during play or transport.

.. pythonscad-example::

   project = Project("StackDemo")
   b1 = project.box(
       BoxType.NO_LID,
       "TrayLower",
       size=(60.0, 60.0, 16.0),
       color=Color("darkcyan"),
       position=(0.0, 0.0, 0.0),
       stackable=StackableMode.INSIDE,
   )
   b1.compartment("CubesA", width_ratio=0.5, holds_pieces=True)
   b1.compartment("CubesB", width_ratio=0.5, holds_pieces=True)
   b2 = project.box(
       BoxType.NO_LID,
       "TrayUpper",
       size=(60.0, 60.0, 16.0),
       color=Color("coral"),
       position=(0.0, 0.0, 16.0),
       stackable=StackableMode.INSIDE,
   )
   b2.compartment("Tokens", holds_pieces=True)
   project.show()


.. _box-type-card-library:

Card Library Box (``BoxType.CARD_LIBRARY``)
-------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.card_library.CardLibraryBoxBuilder`

A specialized card storage box optimized for card decks. It supports standard card sizes or custom dimensions (sleeved or unsleeved via :class:`~pyboxbuilder.helpers.CardSpec`), and incorporates thumb push-through holes or wall scoops (:class:`~pyboxbuilder.enums.FingerCut`) to extract tightly packed decks.

.. pythonscad-example::

   project = Project("CardLibDemo")
   project.box(
       BoxType.CARD_LIBRARY,
       "Deck",
       size=(55.0, 80.0, 25.0),
       color=Color("darkblue"),
   )
   project.show(show_lids=True)


.. _box-type-path:

Polygon Footprint Path Box (``BoxType.PATH``)
---------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.path.PathBoxBuilder`

When rectangular boxes cannot fit around game boards, player mats, or non-rectangular components, ``BoxType.PATH`` builds an open tray whose exterior footprint follows any arbitrary closed 2D polygon path.

.. pythonscad-example::

   project = Project("PathDemo")
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
       color=Color("forestgreen"),
   )
   project.show()


.. _box-type-snap-fit:

Snap-Fit Cantilever Latch (``BoxType.SNAP_FIT``)
------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.snap_fit.SnapFitBoxBuilder`

Features integrated downward-extending cantilever spring arms on opposing walls with positive retention detents (a 45° lead-in ramp and flat horizontal lock shoulder), mating with matching catch pockets recessed into the box body. Thumb pressure on the upper tab face deflects the detents inward to release the lid.

.. pythonscad-example::

   project = Project("SnapFitDemo")
   box = project.box(
       BoxType.SNAP_FIT,
       "SnapBox",
       size=(60.0, 50.0, 24.0),
       color=Color("darkmagenta"),
       cantilever_thickness=2.0,
       cantilever_width=14.0,
       detent_height=0.8,
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.HEX, spacing=8.0),
       ).titled("SNAP"),
   )
   box.compartment("PawnWell", holds_pieces=True)
   project.show(show_lids=True)


.. _box-type-bayonet:

Twist-Lock Bayonet Container (``BoxType.BAYONET``)
--------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.bayonet.BayonetBoxBuilder`

Designed for cylindrical or rounded footprints, the lid and body mate via a quarter-turn (90°) or eighth-turn (45°) bayonet mechanism. The lid features internal retention lugs that enter vertical entry keyways in the box rim and rotate into horizontal retention channels terminating in tactile detent stops.

.. pythonscad-example::

   project = Project("BayonetDemo")
   project.box(
       BoxType.BAYONET,
       "BayonetCanister",
       size=(55.0, 55.0, 35.0),
       color=Color("teal"),
       lug_count=4,
       turn_angle=90.0,
   )
   project.show(show_lids=True)


.. _box-type-threaded:

Threaded Screw Box (``BoxType.THREADED``)
-----------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.threaded.ThreadedBoxBuilder`

Container with helical male/female screw threads on a circular cylindrical profile. The thread profile uses a coarse modified trapezoidal geometry with flat crests and roots (default pitch 3.0mm) and calibrated radial clearance to prevent layer binding, terminating at a flush seating shoulder.

.. pythonscad-example::

   project = Project("ThreadedDemo")
   project.box(
       BoxType.THREADED,
       "ThreadedJar",
       size=(50.0, 50.0, 32.0),
       color=Color("darkolivegreen"),
       thread_pitch=3.0,
       thread_turns=2.0,
   )
   project.show(show_lids=True)


.. _box-type-dispenser:

Gravity Tile & Token Dispenser (``BoxType.DISPENSER``)
------------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.dispenser.DispenserBoxBuilder`

Designed for cardboard tiles (e.g. Carcassonne, Catan), poker chips, or resource tokens during gameplay. Features a top loading chute, a flat internal floor by default (or a configurable angled slide ramp via ``chute_angle`` / ``tile_angle``), a horizontal bottom dispensing slot, a vertical sight slot to monitor remaining stack height, and a curved front finger scoop + bottom floor cutout so you can pinch and pull out the bottom tile with your fingers.

.. pythonscad-example::

   project = Project("DispenserDemo")
   project.box(
       BoxType.DISPENSER,
       "TileChute",
       size=(55.0, 55.0, 70.0),
       color=Color("darkred"),
       token_thickness=3.0,
   )
   project.show(show_lids=True)


.. _box-type-card-shoe:

Angled Draw & Discard Card Shoe (``BoxType.CARD_SHOE``)
-------------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.card_shoe.CardShoeBoxBuilder`

In-game tabletop utility tray with adjacent draw and discard wells. The draw well features a backward-slanted floor and backrest (15°–25° from vertical) with a low front retaining lip to prevent tall draw stacks from toppling while enabling easy one-card-at-a-time draw. The discard well is flat with opposing U-shaped edge finger scoops.

.. pythonscad-example::

   project = Project("CardShoeDemo")
   project.box(
       BoxType.CARD_SHOE,
       "ShoeTray",
       size=(130.0, 85.0, 42.0),
       color=Color("midnightblue"),
       draw_angle=20.0,
       retaining_lip_height=10.0,
       discard_well=True,
   )
   project.show(show_lids=True)


.. _box-type-dice-tray:

Dice Tray & Rolling Arena (``BoxType.DICE_TRAY``)
-------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.dice_tray.DiceTrayBoxBuilder`

A dual-purpose container where the body stores dice or tokens and the deep nesting lid doubles as an active tabletop dice rolling arena. The lid perimeter walls rise at least 25mm above the tray floor with 45° internal corner fillets to bounce rolling dice back toward the center, and a recessed acoustic pad pocket for adhesive felt. In multi-material (MMU) mode, the lid defaults to an inlaid gaming dice pattern (D6 faces) with contrasting title text and pips without cutting through-holes into the rolling arena.

.. pythonscad-example::

   project = Project("DiceTrayDemo")
   box = project.box(
       BoxType.DICE_TRAY,
       "ArenaBox",
       size=(120.0, 90.0, 36.0),
       color=Color("purple"),
       arena_wall_height=28.0,
       felt_pocket_depth=1.2,
   )
   box.compartment("DiceStorage", holds_pieces=True)
   project.show(show_lids=True)


.. _box-type-sleeve-drawer:

Matchbox Sleeve & Drawer (``BoxType.SLEEVE_DRAWER``)
----------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.sleeve_drawer.SleeveDrawerBoxBuilder`

A two-piece matchbox assembly consisting of a hollow 4-sided outer perimeter sleeve and an inner sliding compartment drawer, enabling horizontal drawer access without removing stacked trays above it. The drawer is a solid container with an integrated front pull handle, and the sleeve features a solid back wall (with an optional push-through hole).

.. pythonscad-example::

   project = Project("SleeveDrawerDemo")
   box = project.box(
       BoxType.SLEEVE_DRAWER,
       "DrawerBox",
       size=(70.0, 60.0, 28.0),
       color=Color("sienna"),
       drawer_handle_style="handle",
       drawer_handle_length=4.0,
   )
   box.compartment("Cards", holds_pieces=True)
   project.show(show_lids=True)


.. _box-type-clamshell:

Bifold Clamshell Book Box (``BoxType.CLAMSHELL``)
-------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.clamshell.ClamshellBoxBuilder`

Two symmetrical tray halves joined along a central filament-pin spine hinge, unfolding 180° flat onto the table so both halves serve as accessible token or card trays during play. A standard 1.75mm filament strand threads through the interleaved spine knuckles after printing, and a front snap catch holds the book securely closed during storage.

.. pythonscad-example::

   project = Project("ClamshellDemo")
   project.box(
       BoxType.CLAMSHELL,
       "BookBox",
       size=(90.0, 65.0, 32.0),
       color=Color("darkslateblue"),
       filament_diameter=1.75,
       hinge_count=5,
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.HEX, spacing=8.0),
       ).titled("TOME"),
   )
   project.show(show_lids=True)


.. _box-type-modular-interlock:

Modular Interlocking Play Trays (``BoxType.MODULAR_INTERLOCK``)
---------------------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.modular_interlock.ModularInterlockBoxBuilder`

Trays featuring perimeter interlocking joints on outer walls to lock multiple boxes side-by-side into a unified player dashboard or shared bank on the table. Supports sliding dovetails (with 0.15mm clearance) and Gridfinity-compatible tiered base profiles.

.. pythonscad-example::

   project = Project("ModularDemo")
   box = project.box(
       BoxType.MODULAR_INTERLOCK,
       "ModularTray",
       size=(65.0, 65.0, 24.0),
       color=Color("steelblue"),
       wall_thickness=4.0,
       interlock_type=InterlockType.DOVETAIL,
       dovetail_clearance=0.15,
   )
   box.compartment("Items", holds_pieces=True)
   project.show(show_lids=True)


.. _box-type-print-in-place-hinge:

Monolithic Print-In-Place Hinge Box (``BoxType.PRINT_IN_PLACE_HINGE``)
----------------------------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.pip_hinge.PrintInPlaceHingeBoxBuilder`

A single-piece, zero-assembly hinged box where body and lid are laid flat at 180° on the print bed in a single print job. Joined by an interlocking print-in-place knuckle hinge in the middle section along the shared mating rim at ``z = height / 2.0`` with calibrated radial and axial air gaps and 45° self-supporting overhang chamfers, complemented by a snap-fit ridge catch on the front walls.

.. pythonscad-example::

   project = Project("PIPHingeDemo")
   box = project.box(
       BoxType.PRINT_IN_PLACE_HINGE,
       "HingedBox",
       size=(60.0, 45.0, 22.0),
       color=Color("forestgreen"),
       pip_bridge_width=0.40,
       pip_bridge_thickness=0.40,
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.HEX, spacing=8.0),
       ).titled("PIPKIT"),
   )
   box.compartment("Tools", holds_pieces=True)
   project.show(show_lids=True)


.. _box-type-inset-hinge:

Print-In-Place Inset Hinge Box (``BoxType.INSET_HINGE``)
--------------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.inset_hinge.InsetHingeBoxBuilder`

A second print-in-place hinged box variant based on ``MakeBoxAndLidWithInsetHinge`` from ``hinge_box.scad``. The base and lid halves sit side-by-side along the X axis separated by ``2 * pip_radial_clearance`` (default ``0.60 mm``) and are joined by a recessed print-in-place conical knuckle hinge (``InsetHinge``) with 45° self-supporting mounting brackets, a self-aligning perimeter rim and rabbet, and a front snap-latch tab (``MakeLidTab``).

.. pythonscad-example::

   project = Project("InsetHingeDemo")
   box = project.box(
       BoxType.INSET_HINGE,
       "InsetHingeBox",
       size=(60.0, 50.0, 26.0),
       color=Color("seagreen"),
       pip_hinge_radius=3.0,
       pip_radial_clearance=0.30,
   )
   box.compartment("Tokens", holds_pieces=True)
   project.show(show_lids=True)


.. _box-type-sliding-hinge:

Sliding & Spin Catch Hinge Box (``BoxType.SLIDING_HINGE``)
----------------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.sliding_hinge.SlidingHingeBoxBuilder`

A hinged-lid box that combines a rear filament-pin knuckle hinge with a print-in-place mechanical retention catch — defaulting to a captive horizontal dovetail sliding bolt (``CatchType.SLIDE_ACROSS``), with built-in support for ``CatchType.SLIDE_UP`` (vertical captive front-wall slider), ``CatchType.SPIN`` (print-in-place rotary cam / turn-button latch that hooks onto the lid when spun up and releases when spun down), ``CatchType.PUSH_BUTTON``, ``CatchType.TOGGLE_LATCH``, ``CatchType.PINCH_SLIDE``, and ``CatchType.ROTARY_BOLT``, as well as dual side-wall card-library sliding latches (``slide_catch_style="card_library"``).

.. pythonscad-example::

   project = Project("SlidingHingeDemo")
   box = project.box(
       BoxType.SLIDING_HINGE,
       "SlideHingeBox",
       size=(65.0, 50.0, 24.0),
       color=Color("darkslateblue"),
       catch_type=CatchType.SLIDE_ACROSS,
   )
   box.compartment("Deck", holds_pieces=True)
   project.show(show_lids=True)


Lid Retention Catches (``CatchType``)
-------------------------------------

All lidded box types requiring positive closure retention (sliding, cap, slipover, hinged, clamshell, snap-fit) support the unified :class:`~pyboxbuilder.enums.CatchType` mechanism (FR-099):

* **``CatchType.BUMP``** (``"bump"``): Spherical/hemispherical bump detents dropping into matching oversized clearance dimples (0.1mm clearance). Standard for sliding lids, cap boxes, and slipover boxes.
* **``CatchType.WEDGE``** (``"wedge"``): Asymmetric ramped wedge barbs/ridges featuring a low-force lead-in ramp (30°–45°) and a flat horizontal retaining shoulder that snaps into an undercut groove or shelf. Standard for hinged and cantilever snap-fit lids.
* **``CatchType.LOOP``** (``"loop"``): Flexible strap/loop tabs carrying an aperture window that clips over a matching retaining stud or hook on the opposing body wall.
* **``CatchType.MAGNET``** (``"magnet"``): Paired cylindrical pockets in lid and body sized for press-fit or adhesive aftermarket neodymium disc magnets (e.g. 3×2mm, 4×2mm, 6×3mm) with zero collision volume when closed.
* **``CatchType.LEAF_SPRING``** (``"leaf_spring"``): Compliant cantilever flexure arms with relief clearance slots cut behind detent beads, preventing PLA fatigue and wear across high cycles.
* **``CatchType.SLIDE_ACROSS``** (``"slide_across"``): Captive print-in-place horizontal dovetail sliding bolt in the lid that slides across into an undercut mortise roof in the body wall (supports ``slide_catch_style="front"`` or ``"card_library"`` dual side bolts).
* **``CatchType.SLIDE_UP``** (``"slide_up"``): Captive print-in-place vertical dovetail slider on the front wall that slides up (``+Z``) behind the lid's front strike bridge to lock and slides down (``-Z``) to release.
* **``CatchType.SPIN``** (``"spin"``): Print-in-place rotary turn-button / cam catch on the front wall using a 45° double-cone hourglass bearing; hooks onto the lid's front ledge when spun up (``0°``) and releases the lid when spun down (``90°–180°``).
* **``CatchType.PUSH_BUTTON``** (``"push_button"``): Compliant thumb-press flexure button on the front wall that deflects inward to release the lid's catch loop.
* **``CatchType.TOGGLE_LATCH``** (``"toggle_latch"``): Print-in-place articulated draw-latch bail on the front wall that hooks over the lid's front stud.
* **``CatchType.PINCH_SLIDE``** (``"pinch_slide"``): Dual opposing captive dovetail sliders on the lid front that pinch together toward the center to release both bolts simultaneously.
* **``CatchType.ROTARY_BOLT``** (``"rotary_bolt"``): Flush print-in-place quarter-turn rotary cam disk inside the lid that swings an eccentric locking bar under the front wall rim.
* **``CatchType.NONE``** (``"none"``): Generates a smooth friction fit or track slide without detent bumps, notches, or hooks.

Configure catches via ``catch_type`` and ``catch_size`` on any box builder:

.. code-block:: python

   # Sliding lid with magnet retention pockets:
   box = project.box(
       BoxType.SLIDING,
       "Tokens",
       size=(60.0, 60.0, 22.0),
       catch_type=CatchType.MAGNET,
       catch_size=4.0,  # 4mm magnet diameter
   )

   # Cap box with flexible loop retention:
   cap = project.box(
       BoxType.CAP,
       "Cards",
       size=(70.0, 50.0, 30.0),
       catch_type=CatchType.LOOP,
   )


Universal Stacking Architecture (``StackableMode``)
---------------------------------------------------

All lidless open trays (``NO_LID``, ``PATH``) and box types whose lids have a flat underside and print right-side up on the build plate (``SLIDING``, ``SLIDING_CATCH``, ``CARD_LIBRARY``, ``INSET`` without a front catch, ``MAGNETIC``, ``MODULAR_INTERLOCK``, and ``SLEEVE_DRAWER``) support the 3D-printer-safe :class:`~pyboxbuilder.enums.StackableMode` and :class:`~pyboxbuilder.enums.StackableShape` architecture (**FR-101**, **SC-101**, ``STACKABLE_BOX_TYPES``):

.. note::

   Box types whose lids have downward walls, skirts, hinge knuckles, or cantilever latches (such as ``CAP``, ``SLIPOVER``, ``CLAMSHELL``, ``FILAMENT_HINGE``, ``SNAP_FIT``, and ``PRINT_IN_PLACE_HINGE``) must be flipped upside down on the build plate to print. Because both the upside-down lid's top face and the upright box's bottom face are build-plate planes, passive top-boss stacking modes (``PYRAMIDS``, ``PYRAMID``, ``INDENTS``, ``FEET``, ``PERIMETER``, ``PATTERN``) raise a ``ValueError`` on those flipped-lid box types. Instead, use **``StackableMode.SLIDE_LATCH``** (or ``StackableMode.LATCH``) to stack flipped-lid boxes via captive print-in-place vertical dovetail push-up latches on the side walls!

* **``StackableMode.SLIDE_LATCH``** / **``StackableMode.LATCH``** (``"slide_latch"`` / ``"latch"``): **Captive print-in-place vertical dovetail push-up stacking latches** mounted on the opposing side walls of the box body (``LATCH_STACKABLE_BOX_TYPES``). Because the latch mechanism sits on the exterior side walls of the upright box body (with ``0.30 mm`` print-in-place clearance and 45° self-supporting slopes), both the box bottom (``z = 0``) and any flipped lid's top face (``z = height``) remain 100% flat on the print bed. When a second box is placed on top, pushing the side dovetail sliders upward bridges the seam and snaps into the matching bottom dovetail receiver sockets of the upper box.
* **``StackableMode.PATTERN``** (``"pattern"``): **Pattern-matched stacking** where the decorative pattern on the lid (e.g. ``PatternType.HEX``, ``TRIANGLE``, ``SQUARE``, ``PENROSE``, or whatever pattern is configured on the box/lid) is matched on the underside of the box body. On the bottom of the box (``z = 0``), the entire outer perimeter border and all the pattern tiles sit flat on the print bed while only the narrow web channels between the tiles are recessed with a 45° bevel; on top of the lid, a matching raised pattern web ridge locks into the bottom of the box stacked above it.
* **``StackableMode.PYRAMIDS``** (``"pyramids"``): A set/grid of $N \times N$ 45° square pyramid socket indents recessed into the flat ``z = 0`` bottom floor, mating with a matching grid of upward-pointing 45° pyramids on the lid/top rim. Eliminates wide unsupported bridges while keeping indentation depth shallow enough for standard floors and lids.
* **``StackableMode.PYRAMID``** (``"pyramid"``): A single 45° square pyramid socket recessed into each corner of the flat ``z = 0`` bottom floor, mating with a matching 45° pyramid boss on the lid/top rim.
* **``StackableMode.INDENTS``** (``"indents"``): Recessed corner sockets in the underside floor of the box body, and raised locator bosses projecting upward from the lid top deck or top rim (defaults to 45° ``StackableShape.PYRAMIDS``).
* **``StackableMode.FEET``** (``"feet"``): Corner locator pads and matching sockets. Keeps the box bottom flat on the build plate (``z = 0``) with recessed 45° pyramid sockets and upward-pointing top bosses so the box floor never prints in mid-air.
* **``StackableMode.PERIMETER``** (``"perimeter"``): Continuous 45° V-groove / V-ridge perimeter channel and matching rim around the box perimeter.
* **``StackableMode.INSIDE``** (``"inside"``): Stepped inner recess in the top rim that the tray above nests down into (standard for open trays).
* **``StackableMode.OUTSIDE``** (``"outside"``): Perimeter skirt around the outside base that fits over the tray below.

When stacked at nominal height, two identical boxes mate with zero collision volume (``volume(lower & upper) < 0.05mm³``) and positive horizontal slide resistance along both X and Y axes.

Configuration parameters available on all box builders:

.. list-table::
   :header-rows: 1
   :widths: 25 15 60

   * - Parameter
     - Default
     - Description
   * - ``stackable``
     - ``None``
     - :class:`~pyboxbuilder.enums.StackableMode` (``SLIDE_LATCH``, ``LATCH``, ``PATTERN``, ``PYRAMIDS``, ``PYRAMID``, ``INDENTS``, ``FEET``, ``PERIMETER``, ``INSIDE``, ``OUTSIDE``).
   * - ``stackable_shape``
     - ``None`` (auto)
     - :class:`~pyboxbuilder.enums.StackableShape` (``PATTERN`` for pattern-matched stacking, ``PYRAMIDS`` for a set of 45° pyramids, ``PYRAMID`` for a single 45° pyramid, ``CONE`` for 45° cones, or ``FLAT``).
   * - ``stackable_pattern``
     - ``None`` (from lid / ``HEX``)
     - :class:`~pyboxbuilder.enums.PatternType` used when ``stackable=StackableMode.PATTERN`` (automatically inherits from ``pattern`` / ``lid.pattern``, or defaults to ``PatternType.HEX``).
   * - ``stackable_pyramid_count``
     - ``None`` (auto)
     - Pyramid configuration per corner when using ``StackableShape.PYRAMIDS``: an ``int`` $N$ ($N \times N$ on all 4 corners), a 2-tuple ``(nx, ny)`` ($n_x \times n_y$ on all 4 corners), or a 4-tuple ``(c_fl, c_fr, c_bl, c_br)`` specifying the pyramid grid per corner ``(front_left, front_right, back_left, back_right)``.
   * - ``stackable_top_pyramid_count``
     - ``None`` (from ``stackable_pyramid_count``)
     - Override the pyramid configuration on the **top** face (lid or open-tray top rim) independently of the bottom face to key specific pairs of boxes together.
   * - ``stackable_bottom_pyramid_count``
     - ``None`` (from ``stackable_pyramid_count``)
     - Override the pyramid configuration on the **bottom** floor independently of the top face to match the box directly beneath it.
   * - ``stackable_top``
     - ``True``
     - Whether to generate raised stacking bosses on the top face (set ``False`` on the top-most box of a stack so its lid is completely flush).
   * - ``stackable_bottom``
     - ``True``
     - Whether to generate recessed stacking sockets in the bottom floor (set ``False`` on the bottom-most box of a stack so its floor is solid).
   * - ``stackable_printer_safe``
     - ``True``
     - Keeps the box bottom flat on the build plate (``z = 0``) with recessed 45° sockets and top bosses so the floor never prints suspended in mid-air.
   * - ``stackable_foot_size``
     - ``max(6.0, wall * 2.5)``
     - Width and length (mm) of each square corner pad.
   * - ``stackable_foot_height``
     - ``1.2``
     - Target height/depth (mm) of pyramids/feet, bounded by floor/lid thickness.
   * - ``stackable_foot_inset``
     - ``wall + 1.0``
     - Inset distance (mm) from outer box corners.
   * - ``stackable_fit_offset``
     - ``0.15``
     - Lateral fit clearance (mm) between boss and socket walls.

.. pythonscad-example::

   project = Project("StackDemoLidded")
   b1 = project.box(
       BoxType.SLIDING,
       "BottomBox",
       size=(60.0, 80.0, 22.0),
       color=Color("midnightblue"),
       position=(0.0, 0.0, 0.0),
       stackable=StackableMode.PYRAMIDS,
       stackable_foot_size=7.0,
       stackable_foot_height=1.2,
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.HEX, spacing=9.0),
       ).titled("LOWER"),
   )
   b1.compartment("Cubes", width_ratio=0.5, holds_pieces=True)
   b1.compartment("Tokens", width_ratio=0.5, holds_pieces=True)
   b2 = project.box(
       BoxType.SLIDING,
       "TopBox",
       size=(60.0, 80.0, 22.0),
       color=Color("coral"),
       position=(0.0, 0.0, 28.0),
       stackable=StackableMode.PYRAMIDS,
       stackable_foot_size=7.0,
       stackable_foot_height=1.2,
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("white"),
           text_color=Color("midnightblue"),
           pattern=PatternBuilder(PatternType.HEX, spacing=9.0),
       ).titled("UPPER"),
   )
   b2.compartment("Cards", holds_pieces=True)
   project.show(show_lids=True)


Pattern-Matched Stacking (``StackableMode.PATTERN``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When ``stackable=StackableMode.PATTERN`` is configured, the decorative pattern on the lid is matched directly onto the underside of the box body. Both the lid and the box are shown below (``project.show(show_lids=True)``) with a vertical exploded gap so the raised 45°-drafted pattern web ridge on the lid, the interior compartments, and the matching recessed pattern lattice on the underside of the upper box are all clearly visible:

.. pythonscad-example::

   project = Project("StackDemoPattern")
   b_lower = project.box(
       BoxType.SLIDING,
       "LowerPatternBox",
       size=(60.0, 75.0, 22.0),
       color=Color("darkslateblue"),
       position=(0.0, 0.0, 0.0),
       stackable=StackableMode.PATTERN,
       stackable_foot_height=1.2,
       lid=LidBuilder(
           pattern=PatternBuilder(PatternType.HEX, spacing=9.0),
       ),
   )
   b_lower.compartment("LowerWell", width_ratio=0.5, holds_pieces=True)
   b_lower.compartment("LowerTokens", width_ratio=0.5, holds_pieces=True)
   b_upper = project.box(
       BoxType.SLIDING,
       "UpperPatternBox",
       size=(60.0, 75.0, 22.0),
       color=Color("teal"),
       position=(0.0, 0.0, 28.0),
       stackable=StackableMode.PATTERN,
       stackable_foot_height=1.2,
       lid=LidBuilder(
           pattern=PatternBuilder(PatternType.HEX, spacing=9.0),
       ),
   )
   b_upper.compartment("UpperWell", holds_pieces=True)
   project.show(show_lids=True)


Push-Up Slide-Latch Stacking for Flipped-Lid Boxes (``StackableMode.SLIDE_LATCH``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For box types whose lids must be printed upside down (such as ``FILAMENT_HINGE``, ``CLAMSHELL``, ``PRINT_IN_PLACE_HINGE``, ``CAP``, ``SLIPOVER``, and ``SNAP_FIT``), ``StackableMode.SLIDE_LATCH`` (or ``StackableMode.LATCH``) places captive print-in-place vertical dovetail sliders and bottom receiver sockets on the left and right side walls so you can push the latches up to link the top and bottom boxes together:

.. pythonscad-example::

   project = Project("StackDemoSlideLatch")
   b_hinge_low = project.box(
       BoxType.FILAMENT_HINGE,
       "LowerHingeBox",
       size=(60.0, 75.0, 24.0),
       color=Color("darkslategray"),
       position=(0.0, 0.0, 0.0),
       stackable=StackableMode.SLIDE_LATCH,
   )
   b_hinge_low.compartment("LowerDice", width_ratio=0.5, holds_pieces=True)
   b_hinge_low.compartment("LowerGems", width_ratio=0.5, holds_pieces=True)
   b_hinge_top = project.box(
       BoxType.FILAMENT_HINGE,
       "UpperHingeBox",
       size=(60.0, 75.0, 24.0),
       color=Color("peru"),
       position=(0.0, 0.0, 30.0),
       stackable=StackableMode.SLIDE_LATCH,
   )
   b_hinge_top.compartment("UpperCards", holds_pieces=True)
   project.show(show_lids=True)


Keyed Pyramid Configurations for Enforcing Stacking Order (``project.stack_order``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

When multiple similar slip-on/sliding-lid boxes (``BoxType.SLIDING``, e.g. card decks or tiered item trays) are stacked in a vertical column, you can configure **keyed pyramid ridges** on the top of each lid and the bottom of the box above it so the boxes physically lock only in the exact bottom-to-top order:

- **Bottom box** (``box[0]``): ``stackable_bottom=False`` (solid flat floor) and ``stackable_top_pyramid_count=2`` ($2 \times 2$ pyramids per corner on its lid).
- **Middle boxes** (``box[i]``): ``stackable_bottom_pyramid_count`` matches ``box[i - 1]``'s lid, while ``stackable_top_pyramid_count`` advances to the next mutually incompatible pyramid grid in ``STACKING_ORDER_PYRAMID_CONFIGS`` (``2``, ``3``, ``(2, 3, 3, 2)``, ``(3, 2, 2, 3)``, ``(2, 2, 3, 3)``, ``(3, 3, 2, 2)``, ``4``). Because the peaks of a $2 \times 2$ corner pad hit the solid floor webs of a $3 \times 3$ socket (and vice versa), out-of-order boxes physically interfere and refuse to seat flush.
- **Top box** (``box[-1]``): ``stackable_bottom_pyramid_count`` matches the lid below it, and ``stackable_top=False`` keeps the top lid completely flat.

Use :meth:`~pyboxbuilder.project.core.Project.stack_order` (or let :class:`~pyboxbuilder.project.compiler.LayoutCompiler` auto-assign keyed pyramid configs to vertical ``StackableMode.PYRAMIDS`` columns):

.. pythonscad-example::

   project = Project("StackOrderDemo")
   c1 = project.box(
       BoxType.SLIDING,
       "DeckTier1_Bottom",
       size=(65.0, 90.0, 16.0),
       color=Color("darkred"),
       position=(0.0, 0.0, 0.0),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.DENSE_HEX),
       ).titled("TIER 1"),
   )
   c1.compartment("Cards", holds_pieces=True)
   c2 = project.box(
       BoxType.SLIDING,
       "DeckTier2_Middle",
       size=(65.0, 90.0, 16.0),
       color=Color("forestgreen"),
       position=(0.0, 0.0, 20.0),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.DENSE_HEX),
       ).titled("TIER 2"),
   )
   c2.compartment("Cards", holds_pieces=True)
   c3 = project.box(
       BoxType.SLIDING,
       "DeckTier3_Top",
       size=(65.0, 90.0, 16.0),
       color=Color("royalblue"),
       position=(0.0, 0.0, 40.0),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.DENSE_HEX),
       ).titled("TIER 3"),
   )
   c3.compartment("Cards", holds_pieces=True)
   project.stack_order(c1, c2, c3)
   project.show(show_lids=True)






