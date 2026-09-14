"""Scratch copy of scripts/forage_probe.py for RBT-16 (W4, depleting arena).  Same trials (each best
ALONE in the arena on fresh seeds, so depletion is by that robot only), plus the split of items eaten
in the first half vs the second half of the season from sim.food_events ticks.  Not a library change."""
import json, sys, numpy as np
from dataclasses import replace
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize
run = sys.argv[1]; gens = [int(x) for x in sys.argv[2].split(",")]; n = int(sys.argv[3]) if len(sys.argv) > 3 else 6
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
def trial(g, seed, mode):
    c = replace(cfg, random_start=True)
    sp = spawn_layout(1, c, seed)
    sim = Simulation([g], c, spawns=sp); sim.set_food_seed(seed)
    b = sim.brains[0]; ph = synthesize(g, c.synthesis)
    for i, ui in enumerate(ph.units):
        k = ui.unit.kind
        if mode == "no_food" and k == "sensor" and ui.unit.source in ("food", "agent"): b.W[:, i] = 0
        elif mode == "no_env" and k == "sensor" and ui.unit.source != "oscillator": b.W[:, i] = 0
        elif mode == "no_local" and ui.part is not None and k != "effector": b.W[i, :] = 0; b.W[:, i] = 0; b.bias[i] = 0
    p0 = sim.center_of_mass(0)[:2].copy(); path = 0.0; last = p0.copy()
    steps = int(round(c.duration / c.control_dt))
    for t in range(steps):
        sim.step()
        if t % 10 == 0:
            p = sim.center_of_mass(0)[:2]; path += float(np.linalg.norm(p - last)); last = p.copy()
    half = steps // 2
    first = sum(1 for (tick, ri, x, y) in sim.food_events if tick <= half)
    second = len(sim.food_events) - first
    return {"food": float(sim.food_eaten[0]), "first_half": float(first), "second_half": float(second), "disp": float(np.linalg.norm(sim.center_of_mass(0)[:2] - p0)), "path": path, "work": float(sim.work[0]) / 1000}
out = {}
for kind in ("holistic", "conventional"):
    for gen in gens:
        try: g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
        except FileNotFoundError: continue
        ph = synthesize(g, cfg.synthesis)
        srcs = sorted({u.unit.source for u in ph.units if u.unit.kind == "sensor"})
        row = {}
        for mode in ("intact", "no_food", "no_env", "no_local"):
            rs = [trial(g, 7000 + s, mode) for s in range(n)]
            row[mode] = {k: float(np.mean([r[k] for r in rs])) for k in rs[0]}
        out[f"{kind}:{gen}"] = {"parts": len(ph.parts), "units": len(ph.units), "sensors": srcs, "modes": row}
        print(f"{kind:12s} g{gen:3d} parts {len(ph.parts):2d} units {len(ph.units):3d} sensors {srcs}", flush=True)
        print("     " + "  ".join(f"{m}: food {row[m]['food']:.2f} ({row[m]['first_half']:.2f}+{row[m]['second_half']:.2f}) disp {row[m]['disp']:.2f} path {row[m]['path']:.1f} work {row[m]['work']:.1f}kJ" for m in row), flush=True)
json.dump(out, open(f"{run}/../probe_split.json", "w"), indent=1)
