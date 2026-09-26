"""RBT-81 adversary: does the depth-1 term suffice, or does the instrument still need a
behavioural column? Testing my own RBT-78 recommendation before repeating it.

On RBT-78 I reported that depth 1 correlates +0.985 with the network's realised steering
response where depth 4 gives +0.35 and depth 8 gives -0.32, and proposed adding a measured
small-signal response to this instrument. That +0.985 was computed over fourteen committed
bests of which EIGHT have no direct nose->effector wiring at all and contribute (0, 0). Three
or four informative points cannot support a correlation, and a recommendation resting on it
should not be repeated without a real denominator.

So: drift lineages from the same pools and the same process RBT-78 used, keeping the ones that
actually carry direct wiring, and comparing for each

    a           the depth-1 gradient term, what RBT-81 now reports
    measured    the network's own steering response to a small nose differential, run to a
                fixed point through the real recurrent update with tanh in place

If they track, the depth-1 term is sufficient and my proposal is redundant surface. If they
come apart, the instrument is still blind to something and the column is worth its cost.

No world, no simulation. Usage: adversary.py [--n 1500]
"""
from __future__ import annotations

import argparse, os, sys, zlib
from dataclasses import replace

import numpy as np

sys.path.insert(0, "runs/RBT-78")
from reconcile import MASTER_SEED, POOLS, _load

from rabbitstew.analysis import steering_terms
from rabbitstew.brain import RuntimeBrain
from rabbitstew.genetics import mutate_controller
from rabbitstew.synthesis import synthesize


def measured(ph, drive=0.01, ticks=400):
    """Realised steering response per unit nose differential (RBT-78's calibrated form)."""
    t = steering_terms(ph)
    if t is None:
        return None
    eL, eR = t["effectors"]
    nL, nR = t["noses"]
    out = []
    for d in (0.0, drive):
        b = RuntimeBrain(ph)
        vals = np.zeros(len(b.sensors))
        for j, s in enumerate(b.sensors):
            if s.unit == nL:
                vals[j] = 0.5 + d / 2
            elif s.unit == nR:
                vals[j] = 0.5 - d / 2
        for _ in range(ticks):
            b.step(vals)
        out.append(float(b.activation[list(eL)].sum() + b.activation[list(eR)].sum()))
    return (out[1] - out[0]) / drive


p = argparse.ArgumentParser()
p.add_argument("--n", type=int, default=1500)
p.add_argument("--k", type=int, default=19)
args = p.parse_args()

rows = []
for label in POOLS:
    cfg, pool = _load(label)
    mcfg = replace(cfg.mutation, add_link_rate=0.15, remove_link_rate=0.1)
    for i in range(args.n):
        rng = np.random.default_rng(np.random.SeedSequence([MASTER_SEED, zlib.crc32(label.encode()), args.k, i]))
        g = pool[i % len(pool)]
        for _ in range(args.k):
            g = mutate_controller(g, rng, mcfg)
        ph = synthesize(g, cfg.sim.synthesis)
        t = steering_terms(ph)
        if t is None:
            continue
        m = measured(ph)
        rows.append((label, t["a"], t["c"], t["rho"], m))

for label in list(POOLS) + ["ALL"]:
    sub = [r for r in rows if label == "ALL" or r[0] == label]
    a = np.array([r[1] for r in sub]); m = np.array([r[4] for r in sub])
    wired = np.abs(a) > 1e-9
    print(f"\n=== {label}  n={len(sub)}, of which {int(wired.sum())} carry direct wiring ===")
    if wired.sum() < 3:
        print("   too few wired lineages to say anything")
        continue
    aw, mw = a[wired], m[wired]
    print(f"  corr(a, measured) over WIRED only : {np.corrcoef(aw, mw)[0,1]:+.4f}   (n={len(aw)})")
    print(f"  corr including the unwired zeros  : {np.corrcoef(a, m)[0,1]:+.4f}   (n={len(a)})"
          f"   <- the RBT-78 number's denominator")
    ratio = mw / aw
    print(f"  measured / a : median {np.median(ratio):+.4f}  IQR "
          f"[{np.percentile(ratio,25):+.4f}, {np.percentile(ratio,75):+.4f}]  "
          f"sign agreement {int((np.sign(aw)==np.sign(mw)).sum())}/{len(aw)}")
    big = np.abs(aw) >= 1.0
    if big.any():
        print(f"  among |a| >= 1 (n={int(big.sum())}): median ratio {np.median((mw/aw)[big]):+.4f}, "
              f"sign agreement {int((np.sign(aw[big])==np.sign(mw[big])).sum())}/{int(big.sum())}")
    # where does the instrument disagree with the network?
    flip = wired & (np.sign(a) != np.sign(m)) & (np.abs(a) > 0.1)
    print(f"  lineages where a and the network disagree in SIGN at |a| > 0.1: "
          f"{int(flip.sum())}/{int((wired & (np.abs(a) > 0.1)).sum())}")
