"""RBT-120 readout adversary: M3 at every generation, not only at final/.

    PYTHONPATH=<checkout at 9132b78> python m3_every_generation.py [--workers 4] runs/RBT-120/B<k>/<seed> ...

K4 recompiles final/ members under the run's config, and the compile applies the cap, so K4 would pass even if a
run had scored some generations unbudgeted.  This re-scores the committed per-generation champion
(<line>/holistic/best_genNNNN.json) of every holistic line at every generation, on that generation's own worlds
(history.json: terrain_seed, start_seeds), twice: under the directory's config.json (motor_budget 1.77) and with the
budget off (motor_budget 0), and asks which reproduces the fitness history.json recorded for that champion.
Re-scoring committed genomes only; no evolution is run.
"""
import argparse
import json
import os
import sys
from dataclasses import replace
from multiprocessing import Pool

import numpy as np

from rabbitstew.evolution import EvolutionConfig, generation_sim
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import run_group


def _solo(args):
    gd, sim, seed = args
    return run_group([Genotype.from_dict(gd)], sim, seed)[0]["score"]


def tasks_for(sd, line):
    cfg_d = json.load(open(os.path.join(sd, line, "config.json")))
    assert cfg_d["sim"]["world"]["motor_budget"] == 1.77, f"{sd}/{line}: config motor_budget {cfg_d['sim']['world'].get('motor_budget')}"
    cfg = EvolutionConfig.from_dict(cfg_d)
    hist = [e for e in json.load(open(os.path.join(sd, line, "history.json")))["history"] if e["population"] == "holistic"]
    out = []
    for e in sorted(hist, key=lambda e: e["generation"]):
        g = e["generation"]
        gd = json.load(open(os.path.join(sd, line, "holistic", f"best_gen{g:04d}.json")))
        sim_b = generation_sim(cfg, e["terrain_seed"], g)
        assert sim_b.world.motor_budget == 1.77
        sim_o = replace(sim_b, world=replace(sim_b.world, motor_budget=0.0))
        out.append((sd, line, g, e["best_fitness"], gd, sim_b, sim_o, e["start_seeds"]))
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--lines", default="U,D,C")
    ap.add_argument("seed_dirs", nargs="+")
    a = ap.parse_args(argv)
    items = [t for sd in a.seed_dirs for L in a.lines.split(",") for t in tasks_for(sd, L)]
    jobs = []
    for (_, _, _, _, gd, sb, so, ss) in items:
        for sim in (sb, so):
            jobs += [(gd, sim, s) for s in ss]
    with Pool(a.workers) as pool:
        res = pool.map(_solo, jobs, chunksize=4)
    k = 0
    n_b = n_o = n_both = n = 0
    worst_b = 0.0
    print("# M3 at every generation: per-generation holistic champion re-scored on its own worlds, budget on (1.77) and off")
    print(f"# {'dir':22s} line  gens  match_budgeted  match_unbudgeted  max|recorded - budgeted|  gens where budget changes the score")
    per = {}
    for (sd, L, g, rec, gd, sb, so, ss) in items:
        nb = len(ss)
        fb = float(np.mean(res[k:k + nb])); k += nb
        fo = float(np.mean(res[k:k + nb])); k += nb
        mb, mo = abs(fb - rec) < 1e-6, abs(fo - rec) < 1e-6
        p = per.setdefault((sd, L), [0, 0, 0, 0.0, 0])
        p[0] += 1; p[1] += mb; p[2] += mo; p[3] = max(p[3], abs(fb - rec)); p[4] += abs(fb - fo) > 1e-6
        n += 1; n_b += mb; n_o += mo; n_both += mb and mo; worst_b = max(worst_b, abs(fb - rec))
    for (sd, L), (c, mb, mo, w, ch) in per.items():
        print(f"  {sd:22s} {L:4s} {c:5d} {mb:15d} {mo:17d} {w:24.2e} {ch:6d}")
    print(f"\nTOTAL {n} generation champions: reproduced under the budget {n_b}; under no budget {n_o}; "
          f"by both (budget inert on that champion) {n_both}; max |recorded - budgeted| {worst_b:.2e}")
    print("M3 every-generation: " + ("PASS (every recorded champion fitness is the budgeted score)" if n_b == n else "FAIL"))
    return 0 if n_b == n else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
