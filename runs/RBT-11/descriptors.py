"""Controller descriptors of the holistic and conventional bests at given generations."""
import json, sys
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig
from rabbitstew.analysis import controller_descriptors
run = sys.argv[1]; gens = [int(x) for x in sys.argv[2:]]
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
out = {}
for kind in ("holistic", "conventional"):
    for gen in gens:
        g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
        d = controller_descriptors(g, cfg)
        out[f"{kind}/{gen}"] = d
        keys = ["units", "global_neurons", "live_effectors", "driven_effectors", "env_driven_effectors", "oscillator_driven_effectors", "cyclic_units", "sensor_sources"]
        print(kind, gen, {k: d.get(k) for k in keys})
json.dump(out, open(f"{run}/descriptors.json", "w"), indent=1)
