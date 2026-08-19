# SPDX-License-Identifier: Apache-2.0
from pyboxbuilder import BoxType, Project, ScoopSide
from pybosl2 import cuboid

project = Project("A", game_box_size=(400, 200, 60), generate_spacers=False)
box = project.box(BoxType.NO_LID, "no_lid", size=(100, 80, 40), position=(0, 0, 0),
                  auto_finger_holes=False)
project._resolve_final_layout()
plain = project._build_box_solids(box)[0]
box.finger_hole(ScoopSide.FRONT)
project._resolve_final_layout()
holed = project._build_box_solids(box)[0]

removed = plain - holed
# Compute bounding box / size manually using pybosl2 or python
from pyboxbuilder.rounding import max_radius
# Print size and position
print(f"removed position: {removed.position if hasattr(removed, 'position') else 'no position'}")
print(f"removed size: {removed.size if hasattr(removed, 'size') else 'no size'}")
