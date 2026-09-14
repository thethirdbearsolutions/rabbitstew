"""How much of a season's yield is shared by everyone alive in it?

The synthetic sweep shows the yield-heritability statistic reads up to +0.43 with a true value of
zero when a season effect is strong. That is only a real problem for the programme's numbers if the
ecology actually HAS a strong season effect. This measures it on a real run, from the per-season
`last_score` the RBT-27 telemetry logs for every living individual every season.

season share = between-season variance of individual season scores / total variance
             = the intraclass correlation by season, which is exactly the `w` of the sweep.
"""
import json, os, sys
from collections import defaultdict
import numpy as np
from rabbitstew.analysis import realised_heritability
from rabbitstew.ecology import Ecology, EcologyConfig
from rabbitstew.evolution import EvolutionConfig
from rabbitstew.simulation import FoodConfig, SimConfig

OUT = os.environ.get("RBT82_OUT", "/tmp/rbt82-neutral")  # bulk output, not committed
os.makedirs(OUT, exist_ok=True)

evo = EvolutionConfig(seed=801, brain_model="foraging", conventional_topology=True, workers=4,
                      sim=SimConfig(duration=15.0, random_start=True, score="food",
                                    food=FoodConfig(items=12, radius=3.0, eat_radius=0.35, decay=1.0,
                                                    regrow=True, clearance=0.8, work_cost=0.03)))
# The neutral control's economy, as docs/foraging-world.md describes it: no starvation, free
# breeding, turnover by age only -- so yield cannot be selected on and true heritability is ~0.
eco = EcologyConfig(seasons=120, capacity=20, challenge="foraging", group_size=4, max_age=20,
                    starvation=False, birth_threshold=0.0, birth_cost=0.0, living_cost=0.0,
                    initial_energy=3.0, stagger_ages=True, log_every=1000)
Ecology(evo, eco, out_dir=OUT, log=None).run()

rows = [json.loads(l) for l in open(os.path.join(OUT, "lineage.jsonl"))]
for kind in ("holistic", "conventional"):
    by_season = defaultdict(list)
    for r in rows:
        if r["population"] == kind and r.get("evals", 0) > 0:
            by_season[r["generation"]].append(float(r.get("last_score", 0.0)))
    seasons = [v for v in by_season.values() if len(v) > 1]
    allv = np.array([x for v in seasons for x in v], dtype=float)
    means = np.array([np.mean(v) for v in seasons], dtype=float)
    counts = np.array([len(v) for v in seasons], dtype=float)
    grand = allv.mean()
    between = float(np.sum(counts * (means - grand) ** 2) / allv.size)
    total = float(allv.var())
    h5 = realised_heritability(OUT, kind, min_evals=5)
    print(f"{kind:13s} season share w = {between / total:.3f}   "
          f"(between {between:.4f} of total {total:.4f}; {len(seasons)} seasons, {allv.size} rows)")
    print(f"{'':13s} reported yield heritability = {h5['heritability']} (n={h5['n']}, min_evals=5)")
