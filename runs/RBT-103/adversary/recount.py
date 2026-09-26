"""RBT-103 adversary: re-derive the 8/10 count and t(9) from the committed readouts, and
apply the PRE-FIX readback (total depth-2 a compared against 2w) as a counterfactual that
drops every body whose own evolved a is non-zero."""
import re, sys, numpy as np
from scipy import stats
SEEDS = [1, 2, 3, 4, 7, 801, 804, 805, 806, 807]
def t_int(x):
    x = np.asarray(x, float); n = len(x); m = x.mean()
    h = stats.t.ppf(0.975, n - 1) * x.std(ddof=1) / np.sqrt(n)
    return m, m - h, m + h
def parse(path):
    txt = open(path).read()
    own = {int(g): float(a) for g, a in re.findall(r"^g(\d+)\s+([+-]\d+\.\d+) \|", txt, re.M)}
    inc = {int(g): (float(a), float(b)) for g, a, b in
           re.findall(r"^g(\d+)\s+[+-]1\s+\d+\.\d+ \|\s+([+-]\d+\.\d+) \|\s+([+-]\d+\.\d+)", txt, re.M)}
    base = {int(g): float(b) for g, b in re.findall(r"^g(\d+)\s+[+-]1\s+(\d+\.\d+) \|", txt, re.M)}
    return own, inc, base
def verdict(x):
    m, lo, hi = t_int(x)
    return m, lo, hi, ("PAYS" if lo > 0 else "NEGATIVE" if hi < 0 else "unresolved")
src = sys.argv[1] if len(sys.argv) > 1 else "docs/artifacts/RBT-103-seed-{}.txt"
print("## a = 64, as committed (all scored bodies)            | pre-fix counterfactual (own a != 0 dropped)")
means, pays, pays_pf, means_pf = [], 0, 0, []
for s in SEEDS:
    own, inc, base = parse(src.format(s))
    x = [inc[g][1] for g in inc]
    m, lo, hi, v = verdict(x)
    keep = [inc[g][1] for g in inc if abs(own.get(g, 0)) < 1e-9]
    if len(keep) >= 2:
        m2, lo2, hi2, v2 = verdict(keep)
    else:
        m2 = lo2 = hi2 = float("nan"); v2 = "n<2"
    means.append(m); pays += v == "PAYS"
    means_pf.append(m2); pays_pf += v2 == "PAYS"
    print(f"{s:>4} n={len(x)} {m:+.3f} [{lo:+.3f}, {hi:+.3f}] {v:10s} | n={len(keep)} {m2:+.3f} [{lo2:+.3f}, {hi2:+.3f}] {v2}"
          f"   mean base {np.mean(list(base.values())):.3f}  gain/base {m/np.mean(list(base.values())):.2f}")
m, lo, hi = t_int(means)
print(f"\ncommitted: PAYS {pays}/10; across-population t(9) mean {m:+.3f} [{lo:+.3f}, {hi:+.3f}]")
m, lo, hi = t_int([x for x in means_pf if x == x])
print(f"pre-fix counterfactual: PAYS {pays_pf}/10; mean {m:+.3f} [{lo:+.3f}, {hi:+.3f}]")
