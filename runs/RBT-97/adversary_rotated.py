"""RBT-97 adversary, round 2: the rotated decoy, per robot and per rotation angle.

The answer's readouts (docs/artifacts/RBT-97-{p801-mechanism,w4b-control}.txt) print the rotated
decoy POOLED only: the per-robot table carries base / motif / phantom / anti and no rotated column,
so the pooled rotated figures cannot be re-derived from the committed files.  This re-runs the
author's own bout() (runs/RBT-97/mechanism.py, imported, not reimplemented) for base, motif and
rotated on both populations at a = 64 and 384, 64 seeds from 7000, signs per robot, and prints:

  1. the per-robot rotated deltas and the pooled figures, to compare against the committed pooled
     line (reproduction check: the simulator is deterministic, so they must agree exactly);
  2. retention split by the rotation angle theta of each bout (the same generator mechanism.py uses:
     default_rng([seed, gen, 97]).uniform(30, 330 deg)).  A rotated field's gradient is the true
     gradient rotated by theta, so for theta near the band edges the decoy still points within
     ~30-60 deg of the food.  If the gain is food-dependent, retention should RISE toward the
     edges (|theta| near 30 deg) and be lowest near 180 deg; a gait effect predicts no trend.

Usage: python runs/RBT-97/adversary_rotated.py [procs]   (~5 min on four cores)
"""
import math
import os
import sys
from multiprocessing import get_context

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "runs", "RBT-97"))
import numpy as np

import mechanism as mech  # the author's instrument

SEEDS = [7000 + i for i in range(64)]
LADDER = (64.0, 384.0)
T975 = {6: 2.447}


def theta(gen, seed):
    return math.degrees(float(np.random.default_rng([seed, gen, 97]).uniform(mech.ROT_LO, mech.ROT_HI)))


def tint(v):
    v = np.asarray(v, float)
    m = float(v.mean())
    h = T975[len(v) - 1] * float(v.std(ddof=1)) / math.sqrt(len(v))
    return m, m - h, m + h


def main():
    procs = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    L = ["RBT-97 adversary round 2: the rotated decoy per robot and per rotation angle (author's bout(), re-run)", ""]
    for pop in ("p801", "w4b"):
        gens = list(mech.cds.POPULATIONS[pop]["gens"])
        mech.CFG[pop] = mech.cds.config(pop)
        mech.SIGN.update({(pop, g): s for g, s in mech.signs_for(pop, gens, "per-robot").items()})
        tasks = [(pop, g, 0.0, s, "base") for g in gens for s in SEEDS]
        tasks += [(pop, g, a, s, c) for g in gens for a in LADDER for s in SEEDS for c in ("motif", "rotated")]
        with get_context("fork").Pool(procs) as pool:
            rows = pool.map(mech.bout, tasks, chunksize=16)
        by = {(r[1], r[2], r[3], r[4]): r for r in rows}
        expl = sum(1 for r in rows if r[10])
        L.append(f"== {pop}: {len(rows)} bouts, {expl} exploded")
        for a in LADDER:
            L.append(f"   a = {a:.0f}   per robot: motif delta, rotated delta, retention")
            md, rd = [], []
            for g in gens:
                m = float(np.mean([by[(g, a, s, 'motif')][9] - by[(g, 0.0, s, 'base')][9] for s in SEEDS]))
                r = float(np.mean([by[(g, a, s, 'rotated')][9] - by[(g, 0.0, s, 'base')][9] for s in SEEDS]))
                md.append(m)
                rd.append(r)
                L.append(f"      g{g:<4d} motif {m:+7.3f}  rotated {r:+7.3f}  retained {100 * r / m:+7.1f}%")
            mm, mlo, mhi = tint(md)
            rm, rlo, rhi = tint(rd)
            L.append(f"      pooled: motif {mm:+.3f} [{mlo:+.3f}, {mhi:+.3f}], rotated {rm:+.3f} [{rlo:+.3f}, {rhi:+.3f}], "
                     f"retention {100 * rm / mm:+.1f}%")
            # by rotation angle: fold theta onto its angular distance from identity, 30..180 deg
            bins = [(30, 60), (60, 90), (90, 120), (120, 150), (150, 180)]
            L.append("      retention by |theta| (angular distance of the decoy from the true layout):")
            for lo, hi in bins:
                ds, dm = [], []
                for g in gens:
                    for s in SEEDS:
                        th = theta(g, s)
                        dist = min(th, 360 - th)
                        if lo <= dist < hi or (hi == 180 and dist == 180):
                            b = by[(g, 0.0, s, "base")][9]
                            ds.append(by[(g, a, s, "rotated")][9] - b)
                            dm.append(by[(g, a, s, "motif")][9] - b)
                se = float(np.std(ds, ddof=1) / math.sqrt(len(ds))) if len(ds) > 1 else float("nan")
                L.append(f"        {lo:3d}-{hi:3d} deg  n = {len(ds):3d} bouts  rotated delta {np.mean(ds):+6.3f} (se {se:.3f})  "
                         f"motif delta on the same bouts {np.mean(dm):+6.3f}  retention {100 * np.mean(ds) / np.mean(dm):+6.1f}%")
            L.append("")
    sys.stdout.write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
