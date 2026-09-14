"""Scratch readout for RBT-16: history at the listed seasons, bottleneck/recovery, first crossover,
extinctions, founders at the last season, and yield heritability (child vs parents' mean lifetime
yield, evals >= 5 on both sides)."""
import json, sys, numpy as np
from rabbitstew.analysis import read_lineage, founders
run = sys.argv[1]
H = json.load(open(f"{run}/history.json"))["history"]
by = {}
for e in H: by.setdefault(e["population"], {})[e["season"]] = e
seasons = [0, 11, 20, 32, 60, 100, 200, 300, 400, 500, 599]
print("season | pop | alive | births | deaths | mean gain | best gain")
for s in seasons:
    for k in ("holistic", "conventional"):
        e = by[k].get(s)
        if e: print(f"{s:6d} | {k:12s} | {e['alive']:3d} | {e['births']:3d} | {e['deaths']:3d} | {e['mean_lifetime_score']:+.3f} | {e['best_lifetime_score']:+.3f}")
for k in ("holistic", "conventional"):
    ss = sorted(by[k]); alive = [by[k][s]["alive"] for s in ss]
    lo = int(np.argmin(alive)); cap = max(alive)
    rec = next((s for s in ss[lo:] if by[k][s]["alive"] >= cap), None)
    ext = next((s for s in ss if by[k][s]["alive"] == 0), None)
    print(f"{k}: min alive {alive[lo]} at season {ss[lo]}; back to {cap} at season {rec}; extinct at {ext}; last season logged {ss[-1]} alive {alive[-1]}")
cross = next((s for s in sorted(by["holistic"]) if s in by["conventional"] and by["holistic"][s]["mean_lifetime_score"] > by["conventional"][s]["mean_lifetime_score"]), None)
print("first season holistic mean gain > wheeled:", cross)
# sustained crossover: first season after which holistic > wheeled for 20 consecutive seasons
ss = sorted(s for s in by["holistic"] if s in by["conventional"])
sust = next((s for i, s in enumerate(ss) if all(by["holistic"][t]["mean_lifetime_score"] > by["conventional"][t]["mean_lifetime_score"] for t in ss[i:i+20]) and len(ss[i:i+20]) == 20), None)
print("first season of a 20-season run of holistic > wheeled:", sust)
lin = read_lineage(run)
for kind in ("holistic", "conventional"):
    recs = [r for (k, _), r in lin.items() if k == kind]
    if not recs: print(kind, "no lineage"); continue
    last = max(r["generation"] for r in recs)
    print(kind, "founders at season", last, founders(lin, kind, [r["name"] for r in recs if r["generation"] == last]))
    byname = {r["name"]: r for r in recs}  # last record per name (lifetime mean yield)
    xs, ys = [], []
    for r in byname.values():
        if not r["parents"] or r["evals"] < 5: continue
        ps = [byname[p]["fitness"] for p in r["parents"] if p in byname and byname[p]["evals"] >= 5]
        if ps: xs.append(float(np.mean(ps))); ys.append(float(r["fitness"]))
    r = float(np.corrcoef(xs, ys)[0, 1]) if len(xs) > 10 else float("nan")
    print(f"{kind} yield heritability (Pearson r, child vs parents' mean, evals>=5): r={r:+.3f} n={len(xs)}")
