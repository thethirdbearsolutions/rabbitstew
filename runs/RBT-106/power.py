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
    print("\n  q = 0.08 is the no-selection false-positive rate of HELD allowed for clustering (binomial 5%, inflated);")
    print("  under H_none SUPPORTED's count fires with the probability printed, which is the verdict's false-positive rate.")


if __name__ == "__main__":
    main()
