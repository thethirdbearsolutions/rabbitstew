"""Group probe for RBT-17 (W5, crowded arena).  Eight copies of a season's best share one arena
over several seeds, intact and with the agent sensors, the food sensors, both noses, or every
environmental sensor blanked (outgoing weights of the sensor units zeroed before the run).
Replicates run_group() with a Simulation so the brains can be lesioned before sim.run().
Usage: python group_probe.py RUN GEN[,GEN...] [GROUP=8] [SEEDS=8]"""
import json, sys, numpy as np
from dataclasses import replace
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

run = sys.argv[1]
gens = [int(x) for x in sys.argv[2].split(",")]
group = int(sys.argv[3]) if len(sys.argv) > 3 else 8
nseeds = int(sys.argv[4]) if len(sys.argv) > 4 else 8
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
MODES = ("intact", "no_agent", "no_food", "no_noses", "no_env")


def blank(b, ph, mode):
    for i, ui in enumerate(ph.units):
        if ui.unit.kind != "sensor":
            continue
        src = ui.unit.source
        if mode == "no_agent" and src == "agent": b.W[:, i] = 0
        elif mode == "no_food" and src == "food": b.W[:, i] = 0
        elif mode == "no_noses" and src in ("food", "agent"): b.W[:, i] = 0
        elif mode == "no_env" and src != "oscillator": b.W[:, i] = 0


def group_trial(g, seed, mode):
    c = replace(cfg, random_start=True)
    gs = [g] * group
    spawns = spawn_layout(group, c, seed)
    sim = Simulation(gs, c, spawns=spawns)
    if c.food is not None:
        sim.set_food_seed(seed)
    ph = synthesize(g, c.synthesis)
    for b in sim.brains:
        blank(b, ph, mode)
    p0 = [sim.center_of_mass(i)[:2].copy() for i in range(group)]
    sim.run()
    return {
        "food": float(np.mean(sim.food_eaten)),
        "food_total": float(np.sum(sim.food_eaten)),
        "work": float(np.mean(sim.work)) / 1000,
        "disp": float(np.mean([np.linalg.norm(sim.center_of_mass(i)[:2] - p0[i]) for i in range(group)])),
        "score": float(np.mean([sim.score(i) for i in range(group)])),
    }


out = {}
for kind in ("holistic", "conventional"):
    for gen in gens:
        try:
            g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
        except FileNotFoundError:
            continue
        ph = synthesize(g, cfg.synthesis)
        srcs = sorted({u.unit.source for u in ph.units if u.unit.kind == "sensor"})
        n_agent = sum(1 for u in ph.units if u.unit.kind == "sensor" and u.unit.source == "agent")
        n_food = sum(1 for u in ph.units if u.unit.kind == "sensor" and u.unit.source == "food")
        print(f"{kind:12s} g{gen:3d} parts {len(ph.parts):2d} units {len(ph.units):3d} sensors {srcs} (food x{n_food}, agent x{n_agent}); group {group}, {nseeds} seeds", flush=True)
        row = {}
        for mode in MODES:
            rs = [group_trial(g, 9000 + s, mode) for s in range(nseeds)]
            row[mode] = {k: float(np.mean([r[k] for r in rs])) for k in rs[0]}
            row[mode]["food_sd"] = float(np.std([r["food"] for r in rs]))
            print(f"     {mode:9s} items/robot {row[mode]['food']:.3f} (sd over seeds {row[mode]['food_sd']:.2f})  score {row[mode]['score']:+.3f}  disp {row[mode]['disp']:.2f} m  work {row[mode]['work']:.1f} kJ", flush=True)
        out[f"{kind}_g{gen}"] = {"sensors": srcs, "n_food": n_food, "n_agent": n_agent, "parts": len(ph.parts), "units": len(ph.units), "modes": row}
json.dump(out, open(f"{run}/../group_probe_g{'_'.join(map(str, gens))}.json", "w"), indent=1)
