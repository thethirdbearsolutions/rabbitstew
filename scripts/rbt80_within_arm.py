"""RBT-80 (c): carriers against non-carriers INSIDE the seeded arm, per seed.

The ticket's measure list asked for "yield of carriers vs non-carriers once the
seeded population is mixed". The report gave only the arm-level contrast
(seeded minus control), which cannot separate THE COMPASS from THE INSTALLATION
-- and the cross-seed dose-response is flat (seed C carries 0.21 more than seed
B and earns +0.002 more). RBT-78's agent-smell control is the precedent.

Design. Within the seeded arm only, over the sampled plateau seasons 250-299:
classify every living conventional individual as carrier or not by the same
re-signed steering-gain predicate as the carriage tables, then compare the
season score (`last_score` in lineage.jsonl) of the two groups. PAIRED BY
SEASON -- the difference of the two group means is taken within each season and
then averaged -- because terrain and food seeds change every season and a
pooled mean would let seasonal difficulty masquerade as a group effect.

Individuals with `evals` == 0 (newborns, never evaluated, last_score 0.0 by
construction) are excluded; including them would score a group by its birth
rate rather than its foraging.

Reported under both the depth-2 predicate (the shortest path that contains the
routed motif RBT-65 installs) and the depth-4 one the original report used.
The depth-1 term is identically zero on every genome here -- see
scripts/rbt80_predicates.py -- so it defines no groups and is not reported.

Usage: ./v/bin/python scripts/rbt80_within_arm.py [procs]
"""
import json, os, sys, numpy as np
from multiprocessing import Pool
from rabbitstew.analysis import steering_terms
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig
from rabbitstew.synthesis import synthesize

ROOT = "runs/RBT-80"
SEEDS = {"A": "seedA", "B": "seedB", "C": "seedC"}
ARM = "seeded"
THRESH = 16.0
FOUNDER_BACKWARD = True
DEPTHS = (2, 4)
PROCS = int(sys.argv[1]) if len(sys.argv) > 1 else 4


def gains(task):
    root, name, cfgd = task
    p = f"{root}/{ARM}/conventional/genomes/{name}.json"
    if not os.path.exists(p):
        return name, None
    ph = synthesize(Genotype.load(p), SimConfig.from_dict(cfgd).synthesis)
    st = steering_terms(ph, depth=1)
    if st is None:
        return name, None
    return name, {d: steering_terms(ph, depth=d)["path"]["a"] for d in DEPTHS}


def rows_by_season(root):
    out = {}
    for line in open(f"{root}/{ARM}/lineage.jsonl"):
        r = json.loads(line)
        if r["population"] == "conventional":
            out.setdefault(r["generation"], []).append(r)
    return out


if __name__ == "__main__":
    print("RBT-80 (c) — carriers vs non-carriers INSIDE the seeded arm")
    print("plateau seasons 250-299 sampled every 10; paired by season; "
          f"carrier iff re-signed a >= +{THRESH:g}\n")
    for lab, sd in SEEDS.items():
        root = f"{ROOT}/{sd}"
        if not os.path.isdir(f"{root}/{ARM}"):
            continue
        cache = json.load(open(f"{root}/dircache.json"))[ARM]
        cfgd = json.load(open(f"{root}/{ARM}/config.json"))["sim"]
        rec = rows_by_season(root)
        seasons = [s for s in sorted(rec) if 250 <= s <= 299 and (s % 10 == 0 or s == max(rec))]
        names = sorted({r["name"] for s in seasons for r in rec[s]})
        with Pool(PROCS) as p:
            g = dict(p.map(gains, [(root, n, cfgd) for n in names], chunksize=8))
        print(f"### seed {lab}: {len(seasons)} seasons, {len(names)} distinct genotypes")
        print("| depth | seasons used | carrier n | non-carrier n | carrier mean | "
              "non-carrier mean | paired difference | 95% CI | seasons carrier ahead |")
        print("|---|---|---|---|---|---|---|---|---|")
        for d in DEPTHS:
            per, nc, nn = [], 0, 0
            for s in seasons:
                A, B = [], []
                for r in rec[s]:
                    if r.get("evals", 0) < 1 or g.get(r["name"]) is None:
                        continue
                    head = cache.get(r["name"])
                    if head is None:
                        continue
                    back = abs(head) > 90
                    a = g[r["name"]][d] if (back == FOUNDER_BACKWARD) else -g[r["name"]][d]
                    (A if a >= THRESH else B).append(r["last_score"])
                if A and B:
                    per.append((s, float(np.mean(A)), float(np.mean(B))))
                    nc += len(A); nn += len(B)
            if not per:
                print(f"| {d} | 0 | - | - | - | - | no season had both groups | - | - |")
                continue
            diff = np.array([x[1] - x[2] for x in per])
            rng = np.random.default_rng(11)
            bs = np.array([rng.choice(diff, diff.size).mean() for _ in range(20000)])
            print(f"| {d} | {len(per)}/{len(seasons)} | {nc} | {nn} | "
                  f"{np.mean([x[1] for x in per]):.3f} | {np.mean([x[2] for x in per]):.3f} | "
                  f"{diff.mean():+.3f} | [{np.percentile(bs,2.5):+.3f}, "
                  f"{np.percentile(bs,97.5):+.3f}] | {int((diff>0).sum())}/{len(per)} |")
        print()
