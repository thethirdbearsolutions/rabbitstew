"""RBT-78 adversary probe: the two lines the author flagged as unchecked.

Named adversary: the RBT-8 delegate (RBT-62's author), assigned by the coordinator on the
grounds that being party to the disagreement is the reason to attack the reconciliation, not
an objection to it. Attack B is aimed at a criterion of my own.

A. IS "HAS AT LEAST ONE OUTGOING LINK" THE RIGHT MATCHING VARIABLE?
   The report matches food and agent pathways on a binary: does the pair have any outgoing
   link. If the pathways still differ in link COUNT or total WEIGHT among the lineages that
   pass that filter, the matched comparison is still confounded, and the direction of the
   residual says whether the report's conclusion is understated or overstated.

B. WHAT DOES |a| > |c| COLLAPSE?
   Claim under test: |a| > |c| is not a graded measure of antisymmetry at all. With
   a = (s1-s2)/2 and c = (s1+s2)/2,

       |a| > |c|  <=>  (s1-s2)^2 > (s1+s2)^2  <=>  -4*s1*s2 > 0  <=>  s1*s2 < 0

   so the criterion is EXACTLY "the two noses' steering gains have opposite signs", with zero
   magnitude content. s1 = +100, s2 = -0.001 passes it while being 99.999% a one-nose
   pirouette. This asserts the equivalence numerically, then measures how balanced the
   passing lineages actually are, via

       r = min(|s1|,|s2|) / max(|s1|,|s2|)

   which is 1 for a true 4-link antisymmetric motif and -> 0 for an effectively single-nose
   circuit. Recovering s1 = a + c and s2 = c - a needs no change to reconcile.py's terms().

Usage: adversary.py [--n 5000] [--workers 4]
"""
from __future__ import annotations

import argparse, os, sys, zlib
from dataclasses import replace
from multiprocessing import Pool

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from reconcile import MASTER_SEED, POOLS, THRESHOLDS, _load, _nose_eff, terms

from rabbitstew.genetics import mutate_controller
from rabbitstew.synthesis import synthesize


def pathway_stats(ph, source):
    """(n_links, total_abs_weight) leaving the two sensors of this pair."""
    nose, _ = _nose_eff(ph, source)
    idx = set(nose.values())
    links = [(s, d, w) for s, d, w in ph.links if s in idx]
    return len(links), float(sum(abs(w) for _, _, w in links))


def chunk(task):
    label, lo, hi, k, add, rem = task
    cfg, pool = _load(label)
    mcfg = replace(cfg.mutation, add_link_rate=add, remove_link_rate=rem)
    rows = []
    for i in range(lo, hi):
        rng = np.random.default_rng(np.random.SeedSequence([MASTER_SEED, zlib.crc32(label.encode()), k, i]))
        g = pool[i % len(pool)]
        for _ in range(k):
            g = mutate_controller(g, rng, mcfg)
        ph = synthesize(g, cfg.sim.synthesis)
        t = terms(ph)
        if t is None:
            continue
        ctrl = terms(ph, source="agent")
        fn, fw = pathway_stats(ph, "food")
        an, aw = pathway_stats(ph, "agent")
        rows.append((t["path"][0], t["path"][1],
                     (ctrl["path"][0] if ctrl else np.nan), (ctrl["path"][1] if ctrl else np.nan),
                     fn, fw, an, aw))
    return rows


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--n", type=int, default=5000)
    p.add_argument("--k", type=int, default=19)
    p.add_argument("--add", type=float, default=0.15)
    p.add_argument("--rem", type=float, default=0.1)
    p.add_argument("--workers", type=int, default=4)
    args = p.parse_args()

    # ---- B, part 1: the algebraic equivalence, asserted before anything is measured ------
    rng = np.random.default_rng(0)
    s1, s2 = rng.normal(0, 10, 200000), rng.normal(0, 10, 200000)
    a, c = (s1 - s2) / 2, (s1 + s2) / 2
    assert np.array_equal(np.abs(a) > np.abs(c), s1 * s2 < 0), "equivalence failed"
    print("=== B1: |a| > |c|  ==  sign(s1) != sign(s2), asserted on 200,000 random pairs: EXACT ===")
    print("    the criterion carries zero magnitude information; it is a sign test.\n")

    for label in POOLS:
        cfg, pool = _load(label)
        tasks = [(label, lo, min(lo + 50, args.n), args.k, args.add, args.rem)
                 for lo in range(0, args.n, 50)]
        rows = []
        with Pool(args.workers) as pp:
            for r in pp.imap_unordered(chunk, tasks, chunksize=1):
                rows.extend(r)
        ap = np.array([r[0] for r in rows]); cp = np.array([r[1] for r in rows])
        ac = np.array([r[2] for r in rows]); cc = np.array([r[3] for r in rows])
        fn = np.array([r[4] for r in rows]); fw = np.array([r[5] for r in rows])
        an = np.array([r[6] for r in rows]); aw = np.array([r[7] for r in rows])
        print(f"=== {label}  (n={len(rows)}) ===")

        # ---- A: is "wired at all" enough? -------------------------------------------
        both = (fn > 0) & (an > 0)
        print(f"  A. matching variable. both pathways wired: {both.sum()}/{len(rows)} "
              f"({100*both.mean():.1f}%)")
        print(f"     among those, mean outgoing LINKS   food {fn[both].mean():.3f}  "
              f"agent {an[both].mean():.3f}   ratio {fn[both].mean()/max(an[both].mean(),1e-9):.3f}")
        print(f"     among those, mean total |WEIGHT|   food {fw[both].mean():.3f}  "
              f"agent {aw[both].mean():.3f}   ratio {fw[both].mean()/max(aw[both].mean(),1e-9):.3f}")
        # the strictest available match: identical link count, pair by pair
        eq = both & (fn == an)
        print(f"     STRICT match (identical link count): {eq.sum()} lineages")
        for t in THRESHOLDS:
            print(f"       |a|>={t:<3} food {100*(np.abs(ap[eq])>=t).mean():6.2f}%   "
                  f"agent {100*(np.abs(ac[eq])>=t).mean():6.2f}%")

        # ---- B, part 2: how balanced are the "gradient-dominant" lineages? -----------
        s1p, s2p = ap + cp, cp - ap
        r = np.minimum(np.abs(s1p), np.abs(s2p)) / np.maximum(np.abs(s1p), np.abs(s2p))
        for t in (32, 64):
            sel = (ap >= t) & (np.abs(ap) > np.abs(cp))
            if not sel.any():
                print(f"  B. a>={t} AND |a|>|c|: 0 lineages")
                continue
            rr = r[sel]
            print(f"  B. a>={t} AND |a|>|c|: {sel.sum()} lineages; balance r = "
                  f"min|s|/max|s| (1.0 = true motif)")
            print(f"       median r {np.median(rr):.4f}   r<0.5 {100*(rr<0.5).mean():.1f}%   "
                  f"r<0.1 {100*(rr<0.1).mean():.1f}%   r<0.01 {100*(rr<0.01).mean():.1f}%")
            print(f"       deciles {np.round(np.percentile(rr,[10,25,50,75,90]),4).tolist()}")
        print()

# --------------------------------------------------------------------------- #
# B, part 3: |a| > |c| weights the two terms equally. RBT-61 did not measure them
# equal. Its dose-response gives a = 64 -> +0.897 items; the withdrawn spike's pure
# common mode at w = 32 (c = 64, a ~ 0) -> -1.502. Linearising both, which is crude
# and stated as such, the pirouette costs ~1.67x per unit what the gradient earns:
#     net ~ (0.897/64)*a - (1.502/64)*|c|,  break-even at a/|c| = 1.674
# So |a| > |c| -- break-even at a/|c| = 1.0 -- passes a wide band of circuits that
# these slopes call net-harmful. Run as: PAYOFF=1 adversary.py
# --------------------------------------------------------------------------- #
if __name__ == "__main__" and os.environ.get("PAYOFF"):
    GAIN, COST, BREAKEVEN = 0.897 / 64, 1.502 / 64, 1.502 / 0.897
    print(f"\n=== B3: payoff-weighted, slopes +{GAIN:.5f}/unit a, -{COST:.5f}/unit |c| "
          f"(break-even a/|c| = {BREAKEVEN:.3f}) ===")
    for label in POOLS:
        cfg, pool = _load(label)
        tasks = [(label, lo, min(lo + 50, args.n), args.k, args.add, args.rem)
                 for lo in range(0, args.n, 50)]
        rows = []
        with Pool(args.workers) as pp:
            for r in pp.imap_unordered(chunk, tasks, chunksize=1):
                rows.extend(r)
        ap = np.array([r[0] for r in rows]); cp = np.array([r[1] for r in rows])
        fn = np.array([r[4] for r in rows]); an = np.array([r[6] for r in rows])
        ac = np.array([r[2] for r in rows])
        both = (fn > 0) & (an > 0); eq = both & (fn == an)
        print(f"  {label}: strict-match n = {eq.sum()}; counts at each threshold")
        for t in THRESHOLDS:
            print(f"    |a|>={t:<3} food {int((np.abs(ap[eq])>=t).sum()):3d}/{eq.sum()}   "
                  f"agent {int((np.abs(ac[eq])>=t).sum()):3d}/{eq.sum()}")
        sel = (ap >= 32) & (np.abs(ap) > np.abs(cp))
        if sel.any():
            ratio = np.abs(ap[sel]) / np.maximum(np.abs(cp[sel]), 1e-12)
            net = GAIN * ap[sel] - COST * np.abs(cp[sel])
            print(f"    of the {sel.sum()} lineages passing a>=32 AND |a|>|c|:")
            print(f"      a/|c| median {np.median(ratio):.4f}, max {ratio.max():.4f}; "
                  f"clearing the {BREAKEVEN:.2f} break-even: {int((ratio > BREAKEVEN).sum())}")
            print(f"      estimated net items: median {np.median(net):+.4f}, "
                  f"best {net.max():+.4f}; net-positive {int((net > 0).sum())}/{sel.sum()}")
