"""RBT-125 adversary: do the gate's pinned tree (0ec395f) and PR #414's head (c40ecd5, + RBT-120's motor budget) compute
the gate's seasons bit for bit?  Run under each tree's PYTHONPATH; prints a digest of qpos, work, food_eaten and
food_pos after every season: one committed Pioneer (RBT-19 P-801 g590) with and without the a = 6 motif, in every
registered world cell, 3 seeds, plus the rotated decoy (patched) at PW-G2.5.

    PYTHONPATH=<tree> python probe_tree_parity.py <tree>
"""
import hashlib, json, os, sys
import numpy as np
TREE = sys.argv[1]
sys.path.insert(0, TREE); sys.path.insert(0, os.path.join(TREE, "runs/RBT-125/gate"))
import prize_gate  # noqa
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
import rabbitstew
assert rabbitstew.__file__.startswith(TREE), rabbitstew.__file__
rp = prize_gate.rp
HERE = os.path.dirname(os.path.abspath(__file__))
BODY = os.path.join(HERE, "..", "..", "RBT-19/P-801/conventional/best_gen0590.json")
h = hashlib.sha256()
for cell in sorted(os.listdir(os.path.join(TREE, "runs/RBT-125/gate/worlds"))):
    cfg = SimConfig.from_dict(json.load(open(os.path.join(TREE, "runs/RBT-125/gate/worlds", cell, "config.json")))["sim"])
    for w in (0.0, 3.0):
        for seed in (7000, 7001, 7002):
            for decoy in ((False, True) if cell == "PW-G2.5" and w else (False,)):
                g = Genotype.load(BODY)
                if w:
                    g = rp.routed.install(g, w, sign=-1.0)
                sim = (rp.mech.RotatedSmell if decoy else Simulation)([g], cfg, spawns=spawn_layout(1, cfg, seed))
                if decoy:
                    sim._rot = 1.234
                sim.set_food_seed(seed)
                sim.run()
                for a in (sim.data.qpos, sim.work, sim.food_eaten, sim.food_pos):
                    h.update(np.ascontiguousarray(a).tobytes())
print(f"{h.hexdigest()}  ({len(os.listdir(os.path.join(TREE, 'runs/RBT-125/gate/worlds')))} cells x w{{0,3}} x 3 seeds + decoy)")
