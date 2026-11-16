Lid Labels Guide & Showcase
===========================

``pyboxbuilder`` supports auto-sized, multi-material flush-inlaid lid labels via :class:`~pyboxbuilder.lid.builder.LidBuilder` and :class:`~pyboxbuilder.enums.LabelMode`.

Every label automatically:

- Fits within the configured ``border_margin_mm`` (default ``10.0 mm`` on all lids, falling back to ``5.0 mm`` only on narrow polygon lid arms) and caps font height at ``max_text_height_mm`` (default ``16.0 mm``).
- Enforces a ``1.5 mm`` outer border ring (``LABEL_BORDER_MM``) and ``1.5 mm`` clearance (``LABEL_TEXT_GAP_MM``) around the highest and longest text edges in framed mode so text never touches the border.
- Cuts diagonal hatching spaces as open through-holes through the lid when framed, while reserving ``frame_color`` strictly for the outer edge border ring so the ``1.5 mm`` inner spacing and strips keep the lid's own colour.
- Restricts multi-color logos and shape inlays strictly to the top inlay layer (``0.6 mm``), keeping backing layers single-color to minimize color switches.

.. contents:: On this page
   :local:
   :depth: 2


Framed Labels (Default Open Strips)
-----------------------------------

Setting ``label_mode=LabelMode.FRAMED`` (the default whenever text is provided) surrounds the lettering with a ``1.5 mm`` rounded outer border ring and ``45°`` diagonal support strips separated by open through-hole spaces cut completely through the lid:

.. pythonscad-example::

   project = Project("FramedDefaultLabelDemo")
   project.box(
       BoxType.SLIDING,
       "Tokens",
       size=(100.0, 75.0, 22.0),
       color=Color("darkslateblue"),
       lid=LidBuilder(
           text="TOKENS",
           label_mode=LabelMode.FRAMED,
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.HEX, spacing=9.0),
       ),
   )
   project.show(lids_only=True)


Framed Labels with Accented Outer Border (``frame_color``)
----------------------------------------------------------

Passing ``frame_color`` adds a contrasting colour exclusively to the outer ``1.5 mm`` edge border ring of the label frame. The interior ``1.5 mm`` gap, diagonal strips holding the text, and open through-hole slots remain unchanged:

.. pythonscad-example::

   project = Project("FramedAccentLabelDemo")
   project.box(
       BoxType.CAP,
       "HexTiles",
       size=(110.0, 80.0, 24.0),
       color=Color("darkslategray"),
       lid=LidBuilder(
           text="Hex Tiles",
           label_mode=LabelMode.FRAMED,
           text_color=Color("white"),
           frame_color=Color("gold"),
           pattern=PatternBuilder(PatternType.DENSE_HEX),
       ),
   )
   project.show(lids_only=True)


Frameless Labels (``LabelMode.FRAMELESS``)
------------------------------------------

Setting ``label_mode=LabelMode.FRAMELESS`` (or ``"frameless"``) inlays just the lettering directly into the top layer of the lid with no border ring or diagonal hatching strips, keeping surrounding surface patterns maximally open:

.. pythonscad-example::

   project = Project("FramelessLabelDemo")
   project.box(
       BoxType.SLIDING,
       "Resources",
       size=(100.0, 75.0, 22.0),
       color=Color("teal"),
       lid=LidBuilder(
           text="Resources",
           label_mode=LabelMode.FRAMELESS,
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.OCTAGON, spacing=9.0),
       ),
   )
   project.show(lids_only=True)


Diagonal & Multi-Line Labels
----------------------------

Enable ``diagonal=True`` to orient text along the lid's corner-to-corner diagonal, and use ``\n`` for multi-line titles or ``max_text_height_mm`` to tune the maximum letter height:

.. pythonscad-example::

   project = Project("DiagonalLabelDemo")
   project.box(
       BoxType.CAP,
       "PlayerCards",
       size=(95.0, 95.0, 24.0),
       color=Color("maroon"),
       lid=LidBuilder(
           text="PLAYER\nCARDS",
           label_mode=LabelMode.FRAMELESS,
           diagonal=True,
           text_color=Color("gold"),
           max_text_height_mm=14.0,
           pattern=PatternBuilder(PatternType.VORONOI, spacing=10.0),
       ),
   )
   project.show(lids_only=True)


Custom Border, Gap & Corner Rounding
------------------------------------

Fine-tune the label's geometry with ``label_border_mm`` (outer ring width), ``label_text_gap_mm`` (clearance around text), ``label_rounding_mm`` (outer frame corner radius), and ``label_clearance_mm`` (standoff between the label and the surrounding pattern):

.. pythonscad-example::

   project = Project("CustomLabelMetricsDemo")
   project.box(
       BoxType.SLIDING,
       "Money",
       size=(100.0, 75.0, 22.0),
       color=Color("navy"),
       lid=LidBuilder(
           text="Money",
           label_mode=LabelMode.FRAMED,
           text_color=Color("white"),
           frame_color=Color("silver"),
           label_border_mm=2.0,
           label_text_gap_mm=2.5,
           label_rounding_mm=6.0,
           label_clearance_mm=1.5,
           pattern=PatternBuilder(PatternType.TRIANGLE, spacing=9.0),
       ),
   )
   project.show(lids_only=True)


Multi-Color Shapes & Top-Layer Logos
------------------------------------

The ``logo`` field accepts single- or multi-color SVGs, multi-color CSG solids, ``PatternResult`` tiles, or sequences of ``(shape, color)`` pairs. All colours are automatically clipped to the top inlay layer (``0.6 mm``) and consolidated by colour so backing layers print cleanly with minimal colour changes:

.. pythonscad-example::

   from pybosl2 import cuboid, cylinder

   emblem = [
       (cylinder(height=0.6, radius=14.0), Color("gold")),
       (cuboid([14.0, 14.0, 0.6]), Color("crimson")),
       (cylinder(height=0.6, radius=4.0), Color("white")),
   ]

   project = Project("MultiColorLogoLabelDemo")
   project.box(
       BoxType.CAP,
       "FactionBox",
       size=(100.0, 80.0, 24.0),
       color=Color("darkslateblue"),
       lid=LidBuilder(
           logo=emblem,
           pattern=PatternBuilder(PatternType.HEX, spacing=9.0),
       ),
   )
   project.show(lids_only=True)


Labels Over Multi-Color Inlaid Patterns
---------------------------------------

When paired with a multi-color tessellation pattern (such as ``PatternType.STEPPED_CUBE`` or ``PatternType.PENROSE``), framed and frameless labels reserve clean space out of the colored tile layer while keeping a continuous structural floor and underside hex backing lattice:

.. pythonscad-example::

   project = Project("LabelOnTessellationDemo")
   project.box(
       BoxType.CAP,
       "Gems",
       size=(105.0, 80.0, 24.0),
       color=Color("darkslategray"),
       lid=LidBuilder(
           text="GEMS",
           label_mode=LabelMode.FRAMED,
           text_color=Color("white"),
           frame_color=Color("gold"),
           pattern=PatternBuilder(
               PatternType.STEPPED_CUBE,
               spacing=12.0,
               inlay=True,
               colors=(Color("teal"), Color("lightskyblue"), Color("navy"), Color("gold")),
           ),
       ),
   )
   project.show(lids_only=True)
