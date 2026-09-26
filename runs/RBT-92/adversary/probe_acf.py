"""RBT-92 adversary: the lag-60 deaths autocorrelation re-derived with numpy, independently of cohort_cycle.py.

    python runs/RBT-92/adversary/probe_acf.py > runs/RBT-92/adversary/probe_acf.txt
"""
import csv
import os

import numpy as np

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "RBT-71")
print(__doc__.split("\n\n")[0])
n60 = 0
for kind in ("forage", "neutral"):
    for seed in (804, 805, 806):
        rows = list(csv.DictReader(open(os.path.join(ROOT, f"{kind}-{seed}", "seasons.txt")), delimiter="\t"))
        for pop in ("holistic", "conventional"):
            d = np.array([int(r["deaths"]) for r in rows if r["population"] == pop and 100 <= int(r["season"]) < 600], float)
            d -= d.mean()
            v = (d * d).sum()
            ac = {L: (d[:-L] * d[L:]).sum() / v for L in range(30, 91)}
            pk = max(ac, key=ac.get)
            n60 += pk == 60
            print(f"{kind}-{seed} {pop:12s} peak lag in 30..90: {pk}  acf60 {ac[60]:+.3f}")
print(f"peak at lag 60: {n60}/12")
