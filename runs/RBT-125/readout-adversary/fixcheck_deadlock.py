"""#446 FIX-CHECK (c): can food placement deadlock, or silently place food in reach, when the clearance can't be met?

_food_spot tries 256 draws, then returns the LAST draw unchecked.  Worst case: the clearance zone covers the whole
food disc (a food radius smaller than clearance around a robot at the centre), under root/surface/root on the fixed
tree.  Printed: wall time of set_food_seed + a season (no hang), and how many placed items violate the clearance
(the fallback's cost), for food radius 0.5 (impossible), 1.2 (tight) and 3.0 (committed).

    PYTHONPATH=<tree> python fixcheck_deadlock.py <tree>
"""
import json, os, sys, time
from dataclasses import replace
import numpy as np
T = os.path.abspath(sys.argv[1]); sys.path.insert(0, T)
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig, Simulation  # noqa: E402
from rabbitstew.world import Spawn  # noqa: E402
g = Genotype.load(os.path.join(T, "runs/RBT-19/P-801/conventional/best_gen0590.json"))
c0 = SimConfig.from_dict(json.load(open(os.path.join(T, "runs/RBT-125/gate/worlds/U-G0/config.json")))["sim"])
print("| food radius (m) | rule | set_food_seed + 15 s season (s) | items placed | placed inside clearance (surface dist) | items eaten |")
print("|---|---|---|---|---|---|")
for R in (0.5, 1.2, 3.0):
    for kw in ({"eat_from": "root", "eat_rule": "surface"}, {"eat_rule": "surface", "clear_from": "geoms"}, {}):
        cfg = replace(c0, food=replace(c0.food, radius=R, **kw))
        t = time.time()
        sim = Simulation([g], cfg, spawns=[Spawn(position=(0.0, 0.0, 0.0), yaw=0.0)])
        sim.set_food_seed(5)
        eat = sim._eat_geoms[0]
        d0 = sim._surface_distance(eat, sim.food_pos) if cfg.food.eat_rule == "surface" else np.linalg.norm(sim.food_pos - sim._robot_positions()[0], axis=1)
        bad = int(np.sum(d0 < cfg.food.clearance))
        sim.run()
        rule = "/".join([cfg.food.eat_from, cfg.food.eat_rule, cfg.food.clear_from])
        print(f"| {R} | {rule} | {time.time() - t:.1f} | {len(d0)} | {bad} | {int(sim.food_eaten[0])} |", flush=True)
