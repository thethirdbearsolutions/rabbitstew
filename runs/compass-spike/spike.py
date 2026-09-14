"""Would a hand-built Braitenberg compass actually earn anything in this world?

RBT-45 established what the *search* does: the crossed pairing is proposed in about
1% of realistic lineages, and at the default operator it can never get much above
15% because drift eats the global brain the circuit has to route through. That says
nothing about whether the circuit would be *worth* having. Ten world arms failed to
make sensing pay, and every nose that looked useful has evaporated under a proper
lesion. So before anyone spends a 600-season run widening the operator, the cheap
question is:

    if a Pioneer simply HAD the circuit, would it eat more?

This needs the world but not evolution -- no selection, no seasons, no breeding. An
evolved mower is taken as-is, the compass is installed by hand directly into the
live weight matrix (`W[dst, src]`, exactly where `brake_or_compass.py` blanks), and
the same robot is run with and without it on the same food layout and the same start.

The spike is deliberately **generous to the compass**: both signs, five magnitudes
spanning subtle to dominant, and the best variant is allowed to be chosen. To keep
that generosity from manufacturing a winner, the seeds are split -- the variant is
chosen on the first half and its effect reported on the held-out half.

Controls, because "adding drive" is not the same as "adding a compass":
  - blanked  : food and agent sensors zeroed, the standard reference
  - uncrossed: same links, nose to its OWN wheel -- wiring that is not a compass
  - sham     : same magnitudes, crossed, but sourced from the wheels' joint_velocity
               sensors instead of their noses -- drive with no smell in it

Standing rules honoured: 64 PAIRED seeds, never 8-16 (RBT-38/39); individuals are
the unit of analysis and intervals bootstrap over robots, not bouts (RBT-45 §6.5).

No library changes. Usage: python runs/compass-spike/spike.py [--seeds 64]
"""

from __future__ import annotations

import argparse
import json
import os
from dataclasses import replace
from multiprocessing import Pool

import numpy as np

from rabbitstew.genotype import Genotype
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout
from rabbitstew.synthesis import synthesize

RUN = "runs/RBT-23/W4b-801"
GENS = (90, 190, 290, 390, 490, 550, 590)
MAGS = (0.5, 1.0, 2.0, 4.0, 8.0)
SEED0 = 9000

_CFG = None


def cfg():
    global _CFG
    if _CFG is None:
        _CFG = SimConfig.from_dict(json.load(open(f"{RUN}/config.json"))["sim"])
    return _CFG


def wiring(gen):
    """Phenotype indices of the two wheel noses, their joint_velocity sensors, and their effectors."""
    ph = synthesize(Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json"), cfg().synthesis)
    nose, jv, eff = {}, {}, {}
    for i, u in enumerate(ph.units):
        if u.part in (1, 2) and u.unit.kind == "sensor" and u.unit.source == "food":
            nose[u.part] = i
        if u.part in (1, 2) and u.unit.kind == "sensor" and u.unit.source == "joint_velocity":
            jv[u.part] = i
        if u.part in (1, 2) and u.unit.kind == "effector":
            eff[u.part] = i
    blank = [i for i, u in enumerate(ph.units)
             if u.unit.kind == "sensor" and u.unit.source in ("food", "agent")]
    return nose, jv, eff, blank


def conditions():
    out = [("baseline", None, 0.0), ("blanked", None, 0.0)]
    for fam in ("crossed", "uncrossed", "sham"):
        for m in MAGS:
            for sgn in (+1, -1):
                out.append((fam, sgn, m))
    return out


def label(c):
    fam, sgn, m = c
    return fam if sgn is None else f"{fam}{'+' if sgn > 0 else '-'}{m}"


def bout(task):
    gen, seed, cond = task
    fam, sgn, m = cond
    c = replace(cfg(), random_start=True)
    g = Genotype.load(f"{RUN}/conventional/best_gen{gen:04d}.json")
    sim = Simulation([g], c, spawns=spawn_layout(1, c, seed))
    sim.set_food_seed(seed)
    nose, jv, eff, blank = wiring(gen)
    W = sim.brains[0].W
    if fam == "blanked":
        for i in blank:
            W[:, i] = 0
    elif fam == "crossed":                      # nose on one wheel drives the OTHER wheel
        W[eff[2], nose[1]] += sgn * m
        W[eff[1], nose[2]] += sgn * m
    elif fam == "uncrossed":                    # nose drives its own wheel
        W[eff[1], nose[1]] += sgn * m
        W[eff[2], nose[2]] += sgn * m
    elif fam == "sham":                         # crossed, but carrying no smell
        W[eff[2], jv[1]] += sgn * m
        W[eff[1], jv[2]] += sgn * m

    disc = c.food.radius
    steps = int(round(c.duration / c.control_dt))
    last = sim.center_of_mass(0)[:2].copy()
    in_ticks = in_path = 0.0
    near = []
    for _ in range(steps):
        sim.step()
        p = sim.center_of_mass(0)[:2]
        r = float(np.linalg.norm(p))
        in_path += float(np.linalg.norm(p - last)) if r <= disc else 0.0
        last = p.copy()
        if r <= disc:
            in_ticks += 1
            live = sim.food_pos[sim.food_alive] if len(sim.food_alive) else sim.food_pos
            if len(live):
                near.append(float(np.linalg.norm(live - p, axis=1).min()))
    food = float(sim.food_eaten[0])
    return {
        "gen": gen, "seed": seed, "cond": label(cond),
        "food": food,
        "in_disc": in_ticks / steps,
        "in_path": in_path,
        "items_per_m": food / in_path if in_path > 0.05 else 0.0,
        "near": float(np.mean(near)) if near else float("nan"),
        "exploded": bool(sim.exploded[0]),
    }


def paired(rows, cond, gens, seeds):
    """Mean (cond - baseline) per robot, on the given seeds."""
    base = {(r["gen"], r["seed"]): r for r in rows if r["cond"] == "baseline"}
    per_robot = []
    for g in gens:
        d = [rows_by[(g, s, cond)]["food"] - base[(g, s)]["food"]
             for s in seeds if (g, s, cond) in rows_by and (g, s) in base]
        if d:
            per_robot.append(float(np.mean(d)))
    return per_robot


def boot_ci(v, draws=20000, seed=3):
    rng = np.random.default_rng(seed)
    v = np.asarray(v, float)
    m = np.array([rng.choice(v, len(v)).mean() for _ in range(draws)])
    return float(v.mean()), (float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))), float((m <= 0).mean())


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=64)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    seeds = [SEED0 + i for i in range(args.seeds)]
    pick_seeds, hold_seeds = seeds[: args.seeds // 2], seeds[args.seeds // 2:]
    conds = conditions()
    tasks = [(g, s, c) for g in GENS for s in seeds for c in conds]
    print(f"{len(GENS)} robots x {len(seeds)} paired seeds x {len(conds)} conditions = {len(tasks)} bouts", flush=True)

    import time
    t0 = time.time()
    with Pool(args.workers) as p:
        rows = p.map(bout, tasks, chunksize=8)
    print(f"done in {time.time() - t0:.0f}s", flush=True)

    rows_by = {(r["gen"], r["seed"], r["cond"]): r for r in rows}
    out = {"run": RUN, "gens": list(GENS), "seeds": seeds, "rows": rows,
           "pick_seeds": pick_seeds, "hold_seeds": hold_seeds}

    print(f"\nbaseline solo yield, {len(seeds)} seeds:")
    base_by_gen = {}
    for g in GENS:
        v = [rows_by[(g, s, "baseline")]["food"] for s in seeds]
        base_by_gen[g] = float(np.mean(v))
        print(f"  gen {g}: {np.mean(v):.2f} items")
    print(f"  mean across robots: {np.mean(list(base_by_gen.values())):.2f}")

    ex = {}
    for c in conds:
        v = [rows_by[(g, s, label(c))]["exploded"] for g in GENS for s in seeds]
        ex[label(c)] = sum(v) / len(v)

    print(f"\nall conditions, paired vs baseline, all {len(seeds)} seeds "
          f"(mean items gained per bout, bootstrapped over the {len(GENS)} robots):\n")
    print("| condition | Δ items | 95% CI | P(Δ≤0) | Δ items/m | Δ near-dist | exploded |")
    print("|---|---|---|---|---|---|---|")
    summary = {}
    for c in conds:
        lab = label(c)
        if lab == "baseline":
            continue
        d = paired(rows, lab, GENS, seeds)
        m, ci, pneg = boot_ci(d)
        dm = np.mean([np.mean([rows_by[(g, s, lab)]["items_per_m"] - rows_by[(g, s, "baseline")]["items_per_m"]
                               for s in seeds]) for g in GENS])
        dn = np.mean([np.nanmean([rows_by[(g, s, lab)]["near"] - rows_by[(g, s, "baseline")]["near"]
                                  for s in seeds]) for g in GENS])
        summary[lab] = {"delta": m, "ci": ci, "p_le_0": pneg, "d_items_per_m": float(dm),
                        "d_near": float(dn), "exploded": ex[lab]}
        print(f"| {lab} | {m:+.3f} | [{ci[0]:+.3f}, {ci[1]:+.3f}] | {pneg:.3f} | {dm:+.4f} | {dn:+.3f} m | {100*ex[lab]:.0f}% |")

    # honest selection: choose the best crossed variant on pick_seeds, report on hold_seeds
    print(f"\nheld-out test: best CROSSED variant chosen on {len(pick_seeds)} seeds, "
          f"reported on the {len(hold_seeds)} it never saw\n")
    crossed = [label(c) for c in conds if c[0] == "crossed"]
    picked = max(crossed, key=lambda lab: np.mean(paired(rows, lab, GENS, pick_seeds)))
    for name, group in (("chosen on pick half", pick_seeds), ("HELD OUT", hold_seeds)):
        d = paired(rows, picked, GENS, group)
        m, ci, pneg = boot_ci(d)
        print(f"  {picked:14s} {name:20s} Δ = {m:+.3f} items  95% CI [{ci[0]:+.3f}, {ci[1]:+.3f}]  P(Δ≤0) = {pneg:.3f}")
    out["picked_crossed"] = picked
    d_hold = paired(rows, picked, GENS, hold_seeds)
    m, ci, pneg = boot_ci(d_hold)
    out["held_out"] = {"variant": picked, "delta": m, "ci": list(ci), "p_le_0": pneg,
                       "per_robot": d_hold}
    out["summary"] = summary
    out["baseline_by_gen"] = base_by_gen

    with open("runs/compass-spike/spike.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"\nper-robot held-out Δ: {[round(x, 2) for x in d_hold]}")
    print("wrote runs/compass-spike/spike.json")
