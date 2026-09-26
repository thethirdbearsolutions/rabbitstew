"""RBT-97 adversary, round 2: the routed-motif pooled figures re-derived from the committed
per-robot rows (docs/artifacts/RBT-97-routed-{p801,w4b-control}.txt), t(df 6) over robots, plus
seed-level-free checks: k/n robots improved and the W4b control against genotype_motif.txt
(+0.277, +0.879 on seeds 9000..9063).

Usage: python runs/RBT-97/adversary_routed.py
"""
import math, os, re, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(ROOT)
import numpy as np
ROW = re.compile(r"^g(\d+)\s+[+-][\d.]+°\s+([+-]1)\s+([\d.]+)\s+\|\s+([+-][\d.]+)\s+\|\s+([+-][\d.]+)")
for path in ("docs/artifacts/RBT-97-routed-p801.txt", "docs/artifacts/RBT-97-routed-w4b-control.txt"):
    rows = [m.groups() for m in map(ROW.match, open(path)) if m]
    print(f"{path}: {len(rows)} robots; the readout carries {sum('unstable' in l for l in open(path))} QACC-instability warnings and no explosion count")
    for j, w in ((3, 16), (4, 32)):
        v = np.array([float(r[j]) for r in rows])
        se = v.std(ddof=1) / math.sqrt(len(v)); h = 2.447 * se
        print(f"   w = {w} (a = {2 * w}): {v.mean():+.3f} [{v.mean() - h:+.3f}, {v.mean() + h:+.3f}]  improved {int((v > 0).sum())}/{len(v)}"
              f"  -> {'PAYS' if v.mean() - h > 0 else 'NEGATIVE' if v.mean() + h < 0 else 'NULL'}")
