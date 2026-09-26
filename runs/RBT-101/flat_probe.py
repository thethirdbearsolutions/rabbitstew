"""RBT-101: the C4 endpoint prior that docs/held-out-challenges.md section 13 names as missing ("any measurement of
a foraging population on flat terrain"; "scripts/forage_probe.py with the run's config at --terrain flat on
committed bests, 64 paired draws, before the arm: a probe, not a run of the arm").

Each body alone in the arena, as scripts/forage_probe.py runs it, on paired draws: the same start and food seed
on the baseline's random terrain (fourteen obstacles, terrain seed = the draw) and on flat terrain.  Items eaten
per 15 s bout, flat minus random, per body; mean and t over the draws.  Solo, so it is a prior on what the
obstacles do to one forager's yield, not the ecology's group income; it is read for the point prediction only.

    python runs/RBT-101/flat_probe.py RUN_DIR SEED GEN [N] >> runs/RBT-101/flat_probe.txt
"""
import json
import math
import sys
from dataclasses import replace

import numpy as np

from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout

SEED0 = 7000


def bout(g, cfg, seed, terrain):
    w = replace(cfg.world, terrain=terrain, terrain_seed=(seed if terrain == "random" else None))
    c = replace(cfg, random_start=True, world=w)
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    p0 = sim.center_of_mass(0)[:2].copy()
    for _ in range(int(round(c.duration / c.control_dt))):
        sim.step()
    return float(sim.food_eaten[0]), float(np.linalg.norm(sim.center_of_mass(0)[:2] - p0))


def main(run, seed, gen, n=64):
    cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
    for kind in ("holistic", "conventional"):
        g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
        d, fr, ff, dr, df = [], [], [], [], []
        for s in range(n):
            a, x = bout(g, cfg, SEED0 + s, "random")
            b, y = bout(g, cfg, SEED0 + s, "flat")
            fr.append(a); ff.append(b); dr.append(x); df.append(y); d.append(b - a)
        m, sd = float(np.mean(d)), float(np.std(d, ddof=1))
        t = m / (sd / math.sqrt(n)) if sd > 0 else float("nan")
        print(f"{seed}\t{kind}\tg{gen}\tn={n}\tfood random {np.mean(fr):.3f}\tflat {np.mean(ff):.3f}\tflat-random {m:+.3f} (t {t:+.2f}, "
              f"{sum(x > 0 for x in d)} up {sum(x < 0 for x in d)} down)\tdisplacement random {np.mean(dr):.2f} m flat {np.mean(df):.2f} m", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 64)
