"""RBT-124: the RBT-121 adversary's motors-off probe (phys_passive.py), re-run with settle_until_rest.

    passive.py [--per-group K] [--workers W] [--draws N] SEED_DIR [...] > passive.txt

The SAME holistic members as phys_passive.py / audit A's probe_passive.py (rng 121, K per group per directory, drawn
first from the holistic fauna), and the designed members beside them, on decompose.py's draws.  Every Effector output
is held at 0 for a whole 15 s season (the "moves by itself" null) under four settles:
  s1     the committed settle (1 s, then velocities zeroed and the COM re-centred)
  s5     a fixed 5 s settle (the adversary's zero5)
  rest   settle_until_rest 0.01 m/s, settle_max 5 s (RBT-124's flag)
  rest10 the same with settle_max 10 s
  tight  settle_until_rest 0.003 m/s, settle_max 10 s
Per member: COM displacement over the season (m), food, the seconds the settle used, and the static-reach food
expectation of the settled pose (rabbitstew.levers.static_reach_food: 12 x the area within eat_radius of a geom centre
but outside the clearance disc, over the area items can land in), and the deepest penetration between two of the
body's own geoms after the settle ("pen").  Nothing is written into any run.
"""
import argparse
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
from rabbitstew.levers import _sim, static_reach_food  # noqa: E402

SETTLES = {"s1": {}, "s5": dict(settle_time=5.0), "rest": dict(settle_until_rest=0.01, settle_max=5.0),
           "rest10": dict(settle_until_rest=0.01, settle_max=10.0), "tight": dict(settle_until_rest=0.003, settle_max=10.0)}


def job(args):
    gd, sc, start = args
    g = Genotype.from_dict(gd)
    out = {}
    for name, kw in SETTLES.items():
        sim = _sim(g, replace(sc, **kw), start)
        reach = static_reach_food(sim)
        own = set(sim.robots[0].geoms)
        pen = max([-float(c.dist) for c in sim.data.contact[: sim.data.ncon] if c.geom1 in own and c.geom2 in own] or [0.0])
        sim.brains[0].effector_output = lambda *a: 0.0
        c0 = sim.center_of_mass(0)[:2].copy()
        sim.run()
        out[name] = (float(np.linalg.norm(sim.center_of_mass(0)[:2] - c0)), float(sim.food_eaten[0]), float(sim.settle_seconds), reach, pen)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-group", type=int, default=5)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--draws", type=int, default=1)
    ap.add_argument("dirs", nargs="+")
    a = ap.parse_args()
    tasks, keys = [], []
    for dd in a.dirs:
        op, seed = decompose.parse_seed_dir(dd)
        cfg = world.evolution_config("U", op, seed=seed)
        streams = spawn_streams(seed, cfg.holistic_stream_salt)
        rng = np.random.default_rng(121)  # phys_passive.py's picks: holistic first
        for kind in (HOLISTIC, CONVENTIONAL):
            groups = {"founders": initial_population(kind, cfg, streams[kind]).members}
            for L in "UDC":
                p = os.path.join(dd, L, kind, "final")
                groups[L] = [Genotype.load(os.path.join(p, f)) for f in sorted(os.listdir(p))]
            for gname, ms in groups.items():
                for i in rng.choice(len(ms), a.per_group, replace=False):
                    for t, s in decompose.DRAWS[: a.draws]:
                        tasks.append((ms[i].to_dict(), generation_sim(cfg, t), s))
                        keys.append((kind, gname, "/".join(os.path.normpath(dd).split(os.sep)[-2:]), int(i), t))
    with ProcessPoolExecutor(a.workers) as pool:
        res = list(pool.map(job, tasks, chunksize=1))
    names = list(SETTLES)
    print(f"# passive.py: {a.per_group} per group per directory over {len(a.dirs)} dirs, draws {decompose.DRAWS[: a.draws]}; motors off for the whole season")
    print("# per settle: disp mean/max (m) | #>0.05 m | #>0.25 m | food total | static-reach food expectation (sum) | settle s mean/max")
    for kind in (HOLISTIC, CONVENTIONAL):
        for gname in ("founders", "U", "D", "C"):
            R = [r for r, k in zip(res, keys) if k[0] == kind and k[1] == gname]
            line = f"{kind[:4]} {gname:8s} n={len(R):3d}"
            for nm in names:
                v = np.array([r[nm] for r in R])
                line += f" | {nm}: {v[:, 0].mean():.3f}/{v[:, 0].max():.2f} #{int((v[:, 0] > 0.05).sum())} #{int((v[:, 0] > 0.25).sum())} F{int(v[:, 1].sum())} E{v[:, 3].sum():.2f} S{v[:, 2].mean():.1f}/{v[:, 2].max():.1f}"
            print(line)
    H = [r for r, k in zip(res, keys) if k[0] == HOLISTIC]
    for nm in names:
        v = np.array([r[nm] for r in H])
        jam = v[:, 4] > 0.01
        print(f"# holistic {nm:6s} without a > 1 cm self-penetration (n={int((~jam).sum())}): >0.05 m {int((v[~jam, 0] > 0.05).sum())}, max disp {v[~jam, 0].max():.3f}; "
              f"with one (n={int(jam.sum())}): >0.05 m {int((v[jam, 0] > 0.05).sum())}")
    for nm in names:
        v = np.array([r[nm] for r in H])
        print(f"# holistic total {nm:6s}: >0.05 m {int((v[:, 0] > 0.05).sum())}, >0.25 m {int((v[:, 0] > 0.25).sum())} of {len(v)}; food {int(v[:, 1].sum())}; static-reach expectation {v[:, 3].sum():.2f}; max disp {v[:, 0].max():.3f}")
    print("# holistic members > 0.05 m under any settle: key | " + " | ".join(f"{nm} disp food S" for nm in names))
    for r, k in zip(res, keys):
        if k[0] == HOLISTIC and any(r[nm][0] > 0.05 for nm in names):
            print(f"#   {k[1]:8s} {k[2]} #{k[3]:2d} t{k[4]} | " + " | ".join(f"{r[nm][0]:.3f} {r[nm][1]:.0f} {r[nm][2]:.2f}" for nm in names)
                  + f" | pen {max(r[nm][4] for nm in names) * 100:.1f} cm")
    print("# members eating with motors off under any settle: key | " + " | ".join(f"{nm} disp food E" for nm in names))
    for r, k in zip(res, keys):
        if any(r[nm][1] > 0 for nm in names):
            print(f"#   {k[0][:4]} {k[1]:8s} {k[2]} #{k[3]:2d} t{k[4]} | " + " | ".join(f"{r[nm][0]:.3f} {r[nm][1]:.0f} {r[nm][3]:.3f}" for nm in names))


if __name__ == "__main__":
    main()
