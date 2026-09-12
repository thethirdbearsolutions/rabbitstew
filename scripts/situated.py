"""Is the holistic controller situated (does its behaviour depend on sensing) and distributed (do local
brains carry it)?  Fresh-draw solo trials of each holistic best under lesions: env sensors blanked,
oscillators blanked, global brain silenced, local brains silenced.  Plus wiring counts."""
import json, sys, numpy as np
from dataclasses import replace
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize
from rabbitstew.analysis import controller_descriptors

CASES = [
    ("A-301 final", "redesign/A-301", "best_gen0199.json"),
    ("A-302 final", "redesign/A-302", "best_gen0199.json"),
    ("C-301 g60 (end of solo phase)", "redesign/C-301", "best_gen0060.json"),
    ("C-301 g100 (competitive)", "redesign/C-301", "best_gen0100.json"),
    ("cap-401 g25 (solo curriculum)", "solo/cap-401", "best_gen0025.json"),
    ("cap-402 g25 (solo curriculum)", "solo/cap-402", "best_gen0025.json"),
    ("random/rich-201 final", "random/rich-201", "best_gen0249.json"),
    ("random/paper-201 final", "random/paper-201", "best_gen0249.json"),
    ("flat/rich-202 final", "flat/rich-202", "best_gen0249.json"),
]
SEEDS = list(range(6000, 6000 + int(sys.argv[1]) if len(sys.argv) > 1 else 6008))

def lesioned_solo(g, cfg, seed, mode):
    cfg = replace(cfg, opponent_proxy=True)
    spawn = spawn_layout(2, cfg, seed)[0]
    sim = Simulation([g], cfg, spawns=[spawn])
    b = sim.brains[0]
    ph = synthesize(g, cfg.synthesis)
    for i, ui in enumerate(ph.units):
        kind = ui.unit.kind
        is_env_sensor = kind == "sensor" and ui.unit.source != "oscillator"
        is_osc = kind == "sensor" and ui.unit.source == "oscillator"
        silence = False
        if mode == "no_env_sensors" and is_env_sensor: b.W[:, i] = 0.0
        elif mode == "no_oscillators" and is_osc: b.W[:, i] = 0.0
        elif mode == "no_global" and ui.part is None: silence = True
        elif mode == "no_local" and ui.part is not None and kind != "effector": silence = True  # effectors keep their bias; only local thought is removed
        if silence:
            b.W[i, :] = 0.0; b.W[:, i] = 0.0; b.bias[i] = 0.0
    sim.run()
    return {"progress": float(sim.progress(0)), "tat": float(sim.time_at_target(0)), "closeness": float(sim.closeness(0))}

def wiring(g, cfg):
    ph = synthesize(g, cfg.synthesis)
    units = ph.units
    parts = {}
    same_part = cross_part = global_links = 0
    for s, d, w in ph.links:
        ps, pd = units[s].part, units[d].part
        if ps is None or pd is None: global_links += 1
        elif ps == pd: same_part += 1
        else: cross_part += 1
    # reflex arcs: a sensor and an effector of the same part joined by a path that stays inside the part
    out = {i: [] for i in range(len(units))}
    for s, d, _ in ph.links: out[s].append(d)
    arcs = 0
    for i, ui in enumerate(units):
        if ui.unit.kind != "sensor" or ui.part is None: continue
        seen, frontier = {i}, [i]
        while frontier:
            u = frontier.pop()
            for v in out[u]:
                if v in seen or units[v].part != ui.part: continue
                seen.add(v)
                if units[v].unit.kind == "effector": arcs += 1
                else: frontier.append(v)
    d = controller_descriptors(g, cfg)
    n_local = sum(1 for u in units if u.part is not None)
    return {"units": d["units"], "global_units": d["global_neurons"], "local_units": n_local, "parts": len(ph.parts),
            "links_same_part": same_part, "links_cross_part": cross_part, "links_global": global_links,
            "live_effectors": d["live_effectors"], "env_driven_effectors": d["env_driven_effectors"], "osc_driven": d["oscillator_driven_effectors"],
            "bias_only_effectors": d["active_effectors"] - d["driven_effectors"], "reflex_arcs": arcs, "sensor_sources": d["sensor_sources"]}

results = []
for label, run, fname in CASES:
    cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
    g = Genotype.load(f"{run}/holistic/{fname}")
    w = wiring(g, cfg)
    row = {"label": label, "wiring": w, "scores": {}}
    for mode in ("intact", "no_env_sensors", "no_oscillators", "no_global", "no_local"):
        rs = [lesioned_solo(g, cfg, s, mode) for s in SEEDS]
        row["scores"][mode] = {k: float(np.mean([r[k] for r in rs])) for k in rs[0]}
    results.append(row)
    sc = row["scores"]
    print(f"{label:32s} units {w['units']:3d} (global {w['global_units']}, local {w['local_units']} over {w['parts']} parts)  links same-part {w['links_same_part']} cross-part {w['links_cross_part']} global {w['links_global']}  reflex arcs {w['reflex_arcs']}  effectors live {w['live_effectors']} env-driven {w['env_driven_effectors']} osc {w['osc_driven']} bias-only {w['bias_only_effectors']}", flush=True)
    print("   progress: " + "  ".join(f"{m} {sc[m]['progress']:+.2f}" for m in sc) + "   |   tat: " + "  ".join(f"{m} {sc[m]['tat']:.2f}" for m in sc), flush=True)
json.dump(results, open("situated.json", "w"), indent=1)
print("done")
