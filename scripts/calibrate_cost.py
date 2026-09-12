"""What does the ecology's basal living cost have to be?  Sets it so that living is possible but not free.
The food economy's opposite number (calibrate_food.py): this one measures the solo challenge the
ecology defaults to, where the gain is a closeness score rather than food.  Prints, for each candidate
cost, the share of random founders of each population that pay their way and how long a zero-scorer
lasts on its founding energy.  usage: calibrate_cost.py [N_PER_POPULATION] [SEASONS]"""
import sys

import numpy as np

from rabbitstew.ecology import EcologyConfig
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, BoutRunner, EvolutionConfig, draw_start_seeds, draw_terrain_seed, generation_sim, initial_population

n = int(sys.argv[1]) if len(sys.argv) > 1 else 60
seasons = int(sys.argv[2]) if len(sys.argv) > 2 else 4
COSTS = (0.02, 0.05, 0.1, 0.25)

# the ecology subcommand's own defaults, so the numbers describe the run somebody gets for free
evo = EvolutionConfig(seed=0, brain_model="rich", conventional_topology=True, population_size=n)
evo.sim.score, evo.sim.random_start, evo.sim.terrain = "closeness", True, "random"
eco = EcologyConfig()
rng = np.random.default_rng(0)
runner = BoutRunner(evo.sim, 1)
pops = {kind: list(initial_population(kind, evo, rng).members) for kind in (HOLISTIC, CONVENTIONAL)}
scores = {kind: [] for kind in pops}
for season in range(seasons):
    sim = generation_sim(evo, draw_terrain_seed(evo, rng), season)
    start = draw_start_seeds(evo, rng)[0]
    for kind, members in pops.items():
        scores[kind].append([r["fitness"][0] for r in runner.run([(m, None, False, start) for m in members], sim)])
runner.close()

for kind in pops:
    per_season = np.array(scores[kind])  # seasons x individuals
    earned = per_season.mean(axis=0)  # what each founder earns a season
    q = lambda a: " ".join(f"{np.percentile(a, p):.3f}" for p in (10, 50, 90))
    print(f"{kind:12s} n={n} over {seasons} seasons  score p10/50/90: {q(per_season.ravel())}  max {per_season.max():.3f}", flush=True)
    for cost in COSTS:
        net = earned - cost
        starve = eco.initial_energy / cost  # seasons a founder that never scores lives on its founding energy
        mark = " <- default" if cost == eco.living_cost else ""
        print(f"  cost {cost:<5} net-positive founders {100 * (net > 0).mean():4.0f}%  best net {net.max():+.3f}/season  zero-scorer lives {starve:.0f} of {eco.max_age} seasons{mark}")
