"""RBT-90 part 2 adversary, probe D: does the depth interval [15, 26] test the search, or the demography?

Median first-parent depth of the living is, to first order, how many generations the population's
births add up to.  Births and deaths per season are fixed by the economy (capacity, living cost,
breeding threshold), not by what the genomes do.  So this asks whether a population with NO
selection at all, the same per-season births and deaths read from the committed seasons.txt, lands in
the interval too.

Neutral null, per replicate: each season, the season's deaths are removed from the living (uniformly
at random, or oldest first: two bounds on age structure), then the season's births each take a first
parent uniformly from those alive at the start of the season, at the parent's depth + 1.  The median
depth of the living at the last season is read against [15, 26], as part2_readout.depth reads the run.

usage: depth_null.py [REPS] [SEED ...]    (reads runs/RBT-90/forage-SEED/seasons.txt only)
"""
import importlib.util
import pathlib
import statistics as st
import sys

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("ro", HERE.parent / "part2_readout.py")
ro = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ro)
PI = ro.DEPTH_PI


def schedule(seed, pop):
    rows = [l.split("\t") for l in (HERE.parent / f"forage-{seed}" / "seasons.txt").read_text().splitlines()[1:]]
    return [(int(r[2]), int(r[3]), int(r[4])) for r in rows if r[1] == pop]


def neutral(sched, rng, oldest_first):
    alive0 = sched[0][0]
    depth = [0] * alive0
    born = [0] * alive0
    for s, (alive, b, d) in enumerate(sched[1:], start=1):
        parents = list(depth)
        if d:
            if oldest_first:
                order = sorted(range(len(depth)), key=lambda i: born[i])[:d]
            else:
                order = rng.choice(len(depth), size=min(d, len(depth)), replace=False)
            keep = sorted(set(range(len(depth))) - set(int(i) for i in order))
            depth, born = [depth[i] for i in keep], [born[i] for i in keep]
        if b and parents:
            ps = rng.integers(0, len(parents), b)
            depth += [parents[p] + 1 for p in ps]
            born += [s] * b
    return st.median(depth) if depth else float("nan")


if __name__ == "__main__":
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    seeds = [int(a) for a in sys.argv[2:]] or ro.SEEDS
    rng = np.random.default_rng(90)
    print(f"interval {list(PI)}; neutral null over {reps} replicates per seed and fauna (median depth of the living "
          f"at the last season; share of replicates inside the interval)")
    print(f"{'seed':>5s} {'fauna':>12s} {'births':>6s} {'run':>5s} | {'uniform deaths':>28s} | {'oldest die first':>28s}")
    inside = {True: [], False: []}
    for seed in seeds:
        for pop, dep in (("holistic", ro.depth(HERE.parent / f"forage-{seed}")["median"]),
                         ("conventional", ro.depth(HERE.parent / f"forage-{seed}", "conventional")["median"])):
            sch = schedule(seed, pop)
            cells = []
            for oldest in (False, True):
                ms = [neutral(sch, rng, oldest) for _ in range(reps)]
                share = np.mean([PI[0] <= m <= PI[1] for m in ms])
                inside[oldest].append(share)
                cells.append(f"{np.median(ms):5.1f} ({np.percentile(ms, 2.5):4.1f}-{np.percentile(ms, 97.5):4.1f}) in {share:4.2f}")
            print(f"{seed:5d} {pop:>12s} {sum(b for _, b, _ in sch):6d} {dep:5.1f} | {cells[0]:>28s} | {cells[1]:>28s}", flush=True)
    print(f"\nmean share of neutral replicates inside {list(PI)}: uniform deaths {np.mean(inside[False]):.2f}, "
          f"oldest first {np.mean(inside[True]):.2f}")
