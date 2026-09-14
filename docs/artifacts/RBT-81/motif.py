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

Writing e1 + e2 = a*(n1 - n2) + c*(n1 + n2), a is the GRADIENT coefficient (what steers)
and c = (s1 + s2)/2 the COMMON-MODE coefficient (the pirouette term, worth -1.502 items
when it dominates). The audit dose-response, calibrated by installing the motif and
reading a back (calibration.json, median over the 7 robots): a = 16 is the inert boundary
(+0.054, CI straddling zero), a = 32 gives +0.246, a = 64 gives +0.897.

CORRECTION, 2026-09-13: the first version of this script returned s1 - s2, which is 2a, and
compared it against thresholds that are in a units -- so every reported rate was counted at
half the intended gain. Caught by the RBT-8 delegate on RBT-45. Fixed here.

CORRECTION, 2026-09-14 (RBT-81): P was the SIGNED sum of weight products along every path of
up to four links.  That series converges only if the recurrent core's spectral radius is
below 1, and it is above 1 on every committed Pioneer best (1.57-4.92; RBT-67's adversary),
so the depth-4 value was set by where the counting stopped: nine of fourteen bests returned
exactly the depth-1 term, five returned an arbitrary truncation of a divergent series, and
over the drift lineages 100% of those clearing |a| >= 16 moved by more than 20% between
depth 4 and depth 8 (RBT-78's truncation.py).  `a` and `c` are now the DEPTH-1 terms -- the
weight on the direct nose->effector links, exact on every brain -- computed by
``rabbitstew.analysis.steering_terms``.  And the "gradient-dominant" column, |a| > |c|, was
algebraically s1 * s2 < 0: a sign test with no magnitude in it (RBT-78's adversary).  It is
replaced by the BALANCE ratio r = min(|s1|,|s2|) / max(|s1|,|s2|) reported as a number and
the sign of s1 * s2 reported separately; no pass/fail threshold is defined on either.  The
numbers in runs/RBT-45/motif.json and REPORT.md were produced by the earlier version and are
left as reported.

Caveat that still stands: even at depth 1 the brain's tanh means the realised gain depends
on operating point; the audit measured per-effector tanh gains of 0.407 and 0.197 on the
shipped robots, so a given k_steer buys less than its face value.

No library changes here; reach.py is untouched and its cells.json still reproduces.
Usage: ./v/bin/python runs/RBT-45/motif.py [--n 2000]
"""

from __future__ import annotations

import argparse, json, os, sys, time, zlib
from dataclasses import replace
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import reach
from rabbitstew.analysis import steering_terms
from rabbitstew.genetics import mutate_controller
from rabbitstew.synthesis import synthesize

MASTER_SEED = reach.MASTER_SEED
THRESHOLDS = (1, 4, 16, 32, 64)


def steering_gain(ph):
    """Depth-1 (direct-link) coefficients on the steering axis e1 + e2: ``(a, c, r, sign)``.

    ``a`` is the coefficient on (n1 - n2) -- what steers; ``c`` on (n1 + n2) -- the pirouette
    term; ``r`` the balance of the two noses' gains, 1 for a true four-link motif and 0 for a
    single wired nose; ``sign`` is sign(s1 * s2), -1 opposed, +1 aligned, 0 if a nose is unwired.
    ``(None, None, None, None)`` without a food nose and a live effector on both wheels.
    """
    t = steering_terms(ph)
    if t is None:
        return None, None, None, None
    return float(t["a"]), float(t["c"]), float(t["balance"]), int(t["opposed"])


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
        rows.append(steering_gain(synthesize(g, cfg.sim.synthesis)))
    return cid, rows


def summarise(cell, rows):
    rows = [r for r in rows if r[0] is not None]
    a = np.array([r[0] for r in rows])
    r_ = np.array([r[2] for r in rows])
    opposed = np.array([r[3] < 0 for r in rows])
    out = {"kind": cell["kind"], "add": cell["add"], "rem": cell["rem"], "k_mut": cell["k"], "n": len(a),
           "median_abs_a": round(float(np.median(np.abs(a))), 4),
           "p95_abs_a": round(float(np.percentile(np.abs(a), 95)), 3),
           "max_abs_a": round(float(np.abs(a).max()), 3),
           "median_balance_r": round(float(np.median(r_)), 4),
           "frac_opposed": round(float(opposed.mean()), 5)}  # sign(s1*s2) < 0: the retired |a|>|c| test, named for what it is
    for t in THRESHOLDS:
        out[f"frac_a_ge_{t}"] = round(float((a >= t).mean()), 5)  # correct sign
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    cfg = reach.config()

    print("=== what the evolved population itself carries (no mutation); depth-1 terms ===")
    for label, gens in (("final population", None),):
        va, vr, vs = [], [], []
        for g in reach.parents("conventional"):
            a, c, r, s = steering_gain(synthesize(g, cfg.sim.synthesis))
            if a is None:
                continue
            va.append(a); vr.append(r); vs.append(s)
        va, vr, vs = np.array(va), np.array(vr), np.array(vs)
        print(f"  {label}: n={len(va)}  median|a| {np.median(np.abs(va)):.3f}  max|a| {np.abs(va).max():.3f}  "
              f"|a|>=16: {(np.abs(va)>=16).sum()}/{len(va)}  opposed sign: {(vs < 0).sum()}/{len(va)}  median balance r {np.median(vr):.3f}")

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
    json.dump({"master_seed": MASTER_SEED, "depth": 1, "cells": res,
               "seconds": round(time.time() - t0, 1)}, open("runs/RBT-45/motif.json", "w"), indent=1)

    print("\nsigned DEPTH-1 steering gain delivered to the e1+e2 axis by the wheel-nose pair")
    print("(the audit's dose-response: |k|=16 inert, 32 gives +0.246 items, 64 gives +0.897; RBT-67: still rising at 384)\n")
    print("| add | mutations | median |a| | a>=16 (inert bdry) | a>=32 (+0.246) | a>=64 (+0.897) | median balance r | opposed sign |")
    print("|---|---|---|---|---|---|---|---|")
    for r in res:
        print(f"| {r['add']} | {r['k_mut']} | {r['median_abs_a']:.3f} | {100*r['frac_a_ge_16']:.2f}% "
              f"| {100*r['frac_a_ge_32']:.2f}% | {100*r['frac_a_ge_64']:.2f}% | {r['median_balance_r']:.3f} | {100*r['frac_opposed']:.2f}% |")
    print(f"\nwrote runs/RBT-45/motif.json in {time.time()-t0:.0f}s")
