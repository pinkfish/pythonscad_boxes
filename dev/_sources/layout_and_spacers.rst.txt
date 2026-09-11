Auto-Layout & Automatic Spacers
===============================

Designing a board game insert requires arranging multiple boxes into the outer game box without collisions, while preventing trays from sliding around when the game box is stored vertically or transported.

``pyboxbuilder`` provides two complementary layout workflows:

1. **Declarative Structural Layout** (:func:`~pyboxbuilder.layout.columns`, :func:`~pyboxbuilder.layout.rows`, :func:`~pyboxbuilder.layout.stack`): State how boxes are arranged relative to each other, and let the library calculate their physical 3D positions.
2. **Automatic 3D Bin Packing**: Let the guillotine 3D packing engine arrange boxes within the container automatically.
3. **Automatic Spacer Generation** (``generate_spacers=True``): Automatically detect leftover voids inside the game box and generate printable filler trays to lock the insert securely in place.

.. contents:: On this page
   :local:
   :depth: 2


Declarative Arrangement
-----------------------

In real board game inserts, trays are tightly structured: player boxes stack in one column, card wells line up in a row, and resource trays fill another column. Specifying absolute XYZ coordinates manually is brittle because resizing any single tray forces recalculating every other box's coordinates.

The :mod:`pyboxbuilder.layout` module solves this by letting you describe the arrangement hierarchically:

- :func:`~pyboxbuilder.layout.columns`: Arranges children side-by-side along the X-axis (width).
- :func:`~pyboxbuilder.layout.rows`: Arranges children front-to-back along the Y-axis (length).
- :func:`~pyboxbuilder.layout.stack`: Arranges children bottom-to-top along the Z-axis (height).

Groups can be nested arbitrarily, and you can specify a ``gap`` (in mm) between adjacent boxes to ensure clearance for easy removal.

.. pythonscad-example::

   project = Project("ArrangeDemo", game_box_size=(130.0, 90.0, 30.0))

   # Define the boxes by size without specifying (x, y, z) positions:
   project.box(BoxType.CAP, "P1", size=(40.0, 40.0, 20.0), lid=LidBuilder(text="P1"))
   project.box(BoxType.CAP, "P2", size=(40.0, 40.0, 20.0), lid=LidBuilder(text="P2"))
   project.box(BoxType.CAP, "Cards", size=(40.0, 80.0, 20.0), lid=LidBuilder(text="CARDS"))
   project.box(BoxType.SLIDING, "Tokens", size=(40.0, 80.0, 20.0), lid=LidBuilder(text="TOKENS"))

   # Arrange in 3 columns:
   # Col 1: Two player boxes along Y
   # Col 2: Card box
   # Col 3: Sliding token box
   project.arrange(
       columns(
           rows("P1", "P2"),
           "Cards",
           "Tokens",
           gap=2.0,
       )
   )

   project.show(show_lids=True)


Automatic 3D Bin Packing
------------------------

If you do not call :meth:`~pyboxbuilder.project.core.Project.arrange` and omit explicit ``position=(x, y, z)`` coordinates, ``pyboxbuilder`` automatically runs its 3D guillotine bin packer (:mod:`pyboxbuilder.packing.guillotine`).

The packer optimizes the placement of all boxes to fit inside the declared :attr:`~pyboxbuilder.project.core.Project.game_box_size`. If the boxes cannot fit, it reports a :class:`~pyboxbuilder.packing.layout.PackingError` identifying the overflow.


Automatic Spacer Generation
---------------------------

Commercial game boxes rarely match the exact sum of your components' dimensions. When an insert leaves unfilled space along a side or corner, components will shift, slide, and open during shelf storage or travel.

When ``generate_spacers=True`` is passed to :class:`~pyboxbuilder.project.core.Project` (enabled by default), ``pyboxbuilder``:

1. Computes the geometric difference between the outer ``game_box_size`` and the placed boxes.
2. Decomposes leftover void regions into printable rectangular trays (:class:`~pyboxbuilder.packing.spacer.SpacerSpec`).
3. Generates hollow organizer trays or solid blocks for each void, sizing them to fill the gap while leaving slight clearance for easy insertion.
4. Includes the spacer trays in 3D previews (:meth:`~pyboxbuilder.project.core.Project.show`), exports (:meth:`~pyboxbuilder.project.core.Project.export`), and blueprint layout PDFs.

Here is an example with two trays in a game box; ``pyboxbuilder`` automatically calculates and renders the spacer trays filling the vacant space:

.. pythonscad-example::

   project = Project(
       "SpacerDemo",
       game_box_size=(90.0, 90.0, 25.0),
       generate_spacers=True,
   )

   # Place two trays leaving an L-shaped void along the back and right:
   project.box(
       BoxType.CAP,
       "MainTray",
       size=(50.0, 50.0, 20.0),
       position=(2.0, 2.0, 0.0),
       lid=LidBuilder(text="MAIN"),
   )
   project.box(
       BoxType.CAP,
       "SideTray",
       size=(32.0, 50.0, 20.0),
       position=(54.0, 2.0, 0.0),
       lid=LidBuilder(text="SIDE"),
   )

   # project.show() renders both boxes AND the auto-generated spacer pieces!
   project.show(show_lids=True)


Inspecting Spacer Pieces in Python
----------------------------------

You can also inspect the generated spacer pieces programmatically via :meth:`~pyboxbuilder.project.core.Project.build`:

.. code-block:: python

   build = project.build()
   for piece in build.pieces:
       if piece.kind == "spacer":
           print(f"Spacer {piece.label}: size={piece.size} at {piece.position}")
