"""RBT-104 wave-0 futility gate: the no-selection baseline at every depth (PREREGISTRATION.md §6.2).

The design adversary's `adversary/persistence.py`, imported unchanged, at depths 0..30 instead of
its 0, 1, 2, 4, 8, 12, 16, 20, and at K = 8 only (the gate reads S8).  Each of the seed's 30
planted founders (`seed_founders.py`, the files S8 loads) is carried down 20 independent lineages
of `mutate_controller` under part 2's MutationConfig with link_scale 8 and no selection.  At each
depth: the fraction of lineages that still carry the planted structure with its founder's sign and
own-link |a| >= 24.7145 (the a = 64 rung).  `peek.py` reads this table.

Usage: baseline.py SEED FOUNDERS_DIR [--reps 20] [--procs 4]  > baseline-SEED.txt
"""
import argparse
import glob
import importlib.util
import os
import sys
from concurrent.futures import ProcessPoolExecutor

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location("persistence", os.path.join(_HERE, "adversary", "persistence.py"))
per = importlib.util.module_from_spec(_spec)
sys.modules["persistence"] = per  # so the pool can pickle per.lineage
_spec.loader.exec_module(per)
per.DEPTHS = tuple(range(31))
K = 8.0


def wilson_hi(k, n, z=1.6449):
    """One-sided 95% upper bound (Wilson)."""
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / d
    return min(1.0, c + h)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seed", type=int)
    ap.add_argument("founders")
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args()
    paths = sorted(glob.glob(os.path.join(a.founders, "conventional", "*.json")))
    planted = [p for p in paths if int(os.path.basename(p)[:3]) % 2 == 0]
    tasks = [(a.seed, p, K, r) for p in planted for r in range(a.reps)]
    with ProcessPoolExecutor(a.procs) as ex:
        L = [out for _, out in ex.map(per.lineage, tasks, chunksize=4)]
    print(f"# RBT-104 no-selection baseline, seed {a.seed}, K = 8: {len(planted)} planted founders x {a.reps} "
          f"lineages = {len(L)}; adversary/persistence.py's lineage(), unchanged, at depths 0-30")
    print("# depth\tlineages\tpaying\tfraction\tupper95_one_sided")
    for j, depth in enumerate(per.DEPTHS):
        k = sum(l[j]["paying"] for l in L)
        print(f"{depth}\t{len(L)}\t{k}\t{k / len(L):.4f}\t{wilson_hi(k, len(L)):.4f}")


if __name__ == "__main__":
    main()
