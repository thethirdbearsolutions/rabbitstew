"""RBT-120 readout, descriptive (the design adversary's SHOULD 6): apportion the motor budget between its two parts.

    apportion.py [--per-group K] [--workers W] SEED_DIR [...]  > apportion_<O|B>.txt

For each seed directory (RBT-113 O or RBT-120 B, `final/` restored), K holistic members per group (founders, U, D, C;
rng 120) are scored solo on decompose.py's first fixed draw three ways, after the design adversary's probe_clamp.py:
  off     --motor-budget 0 (RBT-113's physics)
  cap     the Sum-gear cap alone (the servo clamp patched out)
  budget  the registered motor budget, cap + servo clamp
Every config is built from the seed directory's own config.json with only motor_budget (and the clamp) varied, so the
same script reads O and B directories.  It prints mean work (yield units) and net yield per group and way: how much of
the budget's effect on these bodies is the cap and how much the clamp.  Nothing is written into any run.
"""
import argparse
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

import rabbitstew.world as rw
from rabbitstew.evolution import HOLISTIC, EvolutionConfig, generation_sim, initial_population, spawn_streams
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import run_group

TERRAIN, START = 1131, 2131  # decompose.py's first fixed draw
WAYS = ("off", "cap", "budget")
_LIMIT = rw._servo_limit


def job(args):
    gd, sim, way = args
    rw._servo_limit = (lambda gear, config: {}) if way == "cap" else _LIMIT
    if way == "off":
        sim = replace(sim, world=replace(sim.world, motor_budget=0.0))
    else:
        sim = replace(sim, world=replace(sim.world, motor_budget=1.77))
    r = run_group([Genotype.from_dict(gd)], sim, START)[0]
    rw._servo_limit = _LIMIT
    return r["work"] * sim.food.work_cost / 1000.0, r["score"]


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-group", type=int, default=10)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("dirs", nargs="+")
    a = ap.parse_args(argv)
    tasks, keys = [], []
    for d in a.dirs:
        cfg = EvolutionConfig.from_dict(json.load(open(os.path.join(d, "U", "config.json"))))
        sim = generation_sim(cfg, TERRAIN)
        if os.path.basename(os.path.dirname(os.path.abspath(d.rstrip("/")))).startswith("B"):  # the ruling's M3
            assert sim.world.motor_budget == 1.77, f"{d}: a B directory whose config does not carry the budget"
        rng = np.random.default_rng(120)
        groups = {"founders": initial_population(HOLISTIC, cfg, spawn_streams(cfg.seed, cfg.holistic_stream_salt)[HOLISTIC]).members}
        for L in "UDC":
            p = os.path.join(d, L, HOLISTIC, "final")
            groups[L] = [Genotype.load(os.path.join(p, f)) for f in sorted(os.listdir(p))]
        for g, ms in groups.items():
            for i in rng.choice(len(ms), min(a.per_group, len(ms)), replace=False):
                for way in WAYS:
                    tasks.append((ms[i].to_dict(), sim, way))
                    keys.append((g, way))
    with ProcessPoolExecutor(a.workers) as pool:
        res = list(pool.map(job, tasks, chunksize=3))
    print(f"# RBT-120 apportion.py: {a.per_group} holistic members per group per directory over {len(a.dirs)} directories, "
          f"draw ({TERRAIN}, {START}); work in yield units, net yield; off / cap alone / cap + servo clamp")
    for g in ("founders", "U", "D", "C"):
        cells = []
        for way in WAYS:
            v = np.array([r for r, k in zip(res, keys) if k == (g, way)])
            cells.append(f"{way} work {v[:, 0].mean():.3f} net {v[:, 1].mean():+.3f}")
        print(f"  {g:9s} " + "   ".join(cells))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
