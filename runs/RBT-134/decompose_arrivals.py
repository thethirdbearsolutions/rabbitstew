"""RBT-134 pricing probe: WHICH factor withholds the gain on RBT-91's drift arrivals?

Exploratory, design-time only (RBT-134 DESIGN.md section 2). No simulation, no world, no
selection, and it reads nothing but RBT-91's committed readouts and RBT-78's committed pools.

RBT-91 measured the predicate unit's links-alone response on every structural arrival and found
0 of 84 at or above the paying rung (docs/rbt-91-weight-scale-decision.md:30). The response is a
chain: nose links in -> the interneuron's transfer slope at its bias -> links out -> each drive
Effector's tanh slope at its bias. This regenerates each arrival from its lineage index (the seed
is a function of the index alone, structural_rate.py:199-203, so nothing else is re-run) and
re-reads the links-alone response under counterfactual edits of ONE phenotype at a time:

  as-is       structural_rate.links_alone_a, unchanged (must reproduce the committed readout)
  tanh        the predicate unit's transfer function set to tanh
  bk0         the predicate unit's bias set to 0
  bE0         every drive Effector's bias set to 0
  tk, kE, tE  the pairs (tanh + bk0), (bk0 + bE0), (tanh + bE0)
  unit        all three: what the four links alone could deliver at a unit slope

Each counterfactual is an upper bound on what an operator change aimed at that factor could buy
an arrival that already exists; none of them is an operator. The links' own product is the last
column, and it is the one no slope or bias change can raise.

Usage: decompose_arrivals.py --readout docs/artifacts/RBT-91-alone-baseline.txt [--sigma 0.4]
"""
import argparse
import copy
import importlib.util
import os
import re
import zlib
from dataclasses import replace

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("sr", os.path.join(_HERE, "..", "RBT-91", "structural_rate.py"))
sr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sr)
rbt78 = sr.rbt78

from rabbitstew.fixed import drive_effector_units
from rabbitstew.genetics import mutate_controller
from rabbitstew.synthesis import synthesize

PAYING = 6.8664  # RBT-91 as printed; a WHOLE-BRAIN reading of the installed motif (ERRATA.md:142, H41)
#: like-for-like own-link rungs (runs/RBT-72-adversary/probe_rung.txt; runs/RBT-104/drift_reach.py:17-20)
RUNGS = {"a16 6.2831": 6.2831, "a32 12.5236": 12.5236, "a64 24.7145": 24.7145}


def regenerate(label, i, k, add, rem, sigma):
    cfg, pool = rbt78._load(label)
    mcfg = replace(cfg.mutation, add_link_rate=add, remove_link_rate=rem)
    if sigma is not None:
        mcfg = replace(mcfg, weight_sigma=sigma)
    rng = np.random.default_rng(np.random.SeedSequence([rbt78.MASTER_SEED, zlib.crc32(label.encode()), k, i]))
    g = pool[i % len(pool)]
    for _ in range(k):
        g = mutate_controller(g, rng, mcfg)
    return synthesize(g, cfg.sim.synthesis)


def edited(ph, k, func=None, bk=None, bE=None):
    ph = copy.deepcopy(ph)
    if func is not None:
        ph.units[k].unit.func = func
    if bk is not None:
        ph.units[k].unit.bias = bk
    if bE is not None:
        le, re_ = drive_effector_units(ph)
        for e in le + re_:
            ph.units[e].unit.bias = bE
    return ph


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--readout", required=True)
    ap.add_argument("--sigma", type=float, default=None)
    ap.add_argument("--k", type=int, default=19)
    a = ap.parse_args()
    hits = re.findall(r"(\S+) lineage (\d+): \d+ unit\(s\), LINKS ALONE ([+-][\d.]+)", open(a.readout).read())
    rows = []
    for label, i, committed in hits:
        ph = regenerate(label, int(i), a.k, 0.15, 0.1, a.sigma)
        units = sr.motif_units(ph)
        k = units[0]
        nL, nR = sr._wheel_noses(ph)
        le, re_ = drive_effector_units(ph)
        w = {}
        for s, d, wt in ph.links:
            w[(s, d)] = w.get((s, d), 0.0) + wt
        uL, uR = w[(nL, k)], w[(nR, k)]
        vL, vR = w.get((k, le[0]), 0.0), w.get((k, re_[0]), 0.0)
        bk = ph.units[k].unit.bias
        func = ph.units[k].unit.func
        bEs = [ph.units[e].unit.bias for e in le + re_]
        r = dict(label=label, i=int(i), func=func, bk=bk, bE=max(abs(x) for x in bEs),
                 committed=float(committed),
                 asis=sr.links_alone_a(ph, k),
                 tanh=sr.links_alone_a(edited(ph, k, func="tanh"), k),
                 bk0=sr.links_alone_a(edited(ph, k, bk=0.0), k),
                 bE0=sr.links_alone_a(edited(ph, k, bE=0.0), k),
                 unit=sr.links_alone_a(edited(ph, k, func="tanh", bk=0.0, bE=0.0), k),
                 tk=sr.links_alone_a(edited(ph, k, func="tanh", bk=0.0), k),
                 kE=sr.links_alone_a(edited(ph, k, bk=0.0, bE=0.0), k),
                 tE=sr.links_alone_a(edited(ph, k, func="tanh", bE=0.0), k),
                 prod=(uL - uR) / 2.0 * (vL + vR) / 2.0, u=(abs(uL) + abs(uR)) / 2, v=(abs(vL) + abs(vR)) / 2)
        rows.append(r)
    print(f"# RBT-134 decomposition of RBT-91 arrivals: {a.readout}  (sigma={a.sigma or 0.4})\n")
    print(f"| label | lineage | func | b_k | max|b_E| | as-is | committed | tanh | b_k=0 | b_E=0 | slope=1 | (uL-uR)/2*(vL+vR)/2 |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for r in rows:
        print(f"| {r['label']} | {r['i']} | {r['func']} | {r['bk']:+.2f} | {r['bE']:.2f} | {r['asis']:+.4f} | "
              f"{r['committed']:+.4f} | {r['tanh']:+.4f} | {r['bk0']:+.4f} | {r['bE0']:+.4f} | {r['unit']:+.4f} | {r['prod']:+.4f} |")
    n = len(rows)
    rep = sum(1 for r in rows if abs(r["asis"] - r["committed"]) < 5e-5)
    print(f"\nreproduces committed readout: {rep} of {n}")
    funcs = {}
    for r in rows:
        funcs[r["func"]] = funcs.get(r["func"], 0) + 1
    print("predicate unit transfer functions: " + ", ".join(f"{f} {c}" for f, c in sorted(funcs.items(), key=lambda x: -x[1])))
    print("  (b_k=0 on a `sign` unit reads ~1/drive: sign(+-d) is +-1 at any d, a probe artifact, not a gain;")
    print("   so b_k=0 columns are also given over non-`sign` units only)")
    for col in ("asis", "tanh", "bk0", "bE0", "tk", "kE", "tE", "unit"):
        v = np.array([abs(r[col]) for r in rows])
        vs = np.array([abs(r[col]) for r in rows if r["func"] != "sign"])
        if col in ("bk0", "kE"):
            print(f"  {col:6s} non-sign: >= rung {int((vs >= PAYING).sum())} of {len(vs)}; median {np.median(vs):.4f}")
        print(f"  {col:6s}: >= rung {int((v >= PAYING).sum())} of {n}; >= rung/2 {int((v >= PAYING / 2).sum())}; "
              f"median {np.median(v):.4f}; max {v.max():.4f}")
    print("\n  against the own-link rungs (ERRATA H41), excluding nothing:")
    for col in ("asis", "tk", "kE", "unit"):
        v = np.array([abs(r[col]) for r in rows if r["func"] != "sign" or col in ("asis", "unit")])
        print(f"  {col:6s} (n={len(v)}): " + "; ".join(f"{name} {int((v >= x).sum())}" for name, x in RUNGS.items()))
    bk = np.array([abs(r["bk"]) for r in rows]); bE = np.array([r["bE"] for r in rows])
    print(f"  |b_k| median {np.median(bk):.2f} p90 {np.quantile(bk, .9):.2f}; max|b_E| median {np.median(bE):.2f} p90 {np.quantile(bE, .9):.2f}")
    # THE SLOPE BOUND.  With links alone the response is (uL-uR)/2 * f'(b_k) * mean over the drive Effectors of
    # v_E sech^2(b_E + v_E f(b_k)), and the predicate makes v_L, v_R the same sign, so |a| <= |product| * max f'.
    # max f' at the probe (SETTLE = 12 ticks from rest): tanh, sin, relu 1; integrate 2(1 - 0.9^12) = 1.436;
    # abs (even), differentiate (0 once settled) and sign (0 off b_k = 0 exactly) 0.  So for ANY operator change
    # that leaves these lineages' link weights and structure as they are and moves only biases, this is the most
    # that can reach each rung.
    fmax = {"tanh": 1.0, "sin": 1.0, "relu": 1.0, "integrate": 2 * (1 - 0.9 ** 12), "abs": 0.0, "differentiate": 0.0, "sign": 0.0}
    print("\n  SLOPE BOUND (|product| x max f'; any bias-only change on these links): " + "; ".join(
        f"{name} <= {sum(1 for r in rows if fmax[r['func']] * abs(r['prod']) >= x)}" for name, x in RUNGS.items()))
    p = np.array([abs(r["prod"]) for r in rows])
    print(f"  link product |(uL-uR)/2*(vL+vR)/2|: median {np.median(p):.4f}; max {p.max():.4f}; >= rung {int((p >= PAYING).sum())}")
    u = np.array([r["u"] for r in rows]); v = np.array([r["v"] for r in rows])
    print(f"  mean |w| per link: in median {np.median(u):.3f} max {u.max():.3f}; out median {np.median(v):.3f} max {v.max():.3f}")


if __name__ == "__main__":
    main()
