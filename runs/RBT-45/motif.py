"""RBT-45 recount: does the operator ever propose the motif that actually pays?

RBT-45 measured the operator's reach against a 2-link "crossed" pattern (each wheel
nose into the OTHER wheel's effector). The sim audit (runs/sim-audit/) showed that on
this body the two wheel hinges are antiparallel, so effector SUM is the steering axis
and effector DIFFERENCE is the throttle. The 2-link crossed pattern therefore puts the
common mode on the steering axis: it is a spinner, measured at -1.502 items, 0/7 robots.
What steers is a 4-link antisymmetric motif, +0.897 items, 7/7.

So RBT-45's reach numbers count the wrong thing, and its classifier could not have seen
the right one anyway: it builds influence from abs(w), and the working motif is DEFINED
by a sign pattern; and it clamps each link at 3.0 while the circuit needs a gain of 16-64.

This recounts the same drift process against the quantity that decides whether a robot
steers, with no simulation at all:

    a = ( [P(n1->e1) + P(n1->e2)] - [P(n2->e1) + P(n2->e2)] ) / 2

where P is the SIGNED sum of weight products along every path of up to four links, with NO
per-link clamp. Writing e1 + e2 = a*(n1 - n2) + c*(n1 + n2), a is the GRADIENT coefficient
(what steers) and c = (s1 + s2)/2 the COMMON-MODE coefficient (the pirouette term, worth
-1.502 items when it dominates). The audit dose-response, calibrated by installing the motif
and reading a back (calibration.json, median over the 7 robots): a = 16 is the inert boundary
(+0.054, CI straddling zero), a = 32 gives +0.246, a = 64 gives +0.897.

CORRECTION, 2026-09-13: the first version of this script returned s1 - s2, which is 2a, and
compared it against thresholds that are in a units -- so every reported rate was counted at
half the intended gain. Caught by the RBT-8 delegate on RBT-45. Fixed here.

Caveat stated up front: this is a linearisation. The brain's tanh means the realised gain
depends on operating point; the audit measured per-effector tanh gains of 0.407 and 0.197
on the shipped robots, so a given k_steer buys less than its face value. The thresholds
below should be read as a permissive upper bound on reachability.

No library changes; reach.py is untouched and its cells.json still reproduces.
Usage: ./v/bin/python runs/RBT-45/motif.py [--n 2000]
"""

from __future__ import annotations

import argparse, json, os, sys, time, zlib
from dataclasses import replace
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import reach
from rabbitstew.genetics import mutate_controller
from rabbitstew.genotype import JointType
from rabbitstew.synthesis import synthesize

MASTER_SEED = reach.MASTER_SEED
DEPTH = 4
THRESHOLDS = (1, 4, 16, 32, 64)


def steering_gain(ph):
    """Signed coefficient on (n1 - n2) arriving at the steering axis e1 + e2."""
    n = len(ph.units)
    nose, eff = {}, {}
    for i, u in enumerate(ph.units):
        if u.part in (1, 2) and u.unit.kind == "sensor" and u.unit.source == "food":
            nose[u.part] = i
        if u.part in (1, 2) and u.unit.kind == "effector":
            eff[u.part] = i
    if len(nose) != 2 or len(eff) != 2:
        return None, None
    M = np.zeros((n, n))
    for s, d, w in ph.links:
        M[d, s] += w                      # SIGNED, and no 3.0 clamp
    # signed path sums up to DEPTH links, from each nose
    out = {}
    for part, si in nose.items():
        v = np.zeros(n); v[si] = 1.0
        tot = np.zeros(n)
        for _ in range(DEPTH):
            v = M @ v
            tot += v
            if not v.any():
                break
        out[part] = tot
    # e1 + e2 = s1*n1 + s2*n2 = a*(n1 - n2) + c*(n1 + n2), exactly, whatever the path structure.
    # a is the GRADIENT coefficient (what steers); c is the COMMON-MODE coefficient (the
    # pirouette term, worth -1.502 items when it dominates).
    s1 = out[1][eff[1]] + out[1][eff[2]]
    s2 = out[2][eff[1]] + out[2][eff[2]]
    a = (s1 - s2) / 2.0
    c = (s1 + s2) / 2.0
    return float(a), float(c)


def cell_id(c):
    return f"motif|{c['kind']}|add{c['add']}|rem{c['rem']}|k{c['k']}"


def run_chunk(task):
    cell, lo, hi = task
    cfg = reach.config()
    pool = reach.parents(cell["kind"])
    mcfg = replace(cfg.mutation, add_link_rate=cell["add"], remove_link_rate=cell["rem"])
    cid = cell_id(cell)
    rows = []
    for i in range(lo, hi):
        rng = np.random.default_rng(np.random.SeedSequence([MASTER_SEED, zlib.crc32(cid.encode()), i]))
        g = pool[i % len(pool)]
        for _ in range(cell["k"]):
            g = mutate_controller(g, rng, mcfg)
        a, c = steering_gain(synthesize(g, cfg.sim.synthesis))
        rows.append((a, c))
    return cid, rows


def summarise(cell, rows):
    a = np.array([r[0] for r in rows if r[0] is not None])
    c = np.array([r[1] for r in rows if r[0] is not None])
    dom = np.abs(a) > np.abs(c)          # gradient beats common mode on the steering axis
    out = {"kind": cell["kind"], "add": cell["add"], "rem": cell["rem"], "k_mut": cell["k"], "n": len(a),
           "median_abs_a": round(float(np.median(np.abs(a))), 4),
           "p95_abs_a": round(float(np.percentile(np.abs(a), 95)), 3),
           "max_abs_a": round(float(np.abs(a).max()), 3),
           "frac_gradient_dominant": round(float(dom.mean()), 5)}
    for t in THRESHOLDS:
        out[f"frac_a_ge_{t}"] = round(float((a >= t).mean()), 5)                  # correct sign
        out[f"frac_a_ge_{t}_dominant"] = round(float(((a >= t) & dom).mean()), 5) # and gradient-dominant
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    cfg = reach.config()

    print("=== what the evolved population itself carries (no mutation) ===")
    for label, gens in (("final population", None),):
        va, vc = [], []
        for g in reach.parents("conventional"):
            a, c = steering_gain(synthesize(g, cfg.sim.synthesis))
            va.append(a); vc.append(c)
        va, vc = np.array(va), np.array(vc)
        dom = np.abs(va) > np.abs(vc)
        print(f"  {label}: n={len(va)}  median|a| {np.median(np.abs(va)):.3f}  max|a| {np.abs(va).max():.3f}  "
              f"|a|>=16: {(np.abs(va)>=16).sum()}/{len(va)}  gradient-dominant: {dom.sum()}/{len(va)}")

    cells = [{"kind": "conventional", "add": a, "rem": 0.1, "k": kk, "n": args.n}
             for a, kk in [(0.15, 19), (0.15, 23), (0.15, 50), (0.15, 200),
                           (0.3, 20), (0.6, 20), (1.0, 20), (1.0, 50)]]
    by = {cell_id(c): c for c in cells}
    tasks = [(c, lo, min(lo + 50, c["n"])) for c in cells for lo in range(0, c["n"], 50)]
    print(f"\n{len(cells)} cells x {args.n} lineages, {len(tasks)} chunks", flush=True)
    t0 = time.time()
    got = {cid: [] for cid in by}
    with Pool(args.workers) as p:
        for cid, rows in p.imap_unordered(run_chunk, tasks, chunksize=1):
            got[cid].extend(rows)

    res = [summarise(by[cid], got[cid]) for cid in by]
    res.sort(key=lambda r: (r["add"], r["k_mut"]))
    json.dump({"master_seed": MASTER_SEED, "depth": DEPTH, "cells": res,
               "seconds": round(time.time() - t0, 1)}, open("runs/RBT-45/motif.json", "w"), indent=1)

    print("\nsigned steering gain delivered to the e1+e2 axis by the wheel-nose pair")
    print("(the audit's dose-response: |k|=16 inert, 32 gives +0.246 items, 64 gives +0.897)\n")
    print("| add | mutations | median |a| | a>=16 (inert bdry) | a>=32 (+0.246) | a>=64 (+0.897) | a>=32 AND gradient-dominant |")
    print("|---|---|---|---|---|---|")
    for r in res:
        print(f"| {r['add']} | {r['k_mut']} | {r['median_abs_a']:.3f} | {100*r['frac_a_ge_16']:.2f}% "
              f"| {100*r['frac_a_ge_32']:.2f}% | {100*r['frac_a_ge_64']:.2f}% | {100*r['frac_a_ge_32_dominant']:.2f}% |")
    print(f"\nwrote runs/RBT-45/motif.json in {time.time()-t0:.0f}s")
