"""Wiring of a best: controller descriptors (sensor_sources, env_driven_effectors) and which
segments carry the food/agent sensors.  Usage: wiring.py <run> <kind> <gen>"""
import json, sys
from rabbitstew.analysis import controller_descriptors
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig
from rabbitstew.synthesis import synthesize
run, kind, gen = sys.argv[1], sys.argv[2], int(sys.argv[3])
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
d = controller_descriptors(g, cfg)
print(f"{kind} g{gen}: sensor_sources {d['sensor_sources']}  env_driven_effectors {d['env_driven_effectors']}/{d['driven_effectors']} driven "
      f"({d['live_effectors']} live, {d['active_effectors']} active); units {d['units']} links {d['links']} global_neurons {d['global_neurons']} mean_sensor_path {d['mean_sensor_path']}")
ph = synthesize(g, cfg.synthesis)
for i, u in enumerate(ph.units):
    if u.unit.kind == "sensor" and u.unit.source in ("food", "agent"):
        p = ph.parts[u.part] if u.part is not None else None
        desc = "global" if p is None else f"part {u.part} (parent {p.parent}, joint {getattr(p.joint_type, 'name', p.joint_type)})"
        outs = [(j, round(w, 2)) for s, j, w in ph.links if s == i]
        print(f"  unit {i} {u.unit.source} sensor on {desc}; outgoing links -> {outs}")
