"""Aggregate nearmiss.sh output: pooled histogram of EPA horizon sizes, per-unit maxima, and a log-linear tail fit
P(nedges >= n) extrapolated to the overflow threshold (n = 25)."""
import sys
from collections import Counter

import numpy as np

pool, maxima, iters = Counter(), [], 0
for line in open(sys.argv[1]):
    f = line.split()
    unit, h = f[0], f[f.index("hist") + 1:]
    hist = {int(a): int(b) for a, b in (x.split(":") for x in h)}
    pool.update(hist)
    maxima.append((unit, max(hist)))
    iters += int(f[f.index("epa_iterations") + 1])
print(f"units {len(maxima)}  EPA iterations {iters:.3e}  overflow lines 0" if all(" overflow 0 " in l for l in open(sys.argv[1])) else "OVERFLOW SEEN")
print("pooled hist:", " ".join(f"{k}:{pool[k]}" for k in sorted(pool)))
print("per-unit max horizon:", sorted(m for _, m in maxima), " overall max", max(m for _, m in maxima))
ks = np.array(sorted(pool))
tail = np.array([sum(pool[j] for j in ks if j >= k) for k in ks]) / iters
sel = (ks >= 8) & (tail * iters >= 3)
b, a = np.polyfit(ks[sel], np.log10(tail[sel]), 1)
print(f"tail fit on n in {list(ks[sel])}: log10 P(>=n) = {a:.2f} + {b:.3f} n  (factor {10**b:.3f} per edge)")
p25 = 10 ** (a + b * 25)
print(f"extrapolated P(nedges >= 25) per EPA iteration = {p25:.2e}; expected overflows in these iterations = {p25 * iters:.2e}")
