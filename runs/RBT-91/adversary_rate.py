"""RBT-91 adversary probe on the structural-rate measurement (runs/RBT-91/structural_rate.py).

Four checks the decision's flip rests on, none of which the readout answers:

1. WHICH PARENT each arrival descends from.  The lineage generator takes ``pool[i % len(pool)]``,
   so lineage indices 176, 2430 and 3550 on a pool of seven all descend from the same parent.
   Four arrivals from two parents is a smaller sample than "4 in 10,000" reads as.
2. IS THE 92% THE MOTIF'S?  ``small_signal_a`` reads the whole brain's nose->Effector response,
   not the predicate unit's contribution.  Ablate the predicate unit's four links (noses -> k,
   k -> Effectors) and re-read: if the response survives the ablation, the magnitude belongs to
   other wiring and the motif carries none of it.
3. IS 6.3 REMARKABLE?  The realised |a| of every lineage, structure or not, over RBT-78's
   denominator, so the arrival's magnitude can be read against what structureless drift
   produces on the same parents.
4. IS THE STRUCTURAL RATE INVARIANT TO weight_sigma?  The coordinator ruled it is "by
   construction".  The predicate is a sign pattern on summed weights; ``add_link`` draws new
   weights from N(0, 1) whatever sigma is, but inherited links change sign under larger steps.
   Re-count on the same denominator at weight_sigma 0.4 (the operator), 2.0 and 4.0.

Denominator, seeds and predicate are structural_rate.py's, imported, not reimplemented.
No simulation, no world.

Usage: adversary_rate.py [--n 5000] [--workers 4]
"""
import argparse
import importlib.util
import os
import zlib
from dataclasses import replace

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("sr", os.path.join(_HERE, "structural_rate.py"))
sr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sr)
rbt78 = sr.rbt78

from rabbitstew.genetics import mutate_controller
from rabbitstew.synthesis import synthesize

HITS = {"W4b-801-bests": (176, 2430, 3550), "P-801-final60": (109,)}


def lineage(label, i, k=19, add=0.15, rem=0.1, sigma=None):
    cfg, pool = rbt78._load(label)
    mcfg = replace(cfg.mutation, add_link_rate=add, remove_link_rate=rem)
    if sigma is not None:
        mcfg = replace(mcfg, weight_sigma=sigma)
    rng = np.random.default_rng(np.random.SeedSequence([rbt78.MASTER_SEED, zlib.crc32(label.encode()), k, i]))
    g = pool[i % len(pool)]
    for _ in range(k):
        g = mutate_controller(g, rng, mcfg)
    return cfg, pool, g


def chunk(task):
    label, lo, hi, sigma = task
    cfg, pool = rbt78._load(label)
    mcfg = replace(cfg.mutation, add_link_rate=0.15, remove_link_rate=0.1)
    if sigma is not None:
        mcfg = replace(mcfg, weight_sigma=sigma)
    vals, present, flips = [], 0, 0
    for i in range(lo, hi):
        rng = np.random.default_rng(np.random.SeedSequence([rbt78.MASTER_SEED, zlib.crc32(label.encode()), 19, i]))
        g = pool[i % len(pool)]
        for _ in range(19):
            g = mutate_controller(g, rng, mcfg)
        ph = synthesize(g, cfg.sim.synthesis)
        if sigma is None:
            vals.append(abs(sr.small_signal_a(ph)))
        if sr.motif_units(ph):
            present += 1
    return label, sigma, vals, present



def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5000)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()

    print("# RBT-91 adversary: the four arrivals, their parents, the ablation, the background, and weight_sigma\n")

    # 1 + 2: parents and ablation ------------------------------------------------------------
    print("## 1. Which parent each arrival descends from, and 2. whether the magnitude is the motif unit's\n")
    for label, idxs in HITS.items():
        cfg, pool, _ = lineage(label, idxs[0])
        d, how = rbt78.POOLS[label]
        for i in idxs:
            cfg, pool, g = lineage(label, i)
            ph = synthesize(g, cfg.sim.synthesis)
            units = sr.motif_units(ph)
            a_full = sr.small_signal_a(ph)
            parent = pool[i % len(pool)]
            ph_p = synthesize(parent, cfg.sim.synthesis)
            a_parent = sr.small_signal_a(ph_p)
            # ablation: zero the predicate unit's motif links in the runtime brain
            from rabbitstew.brain import RuntimeBrain
            noses = sr._wheel_noses(ph)
            le, re_ = sr.drive_effector_units(ph)
            a_abl = float("nan")
            a_only = float("nan")
            if units:
                k = units[0]
                # measure by editing the phenotype's link list: drop nose->k and k->effector links
                kept = [(s, d_, w) for (s, d_, w) in ph.links
                        if not ((s in noses and d_ == k) or (s == k and (d_ in le or d_ in re_)))]
                only = [(s, d_, w) for (s, d_, w) in ph.links
                        if ((s in noses and d_ == k) or (s == k and (d_ in le or d_ in re_)))]
                saved = ph.links
                ph.links = kept
                a_abl = sr.small_signal_a(ph)
                ph.links = only
                a_only = sr.small_signal_a(ph)
                ph.links = saved
            print(f"  {label} lineage {i:5d}: parent index {i % len(pool)} of {len(pool)} ({parent.name}); "
                  f"parent's bare response {a_parent:+.4f}; lineage full {a_full:+.4f}; "
                  f"motif unit's links removed {a_abl:+.4f}; motif unit's links alone {a_only:+.4f}")
    print("\n  Read: 'links removed' is the response the lineage would have without the predicate unit's motif;")
    print("  'links alone' is the predicate unit's own contribution with everything else silenced.\n")

    # 3: background distribution -------------------------------------------------------------
    print(f"## 3. Realised |a| of EVERY lineage on the denominator (structure or not), n = {a.n} per pool\n")
    from concurrent.futures import ProcessPoolExecutor

    for label in rbt78.POOLS:
        tasks = [(label, lo, min(lo + a.n // a.workers, a.n), None) for lo in range(0, a.n, a.n // a.workers)]
        vals = []
        with ProcessPoolExecutor(a.workers) as ex:
            for _, _, v, _ in ex.map(chunk, tasks):
                vals += v
        v = np.array([x for x in vals if np.isfinite(x)])
        print(f"  {label}: n={len(v)}  median |a| {np.median(v):.3f}  p90 {np.percentile(v, 90):.3f}  p99 {np.percentile(v, 99):.3f}  "
              f"max {v.max():.3f}  >=3.57 (null rung): {(v >= 3.57).sum()}  >=6.87 (paying rung): {(v >= 6.87).sum()}  >=6.33: {(v >= 6.33).sum()}")
    print("\n  Read: how many structureless lineages reach the magnitude the 92% arrival is credited with.\n")

    # 4: weight_sigma --------------------------------------------------------------------------
    print(f"## 4. The structural count on the same denominator at weight_sigma 0.4 (operator), 2.0 and 4.0\n")
    print(f"  {'pool':16s} {'sigma':>6s} {'present':>8s}")
    for sigma in (None, 2.0, 4.0):
        for label in rbt78.POOLS:
            tasks = [(label, lo, min(lo + a.n // a.workers, a.n), sigma) for lo in range(0, a.n, a.n // a.workers)]
            present = 0
            with ProcessPoolExecutor(a.workers) as ex:
                for _, _, _, p in ex.map(chunk, tasks):
                    present += p
            print(f"  {label:16s} {0.4 if sigma is None else sigma:6.1f} {present:8d}")
    print("\n  Read: if the count moves with sigma the rate is not invariant by construction; the predicate is a")
    print("  sign pattern and inherited links change sign under larger steps.")


if __name__ == "__main__":
    main()
