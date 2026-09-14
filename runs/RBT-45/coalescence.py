"""RBT-45 companion: how independent are the 60 conventional genotypes at season 599?

The drift grid gives a per-lineage probability.  Comparing it to "0 of 60 saved
genotypes" only works if those 60 are 60 lineages.  They are not, and this counts
by how much: distinct founders behind them, and the number of distinct ancestors
they collapse to at each depth back.
"""

from __future__ import annotations

import json

from rabbitstew.analysis import read_lineage

RUN_DIR = "runs/RBT-23/W4b-801"


def main(population="conventional"):
    lin = read_lineage(RUN_DIR)
    recs = {name: r for (pop, name), r in lin.items() if pop == population}
    alive = [r for r in recs.values() if r["generation"] == 599]

    # distinct ancestors d reproduction events back, along the chain of first parents
    levels = []
    for d in range(0, 26):
        anc = set()
        for r in alive:
            cur = r
            for _ in range(d):
                if not cur["parents"] or cur["parents"][0] not in recs:
                    break
                cur = recs[cur["parents"][0]]
            anc.add(cur["name"])
        levels.append({"depth_back": d, "distinct_ancestors": len(anc)})

    founders = set()
    for r in alive:
        seen, stack = set(), [r["name"]]
        while stack:
            nm = stack.pop()
            if nm in seen or nm not in recs:
                continue
            seen.add(nm)
            rec = recs[nm]
            if not rec["parents"]:
                founders.add(nm)
            stack.extend(rec["parents"])
    out = {
        "population": population,
        "alive_at_599": len(alive),
        "distinct_founders_behind_them": len(founders),
        "distinct_first_parent_ancestors_by_depth": levels,
        "total_unique_individuals_in_run": len(recs),
        "total_founders_in_run": sum(1 for r in recs.values() if not r["parents"]),
    }
    print(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    both = {p: main(p) for p in ("conventional", "holistic")}
    with open("runs/RBT-45/coalescence.json", "w") as f:
        json.dump(both, f, indent=1)
