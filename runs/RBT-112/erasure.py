"""RBT-112 step 3: the erasure rate u, default against global_bias_sigma = 0 (DECISION.md, fixed before the run).

Reads runs/RBT-112/baseline/baseline-w32[-S0]-SEED.txt.  f(d) = pooled pay32 fraction over the ten
seeds; u(d) = 1 - f(d)^(1/d); the primary is u(8).  Also: the same on `same` (the structure's own decay),
per-seed u(8) with a t(9) interval, pay-rung persistence by depth, and the byte-identity precondition
against RBT-106's committed default tables.

Usage: erasure.py  > erasure.txt
"""
import os

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
T975_9 = 2.2622
COLS = {"same": 2, "pay32": 5, "pay64": 8}


def table(path):
    rows = [l.rstrip("\n").split("\t") for l in open(path) if not l.startswith("#")]
    return {int(r[0]): r for r in rows}


def load(tag):
    return {s: table(os.path.join(_HERE, "baseline", f"baseline-w32{tag}-{s}.txt")) for s in SEEDS}


def f(T, col, d, seeds=SEEDS):
    return sum(int(T[s][d][COLS[col]]) for s in seeds) / sum(int(T[s][d][1]) for s in seeds)


def u(p, d):
    return 1 - p ** (1 / d) if p > 0 else 1.0


def decide(x):
    return "u <= 0.12: WORTH RUNNING the arm" if x <= 0.12 else ("u >= 0.20: STOP and report" if x >= 0.20 else "0.12 < u < 0.20: GREY, the coordinator decides")


def main():
    D, Z = load(""), load("-S0")
    same = all(open(os.path.join(_HERE, "baseline", f"baseline-w32-{s}.txt")).read().splitlines()[1:]
               == open(os.path.join(_ROOT, "runs", "RBT-106", "baseline", f"baseline-w32-{s}.txt")).read().splitlines()[1:] for s in SEEDS)
    print("# RBT-112 step 3: the operator-alone erasure of RBT-106 H's planted w = 32 compass, K = 1, no selection, no crossover")
    print("# 10 seeds x 30 planted founders x 20 lineages = 6000 per arm; each S = 0 lineage is its default twin draw for draw\n")
    print(f"precondition: the default reproduces RBT-106's committed baseline-w32-SEED.txt below the header on all ten seeds: {'YES' if same else 'NO -> VOID'}\n")
    print("pay-rung persistence f(d), pooled (pay32: structure with its sign and own links >= 12.5236; RBT-106 H's criterion)")
    print("| depth | pay32 default | pay32 S = 0 | same default | same S = 0 | pay64 default | pay64 S = 0 | own-links median default / S = 0 | whole-brain median default / S = 0 |")
    print("|---|---|---|---|---|---|---|---|---|")
    for d in (0, 1, 2, 4, 8, 12, 16, 25, 40):
        med = lambda T, c: np.median([float(T[s][d][c]) for s in SEEDS])
        print(f"| {d} | {f(D, 'pay32', d):.4f} | {f(Z, 'pay32', d):.4f} | {f(D, 'same', d):.4f} | {f(Z, 'same', d):.4f} | "
              f"{f(D, 'pay64', d):.4f} | {f(Z, 'pay64', d):.4f} | {med(D, 11):.2f} / {med(Z, 11):.2f} | {med(D, 12):.3f} / {med(Z, 12):.3f} |")
    print("\nu(d) = 1 - f(d)^(1/d), per generation")
    print("| d | u pay32 default | **u pay32 S = 0** | u same default (structure's own) | u same S = 0 |")
    print("|---|---|---|---|---|")
    for d in (1, 2, 4, 8, 16):
        print(f"| {d} | {u(f(D, 'pay32', d), d):.3f} | **{u(f(Z, 'pay32', d), d):.3f}** | {u(f(D, 'same', d), d):.3f} | {u(f(Z, 'same', d), d):.3f} |")
    print("\nper seed, u(8) on pay32")
    print("| seed | default | S = 0 |")
    print("|---|---|---|")
    ud, uz = [], []
    for s in SEEDS:
        a, b = u(f(D, "pay32", 8, (s,)), 8), u(f(Z, "pay32", 8, (s,)), 8)
        ud.append(a); uz.append(b)
        print(f"| {s} | {a:.3f} | {b:.3f} |")
    for name, v in (("default", ud), ("S = 0", uz), ("S = 0 - default, paired", list(np.subtract(uz, ud)))):
        m, h = np.mean(v), T975_9 * np.std(v, ddof=1) / np.sqrt(len(v))
        print(f"  mean over seeds, {name}: {m:+.3f} [{m - h:+.3f}, {m + h:+.3f}] (t(9))")
    ud8, uz8 = u(f(D, "pay32", 8), 8), u(f(Z, "pay32", 8), 8)
    print(f"\nPRIMARY u(8), pooled: default {ud8:.3f}; S = 0 {uz8:.3f}; the structure's own decay (same, S = 0) {u(f(Z, 'same', 8), 8):.3f}")
    side = {d: decide(u(f(Z, 'pay32', d), d)) for d in (1, 4)}
    for d, t in side.items():
        if t != decide(uz8):
            print(f"  note: u({d}) at S = 0 falls in a different band ({t}); u(8) governs (DECISION.md)")
    print(f"DECISION (DECISION.md): {'VOID (precondition failed)' if not same else decide(uz8)}")


if __name__ == "__main__":
    main()
