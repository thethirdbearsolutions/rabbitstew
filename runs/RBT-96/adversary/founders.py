"""RBT-96 adversary, item 3: shared founders or luck, for the A/B-versus-A/A inversion.

From the committed generations.txt only (RBT-96 s0/s1, RBT-85 base/prot), no simulation:
  1. generation 0: do the two arms of a pair share their holistic founders? (identical gen-0 row)
  2. per-fifth RMS of the paired checkpoint difference, both designs: if shared founders are what
     keeps RBT-85's pairs tight, its pairs should be tighter early and the gap should persist;
     if it is luck, the designs should look alike once seed 201 is set aside.
  3. cross-seed correlation of the two arms (RBT-85 reported +0.97).
  4. 'discovery' runs: final fifth minus first fifth, per run, both designs.
  5. how surprising RBT-85's tight spread is under the A/A null, and the power of the proposed
     founder-sharing A/A at 4 and 8 seeds (Monte Carlo, seeded).

    python runs/RBT-96/adversary/founders.py > runs/RBT-96/adversary/founders.txt
"""
import math
import os
import statistics as st

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
R96 = os.path.dirname(HERE)
R85 = os.path.join(R96, "..", "RBT-85")
SEEDS = (201, 202, 203, 204)
FIFTHS = [(0, 50), (50, 100), (100, 150), (150, 200), (200, 250)]


def rows(path):
    out = {}
    for l in open(path).read().splitlines()[1:]:
        f = l.split("\t")
        out[int(f[0])] = f
    return out


def champ(r):
    return {g: float(f[13]) for g, f in r.items() if f[13]}


def fifth_means(c):
    return [st.mean(v for g, v in c.items() if lo <= g < hi) for lo, hi in FIFTHS]


def main():
    designs = {"RBT-96 A/A (s1 - s0)": (R96, "s0", "s1"), "RBT-85 A/B (prot - base)": (R85, "base", "prot")}
    data = {}
    print("RBT-96 adversary item 3: founders or luck (committed generations.txt only)\n")
    print("1. generation 0 (founders evaluated, before any reproduction): is the arms' gen-0 row identical?")
    for name, (root, a, b) in designs.items():
        ra = {s: rows(os.path.join(root, f"{a}-{s}", "generations.txt")) for s in SEEDS}
        rb = {s: rows(os.path.join(root, f"{b}-{s}", "generations.txt")) for s in SEEDS}
        data[name] = (ra, rb)
        same0 = [ra[s][0][3:] == rb[s][0][3:] for s in SEEDS]
        firstdiff = []
        for s in SEEDS:
            g = next((g for g in sorted(ra[s]) if ra[s][g][3:8] != rb[s][g][3:8]), None)
            firstdiff.append(g)
        print(f"   {name:28s} gen-0 holistic+champion columns identical: {same0}; first generation the holistic columns differ: {firstdiff}")

    print("\n2. RMS over seeds of the per-fifth paired difference in mean champion fitness (fifth = 50 generations, 11 checkpoints each)")
    print(f"   {'design':28s} " + "  ".join(f"g{lo}-{hi - 1:<5d}" for lo, hi in FIFTHS) + "   (without seed 201)")
    for name, (ra, rb) in data.items():
        per = {s: [y - x for x, y in zip(fifth_means(champ(ra[s])), fifth_means(champ(rb[s])))] for s in SEEDS}
        rms = [math.sqrt(st.mean(per[s][k] ** 2 for s in SEEDS)) for k in range(5)]
        rms3 = [math.sqrt(st.mean(per[s][k] ** 2 for s in SEEDS if s != 201)) for k in range(5)]
        print(f"   {name:28s} " + "  ".join(f"{x:.3f}     " for x in rms) + "   " + " ".join(f"{x:.3f}" for x in rms3))
        print(f"   {'':28s} per seed, final fifth: " + " ".join(f"{s} {per[s][4]:+.3f}" for s in SEEDS) + "; first fifth: " + " ".join(f"{s} {per[s][0]:+.3f}" for s in SEEDS))

    print("\n3. cross-seed correlation of the two arms' final-fifth means")
    for name, (ra, rb) in data.items():
        xa = [fifth_means(champ(ra[s]))[4] for s in SEEDS]
        xb = [fifth_means(champ(rb[s]))[4] for s in SEEDS]
        r4 = np.corrcoef(xa, xb)[0, 1]
        r3 = np.corrcoef(xa[1:], xb[1:])[0, 1]
        print(f"   {name:28s} r = {r4:+.3f} (4 seeds); {r3:+.3f} without 201.  arm means by seed: " + ", ".join(f"{x:.3f}/{y:.3f}" for x, y in zip(xa, xb)))

    print("\n4. climb per run: final-fifth mean minus first-fifth mean, and the largest fifth-to-fifth rise")
    for name, (ra, rb) in data.items():
        for arm, r in zip(name.split("(")[1].rstrip(")").split(" - ")[::-1], (ra, rb)):
            vals = []
            for s in SEEDS:
                fm = fifth_means(champ(r[s]))
                vals.append(f"{s} {fm[4] - fm[0]:+.2f} (max rise {max(b - a for a, b in zip(fm, fm[1:])):+.2f})")
            print(f"   {name[:6]} {arm:5s} " + "  ".join(vals))

    print("\n5. luck and power (Monte Carlo, normal model, numpy seed 96, 200000 draws)")
    rng = np.random.default_rng(96)
    sig = 0.128139  # the A/A RMS
    n = 200000
    d = rng.normal(0, sig, (n, 4))
    sd = d.std(axis=1, ddof=1)
    print(f"   under the A/A null (sigma {sig:.3f}), P(four pairs' SD <= RBT-85's 0.0462) = {np.mean(sd <= 0.0462):.3f}")
    # a two-component picture: one run in eight 'discovers' (RBT-96: 1 of 8 runs); P(none in RBT-85's 8 runs)
    for p in (1 / 8, 1 / 16):
        print(f"   if a run makes a seed-201-sized discovery with probability {p:.3f}: P(none of RBT-85's 8 runs does) = {(1 - p) ** 8:.3f}")
    # power of a founder-sharing A/A at k seeds to show sigma_fs < sigma_aa, one-sided F test on RMS^2 ratio (df k, 4)
    for k in (4, 8, 16):
        crit = np.quantile(rng.chisquare(4, n) / 4 / (rng.chisquare(k, n) / k), 0.95)  # F(4, k) 95th pct of aa/fs
        for true_fs in (0.046, 0.064, 0.090):
            aa = sig ** 2 * rng.chisquare(4, n) / 4
            fs = true_fs ** 2 * rng.chisquare(k, n) / k
            print(f"   founder-sharing A/A at {k:2d} seeds vs this 4-seed A/A: power to call it tighter (one-sided 5%) if its sigma is {true_fs:.3f}: {np.mean(aa / fs > crit):.2f}")


if __name__ == "__main__":
    main()
