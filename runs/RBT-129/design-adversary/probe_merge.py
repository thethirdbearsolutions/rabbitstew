"""Probe 2: is the N arm a null for M's starting point?  And can habitability alone make a share WIN?

(a) Merge-time composition.  Equal bodies (edge 0), but the holistic fauna holds only k of its 60 slots at the
    merge (a slow founding refill, RBT-118 §2/§3; RBT-100 founders6 had 8-60 holistic and 2-7 designed alive at
    season 59).  The N arm always starts at 1:1 (a copy of one fauna), so it cannot see this.  Printed: mean share at
    the merge, mean share over 240-299, and the rate of a (false) body WIN under the design's statistic
    y = share - 0.5, and under the change statistic y' = share - share_at_merge, at n 8, BH half (q/2) and
    worst (q/36), with the design's margin |mean| >= 0.10 applied to the WIN.
(b) Partial pre-merge extinction.  One fauna is extinct in its own ecology before season 60 on j of 8 seeds (so the
    point is not EXCLUDED, which needs >= 5 of 8); the M arm on those seeds reads share 1 (y = +0.5).  The other
    seeds are no-edge seeds drawn from the replica null.  Printed: P(H-WIN) at q/2 and q/36.

python3 probe_merge.py [reps]
"""
import sys

import numpy as np

import adv_replica as A

reps = int(sys.argv[1]) if len(sys.argv) > 1 else 300
rng = np.random.default_rng(12903)
q2, qw = A.Q / 2, A.Q / 36


def win_margin(y, n, alpha, B=4000, r=np.random.default_rng(9)):
    x = y[r.integers(0, len(y), size=(B, n))]
    t = A.t_stat(x)
    c = A.t_crit(alpha, n - 1)
    m = x.mean(1)
    return float(np.mean((np.abs(t) > c) & (np.abs(m) >= 0.10)))


print(f"# probe_merge (a): edge 0, holistic alive at the merge = k of 60, designed 60; {reps} replica seeds per row")
print("# cols: rule g0 k | share at merge | share 240-299 | false WIN rate on y (q/2, q/36) | on y' = share - share_at_merge (q/2, q/36)")
nulls = {}
for rule in ("lottery", "energy"):
    for g0 in (0.8, 1.3):
        for k in (60, 45, 30, 15):
            res = [A.merged_history_k(rng, g0, g0, rule, keep_H=k) for _ in range(reps)]
            sh = np.array([r[0] for r in res])
            s0 = np.array([r[1] for r in res])
            if k == 60:
                nulls[(rule, g0)] = sh
            y, y2 = sh - 0.5, sh - s0
            print(f"  {rule:7s} g0 {g0:.1f} k {k:2d} | merge {s0.mean():.3f} | window {sh.mean():.3f} sd {sh.std(ddof=1):.3f} | "
                  f"y: {win_margin(y, 8, q2):.2f}, {win_margin(y, 8, qw):.2f} | y': {win_margin(y2, 8, q2):.2f}, {win_margin(y2, 8, qw):.2f}",
                  flush=True)

print()
print("# probe_merge (b): designed extinct before the merge on j of 8 seeds (y = +0.5 there; point not EXCLUDED at j <= 4);")
print("# the other 8 - j seeds from the replica null at that rule and g0.  P(H-WIN incl. the 0.10 margin) at q/2, q/36")
r = np.random.default_rng(11)
for (rule, g0), sh in nulls.items():
    row = []
    for j in (0, 1, 2, 3, 4):
        B = 20000
        x = sh[r.integers(0, len(sh), size=(B, 8))] - 0.5
        x[:, :j] = 0.5
        t = A.t_stat(x)
        m = x.mean(1)
        out = []
        for a in (q2, qw):
            c = A.t_crit(a, 7)
            out.append(float(np.mean((t > c) & (m >= 0.10))))
        row.append(f"j={j}: {out[0]:.2f}/{out[1]:.2f}")
    print(f"  {rule:7s} g0 {g0:.1f} | " + "  ".join(row), flush=True)
