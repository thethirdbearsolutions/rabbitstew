"""Supplementary heritability for a survival (mu+lambda) run.

`rabbitstew heritability` pairs every lineage record with its birth parents.  Under --survival a
survivor is re-logged every generation under a new name with its running-mean fitness and its
original parents, so it is counted once per generation it survives.  This variant pairs each
newborn child once, on its first evaluation (`last_fitness`), with the mean of its parents'
fitness as logged in the generation it was bred from (the parents' running mean at that point).
"""
import sys, json, numpy as np
run = sys.argv[1]
windows = [None, (1, 51), (51, 101), (101, 151)]
recs = [json.loads(l) for l in open(f"{run}/lineage.jsonl") if l.strip()]
for kind in ("holistic", "conventional"):
    byname = {r["name"]: r for r in recs if r["population"] == kind}
    for w in windows:
        xs, ys = [], []
        for r in byname.values():
            if not r["parents"] or r.get("survivor_of"):
                continue
            if w and not (w[0] <= r["generation"] < w[1]):
                continue
            ps = [byname[p]["fitness"] for p in r["parents"] if p in byname]
            if ps:
                xs.append(float(np.mean(ps))); ys.append(float(r.get("last_fitness", r["fitness"])))
        n = len(xs)
        h = round(float(np.corrcoef(xs, ys)[0, 1]), 4) if n >= 10 and np.std(xs) > 0 and np.std(ys) > 0 else None
        label = "all" if w is None else f"gens {w[0]}-{w[1]-1}"
        print(f"{kind:12s} {label:14s} newborn-only heritability {h} (n={n})")
