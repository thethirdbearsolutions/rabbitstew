"""RBT-132 fix-check, item 4: reproduce probe_power.py's Fisher numbers independently (scipy.stats.fisher_exact, not
probe_power's own hypergeometric sums), and extend the null past K5's cap.

    python runs/RBT-116/design-adversary/rbt132_fisher_check.py > runs/RBT-116/design-adversary/rbt132_fisher_check.txt

Needs scipy (not a project dependency).  Exact sums over both binomials; founders N = evolved N.  No probe data.
"""
import numpy as np
from scipy import stats


def rate(n, pf, pe):
    kf = stats.binom.pmf(np.arange(n + 1), n, pf)
    ke = stats.binom.pmf(np.arange(n + 1), n, pe)
    tot = 0.0
    for k in range(n + 1):
        if kf[k] < 1e-14:
            continue
        for e in range(n + 1):
            if ke[e] > 1e-14 and stats.fisher_exact([[e, n - e], [k, n - k]], alternative="greater")[1] <= 0.05:
                tot += kf[k] * ke[e]
    return tot


print("# rbt132_fisher_check.py: one-sided Fisher exact at 0.05 (scipy), evolved vs founders' pooled confirmed-STEERS")
grid = (0.001, 0.005, 0.01, 0.02, 0.03, 0.05, 0.10, 0.15, 0.20, 0.30)
print("## null by eps:  " + " ".join(f"{e:>6g}" for e in grid))
for n in (80, 160):
    print(f"   N {n:3d}        " + " ".join(f"{rate(n, e, e):6.4f}" for e in grid))
print("## power at tau 2 s priors (two-nose SENS 0.40, one-nose 0.24), founders eps 0.005; pe = q SENS + (1 - q) eps")
for n in (80, 160):
    for lab, s in (("two", 0.40), ("one", 0.24)):
        print(f"   N {n:3d} {lab}-nose: " + " / ".join(f"q {q:.2f} {rate(n, 0.005, q * s + (1 - q) * 0.005):.3f}" for q in (0.10, 0.25, 0.50)))
