"""RBT-101: the C4 endpoint prior that docs/held-out-challenges.md section 13 names as missing ("any measurement of
a foraging population on flat terrain"; "scripts/forage_probe.py with the run's config at --terrain flat on
committed bests, 64 paired draws, before the arm: a probe, not a run of the arm").

Each body alone in the arena, as scripts/forage_probe.py runs it, on paired draws: the same start and food seed
on the baseline's random terrain (fourteen obstacles, terrain seed = the draw) and on flat terrain.  Items eaten
per 15 s bout, flat minus random, per body; mean and t over the draws.  Solo, so it is a prior on what the
obstacles do to one forager's yield, not the ecology's group income; it is read for the point prediction only.

    python runs/RBT-101/flat_probe.py RUN_DIR SEED GEN [N] >> runs/RBT-101/flat_probe.txt
    python runs/RBT-101/flat_probe.py --summary runs/RBT-101/flat_probe.txt   (across seeds, from the rows above)
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


def summary(path):
    import re
    import statistics as st
    T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262}
    d = {}
    for line in open(path):
        if line.startswith("#") or "\t" not in line:
            continue
        f = line.split("\t")
        d.setdefault(f[1], {})[f[0]] = float(re.search(r"flat-random ([-+][0-9.]+)", line).group(1))
    seeds = [s for s in d["holistic"] if s in d["conventional"]]
    rows = [(k, [d[k][s] for s in seeds]) for k in ("conventional", "holistic")]
    rows.append(("holistic - conventional", [d["holistic"][s] - d["conventional"][s] for s in seeds]))
    print(f"# summary over {len(seeds)} seeds ({' '.join(seeds)}): flat - random items per bout, mean and 95% t(n-1) interval over seeds")
    for k, v in rows:
        n, m, sd = len(v), st.fmean(v), st.stdev(v)
        hw = T975[n - 1] * sd / math.sqrt(n)
        print(f"# {k:24s} mean {m:+.3f}  [{m - hw:+.3f}, {m + hw:+.3f}]  positive {sum(x > 0 for x in v)}/{n}  negative {sum(x < 0 for x in v)}/{n}")


if __name__ == "__main__":
    if sys.argv[1] == "--summary":
        summary(sys.argv[2])
        sys.exit(0)
    main(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]) if len(sys.argv) > 4 else 64)
