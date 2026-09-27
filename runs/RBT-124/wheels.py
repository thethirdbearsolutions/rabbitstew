"""RBT-124: what the holistic U line's ball-joint work was doing before the cone took it away.

    wheels.py [--per-group K] [--workers W] SEED_DIR [...] > wheels.txt

Under the committed physics (flags off), on RBT-113's first draw, for the holistic U and D finals (K per directory, rng
124, as sample.py): the share of actuator work by joint type, and for ball joints by (child round: sphere/cylinder, or
not) x (child touching something at the tick's end, or not); and the intact season's food and COM displacement, off
and under ball_cone = hinge_range = pi/2.  A round child spinning on a ball joint against the ground is a wheel the cone
removes; a free spinning limb is a ghost rotor.  Nothing is written into any run.
"""
import argparse
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

from rabbitstew.evolution import HOLISTIC, generation_sim  # noqa: E402
from rabbitstew.genotype import Genotype, JointType, Shape  # noqa: E402
from rabbitstew.levers import _sim  # noqa: E402

T, START = decompose.DRAWS[0]


def job(args):
    gd, sc = args
    g = Genotype.from_dict(gd)
    out = {}
    for on in (False, True):
        cfg = replace(sc, world=replace(sc.world, ball_cone=math.pi / 2, hinge_range=math.pi / 2)) if on else sc
        sim = _sim(g, cfg, START)
        m, d, idx, ph = sim.model, sim.data, sim.robots[0], sim.phenotypes[0]
        c0 = sim.center_of_mass(0)[:2].copy()
        sim.actuator_work = np.zeros(m.nu)
        acc = {}
        for _ in range(int(round(cfg.duration / cfg.control_dt))):
            before = sim.actuator_work.copy()
            sim.step()
            dw = sim.actuator_work - before
            touched = {int(c.geom1) for c in d.contact[: d.ncon]} | {int(c.geom2) for c in d.contact[: d.ncon]}
            for (pi, _dof), aid in idx.actuators.items():
                p = ph.parts[pi]
                k = p.joint_type.name
                if p.joint_type == JointType.BALL:
                    k += (" round" if p.shape in (Shape.SPHERE, Shape.CYLINDER) else " limb") + (" contact" if idx.geoms[pi] in touched else " free")
                acc[k] = acc.get(k, 0.0) + float(dw[aid])
        out[on] = dict(acc=acc, W=float(sim.actuator_work.sum()), food=float(sim.food_eaten[0]),
                       disp=float(np.linalg.norm(sim.center_of_mass(0)[:2] - c0)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-group", type=int, default=5)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("dirs", nargs="+")
    a = ap.parse_args()
    tasks, keys = [], []
    for dd in a.dirs:
        op, seed = decompose.parse_seed_dir(dd)
        cfg = world.evolution_config("U", op, seed=seed)
        sc = replace(generation_sim(cfg, T), random_start=True)
        rng = np.random.default_rng(124)
        for L in "UD":
            p = os.path.join(dd, L, HOLISTIC, "final")
            fs = sorted(os.listdir(p))
            for i in sorted(rng.choice(len(fs), a.per_group, replace=False)):
                tasks.append((Genotype.load(os.path.join(p, fs[i])).to_dict(), sc))
                keys.append(L)
    with ProcessPoolExecutor(a.workers) as pool:
        res = list(pool.map(job, tasks, chunksize=1))
    print(f"# wheels.py: holistic U and D finals, {a.per_group} per directory over {len(a.dirs)} dirs, draw ({T}, {START})")
    for L in "UD":
        R = [r for r, k in zip(res, keys) if k == L]
        for on in (False, True):
            W = sum(r[on]["W"] for r in R)
            ks = sorted({k for r in R for k in r[on]["acc"]})
            shares = ", ".join(f"{k} {sum(r[on]['acc'].get(k, 0) for r in R) / W:.2f}" for k in ks) if W > 0 else "-"
            print(f"{L} {'ranges' if on else 'off   '} n={len(R)} work {W / len(R):8.0f} J  food {np.mean([r[on]['food'] for r in R]):.2f}  "
                  f"disp {np.mean([r[on]['disp'] for r in R]):.2f} m  | work share: {shares}")


if __name__ == "__main__":
    main()
