"""RBT-97 item 4: which sign is g500's own?

g500 is the one P-801 robot that does not fit the arm's picture: its own compass pays least
of the seven (+1.031 at a = 64) and its ANTI-compass also pays (+0.609, and +1.234 at
a = 384). I flagged it in the report and the coordinator asked for its direction of travel at
the reference probe.

The first thing to say is that it is already there. `scripts/travel_direction.py` probes 16
seeds at the config's own 15 s duration, which IS the reference setting (16 x 15 s), so the
committed +23.8 deg with R = 0.506 in `docs/runs/RBT-69-travel-direction.txt` is not a cheap
reading that a longer probe would fix. **R = 0.506 is a property of the robot, not of the
probe**: this robot's direction of travel is genuinely inconsistent where the other six are
not (R = 0.62 to 0.84).

So the useful measurement is not "again, but longer" -- it is the SHAPE of the distribution.
This reports, per robot, the pooled offset and R at 16 seeds (reproducing the committed
table, which is the calibration) and then g500 at 64 seeds broken down PER SEED: how many
bouts it drives forward, how many backward, and how concentrated each bout is. A robot that
drives forward on half its bouts and backward on the other half has no single chemotactic
sign, and both installed signs would pay on the bouts that suit them.

Usage: g500_direction.py [--pop p801] [--gen 500] [--seeds 64] [--procs 4]
"""
import argparse
import importlib.util
import os
import sys
from dataclasses import replace
from multiprocessing import get_context

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
sys.path.insert(0, os.path.join(_ROOT, "scripts"))


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


mech = _load("rbt97_mechanism", os.path.join(_HERE, "mechanism.py"))
td = _load("travel_direction", os.path.join(_ROOT, "scripts", "travel_direction.py"))
cds = mech.cds

from rabbitstew.simulation import Simulation, spawn_layout  # noqa: E402

CFG = {}


def per_seed(task):
    """(seed, circular mean offset in degrees, R) for one bout. td's probe, one seed."""
    pop, gen, seed = task
    cfg = replace(CFG[pop], random_start=True)
    g = cds.genotype(pop, gen)
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, seed))
    sim.set_food_seed(seed)
    last = sim.data.xpos[sim.robots[0].root_body][:2].copy()
    out = []
    for _ in range(int(round(cfg.duration / cfg.control_dt))):
        sim.step()
        if sim.exploded[0]:
            break
        pos = sim.data.xpos[sim.robots[0].root_body][:2]
        d = pos - last
        if np.linalg.norm(d) > 1e-3:
            out.append(td.wrap(float(np.arctan2(d[1], d[0])) - td.yaw_of(sim)))
        last = pos.copy()
    if not out:
        return seed, float("nan"), 0.0, 0
    deg, R = td.circ(np.array(out))
    return seed, deg, R, len(out)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pop", default="p801")
    p.add_argument("--gen", type=int, default=500)
    p.add_argument("--seeds", type=int, default=64)
    p.add_argument("--procs", type=int, default=4)
    args = p.parse_args()
    pop = args.pop
    gens = list(cds.POPULATIONS[pop]["gens"])
    CFG[pop] = cds.config(pop)
    committed = mech.travel_table(pop)

    print(f"# RBT-97 item 4: g{args.gen}'s direction of travel on {pop}")
    print(f"{cds.POPULATIONS[pop]['run']}; probe = scripts/travel_direction.py's, which is")
    print("16 seeds x the config's own 15 s duration -- i.e. already the reference setting.\n")

    print("## All seven at 16 seeds: does the committed table reproduce?")
    tasks = [(pop, g, 9000 + i) for g in gens for i in range(16)]
    with get_context("fork").Pool(args.procs) as pool:
        rows = pool.map(per_seed, tasks, chunksize=4)
    by = {}
    for (pop_, g, seed), r in zip(tasks, rows):
        by.setdefault(g, []).append(r)
    print(f"{'gen':>6s} {'offset':>9s} {'R':>6s} | {'committed':>10s} | drives")
    for g in gens:
        angs = np.concatenate([[np.radians(r[1])] * r[3] for r in by[g] if r[3]])
        deg, R = td.circ(angs)
        print(f"g{g:<5d} {deg:+8.1f}° {R:6.3f} | {committed[g]:+9.1f}° | "
              f"{'BACKWARD' if abs(deg) > 90 else 'forward'}")

    print(f"\n## g{args.gen} at {args.seeds} seeds, per bout")
    tasks = [(pop, args.gen, 9000 + i) for i in range(args.seeds)]
    with get_context("fork").Pool(args.procs) as pool:
        rows = pool.map(per_seed, tasks, chunksize=4)
    good = [r for r in rows if r[3]]
    back = [r for r in good if abs(r[1]) > 90]
    fwd = [r for r in good if abs(r[1]) <= 90]
    angs = np.concatenate([[np.radians(r[1])] * r[3] for r in good])
    deg, R = td.circ(angs)
    print(f"  pooled over {len(good)} bouts: {deg:+.1f}° R = {R:.3f}")
    print(f"  bouts driving forward:  {len(fwd):>3d}/{len(good)}  "
          f"(median |offset| {np.median([abs(r[1]) for r in fwd]) if fwd else float('nan'):.1f}°, "
          f"median within-bout R {np.median([r[2] for r in fwd]) if fwd else float('nan'):.2f})")
    print(f"  bouts driving backward: {len(back):>3d}/{len(good)}  "
          f"(median |offset| {np.median([abs(r[1]) for r in back]) if back else float('nan'):.1f}°, "
          f"median within-bout R {np.median([r[2] for r in back]) if back else float('nan'):.2f})")
    q = np.percentile([abs(r[1]) for r in good], [10, 25, 50, 75, 90])
    print(f"  |offset| deciles over bouts: " + ", ".join(f"{x:.0f}°" for x in q))
    print("\n  A robot that drives one way on some bouts and the other way on others has no")
    print("  single chemotactic sign, and each installed sign pays on the bouts that suit it.")
    print("  That is the reading to check against the arm's finding that BOTH signs pay on it.")


if __name__ == "__main__":
    main()
