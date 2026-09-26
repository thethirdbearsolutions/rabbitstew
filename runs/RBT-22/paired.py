"""Paired re-analysis: the lesion modes share their seeds, so the difference is paired."""
import json, sys, numpy as np
from dataclasses import replace
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize
run, kind, gen, n = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
def trial(seed, mode):
    c = replace(cfg, random_start=True)
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed)); sim.set_food_seed(seed)
    b = sim.brains[0]; ph = synthesize(g, c.synthesis)
    for i, ui in enumerate(ph.units):
        if mode == "no_food" and ui.unit.kind == "sensor" and ui.unit.source in ("food", "agent"): b.W[:, i] = 0
    for _ in range(int(round(c.duration / c.control_dt))): sim.step()
    return float(sim.food_eaten[0])
seeds = [7000 + s for s in range(n)]
a = np.array([trial(s, "intact") for s in seeds])
b_ = np.array([trial(s, "no_food") for s in seeds])
d = a - b_
se_unpaired = np.sqrt(a.var(ddof=1)/n + b_.var(ddof=1)/n)
se_paired = d.std(ddof=1) / np.sqrt(n)
print(f"{kind} g{gen}, n={n} paired seeds")
print(f"  intact  {a.mean():.3f}  (own SE {a.std(ddof=1)/np.sqrt(n):.3f})")
print(f"  no_food {b_.mean():.3f}  (own SE {b_.std(ddof=1)/np.sqrt(n):.3f})")
print(f"  difference {d.mean():+.3f}  unpaired SE {se_unpaired:.3f} (t={d.mean()/se_unpaired:.2f})"
      f"  PAIRED SE {se_paired:.3f} (t={d.mean()/se_paired if se_paired else float('nan'):.2f})")
print(f"  per-seed differences: {list(d.astype(int))}")
print(f"  seeds where the lesion changed nothing: {int((d==0).sum())} of {n}")
