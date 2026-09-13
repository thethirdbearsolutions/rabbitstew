"""Depth of the lineages alive at a GIVEN season, not at the latest one (RBT-60).

The pre-registered checkpoints are season 150 and season 599, and the law
predicts depth at any season, so the read has to be anchored to the season
asked for rather than to however far the run has got.
usage: checkpoint.py RUN SEASON [SEASON...]
"""
import json, statistics as st, sys
from collections import defaultdict

run = sys.argv[1]
seasons = [int(x) for x in sys.argv[2:]]
recs = defaultdict(dict)
with open(f"{run}/lineage.jsonl") as f:
    for line in f:
        r = json.loads(line)
        # keep the record AS OF each season: last record at or before the target
        recs[r["population"]].setdefault(r["name"], {})[r["generation"]] = r
A = json.load(open(f"{run}/config.json"))["ecology"]["max_age"]
print(f"{run}   max_age = {A}\n")
print(f"{'season':>6} {'pop':12} {'alive':>5} {'fnd':>4} {'depth med':>9} {'min':>4} {'max':>4} {'2S/A':>6} {'ratio':>6} {'in 18-24?':>9}")
for S in seasons:
    for kind, byname in recs.items():
        # an individual is alive at S if it has a record at exactly S
        at = {n: gens[S] for n, gens in byname.items() if S in gens}
        if not at:
            print(f"{S:6d} {kind:12} — no records at this season")
            continue
        # parent lookup uses each ancestor's earliest record, which always exists
        first = {n: gens[min(gens)] for n, gens in byname.items()}
        ds, fnd = [], set()
        for r in at.values():
            d, cur, seen = 0, r, set()
            while cur["parents"] and cur["parents"][0] in first and cur["name"] not in seen:
                seen.add(cur["name"]); cur = first[cur["parents"][0]]; d += 1
            ds.append(d); fnd.add(cur["name"])
        med, pred = st.median(ds), 2 * S / A
        band = "YES" if 18 <= med <= 24 else "no"
        print(f"{S:6d} {kind:12} {len(at):5d} {len(fnd):4d} {med:9.1f} {min(ds):4d} {max(ds):4d} "
              f"{pred:6.1f} {med/pred:6.2f} {band:>9}")
