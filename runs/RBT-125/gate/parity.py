"""RBT-125 gate: tree parity (the coordinator's ruling on #418).  The gate runs on #414's fixed tree; every §A cell uses
the legacy eating rules, so the fixed tree must compute each of them bit for bit as 0ec395f (the tree the adversary
checked) does.  Adapted from runs/RBT-125/adversary/probe_tree_parity.py, with one digest PER CELL and the cells read
from one worlds/ directory for both trees.

Run under each tree's PYTHONPATH:   PYTHONPATH=<tree> python parity.py <tree> <worlds dir>
Prints one line per cell: its digest of qpos, work, food_eaten and food_pos after every season -- RBT-19 P-801's g590
Pioneer with and without the a = 6 motif, 3 seeds, plus the patched rotated decoy at a = 6 in the PW cells.
"""
import hashlib
import json
import os
import sys

import numpy as np

TREE, WORLDS = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
sys.argv = sys.argv[:1]
sys.path.insert(0, TREE)
sys.path.insert(0, os.path.join(TREE, "runs", "RBT-125", "gate"))
import prize_gate  # noqa: E402

import rabbitstew  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout  # noqa: E402

assert os.path.abspath(rabbitstew.__file__).startswith(TREE), rabbitstew.__file__
rp = prize_gate.rp
BODY = os.path.join(TREE, "runs", "RBT-19", "P-801", "conventional", "best_gen0590.json")
for cell in sorted(os.listdir(WORLDS)):
    cfg = SimConfig.from_dict(json.load(open(os.path.join(WORLDS, cell, "config.json")))["sim"])
    h = hashlib.sha256()
    for w in (0.0, 3.0):
        for seed in (7000, 7001, 7002):
            for decoy in ((False, True) if cell.startswith("PW") and w else (False,)):
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
    print(f"{cell} {h.hexdigest()}", flush=True)
