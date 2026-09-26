"""RBT-107 design adversary: how much does the garden's Delta0 depend on WHICH eight worlds are used?

    python runs/RBT-107/adversary/probe_worlds.py RUN_DIR KIND SEASON J0 J1 [--workers W] [--refund-draws D]

Runs the garden's own bout (garden.py: BoutRunner.run_groups on the RBT-90 base sim, groups of four from
default_rng([107, j]), exploder gains 0) for worlds j in [J0, J1), and prints, per world, the population's mean gain on
random and on flat ground and their difference.  Worlds 0..7 are the garden's registered worlds (and must reproduce the
committed garden row means); worlds 8.. are fresh worlds from the same generator.  --refund-draws D also runs
probe_refund.py's world convention (RBT-101 readout adversary: draws from random.Random(f"RBT-101 refund {seed}"),
random terrain seed = start seed = the draw, groups from random.Random(f"{seed} C0 {kind} {d}").shuffle).
Only pre-onset (C0) or no-event base populations are read here; no shift arm.
"""
import argparse
import os
import random
import statistics as st
import sys
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import garden as Gd  # noqa: E402
from rabbitstew.evolution import BoutRunner  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402


def world_seeds(j):
    r = np.random.default_rng([107, 1000 + j])
    return int(r.integers(0, 2**31 - 1)), int(r.integers(0, 2**31 - 1))


def run(runner, sim0, pop, groups, tseed, sseed):
    out = {}
    for terr in ("random", "flat"):
        w = replace(sim0.world, terrain=terr, terrain_seed=(tseed if terr == "random" else None))
        res = runner.run_groups([([pop[i] for i in g], sseed) for g in groups], replace(sim0, world=w))
        vals = [0.0 if r["exploded"] else float(r["score"]) for rs in res for r in rs]
        out[terr] = st.fmean(vals)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run"); ap.add_argument("kind"); ap.add_argument("season", type=int)
    ap.add_argument("j0", type=int); ap.add_argument("j1", type=int)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--refund-draws", type=int, default=0)
    a = ap.parse_args()
    import json
    seed = int(json.load(open(os.path.join(a.run, "config.json")))["seed"])
    names = sorted(Gd.R92.Arm(a.run).alive_at(a.kind, a.season))
    pop = [Genotype.load(os.path.join(a.run, a.kind, "genomes", f"{n}.json")) for n in names]
    sim0 = Gd.base_sim(seed)
    runner = BoutRunner(sim0, a.workers)
    print(f"# probe_worlds seed {seed} {a.kind} season {a.season} n={len(pop)}")
    d = []
    for j in range(a.j0, a.j1):
        tseed, sseed = world_seeds(j)
        order = np.random.default_rng([107, j]).permutation(len(pop))
        groups = [[int(i) for i in order[g:g + 4]] for g in range(0, len(order), 4)]
        o = run(runner, sim0, pop, groups, tseed, sseed)
        d.append(o["flat"] - o["random"])
        print(f"garden-world {j:3d} random {o['random']:+.4f} flat {o['flat']:+.4f} flat-random {d[-1]:+.4f}", flush=True)
    if d:
        print(f"GARDEN-WORLDS [{a.j0},{a.j1}) mean flat-random {st.fmean(d):+.4f} sd over worlds {st.stdev(d) if len(d) > 1 else 0:.4f}")
    if a.refund_draws:
        rnd = random.Random(f"RBT-101 refund {seed}")
        draws = [rnd.randrange(1, 2**31 - 1) for _ in range(a.refund_draws)]
        e = []
        for k, dr in enumerate(draws):
            idx = list(range(len(pop)))
            order = [names[i] for i in idx]
            random.Random(f"{seed} C0 {a.kind} {k}").shuffle(order)
            pos = {n: i for i, n in enumerate(names)}
            groups = [[pos[n] for n in order[g:g + 4]] for g in range(0, len(order), 4)]
            o = run(runner, sim0, pop, groups, dr, dr)
            e.append(o["flat"] - o["random"])
            print(f"refund-draw {k} seed {dr} random {o['random']:+.4f} flat {o['flat']:+.4f} flat-random {e[-1]:+.4f}", flush=True)
        print(f"REFUND-DRAWS mean flat-random {st.fmean(e):+.4f}")
    runner.close()


if __name__ == "__main__":
    main()
