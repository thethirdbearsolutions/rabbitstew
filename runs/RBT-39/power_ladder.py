"""How many items on its own path would this null have caught? (RBT-39, after the adversary.)

`power_check.py` sampled the planted fraction at 0 / 25 / 50 / 100% and the report then read a
detection threshold off a straight line through those points, quoting ~7% of the crop. The adversary
(RBT-8 delegate) measured the low end directly and found the crossing between 10% and 15%: the
response is sublinear there, so the extrapolation was optimistic by about 2x. They also diagnosed
why the fraction axis could not have resolved it -- planting is quantised to whole items, and with 24
items in the arena each one is 4.2% of the crop, so 7.5% and 10% plant the same two items and return
identical numbers.

So this sweeps **whole items planted**, which is the quantity the instrument actually has, and
reports the threshold in items first and as a fraction second. There is no interpolation anywhere:
the threshold is the smallest k whose paired t reaches the bar, measured.

Planting k items on the robot's own recorded path is what a perfect compass would have achieved for
that many items, since a robot that steers to food ends up with food where it went. Everything else
is held: the same bouts, the same seeds, the same null layouts, the same paired t over seeds.

usage: power_ladder.py RUN KIND GEN [N_SEEDS] [N_DRAWS] [MAX_K]
"""
import json
import sys
from dataclasses import replace

import numpy as np

from rabbitstew.forage_null import replay_many, within_season_regrowth, world_layouts, world_spot_fn
from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout

BAR = 2.5  #: the paired-t bar the verdict rule uses

run, kind, gen = sys.argv[1], sys.argv[2], int(sys.argv[3])
n = int(sys.argv[4]) if len(sys.argv) > 4 else 16
draws = int(sys.argv[5]) if len(sys.argv) > 5 else 200
max_k = int(sys.argv[6]) if len(sys.argv) > 6 else 6

cfg = SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])
g = Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")
food = cfg.food
disc, eat = food.radius, food.eat_radius
regrow = within_season_regrowth(food)
KS = list(range(0, max_k + 1))


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
    out = {"null": float(replay_many(geoms, layouts, eat, regrow=regrow, spot_fn=spot).mean()),
           "real": float(sim.food_eaten[0])}
    rng = np.random.default_rng(seed)
    centroids = geoms.mean(axis=1)
    for k in KS:
        lay = layouts[0].copy()
        if k:
            lay[:k] = centroids[rng.integers(0, len(centroids), k)]
        out[k] = float(replay_many(geoms, lay[None], eat, regrow=regrow, spot_fn=spot)[0])
    return out


rs = [bout(9000 + s) for s in range(n)]
print(f"{run} {kind} g{gen}: {n} seeds x {draws} null layouts, {food.items} items in the arena "
      f"(one item = {100 / food.items:.1f}% of the crop)")
print(f"{'planted':>8} {'% crop':>7} {'items':>7} {'null':>7} {'t':>7}   verdict")
crossing = None
for k in KS:
    d = np.array([r[k] - r["null"] for r in rs])
    se = float(d.std(ddof=1) / np.sqrt(len(d)))
    t = float(d.mean() / se) if se > 0 else float("nan")
    obs, nul = float(np.mean([r[k] for r in rs])), float(np.mean([r["null"] for r in rs]))
    v = "ABOVE" if t >= BAR else "indistinguishable"
    if crossing is None and t >= BAR:
        crossing = k
    print(f"{k:8d} {100 * k / food.items:6.1f}% {obs:7.3f} {nul:7.3f} {t:+7.2f}   {v}")
real = np.array([r["real"] - r["null"] for r in rs])
rt = float(real.mean() / (real.std(ddof=1) / np.sqrt(len(real)))) if real.std(ddof=1) > 0 else float("nan")
print(f"\nthe real bout, for comparison: {np.mean([r['real'] for r in rs]):.3f} items against the same "
      f"null, t = {rt:+.2f}")
if crossing is None:
    print(f"threshold: NOT REACHED by {max_k} items ({100 * max_k / food.items:.1f}% of the crop) -- "
          f"this champion's null is less sensitive than the ladder tested")
else:
    print(f"threshold: **{crossing} item{'s' if crossing != 1 else ''} on its own path** "
          f"({100 * crossing / food.items:.1f}% of the crop) is the smallest planting this test "
          f"detects at n = {n}. Measured, not interpolated.")
print(json.dumps({"run": run, "kind": kind, "gen": gen, "seeds": n, "draws": draws,
                  "items": food.items, "threshold_items": crossing, "real_t": rt}))
