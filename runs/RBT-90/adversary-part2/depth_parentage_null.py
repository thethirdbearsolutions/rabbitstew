"""RBT-90 part 2 adversary, probe D2: depth with the run's own survival record and random parentage.

depth_null.py showed the interval's verdict turns on the age structure of mortality, which the
economy decides.  This null keeps everything the run actually did about WHO WAS ALIVE WHEN (every
individual's season of birth and its last season, from lineage.jsonl) and randomises only WHO
PARENTED: each birth's first parent is drawn uniformly from those alive in the season before it was
born.  If the interval is still met, it does not see selection on reproduction either; what it tests
is the demography (births, and how long individuals live).

usage: depth_parentage_null.py BULK_ROOT [REPS] [SEED ...]
"""
import json
import statistics as st
import sys

import numpy as np

SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
PI = (15, 26)


def load(run, pop):
    alive, first, parent = {}, {}, {}
    for l in open(f"{run}/lineage.jsonl"):
        r = json.loads(l)
        if r["population"] != pop:
            continue
        s, n = r["generation"], r["name"]
        alive.setdefault(s, []).append(n)
        if n not in first:
            first[n] = s
            parent[n] = r["parents"][0] if r["parents"] else None
    return alive, first, parent


def median_depth(alive, first, parent):
    last = max(alive)
    d = {}

    def depth(n):
        chain = []
        while n is not None and n not in d:
            chain.append(n)
            p = parent.get(n)
            n = p if p in first else None
        base = d[n] if n is not None else -1
        for x in reversed(chain):
            base += 1
            d[x] = base
        return d[chain[0]] if chain else base
    return st.median(depth(n) for n in alive[last])


if __name__ == "__main__":
    bulk = sys.argv[1]
    reps = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    seeds = [int(a) for a in sys.argv[3:]] or SEEDS
    rng = np.random.default_rng(90)
    print(f"median first-parent depth of the living at the last season: the run, and {reps} random-parentage "
          f"replicates on the run's own survival record; share of replicates inside {list(PI)}")
    shares = []
    for seed in seeds:
        for pop in ("holistic", "conventional"):
            alive, first, parent = load(f"{bulk}/forage-{seed}", pop)
            real = median_depth(alive, first, parent)
            ms = []
            for _ in range(reps):
                rp = {}
                for n, s in first.items():
                    if parent[n] is None:
                        rp[n] = None
                    else:
                        # the season before; a genome born in a run's first season (a restart) draws from
                        # the non-newborns alive with it
                        pool = alive.get(s - 1) or [x for x in alive[s] if first[x] < s or parent[x] is None]
                        rp[n] = pool[rng.integers(len(pool))]
                ms.append(median_depth(alive, first, rp))
            share = float(np.mean([PI[0] <= m <= PI[1] for m in ms]))
            shares.append(share)
            print(f"{seed:5d} {pop:>12s}  run {real:5.1f}  null {np.median(ms):5.1f} "
                  f"({np.percentile(ms, 2.5):4.1f}-{np.percentile(ms, 97.5):4.1f})  inside {share:.2f}", flush=True)
    print(f"\nmean share of random-parentage replicates inside {list(PI)}: {np.mean(shares):.2f}")
