.. _box-insert-root:

Root (root)
===========

Root board game insert — pyboxbuilder port of `examples/root.scad`.

- **Source Script**: ``boxes/root/root.py``
- **Game Box Dimensions**: ``214 × 278 × 67 mm`` (usable height ``39 mm`` with ``28 mm`` board storage)
- **Boxes**: 21 sub-box(es), 6 spacer tray(s)
- **Box Types Used**: :ref:`BoxType.SLIDING <box-type-sliding>`, :ref:`BoxType.CAP <box-type-cap>`, :ref:`BoxType.NO_LID <box-type-no-lid>`

Box & Expansion Selector
------------------------

Select the Root expansions or individual factions you own to see a live breakdown 
by box type, inspect the matching layout in 3-D, and download ready-to-print ZIP archives:

.. raw:: html

   <div class="box-selector" data-box-selector>
     <script type="application/json" data-box-selector-config>{"projectName":"Root","defaultPreset":"base_riverfolk","boardStorage":{"capacityMm":28.0,"totalBoxHeightMm":67.0,"thinTopSpaceHint":"Base Game boards (~22 mm) leave a thin ~6 mm space at the top where Riverfolk's 2 faction boards and rules would go. Place a thin ~6 mm foam/cardboard pad on top of the trays to keep lids snug, or leave open to fit Riverfolk boards later.","exactFitHint":"Base + Riverfolk boards (~28 mm) fill the 28 mm bottom bay flush beneath the 39 mm insert trays.","externalBoxHint":"Expansions beyond Riverfolk exceed the 28 mm board bay in this box: move all game/map and faction boards into a separate dedicated board box, freeing the full 67 mm height of the Base box for expansion insert trays."},"presets":[{"key":"base_only","name":"Base Game Only (No Expansions)","description":"16 core boxes (4 base factions, cards, items, dice) + Base-only spacer trays","subgroups":["shared_cards","items","dice","marquise","eyrie","alliance","vagabond1"],"spacerPresetKey":"base"},{"key":"base_riverfolk","name":"Base + Riverfolk Expansion (Current Layout)","description":"All 21 boxes including Lizard Cult, Riverfolk Company & 2nd Vagabond + Full spacers","subgroups":["shared_cards","items","dice","marquise","eyrie","alliance","vagabond1","lizard_cult","riverfolk_company","vagabond2"],"spacerPresetKey":"base+riverfolk"}],"expansions":[{"key":"base","name":"Base Game","status":"available","required":true,"description":"Core 4 factions (Marquise de Cat, Eyrie Dynasties, Woodland Alliance, Vagabond), shared & overview decks, starting/craftable items, Winter clearing markers, and dice.","subgroups":["shared_cards","items","dice","marquise","eyrie","alliance","vagabond1"],"boardThicknessMm":22.0,"boardsSummary":"Main folded map board, 4 Base faction boards, and Base rulebooks (~22 mm)","notes":""},{"key":"riverfolk","name":"The Riverfolk Expansion","status":"available","required":false,"description":"Adds Lizard Cult, Riverfolk Company, and a 2nd Vagabond tray (extra Vagabond quest/character cards and items already fit in the Base trays).","subgroups":["lizard_cult","riverfolk_company","vagabond2"],"boardThicknessMm":6.0,"boardsSummary":"Lizard Cult & Riverfolk faction boards + expansion rulebook (~6 mm)","notes":""},{"key":"underworld","name":"The Underworld Expansion","status":"planned","required":false,"description":"Underground Duchy & Corvid Conspiracy factions, landmarks, and extra maps.","subgroups":["underground_duchy","corvid_conspiracy"],"boardThicknessMm":11.0,"boardsSummary":"Extra Underground/Lake map board + Duchy & Corvid boards (~11 mm)","notes":"Beyond single-box board capacity: requires moving all boards out to a separate box. Warrior SVGs (duchy_warrior.svg, corvid_warrior.svg) exist in boxes/root/svg/."},{"key":"marauder","name":"The Marauder Expansion","status":"planned","required":false,"description":"Lord of the Hundreds & Keepers in Iron factions, advance setup, and hirelings.","subgroups":["lord_of_the_hundreds","keepers_in_iron"],"boardThicknessMm":7.0,"boardsSummary":"Hundreds & Keepers faction boards + setup/rule sheets (~7 mm)","notes":"Beyond single-box board capacity: requires moving all boards out to a separate box. Warrior SVGs (hundreds_warrior.svg, keepers_warrior.svg) exist in boxes/root/svg/."},{"key":"exiles_and_partisans","name":"Exiles & Partisans Deck","status":"planned","required":false,"description":"Alternative 54-card shared deck storage.","subgroups":[],"boardThicknessMm":0.0,"boardsSummary":"Cards only (no extra boards)","notes":""},{"key":"hirelings_landmarks","name":"Hirelings & Landmarks","status":"planned","required":false,"description":"Modular trays for Hirelings and Landmarks packs.","subgroups":[],"boardThicknessMm":2.0,"boardsSummary":"Hirelings & Landmarks rule/reference sheets (~2 mm)","notes":""}],"subgroups":[{"key":"shared_cards","name":"Shared & Overview Cards","expansion":"base","description":"54-card main deck & overview/reference cards"},{"key":"items","name":"Items, Winter & Extra Tokens","expansion":"base","description":"Vagabond item stacks, ruin loot, Winter clearing markers, and spare token slots"},{"key":"dice","name":"Combat Dice","expansion":"base","description":"2 Root combat dice"},{"key":"marquise","name":"Marquise de Cat","expansion":"base","description":"25 warriors, wood, keep, and buildings"},{"key":"eyrie","name":"Eyrie Dynasties","expansion":"base","description":"20 warriors, 7 roosts, leader & vizier cards"},{"key":"alliance","name":"Woodland Alliance","expansion":"base","description":"10 warriors, 3 bases, 10 sympathy tokens"},{"key":"vagabond1","name":"Vagabond #1 & Quests","expansion":"base","description":"1st Vagabond meeple, items, score, relations & quest/character cards"},{"key":"lizard_cult","name":"Lizard Cult","expansion":"riverfolk","description":"25 warriors, 15 gardens, outcast & score markers"},{"key":"riverfolk_company","name":"Riverfolk Company","expansion":"riverfolk","description":"15 warriors, 9 trade posts, 3 glass gems, score & faction markers"},{"key":"vagabond2","name":"2nd Vagabond","expansion":"riverfolk","description":"2nd Vagabond meeple, score marker & 6 relationship markers"}],"categories":[{"key":"cards","name":"Card Boxes","description":"Sleeved card storage boxes"},{"key":"factions","name":"Faction Boxes","description":"Faction warrior, building & token trays"},{"key":"items_and_dice","name":"Items & Dice Boxes","description":"Shared Vagabond items, clearing markers & dice"},{"key":"spacers","name":"Spacer Trays","description":"Filler trays for unoccupied box space"}],"boxes":[{"label":"BaseCardBox","anchor":"box-root-basecardbox","expansion":"base","subgroup":"shared_cards","category":"cards","categoryName":"Card Boxes","boxType":"SLIDING","boxTypeLabel":"Sliding Lid","dimensions":"79.875 \u00d7 98.5 \u00d7 39 mm","position":"(79.875, 0, 28)","compartments":1,"description":"Shared 54-card main deck","files":[{"uri":"../_stl/boxes/root/BaseCardBox_body.stl?v=280f57b0","filename":"BaseCardBox_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/BaseCardBox_lid.stl?v=f7a52ec0","filename":"BaseCardBox_lid.stl","kind":"lid"}]},{"label":"ErieCardBox","anchor":"box-root-eriecardbox","expansion":"base","subgroup":"eyrie","category":"cards","categoryName":"Card Boxes","boxType":"SLIDING","boxTypeLabel":"Sliding Lid","dimensions":"79.875 \u00d7 98.5 \u00d7 8.6 mm","position":"(0, 0, 28)","compartments":1,"description":"Eyrie leader & vizier cards","files":[{"uri":"../_stl/boxes/root/ErieCardBox_body.stl?v=4ef254db","filename":"ErieCardBox_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/ErieCardBox_lid.stl?v=8fd10207","filename":"ErieCardBox_lid.stl","kind":"lid"}]},{"label":"VagabondCardBox","anchor":"box-root-vagabondcardbox","expansion":"base","subgroup":"vagabond1","category":"cards","categoryName":"Card Boxes","boxType":"SLIDING","boxTypeLabel":"Sliding Lid","dimensions":"79.875 \u00d7 98.5 \u00d7 19.4 mm","position":"(0, 0, 36.6)","compartments":1,"description":"Vagabond quest & character cards","files":[{"uri":"../_stl/boxes/root/VagabondCardBox_body.stl?v=6fe66e01","filename":"VagabondCardBox_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/VagabondCardBox_lid.stl?v=1e30bd13","filename":"VagabondCardBox_lid.stl","kind":"lid"}]},{"label":"OverviewCardBox","anchor":"box-root-overviewcardbox","expansion":"base","subgroup":"shared_cards","category":"cards","categoryName":"Card Boxes","boxType":"SLIDING","boxTypeLabel":"Sliding Lid","dimensions":"79.875 \u00d7 98.5 \u00d7 11 mm","position":"(0, 0, 56)","compartments":1,"description":"Faction overview cards","files":[{"uri":"../_stl/boxes/root/OverviewCardBox_body.stl?v=40e07195","filename":"OverviewCardBox_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/OverviewCardBox_lid.stl?v=08075eb5","filename":"OverviewCardBox_lid.stl","kind":"lid"}]},{"label":"ItemsBoxBottom","anchor":"box-root-itemsboxbottom","expansion":"base","subgroup":"items","category":"items_and_dice","categoryName":"Items & Dice Boxes","boxType":"SLIDING","boxTypeLabel":"Sliding Lid","dimensions":"53.25 \u00d7 103.5 \u00d7 10 mm","position":"(0, 158.333, 28)","compartments":1,"description":"Starting Vagabond items & ruins","files":[{"uri":"../_stl/boxes/root/ItemsBoxBottom_body.stl?v=e62368bb","filename":"ItemsBoxBottom_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/ItemsBoxBottom_lid.stl?v=fb9d850b","filename":"ItemsBoxBottom_lid.stl","kind":"lid"}]},{"label":"ItemsBoxMiddle","anchor":"box-root-itemsboxmiddle","expansion":"base","subgroup":"items","category":"items_and_dice","categoryName":"Items & Dice Boxes","boxType":"SLIDING","boxTypeLabel":"Sliding Lid","dimensions":"53.25 \u00d7 103.5 \u00d7 9 mm","position":"(0, 158.333, 38)","compartments":1,"description":"Craftable items & extra ruin slots","files":[{"uri":"../_stl/boxes/root/ItemsBoxMiddle_body.stl?v=a03ba0bb","filename":"ItemsBoxMiddle_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/ItemsBoxMiddle_lid.stl?v=19dcdaa4","filename":"ItemsBoxMiddle_lid.stl","kind":"lid"}]},{"label":"ItemsBoxWinter","anchor":"box-root-itemsboxwinter","expansion":"base","subgroup":"items","category":"items_and_dice","categoryName":"Items & Dice Boxes","boxType":"SLIDING","boxTypeLabel":"Sliding Lid","dimensions":"53.25 \u00d7 103.5 \u00d7 9 mm","position":"(0, 158.333, 47)","compartments":1,"description":"Winter Map clearing markers","files":[{"uri":"../_stl/boxes/root/ItemsBoxWinter_body.stl?v=eb23ba37","filename":"ItemsBoxWinter_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/ItemsBoxWinter_lid.stl?v=00995441","filename":"ItemsBoxWinter_lid.stl","kind":"lid"}]},{"label":"ItemsBoxExtras","anchor":"box-root-itemsboxextras","expansion":"base","subgroup":"items","category":"items_and_dice","categoryName":"Items & Dice Boxes","boxType":"SLIDING","boxTypeLabel":"Sliding Lid","dimensions":"53.25 \u00d7 103.5 \u00d7 11 mm","position":"(0, 158.333, 56)","compartments":1,"description":"8 generic scenario/extra token pockets","files":[{"uri":"../_stl/boxes/root/ItemsBoxExtras_body.stl?v=9deb1f10","filename":"ItemsBoxExtras_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/ItemsBoxExtras_lid.stl?v=f025454e","filename":"ItemsBoxExtras_lid.stl","kind":"lid"}]},{"label":"MarquisBoxBottom","anchor":"box-root-marquisboxbottom","expansion":"base","subgroup":"marquise","category":"factions","categoryName":"Faction Boxes","boxType":"CAP","boxTypeLabel":"Cap Lid","dimensions":"106.5 \u00d7 59.833 \u00d7 24.5 mm","position":"(0, 98.5, 28)","compartments":1,"description":"Marquise warriors (25 meeples)","files":[{"uri":"../_stl/boxes/root/MarquisBoxBottom_body.stl?v=f5ea0af3","filename":"MarquisBoxBottom_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/MarquisBoxBottom_lid.stl?v=eb8a03ce","filename":"MarquisBoxBottom_lid.stl","kind":"lid"}]},{"label":"MarquisBoxTop","anchor":"box-root-marquisboxtop","expansion":"base","subgroup":"marquise","category":"factions","categoryName":"Faction Boxes","boxType":"SLIDING","boxTypeLabel":"Sliding Lid","dimensions":"106.5 \u00d7 59.833 \u00d7 14.5 mm","position":"(0, 98.5, 52.5)","compartments":1,"description":"Marquise wood, keep, buildings & score","files":[{"uri":"../_stl/boxes/root/MarquisBoxTop_body.stl?v=be7708f9","filename":"MarquisBoxTop_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/MarquisBoxTop_lid.stl?v=0f1520ae","filename":"MarquisBoxTop_lid.stl","kind":"lid"}]},{"label":"ErieBoxBottom","anchor":"box-root-erieboxbottom","expansion":"base","subgroup":"eyrie","category":"factions","categoryName":"Faction Boxes","boxType":"CAP","boxTypeLabel":"Cap Lid","dimensions":"106.5 \u00d7 59.833 \u00d7 24.5 mm","position":"(106.5, 158.333, 28)","compartments":1,"description":"Eyrie warriors (20 meeples)","files":[{"uri":"../_stl/boxes/root/ErieBoxBottom_body.stl?v=41ce480e","filename":"ErieBoxBottom_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/ErieBoxBottom_lid.stl?v=7a12e776","filename":"ErieBoxBottom_lid.stl","kind":"lid"}]},{"label":"ErieBoxTop","anchor":"box-root-erieboxtop","expansion":"base","subgroup":"eyrie","category":"factions","categoryName":"Faction Boxes","boxType":"SLIDING","boxTypeLabel":"Sliding Lid","dimensions":"53.25 \u00d7 59.833 \u00d7 14.5 mm","position":"(53.25, 218.166, 52.5)","compartments":1,"description":"Eyrie roosts, faction & score","files":[{"uri":"../_stl/boxes/root/ErieBoxTop_body.stl?v=190c427c","filename":"ErieBoxTop_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/ErieBoxTop_lid.stl?v=66b3006f","filename":"ErieBoxTop_lid.stl","kind":"lid"}]},{"label":"AllianceBoxBottom","anchor":"box-root-allianceboxbottom","expansion":"base","subgroup":"alliance","category":"factions","categoryName":"Faction Boxes","boxType":"CAP","boxTypeLabel":"Cap Lid","dimensions":"53.25 \u00d7 59.833 \u00d7 24.5 mm","position":"(53.25, 218.166, 28)","compartments":1,"description":"Woodland Alliance warriors (10 meeples)","files":[{"uri":"../_stl/boxes/root/AllianceBoxBottom_body.stl?v=2da2e8a5","filename":"AllianceBoxBottom_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/AllianceBoxBottom_lid.stl?v=2208ea44","filename":"AllianceBoxBottom_lid.stl","kind":"lid"}]},{"label":"AllianceBoxTop","anchor":"box-root-allianceboxtop","expansion":"base","subgroup":"alliance","category":"factions","categoryName":"Faction Boxes","boxType":"SLIDING","boxTypeLabel":"Sliding Lid","dimensions":"53.25 \u00d7 59.833 \u00d7 14.5 mm","position":"(106.5, 158.333, 52.5)","compartments":1,"description":"Alliance bases, sympathy, faction & score","files":[{"uri":"../_stl/boxes/root/AllianceBoxTop_body.stl?v=d8d205bf","filename":"AllianceBoxTop_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/AllianceBoxTop_lid.stl?v=4c5b863a","filename":"AllianceBoxTop_lid.stl","kind":"lid"}]},{"label":"LizardBoxBottom","anchor":"box-root-lizardboxbottom","expansion":"riverfolk","subgroup":"lizard_cult","category":"factions","categoryName":"Faction Boxes","boxType":"CAP","boxTypeLabel":"Cap Lid","dimensions":"106.5 \u00d7 59.833 \u00d7 26.5 mm","position":"(106.5, 98.5, 28)","compartments":1,"description":"Lizard Cult warriors (25 meeples)","files":[{"uri":"../_stl/boxes/root/LizardBoxBottom_body.stl?v=24eec34b","filename":"LizardBoxBottom_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/LizardBoxBottom_lid.stl?v=42acf918","filename":"LizardBoxBottom_lid.stl","kind":"lid"}]},{"label":"LizardBoxTop","anchor":"box-root-lizardboxtop","expansion":"riverfolk","subgroup":"lizard_cult","category":"factions","categoryName":"Faction Boxes","boxType":"SLIDING","boxTypeLabel":"Sliding Lid","dimensions":"79.875 \u00d7 59.833 \u00d7 12.5 mm","position":"(106.5, 98.5, 54.5)","compartments":1,"description":"Lizard gardens, outcast, faction & score","files":[{"uri":"../_stl/boxes/root/LizardBoxTop_body.stl?v=00f0c07b","filename":"LizardBoxTop_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/LizardBoxTop_lid.stl?v=f3fc93d6","filename":"LizardBoxTop_lid.stl","kind":"lid"}]},{"label":"RiverfolkBoxBottom","anchor":"box-root-riverfolkboxbottom","expansion":"riverfolk","subgroup":"riverfolk_company","category":"factions","categoryName":"Faction Boxes","boxType":"CAP","boxTypeLabel":"Cap Lid","dimensions":"53.25 \u00d7 59.833 \u00d7 26.5 mm","position":"(106.5, 218.166, 40.5)","compartments":1,"description":"Riverfolk warriors (15 meeples)","files":[{"uri":"../_stl/boxes/root/RiverfolkBoxBottom_body.stl?v=0c331c5d","filename":"RiverfolkBoxBottom_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/RiverfolkBoxBottom_lid.stl?v=c391c237","filename":"RiverfolkBoxBottom_lid.stl","kind":"lid"}]},{"label":"RiverfolkBoxTop","anchor":"box-root-riverfolkboxtop","expansion":"riverfolk","subgroup":"riverfolk_company","category":"factions","categoryName":"Faction Boxes","boxType":"SLIDING","boxTypeLabel":"Sliding Lid","dimensions":"79.875 \u00d7 59.833 \u00d7 12.5 mm","position":"(106.5, 218.166, 28)","compartments":1,"description":"Riverfolk trade posts, gems & score","files":[{"uri":"../_stl/boxes/root/RiverfolkBoxTop_body.stl?v=ccfed6ed","filename":"RiverfolkBoxTop_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/RiverfolkBoxTop_lid.stl?v=67cdc71d","filename":"RiverfolkBoxTop_lid.stl","kind":"lid"}]},{"label":"VagabondBox","anchor":"box-root-vagabondbox","expansion":"base","subgroup":"vagabond1","category":"factions","categoryName":"Faction Boxes","boxType":"SLIDING","boxTypeLabel":"Sliding Lid","dimensions":"53.25 \u00d7 59.833 \u00d7 19.5 mm","position":"(159.75, 0, 28)","compartments":1,"description":"1st Vagabond meeple, score & relation tokens","files":[{"uri":"../_stl/boxes/root/VagabondBox_body.stl?v=8857fc1a","filename":"VagabondBox_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/VagabondBox_lid.stl?v=c3a127d4","filename":"VagabondBox_lid.stl","kind":"lid"}]},{"label":"VagabondBox2","anchor":"box-root-vagabondbox2","expansion":"riverfolk","subgroup":"vagabond2","category":"factions","categoryName":"Faction Boxes","boxType":"SLIDING","boxTypeLabel":"Sliding Lid","dimensions":"53.25 \u00d7 59.833 \u00d7 19.5 mm","position":"(159.75, 0, 47.5)","compartments":1,"description":"2nd Vagabond meeple, score & relation tokens","files":[{"uri":"../_stl/boxes/root/VagabondBox2_body.stl?v=aab715d8","filename":"VagabondBox2_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/VagabondBox2_lid.stl?v=38de3a0f","filename":"VagabondBox2_lid.stl","kind":"lid"}]},{"label":"DiceBox","anchor":"box-root-dicebox","expansion":"base","subgroup":"dice","category":"items_and_dice","categoryName":"Items & Dice Boxes","boxType":"SLIDING","boxTypeLabel":"Sliding Lid","dimensions":"53.25 \u00d7 59.833 \u00d7 39 mm","position":"(53.25, 158.333, 28)","compartments":1,"description":"2 combat dice","files":[{"uri":"../_stl/boxes/root/DiceBox_body.stl?v=b10b9331","filename":"DiceBox_body.stl","kind":"body"},{"uri":"../_stl/boxes/root/DiceBox_lid.stl?v=c988c591","filename":"DiceBox_lid.stl","kind":"lid"}]}],"spacerSets":{"base+riverfolk":[{"label":"spacer_1","dimensions":"54.25 \u00d7 119.667 \u00d7 14.5 mm","position":"(159.75, 158.333, 52.5)","files":[{"uri":"../_stl/boxes/root/spacer_1.stl?v=4d29cdda","filename":"spacer_1.stl","kind":"spacer"}]},{"label":"spacer_2","dimensions":"54.25 \u00d7 38.667 \u00d7 39 mm","position":"(159.75, 59.833, 28)","files":[{"uri":"../_stl/boxes/root/spacer_2.stl?v=b7ab3da6","filename":"spacer_2.stl","kind":"spacer"}]},{"label":"spacer_3","dimensions":"27.625 \u00d7 59.834 \u00d7 24.5 mm","position":"(186.375, 218.166, 28)","files":[{"uri":"../_stl/boxes/root/spacer_3.stl?v=b0608e81","filename":"spacer_3.stl","kind":"spacer"}]},{"label":"spacer_4","dimensions":"53.25 \u00d7 16.167 \u00d7 39 mm","position":"(0, 261.833, 28)","files":[{"uri":"../_stl/boxes/root/spacer_4.stl?v=925c8932","filename":"spacer_4.stl","kind":"spacer"}]},{"label":"spacer_5","dimensions":"27.625 \u00d7 59.833 \u00d7 12.5 mm","position":"(186.375, 98.5, 54.5)","files":[{"uri":"../_stl/boxes/root/spacer_5.stl?v=ef290ad5","filename":"spacer_5.stl","kind":"spacer"}]},{"label":"spacer_6","dimensions":"26.625 \u00d7 59.834 \u00d7 12 mm","position":"(159.75, 218.166, 40.5)","files":[{"uri":"../_stl/boxes/root/spacer_6.stl?v=fa47bc5e","filename":"spacer_6.stl","kind":"spacer"}]}],"base":[{"label":"spacer_1","dimensions":"80.875 \u00d7 278 \u00d7 39 mm","position":"(133.125, 0, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_add687b498e3.stl?v=1f05ea23","filename":"spacer_1.stl","kind":"spacer"}]},{"label":"spacer_2","dimensions":"133.125 \u00d7 81 \u00d7 19.5 mm","position":"(53.25, 197, 47.5)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_f6d884c13533.stl?v=cd9112dd","filename":"spacer_2.stl","kind":"spacer"}]},{"label":"spacer_3","dimensions":"46.667 \u00d7 54.834 \u00d7 19.5 mm","position":"(139.708, 223.166, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_65700d8429e0.stl?v=3c096881","filename":"spacer_3.stl","kind":"spacer"}]},{"label":"spacer_4","dimensions":"53.25 \u00d7 59.833 \u00d7 14.5 mm","position":"(133.125, 163.333, 52.5)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_d89c65dc97bd.stl?v=8f16fe12","filename":"spacer_4.stl","kind":"spacer"}]},{"label":"spacer_5","dimensions":"53.25 \u00d7 21.167 \u00d7 39 mm","position":"(0, 256.833, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_cd45b402d47e.stl?v=a9af906c","filename":"spacer_5.stl","kind":"spacer"}]},{"label":"spacer_6","dimensions":"26.625 \u00d7 81 \u00d7 19.5 mm","position":"(53.25, 197, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_57dd3dd9f430.stl?v=5fa9cd06","filename":"spacer_6.stl","kind":"spacer"}]}],"base+lizard_cult":[{"label":"spacer_1","dimensions":"107.5 \u00d7 59.834 \u00d7 39 mm","position":"(106.5, 218.166, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_4725b206359c.stl?v=2cb67bfb","filename":"spacer_1.stl","kind":"spacer"}]},{"label":"spacer_2","dimensions":"107.5 \u00d7 59.833 \u00d7 14.5 mm","position":"(106.5, 158.333, 52.5)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_9ab2b8fac77b.stl?v=1568752d","filename":"spacer_2.stl","kind":"spacer"}]},{"label":"spacer_3","dimensions":"54.25 \u00d7 38.667 \u00d7 39 mm","position":"(159.75, 59.833, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_7e6ba060c386.stl?v=3ce68a50","filename":"spacer_3.stl","kind":"spacer"}]},{"label":"spacer_4","dimensions":"53.25 \u00d7 16.167 \u00d7 39 mm","position":"(0, 261.833, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_51da42901f6c.stl?v=067940e9","filename":"spacer_4.stl","kind":"spacer"}]},{"label":"spacer_5","dimensions":"27.625 \u00d7 59.833 \u00d7 12.5 mm","position":"(186.375, 98.5, 54.5)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_a71324494509.stl?v=ff9a0b7e","filename":"spacer_5.stl","kind":"spacer"}]},{"label":"spacer_6","dimensions":"53.25 \u00d7 59.834 \u00d7 5 mm","position":"(53.25, 218.166, 62)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_e0b315c6394c.stl?v=c8db60cd","filename":"spacer_6.stl","kind":"spacer"}]}],"base+riverfolk_company":[{"label":"spacer_1","dimensions":"107.5 \u00d7 119.667 \u00d7 19.5 mm","position":"(106.5, 158.333, 47.5)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_80f963d4284e.stl?v=81d977ce","filename":"spacer_1.stl","kind":"spacer"}]},{"label":"spacer_2","dimensions":"54.25 \u00d7 119.667 \u00d7 19.5 mm","position":"(159.75, 158.333, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_772b16c676be.stl?v=3aa4dbc1","filename":"spacer_2.stl","kind":"spacer"}]},{"label":"spacer_3","dimensions":"54.25 \u00d7 38.667 \u00d7 39 mm","position":"(159.75, 59.833, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_7e6ba060c386.stl?v=3ce68a50","filename":"spacer_3.stl","kind":"spacer"}]},{"label":"spacer_4","dimensions":"54.25 \u00d7 59.833 \u00d7 14.5 mm","position":"(159.75, 98.5, 52.5)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_303ee4c1202a.stl?v=db33c101","filename":"spacer_4.stl","kind":"spacer"}]},{"label":"spacer_5","dimensions":"53.25 \u00d7 59.834 \u00d7 12.5 mm","position":"(53.25, 218.166, 54.5)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_d69e10465b2d.stl?v=5993cecd","filename":"spacer_5.stl","kind":"spacer"}]},{"label":"spacer_6","dimensions":"53.25 \u00d7 16.167 \u00d7 39 mm","position":"(0, 261.833, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_51da42901f6c.stl?v=067940e9","filename":"spacer_6.stl","kind":"spacer"}]},{"label":"spacer_7","dimensions":"79.875 \u00d7 59.834 \u00d7 7 mm","position":"(106.5, 218.166, 40.5)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_a54b74fb82ea.stl?v=dbf36608","filename":"spacer_7.stl","kind":"spacer"}]}],"base+vagabond2":[{"label":"spacer_1","dimensions":"27.625 \u00d7 278 \u00d7 39 mm","position":"(186.375, 0, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_3987cea27208.stl?v=d8f4f9c7","filename":"spacer_1.stl","kind":"spacer"}]},{"label":"spacer_2","dimensions":"79.875 \u00d7 81 \u00d7 39 mm","position":"(0, 197, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_aa40185e94c7.stl?v=c2d56524","filename":"spacer_2.stl","kind":"spacer"}]},{"label":"spacer_3","dimensions":"53.25 \u00d7 158.334 \u00d7 14.5 mm","position":"(133.125, 119.666, 52.5)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_31fd7f44b486.stl?v=c6574607","filename":"spacer_3.stl","kind":"spacer"}]},{"label":"spacer_4","dimensions":"46.667 \u00d7 54.834 \u00d7 24.5 mm","position":"(139.708, 223.166, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_d80080607c79.stl?v=ffa821d5","filename":"spacer_4.stl","kind":"spacer"}]},{"label":"spacer_5","dimensions":"53.25 \u00d7 43.667 \u00d7 24.5 mm","position":"(133.125, 119.666, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_80cabf98779d.stl?v=6d88fadf","filename":"spacer_5.stl","kind":"spacer"}]}],"base+lizard_cult+riverfolk_company":[{"label":"spacer_1","dimensions":"54.25 \u00d7 119.667 \u00d7 14.5 mm","position":"(159.75, 158.333, 52.5)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_82d67750a216.stl?v=0246e0fc","filename":"spacer_1.stl","kind":"spacer"}]},{"label":"spacer_2","dimensions":"54.25 \u00d7 38.667 \u00d7 39 mm","position":"(159.75, 59.833, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_7e6ba060c386.stl?v=3ce68a50","filename":"spacer_2.stl","kind":"spacer"}]},{"label":"spacer_3","dimensions":"106.5 \u00d7 59.834 \u00d7 7 mm","position":"(53.25, 218.166, 60)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_c65156bad221.stl?v=47dd0077","filename":"spacer_3.stl","kind":"spacer"}]},{"label":"spacer_4","dimensions":"27.625 \u00d7 59.834 \u00d7 24.5 mm","position":"(186.375, 218.166, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_1e365c049fe1.stl?v=1c4b5483","filename":"spacer_4.stl","kind":"spacer"}]},{"label":"spacer_5","dimensions":"53.25 \u00d7 16.167 \u00d7 39 mm","position":"(0, 261.833, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_51da42901f6c.stl?v=067940e9","filename":"spacer_5.stl","kind":"spacer"}]},{"label":"spacer_6","dimensions":"27.625 \u00d7 59.833 \u00d7 12.5 mm","position":"(186.375, 98.5, 54.5)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_a71324494509.stl?v=ff9a0b7e","filename":"spacer_6.stl","kind":"spacer"}]},{"label":"spacer_7","dimensions":"26.625 \u00d7 59.834 \u00d7 12 mm","position":"(159.75, 218.166, 40.5)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_26351688f5b1.stl?v=190d58eb","filename":"spacer_7.stl","kind":"spacer"}]},{"label":"spacer_8","dimensions":"53.25 \u00d7 59.834 \u00d7 5.5 mm","position":"(53.25, 218.166, 54.5)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_019f482860a5.stl?v=ce4f0d11","filename":"spacer_8.stl","kind":"spacer"}]}],"base+lizard_cult+vagabond2":[{"label":"spacer_1","dimensions":"107.5 \u00d7 59.834 \u00d7 39 mm","position":"(106.5, 218.166, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_4725b206359c.stl?v=2cb67bfb","filename":"spacer_1.stl","kind":"spacer"}]},{"label":"spacer_2","dimensions":"54.25 \u00d7 38.667 \u00d7 39 mm","position":"(159.75, 59.833, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_7e6ba060c386.stl?v=3ce68a50","filename":"spacer_2.stl","kind":"spacer"}]},{"label":"spacer_3","dimensions":"54.25 \u00d7 59.833 \u00d7 14.5 mm","position":"(159.75, 158.333, 52.5)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_8c5d8641ba89.stl?v=71858273","filename":"spacer_3.stl","kind":"spacer"}]},{"label":"spacer_4","dimensions":"53.25 \u00d7 16.167 \u00d7 39 mm","position":"(0, 261.833, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_51da42901f6c.stl?v=067940e9","filename":"spacer_4.stl","kind":"spacer"}]},{"label":"spacer_5","dimensions":"27.625 \u00d7 59.833 \u00d7 12.5 mm","position":"(186.375, 98.5, 54.5)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_a71324494509.stl?v=ff9a0b7e","filename":"spacer_5.stl","kind":"spacer"}]}],"base+riverfolk_company+vagabond2":[{"label":"spacer_1","dimensions":"107.5 \u00d7 119.667 \u00d7 26.5 mm","position":"(106.5, 158.333, 40.5)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_64aed51d7570.stl?v=c4481047","filename":"spacer_1.stl","kind":"spacer"}]},{"label":"spacer_2","dimensions":"54.25 \u00d7 38.667 \u00d7 39 mm","position":"(159.75, 59.833, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_7e6ba060c386.stl?v=3ce68a50","filename":"spacer_2.stl","kind":"spacer"}]},{"label":"spacer_3","dimensions":"54.25 \u00d7 119.667 \u00d7 12.5 mm","position":"(159.75, 158.333, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_eaddb7a37135.stl?v=33e6acca","filename":"spacer_3.stl","kind":"spacer"}]},{"label":"spacer_4","dimensions":"54.25 \u00d7 59.833 \u00d7 14.5 mm","position":"(159.75, 98.5, 52.5)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_303ee4c1202a.stl?v=db33c101","filename":"spacer_4.stl","kind":"spacer"}]},{"label":"spacer_5","dimensions":"53.25 \u00d7 59.833 \u00d7 12.5 mm","position":"(106.5, 158.333, 54.5)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_1d64b56ac3f7.stl?v=d333ec9f","filename":"spacer_5.stl","kind":"spacer"}]},{"label":"spacer_6","dimensions":"53.25 \u00d7 16.167 \u00d7 39 mm","position":"(0, 261.833, 28)","files":[{"uri":"../_stl/boxes/root/variant_spacers/spacer_51da42901f6c.stl?v=067940e9","filename":"spacer_6.stl","kind":"spacer"}]}]}}</script>
     <div data-box-selector-mount></div>
     <div class="stl-viewer" data-stl-uri="../_stl/boxes/root/BaseCardBox_body.stl?v=280f57b0,../_stl/boxes/root/BaseCardBox_lid.stl?v=f7a52ec0,../_stl/boxes/root/ErieCardBox_body.stl?v=4ef254db,../_stl/boxes/root/ErieCardBox_lid.stl?v=8fd10207,../_stl/boxes/root/VagabondCardBox_body.stl?v=6fe66e01,../_stl/boxes/root/VagabondCardBox_lid.stl?v=1e30bd13,../_stl/boxes/root/OverviewCardBox_body.stl?v=40e07195,../_stl/boxes/root/OverviewCardBox_lid.stl?v=08075eb5,../_stl/boxes/root/ItemsBoxBottom_body.stl?v=e62368bb,../_stl/boxes/root/ItemsBoxBottom_lid.stl?v=fb9d850b,../_stl/boxes/root/ItemsBoxMiddle_body.stl?v=a03ba0bb,../_stl/boxes/root/ItemsBoxMiddle_lid.stl?v=19dcdaa4,../_stl/boxes/root/ItemsBoxWinter_body.stl?v=eb23ba37,../_stl/boxes/root/ItemsBoxWinter_lid.stl?v=00995441,../_stl/boxes/root/ItemsBoxExtras_body.stl?v=9deb1f10,../_stl/boxes/root/ItemsBoxExtras_lid.stl?v=f025454e,../_stl/boxes/root/MarquisBoxBottom_body.stl?v=f5ea0af3,../_stl/boxes/root/MarquisBoxBottom_lid.stl?v=eb8a03ce,../_stl/boxes/root/MarquisBoxTop_body.stl?v=be7708f9,../_stl/boxes/root/MarquisBoxTop_lid.stl?v=0f1520ae,../_stl/boxes/root/ErieBoxBottom_body.stl?v=41ce480e,../_stl/boxes/root/ErieBoxBottom_lid.stl?v=7a12e776,../_stl/boxes/root/ErieBoxTop_body.stl?v=190c427c,../_stl/boxes/root/ErieBoxTop_lid.stl?v=66b3006f,../_stl/boxes/root/AllianceBoxBottom_body.stl?v=2da2e8a5,../_stl/boxes/root/AllianceBoxBottom_lid.stl?v=2208ea44,../_stl/boxes/root/AllianceBoxTop_body.stl?v=d8d205bf,../_stl/boxes/root/AllianceBoxTop_lid.stl?v=4c5b863a,../_stl/boxes/root/LizardBoxBottom_body.stl?v=24eec34b,../_stl/boxes/root/LizardBoxBottom_lid.stl?v=42acf918,../_stl/boxes/root/LizardBoxTop_body.stl?v=00f0c07b,../_stl/boxes/root/LizardBoxTop_lid.stl?v=f3fc93d6,../_stl/boxes/root/RiverfolkBoxBottom_body.stl?v=0c331c5d,../_stl/boxes/root/RiverfolkBoxBottom_lid.stl?v=c391c237,../_stl/boxes/root/RiverfolkBoxTop_body.stl?v=ccfed6ed,../_stl/boxes/root/RiverfolkBoxTop_lid.stl?v=67cdc71d,../_stl/boxes/root/VagabondBox_body.stl?v=8857fc1a,../_stl/boxes/root/VagabondBox_lid.stl?v=c3a127d4,../_stl/boxes/root/VagabondBox2_body.stl?v=aab715d8,../_stl/boxes/root/VagabondBox2_lid.stl?v=38de3a0f,../_stl/boxes/root/DiceBox_body.stl?v=b10b9331,../_stl/boxes/root/DiceBox_lid.stl?v=c988c591,../_stl/boxes/root/spacer_1.stl?v=4d29cdda,../_stl/boxes/root/spacer_2.stl?v=b7ab3da6,../_stl/boxes/root/spacer_3.stl?v=b0608e81,../_stl/boxes/root/spacer_4.stl?v=925c8932,../_stl/boxes/root/spacer_5.stl?v=ef290ad5,../_stl/boxes/root/spacer_6.stl?v=fa47bc5e" data-stl-color="#6f9ac9" style="width:100%;height:420px">
       <div class="stl-viewer-status">Loading 3-D preview&hellip;</div>
     </div>
   </div>

Full Box Packing
----------------

Interactive 3-D view of all boxes, lids, and spacers packed inside the game box:

.. stl:: ../_stl/boxes/root/BaseCardBox_body.stl?v=280f57b0,../_stl/boxes/root/BaseCardBox_lid.stl?v=f7a52ec0,../_stl/boxes/root/ErieCardBox_body.stl?v=4ef254db,../_stl/boxes/root/ErieCardBox_lid.stl?v=8fd10207,../_stl/boxes/root/VagabondCardBox_body.stl?v=6fe66e01,../_stl/boxes/root/VagabondCardBox_lid.stl?v=1e30bd13,../_stl/boxes/root/OverviewCardBox_body.stl?v=40e07195,../_stl/boxes/root/OverviewCardBox_lid.stl?v=08075eb5,../_stl/boxes/root/ItemsBoxBottom_body.stl?v=e62368bb,../_stl/boxes/root/ItemsBoxBottom_lid.stl?v=fb9d850b,../_stl/boxes/root/ItemsBoxMiddle_body.stl?v=a03ba0bb,../_stl/boxes/root/ItemsBoxMiddle_lid.stl?v=19dcdaa4,../_stl/boxes/root/ItemsBoxWinter_body.stl?v=eb23ba37,../_stl/boxes/root/ItemsBoxWinter_lid.stl?v=00995441,../_stl/boxes/root/ItemsBoxExtras_body.stl?v=9deb1f10,../_stl/boxes/root/ItemsBoxExtras_lid.stl?v=f025454e,../_stl/boxes/root/MarquisBoxBottom_body.stl?v=f5ea0af3,../_stl/boxes/root/MarquisBoxBottom_lid.stl?v=eb8a03ce,../_stl/boxes/root/MarquisBoxTop_body.stl?v=be7708f9,../_stl/boxes/root/MarquisBoxTop_lid.stl?v=0f1520ae,../_stl/boxes/root/ErieBoxBottom_body.stl?v=41ce480e,../_stl/boxes/root/ErieBoxBottom_lid.stl?v=7a12e776,../_stl/boxes/root/ErieBoxTop_body.stl?v=190c427c,../_stl/boxes/root/ErieBoxTop_lid.stl?v=66b3006f,../_stl/boxes/root/AllianceBoxBottom_body.stl?v=2da2e8a5,../_stl/boxes/root/AllianceBoxBottom_lid.stl?v=2208ea44,../_stl/boxes/root/AllianceBoxTop_body.stl?v=d8d205bf,../_stl/boxes/root/AllianceBoxTop_lid.stl?v=4c5b863a,../_stl/boxes/root/LizardBoxBottom_body.stl?v=24eec34b,../_stl/boxes/root/LizardBoxBottom_lid.stl?v=42acf918,../_stl/boxes/root/LizardBoxTop_body.stl?v=00f0c07b,../_stl/boxes/root/LizardBoxTop_lid.stl?v=f3fc93d6,../_stl/boxes/root/RiverfolkBoxBottom_body.stl?v=0c331c5d,../_stl/boxes/root/RiverfolkBoxBottom_lid.stl?v=c391c237,../_stl/boxes/root/RiverfolkBoxTop_body.stl?v=ccfed6ed,../_stl/boxes/root/RiverfolkBoxTop_lid.stl?v=67cdc71d,../_stl/boxes/root/VagabondBox_body.stl?v=8857fc1a,../_stl/boxes/root/VagabondBox_lid.stl?v=c3a127d4,../_stl/boxes/root/VagabondBox2_body.stl?v=aab715d8,../_stl/boxes/root/VagabondBox2_lid.stl?v=38de3a0f,../_stl/boxes/root/DiceBox_body.stl?v=b10b9331,../_stl/boxes/root/DiceBox_lid.stl?v=c988c591,../_stl/boxes/root/spacer_1.stl?v=4d29cdda,../_stl/boxes/root/spacer_2.stl?v=b7ab3da6,../_stl/boxes/root/spacer_3.stl?v=b0608e81,../_stl/boxes/root/spacer_4.stl?v=925c8932,../_stl/boxes/root/spacer_5.stl?v=ef290ad5,../_stl/boxes/root/spacer_6.stl?v=fa47bc5e
   :height: 440px

.. raw:: html

   <p><a href="../_stl/boxes/root/BaseCardBox_body.stl?v=280f57b0" data-stl-combine="../_stl/boxes/root/BaseCardBox_body.stl?v=280f57b0,../_stl/boxes/root/BaseCardBox_lid.stl?v=f7a52ec0,../_stl/boxes/root/ErieCardBox_body.stl?v=4ef254db,../_stl/boxes/root/ErieCardBox_lid.stl?v=8fd10207,../_stl/boxes/root/VagabondCardBox_body.stl?v=6fe66e01,../_stl/boxes/root/VagabondCardBox_lid.stl?v=1e30bd13,../_stl/boxes/root/OverviewCardBox_body.stl?v=40e07195,../_stl/boxes/root/OverviewCardBox_lid.stl?v=08075eb5,../_stl/boxes/root/ItemsBoxBottom_body.stl?v=e62368bb,../_stl/boxes/root/ItemsBoxBottom_lid.stl?v=fb9d850b,../_stl/boxes/root/ItemsBoxMiddle_body.stl?v=a03ba0bb,../_stl/boxes/root/ItemsBoxMiddle_lid.stl?v=19dcdaa4,../_stl/boxes/root/ItemsBoxWinter_body.stl?v=eb23ba37,../_stl/boxes/root/ItemsBoxWinter_lid.stl?v=00995441,../_stl/boxes/root/ItemsBoxExtras_body.stl?v=9deb1f10,../_stl/boxes/root/ItemsBoxExtras_lid.stl?v=f025454e,../_stl/boxes/root/MarquisBoxBottom_body.stl?v=f5ea0af3,../_stl/boxes/root/MarquisBoxBottom_lid.stl?v=eb8a03ce,../_stl/boxes/root/MarquisBoxTop_body.stl?v=be7708f9,../_stl/boxes/root/MarquisBoxTop_lid.stl?v=0f1520ae,../_stl/boxes/root/ErieBoxBottom_body.stl?v=41ce480e,../_stl/boxes/root/ErieBoxBottom_lid.stl?v=7a12e776,../_stl/boxes/root/ErieBoxTop_body.stl?v=190c427c,../_stl/boxes/root/ErieBoxTop_lid.stl?v=66b3006f,../_stl/boxes/root/AllianceBoxBottom_body.stl?v=2da2e8a5,../_stl/boxes/root/AllianceBoxBottom_lid.stl?v=2208ea44,../_stl/boxes/root/AllianceBoxTop_body.stl?v=d8d205bf,../_stl/boxes/root/AllianceBoxTop_lid.stl?v=4c5b863a,../_stl/boxes/root/LizardBoxBottom_body.stl?v=24eec34b,../_stl/boxes/root/LizardBoxBottom_lid.stl?v=42acf918,../_stl/boxes/root/LizardBoxTop_body.stl?v=00f0c07b,../_stl/boxes/root/LizardBoxTop_lid.stl?v=f3fc93d6,../_stl/boxes/root/RiverfolkBoxBottom_body.stl?v=0c331c5d,../_stl/boxes/root/RiverfolkBoxBottom_lid.stl?v=c391c237,../_stl/boxes/root/RiverfolkBoxTop_body.stl?v=ccfed6ed,../_stl/boxes/root/RiverfolkBoxTop_lid.stl?v=67cdc71d,../_stl/boxes/root/VagabondBox_body.stl?v=8857fc1a,../_stl/boxes/root/VagabondBox_lid.stl?v=c3a127d4,../_stl/boxes/root/VagabondBox2_body.stl?v=aab715d8,../_stl/boxes/root/VagabondBox2_lid.stl?v=38de3a0f,../_stl/boxes/root/DiceBox_body.stl?v=b10b9331,../_stl/boxes/root/DiceBox_lid.stl?v=c988c591,../_stl/boxes/root/spacer_1.stl?v=4d29cdda,../_stl/boxes/root/spacer_2.stl?v=b7ab3da6,../_stl/boxes/root/spacer_3.stl?v=b0608e81,../_stl/boxes/root/spacer_4.stl?v=925c8932,../_stl/boxes/root/spacer_5.stl?v=ef290ad5,../_stl/boxes/root/spacer_6.stl?v=fa47bc5e" download="Root_full_packing.stl">⬇ Download Full Box Packing STL (<code>Root_full_packing.stl</code>)</a></p>

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
     - ``(79.875, 0, 28)``
     - 1
   * - :ref:`ErieCardBox <box-root-eriecardbox>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``79.875 × 98.5 × 8.6 mm``
     - ``(0, 0, 28)``
     - 1
   * - :ref:`VagabondCardBox <box-root-vagabondcardbox>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``79.875 × 98.5 × 19.4 mm``
     - ``(0, 0, 36.6)``
     - 1
   * - :ref:`OverviewCardBox <box-root-overviewcardbox>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``79.875 × 98.5 × 11 mm``
     - ``(0, 0, 56)``
     - 1
   * - :ref:`ItemsBoxBottom <box-root-itemsboxbottom>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``53.25 × 103.5 × 10 mm``
     - ``(0, 158.333, 28)``
     - 1
   * - :ref:`ItemsBoxMiddle <box-root-itemsboxmiddle>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``53.25 × 103.5 × 9 mm``
     - ``(0, 158.333, 38)``
     - 1
   * - :ref:`ItemsBoxWinter <box-root-itemsboxwinter>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``53.25 × 103.5 × 9 mm``
     - ``(0, 158.333, 47)``
     - 1
   * - :ref:`ItemsBoxExtras <box-root-itemsboxextras>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``53.25 × 103.5 × 11 mm``
     - ``(0, 158.333, 56)``
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
     - ``(106.5, 158.333, 28)``
     - 1
   * - :ref:`ErieBoxTop <box-root-erieboxtop>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``53.25 × 59.833 × 14.5 mm``
     - ``(53.25, 218.166, 52.5)``
     - 1
   * - :ref:`AllianceBoxBottom <box-root-allianceboxbottom>`
     - :ref:`BoxType.CAP <box-type-cap>`
     - ``53.25 × 59.833 × 24.5 mm``
     - ``(53.25, 218.166, 28)``
     - 1
   * - :ref:`AllianceBoxTop <box-root-allianceboxtop>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``53.25 × 59.833 × 14.5 mm``
     - ``(106.5, 158.333, 52.5)``
     - 1
   * - :ref:`LizardBoxBottom <box-root-lizardboxbottom>`
     - :ref:`BoxType.CAP <box-type-cap>`
     - ``106.5 × 59.833 × 26.5 mm``
     - ``(106.5, 98.5, 28)``
     - 1
   * - :ref:`LizardBoxTop <box-root-lizardboxtop>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``79.875 × 59.833 × 12.5 mm``
     - ``(106.5, 98.5, 54.5)``
     - 1
   * - :ref:`RiverfolkBoxBottom <box-root-riverfolkboxbottom>`
     - :ref:`BoxType.CAP <box-type-cap>`
     - ``53.25 × 59.833 × 26.5 mm``
     - ``(106.5, 218.166, 40.5)``
     - 1
   * - :ref:`RiverfolkBoxTop <box-root-riverfolkboxtop>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``79.875 × 59.833 × 12.5 mm``
     - ``(106.5, 218.166, 28)``
     - 1
   * - :ref:`VagabondBox <box-root-vagabondbox>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``53.25 × 59.833 × 19.5 mm``
     - ``(159.75, 0, 28)``
     - 1
   * - :ref:`VagabondBox2 <box-root-vagabondbox2>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``53.25 × 59.833 × 19.5 mm``
     - ``(159.75, 0, 47.5)``
     - 1
   * - :ref:`DiceBox <box-root-dicebox>`
     - :ref:`BoxType.SLIDING <box-type-sliding>`
     - ``53.25 × 59.833 × 39 mm``
     - ``(53.25, 158.333, 28)``
     - 1
   * - :ref:`spacer_1 <spacer-root-spacer_1>`
     - :ref:`BoxType.NO_LID <box-type-no-lid>` (spacer)
     - ``54.25 × 119.667 × 14.5 mm``
     - ``(159.75, 158.333, 52.5)``
     - —
   * - :ref:`spacer_2 <spacer-root-spacer_2>`
     - :ref:`BoxType.NO_LID <box-type-no-lid>` (spacer)
     - ``54.25 × 38.667 × 39 mm``
     - ``(159.75, 59.833, 28)``
     - —
   * - :ref:`spacer_3 <spacer-root-spacer_3>`
     - :ref:`BoxType.NO_LID <box-type-no-lid>` (spacer)
     - ``27.625 × 59.834 × 24.5 mm``
     - ``(186.375, 218.166, 28)``
     - —
   * - :ref:`spacer_4 <spacer-root-spacer_4>`
     - :ref:`BoxType.NO_LID <box-type-no-lid>` (spacer)
     - ``53.25 × 16.167 × 39 mm``
     - ``(0, 261.833, 28)``
     - —
   * - :ref:`spacer_5 <spacer-root-spacer_5>`
     - :ref:`BoxType.NO_LID <box-type-no-lid>` (spacer)
     - ``27.625 × 59.833 × 12.5 mm``
     - ``(186.375, 98.5, 54.5)``
     - —
   * - :ref:`spacer_6 <spacer-root-spacer_6>`
     - :ref:`BoxType.NO_LID <box-type-no-lid>` (spacer)
     - ``26.625 × 59.834 × 12 mm``
     - ``(159.75, 218.166, 40.5)``
     - —

Individual Boxes & Parts
------------------------

.. _box-root-basecardbox:

BaseCardBox
^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``79.875 × 98.5 × 39 mm``
- **Packed Position**: ``(79.875, 0, 28)``
- **Compartments (1)**: ``Cards`` (75.875 × 94.5 mm)

**Assembled Box (BaseCardBox — Body + Lid)**

.. stl:: ../_stl/boxes/root/BaseCardBox_body.stl?v=280f57b0,../_stl/boxes/root/BaseCardBox_lid.stl?v=f7a52ec0
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/BaseCardBox_body.stl?v=280f57b0" data-stl-combine="../_stl/boxes/root/BaseCardBox_body.stl?v=280f57b0,../_stl/boxes/root/BaseCardBox_lid.stl?v=f7a52ec0" download="BaseCardBox_assembled.stl">⬇ Download Assembled BaseCardBox STL (<code>BaseCardBox_assembled.stl</code>)</a></p>

**Part: BaseCardBox Body**

.. stl:: ../_stl/boxes/root/BaseCardBox_body.stl?v=280f57b0
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/BaseCardBox_body.stl?v=280f57b0" download="BaseCardBox_body.stl">⬇ Download BaseCardBox Body STL (<code>BaseCardBox_body.stl</code>)</a></p>

**Part: BaseCardBox Lid**

.. stl:: ../_stl/boxes/root/BaseCardBox_lid.stl?v=f7a52ec0
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/BaseCardBox_lid.stl?v=f7a52ec0" download="BaseCardBox_lid.stl">⬇ Download BaseCardBox Lid STL (<code>BaseCardBox_lid.stl</code>)</a></p>

.. _box-root-eriecardbox:

ErieCardBox
^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``79.875 × 98.5 × 8.6 mm``
- **Packed Position**: ``(0, 0, 28)``
- **Stackable Mode**: ``StackableMode.PYRAMIDS``
- **Stacking Order Key**: bottom ``flat (bottom of stack)``, top ``pyramids=2``
- **Compartments (1)**: ``Cards`` (75.875 × 94.5 mm)

**Assembled Box (ErieCardBox — Body + Lid)**

.. stl:: ../_stl/boxes/root/ErieCardBox_body.stl?v=4ef254db,../_stl/boxes/root/ErieCardBox_lid.stl?v=8fd10207
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/ErieCardBox_body.stl?v=4ef254db" data-stl-combine="../_stl/boxes/root/ErieCardBox_body.stl?v=4ef254db,../_stl/boxes/root/ErieCardBox_lid.stl?v=8fd10207" download="ErieCardBox_assembled.stl">⬇ Download Assembled ErieCardBox STL (<code>ErieCardBox_assembled.stl</code>)</a></p>

**Part: ErieCardBox Body**

.. stl:: ../_stl/boxes/root/ErieCardBox_body.stl?v=4ef254db
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ErieCardBox_body.stl?v=4ef254db" download="ErieCardBox_body.stl">⬇ Download ErieCardBox Body STL (<code>ErieCardBox_body.stl</code>)</a></p>

**Part: ErieCardBox Lid**

.. stl:: ../_stl/boxes/root/ErieCardBox_lid.stl?v=8fd10207
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ErieCardBox_lid.stl?v=8fd10207" download="ErieCardBox_lid.stl">⬇ Download ErieCardBox Lid STL (<code>ErieCardBox_lid.stl</code>)</a></p>

.. _box-root-vagabondcardbox:

VagabondCardBox
^^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``79.875 × 98.5 × 19.4 mm``
- **Packed Position**: ``(0, 0, 36.6)``
- **Stackable Mode**: ``StackableMode.PYRAMIDS``
- **Stacking Order Key**: bottom ``pyramids=2``, top ``pyramids=3``
- **Compartments (1)**: ``Cards`` (75.875 × 94.5 mm)

**Assembled Box (VagabondCardBox — Body + Lid)**

.. stl:: ../_stl/boxes/root/VagabondCardBox_body.stl?v=6fe66e01,../_stl/boxes/root/VagabondCardBox_lid.stl?v=1e30bd13
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/VagabondCardBox_body.stl?v=6fe66e01" data-stl-combine="../_stl/boxes/root/VagabondCardBox_body.stl?v=6fe66e01,../_stl/boxes/root/VagabondCardBox_lid.stl?v=1e30bd13" download="VagabondCardBox_assembled.stl">⬇ Download Assembled VagabondCardBox STL (<code>VagabondCardBox_assembled.stl</code>)</a></p>

**Part: VagabondCardBox Body**

.. stl:: ../_stl/boxes/root/VagabondCardBox_body.stl?v=6fe66e01
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/VagabondCardBox_body.stl?v=6fe66e01" download="VagabondCardBox_body.stl">⬇ Download VagabondCardBox Body STL (<code>VagabondCardBox_body.stl</code>)</a></p>

**Part: VagabondCardBox Lid**

.. stl:: ../_stl/boxes/root/VagabondCardBox_lid.stl?v=1e30bd13
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/VagabondCardBox_lid.stl?v=1e30bd13" download="VagabondCardBox_lid.stl">⬇ Download VagabondCardBox Lid STL (<code>VagabondCardBox_lid.stl</code>)</a></p>

.. _box-root-overviewcardbox:

OverviewCardBox
^^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``79.875 × 98.5 × 11 mm``
- **Packed Position**: ``(0, 0, 56)``
- **Stackable Mode**: ``StackableMode.PYRAMIDS``
- **Stacking Order Key**: bottom ``pyramids=3``, top ``flat (top of stack)``
- **Compartments (1)**: ``Cards`` (75.875 × 94.5 mm)

**Assembled Box (OverviewCardBox — Body + Lid)**

.. stl:: ../_stl/boxes/root/OverviewCardBox_body.stl?v=40e07195,../_stl/boxes/root/OverviewCardBox_lid.stl?v=08075eb5
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/OverviewCardBox_body.stl?v=40e07195" data-stl-combine="../_stl/boxes/root/OverviewCardBox_body.stl?v=40e07195,../_stl/boxes/root/OverviewCardBox_lid.stl?v=08075eb5" download="OverviewCardBox_assembled.stl">⬇ Download Assembled OverviewCardBox STL (<code>OverviewCardBox_assembled.stl</code>)</a></p>

**Part: OverviewCardBox Body**

.. stl:: ../_stl/boxes/root/OverviewCardBox_body.stl?v=40e07195
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/OverviewCardBox_body.stl?v=40e07195" download="OverviewCardBox_body.stl">⬇ Download OverviewCardBox Body STL (<code>OverviewCardBox_body.stl</code>)</a></p>

**Part: OverviewCardBox Lid**

.. stl:: ../_stl/boxes/root/OverviewCardBox_lid.stl?v=08075eb5
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/OverviewCardBox_lid.stl?v=08075eb5" download="OverviewCardBox_lid.stl">⬇ Download OverviewCardBox Lid STL (<code>OverviewCardBox_lid.stl</code>)</a></p>

.. _box-root-itemsboxbottom:

ItemsBoxBottom
^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``53.25 × 103.5 × 10 mm``
- **Packed Position**: ``(0, 158.333, 28)``
- **Stackable Mode**: ``StackableMode.PYRAMIDS``
- **Stacking Order Key**: bottom ``flat (bottom of stack)``, top ``pyramids=2``
- **Compartments (1)**: ``Items`` (D=6 mm, 22 elements)

**Assembled Box (ItemsBoxBottom — Body + Lid)**

.. stl:: ../_stl/boxes/root/ItemsBoxBottom_body.stl?v=e62368bb,../_stl/boxes/root/ItemsBoxBottom_lid.stl?v=fb9d850b
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxBottom_body.stl?v=e62368bb" data-stl-combine="../_stl/boxes/root/ItemsBoxBottom_body.stl?v=e62368bb,../_stl/boxes/root/ItemsBoxBottom_lid.stl?v=fb9d850b" download="ItemsBoxBottom_assembled.stl">⬇ Download Assembled ItemsBoxBottom STL (<code>ItemsBoxBottom_assembled.stl</code>)</a></p>

**Part: ItemsBoxBottom Body**

.. stl:: ../_stl/boxes/root/ItemsBoxBottom_body.stl?v=e62368bb
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxBottom_body.stl?v=e62368bb" download="ItemsBoxBottom_body.stl">⬇ Download ItemsBoxBottom Body STL (<code>ItemsBoxBottom_body.stl</code>)</a></p>

**Part: ItemsBoxBottom Lid**

.. stl:: ../_stl/boxes/root/ItemsBoxBottom_lid.stl?v=fb9d850b
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxBottom_lid.stl?v=fb9d850b" download="ItemsBoxBottom_lid.stl">⬇ Download ItemsBoxBottom Lid STL (<code>ItemsBoxBottom_lid.stl</code>)</a></p>

.. _box-root-itemsboxmiddle:

ItemsBoxMiddle
^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``53.25 × 103.5 × 9 mm``
- **Packed Position**: ``(0, 158.333, 38)``
- **Stackable Mode**: ``StackableMode.PYRAMIDS``
- **Stacking Order Key**: bottom ``pyramids=2``, top ``pyramids=3``
- **Compartments (1)**: ``Items`` (D=5 mm, 20 elements)

**Assembled Box (ItemsBoxMiddle — Body + Lid)**

.. stl:: ../_stl/boxes/root/ItemsBoxMiddle_body.stl?v=a03ba0bb,../_stl/boxes/root/ItemsBoxMiddle_lid.stl?v=19dcdaa4
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxMiddle_body.stl?v=a03ba0bb" data-stl-combine="../_stl/boxes/root/ItemsBoxMiddle_body.stl?v=a03ba0bb,../_stl/boxes/root/ItemsBoxMiddle_lid.stl?v=19dcdaa4" download="ItemsBoxMiddle_assembled.stl">⬇ Download Assembled ItemsBoxMiddle STL (<code>ItemsBoxMiddle_assembled.stl</code>)</a></p>

**Part: ItemsBoxMiddle Body**

.. stl:: ../_stl/boxes/root/ItemsBoxMiddle_body.stl?v=a03ba0bb
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxMiddle_body.stl?v=a03ba0bb" download="ItemsBoxMiddle_body.stl">⬇ Download ItemsBoxMiddle Body STL (<code>ItemsBoxMiddle_body.stl</code>)</a></p>

**Part: ItemsBoxMiddle Lid**

.. stl:: ../_stl/boxes/root/ItemsBoxMiddle_lid.stl?v=19dcdaa4
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxMiddle_lid.stl?v=19dcdaa4" download="ItemsBoxMiddle_lid.stl">⬇ Download ItemsBoxMiddle Lid STL (<code>ItemsBoxMiddle_lid.stl</code>)</a></p>

.. _box-root-itemsboxwinter:

ItemsBoxWinter
^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``53.25 × 103.5 × 9 mm``
- **Packed Position**: ``(0, 158.333, 47)``
- **Stackable Mode**: ``StackableMode.PYRAMIDS``
- **Stacking Order Key**: bottom ``pyramids=3``, top ``pyramids=(2, 3, 3, 2)``
- **Compartments (1)**: ``WinterTokens`` (D=5 mm, 12 elements)

**Assembled Box (ItemsBoxWinter — Body + Lid)**

.. stl:: ../_stl/boxes/root/ItemsBoxWinter_body.stl?v=eb23ba37,../_stl/boxes/root/ItemsBoxWinter_lid.stl?v=00995441
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxWinter_body.stl?v=eb23ba37" data-stl-combine="../_stl/boxes/root/ItemsBoxWinter_body.stl?v=eb23ba37,../_stl/boxes/root/ItemsBoxWinter_lid.stl?v=00995441" download="ItemsBoxWinter_assembled.stl">⬇ Download Assembled ItemsBoxWinter STL (<code>ItemsBoxWinter_assembled.stl</code>)</a></p>

**Part: ItemsBoxWinter Body**

.. stl:: ../_stl/boxes/root/ItemsBoxWinter_body.stl?v=eb23ba37
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxWinter_body.stl?v=eb23ba37" download="ItemsBoxWinter_body.stl">⬇ Download ItemsBoxWinter Body STL (<code>ItemsBoxWinter_body.stl</code>)</a></p>

**Part: ItemsBoxWinter Lid**

.. stl:: ../_stl/boxes/root/ItemsBoxWinter_lid.stl?v=00995441
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxWinter_lid.stl?v=00995441" download="ItemsBoxWinter_lid.stl">⬇ Download ItemsBoxWinter Lid STL (<code>ItemsBoxWinter_lid.stl</code>)</a></p>

.. _box-root-itemsboxextras:

ItemsBoxExtras
^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``53.25 × 103.5 × 11 mm``
- **Packed Position**: ``(0, 158.333, 56)``
- **Stackable Mode**: ``StackableMode.PYRAMIDS``
- **Stacking Order Key**: bottom ``pyramids=(2, 3, 3, 2)``, top ``flat (top of stack)``
- **Compartments (1)**: ``Extras`` (D=7 mm, 16 elements)

**Assembled Box (ItemsBoxExtras — Body + Lid)**

.. stl:: ../_stl/boxes/root/ItemsBoxExtras_body.stl?v=9deb1f10,../_stl/boxes/root/ItemsBoxExtras_lid.stl?v=f025454e
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxExtras_body.stl?v=9deb1f10" data-stl-combine="../_stl/boxes/root/ItemsBoxExtras_body.stl?v=9deb1f10,../_stl/boxes/root/ItemsBoxExtras_lid.stl?v=f025454e" download="ItemsBoxExtras_assembled.stl">⬇ Download Assembled ItemsBoxExtras STL (<code>ItemsBoxExtras_assembled.stl</code>)</a></p>

**Part: ItemsBoxExtras Body**

.. stl:: ../_stl/boxes/root/ItemsBoxExtras_body.stl?v=9deb1f10
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxExtras_body.stl?v=9deb1f10" download="ItemsBoxExtras_body.stl">⬇ Download ItemsBoxExtras Body STL (<code>ItemsBoxExtras_body.stl</code>)</a></p>

**Part: ItemsBoxExtras Lid**

.. stl:: ../_stl/boxes/root/ItemsBoxExtras_lid.stl?v=f025454e
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ItemsBoxExtras_lid.stl?v=f025454e" download="ItemsBoxExtras_lid.stl">⬇ Download ItemsBoxExtras Lid STL (<code>ItemsBoxExtras_lid.stl</code>)</a></p>

.. _box-root-marquisboxbottom:

MarquisBoxBottom
^^^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.CAP <box-type-cap>`
- **Outer Dimensions**: ``106.5 × 59.833 × 24.5 mm``
- **Packed Position**: ``(0, 98.5, 28)``
- **Compartments (1)**: ``Warriors`` (6 elements)

**Assembled Box (MarquisBoxBottom — Body + Lid)**

.. stl:: ../_stl/boxes/root/MarquisBoxBottom_body.stl?v=f5ea0af3,../_stl/boxes/root/MarquisBoxBottom_lid.stl?v=eb8a03ce
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/MarquisBoxBottom_body.stl?v=f5ea0af3" data-stl-combine="../_stl/boxes/root/MarquisBoxBottom_body.stl?v=f5ea0af3,../_stl/boxes/root/MarquisBoxBottom_lid.stl?v=eb8a03ce" download="MarquisBoxBottom_assembled.stl">⬇ Download Assembled MarquisBoxBottom STL (<code>MarquisBoxBottom_assembled.stl</code>)</a></p>

**Part: MarquisBoxBottom Body**

.. stl:: ../_stl/boxes/root/MarquisBoxBottom_body.stl?v=f5ea0af3
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/MarquisBoxBottom_body.stl?v=f5ea0af3" download="MarquisBoxBottom_body.stl">⬇ Download MarquisBoxBottom Body STL (<code>MarquisBoxBottom_body.stl</code>)</a></p>

**Part: MarquisBoxBottom Lid**

.. stl:: ../_stl/boxes/root/MarquisBoxBottom_lid.stl?v=eb8a03ce
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/MarquisBoxBottom_lid.stl?v=eb8a03ce" download="MarquisBoxBottom_lid.stl">⬇ Download MarquisBoxBottom Lid STL (<code>MarquisBoxBottom_lid.stl</code>)</a></p>

.. _box-root-marquisboxtop:

MarquisBoxTop
^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``106.5 × 59.833 × 14.5 mm``
- **Packed Position**: ``(0, 98.5, 52.5)``
- **Compartments (1)**: ``WoodAndBuildings`` (20 elements)

**Assembled Box (MarquisBoxTop — Body + Lid)**

.. stl:: ../_stl/boxes/root/MarquisBoxTop_body.stl?v=be7708f9,../_stl/boxes/root/MarquisBoxTop_lid.stl?v=0f1520ae
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/MarquisBoxTop_body.stl?v=be7708f9" data-stl-combine="../_stl/boxes/root/MarquisBoxTop_body.stl?v=be7708f9,../_stl/boxes/root/MarquisBoxTop_lid.stl?v=0f1520ae" download="MarquisBoxTop_assembled.stl">⬇ Download Assembled MarquisBoxTop STL (<code>MarquisBoxTop_assembled.stl</code>)</a></p>

**Part: MarquisBoxTop Body**

.. stl:: ../_stl/boxes/root/MarquisBoxTop_body.stl?v=be7708f9
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/MarquisBoxTop_body.stl?v=be7708f9" download="MarquisBoxTop_body.stl">⬇ Download MarquisBoxTop Body STL (<code>MarquisBoxTop_body.stl</code>)</a></p>

**Part: MarquisBoxTop Lid**

.. stl:: ../_stl/boxes/root/MarquisBoxTop_lid.stl?v=0f1520ae
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/MarquisBoxTop_lid.stl?v=0f1520ae" download="MarquisBoxTop_lid.stl">⬇ Download MarquisBoxTop Lid STL (<code>MarquisBoxTop_lid.stl</code>)</a></p>

.. _box-root-erieboxbottom:

ErieBoxBottom
^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.CAP <box-type-cap>`
- **Outer Dimensions**: ``106.5 × 59.833 × 24.5 mm``
- **Packed Position**: ``(106.5, 158.333, 28)``
- **Compartments (1)**: ``Warriors`` (4 elements)

**Assembled Box (ErieBoxBottom — Body + Lid)**

.. stl:: ../_stl/boxes/root/ErieBoxBottom_body.stl?v=41ce480e,../_stl/boxes/root/ErieBoxBottom_lid.stl?v=7a12e776
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/ErieBoxBottom_body.stl?v=41ce480e" data-stl-combine="../_stl/boxes/root/ErieBoxBottom_body.stl?v=41ce480e,../_stl/boxes/root/ErieBoxBottom_lid.stl?v=7a12e776" download="ErieBoxBottom_assembled.stl">⬇ Download Assembled ErieBoxBottom STL (<code>ErieBoxBottom_assembled.stl</code>)</a></p>

**Part: ErieBoxBottom Body**

.. stl:: ../_stl/boxes/root/ErieBoxBottom_body.stl?v=41ce480e
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ErieBoxBottom_body.stl?v=41ce480e" download="ErieBoxBottom_body.stl">⬇ Download ErieBoxBottom Body STL (<code>ErieBoxBottom_body.stl</code>)</a></p>

**Part: ErieBoxBottom Lid**

.. stl:: ../_stl/boxes/root/ErieBoxBottom_lid.stl?v=7a12e776
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ErieBoxBottom_lid.stl?v=7a12e776" download="ErieBoxBottom_lid.stl">⬇ Download ErieBoxBottom Lid STL (<code>ErieBoxBottom_lid.stl</code>)</a></p>

.. _box-root-erieboxtop:

ErieBoxTop
^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``53.25 × 59.833 × 14.5 mm``
- **Packed Position**: ``(53.25, 218.166, 52.5)``
- **Compartments (1)**: ``Roosts`` (6 elements)

**Assembled Box (ErieBoxTop — Body + Lid)**

.. stl:: ../_stl/boxes/root/ErieBoxTop_body.stl?v=190c427c,../_stl/boxes/root/ErieBoxTop_lid.stl?v=66b3006f
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/ErieBoxTop_body.stl?v=190c427c" data-stl-combine="../_stl/boxes/root/ErieBoxTop_body.stl?v=190c427c,../_stl/boxes/root/ErieBoxTop_lid.stl?v=66b3006f" download="ErieBoxTop_assembled.stl">⬇ Download Assembled ErieBoxTop STL (<code>ErieBoxTop_assembled.stl</code>)</a></p>

**Part: ErieBoxTop Body**

.. stl:: ../_stl/boxes/root/ErieBoxTop_body.stl?v=190c427c
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ErieBoxTop_body.stl?v=190c427c" download="ErieBoxTop_body.stl">⬇ Download ErieBoxTop Body STL (<code>ErieBoxTop_body.stl</code>)</a></p>

**Part: ErieBoxTop Lid**

.. stl:: ../_stl/boxes/root/ErieBoxTop_lid.stl?v=66b3006f
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/ErieBoxTop_lid.stl?v=66b3006f" download="ErieBoxTop_lid.stl">⬇ Download ErieBoxTop Lid STL (<code>ErieBoxTop_lid.stl</code>)</a></p>

.. _box-root-allianceboxbottom:

AllianceBoxBottom
^^^^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.CAP <box-type-cap>`
- **Outer Dimensions**: ``53.25 × 59.833 × 24.5 mm``
- **Packed Position**: ``(53.25, 218.166, 28)``
- **Compartments (1)**: ``Warriors`` (4 elements)

**Assembled Box (AllianceBoxBottom — Body + Lid)**

.. stl:: ../_stl/boxes/root/AllianceBoxBottom_body.stl?v=2da2e8a5,../_stl/boxes/root/AllianceBoxBottom_lid.stl?v=2208ea44
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/AllianceBoxBottom_body.stl?v=2da2e8a5" data-stl-combine="../_stl/boxes/root/AllianceBoxBottom_body.stl?v=2da2e8a5,../_stl/boxes/root/AllianceBoxBottom_lid.stl?v=2208ea44" download="AllianceBoxBottom_assembled.stl">⬇ Download Assembled AllianceBoxBottom STL (<code>AllianceBoxBottom_assembled.stl</code>)</a></p>

**Part: AllianceBoxBottom Body**

.. stl:: ../_stl/boxes/root/AllianceBoxBottom_body.stl?v=2da2e8a5
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/AllianceBoxBottom_body.stl?v=2da2e8a5" download="AllianceBoxBottom_body.stl">⬇ Download AllianceBoxBottom Body STL (<code>AllianceBoxBottom_body.stl</code>)</a></p>

**Part: AllianceBoxBottom Lid**

.. stl:: ../_stl/boxes/root/AllianceBoxBottom_lid.stl?v=2208ea44
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/AllianceBoxBottom_lid.stl?v=2208ea44" download="AllianceBoxBottom_lid.stl">⬇ Download AllianceBoxBottom Lid STL (<code>AllianceBoxBottom_lid.stl</code>)</a></p>

.. _box-root-allianceboxtop:

AllianceBoxTop
^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``53.25 × 59.833 × 14.5 mm``
- **Packed Position**: ``(106.5, 158.333, 52.5)``
- **Compartments (1)**: ``BasesAndSympathy`` (8 elements)

**Assembled Box (AllianceBoxTop — Body + Lid)**

.. stl:: ../_stl/boxes/root/AllianceBoxTop_body.stl?v=d8d205bf,../_stl/boxes/root/AllianceBoxTop_lid.stl?v=4c5b863a
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/AllianceBoxTop_body.stl?v=d8d205bf" data-stl-combine="../_stl/boxes/root/AllianceBoxTop_body.stl?v=d8d205bf,../_stl/boxes/root/AllianceBoxTop_lid.stl?v=4c5b863a" download="AllianceBoxTop_assembled.stl">⬇ Download Assembled AllianceBoxTop STL (<code>AllianceBoxTop_assembled.stl</code>)</a></p>

**Part: AllianceBoxTop Body**

.. stl:: ../_stl/boxes/root/AllianceBoxTop_body.stl?v=d8d205bf
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/AllianceBoxTop_body.stl?v=d8d205bf" download="AllianceBoxTop_body.stl">⬇ Download AllianceBoxTop Body STL (<code>AllianceBoxTop_body.stl</code>)</a></p>

**Part: AllianceBoxTop Lid**

.. stl:: ../_stl/boxes/root/AllianceBoxTop_lid.stl?v=4c5b863a
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/AllianceBoxTop_lid.stl?v=4c5b863a" download="AllianceBoxTop_lid.stl">⬇ Download AllianceBoxTop Lid STL (<code>AllianceBoxTop_lid.stl</code>)</a></p>

.. _box-root-lizardboxbottom:

LizardBoxBottom
^^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.CAP <box-type-cap>`
- **Outer Dimensions**: ``106.5 × 59.833 × 26.5 mm``
- **Packed Position**: ``(106.5, 98.5, 28)``
- **Compartments (1)**: ``Warriors`` (25 elements)

**Assembled Box (LizardBoxBottom — Body + Lid)**

.. stl:: ../_stl/boxes/root/LizardBoxBottom_body.stl?v=24eec34b,../_stl/boxes/root/LizardBoxBottom_lid.stl?v=42acf918
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/LizardBoxBottom_body.stl?v=24eec34b" data-stl-combine="../_stl/boxes/root/LizardBoxBottom_body.stl?v=24eec34b,../_stl/boxes/root/LizardBoxBottom_lid.stl?v=42acf918" download="LizardBoxBottom_assembled.stl">⬇ Download Assembled LizardBoxBottom STL (<code>LizardBoxBottom_assembled.stl</code>)</a></p>

**Part: LizardBoxBottom Body**

.. stl:: ../_stl/boxes/root/LizardBoxBottom_body.stl?v=24eec34b
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/LizardBoxBottom_body.stl?v=24eec34b" download="LizardBoxBottom_body.stl">⬇ Download LizardBoxBottom Body STL (<code>LizardBoxBottom_body.stl</code>)</a></p>

**Part: LizardBoxBottom Lid**

.. stl:: ../_stl/boxes/root/LizardBoxBottom_lid.stl?v=42acf918
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/LizardBoxBottom_lid.stl?v=42acf918" download="LizardBoxBottom_lid.stl">⬇ Download LizardBoxBottom Lid STL (<code>LizardBoxBottom_lid.stl</code>)</a></p>

.. _box-root-lizardboxtop:

LizardBoxTop
^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``79.875 × 59.833 × 12.5 mm``
- **Packed Position**: ``(106.5, 98.5, 54.5)``
- **Compartments (1)**: ``Gardens`` (12 elements)

**Assembled Box (LizardBoxTop — Body + Lid)**

.. stl:: ../_stl/boxes/root/LizardBoxTop_body.stl?v=00f0c07b,../_stl/boxes/root/LizardBoxTop_lid.stl?v=f3fc93d6
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/LizardBoxTop_body.stl?v=00f0c07b" data-stl-combine="../_stl/boxes/root/LizardBoxTop_body.stl?v=00f0c07b,../_stl/boxes/root/LizardBoxTop_lid.stl?v=f3fc93d6" download="LizardBoxTop_assembled.stl">⬇ Download Assembled LizardBoxTop STL (<code>LizardBoxTop_assembled.stl</code>)</a></p>

**Part: LizardBoxTop Body**

.. stl:: ../_stl/boxes/root/LizardBoxTop_body.stl?v=00f0c07b
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/LizardBoxTop_body.stl?v=00f0c07b" download="LizardBoxTop_body.stl">⬇ Download LizardBoxTop Body STL (<code>LizardBoxTop_body.stl</code>)</a></p>

**Part: LizardBoxTop Lid**

.. stl:: ../_stl/boxes/root/LizardBoxTop_lid.stl?v=f3fc93d6
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/LizardBoxTop_lid.stl?v=f3fc93d6" download="LizardBoxTop_lid.stl">⬇ Download LizardBoxTop Lid STL (<code>LizardBoxTop_lid.stl</code>)</a></p>

.. _box-root-riverfolkboxbottom:

RiverfolkBoxBottom
^^^^^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.CAP <box-type-cap>`
- **Outer Dimensions**: ``53.25 × 59.833 × 26.5 mm``
- **Packed Position**: ``(106.5, 218.166, 40.5)``
- **Compartments (1)**: ``Warriors`` (6 elements)

**Assembled Box (RiverfolkBoxBottom — Body + Lid)**

.. stl:: ../_stl/boxes/root/RiverfolkBoxBottom_body.stl?v=0c331c5d,../_stl/boxes/root/RiverfolkBoxBottom_lid.stl?v=c391c237
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/RiverfolkBoxBottom_body.stl?v=0c331c5d" data-stl-combine="../_stl/boxes/root/RiverfolkBoxBottom_body.stl?v=0c331c5d,../_stl/boxes/root/RiverfolkBoxBottom_lid.stl?v=c391c237" download="RiverfolkBoxBottom_assembled.stl">⬇ Download Assembled RiverfolkBoxBottom STL (<code>RiverfolkBoxBottom_assembled.stl</code>)</a></p>

**Part: RiverfolkBoxBottom Body**

.. stl:: ../_stl/boxes/root/RiverfolkBoxBottom_body.stl?v=0c331c5d
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/RiverfolkBoxBottom_body.stl?v=0c331c5d" download="RiverfolkBoxBottom_body.stl">⬇ Download RiverfolkBoxBottom Body STL (<code>RiverfolkBoxBottom_body.stl</code>)</a></p>

**Part: RiverfolkBoxBottom Lid**

.. stl:: ../_stl/boxes/root/RiverfolkBoxBottom_lid.stl?v=c391c237
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/RiverfolkBoxBottom_lid.stl?v=c391c237" download="RiverfolkBoxBottom_lid.stl">⬇ Download RiverfolkBoxBottom Lid STL (<code>RiverfolkBoxBottom_lid.stl</code>)</a></p>

.. _box-root-riverfolkboxtop:

RiverfolkBoxTop
^^^^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``79.875 × 59.833 × 12.5 mm``
- **Packed Position**: ``(106.5, 218.166, 28)``
- **Compartments (1)**: ``TradePosts`` (14 elements)

**Assembled Box (RiverfolkBoxTop — Body + Lid)**

.. stl:: ../_stl/boxes/root/RiverfolkBoxTop_body.stl?v=ccfed6ed,../_stl/boxes/root/RiverfolkBoxTop_lid.stl?v=67cdc71d
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/RiverfolkBoxTop_body.stl?v=ccfed6ed" data-stl-combine="../_stl/boxes/root/RiverfolkBoxTop_body.stl?v=ccfed6ed,../_stl/boxes/root/RiverfolkBoxTop_lid.stl?v=67cdc71d" download="RiverfolkBoxTop_assembled.stl">⬇ Download Assembled RiverfolkBoxTop STL (<code>RiverfolkBoxTop_assembled.stl</code>)</a></p>

**Part: RiverfolkBoxTop Body**

.. stl:: ../_stl/boxes/root/RiverfolkBoxTop_body.stl?v=ccfed6ed
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/RiverfolkBoxTop_body.stl?v=ccfed6ed" download="RiverfolkBoxTop_body.stl">⬇ Download RiverfolkBoxTop Body STL (<code>RiverfolkBoxTop_body.stl</code>)</a></p>

**Part: RiverfolkBoxTop Lid**

.. stl:: ../_stl/boxes/root/RiverfolkBoxTop_lid.stl?v=67cdc71d
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/RiverfolkBoxTop_lid.stl?v=67cdc71d" download="RiverfolkBoxTop_lid.stl">⬇ Download RiverfolkBoxTop Lid STL (<code>RiverfolkBoxTop_lid.stl</code>)</a></p>

.. _box-root-vagabondbox:

VagabondBox
^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``53.25 × 59.833 × 19.5 mm``
- **Packed Position**: ``(159.75, 0, 28)``
- **Stackable Mode**: ``StackableMode.PYRAMIDS``
- **Stacking Order Key**: bottom ``flat (bottom of stack)``, top ``pyramids=2``
- **Compartments (1)**: ``ItemsAndScore`` (7 elements)

**Assembled Box (VagabondBox — Body + Lid)**

.. stl:: ../_stl/boxes/root/VagabondBox_body.stl?v=8857fc1a,../_stl/boxes/root/VagabondBox_lid.stl?v=c3a127d4
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/VagabondBox_body.stl?v=8857fc1a" data-stl-combine="../_stl/boxes/root/VagabondBox_body.stl?v=8857fc1a,../_stl/boxes/root/VagabondBox_lid.stl?v=c3a127d4" download="VagabondBox_assembled.stl">⬇ Download Assembled VagabondBox STL (<code>VagabondBox_assembled.stl</code>)</a></p>

**Part: VagabondBox Body**

.. stl:: ../_stl/boxes/root/VagabondBox_body.stl?v=8857fc1a
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/VagabondBox_body.stl?v=8857fc1a" download="VagabondBox_body.stl">⬇ Download VagabondBox Body STL (<code>VagabondBox_body.stl</code>)</a></p>

**Part: VagabondBox Lid**

.. stl:: ../_stl/boxes/root/VagabondBox_lid.stl?v=c3a127d4
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/VagabondBox_lid.stl?v=c3a127d4" download="VagabondBox_lid.stl">⬇ Download VagabondBox Lid STL (<code>VagabondBox_lid.stl</code>)</a></p>

.. _box-root-vagabondbox2:

VagabondBox2
^^^^^^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``53.25 × 59.833 × 19.5 mm``
- **Packed Position**: ``(159.75, 0, 47.5)``
- **Stackable Mode**: ``StackableMode.PYRAMIDS``
- **Stacking Order Key**: bottom ``pyramids=2``, top ``flat (top of stack)``
- **Compartments (1)**: ``ItemsAndScore`` (7 elements)

**Assembled Box (VagabondBox2 — Body + Lid)**

.. stl:: ../_stl/boxes/root/VagabondBox2_body.stl?v=aab715d8,../_stl/boxes/root/VagabondBox2_lid.stl?v=38de3a0f
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/VagabondBox2_body.stl?v=aab715d8" data-stl-combine="../_stl/boxes/root/VagabondBox2_body.stl?v=aab715d8,../_stl/boxes/root/VagabondBox2_lid.stl?v=38de3a0f" download="VagabondBox2_assembled.stl">⬇ Download Assembled VagabondBox2 STL (<code>VagabondBox2_assembled.stl</code>)</a></p>

**Part: VagabondBox2 Body**

.. stl:: ../_stl/boxes/root/VagabondBox2_body.stl?v=aab715d8
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/VagabondBox2_body.stl?v=aab715d8" download="VagabondBox2_body.stl">⬇ Download VagabondBox2 Body STL (<code>VagabondBox2_body.stl</code>)</a></p>

**Part: VagabondBox2 Lid**

.. stl:: ../_stl/boxes/root/VagabondBox2_lid.stl?v=38de3a0f
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/VagabondBox2_lid.stl?v=38de3a0f" download="VagabondBox2_lid.stl">⬇ Download VagabondBox2 Lid STL (<code>VagabondBox2_lid.stl</code>)</a></p>

.. _box-root-dicebox:

DiceBox
^^^^^^^

- **Box Type**: :ref:`BoxType.SLIDING <box-type-sliding>`
- **Outer Dimensions**: ``53.25 × 59.833 × 39 mm``
- **Packed Position**: ``(53.25, 158.333, 28)``
- **Compartments (1)**: ``Dice`` (2 elements)

**Assembled Box (DiceBox — Body + Lid)**

.. stl:: ../_stl/boxes/root/DiceBox_body.stl?v=b10b9331,../_stl/boxes/root/DiceBox_lid.stl?v=c988c591
   :height: 320px

.. raw:: html

   <p><a href="../_stl/boxes/root/DiceBox_body.stl?v=b10b9331" data-stl-combine="../_stl/boxes/root/DiceBox_body.stl?v=b10b9331,../_stl/boxes/root/DiceBox_lid.stl?v=c988c591" download="DiceBox_assembled.stl">⬇ Download Assembled DiceBox STL (<code>DiceBox_assembled.stl</code>)</a></p>

**Part: DiceBox Body**

.. stl:: ../_stl/boxes/root/DiceBox_body.stl?v=b10b9331
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/DiceBox_body.stl?v=b10b9331" download="DiceBox_body.stl">⬇ Download DiceBox Body STL (<code>DiceBox_body.stl</code>)</a></p>

**Part: DiceBox Lid**

.. stl:: ../_stl/boxes/root/DiceBox_lid.stl?v=c988c591
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/DiceBox_lid.stl?v=c988c591" download="DiceBox_lid.stl">⬇ Download DiceBox Lid STL (<code>DiceBox_lid.stl</code>)</a></p>

Spacer Trays
------------

.. _spacer-root-spacer_1:

spacer_1
^^^^^^^^

- **Type**: :ref:`BoxType.NO_LID <box-type-no-lid>` filler spacer tray
- **Outer Dimensions**: ``54.25 × 119.667 × 14.5 mm``
- **Packed Position**: ``(159.75, 158.333, 52.5)``

.. stl:: ../_stl/boxes/root/spacer_1.stl?v=4d29cdda
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/spacer_1.stl?v=4d29cdda" download="spacer_1.stl">⬇ Download spacer_1 STL (<code>spacer_1.stl</code>)</a></p>

.. _spacer-root-spacer_2:

spacer_2
^^^^^^^^

- **Type**: :ref:`BoxType.NO_LID <box-type-no-lid>` filler spacer tray
- **Outer Dimensions**: ``54.25 × 38.667 × 39 mm``
- **Packed Position**: ``(159.75, 59.833, 28)``

.. stl:: ../_stl/boxes/root/spacer_2.stl?v=b7ab3da6
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/spacer_2.stl?v=b7ab3da6" download="spacer_2.stl">⬇ Download spacer_2 STL (<code>spacer_2.stl</code>)</a></p>

.. _spacer-root-spacer_3:

spacer_3
^^^^^^^^

- **Type**: :ref:`BoxType.NO_LID <box-type-no-lid>` filler spacer tray
- **Outer Dimensions**: ``27.625 × 59.834 × 24.5 mm``
- **Packed Position**: ``(186.375, 218.166, 28)``

.. stl:: ../_stl/boxes/root/spacer_3.stl?v=b0608e81
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/spacer_3.stl?v=b0608e81" download="spacer_3.stl">⬇ Download spacer_3 STL (<code>spacer_3.stl</code>)</a></p>

.. _spacer-root-spacer_4:

spacer_4
^^^^^^^^

- **Type**: :ref:`BoxType.NO_LID <box-type-no-lid>` filler spacer tray
- **Outer Dimensions**: ``53.25 × 16.167 × 39 mm``
- **Packed Position**: ``(0, 261.833, 28)``

.. stl:: ../_stl/boxes/root/spacer_4.stl?v=925c8932
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/spacer_4.stl?v=925c8932" download="spacer_4.stl">⬇ Download spacer_4 STL (<code>spacer_4.stl</code>)</a></p>

.. _spacer-root-spacer_5:

spacer_5
^^^^^^^^

- **Type**: :ref:`BoxType.NO_LID <box-type-no-lid>` filler spacer tray
- **Outer Dimensions**: ``27.625 × 59.833 × 12.5 mm``
- **Packed Position**: ``(186.375, 98.5, 54.5)``

.. stl:: ../_stl/boxes/root/spacer_5.stl?v=ef290ad5
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/spacer_5.stl?v=ef290ad5" download="spacer_5.stl">⬇ Download spacer_5 STL (<code>spacer_5.stl</code>)</a></p>

.. _spacer-root-spacer_6:

spacer_6
^^^^^^^^

- **Type**: :ref:`BoxType.NO_LID <box-type-no-lid>` filler spacer tray
- **Outer Dimensions**: ``26.625 × 59.834 × 12 mm``
- **Packed Position**: ``(159.75, 218.166, 40.5)``

.. stl:: ../_stl/boxes/root/spacer_6.stl?v=fa47bc5e
   :height: 280px

.. raw:: html

   <p><a href="../_stl/boxes/root/spacer_6.stl?v=fa47bc5e" download="spacer_6.stl">⬇ Download spacer_6 STL (<code>spacer_6.stl</code>)</a></p>
