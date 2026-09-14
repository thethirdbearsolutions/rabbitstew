"""The hypothesis the first test did not actually try: a shared SEASON effect.

If a season is generous to everyone alive in it, then a parent and child whose lives overlap share
season draws, and their lifetime means correlate with no inheritance whatsoever. The first null test
drew each individual's yield independently, so it could not have detected this.

yield(i, s) = season[s] * w + individual noise * (1 - w)   -- parentage still carries NOTHING.
"""
import json, os, sys
import numpy as np
from rabbitstew.analysis import realised_heritability

OUT = os.environ.get("RBT82_OUT", "/tmp/rbt82-synth")  # bulk output, not committed


def synth(path, w, seasons=600, capacity=60, max_age=60, seed=0):
    rng = np.random.default_rng(seed)
    season = rng.normal(1.0, 1.0, seasons)      # the season's generosity, shared by all alive
    rows = []
    pop = [{"name": f"f{i}", "parents": [], "age": int(rng.integers(0, max_age)), "sum": 0.0, "evals": 0}
           for i in range(capacity)]
    counter = 0
    for s in range(seasons):
        for m in pop:
            m["sum"] += w * season[s] + (1 - w) * float(rng.normal(1.0, 1.0))
            m["evals"] += 1
            m["age"] += 1
        alive = [m for m in pop if m["age"] < max_age]
        dead = len(pop) - len(alive)
        pop = alive
        for _ in range(min(dead, capacity - len(pop))):
            if not pop:
                break
            p = pop[int(rng.integers(0, len(pop)))]
            counter += 1
            pop.append({"name": f"c{counter}", "parents": [p["name"]], "age": 0, "sum": 0.0, "evals": 0})
        for m in pop:
            rows.append({"generation": s, "population": "holistic", "name": m["name"],
                         "parents": list(m["parents"]), "fitness": round(m["sum"] / max(1, m["evals"]), 4),
                         "nodes": 3, "energy": 1.0, "age": m["age"], "evals": m["evals"], "last_score": 0.0})
    with open(os.path.join(path, "lineage.jsonl"), "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


print(f"{'season share w':>14} | " + "  ".join(f"seed {s}" for s in range(3)) + "   mean")
print("-" * 56)
for w in (0.0, 0.25, 0.5, 0.75, 1.0):
    got = []
    for s in range(3):
        d = os.path.join(OUT, f"w{int(w*100)}s{s}")
        os.makedirs(d, exist_ok=True)
        synth(d, w, seed=100 + s)
        h = realised_heritability(d, "holistic", min_evals=5)
        got.append(h["heritability"])
    print(f"{w:14.2f} | " + "  ".join(f"{g:+.3f}" for g in got) + f"   {np.mean(got):+.3f}")
print("\nTrue parent-offspring correlation is EXACTLY ZERO in every row: parentage carries nothing.")
print("Any number above zero is the instrument reading shared seasons as inheritance.")
