"""How much do random robots eat?  Sets the basal cost so that living is possible but not free.
usage: calibrate_food.py N_HOLISTIC N_PIONEER"""
import sys, json, numpy as np
from rabbitstew.genotype import BrainVocabulary, random_genotype
from rabbitstew.fixed import pioneer_genotype
from rabbitstew.simulation import FoodConfig, SimConfig, SynthesisConfig, run_group
nh, npi = int(sys.argv[1]), int(sys.argv[2])
v = BrainVocabulary.named("foraging")
cfg = SimConfig(duration=15.0, random_start=True, score="food", synthesis=SynthesisConfig(mass_budget=15.34), food=FoodConfig(items=12, radius=3.0, eat_radius=0.35, decay=1.0, work_cost=0.0, clearance=0.8))
rng = np.random.default_rng(0)
hol = [random_genotype(rng, name=f"h{i}", vocab=v) for i in range(nh)]
pio = [pioneer_genotype(rng, hidden=6, rich=True, sources=v.sensor_sources, name=f"p{i}") for i in range(npi)]
def groups(gs, size=4):
    return [(gs[i:i+size], 100 + i) for i in range(0, len(gs), size)]
out = {}
for label, gs in (("holistic", hol), ("pioneer", pio)):
    rows = [r for grp in groups(gs) for r in run_group(grp[0], cfg, grp[1])]
    food = np.array([r["food"] for r in rows]); work = np.array([r["work"] for r in rows]) / 1000.0; path = np.array([r["path"] for r in rows])
    out[label] = {"food": food.tolist(), "work_kJ": work.tolist(), "path": path.tolist()}
    q = lambda a: " ".join(f"{np.percentile(a, p):.2f}" for p in (10, 25, 50, 75, 90))
    print(f"{label:9s} n={len(rows)}  food eaten p10/25/50/75/90: {q(food)}   frac>0: {(food>0).mean():.2f}   work kJ: {q(work)}   displacement m: {q(path)}", flush=True)
json.dump(out, open("calibrate_food.json", "w"))
