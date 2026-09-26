"""RBT-103: does the routed compass pay on a population it did not come from?

RBT-97 established that the routed motif -- RBT-87's, through a global tanh interneuron, the
circuit the genotype can actually represent -- pays on W4b-801 and P-801, and that on P-801
the gain is food-dependent. Both are the populations the compass question came from. RBT-84
showed that "regularities" here can be founding-population properties, so whether the prize
belongs to this world or to those two lineages is open.

This is `runs/RBT-97/routed_p801.py` generalised from the two committed populations to any run
directory, so RBT-90 part 2's ten seeds can be read with the same instrument that produced the
numbers they are compared against. Pointed at `runs/RBT-19/P-801` it IS that instrument, which
is the positive control: it must return RBT-97's +0.969 and +3.018 before any new body counts.

Three things it does that the RBT-97 script did not have to:

* **the direction probe is run both ways.** The tree holds two direction instruments and they
  are not the same: `travel_direction_check.py` (seeds 7000+, every tenth tick, centre of
  mass, no break on explode) is the one that produced the committed table, and
  `travel_direction.py` samples every tick from the root body on seeds 9000+. They agree on
  every classification on P-801 and disagree on R. A body they disagree about is UNDETERMINED
  and leaves both the numerator and the denominator, rather than being signed on a coin flip.
* **the install is read back.** A routed motif's nose-to-Effector path is length two, so the
  depth-1 steering term is 0.0 by construction (RBT-87); the analogue is
  `steering_terms(ph, depth=2)["path"]["a"]`, which must read the installed 2w. An install
  that did not land is not a null, and this is what tells the two apart.
* **the body plan is checked before anything is installed.** The motif needs a food sensor and
  an effector on each of two wheel nodes. Evolved (holistic) morphologies do not have that --
  on RBT-90's seeds the holistic champion raises StopIteration here -- so a body that cannot
  carry the circuit is reported as such and never scored.

Usage:
  routed_populations.py --run runs/RBT-19/P-801                     # the positive control
  routed_populations.py --run runs/RBT-90/forage-805 --label 805
"""
import argparse
import importlib.util
import json
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


routed = _load("rbt97_routed", os.path.join(_ROOT, "runs", "RBT-97", "routed_p801.py"))
g500 = _load("rbt97_g500", os.path.join(_ROOT, "runs", "RBT-97", "g500_direction.py"))
mech = routed.mech

from rabbitstew.analysis import steering_terms  # noqa: E402
from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig, Simulation, spawn_layout  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402

#: the body rule, fixed on the ticket before any body was read
GENS = (0, 100, 200, 300, 400, 500, 590)
RUN = {}


def config(run):
    return SimConfig.from_dict(json.load(open(f"{run}/config.json"))["sim"])


def genotype(run, kind, gen):
    return Genotype.load(f"{run}/{kind}/best_gen{gen:04d}.json")


def direction_bout(task):
    """One direction bout under one of the two probes. g500_direction.py's sampler."""
    run, kind, gen, i, probe = task
    P = g500.PROBES[probe]
    cfg = RUN[run]
    seed = P["seed0"] + i
    g = genotype(run, kind, gen)
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, seed))
    sim.set_food_seed(seed)
    pos_of = (lambda s_: s_.center_of_mass(0)[:2]) if P["com"] else \
             (lambda s_: s_.data.xpos[s_.robots[0].root_body][:2])
    last = np.array(pos_of(sim), dtype=float).copy()
    out = []
    for t in range(int(round(cfg.duration / cfg.control_dt))):
        sim.step()
        if P["stop_on_explode"] and sim.exploded[0]:
            break
        if t % P["every"]:
            continue
        pos = np.array(pos_of(sim), dtype=float)
        d = pos - last
        if np.linalg.norm(d) > 1e-3:
            out.append(g500.td.wrap(float(np.arctan2(d[1], d[0])) - g500.td.yaw_of(sim)))
        last = pos.copy()
    if not out:
        return gen, probe, 0.0, 0.0, 0
    o = np.array(out)
    return gen, probe, float(np.sum(np.sin(o))), float(np.sum(np.cos(o))), len(o)


def income_bout(task):
    """One income bout: base if w is 0, else the routed motif at that w and sign."""
    run, kind, gen, w, sign, seed = task
    cfg = RUN[run]
    g = genotype(run, kind, gen)
    if w:
        g = routed.install(g, w, sign=sign)
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, seed))
    sim.set_food_seed(seed)
    for _ in range(int(round(cfg.duration / cfg.control_dt))):
        sim.step()
    return gen, w, seed, float(sim.food_eaten[0]), bool(sim.exploded[0])


def path_a(g, cfg):
    """The depth-2 path term -- RBT-87's quantity for a routed motif (depth 1 reads 0 on it)."""
    terms = steering_terms(synthesize(g, cfg.synthesis), depth=2)
    return None if terms is None else float(terms["path"]["a"])


def readback(run, kind, gen, w, sign, cfg):
    """(installed a, the body's own a before the install).

    The install is the DIFFERENCE, not the total. Bodies carry evolved nose-to-Effector wiring
    of their own -- RBT-67 prints it as "evolved a before install", and on P-801 it is -0.56 on
    g400, -0.59 on g590 and non-zero on g500 -- so comparing the total against 2w voids exactly
    the bodies whose brains already steer on smell. An earlier version of this function did
    that and called three of seven P-801 bodies void while they were returning RBT-97's income
    numbers to the digit; the positive control is what caught it.
    """
    g0 = genotype(run, kind, gen)
    before = path_a(g0, cfg)
    after = path_a(routed.install(g0, w, sign=sign), cfg)
    if before is None or after is None:
        return None, None
    return after - before, before


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run", required=True)
    p.add_argument("--config-from", default=None, dest="config_from",
                   help="take the WORLD from this run's config.json while keeping --run's bodies; "
                        "this is the world control -- RBT-90's world has 12 items on random "
                        "terrain, P-801's has 26 in three patches on flat, so a population "
                        "difference and a world difference are otherwise confounded")
    p.add_argument("--kind", default="conventional")
    p.add_argument("--gens", default=None,
                   help="override the committed body rule; W4b-801's bests are at 90..590, not "
                        "0..590, so the world control needs it. Any override is printed.")
    p.add_argument("--label", default=None)
    p.add_argument("--w", default="16,32")
    p.add_argument("--seeds", type=int, default=64)
    p.add_argument("--seed0", type=int, default=7000)
    p.add_argument("--procs", type=int, default=4)
    args = p.parse_args()

    run, kind = args.run.rstrip("/"), args.kind
    gens_rule = GENS if not args.gens else tuple(int(x) for x in args.gens.split(","))
    label = args.label or os.path.basename(run)
    ws = [float(x) for x in args.w.split(",")]
    seeds = [args.seed0 + i for i in range(args.seeds)]
    cfg = config(args.config_from) if args.config_from else config(run)
    RUN[run] = cfg

    print(f"# RBT-103: does the routed compass pay on {label}?")
    print(f"{run}/{kind}, bests {list(gens_rule)}"
          + ("" if not args.gens else " (--gens OVERRIDE of the committed rule)")
          + " (the rule fixed on the ticket before any body was read)")
    if args.config_from:
        print(f"WORLD CONTROL: bodies from {run}, world from {args.config_from}/config.json")
    print(f"world: {cfg.food.items} items, radius {cfg.food.radius:g}, patches {cfg.food.patches}, "
          f"regrow {cfg.food.regrow}, decay {cfg.food.decay:g}, duration {cfg.duration:g}s, "
          f"random_start {cfg.random_start}")
    print(f"{args.seeds} paired seeds from {seeds[0]}; w = {[int(w) for w in ws]} (a = 2w)\n")

    # --- the body plan, before anything is installed
    bodies, unusable, missing = [], [], []
    for gen in gens_rule:
        path = f"{run}/{kind}/best_gen{gen:04d}.json"
        if not os.path.exists(path):
            # a file that is not there is not a body plan that cannot carry the circuit, and an
            # earlier version of this script reported it as one
            missing.append(gen)
            continue
        try:
            routed.unit_indices(genotype(run, kind, gen))
            bodies.append(gen)
        except Exception as e:  # noqa: BLE001 -- the point is to report, not to raise
            unusable.append((gen, f"{type(e).__name__}: {e}" if str(e) else type(e).__name__))
    if missing:
        print(f"## STOPPING: no best_gen file for {', '.join('g' + str(g) for g in missing)} in "
              f"{run}/{kind}")
        print("   That is a wrong --gens for this run, not a result. Nothing is scored.")
        return
    print(f"## Body plan: {len(bodies)} of {len(gens_rule)} bests can carry the circuit")
    if unusable:
        for gen, why in unusable:
            print(f"  g{gen}: CANNOT CARRY IT -- {why}")
        print("  A body with no food sensor on each of two wheel nodes has no pair of noses to")
        print("  take a difference between. It is not scored and it is not a null.")
    if not bodies:
        print("\nNo body can carry the motif; nothing to score.")
        return

    # --- direction, both probes
    tasks = [(run, kind, gen, i, k) for k in g500.PROBES for gen in bodies for i in range(16)]
    with get_context("fork").Pool(args.procs) as pool:
        rows = pool.map(direction_bout, tasks, chunksize=4)
    by = {}
    for r in rows:
        by.setdefault((r[1], r[0]), []).append(r[2:])
    print(f"\n## Direction of travel, both probes ({', '.join(g500.PROBES)})")
    print(f"{'gen':>6s} | " + " | ".join(f"{'probe ' + k:>22s}" for k in g500.PROBES)
          + " | sign | agree")
    sign, undetermined = {}, []
    for gen in bodies:
        cells, backs = [], []
        for k in g500.PROBES:
            sn = sum(x[0] for x in by[(k, gen)])
            cs = sum(x[1] for x in by[(k, gen)])
            n = sum(x[2] for x in by[(k, gen)])
            deg = float(np.degrees(np.arctan2(sn / n, cs / n))) if n else float("nan")
            R = float(np.hypot(sn / n, cs / n)) if n else 0.0
            cells.append(f"{deg:+8.1f}° R={R:5.3f}")
            backs.append(abs(deg) > 90 if n else None)
        agree = backs[0] is not None and backs[0] == backs[1]
        if not agree:
            undetermined.append(gen)
            s = float("nan")
        else:
            s = +1.0 if backs[0] == mech.rs.PUBLISHED_IS_BACKWARD else -1.0
            sign[gen] = s
        print(f"g{gen:<5d} | " + " | ".join(f"{c:>22s}" for c in cells)
              + f" | {'--' if not agree else f'{s:+.0f}'} | {'yes' if agree else 'NO -> UNDETERMINED'}")
    if undetermined:
        print(f"  {len(undetermined)} body(ies) undetermined: the two probes disagree about which way")
        print("  they drive, so the compass has no defined sign on them. Out of the numerator AND")
        print("  the denominator, per the pre-registration.")
    scored = [g for g in bodies if g in sign]
    if not scored:
        print("\nNo body has a determined sign; this population is NOT READABLE, not a null.")
        return

    # --- the install, read back before it is scored
    print(f"\n## Install readback: the CHANGE in the depth-2 path a, which must equal the")
    print("   installed 2w (RBT-87). The body's own term before the install is printed beside")
    print("   it, because the total is the sum of the two and only the change is the install.")
    print(f"{'gen':>6s} {'own a':>9s} | " + " | ".join(f"{'w=' + str(int(w)):>20s}" for w in ws))
    bad = []
    for gen in scored:
        cells, own = [], None
        for w in ws:
            got, own = readback(run, kind, gen, w, sign[gen], cfg)
            want = sign[gen] * 2 * w
            ok = got is not None and abs(got - want) < 1e-6
            cells.append(f"{got:+10.4f} vs {want:+6.1f}" if got is not None else "     none")
            if not ok:
                bad.append((gen, w, got, want))
        print(f"g{gen:<5d} {own if own is not None else float('nan'):+9.4f} | "
              + " | ".join(f"{c:>20s}" for c in cells))
    if bad:
        print("  READBACK FAILED on: " + ", ".join(f"g{g} w={w:g}" for g, w, _, _ in bad))
        print("  An install that did not land is not a null; those cells are void.")
    else:
        print("  every install lands exactly on its 2w")

    # --- income
    tasks = [(run, kind, gen, 0.0, 0.0, s) for gen in scored for s in seeds]
    tasks += [(run, kind, gen, w, sign[gen], s) for gen in scored for w in ws for s in seeds]
    with get_context("fork").Pool(args.procs) as pool:
        rows = pool.map(income_bout, tasks, chunksize=16)
    got = {(r[0], r[1], r[2]): r[3] for r in rows}
    blew = {(r[0], r[1], r[2]): r[4] for r in rows}
    base = {(gen, s): got[(gen, 0.0, s)] for gen in scored for s in seeds}

    print(f"\n## Income: the motif against each body's own baseline, {args.seeds} paired seeds")
    print(f"{'gen':>6s} {'sign':>5s} {'base':>8s} | "
          + " | ".join(f"{'w=' + str(int(w)) + ' (a=' + str(int(2 * w)) + ')':>16s}" for w in ws))
    per = {w: [] for w in ws}
    for gen in scored:
        cells = []
        for w in ws:
            d = float(np.mean([got[(gen, w, s)] - base[(gen, s)] for s in seeds]))
            per[w].append(d)
            cells.append(f"{d:+16.3f}")
        print(f"g{gen:<5d} {sign[gen]:+5.0f} {np.mean([base[(gen, s)] for s in seeds]):8.3f} | "
              + " | ".join(cells))

    print(f"\n{'w':>5s} {'a':>5s} | {'delta':>8s} {'t(df=' + str(len(scored) - 1) + ') 95%':>22s}"
          f" {'improved':>9s} {'zeros':>12s} | verdict")
    verdicts = {}
    for w in ws:
        m, lo, hi = mech.t_interval(per[w])
        z = sum(1 for gen in scored for s in seeds if got[(gen, w, s)] == base[(gen, s)])
        n = len(scored) * len(seeds)
        veto = z > n / 2
        v = ("PAYS" if lo > 0 and not veto else
             "NEGATIVE" if hi < 0 and not veto else
             "VETOED by the zero count" if veto else "unresolved at this n")
        verdicts[w] = v
        x = sum(1 for gen in scored for s in seeds if blew[(gen, w, s)])
        xb = sum(1 for gen in scored for s in seeds if blew[(gen, 0.0, s)])
        print(f"{w:5.0f} {2 * w:5.0f} | {m:+8.3f} [{lo:+9.3f}, {hi:+9.3f}] "
              f"{sum(1 for d in per[w] if d > 0):>5d}/{len(per[w])} {z:>6d}/{n} | {v}"
              f"   (exploded {x}/{n}, base {xb}/{n})")

    print(f"\nPre-registered rules: PAYS if the t(df = n-1) interval over bodies excludes zero from")
    print("above and RBT-38's zero-count veto passes; NEGATIVE if it excludes zero from below;")
    print("unresolved at this n otherwise. A population with more than two undetermined bodies is")
    print("NOT READABLE rather than null. The across-population rule is read at a = 64.")
    print(f"\nROW {label}: " + "  ".join(
        f"a={int(2 * w)} {np.mean(per[w]):+.3f} {verdicts[w]}" for w in ws)
        + f"  bodies {len(scored)}/{len(gens_rule)}"
        + (f"  undetermined {len(undetermined)}" if undetermined else "")
        + (f"  unusable {len(unusable)}" if unusable else ""))


if __name__ == "__main__":
    main()
