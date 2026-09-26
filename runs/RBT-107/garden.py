"""RBT-107: the common garden.  A population's income on fixed worlds, flat and random, by the ecology's own bout.

    python runs/RBT-107/garden.py RUN_DIR KIND SEASON LABEL [--draws J] [--workers W] >> OUT.txt

The population is every KIND individual alive at SEASON in RUN_DIR (RBT-92's Arm on RUN_DIR/lineage-last.txt), each
loaded from its genome at birth (RUN_DIR/KIND/genomes/NAME.json).  Its income is measured the way the ecology measures
a season, with the ecology's own group bout (BoutRunner.run_groups: groups of four of the same fauna share an arena,
gain = food - work_cost x work, an exploder gains 0), on J fixed worlds that are the same for every population, arm,
seed and season read (and the same price, unless --work-cost sets another for every population alike):
    world j (j = 0..J-1):  terrain_seed_j, start_seed_j   from numpy default_rng([107, 1000 + j])
                           the grouping: a permutation of the population sorted by name, from default_rng([107, j])
and on each world twice, on the baseline's random terrain (terrain_seed_j) and on flat ground, with the same start
seed and the same groups.  The simulator config is the RBT-90 part 2 baseline's (runs/RBT-90/forage-SEED/config.json
"sim"), the same for every arm, so the only thing that differs between two rows is who is in the population.

Output: one row per individual, tab separated, with a '#' header naming run, kind, season, label, J and time:
    label seed kind season name  gain_flat gain_random  food_flat food_random  work_flat work_random  exploded_flat exploded_random
each a mean over the J worlds.  garden_readout.py reads these rows; nothing here scores anything.
"""
import argparse
import importlib.util
import json
import os
import sys
import time
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
from rabbitstew.evolution import BoutRunner, EvolutionConfig  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402

_spec = importlib.util.spec_from_file_location("r92", os.path.join(ROOT, "runs", "RBT-92", "readout.py"))
R92 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(R92)


def worlds(J):
    out = []
    for j in range(J):
        r = np.random.default_rng([107, 1000 + j])
        out.append((int(r.integers(0, 2**31 - 1)), int(r.integers(0, 2**31 - 1))))
    return out


def base_sim(seed):
    raw = json.load(open(os.path.join(ROOT, "runs", "RBT-90", f"forage-{seed}", "config.json")))
    raw.pop("ecology", None)
    return EvolutionConfig.from_dict(raw).sim


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("kind", choices=("holistic", "conventional"))
    ap.add_argument("season", type=int)
    ap.add_argument("label")
    ap.add_argument("--draws", type=int, default=8)
    ap.add_argument("--world-start", type=int, default=0,
                    help="first world index: the population is run on worlds [world-start, world-start + draws); world j is the "
                         "same whatever the start, so parts run separately merge exactly (garden_merge.py)")
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--work-cost", type=float, default=None,
                    help="the garden's price per kJ (default: the baseline's 0.03); the C2 positive control uses 0.08")
    a = ap.parse_args()
    cfg = json.load(open(os.path.join(a.run, "config.json")))
    seed = int(cfg["seed"])
    arm = R92.Arm(a.run)
    names = sorted(arm.alive_at(a.kind, a.season))
    if not names:
        print(f"# {a.label} seed {seed} {a.kind} season {a.season}: nobody alive (extinct); no rows")
        return
    pop = [Genotype.load(os.path.join(a.run, a.kind, "genomes", f"{n}.json")) for n in names]
    sim0 = base_sim(seed)
    if a.work_cost is not None:
        sim0 = replace(sim0, food=replace(sim0.food, work_cost=a.work_cost))
    runner = BoutRunner(sim0, a.workers)
    acc = {n: {k: 0.0 for k in ("gf", "gr", "ff", "fr", "wf", "wr", "xf", "xr")} for n in names}
    t0 = time.time()
    for j, (tseed, sseed) in list(enumerate(worlds(a.world_start + a.draws)))[a.world_start:]:
        order = np.random.default_rng([107, j]).permutation(len(pop))
        groups = [[int(i) for i in order[g:g + 4]] for g in range(0, len(order), 4)]
        for terr, tag in (("random", "r"), ("flat", "f")):
            w = replace(sim0.world, terrain=terr, terrain_seed=(tseed if terr == "random" else None))
            sim = replace(sim0, world=w)
            res = runner.run_groups([([pop[i] for i in grp], sseed) for grp in groups], sim)
            for grp, rs in zip(groups, res):
                for i, r in zip(grp, rs):
                    d = acc[names[i]]
                    d["g" + tag] += 0.0 if r["exploded"] else float(r["score"])
                    d["f" + tag] += float(r["food"])
                    d["w" + tag] += float(r["work"])
                    d["x" + tag] += 1.0 if r["exploded"] else 0.0
    J = float(a.draws)
    print(f"# garden {a.label} seed {seed} {a.kind} season {a.season} n={len(names)} J={a.draws} worlds={a.world_start}..{a.world_start + a.draws - 1} run={a.run} "
          f"work_cost={sim0.food.work_cost} ({time.time() - t0:.0f} s, workers {a.workers})")
    for n in names:
        d = acc[n]
        print("\t".join([a.label, str(seed), a.kind, str(a.season), n] +
                        [f"{d[k] / J:.4f}" for k in ("gf", "gr", "ff", "fr", "wf", "wr")] + [f"{int(d['xf'])}", f"{int(d['xr'])}"]),
              flush=True)


if __name__ == "__main__":
    main()
