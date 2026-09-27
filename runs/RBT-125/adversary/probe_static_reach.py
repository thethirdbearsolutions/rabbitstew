"""RBT-125 adversary: does clear_from = geoms close the static-reach leak under eat_rule = surface?

clear_from = geoms keeps new items `clearance` (0.8 m) from every geom CENTRE; surface eating eats within eat_radius
(0.35 m) of a geom's SURFACE.  A limb longer than about 2 x (0.8 - 0.35) has surface within reach of spots that are
clear of its centre.  A motors-off rod (side_effects.py's rod with the effector bias 0) cannot move, so every item it
eats is static reach.  20 seasons (seeds 2131..2150), U-G0's food block, flat terrain, the committed regrowth.
"""
import json, os, sys
from dataclasses import replace
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)
from rabbitstew.genotype import Brain, Connection, Effector, Genotype, JointType, Node, Segment, Shape
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout


def rod(a):
    arm = Segment(Shape.BOX, (float(a), 1.0, 1.0), Brain(units=[Effector(dof=0, bias=0.0)]))
    conn = Connection(child=1, position=(1.0, 0.0, 0.0), scale=1.0, joint_type=JointType.HINGE, axis=(0.0, 0.0, 1.0), joint_limit=None)
    return Genotype(nodes=[Node(Segment(Shape.BOX, (1.0, 1.0, 1.0), Brain(units=[])), [conn]), Node(arm)], name="rod")


base = SimConfig.from_dict(json.load(open(os.path.join(ROOT, "runs/RBT-125/gate/worlds/U-G0/config.json")))["sim"])
base = replace(base, world=replace(base.world, terrain="flat"))
print("| arm (m) | eat_rule | clear_from | items per season (motors off, 20 seasons) | seasons with any |")
print("|---|---|---|---|---|")
for L in (0.45, 1.5, 3.0, 6.46):
    a = (L / 0.3) ** 1.5
    for rule, clear in (("centre", "root"), ("centre", "geoms"), ("surface", "root"), ("surface", "geoms")):
        cfg = replace(base, food=replace(base.food, eat_rule=rule, clear_from=clear))
        got = []
        for seed in range(2131, 2151):
            sim = Simulation([rod(a)], cfg, spawns=spawn_layout(1, cfg, seed))
            sim.set_food_seed(seed)
            sim.run()
            got.append(float(sim.food_eaten[0]))
        got = np.array(got)
        print(f"| {L} | {rule} | {clear} | {got.mean():.2f} | {np.mean(got > 0):.2f} |", flush=True)
