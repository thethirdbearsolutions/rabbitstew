"""RBT-90 part 2 adversary, probe P: is each champion's path a function of its spawn alone?

The gait null replays a bout's recorded path against other layouts the world could have dealt.  If
the path does not depend on where the food is, then the real layout is just one more draw from the
null's own distribution, E[items - null] = 0 exactly, and "does not beat its own gait" holds by
construction, whatever the null's power.  This runs each champion from one spawn under two different
food layouts (set_food_seed) and compares the centre-of-mass path tick by tick.

usage: path_invariance.py BULK_ROOT [SEED ...]
"""
import json
import sys
from dataclasses import replace

import numpy as np

from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout

SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
SPAWNS = (8000, 8001, 8002, 8003)
OTHER = 777777  # a second food seed, far from any the lab uses


def path(g, cfg, spawn, food_seed):
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, spawn))
    sim.set_food_seed(food_seed)
    ps = []
    for _ in range(int(round(cfg.duration / cfg.control_dt))):
        sim.step()
        ps.append(sim.center_of_mass(0)[:2].copy())
    return np.array(ps), float(sim.food_eaten[0])


if __name__ == "__main__":
    bulk = sys.argv[1]
    seeds = [int(a) for a in sys.argv[2:]] or SEEDS
    print("max |COM difference| (m) between the same spawn under its own layout and under another; items eaten in each")
    for seed in seeds:
        run = f"{bulk}/forage-{seed}"
        cfg = replace(SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"]), random_start=True)
        g = Genotype.load(f"{run}/holistic/best_gen0590.json")
        cells, diffs = [], []
        for sp in SPAWNS:
            a, fa = path(g, cfg, sp, sp)
            b, fb = path(g, cfg, sp, OTHER + sp)
            diffs.append(float(np.abs(a - b).max()))
            cells.append(f"{diffs[-1]:.2e} ({fa:.0f}/{fb:.0f})")
        verdict = "LAYOUT-BLIND (path identical)" if max(diffs) == 0.0 else "path depends on the layout"
        print(f"{seed:5d}  " + "  ".join(cells) + f"   -> {verdict}", flush=True)
