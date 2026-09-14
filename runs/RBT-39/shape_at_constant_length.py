"""Items per in-disc metre depends on the path's SHAPE, not only its length (RBT-39).

Holding in-disc path length flat is the obvious repair to an items-per-metre claim, and it is a
real repair: it removes the confound that "a controller which merely moves more" clears the rate.
It is not sufficient.  A robot that re-covers ground it has already eaten meets less food per metre
than one on fresh ground, so two paths of *identical length* through the same field, with the same
body and no sensing whatsoever, read materially different rates.

This drives one champion's body along four paths of exactly the same length past the same
world-dealt layouts.  Nothing in it senses anything.  Filed because RBT-67 §3 reads a rise in
items per in-disc metre "on in-disc path that is flat" as steering rather than coverage; that
inference needs this number to be small, and it is not.

usage: shape_at_constant_length.py [RUN] [KIND] [GEN] [DRAWS]
"""
import json
import sys

import numpy as np

from rabbitstew.forage_null import replay_many, within_season_regrowth, world_layouts, world_spot_fn
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from dataclasses import replace

run = sys.argv[1] if len(sys.argv) > 1 else "runs/RBT-38/data/RBT-13"
kind = sys.argv[2] if len(sys.argv) > 2 else "conventional"
gen = int(sys.argv[3]) if len(sys.argv) > 3 else 590
draws = int(sys.argv[4]) if len(sys.argv) > 4 else 200

cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
food = cfg.food
disc, eat = food.radius, food.eat_radius
c = replace(cfg, random_start=True)

# One real bout, only to borrow this body's pose, its world's layouts and its real in-disc length.
sim = Simulation([g], c, spawns=spawn_layout(1, c, 9000))
sim.set_food_seed(9000)
layouts = world_layouts(sim, [700000 + d for d in range(draws)])
sim.set_food_seed(9000)
sim.start_recording(every=1)
for _ in range(int(round(c.duration / c.control_dt))):
    sim.step()
shape = sim.trajectory.as_array()[0, :, :2]
shape = shape - shape.mean(axis=0)
spot, regrow = world_spot_fn(sim), within_season_regrowth(food)

L, step = 4.28, 0.01  #: the champion's own in-disc path length, held identical for every shape
n = int(L / step)
r = L / (2 * np.pi)
SHAPES = {
    "straight line, fresh ground": [np.array([-L / 2 + i * step, 0.0]) for i in range(n)],
    "tight zigzag, partly re-covering": [np.array([x, 0.45 * np.sin(6 * x)])
                                         for x in np.linspace(-L / 3, L / 3, n)],
    "one tight circle, retraces itself": [np.array([r * np.cos(t) - r, r * np.sin(t)])
                                          for t in np.linspace(0, 2 * np.pi, n)],
    "out and back over its own track": [np.array([-L / 4 + (i % (n // 2)) * step, 0.0]) for i in range(n)],
}

print(f"{run} {kind} g{gen}: {draws} world-dealt layouts, {food.items} items in a {disc:.1f} m disc")
print(f"every path is exactly {L:.2f} m long, walked by the same body, with no sensing in any of them\n")
print(f"{'path shape':36s} {'items/m':>9s} {'items':>8s}")
rates = {}
for label, pts in SHAPES.items():
    path = np.stack([shape + p for p in pts])
    got = float(replay_many(path, layouts, eat, regrow=regrow, spot_fn=spot).mean())
    rates[label] = got / L
    print(f"{label:36s} {got / L:9.3f} {got:8.2f}")
lo, hi = min(rates.values()), max(rates.values())
print(f"\nspread from shape alone, at pinned length and zero steering: {lo:.3f} to {hi:.3f} items/m, "
      f"a factor of {hi / lo:.2f}")
print("So a rise in items per in-disc metre on flat path is not by itself evidence of steering: a")
print("change that merely straightened the sweeps would produce the same signature.  The test that")
print("is immune to both length and shape is the trajectory null (trajectory_null in forage_null).")
