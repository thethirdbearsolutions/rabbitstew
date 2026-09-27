"""RBT-121 C: how saturated is the breeding lottery?  Reads an ecology run's lineage.jsonl (one row per
individual per season, energy after births) and reports per season: births, and how many individuals
stood at or above the birth threshold afterwards (breeder-eligible but not given a slot, or bred and
still above).  Read-only."""
import json, sys, collections
import numpy as np
path = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-19/P-801/lineage.jsonl"
T = 3.0
by = collections.defaultdict(lambda: collections.defaultdict(list))
for l in open(path):
    r = json.loads(l)
    by[r["population"]][r["generation"]].append(r)
for pop, gens in by.items():
    B, Q, N, E, S = [], [], [], [], []
    for g in sorted(gens):
        rows = gens[g]
        kids = [r for r in rows if r["age"] == 0 and r["evals"] == 0]
        adults = [r for r in rows if r["evals"] > 0]
        B.append(len(kids)); Q.append(sum(r["energy"] >= T for r in adults)); N.append(len(adults))
        E.append(np.median([r["energy"] for r in adults]) if adults else 0)
        S.append(np.mean([r["fitness"] for r in adults]) if adults else 0)
    B, Q, N = map(np.array, (B, Q, N))
    for lo, hi in ((0, 50), (50, 200), (200, 400), (400, len(B))):
        sl = slice(lo, hi)
        print(f"{pop:12s} seasons {lo:3d}-{hi:3d}: alive {N[sl].mean():5.1f}  births/season {B[sl].mean():4.2f}  "
              f"above-threshold after breeding {Q[sl].mean():5.1f}  median energy {np.mean(E[sl]):5.2f}  mean lifetime score {np.mean(S[sl]):.3f}")
