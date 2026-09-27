"""RBT-113 design-adversary probe: split the response into its food and work terms.

Re-scores, solo on 4 fixed draws of the benchmark world, the founders (generation 0, drawn as `evolve` draws them)
and the last generation of each line of a tiny U/D/C run at one seed, and prints mean items eaten, mean work cost
(0.03 x kJ, in yield units) and mean net yield per line and fauna.  Throwaway: not evidence, only a check on what
the lineage.jsonl the arms write can and cannot say.

    decompose.py PROBE_DIR SEED
"""
import glob
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.environ.get("RBT113", "runs/RBT-113")))
from world import evolution_config  # noqa: E402

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import run_group  # noqa: E402

DRAWS = [11, 22, 33, 44]


def _solo(args):
    gd, sim, seed = args
    r = run_group([Genotype.from_dict(gd)], sim, seed)[0]
    return r["food"], r["work"], r["score"]


def score(pool, members, sim):
    tasks = [(g.to_dict(), sim, s) for g in members for s in DRAWS]
    a = np.array(list(pool.map(_solo, tasks, chunksize=2))).reshape(len(members), len(DRAWS), 3).mean(axis=1)
    food, work, y = a[:, 0], a[:, 1] * 0.03 / 1000, a[:, 2]
    return food, work, y


def main(d, seed):
    cfg = evolution_config(population=40, generations=1, seed=seed, workers=1)
    streams = spawn_streams(seed)
    pool = ProcessPoolExecutor(4)
    print(f"# decompose: seed {seed}, {len(DRAWS)} fixed draws; food = items eaten, work = 0.03 x kJ (yield units), yield = food - work")
    for kind in (HOLISTIC, CONVENTIONAL):
        founders = initial_population(kind, cfg, streams[kind]).members
        rows = {"founders (gen 0)": founders}
        for L in "UDC":
            rows[f"{L} last gen"] = [Genotype.load(p) for p in sorted(glob.glob(os.path.join(d, L, kind, "final", "*.json")))]
        print(f"\n## {kind}")
        print(f"  {'':18s} {'n':>3s} {'food':>8s} {'work':>8s} {'yield':>8s} {'P(food>0)':>9s} {'P(work=0)':>9s}")
        for k, ms in rows.items():
            f, w, y = score(pool, ms, cfg.sim)
            print(f"  {k:18s} {len(ms):3d} {f.mean():8.4f} {w.mean():8.4f} {y.mean():+8.4f} {np.mean(f > 0):9.2f} {np.mean(w < 1e-6):9.2f}")


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]))
