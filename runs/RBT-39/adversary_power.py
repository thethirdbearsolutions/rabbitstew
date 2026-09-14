"""RBT-39 adversary: is the 7% detection threshold measured, or extrapolated?

RBT-39 §6 runs its positive control at planted fractions 0/25/50/100% and then says "taking the
response as linear in the planted fraction, t crosses 2.5 at roughly 7% of the crop". That 7% is
the number carrying the report's central claim -- that ten "indistinguishable" verdicts are a
measurement and not a shortage of power -- and it is an extrapolation *below* the lowest point
measured, into the regime where the planted signal is smallest and the response is least likely
to still be linear.

This is RBT-39's own power_check.py, unmodified except that FRACTIONS is read from the
environment, so the low regime can be measured rather than extrapolated. All credit for the
method and the code to its author; the only contribution here is running it where the claim lives.

usage: PC_FRACTIONS=0.05,0.075,0.10,0.15 adversary_power.py RUN KIND GEN [N_SEEDS] [N_DRAWS]
"""

import json
import sys
from dataclasses import replace

import numpy as np

from rabbitstew.forage_null import replay_many, within_season_regrowth, world_layouts, world_spot_fn
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

run, kind, gen = sys.argv[1], sys.argv[2], int(sys.argv[3])
n = int(sys.argv[4]) if len(sys.argv) > 4 else 16
draws = int(sys.argv[5]) if len(sys.argv) > 5 else 200
cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
ph = synthesize(g, cfg.synthesis)
food = cfg.food
disc, eat = food.radius, food.eat_radius
regrow = within_season_regrowth(food)
import os
FRACTIONS = [float(x) for x in os.environ.get("PC_FRACTIONS", "0.0,0.25,0.5,1.0").split(",")]


def bout(seed: int) -> dict:
    c = replace(cfg, random_start=True)
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    real = sim.food_pos.copy()
    layouts = world_layouts(sim, [600000 + 997 * seed + d for d in range(draws)])
    sim.set_food_seed(seed)
    assert np.array_equal(sim.food_pos, real)
    sim.start_recording(every=1)
    for _ in range(int(round(c.duration / c.control_dt))):
        sim.step()
    geoms = sim.trajectory.as_array()[1:, :, :2]
    spot = world_spot_fn(sim)
    null = replay_many(geoms, layouts, eat, regrow=regrow, spot_fn=spot).astype(float)
    # A layout with `frac` of its items planted on the path the robot actually took, the rest drawn
    # by the world as usual.  Planted items sit at the centroid of a randomly chosen frame.
    rng = np.random.default_rng(seed)
    centroids = geoms.mean(axis=1)
    out = {"null": float(null.mean())}
    for frac in FRACTIONS:
        k = int(round(frac * food.items))
        lay = layouts[0].copy()
        if k:
            lay[:k] = centroids[rng.integers(0, len(centroids), k)]
        out[frac] = float(replay_many(geoms, lay[None], eat, regrow=regrow, spot_fn=spot)[0])
    return out


rs = [bout(9000 + s) for s in range(n)]
print(f"{run} {kind} g{gen}: positive control, {n} seeds x {draws} null layouts, "
      f"{food.items} items, planting a fraction of them on the robot's own recorded path")
print(f"{'planted':>9} {'items':>7} {'null':>7} {'ratio':>7} {'t':>7}   verdict")
for frac in FRACTIONS:
    d = np.array([r[frac] - r["null"] for r in rs])
    obs, nul = float(np.mean([r[frac] for r in rs])), float(np.mean([r["null"] for r in rs]))
    se = float(d.std(ddof=1) / np.sqrt(len(d)))
    t = float(d.mean() / se) if se > 0 else float("nan")
    v = "ABOVE its own gait" if t >= 2.5 else "below" if t <= -2.5 else "indistinguishable"
    print(f"{100 * frac:8.0f}% {obs:7.3f} {nul:7.3f} {obs / nul if nul else float('nan'):7.2f} {t:+7.2f}   {v}")
print("\n0% planted is the control on the control: a layout the world dealt, replayed past the same")
print("path, must read indistinguishable.  The rows below it say what a compass would have looked like.")
