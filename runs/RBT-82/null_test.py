"""Does `realised_heritability` read zero when the truth is zero by construction?

Queue item 6 of the coordinator's 2026-09-14 doc: the 801 neutral control's yield heritability is
0.52/0.60 in the docs where RBT-71's seed 804 neutral control reads 0.07. Neither run's lineage is
committed, so neither figure can be re-read. What CAN be checked is the instrument.

This synthesises a lineage in the ecology's own format where every individual's per-season yield is
drawn i.i.d. from one distribution, independent of parentage -- so the TRUE parent-offspring
correlation of lifetime mean yield is exactly zero. The demography is the ecology's: slot-limited
births, death by age, survivors re-logged every season with a running mean, which is what
read_lineage reads the last of.

If the tool returns a large number here, the statistic behind strand 2's headline is measuring
something other than inheritance.
"""
import json, os, sys
import numpy as np
from rabbitstew.analysis import realised_heritability

OUT = os.environ.get("RBT82_OUT", "/tmp/rbt82-synth")  # bulk output, not committed


def synth(path, seasons=600, capacity=60, max_age=60, overlap=True, seed=0, min_evals=5):
    """One neutral ecology's lineage, yields i.i.d. and parentage irrelevant."""
    rng = np.random.default_rng(seed)
    rows = []
    pop = [{"name": f"f{i}", "parents": [], "age": int(rng.integers(0, max_age)),
            "sum": 0.0, "evals": 0} for i in range(capacity)]
    counter = 0
    for s in range(seasons):
        # every living individual faces a season; the yield is the same draw for everyone's
        # distribution and carries nothing from a parent
        for m in pop:
            m["sum"] += float(rng.normal(1.0, 1.0))
            m["evals"] += 1
            m["age"] += 1
        # deaths by age only (the neutral control: no starvation)
        alive = [m for m in pop if m["age"] < max_age]
        dead = len(pop) - len(alive)
        pop = alive
        # slot-limited births; a random living individual breeds
        for _ in range(min(dead, capacity - len(pop))):
            if not pop:
                break
            p = pop[int(rng.integers(0, len(pop)))]
            counter += 1
            pop.append({"name": f"c{counter}", "parents": [p["name"]], "age": 0, "sum": 0.0, "evals": 0})
        for m in pop:
            rows.append({"generation": s, "population": "holistic", "name": m["name"],
                         "parents": list(m["parents"]),
                         "fitness": round(m["sum"] / max(1, m["evals"]), 4),
                         "nodes": 3, "energy": 1.0, "age": m["age"], "evals": m["evals"],
                         "last_score": 0.0})
    with open(os.path.join(path, "lineage.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return len(rows)


for label, seed in (("seed 0", 0), ("seed 1", 1), ("seed 2", 2)):
    d = os.path.join(OUT, f"run{seed}")
    os.makedirs(d, exist_ok=True)
    n = synth(d, seed=seed)
    for me in (0, 5):
        h = realised_heritability(d, "holistic", min_evals=me)
        print(f"{label}: min_evals={me}  n={h['n']:4d}  heritability = {h['heritability']}")
print("\nTrue parent-offspring correlation of lifetime mean yield in every run above: EXACTLY ZERO.")
print("Every yield is an i.i.d. draw; parentage carries nothing.")
