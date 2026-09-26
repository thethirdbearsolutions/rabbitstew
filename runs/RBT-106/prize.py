"""RBT-106 section 2: the prize, uniform world against the one-field patchy world, per population.

Reads, for each of RBT-90 part 2's ten populations, the per-body a = 32 and a = 64 income deltas
(the routed motif against each body's own baseline, 64 paired seeds from 7000) and the base income:
  uniform  docs/artifacts/RBT-103-seed-SEED.txt           (RBT-103, committed)
  patchy   runs/RBT-106/prize/patchy-SEED.txt              (prize.sh: the same harness and bodies,
                                                            world = part 2's config with patches = 3)
and prints per population and t(9) across populations: the gain in each world, the paired
difference and ratio, the base income in each world, and the patchy world's decoy verdict at
a = 64.  The harness check (prize/harness-801-uniform.txt against RBT-103-seed-801.txt) is printed
first: its ROW must equal the committed one.
"""
import os
import re

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)


def t_int(x):
    x = np.asarray(x, float)
    n = len(x)
    h = stats.t.ppf(0.975, n - 1) * x.std(ddof=1) / np.sqrt(n)
    return x.mean(), x.mean() - h, x.mean() + h


def per_body(path):
    """{gen: (base, delta a=32, delta a=64)} from a routed_populations readout."""
    txt = open(path).read()
    rows = re.findall(r"^g(\d+)\s+[+-]1\s+(\d+\.\d+) \|\s+([+-]\d+\.\d+) \|\s+([+-]\d+\.\d+)", txt, re.M)
    return {int(g): (float(b), float(d32), float(d64)) for g, b, d32, d64 in rows}


def verdict(path, a):
    m = re.search(rf"^\s+\d+\s+{a} \|.*\| (PAYS|NEGATIVE|VETOED by the zero count|unresolved at this n)", open(path).read(), re.M)
    return m.group(1) if m else "?"


def decoy(path):
    txt = open(path).read()
    m = re.search(r"motif - decoy\s+([+-]\d+\.\d+) \[\s*([+-]\d+\.\d+),\s*([+-]\d+\.\d+)\];\s+the decoy retains\s+(-?[\d.]+|nan)%", txt)
    v = re.search(r"verdict: (FOOD-DEPENDENT|GAIT EFFECT|UNRESOLVED at this n)", txt)
    return (float(m.group(1)), float(m.group(2)), float(m.group(3)), float(m.group(4)), v.group(1)) if m and v else None


def fmt(x):
    return f"{x[0]:+.3f} [{x[1]:+.3f}, {x[2]:+.3f}]"


def main():
    row = lambda p: re.search(r"^ROW .*$", open(p).read(), re.M).group(0)
    h, c = os.path.join(HERE, "prize", "harness-801-uniform.txt"), os.path.join(ROOT, "docs", "artifacts", "RBT-103-seed-801.txt")
    print("# RBT-106: the routed compass's prize, part 2's uniform world against the one-field patchy world\n")
    if os.path.exists(h):
        same = row(h) == row(c)
        print(f"harness check (restored bodies, own world, seed 801): {row(h)}")
        print(f"                                   committed RBT-103: {row(c)}  -> {'IDENTICAL' if same else 'DIFFERENT'}\n")
    print("| seed | uniform a=64 (RBT-103) | patchy a=64 | patchy - uniform | ratio | uniform a=32 | patchy a=32 | base uniform | base patchy | patchy decoy at a=64 |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    U64, P64, U32, P32, BU, BP, FD = [], [], [], [], [], [], []
    for s in SEEDS:
        up = os.path.join(ROOT, "docs", "artifacts", f"RBT-103-seed-{s}.txt")
        pp = os.path.join(HERE, "prize", f"patchy-{s}.txt")
        if not os.path.exists(pp):
            print(f"| {s} | (patchy readout missing) |")
            continue
        u, p = per_body(up), per_body(pp)
        gens = sorted(set(u) & set(p))
        uu = t_int([u[g][2] for g in gens]); pq = t_int([p[g][2] for g in gens])
        u32 = np.mean([u[g][1] for g in gens]); p32 = np.mean([p[g][1] for g in gens])
        bu = np.mean([u[g][0] for g in gens]); bp = np.mean([p[g][0] for g in gens])
        d = decoy(pp)
        U64.append(uu[0]); P64.append(pq[0]); U32.append(u32); P32.append(p32); BU.append(bu); BP.append(bp)
        FD.append(d[4] if d else "?")
        ds = f"{d[0]:+.3f} [{d[1]:+.3f}, {d[2]:+.3f}], retains {d[3]:.0f}%: {d[4]}" if d else "?"
        print(f"| {s} | {uu[0]:+.3f} {verdict(up, 64)} | {fmt(pq)} {verdict(pp, 64)} | {pq[0] - uu[0]:+.3f} | "
              f"{pq[0] / uu[0]:.2f}x | {u32:+.3f} | {p32:+.3f} | {bu:.3f} | {bp:.3f} | {ds} |")
    if len(P64) < 2:
        return
    n = len(P64)
    print(f"\nacross the {n} populations, t({n - 1}):")
    for name, x in (("uniform a=64", U64), ("patchy a=64", P64), ("patchy - uniform a=64", np.subtract(P64, U64)),
                    ("uniform a=32", U32), ("patchy a=32", P32), ("patchy - uniform a=32", np.subtract(P32, U32)),
                    ("base income uniform", BU), ("base income patchy", BP), ("base patchy - uniform", np.subtract(BP, BU))):
        print(f"  {name:24s} {fmt(t_int(x))}")
    print(f"  ratio of means, a=64: {np.mean(P64) / np.mean(U64):.2f}x;  gain per unit base income, a=64: "
          f"uniform {np.mean(U64) / np.mean(BU):.2f}, patchy {np.mean(P64) / np.mean(BP):.2f}")
    print(f"  patchy decoy verdicts at a=64: " + ", ".join(f"{v} {FD.count(v)}" for v in sorted(set(FD))))
    print(f"\nPRIZE uniform {np.mean(U64):+.3f} patchy {np.mean(P64):+.3f} ratio {np.mean(P64) / np.mean(U64):.2f} n {n}")


if __name__ == "__main__":
    main()
