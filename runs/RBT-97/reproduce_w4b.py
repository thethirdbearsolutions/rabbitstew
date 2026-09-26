"""RBT-97 condition 1: the generalised probe reproduces the hard-coded one, bout for bout.

`tests/test_rbt97_mechanism.py` pins this on six bouts so it can run in the suite. This is
the wider check the coordinator asked for before the arm runs: every robot, every condition,
the same seeds, both implementations, compared bout by bout rather than mean by mean -- a
mean can agree while the individual bouts do not.

The case is the only one the hard-coded script covers: W4b-801, sign +1, W = 32 (a = 64 in
RBT-67's units, since a = 2k), seeds from 9000, which are the original's own seeds.

Usage: reproduce_w4b.py [n_seeds=16] [procs=4]
"""
import os
import sys
from multiprocessing import get_context

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mechanism as gen  # noqa: E402  (loads compass_mechanism as gen.cm)

CONDS = ("base", "motif", "phantom", "antimotif")


def old_bout(t):
    return gen.cm.bout(t)


def new_bout(t):
    return gen.bout(t)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    procs = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    gens = list(gen.cds.POPULATIONS["w4b"]["gens"])
    seeds = [9000 + i for i in range(n)]
    gen.CFG["w4b"] = gen.cds.config("w4b")
    gen.SIGN.update({("w4b", g): +1.0 for g in gens})

    old_tasks = [(g, s, c) for g in gens for s in seeds for c in CONDS]
    new_tasks = [("w4b", g, 0.0 if c == "base" else 64.0, s, c) for g in gens for s in seeds
                 for c in CONDS]
    with get_context("fork").Pool(procs) as pool:
        old = pool.map(old_bout, old_tasks, chunksize=8)
        new = pool.map(new_bout, new_tasks, chunksize=8)

    print("# RBT-97: runs/RBT-97/mechanism.py against scripts/compass_mechanism.py, bout for bout")
    print(f"W4b-801, sign +1, a = 64 (the original's W = 32; a = 2k), "
          f"{len(gens)} robots x {n} seeds x {len(CONDS)} conditions = {len(old)} bouts each\n")
    print("The generalised script installs through compass_replication.install(), which derives")
    print("the four weights from fixed.drive_commands(); the original types them out. Identical")
    print("output is the evidence that the derivation and the typed signs are the same circuit.\n")

    fields = ("bearing_near", "bearing_grad", "align_near", "align_grad", "items")
    bad = []
    worst = {f: 0.0 for f in fields}
    for o, m in zip(old, new):
        assert (o[0], o[1], o[2]) == (m[1], m[3], m[4]), "task lists are not aligned"
        for i, f in enumerate(fields):
            a, b = o[3 + i], m[5 + i]
            if np.isnan(a) and np.isnan(b):
                continue
            d = abs(a - b)
            worst[f] = max(worst[f], d)
            if d != 0.0:
                bad.append((o[0], o[1], o[2], f, a, b))

    print(f"{'field':>14s} | {'max |old - new|':>15s}")
    for f in fields:
        print(f"{f:>14s} | {worst[f]:15.1e}")
    by_cond = {c: sum(1 for x in bad if x[2] == c) for c in CONDS}
    print(f"\nbouts compared {len(old)}; differing values {len(bad)}"
          f"  (per condition: {', '.join(f'{c} {by_cond[c]}' for c in CONDS)})")
    for row in bad[:10]:
        print("  DIFF", row)
    print("\nREPRODUCED EXACTLY" if not bad else "\nNOT REPRODUCED -- the arm must not run")
    return 0 if not bad else 1


if __name__ == "__main__":
    sys.exit(main())
