"""Where the informative density window is, and whether anything can live in it (RBT-24).

Every arm of the foraging fan-out has been run at a density on a doubling
ladder: 3, 6, 12 and 24 items in the 3 m disc (plus 6 in a 4 m disc).  The
docs' own reading is that random lumps bootstrap "somewhere between six and
twelve", and that the six-item arm went extinct at season 51 from a breeding
population with a *positive* budget, which is demographic stochasticity rather
than an economy.  The window the fan-out needs is therefore inside one of its
own doublings, and nobody has measured it.

This measures it, on today's simulator and with no new world: at each density,
what a founder draw of 60 random robots of each population earns in a season,
how many of them are solvent, how long the insolvent ones last on their
founding energy, and what the baseline's evolved blind mower would net there.
Geometry and physics only; no evolution is run.

The two walls of the window:

* **Lower wall, bootstrap.** Too few founders solvent and the survivors are a
  handful, which the six-item arm showed is fatal at capacity 60 whatever the
  budget says.
* **Upper wall, mowing pays.** Where a blind mower of the baseline's measured
  shape is comfortably net positive, sensing is an expense and the arm returns
  a cow.

usage: density_window.py [GROUPS] [DENSITIES]   e.g. density_window.py 15 3,6,8,9,10,12
"""

import json
import sys

import numpy as np

RADIUS = 3.0  #: food disc (m), as in every arm of the fan-out
DURATION = 15.0
GROUP = 4
CLEARANCE = 0.8
DENSITIES = (3, 6, 8, 9, 10, 12, 16, 24)

# the ecology's economy, unchanged across the whole fan-out
WORK_COST = 0.03  #: energy per kJ
BASAL = 0.25  #: energy per season
INITIAL_ENERGY = 3.0  #: what a founder starts with
BIRTH_COST = 1.0  #: what a parent pays and, exactly, all a newborn gets
BIRTH_THRESHOLD = 3.0

# the baseline's evolved blind mower, measured at 12 items (docs/foraging-world.md,
# season 100 of forage-801): 2.25 items over an 11.9 m path on 4.8 kJ.  Its yield is
# what a random walk of its length meets, so it scales linearly in density.
MOWER_ITEMS_AT_12, MOWER_KJ = 2.25, 4.8
SHARED_ARENA = 0.385 / 0.50  #: RBT-21's realised-versus-solo yield for the baseline's founder lump


def founder_draw(groups: int, items: int) -> dict:
    """Run `groups` groups of four random robots of each population for one season."""
    from rabbitstew.fixed import pioneer_genotype
    from rabbitstew.genotype import BrainVocabulary, random_genotype
    from rabbitstew.simulation import FoodConfig, SimConfig, Simulation, SynthesisConfig, spawn_layout

    vocab = BrainVocabulary.named("foraging")
    rng = np.random.default_rng(0)  # the same founder draw at every density, so density is the only difference
    pops = {
        "pioneer": [[pioneer_genotype(rng, hidden=6, rich=True, sources=vocab.sensor_sources, name=f"p{g}_{i}") for i in range(GROUP)] for g in range(groups)],
        "holistic": [[random_genotype(rng, name=f"h{g}_{i}", vocab=vocab) for i in range(GROUP)] for g in range(groups)],
    }
    out = {}
    for kind, pop in pops.items():
        eaten, work, blown = [], [], []
        for g in range(groups):
            cfg = SimConfig(
                duration=DURATION, random_start=True, score="food", synthesis=SynthesisConfig(mass_budget=15.34),
                food=FoodConfig(items=items, radius=RADIUS, eat_radius=0.35, decay=1.0, work_cost=0.0, clearance=CLEARANCE),
            )
            sim = Simulation(pop[g], cfg, spawns=spawn_layout(GROUP, cfg, 100 + g))
            sim.set_food_seed(100 + g)
            sim.run()
            eaten.extend(float(x) for x in sim.food_eaten)
            work.extend(float(x) / 1000.0 for x in sim.work)
            blown.extend(bool(x) for x in sim.exploded)
        out[kind] = {"items": np.array(eaten), "kJ": np.array(work), "exploded": np.array(blown)}
    return out


def report(groups: int, densities) -> dict:
    out = {}
    print(f"founder draw: {groups * GROUP} robots per population per density, one 15 s season, economy work {WORK_COST}/kJ + basal {BASAL}")
    print("'ate' is the mean items of the non-exploded robots; kJ and net are medians (an exploded robot books an\n"
          "unbounded pre-explosion work bill, so no mean over the draw is meaningful); 'boom' counts the exploded.\n")
    header = f"{'items':>5} {'items/m2':>8} | {'pop':9} {'ate':>5} {'kJ':>6} {'net':>7} {'solvent':>8} {'of 60':>6} {'dead by':>8} {'boom':>4}"
    print(header)
    print("-" * len(header))
    for items in densities:
        density = items / (np.pi * RADIUS**2)
        draw = founder_draw(groups, items)
        row = {"items": items, "density": density}
        for kind in ("holistic", "pioneer"):
            ate, kJ, blown = draw[kind]["items"], draw[kind]["kJ"], draw[kind]["exploded"]
            net = ate - WORK_COST * kJ - BASAL
            # An exploded robot books its pre-explosion work, which can be astronomical, so every
            # summary here is a median over the draw and the means are not quoted.  Exploded robots
            # count as insolvent, which is what they are: the work bill kills them in season 0.
            solvent = float(((net > 0) & ~blown).mean())
            ok = ~blown
            # a founder that eats nothing pays basal plus its own work and starts with INITIAL_ENERGY
            idle_burn = BASAL + WORK_COST * float(np.median(kJ[ok]))
            row[kind] = {
                "ate_median": float(np.median(ate[ok])), "ate_mean_ok": float(ate[ok].mean()), "kJ_median": float(np.median(kJ[ok])),
                "net_median": float(np.median(net[ok])), "exploded": int(blown.sum()),
                "solvent_frac": solvent, "solvent_of_60": solvent * 60, "idle_seasons": INITIAL_ENERGY / idle_burn,
                "newborn_seasons": BIRTH_COST / idle_burn,
            }
            print(f"{items:5d} {density:8.3f} | {kind:9} {ate[ok].mean():5.2f} {np.median(kJ[ok]):6.2f} {np.median(net[ok]):+7.2f}"
                  f" {solvent:8.0%} {solvent * 60:6.1f} {INITIAL_ENERGY / idle_burn:8.1f} {int(blown.sum()):4d}", flush=True)
        # The upper wall: what the baseline's evolved mower would net here.  Solo, and again at the
        # realised yield of a shared arena -- RBT-21 measured the baseline's founder lump at 0.385
        # items against its solo probe's 0.50, so a solo probe overstates an ecology yield by ~1.30.
        for label, share in (("alone", 1.0), ("in a group of four", SHARED_ARENA)):
            mower_items = MOWER_ITEMS_AT_12 * items / 12.0 * share
            mower_net = mower_items - WORK_COST * MOWER_KJ - BASAL
            key = "blind_mower_solo" if share == 1.0 else "blind_mower_shared"
            row[key] = {"items": mower_items, "net": mower_net, "recruit_seasons": (BIRTH_THRESHOLD - BIRTH_COST) / mower_net if mower_net > 0 else None}
            note = "mowing pays" if mower_net > 0.5 else ("mowing marginal" if mower_net > 0 else "mowing loses")
            recruit = f", a child of one breeds after {(BIRTH_THRESHOLD - BIRTH_COST) / mower_net:.0f} seasons" if mower_net > 0 else ""
            print(f"{'':5} {'':8} | evolved blind mower {label:18}: {mower_items:4.2f} items, net {mower_net:+.2f} -> {note}{recruit}")
        print()
        out[items] = row
    return out


if __name__ == "__main__":
    groups = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    densities = tuple(int(x) for x in sys.argv[2].split(",")) if len(sys.argv) > 2 else DENSITIES
    res = report(groups, densities)
    json.dump({str(k): {kk: (vv if not isinstance(vv, dict) else vv) for kk, vv in v.items()} for k, v in res.items()}, open("density_window.json", "w"), indent=2, default=float)
    print("wrote density_window.json")
