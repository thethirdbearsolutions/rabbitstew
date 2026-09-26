"""RBT-106 item 3: the operator-alone persistence baseline, the null for "held" (PREREGISTRATION.md §5.1).

RBT-104's design adversary's `adversary/persistence.py` (F6), imported: its `lineage()` is used
unchanged.  Each of a seed's 30 planted founders is carried down REPS independent lineages of
`mutate_controller` under part 2's own MutationConfig at link_scale 1 (both RBT-106 arms run at
the default reach), with no selection and no crossover, and read at every depth 0..40 with RBT-91's
instruments.  The world does not enter: no bout is run.  Depths go to 40 because the patchy world
breeds faster (§4) and its window sits deeper than part 2's 14-17.5.

Founder sets (founders.py):  w = 1 (RBT-104's, the P1 arm) and w = 32 (the H arms).

Per depth, the fraction of lineages whose best predicate unit (persistence.py's rule: the founder's
sign first, then the largest own-link |a|) has
  same     the planted structure with the founder's sign
  pay32    ... and own-link |a| >= 12.5236, the a = 32 rung (RBT-104 drift_reach.py RUNGS)
  pay64    ... and own-link |a| >= 24.7145, the a = 64 rung
with a one-sided 95% Wilson upper bound, and the median whole-brain |a| (the masking reading).
`held.py` reads the table at each living genome's own depth.

Usage: baseline.py SEED W FOUNDERS_DIR [--reps 20] [--procs 4]  > baseline-wW-SEED.txt
"""
import argparse
import glob
import importlib.util
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
_bspec = importlib.util.spec_from_file_location("rbt104_baseline", os.path.join(_ROOT, "runs", "RBT-104", "baseline.py"))
_b = importlib.util.module_from_spec(_bspec)
_bspec.loader.exec_module(_b)  # loads the adversary's persistence.py as sys.modules["persistence"]
per, wilson_hi = _b.per, _b.wilson_hi
per.DEPTHS = tuple(range(41))  # RBT-104's baseline.py sets 0..30; the patchy window sits deeper
RUNG32, RUNG64 = 12.5236, 24.7145


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("seed", type=int)
    ap.add_argument("w", type=float)
    ap.add_argument("founders")
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--procs", type=int, default=4)
    a = ap.parse_args()
    paths = sorted(glob.glob(os.path.join(a.founders, "conventional", "*.json")))
    planted = [p for p in paths if int(os.path.basename(p)[:3]) % 2 == 0]
    tasks = [(a.seed, p, 1.0, r) for p in planted for r in range(a.reps)]
    with ProcessPoolExecutor(a.procs) as ex:
        L = [out for _, out in ex.map(per.lineage, tasks, chunksize=4)]
    print(f"# RBT-106 no-selection baseline, seed {a.seed}, founders w = {a.w:g}, K = 1: {len(planted)} planted founders x "
          f"{a.reps} lineages = {len(L)}; RBT-104 adversary persistence.py's lineage(), unchanged, depths 0-40")
    print("# depth\tlineages\tsame\tsame_frac\tsame_hi95\tpay32\tpay32_frac\tpay32_hi95\tpay64\tpay64_frac\tpay64_hi95\towns_median\twhole_median")
    for j, depth in enumerate(per.DEPTHS):
        rows = [l[j] for l in L]
        n = len(rows)
        same = sum(r["same"] for r in rows)
        p32 = sum(r["same"] and r["alone"] >= RUNG32 for r in rows)
        p64 = sum(r["same"] and r["alone"] >= RUNG64 for r in rows)
        print(f"{depth}\t{n}\t{same}\t{same / n:.4f}\t{wilson_hi(same, n):.4f}\t{p32}\t{p32 / n:.4f}\t{wilson_hi(p32, n):.4f}\t"
              f"{p64}\t{p64 / n:.4f}\t{wilson_hi(p64, n):.4f}\t{np.median([r['alone'] for r in rows]):.4f}\t"
              f"{np.nanmedian([r['whole'] for r in rows]):.4f}")


if __name__ == "__main__":
    main()
