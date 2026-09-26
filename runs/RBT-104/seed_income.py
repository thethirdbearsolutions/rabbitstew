"""RBT-104, coordinator's condition 2 (17:02): what does the seed cost the founders at t = 0?

For each part-2 seed, take the 30 founders that seed_founders.py plants (even i) and score each one
twice on the same paired bouts: as planted, and bare (the identical part-2 founder without the
motif).  Both at K = 1 (the S1 founders) and at K = 8 (the S8 founders: every link times 8, planted
and bare alike, as `--link-scale 8` does at founding).  The bout is RBT-103's (one robot, the arm's
own world from the committed part-2 config, food seed = spawn seed), 16 paired seeds from 7000.

Reported per seed and pooled: mean income bare and planted, and the paired difference with a
t-interval over the 30 founders (each founder's mean over its 16 seeds).  Also printed: the
platform and the MuJoCo version (condition 3).

Usage: seed_income.py [--seeds 801,804,...] [--bouts 16] [--procs 4]
"""
import argparse
import importlib.util
import os
import platform
import sys
from multiprocessing import get_context

import mujoco
import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("sf", os.path.join(_HERE, "seed_founders.py"))
sf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sf)

from rabbitstew.evolution import CONVENTIONAL  # noqa: E402
from rabbitstew.genetics import scale_links  # noqa: E402
from rabbitstew.simulation import Simulation, spawn_layout  # noqa: E402

T975 = {29: 2.045, 9: 2.262}
G = {}  # (seed, i, K, planted) -> genotype; set before the pool forks
CFG = {}


def bout(task):
    seed, i, K, planted, s = task
    cfg = CFG[seed]
    sim = Simulation([G[(seed, i, K, planted)]], cfg, spawns=spawn_layout(1, cfg, s))
    sim.set_food_seed(s)
    for _ in range(int(round(cfg.duration / cfg.control_dt))):
        sim.step()
    return seed, i, K, planted, s, float(sim.food_eaten[0])


def tint(v):
    v = np.asarray(v, float)
    se = float(np.std(v, ddof=1) / np.sqrt(len(v)))
    t = T975.get(len(v) - 1, 1.96)
    return float(v.mean()), float(v.mean() - t * se), float(v.mean() + t * se)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", default="801,804,805,806,807,1,2,3,4,7")
    ap.add_argument("--bouts", type=int, default=16)
    ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args()
    seeds = [int(x) for x in a.seeds.split(",")]
    bseeds = [7000 + j for j in range(a.bouts)]
    for seed in seeds:
        e = sf.part2_ecology(seed)
        CFG[seed] = e.evo.sim
        bare = e.populations[CONVENTIONAL]
        e.runner.close()
        planted = sf.seeded(seed)
        for i in range(0, 60, 2):
            for K in (1.0, 8.0):
                G[(seed, i, K, False)] = scale_links(bare[i].copy(), K)
                G[(seed, i, K, True)] = scale_links(planted[i].copy(), K)
    tasks = [(seed, i, K, p, s) for seed in seeds for i in range(0, 60, 2) for K in (1.0, 8.0)
             for p in (False, True) for s in bseeds]
    with get_context("fork").Pool(a.procs) as pool:
        rows = pool.map(bout, tasks, chunksize=32)
    got = {r[:5]: r[5] for r in rows}
    print("# RBT-104: the seed's cost to the founders at t = 0 (coordinator's condition 2)\n")
    print(f"platform {platform.machine()}, MuJoCo {mujoco.__version__}; 30 planted founders per seed "
          f"(even i), each scored bare and planted on {a.bouts} paired bouts from 7000\n")
    print("| seed | K | bare income | planted income | planted - bare, t(29) over founders | founders with any difference |")
    print("|---|---|---|---|---|---|")
    pooled = {1.0: [], 8.0: []}
    for seed in seeds:
        for K in (1.0, 8.0):
            b = [np.mean([got[(seed, i, K, False, s)] for s in bseeds]) for i in range(0, 60, 2)]
            p = [np.mean([got[(seed, i, K, True, s)] for s in bseeds]) for i in range(0, 60, 2)]
            d = [y - x for x, y in zip(b, p)]
            pooled[K] += d
            m, lo, hi = tint(d)
            print(f"| {seed} | {K:g} | {np.mean(b):.4f} | {np.mean(p):.4f} | {m:+.4f} [{lo:+.4f}, {hi:+.4f}] | "
                  f"{sum(1 for x in d if x != 0)}/30 |")
    for K in (1.0, 8.0):
        per_seed = [np.mean(pooled[K][j:j + 30]) for j in range(0, len(pooled[K]), 30)]
        m, lo, hi = tint(per_seed) if len(per_seed) > 1 else (per_seed[0], float("nan"), float("nan"))
        print(f"\nK = {K:g}: planted - bare, mean over {len(per_seed)} seeds {m:+.4f}, t over seeds [{lo:+.4f}, {hi:+.4f}]")


if __name__ == "__main__":
    main()
