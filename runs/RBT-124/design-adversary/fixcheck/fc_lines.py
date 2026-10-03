"""RBT-124 FIX-CHECK (design adversary): the U line's food and the D line's work on the amended tree, on my own draw.

    fc_lines.py > fc_lines.txt

Run on #420 @ a5c9014.  Every holistic U and D final of restored RBT-113 O1 (seeds 1-3, 40 each: 120 per line; the
designer's sample is 5 per directory over O1 and Z1), on all four registered draws, one plain season each (sim.run).
Variants:
  off        no flags
  ranges     ball_cone = hinge_range = pi/2 (M1 leaf hinge wheels, M2 ball-mounted wheels)
  pack       ranges + settle_until_rest 0.01 (cap 10 s)
  noleaf     ranges, but M2's ball wheel WITHOUT the leaf rule (a round part on a ball joint spins even when it carries
             children): what the leaf rule costs the U line
  budget     ranges + RBT-120's motor_budget 1.77
Reported per line: food a season (exploded seasons out), work (J), exploded seasons.  Nothing is written into any run.
"""
import math
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(HERE))))
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-113"))
import decompose  # noqa: E402
import world  # noqa: E402

from rabbitstew.evolution import HOLISTIC, generation_sim  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import Simulation, spawn_layout  # noqa: E402

PI2 = math.pi / 2
VARIANTS = {
    "off": ({}, {}),
    "ranges": ({"ball_cone": PI2, "hinge_range": PI2}, {}),
    "pack": ({"ball_cone": PI2, "hinge_range": PI2}, {"settle_until_rest": 0.01, "settle_max": 10.0}),
    "noleaf": ({"ball_cone": PI2, "hinge_range": PI2}, {}),
    "budget": ({"ball_cone": PI2, "hinge_range": PI2, "motor_budget": 1.77}, {}),
}


def season(args):
    gd, sc, start, v = args
    if v == "noleaf":
        import rabbitstew.world as W
        if not getattr(W, "_noleaf", False):
            orig = W.is_ball_wheel
            W.is_ball_wheel = lambda part, leaf, config: orig(part, True, config)
            W._noleaf = True
    else:
        import rabbitstew.world as W
        assert not getattr(W, "_noleaf", False)
    w, s = VARIANTS[v]
    cfg = replace(sc, random_start=True, world=replace(sc.world, **w), **s)
    sim = Simulation([Genotype.from_dict(gd)], cfg, spawns=spawn_layout(1, cfg, start))
    sim.set_food_seed(start)
    sim.run()
    return bool(sim.exploded[0]), float(sim.work[0]), float(sim.food_eaten[0])


def main():
    arm = os.path.join(ROOT, "runs", "RBT-113", "O1")
    tasks, keys = {}, {}
    for v in VARIANTS:
        tasks[v], keys[v] = [], []
    for seed in (1, 2, 3):
        cfg = world.evolution_config("U", "", seed=seed)
        for L in "UD":
            p = os.path.join(arm, str(seed), L, HOLISTIC, "final")
            for f in sorted(os.listdir(p)):
                gd = Genotype.load(os.path.join(p, f)).to_dict()
                for terrain, start in decompose.DRAWS:
                    sc = generation_sim(cfg, terrain)
                    for v in VARIANTS:
                        tasks[v].append((gd, sc, start, v))
                        keys[v].append((L, terrain))
    print("# fc_lines.py (#420 @ a5c9014): RBT-113 O1 holistic U and D finals (120 each), four draws; exploded seasons out of food and work")
    print(f"{'variant':8s} {'line':4s} {'draw':>6s} {'n':>4s} {'food/season':>11s} {'work J':>9s} {'exploded':>8s}")
    for v in VARIANTS:  # one pool per variant: the noleaf patch lives only in its own workers
        with ProcessPoolExecutor(4) as pool:
            res = list(pool.map(season, tasks[v], chunksize=4))
        for L in "UD":
            for draw in ("all", 1131):
                rows = [r for r, k in zip(res, keys[v]) if k[0] == L and (draw == "all" or k[1] == draw)]
                ok = [r for r in rows if not r[0]]
                print(f"{v:8s} {L:4s} {str(draw):>6s} {len(rows):4d} {np.mean([r[2] for r in ok]):11.3f} {np.mean([r[1] for r in ok]):9.0f} {len(rows) - len(ok):8d}", flush=True)


if __name__ == "__main__":
    main()
