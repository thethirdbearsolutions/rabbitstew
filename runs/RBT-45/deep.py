"""RBT-45 follow-up: how deep would drift have to go to reach the crossed circuit?

The published grid stops at k = 200, where crossed is 0.147 at the default operator
and still climbing.  A real lineage gets 19.  The obvious next question -- how many
mutations would the default operator actually need for a coin-flip chance at the
circuit that steers -- has an answer, and the answer comes with a catch that §6.3
already hinted at: the same drift that eventually wires the pairing is dismantling
the controller on the way, so there may be no depth at which you have both.

This runs the default operator out to k = 1000 and tracks the crossed rate against
CHASSIS (the chassis-nose gate every evolved Pioneer depends on) and the genotype's
link count, so the two curves can be read against each other.

Usage:  python runs/RBT-45/deep.py [--n 1000]
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import zlib
from dataclasses import replace
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import reach
from rabbitstew.genetics import mutate_controller
from rabbitstew.synthesis import synthesize

MASTER_SEED = reach.MASTER_SEED
K_VALUES = (200, 350, 500, 750, 1000)


def cell_id(k):
    return f"deep|conventional|add0.15|rem0.1|k{k}"


def run_chunk(task):
    k, lo, hi = task
    cfg = reach.config()
    pool = reach.parents("conventional")
    mcfg = replace(cfg.mutation, add_link_rate=0.15, remove_link_rate=0.1)
    cid = cell_id(k)
    rows = []
    for i in range(lo, hi):
        rng = np.random.default_rng(np.random.SeedSequence([MASTER_SEED, zlib.crc32(cid.encode()), i]))
        g = pool[i % len(pool)]
        for _ in range(k):
            g = mutate_controller(g, rng, mcfg)
        rows.append((i % len(pool), reach.measure_conventional(synthesize(g, cfg.sim.synthesis))))
    return k, rows


def cluster_se(by_parent, n_parents, draws=3000, seed=5):
    rng = np.random.default_rng(seed)
    h = np.array([by_parent[p][0] for p in range(n_parents)], float)
    t = np.array([by_parent[p][1] for p in range(n_parents)], float)
    out = np.empty(draws)
    for d in range(draws):
        i = rng.integers(0, n_parents, n_parents)
        out[d] = h[i].sum() / max(t[i].sum(), 1)
    return float(out.std())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    n_parents = len(reach.parents("conventional"))
    tasks = [(k, lo, min(lo + 50, args.n)) for k in K_VALUES for lo in range(0, args.n, 50)]
    print(f"depths {K_VALUES} x {args.n} lineages, {len(tasks)} chunks", flush=True)

    t0 = time.time()
    collected = {k: [] for k in K_VALUES}
    with Pool(args.workers) as p:
        for k, rows in p.imap_unordered(run_chunk, tasks, chunksize=1):
            collected[k].extend(rows)

    out = {"master_seed": MASTER_SEED, "n_per_cell": args.n, "add_link_rate": 0.15, "cells": []}
    print("\n| k | crossed | ±cluster SE | uncrossed | CHASSIS | mean links | food sensors wired |")
    print("|---|---|---|---|---|---|---|")
    for k in K_VALUES:
        recs = collected[k]
        n = len(recs)
        row = {"k": k, "n": n}
        for m in ("pair", "uncrossed", "crossed", "chassis", "half"):
            by_parent = {p: [0, 0] for p in range(n_parents)}
            for pi, r in recs:
                by_parent[pi][1] += 1
                if r[m]:
                    by_parent[pi][0] += 1
            row[m] = sum(v[0] for v in by_parent.values()) / n
            row[m + "_se"] = round(cluster_se(by_parent, n_parents), 5)
        row["mean_links"] = round(float(np.mean([r["links"] for _, r in recs])), 2)
        row["mean_food_wired"] = round(float(np.mean([r["food_wired"] for _, r in recs])), 4)
        out["cells"].append(row)
        print(f"| {k} | {row['crossed']:.4f} | {row['crossed_se']:.4f} | {row['uncrossed']:.4f} | "
              f"{row['chassis']:.4f} | {row['mean_links']:.1f} | {row['mean_food_wired']:.3f} |")

    out["seconds"] = round(time.time() - t0, 1)
    with open("runs/RBT-45/deep.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"\nwrote runs/RBT-45/deep.json in {out['seconds']}s")


if __name__ == "__main__":
    main()
