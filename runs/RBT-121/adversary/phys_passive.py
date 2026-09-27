"""RBT-121 adversary (physics): is audit A's "motors off" really unactuated, and is its drift the settle's remainder?

    phys_passive.py [--per-group K] [--workers W] SEED_DIR [...] > phys_passive.txt

Same holistic members as probe_passive.py (rng 121, K per group per directory, draw 0).  Four seasons each:
  zero    every effector output forced to 0 (audit A's "off"): ctrl = 0.  A POSITION servo then still pulls its joint
          to q = 0 (force = -kp q - kv qdot) and a VELOCITY servo still brakes (force = -kv qdot): actuated, and billed.
  limp    truly unactuated: after the normal 1 s settle (which, like the real protocol, runs with ctrl = 0 and servos
          holding), every actuator's gain and bias are set to 0, so no actuator force exists at all.
  zero5   as zero, but settle_time = 5 s instead of 1 s (tests "the settle ends before the body is at rest")
  on      the evolved controller, for comparison
Reported: COM displacement (m), work billed (J), food; members over 0.25 m; how many joints of each actuator kind.
Nothing is written into any run.
"""
import argparse
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "RBT-113"))
import decompose  # noqa: E402
import world  # noqa: E402

import rabbitstew.simulation as S  # noqa: E402
from rabbitstew.evolution import HOLISTIC, generation_sim, initial_population, spawn_streams  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402

TERRAIN, START = decompose.DRAWS[0]


def season(gd, sc, variant):
    g = Genotype.from_dict(gd)
    cfg = replace(sc, random_start=True)
    if variant == "zero5":
        cfg = replace(cfg, settle_time=5.0)
    sim = S.Simulation([g], cfg, spawns=S.spawn_layout(1, cfg, START))
    sim.set_food_seed(START)
    if variant in ("zero", "zero5", "limp"):
        sim.brains[0].effector_output = lambda *a: 0.0
    if variant == "limp":
        sim.model.actuator_gainprm[:] = 0.0
        sim.model.actuator_biasprm[:] = 0.0
    com0 = sim.center_of_mass(0)[:2].copy()
    n = int(round(cfg.duration / cfg.control_dt))
    for _ in range(n):
        sim.step()
    disp = float(np.linalg.norm(sim.center_of_mass(0)[:2] - com0))
    return [disp, float(sim.work[0]), float(sim.food_eaten[0]), float(sim.exploded[0])]


def job(args):
    gd, sc = args
    ph = S.Simulation([Genotype.from_dict(gd)], replace(sc, settle_time=0.0)).phenotypes[0]
    from rabbitstew.world import driven_dofs
    dr = {pi for pi, _ in driven_dofs(ph)}
    kinds = [ph.parts[pi].motor if ph.parts[pi].joint_type.name != "BALL" else "ball" for pi in dr]
    out = []
    for v in ("zero", "limp", "zero5", "on"):
        out += season(gd, sc, v)
    return out, kinds


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
        groups = {"founders": initial_population(HOLISTIC, cfg, streams[HOLISTIC]).members}
        for L in "UDC":
            p = os.path.join(dd, L, HOLISTIC, "final")
            groups[L] = [Genotype.load(os.path.join(p, f)) for f in sorted(os.listdir(p))]
        for gname, ms in groups.items():
            for i in rng.choice(len(ms), a.per_group, replace=False):
                tasks.append((ms[i].to_dict(), sc))
                keys.append(gname)
    with ProcessPoolExecutor(a.workers) as pool:
        out = list(pool.map(job, tasks, chunksize=1))
    res = np.array([o[0] for o in out])
    kinds = [o[1] for o in out]
    V = ["zero", "limp", "zero5", "on"]
    print(f"# phys_passive.py, {a.per_group} holistic members per group per directory over {len(a.dirs)} dirs; draw ({TERRAIN}, {START})")
    print("# per variant: disp mean/max (m) | #>0.25 m | work mean (J) | food total | exploded")
    for gname in dict.fromkeys(keys):
        sel = [i for i, k in enumerate(keys) if k == gname]
        R = res[sel]
        kk = sum((kinds[i] for i in sel), [])
        line = f"{gname:9s} n={len(R)}"
        for j, v in enumerate(V):
            c = 4 * j
            line += f" | {v}: {R[:, c].mean():.3f}/{R[:, c].max():.2f} #{int((R[:, c] > 0.25).sum())} W{R[:, c + 1].mean():.0f} F{int(R[:, c + 2].sum())} X{int(R[:, c + 3].sum())}"
        print(line + f" | driven joints by kind {dict((m, kk.count(m)) for m in sorted(set(kk)))}")
    print(f"# total > 0.25 m: zero {int((res[:, 0] > 0.25).sum())}, limp {int((res[:, 4] > 0.25).sum())}, zero5 {int((res[:, 8] > 0.25).sum())} of {len(res)}")
    print("# members eating with motors zeroed: disp(zero) food(zero) | disp(limp) food(limp) | food(on)")
    for i in np.nonzero((res[:, 2] > 0) | (res[:, 6] > 0))[0]:
        print(f"#   {keys[i]:9s} {res[i, 0]:.2f} {res[i, 2]:.0f} | {res[i, 4]:.2f} {res[i, 6]:.0f} | {res[i, 14]:.0f}")
    print("# members > 0.25 m in any variant: zero | limp | zero5 (disp m, work J)")
    for i in np.nonzero((res[:, [0, 4, 8]] > 0.25).any(axis=1))[0]:
        print(f"#   {keys[i]:9s} {res[i, 0]:.2f} ({res[i, 1]:.0f} J) | {res[i, 4]:.2f} | {res[i, 8]:.2f} ({res[i, 9]:.0f} J)  driven {kinds[i]}")


if __name__ == "__main__":
    main()
