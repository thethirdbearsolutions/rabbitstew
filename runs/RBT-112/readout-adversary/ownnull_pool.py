"""RBT-112 readout adversary, attack 1 (the instrument): the HELD null on EACH HZ ARM'S OWN genealogy, at S = 0.

POST HOC, PRINT-ONLY.  runs/RBT-112/null_xover_s0.py (unchanged; RBT-106's design adversary's null_xover.py with the
operator at global_bias_sigma = 0 and mu from the S = 0 table) was run on every HZ arm's OWN lineage.jsonl (restored
from ckpt/rbt-112-HZ-SEED), with the arm's own w = 32 founders (runs/RBT-106/founders.py; all ten digests match),
200 replicates per arm (ownnull.sh).  This is RBT-106 h-adversary H1's check, moved to the S = 0 arm.

null_xover prints HELD under the pre-amendment k > B; every replicate is re-scored here under the REGISTERED rule
(k_planted = k - k_bare > B at 300 and 599).  Beside each arm: the null's k_planted distribution at 300 and 599 on
the arm's own genealogy (so n matches the arm's n exactly: asserted), where the observed k_planted falls in it
(the share of replicates at or above it), and the registered B.  If B were far above the own-genealogy null's
95th percentile, the registered bar would be too high under S = 0 and FALSIFIED an artefact of the table.

Usage: ownnull_pool.py OWNNULL_DIR   (files ownnull-HZ-SEED.txt)
"""
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
SEEDS = (801, 4, 804, 805, 806, 807, 1, 2, 3, 7)
CELL = r"(\d+)\((\d+)\)/(\d+)/(\d+)(?: H)?"


def parse(path):
    out, sec = {"x": [], "m": []}, None
    for line in open(path):
        if line.startswith("## FULL"):
            sec = "x"
        elif line.startswith("## designer") or line.startswith("## MUTATION"):
            sec = "m"
        m = re.match(rf"^\| (\d+) \| {CELL} \| {CELL} \| {CELL} \|", line)
        if m and sec:
            v = list(map(int, m.groups()))
            out[sec].append({150: (v[1] - v[2], v[3], v[4]), 300: (v[5] - v[6], v[7], v[8]), 599: (v[9] - v[10], v[11], v[12])})
    return out


def observed(s):
    r = {}
    for season in (300, 599):
        t = open(os.path.join(D, f"HZ-{s}", f"held-{season}.txt")).read()
        m = re.search(r"k_planted = (\d+), n = (\d+), mu = \S+, B = (\d+)", t)
        r[season] = tuple(map(int, m.groups()))
    return r


def main():
    d = sys.argv[1]
    print("# RBT-112 readout adversary: the HELD null on each HZ arm's own genealogy, S = 0 operator (POST HOC, print-only)\n")
    print("| arm | n / B at 300, 599 | null k_planted 300: mean, 95th, 99th | null k_planted 599: mean, 95th, 99th | "
          "observed k_planted 300 / 599 | P(null >= obs) 300 / 599 | P(null >= obs at both) | null HELD (registered rule), full op / mut only | obs above own null's 95th at both |")
    print("|---|---|---|---|---|---|---|---|---|")
    tot = [0, 0, 0, 0]
    above = []
    for s in SEEDS:
        p = parse(os.path.join(d, f"ownnull-HZ-{s}.txt"))
        ob = observed(s)
        X = p["x"]
        r0 = X[0]
        assert (r0[300][1], r0[300][2], r0[599][1], r0[599][2]) == (ob[300][1], ob[300][2], ob[599][1], ob[599][2]), s
        k3 = np.array([r[300][0] for r in X])
        k5 = np.array([r[599][0] for r in X])
        hx = sum(r[300][0] > r[300][2] and r[599][0] > r[599][2] for r in X)
        hm = sum(r[300][0] > r[300][2] and r[599][0] > r[599][2] for r in p["m"])
        tot[0] += hx; tot[1] += len(X); tot[2] += hm; tot[3] += len(p["m"])
        p3, p5 = float((k3 >= ob[300][0]).mean()), float((k5 >= ob[599][0]).mean())
        pb = float(((k3 >= ob[300][0]) & (k5 >= ob[599][0])).mean())
        ab = ob[300][0] > np.percentile(k3, 95) and ob[599][0] > np.percentile(k5, 95)
        if ab:
            above.append(s)
        print(f"| HZ-{s} | {ob[300][1]}/{ob[300][2]}, {ob[599][1]}/{ob[599][2]} | {k3.mean():.1f}, {np.percentile(k3, 95):.0f}, {np.percentile(k3, 99):.0f} | "
              f"{k5.mean():.1f}, {np.percentile(k5, 95):.0f}, {np.percentile(k5, 99):.0f} | {ob[300][0]} / {ob[599][0]} | {p3:.3f} / {p5:.3f} | {pb:.3f} | "
              f"{hx}/{len(X)} / {hm}/{len(p['m'])} | {ab} |")
    print(f"\nPOOLED HZ: registered HELD under no selection on the arms' own genealogies: full operator {tot[0]}/{tot[1]} = "
          f"{100 * tot[0] / tot[1]:.1f}%; mutation only {tot[2]}/{tot[3]} = {100 * tot[2] / tot[3]:.1f}%  "
          f"(registered S = 0 null on part 2's genealogies, power.txt layer 0: 1.5%)")
    print(f"HZ seeds whose observed k_planted is above their own-genealogy null's 95th percentile at both 300 and 599: {len(above)} {above}")


if __name__ == "__main__":
    main()
