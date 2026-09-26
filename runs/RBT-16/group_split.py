"""Scratch for RBT-16: four copies of a best share one depleting arena (24 items, no regrowth), as in
the ecology, on fresh seeds.  Items eaten by the group and by robot 0, split first half / second half
of the season, intact and with robot 0's food/agent sensors blanked.  Not a library change."""
import json, sys, numpy as np
from dataclasses import replace
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize
run = sys.argv[1]; gens = [int(x) for x in sys.argv[2].split(",")]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 8
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
def trial(g, seed, mode):
    c = replace(cfg, random_start=True)
    sim = Simulation([g] * 4, c, spawns=spawn_layout(4, c, seed)); sim.set_food_seed(seed)
    ph = synthesize(g, c.synthesis)
    if mode == "no_food":
        b = sim.brains[0]
        for i, ui in enumerate(ph.units):
            if ui.unit.kind == "sensor" and ui.unit.source in ("food", "agent"): b.W[:, i] = 0
    steps = int(round(c.duration / c.control_dt)); half = steps // 2
    for t in range(steps): sim.step()
    ev = sim.food_events
    return {"group_first": sum(1 for e in ev if e[0] <= half), "group_second": sum(1 for e in ev if e[0] > half),
            "r0_first": sum(1 for e in ev if e[0] <= half and e[1] == 0), "r0_second": sum(1 for e in ev if e[0] > half and e[1] == 0),
            "r0_work": float(sim.work[0]) / 1000}
for kind in ("holistic", "conventional"):
    for gen in gens:
        g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
        for mode in ("intact", "no_food"):
            rs = [trial(g, 7000 + s, mode) for s in range(n)]
            m = {k: float(np.mean([r[k] for r in rs])) for k in rs[0]}
            print(f"{kind:12s} g{gen:3d} x4 {mode:8s} group {m['group_first']+m['group_second']:.2f}/24 ({m['group_first']:.2f}+{m['group_second']:.2f})  robot0 {m['r0_first']+m['r0_second']:.2f} ({m['r0_first']:.2f}+{m['r0_second']:.2f}) work {m['r0_work']:.1f}kJ", flush=True)
