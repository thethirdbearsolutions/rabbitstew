"""RBT-121 audit A, probe 4: limbs that pass through their parent (MuJoCo's parent-child contact filter).

    probe_ghost.py [--per-group K] [--workers W] SEED_DIR [...] > probe_ghost.txt

MuJoCo never collides a body with its parent (and world.py does not re-enable it), so a child on an unlimited ball
joint -- ball joints get no range at all (world.py:217) -- can swing straight through its parent's volume, and a
slider child can slide into it.  A real limb cannot.  This replays K members of every group solo on decompose.py's
first draw, controller on, and every control tick measures the signed distance (mj_geomDistance) of every
parent-child geom pair.  Reported per group: the share of parent-child pairs already interpenetrating when the season starts, the share of ticks with some pair interpenetrating by more than 2 cm,
the deepest interpenetration (m) relative to the smaller part's size, and the share of the season's actuator work
done on joints whose child is interpenetrating its parent at that tick.  Nothing is written into any run.
"""
import argparse
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import mujoco
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "RBT-113"))
import decompose  # noqa: E402
import world  # noqa: E402

import rabbitstew.simulation as S  # noqa: E402
from rabbitstew.evolution import CONVENTIONAL, HOLISTIC, generation_sim, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402

TERRAIN, START = decompose.DRAWS[0]


def job(args):
    gd, sc = args
    g = Genotype.from_dict(gd)
    cfg = replace(sc, random_start=True)
    sim = S.Simulation([g], cfg, spawns=S.spawn_layout(1, cfg, START))
    sim.set_food_seed(START)
    m, d, idx, ph = sim.model, sim.data, sim.robots[0], sim.phenotypes[0]
    pairs = [(idx.geoms[p.index], idx.geoms[p.parent], min(p.size, ph.parts[p.parent].size), p.index) for p in ph.parts if p.parent is not None]
    act_of = {}
    for (pi, dof), aid in idx.actuators.items():
        act_of.setdefault(pi, []).append(aid)
    built = np.mean([mujoco.mj_geomDistance(m, d, g1, g2, 0.5, None) < -0.02 for g1, g2, _, _ in pairs]) if pairs else 0.0
    n = int(round(cfg.duration / cfg.control_dt))
    hit = deep = wghost = wall = 0.0
    for _ in range(n):
        w0 = sim.work[0]
        sim.step()
        dw = sim.work[0] - w0
        wall += dw
        any_hit = False
        for g1, g2, size, pi in pairs:
            dist = mujoco.mj_geomDistance(m, d, g1, g2, 0.5, None)
            if dist < -0.02:
                any_hit = True
                deep = max(deep, -dist / size)
                if pi in act_of and m.nu:
                    p = np.abs(d.actuator_force * d.actuator_velocity)
                    tot = p.sum()
                    if tot > 0:
                        wghost += dw * p[act_of[pi]].sum() / tot
        hit += any_hit
    return [built, hit / n, deep, wghost / wall if wall > 0 else 0.0]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-group", type=int, default=3)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("dirs", nargs="+")
    a = ap.parse_args()
    tasks, keys = [], []
    for dd in a.dirs:
        op, seed = decompose.parse_seed_dir(dd)
        cfg = world.evolution_config("U", op, seed=seed)
        sc = generation_sim(cfg, TERRAIN)
        streams = spawn_streams(seed, cfg.holistic_stream_salt)
        rng = np.random.default_rng(121)
        for kind in (HOLISTIC, CONVENTIONAL):
            groups = {"founders": initial_population(kind, cfg, streams[kind]).members}
            for L in "UDC":
                p = os.path.join(dd, L, kind, "final")
                groups[L] = [Genotype.load(os.path.join(p, f)) for f in sorted(os.listdir(p))]
            for gname, ms in groups.items():
                for i in rng.choice(len(ms), a.per_group, replace=False):
                    tasks.append((ms[i].to_dict(), sc))
                    keys.append((kind, gname))
    with ProcessPoolExecutor(a.workers) as pool:
        res = np.array(list(pool.map(job, tasks, chunksize=1)))
    print(f"# probe_ghost.py, {a.per_group} members per group per directory over {len(a.dirs)} directories; draw ({TERRAIN}, {START})")
    print("# share of parent-child pairs already > 2 cm inside at the start | ticks with a child > 2 cm inside its parent | deepest (x smaller part size) | share of work done on such joints at such ticks; mean / max")
    for key in dict.fromkeys(keys):
        R = res[[k == key for k in keys]]
        print(f"{key[0]:12s} {key[1]:8s} {len(R):4d} " + " ".join(f"{R[:, c].mean():.3f}/{R[:, c].max():.3f}".rjust(13) for c in range(4)))


if __name__ == "__main__":
    main()
