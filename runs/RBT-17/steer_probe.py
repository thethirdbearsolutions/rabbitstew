"""Compass or brake?  A best alone in the arena on fresh seeds: items eaten, path, fraction of the
season its centre of mass spends inside the food disc, and its mean distance to the nearest food
item, intact and with the food, agent, both noses, or every environmental sensor blanked.
Usage: python steer_probe.py RUN KIND GEN [SEEDS=8]"""
import json, sys, numpy as np
from dataclasses import replace
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize
run, kind, gen = sys.argv[1], sys.argv[2], int(sys.argv[3]); n = int(sys.argv[4]) if len(sys.argv) > 4 else 8
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
ph = synthesize(g, cfg.synthesis)
def trial(seed, mode):
    c = replace(cfg, random_start=True)
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed)); sim.set_food_seed(seed)
    b = sim.brains[0]
    for i, ui in enumerate(ph.units):
        if ui.unit.kind != "sensor": continue
        s = ui.unit.source
        if (mode == "no_food" and s == "food") or (mode == "no_agent" and s == "agent") or (mode == "no_noses" and s in ("food", "agent")) or (mode == "no_env" and s != "oscillator"):
            b.W[:, i] = 0
    steps = int(round(c.duration / c.control_dt)); inside = 0; near = []; near_in = []; path = 0.0
    last = sim.center_of_mass(0)[:2].copy()
    for t in range(steps):
        sim.step()
        if t % 10 == 0:
            p = sim.center_of_mass(0)[:2]; path += float(np.linalg.norm(p - last)); last = p.copy()
            inside += float(np.linalg.norm(p) < c.food.radius)
            live = sim.food_pos[np.abs(sim.food_pos).max(axis=1) < 1e5]
            if len(live):
                dn = float(np.linalg.norm(live - p, axis=1).min()); near.append(dn)
                if np.linalg.norm(p) < c.food.radius: near_in.append(dn)
    return {"food": float(sim.food_eaten[0]), "path": path, "in_disc": inside / (steps // 10 + 1), "near": float(np.mean(near)), "near_in": float(np.mean(near_in)) if near_in else float("nan"), "work": float(sim.work[0]) / 1000}
print(f"{kind} g{gen}: {len(ph.parts)} parts, {len(ph.units)} units, sensors {sorted({u.unit.source for u in ph.units if u.unit.kind == 'sensor'})}; {n} seeds alone")
for mode in ("intact", "no_food", "no_agent", "no_noses", "no_env"):
    rs = [trial(7000 + s, mode) for s in range(n)]
    m = {k: float(np.mean([r[k] for r in rs])) for k in rs[0]}
    print(f"  {mode:9s} items {m['food']:.2f}  path {m['path']:.1f} m  in-disc {m['in_disc']*100:.0f}%  nearest food {m['near']:.2f} m (while in disc {m['near_in']:.2f} m)  work {m['work']:.1f} kJ", flush=True)
