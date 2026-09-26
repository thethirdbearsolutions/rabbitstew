"""Ecology readout for RBT-13 (W1, food decay 3 m): season table, bottleneck/recovery, crossover,
founders at the last season, and yield heritability (evals >= 5)."""
import json, sys, numpy as np
from rabbitstew.analysis import read_lineage, founders
run = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-13/W1-801"
h = json.load(open(f"{run}/history.json"))["history"]
kinds = ("holistic", "conventional")
by = {k: {} for k in kinds}
for e in h:
    by[e["population"]][e["season"]] = e
last = max(by["holistic"]) if by["holistic"] else 0
seasons = [s for s in (0, 11, 20, 32, 60, 100, 200, 300, 400, 500, 599) if s <= last]
print(f"last season recorded: {last}")
print("season | holistic alive births deaths mean_gain | wheeled alive births deaths mean_gain")
for s in seasons:
    row = f"{s:6d}"
    for k in kinds:
        e = by[k].get(s)
        row += f" | {e['alive']:5d} {e['births']:6d} {e['deaths']:6d} {e['mean_lifetime_score']:+9.2f}" if e else " |  (absent)"
    print(row)
for k in kinds:
    ss = sorted(by[k])
    alive = [by[k][s]["alive"] for s in ss]
    mn = min(alive); smin = ss[alive.index(mn)]
    rec = next((s for s in ss if s > smin and by[k][s]["alive"] >= 60), None)
    ext = next((s for s in ss if by[k][s]["alive"] == 0), None)
    print(f"{k}: bottleneck min alive {mn} at season {smin}; recovery to 60 at season {rec}; extinction: {ext}")
cross = next((s for s in sorted(by["holistic"]) if s in by["conventional"] and by["holistic"][s]["mean_lifetime_score"] > by["conventional"][s]["mean_lifetime_score"]), None)
print(f"first season holistic mean gain exceeds wheeled: {cross}")
# sustained crossover: first season after which holistic > wheeled in every later season
ss = sorted(s for s in by["holistic"] if s in by["conventional"])
sus = None
for i, s in enumerate(ss):
    if all(by["holistic"][t]["mean_lifetime_score"] > by["conventional"][t]["mean_lifetime_score"] for t in ss[i:]):
        sus = s; break
print(f"first season from which holistic mean gain stays above wheeled: {sus}")
lin = read_lineage(run)
for kind in kinds:
    recs = [r for (k, _), r in lin.items() if k == kind]
    if not recs: continue
    lastg = max(r["generation"] for r in recs)
    print(kind, "founders at generation", lastg, founders(lin, kind, [r["name"] for r in recs if r["generation"] == lastg]))
for kind in kinds:
    byname = {r["name"]: r for (k, _), r in lin.items() if k == kind}
    xs, ys = [], []
    for r in byname.values():
        if not r["parents"] or r.get("evals", 0) < 5: continue
        ps = [byname[p]["fitness"] for p in r["parents"] if p in byname and byname[p].get("evals", 0) >= 5]
        if len(ps) == len(r["parents"]):
            xs.append(float(np.mean(ps))); ys.append(float(r["fitness"]))
    r_ = float(np.corrcoef(xs, ys)[0, 1]) if len(xs) >= 10 else None
    print(f"{kind}: yield heritability r = {r_ if r_ is None else round(r_, 3)} (n = {len(xs)} children with evals >= 5 and all parents evals >= 5)")
