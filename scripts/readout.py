"""The ecology readout for a foraging run: demography, founders, yield heritability and supply.

Sections 1-4 of the RBT-19 package, in one pass over a run directory:

1. **Demography.** Per population, alive/births/deaths and mean lifetime gain at a list of
   seasons; the bottleneck and the recovery; the first season the holistic mean gain exceeds the
   wheeled one; extinctions.
2. **Founders.** How many of the founding cohort are still in the ancestry at the last season.
3. **Heritability of lifetime yield.** Pearson r between a child's lifetime mean yield (the
   `fitness` field of its last lineage record, evals >= 5) and its parents' mean under the same
   rule.  Lifetime, never one season.
4. **Supply.** Per season, the group harvest against the arena's ceiling and the fraction of spots
   standing empty at a season start, read from the arena states saved beside history.json.

usage: readout.py RUN_DIR [SEASONS]    e.g. readout.py runs/RBT-19/P-801 0,11,20,32,60,100,200,300,400,500,599
"""
import json
import os
import sys

import numpy as np

from rabbitstew.analysis import founders, read_lineage

run = sys.argv[1]
marks = [int(x) for x in (sys.argv[2] if len(sys.argv) > 2 else "0,11,20,32,60,100,200,300,400,500,599").split(",")]
hist = json.load(open(f"{run}/history.json"))["history"]
pops = sorted({e["population"] for e in hist})
by = {p: {e["season"]: e for e in hist if e["population"] == p} for p in pops}
last = max(e["season"] for e in hist)

# -- 1. demography ---------------------------------------------------------- #
print("== 1. demography ==")
for p in pops:
    print(f"\n{p}")
    print(f"  {'season':>6s} {'alive':>5s} {'births':>6s} {'deaths':>6s} {'mean gain':>9s} {'best':>7s} {'max age':>7s}")
    for s in marks:
        e = by[p].get(s)
        if e:
            print(f"  {s:6d} {e['alive']:5d} {e['births']:6d} {e['deaths']:6d} {e['mean_lifetime_score']:9.3f} {e['best_lifetime_score']:7.3f} {e['max_age']:7d}")
    series = [(s, by[p][s]["alive"]) for s in sorted(by[p])]
    low_s, low_n = min(series[: min(80, len(series))], key=lambda t: t[1])
    print(f"  bottleneck: {low_n} alive at season {low_s} (of {series[0][1]} founders)")
    rec = next((s for s, n in series if s > low_s and n >= 0.9 * max(n for _, n in series)), None)
    print(f"  recovery to 90% of the run's maximum: season {rec}" if rec is not None else "  never recovered to 90% of the maximum")
    ext = [s for s, n in series if n == 0]
    print(f"  extinct from season {ext[0]}" if ext else "  no extinction")

if len(pops) == 2 and "holistic" in by and "conventional" in by:
    cross = next((s for s in sorted(by["holistic"]) if s in by["conventional"]
                  and by["holistic"][s]["mean_lifetime_score"] > by["conventional"][s]["mean_lifetime_score"]), None)
    print(f"\nfirst season holistic mean gain exceeds wheeled: {cross}" if cross is not None else "\nholistic mean gain never exceeds wheeled")

# -- 2. founders ------------------------------------------------------------ #
print("\n== 2. founders still in the ancestry at the last season ==")
lin = read_lineage(run)          # {(population, name): the individual's last record}
for p in pops:
    alive = [name for (pop, name), r in lin.items() if pop == p and r["generation"] == last]
    f = founders(lin, p, alive)
    print(f"  {p:13s} {f['founders']} founder(s) of the {by[p][0]['alive']} that started, behind {f['of']} alive at season {last}")

# -- 3. heritability of lifetime yield -------------------------------------- #
print("\n== 3. heritability of lifetime yield (parent-child Pearson r, evals >= 5) ==")
for p in pops:
    recs = [r for (pop, _), r in lin.items() if pop == p]
    final = {r["name"]: r["fitness"] for r in recs if r["evals"] >= 5}   # lifetime mean yield, last record
    parents = {r["name"]: r["parents"] for r in recs}
    xs, ys = [], []
    for name, y in final.items():
        ps = [final[q] for q in parents.get(name, []) if q in final]
        if ps:
            xs.append(float(np.mean(ps)))
            ys.append(y)
    if len(xs) >= 3:
        r = float(np.corrcoef(xs, ys)[0, 1])
        print(f"  {p:13s} r = {r:.3f}  over {len(xs)} parent-child pairs")
    else:
        print(f"  {p:13s} too few pairs ({len(xs)})")

# -- 4. supply -------------------------------------------------------------- #
path = f"{run}/arenas.json"
if os.path.exists(path):
    a = json.load(open(path))
    ceiling = a["items"] / (a["regrow_delay"] / a["duration"])
    print(f"\n== 4. supply ({a['items']} spots, {a['patches']} patches, regrow delay {a['regrow_delay']:.0f} s, ceiling {ceiling:.2f} items per group per season) ==")
    print(f"  {'season':>6s} {'population':>13s} {'crop at start':>13s} {'empty':>6s} {'harvest':>8s} {'of ceiling':>10s}")
    for s in marks:
        for row in [r for r in a["seasons"] if r["season"] == s]:
            print(f"  {s:6d} {row['population']:>13s} {row['season_start_crop_mean']:13.2f} {100 * row['empty_fraction']:5.0f}%"
                  f" {row['harvest_per_group']:8.2f} {100 * row['harvest_per_group'] / ceiling:9.0f}%")
    print("\n  means over blocks of 100 seasons:")
    for p in sorted({r["population"] for r in a["seasons"]}):
        rows = [r for r in a["seasons"] if r["population"] == p]
        for lo in range(0, last + 1, 100):
            blk = [r for r in rows if lo <= r["season"] < lo + 100]
            if blk:
                print(f"    {p:13s} seasons {lo:3d}-{min(lo + 99, last):3d}: crop {np.mean([r['season_start_crop_mean'] for r in blk]):5.2f}"
                      f"  empty {100 * np.mean([r['empty_fraction'] for r in blk]):4.0f}%"
                      f"  harvest {np.mean([r['harvest_per_group'] for r in blk]):5.2f} ({100 * np.mean([r['harvest_per_group'] for r in blk]) / ceiling:3.0f}% of ceiling)"
                      f"  per robot {np.mean([r['harvest_per_group'] for r in blk]) / 4:4.2f}")
        over = [r["season"] for r in rows if r["harvest_per_group"] > ceiling]
        print(f"    {p:13s} seasons whose harvest exceeds the ceiling: {len(over)}{' -> ' + str(over[:5]) if over else ' (none; the ledger holds)'}")
else:
    print("\n== 4. supply == no arenas.json: this run was not a persistent world")
