"""RBT-124 design adversary: is the explosion under the cone one chaotic body, or a new failure mode?

    explode.py [--draws N] > explode.txt

Every holistic body of restored RBT-113 O1 (seeds 1-3: regenerated founders and all 40 U/D/C finals, 480 bodies),
one season each on RBT-113's registered draws (decompose.py's (terrain, start) pairs), ranges off and on
(ball_cone = hinge_range = pi/2).  Counts exploded seasons, and lists every body that explodes under one setting
and not the other.  Nothing is written into any run.
"""
import argparse
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-113"))
import decompose  # noqa: E402
import world  # noqa: E402

from rabbitstew.evolution import HOLISTIC, generation_sim, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import Simulation, spawn_layout  # noqa: E402


def season(args):
    gd, sc, start, on = args
    cfg = replace(sc, random_start=True)
    if on:
        cfg = replace(cfg, world=replace(cfg.world, ball_cone=math.pi / 2, hinge_range=math.pi / 2))
    sim = Simulation([Genotype.from_dict(gd)], cfg, spawns=spawn_layout(1, cfg, start))
    sim.set_food_seed(start)
    sim.run()
    return bool(sim.exploded[0]), float(sim.work[0]), float(sim.food_eaten[0])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draws", type=int, default=1)
    ap.add_argument("--workers", type=int, default=4)
    a = ap.parse_args()
    draws = decompose.DRAWS[: a.draws] if hasattr(decompose, "DRAWS") else [(1131, 2131)]
    arm = os.path.join(ROOT, "runs", "RBT-113", "O1")
    tasks, keys = [], []
    for seed in (1, 2, 3):
        cfg = world.evolution_config("U", "", seed=seed)
        groups = {"founders": initial_population(HOLISTIC, cfg, spawn_streams(seed, cfg.holistic_stream_salt)[HOLISTIC]).members}
        for L in "UDC":
            p = os.path.join(arm, str(seed), L, HOLISTIC, "final")
            groups[L] = [Genotype.load(os.path.join(p, f)) for f in sorted(os.listdir(p))]
        for gname, ms in groups.items():
            for i, g in enumerate(ms):
                for terrain, start in draws:
                    sc = generation_sim(cfg, terrain)
                    for on in (False, True):
                        tasks.append((g.to_dict(), sc, start, on))
                        keys.append((seed, gname, i, terrain, on))
    with ProcessPoolExecutor(a.workers) as pool:
        res = list(pool.map(season, tasks, chunksize=4))
    r = dict(zip(keys, res))
    print(f"# explode.py: 480 holistic bodies of RBT-113 O1, draws {draws}, ranges off vs pi/2")
    for on in (False, True):
        n = sum(1 for k, v in r.items() if k[4] == on)
        x = sum(v[0] for k, v in r.items() if k[4] == on)
        print(f"ranges {'on ' if on else 'off'}: {x} exploded of {n} seasons")
    print("bodies whose explosion flag differs (seed group member terrain: off -> on, work J off -> on):")
    for k, v in r.items():
        if not k[4]:
            w = r[k[:4] + (True,)]
            if v[0] != w[0]:
                print(f"  O1/{k[0]} {k[1]:8s} #{k[2]:02d} t{k[3]}: {v[0]} -> {w[0]}, {v[1]:.0f} -> {w[1]:.0f}")


if __name__ == "__main__":
    main()
