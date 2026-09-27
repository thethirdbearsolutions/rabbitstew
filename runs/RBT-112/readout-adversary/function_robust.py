"""RBT-112 readout adversary, attack 4: is FUNCTION FOLLOWS robust?

POST HOC, PRINT-ONLY.  Reads the committed function-patchy.txt of every HZ and HU arm through readout.py's parsers
(imported, unchanged) and prints:
  * per line: the primary F interval, the lesion gain interval, the decoy's retained share, and the call;
    the margin of each COMPASS line (the smaller of F's and gain's lower bounds) and every near miss;
  * the paired F(HZ) - F(HU) per seed; the t interval leaving out each seed, and the two seeds that move it most;
    the sign test; the COMPASS count if the most marginal line flipped either way.
Usage: function_robust.py
"""
import importlib.util
import itertools
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(D))
_spec = importlib.util.spec_from_file_location("rbt112_readout_fr", os.path.join(D, "readout.py"))
ro = importlib.util.module_from_spec(_spec)
sys.modules["rbt112_readout_fr"] = ro
_spec.loader.exec_module(ro)
fmt = lambda x: f"{x[0]:+.3f} [{x[1]:+.3f}, {x[2]:+.3f}]"


def detail(arm, seed):
    d = os.path.join(ROOT, "runs", "RBT-106", f"HU-{seed}") if arm == "HU" else os.path.join(D, f"HZ-{seed}")
    t = open(os.path.join(d, "function-patchy.txt")).read()
    g = re.search(r"gain \(intact - lesioned\)\s+([+-][\d.]+) \[\s*([+-][\d.]+),\s*([+-][\d.]+)\]", t)
    r = re.search(r"the decoy retains\s+([+-]?[\d.]+)%", t)
    return dict(glo=float(g.group(2)) if g else float("nan"), ret=float(r.group(1)) if r else float("nan"))


def main():
    print("# RBT-112 readout adversary: FUNCTION FOLLOWS, robustness (POST HOC, print-only)\n")
    print("| seed | arm | F [lo, hi] | gain lo | decoy retains | call | COMPASS | margin (min of F lo, gain lo) |")
    print("|---|---|---|---|---|---|---|---|")
    rows = {}
    for s in ro.SEEDS:
        for arm in ("HU", "HZ"):
            f = ro.r106.function(os.path.join(ROOT, "runs", "RBT-106", f"HU-{s}") if arm == "HU" else os.path.join(D, f"HZ-{s}"), "patchy")
            x = detail(arm, s)
            rows[(arm, s)] = (f, x)
            print(f"| {s} | {arm} | {f['F']:+.3f} [{f['lo']:+.3f}, {f['hi']:+.3f}] | {x['glo']:+.3f} | {x['ret']:.1f}% | "
                  f"{'FD' if f['fd'] else '-'}, {f['att']} | {f['cfd']} | {min(f['lo'], x['glo']):+.3f} |")
    comp = [s for s in ro.SEEDS if rows[("HZ", s)][0]["cfd"]]
    near = [s for s in ro.SEEDS if not rows[("HZ", s)][0]["cfd"] and rows[("HZ", s)][0]["lo"] > -0.1]
    marg = sorted(comp, key=lambda s: min(rows[("HZ", s)][0]["lo"], rows[("HZ", s)][1]["glo"]))
    print(f"\nHZ COMPASS lines: {len(comp)} {comp}; the most marginal: {marg[0]} "
          f"(F lo {rows[('HZ', marg[0])][0]['lo']:+.3f}); near misses (F lo > -0.1, not COMPASS): {near}")
    print(f"COMPASS count with the two most marginal lines lost: {len(comp) - 2}; with every near miss gained: {len(comp) + len(near)}; "
          f"FOLLOWS needs >= {ro.FD_MANY}")
    hu = [s for s in ro.SEEDS if rows[("HU", s)][0]["lo"] > 0]
    print(f"HU lines with a primary F interval above 0: {hu}")
    dF = {s: rows[("HZ", s)][0]["F"] - rows[("HU", s)][0]["F"] for s in ro.SEEDS}
    print("\npaired F(HZ) - F(HU), patchy-scored, per seed: " + ", ".join(f"{s}: {v:+.3f}" for s, v in dF.items()))
    print(f"all ten: {fmt(ro.t_int(list(dF.values())))}")
    for s in ro.SEEDS:
        print(f"  without {s}: {fmt(ro.t_int([v for k, v in dF.items() if k != s]))}")
    worst = min(itertools.combinations(ro.SEEDS, 2), key=lambda c: ro.t_int([v for k, v in dF.items() if k not in c])[1])
    print(f"the two seeds whose removal lowers the interval most: {worst} -> {fmt(ro.t_int([v for k, v in dF.items() if k not in worst]))}")
    pos = sum(v > 0 for v in dF.values())
    p = sum(math.comb(10, j) for j in range(pos, 11)) / 2 ** 10
    print(f"sign test: {pos} of 10 positive; one-sided P = {p:.4f}, two-sided {min(1, 2 * p):.4f}")


if __name__ == "__main__":
    main()
