Interactive PythonSCAD GUI Forms
================================

In addition to full multi-box :class:`~pyboxbuilder.project.core.Project` inserts,
``pyboxbuilder`` provides two one-line classes —
:class:`~pyboxbuilder.interactive.Box` and :class:`~pyboxbuilder.interactive.CardBox` —
that implement **PythonSCAD's Qt6 interactive class-form protocol**
(``__new__``, ``get_calltip``, and ``on_editor_trigger``).

They give you two benefits at once:

* **Zero-boilerplate standalone boxes:** Create any of the 26 box types or a
  sleeved/angled card tray in a single line without setting up a ``Project`` or
  declaring a game inventory.
* **Native PyQt6 parameter dialog in PythonSCAD:** Click the ``▷`` calltip icon
  (or press ``Ctrl+Shift+Space`` inside an existing call) to edit dimensions,
  box type, lid pattern, label, sleeves, and divider slots in a GUI form that
  automatically rewrites your script when you press **OK**.

.. note::
   Interactive GUI forms require a **Qt6 build of PythonSCAD** (which bundles
   ``PyQt6``) with editor autocompletion enabled in preferences. In Qt5 builds,
   headless CLI runs, or standard Python, ``Box(...)`` and ``CardBox(...)``
   still work identically as normal one-line geometry builders.

Setup (``.pythonscadrc``)
-------------------------

To make ``Box`` and ``CardBox`` available in every PythonSCAD editor session,
add one line to your ``~/.pythonscadrc`` file:

.. code-block:: python

   from pyboxbuilder import Box, CardBox

You can also import them directly at the top of any script.

Using the GUI Form in PythonSCAD
--------------------------------

1. **Insert a new box:** Type ``Box(`` or ``CardBox(`` in the PythonSCAD editor.
   The autocomplete calltip appears with a clickable ``▷`` marker.
2. **Open the parameter form:** Click ``▷`` (or place your cursor anywhere
   inside an existing ``Box(...)`` or ``CardBox(...)`` call and press
   **Ctrl+Shift+Space** — **Control+Shift+Space** on macOS).
3. **Adjust parameters visually:** Choose the box type, dimensions, wall/floor/lid
   thicknesses, lid pattern, label, catch type, elephant's-foot chamfer, or card
   sleeve/orientation/divider settings.
4. **Apply back to code:** Press **OK**. PythonSCAD rewrites the arguments in
   your script automatically, emitting only non-default parameters while
   preserving any extra keyword arguments you wrote by hand.

One-Line Standalone ``Box``
---------------------------

Calling ``Box(...)`` directly returns a 3D solid (the box body, plus its lid
positioned alongside it when ``show_lid=True``):

.. pythonscad-example::

   from pyboxbuilder import Box

   Box(
       box_type="sliding",
       width=80.0,
       length=60.0,
       height=28.0,
       pattern="hex",
       label="TOKENS",
       base_chamfer=0.4,
   ).show()

Key parameters exposed in the ``Box`` form:

* ``box_type`` — any of the 26 :class:`~pyboxbuilder.enums.BoxType` values (e.g. ``"sliding"``, ``"cap"``, ``"slipover"``, ``"magnetic"``, ``"no_lid"``, ``"card_tray"``).
* ``width``, ``length``, ``height`` — outer box dimensions in mm.
* ``wall_thickness``, ``floor_thickness``, ``lid_thickness`` — material thicknesses in mm.
* ``pattern``, ``label`` — lid surface pattern and engraved/framed title text.
* ``catch_type``, ``stackable``, ``base_chamfer`` — lid retention, stacking mode, and bottom elephant's-foot chamfer.
* ``show_lid`` — show body and lid side-by-side (``True``) or body only (``False``).

One-Line ``CardBox`` (Flat, Vertical, Angled & Sleeved)
-------------------------------------------------------

``CardBox(...)`` automatically computes the box dimensions from card size, card
count, sleeve brand/SKU, and storage orientation. Setting ``orientation`` to
``"vertical"`` or ``"angled"`` automatically selects ``BoxType.CARD_TRAY`` with
optional removable divider slots:

.. pythonscad-example::

   from pyboxbuilder import CardBox

   CardBox(
       card_width=63.5,
       card_length=88.0,
       count=80,
       sleeved=True,
       sleeve="Gamegenic",
       orientation="angled",
       tilt_angle=25.0,
       divider_slots=3,
   ).show()

Key parameters exposed in the ``CardBox`` form:

* ``card_width``, ``card_length``, ``count``, ``thickness`` — unsleeved card dimensions and deck count.
* ``sleeved``, ``sleeve`` — toggle sleeve sizing on/off and pick a brand (``"Gamegenic"``, ``"Sleeve Kings"``, ``"Mayday Games"``), grade (``"Standard"``, ``"Premium"``), or catalog SKU.
* ``orientation``, ``tilt_angle``, ``divider_slots`` — store cards ``"flat"``, ``"vertical"``, or ``"angled"`` with slotted divider rails.
* ``box_type`` — leave blank to auto-select ``"sliding"`` for flat stacks or ``"card_tray"`` for vertical/angled rows, or override with any box type.
