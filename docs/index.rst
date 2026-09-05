pyboxbuilder
============

**High-Precision Board Game Inserts & Parametric 3D Printable Box Toolkit for PythonSCAD**

``pyboxbuilder`` is a declarative 3D modeling and board game insert design framework. Built on top of `PythonSCAD <https://github.com/pythonscad/pythonscad>`_ and `pybosl2 <https://github.com/thewhodidthis/pybosl2>`_, it transforms high-level descriptions of games, boxes, and game pieces into production-ready CSG geometry, interactive 3D WebGL models, and printable 3MF files.

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
       lid=LidBuilder(
           pattern=PatternBuilder(PatternType.HEX),
           text="TOKENS",
       ),
   )
   tray = project.box(
       BoxType.NO_LID,
       "Dice",
       size=(46.0, 50.0, 20.0),
       position=(50.0, 2.0, 0.0),
   )
   tray.compartment("D6", width_ratio=0.5, holds_pieces=True)
   tray.compartment("D20", width_ratio=0.5, holds_pieces=True)
   project.show(show_lids=True)

Why pyboxbuilder?
-----------------

Designing inserts by hand in traditional CAD requires tedious trial-and-error math: subtracting wall thicknesses, offsetting dovetail channels, computing lid clearances, and laying out rectangular coordinates. When a box size or card count changes, the entire model must be manually recalculated.

``pyboxbuilder`` replaces manual arithmetic with declarative constraints:

* **Specify What You Need, Not the Booleans**: Define box types, dimensions, card counts, token divisions, and lid decorations. The library derives all mating clearances, corner roundings, draft angles, and boolean carve-outs automatically.
* **Guaranteed Printability**: Every geometric parameter has defaults derived from the box's scale and 3D printing physics (0.4mm nozzle standards, overhang limits, finger reach ergonomics).
* **Instant Interactive 3D Previews**: Inspect models in PythonSCAD's GUI or embed interactive WebGL viewers directly in documentation and web pages.
* **Production 3MF & PDF Pipelines**: Export multi-color (MMU) or single-color 3MF files with geometric change detection (unchanged boxes build in milliseconds) alongside multi-page exploded 3D assembly guides (``layout.pdf``).

Core System Architecture
------------------------

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Subsystem
     - Description & Capabilities
   * - **Box Builders**
     - 13 typed builders in :mod:`pyboxbuilder.builders` supporting sliding dovetails with snap catches, friction caps, telescoping slipovers, print-in-place and filament-pin hinges, magnetic vaults, inset lids, stackable open bins, card libraries, and polygon path footprints.
   * - **Compartments & Ergonomics**
     - Ratio-based compartment division (``box.compartment(...)``), ergonomic rounded token scoops (``holds_pieces=True``), full-depth push-through holes, hex grids, and arbitrary SVG pocket silhouettes.
   * - **Lid Decoration**
     - 11 surface patterns (hex, dense hex, triangles, voronoi, leaf tessellations), multi-color MMU inlays, and embossed/engraved labels with automatic font scaling (:class:`~pyboxbuilder.lid.builder.LidBuilder`).
   * - **Layout & 3D Packing**
     - Declarative relative layout trees (:func:`~pyboxbuilder.layout.columns`, :func:`~pyboxbuilder.layout.rows`, :func:`~pyboxbuilder.layout.stack`) or automated 3D skyline bin packing within the declared :attr:`~pyboxbuilder.project.core.Project.game_box_size`.
   * - **Automatic Spacers**
     - 3D void sweep, merge, and generation of custom-fit open spacer trays (``generate_spacers=True``) to secure components during vertical shelf storage.
   * - **Card & Sleeve Support**
     - Built-in card dimension catalog and sleeve clearance formulas for standard board game card sizes and premium sleeves.

Documentation Index
-------------------

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   getting_started
   box_types
   layout_and_spacers

.. toctree::
   :maxdepth: 2
   :caption: API Reference

   api
