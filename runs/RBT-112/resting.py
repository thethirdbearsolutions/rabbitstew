"""RBT-112 (and RBT-106 F12): each champion's planted-unit resting drive, beside its install control.

RBT-104's readout adversary (PR #264 §5.2, F12) found an H-specific masking route.  A planted w = 32
unit whose bias has walked puts a constant drive v * f(b) on the drive Effectors (f is the unit's
transfer function; tanh as planted).  In their probe that masked the install control completely at
b = 0.3, and on one host of two at b = 0.1.  So, per champion, this prints:
  * whether the champion carries the routed structure (RBT-91's predicate, `motif_units`);
  * the predicate unit read by persistence.py's rule (the largest own-link |a|), and its own-link |a|;
  * whether that |a| is at or above the pay32 rung (12.5236), i.e. whether it is a paying compass;
  * its bias b, its transfer function, and its output weights v_L and v_R onto the two drive Effectors;
  * its resting drive, max(|v_L|, |v_R|) * |f(b)|, and the nominal |32 tanh(b)| the ruling names.
f is the unit's own transfer function at rest (input b alone), so a re-typed unit is read correctly.  In an arm at --global-bias-sigma 0 the planted unit's bias is 0 at founding and never
steps: the crossover operator moves whole global brains, and those are frozen too.  Every carrying
champion there must therefore read b = 0 and resting drive 0.  Anything else is a fault, and it is
printed as FAULT.

Bodies: the conventional bests at --gens (default the readout window, 300, 350, ..., 590).
The install control's reading is function-pc.txt's per-body F, printed beside each row if that file is given.

Usage: resting.py --run RUN [--gens 300,350,...] [--pc RUN_OR_DIR/function-pc.txt] [--frozen]
"""
import argparse
import importlib.util
import json
import math
import os
import re
import sys

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_spec = importlib.util.spec_from_file_location("sr91", os.path.join(_ROOT, "runs", "RBT-91", "structural_rate.py"))
sr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sr)

from rabbitstew.genotype import Genotype  # noqa: E402
from rabbitstew.simulation import SimConfig  # noqa: E402
from rabbitstew.synthesis import synthesize  # noqa: E402

GENS = (300, 350, 400, 450, 500, 550, 590)
RUNG32 = 12.5236


def transfer(func, x):
    """The unit's resting activation under a constant net input x (its bias, every input at 0), per
    rabbitstew.brain's transfer functions: the fixed point for the leaky integrator, 0 for the differentiator."""
    return {"tanh": math.tanh(x), "sin": math.sin(x), "abs": math.tanh(abs(x)), "relu": math.tanh(max(x, 0.0)),
            "sign": float(np.sign(x)), "integrate": float(np.clip(2.0 * math.tanh(x), -1.0, 1.0)),
            "differentiate": 0.0}.get(func, float("nan"))


def read(ph):
    """One champion: the predicate unit with the largest own-link |a|, or None."""
    best = None
    for k in sr.motif_units(ph):
        a = sr.links_alone_a(ph, k)
        if np.isfinite(a) and (best is None or abs(a) > abs(best[1])):
            best = (k, a)
    if best is None:
        return None
    k, a = best
    left_e, right_e = sr.drive_effector_units(ph)
    w = {}
    for s, d, weight in ph.links:
        w[(s, d)] = w.get((s, d), 0.0) + weight
    vL, vR = w.get((k, left_e[0]), 0.0), w.get((k, right_e[0]), 0.0)
    u = ph.units[k].unit
    fb = transfer(u.func, u.bias)
    return dict(k=k, a=float(a), pay=abs(a) >= RUNG32, b=float(u.bias), func=u.func, vL=float(vL), vR=float(vR),
                rest=max(abs(vL), abs(vR)) * abs(fb), nominal=abs(32 * math.tanh(u.bias)))


def pc_per_body(path):
    """function-pc.txt's per-body F, by generation (the install control, one row per body)."""
    out = {}
    if path and os.path.exists(path):
        for line in open(path):
            m = re.match(r"^g(\d+)\s+[\d.]+\s+[\d.]+\s+[\d.]+\s+\|\s+([+-][\d.]+)", line)
            if m:
                out.setdefault(int(m.group(1)), float(m.group(2)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--gens", default=None)
    ap.add_argument("--pc", default=None)
    ap.add_argument("--frozen", action="store_true", help="the arm ran at --global-bias-sigma 0: a carrying champion must read b = 0")
    a = ap.parse_args()
    run = a.run.rstrip("/")
    gens = tuple(int(x) for x in a.gens.split(",")) if a.gens else GENS
    cfg = json.load(open(os.path.join(run, "config.json")))
    sim = SimConfig.from_dict(cfg["sim"])
    gbs = cfg["mutation"].get("global_bias_sigma")
    pc = pc_per_body(a.pc)
    print(f"# RBT-112 / RBT-106 F12: planted-unit resting drive per champion, {run}")
    print(f"# the run's global_bias_sigma: {gbs if gbs is not None else 'default (weight_sigma)'}; install control per body from "
          f"{a.pc if pc else '(not given)'}")
    print("| gen | structure | unit | own-link a | pays (>= 12.52) | func | bias b | v_L | v_R | resting drive max|v| |f(b)| | |32 tanh b| | install control F |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    faults, carriers, drifted = 0, 0, 0
    for gen in gens:
        g = Genotype.load(os.path.join(run, "conventional", f"best_gen{gen:04d}.json"))
        r = read(synthesize(g, sim.synthesis))
        f = f"{pc[gen]:+.3f}" if gen in pc else "-"
        if r is None:
            print(f"| {gen} | no | - | - | - | - | - | - | - | - | - | {f} |")
            continue
        carriers += r["pay"]
        drifted += r["pay"] and r["rest"] > 1.0
        fault = a.frozen and r["pay"] and r["b"] != 0.0
        faults += fault
        print(f"| {gen} | yes | {r['k']} | {r['a']:+.3f} | {'yes' if r['pay'] else 'no'} | {r['func']} | {r['b']:+.4f} | {r['vL']:+.3f} | "
              f"{r['vR']:+.3f} | {r['rest']:.3f} | {r['nominal']:.3f} | {f} |{' FAULT' if fault else ''}")
    print(f"\nRESTING {os.path.basename(run)}: paying planted-unit carriers {carriers} of {len(gens)} champions; "
          f"with resting drive > 1 (the Effector saturates, F12's masking route) {drifted}"
          + (f"; frozen-bias faults {faults}" if a.frozen else ""))
    sys.exit(1 if faults else 0)


if __name__ == "__main__":
    main()
