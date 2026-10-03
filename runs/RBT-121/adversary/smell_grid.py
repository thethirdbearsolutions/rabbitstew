"""RBT-121 adversary on audit C finding 2: is "one nose step buys 0-7% against +25% speed buying 12-37%" robust
to the calibration cell, and are the percentages resolved at n = 200?

    PYTHONPATH=<dir holding C's probe_world.py> python runs/RBT-121/adversary/smell_grid.py [n] [seed0]

Uses auditor C's kinematic model (probe_world.bout) unchanged; varies OMEGA (turn limit) x NOISE (heading noise)
over 0.25/0.5/1.0 x 0.5/1.0/2.0.  Every condition is run on the SAME n seeds, so contrasts are paired; each
percentage is printed with a paired-bootstrap 95% CI.  Also prints the calibration ratios (k = 64 smell / blind-best)
against RBT-106's x1.65 / x2.37, and a proportional nose step (k x1.25, the same relative change as +25% speed).
"""
import sys
from multiprocessing import Pool

import numpy as np

import probe_world as P

n = int(sys.argv[1]) if len(sys.argv) > 1 else 200
S0 = int(sys.argv[2]) if len(sys.argv) > 2 else 70000
CONDS = [("straight", 0.25, "straight", 0), ("fast", 0.3125, "straight", 0), ("arc", 0.25, "arc", 0),
         ("k1", 0.25, "smell", 1.0), ("k1.25", 0.25, "smell", 1.25), ("k1.4", 0.25, "smell", 1.4),
         ("k2", 0.25, "smell", 2.0), ("k2.4", 0.25, "smell", 2.4), ("k2.5", 0.25, "smell", 2.5),
         ("k6", 0.25, "smell", 6.0), ("k64", 0.25, "smell", 64.0)]
WORLDS = {"uniform": dict(), "HP": dict(patches=3)}


def job(a):
    wname, om, noise, label, v, c, k, s = a
    P.OMEGA, P.NOISE = om, noise
    return (wname, om, noise, label, s), P.bout(P.World(wname, **WORLDS[wname]), v, c, k, s)


def pct(a, b, rng):
    r = 100 * (b.mean() / a.mean() - 1)
    idx = rng.integers(0, len(a), (2000, len(a)))
    bs = 100 * (b[idx].mean(1) / a[idx].mean(1) - 1)
    lo, hi = np.percentile(bs, [2.5, 97.5])
    return f"{r:+5.1f}% [{lo:+5.1f},{hi:+5.1f}]"


if __name__ == "__main__":
    cells = [(w, om, nz) for w in WORLDS for om in (0.25, 0.5, 1.0) for nz in (0.5, 1.0, 2.0)]
    tasks = [(w, om, nz, l, v, c, k, S0 + s) for (w, om, nz) in cells for (l, v, c, k) in CONDS for s in range(n)]
    with Pool(4) as pool:
        res = dict(pool.map(job, tasks, chunksize=20))
    rng = np.random.default_rng(1)
    print(f"# C's kinematic model, n = {n} paired seeds from {S0}; v 0.25; +25% speed = blind straight 0.25 -> 0.3125")
    print("# cal = k64 / blind-best (target uniform x1.65, HP x2.37); percentages with paired-bootstrap 95% CI")
    for (w, om, nz) in cells:
        X = {l: np.array([res[(w, om, nz, l, S0 + s)] for s in range(n)], float) for l, *_ in CONDS}
        blind = max(X["straight"].mean(), X["arc"].mean())
        print(f"{w:7s} omega {om:4.2f} noise {nz:3.1f}: blind {blind:4.2f} k6 x{X['k6'].mean() / blind:4.2f} cal x{X['k64'].mean() / blind:4.2f} | "
              f"+25% speed {pct(X['straight'], X['fast'], rng)}  k1->1.4 {pct(X['k1'], X['k1.4'], rng)}  k2->2.4 {pct(X['k2'], X['k2.4'], rng)}  "
              f"k1->1.25 {pct(X['k1'], X['k1.25'], rng)}  k2->2.5 {pct(X['k2'], X['k2.5'], rng)}", flush=True)
