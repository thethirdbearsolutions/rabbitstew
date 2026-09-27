"""RBT-124: the physics pack's levers on a restored RBT-113 sample, flags off and on.

    sample.py [--per-group K] [--workers W] [--draws N] [--variants off,ranges,...] SEED_DIR [...] > OUT

The sample is the RBT-121 probes': restored RBT-113 seed directories (`scripts/durable.sh restore`), their
regenerated founders plus the U, D and C lines' final generation (23), for BOTH faunas; K members per group per
directory, drawn with rng 124.  Each member is measured by `rabbitstew.levers.body_levers` on RBT-113's generation
sim for each of the first N of decompose.py's draws (terrain seed, start seed), under each variant:
  off     the committed physics (every RBT-124 flag off)
  ranges  ball_cone = hinge_range = pi/2
  settle  settle_until_rest = 0.01 m/s, settle_max = 5 s
  pack    both
  cone_*  the ranges at pi/4, 3 pi/4 and 0.95 pi (the cone's sensitivity)
Rows print per variant, fauna and group; `--json` also dumps every member's row.  Nothing is written into any run.
"""
import argparse
import json
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "RBT-113"))
import decompose  # noqa: E402
import world  # noqa: E402

from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, generation_sim, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.levers import HEADER, body_levers, format_row, line_summary  # noqa: E402

VARIANTS = {
    "off": {},
    "ranges": dict(ball_cone=math.pi / 2, hinge_range=math.pi / 2),
    "settle": dict(settle_until_rest=0.01, settle_max=5.0),
    "pack": dict(ball_cone=math.pi / 2, hinge_range=math.pi / 2, settle_until_rest=0.01, settle_max=5.0),
    # the cone's sensitivity (with hinge_range matched)
    "cone_pi4": dict(ball_cone=math.pi / 4, hinge_range=math.pi / 4),
    "cone_3pi4": dict(ball_cone=3 * math.pi / 4, hinge_range=3 * math.pi / 4),
    "cone_0.95pi": dict(ball_cone=0.95 * math.pi, hinge_range=0.95 * math.pi),
}


def apply(sc, v):
    w = {k: v[k] for k in ("ball_cone", "hinge_range") if k in v}
    s = {k: v[k] for k in ("settle_until_rest", "settle_max") if k in v}
    return replace(sc, world=replace(sc.world, **w), **s)


def job(args):
    gd, sc, start = args
    return body_levers(Genotype.from_dict(gd), sc, start)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-group", type=int, default=5)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--draws", type=int, default=1)
    ap.add_argument("--variants", default="off,ranges,settle,pack")
    ap.add_argument("--faunas", default=f"{HOLISTIC},{CONVENTIONAL}")
    ap.add_argument("--json", default=None)
    ap.add_argument("dirs", nargs="+")
    a = ap.parse_args()
    variants = a.variants.split(",")
    tasks, keys = [], []
    for dd in a.dirs:
        op, seed = decompose.parse_seed_dir(dd)
        cfg = world.evolution_config("U", op, seed=seed)
        streams = spawn_streams(seed, cfg.holistic_stream_salt)
        rng = np.random.default_rng(124)
        for kind in a.faunas.split(","):
            groups = {"founders": initial_population(kind, cfg, streams[kind]).members}
            for L in "UDC":
                p = os.path.join(dd, L, kind, "final")
                groups[L] = [Genotype.load(os.path.join(p, f)) for f in sorted(os.listdir(p))]
            for gname, ms in groups.items():
                for i in sorted(rng.choice(len(ms), min(a.per_group, len(ms)), replace=False)):
                    for t, s in decompose.DRAWS[: a.draws]:
                        for v in variants:
                            tasks.append((ms[i].to_dict(), apply(generation_sim(cfg, t), VARIANTS[v]), s))
                            keys.append((v, kind, gname, "/".join(os.path.normpath(dd).split(os.sep)[-2:]), int(i), t))
    with ProcessPoolExecutor(a.workers) as pool:
        res = list(pool.map(job, tasks, chunksize=1))
    names = ["/".join(os.path.normpath(d).split(os.sep)[-2:]) for d in a.dirs]  # ARM/SEED, wherever it was restored
    print(f"# sample.py: {a.per_group} per group per directory, {len(a.dirs)} dirs ({', '.join(names)}), draws {decompose.DRAWS[: a.draws]}")
    for v in variants:
        print(f"\n## variant {v}: {VARIANTS[v]}")
        print(HEADER)
        for kind in a.faunas.split(","):
            for gname in ("founders", "U", "D", "C"):
                rows = [r for r, k in zip(res, keys) if k[0] == v and k[1] == kind and k[2] == gname]
                if rows:
                    s = line_summary(rows)
                    print(format_row(f"{kind[:4]} {gname}", s) + f"  work_free {s['work_free']:.0f} J  reach_food {s['reach_food']:.3f}  exploded {int(sum(r['exploded'] for r in rows))}")
    if a.json:
        with open(a.json, "w") as f:
            json.dump([dict(key=list(k), **r) for k, r in zip(keys, res)], f)


if __name__ == "__main__":
    main()
