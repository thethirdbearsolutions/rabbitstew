"""RBT-106 H readout adversary, attack 1: the HELD null on EACH H ARM'S OWN genealogy.

The registered null (null_rates.txt, 1.0% for pay32) ran the operator down part 2's ten genealogies (uniform world,
no compass).  HP's genealogies are the patchy world's: more births (1668-1861 against 1132-1341), deeper windows,
and 1-3 planted roots.  Here the design adversary's null_xover.py (unchanged) was run on every HU and HP arm's OWN
lineage.jsonl (restored from ckpt/rbt-106-ARM-SEED), with the arm's own w = 32 founders (founders.py, digests
match), 100 replicates per arm, both operators.  null_xover prints HELD under the REGISTERED k > B; this script
re-scores every replicate under the AMENDED rule (k_planted = k - k_bare > B at 300 and 599; §10.2) and puts the
observed arm beside its own null: the null's k_planted at 599 (max, 99th pct) against the arm's k_planted.

Usage: ownnull_pool.py OWNNULL_DIR   (files ownnull-ARM-SEED.txt)
"""
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.dirname(HERE)
SEEDS = (801, 4, 804, 805, 806, 807, 1, 2, 3, 7)


def parse(path):
    out, sec = {"x": [], "m": []}, None
    for line in open(path):
        if line.startswith("## FULL"):
            sec = "x"
        elif line.startswith("## designer"):
            sec = "m"
        m = re.match(r"^\| (\d+) \| (\d+)\((\d+)\)/(\d+)/(\d+)(?: H)? \| (\d+)\((\d+)\)/(\d+)/(\d+)(?: H)? \|", line)
        if m and sec:
            v = list(map(int, m.groups()))
            out[sec].append(dict(k3=v[1] - v[2], n3=v[3], B3=v[4], k5=v[5] - v[6], n5=v[7], B5=v[8]))
    return out


def observed(arm, s):
    r = {}
    for season in (300, 599):
        t = open(os.path.join(D, f"{arm}-{s}", f"held-{season}.txt")).read()
        m = re.search(r"k_planted = (\d+), n = (\d+), mu = \S+, B = (\d+)", t)
        r[season] = tuple(map(int, m.groups()))
    return r


def main():
    d = sys.argv[1]
    print("# RBT-106 H adversary: the HELD null on each arm's own genealogy (null_xover.py, 100 reps per arm), amended rule k_planted > B\n")
    print("| arm | null n/B at 300, 599 (own genealogy) | amended HELD, full operator | amended HELD, mutation only | null k_planted at 599: mean, 99th pct, max | observed k_planted 300 / 599 | observed HELD | observed k_planted 599 above every null replicate? |")
    print("|---|---|---|---|---|---|---|---|")
    tot = {}
    for arm in ("HU", "HP"):
        for s in SEEDS:
            p = parse(os.path.join(d, f"ownnull-{arm}-{s}.txt"))
            ob = observed(arm, s)
            hx = sum(r["k3"] > r["B3"] and r["k5"] > r["B5"] for r in p["x"])
            hm = sum(r["k3"] > r["B3"] and r["k5"] > r["B5"] for r in p["m"])
            k5 = np.array([r["k5"] for r in p["x"]])
            oH = ob[300][0] > ob[300][2] and ob[599][0] > ob[599][2]
            r0 = p["x"][0]
            assert (r0["n3"], r0["B3"], r0["n5"], r0["B5"]) == (ob[300][1], ob[300][2], ob[599][1], ob[599][2]), (arm, s)
            tot.setdefault(arm, [0, 0, 0, 0])
            t = tot[arm]
            t[0] += hx; t[1] += hm; t[2] += len(p["x"]); t[3] += len(p["m"])
            print(f"| {arm}-{s} | {r0['n3']}/{r0['B3']}, {r0['n5']}/{r0['B5']} | {hx}/{len(p['x'])} | {hm}/{len(p['m'])} | "
                  f"{k5.mean():.2f}, {np.percentile(k5, 99):.0f}, {k5.max()} | {ob[300][0]} / {ob[599][0]} | {oH} | "
                  f"{'yes' if ob[599][0] > k5.max() else 'no'} |")
    print()
    for arm, t in tot.items():
        print(f"POOLED {arm}: amended HELD at 300 and 599 under no selection, own genealogies: full operator {t[0]}/{t[2]} = {100 * t[0] / t[2]:.1f}%; "
              f"mutation only {t[1]}/{t[3]} = {100 * t[1] / t[3]:.1f}%")
    print("(registered null on part 2's genealogies, null_rates.txt: 1.0% under either operator)")


if __name__ == "__main__":
    main()
