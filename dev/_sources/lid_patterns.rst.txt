Lid Patterns Guide & Gallery
=============================

``pyboxbuilder`` provides 20 lid surface patterns and multi-color tessellations via :class:`~pyboxbuilder.enums.PatternType` and :class:`~pyboxbuilder.lid.builder.PatternBuilder`.

Patterns fall into two architectural categories:

1. **Perforated Through-Hole Lattices & Botanical Tilings** (``HEX``, ``DENSE_HEX``, ``SQUARE``, ``CIRCLE``, ``TRIANGLE``, ``DENSE_TRIANGLE``, ``OCTAGON``, ``VORONOI``, ``LEAF``, ``LEAF_TESSELLATION``, ``LEAF_VEINS``): Cut open lattices through the lid, saving filament while keeping contents visible and ventilated. Any of these can also be inlaid as a colored top layer by setting ``inlay=True`` or passing ``colors=(...)``.
2. **Multi-Color Inlays & Rhombic / Quasicrystal Tessellations** (``STEPPED_CUBE``, ``PENROSE``, ``AMMANN_BEENKER``, ``TUMBLING_BLOCKS``, ``CHEVRON``, ``DICE``, ``RING``, ``CHECKER``): Inlay a thin ``0.6 mm`` colored tile skin into the top face of the lid above a continuous ``0.8 mm`` structural floor and a selectable underside backing lattice (defaulting to ``PatternType.HEX`` via ``backing_pattern``) to minimize plastic use while preserving full lid strength.

The pattern gallery examples below render **only the sliding lid** (``project.show(lids_only=True)``) with ``border=0.0`` and ``fingernail_catch=False`` so the pattern fills the lid edge-to-edge, while the stacking setup at the end renders **both the lid and the box** (``project.show(show_lids=True)``).

.. contents:: On this page
   :local:
   :depth: 2


Classic Geometric Lattices
--------------------------

Honeycomb Hexagonal Grid (``PatternType.HEX``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Staggered rows of regular hexagons separated by a constant-width structural web. This is the default lid pattern and default underside backing lattice across ``pyboxbuilder``.

.. pythonscad-example::

   project = Project("HexPatternDemo")
   project.box(
       BoxType.SLIDING,
       "HexLid",
       size=(80.0, 60.0, 20.0),
       color=Color("darkslateblue"),
       fingernail_catch=False,
       catch_radius=0.0,
       lid=LidBuilder(
           pattern=PatternBuilder(PatternType.HEX, spacing=9.0, border=0.0),
       ),
   )
   project.show(lids_only=True)


Dense Honeycomb Grid (``PatternType.DENSE_HEX``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A tighter-pitch hexagonal honeycomb that keeps smaller game pieces safely enclosed while maximizing open area.

.. pythonscad-example::

   project = Project("DenseHexPatternDemo")
   project.box(
       BoxType.SLIDING,
       "DenseHexLid",
       size=(80.0, 60.0, 20.0),
       color=Color("teal"),
       fingernail_catch=False,
       catch_radius=0.0,
       lid=LidBuilder(
           pattern=PatternBuilder(PatternType.DENSE_HEX, border=0.0),
       ),
   )
   project.show(lids_only=True)


Square Grid (``PatternType.SQUARE``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Orthogonal square cutouts aligned to a Cartesian grid.

.. pythonscad-example::

   project = Project("SquarePatternDemo")
   project.box(
       BoxType.SLIDING,
       "SquareLid",
       size=(80.0, 60.0, 20.0),
       color=Color("darkslategray"),
       fingernail_catch=False,
       catch_radius=0.0,
       lid=LidBuilder(
           pattern=PatternBuilder(PatternType.SQUARE, spacing=9.0, border=0.0),
       ),
   )
   project.show(lids_only=True)


Circular Grid (``PatternType.CIRCLE``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Circular perforations arranged on an orthogonal grid.

.. pythonscad-example::

   project = Project("CirclePatternDemo")
   project.box(
       BoxType.SLIDING,
       "CircleLid",
       size=(80.0, 60.0, 20.0),
       color=Color("royalblue"),
       fingernail_catch=False,
       catch_radius=0.0,
       lid=LidBuilder(
           pattern=PatternBuilder(PatternType.CIRCLE, spacing=9.0, border=0.0),
       ),
   )
   project.show(lids_only=True)


Alternating Triangle Truss (``PatternType.TRIANGLE``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Equilateral triangular cutouts alternating point-up and point-down to form a diagonal truss web.

.. pythonscad-example::

   project = Project("TrianglePatternDemo")
   project.box(
       BoxType.SLIDING,
       "TriangleLid",
       size=(80.0, 60.0, 20.0),
       color=Color("crimson"),
       fingernail_catch=False,
       catch_radius=0.0,
       lid=LidBuilder(
           pattern=PatternBuilder(PatternType.TRIANGLE, spacing=9.0, border=0.0),
       ),
   )
   project.show(lids_only=True)


Dense Triangle Truss (``PatternType.DENSE_TRIANGLE``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The alternating triangular truss lattice at a finer pitch.

.. pythonscad-example::

   project = Project("DenseTrianglePatternDemo")
   project.box(
       BoxType.SLIDING,
       "DenseTriangleLid",
       size=(80.0, 60.0, 20.0),
       color=Color("firebrick"),
       fingernail_catch=False,
       catch_radius=0.0,
       lid=LidBuilder(
           pattern=PatternBuilder(PatternType.DENSE_TRIANGLE, border=0.0),
       ),
   )
   project.show(lids_only=True)


Octagonal Lattice (``PatternType.OCTAGON``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Regular octagonal openings leaving diagonal-cross webs between neighboring cells.

.. pythonscad-example::

   project = Project("OctagonPatternDemo")
   project.box(
       BoxType.SLIDING,
       "OctagonLid",
       size=(80.0, 60.0, 20.0),
       color=Color("darkgreen"),
       fingernail_catch=False,
       catch_radius=0.0,
       lid=LidBuilder(
           pattern=PatternBuilder(PatternType.OCTAGON, spacing=9.0, border=0.0),
       ),
   )
   project.show(lids_only=True)


Organic & Botanical Patterns
----------------------------

Organic Voronoi Scatter (``PatternType.VORONOI``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deterministic organic scatter of varying-radius cells on a jittered grid.

.. pythonscad-example::

   project = Project("VoronoiPatternDemo")
   project.box(
       BoxType.SLIDING,
       "VoronoiLid",
       size=(80.0, 60.0, 20.0),
       color=Color("seagreen"),
       fingernail_catch=False,
       catch_radius=0.0,
       lid=LidBuilder(
           pattern=PatternBuilder(PatternType.VORONOI, spacing=9.0, border=0.0),
       ),
   )
   project.show(lids_only=True)


Interlocking Midrib Leaves (``PatternType.LEAF``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pointed-oval botanical leaves, each divided by a central midrib, arranged in offset rows.

.. pythonscad-example::

   project = Project("LeafPatternDemo")
   project.box(
       BoxType.SLIDING,
       "LeafLid",
       size=(80.0, 60.0, 20.0),
       color=Color("forestgreen"),
       fingernail_catch=False,
       catch_radius=0.0,
       lid=LidBuilder(
           pattern=PatternBuilder(PatternType.LEAF, spacing=12.0, border=0.0),
       ),
   )
   project.show(lids_only=True)


Edge-to-Edge Leaf Tessellation (``PatternType.LEAF_TESSELLATION``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tessellating leaf silhouettes that tile the plane edge-to-edge so the remaining material forms a continuous net of leaf outlines.

.. pythonscad-example::

   project = Project("LeafTessPatternDemo")
   project.box(
       BoxType.SLIDING,
       "LeafTessLid",
       size=(80.0, 60.0, 20.0),
       color=Color("darkolivegreen"),
       fingernail_catch=False,
       catch_radius=0.0,
       lid=LidBuilder(
           pattern=PatternBuilder(PatternType.LEAF_TESSELLATION, spacing=14.0, border=0.0),
       ),
   )
   project.show(lids_only=True)


Veined Leaf Tessellation (``PatternType.LEAF_VEINS``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The edge-to-edge leaf tessellation enriched with a central midrib and branching lateral veins inside every leaf.

.. pythonscad-example::

   project = Project("LeafVeinsPatternDemo")
   project.box(
       BoxType.SLIDING,
       "LeafVeinsLid",
       size=(80.0, 60.0, 20.0),
       color=Color("olivedrab"),
       fingernail_catch=False,
       catch_radius=0.0,
       lid=LidBuilder(
           pattern=PatternBuilder(PatternType.LEAF_VEINS, spacing=16.0, border=0.0),
       ),
   )
   project.show(lids_only=True)


Multi-Color Rhombic & Quasicrystal Tessellations
------------------------------------------------

All multi-color tessellations automatically inlay a thin ``0.6 mm`` colored tile skin into the top face of the lid above a continuous ``0.8 mm`` structural floor, backed by a selectable underside lattice (defaulting to ``PatternType.HEX``).

Stepped 3D Cube & Diamond Tessellation (``PatternType.STEPPED_CUBE``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A 4-color isometric stepped cube and diamond rhombic tessellation made of 60°/120° rhombi:

* **Color 0 (``peak_color``)**: Top/peak horizontal diamonds.
* **Color 1 (``valley_color``)**: Valley horizontal diamonds (top face of each 3D cube).
* **Color 2 (``left_color``)**: Left-leaning vertical rhombi (left face of each 3D cube).
* **Color 3 (``right_color``)**: Right-leaning vertical rhombi (right face of each 3D cube).

Configure colors via :meth:`~pyboxbuilder.lid.builder.PatternBuilder.stepped_cube` or ``colors=(peak, valley, left, right)``:

.. pythonscad-example::

   project = Project("SteppedCubeLidDemo")
   project.box(
       BoxType.SLIDING,
       "CubeLid",
       size=(80.0, 60.0, 20.0),
       color=Color("#1e1e2e"),
       fingernail_catch=False,
       catch_radius=0.0,
       lid=LidBuilder(
           pattern=PatternBuilder.stepped_cube(
               peak_color=Color("#f7f749"),
               valley_color=Color("#6366cf"),
               left_color=Color("#23c48e"),
               right_color=Color("#5c5d99"),
               spacing=11.0,
               border=0.0,
           ),
       ),
   )
   project.show(lids_only=True)


Ten-Fold Quasiperiodic Penrose Tessellation (``PatternType.PENROSE``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A non-repeating 10-fold quasiperiodic Penrose rhombus tiling generated via de Bruijn's pentagrid. By default it uses 4 colors separating both thick (72°/108°) and thin (36°/144°) rhombi across alternating pentagrid index parity levels, and accepts 2, 3, 4, 5, or more custom colors via :meth:`~pyboxbuilder.lid.builder.PatternBuilder.penrose` or ``colors=(...)``:

.. pythonscad-example::

   project = Project("PenroseLidDemo")
   project.box(
       BoxType.SLIDING,
       "PenroseLid",
       size=(80.0, 60.0, 20.0),
       color=Color("#1b263b"),
       fingernail_catch=False,
       catch_radius=0.0,
       lid=LidBuilder(
           pattern=PatternBuilder.penrose(
               colors=(
                   Color("#f4d35e"),
                   Color("#ee964b"),
                   Color("#2a9d8f"),
                   Color("#4cc9f0"),
               ),
               spacing=10.0,
               border=0.0,
           ),
       ),
   )
   project.show(lids_only=True)


Eight-Fold Ammann–Beenker Quasicrystal (``PatternType.AMMANN_BEENKER``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An 8-fold quasiperiodic tiling of 45°/135° rhombi and 90° squares generated by de Bruijn's octagrid, defaulting to a 4-color palette across shape and octagrid parity levels:

.. pythonscad-example::

   project = Project("AmmannBeenkerLidDemo")
   project.box(
       BoxType.SLIDING,
       "OctagridLid",
       size=(80.0, 60.0, 20.0),
       color=Color("#1d3557"),
       fingernail_catch=False,
       catch_radius=0.0,
       lid=LidBuilder(
           pattern=PatternBuilder(
               PatternType.AMMANN_BEENKER,
               colors=(
                   Color("#f4d35e"),
                   Color("#4ecdc4"),
                   Color("#e76f51"),
                   Color("#457b9d"),
               ),
               spacing=10.0,
               border=0.0,
           ),
       ),
   )
   project.show(lids_only=True)


Isometric Tumbling Blocks (``PatternType.TUMBLING_BLOCKS``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The classic 3-color isometric cube tessellation where each regular hexagon is subdivided into three 60°/120° rhombi (top diamond, left vertical face, right vertical face):

.. pythonscad-example::

   project = Project("TumblingBlocksLidDemo")
   project.box(
       BoxType.SLIDING,
       "TumblingLid",
       size=(80.0, 60.0, 20.0),
       color=Color("#22223b"),
       fingernail_catch=False,
       catch_radius=0.0,
       lid=LidBuilder(
           pattern=PatternBuilder(
               PatternType.TUMBLING_BLOCKS,
               colors=(
                   Color("#f5e663"),
                   Color("#4ecdc4"),
                   Color("#3b5284"),
               ),
               spacing=11.0,
               border=0.0,
           ),
       ),
   )
   project.show(lids_only=True)


Herringbone Chevron Tessellation (``PatternType.CHEVRON``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A 2-color interlocking 60°/120° herringbone chevron rhombus tiling with alternating up-sloping and down-sloping columns:

.. pythonscad-example::

   project = Project("ChevronLidDemo")
   project.box(
       BoxType.SLIDING,
       "ChevronLid",
       size=(80.0, 60.0, 20.0),
       color=Color("#264653"),
       fingernail_catch=False,
       catch_radius=0.0,
       lid=LidBuilder(
           pattern=PatternBuilder(
               PatternType.CHEVRON,
               colors=(Color("#f4a261"), Color("#2a9d8f")),
               spacing=11.0,
               border=0.0,
           ),
       ),
   )
   project.show(lids_only=True)


Multi-Color Thematic & Geometric Inlays
---------------------------------------

Gaming Dice Faces & Pips (``PatternType.DICE``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rounded D6 die faces (1 through 6) with contrasting inlaid pips (or through-hole pips when ``through_holes=True``):

.. pythonscad-example::

   project = Project("DicePatternLidDemo")
   project.box(
       BoxType.SLIDING,
       "DiceLid",
       size=(80.0, 60.0, 20.0),
       color=Color("indigo"),
       fingernail_catch=False,
       catch_radius=0.0,
       lid=LidBuilder(
           pattern=PatternBuilder(
               PatternType.DICE,
               colors=(Color("white"), Color("crimson")),
               spacing=14.0,
               border=0.0,
           ),
       ),
   )
   project.show(lids_only=True)


Concentric Rings (``PatternType.RING``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Concentric outer rings and inner discs (customizable via ``hole_ratio`` and ``through_holes``):

.. pythonscad-example::

   project = Project("RingPatternLidDemo")
   project.box(
       BoxType.SLIDING,
       "RingLid",
       size=(80.0, 60.0, 20.0),
       color=Color("midnightblue"),
       fingernail_catch=False,
       catch_radius=0.0,
       lid=LidBuilder(
           pattern=PatternBuilder(
               PatternType.RING,
               colors=(Color("gold"), Color("teal")),
               spacing=12.0,
               hole_ratio=0.5,
               border=0.0,
           ),
       ),
   )
   project.show(lids_only=True)


Two-Color Checkerboard (``PatternType.CHECKER``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Alternating checkerboard tiles on an orthogonal grid:

.. pythonscad-example::

   project = Project("CheckerPatternLidDemo")
   project.box(
       BoxType.SLIDING,
       "CheckerLid",
       size=(80.0, 60.0, 20.0),
       color=Color("darkslategray"),
       fingernail_catch=False,
       catch_radius=0.0,
       lid=LidBuilder(
           pattern=PatternBuilder(
               PatternType.CHECKER,
               colors=(Color("ivory"), Color("coral")),
               spacing=10.0,
               border=0.0,
           ),
       ),
   )
   project.show(lids_only=True)


Solid Lids (``PatternType.SOLID`` & ``PatternType.NONE``)
---------------------------------------------------------

Use ``PatternType.SOLID`` or ``PatternType.NONE`` when a completely closed, unperforated lid surface is desired:

.. pythonscad-example::

   project = Project("SolidPatternLidDemo")
   project.box(
       BoxType.SLIDING,
       "SolidLid",
       size=(80.0, 60.0, 20.0),
       color=Color("darkslateblue"),
       fingernail_catch=False,
       catch_radius=0.0,
       lid=LidBuilder(
           pattern=PatternBuilder(PatternType.SOLID, border=0.0),
       ),
   )
   project.show(lids_only=True)


Pattern-Matched Stacking (``StackableMode.PATTERN``)
----------------------------------------------------

Setting ``stackable=StackableMode.PATTERN`` (:class:`~pyboxbuilder.enums.StackableMode`) matches the lid's pattern directly onto the underside of the box body. The lid's pattern web is raised above the lid surface with 45° self-supporting draft chamfers, while a matching 45°-drafted recessed pattern groove is carved into the underside of the box floor so stacked boxes lock into the exact same pattern grid without support material.

Unlike the standalone lid gallery above, the stacking setup below renders **both the lid and the box** (``project.show(show_lids=True)``) with an exploded vertical separation so the patterned lid, the box compartments, and the matching underside pattern lattice can all be inspected together:

.. pythonscad-example::

   project = Project("PatternMatchedStackingDemo")
   lower_box = project.box(
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
   lower_box.compartment("TokensA", width_ratio=0.5, holds_pieces=True)
   lower_box.compartment("TokensB", width_ratio=0.5, holds_pieces=True)
   upper_box = project.box(
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
   upper_box.compartment("Cards", holds_pieces=True)
   project.show(show_lids=True)

