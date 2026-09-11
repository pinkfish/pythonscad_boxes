Box Types Guide & Gallery
==========================

``pyboxbuilder`` provides a comprehensive family of 23 box closure mechanisms, tray configurations, and custom footprint types. Each box type (:class:`~pyboxbuilder.enums.BoxType`) is coupled with a dedicated typed builder in :mod:`pyboxbuilder.builders` tailored for specific physical 3D printing requirements, component security, and ease of access during gameplay.

This gallery demonstrates each box type with an interactive 3D STL viewer powered by PythonSCAD. You can rotate, pan, and zoom each model directly in your browser.

.. contents:: On this page
   :local:
   :depth: 2


Sliding Lid (``BoxType.SLIDING``)
---------------------------------

**Builder**: :class:`~pyboxbuilder.builders.sliding.SlidingBoxBuilder`

The sliding dovetail box features integrated side rails along which the lid slides smoothly open and shut. The sliding axis defaults to the length (Y-axis), but can be configured along the width (X-axis) via ``lid_slide_axis="x"``.

It is ideal for token boxes, card decks, and trays where the lid should remain captive without extra hardware.

.. pythonscad-example::

   project = Project("SlidingDemo", game_box_size=(80.0, 80.0, 30.0))
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


Sliding Catch Lid (``BoxType.SLIDING_CATCH``)
---------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.sliding_catch.SlidingCatchBoxBuilder`

A variant of the sliding dovetail box equipped with a detent bump and fingernail catch at the leading edge. When closed, the lid snaps securely into place, preventing accidental opening inside a game box stored vertically on a shelf.

.. pythonscad-example::

   project = Project("CatchDemo", game_box_size=(80.0, 80.0, 30.0))
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


Drop-On Cap Lid (``BoxType.CAP``)
---------------------------------

**Builder**: :class:`~pyboxbuilder.builders.cap.CapBoxBuilder`

A friction-fit cap lid that drops straight onto the box body from above. Supports standard rectangular boxes as well as arbitrary polygon footprints via ``path``. The lid incorporates side finger cutouts (:class:`~pyboxbuilder.box.features.CapFingerMetrics`) that reveal the box body beneath, allowing easy removal by pinching the sides.

Cap boxes are well-suited for player trays, resource banks, and modular organizers where components are unpacked immediately onto the table.

.. pythonscad-example::

   project = Project("CapDemo", game_box_size=(80.0, 80.0, 30.0))
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


Cap Lid on Polygon Footprint (``BoxType.CAP_PATH``)
---------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.cap_path.CapPathBoxBuilder`

Combines the drop-on friction cap lid with an arbitrary 2D polygon footprint. The cap's skirt wraps around the outer perimeter of the polygonal tray, providing a clean friction-fit closure for L-shaped, T-shaped, or irregular spaces.

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
       color=Color("teal"),
   )
   project.show(show_lids=True)


Telescoping Slipover Lid (``BoxType.SLIPOVER``)
-----------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.slipover.SlipoverBoxBuilder`

A classic two-piece shoebox closure where the lid walls telescope down over the full height of the body. Supports standard rectangular boxes as well as arbitrary polygon footprints via ``path``. Internal air-release clearances ensure a smooth slide fit without vacuum resistance.

Slipover lids provide high structural rigidity and a clean exterior finish.

.. pythonscad-example::

   project = Project("SlipoverDemo", game_box_size=(80.0, 90.0, 35.0))
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


Slipover on Polygon Footprint (``BoxType.SLIPOVER_PATH``)
---------------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.slipover_path.SlipoverPathBoxBuilder`

A polygonal sleeve enclosure designed to slide over a custom 2D polygon body tray. It stops against a configurable base foot, creating a full-height outer sleeve for irregular modular organizers.

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
       color=Color("darkcyan"),
   )
   project.show(show_lids=True)


Print-in-Place Pin Hinge (``BoxType.HINGE``)
--------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.hinge.HingeBoxBuilder`

Features an integrated pin hinge printed in place alongside the body and lid. The hinge knuckles print with internal clearance gaps so the lid swings open freely straight off the build plate without requiring assembly or separate hardware.

.. pythonscad-example::

   project = Project("HingeDemo", game_box_size=(80.0, 80.0, 30.0))
   box = project.box(
       BoxType.HINGE,
       "Chest",
       size=(60.0, 50.0, 22.0),
       color=Color("saddlebrown"),
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


Filament Pin Hinge (``BoxType.FILAMENT_HINGE``)
-----------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.filament_hinge.FilamentHingeBoxBuilder`

A compact, durable hinge design whose hinge barrel accepts a short length of standard 1.75 mm 3D printing filament as the hinge pin. Because the pin is inserted post-print, the hinge barrels can be smaller and tighter than print-in-place tolerances permit.

.. pythonscad-example::

   project = Project("FilamentHingeDemo", game_box_size=(80.0, 80.0, 30.0))
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


Magnetic Closure Lid (``BoxType.MAGNETIC``)
-------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.magnetic.MagneticBoxBuilder`

Recesses precision magnet cavities (:class:`~pyboxbuilder.enums.MagnetType`) into the walls of both the box body and lid. Small cylindrical (e.g. 6x3 mm) or rectangular neodymium magnets glued into the sockets provide a snap closure with a flush perimeter.

.. pythonscad-example::

   project = Project("MagneticDemo", game_box_size=(80.0, 80.0, 30.0))
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


Inset Flush Lid (``BoxType.INSET``)
-----------------------------------

**Builder**: :class:`~pyboxbuilder.builders.inset.InsetBoxBuilder`

The inset lid sits flush with the top lip of the box, resting on a stepped internal rabbet shelf carved into the interior perimeter wall. A finger cutout allows the lid to be levered or lifted out.

Inset boxes maximize usable height in tight game boxes where external lid rims would consume too much vertical clearance.

.. pythonscad-example::

   project = Project("InsetDemo", game_box_size=(80.0, 80.0, 30.0))
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


Open & Stackable Trays (``BoxType.NO_LID``)
-------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.no_lid.NoLidBoxBuilder`

Open organizer trays without a lid. Supports standard rectangular boxes as well as arbitrary polygon footprints via ``path``. When ``stackable`` is enabled (:class:`~pyboxbuilder.enums.StackableMode`), an interlocking step rim is added:

- ``StackableMode.INSIDE``: A stepped inner recess in the top rim that the tray above nests down into.
- ``StackableMode.OUTSIDE``: A perimeter skirt around the outside base that fits over the tray below.

Stacked trays cannot slide off each other during play or transport.

.. pythonscad-example::

   project = Project("StackDemo", game_box_size=(80.0, 80.0, 40.0))
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


Card Library Box (``BoxType.CARD_LIBRARY``)
-------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.card_library.CardLibraryBoxBuilder`

A specialized card storage box optimized for card decks. It supports standard card sizes or custom dimensions (sleeved or unsleeved via :class:`~pyboxbuilder.helpers.CardSpec`), and incorporates thumb push-through holes or wall scoops (:class:`~pyboxbuilder.enums.FingerCut`) to extract tightly packed decks.

.. pythonscad-example::

   project = Project("CardLibDemo", game_box_size=(80.0, 100.0, 35.0))
   project.box(
       BoxType.CARD_LIBRARY,
       "Deck",
       size=(55.0, 80.0, 25.0),
       color=Color("darkblue"),
   )
   project.show(show_lids=True)


Polygon Footprint Path Box (``BoxType.PATH``)
---------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.path.PathBoxBuilder`

When rectangular boxes cannot fit around game boards, player mats, or non-rectangular components, ``BoxType.PATH`` builds an open tray whose exterior footprint follows any arbitrary closed 2D polygon path.

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
       color=Color("forestgreen"),
   )
   project.show()


Snap-Fit Cantilever Latch (``BoxType.SNAP_FIT``)
------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.snap_fit.SnapFitBoxBuilder`

Features integrated downward-extending cantilever spring arms on opposing walls with positive retention detents (a 45° lead-in ramp and flat horizontal lock shoulder), mating with matching catch pockets recessed into the box body. Thumb pressure on the upper tab face deflects the detents inward to release the lid.

.. pythonscad-example::

   project = Project("SnapFitDemo", game_box_size=(80.0, 80.0, 40.0))
   box = project.box(
       BoxType.SNAP_FIT,
       "SnapBox",
       size=(60.0, 50.0, 24.0),
       color=Color("darkmagenta"),
       cantilever_thickness=1.6,
       cantilever_width=12.0,
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.HEX, spacing=8.0),
       ).titled("SNAP"),
   )
   box.compartment("PawnWell", holds_pieces=True)
   project.show(show_lids=True)


Twist-Lock Bayonet Container (``BoxType.BAYONET``)
--------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.bayonet.BayonetBoxBuilder`

Designed for cylindrical or rounded footprints, the lid and body mate via a quarter-turn (90°) or eighth-turn (45°) bayonet mechanism. The lid features internal retention lugs that enter vertical entry keyways in the box rim and rotate into horizontal retention channels terminating in tactile detent stops.

.. pythonscad-example::

   project = Project("BayonetDemo", game_box_size=(80.0, 80.0, 50.0))
   project.box(
       BoxType.BAYONET,
       "BayonetCanister",
       size=(55.0, 55.0, 35.0),
       color=Color("teal"),
       lug_count=4,
       turn_angle=90.0,
   )
   project.show(show_lids=True)


Threaded Screw Box (``BoxType.THREADED``)
-----------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.threaded.ThreadedBoxBuilder`

Container with helical male/female screw threads on a circular cylindrical profile. The thread profile uses a coarse modified trapezoidal geometry with flat crests and roots (default pitch 3.0mm) and calibrated radial clearance to prevent layer binding, terminating at a flush seating shoulder.

.. pythonscad-example::

   project = Project("ThreadedDemo", game_box_size=(80.0, 80.0, 50.0))
   project.box(
       BoxType.THREADED,
       "ThreadedJar",
       size=(50.0, 50.0, 32.0),
       color=Color("darkolivegreen"),
       thread_pitch=3.0,
       thread_turns=2.0,
   )
   project.show(show_lids=True)


Gravity Tile & Token Dispenser (``BoxType.DISPENSER``)
------------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.dispenser.DispenserBoxBuilder`

Designed for cardboard tiles (e.g. Carcassonne, Catan), poker chips, or resource tokens during gameplay. Features a top loading chute, an internal slide floor angled at 35°–45° toward the front wall, a horizontal bottom dispensing slot, a vertical sight slot to monitor remaining stack height, and a curved finger scoop.

.. pythonscad-example::

   project = Project("DispenserDemo", game_box_size=(80.0, 80.0, 90.0))
   project.box(
       BoxType.DISPENSER,
       "TileChute",
       size=(55.0, 55.0, 70.0),
       color=Color("darkred"),
       chute_angle=40.0,
       token_thickness=3.0,
   )
   project.show(show_lids=True)


Angled Draw & Discard Card Shoe (``BoxType.CARD_SHOE``)
-------------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.card_shoe.CardShoeBoxBuilder`

In-game tabletop utility tray with adjacent draw and discard wells. The draw well features a backward-slanted floor and backrest (15°–25° from vertical) with a low front retaining lip to prevent tall draw stacks from toppling while enabling easy one-card-at-a-time draw. The discard well is flat with opposing U-shaped edge finger scoops.

.. pythonscad-example::

   project = Project("CardShoeDemo", game_box_size=(150.0, 100.0, 60.0))
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


Dice Tray & Rolling Arena (``BoxType.DICE_TRAY``)
-------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.dice_tray.DiceTrayBoxBuilder`

A dual-purpose container where the body stores dice or tokens and the deep nesting lid doubles as an active tabletop dice rolling arena. The lid perimeter walls rise at least 25mm above the tray floor with 45° internal corner fillets to bounce rolling dice back toward the center, and a recessed acoustic pad pocket for adhesive felt.

.. pythonscad-example::

   project = Project("DiceTrayDemo", game_box_size=(140.0, 110.0, 50.0))
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


Matchbox Sleeve & Drawer (``BoxType.SLEEVE_DRAWER``)
----------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.sleeve_drawer.SleeveDrawerBoxBuilder`

A two-piece matchbox assembly consisting of a hollow 4-sided outer perimeter sleeve and an inner sliding compartment drawer, enabling horizontal drawer access without removing stacked trays above it. The drawer front features an integrated pull tab/lip, and the sleeve back wall features a semi-circular finger push-through hole.

.. pythonscad-example::

   project = Project("SleeveDrawerDemo", game_box_size=(90.0, 80.0, 40.0))
   box = project.box(
       BoxType.SLEEVE_DRAWER,
       "DrawerBox",
       size=(70.0, 60.0, 28.0),
       color=Color("sienna"),
       push_hole_radius=12.0,
       drawer_pull_lip=4.0,
   )
   box.compartment("Cards", holds_pieces=True)
   project.show(show_lids=True)


Bifold Clamshell Book Box (``BoxType.CLAMSHELL``)
-------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.clamshell.ClamshellBoxBuilder`

Two symmetrical tray halves joined along a central spine hinge, unfolding 180° flat onto the table so both halves serve as accessible token or card trays during play. The closing rims feature perimeter snap detents to hold the book securely closed during vertical storage.

.. pythonscad-example::

   project = Project("ClamshellDemo", game_box_size=(110.0, 80.0, 45.0))
   project.box(
       BoxType.CLAMSHELL,
       "BookBox",
       size=(90.0, 65.0, 32.0),
       color=Color("darkslateblue"),
       spine_gap=1.0,
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.HEX, spacing=8.0),
       ).titled("TOME"),
   )
   project.show(show_lids=True)


Modular Interlocking Play Trays (``BoxType.MODULAR_INTERLOCK``)
---------------------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.modular_interlock.ModularInterlockBoxBuilder`

Trays featuring perimeter interlocking joints on outer walls to lock multiple boxes side-by-side into a unified player dashboard or shared bank on the table. Supports sliding dovetails (with 0.15mm clearance) and Gridfinity-compatible tiered base profiles.

.. pythonscad-example::

   project = Project("ModularDemo", game_box_size=(80.0, 80.0, 40.0))
   box = project.box(
       BoxType.MODULAR_INTERLOCK,
       "ModularTray",
       size=(65.0, 65.0, 24.0),
       color=Color("steelblue"),
       interlock_type=InterlockType.DOVETAIL,
   )
   box.compartment("Items", holds_pieces=True)
   project.show(show_lids=True)


Monolithic Print-In-Place Hinge Box (``BoxType.PRINT_IN_PLACE_HINGE``)
----------------------------------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.pip_hinge.PrintInPlaceHingeBoxBuilder`

A single-piece, zero-assembly hinged box where body and lid are laid flat at 180° on the print bed in a single print job. Joined by captive cone-and-socket knuckle joints along the shared top rim, calibrated to 0.35mm radial and 0.40mm axial clearances with 45° self-supporting overhang angles so the hinge breaks free smoothly on first flexion.

.. pythonscad-example::

   project = Project("PIPHingeDemo", game_box_size=(80.0, 80.0, 35.0))
   box = project.box(
       BoxType.PRINT_IN_PLACE_HINGE,
       "HingedBox",
       size=(60.0, 45.0, 22.0),
       color=Color("forestgreen"),
       pip_radial_clearance=0.35,
       pip_axial_clearance=0.40,
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.HEX, spacing=8.0),
       ).titled("PIPKIT"),
   )
   box.compartment("Tools", holds_pieces=True)
   project.show(show_lids=True)


