"""RBT-97 item 5: the ROUTED motif on P-801 -- the circuit the genotype can actually build.

The RBT-97 adversary's qualification 4, which is correct and which I had not noticed. Every
number this ticket leaned on for P-801 -- RBT-67's ladder, and my own arm -- installs the
**direct** four-link motif into the runtime weight matrix. `scripts/genotype_motif.py` proves
that circuit is not genotype-representable: the two wheels are siblings rather than
neighbours, so `nose on wheel 1 -> effector on wheel 2` is rejected by the validator, and the
motif drift could actually propose is the ROUTED one, through a global tanh interneuron
(RBT-87). On W4b the two agree to within 2% (+0.277 routed against +0.246 direct at w = 16,
+0.879 against +0.897 at w = 32, `docs/artifacts/RBT-23-W4b-801/genotype_motif.txt`).

**On P-801 the routed motif had never been run.** So "the magnitude drift never reaches is one
that demonstrably pays" was shown on W4b for a circuit drift can build, and on P-801 only for
one it cannot. This closes that gap.

Two generalisations of `scripts/genotype_motif.py`, which is hard-coded to W4b:

* the run directory, because its `runs/RBT-23/W4b-801` is not committed (RBT-68) while
  `docs/artifacts/RBT-23-W4b-801` is;
* the wheel-node unit indices, which it pins as `NOSE, EFF = 2, 0`. Here they are resolved by
  unit kind and source, and **asserted to equal (2, 0) on both populations**, so the committed
  W4b numbers still reproduce and a body whose brain is laid out differently cannot be
  silently mis-wired.

The sign is set PER ROBOT from the committed travel readouts, as everywhere else on this
ticket. Pre-registered rule, posted before this ran: the motif **pays** at a rung if the mean
paired delta over the seven robots has a t(df = 6) 95% interval excluding zero.

Usage: routed_p801.py [--pop p801|w4b] [--w 16,32] [--seeds 64] [--seed0 7000] [--procs 4]
  The W4b control reproduces `genotype_motif.txt`: routed_p801.py --pop w4b --seed0 9000
"""
import argparse
import importlib.util
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


mech = _load("rbt97_mechanism", os.path.join(_HERE, "mechanism.py"))
cds, rs = mech.cds, mech.rs

from rabbitstew.genotype import Brain, Genotype, Link, Neuron, UnitRef  # noqa: E402
from rabbitstew.simulation import Simulation, spawn_layout  # noqa: E402

import copy  # noqa: E402

WHEELS = (1, 2)
PINNED = (2, 0)  #: scripts/genotype_motif.py's hard-coded (NOSE, EFF); asserted, not assumed
CFG = {}
SIGN = {}


def unit_indices(g):
    """(nose, effector) index inside each wheel node's brain, resolved by kind."""
    out = []
    for nd in WHEELS:
        units = g.nodes[nd].segment.brain.units
        nose = next(i for i, u in enumerate(units)
                    if type(u).__name__ == "Sensor" and getattr(u, "source", None) == "food")
        eff = next(i for i, u in enumerate(units) if type(u).__name__ == "Effector")
        out.append((nose, eff))
    assert out[0] == out[1], f"the two wheels disagree on their brain layout: {out}"
    assert out[0] == PINNED, (
        f"wheel brain layout {out[0]} is not scripts/genotype_motif.py's hard-coded {PINNED}; "
        "its committed numbers would not be comparable")
    return out[0]


def install(g, w, sign=+1.0):
    """RBT-87's routed motif, in the GENOTYPE. `scripts/genotype_motif.py`'s function with the
    unit indices resolved rather than pinned; the wiring and the validate() call are its own."""
    nose, eff = unit_indices(g)
    r = copy.deepcopy(g)
    if r.global_brain is None:
        r.global_brain = Brain()
    gb = r.global_brain
    gb.units.append(Neuron(bias=0.0, func="tanh"))
    k = len(gb.units) - 1
    gb.links.append(Link(UnitRef(WHEELS[0], nose), UnitRef(None, k), +sign))
    gb.links.append(Link(UnitRef(WHEELS[1], nose), UnitRef(None, k), -sign))
    for nd in WHEELS:
        r.nodes[nd].segment.brain.links.append(Link(UnitRef(None, k), UnitRef(nd, eff), w))
    problems = r.validate()
    if problems:
        raise RuntimeError("installed motif is invalid: " + "; ".join(problems))
    return r


def bout(task):
    pop, gen, w, seed = task
    cfg = CFG[pop]
    g = cds.genotype(pop, gen)
    if w:
        g = install(g, w, sign=SIGN[(pop, gen)])
    sim = Simulation([g], cfg, spawns=spawn_layout(1, cfg, seed))
    sim.set_food_seed(seed)
    for _ in range(int(round(cfg.duration / cfg.control_dt))):
        sim.step()
    return pop, gen, w, seed, float(sim.food_eaten[0])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--pop", default="p801", choices=sorted(cds.POPULATIONS))
    p.add_argument("--w", default="16,32", help="per-link gain; a = 2w in RBT-67's units")
    p.add_argument("--seeds", type=int, default=64)
    p.add_argument("--seed0", type=int, default=cds.SEED0)
    p.add_argument("--procs", type=int, default=4)
    args = p.parse_args()

    pop = args.pop
    ws = [float(x) for x in args.w.split(",")]
    gens = list(cds.POPULATIONS[pop]["gens"])
    seeds = [args.seed0 + i for i in range(args.seeds)]
    CFG[pop] = cds.config(pop)
    SIGN.update({(pop, g): s for g, s in mech.signs_for(pop, gens, "per-robot").items()})
    travel = mech.travel_table(pop)

    tasks = [(pop, g, 0.0, s) for g in gens for s in seeds]
    tasks += [(pop, g, w, s) for g in gens for w in ws for s in seeds]
    with get_context("fork").Pool(args.procs) as pool:
        rows = pool.map(bout, tasks, chunksize=16)
    by = {(r[1], r[2], r[3]): r[4] for r in rows}

    print(f"# RBT-97 item 5: the ROUTED motif (RBT-87) on {pop}, signed per robot")
    print(f"{cds.POPULATIONS[pop]['run']}, {len(gens)} robots x {len(seeds)} seeds from "
          f"{seeds[0]}, {len(rows)} bouts, w = {[int(w) for w in ws]} (a = 2w)")
    print("wheel-brain unit indices resolved by kind and asserted equal to "
          f"scripts/genotype_motif.py's {PINNED} on every robot\n")
    base = {(g, s): by[(g, 0.0, s)] for g in gens for s in seeds}
    print(f"{'gen':>6s} {'travel':>9s} {'sign':>5s} {'base':>8s} | "
          + " | ".join(f"{'w=' + str(int(w)) + ' (a=' + str(int(2 * w)) + ')':>16s}" for w in ws))
    per = {w: [] for w in ws}
    for g in gens:
        cells = []
        for w in ws:
            d = float(np.mean([by[(g, w, s)] - base[(g, s)] for s in seeds]))
            per[w].append(d)
            cells.append(f"{d:+16.3f}")
        print(f"g{g:<5d} {travel[g]:+8.1f}° {SIGN[(pop, g)]:+5.0f} "
              f"{np.mean([base[(g, s)] for s in seeds]):8.3f} | " + " | ".join(cells))

    print(f"\n{'w':>5s} {'a':>5s} | {'delta':>8s} {'t(df=' + str(len(gens) - 1) + ') 95%':>22s}"
          f" {'improved':>9s} | verdict")
    for w in ws:
        m, lo, hi = mech.t_interval(per[w])
        pays = (lo > 0) == (hi > 0)
        print(f"{w:5.0f} {2 * w:5.0f} | {m:+8.3f} [{lo:+9.3f}, {hi:+9.3f}] "
              f"{sum(1 for d in per[w] if d > 0):>5d}/{len(per[w])} | "
              f"{'PAYS' if pays else 'not resolved at this n'}")
    print("\nPre-registered rule: pays at a rung if the mean paired delta over the robots has a")
    print("t(df = n-1) 95% interval excluding zero. The routed motif is the one the encoding")
    print("admits, so this is the circuit drift could actually propose.")


if __name__ == "__main__":
    main()
