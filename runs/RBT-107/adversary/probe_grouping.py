"""RBT-107 design adversary: how much of a garden population's mean on ONE world is the draw of who shares an arena?

    python runs/RBT-107/adversary/probe_grouping.py RUN_DIR KIND SEASON WORLD_J K

The garden's population (alive_at, sorted by name), the garden's world j (terrain and start seed), the garden's bout;
only the grouping into fours changes, K times (default_rng([107, 'grouping', k]) permutations; k = 0 is replaced by the
garden's own grouping default_rng([107, j])).  Prints the population mean gain on flat and on random ground per
grouping and their sd over groupings: the part of G that is grouping noise, which more worlds average away and more
seeds do not need to.  Also runs probe_refund.py's C0 set (played season SEASON) with the garden's grouping rule, so
the population definition's effect is seen apart from grouping.  Pre-onset (C0) population of the base arm only.
"""
import json
import os
import statistics as st
import sys
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import garden as Gd  # noqa: E402
from rabbitstew.evolution import BoutRunner  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402


def played(run, kind, s):
    out = []
    for line in open(f"{run}/lineage.jsonl"):
        r = json.loads(line)
        if r["generation"] == s and r["population"] == kind and "food" in r:
            out.append(r["name"])
    return sorted(out)


def mean_gain(runner, sim0, pop, perm, tseed, sseed, terr):
    groups = [[int(i) for i in perm[g:g + 4]] for g in range(0, len(perm), 4)]
    w = replace(sim0.world, terrain=terr, terrain_seed=(tseed if terr == "random" else None))
    res = runner.run_groups([([pop[i] for i in g], sseed) for g in groups], replace(sim0, world=w))
    return st.fmean(0.0 if r["exploded"] else float(r["score"]) for rs in res for r in rs)


def main(run, kind, s, j, K):
    seed = int(json.load(open(os.path.join(run, "config.json")))["seed"])
    sim0 = Gd.base_sim(seed)
    runner = BoutRunner(sim0, 4)
    tseed, sseed = Gd.worlds(j + 1)[j]
    for label, names in (("garden C0 (alive_at, end of season)", sorted(Gd.R92.Arm(run).alive_at(kind, s))),
                         ("probe_refund C0 (played the season)", played(run, kind, s))):
        pop = [Genotype.load(os.path.join(run, kind, "genomes", f"{n}.json")) for n in names]
        print(f"# seed {seed} {kind} season {s} world {j}: {label}, n = {len(pop)}")
        vals = {"flat": [], "random": []}
        for k in range(K if label.startswith("garden") else 1):
            perm = np.random.default_rng([107, j] if k == 0 else [107, 7, k]).permutation(len(pop))
            row = {t: mean_gain(runner, sim0, pop, perm, tseed, sseed, t) for t in ("random", "flat")}
            for t in row:
                vals[t].append(row[t])
            print(f"grouping {k}: random {row['random']:+.4f} flat {row['flat']:+.4f} flat-random {row['flat'] - row['random']:+.4f}", flush=True)
        if len(vals["flat"]) > 1:
            d = [a - b for a, b in zip(vals["flat"], vals["random"])]
            print(f"GROUPING sd over {len(d)} groupings: flat {st.stdev(vals['flat']):.4f} random {st.stdev(vals['random']):.4f} "
                  f"flat-random {st.stdev(d):.4f}")
    runner.close()


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5]))
