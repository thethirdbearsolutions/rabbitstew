"""RBT-112 design adversary: u re-derived from the committed baseline tables with independent code (not erasure.py).
Reads each table's pay32 and lineages columns by header name; pools counts over ten seeds; u(d) = 1 - (f(d)/f(0))^(1/d)
beside the registered 1 - f(d)^(1/d); per-seed u(8) with a t(9) interval; and the log-linear fit of log f over depths 1-16.
Usage: rederive_u.py BASELINE_DIR"""
import math, os, sys
import numpy as np
B = sys.argv[1]
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
def rows(p):
    head = None; out = {}
    for l in open(p):
        if l.startswith("# depth"): head = l[2:].split()
        elif not l.startswith("#"):
            r = dict(zip(head, l.split())); out[int(r["depth"])] = (int(r["pay32"]), int(r["lineages"]), int(r["same"]))
    return out
for tag, name in (("", "default"), ("-S0", "S = 0")):
    T = {s: rows(os.path.join(B, f"baseline-w32{tag}-{s}.txt")) for s in SEEDS}
    f = lambda d, c=0: sum(T[s][d][c] for s in SEEDS) / sum(T[s][d][1] for s in SEEDS)
    print(f"{name}: f(0) {f(0):.4f}; " + "; ".join(f"u({d}) {1 - f(d) ** (1 / d):.3f} (f0-normalised {1 - (f(d) / f(0)) ** (1 / d):.3f})" for d in (1, 2, 4, 8, 16)))
    per = [1 - (T[s][8][0] / T[s][8][1]) ** (1 / 8) for s in SEEDS]
    m, h = np.mean(per), 2.2622 * np.std(per, ddof=1) / math.sqrt(10)
    ds = np.arange(1, 17); slope = np.polyfit(ds, np.log([f(d) for d in ds]), 1)[0]
    print(f"   per-seed u(8): {m:.3f} [{m - h:.3f}, {m + h:.3f}] range {min(per):.3f}-{max(per):.3f}; log-linear fit over depths 1-16: u = {1 - math.exp(slope):.3f}; "
          f"structure 'same' u(8) {1 - f(8, 2) ** (1 / 8):.3f}")
