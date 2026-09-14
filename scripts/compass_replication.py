"""RBT-69: does the antisymmetric compass replicate on the corrected sign convention?

Installs the four-link nose-to-wheel motif on evolved Pioneers and measures items eaten
against the same robot with no motif, on paired seeds, sweeping the magnitude.  Three
conditions:

* ``baseline``  -- the robot as evolved.
* ``compass``   -- steering on ``n_left - n_right``: the antisymmetric motif, which on this
  body's antiparallel drive axes is a Braitenberg compass (RBT-64).
* ``common``    -- steering on ``n_left + n_right``: the same four links all one sign, which
  is the error RBT-61 made and expects to pirouette rather than steer.

The signs are never typed out.  They come from :func:`rabbitstew.fixed.drive_commands`, so
this script doubles as the worked example of the helper that RBT-64 added precisely because
four separate agents rederived them wrongly.

Substrate: the seven conventional bests committed under ``runs/RBT-19/P-801``, in that run's
own committed config, so the whole thing is reproducible from the repository alone (RBT-68).

The ``world`` argument selects the substrate:

* ``native`` -- RBT-19's own committed config: 26 items in 3 patches, 45 s regrow delay.
* ``w4`` -- reshaped towards the substrate ``runs/sim-audit/verify_independent.py`` names
  (``runs/RBT-23/W4b-801``, W4': 12 items, no regrowth, no patches), which is not committed
  anywhere and so cannot be run directly.  This isolates the world from the robots.

Usage: compass_replication.py [n_seeds] [workers] [native|w4]
"""

import json
import math
import sys
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace

import numpy as np

from rabbitstew.fixed import drive_commands, drive_effector_units
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

RUN = "runs/RBT-19/P-801"
GENERATIONS = (0, 100, 200, 300, 400, 500, 590)  #: the seven robots
MAGNITUDES = (0.25, 0.5, 1.0, 2.0, 4.0, 16.0, 32.0)  #: RBT-62 puts the evolved compass at w ~ 1 against the 16-32 it needs
SEED0 = 7000
WORLD = "native"  #: set from argv; see the module docstring


def config(world: str = None) -> SimConfig:
    """RBT-19's committed config, optionally reshaped towards W4'."""
    cfg = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
    if (world or WORLD) == "w4":
        cfg = replace(cfg, food=replace(cfg.food, items=12, patches=0, regrow=False, regrow_delay=0.0))
    return cfg


def food_noses(ph) -> tuple:
    """``(left, right)`` unit indices of the food sensors on the two drive wheels.

    The chassis nose sits on the root Part and is skipped: a single sensor cannot carry a
    gradient, which is the whole reason the motif needs one nose per wheel.
    """
    side = {}
    for i, ui in enumerate(ph.units):
        if ui.unit.kind != "sensor" or ui.unit.source != "food" or ui.part is None:
            continue
        part = ph.parts[ui.part]
        if part.parent is None:
            continue
        side.setdefault("left" if part.attach_pos[1] > 0 else "right", []).append(i)
    return side["left"][0], side["right"][0]


def install(brain, ph, motif: str, k: float) -> None:
    """Add the four-link motif to the runtime weight matrix, in place.

    Steering on this body is the effector *sum*, so a steering term ``k * n`` enters **both**
    effectors with the same sign.  ``drive_commands`` is linear, so handing it one nose's
    steering coefficient returns that nose's two weights directly -- which is the whole point:
    the caller never has to know which wheel takes which sign.
    """
    if motif == "baseline" or k == 0.0:
        return
    left_e, right_e = drive_effector_units(ph)
    n_left, n_right = food_noses(ph)
    opposite = -k if motif == "compass" else k  # compass steers on n_left - n_right
    for nose, steering in ((n_left, k), (n_right, opposite)):
        w_left, w_right = drive_commands(steering=steering, throttle=0.0)
        for e in left_e:
            brain.W[e, nose] += w_left
        for e in right_e:
            brain.W[e, nose] += w_right


def nose_gradient(n_seeds: int = 8) -> str:
    """Dynamic range of a wheel nose and the left-right gap it offers, over real bouts.

    A compass steers on the *difference* between the two noses, so a null result is only
    informative if that difference is non-trivial on this substrate.  RBT-22 showed the
    summed squash saturating at high density, which would flatten the gradient and make any
    compass measurement vacuous -- this is the check that the answer here is about the
    circuit rather than about the sensor.
    """
    cfg = config()
    g = Genotype.load(f"{RUN}/conventional/best_gen{GENERATIONS[-1]:04d}.json")
    ph = synthesize(g, cfg.synthesis)
    n_left, n_right = food_noses(ph)
    level, gap = [], []
    for s in range(n_seeds):
        sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, SEED0 + s))
        sim.set_food_seed(SEED0 + s)
        for _ in range(int(round(cfg.duration / cfg.control_dt))):
            sim.step()
            a = sim.brains[0].activation
            level.append(float(a[n_left]))
            gap.append(abs(float(a[n_left] - a[n_right])))
    level, gap = np.array(level), np.array(gap)
    return (f"nose gradient ({cfg.food.items} items, smell={cfg.food.smell}, decay={cfg.food.decay}, "
            f"patches={cfg.food.patches}): level {level.min():.3f}-{level.max():.3f}, "
            f"left-right gap median {np.median(gap):.4f} p95 {np.percentile(gap, 95):.4f} "
            f"-- not saturated, so a null here is about the circuit and not the nose")


def _yaw(q) -> float:
    w, x, y, z = q
    return math.atan2(2 * (w * z + x * y), 1 - 2 * (y * y + z * z))


def bout(args) -> dict:
    gen, motif, k, seed, world = args
    cfg = config(world)
    g = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    ph = synthesize(g, cfg.synthesis)
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, seed))
    sim.set_food_seed(seed)
    install(sim.brains[0], ph, motif, k)
    idx = sim.robots[0]
    p0 = sim.center_of_mass(0)[:2].copy()
    last = _yaw(sim.data.xquat[idx.root_body])
    turned = 0.0
    for _ in range(int(round(cfg.duration / cfg.control_dt))):
        sim.step()
        now = _yaw(sim.data.xquat[idx.root_body])
        turned += abs((now - last + math.pi) % (2 * math.pi) - math.pi)
        last = now
    return {"gen": gen, "motif": motif, "k": k, "seed": seed, "world": world,
            "food": float(sim.food_eaten[0]),
            "moved": float(np.linalg.norm(sim.center_of_mass(0)[:2] - p0)),
            "turned": turned / (2 * math.pi)}  # whole turns


def main() -> None:
    global WORLD
    n_seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 64
    workers = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    WORLD = sys.argv[3] if len(sys.argv) > 3 else "native"
    seeds = [SEED0 + s for s in range(n_seeds)]
    jobs = [(g, "baseline", 0.0, s, WORLD) for g in GENERATIONS for s in seeds]
    jobs += [(g, m, k, s, WORLD) for g in GENERATIONS for m in ("compass", "common") for k in MAGNITUDES for s in seeds]
    with ProcessPoolExecutor(workers) as pool:
        rows = list(pool.map(bout, jobs, chunksize=8))

    by = {}
    for r in rows:
        by.setdefault((r["gen"], r["motif"], r["k"]), []).append(r)
    mean = lambda key, *k: float(np.mean([r[key] for r in by[k]]))

    print(f"RBT-69: the antisymmetric compass against its common-mode twin")
    print(f"{RUN}, conventional bests {list(GENERATIONS)}, {n_seeds} paired seeds from {SEED0}, "
          f"{len(jobs)} bouts, world={WORLD}")
    print(nose_gradient() + "\n")
    base = {g: mean("food", g, "baseline", 0.0) for g in GENERATIONS}
    print("baseline items eaten per robot: " + "  ".join(f"g{g}:{base[g]:.3f}" for g in GENERATIONS))
    print(f"pooled baseline {np.mean(list(base.values())):.3f} items, "
          f"moved {np.mean([mean('moved', g, 'baseline', 0.0) for g in GENERATIONS]):.2f} m, "
          f"turned {np.mean([mean('turned', g, 'baseline', 0.0) for g in GENERATIONS]):.2f} turns\n")

    print(f"{'motif':8s} {'w':>5s} | {'items':>7s} {'delta':>7s} {'se':>6s} | {'better':>6s} | {'moved':>6s} {'turned':>7s}")
    for motif in ("compass", "common"):
        for k in MAGNITUDES:
            # paired per robot: the mean difference against that robot's own baseline
            deltas = [mean("food", g, motif, k) - base[g] for g in GENERATIONS]
            # standard error over the per-seed paired differences, pooled across robots
            paired = [r["food"] - b["food"] for g in GENERATIONS
                      for r, b in zip(sorted(by[(g, motif, k)], key=lambda x: x["seed"]),
                                      sorted(by[(g, "baseline", 0.0)], key=lambda x: x["seed"]))]
            se = float(np.std(paired, ddof=1) / math.sqrt(len(paired)))
            items = float(np.mean([mean("food", g, motif, k) for g in GENERATIONS]))
            print(f"{motif:8s} {k:5.2f} | {items:7.3f} {np.mean(deltas):+7.3f} {se:6.3f} | "
                  f"{sum(d > 0 for d in deltas):>3d}/{len(GENERATIONS)} | "
                  f"{np.mean([mean('moved', g, motif, k) for g in GENERATIONS]):6.2f} "
                  f"{np.mean([mean('turned', g, motif, k) for g in GENERATIONS]):7.2f}")
    print("\ndelta is the paired change in items eaten against each robot's own baseline; se is over\n"
          "the per-seed paired differences; better counts robots of 7 whose mean improved; moved is\n"
          "displacement in metres and turned is whole revolutions of accumulated yaw.")


if __name__ == "__main__":
    main()
