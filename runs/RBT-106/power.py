"""RBT-106 §6.3: matched-null power for every verdict that can read "absent" (the programme rule since
RBT-102), from committed numbers only.

Layer 1, readout (b) on one line: the RBT-104 design adversary's `power.py`, imported, gives
P(FOOD-DEPENDENT | a fraction p of the seven window champions carries a working a = 64 compass)
from the uniform world's committed per-body F.  In the patchy world a working compass pays about
2.7x more (prize.txt) against a per-body spread that also grows, so the uniform layer is the
conservative one; its p -> P table is reprinted as it stands.

Layer 2, the verdicts over n usable paired seeds, with q_U, q_P = P(a seed's arm is HELD) in the
uniform and patchy worlds:
  H SUPPORTED    #HELD(HP) - #HELD(HU) >= 3   (the paired log-excess condition only lowers it)
  H FALSIFIED-b  #HELD(HP) <= 1
  H FALSIFIED-a  #HELD(HU) >= 5
computed exactly from two independent binomials.  Printed on a grid of (q_U, q_P) and at the
design's stated values (PREREGISTRATION.md §6.3), n = 10 and n = 7 (the VOID floor).

Layer 3, the "HELD" call on one arm under no selection: its false-positive rate is at least the
binomial 5% and is inflated by the clustering of the living by descent.  It is the same in both
arms of a pair, which is why the verdict is a contrast, and it enters through q_U.
"""
import importlib.util
import os
import sys
from math import comb

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_spec = importlib.util.spec_from_file_location("rbt104_adv_power", os.path.join(_ROOT, "runs", "RBT-104", "adversary", "power.py"))
ap = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ap)


def pmf(n, q):
    return [comb(n, i) * q ** i * (1 - q) ** (n - i) for i in range(n + 1)]


def outcomes(n, qU, qP):
    pu, pp = pmf(n, qU), pmf(n, qP)
    sup = sum(pu[i] * pp[j] for i in range(n + 1) for j in range(n + 1) if j - i >= 3)
    fb = sum(pp[:2])
    fa = sum(pu[5:])
    return sup, fb, fa


# Layer 4, the factorial (P1, S1, P8, S8), patchy-scored.  A seed's line in a cell "carries" (keeps a
# working compass in a fraction p = 4/7 of its window champions) with probability q_cell.  Its F is then
# p x (a population's patchy motif - decoy, resampled from prize/patchy-*.txt's ten committed values)
# + (1 - p) x a bare line's F; a non-carrying line's F is a bare line's F: N(0.10, 0.20), from the bare
# part-2 champions' patchy-scored F (+0.223 [-0.196, +0.643], controls/function-patchy-801.txt) and the
# uniform-scored one (+0.033 [-0.141, +0.208], RBT-104 function-controls-801.txt).  Its FD call is layer 1's
# P(FOOD-DEPENDENT | p) for a carrier.  The rules are readout.py's (EVOLVED: >= 3 FD lines and the paired F
# interval > 0; NULL: <= 1 and that interval not > 0) (0.62 at p = 4/7, conservative in the patchy world) and the committed
# false-positive rate 0.10 otherwise.
PATCHY_F = [2.272, 2.049, 2.647, 1.431, 1.830, 1.717, 1.067, 1.897, 3.721, 2.911]   # prize.txt, motif - decoy
P_CARRY, FD_CARRY, FD_BARE = 4 / 7, 0.624, 0.100


def factorial(q, n=10, sims=40000, seed=106):
    from scipy import stats
    import numpy as np
    rng = np.random.default_rng(seed)
    cells = ("S1", "P1", "S8", "P8")
    carry = {c: rng.random((sims, n)) < q[c] for c in cells}
    F = {c: np.where(carry[c], P_CARRY * rng.choice(PATCHY_F, (sims, n)) + (1 - P_CARRY) * rng.normal(0.10, 0.20, (sims, n)),
                     rng.normal(0.10, 0.20, (sims, n))) for c in cells}
    fd = {c: (rng.random((sims, n)) < np.where(carry[c], FD_CARRY, FD_BARE)).sum(1) for c in cells}
    tq = stats.t.ppf(0.975, n - 1)
    lo = lambda x: x.mean(1) - tq * x.std(1, ddof=1) / np.sqrt(n)
    I_lo = lo((F["P8"] - F["P1"]) - (F["S8"] - F["S1"]))
    p1_lo, p8_lo, r_lo = lo(F["P1"] - F["S1"]), lo(F["P8"] - F["S8"]), lo(F["S8"] - F["S1"])
    prize_ok = (fd["P1"] >= 3) & (p1_lo > 0)
    reach_ok = (fd["S8"] >= 3) & (r_lo > 0)
    both = ~prize_ok & ~reach_ok & (I_lo > 0) & (fd["P8"] >= 3) & (fd["P1"] <= 1) & (fd["S8"] <= 1)
    neither = ~prize_ok & ~reach_ok & ~both & (np.max(np.stack([fd[c] for c in cells]), 0) <= 1) & \
        ~((I_lo > 0) | (p1_lo > 0) | (p8_lo > 0) | (r_lo > 0))
    p_null = (fd["P1"] <= 1) & ~(p1_lo > 0)
    p8_null = (fd["P8"] <= 1) & ~(p8_lo > 0)
    return dict(I_pos=float((I_lo > 0).mean()), PRIZE=float((prize_ok & ~reach_ok).mean()), REACH=float((reach_ok & ~prize_ok).mean()),
                EACH=float((prize_ok & reach_ok).mean()), BOTH=float(both.mean()), NEITHER=float(neither.mean()),
                P_EVOLVED=float(prize_ok.mean()), P_NULL=float(p_null.mean()),
                P8_EVOLVED=float(((fd["P8"] >= 3) & (p8_lo > 0)).mean()), P8_NULL=float(p8_null.mean()))


def main():
    print("# RBT-106: matched-null power\n")
    print("## Layer 1 (imported): P(line reads FOOD-DEPENDENT | fraction p of 7 window champions carries a working a = 64 compass)\n")
    print("| p | P(FOOD-DEPENDENT) |\n|---|---|")
    for p in (0.0, 0.29, 0.57, 0.86, 1.0):
        print(f"| {p:.2f} | {ap.p_fd(p):.3f} |")
    print(f"\nfalse positive on bare lines: {ap.p_fd(0.0):.3f} as committed, {ap.p_fd(0.0, centre=True):.3f} centred\n")
    for n in (10, 7):
        print(f"## Layer 2, n = {n} usable paired seeds: P(SUPPORTED count) / P(FALSIFIED-b count) / P(FALSIFIED-a count)\n")
        qs = (0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 0.9)
        print("| q_U \\ q_P | " + " | ".join(f"{q:.2f}" for q in qs) + " |")
        print("|---|" + "---|" * len(qs))
        for qU in qs:
            cells = []
            for qP in qs:
                s, b, a = outcomes(n, qU, qP)
                cells.append(f"{s:.2f} / {b:.2f} / {a:.2f}")
            print(f"| {qU:.2f} | " + " | ".join(cells) + " |")
        print()
    print("## At the design's stated values (§6.3)\n")
    for label, qU, qP in (("H_prize (the prize decides): q_U 0.15, q_P 0.60", 0.15, 0.60),
                          ("H_prize, weaker: q_U 0.15, q_P 0.40", 0.15, 0.40),
                          ("H_both (the uniform prize suffices): q_U 0.60, q_P 0.70", 0.60, 0.70),
                          ("H_none (the operator wins in both): q_U 0.08, q_P 0.08", 0.08, 0.08)):
        for n in (10, 7):
            s, b, a = outcomes(n, qU, qP)
            print(f"  {label}, n = {n}: P(SUPPORTED count) {s:.3f}, P(FALSIFIED-b count) {b:.3f}, P(FALSIFIED-a count) {a:.3f}")
    print("\n## Layer 4: the factorial, patchy-scored; P(verdict | q per cell), n = 10 (and 7)\n")
    print("| scenario | q S1, P1, S8, P8 | P(I > 0) | PRIZE SUFFICES | REACH SUFFICES | EACH | BOTH NEEDED | NEITHER | P-EVOLVED | P-NULL | P8-EVOLVED | P8-NULL |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for name, q in (("null: nothing holds", (0, 0, 0, 0)),
                    ("the prize alone suffices", (0, 0.5, 0, 0.5)),
                    ("the prize suffices, weakly", (0, 0.25, 0, 0.25)),
                    ("reach alone suffices", (0, 0, 0.5, 0.5)),
                    ("each suffices", (0, 0.5, 0.5, 0.7)),
                    ("both needed (the interaction)", (0, 0, 0, 0.5)),
                    ("both needed, weakly", (0, 0, 0, 0.3)),
                    ("both needed, with leakage", (0, 0.1, 0.1, 0.5))):
        for n in (10, 7):
            r = factorial(dict(zip(("S1", "P1", "S8", "P8"), q)), n=n)
            print(f"| {name}, n = {n} | {', '.join(f'{x:g}' for x in q)} | {r['I_pos']:.3f} | {r['PRIZE']:.3f} | {r['REACH']:.3f} | "
                  f"{r['EACH']:.3f} | {r['BOTH']:.3f} | {r['NEITHER']:.3f} | {r['P_EVOLVED']:.3f} | {r['P_NULL']:.3f} | "
                  f"{r['P8_EVOLVED']:.3f} | {r['P8_NULL']:.3f} |")
    print("\n  q = 0.08 is the no-selection false-positive rate of HELD allowed for clustering (binomial 5%, inflated);")
    print("  under H_none SUPPORTED's count fires with the probability printed, which is the verdict's false-positive rate.")


if __name__ == "__main__":
    main()
