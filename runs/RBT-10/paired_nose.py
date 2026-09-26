"""Paired per-seed nose check for one best: on the same fresh seeds, intact vs noses blanked vs every env sensor
blanked; items, in-disc path, distinct 0.7 m cells (2 x eat radius) the in-disc path visits, items per visited cell,
nearest-item distance while in the disc; means with standard errors and the paired intact-minus-lesion difference.
Usage: paired_nose.py RUN KIND GEN [SEEDS=16]"""
import json, sys, numpy as np
from dataclasses import replace
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize
run, kind, gen = sys.argv[1], sys.argv[2], int(sys.argv[3]); n = int(sys.argv[4]) if len(sys.argv) > 4 else 16
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json"); ph = synthesize(g, cfg.synthesis)
R = cfg.food.radius; CELL = 2 * cfg.food.eat_radius
def trial(seed, mode):
    c = replace(cfg, random_start=True)
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed)); sim.set_food_seed(seed); b = sim.brains[0]
    for i, ui in enumerate(ph.units):
        if ui.unit.kind != "sensor": continue
        s = ui.unit.source
        if (mode == "no_noses" and s in ("food", "agent")) or (mode == "no_env" and s != "oscillator"): b.W[:, i] = 0
    steps = int(round(c.duration / c.control_dt)); path_in = 0.0; cells = set(); near_in = []
    last = sim.center_of_mass(0)[:2].copy()
    for t in range(steps):
        sim.step()
        if t % 10 == 0:
            p = sim.center_of_mass(0)[:2]; r = float(np.linalg.norm(p))
            if r <= R:
                path_in += float(np.linalg.norm(p - last)); cells.add((int(np.floor(p[0] / CELL)), int(np.floor(p[1] / CELL))))
                live = sim.food_pos[np.abs(sim.food_pos).max(axis=1) < 1e5]
                if len(live): near_in.append(float(np.linalg.norm(live - p, axis=1).min()))
            last = p.copy()
    food = float(sim.food_eaten[0])
    return dict(items=food, path_in=path_in, cells=len(cells), items_per_cell=food / max(len(cells), 1), items_per_m=food / max(path_in, 1e-9), near_in=float(np.mean(near_in)) if near_in else float("nan"))
modes = ("intact", "no_noses", "no_env"); res = {m: [trial(7000 + s, m) for s in range(n)] for m in modes}
keys = ["items", "path_in", "cells", "items_per_cell", "items_per_m", "near_in"]
chance = CELL * cfg.food.items / (np.pi * R * R)
print(f"{kind} g{gen}, {n} paired seeds; blind-mow chance rate = 2*eat radius*density = {chance:.3f} items/m; cell = {CELL:.2f} m")
print(f"{'mode':9s} " + " ".join(f"{k:>16s}" for k in keys))
for m in modes:
    a = {k: np.array([r[k] for r in res[m]]) for k in keys}
    print(f"{m:9s} " + " ".join(f"{np.nanmean(a[k]):8.2f}+-{np.nanstd(a[k])/np.sqrt(n):5.2f}" for k in keys))
for m in modes[1:]:
    print(f"paired intact - {m}:")
    for k in keys:
        d = np.array([ri[k] - rl[k] for ri, rl in zip(res["intact"], res[m])]); d = d[~np.isnan(d)]
        se = d.std(ddof=1) / np.sqrt(len(d)); print(f"   {k:14s} {d.mean():+7.3f} +- {se:5.3f}  (t = {d.mean()/se if se > 0 else float('nan'):+.1f}, {int((d > 0).sum())} of {len(d)} seeds positive)")
