"""Is the final Pioneer's nose-dependence a compass or a brake?  Alone on fresh seeds, intact vs noses blanked
vs all env sensors blanked: items eaten, path, time fraction inside the 3 m food disc, mean distance from the
centre, and items eaten per metre of path inside the disc.  Usage: brake_or_compass.py <run> <kind> <gen> <n>"""
import json, sys, numpy as np
from dataclasses import replace
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize
run, kind, gen, n = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
R = cfg.food.radius
def trial(seed, mode):
    c = replace(cfg, random_start=True); sp = spawn_layout(1, c, seed)
    sim = Simulation([g], c, spawns=sp); sim.set_food_seed(seed)
    b = sim.brains[0]; ph = synthesize(g, c.synthesis)
    for i, ui in enumerate(ph.units):
        k = ui.unit.kind
        if mode == "no_food" and k == "sensor" and ui.unit.source in ("food", "agent"): b.W[:, i] = 0
        elif mode == "no_env" and k == "sensor" and ui.unit.source != "oscillator": b.W[:, i] = 0
    steps = int(round(c.duration / c.control_dt)); inside = 0; path_in = 0.0; path = 0.0; dist = []
    last = sim.center_of_mass(0)[:2].copy()
    for t in range(steps):
        sim.step()
        p = sim.center_of_mass(0)[:2]; r = float(np.linalg.norm(p)); dist.append(r)
        if t % 10 == 0:
            d = float(np.linalg.norm(p - last)); path += d
            if r <= R: path_in += d
            last = p.copy()
        if r <= R: inside += 1
    return dict(food=float(sim.food_eaten[0]), path=path, inside=inside / steps, mean_r=float(np.mean(dist)), path_in=path_in)
print(f"{kind} g{gen}, n={n} seeds, food disc radius {R} m, eat radius {cfg.food.eat_radius} m")
print("mode     | items eaten  | path (m) | time inside disc | mean dist from centre (m) | items per m of in-disc path")
for mode in ("intact", "no_food", "no_env"):
    rs = [trial(7000 + s, mode) for s in range(n)]
    m = {k: np.mean([r[k] for r in rs]) for k in rs[0]}; sd = np.std([r["food"] for r in rs]) / np.sqrt(n)
    print(f"{mode:8s} | {m['food']:.2f} +- {sd:.2f} | {m['path']:8.1f} | {m['inside']:16.2f} | {m['mean_r']:25.2f} | {m['food']/max(m['path_in'],1e-9):.3f}")
