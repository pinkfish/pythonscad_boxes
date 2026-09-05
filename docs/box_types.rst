Box Types Guide & Gallery
==========================

``pyboxbuilder`` provides a comprehensive family of 13 box closure mechanisms, tray configurations, and custom footprint types. Each box type (:class:`~pyboxbuilder.enums.BoxType`) is coupled with a dedicated typed builder in :mod:`pyboxbuilder.builders` tailored for specific physical 3D printing requirements, component security, and ease of access during gameplay.

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
---------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.sliding_catch.SlidingCatchBoxBuilder`

A variant of the sliding dovetail box equipped with a detent bump and fingernail catch at the leading edge. When closed, the lid snaps securely into place, preventing accidental opening inside a game box stored vertically on a shelf.

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
---------------------------------

**Builder**: :class:`~pyboxbuilder.builders.cap.CapBoxBuilder`

A friction-fit cap lid that drops straight onto the box body from above. The lid incorporates side finger cutouts (:class:`~pyboxbuilder.box.features.CapFingerMetrics`) that reveal the box body beneath, allowing easy removal by pinching the sides.

Cap boxes are well-suited for player trays, resource banks, and modular organizers where components are unpacked immediately onto the table.

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
   )
   project.show(show_lids=True)


Telescoping Slipover Lid (``BoxType.SLIPOVER``)
-----------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.slipover.SlipoverBoxBuilder`

A classic two-piece shoebox closure where the lid walls telescope down over the full height of the body. Internal air-release clearances ensure a smooth slide fit without vacuum resistance.

Slipover lids provide high structural rigidity and a clean exterior finish.

.. pythonscad-example::

   project = Project("SlipoverDemo", game_box_size=(80.0, 80.0, 35.0))
   project.box(
       BoxType.SLIPOVER,
       "MiniDeck",
       size=(55.0, 70.0, 26.0),
       lid=LidBuilder(
           pattern=PatternBuilder(PatternType.CIRCLE),
           text="CARDS",
       ),
   )
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
   )
   project.show(show_lids=True)


Print-in-Place Pin Hinge (``BoxType.HINGE``)
--------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.hinge.HingeBoxBuilder`

Features an integrated pin hinge printed in place alongside the body and lid. The hinge knuckles print with internal clearance gaps so the lid swings open freely straight off the build plate without requiring assembly or separate hardware.

.. pythonscad-example::

   project = Project("HingeDemo", game_box_size=(80.0, 80.0, 30.0))
   project.box(
       BoxType.HINGE,
       "Chest",
       size=(60.0, 50.0, 22.0),
       lid=LidBuilder(text="SUPPLIES"),
   )
   project.show(show_lids=True)


Filament Pin Hinge (``BoxType.FILAMENT_HINGE``)
-----------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.filament_hinge.FilamentHingeBoxBuilder`

A compact, durable hinge design whose hinge barrel accepts a short length of standard 1.75 mm 3D printing filament as the hinge pin. Because the pin is inserted post-print, the hinge barrels can be smaller and tighter than print-in-place tolerances permit.

.. pythonscad-example::

   project = Project("FilamentHingeDemo", game_box_size=(80.0, 80.0, 30.0))
   project.box(
       BoxType.FILAMENT_HINGE,
       "PinBox",
       size=(60.0, 50.0, 22.0),
       lid=LidBuilder(text="GEAR"),
   )
   project.show(show_lids=True)


Magnetic Closure Lid (``BoxType.MAGNETIC``)
-------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.magnetic.MagneticBoxBuilder`

Recesses precision magnet cavities (:class:`~pyboxbuilder.enums.MagnetType`) into the walls of both the box body and lid. Small cylindrical (e.g. 6x3 mm) or rectangular neodymium magnets glued into the sockets provide a snap closure with a flush perimeter.

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


Inset Flush Lid (``BoxType.INSET``)
-----------------------------------

**Builder**: :class:`~pyboxbuilder.builders.inset.InsetBoxBuilder`

The inset lid sits flush with the top lip of the box, resting on a stepped internal rabbet shelf carved into the interior perimeter wall. A finger cutout allows the lid to be levered or lifted out.

Inset boxes maximize usable height in tight game boxes where external lid rims would consume too much vertical clearance.

.. pythonscad-example::

   project = Project("InsetDemo", game_box_size=(80.0, 80.0, 30.0))
   project.box(
       BoxType.INSET,
       "FlushTray",
       size=(60.0, 60.0, 22.0),
       lid=LidBuilder(text="TILES"),
   )
   project.show(show_lids=True)


Open & Stackable Trays (``BoxType.NO_LID``)
-------------------------------------------

**Builder**: :class:`~pyboxbuilder.builders.no_lid.NoLidBoxBuilder`

Open organizer trays without a lid. When ``stackable`` is enabled (:class:`~pyboxbuilder.enums.StackableMode`), an interlocking step rim is added:

- ``StackableMode.INSIDE``: A stepped inner recess in the top rim that the tray above nests down into.
- ``StackableMode.OUTSIDE``: A perimeter skirt around the outside base that fits over the tray below.

Stacked trays cannot slide off each other during play or transport.

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
   )
   project.show()
