"""Pre-launch calibration for the persistent foraging world (RBT-2, built in RBT-19).

Three numbers have to be settled before that world is worth running, and all
three can be measured with today's code, because a persistent world with a
regrowth delay longer than a season *is* the present simulator with
``regrow=False`` and a season-start crop carried in from the season before.

1. **Harvest.** ``E(N0)``: items a group of four random Pioneers eats in a 15 s
   season that starts with ``N0`` items and grows none back, for a uniform and
   for a patchy layout.  The baseline (``forage-801``: 12 items, instant random
   regrowth) is measured alongside as the thing to match.
2. **The ledger.** With a regrow delay of ``d`` seasons, an item eaten in
   season ``s`` is missing from seasons ``s+1..s+d``, so the season-start crop
   settles where ``N* = S - d * E(N*)`` for a world of ``S`` spots.  Solving it
   gives the spot count that puts the founders' season-start crop at the
   baseline's 12, and the harvest they get there.
3. **Smell.** Level and two-nose differential of the ``food`` sensor over the
   disc, for the summed squash ``i/(1+i)`` in use and for the mean and log
   normalisations RBT-22 adds, at decay 1 m and 3 m.  Geometry only, no physics.

5. **The built world** (`world`, added in RBT-19).  The same ledger measured against the
   real persistent arenas rather than the stand-in: arenas created once, run season
   after season with fresh random Pioneers, food state carried by ``run_group``.  This
   is the acceptance test for the implementation.

usage: persistent_supply.py [GROUPS] [SECTIONS]   e.g. persistent_supply.py 12 harvest,ledger,smell
       persistent_supply.py 12 world
"""

import json
import sys

import numpy as np

RADIUS = 3.0  #: food disc (m), as in every arm of the fan-out
NOSE_SEP = 0.33  #: distance between the Pioneer's two wheel noses (m)
DURATION = 15.0
GROUP = 4
PATCHES, PATCH_RADIUS = 3, 0.6
CLEARANCE = 0.8
CROPS = (6, 12, 18, 26, 32)
DELAY_SEASONS = 3  #: regrow delay of 45 s at a 15 s season


# -- layouts ---------------------------------------------------------------- #

def uniform_food(n: int, rng, avoid=None) -> np.ndarray:
    """``n`` items uniform in the disc, none within CLEARANCE of a robot."""
    out = []
    while len(out) < n:
        r, a = RADIUS * np.sqrt(rng.random()), rng.uniform(0, 2 * np.pi)
        p = np.array([r * np.cos(a), r * np.sin(a)])
        if avoid is None or len(avoid) == 0 or np.linalg.norm(avoid - p, axis=1).min() >= CLEARANCE:
            out.append(p)
    return np.array(out)


def patchy_food(n: int, rng, avoid=None, patches: int = PATCHES, patch_radius: float = PATCH_RADIUS):
    """``n`` items in ``patches`` clusters: centres uniform in the disc, items uniform in a patch."""
    centres = uniform_food(patches, rng)
    out = []
    while len(out) < n:
        c = centres[rng.integers(0, patches)]
        r, a = patch_radius * np.sqrt(rng.random()), rng.uniform(0, 2 * np.pi)
        p = c + np.array([r * np.cos(a), r * np.sin(a)])
        if np.linalg.norm(p) > RADIUS:
            continue
        if avoid is None or len(avoid) == 0 or np.linalg.norm(avoid - p, axis=1).min() >= CLEARANCE:
            out.append(p)
    return np.array(out), centres


# -- 1. harvest ------------------------------------------------------------- #

def harvest(groups: int) -> dict:
    from rabbitstew.fixed import pioneer_genotype
    from rabbitstew.genotype import BrainVocabulary, random_genotype
    from rabbitstew.simulation import FoodConfig, SimConfig, Simulation, SynthesisConfig, spawn_layout

    vocab = BrainVocabulary.named("foraging")
    rng = np.random.default_rng(0)
    pops = {
        "pioneer": [[pioneer_genotype(rng, hidden=6, rich=True, sources=vocab.sensor_sources, name=f"p{g}_{i}") for i in range(GROUP)] for g in range(groups)],
        "holistic": [[random_genotype(rng, name=f"h{g}_{i}", vocab=vocab) for i in range(GROUP)] for g in range(groups)],
    }

    def run(genotypes, crop, layout, regrow, seed):
        cfg = SimConfig(
            duration=DURATION, random_start=True, score="food", synthesis=SynthesisConfig(mass_budget=15.34),
            food=FoodConfig(items=crop, radius=RADIUS, eat_radius=0.35, decay=1.0, work_cost=0.0, clearance=CLEARANCE, regrow=regrow),
        )
        spawns = spawn_layout(len(genotypes), cfg, seed)
        sim = Simulation(genotypes, cfg, spawns=spawns)
        sim.set_food_seed(seed)
        if layout != "uniform":  # the patchy layout the persistent world places
            place = np.random.default_rng(seed)
            sim.food_pos = patchy_food(crop, place, sim._robot_positions())[0]
        sim.run()
        return float(sim.food_eaten.sum()), float(sim.work.sum()) / 1000.0

    out = {}
    rows = [("baseline", "uniform", 12, True)] + [(f"crop{c}", lay, c, False) for c in CROPS for lay in ("uniform", "patchy")]
    for label, layout, crop, regrow in rows:
        for kind, pop in pops.items():
            eaten, work = zip(*(run(pop[g], crop, layout, regrow, 100 + g) for g in range(groups)))
            e, w = np.array(eaten), np.array(work)
            key = f"{kind}/{label}/{layout}/{'regrow' if regrow else 'deplete'}"
            out[key] = {"eaten_mean": e.mean(), "eaten_sd": e.std(), "per_robot": e.mean() / GROUP, "work_kJ_mean": w.mean() / GROUP}
            print(f"{kind:9s} {layout:7s} {'regrow' if regrow else 'deplete':7s} crop {crop:3d}  group eats {e.mean():5.2f} ± {e.std():4.2f}"
                  f"  per robot {e.mean() / GROUP:4.2f}  work {w.mean() / GROUP:5.1f} kJ", flush=True)
    return out


# -- 2. the ledger ---------------------------------------------------------- #

def ledger(harvest_by_crop: dict, delay: int = DELAY_SEASONS) -> dict:
    """Season-start crop and harvest at the fixed point ``N* = S - delay * E(N*)``.

    ``harvest_by_crop`` maps a season-start crop to items the group eats that
    season (the depleting measurement above); ``E`` in between is linear in the
    crop, which is what the measurement shows over a factor of five in density.
    """
    crops = np.array(sorted(harvest_by_crop))
    eats = np.array([harvest_by_crop[c] for c in crops])
    slope = float(np.linalg.lstsq(crops[:, None], eats, rcond=None)[0][0])  # E(N) = slope * N through the origin
    out = {"slope_items_per_crop": slope, "spots": {}}
    for spots in (12, 18, 26, 32, 40):
        start = spots / (1.0 + delay * slope)
        out["spots"][spots] = {"season_start_crop": start, "harvest_per_group": slope * start, "per_robot": slope * start / GROUP, "ceiling_per_group": spots / delay}
        print(f"spots {spots:3d}  season-start crop {start:5.1f}  group eats {slope * start:5.2f}/season  per robot {slope * start / GROUP:4.2f}"
              f"  supply ceiling {spots / delay:5.2f}/season", flush=True)
    target = 12.0 * (1.0 + delay * slope)
    out["spots_for_baseline_crop"] = target
    print(f"spots for a season-start crop of 12: {target:.1f}", flush=True)
    return out


# -- 3. smell --------------------------------------------------------------- #

def squash(exps: np.ndarray, mode: str) -> np.ndarray:
    i = {"sum": exps.sum(1), "mean": exps.mean(1), "log": np.log1p(exps.sum(1))}[mode]
    return i / (1.0 + i)


def smell(trials: int = 4000) -> dict:
    rng = np.random.default_rng(7)

    def read(points, food, decay, mode):
        d = np.linalg.norm(food[None, :, :] - points[:, None, :], axis=2)
        return squash(np.exp(-d / decay), mode)

    def row(label, food, aim, decay, mode):
        p = uniform_food(trials, rng)
        level = read(p, food, decay, mode)
        d = np.linalg.norm(aim[None, :, :] - p[:, None, :], axis=2)
        j = np.argmin(d, axis=1)
        near = d.min(axis=1)  # distance to the nearest patch centre (or item, in a uniform layout)
        u = aim[j] - p
        u /= np.linalg.norm(u, axis=1, keepdims=True) + 1e-12
        diff = read(p + u * NOSE_SEP / 2, food, decay, mode) - read(p - u * NOSE_SEP / 2, food, decay, mode)
        far = near > 2.0  # a robot two metres out, which is what a long decay is bought for
        rec = {"level_p10": np.percentile(level, 10), "level_p90": np.percentile(level, 90), "nose_diff_median": float(np.median(diff)),
               "right_sign": float((diff > 0).mean()), "nose_diff_far": float(np.median(diff[far])), "right_sign_far": float((diff[far] > 0).mean())}
        print(f"{label:40s} decay {decay:.0f} m  {mode:4s}  level {rec['level_p10']:.3f}-{rec['level_p90']:.3f}"
              f"  nose difference {rec['nose_diff_median']:.1e} ({100 * rec['right_sign']:.0f}% toward food)"
              f"  beyond 2 m {rec['nose_diff_far']:.1e} ({100 * rec['right_sign_far']:.0f}%)", flush=True)
        return rec

    out = {}
    food_u = uniform_food(12, rng)
    out["baseline 12 uniform d1 sum"] = row("baseline: 12 uniform", food_u, food_u, 1.0, "sum")
    out["W1 12 uniform d3 sum"] = row("W1: 12 uniform", food_u, food_u, 3.0, "sum")
    for n in (12, 26):
        food_p, centres = patchy_food(n, rng)
        for mode in ("sum", "mean", "log"):
            for decay in (1.0, 2.0, 3.0):
                out[f"patchy {n} d{decay:.0f} {mode}"] = row(f"persistent: {n} in {PATCHES} patches r={PATCH_RADIUS}", food_p, centres, decay, mode)
    return out


# -- 4. depletion contrast -------------------------------------------------- #

def depletion(standing=(9, 5, 3, 1, 0)) -> dict:
    """Can the sensor tell a full patch from a stripped one?

    The persistent world's new signal is that a patch runs out, so a robot
    standing a metre from patch A should read less of it once A is eaten down.
    Geometry: three patches 1.8 m from the centre, 120 degrees apart, B and C
    full at nine items; the robot is 1 m outside A, and A empties.
    """
    ang = np.array([0.0, 2 * np.pi / 3, 4 * np.pi / 3])
    centres = np.c_[1.8 * np.cos(ang), 1.8 * np.sin(ang)]
    point = centres[0] * (2.8 / 1.8)  # a metre beyond patch A, outward
    rng = np.random.default_rng(3)
    out = {}
    for mode in ("sum", "mean", "log"):
        for decay in (1.0, 3.0):
            vals = []
            for k in standing:
                items = [c + PATCH_RADIUS * np.sqrt(rng.random(1)) * np.c_[np.cos(a), np.sin(a)][0]
                         for ci, c in enumerate(centres) for a in rng.uniform(0, 2 * np.pi, k if ci == 0 else 9)]
                food = np.array(items).reshape(-1, 2)
                d = np.linalg.norm(food - point, axis=1)[None, :]
                vals.append(float(squash(np.exp(-d / decay), mode)[0]))
            out[f"d{decay:.0f} {mode}"] = dict(zip(map(str, standing), vals))
            drop = vals[0] - vals[-1]
            print(f"patch A at {standing} items, decay {decay:.0f} m {mode:4s}:  "
                  + " ".join(f"{v:.3f}" for v in vals) + f"   full-to-empty contrast {drop:.3f}", flush=True)
    return out


# -- 5. the built world: the acceptance test -------------------------------- #

def world(groups: int = 12, seasons: int = 30, settle_from: int = 15, spots: int = 26, workers: int = 4) -> dict:
    """The same ledger, measured against the *real* persistent arenas rather than a stand-in.

    ``groups`` arenas are created and then run season after season, each season with a fresh
    group of four random Pioneers (founders never improve, so the fixed point is the founders').
    Arena food state carries from one season to the next through ``run_group``'s ``food_state``,
    exactly as :class:`~rabbitstew.ecology.Ecology` carries it.  The settled season-start crop and
    harvest are the acceptance test for the implementation: RBT-2 predicts a crop of 12.6 and 4.48
    items a group at 26 spots.
    """
    from rabbitstew.evolution import BoutRunner
    from rabbitstew.fixed import pioneer_genotype
    from rabbitstew.genotype import BrainVocabulary
    from rabbitstew.simulation import FoodConfig, SimConfig, SynthesisConfig

    vocab = BrainVocabulary.named("foraging")
    rng = np.random.default_rng(0)
    cfg = SimConfig(duration=DURATION, random_start=True, score="food", synthesis=SynthesisConfig(mass_budget=15.34),
                    food=FoodConfig(items=spots, radius=RADIUS, eat_radius=0.35, decay=1.0, work_cost=0.0, clearance=CLEARANCE,
                                    patches=PATCHES, patch_radius=PATCH_RADIUS, regrow_delay=DELAY_SEASONS * DURATION))
    runner = BoutRunner(cfg, workers)
    states = [None] * groups
    seeds = [1000 + i for i in range(groups)]
    rows = []
    try:
        for s in range(seasons):
            crop = [spots if st is None else int(sum(st["alive"])) for st in states]
            pops = [[pioneer_genotype(rng, hidden=6, rich=True, sources=vocab.sensor_sources, name=f"p{s}_{g}_{i}") for i in range(GROUP)] for g in range(groups)]
            out = runner.run_persistent_groups([(pops[g], 100 + s * groups + g, states[g], seeds[g]) for g in range(groups)], cfg)
            eaten = []
            for g, (res, st) in enumerate(out):
                states[g] = st
                eaten.append(sum(r["food"] for r in res))
            rows.append({"season": s, "crop_mean": float(np.mean(crop)), "empty_fraction": 1.0 - float(np.mean(crop)) / spots,
                         "eaten_mean": float(np.mean(eaten)), "eaten_sd": float(np.std(eaten)), "per_robot": float(np.mean(eaten)) / GROUP})
            print(f"season {s:3d}  season-start crop {rows[-1]['crop_mean']:5.2f}/{spots}  ({100 * rows[-1]['empty_fraction']:4.1f}% empty)"
                  f"  group eats {rows[-1]['eaten_mean']:5.2f} ± {rows[-1]['eaten_sd']:4.2f}  per robot {rows[-1]['per_robot']:4.2f}", flush=True)
    finally:
        runner.close()
    tail = rows[settle_from:]
    settled = {"spots": spots, "seasons": seasons, "settle_from": settle_from, "arenas": groups,
               "season_start_crop": float(np.mean([r["crop_mean"] for r in tail])),
               "empty_fraction": float(np.mean([r["empty_fraction"] for r in tail])),
               "group_eats": float(np.mean([r["eaten_mean"] for r in tail])),
               "per_robot": float(np.mean([r["per_robot"] for r in tail])),
               "ceiling_per_group": spots / DELAY_SEASONS, "rows": rows}
    print(f"\nsettled over seasons {settle_from}-{seasons - 1}: season-start crop {settled['season_start_crop']:.2f}"
          f"  ({100 * settled['empty_fraction']:.1f}% of spots empty)  group eats {settled['group_eats']:.2f}"
          f"  per robot {settled['per_robot']:.2f}  supply ceiling {settled['ceiling_per_group']:.2f}", flush=True)
    for label, got, want in (("season-start crop", settled["season_start_crop"], 12.6), ("group eats", settled["group_eats"], 4.48)):
        off = 100 * (got - want) / want
        print(f"  {label:18s} measured {got:5.2f}  predicted {want:5.2f}  off by {off:+5.1f}%  {'OK' if abs(off) <= 25 else 'OUT OF TOLERANCE'}", flush=True)
    return settled


if __name__ == "__main__":
    groups = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    sections = (sys.argv[2] if len(sys.argv) > 2 else "harvest,ledger,smell").split(",")
    result = {}
    if "harvest" in sections:
        print("\n== 1. harvest: what a 15 s season yields ==", flush=True)
        result["harvest"] = harvest(groups)
    if "ledger" in sections and "harvest" in result:
        print(f"\n== 2. the ledger: regrow delay {DELAY_SEASONS} seasons, patchy layout, random Pioneers ==", flush=True)
        by_crop = {c: result["harvest"][f"pioneer/crop{c}/patchy/deplete"]["eaten_mean"] for c in CROPS}
        result["ledger"] = ledger(by_crop)
    if "smell" in sections:
        print("\n== 3. smell: level and two-nose differential ==", flush=True)
        result["smell"] = smell()
    if "depletion" in sections or "smell" in sections:
        print("\n== 4. depletion contrast: a patch being eaten down ==", flush=True)
        result["depletion"] = depletion()
    if "world" in sections:
        print("\n== 5. the built persistent world: settled crop and harvest ==", flush=True)
        result["world"] = world(groups)
    json.dump(result, open("persistent_supply.json", "w"), indent=2, default=float)
