"""Within-season eating profile of the season-0 bests, alone on fresh seeds: cumulative items eaten, work and
displacement from spawn at 15, 30, 45 and 60 s.  Asks whether a 60 s season is four 15 s seasons or a robot leaving the disc."""
import json, sys, numpy as np
from dataclasses import replace
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
run = sys.argv[1]; gen = int(sys.argv[2]) if len(sys.argv) > 2 else 0; n = int(sys.argv[3]) if len(sys.argv) > 3 else 8
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
marks = (15.0, 30.0, 45.0, 60.0)
for kind in ("holistic", "conventional"):
    try: g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
    except FileNotFoundError: continue
    rows = []
    for s in range(n):
        seed = 7000 + s
        c = replace(cfg, random_start=True)
        sim = Simulation([g], c, spawns=spawn_layout(1, c, seed)); sim.set_food_seed(seed)
        p0 = sim.center_of_mass(0)[:2].copy(); steps = int(round(c.duration / c.control_dt)); per = int(round(15.0 / c.control_dt))
        row = []
        for t in range(1, steps + 1):
            sim.step()
            if t % per == 0:
                p = sim.center_of_mass(0)[:2]
                row.append((float(sim.food_eaten[0]), float(sim.work[0]) / 1000, float(np.linalg.norm(p - p0)), float(np.linalg.norm(p))))
        rows.append(row)
    a = np.array(rows)  # seeds x marks x (food, work, disp, r)
    m = a.mean(0)
    print(f"{kind:12s} best_gen{gen:04d}  (mean of {n} seeds; food and work cumulative; r = distance from arena centre, food disc radius {cfg.food.radius if hasattr(cfg,'food') and cfg.food else '?'} m)")
    for i, t in enumerate(marks):
        q = a[:, i, 0] - (a[:, i - 1, 0] if i else 0)
        print(f"   t={t:4.0f}s  food {m[i,0]:.2f} (this quarter {q.mean():.2f})  work {m[i,1]:.1f} kJ  disp {m[i,2]:.2f} m  r {m[i,3]:.2f} m  seeds outside 3 m disc: {int((a[:, i, 3] > 3.0).sum())}/{n}")
    print(f"   net energy at 60 s alone, food value 1, work cost {cfg.food.work_cost if hasattr(cfg,'food') and cfg.food else '?'}: {np.mean(a[:, -1, 0] - 0.03 * a[:, -1, 1]):+.2f} (per 15 s quarter {np.mean(a[:, -1, 0] - 0.03 * a[:, -1, 1]) / 4:+.2f}; baseline basal 0.25 per 15 s, here 1.0 per 60 s)")
    print("   per seed (food this quarter | r at quarter end):")
    for s in range(n):
        q = [a[s, i, 0] - (a[s, i - 1, 0] if i else 0) for i in range(4)]
        print("     seed", 7000 + s, "  ".join(f"{q[i]:.0f}|{a[s,i,3]:.1f}m" for i in range(4)))
