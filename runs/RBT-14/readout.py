"""RBT-14 readout: season table at the ticket's checkpoints, bottleneck/recovery, crossover, extinction,
founders at the last season with survivors, and yield heritability (evals >= 5 for child and parents)."""
import json, sys, numpy as np
from collections import defaultdict
from rabbitstew.analysis import read_lineage, founders
run = sys.argv[1]
hist = json.load(open(f"{run}/history.json"))["history"]
by = defaultdict(dict)
for e in hist:
    by[e["season"]][e["population"]] = e
seasons = sorted(by)
last = seasons[-1]
checkpoints = [s for s in (0, 11, 20, 32, 60, 100, 200, 300, 400, 500, 599) if s <= last]
print(f"run ended at season {last} ({len(seasons)} seasons recorded)")
print("season  pop           alive  births  deaths  mean gain  best gain")
for s in checkpoints:
    for kind in ("holistic", "conventional"):
        e = by[s].get(kind)
        if e is None:
            print(f"{s:6d}  {kind:12s}      -       -       -          -          -"); continue
        print(f"{s:6d}  {kind:12s} {e['alive']:6d}  {e['births']:6d}  {e['deaths']:6d}  {e['mean_lifetime_score']:+9.3f}  {e['best_lifetime_score']:+9.3f}")
print()
for kind in ("holistic", "conventional"):
    rows = [(s, by[s][kind]) for s in seasons if kind in by[s]]
    alive = [(s, e["alive"]) for s, e in rows]
    smin, amin = min(alive, key=lambda t: (t[1], t[0]))
    ext = next((s for s, a in alive if a == 0), None)
    rec = next((s for s, a in alive if s > smin and a >= 60), None)
    dmax = max(rows, key=lambda t: t[1]["deaths"])
    tot_b = sum(e["births"] for _, e in rows); tot_d = sum(e["deaths"] for _, e in rows)
    print(f"{kind}: minimum alive {amin} at season {smin}; worst season {dmax[0]} ({dmax[1]['deaths']} deaths); "
          f"back to 60 at season {rec}; extinct at season {ext}; total births {tot_b}, deaths {tot_d}")
cross = next((s for s in seasons if "holistic" in by[s] and "conventional" in by[s] and by[s]["holistic"]["alive"] > 0
              and by[s]["holistic"]["mean_lifetime_score"] > by[s]["conventional"]["mean_lifetime_score"]), None)
print(f"first season holistic mean gain exceeds wheeled: {cross}")
print()
lin = read_lineage(run)
for kind in ("holistic", "conventional"):
    recs = [r for (k, _), r in lin.items() if k == kind]
    if not recs:
        print(kind, "no lineage"); continue
    lastg = max(r["generation"] for r in recs)
    names = [r["name"] for r in recs if r["generation"] == lastg]
    print(kind, f"last season with survivors {lastg}:", founders(lin, kind, names))
    byname = {r["name"]: r for r in recs}
    xs, ys = [], []
    for r in recs:
        if not r["parents"] or r["evals"] < 5:
            continue
        ps = [byname[p]["fitness"] for p in r["parents"] if p in byname and byname[p]["evals"] >= 5]
        if ps:
            xs.append(float(np.mean(ps))); ys.append(float(r["fitness"]))
    if len(xs) >= 10 and np.std(xs) > 0 and np.std(ys) > 0:
        print(f"   yield heritability: parent-child Pearson r = {np.corrcoef(xs, ys)[0,1]:+.3f} over {len(xs)} children (evals >= 5 both sides)")
    else:
        print(f"   yield heritability: not estimable ({len(xs)} qualifying children)")
