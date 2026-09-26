"""Four-lesion protocol of scripts/situated.py for named cases; usage: situated_case.py OUT.json LABEL=RUN/holistic/FILE ..."""
import json, sys, numpy as np
from dataclasses import replace
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize
from rabbitstew.analysis import controller_descriptors
src = open("scripts/situated.py").read()
# reuse the two helper functions verbatim without running the script's top-level loop
helpers = src[src.index("def lesioned_solo"):src.index("results = []")]
exec(helpers)
SEEDS = list(range(6000, 6008))
out_path = sys.argv[1]
results = []
for spec in sys.argv[2:]:
    label, path = spec.split("=", 1)
    run = path.split("/holistic/")[0]
    cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
    g = Genotype.load(path)
    w = wiring(g, cfg)
    row = {"label": label, "wiring": w, "scores": {}}
    for mode in ("intact", "no_env_sensors", "no_oscillators", "no_global", "no_local"):
        rs = [lesioned_solo(g, cfg, s, mode) for s in SEEDS]
        row["scores"][mode] = {k: float(np.mean([r[k] for r in rs])) for k in rs[0]}
    results.append(row)
    sc = row["scores"]
    print(f"{label:32s} units {w['units']:3d} (global {w['global_units']}, local {w['local_units']} over {w['parts']} parts)  links same-part {w['links_same_part']} cross-part {w['links_cross_part']} global {w['links_global']}  reflex arcs {w['reflex_arcs']}  effectors live {w['live_effectors']} env-driven {w['env_driven_effectors']} osc {w['osc_driven']} bias-only {w['bias_only_effectors']}", flush=True)
    print("   progress: " + "  ".join(f"{m} {sc[m]['progress']:+.2f}" for m in sc) + "   |   tat: " + "  ".join(f"{m} {sc[m]['tat']:.2f}" for m in sc), flush=True)
json.dump(results, open(out_path, "w"), indent=1)
