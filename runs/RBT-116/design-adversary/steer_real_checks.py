"""RBT-116 steer.py design adversary: checks on REAL bodies (RBT-113 O1 U finals, committed checkpoint
ckpt/rbt-113-O1) in FIXTURE worlds only (the PR's own test fixture geometry; test draws (100+i, 200+i); never W1 or its
pool).  Read-only on rabbitstew/ and on runs/RBT-116/steer.py (imported from the PR tree).

  A. The decoy's clearance re-draw against the world's own clearance rule.  steer.draw_theta clears the ROOT only; the
     world's rule is Simulation._clearance_points() (every geom centre under clear_from=geoms, RBT-125, merged; the
     registration's fairness block turns it ON "if merged").  Count seasons whose accepted θ puts a rotated live item
     within the clearance of a geom centre -- a phantom item the real layout can never offer.
  B. Holistic genomes through run_season / stage 1: no crash; sensorless members identical (I1); timing.
  C. The worker path: SimConfig.to_dict/from_dict round trip (steer.py's _job) keeps every W1 flag, and a call through
     _job equals the in-process call.

    python3 steer_real_checks.py PR_TREE CKPT_O1_DIR > steer_real_checks.txt
"""
import importlib.util
import os
import sys
import time
from dataclasses import replace

import numpy as np

tree, ck = sys.argv[1], sys.argv[2]
sys.path.insert(0, tree)
spec = importlib.util.spec_from_file_location("steer", os.path.join(tree, "runs/RBT-116/steer.py"))
steer = importlib.util.module_from_spec(spec)
sys.modules["steer"] = steer
spec.loader.exec_module(steer)
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import FoodConfig, SimConfig, spawn_layout  # noqa: E402

FIX = SimConfig(duration=10.0, random_start=True, start_distance_range=(1.0, 1.5),
                food=FoodConfig(items=4, radius=2.0, decay=1.0, smell_contrast=2.5, smell_tau=2.0))
FIX_G = replace(FIX, food=replace(FIX.food, clear_from="geoms", eat_from="root"))
DRAWS = [steer.Draw(100 + i, 200 + i) for i in range(40)]


def members(kind, n):
    d = os.path.join(ck, "U", kind, "final")
    fs = sorted(os.listdir(d))[:n]
    return [(f, Genotype.load(os.path.join(d, f))) for f in fs]


def n_food(g):
    return sum(1 for _, b in g.brains() for u in b.units if getattr(u, "kind", "") == "sensor" and getattr(u, "source", "") == "food")


print("# steer_real_checks.py: RBT-113 O1 seed 1 U finals; fixture worlds only")
print("\n## A. decoy clearance: accepted θ vs the world's clearance points (clear_from=geoms fixture, clearance 0.8 m)")
tot = viol = 0
worst = []
for kind in ("holistic", "conventional"):
    kt = kv = 0
    for name, g in members(kind, 10):
        for d in DRAWS[:20]:
            cfg = replace(steer.draw_sim(FIX_G, d), opponent_proxy=True)
            sim = steer.Simulation([g], cfg, spawns=[spawn_layout(2, cfg, d.start_seed)[0]])
            sim.set_food_seed(d.start_seed)
            live = steer._live_items(sim)
            pts = sim._clearance_points()
            real_min = float(np.linalg.norm(live[:, None, :] - pts[None, :, :], axis=2).min())
            th, _ = steer.draw_theta(d.start_seed, live, sim.data.xpos[sim.robots[0].root_body][:2], cfg.food.clearance)
            dec_min = float(np.linalg.norm(steer.rotate(live, th)[:, None, :] - pts[None, :, :], axis=2).min())
            kt += 1
            if dec_min < cfg.food.clearance:
                kv += 1
                worst.append((kind, name, d.start_seed, round(real_min, 3), round(dec_min, 3)))
    tot += kt; viol += kv
    print(f"{kind:12s} seasons {kt:4d}  decoy offers a phantom item inside the world's clearance: {kv:3d} ({kv / kt:.3f})")
print(f"all          seasons {tot:4d}  violations {viol} ({viol / tot:.3f}); examples (kind, member, start seed, real min, decoy min):")
for w in sorted(worst, key=lambda r: r[4])[:6]:
    print("   ", w)

print("\n## B. holistic genomes through the battery's stage 1 (FIXTURE, 4 test draws)")
bat = steer.Battery(DRAWS[:4], DRAWS[4:6], DRAWS[6:8])
for kind in ("holistic", "conventional"):
    for name, g in members(kind, 6):
        t0 = time.time()
        s1 = steer._pairs(g, FIX, bat.stage1, steer.run_season)
        same = sum(not steer.trajectories_differ(a, b) for a, b in zip(s1["intact"], s1["decoy"]))
        exc = np.mean([steer.chemotaxis_index(a, a.v_min())[2] for a in s1["intact"]])
        print(f"{kind:12s} {name}  food sensors {n_food(g)}  stage-1 identical {same}/4  "
              f"I1 {'ok' if (n_food(g) > 0 or same == 4) else 'VIOLATED'}  excluded-tick share {exc:.2f}  {time.time() - t0:5.1f} s")

print("\n## C. the worker path (_job): SimConfig round trip and call equality")
W1LIKE = replace(FIX, settle_until_rest=0.01, settle_max=5.0,
                 food=replace(FIX.food, eat_from="root", clear_from="geoms", eat_rule="surface", patches=2, patch_radius=0.4, regrow_delay=60.0))
rt = SimConfig.from_dict(W1LIKE.to_dict())
diffs = [k for k in ("eat_from", "clear_from", "eat_rule", "smell_contrast", "smell_tau", "patches", "patch_radius", "regrow_delay")
         if getattr(rt.food, k) != getattr(W1LIKE.food, k)]
diffs += [k for k in ("settle_until_rest", "settle_max", "duration", "random_start") if getattr(rt, k) != getattr(W1LIKE, k)]
print(f"round-trip field differences: {diffs or 'none'}")
name, g = members("holistic", 1)[0]
small = steer.Battery(DRAWS[:1], DRAWS[1:3], DRAWS[3:5])
a = steer.call_genome(g, FIX, small)
b = steer._job((g.to_dict(), FIX.to_dict(), small.to_dict()))
print(f"in-process call == _job call: {steer._strip(a) == steer._strip(b)}  ({a['call']}, stage {a['stage']})")
