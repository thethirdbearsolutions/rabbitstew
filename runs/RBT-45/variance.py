"""RBT-45 self-audit: are the report's error bars honest?

reach.py quotes a binomial standard error, sqrt(p(1-p)/n) with n = 2000.  That
assumes 2000 independent lineages.  They are not independent: every cell cycles the
same 60 parents about 33 times each, so if the propensity to acquire a pairing
depends on the parent -- and for the *crossed* pairing it plausibly does, since a
crossed path completes in one draw when the parent's global brain already reaches
both effectors -- the true error bar is wider by the design effect.

This measures it.  Lineages are run with the parent index recorded, per-parent rates
are computed, and the honest interval comes from a cluster bootstrap that resamples
*parents* rather than lineages.  Same no-world, no-selection discipline; the readout
is reach.py's, unmodified.

Usage:  python runs/RBT-45/variance.py [--reps 5] [--n 2000]
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
METRICS = ("pair", "uncrossed", "crossed", "half", "chassis")


def cell_id(k, rep):
    return f"var|conventional|add0.15|rem0.1|k{k}|rep{rep}"


def run_chunk(task):
    k, rep, lo, hi = task
    cfg = reach.config()
    pool = reach.parents("conventional")
    mcfg = replace(cfg.mutation, add_link_rate=0.15, remove_link_rate=0.1)
    cid = cell_id(k, rep)
    rows = []
    for i in range(lo, hi):
        rng = np.random.default_rng(np.random.SeedSequence([MASTER_SEED, zlib.crc32(cid.encode()), i]))
        pi = i % len(pool)
        g = pool[pi]
        for _ in range(k):
            g = mutate_controller(g, rng, mcfg)
        r = reach.measure_conventional(synthesize(g, cfg.sim.synthesis))
        rows.append((pi, rep, tuple(bool(r[m]) for m in METRICS)))
    return rows


def cluster_bootstrap(by_parent, n_parents, draws=4000, seed=7):
    """Resample parents with replacement; each parent brings all its lineages."""
    rng = np.random.default_rng(seed)
    hits = np.array([by_parent[p][0] for p in range(n_parents)], dtype=float)
    tot = np.array([by_parent[p][1] for p in range(n_parents)], dtype=float)
    out = np.empty(draws)
    for d in range(draws):
        idx = rng.integers(0, n_parents, n_parents)
        out[d] = hits[idx].sum() / tot[idx].sum()
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=5)
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--ks", type=int, nargs="+", default=[19, 23, 50])
    args = ap.parse_args()

    n_parents = len(reach.parents("conventional"))
    tasks = [(k, rep, lo, min(lo + 100, args.n))
             for k in args.ks for rep in range(args.reps) for lo in range(0, args.n, 100)]
    print(f"{len(args.ks)} depths x {args.reps} replicates x {args.n} lineages, {len(tasks)} chunks", flush=True)

    t0 = time.time()
    out = {"master_seed": MASTER_SEED, "reps": args.reps, "n_per_rep": args.n,
           "parents": n_parents, "depths": {}}
    collected = {k: [] for k in args.ks}
    with Pool(args.workers) as p:
        # map keeps results in task order, so each chunk's depth is known from its task
        for task, chunk in zip(tasks, p.map(run_chunk, tasks, chunksize=1)):
            collected[task[0]].extend(chunk)

    for k, recs in collected.items():
        d = {"n_lineages": len(recs), "metrics": {}}
        for mi, m in enumerate(METRICS):
            by_parent = {p: [0, 0] for p in range(n_parents)}
            per_rep = {r: [0, 0] for r in range(args.reps)}
            for pi, rep, flags in recs:
                by_parent[pi][1] += 1
                per_rep[rep][1] += 1
                if flags[mi]:
                    by_parent[pi][0] += 1
                    per_rep[rep][0] += 1
            n = len(recs)
            hits = sum(v[0] for v in by_parent.values())
            p_hat = hits / n
            binom_se = float(np.sqrt(max(p_hat * (1 - p_hat), 0) / 2000))  # the SE the report quoted, at n=2000
            boot = cluster_bootstrap(by_parent, n_parents)
            # scale the bootstrap (which uses all reps*n lineages) to a single 2000-lineage cell
            cluster_se_full = float(boot.std())
            cluster_se_2000 = cluster_se_full * np.sqrt(args.reps)
            rates = [v[0] / v[1] for v in by_parent.values() if v[1]]
            rep_rates = [v[0] / v[1] for v in per_rep.values()]
            d["metrics"][m] = {
                "p": round(p_hat, 5),
                "binomial_se_at_n2000": round(binom_se, 5),
                "cluster_se_at_n2000": round(float(cluster_se_2000), 5),
                "design_effect": round(float((cluster_se_2000 / binom_se) ** 2), 2) if binom_se > 0 else None,
                "parents_with_zero": int(sum(1 for r in rates if r == 0)),
                "per_parent_rate_min_med_max": [round(float(np.min(rates)), 4),
                                                 round(float(np.median(rates)), 4),
                                                 round(float(np.max(rates)), 4)],
                "replicate_rates": [round(r, 4) for r in rep_rates],
                "per_parent_rates": [round(float(x), 5) for x in rates],
                # P(no lineage of N carries it).  Homogeneous: every lineage draws the
                # pooled p.  Heterogeneous: each lineage draws a parent first, which is
                # what the real run does, and by Jensen this can only raise P(zero).
                "p_zero": {
                    str(N): {
                        "homogeneous": round(float((1 - p_hat) ** N), 4),
                        "heterogeneous": round(float(np.mean([(1 - r) ** N for r in rates])), 4),
                    }
                    for N in (11, 22, 60)
                },
            }
        out["depths"][str(k)] = d

    with open("runs/RBT-45/variance.json", "w") as f:
        json.dump(out, f, indent=1)

    print(f"\n{args.reps} replicates x {args.n} lineages per depth; SEs restated for one 2000-lineage cell\n")
    print("| k | metric | p | binomial SE | cluster SE | design effect | parents never hit | replicate spread |")
    print("|---|---|---|---|---|---|---|---|")
    for k in args.ks:
        for m in METRICS:
            r = out["depths"][str(k)]["metrics"][m]
            lo, hi = min(r["replicate_rates"]), max(r["replicate_rates"])
            print(f"| {k} | {m} | {r['p']:.4f} | {r['binomial_se_at_n2000']:.4f} | {r['cluster_se_at_n2000']:.4f} | "
                  f"{r['design_effect']} | {r['parents_with_zero']}/{out['parents']} | {lo:.4f}–{hi:.4f} |")
    print(f"\nwrote runs/RBT-45/variance.json in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
