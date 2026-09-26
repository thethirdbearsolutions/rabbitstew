"""Yield heritability per population for RBT-15: Pearson r between a child's lifetime mean yield
(the lineage `fitness` field, last record per individual, evals >= 5) and its parents' mean (same rule).
Also prints the repo's realised_heritability (no evals threshold) for comparison."""
import sys, numpy as np
from rabbitstew.analysis import read_lineage, realised_heritability
run = sys.argv[1]; min_evals = int(sys.argv[2]) if len(sys.argv) > 2 else 5
lin = read_lineage(run)
for kind in ("holistic", "conventional"):
    byname = {r["name"]: r for (k, _), r in lin.items() if k == kind}
    ok = {n: r for n, r in byname.items() if r["evals"] >= min_evals}
    xs, ys = [], []
    for r in ok.values():
        ps = [ok[p]["fitness"] for p in r["parents"] if p in ok]
        if r["parents"] and len(ps) == len(r["parents"]):
            xs.append(float(np.mean(ps))); ys.append(float(r["fitness"]))
    n = len(xs)
    r_ = float(np.corrcoef(xs, ys)[0, 1]) if n >= 10 and np.std(xs) > 0 and np.std(ys) > 0 else None
    rh = realised_heritability(run, kind)
    print(f"{kind:12s} evals>={min_evals}: n={n} children, r={None if r_ is None else round(r_, 3)}   "
          f"(individuals with >={min_evals} evals: {len(ok)} of {len(byname)}; parent mean {np.mean(xs) if xs else float('nan'):.3f}, child mean {np.mean(ys) if ys else float('nan'):.3f})   "
          f"repo realised_heritability (no threshold): r={rh['heritability']} n={rh['n']}")
