"""RBT-106 design adversary, items 4 and 7: the factorial's power at the designer's OWN stated q, and the
primary's and the factorial's rates when bare lines' patchy-scored F is what bare_patchy/ measures.

Part A imports the designer's `power.factorial` unchanged and evaluates it at the q the pre-registration
states for P8 (§6.3: "q ~ 0.15-0.3 if the prize matters") and P1 ("q ~ 0.05"), which power.txt does not
tabulate (its "both needed" rows use q_P8 = 0.3 and 0.5).

Part B re-runs the same simulation with the non-carrying line's patchy-scored F and FD rate taken as
arguments (the designer's are N(0.10, 0.20) and 0.10, from the uniform world's per-body spread and seed
801's one patchy negative control).  `factorial_b` is the designer's `factorial` with those two numbers
lifted to parameters and nothing else changed (the rules, the carriers' F, layer 1's FD_CARRY).

Usage: power_adv.py [BARE_MEAN BARE_SD FD_BARE]
"""
import importlib.util
import os
import sys

import numpy as np
from scipy import stats

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("rbt106_power", os.path.join(os.path.dirname(_HERE), "power.py"))
pw = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(pw)


def factorial_b(q, n=10, sims=40000, seed=106, bare_mean=0.10, bare_sd=0.20, fd_bare=0.10):
    rng = np.random.default_rng(seed)
    cells = ("S1", "P1", "S8", "P8")
    carry = {c: rng.random((sims, n)) < q[c] for c in cells}
    F = {c: np.where(carry[c], pw.P_CARRY * rng.choice(pw.PATCHY_F, (sims, n)) + (1 - pw.P_CARRY) * rng.normal(bare_mean, bare_sd, (sims, n)),
                     rng.normal(bare_mean, bare_sd, (sims, n))) for c in cells}
    fd = {c: (rng.random((sims, n)) < np.where(carry[c], pw.FD_CARRY, fd_bare)).sum(1) for c in cells}
    tq = stats.t.ppf(0.975, n - 1)
    lo = lambda x: x.mean(1) - tq * x.std(1, ddof=1) / np.sqrt(n)
    I_lo = lo((F["P8"] - F["P1"]) - (F["S8"] - F["S1"]))
    p1_lo = lo(F["P1"] - F["S1"])
    prize_ok = (fd["P1"] >= 3) & (p1_lo > 0)
    return dict(I_pos=float((I_lo > 0).mean()), P_EVOLVED=float(prize_ok.mean()),
                P_NULL=float(((fd["P1"] <= 1) & ~(p1_lo > 0)).mean()),
                BOTH=float((~prize_ok & (I_lo > 0) & (fd["P8"] >= 3) & (fd["P1"] <= 1) & (fd["S8"] <= 1)).mean()))


def main(argv):
    print("# RBT-106 adversary: power at the designer's stated q, and with a measured patchy bare-line FD rate\n")
    print("## A. The designer's power.factorial, unchanged, at the q the pre-registration states (P1 ~ 0.05, P8 ~ 0.15-0.3)\n")
    print("| q S1, P1, S8, P8 | n | P(I > 0) | BOTH NEEDED | NEITHER | NOT DECIDED (1 - named) | P-NULL | P8-EVOLVED |")
    print("|---|---|---|---|---|---|---|---|")
    for q in ((0, 0.05, 0, 0.15), (0, 0.05, 0, 0.2), (0, 0.05, 0, 0.3), (0, 0.05, 0.05, 0.15), (0, 0.05, 0.05, 0.3)):
        for n in (10, 7):
            r = pw.factorial(dict(zip(("S1", "P1", "S8", "P8"), q)), n=n)
            named = r["PRIZE"] + r["REACH"] + r["EACH"] + r["BOTH"] + r["NEITHER"]
            print(f"| {', '.join(f'{x:g}' for x in q)} | {n} | {r['I_pos']:.3f} | {r['BOTH']:.3f} | {r['NEITHER']:.3f} | {1 - named:.3f} | {r['P_NULL']:.3f} | {r['P8_EVOLVED']:.3f} |")
    if len(argv) >= 3:
        bm, bs, fb = (float(x) for x in argv[:3])
        print(f"\n## B. Non-carrying lines as measured in the patchy world: F ~ N({bm:+.3f}, {bs:.3f}), FD rate {fb:.3f} "
              f"(designer: N(+0.10, 0.20), 0.10)\n")
        print("| scenario | q S1, P1, S8, P8 | designer's P-EVOLVED / P-NULL / P(I>0) | measured bare: P-EVOLVED / P-NULL / P(I>0) |")
        print("|---|---|---|---|")
        for name, q in (("nothing holds", (0, 0, 0, 0)), ("the prize alone suffices", (0, 0.5, 0, 0.5)),
                        ("the prize suffices, weakly", (0, 0.25, 0, 0.25)), ("both needed", (0, 0, 0, 0.5))):
            qd = dict(zip(("S1", "P1", "S8", "P8"), q))
            d = factorial_b(qd)
            m = factorial_b(qd, bare_mean=bm, bare_sd=bs, fd_bare=fb)
            print(f"| {name} | {', '.join(f'{x:g}' for x in q)} | {d['P_EVOLVED']:.3f} / {d['P_NULL']:.3f} / {d['I_pos']:.3f} | "
                  f"{m['P_EVOLVED']:.3f} / {m['P_NULL']:.3f} / {m['I_pos']:.3f} |")
        print("\n(The S1 cell's lines are uniform-world lines scored in the patchy world; P1's are patchy-world lines. "
              "Both are given the same bare distribution here, as in the designer's model.)")


if __name__ == "__main__":
    main(sys.argv[1:])
