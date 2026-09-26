"""RBT-20 readout: season table, bottleneck/recovery, crossover season, extinctions, founders, yield heritability."""
import json, sys
import numpy as np
from rabbitstew.analysis import read_lineage, founders, realised_heritability

run = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-20/W3b-801"
KINDS = ("holistic", "conventional")
data = json.load(open(f"{run}/history.json"))
by = {}
for e in data["history"]:
    by.setdefault(e["season"], {})[e["population"]] = e
last = max(by)
print(f"seasons logged: 0..{last}")

marks = [s for s in (0, 3, 11, 20, 32, 60, 100, 200, 300, 400, 500, 599) if s <= last]
print("\n## Season table (alive / births / deaths / mean lifetime gain / best lifetime gain)")
print("| season | " + " | ".join(f"{k} alive | births | deaths | mean gain | best" for k in KINDS) + " |")
print("|---|" + "---|" * 10)
for s in marks:
    cells = []
    for k in KINDS:
        e = by[s].get(k)
        cells += ["0", "-", "-", "extinct", "-"] if e is None else [str(e["alive"]), str(e["births"]), str(e["deaths"]), f"{e['mean_lifetime_score']:+.2f}", f"{e['best_lifetime_score']:.2f}"]
    print(f"| {s} | " + " | ".join(cells) + " |")

print("\n## Bottleneck, recovery, extinction")
for k in KINDS:
    series = [(s, by[s][k]["alive"]) for s in sorted(by) if k in by[s]]
    smin, amin = min(series, key=lambda t: (t[1], t[0]))
    ext = next((s for s, a in series if a == 0), None)
    rec = next((s for s, a in series if s > smin and a >= 60), None)
    print(f"{k:12s} min alive {amin} at season {smin}; back to 60 at season {rec}; extinct at {ext}; last logged season {series[-1][0]} alive {series[-1][1]}")

cross = next((s for s in sorted(by) if all(k in by[s] for k in KINDS) and by[s]["holistic"]["mean_lifetime_score"] > by[s]["conventional"]["mean_lifetime_score"]), None)
print(f"first season holistic mean gain exceeds wheeled: {cross}")
# sustained crossover: first season after which holistic stays above for 20 seasons
sus = None
seasons = sorted(s for s in by if all(k in by[s] for k in KINDS))
for i, s in enumerate(seasons):
    win = seasons[i:i + 20]
    if len(win) == 20 and all(by[t]["holistic"]["mean_lifetime_score"] > by[t]["conventional"]["mean_lifetime_score"] for t in win):
        sus = s; break
print(f"first season of a 20-season stretch with holistic mean above wheeled: {sus}")

print("\n## Founders at the last season with survivors")
lin = read_lineage(run)
for kind in KINDS:
    recs = [r for (k, _), r in lin.items() if k == kind]
    if not recs:
        print(kind, "no lineage"); continue
    lastg = max(r["generation"] for r in recs)
    names = [r["name"] for r in recs if r["generation"] == lastg]
    print(kind, "season", lastg, founders(lin, kind, names))

print("\n## Yield heritability (Pearson r, child lifetime mean yield vs parents' mean; both with evals >= 5)")
for kind in KINDS:
    byname = {r["name"]: r for (k, _), r in lin.items() if k == kind}
    xs, ys = [], []
    for r in byname.values():
        if not r["parents"] or r["evals"] < 5:
            continue
        ps = [byname[p]["fitness"] for p in r["parents"] if p in byname and byname[p]["evals"] >= 5]
        if ps:
            xs.append(float(np.mean(ps))); ys.append(float(r["fitness"]))
    n = len(xs)
    r_ = float(np.corrcoef(xs, ys)[0, 1]) if n >= 10 and np.std(xs) > 0 and np.std(ys) > 0 else None
    unf = realised_heritability(run, kind)
    print(f"{kind:12s} evals>=5: n={n} r={r_ if r_ is None else round(r_, 3)}   (no evals filter, analysis.realised_heritability: n={unf['n']} r={unf['heritability']})")
    # by thirds of the run
    for lo, hi in ((0, 200), (200, 400), (400, 600)):
        w = realised_heritability(run, kind, window=(lo, hi))
        print(f"{'':12s}   seasons {lo}-{hi}: n={w['n']} r={w['heritability']}")
