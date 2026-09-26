"""RBT-104 (adversary F4/F7, coordinator 18:40): the seeded founders at t = 0 on all ten seeds.

Pools the adversary's `founders_t0.py` readouts (run unchanged): seed 801 is the adversary's own
`adversary/founders-t0-801.txt`, and the other nine are `founders-t0-SEED.txt` beside this script.
For each K it prints the per-seed cost (seeded - bare) and the planted compass's own food dependence
(F seeded - F bare), then the mean over seeds with t(9).
"""
import os
import re

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SEEDS = (801, 804, 805, 806, 807, 1, 2, 3, 4, 7)
T9 = 2.262
ROWS = {"cost": r"\*\*cost: seeded - bare\*\* \(real smell\)", "F": r"\*\*F seeded - F bare\*\*[^|]*"}
num = r"([-+]\d+\.\d+) \[([-+]\d+\.\d+), ([-+]\d+\.\d+)\]"


def read(seed):
    p = os.path.join(HERE, "adversary", "founders-t0-801.txt") if seed == 801 else os.path.join(HERE, f"founders-t0-{seed}.txt")
    txt = open(p).read()
    out = {}
    for key, lab in ROWS.items():
        m = re.search(rf"^\| {lab}\s*\| {num} \| {num} \|", txt, re.M)
        out[key] = (float(m.group(1)), float(m.group(4)), (m.group(2), m.group(3)), (m.group(5), m.group(6)))
    return out


def main():
    print("# RBT-104: the seeded founders at t = 0, all ten seeds (adversary's founders_t0.py, unchanged)\n")
    print("| seed | cost K=1 | cost K=8 | F seeded - F bare, K=1 | K=8 |")
    print("|---|---|---|---|---|")
    agg = {("cost", 1): [], ("cost", 8): [], ("F", 1): [], ("F", 8): []}
    for s in SEEDS:
        r = read(s)
        cells = []
        for key in ("cost", "F"):
            v1, v8, i1, i8 = r[key]
            agg[(key, 1)].append(v1)
            agg[(key, 8)].append(v8)
            cells += [f"{v1:+.3f} [{i1[0]}, {i1[1]}]", f"{v8:+.3f} [{i8[0]}, {i8[1]}]"]
        print(f"| {s} | {cells[0]} | {cells[1]} | {cells[2]} | {cells[3]} |")
    print()
    for key, lab in (("cost", "cost, seeded - bare"), ("F", "planted compass's food dependence, F seeded - F bare")):
        for K in (1, 8):
            v = np.array(agg[(key, K)])
            se = v.std(ddof=1) / np.sqrt(len(v))
            print(f"{lab}, K = {K}: mean over {len(v)} seeds {v.mean():+.4f}, t(9) [{v.mean() - T9 * se:+.4f}, {v.mean() + T9 * se:+.4f}]"
                  f"; seeds whose own interval excludes zero from above: "
                  f"{sum(1 for s in SEEDS if float((read(s)[key][2] if K == 1 else read(s)[key][3])[0]) > 0)}")


if __name__ == "__main__":
    main()
