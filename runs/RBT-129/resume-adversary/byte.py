import sys, os
from rabbitstew.ecology import Ecology, EcologyConfig
from rabbitstew.evolution import EvolutionConfig
from rabbitstew.simulation import FoodConfig, SimConfig
from rabbitstew.world import WorldConfig
import rabbitstew.ecology as E
print("module", E.__file__, file=sys.stderr)
out, variant = sys.argv[1], sys.argv[2]
food = FoodConfig(items=4, radius=1.5, eat_radius=0.4, regrow_delay=2) if variant != "plain" else FoodConfig(items=4, radius=1.5, eat_radius=0.4)
evo = EvolutionConfig(seed=7, brain_model="foraging", conventional_topology=True, workers=int(sys.argv[3]),
      sim=SimConfig(duration=0.3, random_start=True, score="food", world=WorldConfig(terrain="random"), food=food))
kw = dict(seasons=8, capacity=6, challenge="foraging", group_size=2, max_age=40, birth_threshold=0.0, birth_cost=0.0,
          starvation=False, log_every=1000, sweep_log=True)
if variant == "merge": kw.update(merge_after=3, pooled_capacity=12)
if variant == "starve": kw.update(starvation=True, living_cost=5.0, birth_threshold=50.0, seasons=10)
Ecology(evo, EcologyConfig(**kw), out_dir=out, log=None).run()
