Lid Patterns Guide & Gallery
=============================

``pyboxbuilder`` provides 20 lid surface patterns and multi-color tessellations via :class:`~pyboxbuilder.enums.PatternType` and :class:`~pyboxbuilder.lid.builder.PatternBuilder`.

Patterns fall into two architectural categories:

1. **Perforated Through-Hole Lattices & Botanical Tilings** (``HEX``, ``DENSE_HEX``, ``SQUARE``, ``CIRCLE``, ``TRIANGLE``, ``DENSE_TRIANGLE``, ``OCTAGON``, ``VORONOI``, ``LEAF``, ``LEAF_TESSELLATION``, ``LEAF_VEINS``): Cut open lattices through the lid within the solid perimeter border, saving filament while keeping contents visible and ventilated. Any of these can also be inlaid as a colored top layer by setting ``inlay=True`` or passing ``colors=(...)``.
2. **Multi-Color Inlays & Rhombic / Quasicrystal Tessellations** (``STEPPED_CUBE``, ``PENROSE``, ``AMMANN_BEENKER``, ``TUMBLING_BLOCKS``, ``CHEVRON``, ``DICE``, ``RING``, ``CHECKER``): Inlay a thin ``0.6 mm`` colored tile skin into the top face of the lid above a continuous ``0.8 mm`` structural floor and a selectable underside backing lattice (defaulting to ``PatternType.HEX`` via ``backing_pattern``) to minimize plastic use while preserving full lid strength.

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
   box = project.box(
       BoxType.SLIDING,
       "HexBox",
       size=(70.0, 55.0, 20.0),
       color=Color("darkslateblue"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.HEX, spacing=9.0),
       ).titled("HEX"),
   )
   box.compartment("Well", holds_pieces=True)
   project.show(show_lids=True)


Dense Honeycomb Grid (``PatternType.DENSE_HEX``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A tighter-pitch hexagonal honeycomb that keeps smaller game pieces safely enclosed while maximizing open area.

.. pythonscad-example::

   project = Project("DenseHexPatternDemo")
   box = project.box(
       BoxType.SLIDING,
       "DenseHexBox",
       size=(70.0, 55.0, 20.0),
       color=Color("teal"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.DENSE_HEX),
       ).titled("DENSE"),
   )
   box.compartment("Well", holds_pieces=True)
   project.show(show_lids=True)


Square Grid (``PatternType.SQUARE``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Orthogonal square cutouts aligned to a Cartesian grid.

.. pythonscad-example::

   project = Project("SquarePatternDemo")
   box = project.box(
       BoxType.SLIDING,
       "SquareBox",
       size=(70.0, 55.0, 20.0),
       color=Color("darkslategray"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("coral"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.SQUARE, spacing=9.0),
       ).titled("SQUARE"),
   )
   box.compartment("Well", holds_pieces=True)
   project.show(show_lids=True)


Circular Grid (``PatternType.CIRCLE``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Circular perforations arranged on an orthogonal grid.

.. pythonscad-example::

   project = Project("CirclePatternDemo")
   box = project.box(
       BoxType.SLIDING,
       "CircleBox",
       size=(70.0, 55.0, 20.0),
       color=Color("royalblue"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.CIRCLE, spacing=9.0),
       ).titled("CIRCLE"),
   )
   box.compartment("Well", holds_pieces=True)
   project.show(show_lids=True)


Alternating Triangle Truss (``PatternType.TRIANGLE``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Equilateral triangular cutouts alternating point-up and point-down to form a diagonal truss web.

.. pythonscad-example::

   project = Project("TrianglePatternDemo")
   box = project.box(
       BoxType.SLIDING,
       "TriangleBox",
       size=(70.0, 55.0, 20.0),
       color=Color("crimson"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("silver"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.TRIANGLE, spacing=9.0),
       ).titled("TRUSS"),
   )
   box.compartment("Well", holds_pieces=True)
   project.show(show_lids=True)


Dense Triangle Truss (``PatternType.DENSE_TRIANGLE``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The alternating triangular truss lattice at a finer pitch.

.. pythonscad-example::

   project = Project("DenseTrianglePatternDemo")
   box = project.box(
       BoxType.SLIDING,
       "DenseTriangleBox",
       size=(70.0, 55.0, 20.0),
       color=Color("firebrick"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.DENSE_TRIANGLE),
       ).titled("DENSE TRI"),
   )
   box.compartment("Well", holds_pieces=True)
   project.show(show_lids=True)


Octagonal Lattice (``PatternType.OCTAGON``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Regular octagonal openings leaving diagonal-cross webs between neighboring cells.

.. pythonscad-example::

   project = Project("OctagonPatternDemo")
   box = project.box(
       BoxType.SLIDING,
       "OctagonBox",
       size=(70.0, 55.0, 20.0),
       color=Color("darkgreen"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.OCTAGON, spacing=9.0),
       ).titled("OCTAGON"),
   )
   box.compartment("Well", holds_pieces=True)
   project.show(show_lids=True)


Organic & Botanical Patterns
----------------------------

Organic Voronoi Scatter (``PatternType.VORONOI``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Deterministic organic scatter of varying-radius cells on a jittered grid.

.. pythonscad-example::

   project = Project("VoronoiPatternDemo")
   box = project.box(
       BoxType.SLIDING,
       "VoronoiBox",
       size=(70.0, 55.0, 20.0),
       color=Color("seagreen"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.VORONOI, spacing=9.0),
       ).titled("VORONOI"),
   )
   box.compartment("Well", holds_pieces=True)
   project.show(show_lids=True)


Interlocking Midrib Leaves (``PatternType.LEAF``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Pointed-oval botanical leaves, each divided by a central midrib, arranged in offset rows.

.. pythonscad-example::

   project = Project("LeafPatternDemo")
   box = project.box(
       BoxType.SLIDING,
       "LeafBox",
       size=(70.0, 55.0, 20.0),
       color=Color("forestgreen"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.LEAF, spacing=12.0),
       ).titled("LEAF"),
   )
   box.compartment("Well", holds_pieces=True)
   project.show(show_lids=True)


Edge-to-Edge Leaf Tessellation (``PatternType.LEAF_TESSELLATION``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Tessellating leaf silhouettes that tile the plane edge-to-edge so the remaining material forms a continuous net of leaf outlines.

.. pythonscad-example::

   project = Project("LeafTessPatternDemo")
   box = project.box(
       BoxType.SLIDING,
       "LeafTessBox",
       size=(70.0, 55.0, 20.0),
       color=Color("darkolivegreen"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.LEAF_TESSELLATION, spacing=14.0),
       ).titled("CANOPY"),
   )
   box.compartment("Well", holds_pieces=True)
   project.show(show_lids=True)


Veined Leaf Tessellation (``PatternType.LEAF_VEINS``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The edge-to-edge leaf tessellation enriched with a central midrib and branching lateral veins inside every leaf.

.. pythonscad-example::

   project = Project("LeafVeinsPatternDemo")
   box = project.box(
       BoxType.SLIDING,
       "LeafVeinsBox",
       size=(70.0, 55.0, 20.0),
       color=Color("olivedrab"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.LEAF_VEINS, spacing=16.0),
       ).titled("FLORA"),
   )
   box.compartment("Well", holds_pieces=True)
   project.show(show_lids=True)


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

   project = Project("SteppedCubeDemo")
   box = project.box(
       BoxType.SLIDING,
       "CubeLidBox",
       size=(80.0, 65.0, 22.0),
       color=Color("#1e1e2e"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder.stepped_cube(
               peak_color=Color("#f7f749"),
               valley_color=Color("#6366cf"),
               left_color=Color("#23c48e"),
               right_color=Color("#5c5d99"),
               spacing=11.0,
           ),
       ).titled("CUBES"),
   )
   box.compartment("Tokens", holds_pieces=True)
   project.show(show_lids=True)


Ten-Fold Quasiperiodic Penrose Tessellation (``PatternType.PENROSE``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A non-repeating 10-fold quasiperiodic Penrose rhombus tiling generated via de Bruijn's pentagrid. By default it uses 4 colors separating both thick (72°/108°) and thin (36°/144°) rhombi across alternating pentagrid index parity levels, and accepts 2, 3, 4, 5, or more custom colors via :meth:`~pyboxbuilder.lid.builder.PatternBuilder.penrose` or ``colors=(...)``:

.. pythonscad-example::

   project = Project("PenroseDemo")
   box = project.box(
       BoxType.SLIDING,
       "PenroseLidBox",
       size=(80.0, 65.0, 22.0),
       color=Color("#1b263b"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("#f4d35e"),
           text_color=Color("white"),
           pattern=PatternBuilder.penrose(
               colors=(
                   Color("#f4d35e"),
                   Color("#ee964b"),
                   Color("#2a9d8f"),
                   Color("#4cc9f0"),
               ),
               spacing=10.0,
           ),
       ).titled("PENROSE"),
   )
   box.compartment("Tiles", holds_pieces=True)
   project.show(show_lids=True)


Eight-Fold Ammann–Beenker Quasicrystal (``PatternType.AMMANN_BEENKER``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

An 8-fold quasiperiodic tiling of 45°/135° rhombi and 90° squares generated by de Bruijn's octagrid, defaulting to a 4-color palette across shape and octagrid parity levels:

.. pythonscad-example::

   project = Project("AmmannBeenkerDemo")
   box = project.box(
       BoxType.SLIDING,
       "OctagridBox",
       size=(80.0, 65.0, 22.0),
       color=Color("#1d3557"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("#f4d35e"),
           text_color=Color("white"),
           pattern=PatternBuilder(
               PatternType.AMMANN_BEENKER,
               colors=(
                   Color("#f4d35e"),
                   Color("#4ecdc4"),
                   Color("#e76f51"),
                   Color("#457b9d"),
               ),
               spacing=10.0,
           ),
       ).titled("OCTAGRID"),
   )
   box.compartment("Well", holds_pieces=True)
   project.show(show_lids=True)


Isometric Tumbling Blocks (``PatternType.TUMBLING_BLOCKS``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The classic 3-color isometric cube tessellation where each regular hexagon is subdivided into three 60°/120° rhombi (top diamond, left vertical face, right vertical face):

.. pythonscad-example::

   project = Project("TumblingBlocksDemo")
   box = project.box(
       BoxType.SLIDING,
       "TumblingBox",
       size=(80.0, 65.0, 22.0),
       color=Color("#22223b"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("#f5e663"),
           text_color=Color("white"),
           pattern=PatternBuilder(
               PatternType.TUMBLING_BLOCKS,
               colors=(
                   Color("#f5e663"),
                   Color("#4ecdc4"),
                   Color("#3b5284"),
               ),
               spacing=11.0,
           ),
       ).titled("BLOCKS"),
   )
   box.compartment("Well", holds_pieces=True)
   project.show(show_lids=True)


Herringbone Chevron Tessellation (``PatternType.CHEVRON``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

A 2-color interlocking 60°/120° herringbone chevron rhombus tiling with alternating up-sloping and down-sloping columns:

.. pythonscad-example::

   project = Project("ChevronDemo")
   box = project.box(
       BoxType.SLIDING,
       "ChevronBox",
       size=(80.0, 65.0, 22.0),
       color=Color("#264653"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("#f4a261"),
           text_color=Color("white"),
           pattern=PatternBuilder(
               PatternType.CHEVRON,
               colors=(Color("#f4a261"), Color("#2a9d8f")),
               spacing=11.0,
           ),
       ).titled("CHEVRON"),
   )
   box.compartment("Well", holds_pieces=True)
   project.show(show_lids=True)


Multi-Color Thematic & Geometric Inlays
---------------------------------------

Gaming Dice Faces & Pips (``PatternType.DICE``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Rounded D6 die faces (1 through 6) with contrasting inlaid pips (or through-hole pips when ``through_holes=True``):

.. pythonscad-example::

   project = Project("DicePatternDemo")
   box = project.box(
       BoxType.SLIDING,
       "DiceLidBox",
       size=(80.0, 65.0, 22.0),
       color=Color("indigo"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(
               PatternType.DICE,
               colors=(Color("white"), Color("crimson")),
               spacing=14.0,
           ),
       ).titled("DICE"),
   )
   box.compartment("Well", holds_pieces=True)
   project.show(show_lids=True)


Concentric Rings (``PatternType.RING``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Concentric outer rings and inner discs (customizable via ``hole_ratio`` and ``through_holes``):

.. pythonscad-example::

   project = Project("RingPatternDemo")
   box = project.box(
       BoxType.SLIDING,
       "RingLidBox",
       size=(80.0, 65.0, 22.0),
       color=Color("midnightblue"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(
               PatternType.RING,
               colors=(Color("gold"), Color("teal")),
               spacing=12.0,
               hole_ratio=0.5,
           ),
       ).titled("RINGS"),
   )
   box.compartment("Well", holds_pieces=True)
   project.show(show_lids=True)


Two-Color Checkerboard (``PatternType.CHECKER``)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Alternating checkerboard tiles on an orthogonal grid:

.. pythonscad-example::

   project = Project("CheckerPatternDemo")
   box = project.box(
       BoxType.SLIDING,
       "CheckerLidBox",
       size=(80.0, 65.0, 22.0),
       color=Color("darkslategray"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(
               PatternType.CHECKER,
               colors=(Color("ivory"), Color("coral")),
               spacing=10.0,
           ),
       ).titled("CHECKER"),
   )
   box.compartment("Well", holds_pieces=True)
   project.show(show_lids=True)


Solid Lids (``PatternType.SOLID`` & ``PatternType.NONE``)
---------------------------------------------------------

Use ``PatternType.SOLID`` or ``PatternType.NONE`` when a completely closed, unperforated lid surface is desired:

.. pythonscad-example::

   project = Project("SolidPatternDemo")
   box = project.box(
       BoxType.SLIDING,
       "SolidLidBox",
       size=(70.0, 55.0, 20.0),
       color=Color("darkslateblue"),
       lid=LidBuilder(
           label_mode=LabelMode.FRAMED,
           frame_color=Color("gold"),
           text_color=Color("white"),
           pattern=PatternBuilder(PatternType.SOLID),
       ).titled("SOLID"),
   )
   box.compartment("Well", holds_pieces=True)
   project.show(show_lids=True)

