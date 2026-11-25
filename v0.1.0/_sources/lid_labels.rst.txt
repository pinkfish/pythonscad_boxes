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


Solid Background Framed Labels
------------------------------

Set ``label_solid_background=True`` to replace the diagonal through-hole strips inside a framed label with a solid unperforated background (keeping the lid's own colour inside the frame), or pass ``label_background_color`` to inlay a contrasting solid background colour in the top layer inside the border ring:

.. pythonscad-example::

   project = Project("SolidBackgroundLabelDemo")
   project.box(
       BoxType.CAP,
       "VictoryPoints",
       size=(110.0, 80.0, 24.0),
       color=Color("darkslategray"),
       lid=LidBuilder(
           text="Victory\nPoints",
           label_mode=LabelMode.FRAMED,
           text_color=Color("white"),
           frame_color=Color("gold"),
           label_background_color=Color("navy"),
           pattern=PatternBuilder(PatternType.HEX, spacing=9.0),
       ),
   )
   project.show(lids_only=True)


Decorative Plaque Shapes (``LabelShape``)
-----------------------------------------

Pass ``label_shape`` (a :class:`~pyboxbuilder.enums.LabelShape` member or string) to replace the default rounded rectangle with a themed plaque silhouette. All decorative shapes default to a clean solid interior (no busy diagonal hatching) unless ``label_solid_background=False`` is set explicitly:

- ``LabelShape.CHAMFERED`` — sci-fi octagonal plaque with 45° beveled corners
- ``LabelShape.PILL`` — capsule / stadium plaque with semicircular ends
- ``LabelShape.HEXAGON`` — elongated hexagonal lozenge with pointed chevron ends
- ``LabelShape.HEX_BRACKET`` — open hex-angled end brackets with an open top and bottom center (HUD / Brink tile style)
- ``LabelShape.NOTCHED`` — art-deco / ticket plaque with concave corner notches
- ``LabelShape.RIBBON`` — banner plaque with swallowtail V-notched ends
- ``LabelShape.DOUBLE_FRAME`` — premium nameplate with an outer border ring and thin inner pinstripe
- ``LabelShape.UNDERLINE`` — minimalist header with clean lettering and a bold accent bar underneath

Sci-Fi Open Hex-Bracket & Custom Typography
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Combine ``LabelShape.HEX_BRACKET`` with ``font`` and ``text_spacing`` for open hex-angled end brackets (leaving the center of the top and bottom edges open) and wide-tracked geometric sci-fi lettering:

.. pythonscad-example::

   from pyboxbuilder import LabelShape

   project = Project("HexBracketBrinkStyleDemo")
   project.box(
       BoxType.CAP,
       "Actions",
       size=(115.0, 82.0, 22.0),
       color=Color("darkslategray"),
       lid=LidBuilder(
           text="ACTIONS",
           label_mode=LabelMode.FRAMED,
           label_shape=LabelShape.HEX_BRACKET,
           font="Futura:style=Bold",
           text_spacing=1.18,
           text_color=Color("white"),
           frame_color=Color("gold"),
           pattern=PatternBuilder(PatternType.VORONOI),
       ),
   )
   project.show(lids_only=True)


Sci-Fi Chamfered Plaque with Chevron Finial
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. pythonscad-example::

   from pyboxbuilder import LabelFinial, LabelShape

   project = Project("ChamferedChevronLabelDemo")
   project.box(
       BoxType.CAP,
       "Starships",
       size=(115.0, 82.0, 22.0),
       color=Color("darkslategray"),
       lid=LidBuilder(
           text="Starships",
           label_mode=LabelMode.FRAMED,
           label_shape=LabelShape.CHAMFERED,
           label_finial=LabelFinial.CHEVRON,
           text_color=Color("white"),
           frame_color=Color("gold"),
           pattern=PatternBuilder(PatternType.VORONOI),
       ),
   )
   project.show(lids_only=True)


Hexagonal Lozenge & Capsule Pill
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. pythonscad-example::

   from pyboxbuilder import LabelFinial, LabelShape

   project = Project("HexagonAndPillLabelDemo")
   project.box(
       BoxType.CAP,
       "HexPlaque",
       size=(115.0, 78.0, 20.0),
       position=(0.0, 0.0, 0.0),
       color=Color("darkslategray"),
       lid=LidBuilder(
           text="Hex Tiles",
           label_mode=LabelMode.FRAMED,
           label_shape=LabelShape.HEXAGON,
           text_color=Color("white"),
           frame_color=Color("limegreen"),
           pattern=PatternBuilder(PatternType.HEX, spacing=9.0),
       ),
   )
   project.box(
       BoxType.CAP,
       "PillPlaque",
       size=(115.0, 78.0, 20.0),
       position=(125.0, 0.0, 0.0),
       color=Color("midnightblue"),
       lid=LidBuilder(
           text="Actions",
           label_mode=LabelMode.FRAMED,
           label_shape=LabelShape.PILL,
           label_finial=LabelFinial.TRIPLE_DOT,
           text_color=Color("white"),
           frame_color=Color("deepskyblue"),
           pattern=PatternBuilder(PatternType.VORONOI),
       ),
   )
   project.show(lids_only=True)


Art-Deco Notched & Swallowtail Ribbon
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. pythonscad-example::

   from pyboxbuilder import LabelFinial, LabelShape

   project = Project("NotchedAndRibbonLabelDemo")
   project.box(
       BoxType.CAP,
       "NotchedPlaque",
       size=(115.0, 78.0, 20.0),
       position=(0.0, 0.0, 0.0),
       color=Color("maroon"),
       lid=LidBuilder(
           text="Tickets",
           label_mode=LabelMode.FRAMED,
           label_shape=LabelShape.NOTCHED,
           label_finial=LabelFinial.DIAMOND,
           text_color=Color("white"),
           frame_color=Color("goldenrod"),
           pattern=PatternBuilder(PatternType.OCTAGON, spacing=9.0),
       ),
   )
   project.box(
       BoxType.CAP,
       "RibbonPlaque",
       size=(115.0, 78.0, 20.0),
       position=(125.0, 0.0, 0.0),
       color=Color("navy"),
       lid=LidBuilder(
           text="Events",
           label_mode=LabelMode.FRAMED,
           label_shape=LabelShape.RIBBON,
           text_color=Color("white"),
           frame_color=Color("crimson"),
           pattern=PatternBuilder(PatternType.HEX, spacing=9.0),
       ),
   )
   project.show(lids_only=True)


Classic, Vintage, Scroll & Ornate Plaque Shapes
-----------------------------------------------

In addition to modern geometric frames, ``LabelShape`` includes vintage, heraldic, and scroll-style plaques built directly into ``LidBuilder``:

- ``LabelShape.OVAL`` — classic elliptical apothecary / medallion plaque
- ``LabelShape.SCALLOPED`` — vintage antique label with protruding quatrefoil corner lobes
- ``LabelShape.BRACKET`` — Victorian bookplate cartouche with pointed ogee bracket ends
- ``LabelShape.SHIELD`` — heraldic crest / shield plaque tapering to a pointed base
- ``LabelShape.SCROLL`` — parchment scroll banner with rolled cylindrical curls on both ends
- ``LabelShape.CORNER_STUD`` — vintage industrial brass nameplate with four riveted corner studs
- ``LabelShape.ORNATE_FRAME`` — Victorian double-line frame accented with four corner diamond rosettes

Victorian Ornate Frame with Fleuron Finial
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. pythonscad-example::

   from pyboxbuilder import LabelFinial, LabelShape

   project = Project("OrnateFrameFleuronDemo")
   project.box(
       BoxType.CAP,
       "Artifacts",
       size=(120.0, 84.0, 22.0),
       color=Color("darkslateblue"),
       lid=LidBuilder(
           text="Artifacts",
           label_mode=LabelMode.FRAMED,
           label_shape=LabelShape.ORNATE_FRAME,
           label_finial=LabelFinial.FLEURON,
           text_color=Color("white"),
           frame_color=Color("gold"),
           pattern=PatternBuilder(PatternType.VORONOI),
       ),
   )
   project.show(lids_only=True)


Vintage Scalloped & Bookplate Bracket
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. pythonscad-example::

   from pyboxbuilder import LabelFinial, LabelShape

   project = Project("ScallopedAndBracketDemo")
   project.box(
       BoxType.CAP,
       "ScallopedLabel",
       size=(115.0, 80.0, 20.0),
       position=(0.0, 0.0, 0.0),
       color=Color("maroon"),
       lid=LidBuilder(
           text="Potions",
           label_mode=LabelMode.FRAMED,
           label_shape=LabelShape.SCALLOPED,
           text_color=Color("white"),
           frame_color=Color("goldenrod"),
           pattern=PatternBuilder(PatternType.HEX, spacing=9.0),
       ),
   )
   project.box(
       BoxType.CAP,
       "BracketLabel",
       size=(115.0, 80.0, 20.0),
       position=(125.0, 0.0, 0.0),
       color=Color("navy"),
       lid=LidBuilder(
           text="Chronicles",
           label_mode=LabelMode.FRAMED,
           label_shape=LabelShape.BRACKET,
           label_finial=LabelFinial.SPEAR,
           text_color=Color("white"),
           frame_color=Color("silver"),
           pattern=PatternBuilder(PatternType.HEX, spacing=9.0),
       ),
   )
   project.show(lids_only=True)


Riveted Brass Nameplate & Minimalist Underline
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. pythonscad-example::

   from pyboxbuilder import LabelShape

   project = Project("CornerStudAndUnderlineDemo")
   project.box(
       BoxType.CAP,
       "StuddedPlate",
       size=(115.0, 78.0, 20.0),
       position=(0.0, 0.0, 0.0),
       color=Color("darkslategray"),
       lid=LidBuilder(
           text="Locomotives",
           label_mode=LabelMode.FRAMED,
           label_shape=LabelShape.CORNER_STUD,
           text_color=Color("white"),
           frame_color=Color("orange"),
           pattern=PatternBuilder(PatternType.HEX, spacing=9.0),
       ),
   )
   project.box(
       BoxType.CAP,
       "UnderlineHeader",
       size=(115.0, 78.0, 20.0),
       position=(125.0, 0.0, 0.0),
       color=Color("darkslategray"),
       lid=LidBuilder(
           text="Resources",
           label_mode=LabelMode.FRAMED,
           label_shape=LabelShape.UNDERLINE,
           text_color=Color("white"),
           frame_color=Color("gold"),
           pattern=PatternBuilder(PatternType.VORONOI),
       ),
   )
   project.show(lids_only=True)


Typographic Finials Under Text (``LabelFinial``)
------------------------------------------------

Add a decorative ornament underneath any lid title (framed or frameless) using ``label_finial`` (:class:`~pyboxbuilder.enums.LabelFinial`). Finials automatically expand the plaque cleanly below the text and print in ``frame_color`` (falling back to ``text_color``):

- ``LabelFinial.DIAMOND`` — classic horizontal rule with a centered diamond (``─── ◆ ───``)
- ``LabelFinial.TRIPLE_DOT`` — rule with a centered three-dot trio (``─── • ● • ───``)
- ``LabelFinial.FLEURON`` — four-point compass star fleuron flanked by tapered rules (``─── ✦ ───``)
- ``LabelFinial.CHEVRON`` — sci-fi opposing chevron divider with a centered pip
- ``LabelFinial.SCROLLWORK`` — vintage curled double-scroll flourish with a center diamond
- ``LabelFinial.SPEAR`` — double-pointed tapered Victorian rule (``◄━━━━━━►``)


Combined Text + Image / Emblem Inside a Framed Label
----------------------------------------------------

Pass both ``text`` and ``logo`` to :class:`~pyboxbuilder.lid.builder.LidBuilder` to reserve a dedicated image bay inside any framed plaque (such as ``LabelShape.SCROLL``, ``LabelShape.SHIELD``, or ``LabelShape.ORNATE_FRAME``). Control placement with ``logo_position`` (``"top"``, ``"left"``, ``"right"``, or ``"bottom"``) and optional ``label_logo_size_mm``:

Parchment Scroll with Emblem & Scrollwork Finial
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. pythonscad-example::

   from pybosl2 import cuboid, cylinder
   from pyboxbuilder import LabelFinial, LabelShape

   emblem = [
       (cylinder(height=0.6, radius=10.0), Color("gold")),
       (cuboid([10.0, 10.0, 0.6]), Color("crimson")),
       (cylinder(height=0.6, radius=3.0), Color("white")),
   ]

   project = Project("ScrollWithCrestDemo")
   project.box(
       BoxType.CAP,
       "ScrollWithCrest",
       size=(125.0, 92.0, 24.0),
       color=Color("saddlebrown"),
       lid=LidBuilder(
           text="Treasury",
           logo=emblem,
           logo_position="top",
           label_mode=LabelMode.FRAMED,
           label_shape=LabelShape.SCROLL,
           label_finial=LabelFinial.SCROLLWORK,
           text_color=Color("white"),
           frame_color=Color("gold"),
           label_background_color=Color("navy"),
           pattern=PatternBuilder(PatternType.HEX, spacing=9.0),
       ),
   )
   project.show(lids_only=True)


Heraldic Shield Crest & Side-Emblem Badge
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. pythonscad-example::

   from pybosl2 import cuboid, cylinder
   from pyboxbuilder import LabelFinial, LabelShape

   emblem = [
       (cylinder(height=0.6, radius=10.0), Color("gold")),
       (cuboid([10.0, 10.0, 0.6]), Color("crimson")),
       (cylinder(height=0.6, radius=3.0), Color("white")),
   ]

   project = Project("ShieldAndSideBadgeDemo")
   project.box(
       BoxType.CAP,
       "ShieldWithCrest",
       size=(120.0, 95.0, 24.0),
       position=(0.0, 0.0, 0.0),
       color=Color("forestgreen"),
       lid=LidBuilder(
           text="Knights",
           logo=emblem,
           logo_position="top",
           label_mode=LabelMode.FRAMED,
           label_shape=LabelShape.SHIELD,
           label_finial=LabelFinial.DIAMOND,
           text_color=Color("white"),
           frame_color=Color("gold"),
           pattern=PatternBuilder(PatternType.HEX, spacing=9.0),
       ),
   )
   project.box(
       BoxType.CAP,
       "BadgeWithSideLogo",
       size=(125.0, 95.0, 24.0),
       position=(130.0, 0.0, 0.0),
       color=Color("maroon"),
       lid=LidBuilder(
           text="Guild",
           logo=emblem,
           logo_position="left",
           label_mode=LabelMode.FRAMED,
           label_shape=LabelShape.ORNATE_FRAME,
           label_finial=LabelFinial.FLEURON,
           text_color=Color("white"),
           frame_color=Color("gold"),
           pattern=PatternBuilder(PatternType.VORONOI),
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
