"""RBT-97: does the compass gain depend on where the food actually is?

`scripts/compass_mechanism.py` answered that on W4b-801 and is hard-coded to it: one
population, one sign, one magnitude, and the four motif weights typed out by hand. RBT-67
then measured the gain on P-801 as well and said so in its own pre-registration: the
manipulation check was *"not run in this harness"*, and whether the robot is still aiming at
food at high `a` is *"an open question this package does not answer"*. On P-801 the yield
numbers are compatible with chemotaxis and with a gait effect -- in-disc path falls 4.55 to
4.05 m while items per in-disc metre rises 0.615 to 1.783, and rail% reaches 14.7% at
a = 384 -- so until the decoy control is run there, "pays" means yield and not chemotaxis.

This is that script generalised over population, sign and magnitude, with two changes:

* **the sign is set per ROBOT, not per population.** RBT-69's standing rule is that
  direction of travel belongs to the individual. P-801's g100 (+177.2 deg) and g400
  (+165.1 deg) drive backward inside a forward-driving population, so RBT-67's
  population sign gave those two an ANTI-compass at every rung. Here each robot gets its
  own, and the two inverted ones are kept and reported as the in-sample sign control.
* **the four weights are never typed out.** They come from `compass_replication.install`,
  which derives them from `fixed.drive_commands`, exactly as RBT-67 installed them. The
  magnitude is quoted in RBT-67's units: `a = 2k`, so the hard-coded `W = 32` of the
  original is `a = 64` here.

Conditions, unchanged from the original:

* ``base``      -- the robot as evolved.
* ``motif``     -- the compass for THIS robot's direction of travel.
* ``phantom``   -- the same install, but the food sensors smell a decoy layout drawn from a
  different seed while the real items stay where they are and stay edible. Same item count,
  same decay, same spatial statistics, no correlation with the food actually present. **If
  the gain survives this, it is not a food-direction circuit.**
* ``antimotif`` -- the same install inverted: the anti-compass for this robot.

`tests/test_rbt97_mechanism.py` pins the generalisation: for W4b at sign +1 and a = 64 the
installed weight matrix and the per-bout output are identical to the hard-coded script's,
which is the condition the coordinator set before this arm may run.

Usage: mechanism.py [--pop p801|w4b] [--a 64,384] [--seeds 64] [--seed0 7000]
                    [--sign per-robot|population|+1|-1] [--procs 4] [--conds ...]
"""
import argparse
import importlib.util
import json
import os
import sys
from dataclasses import replace

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


cr = _load("compass_replication", os.path.join(_ROOT, "scripts", "compass_replication.py"))
cm = _load("compass_mechanism", os.path.join(_ROOT, "scripts", "compass_mechanism.py"))
#: RBT-67's own population table, imported rather than restated: run dir, gens, population sign.
cds = _load("compass_dose_response",
            os.path.join(_ROOT, "docs", "artifacts", "RBT-67", "compass_dose_response.py"))
rs = _load("resign_rbt67", os.path.join(_HERE, "resign_rbt67.py"))

from rabbitstew.simulation import SimConfig, Simulation, spawn_layout  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402

CFG = {}      #: pop -> SimConfig, filled by main() before the fork pool starts
SIGN = {}     #: (pop, gen) -> +1 / -1, the sign installed on that robot
DECOY_OFFSET = 5000  #: the original's decoy seed offset, kept so the test can compare


def travel_table(pop):
    """Per-generation travel offsets, parsed from the committed readouts.

    Two formats, because the two populations were measured by different scripts:
    RBT-69's `gen  100: offset   +177.2 deg` and W4b's `| 90 | -179.0 | 0.678 |` table.
    The parse is checked against `resign_rbt67.TRAVEL`, which is what §1's per-robot
    re-signing used, so the two readings cannot drift apart silently.
    """
    import re
    if pop == "p801":
        path = os.path.join(_ROOT, "docs", "runs", "RBT-69-travel-direction.txt")
        pat = re.compile(r"^\s*gen\s+(\d+):\s*offset\s+([-+][\d.]+)\s*deg")
    else:
        path = os.path.join(_ROOT, "docs", "artifacts", "RBT-23-W4b-801", "travel_direction.txt")
        pat = re.compile(r"^\|\s*(\d+)\s*\|\s*([-+][\d.]+)\s*\|")
    out = {}
    for line in open(path):
        m = pat.match(line)
        if m:
            out[int(m.group(1))] = float(m.group(2))
    assert out == rs.TRAVEL[pop], f"{path} disagrees with resign_rbt67.TRAVEL[{pop}]"
    return out


def signs_for(pop, gens, mode):
    """The installed sign per robot. `per-robot` is this ticket's contribution."""
    if mode == "population":
        return {g: float(cds.POPULATIONS[pop]["sign"]) for g in gens}
    if mode in ("+1", "-1"):
        return {g: float(mode) for g in gens}
    travel = travel_table(pop)
    # the published motif (+1) is the compass for a BACKWARD driver (RBT-69's resolution)
    return {g: (+1.0 if (abs(travel[g]) > 90) == rs.PUBLISHED_IS_BACKWARD else -1.0) for g in gens}


def ascent_bearing(pos, live, decay):
    """Bearing of steepest ascent of sum_i exp(-d_i/decay) at `pos`.

    `scripts/compass_mechanism.py`'s function with the decay passed in rather than read from
    a module global, because the two populations' configs differ. The squash is monotone, so
    it cannot change the direction.
    """
    d = live - pos
    r = np.linalg.norm(d, axis=1)
    ok = r > 1e-9
    if not ok.any():
        return None
    wgt = (np.exp(-r[ok] / decay) / r[ok])[:, None]
    g = (wgt * d[ok]).sum(axis=0)
    if np.linalg.norm(g) < 1e-12:
        return None
    return float(np.arctan2(g[1], g[0]))


def bout(task):
    """One bout. Returns (pop, gen, a, seed, cond, bearings..., items)."""
    pop, gen, a, seed, cond = task
    cfg = CFG[pop]
    decay = cfg.food.decay if cfg.food is not None else 1.0
    g = cds.genotype(pop, gen)
    ph = synthesize(g, cfg.synthesis)
    sim = cm.DecoySmell([g], cfg, spawns=spawn_layout(1, cfg, seed))
    sim.set_food_seed(seed)
    if cond == "phantom":
        probe = Simulation([g], cfg, spawns=spawn_layout(1, cfg, seed))
        probe.set_food_seed(seed + DECOY_OFFSET)
        sim._decoy = np.array(probe.food_pos, dtype=float).reshape(-1, 2).copy()
    k = SIGN[(pop, gen)] * cds.k_of(a)
    if cond in ("motif", "phantom"):
        cr.install(sim.brains[0], ph, "compass", k)
    elif cond == "antimotif":
        cr.install(sim.brains[0], ph, "compass", -k)

    prev = cm.yaw_of(sim)
    dt = cfg.control_dt
    b_near, b_grad, al_near, al_grad = [], [], [], []
    for _ in range(int(round(cfg.duration / cfg.control_dt))):
        sim.step()
        if sim.exploded[0]:
            break
        pos = sim.data.xpos[sim.robots[0].root_body][:2]
        live = sim.food_pos[np.max(np.abs(sim.food_pos), axis=1) < cm.PARKED]
        cur = cm.yaw_of(sim)
        rate = cm.wrap(cur - prev) / dt
        prev = cur
        if len(live) == 0:
            continue
        d = live - pos
        j = int(np.argmin(np.linalg.norm(d, axis=1)))
        bn = cm.wrap(float(np.arctan2(d[j, 1], d[j, 0])) - cur)
        b_near.append(abs(bn))
        al_near.append(np.sign(bn) * rate)
        ab = ascent_bearing(pos, live, decay)
        if ab is not None:
            bg = cm.wrap(ab - cur)
            b_grad.append(abs(bg))
            al_grad.append(np.sign(bg) * rate)
    f = lambda v: float(np.mean(v)) if v else float("nan")
    return (pop, gen, a, seed, cond, f(b_near), f(b_grad), f(al_near), f(al_grad),
            float(sim.food_eaten[0]), bool(sim.exploded[0]))


def boot(vals, rng, draws=20000):
    v = np.asarray(vals, float)
    m = np.array([rng.choice(v, len(v)).mean() for _ in range(draws)])
    return float(v.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))


def calibration(pop, gens, seeds, by, a_anchor):
    """RBT-66's rule: the instrument must recover a gain it was handed, on each body.

    `base` and `motif` at the anchor rung are re-derived here from the same seeds RBT-67
    used, with the same install, so they should reproduce its committed per-robot numbers
    exactly. On a robot whose sign this arm INVERTED relative to RBT-67's population sign,
    the comparable condition is this arm's `antimotif`, which is the circuit RBT-67 actually
    installed on it -- so every robot is checked at the anchor, not just the ones the
    population sign happened to suit. A body that fails has its phantom number declared
    void, per the pre-registration.
    """
    ref = json.load(open(os.path.join(_ROOT, "docs", "artifacts", "RBT-67", f"{pop}.json")))
    cells = {float(c["a"]): {int(r["gen"]): r for r in c["robots"]} for c in ref["cells"]}
    pop_sign = float(cds.POPULATIONS[pop]["sign"])
    out = []
    for gen in gens:
        mine_b = float(np.mean([by[(gen, 0.0, s, "base")][9] for s in seeds]))
        theirs_b = float(cells[0.0][gen]["items"])
        same_sign = SIGN[(pop, gen)] == pop_sign
        mine_d = theirs_d = float("nan")
        cond = "motif" if same_sign else "antimotif"
        if a_anchor in cells:
            mine_d = float(np.mean([by[(gen, a_anchor, s, cond)][9] - by[(gen, 0.0, s, "base")][9]
                                    for s in seeds]))
            theirs_d = float(cells[a_anchor][gen]["delta"])
        ok = abs(mine_b - theirs_b) < 1e-9 and (np.isnan(mine_d) or abs(mine_d - theirs_d) < 1e-9)
        out.append((gen, mine_b, theirs_b, mine_d, theirs_d, cond, ok))
    return out


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pop", default="p801", choices=sorted(cds.POPULATIONS))
    p.add_argument("--a", default="64,384", help="steering coefficients in RBT-67's units (a = 2k)")
    p.add_argument("--seeds", type=int, default=64)
    p.add_argument("--seed0", type=int, default=cds.SEED0)
    p.add_argument("--sign", default="per-robot", choices=["per-robot", "population", "+1", "-1"])
    p.add_argument("--conds", default="base,motif,phantom,antimotif")
    p.add_argument("--procs", type=int, default=4)
    args = p.parse_args()

    pop = args.pop
    ladder = [float(x) for x in args.a.split(",")]
    conds = args.conds.split(",")
    gens = list(cds.POPULATIONS[pop]["gens"])
    seeds = [args.seed0 + i for i in range(args.seeds)]
    CFG[pop] = cds.config(pop)
    SIGN.update({(pop, g): s for g, s in signs_for(pop, gens, args.sign).items()})

    tasks = [(pop, g, 0.0, s, "base") for g in gens for s in seeds]
    tasks += [(pop, g, a, s, c) for g in gens for a in ladder for s in seeds
              for c in conds if c != "base"]
    from multiprocessing import get_context
    with get_context("fork").Pool(args.procs) as pool:
        rows = pool.map(bout, tasks, chunksize=16)
    by = {(r[1], r[2], r[3], r[4]): r for r in rows}

    cfg = CFG[pop]
    travel = travel_table(pop)
    print(f"# RBT-97: is the compass gain food-dependent on {pop}?  "
          f"{len(gens)} robots x {len(seeds)} seeds, {len(rows)} bouts")
    print(f"substrate {cds.POPULATIONS[pop]['run']}, its own committed config "
          f"({cfg.food.items} items, patches {cfg.food.patches}, regrow {cfg.food.regrow}, "
          f"smell {cfg.food.smell}, decay {cfg.food.decay})")
    print(f"seeds {seeds[0]}..{seeds[-1]}; decoy layout from seed + {DECOY_OFFSET}")
    print(f"sign mode: {args.sign}; a = 2k, installed through drive_commands()\n")
    print("sign per robot (published motif +1 is the compass for a BACKWARD driver):")
    for g in gens:
        print(f"  g{g:<4d} travel {travel[g]:+7.1f} deg  "
              f"{'BACKWARD' if abs(travel[g]) > 90 else 'forward':>8s}  "
              f"-> sign {SIGN[(pop, g)]:+.0f}  "
              f"{'(inverted vs RBT-67 population sign)' if SIGN[(pop, g)] != cds.POPULATIONS[pop]['sign'] else ''}")

    print("\n## Positive control: does this harness recover RBT-67's committed numbers?")
    anchor = ladder[0] if ladder else 64.0
    print(f"   Each robot's baseline, and its delta at a = {anchor:.0f}, against RBT-67's committed")
    print("   per-robot numbers on the same seeds. On a robot whose sign this arm inverted, the")
    print("   comparable condition is this arm's ANTImotif -- the circuit RBT-67 installed there.")
    print(f"{'gen':>6s} {'base here':>10s} {'RBT-67':>10s} | {'cond':>9s} {'delta here':>11s} "
          f"{'RBT-67':>10s} | ok")
    cal = calibration(pop, gens, seeds, by, anchor)
    for gen, mb, tb, md, td, cond, ok in cal:
        print(f"g{gen:<5d} {mb:10.4f} {tb:10.4f} | {cond:>9s} {md:11.4f} {td:10.4f} | "
              f"{'yes' if ok else 'NO -- VOID'}")
    void = {gen for gen, *_, ok in cal if not ok}

    rng = np.random.default_rng(5)
    base = {(g, s): by[(g, 0.0, s, "base")][9] for g in gens for s in seeds}
    print("\n## Per robot, per rung: items eaten against the robot's own baseline")
    print(f"{'gen':>6s} {'sign':>5s} {'a':>5s} | {'base':>7s} {'motif':>8s} {'phantom':>8s} "
          f"{'anti':>8s} | {'retained':>9s} | {'bearing near':>13s} {'bearing grad':>13s}")
    retained_rows = {}
    for a in ladder:
        for g in gens:
            d = {c: float(np.mean([by[(g, a, s, c)][9] - base[(g, s)] for s in seeds]))
                 for c in conds if c != "base"}
            frac = d["phantom"] / d["motif"] if abs(d.get("motif", 0.0)) > 1e-9 else float("nan")
            retained_rows.setdefault(a, []).append((g, d, frac))
            sub = [by[(g, a, s, "motif")] for s in seeds]
            print(f"g{g:<5d} {SIGN[(pop, g)]:+5.0f} {a:5.0f} | {np.mean([base[(g, s)] for s in seeds]):7.3f} "
                  f"{d.get('motif', float('nan')):+8.3f} {d.get('phantom', float('nan')):+8.3f} "
                  f"{d.get('antimotif', float('nan')):+8.3f} | {100 * frac:8.1f}% | "
                  f"{np.nanmean([r[5] for r in sub]):13.3f} {np.nanmean([r[6] for r in sub]):13.3f}"
                  + ("   VOID" if g in void else ""))

    print("\n## Pooled. Under per-robot signing EVERY robot carries its own compass, so there is")
    print("   no inverted group here -- that is the point of the signing. The in-sample sign")
    print("   control is the `antimotif` column, each robot's own anti-compass; and for the two")
    print("   robots RBT-67's population sign inverted, this arm's antimotif reproduces RBT-67's")
    print("   published motif number exactly (see the positive control above).")
    pop_sign = float(cds.POPULATIONS[pop]["sign"])
    keep = [g for g in gens if g not in void]
    correct = [g for g in keep if SIGN[(pop, g)] == pop_sign] if args.sign != "per-robot" else \
              [g for g in keep if SIGN[(pop, g)] == (+1.0 if abs(travel[g]) > 90 else -1.0)]
    inverted = [g for g in keep if g not in correct]
    for a in ladder:
        rows_a = {g: d for g, d, _ in retained_rows[a]}
        for label, group in (("compass", correct), ("inverted", inverted)):
            if not group:
                continue
            print(f"\n  a = {a:.0f}, {label} (n = {len(group)}): " + ", ".join(f"g{g}" for g in group))
            for c in conds:
                if c == "base":
                    continue
                m, lo, hi = boot([rows_a[g][c] for g in group], rng)
                print(f"    {c:10s} {m:+8.3f} [{lo:+7.3f}, {hi:+7.3f}]  "
                      f"{sum(1 for g in group if rows_a[g][c] > 0)}/{len(group)} improved")
            md = [rows_a[g]["motif"] for g in group]
            pd_ = [rows_a[g]["phantom"] for g in group]
            diff, dlo, dhi = boot([m - p_ for m, p_ in zip(md, pd_)], rng)
            frac = float(np.mean(pd_)) / float(np.mean(md)) if abs(np.mean(md)) > 1e-9 else float("nan")
            print(f"    motif - phantom {diff:+8.3f} [{dlo:+7.3f}, {dhi:+7.3f}]; "
                  f"phantom retains {100 * frac:.1f}% of the motif's gain")
            if label == "compass":
                verdict = ("FOOD-DEPENDENT" if frac < 0.25 and dlo > 0 else
                           "GAIT EFFECT" if frac >= 0.75 and (dlo > 0) == (dhi > 0) else
                           "UNRESOLVED at this n")
                print(f"    verdict at a = {a:.0f}: {verdict}   "
                      f"(pre-registered: food-dependent if retained < 25% and the "
                      f"motif-minus-phantom CI excludes zero)")

    print("\n## Zero-count veto (RBT-38): an effect is not real if the manipulation moves")
    print("   nothing on more than half the seeds.")
    for a in ladder:
        for c in conds:
            if c == "base":
                continue
            z = sum(1 for g in keep for s in seeds if by[(g, a, s, c)][9] == base[(g, s)])
            n = len(keep) * len(seeds)
            print(f"  a = {a:5.0f}  {c:10s} unmoved on {z}/{n} bouts"
                  + ("   VETO" if z > n / 2 else ""))


if __name__ == "__main__":
    main()
