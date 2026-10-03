"""Probe 1: can a RESOLVING point read TIE while the income edge is at or above the design's own margins?

Uses the design's replica (power.merged_history) and its own resolvable() unchanged.  For each breeding rule and
regime g0, and each true income edge, prints: RESOLVING at n 8 / 16 (power.resolvable), and the probability of
the share TIE (TOST at +-0.10) and of the WIN call, at n 8 and 16, at alpha = q/2 (BH half) and alpha = q (the BH
bound when most TIE tests reject).  An edge of 0.15 is the income layer's own TIE margin delta_i, and 0.10 is RBT-121
B's selection threshold; a TIE there is a TIE the income layer would not grant.

python3 probe_tie.py RULE [reps]   (RULE lottery|energy)
"""
import sys

import numpy as np

import adv_replica as A

rule = sys.argv[1]
reps = int(sys.argv[2]) if len(sys.argv) > 2 else 400
rng = np.random.default_rng(12901 if rule == "lottery" else 12902)
print(f"# probe_tie: rule {rule}, {reps} replica seeds per row; TIE = TOST +-0.10 on share - 0.5")
print("# cols: g0 | RESOLVING n8/n16 (power.resolvable) | edge | mean share | seed SD | "
      "TIE n8 q/2, q | TIE n16 q/2, q | WIN n8 q/2 | WIN n16 q/2")
for g0 in (0.8, 0.9, 1.0, 1.1, 1.3):
    r8 = A.P.resolvable(g0, rule, 8, reps=300)
    r16 = A.P.resolvable(g0, rule, 16, reps=300)
    tag = f"{'Y' if r8 >= 0.8 else 'n'}({r8:.2f})/{'Y' if r16 >= 0.8 else 'n'}({r16:.2f})"
    for edge in (0.0, 0.10, 0.15, 0.20, round(0.25 * g0, 3)):
        sh = np.array([A.P.merged_history(rng, g0 + edge / 2, g0 - edge / 2, rule)[0] for _ in range(reps)])
        q2, q = A.Q / 2, A.Q
        row = [A.tie_rate(sh, 8, q2), A.tie_rate(sh, 8, q), A.tie_rate(sh, 16, q2), A.tie_rate(sh, 16, q),
               A.win_rate(sh, 8, q2, sign=+1), A.win_rate(sh, 16, q2, sign=+1)]
        print(f"  g0 {g0:.1f} | RES {tag} | edge {edge:.3f} | share {sh.mean():.3f} sd {sh.std(ddof=1):.3f} | "
              f"TIE n8 {row[0]:.2f},{row[1]:.2f} | TIE n16 {row[2]:.2f},{row[3]:.2f} | WIN n8 {row[4]:.2f} | WIN n16 {row[5]:.2f}",
              flush=True)
