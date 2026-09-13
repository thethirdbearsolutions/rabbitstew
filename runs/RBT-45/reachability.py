"""RBT-45 follow-up: did the run evolve *away* from being able to propose a pairing?

§6.4 of my report flagged, without measuring it, that the drift baseline starts from
the run's converged endpoint genotypes rather than its founders, and that founders
might give a different number.  §6.5 then showed parent identity carries a design
effect of 2-9, so "which genotype you start from" is not a footnote.

That turns the caveat into a question worth asking directly: **does a genotype's
propensity to have a pairing proposed change over the 600 seasons?**  If late
genotypes propose pairings less readily than early ones, selection has not removed
the pairing -- it has moved the population into a region where the pairing is harder
for the operator to reach.  That is a different claim from either possibility in the
ticket, it bears on whether RBT-42's operator would even help a *converged*
population, and it needs no world.

Method: each saved genotype is used as the sole parent of its own batch of lineages,
k = 19 mutations of drift at the default operator, no selection.  So each genotype
gets its own p, and the comparison is between groups of genotypes -- bootstrapped
over genotypes, not lineages, per §6.5.

Usage:  python runs/RBT-45/reachability.py [--n 500] [--k 19]
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import time
import zlib
from dataclasses import replace
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import reach
from rabbitstew.genetics import mutate_controller
from rabbitstew.genotype import Genotype
from rabbitstew.synthesis import synthesize

MASTER_SEED = reach.MASTER_SEED
METRICS = ("pair", "uncrossed", "crossed", "half", "chassis")


def genotypes():
    """(group, label, genotype) for every saved conventional genotype in RBT-23."""
    out = []
    for path in sorted(glob.glob(os.path.join(reach.RUN_DIR, "conventional", "best_gen*.json"))):
        gen = int(re.search(r"best_gen(\d+)", path).group(1))
        out.append(("best", gen, Genotype.load(path)))
    for i, g in enumerate(reach.parents("conventional")):
        out.append(("final", i, g))
    return out


def run_one(task):
    group, label, k, n = task
    cfg = reach.config()
    mcfg = replace(cfg.mutation, add_link_rate=0.15, remove_link_rate=0.1)
    if group == "best":
        g0 = Genotype.load(os.path.join(reach.RUN_DIR, "conventional", f"best_gen{label:04d}.json"))
    else:
        g0 = reach.parents("conventional")[label]
    cid = f"rch|{group}|{label}|k{k}"
    hits = {m: 0 for m in METRICS}
    links = []
    for i in range(n):
        rng = np.random.default_rng(np.random.SeedSequence([MASTER_SEED, zlib.crc32(cid.encode()), i]))
        g = g0
        for _ in range(k):
            g = mutate_controller(g, rng, mcfg)
        r = reach.measure_conventional(synthesize(g, cfg.sim.synthesis))
        for m in METRICS:
            if r[m]:
                hits[m] += 1
        links.append(r["links"])
    base = reach.measure_conventional(synthesize(g0, cfg.sim.synthesis))
    return {
        "group": group, "label": label, "n": n,
        **{m: hits[m] / n for m in METRICS},
        "parent_links": base["links"],
        "parent_half": bool(base["half"]),
        "parent_chassis_infl": base["chassis_infl"],
        "mean_links": round(float(np.mean(links)), 2),
    }


def boot_diff(a, b, draws=10000, seed=11):
    """Bootstrap over genotypes: mean(b) - mean(a), and the share of draws below zero."""
    rng = np.random.default_rng(seed)
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = np.empty(draws)
    for i in range(draws):
        d[i] = rng.choice(b, len(b)).mean() - rng.choice(a, len(a)).mean()
    return float(d.mean()), (float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))), float((d < 0).mean())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=500)
    ap.add_argument("--k", type=int, default=19)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    tasks = [(grp, lab, args.k, args.n) for grp, lab, _ in genotypes()]
    print(f"{len(tasks)} genotypes x {args.n} lineages at k={args.k}", flush=True)
    t0 = time.time()
    with Pool(args.workers) as p:
        rows = p.map(run_one, tasks, chunksize=1)

    bests = sorted([r for r in rows if r["group"] == "best"], key=lambda r: r["label"])
    final = [r for r in rows if r["group"] == "final"]
    early = [r for r in bests if r["label"] <= 90]
    late = [r for r in bests if r["label"] >= 500]

    out = {"master_seed": MASTER_SEED, "k": args.k, "n_per_genotype": args.n,
           "rows": rows, "comparisons": {}}

    print(f"\nper-genotype drift rates at k={args.k}, default operator, {args.n} lineages each\n")
    print("| group | metric | n genotypes | mean p | min | max | spread |")
    print("|---|---|---|---|---|---|---|")
    for name, grp in (("bests gen 0-90", early), ("bests gen 500-590", late), ("final population", final)):
        for m in ("pair", "uncrossed", "crossed"):
            v = [r[m] for r in grp]
            print(f"| {name} | {m} | {len(grp)} | {np.mean(v):.4f} | {min(v):.4f} | {max(v):.4f} | "
                  f"{max(v) - min(v):.4f} |")

    print(f"\nearly (gen 0-90, n={len(early)}) vs late (gen 500-590, n={len(late)}), "
          f"bootstrapped over genotypes:\n")
    print("| metric | early | late | late - early | 95% CI | P(late < early) |")
    print("|---|---|---|---|---|---|")
    for m in METRICS:
        a = [r[m] for r in early]
        b = [r[m] for r in late]
        d, ci, pneg = boot_diff(a, b)
        out["comparisons"][m] = {"early": round(float(np.mean(a)), 5), "late": round(float(np.mean(b)), 5),
                                 "diff": round(d, 5), "ci95": [round(c, 5) for c in ci],
                                 "p_late_below_early": round(pneg, 4)}
        print(f"| {m} | {np.mean(a):.4f} | {np.mean(b):.4f} | {d:+.4f} | "
              f"[{ci[0]:+.4f}, {ci[1]:+.4f}] | {pneg:.3f} |")

    gens = np.array([r["label"] for r in bests], float)
    print("\ntrend across all 60 bests (Spearman rho vs season):")
    for m in METRICS:
        v = np.array([r[m] for r in bests], float)
        rk_g, rk_v = gens.argsort().argsort(), v.argsort().argsort()
        rho = float(np.corrcoef(rk_g, rk_v)[0, 1])
        out.setdefault("trend", {})[m] = round(rho, 4)
        print(f"   {m:10s} rho = {rho:+.3f}")

    out["seconds"] = round(time.time() - t0, 1)
    with open("runs/RBT-45/reachability.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"\nwrote runs/RBT-45/reachability.json in {out['seconds']}s")


if __name__ == "__main__":
    main()
