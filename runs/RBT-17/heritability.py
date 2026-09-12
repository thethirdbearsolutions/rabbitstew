"""Yield heritability for an ecology run: Pearson r between a child's lifetime mean yield
(`fitness`, evals >= 5) and the mean of its parents' (same rule), per population."""
import sys, numpy as np
from rabbitstew.analysis import read_lineage
run = sys.argv[1]; min_evals = int(sys.argv[2]) if len(sys.argv) > 2 else 5
lin = read_lineage(run)
for kind in ("holistic", "conventional"):
    xs, ys = [], []
    for (k, name), r in lin.items():
        if k != kind or not r["parents"] or r.get("evals", 0) < min_evals:
            continue
        ps = [lin[(k, p)] for p in r["parents"] if (k, p) in lin and lin[(k, p)].get("evals", 0) >= min_evals]
        if not ps:
            continue
        xs.append(np.mean([p["fitness"] for p in ps])); ys.append(r["fitness"])
    n = len(xs)
    r_ = float(np.corrcoef(xs, ys)[0, 1]) if n > 2 else float("nan")
    print(f"{kind:12s} pairs {n:4d}  parent mean {np.mean(xs) if n else float('nan'):+.3f}  child mean {np.mean(ys) if n else float('nan'):+.3f}  Pearson r {r_:.3f}")
