"""RBT-106 P1 readout, F12 (RBT-104 readout adversary's lesson, coordinator 04:50): could an arm's install
control fail BY CONSTRUCTION?  POST HOC diagnostics beside the registered control; they score nothing.

For each arm (P1 and RBT-104's S1, restored from checkpoint) and each of the readout's seven bests
(function.GENS: 300, 350, ..., 590):

  planted-type units   every global unit fed by a wheel nose and feeding a drive Effector (the routed
                       motif's shape; routed.unit_indices gives the nose and Effector indices), with its
                       bias b, function f, output weights v to the drive Effectors, and RESTING DRIVE
                       max |v * f(b)| (f of the bias: the unit's output with no input).  For sign/integrate/
                       differentiate units the static value is not defined and is printed as n/a.
  Effector operating   RBT-104's readout adversary `sat_probe.body_stats`, imported: the a = 64 install
  point                control's body built exactly as function.py builds it, 4 paired seeds, real smell;
                       sat = P(|x_host| > 2) (tanh slope < 0.07) and T = the share of the compass's effect
                       reaching the Effector (1 = all).  RBT-104's reference: S1 hosts T 0.36-0.53, sat
                       0.31-0.55; S8 (x8) hosts T 0.04-0.08, sat 0.91-0.96 (sat_probe.txt).
  control              the arm's committed function-pc.txt (function.py --install 32, own world): the LINE call.

"By construction" (the question F12 asks), fixed here before reading any arm: an arm's control is flagged
MASKED BY CONSTRUCTION if its median T over the seven bests is below 0.10 (the x8 hosts' range), or if 4 or
more of its seven bests carry a planted-type unit with resting drive above 1 (RBT-106 §5.1's bias gate).  A
flagged arm that fails its control is UNUSABLE under the pre-registration's own rule (§6.1), not a null; the
rule itself is unchanged: an arm is usable iff its control passes.

Usage: f12.py BULK_ROOT ARM-SEED [ARM-SEED ...]   (runs from a checkout whose rabbitstew/ is c872e80's)
"""
import importlib.util
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
_s = importlib.util.spec_from_file_location("rbt104_sat_probe", os.path.join(ROOT, "runs", "RBT-104", "readout-adversary", "sat_probe.py"))
sp = importlib.util.module_from_spec(_s)
sys.modules["rbt104_sat_probe"] = sp
_s.loader.exec_module(sp)
fn, rp, routed = sp.fn, sp.rp, sp.routed

STATIC = {"tanh": np.tanh, "sin": np.sin, "abs": np.abs, "relu": lambda x: max(0.0, x)}
T_MASKED, DRIVE_MASKED, N_DRIVE = 0.10, 1.0, 4


def planted_units(g):
    """[(k, func, bias, [v...], resting drive or None)] for global units fed by a wheel nose and feeding a drive Effector."""
    nose, eff = routed.unit_indices(g)
    gb = g.global_brain
    if gb is None:
        return []
    out = []
    for k, u in enumerate(gb.units):
        ins = [l for l in gb.links if l.dst.node is None and l.dst.index == k and l.src.node in routed.WHEELS and l.src.index == nose]
        if not ins:
            continue
        vs = [l.weight for nd in routed.WHEELS for l in g.nodes[nd].segment.brain.links
              if l.src.node is None and l.src.index == k and l.dst.node == nd and l.dst.index == eff]
        if not vs:
            continue
        f = STATIC.get(u.func)
        drive = None if f is None else float(max(abs(v * f(u.bias)) for v in vs))
        out.append((k, u.func, float(u.bias), [float(v) for v in vs], drive))
    return out


def control(arm_dir):
    p = os.path.join(arm_dir, "function-pc.txt")
    if not os.path.exists(p):
        return "missing"
    m = re.search(r"^LINE \S+: (.+?)\s+F ([+-][\d.]+ \[[+-][\d.]+, [+-][\d.]+\])", open(p).read(), re.M)
    return f"{m.group(1)}, F {m.group(2)}" if m else "unparsed"


def main():
    bulk, arms = sys.argv[1], sys.argv[2:]
    seeds = [7000 + i for i in range(4)]
    print("# RBT-106 P1 readout, F12: planted-unit resting drive and the drive-Effector operating point under each arm's install control (POST HOC)")
    print(f"# bests {list(fn.GENS)}; sat_probe.body_stats (RBT-104 readout adversary), install w = 32, input +-1, 4 seeds, real smell")
    print(f"# flag MASKED BY CONSTRUCTION: median T < {T_MASKED} over the bests, or >= {N_DRIVE} of 7 bests carry a planted-type unit "
          f"with resting drive > {DRIVE_MASKED}\n")
    summary = []
    for arm in arms:
        run = os.path.join(bulk, arm)
        cfg = rp.config(run)
        rp.RUN[run] = cfg
        print(f"## {arm} (world: patches {cfg.food.patches})\n")
        print("| best | planted-type units: func, b, v, resting drive | median abs(x_host) | sat P(abs(x_host) > 2) | T |")
        print("|---|---|---|---|---|")
        Ts, driven = [], 0
        for gen in fn.GENS:
            g = rp.genotype(run, "conventional", gen)
            pu = planted_units(g)
            x, c = sp.body_stats(run, cfg, gen, 32.0, 1.0, seeds)
            T = float(np.mean(np.abs(np.tanh(x + c) - np.tanh(x))) / max(1e-12, np.mean(np.abs(np.tanh(c)))))
            Ts.append(T)
            big = any(d is not None and d > DRIVE_MASKED for *_, d in pu)
            driven += big
            desc = "; ".join(f"{fu} b {b:+.3f} v [{', '.join(f'{v:+.2f}' for v in vs)}] drive {'n/a' if d is None else f'{d:.3f}'}"
                             for _, fu, b, vs, d in pu) or "none"
            print(f"| g{gen} | {desc} | {np.median(np.abs(x)):.2f} | {np.mean(np.abs(x) > 2):.3f} | {T:.3f} |")
            sys.stdout.flush()
        mT = float(np.median(Ts))
        masked = mT < T_MASKED or driven >= N_DRIVE
        ctl = control(os.path.join(ROOT, "runs", "RBT-106", arm))
        print(f"\nF12 {arm}: median T {mT:.3f}; bests with a planted-type unit driving > {DRIVE_MASKED}: {driven}/7; "
              f"control (function-pc.txt): {ctl}; {'MASKED BY CONSTRUCTION' if masked else 'not masked by construction'}\n")
        summary.append((arm, mT, driven, ctl, masked))
    print("## Summary\n\n| arm | median T | bests driving > 1 | install control | by construction |\n|---|---|---|---|---|")
    for arm, mT, d, ctl, masked in summary:
        print(f"| {arm} | {mT:.3f} | {d}/7 | {ctl} | {'MASKED' if masked else 'no'} |")


if __name__ == "__main__":
    main()
