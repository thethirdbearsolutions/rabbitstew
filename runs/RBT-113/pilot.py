"""RBT-113 pilot (PREREGISTRATION.md §2): is solo foraging yield heritable among the founders the benchmark starts
from, and what does one solo evaluation cost?

For each fauna (the holistic random bodies and the designed body with random controllers, both with the
`foraging` vocabulary), N founders are drawn exactly as `evolve` draws them; each gets one child by the
benchmark's own operator (holistic `mutate`; designed body `mutate_controller`, --conventional-topology), with
no crossover and no selection.  Parent and child are each scored solo on D fresh start draws of the benchmark's
world (world.py).  Printed: seconds per solo season, the trait's spread, and the parent-offspring regression
slope of the child's mean on the parent's mean with a bootstrap 95% CI.  A one-parent regression on an asexual
child estimates broad-sense H^2 of the D-draw mean (the child is the parent plus one mutation): this is the
quantity the realised heritability of the benchmark is to be compared with.

Usage: pilot.py N D SEED WORKERS > pilot.txt
"""
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from world import evolution_config  # noqa: E402

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genetics import mutate, mutate_controller  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import run_group  # noqa: E402


def _solo(args):
    gd, sim, seed = args
    t = time.time()
    r = run_group([Genotype.from_dict(gd)], sim, seed)[0]
    return r["score"], r["food"], r["work"], r["path"], time.time() - t


def slope_ci(x, y, rng, B=2000):
    x, y = np.asarray(x), np.asarray(y)
    b = float(np.polyfit(x, y, 1)[0]) if np.var(x) > 0 else float("nan")
    bs = []
    for _ in range(B):
        i = rng.integers(0, len(x), len(x))
        if np.var(x[i]) > 0:
            bs.append(np.polyfit(x[i], y[i], 1)[0])
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return b, float(lo), float(hi)


def main(n, d, seed, workers):
    cfg = evolution_config(population=n, generations=1, seed=seed, workers=1)
    streams = spawn_streams(seed)
    draws = np.random.default_rng(seed + 1_000_003)
    pool = ProcessPoolExecutor(workers)
    print(f"# RBT-113 pilot: N={n} founders per fauna, D={d} solo draws each for parent and child, seed {seed}")
    for kind in (HOLISTIC, CONVENTIONAL):
        rng = streams[kind]
        pop = initial_population(kind, cfg, rng)
        op = mutate if kind == HOLISTIC else mutate_controller
        kids = [op(p, rng, cfg.mutation) for p in pop.members]
        tasks = []
        for g in pop.members + kids:
            for _ in range(d):
                tasks.append((g.to_dict(), cfg.sim, int(draws.integers(0, 2**31 - 1))))
        t0 = time.time()
        res = list(pool.map(_solo, tasks, chunksize=1))
        wall = time.time() - t0
        arr = np.array([r[:4] for r in res]).reshape(2 * n, d, 4).mean(axis=1)
        secs = np.array([r[4] for r in res])
        par, kid = arr[:n], arr[n:]
        print(f"\n## {kind}")
        print(f"seconds per solo season: mean {secs.mean():.2f}, median {np.median(secs):.2f}, p95 {np.percentile(secs, 95):.2f}; wall {wall:.0f}s on {workers} workers")
        for j, name in enumerate(("yield", "food", "work_J", "path_m")):
            b, lo, hi = slope_ci(par[:, j], kid[:, j], np.random.default_rng(7))
            q = np.percentile(par[:, j], [10, 50, 90])
            print(f"{name:8s} parents mean {par[:, j].mean():+.4f} sd {par[:, j].std(ddof=1):.4f} p10/50/90 {q[0]:+.4f} {q[1]:+.4f} {q[2]:+.4f}"
                  f" | child-on-parent slope {b:+.3f} [95% CI {lo:+.3f}, {hi:+.3f}]")
        nz = float(np.mean(np.abs(par[:, 0]) > 1e-3))
        print(f"fraction of founders with |yield| > 0.001: {nz:.2f}")
    pool.shutdown()


if __name__ == "__main__":
    main(*(int(a) for a in sys.argv[1:5]))
