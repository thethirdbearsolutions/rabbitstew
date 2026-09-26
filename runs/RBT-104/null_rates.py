"""RBT-104 Amendment 3: the "held" null with the operator's crossover, restated at RBT-104's rules.

Source: RBT-106's design adversary, `null_xover.py` (copied beside the readouts in `null_xover/`,
from origin/results/RBT-106-adversary at 85cdee48, unedited), run on the ten RBT-90 part-2
genealogies with RBT-104's own founders, plant (w = 1) and scale (K = 8), at RBT-104's criterion
(`pay64`: the root's sign, own links >= 24.7145) and RBT-104's baseline (RBT-106's
`baseline-w1-k8-SEED.txt` pay64 column, identical to RBT-104's `baseline-{801,4}.txt` at depths
0-30).  Twenty replicates per seed, seasons 150, 300, 599.  The operator is the ecology's own:
crossover_controller (rate 0.3; the mate's global brain taken with p 0.5) then mutate_controller.

This script only re-reads those committed tables; it simulates nothing.  Per seed it prints the
rate at which the NULL (no selection on the compass) produces each of RBT-104's readings:
  gate      season 150, as the gate was defined (k = planted- + bare-rooted hits) > B
  gate_p    season 150, k_planted > B
  held_old  RBT-104's first HELD rule: k > B at both 300 and 599 (bare-rooted hits counted)
  HELD      Amendment 3's rule: k_planted > B at both 300 and 599
and, beside each, the mutation-only operator's rate (the null the design first used).
"""
import glob
import math
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
CELL = re.compile(r"(\d+)\((\d+)\)/(\d+)/(\d+)")


def parse(seed):
    txt = open(os.path.join(HERE, "null_xover", f"xnull-w1-k8-{seed}.txt")).read()
    blocks = re.split(r"^## ", txt, flags=re.M)[1:]
    out = {}
    for b in blocks:
        key = "xover" if b.startswith("FULL OPERATOR") else "mutonly"
        reps = []
        for line in b.splitlines():
            if not re.match(r"^\| \d+ \|", line):
                continue
            cells = [tuple(map(int, m)) for m in CELL.findall(line)]
            reps.append(cells)  # [(k, kb, n, B) at 150, 300, 599]
        out[key] = reps
    return out


def rates(reps):
    n = len(reps)
    g = sum(r[0][0] > r[0][3] for r in reps)
    gp = sum(r[0][0] - r[0][1] > r[0][3] for r in reps)
    ho = sum(r[1][0] > r[1][3] and r[2][0] > r[2][3] for r in reps)
    hn = sum(r[1][0] - r[1][1] > r[1][3] and r[2][0] - r[2][1] > r[2][3] for r in reps)
    kb = sum(c[1] for r in reps for c in r)
    k = sum(c[0] for r in reps for c in r)
    return dict(n=n, gate=g, gate_p=gp, held_old=ho, HELD=hn, kb=kb, k=k)


def poibin_ge(ps, m):
    """P(at least m successes) for independent Bernoulli(ps)."""
    dist = [1.0]
    for p in ps:
        nd = [0.0] * (len(dist) + 1)
        for i, v in enumerate(dist):
            nd[i] += v * (1 - p)
            nd[i + 1] += v * p
        dist = nd
    return sum(dist[m:])


def _hi(k, n, z=1.6449):
    p = k / n
    d = 1 + z * z / n
    return min(1.0, (p + z * z / (2 * n)) / d + z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d)


def main():
    print("# RBT-104 Amendment 3: null rates with the operator's crossover, at RBT-104's rules\n")
    print("source: runs/RBT-104/null_xover/xnull-w1-k8-SEED.txt (RBT-106 adversary, 85cdee48), 20 replicates per seed\n")
    print("| seed | gate (k > B at 150) | gate on k_planted | old HELD (k, 300 & 599) | **HELD (k_planted, 300 & 599)** | bare share of k | mutation-only: gate / old HELD |")
    print("|---|---|---|---|---|---|---|")
    tot = {}
    per_seed = {}
    for s in SEEDS:
        d = parse(s)
        x, m = rates(d["xover"]), rates(d["mutonly"])
        per_seed[s] = x
        for k_, v in x.items():
            tot[k_] = tot.get(k_, 0) + v
        print(f"| {s} | {x['gate']}/{x['n']} | {x['gate_p']}/{x['n']} | {x['held_old']}/{x['n']} | **{x['HELD']}/{x['n']}** | "
              f"{x['kb']}/{x['k']} | {m['gate']}/{m['n']} / {m['held_old']}/{m['n']} |")
    N = tot["n"]
    print(f"| **all** | {tot['gate']}/{N} = {tot['gate'] / N:.3f} | {tot['gate_p']}/{N} = {tot['gate_p'] / N:.3f} | "
          f"{tot['held_old']}/{N} = {tot['held_old'] / N:.3f} | **{tot['HELD']}/{N} = {tot['HELD'] / N:.3f}** | "
          f"{tot['kb']}/{tot['k']} = {tot['kb'] / tot['k']:.2f} | |")
    ps = [per_seed[s]["HELD"] / per_seed[s]["n"] for s in SEEDS]
    po = [per_seed[s]["held_old"] / per_seed[s]["n"] for s in SEEDS]
    print(f"\nP(HELD on >= 2 of 10 seeds | null), seed rates as measured: Amendment 3's rule {poibin_ge(ps, 2):.4f}; the first rule {poibin_ge(po, 2):.4f}")
    r = tot["HELD"] / N
    print(f"  at the pooled rate {r:.3f} per seed: {poibin_ge([r] * 10, 2):.4f}; at its one-sided 95% upper bound "
          f"({1 - 0.05 ** (1 / N) if tot['HELD'] == 0 else _hi(tot['HELD'], N):.4f}): {poibin_ge([_hi(tot['HELD'], N)] * 10, 2):.4f}")
    gp = [per_seed[s]["gate"] / per_seed[s]["n"] for s in (801, 4)]
    print(f"P(the gate reads CONTINUE on >= 1 of seeds 801, 4 | null), as the gate was defined: {poibin_ge(gp, 1):.3f} "
          f"(801 {gp[0]:.2f}, 4 {gp[1]:.2f})")


if __name__ == "__main__":
    main()
