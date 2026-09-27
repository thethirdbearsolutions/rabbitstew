"""RBT-125 world gate, part C: how saturated the contrast channel is on the real bodies (the ruling's M7).

For every contrast cell, RBT-90 part 2's ten populations' designed-body bests (generations 0..590, the §A bodies, as
they are: no motif) each run 2 solo seasons (seeds 7000, 7001, the harness's first two).  Every control tick, every
food nose's reading c is recorded; reported per cell: the median and p90 of |c| over all noses and ticks, the same for
the wheel difference |c_L - c_R| (the routed compass's input), and the share of readings with |c| > 0.9.

    saturation.py BODIES_ROOT [--procs 4]
"""
import argparse
import json
import os
import sys
from multiprocessing import get_context

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout  # noqa: E402

SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
GENS = (0, 100, 200, 300, 400, 500, 590)
CELLS = ("PW-G2.5", "PW-G10", "PW-G2.5-tau1", "HP-G2.5", "HP-G10", "U-G2.5", "U-G10")
WHEELS = (1, 2)


def season(task):
    cell, path, seed = task
    cfg = SimConfig.from_dict(json.load(open(os.path.join(HERE, "worlds", cell, "config.json")))["sim"])
    sim = Simulation([Genotype.load(path)], cfg, spawns=spawn_layout(1, cfg, seed))
    sim.set_food_seed(seed)
    ph = sim.phenotypes[0]
    ks = [k for k, s in enumerate(sim.brains[0].sensors) if s.source == "food"]
    wheel = {ph.parts[sim.brains[0].sensors[k].part].node: k for k in ks if ph.parts[sim.brains[0].sensors[k].part].node in WHEELS}
    allc, diff = [], []
    orig = sim._food_contrast

    def rec(ri, _orig=orig):
        out = _orig(ri)
        allc.extend(abs(v) for v in out.values())
        if len(wheel) == 2:
            diff.append(abs(out[wheel[1]] - out[wheel[2]]))
        return out
    sim._food_contrast = rec
    for _ in range(int(round(cfg.duration / cfg.control_dt))):
        sim.step()
        if sim.exploded[0]:
            break
    return cell, np.array(allc, float), np.array(diff, float)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bodies_root")
    ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args()
    tasks = [(c, os.path.join(a.bodies_root, f"forage-{s}", "conventional", f"best_gen{g:04d}.json"), sd)
             for c in CELLS for s in SEEDS for g in GENS for sd in (7000, 7001)]
    with get_context("fork").Pool(a.procs) as pool:
        rows = pool.map(season, tasks, chunksize=4)
    print(f"# saturation of the contrast channel on the real bodies: {len(SEEDS) * len(GENS)} designed bests x 2 seasons per cell, no motif")
    print("| cell | median \\|c\\| | p90 \\|c\\| | share \\|c\\| > 0.9 | median \\|c_L - c_R\\| | p90 \\|c_L - c_R\\| |")
    print("|---|---|---|---|---|---|")
    for c in CELLS:
        A = np.concatenate([r[1] for r in rows if r[0] == c])
        D = np.concatenate([r[2] for r in rows if r[0] == c])
        print(f"| {c} | {np.median(A):.3f} | {np.quantile(A, 0.9):.3f} | {(A > 0.9).mean():.3f} | {np.median(D):.3f} | {np.quantile(D, 0.9):.3f} |")


if __name__ == "__main__":
    main()
