"""Which way does a population actually drive? RBT-69 / RBT-76.

The Pioneer has a designed front, and `drive_straight_genotype`'s (+p, -p)
defines "forward" relative to it. Evolution never agreed to that: nothing in a
foraging ecology rewards driving nose-first over tail-first, so each lineage is
free to fix on either, and they do.

This matters because it flips the sign of every hand-installed sensorimotor
circuit. A chemotactic steering term for a forward-driver is an ANTI-chemotactic
term for a reverse-driver, with identical weights. Measure this before
installing a circuit on a population, or the result is a coin flip.

Reports the circular mean of (travel azimuth - body yaw) per robot, with the
resultant length R as a concentration measure (1.0 = perfectly consistent).

Usage: python scripts/travel_direction.py <run-dir> [gens...]
"""
import json, sys, glob, numpy as np
from dataclasses import replace
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout


def yaw_of(s):
    q = s.data.xquat[s.robots[0].root_body]
    return float(np.arctan2(2 * (q[0] * q[3] + q[1] * q[2]), 1 - 2 * (q[2] ** 2 + q[3] ** 2)))


def wrap(a):
    return float((a + np.pi) % (2 * np.pi) - np.pi)


def offsets(run, gen, cfg, seeds=16):
    g = Genotype.load(f"{run}/conventional/best_gen{gen:04d}.json")
    out = []
    for seed in range(9000, 9000 + seeds):
        c = replace(cfg, random_start=True)
        sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
        sim.set_food_seed(seed)
        last = sim.data.xpos[sim.robots[0].root_body][:2].copy()
        for _ in range(int(round(c.duration / c.control_dt))):
            sim.step()
            if sim.exploded[0]:
                break
            pos = sim.data.xpos[sim.robots[0].root_body][:2]
            d = pos - last
            if np.linalg.norm(d) > 1e-3:
                out.append(wrap(float(np.arctan2(d[1], d[0])) - yaw_of(sim)))
            last = pos.copy()
    return np.array(out)


def circ(o):
    s, c = np.mean(np.sin(o)), np.mean(np.cos(o))
    return float(np.degrees(np.arctan2(s, c))), float(np.hypot(s, c))


def trace(run, seeds=6):
    """Travel direction across evolutionary time: is it fixed, or does it drift?

    A trait under selection is pinned. A trait selection cannot see wanders. Run
    this before concluding anything about "the population" - the answer can be
    different at gen 200 and gen 400 of the same run.
    """
    cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
    gens = sorted(int(f.split("best_gen")[1][:4])
                  for f in glob.glob(f"{run}/conventional/best_gen*.json"))
    gens = [g for g in gens if g % 50 == 0 or g == gens[-1]]
    print(f"{run}")
    print("| gen | travel offset (deg) | R | facing |")
    print("|---|---|---|---|")
    flips, prev = 0, None
    for gen in gens:
        o = offsets(run, gen, cfg, seeds)
        if not len(o):
            continue
        m, R = circ(o)
        back = abs(m) > 90
        if prev is not None and back != prev:
            flips += 1
        prev = back
        print(f"| {gen} | {m:+.1f} | {R:.2f} | {'BACKWARD' if back else 'forward'} |")
    print(f"\n{flips} direction flips across {len(gens)} sampled generations.")
    if flips:
        print("Direction of travel is NOT fixed in this lineage. Any circuit whose sign")
        print("depends on it is sign-unstable across evolutionary time.")


def main(run, gens=None):
    cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
    if not gens:
        gens = [int(f.split("best_gen")[1][:4])
                for f in sorted(glob.glob(f"{run}/conventional/best_gen*.json"))]
        gens = [g for g in gens if g in (90, 190, 290, 390, 490, 550, 590)] or gens[-7:]
    print(f"{run}")
    print("| gen | travel azimuth - body yaw (deg) | R |")
    print("|---|---|---|")
    pooled = []
    for gen in gens:
        o = offsets(run, gen, cfg)
        pooled += list(o)
        m, R = circ(o)
        print(f"| {gen} | {m:+.1f} | {R:.3f} |")
    m, R = circ(np.array(pooled))
    print(f"\nPOOLED {m:+.1f} deg, R={R:.3f}  -> "
          f"{'drives BACKWARD (reverse of the designed front)' if abs(m) > 90 else 'drives FORWARD'}")


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[2] == "--trace":
        trace(sys.argv[1])
    else:
        main(sys.argv[1], [int(x) for x in sys.argv[2:]])
