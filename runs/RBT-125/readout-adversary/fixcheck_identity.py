"""#446 FIX-CHECK (b): per eating rule x clearance, a digest of fixture seasons, to compare two trees byte for byte.

Fixture: a committed Pioneer (RBT-19 P-801 g590) and RBT-113's seed-1 generation-0 holistic founder 0, in the U-G0
and PW-G2.5 gate worlds, 3 seeds each (regrowth draws food spots through _food_spot, so every rule's clearance path
is exercised).  Digest of qpos, work, food_eaten, food_pos, food_spots after each 15 s season.

    PYTHONPATH=<tree> python fixcheck_identity.py <tree>
"""
import hashlib, json, os, sys
from dataclasses import replace
import numpy as np
T = os.path.abspath(sys.argv[1]); sys.path.insert(0, T); sys.path.insert(0, os.path.join(T, "runs/RBT-113"))
import rabbitstew  # noqa: E402
assert os.path.dirname(rabbitstew.__file__).startswith(T), rabbitstew.__file__
import world as rbt113  # noqa: E402
from rabbitstew.evolution import HOLISTIC, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout  # noqa: E402

RULES = {"committed any/centre/root": {}, "root/centre/root": {"eat_from": "root"}, "sensor/centre/root": {"eat_from": "sensor"},
         "any/centre/geoms": {"clear_from": "geoms"}, "any/surface/geoms": {"eat_rule": "surface", "clear_from": "geoms"},
         "any/surface/root": {"eat_rule": "surface"}, "root/surface/root": {"eat_from": "root", "eat_rule": "surface"}}
bodies = {"pioneer": Genotype.load(os.path.join(T, "runs/RBT-19/P-801/conventional/best_gen0590.json"))}
m = initial_population(HOLISTIC, rbt113.evolution_config("U", "", seed=1), spawn_streams(1)[HOLISTIC]).members[0]
bodies["holistic"] = m.genotype if hasattr(m, "genotype") else m
for name, kw in RULES.items():
    h = hashlib.sha256()
    for cell in ("U-G0", "PW-G2.5"):
        c0 = SimConfig.from_dict(json.load(open(os.path.join(T, "runs/RBT-125/gate/worlds", cell, "config.json")))["sim"])
        cfg = replace(c0, food=replace(c0.food, **kw), random_start=True)
        for b in bodies.values():
            for seed in (900, 901, 902):
                sim = Simulation([b], cfg, spawns=spawn_layout(1, cfg, seed))
                sim.set_food_seed(seed)
                sim.run()
                for a in (sim.data.qpos, sim.work, sim.food_eaten, sim.food_pos, sim.food_spots):
                    h.update(np.ascontiguousarray(a).tobytes())
    print(f"{name:22s} {h.hexdigest()[:16]}", flush=True)
