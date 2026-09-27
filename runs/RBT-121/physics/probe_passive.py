"""RBT-121 audit A, probe 2: does anything move, or eat, with every motor switched off?

    probe_passive.py [--per-group K] [--workers W] SEED_DIR [...] > probe_passive.txt

Replays K members of every group (founders, U, D, C; both faunas) solo on decompose.py's first fixed draw (terrain
1131, start 2131), exactly as a season is run (settle 1 s, zero velocities, re-centre, 15 s), but with every actuator
command held at 0 for the whole season ("off").  A body with no motor output can only move by energy the protocol or
the contact model hands it: a settle that ends before the body has come to rest (the spawn drop's remainder), or
overlapping geoms of the same robot pushing each other apart.  Reported per group:

  disp    COM horizontal displacement over the season (m) with motors off
  path    COM path length (m) with motors off
  food    items eaten with motors off (a regrown item landing on a motionless body is the only other way)
  selfpen deepest contact penetration between two geoms of the SAME robot at any substep (m)
  pen     deepest contact penetration of any kind (m)
  vmax    max body speed (m/s)
the same motors-off season on flat ground (terrain "flat": separates rolling off an obstacle from the protocol), and, with the evolved controller intact, the same season's food, work (J) and selfpen for comparison.
Nothing is written into any run.
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


def season(gd, sc, off, flat=False):
    g = Genotype.from_dict(gd)
    cfg = replace(sc, random_start=True)
    if flat:
        cfg = replace(cfg, world=replace(cfg.world, terrain="flat"))
    sim = S.Simulation([g], cfg, spawns=S.spawn_layout(1, cfg, START))
    sim.set_food_seed(START)
    if off:
        sim.brains[0].effector_output = lambda *a: 0.0
    m, d, idx = sim.model, sim.data, sim.robots[0]
    own = set(idx.geoms)
    com0 = sim.center_of_mass(0)[:2].copy()
    prev, path, selfpen, pen, vmax = com0.copy(), 0.0, 0.0, 0.0, 0.0
    n = int(round(cfg.duration / cfg.control_dt))
    early = None
    for t in range(n):
        if t == int(round(2.0 / cfg.control_dt)):
            early = float(np.linalg.norm(sim.center_of_mass(0)[:2] - com0))
        sim.step()
        for c in d.contact[: d.ncon]:
            pen = max(pen, -c.dist)
            if c.geom1 in own and c.geom2 in own:
                selfpen = max(selfpen, -c.dist)
        vmax = max(vmax, float(np.linalg.norm(d.cvel[idx.bodies, 3:], axis=1).max()))
        com = sim.center_of_mass(0)[:2]
        path += float(np.linalg.norm(com - prev))
        prev = com.copy()
    return [float(np.linalg.norm(prev - com0)), path, float(sim.food_eaten[0]), selfpen, pen, vmax, float(sim.work[0]), float(sim.exploded[0]), early]


def job(args):
    gd, sc = args
    return season(gd, sc, True) + season(gd, sc, False) + season(gd, sc, True, flat=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-group", type=int, default=5)
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
    print(f"# probe_passive.py, {a.per_group} members per group per directory over {len(a.dirs)} directories; draw ({TERRAIN}, {START})")
    print("# motors OFF: disp, disp by t = 2 s, path (m), food, selfpen, pen (m), vmax (m/s) | motors OFF on FLAT ground: disp, food | controller ON: food, work (J), selfpen, pen (m)")
    print("# mean / max over members")
    hdr = ["off.disp", "off.disp@2s", "off.path", "off.food", "off.selfpen", "off.pen", "off.vmax", "flatoff.disp", "flatoff.food", "on.food", "on.work", "on.selfpen", "on.pen"]
    cols = [0, 8, 1, 2, 3, 4, 5, 18, 20, 11, 15, 12, 13]
    print(f"{'fauna':12s} {'group':8s} {'n':>4s} " + " ".join(f"{h:>13s}" for h in hdr))
    for key in dict.fromkeys(keys):
        R = res[[k == key for k in keys]]
        print(f"{key[0]:12s} {key[1]:8s} {len(R):4d} " + " ".join(f"{R[:, c].mean():.3f}/{R[:, c].max():.3f}".rjust(13) for c in cols))
    far = res[:, 0] > 0.25
    print(f"# members that drift > 0.25 m with motors off: {int(far.sum())} of {len(res)}")
    for i in np.nonzero(far)[0]:
        print(f"#   {keys[i][0]} {keys[i][1]}: off disp {res[i, 0]:.2f} m, off food {res[i, 2]:.0f}, off selfpen {res[i, 3]:.3f} m, off vmax {res[i, 5]:.2f}, off disp by 2 s {res[i, 8]:.2f} m, on flat ground off disp {res[i, 18]:.2f} m")


if __name__ == "__main__":
    main()
