"""What per-link weight scale does the operator actually reach? (RBT-61 follow-on)

The 4-link antisymmetric motif with weight w on each link puts a = 2w on the steering axis.
RBT-61's payoff points therefore need per-link weights of w = 8 (null), 16 (+0.25) and 32 (+0.90).
`mutate_weights` is an unbounded random walk, step sigma 0.4, with a reset to N(0,1), so nothing
forbids w = 32 in principle.  This asks what it reaches in practice.

usage: weight_scale.py RUN LABEL
"""
import glob, json, sys
import numpy as np
from rabbitstew.genotype import Genotype

run, label = sys.argv[1], sys.argv[2]
for kind in ("conventional", "holistic"):
    W = []
    for f in sorted(glob.glob(f"{run}/{kind}/final/*.json")):
        for _, brain in Genotype.load(f).brains():
            W += [abs(l.weight) for l in brain.links]
    if not W:
        continue
    W = np.array(W)
    print(f"{label:26} {kind:12} links={len(W):6d}  median {np.median(W):5.2f}  "
          f"p99 {np.percentile(W,99):6.2f}  max {W.max():7.2f}   "
          f"|w|>=8 {int((W>=8).sum()):4d} ({(W>=8).mean():.4%})  "
          f">=16 {int((W>=16).sum()):3d}  >=32 {int((W>=32).sum()):3d}")
