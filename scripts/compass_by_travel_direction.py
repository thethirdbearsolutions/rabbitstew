"""Per-robot test of RBT-69's resolution: does direction of travel predict who the motif helps?

The settled reading is that an identical antisymmetric motif is a compass for a
backward-driving population and an anti-compass for a forward-driving one.  That was
established by comparing two populations' *pooled* means.  This tests it one level down,
within a single population, where it makes a sharper prediction: the robots that drive
backward should be exactly the robots the motif helps.

Travel offsets come from scripts/travel_direction_check.py and are pasted in below rather
than recomputed, so the two measurements stay independent.
"""
import json, sys, numpy as np
from concurrent.futures import ProcessPoolExecutor
sys.path.insert(0, "scripts")
from compass_replication import install, RUN, GENERATIONS, SEED0, config
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

def bout(t):
    gen, cond, w, seed = t
    cfg = config("native")
    g = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    ph = synthesize(g, cfg.synthesis)
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, seed)); sim.set_food_seed(seed)
    install(sim.brains[0], ph, cond, w)
    for _ in range(int(round(cfg.duration / cfg.control_dt))): sim.step()
    return (gen, cond, seed, float(sim.food_eaten[0]))

if __name__ == "__main__":
    seeds = [SEED0 + i for i in range(64)]
    tasks = [(g, c, 32.0, s) for g in GENERATIONS for c in ("baseline", "compass") for s in seeds]
    with ProcessPoolExecutor(4) as p: rows = list(p.map(bout, tasks, chunksize=16))
    by = {(r[0], r[1], r[2]): r[3] for r in rows}
    # measured independently in travel_check.py
    travel = {0: -0.4, 100: +177.2, 200: -4.3, 300: -2.3, 400: +165.1, 500: +23.8, 590: +2.1}
    print(f"{'gen':>5s} {'travel':>9s} {'drives':>9s} | {'motif delta w=32':>17s}")
    deltas = {}
    for g in GENERATIONS:
        d = float(np.mean([by[(g,'compass',s)] - by[(g,'baseline',s)] for s in seeds]))
        deltas[g] = d
        back = abs(travel[g]) > 90
        print(f"{g:5d} {travel[g]:+8.1f}° {'BACKWARD' if back else 'forward':>9s} | {d:+17.3f}")
    fwd = [deltas[g] for g in GENERATIONS if abs(travel[g]) <= 90]
    bwd = [deltas[g] for g in GENERATIONS if abs(travel[g]) > 90]
    print(f"\nforward-drivers  (n={len(fwd)}): mean delta {np.mean(fwd):+.3f}   improved {sum(1 for x in fwd if x>0)}/{len(fwd)}")
    print(f"backward-drivers (n={len(bwd)}): mean delta {np.mean(bwd):+.3f}   improved {sum(1 for x in bwd if x>0)}/{len(bwd)}")
