"""RBT-113 (PREREGISTRATION.md §2.1): heritability of the trait's ecology twin, lifetime mean foraging yield, on
committed data only.

Reads committed `lineage-last.txt` files (one row per individual at its last observation: population, name,
generation, age, evals, fitness = lifetime mean yield, parents) of paper 5's foraging ecology arms and prints,
per run and fauna, the parent-offspring correlation (paper 5 §4's statistic: child's lifetime mean yield on the
mean of its parents', both with at least MIN_EVALS evaluations, as `rabbitstew heritability --min-evals 5`) and
the regression slope, with a bootstrap 95% CI over children.  Nothing is simulated.

Usage: h2_committed.py RUN_DIR... > h2_committed.txt
"""
import os
import sys

import numpy as np

MIN_EVALS = 5


def rows(path):
    with open(path) as f:
        head = f.readline().rstrip("\n").split("\t")
        for line in f:
            v = line.rstrip("\n").split("\t")
            yield dict(zip(head, v + [""] * (len(head) - len(v))))


def pairs(path, kind):
    fit, ev, par = {}, {}, {}
    for r in rows(path):
        if r["population"] != kind:
            continue
        fit[r["name"]], ev[r["name"]] = float(r["fitness"]), int(r["evals"])
        par[r["name"]] = [p for p in r["parents"].split(",") if p]
    x, y = [], []
    for n, ps in par.items():
        ps = [p for p in ps if p in fit and ev[p] >= MIN_EVALS]
        if ps and ev[n] >= MIN_EVALS:
            x.append(np.mean([fit[p] for p in ps]))
            y.append(fit[n])
    return np.array(x), np.array(y)


def ci(x, y, rng, B=2000):
    rs, bs = [], []
    for _ in range(B):
        i = rng.integers(0, len(x), len(x))
        if np.std(x[i]) > 0 and np.std(y[i]) > 0:
            rs.append(np.corrcoef(x[i], y[i])[0, 1])
            bs.append(np.polyfit(x[i], y[i], 1)[0])
    return np.percentile(rs, [2.5, 97.5]), np.percentile(bs, [2.5, 97.5])


if __name__ == "__main__":
    print(f"# RBT-113: parent-offspring heritability of lifetime mean yield on committed lineage-last.txt (min evals {MIN_EVALS})")
    print(f"{'run':34s} {'fauna':12s} {'pairs':>5s} {'r':>7s} {'r 95% CI':>17s} {'slope':>7s} {'slope 95% CI':>17s}")
    for run in sys.argv[1:]:
        p = os.path.join(run, "lineage-last.txt")
        for kind in ("holistic", "conventional"):
            x, y = pairs(p, kind)
            if len(x) < 10:
                print(f"{run:34s} {kind:12s} {len(x):5d}  too few pairs")
                continue
            r = np.corrcoef(x, y)[0, 1]
            b = np.polyfit(x, y, 1)[0]
            (rl, rh), (bl, bh) = ci(x, y, np.random.default_rng(113))
            print(f"{run:34s} {kind:12s} {len(x):5d} {r:+7.3f} [{rl:+.3f}, {rh:+.3f}] {b:+7.3f} [{bl:+.3f}, {bh:+.3f}]")
