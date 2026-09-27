"""RBT-121 adversary: does income buy offspring in a committed ecology?  Read-only on runs/RBT-19/P-801/lineage.jsonl.

For every individual born in seasons 50-500 (so its whole life is inside the run), read: lifetime mean score (the
last row's `fitness`, mean gain per season), lifespan, how it died (age >= 59 at its last row, else starved),
seasons spent at or above the birth threshold (energy after births >= 3), and number of children (rows whose
parents[0] names it).  Report offspring by income quintile, so the realised selection gradient on income is read
off a real run instead of a replica.  Also: the number above threshold per season, to check audit C's ~50 of 58."""
import collections, json, sys
import numpy as np
path = sys.argv[1] if len(sys.argv) > 1 else "../../RBT-19/P-801/lineage.jsonl"
rows = collections.defaultdict(list); kids = collections.Counter(); elig_per_season = collections.defaultdict(lambda: collections.Counter())
alive_per_season = collections.defaultdict(collections.Counter)
for l in open(path):
    r = json.loads(l)
    rows[(r["population"], r["name"])].append(r)
    if r["age"] == 0 and r["evals"] == 0 and r["parents"]:
        kids[(r["population"], r["parents"][0])] += 1
    if r["evals"] > 0:
        alive_per_season[r["population"]][r["generation"]] += 1
        elig_per_season[r["population"]][r["generation"]] += r["energy"] >= 3.0
for pop in ("holistic", "conventional"):
    g = sorted(elig_per_season[pop]); sl = [x for x in g if 50 <= x < 600]
    print(f"## {pop}: seasons 50-599 alive (evaluated) {np.mean([alive_per_season[pop][x] for x in sl]):.1f}, "
          f"at/above threshold after births {np.mean([elig_per_season[pop][x] for x in sl]):.1f}")
    recs = []
    for (p, name), rs in rows.items():
        if p != pop:
            continue
        rs.sort(key=lambda r: r["generation"])
        born = rs[0]["generation"]
        if rs[0]["age"] != 0 or not (50 <= born <= 500):
            continue
        last = rs[-1]
        if last["generation"] >= 599:
            continue
        adult = [r for r in rs if r["evals"] > 0]
        if not adult:
            continue
        inc = adult[-1]["fitness"]
        recs.append((inc, len(adult), last["age"] >= 59, sum(r["energy"] >= 3.0 for r in adult), kids[(p, name)]))
    a = np.array(recs, dtype=float)
    print(f"   {len(a)} complete lives; died of age {a[:,2].mean():.2f}; mean children {a[:,4].mean():.2f}; "
          f"corr(income, children) {np.corrcoef(a[:,0], a[:,4])[0,1]:+.3f}; corr(income, lifespan) {np.corrcoef(a[:,0], a[:,1])[0,1]:+.3f}")
    q = np.quantile(a[:, 0], [0, .2, .4, .6, .8, 1])
    print("   income quintile | mean income | lifespan | died of age | seasons eligible | children")
    for i in range(5):
        m = (a[:, 0] >= q[i]) & (a[:, 0] <= q[i + 1] if i == 4 else a[:, 0] < q[i + 1])
        b = a[m]
        print(f"   Q{i+1} [{q[i]:+.2f},{q[i+1]:+.2f}] | {b[:,0].mean():+.3f} | {b[:,1].mean():5.1f} | {b[:,2].mean():.2f} | {b[:,3].mean():5.1f} | {b[:,4].mean():.2f}")
    top = a[a[:, 0] >= q[2]]
    x = top[:, 0]; y = top[:, 4]
    print(f"   above-median incomes only: slope children per unit income {np.polyfit(x, y, 1)[0]:+.3f} "
          f"(mean children {y.mean():.2f}; relative gradient per unit income {np.polyfit(x, y, 1)[0]/y.mean():+.3f})")
