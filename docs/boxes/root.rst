.. _box-insert-root:

Root (root)
===========

Root board game insert — pyboxbuilder port of `examples/root.scad`.

- **Source Script**: ``boxes/root/root.py``
- **Game Box Dimensions**: ``214 × 278 × 67 mm``
- **Boxes**: 20 sub-box(es), 3 spacer tray(s)
- **Box Types Used**: :ref:`BoxType.SLIDING <box-type-sliding>`, :ref:`BoxType.CAP <box-type-cap>`, :ref:`BoxType.NO_LID <box-type-no-lid>`

Full Box Packing
----------------

Interactive 3-D view of all boxes, lids, and spacers packed inside the game box:

.. stl:: ../_stl/boxes/root/BaseCardBox_body.stl,../_stl/boxes/root/BaseCardBox_lid.stl,../_stl/boxes/root/ErieCardBox_body.stl,../_stl/boxes/root/ErieCardBox_lid.stl,../_stl/boxes/root/VagabondCardBox_body.stl,../_stl/boxes/root/VagabondCardBox_lid.stl,../_stl/boxes/root/OverviewCardBox_body.stl,../_stl/boxes/root/OverviewCardBox_lid.stl,../_stl/boxes/root/ItemsBoxBottom_body.stl,../_stl/boxes/root/ItemsBoxBottom_lid.stl,../_stl/boxes/root/ItemsBoxMiddle_body.stl,../_stl/boxes/root/ItemsBoxMiddle_lid.stl,../_stl/boxes/root/ItemsBoxWinter_body.stl,../_stl/boxes/root/ItemsBoxWinter_lid.stl,../_stl/boxes/root/ItemsBoxExtras_body.stl,../_stl/boxes/root/ItemsBoxExtras_lid.stl,../_stl/boxes/root/MarquisBoxBottom_body.stl,../_stl/boxes/root/MarquisBoxBottom_lid.stl,../_stl/boxes/root/MarquisBoxTop_body.stl,../_stl/boxes/root/MarquisBoxTop_lid.stl,../_stl/boxes/root/ErieBoxBottom_body.stl,../_stl/boxes/root/ErieBoxBottom_lid.stl,../_stl/boxes/root/ErieBoxTop_body.stl,../_stl/boxes/root/ErieBoxTop_lid.stl,../_stl/boxes/root/AllianceBoxBottom_body.stl,../_stl/boxes/root/AllianceBoxBottom_lid.stl,../_stl/boxes/root/AllianceBoxTop_body.stl,../_stl/boxes/root/AllianceBoxTop_lid.stl,../_stl/boxes/root/LizardBoxBottom_body.stl,../_stl/boxes/root/LizardBoxBottom_lid.stl,../_stl/boxes/root/LizardBoxTop_body.stl,../_stl/boxes/root/LizardBoxTop_lid.stl,../_stl/boxes/root/RiverfolkBoxBottom_body.stl,../_stl/boxes/root/RiverfolkBoxBottom_lid.stl,../_stl/boxes/root/RiverfolkBoxTop_body.stl,../_stl/boxes/root/RiverfolkBoxTop_lid.stl,../_stl/boxes/root/VagabondBox_body.stl,../_stl/boxes/root/VagabondBox_lid.stl,../_stl/boxes/root/DiceBox_body.stl,../_stl/boxes/root/DiceBox_lid.stl,../_stl/boxes/root/spacer_1.stl,../_stl/boxes/root/spacer_2.stl,../_stl/boxes/root/spacer_3.stl
   :height: 440px

.. raw:: html

   <p><a href="../_stl/boxes/root/BaseCardBox_body.stl" data-stl-combine="../_stl/boxes/root/BaseCardBox_body.stl,../_stl/boxes/root/BaseCardBox_lid.stl,../_stl/boxes/root/ErieCardBox_body.stl,../_stl/boxes/root/ErieCardBox_lid.stl,../_stl/boxes/root/VagabondCardBox_body.stl,../_stl/boxes/root/VagabondCardBox_lid.stl,../_stl/boxes/root/OverviewCardBox_body.stl,../_stl/boxes/root/OverviewCardBox_lid.stl,../_stl/boxes/root/ItemsBoxBottom_body.stl,../_stl/boxes/root/ItemsBoxBottom_lid.stl,../_stl/boxes/root/ItemsBoxMiddle_body.stl,../_stl/boxes/root/ItemsBoxMiddle_lid.stl,../_stl/boxes/root/ItemsBoxWinter_body.stl,../_stl/boxes/root/ItemsBoxWinter_lid.stl,../_stl/boxes/root/ItemsBoxExtras_body.stl,../_stl/boxes/root/ItemsBoxExtras_lid.stl,../_stl/boxes/root/MarquisBoxBottom_body.stl,../_stl/boxes/root/MarquisBoxBottom_lid.stl,../_stl/boxes/root/MarquisBoxTop_body.stl,../_stl/boxes/root/MarquisBoxTop_lid.stl,../_stl/boxes/root/ErieBoxBottom_body.stl,../_stl/boxes/root/ErieBoxBottom_lid.stl,../_stl/boxes/root/ErieBoxTop_body.stl,../_stl/boxes/root/ErieBoxTop_lid.stl,../_stl/boxes/root/AllianceBoxBottom_body.stl,../_stl/boxes/root/AllianceBoxBottom_lid.stl,../_stl/boxes/root/AllianceBoxTop_body.stl,../_stl/boxes/root/AllianceBoxTop_lid.stl,../_stl/boxes/root/LizardBoxBottom_body.stl,../_stl/boxes/root/LizardBoxBottom_lid.stl,../_stl/boxes/root/LizardBoxTop_body.stl,../_stl/boxes/root/LizardBoxTop_lid.stl,../_stl/boxes/root/RiverfolkBoxBottom_body.stl,../_stl/boxes/root/RiverfolkBoxBottom_lid.stl,../_stl/boxes/root/RiverfolkBoxTop_body.stl,../_stl/boxes/root/RiverfolkBoxTop_lid.stl,../_stl/boxes/root/VagabondBox_body.stl,../_stl/boxes/root/VagabondBox_lid.stl,../_stl/boxes/root/DiceBox_body.stl,../_stl/boxes/root/DiceBox_lid.stl,../_stl/boxes/root/spacer_1.stl,../_stl/boxes/root/spacer_2.stl,../_stl/boxes/root/spacer_3.stl" download="Root_full_packing.stl">⬇ Download Full Box Packing STL (<code>Root_full_packing.stl</code>)</a></p>

Parts Overview
--------------

.. list-table::
   :header-rows: 1
   :widths: 26 24 20 18 12

   * - Box / Spacer
     - Box Type
     - Dimensions (W × L × H)
     - Packed Position
     - Compartments
   * - :ref:`BaseCardBox <box-root-basecardbox>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``79.875 × 98.5 × 39 mm``
     - ``(0, 0, 28)``
     - 1
   * - :ref:`ErieCardBox <box-root-eriecardbox>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``79.875 × 98.5 × 8.6 mm``
     - ``(79.875, 0, 28)``
     - 1
   * - :ref:`VagabondCardBox <box-root-vagabondcardbox>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``79.875 × 98.5 × 19.4 mm``
     - ``(79.875, 0, 36.6)``
     - 1
   * - :ref:`OverviewCardBox <box-root-overviewcardbox>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``79.875 × 98.5 × 11 mm``
     - ``(79.875, 0, 56)``
     - 1
   * - :ref:`ItemsBoxBottom <box-root-itemsboxbottom>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``53.25 × 103.5 × 10 mm``
     - ``(159.75, 0, 28)``
     - 1
   * - :ref:`ItemsBoxMiddle <box-root-itemsboxmiddle>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``53.25 × 103.5 × 9 mm``
     - ``(159.75, 0, 38)``
     - 1
   * - :ref:`ItemsBoxWinter <box-root-itemsboxwinter>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``53.25 × 103.5 × 9 mm``
     - ``(159.75, 0, 47)``
     - 1
   * - :ref:`ItemsBoxExtras <box-root-itemsboxextras>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``53.25 × 103.5 × 11 mm``
     - ``(159.75, 0, 56)``
     - 1
   * - :ref:`MarquisBoxBottom <box-root-marquisboxbottom>`
     - :ref:`BoxType.CAP <box-type-cap>`
     - ``106.5 × 59.833 × 24.5 mm``
     - ``(0, 98.5, 28)``
     - 1
   * - :ref:`MarquisBoxTop <box-root-marquisboxtop>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``106.5 × 59.833 × 14.5 mm``
     - ``(0, 98.5, 52.5)``
     - 1
   * - :ref:`ErieBoxBottom <box-root-erieboxbottom>`
     - :ref:`BoxType.CAP <box-type-cap>`
     - ``106.5 × 59.833 × 24.5 mm``
     - ``(0, 158.333, 28)``
     - 1
   * - :ref:`ErieBoxTop <box-root-erieboxtop>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``53.25 × 59.833 × 14.5 mm``
     - ``(0, 158.333, 52.5)``
     - 1
   * - :ref:`AllianceBoxBottom <box-root-allianceboxbottom>`
     - :ref:`BoxType.CAP <box-type-cap>`
     - ``53.25 × 59.833 × 25.5 mm``
     - ``(106.5, 98.5, 28)``
     - 1
   * - :ref:`AllianceBoxTop <box-root-allianceboxtop>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``53.25 × 59.833 × 13.5 mm``
     - ``(106.5, 98.5, 53.5)``
     - 1
   * - :ref:`LizardBoxBottom <box-root-lizardboxbottom>`
     - :ref:`BoxType.CAP <box-type-cap>`
     - ``106.5 × 59.833 × 26.5 mm``
     - ``(0, 218.166, 28)``
     - 1
   * - :ref:`LizardBoxTop <box-root-lizardboxtop>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``79.875 × 59.833 × 12.5 mm``
     - ``(0, 218.166, 54.5)``
     - 1
   * - :ref:`RiverfolkBoxBottom <box-root-riverfolkboxbottom>`
     - :ref:`BoxType.CAP <box-type-cap>`
     - ``53.25 × 59.833 × 26.5 mm``
     - ``(106.5, 218.166, 28)``
     - 1
   * - :ref:`RiverfolkBoxTop <box-root-riverfolkboxtop>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``79.875 × 59.833 × 12.5 mm``
     - ``(79.875, 218.166, 54.5)``
     - 1
   * - :ref:`VagabondBox <box-root-vagabondbox>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``53.25 × 59.833 × 16 mm``
     - ``(106.5, 158.333, 28)``
     - 1
   * - :ref:`DiceBox <box-root-dicebox>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``53.25 × 59.833 × 23 mm``
     - ``(106.5, 158.333, 44)``
     - 1
   * - :ref:`spacer_1 <spacer-root-spacer_1>`
     - :ref:`BoxType.NO_LID <box-type-no-lid>` (spacer)
     - ``210.72 × 274.72 × 28 mm``
     - ``(1.64, 1.64, 0)``
     - —
   * - :ref:`spacer_2 <spacer-root-spacer_2>`
     - :ref:`BoxType.NO_LID <box-type-no-lid>` (spacer)
     - ``50.97 × 171.22 × 39 mm``
     - ``(161.39, 105.14, 28)``
     - —
   * - :ref:`spacer_3 <spacer-root-spacer_3>`
     - :ref:`BoxType.NO_LID <box-type-no-lid>` (spacer)
     - ``49.97 × 56.553 × 14.5 mm``
     - ``(54.89, 159.973, 52.5)``
     - —

Individual Boxes & Parts
------------------------

.. _box-root-basecardbox:

BaseCardBox
^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``79.875 × 98.5 × 39 mm``
- **Packed Position**: ``(0, 0, 28)``
- **Compartments (1)**: ``Cards`` (75.875 × 94.5 mm)

**Assembled Box (BaseCardBox — Body + Lid)**

.. stl:: ../_stl/boxes/root/BaseCardBox_body.stl,../_stl/boxes/root/BaseCardBox_lid.stl
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/BaseCardBox_body.stl" data-stl-combine="../_stl/boxes/root/BaseCardBox_body.stl,../_stl/boxes/root/BaseCardBox_lid.stl" download="BaseCardBox_assembled.stl">⬇ Download Assembled BaseCardBox STL (<code>BaseCardBox_assembled.stl</code>)</a></p>

**Part: BaseCardBox Body**

.. stl:: ../_stl/boxes/root/BaseCardBox_body.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/BaseCardBox_body.stl" download="BaseCardBox_body.stl">⬇ Download BaseCardBox Body STL (<code>BaseCardBox_body.stl</code>)</a></p>

**Part: BaseCardBox Lid**

.. stl:: ../_stl/boxes/root/BaseCardBox_lid.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/BaseCardBox_lid.stl" download="BaseCardBox_lid.stl">⬇ Download BaseCardBox Lid STL (<code>BaseCardBox_lid.stl</code>)</a></p>

.. _box-root-eriecardbox:

ErieCardBox
^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``79.875 × 98.5 × 8.6 mm``
- **Packed Position**: ``(79.875, 0, 28)``
- **Stackable Mode**: ``StackableMode.PYRAMIDS``
- **Stacking Order Key**: bottom ``flat (bottom of stack)``, top ``pyramids=2``
- **Compartments (1)**: ``Cards`` (75.875 × 94.5 mm)

**Assembled Box (ErieCardBox — Body + Lid)**

.. stl:: ../_stl/boxes/root/ErieCardBox_body.stl,../_stl/boxes/root/ErieCardBox_lid.stl
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/ErieCardBox_body.stl" data-stl-combine="../_stl/boxes/root/ErieCardBox_body.stl,../_stl/boxes/root/ErieCardBox_lid.stl" download="ErieCardBox_assembled.stl">⬇ Download Assembled ErieCardBox STL (<code>ErieCardBox_assembled.stl</code>)</a></p>

**Part: ErieCardBox Body**

.. stl:: ../_stl/boxes/root/ErieCardBox_body.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ErieCardBox_body.stl" download="ErieCardBox_body.stl">⬇ Download ErieCardBox Body STL (<code>ErieCardBox_body.stl</code>)</a></p>

**Part: ErieCardBox Lid**

.. stl:: ../_stl/boxes/root/ErieCardBox_lid.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ErieCardBox_lid.stl" download="ErieCardBox_lid.stl">⬇ Download ErieCardBox Lid STL (<code>ErieCardBox_lid.stl</code>)</a></p>

.. _box-root-vagabondcardbox:

VagabondCardBox
^^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``79.875 × 98.5 × 19.4 mm``
- **Packed Position**: ``(79.875, 0, 36.6)``
- **Stackable Mode**: ``StackableMode.PYRAMIDS``
- **Stacking Order Key**: bottom ``pyramids=2``, top ``pyramids=3``
- **Compartments (1)**: ``Cards`` (75.875 × 94.5 mm)

**Assembled Box (VagabondCardBox — Body + Lid)**

.. stl:: ../_stl/boxes/root/VagabondCardBox_body.stl,../_stl/boxes/root/VagabondCardBox_lid.stl
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/VagabondCardBox_body.stl" data-stl-combine="../_stl/boxes/root/VagabondCardBox_body.stl,../_stl/boxes/root/VagabondCardBox_lid.stl" download="VagabondCardBox_assembled.stl">⬇ Download Assembled VagabondCardBox STL (<code>VagabondCardBox_assembled.stl</code>)</a></p>

**Part: VagabondCardBox Body**

.. stl:: ../_stl/boxes/root/VagabondCardBox_body.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/VagabondCardBox_body.stl" download="VagabondCardBox_body.stl">⬇ Download VagabondCardBox Body STL (<code>VagabondCardBox_body.stl</code>)</a></p>

**Part: VagabondCardBox Lid**

.. stl:: ../_stl/boxes/root/VagabondCardBox_lid.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/VagabondCardBox_lid.stl" download="VagabondCardBox_lid.stl">⬇ Download VagabondCardBox Lid STL (<code>VagabondCardBox_lid.stl</code>)</a></p>

.. _box-root-overviewcardbox:

OverviewCardBox
^^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``79.875 × 98.5 × 11 mm``
- **Packed Position**: ``(79.875, 0, 56)``
- **Stackable Mode**: ``StackableMode.PYRAMIDS``
- **Stacking Order Key**: bottom ``pyramids=3``, top ``flat (top of stack)``
- **Compartments (1)**: ``Cards`` (75.875 × 94.5 mm)

**Assembled Box (OverviewCardBox — Body + Lid)**

.. stl:: ../_stl/boxes/root/OverviewCardBox_body.stl,../_stl/boxes/root/OverviewCardBox_lid.stl
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/OverviewCardBox_body.stl" data-stl-combine="../_stl/boxes/root/OverviewCardBox_body.stl,../_stl/boxes/root/OverviewCardBox_lid.stl" download="OverviewCardBox_assembled.stl">⬇ Download Assembled OverviewCardBox STL (<code>OverviewCardBox_assembled.stl</code>)</a></p>

**Part: OverviewCardBox Body**

.. stl:: ../_stl/boxes/root/OverviewCardBox_body.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/OverviewCardBox_body.stl" download="OverviewCardBox_body.stl">⬇ Download OverviewCardBox Body STL (<code>OverviewCardBox_body.stl</code>)</a></p>

**Part: OverviewCardBox Lid**

.. stl:: ../_stl/boxes/root/OverviewCardBox_lid.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/OverviewCardBox_lid.stl" download="OverviewCardBox_lid.stl">⬇ Download OverviewCardBox Lid STL (<code>OverviewCardBox_lid.stl</code>)</a></p>

.. _box-root-itemsboxbottom:

ItemsBoxBottom
^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``53.25 × 103.5 × 10 mm``
- **Packed Position**: ``(159.75, 0, 28)``
- **Stackable Mode**: ``StackableMode.PYRAMIDS``
- **Stacking Order Key**: bottom ``flat (bottom of stack)``, top ``pyramids=2``
- **Compartments (1)**: ``Items`` (D=6 mm, 22 elements)

**Assembled Box (ItemsBoxBottom — Body + Lid)**

.. stl:: ../_stl/boxes/root/ItemsBoxBottom_body.stl,../_stl/boxes/root/ItemsBoxBottom_lid.stl
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxBottom_body.stl" data-stl-combine="../_stl/boxes/root/ItemsBoxBottom_body.stl,../_stl/boxes/root/ItemsBoxBottom_lid.stl" download="ItemsBoxBottom_assembled.stl">⬇ Download Assembled ItemsBoxBottom STL (<code>ItemsBoxBottom_assembled.stl</code>)</a></p>

**Part: ItemsBoxBottom Body**

.. stl:: ../_stl/boxes/root/ItemsBoxBottom_body.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxBottom_body.stl" download="ItemsBoxBottom_body.stl">⬇ Download ItemsBoxBottom Body STL (<code>ItemsBoxBottom_body.stl</code>)</a></p>

**Part: ItemsBoxBottom Lid**

.. stl:: ../_stl/boxes/root/ItemsBoxBottom_lid.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxBottom_lid.stl" download="ItemsBoxBottom_lid.stl">⬇ Download ItemsBoxBottom Lid STL (<code>ItemsBoxBottom_lid.stl</code>)</a></p>

.. _box-root-itemsboxmiddle:

ItemsBoxMiddle
^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``53.25 × 103.5 × 9 mm``
- **Packed Position**: ``(159.75, 0, 38)``
- **Stackable Mode**: ``StackableMode.PYRAMIDS``
- **Stacking Order Key**: bottom ``pyramids=2``, top ``pyramids=3``
- **Compartments (1)**: ``Items`` (D=5 mm, 20 elements)

**Assembled Box (ItemsBoxMiddle — Body + Lid)**

.. stl:: ../_stl/boxes/root/ItemsBoxMiddle_body.stl,../_stl/boxes/root/ItemsBoxMiddle_lid.stl
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxMiddle_body.stl" data-stl-combine="../_stl/boxes/root/ItemsBoxMiddle_body.stl,../_stl/boxes/root/ItemsBoxMiddle_lid.stl" download="ItemsBoxMiddle_assembled.stl">⬇ Download Assembled ItemsBoxMiddle STL (<code>ItemsBoxMiddle_assembled.stl</code>)</a></p>

**Part: ItemsBoxMiddle Body**

.. stl:: ../_stl/boxes/root/ItemsBoxMiddle_body.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxMiddle_body.stl" download="ItemsBoxMiddle_body.stl">⬇ Download ItemsBoxMiddle Body STL (<code>ItemsBoxMiddle_body.stl</code>)</a></p>

**Part: ItemsBoxMiddle Lid**

.. stl:: ../_stl/boxes/root/ItemsBoxMiddle_lid.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxMiddle_lid.stl" download="ItemsBoxMiddle_lid.stl">⬇ Download ItemsBoxMiddle Lid STL (<code>ItemsBoxMiddle_lid.stl</code>)</a></p>

.. _box-root-itemsboxwinter:

ItemsBoxWinter
^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``53.25 × 103.5 × 9 mm``
- **Packed Position**: ``(159.75, 0, 47)``
- **Stackable Mode**: ``StackableMode.PYRAMIDS``
- **Stacking Order Key**: bottom ``pyramids=3``, top ``pyramids=(2, 3, 3, 2)``
- **Compartments (1)**: ``WinterTokens`` (D=5 mm, 12 elements)

**Assembled Box (ItemsBoxWinter — Body + Lid)**

.. stl:: ../_stl/boxes/root/ItemsBoxWinter_body.stl,../_stl/boxes/root/ItemsBoxWinter_lid.stl
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxWinter_body.stl" data-stl-combine="../_stl/boxes/root/ItemsBoxWinter_body.stl,../_stl/boxes/root/ItemsBoxWinter_lid.stl" download="ItemsBoxWinter_assembled.stl">⬇ Download Assembled ItemsBoxWinter STL (<code>ItemsBoxWinter_assembled.stl</code>)</a></p>

**Part: ItemsBoxWinter Body**

.. stl:: ../_stl/boxes/root/ItemsBoxWinter_body.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxWinter_body.stl" download="ItemsBoxWinter_body.stl">⬇ Download ItemsBoxWinter Body STL (<code>ItemsBoxWinter_body.stl</code>)</a></p>

**Part: ItemsBoxWinter Lid**

.. stl:: ../_stl/boxes/root/ItemsBoxWinter_lid.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxWinter_lid.stl" download="ItemsBoxWinter_lid.stl">⬇ Download ItemsBoxWinter Lid STL (<code>ItemsBoxWinter_lid.stl</code>)</a></p>

.. _box-root-itemsboxextras:

ItemsBoxExtras
^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``53.25 × 103.5 × 11 mm``
- **Packed Position**: ``(159.75, 0, 56)``
- **Stackable Mode**: ``StackableMode.PYRAMIDS``
- **Stacking Order Key**: bottom ``pyramids=(2, 3, 3, 2)``, top ``flat (top of stack)``
- **Compartments (1)**: ``Extras`` (D=7 mm, 16 elements)

**Assembled Box (ItemsBoxExtras — Body + Lid)**

.. stl:: ../_stl/boxes/root/ItemsBoxExtras_body.stl,../_stl/boxes/root/ItemsBoxExtras_lid.stl
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxExtras_body.stl" data-stl-combine="../_stl/boxes/root/ItemsBoxExtras_body.stl,../_stl/boxes/root/ItemsBoxExtras_lid.stl" download="ItemsBoxExtras_assembled.stl">⬇ Download Assembled ItemsBoxExtras STL (<code>ItemsBoxExtras_assembled.stl</code>)</a></p>

**Part: ItemsBoxExtras Body**

.. stl:: ../_stl/boxes/root/ItemsBoxExtras_body.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxExtras_body.stl" download="ItemsBoxExtras_body.stl">⬇ Download ItemsBoxExtras Body STL (<code>ItemsBoxExtras_body.stl</code>)</a></p>

**Part: ItemsBoxExtras Lid**

.. stl:: ../_stl/boxes/root/ItemsBoxExtras_lid.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxExtras_lid.stl" download="ItemsBoxExtras_lid.stl">⬇ Download ItemsBoxExtras Lid STL (<code>ItemsBoxExtras_lid.stl</code>)</a></p>

.. _box-root-marquisboxbottom:

MarquisBoxBottom
^^^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.CAP <box-type-cap>`
- **Outer Dimensions**: ``106.5 × 59.833 × 24.5 mm``
- **Packed Position**: ``(0, 98.5, 28)``
- **Compartments (1)**: ``Warriors`` (6 elements)

**Assembled Box (MarquisBoxBottom — Body + Lid)**

.. stl:: ../_stl/boxes/root/MarquisBoxBottom_body.stl,../_stl/boxes/root/MarquisBoxBottom_lid.stl
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/MarquisBoxBottom_body.stl" data-stl-combine="../_stl/boxes/root/MarquisBoxBottom_body.stl,../_stl/boxes/root/MarquisBoxBottom_lid.stl" download="MarquisBoxBottom_assembled.stl">⬇ Download Assembled MarquisBoxBottom STL (<code>MarquisBoxBottom_assembled.stl</code>)</a></p>

**Part: MarquisBoxBottom Body**

.. stl:: ../_stl/boxes/root/MarquisBoxBottom_body.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/MarquisBoxBottom_body.stl" download="MarquisBoxBottom_body.stl">⬇ Download MarquisBoxBottom Body STL (<code>MarquisBoxBottom_body.stl</code>)</a></p>

**Part: MarquisBoxBottom Lid**

.. stl:: ../_stl/boxes/root/MarquisBoxBottom_lid.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/MarquisBoxBottom_lid.stl" download="MarquisBoxBottom_lid.stl">⬇ Download MarquisBoxBottom Lid STL (<code>MarquisBoxBottom_lid.stl</code>)</a></p>

.. _box-root-marquisboxtop:

MarquisBoxTop
^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``106.5 × 59.833 × 14.5 mm``
- **Packed Position**: ``(0, 98.5, 52.5)``
- **Compartments (1)**: ``WoodAndBuildings`` (20 elements)

**Assembled Box (MarquisBoxTop — Body + Lid)**

.. stl:: ../_stl/boxes/root/MarquisBoxTop_body.stl,../_stl/boxes/root/MarquisBoxTop_lid.stl
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/MarquisBoxTop_body.stl" data-stl-combine="../_stl/boxes/root/MarquisBoxTop_body.stl,../_stl/boxes/root/MarquisBoxTop_lid.stl" download="MarquisBoxTop_assembled.stl">⬇ Download Assembled MarquisBoxTop STL (<code>MarquisBoxTop_assembled.stl</code>)</a></p>

**Part: MarquisBoxTop Body**

.. stl:: ../_stl/boxes/root/MarquisBoxTop_body.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/MarquisBoxTop_body.stl" download="MarquisBoxTop_body.stl">⬇ Download MarquisBoxTop Body STL (<code>MarquisBoxTop_body.stl</code>)</a></p>

**Part: MarquisBoxTop Lid**

.. stl:: ../_stl/boxes/root/MarquisBoxTop_lid.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/MarquisBoxTop_lid.stl" download="MarquisBoxTop_lid.stl">⬇ Download MarquisBoxTop Lid STL (<code>MarquisBoxTop_lid.stl</code>)</a></p>

.. _box-root-erieboxbottom:

ErieBoxBottom
^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.CAP <box-type-cap>`
- **Outer Dimensions**: ``106.5 × 59.833 × 24.5 mm``
- **Packed Position**: ``(0, 158.333, 28)``
- **Compartments (1)**: ``Warriors`` (4 elements)

**Assembled Box (ErieBoxBottom — Body + Lid)**

.. stl:: ../_stl/boxes/root/ErieBoxBottom_body.stl,../_stl/boxes/root/ErieBoxBottom_lid.stl
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/ErieBoxBottom_body.stl" data-stl-combine="../_stl/boxes/root/ErieBoxBottom_body.stl,../_stl/boxes/root/ErieBoxBottom_lid.stl" download="ErieBoxBottom_assembled.stl">⬇ Download Assembled ErieBoxBottom STL (<code>ErieBoxBottom_assembled.stl</code>)</a></p>

**Part: ErieBoxBottom Body**

.. stl:: ../_stl/boxes/root/ErieBoxBottom_body.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ErieBoxBottom_body.stl" download="ErieBoxBottom_body.stl">⬇ Download ErieBoxBottom Body STL (<code>ErieBoxBottom_body.stl</code>)</a></p>

**Part: ErieBoxBottom Lid**

.. stl:: ../_stl/boxes/root/ErieBoxBottom_lid.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ErieBoxBottom_lid.stl" download="ErieBoxBottom_lid.stl">⬇ Download ErieBoxBottom Lid STL (<code>ErieBoxBottom_lid.stl</code>)</a></p>

.. _box-root-erieboxtop:

ErieBoxTop
^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``53.25 × 59.833 × 14.5 mm``
- **Packed Position**: ``(0, 158.333, 52.5)``
- **Compartments (1)**: ``Roosts`` (6 elements)

**Assembled Box (ErieBoxTop — Body + Lid)**

.. stl:: ../_stl/boxes/root/ErieBoxTop_body.stl,../_stl/boxes/root/ErieBoxTop_lid.stl
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/ErieBoxTop_body.stl" data-stl-combine="../_stl/boxes/root/ErieBoxTop_body.stl,../_stl/boxes/root/ErieBoxTop_lid.stl" download="ErieBoxTop_assembled.stl">⬇ Download Assembled ErieBoxTop STL (<code>ErieBoxTop_assembled.stl</code>)</a></p>

**Part: ErieBoxTop Body**

.. stl:: ../_stl/boxes/root/ErieBoxTop_body.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ErieBoxTop_body.stl" download="ErieBoxTop_body.stl">⬇ Download ErieBoxTop Body STL (<code>ErieBoxTop_body.stl</code>)</a></p>

**Part: ErieBoxTop Lid**

.. stl:: ../_stl/boxes/root/ErieBoxTop_lid.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ErieBoxTop_lid.stl" download="ErieBoxTop_lid.stl">⬇ Download ErieBoxTop Lid STL (<code>ErieBoxTop_lid.stl</code>)</a></p>

.. _box-root-allianceboxbottom:

AllianceBoxBottom
^^^^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.CAP <box-type-cap>`
- **Outer Dimensions**: ``53.25 × 59.833 × 25.5 mm``
- **Packed Position**: ``(106.5, 98.5, 28)``
- **Compartments (1)**: ``Warriors`` (4 elements)

**Assembled Box (AllianceBoxBottom — Body + Lid)**

.. stl:: ../_stl/boxes/root/AllianceBoxBottom_body.stl,../_stl/boxes/root/AllianceBoxBottom_lid.stl
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/AllianceBoxBottom_body.stl" data-stl-combine="../_stl/boxes/root/AllianceBoxBottom_body.stl,../_stl/boxes/root/AllianceBoxBottom_lid.stl" download="AllianceBoxBottom_assembled.stl">⬇ Download Assembled AllianceBoxBottom STL (<code>AllianceBoxBottom_assembled.stl</code>)</a></p>

**Part: AllianceBoxBottom Body**

.. stl:: ../_stl/boxes/root/AllianceBoxBottom_body.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/AllianceBoxBottom_body.stl" download="AllianceBoxBottom_body.stl">⬇ Download AllianceBoxBottom Body STL (<code>AllianceBoxBottom_body.stl</code>)</a></p>

**Part: AllianceBoxBottom Lid**

.. stl:: ../_stl/boxes/root/AllianceBoxBottom_lid.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/AllianceBoxBottom_lid.stl" download="AllianceBoxBottom_lid.stl">⬇ Download AllianceBoxBottom Lid STL (<code>AllianceBoxBottom_lid.stl</code>)</a></p>

.. _box-root-allianceboxtop:

AllianceBoxTop
^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``53.25 × 59.833 × 13.5 mm``
- **Packed Position**: ``(106.5, 98.5, 53.5)``
- **Compartments (1)**: ``BasesAndSympathy`` (6 elements)

**Assembled Box (AllianceBoxTop — Body + Lid)**

.. stl:: ../_stl/boxes/root/AllianceBoxTop_body.stl,../_stl/boxes/root/AllianceBoxTop_lid.stl
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/AllianceBoxTop_body.stl" data-stl-combine="../_stl/boxes/root/AllianceBoxTop_body.stl,../_stl/boxes/root/AllianceBoxTop_lid.stl" download="AllianceBoxTop_assembled.stl">⬇ Download Assembled AllianceBoxTop STL (<code>AllianceBoxTop_assembled.stl</code>)</a></p>

**Part: AllianceBoxTop Body**

.. stl:: ../_stl/boxes/root/AllianceBoxTop_body.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/AllianceBoxTop_body.stl" download="AllianceBoxTop_body.stl">⬇ Download AllianceBoxTop Body STL (<code>AllianceBoxTop_body.stl</code>)</a></p>

**Part: AllianceBoxTop Lid**

.. stl:: ../_stl/boxes/root/AllianceBoxTop_lid.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/AllianceBoxTop_lid.stl" download="AllianceBoxTop_lid.stl">⬇ Download AllianceBoxTop Lid STL (<code>AllianceBoxTop_lid.stl</code>)</a></p>

.. _box-root-lizardboxbottom:

LizardBoxBottom
^^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.CAP <box-type-cap>`
- **Outer Dimensions**: ``106.5 × 59.833 × 26.5 mm``
- **Packed Position**: ``(0, 218.166, 28)``
- **Compartments (1)**: ``Warriors`` (25 elements)

**Assembled Box (LizardBoxBottom — Body + Lid)**

.. stl:: ../_stl/boxes/root/LizardBoxBottom_body.stl,../_stl/boxes/root/LizardBoxBottom_lid.stl
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/LizardBoxBottom_body.stl" data-stl-combine="../_stl/boxes/root/LizardBoxBottom_body.stl,../_stl/boxes/root/LizardBoxBottom_lid.stl" download="LizardBoxBottom_assembled.stl">⬇ Download Assembled LizardBoxBottom STL (<code>LizardBoxBottom_assembled.stl</code>)</a></p>

**Part: LizardBoxBottom Body**

.. stl:: ../_stl/boxes/root/LizardBoxBottom_body.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/LizardBoxBottom_body.stl" download="LizardBoxBottom_body.stl">⬇ Download LizardBoxBottom Body STL (<code>LizardBoxBottom_body.stl</code>)</a></p>

**Part: LizardBoxBottom Lid**

.. stl:: ../_stl/boxes/root/LizardBoxBottom_lid.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/LizardBoxBottom_lid.stl" download="LizardBoxBottom_lid.stl">⬇ Download LizardBoxBottom Lid STL (<code>LizardBoxBottom_lid.stl</code>)</a></p>

.. _box-root-lizardboxtop:

LizardBoxTop
^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``79.875 × 59.833 × 12.5 mm``
- **Packed Position**: ``(0, 218.166, 54.5)``
- **Compartments (1)**: ``Gardens`` (12 elements)

**Assembled Box (LizardBoxTop — Body + Lid)**

.. stl:: ../_stl/boxes/root/LizardBoxTop_body.stl,../_stl/boxes/root/LizardBoxTop_lid.stl
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/LizardBoxTop_body.stl" data-stl-combine="../_stl/boxes/root/LizardBoxTop_body.stl,../_stl/boxes/root/LizardBoxTop_lid.stl" download="LizardBoxTop_assembled.stl">⬇ Download Assembled LizardBoxTop STL (<code>LizardBoxTop_assembled.stl</code>)</a></p>

**Part: LizardBoxTop Body**

.. stl:: ../_stl/boxes/root/LizardBoxTop_body.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/LizardBoxTop_body.stl" download="LizardBoxTop_body.stl">⬇ Download LizardBoxTop Body STL (<code>LizardBoxTop_body.stl</code>)</a></p>

**Part: LizardBoxTop Lid**

.. stl:: ../_stl/boxes/root/LizardBoxTop_lid.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/LizardBoxTop_lid.stl" download="LizardBoxTop_lid.stl">⬇ Download LizardBoxTop Lid STL (<code>LizardBoxTop_lid.stl</code>)</a></p>

.. _box-root-riverfolkboxbottom:

RiverfolkBoxBottom
^^^^^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.CAP <box-type-cap>`
- **Outer Dimensions**: ``53.25 × 59.833 × 26.5 mm``
- **Packed Position**: ``(106.5, 218.166, 28)``
- **Compartments (1)**: ``Warriors`` (6 elements)

**Assembled Box (RiverfolkBoxBottom — Body + Lid)**

.. stl:: ../_stl/boxes/root/RiverfolkBoxBottom_body.stl,../_stl/boxes/root/RiverfolkBoxBottom_lid.stl
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/RiverfolkBoxBottom_body.stl" data-stl-combine="../_stl/boxes/root/RiverfolkBoxBottom_body.stl,../_stl/boxes/root/RiverfolkBoxBottom_lid.stl" download="RiverfolkBoxBottom_assembled.stl">⬇ Download Assembled RiverfolkBoxBottom STL (<code>RiverfolkBoxBottom_assembled.stl</code>)</a></p>

**Part: RiverfolkBoxBottom Body**

.. stl:: ../_stl/boxes/root/RiverfolkBoxBottom_body.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/RiverfolkBoxBottom_body.stl" download="RiverfolkBoxBottom_body.stl">⬇ Download RiverfolkBoxBottom Body STL (<code>RiverfolkBoxBottom_body.stl</code>)</a></p>

**Part: RiverfolkBoxBottom Lid**

.. stl:: ../_stl/boxes/root/RiverfolkBoxBottom_lid.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/RiverfolkBoxBottom_lid.stl" download="RiverfolkBoxBottom_lid.stl">⬇ Download RiverfolkBoxBottom Lid STL (<code>RiverfolkBoxBottom_lid.stl</code>)</a></p>

.. _box-root-riverfolkboxtop:

RiverfolkBoxTop
^^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``79.875 × 59.833 × 12.5 mm``
- **Packed Position**: ``(79.875, 218.166, 54.5)``
- **Compartments (1)**: ``TradePosts`` (12 elements)

**Assembled Box (RiverfolkBoxTop — Body + Lid)**

.. stl:: ../_stl/boxes/root/RiverfolkBoxTop_body.stl,../_stl/boxes/root/RiverfolkBoxTop_lid.stl
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/RiverfolkBoxTop_body.stl" data-stl-combine="../_stl/boxes/root/RiverfolkBoxTop_body.stl,../_stl/boxes/root/RiverfolkBoxTop_lid.stl" download="RiverfolkBoxTop_assembled.stl">⬇ Download Assembled RiverfolkBoxTop STL (<code>RiverfolkBoxTop_assembled.stl</code>)</a></p>

**Part: RiverfolkBoxTop Body**

.. stl:: ../_stl/boxes/root/RiverfolkBoxTop_body.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/RiverfolkBoxTop_body.stl" download="RiverfolkBoxTop_body.stl">⬇ Download RiverfolkBoxTop Body STL (<code>RiverfolkBoxTop_body.stl</code>)</a></p>

**Part: RiverfolkBoxTop Lid**

.. stl:: ../_stl/boxes/root/RiverfolkBoxTop_lid.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/RiverfolkBoxTop_lid.stl" download="RiverfolkBoxTop_lid.stl">⬇ Download RiverfolkBoxTop Lid STL (<code>RiverfolkBoxTop_lid.stl</code>)</a></p>

.. _box-root-vagabondbox:

VagabondBox
^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``53.25 × 59.833 × 16 mm``
- **Packed Position**: ``(106.5, 158.333, 28)``
- **Stackable Mode**: ``StackableMode.PYRAMIDS``
- **Stacking Order Key**: bottom ``flat (bottom of stack)``, top ``pyramids=2``
- **Compartments (1)**: ``ItemsAndScore`` (3 elements)

**Assembled Box (VagabondBox — Body + Lid)**

.. stl:: ../_stl/boxes/root/VagabondBox_body.stl,../_stl/boxes/root/VagabondBox_lid.stl
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/VagabondBox_body.stl" data-stl-combine="../_stl/boxes/root/VagabondBox_body.stl,../_stl/boxes/root/VagabondBox_lid.stl" download="VagabondBox_assembled.stl">⬇ Download Assembled VagabondBox STL (<code>VagabondBox_assembled.stl</code>)</a></p>

**Part: VagabondBox Body**

.. stl:: ../_stl/boxes/root/VagabondBox_body.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/VagabondBox_body.stl" download="VagabondBox_body.stl">⬇ Download VagabondBox Body STL (<code>VagabondBox_body.stl</code>)</a></p>

**Part: VagabondBox Lid**

.. stl:: ../_stl/boxes/root/VagabondBox_lid.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/VagabondBox_lid.stl" download="VagabondBox_lid.stl">⬇ Download VagabondBox Lid STL (<code>VagabondBox_lid.stl</code>)</a></p>

.. _box-root-dicebox:

DiceBox
^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``53.25 × 59.833 × 23 mm``
- **Packed Position**: ``(106.5, 158.333, 44)``
- **Stackable Mode**: ``StackableMode.PYRAMIDS``
- **Stacking Order Key**: bottom ``pyramids=2``, top ``flat (top of stack)``
- **Compartments (1)**: ``Dice`` (2 elements)

**Assembled Box (DiceBox — Body + Lid)**

.. stl:: ../_stl/boxes/root/DiceBox_body.stl,../_stl/boxes/root/DiceBox_lid.stl
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/DiceBox_body.stl" data-stl-combine="../_stl/boxes/root/DiceBox_body.stl,../_stl/boxes/root/DiceBox_lid.stl" download="DiceBox_assembled.stl">⬇ Download Assembled DiceBox STL (<code>DiceBox_assembled.stl</code>)</a></p>

**Part: DiceBox Body**

.. stl:: ../_stl/boxes/root/DiceBox_body.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/DiceBox_body.stl" download="DiceBox_body.stl">⬇ Download DiceBox Body STL (<code>DiceBox_body.stl</code>)</a></p>

**Part: DiceBox Lid**

.. stl:: ../_stl/boxes/root/DiceBox_lid.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/DiceBox_lid.stl" download="DiceBox_lid.stl">⬇ Download DiceBox Lid STL (<code>DiceBox_lid.stl</code>)</a></p>

Spacer Trays
------------

.. _spacer-root-spacer_1:

spacer_1
^^^^^^^^

- **Type**: :ref:`BoxType.NO_LID <box-type-no-lid>` filler spacer tray
- **Outer Dimensions**: ``210.72 × 274.72 × 28 mm``
- **Packed Position**: ``(1.64, 1.64, 0)``

.. stl:: ../_stl/boxes/root/spacer_1.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/spacer_1.stl" download="spacer_1.stl">⬇ Download spacer_1 STL (<code>spacer_1.stl</code>)</a></p>

.. _spacer-root-spacer_2:

spacer_2
^^^^^^^^

- **Type**: :ref:`BoxType.NO_LID <box-type-no-lid>` filler spacer tray
- **Outer Dimensions**: ``50.97 × 171.22 × 39 mm``
- **Packed Position**: ``(161.39, 105.14, 28)``

.. stl:: ../_stl/boxes/root/spacer_2.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/spacer_2.stl" download="spacer_2.stl">⬇ Download spacer_2 STL (<code>spacer_2.stl</code>)</a></p>

.. _spacer-root-spacer_3:

spacer_3
^^^^^^^^

- **Type**: :ref:`BoxType.NO_LID <box-type-no-lid>` filler spacer tray
- **Outer Dimensions**: ``49.97 × 56.553 × 14.5 mm``
- **Packed Position**: ``(54.89, 159.973, 52.5)``

.. stl:: ../_stl/boxes/root/spacer_3.stl
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/spacer_3.stl" download="spacer_3.stl">⬇ Download spacer_3 STL (<code>spacer_3.stl</code>)</a></p>
