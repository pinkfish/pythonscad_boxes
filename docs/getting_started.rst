Getting Started
===============

Welcome to ``pyboxbuilder``! This guide introduces the core concepts and walks you through:

1. **Creating your very first box** and previewing it in 3D.
2. **Designing standalone boxes** (such as dice boxes or modular token trays) without an enclosing game box.
3. **Building a complete game insert** that packs multiple boxes, trays, and automatic spacer trays into a publisher's game box.
4. **Exporting and 3D printing** your designs using the built-in CLI runner.

.. note::
   All example code below uses the interactive 3D WebGL viewer. You can rotate, pan, and zoom the rendered models directly in your browser.

Creating Your First Box
-----------------------

Every box in ``pyboxbuilder`` belongs to a :class:`~pyboxbuilder.project.core.Project`. A project defines project-wide defaults (such as wall thickness, floor thickness, and edge rounding) and holds all the boxes you create.

Here is a minimal script that creates a simple dice or token box with a sliding lid:

.. pythonscad-example::

    from pyboxbuilder import BoxType, Project

    # Create a project. Setting game_box_size=None indicates a standalone box.
    project = Project("Quickstart", game_box_size=None)

    # Add a sliding-lid box
    project.box(
        BoxType.SLIDING,
        "DiceBox",
        size=(65.0, 45.0, 25.0),
        wall_thickness=2.0,
    )

    # In PythonSCAD, preview the box and its lid
    project.show(show_lids=True)

In this snippet:

* :class:`~pyboxbuilder.project.core.Project` initializes the project. Specifying ``game_box_size=None`` tells ``pyboxbuilder`` that this box is standalone and does not need to be packed inside a board game's cardboard box.
* :meth:`~pyboxbuilder.project.core.Project.box` registers a new box. We choose ``BoxType.SLIDING``, give it a label (``"DiceBox"``), and assign it an outer size of 65 mm × 45 mm × 25 mm.
* :meth:`~pyboxbuilder.project.core.Project.show` renders the pieces in PythonSCAD. Passing ``show_lids=True`` displays both the box body and its sliding lid side-by-side.

Designing Standalone Boxes
--------------------------

Standalone boxes are ideal when you want to print individual tabletop organizers, such as:

* Bit trays and token holders used during gameplay.
* Dice vaults and miniature boxes.
* Modular organizer bins with magnetic or interlocking lids.

When ``game_box_size=None``, each box is exported independently without constraints from an enclosing game box.

Dividing into Compartments
~~~~~~~~~~~~~~~~~~~~~~~~~~

Rather than calculating internal wall widths and floor offsets by hand, you can define compartments using relative width and length ratios via ``box.compartment(...)``:

.. pythonscad-example::

    from pyboxbuilder import BoxType, Project

    project = Project("TokenOrganizer", game_box_size=None)

    tray = project.box(
        BoxType.NO_LID,
        "ResourceTray",
        size=(85.0, 55.0, 22.0),
        wall_thickness=2.0,
    )

    # Divide into two equal wells across the width (50% each)
    # holds_pieces=True rounds the bottom corners into an ergonomic scoop
    tray.compartment("Wood", width_ratio=0.5, holds_pieces=True)
    tray.compartment("Stone", width_ratio=0.5, holds_pieces=True)

    project.show()

Key features used here:

* ``width_ratio=0.5``: Divides the usable interior into two equal wells. The library calculates divider wall thickness and floor spacing automatically.
* ``holds_pieces=True``: Shapes the bottom corners into smooth ergonomic scoops so tokens can be swept out easily with a fingertip.

Adding Lids, Patterns, and Labels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can customize lids with geometric patterns, finger grips, or text labels:

.. code-block:: python

    from pyboxbuilder import BoxType, PatternType, Project

    project = Project("FancyBox", game_box_size=None)

    fancy = project.box(
        BoxType.SLIDING,
        "Gems",
        size=(70.0, 50.0, 30.0),
    )

    # Decorate the sliding lid with a hex pattern
    fancy.lid.pattern(PatternType.HEX, border_margin_mm=4.0)

See the :doc:`box_types` guide for full details on each lid style (capacitive, magnetic, hinge, slipover, and sliding).

Building a Game Box Insert
--------------------------

When designing an insert for a retail board game, the goal is to pack multiple sub-boxes snugly into the publisher's cardboard box, leaving room at the top for folded boards and rulebooks.

To build a full insert:

1. Measure the inside dimensions of the cardboard game box ``(width, length, height)`` in mm.
2. Pass ``game_box_size=(W, L, H)`` to :class:`~pyboxbuilder.project.core.Project`.
3. Set ``board_thickness`` to reserve height at the top for the game board and rulebook.
4. Set ``generate_spacers=True`` to automatically fill leftover voids with custom-fit spacer trays.

Arranging Boxes & Generating Spacers
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can position boxes declaratively using :func:`~pyboxbuilder.layout.columns`, :func:`~pyboxbuilder.layout.rows`, and :func:`~pyboxbuilder.layout.stack`, or explicit coordinates, and let the spacer generator compute the rest:

.. pythonscad-example::

    from pyboxbuilder import BoxType, Project

    # Define the game box interior: 100mm x 90mm x 28mm
    project = Project(
        "GameInsertDemo",
        game_box_size=(100.0, 90.0, 28.0),
        board_thickness=6.0,   # Leaves 6mm at the top for the board
        generate_spacers=True, # Auto-fills dead space with open trays
    )

    # Box 1: An open card caddy
    project.box(
        BoxType.NO_LID,
        "Cards",
        size=(46.0, 50.0, 20.0),
        position=(2.0, 2.0, 0.0),
    )

    # Box 2: A sliding token box
    project.box(
        BoxType.SLIDING,
        "Tokens",
        size=(46.0, 50.0, 20.0),
        position=(50.0, 2.0, 0.0),
    )

    project.show(show_lids=True)

In this preview:

* The **Cards** and **Tokens** boxes are placed side-by-side.
* The remaining void along the back of the game box is automatically detected and filled with a custom-fitted spacer tray (``Spacer_...``).
* When packed into the game box, the components and spacers lock together to prevent shifting when the game is stored vertically.

Exporting and 3D Printing with CLI
----------------------------------

Every script can be run through the unified CLI entrypoint :func:`~pyboxbuilder.run`:

.. code-block:: python

    from pyboxbuilder import BoxType, Project, run

    project = Project("MyInsert", game_box_size=(295.0, 295.0, 70.0))
    # ... define boxes ...

    if __name__ == "__main__":
        run(project)

Command-Line Usage
~~~~~~~~~~~~~~~~~~

Preview in PythonSCAD:

.. code-block:: bash

    python my_insert.py

Preview with all lids included:

.. code-block:: bash

    python my_insert.py --lids

Preview only a specific box:

.. code-block:: bash

    python my_insert.py --box Tokens

Export printable 3MF / STL files:

.. code-block:: bash

    python my_insert.py --export --out ./output/

Next Steps
----------

* Explore all available lid mechanisms and box styles in :doc:`box_types`.
* Learn advanced multi-column layouts and custom spacer options in :doc:`layout_and_spacers`.
* Browse the full class and method documentation in the :doc:`api`.
