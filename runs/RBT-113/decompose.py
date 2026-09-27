"""RBT-113 endpoint food/work decomposition (PREREGISTRATION.md §5.5; the design adversary's D1(a)), fixed before any
arm runs.

    decompose.py [--workers W] SEED_DIR [SEED_DIR ...]

A SEED_DIR is `runs/RBT-113/<ARM>/<OP><SEED>` (e.g. `O1/1`, `Z1/Z1`) holding the line runs U/, D/, C/, with each line's
`<fauna>/final/` (its generation-23 population) RESTORED from the arm's checkpoint branch (`scripts/durable.sh
restore runs/RBT-113/<ARM> rbt-113-<ARM>`): `final/` is bulk and is not in the arm PRs.

For each seed directory and fauna it re-scores, solo, on the FIXED draws below (identical for every seed directory,
line and fauna, so every contrast is paired on its worlds):
  * the founders (generation 0), regenerated exactly as `evolve` drew them (world.evolution_config for the seed
    directory's operator and seed, so the Z holistic founders come from salt 1), and checked against the U line's
    generation-0 lineage rows (names, and the body-plan hash on the holistic side);
  * each line's `final/` (generation G-1), checked to be G-1's names and N genomes.
Per member it records mean items eaten (`food`), mean work cost in yield units (`work` = 0.03 x J / 1000, the term
`food_score` subtracts) and mean net yield (`net` = food - work; an exploded season books 0 of each).  It writes
`<SEED_DIR>/decompose.json` (group means, SDs and counts; the readout consumes it) and prints a table.  Nothing here
changes a run.
"""
import argparse
import glob
import json
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import world  # noqa: E402

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, generation_sim, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genetics import body_plan_hash  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import run_group  # noqa: E402

#: the fixed draws, (terrain seed, start seed): pre-registered, never re-drawn
DRAWS = [(1131, 2131), (1132, 2132), (1133, 2133), (1134, 2134)]
WORK_COST = 0.03  # world.WORLD's --work-cost; asserted against the config below
GROUPS = ("founders", "U", "D", "C")


def _solo(args):
    gd, sim, seed = args
    r = run_group([Genotype.from_dict(gd)], sim, seed)[0]
    return r["food"], r["work"], r["score"]


def parse_seed_dir(d):
    name = os.path.basename(d.rstrip("/"))
    op = "Z" if name.startswith("Z") else ""
    return op, int(name[len(op):])


def score(pool, members, cfg):
    sims = [generation_sim(cfg, t) for t, _ in DRAWS]
    tasks = [(g.to_dict(), sims[j], s) for g in members for j, (_, s) in enumerate(DRAWS)]
    a = np.array(list(pool.map(_solo, tasks, chunksize=2)), float).reshape(len(members), len(DRAWS), 3).mean(axis=1)
    food, work, net = a[:, 0], a[:, 1] * WORK_COST / 1000.0, a[:, 2]
    assert np.allclose(food - work, net, atol=1e-9), "net is not food - 0.03 x kJ"
    return food, work, net


def decompose(d, pool):
    op, seed = parse_seed_dir(d)
    ucfg = json.load(open(os.path.join(d, "U", "config.json")))
    G, N = ucfg["generations"], ucfg["population_size"]
    cfg = world.evolution_config("U", op, population=N, generations=G, seed=seed)
    assert cfg.sim.food.work_cost == WORK_COST
    streams = spawn_streams(seed, cfg.holistic_stream_salt)
    g0 = [json.loads(l) for l in open(os.path.join(d, "U", "lineage.jsonl")) if l.strip()]
    out = {"seed_dir": d, "operator": op or "default", "seed": seed, "generation": G - 1, "draws": DRAWS, "faunae": {}}
    for kind in (HOLISTIC, CONVENTIONAL):
        founders = initial_population(kind, cfg, streams[kind]).members
        rows0 = [r for r in g0 if r["population"] == kind and r["generation"] == 0]
        assert [f.name for f in founders] == [r["name"] for r in rows0], f"{d} {kind}: regenerated founders' names differ"
        if kind == HOLISTIC:
            assert [body_plan_hash(f) for f in founders] == [r["body"] for r in rows0], f"{d}: regenerated founders' bodies differ"
        groups = {"founders": founders}
        for L in "UDC":
            files = sorted(glob.glob(os.path.join(d, L, kind, "final", "*.json")))
            members = [Genotype.load(p) for p in files]
            assert len(members) == N, f"{d} {L} {kind}: {len(members)} final genomes, expected {N} (restore the checkpoint)"
            assert all(m.name.startswith(("h" if kind == HOLISTIC else "c") + f"{G - 1}-") for m in members), f"{d} {L} {kind}: final/ is not generation {G - 1}"
            groups[L] = members
        res = {}
        for k, ms in groups.items():
            f, w, y = score(pool, ms, cfg)
            res[k] = {"n": len(ms), "food": float(f.mean()), "work": float(w.mean()), "net": float(y.mean()),
                      "food_sd": float(f.std(ddof=1)), "work_sd": float(w.std(ddof=1)),
                      "p_food": float(np.mean(f > 0)), "p_still": float(np.mean(w < 1e-9))}
        out["faunae"][kind] = res
    with open(os.path.join(d, "decompose.json"), "w") as fh:
        json.dump(out, fh, indent=1)
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("seed_dirs", nargs="+")
    a = ap.parse_args(argv)
    pool = ProcessPoolExecutor(a.workers)
    print(f"# RBT-113 endpoint decomposition (runs/RBT-113/decompose.py): {len(DRAWS)} fixed draws; food = items eaten, "
          f"work = {WORK_COST} x kJ (yield units), net = food - work")
    for d in a.seed_dirs:
        out = decompose(d, pool)
        for kind, res in out["faunae"].items():
            print(f"\n{d} {kind} (generation {out['generation']})")
            print(f"  {'group':9s} {'n':>3s} {'food':>8s} {'work':>8s} {'net':>8s} {'P(food>0)':>9s} {'P(work=0)':>9s}")
            for k in GROUPS:
                r = res[k]
                print(f"  {k:9s} {r['n']:3d} {r['food']:8.4f} {r['work']:8.4f} {r['net']:+8.4f} {r['p_food']:9.2f} {r['p_still']:9.2f}")
    pool.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
